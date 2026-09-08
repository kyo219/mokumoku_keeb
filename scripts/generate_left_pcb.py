#!/usr/bin/env python3
"""Generate the left-half PCB (placement + outline + antenna keep-out).

Run with KiCad's bundled Python (needs pcbnew):
  ~/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/*/bin/python3 \
      scripts/generate_left_pcb.py

Reads the netlist exported from the generated schematic, then builds
hardware/kicad/left/mokumoku_keeb_left.kicad_pcb:
  - 28 hotswap switches on a 19.05mm grid (key R0C0 center at (50, 50))
  - diodes on the back side between rows
  - nice!nano (antenna toward the top board edge, ADR-0007), nice!view header
  - JST PH on the back in the battery zone
  - cutout board outline per docs/key-layout.md
  - antenna keep-out rule area (all copper layers)
SW29 (slide switch) and SW30 (reset) have no verified footprint yet and are
NOT placed (Alps drawing / part selection pending).
Routing is a later phase - DRC "unconnected items" are expected.
"""

import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LEFT = REPO / "hardware" / "kicad" / "left"
SCH = LEFT / "mokumoku_keeb_left.kicad_sch"
PCB = LEFT / "mokumoku_keeb_left.kicad_pcb"
KICAD_CLI = str(Path.home() / "Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli")
STD_FP = Path.home() / "Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints"
PRJ_FP = REPO / "hardware" / "kicad" / "footprints"

import pcbnew  # noqa: E402
from pcbnew import VECTOR2I_MM  # noqa: E402

P = 19.05
X0, Y0 = 50.0, 50.0
KEYS = [(r, c) for r in range(4) for c in range(6)] + [(4, c) for c in range(3)] + [(3, 6)]

# board outline (same shape as concept mock; margin 1.5mm past keycap edge)
M = 9.525 + 1.5
TOP, LFT = Y0 - M, X0 - M
RGT = X0 + 6 * P + M
MAIN_BOT = Y0 + 3 * P + M
FOOT_R = X0 + 2 * P + M
FOOT_BOT = Y0 + 4 * P + M
OUTLINE = [(LFT, TOP), (RGT, TOP), (RGT, MAIN_BOT), (FOOT_R, MAIN_BOT),
           (FOOT_R, FOOT_BOT), (LFT, FOOT_BOT)]

NANO = (X0 + 6 * P, 57.0, 180)      # antenna end at top edge (ADR-0007)
NVIEW = (X0 + 6 * P - 5.08, 76.0, 90)  # 5-pin header centered on tab, below nano courtyard
JST = (162.0, 88.0, 0)              # back side, C6 tab free area (battery leads reach)

# antenna keep-out: nano top portion + 5mm margin, open to the top edge
KEEPOUT = [(NANO[0] - 8.89 - 5, TOP), (RGT, TOP),
           (RGT, 52.0), (NANO[0] - 8.89 - 5, 52.0)]


def tokenize(text):
    return re.findall(r'"(?:[^"\\]|\\.)*"|[()]|[^\s()"]+', text)


def parse(tokens, i=0):
    assert tokens[i] == "("
    i += 1
    out = []
    while tokens[i] != ")":
        if tokens[i] == "(":
            node, i = parse(tokens, i)
            out.append(node)
        else:
            out.append(tokens[i])
            i += 1
    return out, i + 1


def unq(s):
    return s[1:-1] if isinstance(s, str) and s.startswith('"') else s


def read_netlist():
    with tempfile.TemporaryDirectory() as td:
        np = Path(td) / "l.net"
        res = subprocess.run([KICAD_CLI, "sch", "export", "netlist", "--format",
                              "kicadsexpr", "-o", str(np), str(SCH)],
                             capture_output=True, text=True)
        if res.returncode != 0:
            sys.exit(res.stderr)
        node, _ = parse(tokenize(np.read_text()))
    comps, nets = {}, {}
    for sec in node:
        if isinstance(sec, list) and sec and sec[0] == "components":
            for c in sec[1:]:
                ref = unq([x[1] for x in c if isinstance(x, list) and x[0] == "ref"][0])
                fps = [x[1] for x in c if isinstance(x, list) and x[0] == "footprint"]
                comps[ref] = unq(fps[0]) if fps else ""
        if isinstance(sec, list) and sec and sec[0] == "nets":
            for n in sec[1:]:
                name = unq([x[1] for x in n if isinstance(x, list) and x[0] == "name"][0])
                for nd in n:
                    if isinstance(nd, list) and nd[0] == "node":
                        ref = unq([x[1] for x in nd if isinstance(x, list) and x[0] == "ref"][0])
                        pin = unq([x[1] for x in nd if isinstance(x, list) and x[0] == "pin"][0])
                        nets.setdefault(name, []).append((ref, pin))
    return comps, nets


