#!/usr/bin/env python3
"""Verify the generated left-half schematic against the ADR-0002 connectivity.

Exports a netlist with kicad-cli and asserts:
- each COLc net contains exactly the switches of column c plus nano pad
- each ROWr net contains exactly the diode cathodes of row r plus nano pad
- nice!view, battery, reset and power nets are wired as designed

Usage: python3 scripts/verify_left_netlist.py
"""

import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCH = REPO / "hardware" / "kicad" / "left" / "mokumoku_keeb_left.kicad_sch"
KICAD_CLI = str(Path.home() / "Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli")

KEYS = [(r, c) for r in range(4) for c in range(6)] + [(4, c) for c in range(3)] + [(3, 6)]
NANO_PAD = {  # net -> nano symbol pin number (project symbol numbering)
    "NV_CS": "1", "NV_MOSI": "5", "NV_SCK": "6",
    "ROW0": "7", "ROW1": "8", "ROW2": "9", "ROW3": "10", "ROW4": "11",
    "COL0": "12", "COL1": "13", "COL2": "14", "COL3": "15", "COL4": "16",
    "COL5": "17", "COL6": "18",
    "VCC": "21", "RST": "22", "BAT_SW": "24",
}


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


def main():
    with tempfile.TemporaryDirectory() as td:
        net_path = Path(td) / "left.net"
        res = subprocess.run(
            [KICAD_CLI, "sch", "export", "netlist", "--format", "kicadsexpr",
             "-o", str(net_path), str(SCH)],
            capture_output=True, text=True)
        if res.returncode != 0:
            sys.exit(f"kicad-cli failed:\n{res.stdout}\n{res.stderr}")
        node, _ = parse(tokenize(net_path.read_text()))

    nets = {}
    for sec in node:
        if isinstance(sec, list) and sec and sec[0] == "nets":
            for net in sec[1:]:
                name = unq([x[1] for x in net if isinstance(x, list) and x[0] == "name"][0])
                pads = set()
                for nd in net:
                    if isinstance(nd, list) and nd[0] == "node":
                        ref = unq([x[1] for x in nd if isinstance(x, list) and x[0] == "ref"][0])
                        pin = unq([x[1] for x in nd if isinstance(x, list) and x[0] == "pin"][0])
                        pads.add((ref, pin))
                nets[name] = pads

    # map SW/D refs back to (row, col): generation order is KEYS order
    sw_of = {key: f"SW{i+1}" for i, key in enumerate(KEYS)}
    d_of = {key: f"D{i+1}" for i, key in enumerate(KEYS)}

    errors = []

    def expect(net, pads):
        got = nets.get(net)
        if got is None:
            errors.append(f"net {net}: MISSING")
        elif got != pads:
            errors.append(f"net {net}:\n  expected {sorted(pads)}\n  got      {sorted(got)}")

    for c in range(7):
        pads = {(sw_of[(r, cc)], "1") for (r, cc) in KEYS if cc == c}
        pads.add(("U1", NANO_PAD[f"COL{c}"]))
        expect(f"COL{c}", pads)
    for r in range(5):
        pads = {(d_of[(rr, c)], "1") for (rr, c) in KEYS if rr == r}  # pin1 = cathode
        pads.add(("U1", NANO_PAD[f"ROW{r}"]))
        expect(f"ROW{r}", pads)
    # per-key switch->diode-anode nets (unnamed): every SW pin2 with its D pin2
    keyed = 0
    for key in KEYS:
        want = {(sw_of[key], "2"), (d_of[key], "2")}
        if want in nets.values():
            keyed += 1
    if keyed != 28:
        errors.append(f"switch->diode anode nets: expected 28 matches, got {keyed}")

    expect("NV_MOSI", {("U1", "5"), ("J2", "1")})
    expect("NV_SCK", {("U1", "6"), ("J2", "2")})
    expect("NV_CS", {("U1", "1"), ("J2", "5")})
    expect("VCC", {("U1", "21"), ("J2", "3")})
    expect("RST", {("U1", "22"), ("SW30", "1")})
    expect("BAT_SW", {("U1", "24"), ("SW29", "1")})
    # power symbols (#FLG/#PWR) are not emitted as netlist nodes; ERC checks them
    expect("BAT_PLUS", {("J1", "1"), ("SW29", "2")})
    gnd = nets.get("GND", set())
    for pad in [("U1", "3"), ("U1", "4"), ("U1", "23"), ("J1", "2"), ("J2", "4"), ("SW30", "2")]:
        if pad not in gnd:
            errors.append(f"GND missing {pad}")

    if errors:
        print("NG:\n" + "\n".join(errors))
        sys.exit(1)
    print(f"OK: all nets match ADR-0002 design ({len(nets)} nets total)")


if __name__ == "__main__":
    main()
