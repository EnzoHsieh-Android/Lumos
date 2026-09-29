severity: minor

## F1 S3 守衛測試沿用「散落複本要對齊」的既有形狀,卻沒接既有 `_doc_sync` 命名慣例
severity: minor
blocking: 否
引句:「範本內容守衛應在三處都找到資料狀態的指路或子題標頭」
file: `docs/lumos-toolchain-knowledge/Projects/代碼審資料狀態鏡頭_計劃.md:67`
說明:S3([test:t_data_state_lens_mirrors])驗的是「同一件事的濃縮複本散落在 reference.md 兩處 + 代碼審 skill 步驟 2,要三處都對得上」——這正是本 repo 既有「散落同步要守衛」的那個形狀,既有三個實例(`t_marker_doc_sync`、`t_tension_doc_sync`、`t_security_seat_doc_sync`)全部用 `_doc_sync` 收尾命名。計劃第 9 點只解釋了 S1/S2(單篇缺項回報)為什麼**不**套 `t_tension_doc_sync` 那種形狀,理由成立;但沒有解釋 S3 明明是同一形狀,命名卻換成 `_mirrors`——這裡是命名沒對齊既有慣例,不是結構不對。
file: `scripts/test_lumos.py:6873`(`t_marker_doc_sync`)
file: `scripts/test_lumos.py:40152`(`t_tension_doc_sync`)
file: `scripts/test_lumos.py:41128`(`t_security_seat_doc_sync`)

## F2 lands_in 只列 pitfalls-code-loop,但改動面最大的檔案(範本第 1 點十行區塊)住在 design-loop skill 目錄下,判不準要不要也列 design-loop(⚠ 判不準,依嚴重度錨頂多 minor)
severity: minor
blocking: 否
引句:「代碼審派工詞的單一來源是 design-loop skill 的派工範本第 3 節」
file: `docs/lumos-toolchain-knowledge/Projects/代碼審資料狀態鏡頭_計劃.md:33`
file: `docs/lumos-toolchain-knowledge/Projects/代碼審資料狀態鏡頭_計劃.md:10`(lands_in 只列 `Systems/pitfalls-code-loop`)
說明:對照 §7.6 落點檢查點(`skills/lumos-design-loop/templates.md:267`「落點合不合理:計劃的 lands_in 列了現況要寫進哪幾篇」),本計劃九成改動(設計第 8 點整段十行圍欄)落在 `skills/lumos-design-loop/templates.md` 第 3 節,實體檔案在 design-loop skill 目錄下;但 `docs/lumos-toolchain-knowledge/Systems/design-loop.md` 與 `docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md` 的 `about_code` 欄位目前**都只列 `scripts/lumos`**,兩篇誰才是 `templates.md`/`reference.md`/`skills/lumos-code-loop/SKILL.md` 的家,圖譜裡查無正式登記(`about_code` 全 repo 沒有任何節點列出這三支檔)。計劃選 pitfalls-code-loop 可以用「這是代碼審的內容,只是借放在共用範本檔裡」自圓,但這屬於既有欠帳(每支檔有家 2026-09-11 只擋新增違規,不代表舊欠帳已有答案),不是這份材料自己講得清的問題,判不準,交編排者定。

不對齊共 2 條,其中 major 0 條。
