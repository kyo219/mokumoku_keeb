# scripts/

補助スクリプト。標準ライブラリのみ使用(現状は追加依存なし。必要になったらuvで環境構築)。

| スクリプト | 役割 |
| --- | --- |
| `generate_left_schematic.py` | ADR-0002のマトリクス/GPIO定義から左基板回路図(`hardware/kicad/left/`)を生成。**回路図は生成物、こちらが編集対象**。ピン変更時はADR/electrical.mdと同時更新して再生成する |
| `verify_left_netlist.py` | 生成した回路図のネットリストをkicad-cliで書き出し、ADR-0002の期待結線(全COL/ROW/nice!view/電源ネット)と自動照合する |
| `generate_footprints.py` | カスタムフットプリント(`hardware/kicad/footprints/mokumoku_keeb.pretty/`)を公式データシート由来の座標で生成。検証状態は footprints/README.md の表を参照 |
| `generate_left_pcb.py` | 左基板PCBを生成(KiCad付属python3で実行)。ネットリスト読込→28キー配置→裏面ダイオード→nano/view/JST配置→切り欠き外形→アンテナkeep-out。配線は含まない |
| `render_concept_layout.py` / `render_side_view.py` | 概観モック(上面・断面)を `assets/renders/` に生成 |

前提: KiCad 10が `~/Applications/KiCad/` にあること。

```
python3 scripts/generate_left_schematic.py
python3 scripts/verify_left_netlist.py
~/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli sch erc --severity-all \
  hardware/kicad/left/mokumoku_keeb_left.kicad_sch
```
