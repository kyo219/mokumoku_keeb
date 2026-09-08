# 参考資料・出典記録(References)

**公式資料を優先する。** 確認できていない内容を「確認済み」と記載しないこと。
外部設計を参考にした場合は、参考箇所・出典・ライセンスをこのファイルに追記する。

## 確認済み資料

### nice!nano v2(確認日: 2026-09-08)

出典: [nicekeyboards.com — nice!nano Docs](https://nicekeyboards.com/docs/nice-nano/) / [Pinout and Schematic](https://nicekeyboards.com/docs/nice-nano/pinout-schematic)(公式ピン配置図 pinout-v2.png・回路図画像を目視確認)

- MCU: nRF52840(Flash 1MB / RAM 256KB)
- USB-Cはミッドマウントで基板全体厚 **3.2mm**
- 使用可能GPIO: ヘッダー18ピン + 裏面パッド3ピン(P1.01 / P1.02 / P1.07)= **計21ピン**(裏面にSWC/SWDパッドもあり)
- ピン配置(公式図より。D番号=Pro Micro互換名):
  - 左列(上→下): GND, **D1=P0.06**, **D0=P0.08**, GND, GND, **D2=P0.17**, **D3=P0.20**, **D4=P0.22**, **D5=P0.24**, **D6=P1.00**, **D7=P0.11**, **D8=P1.04**, **D9=P1.06**
  - 右列(上→下): **BATTERY+**, **BATTERY+**, GND, **RESET**, **3.3V(VCC)**, **D21=P0.31**, **D20=P0.29**, **D19=P0.02**, **D18=P1.15**, **D15=P1.13**, **D14=P1.11**, **D16=P0.10**, **D10=P0.09**
- 電源・充電:
  - 3.7V LiPo前提。充電電流は標準 **約100mA**、基板上の「BOOST」ジャンパをブリッジすると **約500mA**(**500mAh超のバッテリーのみ**。公式が小容量への使用を明確に警告)
  - **P0.13をLowにすると3.3V VCCピンの出力を遮断**できる(オンボードMOSFET、外部部品の待機電力削減用)
  - 回路図はブロックとして「Charging and Power Path」「VCC Regulator and Cut Off」「USB Port」「Status LED」を確認(個別部品定数までは画像解像度の都合で未確認)
- バッテリー残量: ZMK公式ボード定義で `zmk,battery-nrf-vddh`(VDDH電圧測定)を使用 → **ADC用GPIOを消費しない**(v1のP0.04測定とは異なる)
- ⚠️ 未確認のまま: アンテナkeep-outの公式推奨寸法(公式ドキュメントに記載を発見できず)、公式の電源スイッチ推奨接続位置

### nice!view(確認日: 2026-09-08)

出典: [nicekeyboards.com — nice!view Docs](https://nicekeyboards.com/docs/nice-view/) / Pinout and Schematic(公式ピン配置図・寸法図を目視確認)

- 外形: **14mm × 36mm**(V-Cutにより+0.1〜0.2mmの可能性、公式図注記)、基板厚約1mm+ディスプレイ約1mm
- ピン: **5ピン、左から MOSI, SCK, VCC, GND, CS**、ピッチ **2.54mm**、端から1.92mm
- ディスプレイ: Sharpメモリ液晶(LS0xx系)**160×68**、SPI(ZMK定義で最大1MHz)、**CSはactive-high**、MISO不要
- OLED互換ソケットで使う場合はCSをD1へ配線する慣例(本プロジェクトはネイティブ5ピン接続なので該当せず)

### ZMK公式リポジトリ(確認日: 2026-09-08)

出典: [github.com/zmkfirmware/zmk](https://github.com/zmkfirmware/zmk)(mainブランチ、**MITライセンス**)

- `app/boards/nicekeyboards/nice_nano/nice_nano_nrf52840_zmk_2_0_0.overlay`:
  - `EXT_POWER` ノード = **P0.13 / GPIO_ACTIVE_HIGH**(VCC遮断制御)
  - バッテリー = `zmk,battery-nrf-vddh`
- `app/boards/shields/nice_view/nice_view.overlay`: `sharp,ls0xx` 160×68、SPI max 1MHz
- `app/boards/shields/nice_view_adapter/boards/nice_nano_nrf52840_zmk.overlay`(**標準ピン割り当て**):
  - SCK = P0.20(D3)、MOSI = P0.17(D2)、CS = pro_micro 1(D1=P0.06、active-high)、MISO = P0.25(ダミー、ヘッダー外)
- Helix / Corne 等のshield定義が同リポジトリに存在し、split構成の実装例として参照可能

### Kailh MXホットスワップソケット PG151101S11(確認日: 2026-09-08)

出典: Kailh(Kaihua Electronics)Product Specification KH-PS1607-10 Rev.B([keyboardio/keyswitch_documentationミラー](https://github.com/keyboardio/keyswitch_documentation/blob/master/datasheets/Kailh/PG151101S11-MX-Socket.pdf)。通称CPG151101S11)

- 本体高さ(PCB裏面からの突出): **1.85±0.1mm**、本体外形 10.90×5.89mm、厚み方向断面 3.05mm(端子部含む)
- スイッチピン受け穴: Ø3.00mm×2(水平間隔6.35mm、垂直オフセット2.54mm)— MXピン位置と一致
- **推奨PCBレイアウトは基板厚1.6mm(単面)前提**と明記 → 1.2mm化の検証課題の根拠
- 定格: 12V/10mA max(信号用)、挿抜寿命100サイクル、手はんだ350℃/3秒以内

### Alps Alpine スライドスイッチ SSSS811101(確認日: 2026-09-08)

出典: [Alps Alpine公式製品ページ](https://tech.alpsalpine.com/e/products/detail/SSSS811101/)

- 単極・2ポジション、表面実装(リフロー)、本体 6.7×2.6×1.4mm、アクチュエータ高1.1mm、トラベル1.5mm
- **定格 0.3A 5V DC max** / 50μA 3V DC min、動作温度 -40〜+85℃
- ⚠️ 流通サイトの寸法表記(7.7×5×1.9mm等)と公式値に差異あり(端子込み外形の可能性)。**公式PDF図面での照合をフットプリント作成時に必須とする**

### JST PHコネクタ(確認日: 2026-09-08)

出典: [JST公式データシート ePH.pdf](https://www.jst-mfg.com/product/pdf/eng/ePH.pdf)、[DigiKey製品ページ](https://www.digikey.com/en/products/detail/jst-sales-america-inc/S2B-PH-SM4-TB/926655)

- PHシリーズ: 2.0mmピッチ、定格2A/100V AC・DC、-25〜+85℃
- S2B-PH-SM4-TB(LF)(SN): 2ピン・表面実装・横型(サイドエントリー)
- ⚠️ **極性は規格で定まらない**。購入バッテリーの実物極性確認が必須(ADR-0003)

### 1N4148W ダイオード(確認日: 2026-09-08)

出典: [Diodes Inc. 製品ページ](https://www.diodes.com/part/view/1N4148W)、[MCC データシート](https://www.mccsemi.com/pdf/Products/1N4148W(SOD-123).pdf)ほか複数メーカー

- 小信号高速スイッチングダイオード、SOD-123、VR 75V / VRRM 100V、IF 150mA、trr約4ns
- 複数メーカーが製造するセカンドソース定番品

## 今後確認すべき資料(未確認)

| # | 資料 | 確認したい内容 | 状態 |
| --- | --- | --- | --- |
| 1 | nice!nanoアンテナkeep-out実例 | 実績あるnice!nanoボード(FelixKeeb等)のkeep-out寸法実例(暫定方針はADR-0007) | 未確認 |
| 2 | ZMK公式ドキュメント(zmk.dev) | split詳細設定、peripheral電池残量のcentral集約表示のサポート状況、省電力設定 | 未確認 |
| 3 | Cherry MX(または互換)公式寸法資料 | プレート開口、プレート〜PCB距離、ピン位置(3/5ピン)、センターポスト径 | 未確認 |
| 4 | Alps SSSS811101 公式PDF図面 | フットプリント寸法・ノブ形状(公式ページ数値は確認済み。流通表記との差異解消) | 未確認 |
| 5 | コンスルー(Mac8)公式図面 | 型番、高さ(2.5/3.5mm)、対応基板厚、推奨穴径(ADR-0006の確定条件) | 未確認 |
| 6 | Mill-Max 315系ソケット図面 | 代替ソケットの高さ・穴径(コンスルー不適合時の代替) | 未確認 |
| 7 | LiPoバッテリー仕様(型番未定) | 寸法、容量(≤500mAh方針、ADR-0004)、保護回路、コネクタ極性 | 未確認 |
| 8 | nice!view用5ピン低背ソケットの図面 | 高さ(積層クリアランス計算後に選定) | 未確認 |
| 9 | P0.09/P0.10(D10/D16)のNFCピン扱い | nice!nanoボード定義でGPIO化済みかの確認(nfct-pins-as-gpios) | 未確認 |

## 参考にする公開設計(参考のみ。無断複製禁止)

| 設計 | 参考にしたい点 | ライセンス | 参照状況 |
| --- | --- | --- | --- |
| FelixKeeb | 薄型MX+無線構成の考え方 | 未確認 | 未参照(今後確認) |
| Helix | 左右分割・リバーシブルPCBの構成 | 未確認 | ZMK shield定義のみ参照(MIT) |
| Corne (crkbd) | split+nice!nano/nice!view運用、ZMK shield構成 | 未確認 | ZMK shield定義のみ参照(MIT) |

**運用ルール:**

- 実際に参照した時点で、参照したリビジョン/URL・参考にした具体的箇所・ライセンス条項をこの表に記録する。
- 回路・フットプリント・基板データをそのまま流用する場合は、ライセンスが許諾しているかを確認し、必要な帰属表示を行う。
- 「参考にした」と「流用した」を区別して記録する。
