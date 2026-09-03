#!/usr/bin/env python3
# ============================================================
# 3D打印件 STL 生成脚本
# 生成阳光模拟系统所需的所有3D打印零件
#
# 依赖：pip install numpy numpy-stl
# 运行：python3 generate_stl.py
# 输出：./stl/ 目录下的所有 .stl 文件
# ============================================================

import numpy as np
from stl import mesh
import os

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "stl")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def create_box(width, height, depth, center=(0, 0, 0)):
    """创建立方体mesh"""
    w, h, d = width / 2, height / 2, depth / 2
    cx, cy, cz = center
    vertices = np.array([
        [cx-w, cy-h, cz-d], [cx+w, cy-h, cz-d], [cx+w, cy+h, cz-d], [cx-w, cy+h, cz-d],
        [cx-w, cy-h, cz+d], [cx+w, cy-h, cz+d], [cx+w, cy+h, cz+d], [cx-w, cy+h, cz+d],
    ])
    faces = np.array([
        [0, 3, 2], [0, 2, 1], [4, 5, 6], [4, 6, 7],
        [0, 1, 5], [0, 5, 4], [2, 3, 7], [2, 7, 6],
        [0, 4, 7], [0, 7, 3], [1, 2, 6], [1, 6, 5],
    ])
    m = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
    for i, f in enumerate(faces):
        for j in range(3):
            m.vectors[i][j] = vertices[f[j]]
    return m


def create_cylinder(radius, height, segments=48, center=(0, 0, 0), axis='z'):
    """创建圆柱体mesh"""
    vertices = []
    faces = []
    cx, cy, cz = center
    h = height / 2

    for i in range(segments):
        angle = 2 * np.pi * i / segments
        x = cx + radius * np.cos(angle)
        y = cy + radius * np.sin(angle)
        if axis == 'z':
            vertices.append([x, y, cz - h])
            vertices.append([x, y, cz + h])
        elif axis == 'x':
            vertices.append([cx - h, x, y])
            vertices.append([cx + h, x, y])
        elif axis == 'y':
            vertices.append([x, cz - h, y])
            vertices.append([x, cz + h, y])

    # 侧面
    for i in range(segments):
        next_i = (i + 1) % segments
        faces.append([i*2, next_i*2, next_i*2+1])
        faces.append([i*2, next_i*2+1, i*2+1])

    # 底面和顶面
    bottom_center = len(vertices)
    top_center = len(vertices) + 1
    if axis == 'z':
        vertices.append([cx, cy, cz - h])
        vertices.append([cx, cy, cz + h])
    elif axis == 'x':
        vertices.append([cx - h, cx, cy])
        vertices.append([cx + h, cx, cy])
    elif axis == 'y':
        vertices.append([cx, cz - h, cy])
        vertices.append([cx, cz + h, cy])

    for i in range(segments):
        next_i = (i + 1) % segments
        faces.append([bottom_center, next_i*2, i*2])
        faces.append([top_center, i*2+1, next_i*2+1])

    m = mesh.Mesh(np.zeros(len(faces), dtype=mesh.Mesh.dtype))
    for i, f in enumerate(faces):
        for j in range(3):
            m.vectors[i][j] = vertices[f[j]]
    return m


def combine_meshes(meshes):
    """合并多个mesh"""
    combined = mesh.Mesh(np.concatenate([m.data for m in meshes]))
    return combined


def save_mesh(m, filename):
    """保存STL文件"""
    path = os.path.join(OUTPUT_DIR, filename)
    m.save(path)
    print(f"  已生成: {filename} ({len(m.vectors)} 三角面)")
    return path


