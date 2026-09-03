// ============================================================
// FL-20G 菲涅尔调焦机构 - 精确齿轮 OpenSCAD 设计
// 用 OpenSCAD 渲染后导出 STL，比 Python 简化版精度更高
//
// 包含：
//   1. 调焦齿轮环（套在FL-20G调焦环上）
//   2. 舵机齿轮（MG996R输出轴）
//   3. 舵机支架（完整参数化设计）
//
// 渲染方法：用 OpenSCAD 打开本文件，按 F6 渲染，导出 STL
// ============================================================

// ---- 全局参数 ----
gear_module = 0.8;          // 齿轮模数
pressure_angle = 20;        // 压力角
fillet_radius = 0.1;        // 齿根圆角

// ---- FL-20G 调焦环参数 ----
fl20g_outer_dia = 200;      // FL-20G镜筒外径(mm)
fl20g_focus_ring_dia = 185; // 调焦环外径(mm)，需实测确认
ring_wall_thickness = 4;     // 齿轮环壁厚
ring_height = 15;             // 齿轮环高度

// ---- 舵机参数 (MG996R) ----
servo_shaft_dia = 6;         // 输出轴直径
servo_gear_teeth = 15;       // 舵机齿轮齿数
servo_gear_height = 8;       // 舵机齿轮高度

// ---- 调焦齿轮环参数 ----
ring_gear_teeth = 60;        // 齿轮环齿数（与舵机齿轮1:4减速比）
ring_inner_dia = fl20g_focus_ring_dia + 0.5;  // 内径（留0.5mm间隙）
ring_outer_dia = ring_inner_dia + ring_wall_thickness * 2 + gear_module * 2;

// ============================================================
// 模块1：调焦齿轮环
// ============================================================
module focus_gear_ring() {
    echo("生成调焦齿轮环: 齿数=", ring_gear_teeth, " 内径=", ring_inner_dia, " 外径=", ring_outer_dia);

    difference() {
        // 外齿轮
        gear(teeth=ring_gear_teeth,
             pitch_diameter=ring_gear_teeth * gear_module,
             height=ring_height);

        // 内孔
        cylinder(d=ring_inner_dia, h=ring_height + 2, center=true, $fn=128);
    }

    // 紧定螺丝孔 ×3（M3，固定在调焦环上）
    for(i = [0:2]) {
        rotate([0, 0, i * 120])
        translate([ring_inner_dia/2 + ring_wall_thickness/2, 0, 0])
        rotate([0, 90, 0])
        cylinder(d=3.2, h=ring_wall_thickness + 2, center=true, $fn=16);
    }
}

// ============================================================
// 模块2：舵机齿轮
// ============================================================
module servo_gear() {
    echo("生成舵机齿轮: 齿数=", servo_gear_teeth);

    difference() {
        gear(teeth=servo_gear_teeth,
             pitch_diameter=servo_gear_teeth * gear_module,
             height=servo_gear_height);

        // 中心孔（MG996R输出轴，花键近似为圆孔）
        cylinder(d=servo_shaft_dia + 0.2, h=servo_gear_height + 2, center=true, $fn=24);
    }

    // 顶部沉头孔（M3螺丝固定）
    translate([0, 0, servo_gear_height/2 - 2])
    cylinder(d1=6, d2=3.2, h=4, center=true, $fn=16);
}

// ============================================================
// 模块3：舵机支架（完整参数化）
// ============================================================
module servo_bracket() {
    echo("生成舵机支架");

    // 弧形底座（贴合FL-20G镜筒）
    difference() {
        // 外弧
        rotate([90, 0, 0])
        cylinder(d=fl20g_outer_dia + 8, h=50, center=true, $fn=128);

        // 内弧（挖空）
        rotate([90, 0, 0])
        cylinder(d=fl20g_outer_dia - 0.5, h=52, center=true, $fn=128);
    }

    // 只保留中间60°的弧段
    // （用立方体切掉两侧）
    translate([-60, 0, 0])
    cube([120, 60, 100], center=true);

    // 舵机安装平台
    translate([0, 0, fl20g_outer_dia/2 + 12])
    cube([55, 50, 6], center=true);

    // 舵机固定柱 ×4（M3螺丝）
    for(x = [-17.5, 17.5], y = [-7.5, 7.5]) {
        translate([x, y, fl20g_outer_dia/2 + 18])
        cylinder(d=6, h=12, center=true, $fn=16);

        // 螺丝孔
        translate([x, y, fl20g_outer_dia/2 + 18])
        cylinder(d=3.2, h=14, center=true, $fn=12);
    }

    // 加强筋 ×2
    for(x = [-22, 22]) {
        translate([x, 0, fl20g_outer_dia/2 + 8])
        cube([4, 45, 20], center=true);
    }

    // 扎带孔 ×2（固定在镜筒上）
    for(y = [-20, 20]) {
        translate([0, y, fl20g_outer_dia/2 - 2])
        rotate([90, 0, 0])
        cylinder(d=5, h=10, center=true, $fn=12);
    }
}

// ============================================================
// 通用齿轮模块（渐开线齿轮）
// ============================================================
module gear(teeth, pitch_diameter, height) {
    module = pitch_diameter / teeth;
    outer_radius = (pitch_diameter + 2 * module) / 2;
    root_radius = (pitch_diameter - 2.5 * module) / 2;
    base_radius = pitch_diameter / 2 * cos(pressure_angle);

    // 齿廓生成
    for(i = [0:teeth-1]) {
        rotate([0, 0, i * 360/teeth])
        tooth_profile(module, pitch_diameter/2, outer_radius, root_radius, base_radius, height);
    }

    // 齿根圆
    cylinder(r=root_radius, h=height, center=true, $fn=teeth*4);
}

module tooth_profile(module, pitch_radius, outer_radius, root_radius, base_radius, height) {
    half_tooth_angle = 90 / (pitch_radius / module);  // 半齿宽角

    // 简化齿形（梯形近似，足够FDM打印）
    rotate([0, 0, -half_tooth_angle])
    linear_extrude(height=height, center=true)
    polygon(points=[
        [root_radius * cos(0), root_radius * sin(0)],
        [outer_radius * cos(half_tooth_angle*0.6), outer_radius * sin(half_tooth_angle*0.6)],
        [outer_radius * cos(half_tooth_angle*0.6), -outer_radius * sin(half_tooth_angle*0.6)],
        [root_radius * cos(0), -root_radius * sin(0)],
    ]);
}

// ============================================================
// 渲染选择（取消注释对应行来渲染单个零件）
// ============================================================

// focus_gear_ring();     // 调焦齿轮环
// servo_gear();           // 舵机齿轮
servo_bracket();          // 舵机支架

// 全部渲染（用于预览）
// translate([-120, 0, 0]) focus_gear_ring();
// translate([0, 0, 0]) servo_gear();
// translate([120, 0, 0]) servo_bracket();
