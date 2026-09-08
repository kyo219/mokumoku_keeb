# hardware/kicad/left/ — 左基板KiCadプロジェクト

左半分(正)のKiCadプロジェクト。**回路図は `scripts/generate_left_schematic.py` による生成物**であり、結線の手編集は禁止(変更はADR-0002・electrical.md・スクリプトを同時更新して再生成)。

- `mokumoku_keeb_left.kicad_sch` — 回路図(生成物)
- `mokumoku_keeb_left.kicad_pro` — プロジェクト設定(KiCadでの編集は可)
- `sym-lib-table` — プロジェクトシンボルライブラリ(`../symbols/`)の参照

## 検証

```
python3 scripts/generate_left_schematic.py   # 再生成
python3 scripts/verify_left_netlist.py       # ネットリストをADR-0002と自動照合
kicad-cli sch erc mokumoku_keeb_left.kicad_sch  # ERC
```

## 状態・注意

- **Rev.Aドラフト。フットプリント未割り当て・PCB未着手。製造可能ではない。**
- JST極性は「pin1=+」の**仮置き**(回路図上に注記あり)。実バッテリー確認後に確定(ADR-0003)。
- 右基板は本プロジェクトのミラーとして後続フェーズで生成する(ADR-0001)。
