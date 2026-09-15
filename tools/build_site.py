#!/usr/bin/env python3
"""SurviveOs 总站生成器。

读取仓库现有内容（0002 清单 + 各区域/模块文档 + git 历史），在 docs/ 下生成一套
可直接用 GitHub Pages 发布的静态站点：

  docs/index.html                 总站首页：进度仪表盘 / 7 区域模块索引 / 最新动态时间线
  docs/<区域>/<模块>/...html      仓库里的 .md 渲染成网页，.html 原样搬运，代码文件带预览页

不依赖任何第三方库，只用标准库；GitHub Actions 里 `python3 tools/build_site.py` 即可。
本脚本不改动仓库里的任何原始文档，只写 docs/。
"""

import html
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs"
LIST_DOC = ROOT / "00-总览" / "0002-区域与子模块清单.md"

SKIP_DIRS = {".git", ".github", "docs", "tools", "node_modules", "_backup"}
COPY_EXT = {".html", ".htm", ".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp",
            ".pdf", ".css", ".js", ".json", ".stl", ".zip", ".3mf"}
CODE_EXT = {".yaml", ".yml", ".py", ".scad", ".sh", ".txt", ".csv", ".ino", ".c", ".cpp"}

STATUS_META = {
    "✅": ("done", "已完成"),
    "🚧": ("wip", "设计中"),
    "⬜": ("todo", "待设计"),
    "🆕": ("new", "待补录"),
}
STATUS_ORDER = ["✅", "🚧", "🆕", "⬜"]
CN_TZ = timezone(timedelta(hours=8))


# --------------------------------------------------------------------------
# 极简 Markdown 渲染（够用即可：标题/列表/表格/代码块/引用/分割线/行内样式）
# --------------------------------------------------------------------------

def _inline(text: str) -> str:
    out = html.escape(text, quote=False)
    codes: list[str] = []

    def stash_code(m: re.Match) -> str:
        codes.append(m.group(1))
        return f"\x00{len(codes) - 1}\x00"

    out = re.sub(r"`([^`]+)`", stash_code, out)
    out = re.sub(r"!\[([^\]]*)\]\(([^)\s]+)\)",
                 lambda m: f'<img src="{_fix_href(m.group(2))}" alt="{m.group(1)}">', out)
    out = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)",
                 lambda m: f'<a href="{_fix_href(m.group(2))}">{m.group(1)}</a>', out)
    out = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])", r"<em>\1</em>", out)
    out = re.sub(r"(?<!\()\b(https?://[^\s<）)，。]+)",
                 lambda m: f'<a href="{m.group(1)}">{m.group(1)}</a>', out)
    out = re.sub(r"\x00(\d+)\x00", lambda m: f"<code>{codes[int(m.group(1))]}</code>", out)
    return out


def _fix_href(href: str) -> str:
    """仓库内 .md 链接指向生成后的 .html；外链原样保留。"""
    if href.startswith(("http://", "https://", "#", "mailto:")):
        return href
    anchor = ""
    if "#" in href:
        href, anchor = href.split("#", 1)
        anchor = "#" + anchor
    if href.endswith(".md"):
        href = href[:-3] + ".html"
    elif Path(href).suffix.lower() in CODE_EXT:
        href = href + ".html"
    return href + anchor


