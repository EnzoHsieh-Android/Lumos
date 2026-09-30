severity: major

## F1 字眼表在工具裡另立一份,又規定「先改量測程式」,卻沒有機械釘住兩邊一致(既有先例有)
severity: major
blocking: 是
引句:「字眼表、邊界與過濾照量測程式 `neg_revisit_measure.py` 的常數與函式,只差〈與參考實作的刻意差異〉那幾條;要改字眼先改量測程式、重跑報告再改正式工具。」
file: `scripts/lumos:28640`(_DRIFT_M1_HIST_WORDS 抄自參考實作,註解寫明不引用 NEG_LEXICONS)、`scripts/test_lumos.py:55922`(逐字 54 個的釘)、`scripts/test_lumos.py:56765`(載入參考實作 old_sentence_exp.py 逐一比對)
1. 既有做法:舊句檢查 m1 同樣是「正式工具抄參考實作的表」,但有機械守衛——55922 釘表內容、56765 在測試裡直接載入參考實作模組跟正式函式逐一比對。
2. spec 的 S1 到 S5 釘的是例句,唯一跟量測程式比對的 S8 是 `[manual:…實作時寫一次性比對…]`,做完就沒了。窄表 20 個中文詞、4 個英文詞、固定組合 13 個、歷史 18 個、規則 9 個,共約 60 個字串會在 `scripts/lumos` 與 `governance/eval/negation-revisit/neg_revisit_measure.py` 兩處各存一份。
3. 失敗場景:有人為了降誤報在工具裡加一個歷史字眼(例如 spec 自己說「先改量測程式」的規則被略過),兩邊分岔。上線第 8 週照〈做法〉7 用量測程式重放,量出的準度與召回不再是工具實際行為,門檻判斷(≥70%、≥50%)用錯口徑,卻沒有任何測試變紅。等於引入第二種做法(手動比對取代既有的機械釘)。
4. 修法:S8 改成有 `[test:]` 的測試,載入量測程式(消費端沒有就跳過,同 56765 寫法),把正式表與量測程式的表、`classify_text` 對同一批例句的判定逐一比對;刻意差異第 1 到 3 條在測試裡列成明確例外。

## F2 歷史字眼表與 NEG_LEXICONS、_DRIFT_M1_HIST_WORDS 的關係 spec 完全沒交代
severity: minor
blocking: 否
引句:「歷史字眼(當時、原本、原先、曾、之前、以前、那時、起初、後來、已補、已修、修掉、改成、改為、已經有、現在有了、已上線、已做完)」
file: `scripts/lumos:28640`、`scripts/lumos:4293`
1. repo 現有兩份否定或歷史字眼表:`NEG_LEXICONS`(符號檢查用、可由 config 的 neg_lexicon / neg_extra 換語系)與 m1 的 54 詞 `_DRIFT_M1_HIST_WORDS`(內含原本、原先、曾、改成、改為,共 5 個跟本 spec 重疊;另含「沒有」所以不能直接拿來用)。m1 的註解明寫「★不引用它★」並說明理由,這是既有先例。
2. spec 新增第三份、加上「規則字眼」第四份,卻沒有一句說明為什麼不共用、跟前兩份怎樣互不牽連、也沒說明不吃 `neg_lexicon` / `neg_extra` 設定(專案自訂的「已封存」「凍結」之類不會影響本提醒)。下一個讀的人會分不清該改哪一份。
3. 修法:〈做法〉1 補兩句:本表獨立於 NEG_LEXICONS 與 `_DRIFT_M1_HIST_WORDS`(理由:後者含「沒有」會把「目前沒有」整批吃掉;前者為符號檢查而增減)、不讀 `neg_lexicon`;並在檔案註解照 28640 的寫法標明來源。

## F3 「提醒」另起一種嚴重度,跟既有的 gate=warn 並存但語意不同,spec 只用「不寫帳」一個理由
severity: minor
blocking: 否
引句:「**提醒不進 violations**。只有 `cmd_note_shape` 在 `--staged` 時傳清單」
file: `scripts/lumos:25456`(早退)、`scripts/lumos:25458`(gate=warn 的標頭)、`scripts/lumos:25471`(warn 寫 warned 帳)
1. 既有:note-shape 已有 warn 級(`note_shape.gate=warn`,印「提醒(note_shape.gate=warn,不擋)」並寫 `warned`);note_audit、drift 也是同一套(26253、28602)。
2. spec 的提醒是第三種結果:印、不擋、不寫帳、不進 violations、不受 gate 值影響(gate=block 專案也印)。同一個 `cmd_note_shape` 於是有兩種「提醒」,標頭字樣也不同(既有的帶開關名稱與「不擋」,spec 的是「提醒(不擋):」),還要改早退條件。spec 的理由(帳本雜訊)成立,但沒回答「為什麼不做成 violation 帶 per-rule 嚴重度」這個明顯的替代,也沒說 gate=warn 專案同時有違規與提示時,兩段標頭並列是否可以。
3. 影響有限:不會做錯行為,屬設計交代不足。修法:〈做法〉3 加一句對照既有 warn 級的取捨;標頭字樣改成跟 `drift_check.old_sentence` 的 `提醒:…(note_shape.negation=warn,不擋)` 同格式(見 `scripts/lumos:29533`)。

