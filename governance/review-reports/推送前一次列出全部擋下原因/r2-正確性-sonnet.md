severity: major

第二輪正確性/邏輯席報告。對照程式是 prepush-collect 工作樹的 `scripts/hooks/pre-push` 與 `scripts/lumos`。我跑了 git 的 `--dry-run`、`--no-dry-run`、`rev-parse` 行為實驗,實驗目錄已刪。

## 做法第 1 點(掛鉤收集)

severity: major
blocking: 是 — 代碼審這道回 1,但掛鉤一筆都沒記到時,擋下會被吞掉,掛鉤往下跑全套,推送放行。
引句:「掛鉤讀它,替每個 `reason_kind` 各記一筆」
問題:計劃只寫了 `code-loop check` 回 1 之後,「掛鉤讀 `LUMOS-BLOCKS:` 再逐 `reason_kind` 記帳」。它沒寫「讀不到就退回記一筆」。現在掛鉤對 `cl_rc -eq 1` 是直接 `exit 1`。改成收集後,擋下只靠「有記到至少一筆」來保留。
具體失敗情境:
- `code-loop check` 在印出 `LUMOS-BLOCKS:` 之前就以 rc1 結束。例如 Python 未捕捉的例外,Python 例外的結束碼本來就是 1,現有程式碼已經把它當擋下。
- 那一行是空的,或 `reason_kind` 不在掛鉤寫死的對照表裡。計劃自己說合約測試是 `bound_tests`,現在這個回傳值沒有該欄位;`tier=high` 時重跑合約測試那個擋下點也一樣沒有。
- 以上任一種,記到 0 筆。其他 8 道又都沒擋,`$_PP_TMP/blocks` 是空的,判斷點放行,接著跑全套,推送過關。
- 這正是計劃自己說的最大風險:「某道擋下被吞掉、變成放行」。
修法:規則寫成「`cl_rc` 等於 1 時,不論 `LUMOS-BLOCKS:` 解析出幾筆,至少記一筆 `code-loop`,原因用通用句」。對照表查不到就用通用句。
S4、S13 要加「rc1 且沒有 `LUMOS-BLOCKS:` 行」的案例。
讀 `LUMOS-BLOCKS:` 時取最後一個符合的行,避免輸出裡別處引用的字樣干擾。
程式佐證:`scripts/hooks/pre-push:456-480`。

