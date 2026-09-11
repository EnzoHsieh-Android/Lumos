severity: major

H1 非程式檔編輯會被誤算成零推播
severity: major
blocking: 是
引句:「逐字稿裡每一次 Edit/Write/MultiEdit(Codex 是 apply_patch)呼叫都是一列」
file: `scripts/hooks/claude/impact-hook.py:147`
`README.md` 或 `docs/x.md` 的 Edit 會被 hook 明確排除；若下一步讀取 `Systems/a.md`，照 spec 卻產生一列零推播 miss，把不在 hook 適用範圍的編輯當成漏推。

H2 Codex 沒有可供配對的呼叫編號
severity: major
blocking: 是
引句:「推播清單用呼叫編號去配 hook 附件」
file: `governance/eval/lens-utilization/recount.py:18`
Codex 的 developer 附件沒有 `toolUseID`，現行程式明載只能用同輪最近呼叫的啟發式配對；同輪有兩次 apply_patch 與兩份附件時，spec 要求的精確配對無資料可實作，可能把 A 的推播清單配給 B。

H3 多檔 apply_patch 與單一 F 資料模型不相容
severity: major
blocking: 是
引句:「輸出:三類各自的清單(被改的檔 F、筆記、工作階段雜湊、時間)與分佈」
file: `scripts/hooks/claude/impact-hook.py:753`
file: `governance/eval/lens-utilization/recount.py:273`
一個 patch 同時修改 `src/a.py`、`src/b.py` 時，hook 逐檔計算後把兩份 context 合成一個附件，但 spec 規定每次 apply_patch 只有一列及一個 F；沿現況取第一個標頭會漏掉 `b.py`，若合併推播節點又會把只為 B 推的節點誤算成 A 已推。

H4 失敗的 Read 仍會被當成真的讀過
severity: major
blocking: 是
引句:「讀取怎麼認:沿用既有高信心判法(Read 工具、單純讀動詞、lumos context|show|contracts)」
file: `governance/eval/lens-utilization/recount.py:393`
逐字稿若有 `Read Systems/gone.md`，其 tool result 是「file not found」，現行高信心判法仍只看 tool_use 並記為 touched；照字面沿用會把 agent 根本沒看到內容的節點列成 miss。

H5 about_code 與編輯目標的路徑口徑未接合
severity: major
blocking: 是
引句:「關於欄:該筆記開頭的 about_code 欄位含 F」
file: `governance/eval/lens-utilization/recount.py:384`
file: `scripts/lumos:11035`
Claude Edit 的 F 通常是 `/Users/enzo/harness/lumos-toolchain/scripts/lumos`，但 about_code 被強制存成 `scripts/lumos`；spec 沒定義轉 repo-relative、symlink、Unicode 與 `..` 的正規化，直接判「含 F」會把真正命中降成判不出。

H6 impact 的 direct 輸出不等於反查到的全部直連
severity: major
blocking: 是
引句:「該筆記在 direct 清單(impact 抓直連有兩條規則:正文反引號寫到 F 的完整路徑,或裸檔名在 git 追蹤的檔裡唯一時的檔名比對」
file: `scripts/lumos:20458`
file: `scripts/lumos:20643`
`Issues/vendored測試套件在消費端假紅.md` 同時直引 `scripts/test_lumos.py` 且有 pitfall trigger；現行 `cmd_impact` 會先把 incident 節點從 direct 移除，因此照 spec 查 direct 會把確實直連的讀取錯分到 about_code 或判不出。

H7 git 加入時間不能證明筆記當時不存在
severity: major
blocking: 是
引句:「git 第一次加入的時間晚於編輯,或還沒進版控)→ 不算 miss,另計——推播當下它不存在」
file: `scripts/lumos:20294`
星期一 10:00 建立未追蹤筆記、10:05 編輯程式、11:00 才提交時，hook 在 10:05 已能從工作樹讀到該筆記；spec 卻因首次提交晚於編輯而列成「事後才有」，消掉一筆真 miss，未追蹤但早已存在的筆記也同樣被錯排除。

H8 ISO 週沒有定義時區
severity: major
blocking: 是
引句:「只收編輯時間落在上一個完整 ISO 週的列(逐字稿每行帶時間)」
file: `governance/autonomous-loop.sh:423`
file: `scripts/test_lumos.py:33690`
逐字稿時間是 UTC 的 `Z`，週戳則由主機本地時區產生；`2026-09-06T16:30:00Z` 在台北已是星期一，直接按 UTC 屬 W36、轉台北則屬 W37，照 spec 無法唯一決定該列進哪份週檔。

H9 「認不得的段標頭」沒有可執行定義
severity: major
blocking: 是
引句:「某段實際解析到的行數少於標頭宣稱的 N,或遇到認不得的段標頭 → 那筆 pushed_complete=false」
file: `scripts/hooks/claude/impact-hook.py:670`
現行同一附件還會出現 `[kt 效能檢核——…]` 之類第五種標頭；若它算「認不得的段標頭」，大量正常推播會被標不完整並整筆排除，若不算，spec 又沒有規則區分它與未來真正漏解析的推播段。

H10 每檔逾時沒有整次週跑的總預算
severity: major
blocking: 是
引句:「每個子行程設 60 秒逾時,逾時那支檔的分類記判不出並計數」
file: `governance/autonomous-loop.sh:41`
file: `governance/autonomous-loop.sh:449`
上一週若有 100 個不同的 miss 候選檔且 impact 都卡到逾時，週跑可持有自主迴圈整跑鎖約 100 分鐘；這期間後續治理步驟與另一輪排程都不能進場，單檔 fail-open 並沒有保住整體排程。

全份最高嚴重度是 major,blocking 共 10 條