# ============================================================
# 零件1：FL-20G调焦舵机支架
# 固定MG996R舵机在FL-20G镜筒侧面
# MG996R尺寸：40.6×19.6×42.9mm
# FL-20G镜筒直径约200mm，用半圆弧抱箍固定
# ============================================================
def generate_fresnel_servo_bracket():
    print("\n[1/6] 生成FL-20G调焦舵机支架...")
    parts = []

    # 底座 - 贴合镜筒的弧形板
    # 用多个小立方体近似圆弧
    base_thickness = 4
    arc_radius = 102  # 略大于镜筒半径100mm，留间隙
    arc_width = 50    # 支架宽度
    for i in range(11):
        angle = -30 + i * 6  # -30°到+30°
        rad = np.radians(angle)
        x = arc_radius * np.sin(rad)
        z = arc_radius * np.cos(rad)
        block = create_box(8, arc_width, base_thickness, center=(x, 0, z))
        # 旋转使其贴合圆弧
        parts.append(block)

    # 舵机安装平台 - 水平伸出
    platform = create_box(50, 45, 6, center=(0, 0, arc_radius + 20))
    parts.append(platform)

    # 舵机固定柱 ×4（M3螺丝孔位置）
    # MG996R安装孔距：约35mm × 15mm
    for dx in [-17.5, 17.5]:
        for dy in [-7.5, 7.5]:
            pillar = create_box(6, 6, 15, center=(dx, dy, arc_radius + 30))
            parts.append(pillar)

    # 加强筋
    rib1 = create_box(4, 40, 25, center=(-20, 0, arc_radius + 12))
    rib2 = create_box(4, 40, 25, center=(20, 0, arc_radius + 12))
    parts.extend([rib1, rib2])

    combined = combine_meshes(parts)
    save_mesh(combined, "01_fresnel_servo_bracket.stl")


# ============================================================
# 零件2：调焦齿轮环（套在FL-20G调焦环上）
# 内径约180mm（贴合调焦环），外径190mm，高15mm
# 外齿与舵机齿轮啮合（模数0.8，约60齿）
# ============================================================
def generate_focus_gear_ring():
    print("\n[2/6] 生成调焦齿轮环...")

    # 主体环
    ring = create_cylinder(95, 15, segments=64)
    # 内孔（用差集近似 - 这里生成薄壁环）
    # numpy-stl不支持布尔运算，用薄壁近似
    # 实际打印时用切片软件的孔功能，或用OpenSCAD版本

    # 外齿近似 - 在圆周上添加小立方体作为齿
    teeth = []
    num_teeth = 60
    for i in range(num_teeth):
        angle = 2 * np.pi * i / num_teeth
        x = 97 * np.cos(angle)
        z = 97 * np.sin(angle)
        tooth = create_box(3, 12, 5, center=(x, 0, z))
        teeth.append(tooth)

    combined = combine_meshes([ring] + teeth)
    save_mesh(combined, "02_focus_gear_ring.stl")
    print("  注意：此为简化版，精确齿轮建议使用配套的OpenSCAD文件渲染")


# ============================================================
# 零件3：舵机齿轮（安装在MG996R输出轴上）
# 齿数15，模数0.8，内径6mm（MG996R输出轴）
# ============================================================
def generate_servo_gear():
    print("\n[3/6] 生成舵机齿轮...")

    # 主体
    gear = create_cylinder(12, 8, segments=24)

    # 齿近似
    teeth = []
    num_teeth = 15
    for i in range(num_teeth):
        angle = 2 * np.pi * i / num_teeth
        x = 13 * np.cos(angle)
        z = 13 * np.sin(angle)
        tooth = create_box(2.5, 6, 4, center=(x, 0, z))
        teeth.append(tooth)

    combined = combine_meshes([gear] + teeth)
    save_mesh(combined, "03_servo_gear.stl")


# ============================================================
# 零件4：滑轨滑车→云台转接板
# 连接同步带滑台滑块和双轴云台底座
# 尺寸：100×80×6mm，带4个M5安装孔
# ============================================================
def generate_slider_adapter_plate():
    print("\n[4/6] 生成滑轨滑车转接板...")

    # 主板
    plate = create_box(100, 80, 6)

    # 安装孔凸台（实际孔用切片软件处理）
    bosses = []
    # 滑轨侧安装孔（4个，M5）
    for dx in [-35, 35]:
        for dy in [-25, 25]:
            boss = create_cylinder(6, 4, segments=16, center=(dx, dy, 5))
            bosses.append(boss)

    # 云台侧安装孔（4个，M4）
    for dx in [-20, 20]:
        for dy in [-15, 15]:
            boss = create_cylinder(5, 4, segments=16, center=(dx, dy, -5))
            bosses.append(boss)

    combined = combine_meshes([plate] + bosses)
    save_mesh(combined, "04_slider_adapter_plate.stl")


