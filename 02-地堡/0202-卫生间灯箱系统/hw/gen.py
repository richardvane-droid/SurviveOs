# -*- coding: utf-8 -*-
"""生成地堡灯箱卫生间·硬件专题库的独立页面"""
import os

OUT = os.path.dirname(os.path.abspath(__file__))

CSS = """
:root{--bg:#faf6ec;--card:#fffdf7;--line:#e6dcc3;--ink:#2f2a1f;--muted:#7a7260;--accent:#b98a2f;--accent-deep:#8a6420;--accent-soft:#f3e7c8;--shadow:0 1px 3px rgba(180,150,80,.12);}
*{box-sizing:border-box;margin:0;padding:0;}
body{background:var(--bg);color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif;line-height:1.68;}
.wrap{max-width:860px;margin:0 auto;padding:18px 16px 64px;}
nav.top{display:flex;gap:10px;align-items:center;margin-bottom:16px;flex-wrap:wrap;}
nav.top a{font-size:12.5px;font-weight:600;color:var(--accent-deep);background:var(--accent-soft);border:1px solid var(--line);border-radius:999px;padding:6px 12px;text-decoration:none;}
nav.top a:hover{background:#efdcb2;}
nav.top .spacer{flex:1;}
h1{font-size:25px;font-weight:800;letter-spacing:.02em;margin-top:2px;}
.tag{display:inline-block;font-size:11px;font-weight:700;color:#fff;background:var(--accent);border-radius:999px;padding:3px 11px;margin-bottom:10px;letter-spacing:.06em;}
.lead{color:var(--muted);font-size:14px;margin:10px 0 14px;}
.price{font-size:14.5px;font-weight:800;color:var(--accent-deep);margin-bottom:16px;}
.fig{border:1px solid var(--line);border-radius:16px;background:#fff;padding:10px;box-shadow:var(--shadow);margin-bottom:8px;}
.fig img{width:100%;border-radius:12px;display:block;}
.fig .cap{font-size:11.5px;color:var(--muted);padding:8px 4px 2px;text-align:center;}
h2{font-size:17px;font-weight:800;margin:24px 0 10px;padding-left:11px;border-left:4px solid var(--accent);}
p{font-size:14px;color:#3d3729;margin:9px 0;}
p b{color:var(--ink);}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:14px 16px;box-shadow:var(--shadow);margin:10px 0;}
table{width:100%;border-collapse:collapse;font-size:13px;background:var(--card);border:1px solid var(--line);border-radius:12px;overflow:hidden;margin:12px 0;}
th{background:var(--accent-soft);text-align:left;padding:9px 12px;color:var(--ink);font-size:12.5px;border-bottom:1px solid var(--line);}
td{padding:8px 12px;border-top:1px solid var(--line);color:#3d3729;vertical-align:top;}
td:first-child{font-weight:700;color:var(--ink);white-space:nowrap;}
.buy{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:6px;}
@media(max-width:600px){.buy{grid-template-columns:1fr;}}
.buy a{display:block;background:var(--card);border:1px solid var(--line);border-radius:14px;padding:14px 16px;text-decoration:none;box-shadow:var(--shadow);color:var(--ink);}
.buy a b{color:var(--accent-deep);font-size:14px;display:block;}
.buy a span{font-size:12px;color:var(--muted);display:block;margin-top:4px;}
.nav2{display:flex;justify-content:space-between;gap:10px;margin-top:28px;}
.nav2 a{font-size:13px;font-weight:600;color:var(--accent-deep);text-decoration:none;border:1px solid var(--line);border-radius:999px;padding:9px 15px;background:var(--card);box-shadow:var(--shadow);}
.nav2 a.next{margin-left:auto;}
.warn{background:#fdf3e3;border:1px dashed var(--accent);border-radius:12px;padding:12px 14px;font-size:13px;color:#5a4a20;margin:14px 0;}
footer{text-align:center;margin-top:30px;color:var(--muted);font-size:12px;}
"""

