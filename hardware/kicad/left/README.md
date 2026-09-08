# hardware/kicad/left/ — 左基板KiCadプロジェクト

左半分(正)のKiCadプロジェクト。**回路図・PCBともスクリプトによる生成物**であり、結線・配置の手編集は禁止(変更はADR・docs・スクリプトを同時更新して再生成)。

- `mokumoku_keeb_left.kicad_sch` — 回路図(`scripts/generate_left_schematic.py` の生成物、フットプリント割り当て済み)
- `mokumoku_keeb_left.kicad_pcb` — PCB(`scripts/generate_left_pcb.py` の生成物。**配置+外形+アンテナkeep-outまで。配線は未着手**)
- `mokumoku_keeb_left.kicad_pro` / `sym-lib-table` / `fp-lib-table` — プロジェクト設定とライブラリ参照

## 検証

```
python3 scripts/generate_left_schematic.py   # 回路図再生成
python3 scripts/verify_left_netlist.py       # ネットリストをADR-0002と自動照合
kicad-cli sch erc ...left.kicad_sch          # ERC(現在0違反)
<KiCad付属python3> scripts/generate_left_pcb.py   # PCB再生成
kicad-cli pcb drc ...left.kicad_pcb          # DRC(現在: 未配線92件のみ、他0違反)
```

## 状態・注意

- **Rev.Aドラフト。配線未着手であり製造可能ではない。**
- PCBの内容: 28キー(19.05mmグリッド、R0C0=(50,50))、裏面ダイオード、nice!nano(アンテナ=上端向き、ADR-0007)、nice!view用5ピンヘッダ、JST(裏面・C6タブ下部)、切り欠き外形、アンテナkeep-out rule area
- **SW29(スライドスイッチ)・SW30(リセット)は未配置**(検証済みフットプリントがないため。Alps図面入手・リセット部品選定後に配置)
- JST極性は「pin1=+」の**仮置き**(回路図上に注記あり)。実バッテリー確認後に確定(ADR-0003)。
- 右基板は本プロジェクトのミラーとして後続フェーズで生成する(ADR-0001)。
