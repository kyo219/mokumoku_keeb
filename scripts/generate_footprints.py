#!/usr/bin/env python3
"""Generate project footprints (hardware/kicad/footprints/mokumoku_keeb.pretty).

Sources (see docs/references.md, all dimensions in mm, KiCad top view, y down):

SW_MX_HotSwap_Kailh_PG151101S11_1u
  - Cherry MX official datasheet: center post Ø4.0 at origin, fixation pins
    Ø1.7 at (±5.08, 0), terminals at (2.54, -5.08) and (-3.81, -2.54)
    (matches KiCad standard SW_Cherry_MX_1.00u_PCB geometry).
  - Kailh PG151101S11 datasheet: socket holes Ø3.00 (NPTH) at the terminal
    positions (6.35mm horizontal / 2.54mm vertical spacing), SMD pads
    2.55 x 2.5 on the BACK side; lead centers ~3.175mm outboard of each hole
    (derived from body 10.90 / overall 14.50 drawing).
  - Socket mounts on B.Cu (hand-solder). Switch inserts from the front.

nice_nano_v2
  - 2 rows x 12 pins, 2.54mm pitch, 15.24mm row spacing (Pro Micro
    convention); drill 1.0mm (consule spring-pin hole size TO BE CONFIRMED
    against Mac8 drawing - ADR-0006).
  - Numbering matches the project schematic symbol: 1..12 top->bottom on the
    left, 13..24 bottom->top on the right (pin 24 = RAW/B+ top right).
  - Board outline / antenna zone on Fab/Dwgs layers are APPROXIMATE
    (official outline dims unverified) - do not use for final clearance.
"""

import uuid
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "hardware" / "kicad" / "footprints" / "mokumoku_keeb.pretty"


def u():
    return str(uuid.uuid4())


def pad_npth(x, y, drill):
    return (f'  (pad "" np_thru_hole circle (at {x} {y}) (size {drill} {drill}) '
            f'(drill {drill}) (layers "*.Cu" "*.Mask") (uuid "{u()}"))')


def pad_tht(num, x, y, size, drill, shape="circle"):
    return (f'  (pad "{num}" thru_hole {shape} (at {x} {y}) (size {size} {size}) '
            f'(drill {drill}) (layers "*.Cu" "*.Mask") (remove_unused_layers no) (uuid "{u()}"))')


def pad_smd_back(num, x, y, w, h):
    return (f'  (pad "{num}" smd roundrect (at {x} {y}) (size {w} {h}) '
            f'(layers "B.Cu" "B.Paste" "B.Mask") (roundrect_rratio 0.1) (uuid "{u()}"))')


def rect(x1, y1, x2, y2, layer, width=0.1):
    return (f'  (fp_rect (start {x1} {y1}) (end {x2} {y2}) '
            f'(stroke (width {width}) (type default)) (fill no) (layer "{layer}") (uuid "{u()}"))')


def text(kind, s, x, y, layer, hide=False, size=1.0):
    return (f'  (fp_text {kind} "{s}" (at {x} {y} 0) (layer "{layer}"){" (hide yes)" if hide else ""}\n'
            f'    (effects (font (size {size} {size}) (thickness 0.15))) (uuid "{u()}"))')


def footprint(name, descr, attrs, items):
    body = "\n".join(items)
    return f'''(footprint "{name}"
  (version 20240108)
  (generator "generate_footprints")
  (generator_version "1.0")
  (layer "F.Cu")
  (descr "{descr}")
  (attr {attrs})
{body}
)
'''


def hotswap():
    items = [
        text("reference", "REF**", 0, -8.9, "F.SilkS"),
        text("value", "SW_MX_HotSwap", 0, 8.9, "F.Fab"),
        # switch body (15.6 sq) on F.Fab, courtyard slightly larger
        rect(-7.8, -7.8, 7.8, 7.8, "F.Fab"),
        rect(-8.05, -8.05, 8.05, 8.05, "F.CrtYd", 0.05),
        # plate cutout reference (14.0 sq per Cherry datasheet) on Dwgs
        rect(-7.0, -7.0, 7.0, 7.0, "Dwgs.User", 0.08),
        text("user", "plate cutout 14.0", 0, 6.3, "Dwgs.User", size=0.7),
        # center post + fixation pins (Cherry MX official)
        pad_npth(0, 0, 4.0),
        pad_npth(-5.08, 0, 1.7),
        pad_npth(5.08, 0, 1.7),
        # Kailh socket holes (NPTH 3.0) at MX terminal positions
        pad_npth(2.54, -5.08, 3.0),
        pad_npth(-3.81, -2.54, 3.0),
        # socket SMD pads on back copper
        pad_smd_back(1, 5.715, -5.08, 2.55, 2.5),
        pad_smd_back(2, -6.985, -2.54, 2.55, 2.5),
        # socket body outline on B.Fab (10.90 x 5.89 spanning both holes)
        rect(-6.085, -6.755, 4.815, -0.865, "B.Fab"),
        text("user", "Kailh PG151101S11 on BACK", 0, -1.7, "B.Fab", size=0.6),
    ]
    return footprint(
        "SW_MX_HotSwap_Kailh_PG151101S11_1u",
        "Cherry MX 1u with Kailh PG151101S11 hotswap socket on back; "
        "Cherry MX + Kailh official datasheets (docs/references.md); "
        "pad offsets derived from drawing - verify against real socket before fab",
        "through_hole", items)


def nice_nano():
    items = [
        text("reference", "REF**", 0, -18.5, "F.SilkS"),
        text("value", "nice_nano_v2", 0, 18.5, "F.Fab"),
    ]
    for i in range(12):
        y = -13.97 + i * 2.54
        shape = "rect" if i == 0 else "circle"
        items.append(pad_tht(i + 1, -7.62, y, 1.6, 1.0, shape))       # left 1..12
        items.append(pad_tht(24 - i, 7.62, y, 1.6, 1.0))              # right 24..13
    # approximate module outline (Pro Micro class, USB at top) - APPROXIMATE
    items += [
        rect(-8.89, -16.51, 8.89, 16.51, "F.Fab"),
        rect(-9.15, -16.8, 9.15, 16.8, "F.CrtYd", 0.05),
        text("user", "USB-C (top)", 0, -15.2, "F.Fab", size=0.8),
        text("user", "ANTENNA end", 0, 15.2, "F.Fab", size=0.8),
        # antenna keep-out hint: bottom of module + 5mm beyond (ADR-0007)
        rect(-8.89, 10.5, 8.89, 21.5, "Dwgs.User", 0.08),
        text("user", "ANT KEEPOUT ADR-0007 (approx)", 0, 20.3, "Dwgs.User", size=0.7),
        text("user", "outline approx - verify", 0, 0, "F.Fab", size=0.7),
    ]
    return footprint(
        "nice_nano_v2",
        "nice!nano v2 socketed (2x12 2.54mm, 15.24mm row spacing, Pro Micro convention); "
        "drill 1.0mm PENDING consule drawing check (ADR-0006); outline/antenna zone approximate",
        "through_hole", items)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "SW_MX_HotSwap_Kailh_PG151101S11_1u.kicad_mod").write_text(hotswap())
    (OUT / "nice_nano_v2.kicad_mod").write_text(nice_nano())
    print(f"wrote 2 footprints to {OUT}")


if __name__ == "__main__":
    main()
