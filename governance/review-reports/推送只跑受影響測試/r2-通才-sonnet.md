severity: major

**逐節結果**
- 白話、PRIOR-ART、舊否決對照、現況:已讀,無 finding。我核對過 CI 的 `pull_request` 事件(`.github/workflows/ci.yml:9`)、PR 一律全套(`ci.yml:83`)、`_DOCS_ONLY_NEVER` 含 anchor-baseline(`scripts/lumos:61675`)。main 近 200 個提交裡 149 個是 PR 合併,「功能分支靠 PR 的 CI 後盾」這個前提成立。
- 範圍、做法 1、做法 3、做法 4:已讀,無 finding。`_krc_all3` 確實宣告了沒用到(`scripts/hooks/pre-push:897`),`run_group` 確實是任一片回 3 就整組回 3。

---

severity: major
blocking: 是(照字面做,RETIRE-IF 永遠量不出來,這條撤除機制等於不存在)
段落:RETIRE-IF
問題:數法依賴兩份資料,實際都不存在。
- 其一,「`lumos ci-status` 記進治理帳的 PR 結果」做不到。`ci-status` 只讀 `.ci-log.jsonl`,不是治理帳。
  - 該檔每筆只有 ts、run_id、sha、branch、workflow、conclusion、failed_step,沒有事件類型(PR 或 push),也沒有 PR 編號。
  - 該檔只在有人跑過 `lumos ci-wait` 時才寫,沒等 CI 的紅燈不會進帳。
  - 該檔放在 `env.vault.parent`,`git ls-files` 查不到,是各機器本地檔。
- 其二,「同提交的推送前檢查紀錄」沒有。`docs/.governance-log.jsonl` 的 gate 欄(check-s、delguard、code-loop、bound-tests、lint-new 等)裡沒有任何一種記「推送前測試套件綠」。掛鉤跑完套件只印一行統計,不落帳。
- 結果是分母(PR 數)、分子(CI 紅且本機綠)都抓不到,且有選擇偏誤。
引句:「數法:`lumos ci-status` 記進治理帳的 PR 結果,對照同提交的推送前檢查紀錄。」
佐證:`scripts/lumos:62930`(CI_LOG_NAME)、`scripts/lumos:63191-63199`(`_ci_record` 欄位)、`scripts/lumos:63281-63330`(`cmd_ci_status` 只讀 ci-log);另用 grep 對 `docs/.governance-log.jsonl` 統計全部 gate 名稱,無測試套件類。
建議:要嘛先加一筆「推送前套件結果」落帳並讓 ci-log 帶 event 與 PR 編號,要嘛改成可手工數的口徑(例如 `gh pr list` 配 check 結論)。

severity: major
blocking: 是(照字面實作會做出語意不同的行為,或需要實作者自己重構掛鉤來猜)
段落:做法 2
問題:「沿用 light、關鍵字與自主迴圈照現行」跟現行掛鉤結構對不上。
- 現行 `_suite_this="light"` 只在兩個條件同時成立時才設:spec-gate 印「改動風險分級:light」,且 pitfalls 說 `light_ok:true`。
- `_SUITE_KEYS`(來自 `affected_keys`)與 `_AUTOLOOP_FULL`(來自 `autoloop_full`)都只在這個 `if` 內讀取(`scripts/hooks/pre-push:572-577`)。
- spec 要的是功能分支「原本判 full」也降成 light。但在不符合 light 條件的 full 路徑上,這兩個值從來沒被讀過。實作者得自己決定要不要把讀取搬出 `if`。
- 更重要的是 `light_ok` 的語意被默默拿掉了。掛鉤註解寫明它的用途:範圍裡有測試檔、skills、workflow 這種既非文件也非程式的檔,不准少跑全套(r1 資安席)。
- 照 spec 字面,這類改動在功能分支上連關鍵字子集的保證都沒有,spec 卻沒提這個取捨。實務隱患只寫了「CI 才看到」,沒有點出被刻意擋過的那一類。
- 同一段的訊息也要改:現行 light 無關鍵字時印「CI 會跑全套當後盾」。功能分支若沒開 PR,CI 不會跑(push 事件只收 main 與 tag),這句話會誤導。
引句:「這個 ref 原本判 `full` 時改判 `light`(沿用 `_SUITE_LIGHT`,不新增狀態);關鍵字照現行從 `pf_json` 的 `affected_keys` 取、自主迴圈照現行 `autoloop_full`。」
佐證:`scripts/hooks/pre-push:544-578`(`_suite_this` 判定與 light 條件)、`scripts/hooks/pre-push:1001`(「CI 會跑全套當後盾」);`.github/workflows/ci.yml:4-9`(push 只收 main 與 tag)。
建議:明講功能分支路徑是否仍受 `light_ok` 約束,以及關鍵字與 `autoloop_full` 的取值位置,並新增一條驗收條款釘住這點。