# 硬件数据
HW = [
 dict(slug="yuba", name="1000W 浴霸（石英红外）", tag="灯箱核心光源", price="参考价 300-500 元",
  img="https://aka.doubaocdn.com/s/NRR4fUGbaN", cap="拆解原理图：石英红外灯管 ×4 · 反射罩 · 格栅 · 温控",
  paras=[
   "整个灯箱的“太阳芯”。石英红外灯管通电后灯丝升至约 <b>2,800K</b>，同时辐射<b>可见光与近红外（IR）</b>：可见光负责“照亮”，红外直接照到皮肤上产热。",
   "光效 18-20 lm/W → 1000W ≈ <b>19,000 lm</b>，这就是灯箱的总光通；配合六面镜的反射，1 个灯源被“复制”成满屋子光。",
   "红外部分抵消湿身蒸发散热——这是冬季洗澡“湿着不冷”的关键，也让 15 分钟晨浴的体温上升有物理支撑。",
  ],
  params=[("功率","1000W"),("色温","≈2,800K 暖光"),("光通量","≈19,000 lm"),("红外辐射","有（取暖核心）"),("布局建议","两灯朝玻璃门直射出光 + 两灯朝镜面空间反射出光"),("控制","灯/热独立开关，可接智能开关")],
  taobao=[("淘宝·四灯红外浴霸","浴霸四灯红外"),("淘宝·1000W","浴霸 1000w")],
  xianyu="浴霸 拆机",
  warn="别买“LED 灯暖合一”款当主光源——LED 无红外、光谱偏冷，既没有暖光质感也丢了红外取暖；本方案主灯必须是石英/碳纤维红外浴霸，LED 只做 5000K 唤醒辅助。"),

 dict(slug="mosaic", name="镜面不锈钢马赛克", tag="灯箱镜面材料", price="参考价 19-20㎡ × 200-350 元/㎡ ≈ 3,800-7,000 元",
  img="https://aka.doubaocdn.com/s/6sVwk1vUdw", cap="拆解原理图：抛光镜面表层 · 粘结层 · 基层墙面",
  paras=[
   "灯箱的“反射皮肤”。表层 304 不锈钢镜面 ≈ <b>0.9-0.95 镜面反射率</b>：光打上去不是被吸收而是被“弹回”空间，五面合围后，浴霸的一盏灯通过无穷次反射变成“满屋子灯”。",
   "勾缝用 <b>1mm 细缝</b>——勾缝剂是漫反射暗区，缝越细、反射折损越小；地面同铺，防滑交给防滑拖鞋（见方案“六面全镜”）。",
   "配合不锈钢蹲便与镜面盖板，整个空间不存在“暗吸收体”，灯箱效率最大化。",
  ],
  params=[("材质","304 不锈钢抛光镜面"),("厚度","0.8-1.0mm"),("反射率","≈0.9-0.95"),("表面","光面（非拉丝）"),("勾缝","≤1mm 细缝"),("用量","19-20㎡（2㎡卫生间六面）")],
  taobao=[("淘宝·镜面不锈钢马赛克","镜面不锈钢马赛克"),("淘宝·0.8mm厚","镜面不锈钢马赛克0.8厚")],
  xianyu="镜面不锈钢马赛克",
  warn="千万别买“仿镜面墙贴/贴膜”——反射率仅 0.3-0.5 且易起泡，灯箱光效直接腰斩；必须真 304 抛光件，先索样再下单。"),

 dict(slug="glassdoor", name="超白钢化玻璃门", tag="唯一出光口", price="参考价 2,000-3,500 元（含五金）",
  img="https://aka.doubaocdn.com/s/RC9gO6eAv9", cap="效果示意：门 = 灯箱唯一的出光口",
  paras=[
   "灯箱唯一的光“出口”，透过率直接决定地堡亮度。<b>超白玻璃（低铁）透光 91-92%</b>，普通玻璃只有 83-86%——差 8% 就是地堡里肉眼可辨的亮度差。",
   "10mm 钢化保证安全；对近红外透射 70-85%，所以门关着也有约 <b>500W</b> 辐射热进地堡（门开是 900W 全量供暖）。",
   "框架尽量细窄——框越细，出光缝越大；隐私用<b>门外拉帘</b>解决，不牺牲透光率。",
  ],
  params=[("透光率","≥91%（超白）"),("厚度","10mm 钢化"),("近红外透射","70-85%"),("隐私方案","门外遮光帘（非电控玻璃）"),("五金","细窄框架移门/平开")],
  taobao=[("淘宝·超白钢化移门","超白钢化玻璃移门"),("淘宝·平开门","超白钢化玻璃平开门")],
  xianyu="超白钢化玻璃门",
  warn="一定要“超白”：看玻璃侧面发蓝是超白、发绿是普通玻璃；夹胶玻璃会降透光，别用。"),

 dict(slug="squat", name="不锈钢蹲便 + 镜面盖板", tag="地面反射闭环", price="蹲便 150-600 元 + 镜面盖 300-800 元（定制）",
  img="https://aka.doubaocdn.com/s/ipwkdmGPkV", cap="效果示意：六面镜空间内的不锈钢蹲便",
  paras=[
   "陶瓷蹲便是“暗吸收体”，会吃掉地面反射；<b>不锈钢蹲便</b>与马赛克同为镜面材料，让地面反射不中断。",
   "<b>镜面盖板</b>（304 镜面 + 钢框，承重 ≥150kg）盖上后与地面齐平，整个地面闭合为一面完整镜子——无限镜在脚底连通，灯箱再无“暗区”。",
   "防臭水封照常，掀盖即用；边缘做 2cm 警示细缝防误踩。",
  ],
  params=[("蹲便材质","不锈钢（非陶瓷）"),("盖板材质","304 镜面 + 钢框"),("承重","≥150kg"),("闭合效果","地面成完整镜面"),("水封","防臭水封照常")],
  taobao=[("淘宝·不锈钢蹲便器","不锈钢蹲便器"),("淘宝·不锈钢镜面板定制","不锈钢镜面板定制")],
  xianyu="不锈钢蹲便器",
  warn="镜面盖板是定制件：按蹲便外沿尺寸做 + 内置加强筋保证承重，务必让加工店确认≥150kg 载荷；边缘警示细缝不能省。"),

 dict(slug="shower", name="空气注入顶喷花洒", tag="热带雨淋", price="参考价 国产 300-1,200 / 进口 2,000-3,500 元",
  img="https://aka.doubaocdn.com/s/dMYpBZHEwY", cap="拆解原理图：文丘里水气混合腔 · 空气注入 · 出水面板",
  paras=[
   "把淋浴变成“热带阵雨”。核心是<b>文丘里效应</b>：水流高速穿过收缩腔形成负压、自动吸入空气，在混合腔里把水打成“含气泡的大水珠”——颗粒更大更软、落体更密，包裹全身。",
   "含气水流还更省水（约 <b>30%</b>）；配合软水系统，水流温润不刺痛、皮肤不紧绷。",
   "选购认准“空气注入”标识，顶喷直径 ≥25cm；配增压泵可让雨淋更饱满。",
  ],
  params=[("顶喷直径","≥25cm"),("核心结构","文丘里水气混合腔"),("省水","约 30%"),("体感","大颗软水珠·包裹式"),("配合","软水 + 增压泵更佳")],
  taobao=[("淘宝·空气注入顶喷","空气注入顶喷花洒"),("淘宝·进口(汉斯格雅)","汉斯格雅飞雨")],
  xianyu="空气注入花洒",
  warn="淘宝很多“增压花洒”只是缩小出水孔（假增压、刺肤、易堵），务必认准“空气注入/空气增压”真文丘里结构。"),

 dict(slug="softener", name="离子交换软水机", tag="镜面保洁员", price="参考价 家用 2,500-5,000 / 进口 1 万+ 元",
  img="https://aka.doubaocdn.com/s/EtXCgDUsZU", cap="拆解原理图：树脂罐 · 控制阀头 · 盐箱 · 再生管路",
  paras=[
   "镜面马赛克与玻璃门“永不结垢”的根本保证。水流经树脂罐时，<b>钠型阳离子树脂用 Na⁺ 交换掉水里的 Ca²⁺/Mg²⁺</b>——水垢的“原料”被拿走，硬水变软水。",
   "树脂饱和后用盐箱里的盐水再生（需定期加软水盐）；再生周期取决于用水量与树脂量。",
   "装于<b>地堡侧</b>，只把软水管引入卫生间；无盐“阻垢柔水器”不是真软化，不推荐。",
  ],
  params=[("原理","离子交换树脂置换 Ca²⁺/Mg²⁺"),("安装位置","地堡侧，软水管入卫生间"),("耗材","软水盐（定期再生）"),("体积","约 30×40×55cm + 盐箱"),("效果","镜面无水垢白斑·沐浴更丝滑")],
  taobao=[("淘宝·小型软水机","小型软水机离子交换"),("淘宝·进口","怡口软水机")],
  xianyu="软水机",
  warn="无盐“阻垢柔水器”（200-900 元）只是阻垢不是软化，对“镜面不结垢”这个硬需求效果弱——预算够就上真离子交换。"),

 dict(slug="heater", name="华为智联电热水器（60L）", tag="醒来即太阳", price="参考价 1,200-2,500 元",
  img="https://aka.doubaocdn.com/s/nKfWdGialR", cap="拆解原理图：搪瓷内胆 · 加热管 · 镁棒 · 保温层",
  paras=[
   "晨浴模式的“热水供应器”。<b>搪瓷内胆</b> + 加热管把 60L 水预热到设定温度（保温层锁热），<b>镁棒牺牲阳极</b>防内胆腐蚀（需定期更换）。",
   "鸿蒙智联款可被<b>华为智慧生活 App</b> 控制：晨起前远程预热，与浴霸、风机组成“晨浴场景”一键联动——人进卫生间即有 40°C 热水。",
   "60L 对两人连续洗足够；2000-3000W 大功率，需独立回路。",
  ],
  params=[("容量","60L"),("功率","2000-3000W（独立回路）"),("智联","鸿蒙智联 / 华为智慧生活 App"),("防腐蚀","镁棒 2-3 年一换"),("场景","晨浴场景远程预热")],
  taobao=[("淘宝·鸿蒙智联电热水器","鸿蒙智联电热水器"),("淘宝·生态款","华为智联电热水器")],
  xianyu="华为智联热水器",
  warn="必须认准“鸿蒙智联/华为智家”标识，收货后先试能否被 App 发现——能连上才是真智联；非生态款无法进“晨浴场景”。"),

 dict(slug="valve", name="恒温混水阀 + 冷冲档", tag="冷水收尾执行器", price="参考价 200-800 元",
  img="https://aka.doubaocdn.com/s/bsuvZwipEj", cap="拆解原理图：感温蜡包 · 冷热水进水 · 混合出水 · 调节阀芯",
  paras=[
   "晨浴序列“冷水收尾”的执行器。内部<b>感温蜡包</b>随混合水温热胀冷缩，自动微调冷热进水比例，出水恒定在设定温度——水温不漂、不怕烫。",
   "<b>冷冲档</b> = 把设定温度从 40°C 打到 ≈20°C，在 30s 内实现“冷水收尾”，激活交感神经完成晨浴的提神冲刺。",
   "带 40°C 防烫锁定 + 可外控款，才能接智能场景自动冷冲。",
  ],
  params=[("恒温原理","感温蜡包自动调节"),("设定范围","20-40°C（冷冲档≈20°C）"),("防烫锁","40°C"),("可外控","电磁/智能款支持"),("应用","晨浴 12-13min 冷水收尾")],
  taobao=[("淘宝·恒温混水阀","恒温混水阀"),("淘宝·可外控款","恒温混水阀 电磁")],
  xianyu="恒温混水阀",
  warn="选带 40°C 防烫锁定 + 可编程/外控的款式才能接智能冷冲；廉价款无锁温，水温会漂，冬季冷水冲击有风险。"),

 dict(slug="fan", name="变频静音排风扇（100mm）", tag="排气与保温平衡", price="参考价 200-600 元",
  img="https://aka.doubaocdn.com/s/fcgUtfSAeP", cap="拆解原理图：离心叶轮 · 直流无刷电机 · 止回阀 · 出风口",
  paras=[
   "“排气够用又安静”的平衡点。<b>离心叶轮 + 直流无刷电机</b>：150-200 m³/h 风量、80-150Pa 静压，三档变频（60/100/150 m³/h），淋浴高档排雾、平时低档保温。",
   "高档噪声 ≤33 dB(A)——风量满足 2㎡ 卫生间 15-20 次/h 换气的同时不吵。",
   "<b>止回阀叶片</b>防室外风倒灌并保温；静音关键在电机级数与叶片设计。",
  ],
  params=[("口径","100mm 管道风机"),("风量","150-200 m³/h"),("静压","80-150Pa"),("噪声","低/中/高 ≤28/31/33 dB(A)"),("功能","三档变频 + 止回阀 + 湿度联动"),("年耗电","≈40 kWh ≈¥25/年")],
  taobao=[("淘宝·变频静音管道排风扇","变频静音管道排风扇100mm"),("淘宝·大风轮静音","静音管道风机 100mm")],
  xianyu="管道风机 静音",
  warn="别买便宜轴流扇（噪声大、静压低）；管道每加 1 个弯头掉风量 15-30%，管路尽量短直；配湿度传感器做联动。"),

 dict(slug="led", name="可调色温 LED 面板（5000K 唤醒档）", tag="5000K 唤醒档", price="参考价 可调 300-900 / 固定 5000K 150-400 元",
  img="https://aka.doubaocdn.com/s/3WuVPddxSV", cap="拆解原理图：双色温灯珠(2700K+5000K) · 导光板 · 扩散板 · 驱动",
  paras=[
   "补上浴霸暖光“蓝光不足”的短板。<b>双色温灯珠（2700K + 5000K）</b>+ 导光板 + 扩散板：驱动按比例点亮两排灯珠，混出任意识别的色温。",
   "5000K 的“视黑素比”≈ <b>0.82</b>（暖光仅 0.45）——同照度下对生物钟的刺激近乎翻倍，是晨浴唤醒效率的“加速器”。",
   "晨间从暖光渐变到 5000K = 模拟“日出→正午”的晨光进程；晚间切回纯暖光保护睡眠。",
  ],
  params=[("功率/光通","20-30W / 2,000-3,000 lm"),("色温范围","2700-6500K（可调款）"),("显色指数","Ra ≥90"),("视黑素比","5000K ≈0.82"),("放置","眼平高度 + 扩散面板防眩光")],
  taobao=[("淘宝·可调色温平板灯","可调色温LED平板灯"),("淘宝·固定5000K","5000K平板灯")],
  xianyu="可调色温平板灯",
  warn="要 Ra≥90（显色指数），不然镜面里肤色失真；固定 5000K 已经够用，可调色温是“日出渐变”的锦上添花。"),

 dict(slug="curtain", name="门外遮光帘", tag="隐私方案（替代电控玻璃）", price="参考价 100-500 元",
  img="https://aka.doubaocdn.com/s/e9UawdEpT8", cap="拆解原理图：卷管 · 帘布面料 · 底杆配重 · 拉珠/电机",
  paras=[
   "灯箱核心是“门=出光口”，任何降低透光率的东西都是敌人——<b>电控玻璃透光仅≈80% 且贵（1,500-3,500 元/㎡）</b>，所以用门外拉帘。",
   "帘在<b>门外</b>、需要私密时才拉，玻璃门保持 90%+ 全透光，灯箱亮度一分不损；可换可洗、零故障。",
   "选半透纱帘时，灯箱光透过帘子还给地堡留一盏“发光窗帘”，夜里走路都省灯。",
  ],
  params=[("位置","玻璃门外侧"),("类型","遮光卷帘 / 半透纱帘"),("透光","门保持 ≥91%（帘不介入光路）"),("维护","可换可洗零故障"),("附带","半透纱帘=地堡“发光窗帘”")],
  taobao=[("淘宝·遮光卷帘","卫生间遮光卷帘"),("淘宝·半透纱帘","半透纱帘")],
  xianyu="卫生间卷帘",
  warn="尺寸按门框外沿量好再下单；若选电动卷帘，注意与智能家居的兼容协议（一般走 Zigbee/WiFi 窗帘电机）。"),

 dict(slug="boostpump", name="增压泵", tag="雨淋补压（可选）", price="参考价 200-800 元",
  img="https://aka.doubaocdn.com/s/FJ8Hwki5RZ", cap="拆解原理图：泵壳 · 离心叶轮 · 永磁电机 · 压力开关",
  paras=[
   "电热水器水压不足时的“补压器”。<b>离心叶轮</b>把低水压提升到 1.5-2.5 bar，让空气注入雨淋的混合腔充分吸气、出水更饱满。",
   "装于<b>地堡侧</b>（远离淋浴区）+ 软连接减震降噪，避免泵的嗡嗡声传进镜面盒子里。",
   "扬程选 0.8MPa 内够用即可，太大反而冲击管路、增加噪声。",
  ],
  params=[("原理","离心叶轮增压"),("出水压力","1.5-2.5 bar"),("扬程","≤0.8MPa 够用"),("安装","地堡侧 + 软连接"),("适用","电热水器水压不足时")],
  taobao=[("淘宝·家用增压泵","家用增压泵"),("淘宝·静音款","静音增压泵 变频")],
  xianyu="增压泵",
  warn="注意噪声与震动——别买直连式嗡嗡响的老款；选带压力开关自动启停的变频静音款。"),

 dict(slug="sump", name="污水提升泵", tag="地下排水必需", price="参考价 1,500-5,000 元",
  img="https://aka.doubaocdn.com/s/2t2OVzuJQv", cap="拆解原理图：集水箱 · 切割刀盘 · 叶轮 · 液位浮球 · 防回流阀",
  paras=[
   "地堡排水位低于市政管网时的“水泵站”。废水先汇入<b>集水箱</b>，液位浮球到点自动启动，<b>切割刀盘</b>把杂物打碎后，叶轮把污水提升到室外排水点。",
   "配<b>防回流阀</b>防止倒灌；2㎡ 卫生间用 300W 家用款足够。",
   "地下空间排水必需件——没有它，地堡的下水根本排不出去。",
  ],
  params=[("结构","集水箱 + 切割刀盘 + 叶轮"),("启停","液位浮球自动"),("防倒灌","防回流阀"),("功率","家用 300W 级"),("适用","排水位低于市政管网")],
  taobao=[("淘宝·污水提升泵","污水提升泵 家用"),("淘宝·带切割","污水提升泵 切割刀")],
  xianyu="污水提升泵",
  warn="必须选带<b>切割刀 + 防回流阀</b>的款；确认扬程能覆盖从地堡到室外排水点的落差，别买裸泵不带集水箱。"),

 dict(slug="dehumidifier", name="除湿机", tag="杭州冬季刚需", price="参考价 800-1,500 元",
  img="https://aka.doubaocdn.com/s/kEoN3N7CUL", cap="拆解原理图：压缩机 · 冷凝器 · 蒸发器 · 风机 · 集水水箱",
  paras=[
   "杭州冬季 RH 80%+ 的“湿度终结者”。<b>压缩制冷</b>把空气中水分在蒸发器冷凝成水收集（12L/天），配合浴霸烘干闭环，让镜面不起雾、地堡不返潮。",
   "对灯箱的意义：镜面起雾=反射率下降=灯箱变糊；除湿 + 排风扇是“镜面长期锃亮”的环境保障。",
   "放地堡中心、排水管接入地漏可免倒水；选噪声 ≤42dB 款。",
  ],
  params=[("原理","压缩制冷冷凝除湿"),("日除湿量","12L/天"),("放置","地堡中心"),("排水","接地漏免倒水"),("噪声","≤42dB")],
  taobao=[("淘宝·除湿机 12L","除湿机 12L"),("淘宝·静音款","静音除湿机")],
  xianyu="除湿机",
  warn="冬天除湿效率会随室温下降而打折，注意选低温除湿能力强的压缩机款；水箱与湿度传感器联动，别让水满停机误事。"),
]

