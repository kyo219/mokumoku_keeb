#!/usr/bin/env python3
"""Generate the left-half schematic (hardware/kicad/left/) from the design data
in ADR-0002 (matrix/GPIO) and docs/key-layout.md.

The schematic is the generated artifact; this script is the editable source.
If pins or the matrix change, update ADR-0002/electrical.md and this script
together (AGENTS.md rule), then re-run.

Usage:  python3 scripts/generate_left_schematic.py
Requires KiCad 9 installed (symbol libraries are copied from the app bundle).
"""

import re
import sys
import uuid
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT_DIR = REPO / "hardware" / "kicad" / "left"
PROJECT = "mokumoku_keeb_left"
KICAD_SYMBOL_DIR = Path.home() / "Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols"
PROJECT_LIB = REPO / "hardware" / "kicad" / "symbols" / "mokumoku_keeb.kicad_sym"

# --- Design data (must match ADR-0002 / docs/key-layout.md) ---------------
ROWS = 5
COLS = 7
# (row, col) positions that have a key: R0-R3 x C0-C5, R4 x C0-C2, R3 x C6
KEYS = [(r, c) for r in range(4) for c in range(6)] + [(4, c) for c in range(3)] + [(3, 6)]
assert len(KEYS) == 28

# nice!nano pin number (per project symbol) -> net label
NANO_NETS = {
    1: "NV_CS",     # D1/P0.06
    2: None,        # D0/P0.08  spare
    3: "GND", 4: "GND",
    5: "NV_MOSI",   # D2/P0.17
    6: "NV_SCK",    # D3/P0.20
    7: "ROW0",      # D4/P0.22
    8: "ROW1",      # D5/P0.24
    9: "ROW2",      # D6/P1.00
    10: "ROW3",     # D7/P0.11
    11: "ROW4",     # D8/P1.04
    12: "COL0",     # D9/P1.06
    13: "COL1",     # D10/P0.09
    14: "COL2",     # D16/P0.10
    15: "COL3",     # D14/P1.11
    16: "COL4",     # D15/P1.13
    17: "COL5",     # D18/P1.15
    18: "COL6",     # D19/P0.02
    19: None,       # D20/P0.29 spare
    20: None,       # D21/P0.31 spare
    21: "VCC",
    22: "RST",
    23: "GND",
    24: "BAT_SW",   # RAW/B+ (battery via slide switch)
}

# --- Minimal s-expression parsing ----------------------------------------


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


def find_all(node, head):
    return [x for x in node if isinstance(x, list) and x and x[0] == head]


def find_one(node, head):
    hits = find_all(node, head)
    return hits[0] if hits else None


def unq(s):
    return s[1:-1] if isinstance(s, str) and s.startswith('"') else s


def extract_symbol(lib_file, name):
    """Return (raw_text, pins) for a symbol; pins = {number: (x, y)} in
    symbol-local coordinates (y up)."""
    text = lib_file.read_text()
    marker = f'(symbol "{name}"'
    start = text.index(marker)
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "(":
            depth += 1
        elif text[i] == ")":
            depth -= 1
            if depth == 0:
                raw = text[start : i + 1]
                break
    node, _ = parse(tokenize(raw))
    pins = {}
    for sub in find_all(node, "symbol") + [node]:
        for pin in find_all(sub, "pin"):
            at = find_one(pin, "at")
            num = unq(find_one(pin, "number")[1])
            pins[num] = (float(at[1]), float(at[2]))
    return raw, pins


