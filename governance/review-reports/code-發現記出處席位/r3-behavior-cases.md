# r3 待驗案例(修前 af2fb6f85 → 修後 aff4a913c)

案例只是待驗範圍,不是「已修好」的證據;新席自己跑兩版核對,可補案例。測試指令 `python3.14 scripts/test_lumos.py -k <關鍵字>`。

| 組 | 角色 | 待驗行為 | 出處 |
|---|---|---|---|
| G1 | repair | 三種 `--finding-seat` 擋下與推遲提醒都在原處呼叫 `_gate_event_or_warn`,迴圈名與席名過 `_esc_clean`;推遲時治理帳多一筆 `finding-seat-since-overridden` | 鄰居 `refuted-set-missing` 寫法 |
| G1 | preserve | 三種擋下事件照舊各留一筆、rc2、帳不變 | 計劃 S1、S3 |
| G2 | repair | 十萬字元席名的 `gov --stats` 10 秒內跑完 | 席位量測 |
| G3 | repair | `正確性-2-sonnet`、`外家codex-5-mini`、`外家codex-6-mini` 原樣分列;` 空白席-sonnet ` 與 `空白席-sonnet` 併成一列 | 計劃〈做法〉統計 |
| G3 | preserve | `架構對齊r2-sonnet`、`外家finder2-codex`、gemini-2/3 照舊 | 計劃 S8 |
| G4 | repair | 本筆早於生效日時帳上有壞時間列也不擋;覆寫 `2999-01-01` 放行 | 計劃〈回退〉「變回選填」 |
| G4 | preserve | 本筆不早於生效日、帳上有壞時間列 → rc2 留 `finding-seat-badts`;首筆早於生效日不必填 | 計劃 S6 |
| G5 | repair | `--help` 寫明要跟 --loop 一起給;三份手冊「目前 YYYY-MM-DD」等於常數 | 計劃 S12 |

文件類:SKILL.md 第 6 步完整指令、reference.md 第 38 行與範本行尾續行、系統筆記新增說明,核對跟程式一致。
