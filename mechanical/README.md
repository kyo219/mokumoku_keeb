# mechanical/

ケース・プレートの機構設計を置くディレクトリ。設計方針は `docs/mechanical.md` を参照。
**CADデータはまだ作成していない**(初期整備フェーズ)。

| サブディレクトリ | 用途 |
| --- | --- |
| `cad/` | 編集可能なCADソース(FreeCAD / Fusion等。形式は未確定) |
| `plates/` | スイッチプレート(約1.5mm厚候補)の設計データ |
| `case/` | ケース(トップ・ボトム)の設計データ |
| `exports/` | STL / STEP / DXF などの出力物 |

- ソース(`cad/`)と出力物(`exports/`)を分離する。
- 発注に使う製造データは `production/<revision>/` へ凍結する(AGENTS.md参照)。