def rotated(vec, rot):
    """Symbol-local (y up) -> schematic offset (y down) for rotation rot."""
    lx, ly = vec
    x, y = lx, -ly  # to y-down axes
    for _ in range(rot // 90):
        x, y = y, -x  # visual CCW rotation in y-down coords
    return x, y


def pin_abs(pos, rot, local):
    dx, dy = rotated(local, rot)
    return (round(pos[0] + dx, 4), round(pos[1] + dy, 4))


# --- Schematic emission ---------------------------------------------------

ROOT_UUID = str(uuid.uuid4())
body = []
ref_counters = {}


def u():
    return str(uuid.uuid4())


def next_ref(prefix):
    ref_counters[prefix] = ref_counters.get(prefix, 0) + 1
    return f"{prefix}{ref_counters[prefix]}"


# footprint assignment per reference prefix (docs: footprints/README.md)
FOOTPRINTS = {
    "SW_MX": "mokumoku_keeb:SW_MX_HotSwap_Kailh_PG151101S11_1u",
    "D": "Diode_SMD:D_SOD-123",
    "U1": "mokumoku_keeb:nice_nano_v2",
    "J1": "Connector_JST:JST_PH_S2B-PH-SM4-TB_1x02-1MP_P2.00mm_Horizontal",
    "J2": "Connector_PinHeader_2.54mm:PinHeader_1x05_P2.54mm_Vertical",
    # SW29 (SSSS811101) / SW30 (reset): no verified footprint yet -> empty
}


def place(lib_id, pos, rot, ref, value, pins, extra_props="", footprint=""):
    pin_lines = "\n".join(f'    (pin "{n}" (uuid "{u()}"))' for n in sorted(pins, key=lambda s: (len(s), s)))
    body.append(f'''  (symbol (lib_id "{lib_id}") (at {pos[0]} {pos[1]} {rot}) (unit 1)
    (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)
    (uuid "{u()}")
    (property "Reference" "{ref}" (at {pos[0]} {pos[1] - 5.08} 0)
      (effects (font (size 1.27 1.27))))
    (property "Value" "{value}" (at {pos[0]} {pos[1] + 5.08} 0)
      (effects (font (size 1.27 1.27))))
    (property "Footprint" "{footprint}" (at {pos[0]} {pos[1]} 0)
      (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "" (at {pos[0]} {pos[1]} 0)
      (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Description" "" (at {pos[0]} {pos[1]} 0)
      (effects (font (size 1.27 1.27)) (hide yes))){extra_props}
{pin_lines}
    (instances (project "{PROJECT}"
      (path "/{ROOT_UUID}" (reference "{ref}") (unit 1))))
  )''')


def glabel(text, pos, rot, shape="input"):
    body.append(f'''  (global_label "{text}" (shape {shape}) (at {pos[0]} {pos[1]} {rot}) (fields_autoplaced yes)
    (effects (font (size 1.27 1.27)) (justify {"left" if rot in (0,) else "right" if rot == 180 else "left"}))
    (uuid "{u()}")
    (property "Intersheetrefs" "${{INTERSHEET_REFS}}" (at {pos[0]} {pos[1]} 0)
      (effects (font (size 1.27 1.27)) (hide yes)))
  )''')


def wire(p1, p2):
    body.append(f'''  (wire (pts (xy {p1[0]} {p1[1]}) (xy {p2[0]} {p2[1]}))
    (stroke (width 0) (type default)) (uuid "{u()}"))''')


def no_connect(pos):
    body.append(f'  (no_connect (at {pos[0]} {pos[1]}) (uuid "{u()}"))')


def text_note(s, pos, size=1.27):
    body.append(f'''  (text "{s}" (exclude_from_sim no) (at {pos[0]} {pos[1]} 0)
    (effects (font (size {size} {size})) (justify left bottom)) (uuid "{u()}"))''')


def main():
    if not KICAD_SYMBOL_DIR.exists():
        sys.exit(f"KiCad symbol dir not found: {KICAD_SYMBOL_DIR}")

    libs = {}
    wanted = [
        ("Switch", "SW_Push"),
        ("Switch", "SW_SPDT"),
        ("Device", "D"),
        ("Connector_Generic", "Conn_01x02"),
        ("Connector_Generic", "Conn_01x05"),
        ("power", "GND"),
        ("power", "VCC"),
        ("power", "PWR_FLAG"),
    ]
    for libname, sym in wanted:
        raw, pins = extract_symbol(KICAD_SYMBOL_DIR / f"{libname}.kicad_sym", sym)
        raw = raw.replace(f'(symbol "{sym}"', f'(symbol "{libname}:{sym}"', 1)
        libs[f"{libname}:{sym}"] = (raw, pins)
    raw, pins = extract_symbol(PROJECT_LIB, "nice_nano_v2")
    raw = raw.replace('(symbol "nice_nano_v2"', '(symbol "mokumoku_keeb:nice_nano_v2"', 1)
    libs["mokumoku_keeb:nice_nano_v2"] = (raw, pins)

    sw_pins = libs["Switch:SW_Push"][1]
    d_pins = libs["Device:D"][1]

    # --- Key matrix cells (physical grid layout, col2row) ---
    X0, Y0, PITCH_X, PITCH_Y = 63.5, 38.1, 30.48, 33.02
    for (r, c) in KEYS:
        cx, cy = X0 + c * PITCH_X, Y0 + r * PITCH_Y
        ref = next_ref("SW")
        place("Switch:SW_Push", (cx, cy), 0, ref, "MX", sw_pins, footprint=FOOTPRINTS["SW_MX"])
        p1 = pin_abs((cx, cy), 0, sw_pins["1"])
        p2 = pin_abs((cx, cy), 0, sw_pins["2"])
        glabel(f"COL{c}", p1, 180)
        # diode below-right of the switch, cathode down toward ROW label
        dref = next_ref("D")
        drot = 90 if rotated(d_pins["2"], 90)[1] < 0 else 270  # anode up
        anode_target = (p2[0], p2[1] + 2.54)
        dx, dy = rotated(d_pins["2"], drot)
        dpos = (round(anode_target[0] - dx, 4), round(anode_target[1] - dy, 4))
        place("Device:D", dpos, drot, dref, "1N4148W", d_pins, footprint=FOOTPRINTS["D"])
        wire(p2, anode_target)
        kath = pin_abs(dpos, drot, d_pins["1"])
        row_pt = (kath[0], kath[1] + 2.54)
        wire(kath, row_pt)
        glabel(f"ROW{r}", row_pt, 270)

    # --- nice!nano ---
    nano_pins = libs["mokumoku_keeb:nice_nano_v2"][1]
    npos = (285.75, 190.5)
    place("mokumoku_keeb:nice_nano_v2", npos, 0, "U1", "nice!nano v2", nano_pins, footprint=FOOTPRINTS["U1"])
    for num, net in NANO_NETS.items():
        pt = pin_abs(npos, 0, nano_pins[str(num)])
        left_side = nano_pins[str(num)][0] < 0
        if net is None:
            no_connect(pt)
        elif net == "GND":
            grot = 0  # place GND power symbol via label instead
            glabel("GND", pt, 180 if left_side else 0)
        else:
            glabel(net, pt, 180 if left_side else 0)

    # --- battery connector + slide switch (support section) ---
    jst_pins = libs["Connector_Generic:Conn_01x02"][1]
    jpos = (63.5, 215.9)
    place("Connector_Generic:Conn_01x02", jpos, 0, "J1", "JST_PH_S2B-PH-SM4-TB", jst_pins, footprint=FOOTPRINTS["J1"])
    j1 = pin_abs(jpos, 0, jst_pins["1"])
    j2 = pin_abs(jpos, 0, jst_pins["2"])
    # NOTE: polarity TBD (ADR-0003) - pin1=BAT+ assumed until battery verified
    glabel("BAT_PLUS", j1, 180)
    glabel("GND", j2, 180)
    text_note("JST PH polarity ASSUMED pin1=+ / pin2=- : VERIFY against real battery before fab (ADR-0003)", (40.64, 227.0))

    sp_pins = libs["Switch:SW_SPDT"][1]
    spos = (114.3, 215.9)
    place("Switch:SW_SPDT", spos, 0, "SW29", "SSSS811101", sp_pins)
    common = pin_abs(spos, 0, sp_pins["2"])
    throw_a = pin_abs(spos, 0, sp_pins["1"])
    throw_b = pin_abs(spos, 0, sp_pins["3"])
    glabel("BAT_PLUS", common, 180)
    glabel("BAT_SW", throw_a, 0)
    no_connect(throw_b)
    text_note("Power switch in BATTERY+ line. 0.3A rating: never bridge nice!nano BOOST jumper (ADR-0004)", (40.64, 231.0))

    # --- reset switch ---
    rpos = (165.1, 215.9)
    place("Switch:SW_Push", rpos, 0, "SW30", "RESET", sw_pins)
    r1 = pin_abs(rpos, 0, sw_pins["1"])
    r2 = pin_abs(rpos, 0, sw_pins["2"])
    glabel("RST", r1, 180)
    glabel("GND", r2, 0)

    # --- nice!view connector (pin order per official pinout: MOSI SCK VCC GND CS) ---
    nv_pins = libs["Connector_Generic:Conn_01x05"][1]
    vpos = (215.9, 215.9)
    place("Connector_Generic:Conn_01x05", vpos, 0, "J2", "nice_view", nv_pins, footprint=FOOTPRINTS["J2"])
    nv_nets = {"1": "NV_MOSI", "2": "NV_SCK", "3": "VCC", "4": "GND", "5": "NV_CS"}
    for num, net in nv_nets.items():
        glabel(net, pin_abs(vpos, 0, nv_pins[num]), 180)

    # --- PWR_FLAGs (BAT_PLUS and GND are externally driven) ---
    pf_pins = libs["power:PWR_FLAG"][1]
    for i, net in enumerate(["BAT_PLUS", "GND"]):
        fpos = (63.5 + i * 25.4, 251.46)
        place("power:PWR_FLAG", fpos, 0, f"#FLG{i+1:02d}", "PWR_FLAG", pf_pins)
        fp = pin_abs(fpos, 0, pf_pins["1"])
        glabel(net, (fp[0], fp[1] + 2.54), 270)
        wire(fp, (fp[0], fp[1] + 2.54))

    # --- title-block-ish notes ---
    text_note("mokumoku-keeb LEFT half - Rev.A draft. GENERATED by scripts/generate_left_schematic.py - do not hand-edit wiring.", (40.64, 26.0), 2.0)
    text_note("Matrix: 5 rows x 7 cols, col2row (diode cathode -> ROW). 28 keys. ADR-0002.", (40.64, 30.5))

    lib_blob = "\n".join(
        "    " + raw.replace("\n", "\n    ") for raw, _ in libs.values()
    )
    sch = f'''(kicad_sch (version 20250114) (generator "generate_left_schematic") (generator_version "9.0")
  (uuid "{ROOT_UUID}")
  (paper "A2")
  (title_block
    (title "mokumoku-keeb left half")
    (rev "A-draft")
    (comment 1 "Generated - see scripts/generate_left_schematic.py")
  )
  (lib_symbols
{lib_blob}
  )
{chr(10).join(body)}
  (sheet_instances (path "/" (page "1")))
)
'''
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / f"{PROJECT}.kicad_sch").write_text(sch)
    pro = '{\n  "meta": { "filename": "%s.kicad_pro", "version": 3 },\n  "schematic": { "legacy_lib_list": [] }\n}\n' % PROJECT
    pro_path = OUT_DIR / f"{PROJECT}.kicad_pro"
    if not pro_path.exists():
        pro_path.write_text(pro)
    (OUT_DIR / "fp-lib-table").write_text(
        '(fp_lib_table (version 7)\n'
        '  (lib (name "mokumoku_keeb")(type "KiCad")'
        '(uri "${KIPRJMOD}/../footprints/mokumoku_keeb.pretty")(options "")(descr "project footprints"))\n)\n'
    )
    (OUT_DIR / "sym-lib-table").write_text(
        '(sym_lib_table (version 7)\n'
        '  (lib (name "mokumoku_keeb")(type "KiCad")'
        '(uri "${KIPRJMOD}/../symbols/mokumoku_keeb.kicad_sym")(options "")(descr "project symbols"))\n)\n'
    )
    print(f"wrote {OUT_DIR / (PROJECT + '.kicad_sch')}")
    print(f"symbols: {len(ref_counters)} kinds, refs: {ref_counters}")


if __name__ == "__main__":
    main()
