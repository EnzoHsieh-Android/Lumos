severity: major

# r1 正確性審查(sonnet):治理帳例行紀錄分流_計劃

逐節讀完(frontmatter、盤點、範圍、做法 1-6、實務隱患、驗收條款、回退、天花板)。壞引用:5 個 [[連結]] 與 lands_in 目標存在,intake 已查,不重報。四支直接寫帳的函式與判定類讀者(`_loop_close_stamps` `scripts/lumos:10189`、`_escape_released_loops` `scripts/lumos:11141`、`_fix_check_events` `scripts/lumos:12366`、`_codeloop_read_from_ledger` `scripts/lumos:42313`、`_codeloop_read_dispositions` `scripts/lumos:43295`)讀的種類實查都在左欄,這部分成立。

## 發現

1. 人為繞道(LUMOS_SKIP_*)的痕跡被分流表送進本機帳,與表自己的左欄原則、以及工具對使用者的承諾矛盾
severity: major
   blocking: 是 判準:左欄原則(繞道痕跡留版控帳)被表自己違反,實作照表做會讓「人按了逃生口」的稽核痕跡從版控帳消失,別台機器與 CI 端的稽核讀不到。
   spec 段落:〈做法〉2 分流表右欄(note-shape 全部;note-audit:skipped、skipped-env;note-reread:skipped、skipped-env;drift-check:skipped-env、skipped)對照左欄標題與 [m5] 的 code-loop:skipped-env 處理。
   引句:「code-loop:passed、skipped、dispositions、recall-miss、skipped-env(繞過代碼審的痕跡,工具承諾「留在治理帳上」)」
   問題:左欄把 code-loop:skipped-env 留版控帳,理由是它是人用環境變數繞道的痕跡。但同一型的繞道在別的閘全進右欄:設 `LUMOS_SKIP_NOTE_SHAPE=1`、`LUMOS_SKIP_DRIFT_CHECK=1`、`LUMOS_SKIP_NOTE_AUDIT=1`,各閘都印「已記進治理帳」並落 skipped-env(note-shape 在 `scripts/lumos:29661-29663`、drift-check 在 `scripts/lumos:34700-34702`、note-audit 在 `scripts/lumos:30848-30849`),CLAUDE.md 也寫「單次跳過、會留帳」。照表實作,這三種都只落 `.git/lumos/governance-local.jsonl`,版控帳一筆不留;「分流規則一句話」說「人或 AI 主動做的決定留在版控帳」,逃生口正是人的主動決定,而且「拿不準的留在版控帳」這條兜底也沒被用上。另外 note-audit:skipped 一個 kind 兩個來源,表以「閘名+種類」分流分不開:`cmd_note_audit_skip`(人寫理由的略過,`scripts/lumos:30927`,指令說明「要理由、會留帳」)與自動「沒有起點」略過(`scripts/lumos:30368`)都是 gate=note-audit kind=skipped,整個進右欄,人寫理由的那筆就也進了本機帳(它另有 verdict 檔進版控,但帳上這一行是唯一能被 `lumos gov` 與別台機器統計到的)。
   佐證:`scripts/lumos:29661`、`scripts/lumos:34700`、`scripts/lumos:30848`、`scripts/lumos:30927`、`scripts/lumos:30368`。判定本身不讀這些行,所以不會讓閘從擋變放,但稽核痕跡丟失與「已記進治理帳」的訊息對不上。

2. 目標「平常工作目錄乾淨」沒達到:`lumos show` / `lumos context` 每次查圖譜也會弄髒版控檔,spec 未列為範圍外也未處理
severity: minor
   blocking: 否 判準:不影響分流正確性與任何判定,只是動機句宣稱的效果在這個 repo 與雲端工作階段打折。
   spec 段落:summary 的 WHY 與〈白話〉。
   引句:「兩者分開後平常提交推送完工作目錄就是乾淨的」
   問題:CLAUDE.md 要求動手前先 `lumos search/context/show`,而 `cmd_show`/`cmd_context` 每次都 append 版控的 `docs/.usage-log.jsonl`(`_usage_log` `scripts/lumos:16181-16192`,呼叫點 `scripts/lumos:16197`、`scripts/lumos:16256`;`docs/.usage-log.jsonl` 在 `git ls-files` 內且列在 `_BOOKKEEPING_FILES` `scripts/lumos:24193`)。雲端工作階段在讀完筆記後、提交前工作目錄就已髒,REVISIT 2026-12-01 要數的「被打斷次數」不會只剩「主動決定之後那幾次」。[S1] 只量治理帳所以不會紅,但〈範圍〉「不做」沒有把 usage-log 排除在外,讀者會以為問題解決。
   佐證:`scripts/lumos:20553`(既有註解承認這本帳因唯讀指令變髒)。

