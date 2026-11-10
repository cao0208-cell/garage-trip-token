#!/usr/bin/env python3
"""Render open-source README diagrams for the garage trip-token V2 system."""
from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT = Path("/workspace/garage-trip-token-oss/docs/images")
OUT.mkdir(parents=True, exist_ok=True)

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
RED = (232, 120, 100)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(BOLD if bold else REG, size, index=SC)


def text_size(draw: ImageDraw.ImageDraw, text: str, f: ImageFont.FreeTypeFont):
    b = draw.textbbox((0, 0), text, font=f)
    return b[2] - b[0], b[3] - b[1]


def wrap(draw, text, f, max_w):
    lines, cur = [], ""
    for ch in text:
        trial = cur + ch
        if text_size(draw, trial, f)[0] <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = ch
    if cur:
        lines.append(cur)
    return lines or [""]


def rounded(base, box, radius, fill, outline=None, width=2, shadow=True):
    x0, y0, x1, y1 = box
    if shadow:
        shadow_img = Image.new("RGBA", base.size, (0, 0, 0, 0))
        sd = ImageDraw.Draw(shadow_img)
        sd.rounded_rectangle((x0 + 6, y0 + 8, x1 + 6, y1 + 8), radius=radius, fill=(0, 0, 0, 70))
        shadow_img = shadow_img.filter(ImageFilter.GaussianBlur(8))
        base.alpha_composite(shadow_img)
    d = ImageDraw.Draw(base)
    d.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def center_text(draw, cx, y, text, f, fill=WHITE, anchor="mt"):
    draw.text((cx, y), text, font=f, fill=fill, anchor=anchor)


def draw_arrow(draw, x0, y, x1, color=TEAL, shaft=6):
    if x1 - x0 < 28:
        return
    draw.line((x0, y, x1 - 16, y), fill=color, width=shaft)
    draw.polygon([(x1, y), (x1 - 22, y - 12), (x1 - 22, y + 12)], fill=color)


def new_canvas(w, h):
    img = Image.new("RGBA", (w, h), (*BG, 255))
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for i in range(h):
        a = int(40 * (i / h))
        od.line((0, i, w, i), fill=(0, 18, 24, a))
    img.alpha_composite(overlay)
    blob = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    bd = ImageDraw.Draw(blob)
    bd.ellipse((-200, -180, 420, 360), fill=(*TEAL_DIM, 28))
    bd.ellipse((w - 480, h - 320, w + 160, h + 200), fill=(20, 80, 110, 36))
    img.alpha_composite(blob)
    return img