severity: minor
blocking: 否(措辭與精度問題,不影響實作行為)
段落:標題與全文
問題:標題與內容不符,會誤導讀者。
- 計劃標題寫「只跑受影響測試」,但全文的設計是「推功能分支時本機不跑全套」。
- 關鍵字子集被明說只是冒煙測試,選測也被明確移到第二步,這篇「不做任何新選測」。
- 讀標題的人(尤其下一個 AI)會以為本計劃實作了受影響測試選擇,第二步計劃又會拿同一個詞,造成混淆。
- 檔名與 `lands_in`、測試名(`t_prepush_*`)、`RETIRE-IF` 都沿用這個詞。
引句:「不採:這一步不做任何新選測」
佐證:本檔 `# 推送只跑受影響測試_計劃` 標題。
建議:改名成「推功能分支本機不跑全套_計劃」之類,第二步才保留「受影響測試」。

severity: minor
blocking: 否(斷鏈,不影響掛鉤行為,但 lint 會唸)
段落:related、白話、PRIOR-ART、審計修正紀錄
問題:該節點尚未建立。
- spec 在四處引用 `[[Projects/依實測覆蓋挑測試_計劃]]` 當「第二步另開」的落點。
- `docs/lumos-toolchain-knowledge/Projects/` 下不存在這個檔(`ls` 與 grep 皆 0 筆)。
- 它放在 frontmatter 的 `related`,`lumos lint` 會報斷鏈,計劃讀者點不進去。
引句:「另開 [[Projects/依實測覆蓋挑測試_計劃]]」
佐證:`docs/lumos-toolchain-knowledge/Projects/` 目錄列表。
建議:先建占位節點,或在上線前先刪掉這些引用。

severity: minor
blocking: 否(驗收精度問題,不是漏洞)
段落:驗收條款 S1、S3
問題:S1 一條條款綁了四種情境,測試可能只覆蓋其中一部分就綠。
- S1 同時管「功能分支降 light、印那一行、同次另有推 main 時全套、推 main 時全套、推標籤照現行」。
- S3 又綁同一個測試名 `t_prepush_feature_branch_skips_full`。
- 條款字面寫得出會翻紅的測試,但若實作者只在一種情境斷言,另外幾種就退化而測試仍綠。
- 守衛面的「多 ref 任一要全套就全套」是最容易靜默失效的一條,值得獨立條款。
引句:「同一次推送另有推 main 的 ref 時 應 照舊全套;推 main 時 應 照舊全套;推標籤時 應 照現行」
佐證:本檔〈驗收條款〉S1 與 S3 的 `[test:]` 欄。
建議:至少把「混推 main」與「推標籤」各拆成獨立條款與測試。

severity: minor
blocking: 否(回退說明不完整,不影響前進方向)
段落:回退
問題:回退說明少了半套。
- 只說拿掉掛鉤那一段並把範本改回原文,沒提 S1、S3 的測試與步驟 4 的修補要不要一併回。
- 拿掉掛鉤段而留著 S1、S3 的測試,會讓測試翻紅。
- 步驟 4 的 `run_group` 修補與功能分支降級無關,應明講回退時保留。
- 範本回滾後還要重新注入 `CLAUDE.md` 與 `AGENTS.md`,並重簽 anchor-baseline。
引句:「把掛鉤裡「功能分支降成 light」那一段拿掉,就回到推功能分支本機跑全套;範本那句改回原文再重新注入。」
佐證:本檔〈回退〉;`CLAUDE.md:61` 與 `scripts/templates/graph-discipline.md:59` 同句,`CLAUDE.md:98` 另有一份在紀律區塊外。

---

**實務隱患逐類**
- 守衛面:spec 已寫,但漏了 light_ok 那一類(見上面第二條 major)。
- 併發與負載:無新增隱患。分片數沒改,只減少了跑的測試量。
- 不可逆:無,掛鉤一段與一句說明都能還原。
- 金流、對外送出:無。不改 CI,也不新增對外呼叫。
- 版本錯開:spec 說不改 `pitfalls --json` 欄位,但我沒核對舊 lumos 配新掛鉤時 `affected_keys` 欄位是否一定存在,這點我沒查證。

總結:最嚴重等級是 major,會擋的問題共 2 條。

清理:這次只讀 repo 與跑唯讀查詢,沒有建立臨時目錄,不需要刪檔。
