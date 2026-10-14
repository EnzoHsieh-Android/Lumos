severity: minor

我讀完修補差異,也在 lens-repo 原地跑了相關測試子集。這一輪沒有 major 以上的問題,只有兩條 minor。

跑過的子集:`dispatch_lens_hidden`、`dispatch_lens_hook`、`arch_target`、`question`、`pending`、`lookalike`、`invisible`、`lens_visible`、`residual`,全部 0 失敗。另用腳本實測了 `_lens_visible`、`_lens_text_cap` 和 `_arch_target_rule_show`。實驗放在 scratchpad 的 `cr-lr8-通才/`,沒有寫帳,沒有刪檔。

severity: minor
blocking: 否 — 只影響派工詞的顯示美觀,不影響判斷或安全
引句:「轉成看得見的 \\uXXXX(超出基本平面的 8 碼 \\UXXXXXXXX),換行照留。」
問題:`_lens_visible` 改成走 `_lens_hidden_char`,範圍是整張 Default_Ignorable 表。表裡有 U+FE0F(表情符號的變體選擇符)、U+200D(零寬連字)、U+00AD(軟連字號)。筆記或合約行裡的 ❤️、👨‍👩 這類正常寫法,進派工詞時會被拆成 `\ufe0f`、`\u200d`。審查席要「引原文」時,看到的字串和筆記原文對不上。這跟 `_pq_bad_char` 刻意放行 ❤️ 的寫法不一致,但派工詞本來就是保守出口,所以只算美觀問題。
失敗情境:合約行 `KEY:★INVARIANT★ ❤️ …` 進派工詞變成 `❤\ufe0f …`。我用 3000 行含 ❤️ 的文字實測,150000 個 FE0F 全部被跳脫。本 repo 目前只有 7 篇筆記含這幾個字,實際衝擊小。
佐證:file: `/Users/enzo/orca/workspaces/lumos-toolchain/lens-repo/scripts/lumos:17258`

severity: minor
blocking: 否 — 要超過 12 萬字才會觸發,而且有講明截了
引句:「    room = cap - len(note) - len(_FRAME_CLOSE) - 2」
問題:`_lens_text_cap` 從尾端截,而框外由工具寫死的必答指示都排在整段最後面,例如殘留的必答題和「審查時把上面的表態記錄當可反駁的宣稱」那句。超過 `_LENS_TEXT_MAX` 時,這些指示會先被截掉。截斷說明只講「後面的沒附」,沒講哪些指示不見了。
失敗情境:圖譜段加上殘留段超過 12 萬字(例如 5 條合約各掛很多殘留),text 被截。殘留的必答題 `_LENS_RESIDUAL_ASK` 若排在截點之後就不在派工詞裡,審查席不知道要逐條回答。實際上殘留段本身有 5 條合約、每條 12 筆指標的上限,12 萬字很難碰到,所以只列 minor。
佐證:file: `/Users/enzo/orca/workspaces/lumos-toolchain/lens-repo/scripts/lumos:51600`

已讀,無 finding:
- `_PQ_BLANK_LOOKALIKES` 加 U+303F、U+16FE4、U+13441、U+13442:
  - 它在待決問題那一側有 3 個用法:`_pq_bad_char`、`_pq_blank`、`_pq_leading_problem`。加字只讓這 4 個碼位被當成「看不見的空白」,值裡出現就被擋或視為空值,方向只會變嚴,不會放行更多。
  - 我 grep 過 `docs`、`scripts`、`skills`,這 4 個字只出現在 `scripts/test_lumos.py` 的測試樣本裡,沒有真實筆記含有。
  - question、pending、lookalike、invisible 子集全綠。
- `_kill_esc` 加 `hidden` 參數:預設 False,其餘約 40 個既有呼叫端行為不變。只有 `_lens_visible` 和 `_lens_name_esc` 帶 `hidden=True`。
- 主線的通才鏡頭範本 §7.9、推送前收集、回頭重讀指紋跟這支改動互不影響:
  - 這次改的是 `scripts/hooks/claude/dispatch-lens-hook.py`、`scripts/lumos` 和 `skills/lumos-design-loop/*`,沒有碰到 §7.9 或回頭重讀的程式。
  - `templates.md` §7.6 目標架構段的尾句要求引 ‹ › 之間的字,跟 `_ARCH_TARGET_TAIL` 一致。
  - §7.9 只換「審查鏡頭」第 4 點,不會跟尾句打架。
- 被改的既有測試期望,都是行為真的變了、不是把回歸改綠:
  - 掛鉤 S2:會談專案路徑從換行換成空白,改成名字顯示規則(包 ‹ ›、換行變 `\u000a`)。我讀過掛鉤實作,輸出確實如此。
  - `t_hook_swallowed_timeout`:`_mark("timeout"` 改找 `_mark_event("timeout"`。主線版掛鉤只有 `_mark(`,是這個分支自己改名的;「已附對應說明行」的鄰近斷言仍在。
  - `t_design_dispatch_shows_landing_sizes`:節點名加 ‹ ›,符合名字出口。
- 殘留段每條合約指標上限 12:穩定排序,「這次為什麼列」有原因的先列,被截掉的筆數有印;`_RESIDUAL_INDEX_REL` 已定義;呼叫端傳的是 list,沒有問題。
- `_arch_target_text`:
  - 字數分配、「規則沒附」、`attached`/`starved` 的計數邏輯我讀過,沒有發現越界或除零。
  - `_arch_target_split` 的 `and rs` 條件和 `_arch_target_spec_bt_paths` 換成字串判斷,我逐項對照舊正規式,語意相同。
  - `_arch_target_rule_show` 實測:從尾端剝掉 `[鍵:值]`,保留反引號、反斜線和 `list[int:3]`,規則只有欄位時回「(空名字)」。
- 掛鉤抄本與 lumos 的隱形字判定:`t_dispatch_lens_hidden_chars_every_codepoint` 對全碼位綠。一個附帶觀察不算 finding:掛鉤若在舊系統 python(Unicode 13)下跑,新版表情符號會被當成 Cn 跳脫。這是 r5 起就有的行為,這輪沒有新增。

最高等級 minor,blocking 0 條。
