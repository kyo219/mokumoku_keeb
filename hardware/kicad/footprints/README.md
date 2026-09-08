# footprints/ — フットプリントと検証状態

**未検証のフットプリントを製造用に使用しない**(AGENTS.md)。使用するフットプリントは必ずこの表で状態を管理する。

カスタム品は `mokumoku_keeb.pretty/`(`scripts/generate_footprints.py` の生成物。手編集禁止、変更はスクリプト側で)。

| 部品 | フットプリント | 出所 | 検証状態 |
| --- | --- | --- | --- |
| MXスイッチ+Kailhホットスワップ | `mokumoku_keeb.pretty/SW_MX_HotSwap_Kailh_PG151101S11_1u` | 自作(Cherry MX公式+Kailh公式データシートから生成) | **図面照合済み**(穴位置=Cherry公式、Ø3.0ソケット穴=Kailh公式、pcbnewで座標を数値検証)。⚠️ SMDパッドの張り出し量(±3.175mm)は図面からの導出値 → **実物ソケットで発注前に要確認** |
| nice!nano v2(ソケット) | `mokumoku_keeb.pretty/nice_nano_v2` | 自作(2.54mmピッチ、行間15.24mm=Pro Micro慣例) | **暫定**。ピン番号=プロジェクトシンボルと一致(数値検証済み)。⚠️ ドリル1.0mmは**コンスルー公式図面で要確認**(ADR-0006)。外形・アンテナ領域は近似値 → 実物採寸で確定 |
| バッテリーコネクタ | `Connector_JST:JST_PH_S2B-PH-SM4-TB_1x02-1MP_P2.00mm_Horizontal`(KiCad標準) | KiCad公式ライブラリ(ePH.pdf準拠と明記) | **図面照合済み**(ピッチ2.0±0.05・補強パッド1.5×3.4が公式図面と一致)。⚠️ **極性(pin1=+の仮置き)は実バッテリーで要確認**(ADR-0003) |
| ダイオード 1N4148W | `Diode_SMD:D_SOD-123`(KiCad標準) | KiCad公式ライブラリ | **採用可**(SOD-123標準パッケージ。メーカー推奨パッドとの差異は手はんだ用途で許容) |
| nice!view 5ピン | `Connector_PinHeader_2.54mm:PinHeader_1x05_P2.54mm_Vertical`(KiCad標準) | KiCad公式ライブラリ | **採用可**(標準2.54mmピッチ)。ソケット高さ選定はADR-0006 |
| 電源スライドスイッチ SSSS811101 | **未作成** | — | **Alps公式PDF図面が未入手のため作らない**(推測で作成しない方針)。図面入手後に作成・照合 |
| リセットボタン | **未作成** | — | 型番未定のため未作成 |

## 検証ワークフロー

```
python3 scripts/generate_footprints.py     # カスタムFP再生成
# pcbnewで検証ボードに配置 → 座標数値チェック+PDF目視(scripts/内の手順参照)
```

発注前チェックリスト(docs/verification-checklist.md)で、上表の⚠️項目がすべて解消していることを確認すること。