severity: major
blocking: 是 — 記錄擋下的寫入一旦失敗,擋下就消失,推送放行。
引句:「`$_PP_TMP/blocks` 有任何一行,就呼叫 `lumos push-summary --blocks-file」
問題:整套「有沒有擋下」只看暫存檔 `$_PP_TMP/blocks` 有沒有內容。`pp_record_block` 的 `printf >>` 寫入失敗時,計劃沒有任何處理,例如磁碟滿、`$_PP_TMP` 被別的程序(例如別的會談的清理)刪掉、檔案系統唯讀。
具體失敗情境:
- 某道閘擋下,`pp_record_block` 的 `printf >> $_PP_TMP/blocks` 失敗。bash 只回 rc1 並印一行錯誤,繼續往下跑。
- 判斷點看到沒有檔案或空檔,視為沒有擋下,放行。
- 對照:現有程式對 `mktemp -d` 失敗做了 `exit 1`(`pre-push:225-229`),同一個考量這裡沒有延伸。
修法:`pp_record_block` 另外設一個純量旗標(例如 `_PP_BLOCKED=1`),不依賴檔案。
判斷點用「旗標或檔案任一為真」。寫檔失敗時,彙總退回只印記憶體裡的閘名。
S6 加「`$_PP_TMP` 在擋下後被刪」的案例。

## 做法第 7 點(預演指令)

severity: major
blocking: 是 — 預演模式的掛鉤在判斷點以 0 結束,不跑全套。只要 git 實際推送,全套測試就被跳過。
引句:「它會照常呼叫推送前掛鉤、由 git 組出掛鉤要讀的推送行、保證不送出物件」
問題:「保證不送出物件」不成立。`git push --dry-run <使用者參數>` 的參數若含 `--no-dry-run`,git 會取消預演。
我在 git 2.39.2 實測:`git push --dry-run --no-dry-run o HEAD:refs/heads/m2` 真的把 `m2` 推到遠端了。
具體失敗情境:使用者執行 `lumos push-preview origin HEAD --no-dry-run`。預演模式的掛鉤通過 9 道後 `exit 0`,不跑全套,git 照常送出物件。這是一次沒跑全套的真推送。
修法(二選一,建議兩個都做):
- (a) 預演模式的掛鉤一律 `exit 1`,結果交給結果檔。這樣即使有人讓 git 取消預演,也推不出去。這比只擋參數可靠。
- (b) `push-preview` 拒絕 `--no-dry-run` 與 `--no-verify` 這類參數,並把 `--dry-run` 放在使用者參數之後。
補一條驗收條款。
說明:`--no-verify` 只會讓掛鉤不跑,結果檔不在,回 2,這個情況是安全的。

severity: minor
blocking: 否 — 要走到這步的人少;最壞是預演落帳弄髒版控檔,或誤報成「沒跑成」,不會放行真推送。
引句:「`push-preview` 每次開始時先刪掉那個資料夾裡超過 10 分鐘的票與結果檔」
問題:一次性票的生命週期有兩個缺口。
- 計劃說票 10 分鐘有效,而且寫帳端用「同一條驗法」。但計劃自己的時間節列出的最壞值很容易接近 10 分鐘:新增告警閘最多 300 秒,每個 ref 的漂移判定另加最多 60 秒,多 ref 還會相加。
- 超過 10 分鐘後,寫帳端的驗票失敗,預演事件會寫進版控帳。
- 另一個會談在同一個 repo 開始 `push-preview` 時,會刪掉這一次還在跑的超齡票。
- 結果檔也同樣被刪,這一次就誤報回 2。
修法:
- 寫帳端只在「掛鉤啟動時已驗過的結果」上信任,不重複算年齡。做法是掛鉤驗票通過後,另外 export 一個只有掛鉤能設的旗標。
- 清理改成只刪「超過 1 小時」或「建立者行程已不存在」的票。

severity: minor
blocking: 否 — 不會放行,頂多讓預演少回報或誤報。
引句:「0=閘全過、1=有擋下、2=預演沒跑成」
問題:這三個回傳碼沒有說清楚用誰的結果判定。
- 掛鉤通過後,git 還可能因為 non-fast-forward 之類的原因回 1。我實測 `git push --dry-run` 在「Everything up-to-date」時仍會呼叫掛鉤,rc 為 0。
- 結果檔也可能是壞的:掛鉤被殺在寫檔途中,內容是半行或空檔。
修法:
- 規定「以結果檔為準」。
- 結果檔解析不出數字,一律當成 2。
- 結果檔說零擋下、git 非零時,另外報「閘過了,但 git 本身拒絕:<原訊息>」,不要報成有擋下。

## 做法第 2 點(中斷與陷阱)

severity: minor
blocking: 否 — 這是規則與現有程式對不上,實作時會被紅測試擋住;不會直接變成放行。
引句:「判斷點之前每一行 `"$PY" "$GRAPHCTL"` 呼叫,緊接著都要有 `pp_stop_if_signaled`」
問題:照字面逐行驗,現有程式碼過不了。
- 這個範圍內有好幾行用 `|| true`、管線,或位於 `$(...)` 裡,取不到真實 rc。例如 `bound_tests_advisory` 的兩行(`pre-push:239,241`)、兩處 `loop escape --auto … || true`、`pitfalls … || true`、`test-layers … || true`。
- 規則也跟 S10 的範圍(8 道加 pitfalls、impact 等輔助呼叫)不一致。
- 另外有兩點。「先取回傳碼」若被實作成「只有 rc 等於 1 才擋」,`anchor verify` 與 `doctor --ci` 目前的 `if !` 寫法是「非零就擋」,會讓 rc2(例如基準線檔讀不到)變成放行。
- 「`EXIT` 只負責 `impact_done` 與刪 `$_PP_TMP`」跟第 7 點「掛鉤結束時刪票」互相矛盾。
修法:
- 規則改成枚舉名單,列出哪幾行要、哪幾行(`|| true` 的記帳類)明確排除。
- 明講 anchor 與 doctor 兩道維持「非零就擋」。
- 刪票放進 `EXIT` 的清單,且只在「環境變數是十六進位格式且票存在」時刪,避免變數值帶 `../` 時刪錯東西。

## 做法第 5 點(`--keep-going`)

severity: minor
blocking: 否 — 擋下仍會是擋下,只是少報幾個原因。
引句:「合約測試先紅時照樣算風險分級,後面幾道照判。合約測試那筆的 `reason_kind` 是 `bound_tests`」
問題:判定函式裡合約測試有兩個擋下點,計劃只處理了第一個。
- 第一個是 `not bound_advisory` 時的 `return {"blocked": True …}`。
- 第二個是 `bound_advisory and tier == "high"` 時重跑後的擋下,reason 尾巴帶「(tier=high,--bound-tests-advisory 不適用)」。
- 第二個擋下點也要累積後繼續,並給 `reason_kind: bound_tests`。
- 還有一處不明:pitfalls 失敗時,新增告警閘不需要 tier 與 `data`,要不要判沒寫清楚。
- 兩種選擇都不放行,但行為要寫死並測。
程式佐證:`scripts/lumos:51059-51060`、`scripts/lumos:51088-51093`、`scripts/lumos:51153-51163`。

## 做法第 8 點(預演不寫版控帳)

severity: minor
blocking: 否 — 影響版控檔會不會被預演弄髒,不影響擋不擋。
引句:「lumos 的兩支治理帳寫入器在分流之前」
問題:實際寫治理帳的函式不只兩支。
- `_gate_event`(經 `_gov_routes_local` 分流)與 `_append_governance_log` 是計劃說的兩支。
- 另外還有 `_codeloop_gov_log`(`scripts/lumos:49326`)與 `_codeloop_dispositions_gov_log`,它們直接 `open(…".governance-log.jsonl","a")`,不經分流。
- 還有漂移帳與審查帳的寫入器。
- 計劃有「第一步先盤點」,這點不算錯,但「兩支」的說法會讓盤點誤以為已完成。
- `prepush-summary` 還得加進 `_KNOWN_GATES`(`scripts/lumos:9331`)。否則 `_gate_event` 會印警告並回 False,什麼都不寫,S12 的帳事件寫不出來。計劃也沒提。
- 版本錯開還有一個縫:掛鉤的 `# lumos-hook-cap` 標記只證明掛鉤是新的,不證明掛鉤呼叫的 repo 內 `scripts/lumos` 也認得預演票。
- 新 `push-preview` 加新掛鉤再加舊 `scripts/lumos`,預演事件會照舊寫進版控帳。
- 修法:盤點表要涵蓋所有直接 append 的寫入器;把 `_KNOWN_GATES` 列為必改;掛鉤驗票通過後也探測 lumos 是否支援預演,否則不進預演模式。

