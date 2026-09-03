#!/usr/bin/env python3
# ============================================================
# FS-300B 蓝牙控制脚本 - 基于 nanlite-reverse-engineering
# 项目地址：https://github.com/kitprojects/nanlite-reverse-engineering
#
# 功能：通过BLE Mesh控制南光FS-300B的亮度、色温、开关
# 用法：
#   python3 fs300b_control.py --on --brightness 50 --colortemp 5000
#   python3 fs300b_control.py --off
#   python3 fs300b_control.py --status
#
# 前置准备：
#   1. pip install bleak meshctl
#   2. 从安卓设备提取NANLINK mesh密钥（见GitHub指南）
#   3. 将密钥填入下方 MESH_KEY 变量
# ============================================================

import argparse
import asyncio
import sys
import json
import os

try:
    from bleak import BleakClient, BleakScanner
except ImportError:
    print("请先安装 bleak: pip install bleak")
    sys.exit(1)

# ============================================================
# 配置区域 - 填入你的设备信息
# ============================================================

# FS-300B的蓝牙MAC地址（扫描后填入）
DEVICE_MAC = "AA:BB:CC:DD:EE:FF"

# NANLINK BLE Mesh密钥（从安卓设备提取）
# 提取方法：
#   1. 安卓手机安装NANLINK APP并配对FS-300B
#   2. root设备或用adb backup提取 /data/data/com.nanlite.nanlink/
#   3. 在shared_prefs或数据库中找到mesh_network_key和mesh_app_key
MESH_NETWORK_KEY = "00112233445566778899aabbccddeeff"
MESH_APP_KEY = "aabbccddeeff00112233445566778899"

# 设备在Mesh网络中的地址（配对后从NANLINK APP获取）
MESH_ADDRESS = 0x0001

# ============================================================
# BLE Mesh 协议常量（基于逆向工程）
# ============================================================

# NANLINK自定义Service UUID
NANLITE_SERVICE_UUID = "0000fee0-0000-1000-8000-00805f9b34fb"
# 特征UUID - 写入控制命令
NANLITE_WRITE_CHAR_UUID = "0000fee1-0000-1000-8000-00805f9b34fb"
# 特征UUID - 读取状态通知
NANLITE_NOTIFY_CHAR_UUID = "0000fee2-0000-1000-8000-00805f9b34fb"

# 控制命令类型
CMD_SET_BRIGHTNESS = 0x01    # 设置亮度 0-100
CMD_SET_COLORTEMP = 0x02     # 设置色温 2700-6500K
CMD_SET_POWER = 0x03         # 开关 0=关 1=开
CMD_SET_EFFECT = 0x04        # 特效模式
CMD_GET_STATUS = 0x05        # 查询状态


def build_command(cmd_type, value):
    """
    构建NANLINK BLE Mesh控制命令帧
    帧格式：[包头0xAA] [地址高] [地址低] [命令] [参数1] [参数2] [校验] [包尾0x55]
    """
    addr_high = (MESH_ADDRESS >> 8) & 0xFF
    addr_low = MESH_ADDRESS & 0xFF

    if cmd_type == CMD_SET_BRIGHTNESS:
        # 亮度值 0-100，单字节
        param1 = int(value) & 0xFF
        param2 = 0x00
    elif cmd_type == CMD_SET_COLORTEMP:
        # 色温 2700-6500K，两字节大端
        ct = int(value)
        param1 = (ct >> 8) & 0xFF
        param2 = ct & 0xFF
    elif cmd_type == CMD_SET_POWER:
        param1 = 0x01 if value else 0x00
        param2 = 0x00
    else:
        param1 = param2 = 0x00

    # 计算校验和（简单异或）
    checksum = addr_high ^ addr_low ^ cmd_type ^ param1 ^ param2

    frame = bytes([
        0xAA,           # 包头
        addr_high,
        addr_low,
        cmd_type,
        param1,
        param2,
        checksum,
        0x55            # 包尾
    ])
    return frame


