# scripts/

補助スクリプト。標準ライブラリのみ使用(現状は追加依存なし。必要になったらuvで環境構築)。

| スクリプト | 役割 |
| --- | --- |
| `generate_left_schematic.py` | ADR-0002のマトリクス/GPIO定義から左基板回路図(`hardware/kicad/left/`)を生成。**回路図は生成物、こちらが編集対象**。ピン変更時はADR/electrical.mdと同時更新して再生成する |
| `verify_left_netlist.py` | 生成した回路図のネットリストをkicad-cliで書き出し、ADR-0002の期待結線(全COL/ROW/nice!view/電源ネット)と自動照合する |

前提: KiCad 10が `~/Applications/KiCad/` にあること。

```
python3 scripts/generate_left_schematic.py
python3 scripts/verify_left_netlist.py
~/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli sch erc --severity-all \
  hardware/kicad/left/mokumoku_keeb_left.kicad_sch
```