## 資料狀態五問

- 新舊互讀:新掛鉤配舊 lumos、舊掛鉤配新 lumos,計劃都有交代,我也驗過 `code-loop check --help` 是 argparse,探測可行。新增帳欄位 `preview`、`blocks` 對舊讀者是多餘欄位,不影響判定。唯一的縫是上面那條「新掛鉤加舊 `scripts/lumos`,預演會落版控帳」。
- 寫一半:結果檔與票的半寫入見上面第三條 minor。擋下紀錄檔的寫入失敗見第二條 major。
- 衍生資料:N、M、`prepush-summary` 都從 `blocks` 檔導出。M 只算閘名,代碼審內部多筆算一道,這個定義內部一致。
- 時間:票的 10 分鐘窗口與最壞耗時重疊,見上面第二條 minor。RETIRE-IF 的 8 週與 REVISIT 的日期是否對齊要看上線日,不構成錯誤。
- 不可逆:真推送會多寫版控帳事件,還原提交即可;預演模式靠第三條 major 的修法才能保證不推。

其餘各節(PRIOR-ART、裁判簽名收集的理由、刪除與 tag 跳過、新舊版本探測的 `--help` 做法、`git rev-parse --git-path hooks/pre-push` 會跟著 `core.hooksPath`)已讀,無 finding。我實測了 `--git-path` 確實會跟 `core.hooksPath`。

總結:最高等級 major,blocking 共 3 條。這 3 條是代碼審回 1 但沒有記到擋下、記錄擋下的寫入失敗、預演被 `--no-dry-run` 變成沒跑全套的真推送。