def render_architecture():
    w, h = 1920, 1080
    img = new_canvas(w, h)
    d = ImageDraw.Draw(img)
    d.text((80, 48), "车库行程码自动开门  ·  系统架构", font=font(54, True), fill=WHITE)
    d.text((80, 122), "只读车速  ·  累计前进 500 米  ·  一次性蓝牙行程码  ·  室内短脉冲开门", font=font(28), fill=MUTED)
    d.rounded_rectangle((80, 168, 360, 176), radius=4, fill=TEAL)

    nodes = [
        ("1", "车辆", "只读实时车速", "不向车辆发送\n开门相关报文", ORANGE),
        ("2", "车载 ESP32-S3", "累计前进行驶距离", "满 500 米后生成\n行程号 tripSerial", BLUE),
        ("3", "低优先级蓝牙", "重复广播同一行程码", "约 200ms 一次\n室内端只消费一次", PURPLE),
        ("4", "室内 ESP32-C3", "身份与完整性校验", "新行程且已达\n500 米才开门", TEAL),
        ("5", "T3A 发射模块", "433MHz 固定码", "单次 300ms 脉冲\n永不持续占空", ORANGE),
        ("6", "卷帘门", "学习固定码后开启", "系统不知门的\n实际位置", TEAL),
    ]
    n = len(nodes)
    margin_l, margin_r = 70, 70
    gap = 22
    card_w = (w - margin_l - margin_r - gap * (n - 1)) // n
    card_h = 430
    top = 230
    edges = []
    for i, (num, name, lead, detail, color) in enumerate(nodes):
        x0 = margin_l + i * (card_w + gap)
        x1 = x0 + card_w
        y0, y1 = top, top + card_h
        rounded(img, (x0, y0, x1, y1), 28, (*CARD, 255), outline=LINE, width=2)
        d = ImageDraw.Draw(img)
        cx, cy = x0 + 48, y0 + 48
        d.ellipse((cx - 26, cy - 26, cx + 26, cy + 26), fill=color)
        center_text(d, cx, cy, num, font(28, True), fill=(8, 22, 30), anchor="mm")
        d.text((x0 + 86, y0 + 32), name, font=font(28, True), fill=WHITE)
        # lead may be long; wrap
        yy = y0 + 100
        for line in wrap(d, lead, font(24, True), card_w - 56):
            d.text((x0 + 28, yy), line, font=font(24, True), fill=TEAL)
            yy += 36
        d.line((x0 + 28, y0 + 180, x1 - 28, y0 + 180), fill=LINE, width=2)
        yy = y0 + 200
        for line in detail.split("\n"):
            d.text((x0 + 28, yy), line, font=font(24), fill=MUTED)
            yy += 40
        edges.append((x0, x1, y0, y1))

    d = ImageDraw.Draw(img)
    mid_y = top + card_h // 2
    for i in range(n - 1):
        draw_arrow(d, edges[i][1] + 1, mid_y, edges[i + 1][0] - 1, TEAL, shaft=5)

    principles = [
        ("安全原则", "用真实行驶距离证明“这是一趟出门后再回家”，而不是用蓝牙信号强弱去猜距离。"),
        ("开门方式", "室内模块只打出一次 300ms 脉冲；同一行程号写入本地后不会再用，也不会自动关门。"),
        ("公开边界", "开源介绍不包含配对密钥、默认口令，也不包含车机原有控制功能的实现。"),
    ]
    ptop = 730
    pw = (w - 80 * 2 - 36 * 2) // 3
    for i, (t, body) in enumerate(principles):
        x0 = 80 + i * (pw + 36)
        x1 = x0 + pw
        fill = TEAL_BG if i == 2 else CARD
        rounded(img, (x0, ptop, x1, 1020), 24, (*fill, 255), outline=TEAL if i == 2 else LINE, width=2)
        d = ImageDraw.Draw(img)
        d.text((x0 + 28, ptop + 24), t, font=font(28, True), fill=TEAL)
        yy = ptop + 80
        for line in wrap(d, body, font(24), pw - 56):
            d.text((x0 + 28, yy), line, font=font(24), fill=WHITE)
            yy += 38

    d = ImageDraw.Draw(img)
    d.text((80, 1038), "Garage Trip Token V2  ·  2026-10 打包版", font=font(22), fill=SOFT)
    img.convert("RGB").save(OUT / "architecture.png", "PNG", optimize=True)
    print("wrote architecture.png")


