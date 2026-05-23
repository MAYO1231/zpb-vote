from PIL import Image, ImageDraw, ImageFont
import math

FONTS   = "C:/Users/lawre/AppData/Roaming/Claude/local-agent-mode-sessions/skills-plugin/6680411c-c8de-42f6-bd77-849d60e8546c/e4e2b408-e75c-4388-8417-5f719910f983/skills/canvas-design/canvas-fonts"
WINF    = "C:/Windows/Fonts"

W, H = 1920, 1080

BG       = (8,   8,  16)
SURFACE  = (15,  15, 28)
CARD     = (20,  20, 31)
BORDER   = (30,  30, 46)
GOLD     = (232, 184, 75)
GOLD_DIM = (160, 122, 26)
RED      = (201,  64, 64)
TEXT     = (232, 228, 220)
MUTED    = (90,  88, 112)
DIM      = (46,  44, 63)

img = Image.new("RGB", (W, H), BG)
d   = ImageDraw.Draw(img)

# gradient background
for x in range(W):
    t = x / W
    r = int(BG[0] + (SURFACE[0]-BG[0]) * t * 0.5)
    g = int(BG[1] + (SURFACE[1]-BG[1]) * t * 0.5)
    b = int(BG[2] + (SURFACE[2]-BG[2]) * t * 0.7)
    d.line([(x, 0), (x, H)], fill=(r, g, b))

def glow_overlay(img, cx, cy, color_rgb, radius, max_alpha=22, power=2.2):
    g = Image.new("RGBA", (W, H), (0,0,0,0))
    gd = ImageDraw.Draw(g)
    for r in range(radius, 0, -4):
        a = int(max_alpha * (1 - r/radius) ** power)
        gd.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(*color_rgb, a))
    return Image.alpha_composite(img.convert("RGBA"), g).convert("RGB")

# top-right ambient glow
img = glow_overlay(img, int(W*0.73), int(H*0.06), GOLD, 520, 22, 2.0)
d   = ImageDraw.Draw(img)

def font(path, size):
    try:    return ImageFont.truetype(path, size)
    except: return ImageFont.load_default()

f_zh_serif_lg  = font(f"{WINF}/NotoSerifTC-VF.ttf",   72)
f_zh_serif_md  = font(f"{WINF}/NotoSerifTC-VF.ttf",   32)
f_zh_serif_sm  = font(f"{WINF}/NotoSerifTC-VF.ttf",   18)
f_zh_sans      = font(f"{WINF}/NotoSansTC-VF.ttf",    14)
f_label        = font(f"{FONTS}/InstrumentSans-Bold.ttf",   11)
f_mono         = font(f"{FONTS}/JetBrainsMono-Regular.ttf", 11)
f_num_lg       = font(f"{FONTS}/WorkSans-Bold.ttf",         72)
f_num_md       = font(f"{FONTS}/WorkSans-Bold.ttf",         44)
f_serif_it     = font(f"{FONTS}/IBMPlexSerif-Italic.ttf",   15)

# ────────────────────────────────────────────────────────────────────────────
# LEFT: ceremonial arena
# ────────────────────────────────────────────────────────────────────────────
cx_l, cy_l = 400, 514

# tick ring
for i in range(72):
    a    = math.radians(i * 5)
    r1   = 316
    r2   = 334 if i % 6 == 0 else 322
    col  = GOLD_DIM if i % 6 == 0 else DIM
    x1 = cx_l + r1*math.cos(a); y1 = cy_l + r1*math.sin(a)
    x2 = cx_l + r2*math.cos(a); y2 = cy_l + r2*math.sin(a)
    d.line([x1, y1, x2, y2], fill=col, width=1)

# concentric rings
for radius, col, w in [(307, DIM, 1), (258, BORDER, 1), (190, DIM, 1), (80, DIM, 1)]:
    d.ellipse([cx_l-radius, cy_l-radius, cx_l+radius, cy_l+radius],
              outline=col, width=w)

# gold voting arc
d.arc([cx_l-258, cy_l-258, cx_l+258, cy_l+258], start=-96, end=38, fill=GOLD, width=2)
# red arc (opposing faction)
d.arc([cx_l-258, cy_l-258, cx_l+258, cy_l+258], start=148, end=218, fill=RED, width=1)

# crossed sword diagonals
for ang in [44, -44]:
    a = math.radians(ang); ln = 162
    d.line([cx_l - ln*math.cos(a), cy_l - ln*math.sin(a),
            cx_l + ln*math.cos(a), cy_l + ln*math.sin(a)], fill=MUTED, width=1)

# centre
img = glow_overlay(img, cx_l, cy_l, GOLD, 60, 16, 2.5)
d   = ImageDraw.Draw(img)
d.ellipse([cx_l-5, cy_l-5, cx_l+5, cy_l+5], fill=GOLD)
d.ellipse([cx_l-20, cy_l-20, cx_l+20, cy_l+20], outline=GOLD_DIM, width=1)

# state labels around ring
for lbl, ang in [("PENDING", -120), ("OPEN", -50), ("CLOSED", 20), ("FINISHED", 82)]:
    a  = math.radians(ang); r4 = 354
    lx = cx_l + r4*math.cos(a); ly = cy_l + r4*math.sin(a)
    d.text((lx, ly), lbl, font=f_label, fill=MUTED, anchor="mm")

# title below circle
title_y = cy_l + 352
d.text((cx_l, title_y), "交接萬歲", font=f_zh_serif_md, fill=GOLD, anchor="mm")
d.line([cx_l-108, title_y+24, cx_l+108, title_y+24], fill=GOLD_DIM, width=1)
d.text((cx_l, title_y+44), "LIVE PREDICTION  ·  盲眼劍客", font=f_label,
       fill=MUTED, anchor="mm")

