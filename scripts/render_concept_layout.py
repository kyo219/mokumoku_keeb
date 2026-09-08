#!/usr/bin/env python3
"""Render a dimensioned concept mock-up of both halves to assets/renders/.

Exact: 19.05mm key pitch, key positions (ADR-0002 / key-layout.md),
nice!view 14x36mm (official). Approximate: outline margins, battery,
switch positions - case design is a later phase. This is a mock-up,
not a manufacturing drawing.
"""

from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "assets" / "renders"

P = 19.05
KEYS = [(r, c) for r in range(4) for c in range(6)] + [(4, c) for c in range(3)] + [(3, 6)]
M = 1.5  # outline margin around key caps (provisional)
KW = 18.0  # 1u cap footprint square for drawing

# left-half outline polygon (origin = center of key R0C0, y down, mm)
L = -P / 2 - M
TOP = -P / 2 - M
RIGHT = 6 * P + P / 2 + M
MAIN_BOT = 3 * P + P / 2 + M
FOOT_R = 2 * P + P / 2 + M
FOOT_BOT = 4 * P + P / 2 + M
OUTLINE = [(L, TOP), (RIGHT, TOP), (RIGHT, MAIN_BOT), (FOOT_R, MAIN_BOT),
           (FOOT_R, FOOT_BOT), (L, FOOT_BOT)]

NV_W, NV_H = 14.0, 36.0
NV_CX, NV_CY = 6 * P, 9.5      # above the thumb key (R3C6)
NN_W, NN_H = 17.8, 33.0        # nice!nano approx
NN_CY = NV_CY + 1.5


def svg_half(ox, mirror):
    def tx(x, y):
        x = -x if mirror else x
        return (ox + x, 12 + y - TOP)

    def poly(pts, style):
        s = " ".join(f"{tx(x,y)[0]:.2f},{tx(x,y)[1]:.2f}" for x, y in pts)
        return f'<polygon points="{s}" style="{style}"/>'

    def rect(cx, cy, w, h, style, rx=1.2):
        x, y = tx(cx, cy)
        return (f'<rect x="{x-w/2:.2f}" y="{y-h/2:.2f}" width="{w}" height="{h}" '
                f'rx="{rx}" style="{style}"/>')

    def label(cx, cy, s, size=3.2, anchor="middle", color="#555"):
        x, y = tx(cx, cy)
        return (f'<text x="{x:.2f}" y="{y:.2f}" font-size="{size}" text-anchor="{anchor}" '
                f'fill="{color}" font-family="Hiragino Sans, sans-serif">{s}</text>')

    e = [poly(OUTLINE, "fill:#f8f5ef;stroke:#333;stroke-width:0.6")]
    # keys
    for (r, c) in KEYS:
        e.append(rect(c * P, r * P, KW, KW, "fill:#fff;stroke:#888;stroke-width:0.4", rx=2.2))
    e.append(label(6 * P, 3 * P + 1.2, "1u", 3.0))
    # nice!nano (below nice!view, dashed) then nice!view on top
    e.append(rect(NV_CX, NN_CY, NN_W, NN_H,
                  "fill:none;stroke:#b06;stroke-width:0.4;stroke-dasharray:1.6 1.2"))
    e.append(rect(NV_CX, NV_CY, NV_W, NV_H, "fill:#dfeefe;stroke:#369;stroke-width:0.5"))
    e.append(label(NV_CX, NV_CY + 1, "nice!view", 3.0, color="#369"))
    e.append(label(NV_CX, NV_CY + 5, "(下にnano)", 2.4, color="#b06"))
    # antenna zone at outer(top) end of nano, USB toward keys(bottom)
    e.append(rect(NV_CX, NN_CY - NN_H / 2 - 2.5, NN_W, 5,
                  "fill:#fdd;stroke:#c33;stroke-width:0.3;stroke-dasharray:1 1"))
    e.append(label(NV_CX, NN_CY - NN_H / 2 - 4.5, "アンテナkeep-out", 2.4, color="#c33"))
    e.append(label(NV_CX, NN_CY + NN_H / 2 + 3.4, "USB-C↓", 2.6, color="#b06"))
    # battery (TBD) under main block
    e.append(rect(1 * P, 1.5 * P, 31, 37,
                  "fill:none;stroke:#284;stroke-width:0.4;stroke-dasharray:2 1.5"))
    e.append(label(1 * P, 1.5 * P, "LiPo(裏面/寸法未定)", 2.6, color="#284"))
    # slide switch on outer edge of the C6 tab, below the antenna zone,
    # between nice!view bottom and the thumb key (case-side operation)
    sw_y = (NV_CY + NV_H / 2 + 3 * P - P / 2) / 2  # midway view-bottom .. key-top
    e.append(rect(RIGHT - 1.6, sw_y, 3, 9, "fill:#ffe9b8;stroke:#a80;stroke-width:0.3"))
    e.append(label(RIGHT - 3.4, sw_y + 12, "電源SW", 2.4,
                   anchor="end" if not mirror else "start", color="#a80"))
    e.append(label(RIGHT - 3.4, sw_y + 15.2, "(タブ側面)", 2.2,
                   anchor="end" if not mirror else "start", color="#a80"))
    return e


W, H = 340, 125
parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" '
         f'viewBox="0 0 {W} {H}">',
         '<rect width="100%" height="100%" fill="white"/>',
         '<text x="170" y="8" font-size="4.4" text-anchor="middle" fill="#222" '
         'font-family="Hiragino Sans, sans-serif">mokumoku-keeb(仮称) 概観モック '
         '— ピッチ/キー配置/nice!view寸法は確定値、外形余白・電池・SW位置は仮</text>']
parts += svg_half(14 - L, mirror=False)
parts += svg_half(W - 14 + L, mirror=True)
parts.append('<text x="170" y="122" font-size="3.6" text-anchor="middle" fill="#777" '
             'font-family="Hiragino Sans, sans-serif">左右間・ホスト接続はBLE(ケーブルなし) '
             '/ 左右合計56キー / 19.05mmピッチ</text>')
parts.append("</svg>")

OUT.mkdir(parents=True, exist_ok=True)
(OUT / "concept-layout.svg").write_text("\n".join(parts))
print(f"wrote {OUT / 'concept-layout.svg'}")
