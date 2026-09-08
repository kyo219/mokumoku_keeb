# firmware/zmk/

ZMKのShield定義・設定を置くディレクトリ。方針は `docs/firmware.md` を参照。

**まだ実装していない。** GPIO割り当てが未確定のため、この段階では動作未確認の完成版ZMK設定を作らない方針(AGENTS.md参照)。

## 今後ここに置くもの

- Shield定義(`Kconfig.shield` / `Kconfig.defconfig` / `.dtsi` / `_left.overlay` / `_right.overlay` / `.keymap` / `.conf`)
- ビルド設定(zmk-config形式にするかは未確定)

## ルール

- ピン割り当てを変更したら、回路図・`docs/electrical.md` のGPIO表と**同時に**更新する。
- キーマップ・matrix transformは `docs/key-layout.md`(片側28キー、物理と論理の分離)と整合させる。