# ────────────────────────────────────────────────────────────────────────────
# RIGHT: 3 state cards
# ────────────────────────────────────────────────────────────────────────────
PW  = 282
PH  = 436
PY  = (H - PH) // 2
PXS = [820, 1158, 1496]

for px in PXS:
    d.rounded_rectangle([px, PY, px+PW, PY+PH], radius=12, fill=CARD, outline=BORDER, width=1)

# connector lines
for px in PXS:
    cx2 = px + PW//2
    d.line([cx_l + 312, cy_l, cx2, PY], fill=DIM, width=1)
    d.ellipse([cx2-3, PY-3, cx2+3, PY+3], fill=DIM)

# ── Card 1: PENDING ─────────────────────────────────────────────────────────
p = PXS[0]; mid = p + PW//2
d.text((mid, PY+34), "PENDING", font=f_label, fill=MUTED, anchor="mm")
d.line([p+40, PY+50, p+PW-40, PY+50], fill=DIM, width=1)

bx, by = mid, PY + 195
for r2, af in [(58, 0.10), (42, 0.22), (28, 0.50)]:
    col_p = tuple(int(c*af + BG[j]*(1-af)) for j, c in enumerate(GOLD))
    d.ellipse([bx-r2, by-r2, bx+r2, by+r2], outline=col_p, width=1)
d.ellipse([bx-6, by-6, bx+6, by+6], fill=GOLD)

d.text((mid, PY+285), "等待開放投票", font=f_zh_serif_sm, fill=MUTED, anchor="mm")
d.text((mid, PY+314), "waiting for host", font=f_mono, fill=DIM, anchor="mm")

# ── Card 2: LIVE VOTE ────────────────────────────────────────────────────────
p = PXS[1]; mid = p + PW//2
d.rounded_rectangle([p, PY, p+PW, PY+PH], radius=12, fill=CARD,
                     outline=(*GOLD_DIM,), width=1)
d.text((mid, PY+34), "LIVE VOTE", font=f_label, fill=GOLD, anchor="mm")
d.line([p+40, PY+50, p+PW-40, PY+50], fill=GOLD_DIM, width=1)

vote_data = [("選手 A", 23, GOLD), ("選手 B", 14, RED)]
total     = sum(v[1] for v in vote_data)
vote_ys   = [PY+104, PY+246]

for (name, vote, col), vy in zip(vote_data, vote_ys):
    d.text((p+22, vy), name, font=f_zh_serif_sm, fill=TEXT)
    d.text((p+PW-22, vy+2), str(vote), font=f_num_lg, fill=col, anchor="ra")
    bw = PW - 44; by2 = vy + 54
    d.rounded_rectangle([p+22, by2, p+22+bw, by2+5], radius=3, fill=DIM)
    fw = int(bw * vote / total)
    if fw > 4:
        d.rounded_rectangle([p+22, by2, p+22+fw, by2+5], radius=3, fill=col)
    d.text((p+PW-22, by2+12), f"{round(vote/total*100)}%", font=f_mono,
           fill=MUTED, anchor="ra")

d.text((mid, PY+PH-34), f"{total} / 40  已投票",
       font=f_label, fill=MUTED, anchor="mm")

# ── Card 3: WINNER ───────────────────────────────────────────────────────────
p = PXS[2]; mid = p + PW//2
img = glow_overlay(img, mid, PY+192, GOLD, 170, 26, 1.8)
d   = ImageDraw.Draw(img)

d.rounded_rectangle([p, PY, p+PW, PY+PH], radius=12, fill=CARD, outline=BORDER, width=1)
d.text((mid, PY+34), "RESULT", font=f_label, fill=MUTED, anchor="mm")
d.line([p+40, PY+50, p+PW-40, PY+50], fill=DIM, width=1)

# trophy (text-based since emoji rendering is unreliable)
d.text((mid, PY+110), "▲", font=font(f"{FONTS}/WorkSans-Bold.ttf", 38),
       fill=GOLD, anchor="mm")
d.text((mid, PY+192), "選手 A", font=f_zh_serif_lg, fill=GOLD, anchor="mm")
d.line([p+52, PY+244, p+PW-52, PY+244], fill=GOLD_DIM, width=1)
d.text((mid, PY+272), "獲得本場勝利", font=f_zh_serif_sm, fill=MUTED, anchor="mm")

for j, (nm, mark, mc) in enumerate([
    ("小明", "✓", (100,200,120)),
    ("阿華", "✓", (100,200,120)),
    ("大偉", "✗", (180,80,80)),
    ("珊珊", "✗", (180,80,80)),
]):
    ry = PY + 322 + j * 24
    d.text((p+28, ry), nm, font=f_zh_sans, fill=MUTED)
    d.text((p+PW-28, ry), mark, font=f_mono, fill=mc, anchor="ra")

# ────────────────────────────────────────────────────────────────────────────
# BOTTOM rule + meta labels
# ────────────────────────────────────────────────────────────────────────────
d.line([(72, H-58), (W-72, H-58)], fill=DIM, width=1)
for i, lb in enumerate(["FIREBASE REALTIME DATABASE", "WEBSOCKET  ·  ZERO LATENCY", "GITHUB PAGES"]):
    d.text((72 + i*270, H-36), lb, font=f_label, fill=DIM)
for i, lb in enumerate(["HOST  ·  PARTICIPANT  ·  DISPLAY", "ZERO INSTALL", "v 1.0"]):
    d.text((W-72 - i*220, H-36), lb, font=f_label, fill=DIM, anchor="ra")

# ────────────────────────────────────────────────────────────────────────────
out = "D:/lawre/Documents/Claude/交接聚會/design-reference.png"
img.save(out, "PNG", dpi=(144,144))
print(f"Saved -> {out}  ({W}x{H})")
