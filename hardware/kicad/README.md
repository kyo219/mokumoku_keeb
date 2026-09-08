# hardware/kicad/

KiCadの**編集可能なソース**を置くディレクトリ。KiCad 10.0系を使用(`~/Applications/KiCad`)。

## 構成

- `left/` — **左基板プロジェクト(正)**。回路図はRev.Aドラフトあり(`scripts/generate_left_schematic.py` で生成、ERC 0違反・ネットリスト自動照合済み)。PCBは未着手
- `symbols/` — プロジェクト固有シンボル(`mokumoku_keeb.kicad_sym`: nice_nano_v2 = 公式ピン配置図と照合済み)
- `footprints/` — プロジェクト固有フットプリント(`.pretty`、まだなし)
- `3dmodels/` — 3Dモデル(まだなし)
- 右基板は左のミラーとして後続フェーズで生成(ADR-0001)

## 置かないもの

- Gerber・ドリル・BOM・座標データなどの**生成物** → `production/<revision>/` へ(AGENTS.md参照)

## ルール

- フットプリントは実部品データシートと照合し、検証状態を記録してから製造に使用する(未検証フットプリントの製造使用は禁止)。
- 外部ライブラリ由来のシンボル・フットプリントは出典とライセンスを `docs/references.md` に記録する。
- ERC/DRCを通してから製造候補とする。