NAV_TOTAL = len(HW)

def build(idx):
    h = HW[idx]
    prev = HW[(idx-1) % NAV_TOTAL] if idx > 0 else HW[NAV_TOTAL-1]
    nxt = HW[(idx+1) % NAV_TOTAL] if idx < NAV_TOTAL-1 else HW[0]
    paras = "\n".join("   <p>%s</p>" % p for p in h["paras"])
    params = "\n".join("<tr><td>%s</td><td>%s</td></tr>" % (k,v) for k,v in h["params"])
    tb = "\n".join('<a target="_blank" rel="noopener" href="https://s.taobao.com/search?q=%s"><b>%s</b><span>淘宝搜索直达 →</span></a>' % (q,label) for label,q in h["taobao"])
    page = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{h['name']} · 地堡灯箱卫生间硬件专题</title>
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
<nav class="top">
  <a href="__HUB__">← 硬件专题库</a>
  <a href="__OVERVIEW__">← 项目总览</a>
  <span class="spacer"></span>
  <a href="#buy">购买链接 ↓</a>
</nav>
<span class="tag">{h['tag']}</span>
<h1>{h['name']}</h1>
<p class="lead">地堡·灯箱卫生间 · 硬件专题页 {idx+1}/{NAV_TOTAL}</p>
<div class="price">{h['price']}</div>