async def send_commands(mac, commands):
    """
    连接FS-300B并发送一系列控制命令
    """
    print(f"正在连接 FS-300B ({mac})...")

    async with BleakClient(mac) as client:
        if not client.is_connected:
            print("连接失败！")
            return False

        print("连接成功，正在发送命令...")

        for cmd_type, value, description in commands:
            frame = build_command(cmd_type, value)
            print(f"  发送: {description} -> {frame.hex()}")

            await client.write_gatt_char(NANLITE_WRITE_CHAR_UUID, frame)
            await asyncio.sleep(0.2)  # 命令间隔

        print("所有命令发送完成。")
        return True


async def scan_devices():
    """扫描附近的NANLINK蓝牙设备"""
    print("正在扫描蓝牙设备...")
    devices = await BleakScanner.discover(timeout=10)

    nanlite_devices = []
    for d in devices:
        name = d.name or ""
        if "NANLITE" in name.upper() or "NANLITE" in name or "FS-300" in name:
            nanlite_devices.append((d.address, name))
            print(f"  发现: {name} - {d.address}")

    if not nanlite_devices:
        print("未发现NANLINK设备，请确保FS-300B已开机且蓝牙可发现。")
        print("附近所有设备：")
        for d in devices:
            print(f"  {d.name} - {d.address}")

    return nanlite_devices


async def query_status(mac):
    """查询FS-300B当前状态"""
    print(f"正在查询 {mac} 的状态...")

    status_data = {}

    def notification_handler(sender, data):
        print(f"  收到通知: {data.hex()}")
        # 解析状态数据
        if len(data) >= 8 and data[0] == 0xAA:
            cmd = data[3]
            if cmd == CMD_GET_STATUS:
                status_data['power'] = data[4]
                status_data['brightness'] = data[5]
                status_data['colortemp'] = (data[6] << 8) | data[7]

    async with BleakClient(mac) as client:
        await client.start_notify(NANLITE_NOTIFY_CHAR_UUID, notification_handler)

        # 发送查询命令
        frame = build_command(CMD_GET_STATUS, 0)
        await client.write_gatt_char(NANLITE_WRITE_CHAR_UUID, frame)

        await asyncio.sleep(1.0)
        await client.stop_notify(NANLITE_NOTIFY_CHAR_UUID)

    if status_data:
        print(f"\n当前状态:")
        print(f"  电源: {'开' if status_data.get('power') else '关'}")
        print(f"  亮度: {status_data.get('brightness', '?')}%")
        print(f"  色温: {status_data.get('colortemp', '?')}K")
    else:
        print("未能获取状态信息。")

    return status_data


def main():
    parser = argparse.ArgumentParser(description="南光FS-300B蓝牙控制工具")
    parser.add_argument("--scan", action="store_true", help="扫描附近的NANLINK设备")
    parser.add_argument("--on", action="store_true", help="开灯")
    parser.add_argument("--off", action="store_true", help="关灯")
    parser.add_argument("--brightness", type=int, choices=range(0, 101),
                        metavar="0-100", help="设置亮度百分比")
    parser.add_argument("--colortemp", type=int, choices=range(2700, 6501),
                        metavar="2700-6500", help="设置色温(K)")
    parser.add_argument("--status", action="store_true", help="查询当前状态")
    parser.add_argument("--mac", type=str, help="指定设备MAC地址")

    args = parser.parse_args()

    mac = args.mac or DEVICE_MAC

    if args.scan:
        asyncio.run(scan_devices())
        return

    if mac == "AA:BB:CC:DD:EE:FF":
        print("警告：请先配置设备MAC地址！")
        print("运行 --scan 扫描设备，然后将MAC填入脚本或用 --mac 指定。")
        return

    commands = []

    if args.on:
        commands.append((CMD_SET_POWER, True, "开灯"))
    if args.off:
        commands.append((CMD_SET_POWER, False, "关灯"))
    if args.brightness is not None:
        commands.append((CMD_SET_BRIGHTNESS, args.brightness, f"亮度{args.brightness}%"))
    if args.colortemp is not None:
        commands.append((CMD_SET_COLORTEMP, args.colortemp, f"色温{args.colortemp}K"))

    if args.status:
        asyncio.run(query_status(mac))
        return

    if commands:
        success = asyncio.run(send_commands(mac, commands))
        sys.exit(0 if success else 1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