3. 左欄「各閘的 fail-open」與右欄「bound-tests 全部」互相覆蓋,且 fail-open 留版控帳讓 [S1] 在缺工具的環境會紅
severity: minor
   blocking: 否 判準:歧義只影響一個閘的統計歸屬與乾淨度,不影響留痕判定。
   spec 段落:〈做法〉2 分流表第 8 列左欄與第 4 列右欄。
   引句:「各閘的 fail-open(工具出錯自動放行的痕跡)」
   問題:(a) `_gate_failopen("bound-tests", …)` 真實存在(`scripts/lumos:42943`),它同時屬「bound-tests 全部」(右)與「各閘的 fail-open」(左),表沒說誰優先;「不用萬用字元、唯一例外 check-」又把「各閘的」寫成萬用字元。(b) fail-open 是機器自動放行,不是人的決定,卻留左欄;`lint-new` 在沒裝工具/逾時時每次提交都落一筆(`scripts/lumos:43867`、`scripts/lumos:43874`),`code-loop`/`pitfalls` 算不出 HEAD 或 merge-base 也會落(`scripts/lumos:43736`、`scripts/lumos:43752`、`scripts/lumos:43797`)。這種環境(沒裝 lint 工具的雲端工作階段)每次提交仍弄髒版控帳,[S1]「只產生例行紀錄時一個位元組都不變」在該環境不成立,而動機正是雲端工作階段。唯一讀它的 `_lint_new_autopass_count`(`scripts/lumos:25535`)是本機統計,本來就在 [S3] 的兩本一起讀名單內,留左欄沒有 CI 讀者需要。

4. 本機帳路徑沒寫「相對路徑要解析」與「建 `lumos/` 子資料夾」,照字面實作會寫錯地方或每筆都寫失敗
severity: minor
   blocking: 否 判準:實作細節缺口,[S5] 的測試會抓到,不會悄悄放行。
   spec 段落:〈做法〉3。
   引句:「共用資料夾用 `git rev-parse --git-common-dir` 取(worktree 共用同一份)」
   問題:實測該指令在主工作目錄回相對路徑,根目錄回 `.git`、`docs/` 底下回 `../.git`(相對於執行時的 cwd);`_append_governance_log` 現在的 git 查詢是 `cwd=str(vault)`(`scripts/lumos:1415-1416`),照那個 cwd 取到 `../..` 開頭的相對路徑,若不先以該 cwd 解析成絕對路徑就會寫到錯的目錄。另外 `<共用資料夾>/lumos/` 子資料夾 git 不會預建,spec 沒寫要 mkdir;不建的話 `open(..., "a")` 丟 FileNotFoundError(屬 OSError),`_gate_event` 走回 False、每筆例行事件都印 telemetry-write-failed(`scripts/lumos:1394-1403`),`_append_governance_log` 則整批靜默丟掉(`scripts/lumos:1430-1431`),且 [S4] 的行為會把它誤當成「磁碟問題」。

