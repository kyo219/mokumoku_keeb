#!/usr/bin/env python3
"""Side (front) cross-section mock of the left half, cut near row R1.

Verified dims: plate 1.5 / plate-top to PCB-top 5.0 (Cherry official),
Kailh socket 1.85 below PCB (official), nice!nano board 3.2 (official),
nice!view 14 wide (official). Provisional: PCB 1.6 (candidate), battery
4.0 thick, case walls 1.8, consule height 3.0 - marked (仮).
Heights in mm, y up; rendered into SVG y-down.
"""

from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "assets" / "renders"

P = 19.05
PCB_T = 1.6
PLATE_T = 1.5
PLATE_TOP = 5.0          # above PCB top (Cherry official)
SOCK = 1.85              # below PCB bottom (Kailh official)
BAT_T = 4.0              # 仮
WALL = 1.8               # 仮
CONSULE = 3.0            # 仮 (ADR-0006 pending)
NANO_T = 3.2             # official
VIEW_T = 2.0             # board+display approx
GND = PCB_T + max(SOCK + 0.6, BAT_T + 0.8) + WALL  # case bottom below PCB top

BASE = 40.0  # svg y of PCB top
SC = 7.0     # px per mm


def Y(h):    # height above PCB top -> svg y
    return BASE * SC - h * SC


def X(x):
    return (x + 14) * SC


els = []


def rect(x1, h1, x2, h2, fill, stroke="#333", sw=0.8, dash=""):
    d = f';stroke-dasharray:{dash}' if dash else ''
    els.append(f'<rect x="{X(x1):.1f}" y="{Y(h2):.1f}" width="{(x2-x1)*SC:.1f}" '
               f'height="{(h2-h1)*SC:.1f}" style="fill:{fill};stroke:{stroke};stroke-width:{sw}{d}"/>')


def label(x, h, s, size=11, anchor="start", color="#333"):
    els.append(f'<text x="{X(x):.1f}" y="{Y(h):.1f}" font-size="{size}" text-anchor="{anchor}" '
               f'fill="{color}" font-family="Hiragino Sans, sans-serif">{s}</text>')


L, R = -11.0, 123.8          # board extents (top-view x)
TAB_L = 104.8

# case bottom + walls (resin, ADR-0008)
rect(L - WALL, -GND, R + WALL, -GND + WALL, "#e8e2d8")
rect(L - WALL, -GND, L, PLATE_TOP + PLATE_T, "#e8e2d8")
rect(R, -GND, R + WALL, PLATE_TOP + PLATE_T, "#e8e2d8")
# PCB
rect(L, -PCB_T, R, 0, "#3a7d44", "#2a5", 0.8)
# plate over key zone (stops before nice!view tab)
rect(L, PLATE_TOP, TAB_L, PLATE_TOP + PLATE_T, "#c9ced6")
# switches + caps at C0..C5
for c in range(6):
    x = c * P
    rect(x - 7, 0, x + 7, PLATE_TOP, "#f4f4f4", "#888", 0.6)             # lower body
    rect(x - 7.8, PLATE_TOP, x + 7.8, PLATE_TOP + 6.6, "#fafafa", "#777", 0.7)  # upper body
    rect(x - 3.5, PLATE_TOP + 6.6, x + 3.5, PLATE_TOP + 10.2, "#e77", "#a44", 0.6)  # stem
    rect(x - 8.8, PLATE_TOP + 9.0, x + 8.8, PLATE_TOP + 17.0, "#fff", "#555", 0.9)  # keycap
    rect(x + 1.0, -PCB_T - SOCK, x + 6.0, -PCB_T, "#555", "#333", 0.5)   # hotswap socket
# battery under C0..C2 (仮)
rect(-6, -PCB_T - 0.4 - BAT_T, 44, -PCB_T - 0.4, "#bfe3c8", "#284", 0.8, dash="4 3")
label(19, -PCB_T - 2.6, "LiPo(厚さ仮4.0+膨張余裕)", 10, "middle", "#284")
# nano + view stack on the tab (edge-on: 17.78 wide board)
nx = 114.3
rect(nx - 8.9, CONSULE, nx + 8.9, CONSULE + NANO_T, "#d06", "#903", 0.7)
rect(nx - 7.0, CONSULE + NANO_T + 1.2, nx + 7.0, CONSULE + NANO_T + 1.2 + VIEW_T, "#69c", "#369", 0.7)
label(nx - 8.9, CONSULE + NANO_T + VIEW_T + 4.2, "nice!view(下がnano、コンスルー高さ未定)", 11, "start", "#369")
# slide switch knob through right wall
rect(R - 0.4, 1.0, R + WALL + 0.8, 4.0, "#fc3", "#a80", 0.7)
label(R - 20.0, -4.6, "→電源SWノブ(側面)", 11, "start", "#a80")

# dimension lines + staggered labels on the right
DIMS = [
    (PLATE_TOP + PLATE_T, "プレート上面(底から≈14.7 仮)", "#369"),
    (PLATE_TOP, "プレート 1.5(Cherry公式)/ PCB上面→プレート上面 5.0(MX公式)", "#147"),
    (0, "PCB 1.6(標準候補)", "#2a5"),
    (-PCB_T - SOCK, "ホットスワップソケット 1.85(Kailh公式)", "#555"),
    (-GND, "ケース底(樹脂 ADR-0008・肉厚仮1.8)", "#a86"),
]
lx = X(R + WALL + 26)
ys = []
for h, s, col in DIMS:
    els.append(f'<line x1="{X(L-4)}" y1="{Y(h):.1f}" x2="{lx-6:.1f}" y2="{Y(h):.1f}" '
               f'style="stroke:{col};stroke-width:0.5;stroke-dasharray:2 3"/>')
    y = Y(h) + 3
    while any(abs(y - p) < 15 for p in ys):
        y += 15
    ys.append(y)
    els.append(f'<text x="{lx:.1f}" y="{y:.1f}" font-size="11" fill="{col}" '
               f'font-family="Hiragino Sans, sans-serif">{s}</text>')

W, H = int((R + 30) * SC + 430), int(BASE * SC + 130)
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
       '<rect width="100%" height="100%" fill="white"/>',
       '<text x="14" y="22" font-size="15" fill="#222" font-family="Hiragino Sans, sans-serif">'
       'mokumoku-keeb 断面モック(第2行付近・左半分を正面から) — 公式値と仮値の混在に注意</text>',
       f'<text x="14" y="{H-18}" font-size="12" fill="#777" font-family="Hiragino Sans, sans-serif">'
       '底面〜プレート上面 ≈ '
       f'{GND + PLATE_TOP + PLATE_T:.1f}mm(仮: 電池4.0mm+余裕が支配的) / '
       'キーキャップ・スイッチ上部形状は概形</text>'] + els + ["</svg>"]

OUT.mkdir(parents=True, exist_ok=True)
(OUT / "concept-side.svg").write_text("\n".join(svg))
print(f"wrote {OUT / 'concept-side.svg'}  (case bottom to plate top ~{GND + PLATE_TOP + PLATE_T:.1f}mm)")