def md_to_html(text: str) -> tuple[str, str]:
    """返回 (标题, 正文 HTML)。"""
    title = ""
    if text.startswith("---\n"):
        end = text.find("\n---", 4)
        if end != -1:
            front = text[4:end]
            text = text[end + 4:].lstrip("\n")
            m = re.search(r"^title:\s*(.+)$", front, re.M)
            if m:
                title = m.group(1).strip()

    lines = text.split("\n")
    out: list[str] = []
    i, n = 0, len(lines)
    list_stack: list[str] = []

    def close_lists(level: int = 0) -> None:
        while len(list_stack) > level:
            out.append(f"</{list_stack.pop()}>")

    while i < n:
        line = lines[i]

        if line.startswith("```"):
            close_lists()
            i += 1
            buf = []
            while i < n and not lines[i].startswith("```"):
                buf.append(lines[i])
                i += 1
            i += 1
            out.append("<pre><code>" + html.escape("\n".join(buf)) + "</code></pre>")
            continue

        if not line.strip():
            close_lists()
            i += 1
            continue

        if re.match(r"^\s*(---|\*\*\*|___)\s*$", line):
            close_lists()
            out.append("<hr>")
            i += 1
            continue

        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            close_lists()
            level = len(m.group(1))
            text_h = _inline(m.group(2).strip())
            if not title and level == 1:
                title = re.sub(r"<[^>]+>", "", text_h)
            out.append(f"<h{level}>{text_h}</h{level}>")
            i += 1
            continue

        if line.lstrip().startswith(">"):
            close_lists()
            buf = []
            while i < n and lines[i].lstrip().startswith(">"):
                buf.append(lines[i].lstrip()[1:].lstrip())
                i += 1
            out.append("<blockquote>" + _inline(" ".join(buf)) + "</blockquote>")
            continue

        if line.lstrip().startswith("|") and i + 1 < n and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1]):
            close_lists()
            header = [c.strip() for c in line.strip().strip("|").split("|")]
            i += 2
            rows = []
            while i < n and lines[i].lstrip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            th = "".join(f"<th>{_inline(c)}</th>" for c in header)
            tb = "".join("<tr>" + "".join(f"<td>{_inline(c)}</td>" for c in r) + "</tr>" for r in rows)
            out.append(f'<div class="table-wrap"><table><thead><tr>{th}</tr></thead><tbody>{tb}</tbody></table></div>')
            continue

        m = re.match(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$", line)
        if m:
            indent, marker, body = len(m.group(1)), m.group(2), m.group(3)
            tag = "ul" if marker in "-*+" else "ol"
            level = indent // 2 + 1
            while len(list_stack) > level:
                out.append(f"</{list_stack.pop()}>")
            if len(list_stack) < level:
                out.append(f"<{tag}>")
                list_stack.append(tag)
            out.append(f"<li>{_inline(body)}</li>")
            i += 1
            continue

        close_lists()
        buf = [line]
        i += 1
        while i < n and lines[i].strip() and not re.match(r"^(#{1,6}\s|```|\s*[-*+]\s|\s*\d+[.)]\s|\s*\||\s*>)", lines[i]):
            buf.append(lines[i])
            i += 1
        out.append("<p>" + _inline(" ".join(s.strip() for s in buf)) + "</p>")

    close_lists()
    return title, "\n".join(out)


# --------------------------------------------------------------------------
# 页面外壳
# --------------------------------------------------------------------------

def page_shell(title: str, body: str, depth: int, *, wide: bool = False) -> str:
    up = "../" * depth
    cls = "wide" if wide else ""
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<meta name="robots" content="noindex,nofollow">
<title>{html.escape(title)}</title>
<link rel="stylesheet" href="{up}assets/style.css">
</head>
<body class="{cls}">
{body}
</body>
</html>
"""


STYLE = """/* SurviveOs 总站样式：手机优先，沿用模块方案页的纸墨配色 */
:root{
  --paper:#e7dfc7; --paper-deep:#ddd3b3; --card:#f1ebd9;
  --ink:#2a2318; --ink-soft:#5a5040;
  --jade:#4b5d45; --jade-deep:#374530; --seal:#8a2e21; --brass:#a1793f;
  --line:#c9bd97;
}
*{box-sizing:border-box;}
html{scroll-behavior:smooth;-webkit-text-size-adjust:100%;}
body{
  margin:0;background:var(--paper);color:var(--ink);line-height:1.8;
  font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Noto Sans SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;
  font-size:16px;
  padding:env(safe-area-inset-top,0) 0 calc(32px + env(safe-area-inset-bottom,0));
}
.wrap{max-width:860px;margin:0 auto;padding:0 16px;}
a{color:var(--jade-deep);}
a:hover{color:var(--seal);}
img{max-width:100%;height:auto;}

header.top{background:var(--jade-deep);color:var(--paper);padding:28px 0 22px;}
header.top h1{margin:0 0 6px;font-size:26px;letter-spacing:.06em;}
header.top p{margin:0;color:#cfd6c6;font-size:14px;}
header.top a{color:#e7dfc7;}

nav.regions{position:sticky;top:env(safe-area-inset-top,0);z-index:9;background:var(--paper-deep);
  border-bottom:1px solid var(--line);overflow-x:auto;white-space:nowrap;padding:10px 12px;}
nav.regions a{display:inline-block;margin-right:10px;padding:4px 10px;border:1px solid var(--line);
  border-radius:999px;background:var(--card);text-decoration:none;font-size:14px;}

section{padding:26px 0 6px;}
h2{font-size:20px;margin:0 0 4px;padding-bottom:8px;border-bottom:2px solid var(--jade);}
h2 .sub{font-size:13px;color:var(--ink-soft);font-weight:400;margin-left:8px;}
h3{font-size:17px;margin:22px 0 8px;}

.stats{display:grid;grid-template-columns:repeat(2,1fr);gap:10px;margin:16px 0 8px;}
@media(min-width:560px){.stats{grid-template-columns:repeat(4,1fr);}}
.stat{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px;text-align:center;}
.stat b{display:block;font-size:24px;line-height:1.3;}
.stat span{font-size:13px;color:var(--ink-soft);}
.bar{display:flex;height:12px;border-radius:999px;overflow:hidden;border:1px solid var(--line);margin:6px 0 2px;}
.bar i{display:block;}
.bar .done{background:var(--jade);} .bar .wip{background:var(--brass);}
.bar .new{background:var(--seal);} .bar .todo{background:var(--paper-deep);}
.legend{font-size:13px;color:var(--ink-soft);}

.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 14px;margin:10px 0;}
.card .head{display:flex;gap:8px;align-items:baseline;flex-wrap:wrap;}
.card .code{font-variant-numeric:tabular-nums;color:var(--ink-soft);font-size:14px;}
.card .name{font-weight:600;font-size:16px;}
.card .desc{margin:6px 0 0;font-size:14px;color:var(--ink-soft);}
.badge{font-size:12px;padding:1px 8px;border-radius:999px;border:1px solid var(--line);white-space:nowrap;}
.badge.done{background:var(--jade);color:var(--paper);border-color:var(--jade);}
.badge.wip{background:var(--brass);color:#fff;border-color:var(--brass);}
.badge.new{background:var(--seal);color:#fff;border-color:var(--seal);}
.badge.todo{background:var(--paper-deep);color:var(--ink-soft);}
.links{margin:8px 0 0;padding:0;list-style:none;display:flex;flex-wrap:wrap;gap:8px;}
.links a{display:inline-block;padding:3px 10px;border:1px solid var(--jade);border-radius:6px;
  background:var(--paper);text-decoration:none;font-size:13px;}

ul.timeline{list-style:none;padding:0;margin:12px 0;}
ul.timeline li{border-left:2px solid var(--line);padding:0 0 12px 14px;position:relative;font-size:14px;}
ul.timeline li::before{content:"";position:absolute;left:-5px;top:9px;width:8px;height:8px;
  border-radius:50%;background:var(--jade);}
ul.timeline .date{color:var(--ink-soft);font-variant-numeric:tabular-nums;margin-right:6px;}

footer{margin-top:28px;padding:18px 0;border-top:1px solid var(--line);font-size:13px;color:var(--ink-soft);}

/* 由 .md 渲染出来的文档页 */
body.doc article{background:var(--card);border:1px solid var(--line);border-radius:10px;
  padding:18px 16px;margin:16px 0;}
body.doc h1{font-size:22px;margin:0 0 12px;}
body.doc h2{font-size:19px;margin:24px 0 8px;}
body.doc h3{font-size:16px;}
body.doc pre{background:#efe8d4;border:1px solid var(--line);border-radius:8px;padding:12px;
  overflow-x:auto;font-size:13px;line-height:1.6;}
body.doc code{background:#efe8d4;padding:1px 5px;border-radius:4px;font-size:13px;}
body.doc pre code{background:none;padding:0;}
body.doc blockquote{margin:12px 0;padding:8px 12px;border-left:3px solid var(--brass);
  background:#efe8d4;color:var(--ink-soft);}
.table-wrap{overflow-x:auto;}
table{border-collapse:collapse;min-width:100%;font-size:14px;}
th,td{border:1px solid var(--line);padding:6px 10px;text-align:left;}
th{background:var(--paper-deep);}
.crumb{font-size:13px;color:var(--ink-soft);padding:12px 0 0;}
.crumb a{text-decoration:none;}
"""


# --------------------------------------------------------------------------
# 读取仓库内容
# --------------------------------------------------------------------------

def parse_module_list() -> list[dict]:
    """解析 0002 清单，得到区域 + 模块（状态/编号/名称/说明）。"""
    regions: list[dict] = []
    if not LIST_DOC.exists():
        return regions
    for line in LIST_DOC.read_text(encoding="utf-8").split("\n"):
        m = re.match(r"^##\s+(\d{2})\s+(.+?)\s*$", line)
        if m:
            name = m.group(2)
            note = ""
            mm = re.match(r"^(.*?)（(.*)）$", name)
            if mm:
                name, note = mm.group(1), mm.group(2)
            regions.append({"code": m.group(1), "name": name, "note": note, "modules": []})
            continue
        m = re.match(r"^-\s+([✅🚧⬜🆕])\s+(\d{4})\s+(.*)$", line)
        if m and regions:
            rest = m.group(3)
            if " — " in rest:
                name, desc = rest.split(" — ", 1)
            else:
                name, desc = rest, ""
            regions[0 - 1] if False else None
            regions[-1]["modules"].append({
                "status": m.group(1), "code": m.group(2),
                "name": name.strip(), "desc": desc.strip(),
            })
    return regions


def region_dirs() -> dict[str, Path]:
    out = {}
    for p in sorted(ROOT.iterdir()):
        if p.is_dir() and re.match(r"^\d{2}-", p.name):
            out[p.name[:2]] = p
    return out


def entry_codes(name: str) -> list[str]:
    """`0201-模拟阳光` -> ['0201']；`0601-0603-稀树草原环境系统` -> ['0601','0602','0603']。"""
    m = re.match(r"^(\d{4})(?:-(\d{4}))?(?:-|\.|$)", name)
    if not m:
        return []
    start = int(m.group(1))
    end = int(m.group(2)) if m.group(2) else start
    if end < start or end - start > 20:
        end = start
    return [f"{c:04d}" for c in range(start, end + 1)]


def module_entries() -> dict[str, Path]:
    """模块编号 -> 仓库里承载它的文件夹或 .md 文件。"""
    found: dict[str, Path] = {}
    for rdir in region_dirs().values():
        for entry in sorted(rdir.iterdir()):
            if entry.name.startswith(".") or entry.name == "README.md":
                continue
            for code in entry_codes(entry.name):
                found.setdefault(code, entry)
    return found


def doc_pages(entry: Path) -> list[tuple[str, str]]:
    """模块内可点开的文档：(标题, 相对 docs/ 的链接)。"""
    pages: list[tuple[str, str]] = []
    if entry.is_file():
        if entry.suffix == ".md":
            pages.append((entry.stem, rel_href(entry)))
        return pages
    candidates: list[Path] = []
    for p in sorted(entry.rglob("*")):
        if any(part in SKIP_DIRS for part in p.relative_to(ROOT).parts):
            continue
        if p.is_file() and p.suffix.lower() in {".md", ".html", ".htm"}:
            candidates.append(p)
    # index/README 排前面，子目录里的分页（hw/ 之类）不逐个列出，只留目录首页
    def sort_key(p: Path) -> tuple:
        depth = len(p.relative_to(entry).parts)
        prio = 0 if p.stem.lower() in {"index", "readme"} else 1
        return (depth, prio, p.name)
    for p in sorted(candidates, key=sort_key):
        rel = p.relative_to(entry)
        if len(rel.parts) > 1 and p.stem.lower() not in {"index", "readme"}:
            continue
        label = p.stem
        if label.lower() == "readme":
            label = "模块说明" if len(rel.parts) == 1 else f"{rel.parts[0]}／说明"
        elif label.lower() == "index":
            label = "方案主页" if len(rel.parts) == 1 else f"{rel.parts[0]}／主页"
        pages.append((label, rel_href(p)))
    return pages


def rel_href(path: Path) -> str:
    rel = path.relative_to(ROOT)
    if rel.suffix == ".md":
        rel = rel.with_suffix(".html")
    elif rel.suffix.lower() in CODE_EXT:
        rel = rel.with_name(rel.name + ".html")
    return "/".join(rel.parts)


def git_timeline(limit: int = 24) -> list[tuple[str, str]]:
    try:
        raw = subprocess.run(
            ["git", "-C", str(ROOT), "log", f"-n{limit}", "--date=short", "--pretty=format:%ad\t%s"],
            capture_output=True, text=True, timeout=30, check=True).stdout
    except Exception:
        return []
    items = []
    for line in raw.strip().split("\n"):
        if "\t" in line:
            date, subject = line.split("\t", 1)
            items.append((date, subject))
    return items


# --------------------------------------------------------------------------
# 生成
# --------------------------------------------------------------------------

def copy_and_render() -> None:
    for src in sorted(ROOT.rglob("*")):
        rel = src.relative_to(ROOT)
        if any(part in SKIP_DIRS or part.startswith(".") for part in rel.parts):
            continue
        if src.is_dir() or src.name.startswith("."):
            continue
        suffix = src.suffix.lower()
        if suffix == ".md":
            dest = OUT / rel.with_suffix(".html")
            dest.parent.mkdir(parents=True, exist_ok=True)
            title, body = md_to_html(src.read_text(encoding="utf-8"))
            depth = len(rel.parts) - 1
            up = "../" * depth
            crumb = f'<div class="crumb"><a href="{up}index.html">← 回总站</a> · {html.escape(str(rel.parent))}</div>'
            page = (f'<div class="wrap">{crumb}<article>{body}</article>'
                    f'<footer>来源：仓库文件 <code>{html.escape(str(rel))}</code>，本页由 tools/build_site.py 生成。</footer></div>')
            dest.write_text(page_shell(title or src.stem, page, depth).replace(
                '<body class="">', '<body class="doc">'), encoding="utf-8")
        elif suffix in COPY_EXT:
            dest = OUT / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
        elif suffix in CODE_EXT:
            dest = OUT / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            depth = len(rel.parts) - 1
            up = "../" * depth
            code = html.escape(src.read_text(encoding="utf-8", errors="replace"))
            body = (f'<div class="wrap"><div class="crumb"><a href="{up}index.html">← 回总站</a> · '
                    f'{html.escape(str(rel))}</div><article><h1>{html.escape(src.name)}</h1>'
                    f'<p><a href="{html.escape(src.name)}">下载原文件</a></p><pre><code>{code}</code></pre></article></div>')
            (dest.parent / (src.name + ".html")).write_text(
                page_shell(src.name, body, depth).replace('<body class="">', '<body class="doc">'),
                encoding="utf-8")


def build_index() -> str:
    regions = parse_module_list()
    entries = module_entries()

    counts = {s: 0 for s in STATUS_ORDER}
    total = 0
    for r in regions:
        for mod in r["modules"]:
            counts[mod["status"]] = counts.get(mod["status"], 0) + 1
            total += 1

    parts: list[str] = []
    parts.append('<header class="top"><div class="wrap">'
                 '<h1>SurviveOs · 总站</h1>'
                 '<p>可维护、可生长的乡野生存系统 — 本页由仓库内容自动生成，'
                 '每次 push 后 GitHub Actions 重新构建发布。</p></div></header>')

    nav = "".join(f'<a href="#r{r["code"]}">{r["code"]} {html.escape(r["name"])}</a>' for r in regions)
    parts.append(f'<nav class="regions"><a href="#dash">总览</a>{nav}<a href="#meta">元文档</a>'
                 f'<a href="#timeline">动态</a></nav>')

    parts.append('<div class="wrap">')

    # 仪表盘
    stat_cards = "".join(
        f'<div class="stat"><b>{counts.get(s, 0)}</b><span>{s} {STATUS_META[s][1]}</span></div>'
        for s in STATUS_ORDER)
    bar = "".join(
        f'<i class="{STATUS_META[s][0]}" style="width:{(counts.get(s, 0) / total * 100) if total else 0:.1f}%"></i>'
        for s in STATUS_ORDER)
    parts.append(
        f'<section id="dash"><h2>总览<span class="sub">{len(regions)} 个区域 · {total} 个已知条目</span></h2>'
        f'<div class="stats">{stat_cards}</div><div class="bar">{bar}</div>'
        f'<p class="legend">状态来自 <a href="00-总览/0002-区域与子模块清单.html">0002 区域与子模块清单</a>，'
        f'那份文档是编号与状态的唯一权威来源。</p></section>')

    # 区域板块
    for r in regions:
        cards = []
        for mod in r["modules"]:
            cls, label = STATUS_META[mod["status"]]
            entry = entries.get(mod["code"])
            links = ""
            if entry:
                pages = doc_pages(entry)
                if pages:
                    links = '<ul class="links">' + "".join(
                        f'<li><a href="{html.escape(href)}">{html.escape(text)}</a></li>'
                        for text, href in pages) + "</ul>"
            desc = f'<p class="desc">{html.escape(mod["desc"])}</p>' if mod["desc"] else ""
            cards.append(
                f'<div class="card"><div class="head"><span class="badge {cls}">{mod["status"]} {label}</span>'
                f'<span class="code">{mod["code"]}</span><span class="name">{html.escape(mod["name"])}</span></div>'
                f'{desc}{links}</div>')
        note = f'<p class="legend">{html.escape(r["note"])}</p>' if r["note"] else ""
        rdir = region_dirs().get(r["code"])
        readme = ""
        if rdir and (rdir / "README.md").exists():
            readme = f'<p class="legend"><a href="{rel_href(rdir / "README.md")}">区域说明 README</a></p>'
        parts.append(f'<section id="r{r["code"]}"><h2>{r["code"]} {html.escape(r["name"])}'
                     f'<span class="sub">{len(r["modules"])} 个条目</span></h2>{note}{readme}'
                     + "".join(cards) + "</section>")

    # 元文档
    meta_links = []
    meta_dir = ROOT / "00-总览"
    if meta_dir.exists():
        for p in sorted(meta_dir.iterdir()):
            if p.suffix.lower() in {".md", ".html"}:
                meta_links.append(f'<li><a href="{rel_href(p)}">{html.escape(p.stem)}</a></li>')
    parts.append('<section id="meta"><h2>00 总览<span class="sub">方法论与元文档</span></h2>'
                 '<div class="card"><ul class="links">' + "".join(meta_links) + "</ul></div></section>")

    # 时间线
    tl = git_timeline()
    items = "".join(f'<li><span class="date">{html.escape(d)}</span>{html.escape(s)}</li>' for d, s in tl)
    parts.append('<section id="timeline"><h2>最新动态<span class="sub">取自 git 提交历史</span></h2>'
                 f'<ul class="timeline">{items}</ul></section>')

    now = datetime.now(CN_TZ).strftime("%Y-%m-%d %H:%M")
    parts.append(
        f'<footer>本页由 <code>tools/build_site.py</code> 读取仓库内容生成，'
        f'生成时间 {now}（北京时间）。内容权威来源是 GitHub 仓库 '
        f'<a href="https://github.com/richardvane-droid/SurviveOs">richardvane-droid/SurviveOs</a>，'
        f'总站只是它的一个视图，不单独维护第二份内容。'
        f'另有一份"完整形态设想"站点（非真实进度）：'
        f'<a href="https://richardvane-droid.github.io/surviveos-vision/">surviveos-vision</a>。</footer>')
    parts.append("</div>")
    return page_shell("SurviveOs · 总站", "\n".join(parts), 0)


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    (OUT / "assets").mkdir()
    (OUT / "assets" / "style.css").write_text(STYLE, encoding="utf-8")
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    (OUT / "robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf-8")
    copy_and_render()
    (OUT / "index.html").write_text(build_index(), encoding="utf-8")
    files = sum(1 for _ in OUT.rglob("*") if _.is_file())
    print(f"已生成 {files} 个文件到 {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
