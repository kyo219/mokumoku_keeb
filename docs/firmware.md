# ファームウェア方針(ZMK)

ファームウェアは**ZMK**を使用する。
**この段階では、動作未確認の完成版ZMK設定を作らない。** GPIO割り当て確定後に実装する。

## split構成

- 左右それぞれのnice!nano v2にZMKを書き込む。
- ZMKのsplit機能で、片側が**central**(ホストとBLE HID接続し、peripheral側の入力を統合)、
  もう片側が**peripheral**(キー入力をcentralへBLE送信)となる。
- ZMKの慣例では左がcentralだが、どちらにするかは未確定(バッテリー消費が非対称になる点を考慮して決定)。
- ハードウェアは左右対称とし、central/peripheralはビルド設定でのみ区別する。

## 論理配置

- 全56キー(片側28キー)。物理配置は [key-layout.md](key-layout.md) を一次情報とする。
- **物理配置と論理マトリクスを分離する**:
  - kscanのrow/col構成は電気設計([electrical.md](electrical.md))で決まる(物理の5行×7列と一致しなくてよい)
  - matrix transform で kscan座標 → キーマップ位置へ変換する
  - 右半分はtransformのcol-offset(またはミラー定義)で吸収する

## nice!view対応

- ZMKのnice!view shield機構を利用する(`nice_view`アダプタ相当の構成)。
- SPIピン割り当てはZMK既定と実配線の整合を確認する(GPIO確定後)。

## バッテリー残量表示

- nice!nanoのバッテリー電圧監視(ADC)を有効化し、nice!view上に残量表示する。
- split両側の残量をcentral側へ集約表示する機能(peripheral battery proxy/fetching)は、使用するZMKバージョンでのサポート状況を確認してから採用する。

## 今後必要になる成果物

1. **Shield定義**(`firmware/zmk/` 配下、後続フェーズで作成):
   - `Kconfig.shield` / `Kconfig.defconfig`
   - `<shield>.dtsi`(kscan、matrix transform、physical layout)
   - `<shield>_left.overlay` / `<shield>_right.overlay`(GPIO、nice!view SPI)
   - `<shield>.keymap`(初期キーマップ)
   - `<shield>.conf`(スリープ・バッテリー監視等の設定)
2. GitHub ActionsによるZMKビルド設定(zmk-config形式にするかは未確定)

## GPIO割り当て確定後に作業する項目

- [ ] kscan設定(row/col GPIO、diode direction)の記述
- [ ] matrix transformの記述(56キー、左右オフセット)
- [ ] nice!view SPI設定の記述
- [ ] バッテリーADC設定
- [ ] スリープ・省電力設定(LED非搭載のためディスプレイとBLEが主な消費源)
- [ ] 初期キーマップ作成(追加1uキーは汎用キーとして扱う)
- [ ] 実機でのビルド・書き込み・動作確認([bring-up.md](bring-up.md))

## 制約

- Raspberry Pi Pico / RP2040 は使用しない(nRF52840のみ)。
- OLED対応は不要(nice!view専用)。
- 動作確認まで「動作する設定」と表記しない。