5. worktree 共用同一份本機帳是新的併發面,批次寫入會被其他行程插行,spec 的實務隱患沒有這一類
severity: minor
   blocking: 否 判準:只傷統計類事件(壞行讀端會跳過),不傷判定類讀者。
   spec 段落:〈做法〉3 與〈實務隱患〉(沒有併發項)。
   引句:「共用資料夾用 `git rev-parse --git-common-dir` 取(worktree 共用同一份)」
   問題:現在每個 worktree 有各自的 `docs/.governance-log.jsonl`,同一檔只有一個寫者;分流後多個 worktree 的 pre-commit/pre-push/doctor 會同時往同一個本機檔寫。`_append_governance_log` 用一般緩衝的 `open(path, "a")` 在迴圈裡逐筆 `f.write`(`scripts/lumos:1427-1429`),批次超過緩衝大小(8KB,doctor --ci 對很多節點的 check-s*/check-e* 提醒一批可達這個量)就分成多次 write 系統呼叫,別的行程的整行可以夾在中間:前半行接上別人的整行成為一行壞 JSON,後半行另成一行壞 JSON,兩筆事件一起丟。讀端(`_drift_jsonl_parse`)跳過壞行所以不炸,但 [S3]「分流前後總數相同」在並行場景不保證。〈實務隱患〉七項裡沒有併發一項,也沒寫「無+為什麼」。
   佐證:對照寫版控帳的另一支 `_ledger_append` 用單次 `os.write` 並明講「≤4KB 寫前拒」(`scripts/lumos:18507-18523`),說明這個 repo 對並行追加是在乎原子性的。

6. 本機帳沒有任何成長守衛,而既有的成長警示被明列只讀版控帳
severity: minor
   blocking: 否 判準:只是失去一個提醒,不影響判定。
   spec 段落:〈實務隱患〉帳本成長、〈做法〉4。
   引句:「版控帳成長變慢;本機帳在 `.git` 裡,`git clone` 不帶,不會變成別人的負擔。」
   問題:例行事件(doctor-run、note-shape、delguard 每次提交各一筆)是帳本膨脹的主因,現在全部進沒有大小上限、沒有成長觀測的本機檔。doctor 的帳本成長段只量版控帳(`scripts/lumos:2238-2246`,`_LEDGER_MB_CAP = 5`),[S3] 又明定它只讀版控帳,所以本機帳長多快都沒人叫;而 `cmd_gov` 每次整檔 `read_bytes`(`scripts/lumos:8142-8146`)、`_lint_new_autopass_count` 整檔 `read_text`(`scripts/lumos:25543-25548`),本機帳一大統計類讀者變慢也沒警示。spec 的「回頭看」只有 REVISIT 2026-12-01 數被打斷次數,沒有本機帳大小。⚠ 是否要補守衛交編排者裁(屬範圍取捨)。

## 逐類實務隱患(本案碰到的風險類)

- 守衛面:有 finding 1(稽核痕跡)、3(fail-open 歸屬);判定類讀者實查全在左欄,「分流不會讓閘從擋變放」成立。
- 併發:有 finding 5。
- 效能/資源:有 finding 6;分流後統計類讀者讀兩檔,總量不增,無額外效能問題。
- 回滾:無,還原提交即回原行為;本機帳留著無讀者影響判定,實查除統計類外無讀者。
- 相容:無,舊紀錄兩本都讀,消費專案舊版 lumos 繼續寫版控帳,混版本期間只是兩本都有例行行,不影響判定。
- 跨機器:spec 〈天花板〉2 已承認;S18 沒有 repo 內實際使用度量式撤除條件(`grep retire:度量` 只在本 spec 出現),實害為零。

## 各節

- summary / 白話 / PRIOR-ART / RETIRE-IF / REVISIT:見 finding 2(動機宣稱);其餘已讀,無 finding。
- 盤點:四支寫入器與三個包裝實查屬實(`scripts/lumos:1358`、`1426`、`42423`、`43253`),已讀,無 finding。
- 範圍:見 finding 2。
- 做法 1:已讀,無 finding。
- 做法 2:見 finding 1、3。
- 做法 3:見 finding 4、5。
- 做法 4、5、6:已讀,無 finding(步驟 3 與 6 的「非 git 時」措辭略有出入,但步驟 6 已更正,不算矛盾)。
- 驗收條款 S1-S5:S1 見 finding 3;其餘已讀,無 finding。
- 回退、天花板:已讀,無 finding。

最嚴重 severity: major,blocking 1 條(finding 1);其餘 5 條 minor 不阻擋。
