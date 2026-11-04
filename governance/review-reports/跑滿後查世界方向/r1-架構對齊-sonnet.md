severity: major

這份設計大體沿用 `_cap_retro_check` 的骨架,只有一處在同一支檢查器內引入第二套字數口徑(major)。其餘是命名、提醒訊息與落點上的小出入(minor)。

## 1. 分層與依賴方向:對齊

- 新欄位的驗證放進 `_cap_retro_check`(`scripts/lumos:22399`)。這支本來就是 `--check` 與 `_cap_retro_status`(`scripts/lumos:22547` 起)共用的唯一檢查入口,設計沒有另開檢查函式。
- 骨架改在 `cmd_loop_retro` 的 `--template` 分支(`scripts/lumos:22905`),人裁種類走已有的 `decision` 參數。
- 提醒印在 `--record` 成功之後(`scripts/lumos:22977`)。成功路徑已經拿到 `_data`,所以不用新增跨層呼叫。
- `_loop_ts_key`(`scripts/lumos:19357`)是同檔、位置在前的工具,依賴方向沒有倒過來。
- 沒有發現跨層直呼。

## 2. 命名與錯誤處理:大致對齊,有三處小出入

對齊的部分:
- `verdict` 的三個值用 kebab-case 英文。`_RETRO_FAMILIES` 和 `_RETRO_DECISIONS` 也是這個寫法(`scripts/lumos:22119-22122`)。
- 逐欄列錯的格式「欄位路徑: 原因」同既有的 `bad(f"{tag}.x", …)`(`scripts/lumos:22456-22500`)。
- 先驗型別再往下驗,也同既有的 `isinstance … continue` 寫法。

不對齊的三處:

1. 設計沒有說 `verdict` 的三個值要不要放成模組常數。鄰居都是 `_RETRO_*` 元組,錯誤訊息固定寫「不在固定清單(…)」(`scripts/lumos:22460`、`22497`)。設計只說「只收」三個值,留下寫成行內字面值的空間。
severity: minor
blocking: 否
引句:「`verdict` 只收 `direction-ok`、`change-direction`、`undetermined`」

2. 提醒訊息沒有指定輸出串流與前綴。同函式裡給人看的提示一律走 stderr 並帶 `[retro]` 前綴(`scripts/lumos:22942-22945`)。成功行 `✓ 已記回顧` 走 stdout(`scripts/lumos:22977`)。設計的那行提醒不屬於這兩種,S5 也沒說印去哪。
severity: minor
blocking: 否
引句:「`--record` 成功、`verdict` 是 `change-direction` 時多印一行」

3. 主觸發要寫的 intake 小節叫〈世界查證〉,但同一份 `rN-intake.md` 已經有〈先查世界〉。後者是使用者 2026-11-02 裁定的每輪修補前查證,見 `docs/lumos-toolchain-knowledge/Systems/每輪修補差異派工.md:20`。同一份檔案裡會有兩個名字相近的查證小節。
severity: minor
blocking: 否
引句:「結論與來源寫進 rN-intake.md 的〈世界查證〉」

## 3. 第二種做法:字數口徑算第二套(major),其餘對齊

**字數口徑,不對齊。**
- `_cap_retro_check` 裡所有字數門檻都走 `_retro_text_ok`(`scripts/lumos:22395`)。它對非字串回 False,不丟例外。用到的地方有 `scripts/lumos:22467`、`22483`、`22507`、`22509`。
- 設計讓同一支檢查器出現第二把尺:新欄位改用 `_real_chars`(`scripts/lumos:13923`)。它遇到非字串會丟例外,所以設計又得另加一段「先驗型別」。
- 同一支函式裡會出現兩種「20 字」。`why_cap` 與 `avoid` 的 20 字是去頭尾空白後的長度,`world_check.note` 的 20 字是去掉標點空白後的字元數。
- `_real_chars` 在 repo 裡確實有先例,用在已排除理由與回頭條件結案理由(`scripts/lumos:13920`、`54354`)。但那是別的檢查器,不是回顧檢查器。
- 設計自己承認這是刻意的差異,所以標 ⚠。若要保留,應該在檢查器內收斂成一個口徑,或把理由寫進 `Systems/loop-retro`。
severity: major
blocking: 是
引句:「新欄位刻意用 `_real_chars` 擋全標點的湊字」
file: `scripts/lumos:22483`

**生效日錨點,小出入。**
- 設計說「寫法同 `_SPEC_GATE_SINCE`」。常數格式(帶時區的完整時間戳)與「解不開當成生效日之後」這兩點確實同(`scripts/lumos:14999`)。
- 但鄰居的 `*_SINCE` 全是拿迴圈首筆審查帳時間(`_loop_first_ts_key`)去比(`scripts/lumos:3517`、`14999`、`35288`)。這份設計改拿最新人裁事件的 `ts`,設計沒說為什麼不沿用首筆帳。
- 理由看起來合理,因為回顧檔綁的是人裁。但「同 `_SPEC_GATE_SINCE`」這句話只對常數成立,錨點是新的。
- 另外,`_loop_ts_key` 對非字串的 `ts` 會丟 `AttributeError`,設計沒提這點。
severity: minor
blocking: 否
引句:「寫法同 `_SPEC_GATE_SINCE`,值取合併日的隔天零點」

**網址檢查,對齊。** repo 沒有現成的網址驗證函式,設計自己寫 `http(s)://` 開頭不算第二套。

**版本升級,對齊。**
- 「收 1 或 2」有先例:vault 的 `schema_version` 也是 1 或 2(`scripts/lumos:7598-7601`)。
- 「版本號加日期」這個組合沒有先例,但每一半都有。

**量測方式,小出入。**
- 設計的回頭條件要數「人裁加開的迴圈裡 verdict 是換方向或判不準的次數」。
- 既有的跨迴圈彙整是 `cmd_loop_retro_stats`(`scripts/lumos:22981`),已經在彙整 families 與人裁種類(`scripts/lumos:23004` 附近)。設計沒有讓它彙整 verdict,到時得另用人工統計。
severity: minor
blocking: 否
引句:「人裁加開的迴圈裡世界查證結論是「要換方向」或「判不準」的次數為 0」

## 4. 落點:不對齊

- `lands_in` 只列 `Systems/loop-retro`,但設計要改的手冊檔,家不全在那裡。
- `skills/lumos-code-loop/SKILL.md`、`skills/lumos-code-loop/reference.md`、`skills/lumos-design-loop/templates.md` 的家是 `Systems/每輪修補差異派工`(about_code 在 `docs/lumos-toolchain-knowledge/Systems/每輪修補差異派工.md:10-13`)。既有的〈先查世界〉規則也寫在那篇。
- 專案規則第 5 條是「改了程式要寫說明就寫進改到那支檔的家」,計劃要寫 `lands_in`。
- 設計第 5 點只寫回 `Systems/loop-retro` 一處。主觸發是手冊規定,更該有一行寫進 `每輪修補差異派工`。
- 前一份計劃《審查跑滿回顧_計劃》的 `lands_in` 列了兩篇(`loop-convergence-recording` 與 `loop-retro`),做法是按實際改到的家列。
- ⚠ `lumos-design-loop/SKILL.md` 與 `reference.md` 我在 Systems 的 `about_code` 裡沒找到家,可能是無家的舊帳,請編排者用 `lumos doctor` 的 S8–S10 確認。
severity: minor
blocking: 否
引句:「`Systems/loop-retro` 補一行 WHY(世界查證欄、只在加開時必填、版本 2)」

不對齊共 7 條,其中 major 1 條。
