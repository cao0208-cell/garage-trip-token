#!/usr/bin/env python3
"""Render car-side and home-side circuit diagrams."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT = Path("/workspace/garage-trip-token-oss/docs/images")
REG = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
SC = 2
BG = (8, 22, 30)
CARD = (16, 40, 50)
LINE = (42, 86, 98)
TEAL = (45, 212, 150)
TEAL_DIM = (24, 140, 100)
TEAL_BG = (16, 70, 58)
WHITE = (244, 250, 252)
MUTED = (156, 186, 196)
SOFT = (110, 142, 152)
ORANGE = (245, 158, 66)
BLUE = (86, 170, 230)
PURPLE = (168, 140, 230)
GOLD = (232, 201, 112)
RED = (232, 120, 100)


def font(size, bold=False):
    return ImageFont.truetype(BOLD if bold else REG, size, index=SC)


def rounded(base, box, radius, fill, outline=None, width=2, shadow=True):
    x0, y0, x1, y1 = box
    if shadow:
        sh = Image.new("RGBA", base.size, (0, 0, 0, 0))
        sd = ImageDraw.Draw(sh)
        sd.rounded_rectangle((x0 + 5, y0 + 7, x1 + 5, y1 + 7), radius=radius, fill=(0, 0, 0, 70))
        base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(7)))
    d = ImageDraw.Draw(base)
    d.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def canvas(w, h):
    img = Image.new("RGBA", (w, h), (*BG, 255))
    ov = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    for i in range(h):
        od.line((0, i, w, i), fill=(0, 18, 24, int(40 * i / h)))
    img.alpha_composite(ov)
    blob = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    bd = ImageDraw.Draw(blob)
    bd.ellipse((-200, -160, 400, 340), fill=(*TEAL_DIM, 26))
    bd.ellipse((w - 460, h - 300, w + 140, h + 180), fill=(20, 80, 110, 34))
    img.alpha_composite(blob)
    return img


def text_w(draw, text, f):
    b = draw.textbbox((0, 0), text, font=f)
    return b[2] - b[0]


def wrap(draw, text, f, max_w):
    lines, cur = [], ""
    for ch in text:
        trial = cur + ch
        if text_w(draw, trial, f) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = ch
    if cur:
        lines.append(cur)
    return lines or [""]


def footer(d, img, lines, fill, outline, y0=1020, y1=1236):
    d.rounded_rectangle((80, y0, 1840, y1), radius=22, fill=fill, outline=outline, width=2)
    yy = y0 + 24
    f = font(23)
    for para in lines:
        for line in wrap(d, para, f, 1680):
            d.text((110, yy), line, font=f, fill=WHITE)
            yy += 36
        yy += 6


def title(d, text, sub):
    d.text((80, 44), text, font=font(48, True), fill=WHITE)
    d.text((80, 112), sub, font=font(26), fill=MUTED)
    d.rounded_rectangle((80, 158, 360, 166), radius=4, fill=TEAL)


def pin(d, x, y, w, h, name, note, color=TEAL):
    d.rounded_rectangle((x, y, x + w, y + h), radius=12, fill=(12, 32, 40), outline=color, width=2)
    d.text((x + 16, y + 10), name, font=font(22, True), fill=color)
    if note:
        d.text((x + 16, y + 40), note, font=font(18), fill=MUTED)


def wire(d, pts, color=TEAL, width=4):
    d.line(pts, fill=color, width=width)
    # endpoints
    for (x, y) in (pts[:2], pts[-2:]):
        pass
    d.ellipse((pts[0] - 5, pts[1] - 5, pts[0] + 5, pts[1] + 5), fill=color)
    d.ellipse((pts[-2] - 5, pts[-1] - 5, pts[-2] + 5, pts[-1] + 5), fill=color)


def antenna(d, cx, cy, color=PURPLE):
    # simple whip antenna
    d.line((cx, cy, cx, cy - 36), fill=color, width=3)
    for i, r in enumerate((14, 22, 30)):
        d.arc((cx - r, cy - 36 - r, cx + r, cy - 36 + r), start=210, end=330, fill=color, width=3)


def render_car():
    w, h = 1920, 1280
    img = canvas(w, h)
    d = ImageDraw.Draw(img)
    title(d, "车载端电路  ·  微雪 ESP32-S3-RS485-CAN", "车库功能只从车辆 CAN 总线读取车速，不为开门向车辆发送报文。RS485 端子不使用。")

    # Vehicle box
    rounded(img, (80, 210, 520, 980), 28, (*CARD, 255), LINE, 2)
    d = ImageDraw.Draw(img)
    d.text((120, 236), "车辆侧", font=font(32, True), fill=WHITE)
    d.text((120, 284), "车上的内部通信网络", font=font(22), fill=MUTED)
    d.text((120, 312), "CAN 总线（约 500 kbps）", font=font(22), fill=MUTED)

    rounded(img, (120, 380, 480, 560), 20, (12, 32, 40, 255), ORANGE, 2)
    d = ImageDraw.Draw(img)
    d.text((150, 410), "车辆 CAN 总线", font=font(28, True), fill=ORANGE)
    d.text((150, 460), "CAN-H  高速差分 +", font=font(24), fill=WHITE)
    d.text((150, 504), "CAN-L  高速差分 −", font=font(24), fill=WHITE)

    rounded(img, (120, 600, 480, 760), 20, (12, 32, 40, 255), GOLD, 2)
    d = ImageDraw.Draw(img)
    d.text((150, 628), "车载电源", font=font(28, True), fill=GOLD)
    d.text((150, 678), "常电 / 附件电  12V 级", font=font(24), fill=WHITE)
    d.text((150, 716), "建议 7–36V 端子接入", font=font(22), fill=MUTED)

    d.text((120, 800), "本项目在车辆上只听不写：", font=font(24, True), fill=TEAL)
    d.text((120, 848), "读取实时车速信号", font=font(24), fill=WHITE)
    d.text((120, 890), "累计前进行驶距离", font=font(24), fill=WHITE)
    d.text((120, 932), "不发送开门相关报文", font=font(24), fill=WHITE)

    # Board box
    rounded(img, (640, 210, 1280, 980), 28, (*CARD, 255), TEAL, 3)
    d = ImageDraw.Draw(img)
    d.text((680, 236), "微雪 ESP32-S3-RS485-CAN", font=font(32, True), fill=WHITE)
    d.text((680, 284), "车载板  ·  16MB Flash", font=font(22), fill=MUTED)

    # CAN transceiver
    rounded(img, (680, 350, 1020, 530), 18, (12, 32, 40, 255), TEAL, 2)
    d = ImageDraw.Draw(img)
    d.text((700, 368), "板载 CAN 收发器", font=font(24, True), fill=TEAL)
    d.text((700, 412), "端子：CAN-H、CAN-L", font=font(22), fill=WHITE)
    d.text((700, 450), "片内 TWAI 控制器", font=font(22), fill=WHITE)
    d.text((700, 488), "TX GPIO15  /  RX GPIO16", font=font(20), fill=MUTED)

    # MCU
    rounded(img, (680, 560, 1240, 780), 18, (12, 32, 40, 255), BLUE, 2)
    d = ImageDraw.Draw(img)
    d.text((700, 580), "ESP32-S3 主控", font=font(24, True), fill=BLUE)
    d.text((700, 624), "固件：只读车速  →  累计 500 米  →  生成行程号", font=font(22), fill=WHITE)
    d.text((700, 666), "低优先级蓝牙任务负责广播，不占用 CAN 主循环写存储", font=font(20), fill=MUTED)
    d.text((700, 708), "车库逻辑不调用向车辆发送的 CAN 发送函数", font=font(20), fill=MUTED)
    d.text((700, 744), "RS485 A+/B−  本项目不接线", font=font(20), fill=ORANGE)

    # Power on board
    rounded(img, (680, 810, 1020, 930), 18, (12, 32, 40, 255), GOLD, 2)
    d = ImageDraw.Draw(img)
    d.text((700, 828), "供电", font=font(24, True), fill=GOLD)
    d.text((700, 870), "7–36V 电源端子  优先", font=font(22), fill=WHITE)
    d.text((700, 900), "Type-C  可用于刷写 / 调试", font=font(20), fill=MUTED)

    # BLE radio
    rounded(img, (1060, 350, 1240, 530), 18, (12, 32, 40, 255), PURPLE, 2)
    d = ImageDraw.Draw(img)
    d.text((1080, 372), "BLE 射频", font=font(24, True), fill=PURPLE)
    d.text((1080, 420), "非连接广播", font=font(22), fill=WHITE)
    d.text((1080, 456), "约 200ms 一次", font=font(20), fill=MUTED)
    d.text((1080, 488), "同一行程号", font=font(20), fill=MUTED)
    antenna(d, 1210, 360, PURPLE)

    # Wires vehicle CAN to board
    d = ImageDraw.Draw(img)
    wire(d, [480, 460, 680, 460], ORANGE, 5)
    d.text((500, 420), "CAN-H / CAN-L", font=font(20, True), fill=ORANGE)
    wire(d, [480, 680, 560, 680, 560, 870, 680, 870], GOLD, 5)
    d.text((500, 640), "7–36V 与共地", font=font(20, True), fill=GOLD)

    # Home side receive
    rounded(img, (1400, 210, 1840, 980), 28, (*CARD, 255), LINE, 2)
    d = ImageDraw.Draw(img)
    d.text((1440, 236), "发往室内", font=font(32, True), fill=WHITE)
    d.text((1440, 284), "不是电线，是蓝牙无线电", font=font(22), fill=MUTED)

    rounded(img, (1440, 360, 1800, 700), 20, (16, 70, 58, 255), TEAL, 2)
    d = ImageDraw.Draw(img)
    antenna(d, 1620, 420, TEAL)
    d.text((1480, 470), "蓝牙行程码", font=font(28, True), fill=TEAL)
    d.text((1480, 524), "满 500 米后才开始广播", font=font(22), fill=WHITE)
    d.text((1480, 566), "身份认证 + 一次性行程号", font=font(22), fill=WHITE)
    d.text((1480, 608), "室内 ESP32-C3 接收", font=font(22), fill=WHITE)
    d.text((1480, 650), "同一趟只开一次门", font=font(22), fill=WHITE)

    d.text((1440, 740), "接线要点", font=font(24, True), fill=TEAL)
    d.text((1440, 788), "CAN 只要 H、L 和共地", font=font(22), fill=WHITE)
    d.text((1440, 828), "不要把电机或 220V 接到板子", font=font(22), fill=WHITE)
    d.text((1440, 868), "刷写建议只写应用区 0x10000", font=font(22), fill=WHITE)
    d.text((1440, 908), "以保留引导程序和分区表", font=font(22), fill=MUTED)

    # arrow from BLE to right box
    wire(d, [1240, 430, 1400, 430], PURPLE, 5)
    d.text((1260, 392), "空中广播", font=font(20, True), fill=PURPLE)

    footer(d, img, [
        "读法很简单：车上的 CAN-H、CAN-L 是一对差分信号线，相当于车辆内部的“对话总线”。这块开发板把这路总线接进来，由固件只读车速，再在空中发出行程码。",
        "很多人已经在用 ESP32-S3 CAN 板连接特斯拉的这路接口。本方案要扩展的，不是再去操作车辆功能，而是在“已经能读到车速”的前提上，给家里的卷帘门增加一次可信的自动开门。",
        "注意：不同车型的取电点和 CAN 接入点并不相同，接线前必须核对自己的车型与供电方式，并断开大电流负载。本图只描述本项目使用的接口，不是通用改装手册。",
    ], TEAL_BG, TEAL)

    img.convert("RGB").save(OUT / "circuit-car.png", "PNG", optimize=True)
    print("wrote circuit-car.png")


def render_home():
    w, h = 1920, 1280
    img = canvas(w, h)
    d = ImageDraw.Draw(img)
    title(d, "室内端电路  ·  ESP32-C3 + T3A 433MHz", "室内模块收到合法行程码后，只打出 300ms 高电平脉冲。K1 悬空，不接线。")

    # BLE in
    rounded(img, (80, 210, 460, 560), 28, (*CARD, 255), PURPLE, 2)
    d = ImageDraw.Draw(img)
    antenna(d, 270, 280, PURPLE)
    d.text((120, 320), "来自车载板", font=font(26, True), fill=PURPLE)
    d.text((120, 368), "蓝牙行程码广播", font=font(24), fill=WHITE)
    d.text((120, 412), "非连接接收", font=font(22), fill=MUTED)
    d.text((120, 452), "校验身份与行程号", font=font(22), fill=MUTED)
    d.text((120, 492), "同一行程只消费一次", font=font(22), fill=MUTED)

    # ESP32-C3
    rounded(img, (560, 210, 1180, 980), 28, (*CARD, 255), TEAL, 3)
    d = ImageDraw.Draw(img)
    d.text((600, 236), "室内 ESP32-C3 SuperMini", font=font(32, True), fill=WHITE)
    d.text((600, 284), "4MB Flash  ·  DIO  ·  40MHz  ·  蓝牙名 Garage-C3-BLE", font=font(22), fill=MUTED)

    rounded(img, (600, 350, 1140, 500), 18, (12, 32, 40, 255), BLUE, 2)
    d = ImageDraw.Draw(img)
    d.text((620, 368), "主控固件", font=font(24, True), fill=BLUE)
    d.text((620, 412), "行程码门闩  ·  认证  ·  防重放  ·  脉冲输出", font=font(22), fill=WHITE)
    d.text((620, 450), "自动关门功能永久关闭", font=font(22), fill=MUTED)

    # power
    rounded(img, (600, 530, 860, 650), 16, (12, 32, 40, 255), GOLD, 2)
    d = ImageDraw.Draw(img)
    d.text((620, 548), "供电  3.3V", font=font(22, True), fill=GOLD)
    d.text((620, 588), "与 T3A 共地", font=font(20), fill=WHITE)
    d.text((620, 616), "禁止 5V / 12V 进 GPIO", font=font(18), fill=ORANGE)

    # gpios
    gpios = [
        ("GPIO4", "开门脉冲 300ms", TEAL),
        ("GPIO6", "停止脉冲 300ms", ORANGE),
        ("GPIO5", "关门脉冲 300ms", ORANGE),
    ]
    y = 680
    for name, note, col in gpios:
        rounded(img, (600, y, 1140, y + 80), 14, (12, 32, 40, 255), col, 2)
        d = ImageDraw.Draw(img)
        d.text((624, y + 22), name, font=font(26, True), fill=col)
        d.text((820, y + 24), note, font=font(24), fill=WHITE)
        y += 96

    # T3A
    rounded(img, (1280, 210, 1840, 980), 28, (*CARD, 255), LINE, 2)
    d = ImageDraw.Draw(img)
    d.text((1320, 236), "T3A 固定码发射模块", font=font(32, True), fill=WHITE)
    d.text((1320, 284), "必须 3.3V 供电 / 高电平触发版本", font=font(22), fill=MUTED)

    pairs = [
        ("VCC", "接 ESP32 3.3V", GOLD),
        ("GND", "接 ESP32 GND", GOLD),
        ("K0", "接 GPIO4  开门", TEAL),
        ("K2", "接 GPIO6  停止", ORANGE),
        ("K3", "接 GPIO5  关门", ORANGE),
        ("K1", "保持悬空  不接线", RED),
    ]
    y = 340
    for name, note, col in pairs:
        rounded(img, (1320, y, 1800, y + 70), 14, (12, 32, 40, 255), col, 2)
        d = ImageDraw.Draw(img)
        d.text((1344, y + 18), name, font=font(26, True), fill=col)
        d.text((1480, y + 20), note, font=font(22), fill=WHITE)
        y += 82

    # 433 out
    rounded(img, (1320, 850, 1800, 940), 16, (16, 70, 58, 255), TEAL, 2)
    d = ImageDraw.Draw(img)
    antenna(d, 1760, 880, TEAL)
    d.text((1344, 872), "433MHz 固定码  →  卷帘门接收器", font=font(22, True), fill=WHITE)

    # wires from C3 to T3A conceptually
    d = ImageDraw.Draw(img)
    wire(d, [1180, 420, 1280, 420], TEAL, 5)
    d.text((1190, 382), "短导线", font=font(20, True), fill=TEAL)
    wire(d, [460, 360, 560, 360], PURPLE, 5)

    footer(d, img, [
        "电路约束：T3A 与 ESP32-C3 必须共地，且都工作在 3.3V 逻辑。不要把卷帘门电机线、交流电或 12V 遥控线直接接到 ESP32 的引脚。",
        "输出形态：开、停、关都是单次 300ms 脉冲，到时自动拉低，不持续占用 433MHz。系统不知道门现在是开还是关，测试时请让门停在行程中途，并保持物理停止按钮可用。",
        "电源建议：室内接收器用稳定的 USB 5V 经板上稳压到 3.3V，避免和车库照明或电机启动共用一条会跌落的线路，减少“停电后再上电”带来的异常。",
    ], (70, 32, 28), RED)

    img.convert("RGB").save(OUT / "circuit-home.png", "PNG", optimize=True)
    print("wrote circuit-home.png")


if __name__ == "__main__":
    render_car()
    render_home()
