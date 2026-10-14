severity: minor

我讀了文件修補、掛鉤與測試修補,並在快照 da914963 上實跑了 `-k t_prepush_interrupt`(46 過 0 紅)和 `-k t_prepush_cl_reason_sentences`(2 過 0 紅)。快照的 `scripts/` 與 da914963 相同,`governance/anchor-baseline.json` 裡兩個雜湊(`test_lumos.py`、`pre-push`)跟檔案實際雜湊一致。

逐項核對的結果:

- **S10 新增兩句與 ⑪ 一致。**
  - S10 寫「掛鉤應回 1 擋下」。
  - 掛鉤主殼把非零的子殼離開碼記成 `_rc=1`,最後 `exit 1`。
  - ⑪ 驗 `rc == 1`、片與孫行程都消失。
  - S10 的孫行程那句有 ⑩ 和 ⑫ 對應。
- **Windows 退路的 PITFALL 與程式相符。**
  - 有 `setpgid` 才換群組再 `exec`,`setpgid` 失敗照樣 `exec`,沒有就用 `runpy` 跑,離開碼照實傳出。
  - 欄位齊全,綁了 `[test:]`。
  - 啟動器抽取用的正規式能吃多行單引號字串,起片處檢查也對得上掛鉤現況。
- **第二發 TERM 的 PITFALL 與程式相符。**
  - `_pp_kill_jobs` 的 `sleep 0.2` 加第二發,跟文件寫的一致。
  - 「150 次 32 次留孤兒」的數字在 `governance/review-reports/code-推送前收集/r4-fix.json` 找得到。
  - 我沒有自己重跑 ⑫ 的變異(拿掉第二發、第二發不短等);r4-fix.json 只記了這兩個變異紅過。
- **PYTHONPATH 的 WHY 欄位齊全。** 它有 `[出處:]`、`[因:]`、`[不選:]`;「每個 `$PY` 閘都一樣、修補前就有」的說法,從掛鉤裡到處呼叫 `"$PY"` 可以印證。
- **原因句守衛真的讀計劃。**
  - 它用 `_need_src` 讀計劃檔,取含「**對照表四句的正本在這裡**」的那一行(計劃現況恰好一行),抽出四句後跟 `_PPC_KIND_SENTENCES` 比對。
  - 目前計劃那行抽得出四句,跟常數和掛鉤的 `pp_cl_reason` 逐字一致。

以下兩條是我找到的洞:

severity: minor
blocking: 否 — 只有通用句漏守,文字漂移不影響擋下與否,不到 major
引句:「漂移守衛(結構測試):_PPC_KIND_SENTENCES 自稱照計劃〈做法〉5「對照表四句的正本在這裡」那段逐字寫,這支真的去讀那段比對」
問題:新守衛只讀計劃第 66 行那一段的四句。同一份計劃第 65 行有第五句通用句「代碼審判定擋下(細節在上面)」,掛鉤的 `pp_cl_reason` 預設分支和 `_PPC_KIND_FALLBACK` 也各存一份。`t_prepush_cl_reason_table_matches_lumos` 只拿掛鉤去比常數,從不讀計劃。所以這句的「計劃、掛鉤、常數」鏈在計劃那端是斷的。
失敗情境:有人只改計劃第 65 行的通用句,所有測試照綠。有人把掛鉤和常數一起改掉,也沒有任何東西對照計劃。這正是新守衛想補的「先改計劃再改兩處純靠自律」,只補了四分之四句。
佐證:file: `docs/lumos-toolchain-knowledge/Projects/推送前一次列出全部擋下原因_計劃.md:65`;file: `scripts/hooks/pre-push:142`;file: `scripts/test_lumos.py:65476`

severity: minor
blocking: 否 — 只是範圍判準的存放位置問題,掛鉤行為與測試都不受影響
引句:「在工具鏈的資安範圍外(工具鏈本身的資安只看提示注入、讀寫越界、非刻意的一步繞過;2026-10-14 使用者確認)」
問題:這個資安範圍判準是使用者裁的專案政策,以後別的審查席也會拿來駁回「環境變數注入」類發現。但它只以括號形式埋在這一條 WHY 的 `[因:]` 裡,出處欄寫的是「第四輪代碼審資安席」,不是使用者。它沒有獨立的 `RULE:` 行,沒有 `[依據:人]`、`[since:]`、`[retire:]`、`[confirmed:]`,`lumos search` 用「資安 範圍」之類的詞也難以單獨找到。依 CLAUDE.md 第 3 條,這種寫法只是線索,沒有「挑戰程式碼」的效力;同時它又被當成不加機制的唯一理由。圖譜裡全庫只有 `Systems/bound-tests-gate.md` 這一處出現「非刻意的一步繞過」。
失敗情境:下一輪資安席看到 `PYTHONPATH`、`LD_PRELOAD` 等同族發現時,找不到可引用的獨立規則,可能又當成新發現重提;或有人改了這條 WHY 的敘述,範圍判準就跟著消失。
佐證:file: `docs/lumos-toolchain-knowledge/Systems/bound-tests-gate.md:146`

最高等級 minor,blocking 0 條。