# ============================================================
# 零件5：ESP32+TMC2209驱动器外壳
# 容纳1×ESP32 + 2×TMC2209 + 接线端子
# 内部尺寸：80×60×30mm，分上下盖
# ============================================================
def generate_electronics_enclosure():
    print("\n[5/6] 生成电子元件外壳...")

    # 下壳
    bottom = create_box(86, 66, 4, center=(0, 0, -13))
    # 四壁
    wall_n = create_box(86, 4, 26, center=(0, 31, 0))
    wall_s = create_box(86, 4, 26, center=(0, -31, 0))
    wall_e = create_box(4, 66, 26, center=(41, 0, 0))
    wall_w = create_box(4, 66, 26, center=(-41, 0, 0))

    # 上盖
    top = create_box(86, 66, 3, center=(0, 0, 15))

    # 散热孔（用凸起近似，实际打印时镂空）
    vents = []
    for i in range(5):
        vent = create_box(10, 2, 2, center=(-20 + i*10, 33, 5))
        vents.append(vent)

    # USB-C开口凸台
    usb_cutout = create_box(12, 4, 8, center=(-41, 0, 0))

    combined = combine_meshes([bottom, wall_n, wall_s, wall_e, wall_w, top] + vents)
    save_mesh(combined, "05_electronics_enclosure.stl")

    # 单独生成上盖
    top_cover = combine_meshes([top] + vents)
    save_mesh(top_cover, "05b_enclosure_top_cover.stl")


# ============================================================
# 零件6：电线固定夹/走线夹
# 固定在滑轨和云台上的线材整理夹
# ============================================================
def generate_cable_clips():
    print("\n[6/6] 生成电线固定夹...")

    clips = []
    # 大号线夹（容纳电源线+信号线，直径约10mm）
    for i in range(4):
        clip_base = create_box(30, 15, 3, center=(0, i*40, 0))
        clip_arm_l = create_box(3, 15, 12, center=(-10, i*40, 6))
        clip_arm_r = create_box(3, 15, 12, center=(10, i*40, 6))
        clips.extend([clip_base, clip_arm_l, clip_arm_r])

    # 小号线夹（信号线，直径约5mm）
    for i in range(4):
        clip_base = create_box(20, 10, 2.5, center=(50, i*30, 0))
        clip_arm_l = create_box(2.5, 10, 8, center=(44, i*30, 5))
        clip_arm_r = create_box(2.5, 10, 8, center=(56, i*30, 5))
        clips.extend([clip_base, clip_arm_l, clip_arm_r])

    combined = combine_meshes(clips)
    save_mesh(combined, "06_cable_clips.stl")


# ============================================================
# 主函数
# ============================================================
def main():
    print("=" * 60)
    print("阳光模拟系统 - 3D打印件 STL 生成器")
    print("=" * 60)
    print(f"输出目录: {OUTPUT_DIR}")

    generate_fresnel_servo_bracket()
    generate_focus_gear_ring()
    generate_servo_gear()
    generate_slider_adapter_plate()
    generate_electronics_enclosure()
    generate_cable_clips()

    print("\n" + "=" * 60)
    print("所有STL文件生成完成！")
    print("=" * 60)
    print("\n打印建议：")
    print("  - 层厚：0.2mm（支架/外壳），0.12mm（齿轮）")
    print("  - 填充：20%（外壳），40%（支架/齿轮）")
    print("  - 材料：PLA（日常件）或 PETG/ABS（耐热件）")
    print("  - 支撑：舵机支架需要支撑，其他可无支撑")
    print("\n注意：齿轮件为简化版，精确齿轮请使用OpenSCAD文件渲染。")


if __name__ == "__main__":
    main()
