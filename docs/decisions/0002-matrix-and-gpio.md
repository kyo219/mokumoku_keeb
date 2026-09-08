# ADR-0002: マトリクスは物理一致の5行×7列、GPIO割り当てはZMK標準準拠

## Status

**Accepted**(2026-09-08 ユーザー承認)

## Context

片側28キー(物理配置は4×6+3+1、[../key-layout.md](../key-layout.md))をスキャンするマトリクス配線と、nice!nano v2のGPIO割り当てを決める必要がある。

前提(公式資料確認済み、[../references.md](../references.md)):

- nice!nano v2のヘッダー使用可能GPIOは18本
- バッテリー残量はVDDH測定のためADC用GPIO不要
- ZMK公式のnice!view標準ピンは CS=D1、MOSI=D2、SCK=D3

## Decision

1. **マトリクスは物理配置に沿った行線5本(R0–R4)+列線7本(C0–C6)= GPIO 12本**とする。35交点のうちキーのない7交点(R0–R2×C6、R4×C3–C6)にはスイッチ・ダイオードを置かない。
2. **GPIO割り当て**(左右共通):

| 用途 | ピン |
| --- | --- |
| nice!view CS / MOSI / SCK | D1(P0.06)/ D2(P0.17)/ D3(P0.20)— ZMK標準 |
| Row0–Row4 | D4(P0.22)、D5(P0.24)、D6(P1.00)、D7(P0.11)、D8(P1.04) |
| Col0–Col6 | D9(P1.06)、D10(P0.09)、D16(P0.10)、D14(P1.11)、D15(P1.13)、D18(P1.15)、D19(P0.02) |
| 予備(テストパッド候補) | D0(P0.08)、D20(P0.29)、D21(P0.31) |

3. diode directionは **col2row を第一候補**とする(kscan設定確定時に回路図と同時レビュー)。

## Alternatives

| 案 | 概要 | 不採用理由 |
| --- | --- | --- |
| 4行×7列への詰め替え(11 GPIO) | 追加行R4の3キーを電気的に別行へ折り込みGPIOを1本節約 | GPIOに余裕があり節約の必要がない。物理と電気の座標がズレて配線が交差し、手実装・デバッグ時の追跡性が下がる |
| nice!viewを独自ピンに配置 | 配線自由度が上がる | ZMK標準(`nice_view_adapter`)から外れ、shield定義の流用性が下がる |

## Consequences

- 良い点: 基板配線が物理配置と一致し、テスターでの検証・bring-upが容易。ZMKのnice!view関連設定を標準のまま使える。予備3ピンをテストパッドに回せる。
- 悪い点: 4×7比でGPIOを1本多く使う(実害なし)。
- 注意: **PCB配線の都合でRow/Col個別ピンの入れ替えはあり得る**。その場合は回路図・[../electrical.md](../electrical.md) のGPIO表・ZMK設定を同時更新する(AGENTS.mdルール)。nice!viewの3ピンは標準維持のため入れ替え対象外。
- 波及: [../electrical.md](../electrical.md)(GPIO表確定)、[../firmware.md](../firmware.md)(kscan/transform作業が着手可能に)。

## Verification

- D10(P0.09)/D16(P0.10)はNFC兼用ピン。nice!nanoボード定義でGPIO化されていること(nfct-pins-as-gpios相当)をZMKビルド時に確認する([../references.md](../references.md) 未確認#10)。
- 回路図完成時、ダイオード方向とkscan設定の一致をレビュー(設計チェックリスト)。
- bring-up手順7–8(単キー→全キーマトリクス)で実機検証する。