def lib_dir(fpid):
    lib, _ = fpid.split(":")
    if lib == "mokumoku_keeb":
        return str(PRJ_FP / "mokumoku_keeb.pretty")
    return str(STD_FP / f"{lib}.pretty")


def main():
    comps, nets = read_netlist()
    board = pcbnew.NewBoard(str(PCB))

    netinfo = {}
    for name in nets:
        ni = pcbnew.NETINFO_ITEM(board, name)
        board.Add(ni)
        netinfo[name] = ni
    pad_net = {}
    for name, nodes in nets.items():
        for ref, pin in nodes:
            pad_net[(ref, pin)] = name

    placements = {}
    for i, (r, c) in enumerate(KEYS):
        x, y = X0 + c * P, Y0 + r * P
        placements[f"SW{i+1}"] = (x, y, 0, False)
        placements[f"D{i+1}"] = (x, y + 9.5, 0, True)
    placements["U1"] = (NANO[0], NANO[1], NANO[2], False)
    placements["J2"] = (NVIEW[0], NVIEW[1], NVIEW[2], False)
    placements["J1"] = (JST[0], JST[1], JST[2], True)

    skipped = []
    for ref, fpid in sorted(comps.items()):
        if ref.startswith("#"):
            continue
        if not fpid or ref not in placements:
            skipped.append(ref)
            continue
        name = fpid.split(":")[1]
        fp = pcbnew.FootprintLoad(lib_dir(fpid), name)
        assert fp, fpid
        fp.SetReference(ref)
        board.Add(fp)
        x, y, rot, flip = placements[ref]
        if flip:
            fp.Flip(fp.GetPosition(), False)
        fp.SetPosition(VECTOR2I_MM(x, y))
        fp.SetOrientationDegrees(rot)
        for pad in fp.Pads():
            key = (ref, pad.GetNumber())
            if key in pad_net:
                pad.SetNet(netinfo[pad_net[key]])
        if ref.startswith("D"):
            # keep the silk ref beside the diode (bottom rows would clip the edge)
            fp.Reference().SetPosition(VECTOR2I_MM(x - 6.4, y))
            fp.Reference().SetTextAngleDegrees(0)

    # board outline
    pts = OUTLINE + [OUTLINE[0]]
    for a, b in zip(pts, pts[1:]):
        sh = pcbnew.PCB_SHAPE(board)
        sh.SetShape(pcbnew.SHAPE_T_SEGMENT)
        sh.SetStart(VECTOR2I_MM(*a))
        sh.SetEnd(VECTOR2I_MM(*b))
        sh.SetLayer(pcbnew.Edge_Cuts)
        sh.SetWidth(int(0.1 * 1e6))
        board.Add(sh)

    # antenna keep-out rule area (all copper layers)
    z = pcbnew.ZONE(board)
    z.SetIsRuleArea(True)
    for setter in ["SetDoNotAllowCopperPour", "SetDoNotAllowZoneFills"]:
        if hasattr(z, setter):
            getattr(z, setter)(True)
    z.SetDoNotAllowTracks(True)
    z.SetDoNotAllowVias(True)
    if hasattr(z, "SetDoNotAllowPads"):
        z.SetDoNotAllowPads(False)
    ls = pcbnew.LSET()
    ls.AddLayer(pcbnew.F_Cu)
    ls.AddLayer(pcbnew.B_Cu)
    z.SetLayerSet(ls)
    z.Outline().NewOutline()
    for x, y in KEEPOUT:
        z.Outline().Append(VECTOR2I_MM(x, y))
    z.SetZoneName("antenna_keepout_ADR0007")
    board.Add(z)

    pcbnew.SaveBoard(str(PCB), board)
    print(f"saved {PCB}")
    print(f"placed {len(comps) - len(skipped) - 2} components; "
          f"skipped (no verified footprint): {skipped}")


if __name__ == "__main__":
    main()
