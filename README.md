# mokumoku-keeb(仮称)

左右分割型・ワイヤレス・オーソリニアキーボードの設計リポジトリです。

> **注意**: `mokumoku-keeb` はリポジトリ名由来の仮slugです。正式な製品名は未定です。

## 現在の開発段階

**初期整備フェーズ(設計段階)** — 要件定義とドキュメント整備を行っている段階です。
KiCadの回路図・PCB、ケースCAD、製造データはまだ存在しません。**製造検証前であり、発注可能な状態ではありません。**

## 主な仕様

- 左右分割型オーソリニア配列(列スタッガー・キー回転なし)
- **片側28キー / 左右合計56キー**、全キー1u、キーピッチ19.05mm
- Cherry MX互換スイッチ(通常高さ、3ピン/5ピン対応)+ **Kailh MXホットスワップソケット**
- マイコン: **nice!nano v2**(または互換のPro Micro形状nRF52840)を左右に各1基、ソケット実装
- ディスプレイ: **nice!view**(左右各1、ソケット実装、nice!nanoの上に積層)
- ファームウェア: **ZMK**
- 接続: **Bluetooth LE**(ホスト接続・左右間ともに無線。TRRSケーブル不使用)
- 電源: 左右独立の3.7V LiPoバッテリー + 2ピンJSTコネクタ、USB-C充電
- **LED非搭載**(キーLED・RGB・アンダーグローなし)— 省電力・薄型化を優先
- MX互換を維持したまま可能な限り薄い、薄型サンドイッチ構造を基本案とする

## ドキュメント

| ドキュメント | 内容 |
| --- | --- |
| [docs/product-requirements.md](docs/product-requirements.md) | **仕様の一次情報**。確定要件・未確定事項の整理 |
| [docs/key-layout.md](docs/key-layout.md) | キー配列の定義(論理座標・ミラー規則) |
| [docs/architecture.md](docs/architecture.md) | システム構成図 |
| [docs/electrical.md](docs/electrical.md) | 電気設計(確定事項と検討中の候補) |
| [docs/mechanical.md](docs/mechanical.md) | 機構設計(プレート・ケース・積層) |
| [docs/firmware.md](docs/firmware.md) | ZMKファームウェア方針 |
| [docs/manufacturing.md](docs/manufacturing.md) | 製造方針(Rev.A) |
| [docs/bring-up.md](docs/bring-up.md) | 初号機のbring-up手順 |
| [docs/verification-checklist.md](docs/verification-checklist.md) | 3段階の検証チェックリスト |
| [docs/references.md](docs/references.md) | 参考資料・公式資料・ライセンス記録 |
| [docs/decisions/](docs/decisions/) | 設計判断のADR |
| [docs/revisions/rev-a.md](docs/revisions/rev-a.md) | Rev.Aの記録 |

## リポジトリ構成

```
.
├── AGENTS.md                 # AI・開発者向けの編集ルール
├── README.md
├── docs/                     # 仕様・設計ドキュメント(上表参照)
├── hardware/kicad/           # KiCadソース(回路図・PCB・プロジェクト固有ライブラリ)
├── mechanical/               # ケース・プレートのCADと出力物
├── firmware/zmk/             # ZMK設定・Shield定義
├── production/               # 発注用に凍結した製造データ(リビジョン別)
├── scripts/                  # 補助スクリプト
└── assets/renders/           # レンダリング画像等
```

このリポジトリを編集する際は、まず [AGENTS.md](AGENTS.md) を読んでください。