def render_flow():
    w, h = 1920, 1280
    img = new_canvas(w, h)
    d = ImageDraw.Draw(img)
    d.text((80, 48), "一次完整行程，如何变成一次开门", font=font(54, True), fill=WHITE)
    d.text((80, 122), "车载端累计距离并广播，室内端校验后只执行一次，然后锁定到下一趟行程。", font=font(28), fill=MUTED)
    d.rounded_rectangle((80, 168, 360, 176), radius=4, fill=TEAL)

    steps = [
        ("01", "行程开始", "上电或开始新的累计后，前进距离从零计算。"),
        ("02", "只读车速", "持续读取实时车速，只把向前行驶的距离累加进去。"),
        ("03", "满 500 米", "累计达到 500 米，才生成这趟行程的唯一行程号。"),
        ("04", "蓝牙广播", "同一行程号大约每 200ms 重复广播，便于室内端及时接收。"),
        ("05", "室内校验", "核对身份与完整性，确认这是“已满 500 米”的新行程。"),
        ("06", "开一次门", "输出一次 300ms 开门脉冲，并把行程号写入本地存储。"),
        ("07", "重复无效", "此后同一行程再广播多少次，都不会再开门。"),
        ("08", "下一趟重置", "只有新的行程号再次满足条件，才会开始下一轮自动开门。"),
    ]

    cols = 4
    margin_l, margin_r, top, gap_x, gap_y = 80, 80, 220, 28, 70
    card_w = (w - margin_l - margin_r - gap_x * (cols - 1)) // cols
    card_h = 340
    boxes = []
    for i, (num, title, body) in enumerate(steps):
        r, c = i // cols, i % cols
        x0 = margin_l + c * (card_w + gap_x)
        y0 = top + r * (card_h + gap_y)
        x1, y1 = x0 + card_w, y0 + card_h
        boxes.append((x0, y0, x1, y1))
        rounded(img, (x0, y0, x1, y1), 28, (*CARD, 255), outline=LINE, width=2)
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((x0 + 28, y0 + 28, x0 + 118, y0 + 88), radius=16, fill=TEAL)
        center_text(d, x0 + 73, y0 + 58, num, font(28, True), fill=(8, 22, 30), anchor="mm")
        d.text((x0 + 136, y0 + 42), title, font=font(32, True), fill=WHITE)
        yy = y0 + 120
        for line in wrap(d, body, font(26), card_w - 56):
            d.text((x0 + 28, yy), line, font=font(26), fill=MUTED)
            yy += 42

    d = ImageDraw.Draw(img)
    for i in range(len(boxes) - 1):
        if (i % cols) == cols - 1:
            continue
        x0 = boxes[i][2]
        x1 = boxes[i + 1][0]
        y = (boxes[i][1] + boxes[i][3]) // 2
        draw_arrow(d, x0 + 4, y, x1 - 4, TEAL, shaft=5)

    mid = (boxes[3][3] + boxes[4][1]) // 2
    center_text(d, w // 2, mid, "↓  室内接收之后", font(24, True), fill=TEAL, anchor="mm")

    d.rounded_rectangle((80, 1148, w - 80, 1232), radius=20, fill=TEAL_BG, outline=TEAL, width=2)
    d.text((110, 1170), "不会做的事：不把信号强弱当成距离，不在门口突然上电就开门，也不会在离开后自动关门。", font=font(28), fill=WHITE)

    img.convert("RGB").save(OUT / "trip-flow.png", "PNG", optimize=True)
    print("wrote trip-flow.png")


def render_wiring():
    w, h = 1920, 1000
    img = new_canvas(w, h)
    d = ImageDraw.Draw(img)
    d.text((80, 48), "室内端接线  ·  ESP32-C3 到 T3A", font=font(54, True), fill=WHITE)
    d.text((80, 122), "只使用 3.3V 逻辑和短脉冲。不要把 5V、12V 或卷帘门电机线接到 ESP32 的 GPIO。", font=font(28), fill=MUTED)
    d.rounded_rectangle((80, 168, 360, 176), radius=4, fill=TEAL)

    left = (80, 220, 900, 780)
    right = (1020, 220, 1840, 780)
    rounded(img, left, 32, (*CARD, 255), outline=LINE, width=2)
    rounded(img, right, 32, (*CARD, 255), outline=LINE, width=2)
    d = ImageDraw.Draw(img)
    center_text(d, 490, 260, "室内 ESP32-C3", font(36, True), WHITE, "mt")
    center_text(d, 490, 316, "蓝牙名称 Garage-C3-BLE", font(24), MUTED, "mt")
    center_text(d, 1430, 260, "T3A 433MHz 发射模块", font(36, True), WHITE, "mt")
    center_text(d, 1430, 316, "3.3V 供电 / 高电平触发版本", font(24), MUTED, "mt")

    pins_l = [("3.3V", "供电"), ("GND", "共地"), ("GPIO4", "开门"), ("GPIO6", "停止"), ("GPIO5", "关门")]
    pins_r = [("VCC", "3.3V"), ("GND", "共地"), ("K0", "开门"), ("K2", "停止"), ("K3", "关门")]

    def pin_row(x, y, label, desc):
        d.rounded_rectangle((x, y, x + 280, y + 64), radius=16, fill=(12, 32, 40), outline=TEAL, width=2)
        d.text((x + 20, y + 16), label, font=font(24, True), fill=TEAL)
        d.text((x + 130, y + 16), desc, font=font(24), fill=WHITE)

    y = 380
    for (a, ad), (b, bd) in zip(pins_l, pins_r):
        pin_row(200, y, a, ad)
        pin_row(1290, y, b, bd)
        d.line((480, y + 32, 1290, y + 32), fill=TEAL, width=4)
        d.ellipse((478, y + 24, 494, y + 40), fill=TEAL)
        d.ellipse((1282, y + 24, 1298, y + 40), fill=TEAL)
        y += 76

    d.text((1290, y + 8), "K1 保持悬空，不要接线", font=font(24, True), fill=ORANGE)

    d.rounded_rectangle((80, 820, 1840, 930), radius=20, fill=(70, 32, 28), outline=RED, width=2)
    d.text((110, 848), "安全提醒：先确认 T3A 是 3.3V / 高电平触发型号。测试时让门停在行程中途，并保持物理停止按钮随时可用。系统不能感知门的实际位置。", font=font(26), fill=WHITE)

    img.convert("RGB").save(OUT / "home-wiring.png", "PNG", optimize=True)
    print("wrote home-wiring.png")


if __name__ == "__main__":
    render_architecture()
    render_flow()
    render_wiring()
