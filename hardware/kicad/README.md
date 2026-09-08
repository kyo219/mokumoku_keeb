# hardware/kicad/

KiCadの**編集可能なソース**を置くディレクトリ。回路図・PCBは**まだ作成していない**(初期整備フェーズ)。

## 置くもの

- KiCadプロジェクト(`.kicad_pro` / `.kicad_sch` / `.kicad_pcb`)— 追跡対象
- `symbols/` — プロジェクト固有のシンボル
- `footprints/` — プロジェクト固有のフットプリント(`.pretty`)
- `3dmodels/` — 3Dモデル

## 置かないもの

- Gerber・ドリル・BOM・座標データなどの**生成物** → `production/<revision>/` へ(AGENTS.md参照)

## ルール

- フットプリントは実部品データシートと照合し、検証状態を記録してから製造に使用する(未検証フットプリントの製造使用は禁止)。
- 外部ライブラリ由来のシンボル・フットプリントは出典とライセンスを `docs/references.md` に記録する。
- ERC/DRCを通してから製造候補とする。