<div class="fig"><img src="{h['img']}" alt="{h['name']}" loading="lazy"><div class="cap">{h['cap']}</div></div>

<h2>作用原理</h2>
{paras}

<h2>关键参数</h2>
<table>
<tbody>
{params}
</tbody>
</table>

<h2 id="buy">购买链接（淘宝 / 闲鱼）</h2>
<p>淘宝用下方搜索直达（关键词已预填）；闲鱼请在 App 内搜索 <b>“{h['xianyu']}”</b> 比价——同型号多店比价，按平米计价的务必先索样。</p>
<div class="buy">
{tb}
<a href="https://www.goofish.com" target="_blank" rel="noopener"><b>闲鱼搜索“{h['xianyu']}”</b><span>闲鱼 App 内搜索 →（官网/App 比价）</span></a>
</div>

<div class="warn">⚠️ 选购提醒：{h['warn']}</div>

<div class="nav2">
  <a href="__PREV__">← 上一件：{prev['name']}</a>
  <a class="next" href="__NEXT__">下一件：{nxt['name']} →</a>
</div>
<footer>地堡·灯箱卫生间 · 硬件专题库 · {h['name']}</footer>
</div>
</body>
</html>"""
    with open(os.path.join(OUT, h["slug"] + ".html"), "w", encoding="utf-8") as f:
        f.write(page)
    print("written:", h["slug"] + ".html")

if __name__ == "__main__":
    for i in range(NAV_TOTAL):
        build(i)
    print("total", NAV_TOTAL)