## F4 「已配」的鄰行判定另寫逐行 _revisit_split,沒用既有的 _revisit_lines;圍欄裡的範例會被當成已配
severity: minor
blocking: 否
引句:「同一區塊(`body` 或 `summary`)裡、這一行的原始行號前後 3 行內(空行也算一行)有一行 `_revisit_split` 判成條件式(`cond`)的回頭條件,就不提醒。」
file: `scripts/lumos:26701`(_revisit_lines:剝圍欄、剝行內程式碼後才呼叫 _revisit_split,E5 與 set 共用)、`scripts/lumos:26680`(_revisit_split 的 docstring:「line 要先剝掉行內程式碼,圍欄由呼叫端排除」)
1. `_revisit_split` 的合約要求呼叫端先排除圍欄、剝行內程式碼;spec 對「命中行」有寫這兩步,對「鄰行」沒寫。
2. 場景:否定句後 2 行有個圍欄,裡面是教學用的 `REVISIT:[when-file:x][by:2026-12-31] …` 範例——鄰行判定若直接對 raw 行呼叫 `_revisit_split`,會判成 cond,提醒被錯放。這種範例在 lumos 自己的筆記裡很常見(講回頭條件寫法的那幾篇)。
3. 修法:鄰行改用 `_revisit_lines(text)` 的輸出(已經排除圍欄與行內程式碼、表格行回 None),再用 `_notelines_regions` 限同一區塊;不要另寫第二個逐行掃描。

## F5 子開關讀法跟 `drift_check.old_sentence` 先例有兩處差異,一處沒說明
severity: minor
blocking: 否
引句:「沒寫、設定檔讀不了、`note_shape` 不是物件 → warn,不另加提醒(那三種情況 `_note_shape_config` 已經印了)」
file: `scripts/lumos:28488`(_drift_old_sentence_config 的 docstring 與 28492、28496)、`scripts/lumos:24724`(_note_shape_config)、`scripts/lumos:28476`(_drift_config_text_parts)
1. 先例明講:設定壞時子開關要「另講一句」,因為 gate 那句只講 gate 的預設,不另講會讓人以為子開關也跟著擋。本 spec 反過來說 `_note_shape_config` 已經講過,但那句說的是「筆記形狀擋照預設擋」——讀的人會以為提醒也擋。這正是先例要避免的誤解。
2. 先例的做法是解析一次 JSON、切成 parts 分給各開關(`_drift_config_text_parts`);spec 另寫 `_note_shape_negation_config(text)` 再解析一次同一份文字,並沒有說明為何不擴充既有函式。因為 `_note_shape_config` 有兩個 2 值解包的呼叫端(25313 與 cmd_note_shape),不擴充有理由,但 spec 沒寫,實作者可能改動既有回傳形狀。
3. 修法:壞 JSON 與 note_shape 非物件時比照先例補一句「否定現況句提醒照預設 warn」;寫明不改 `_note_shape_config` 回傳形狀的原因。

## F6 doctor 那一行:讀設定檔與位置沒交代,容易接錯層
severity: minor
blocking: 否
引句:「doctor 開頭筆記形狀擋那幾行:`note_shape.negation=off` 時多印一行」
file: `scripts/lumos:25298`(_note_shape_doctor_lines 自己讀 config,含捷徑檢查)、`scripts/lumos:25335`(`if ci: return out` 早退)
1. `_note_shape_doctor_lines` 用自己的一段安全讀法(排除 symlink)取得 txt,並在 `ci=True` 時於 25335 早退。spec 只說「多印一行」,沒說要重用同一份 txt 傳給新函式、也沒說行要放在早退之前。放在早退之後,推送前與 CI 路徑看不到這行,跟 old_sentence 那行(29688 起,每次 doctor 都唸)不一致。
2. 修法:寫明用同一份 txt、位置在 `mode != "block"` 那行之後、`if ci` 之前,並在 S6 加 ci=True 的一個案例。

已讀,無 finding 的節:〈範圍〉〈回退〉〈實務隱患〉(掛點 `_note_shape_eval` 的 `hints` 出參與 `gov_events` 的 out-param 先例一致,見 `scripts/lumos:1713`;`--diff` 與 doctor 兩個呼叫端不傳參,`scripts/lumos:25366`、25451 確認)。

最高等級:major;blocking 共 1 條
