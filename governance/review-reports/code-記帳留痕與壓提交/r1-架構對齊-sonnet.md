severity: blocker

## F1 新擋的「是不是代碼審」判法跟同檔既有判法(_roster_kind)不同款,會誤傷設計審迴圈

severity: blocker
blocking: yes

觀察到什麼:patch 在 `cmd_canary` 新增的擋是用 `str(loop).startswith("code")`(不帶連字號)判定「這是代碼審」。但同一支檔案裡,`_roster_kind()`(scripts/lumos:9639-9646)明文定義同一件事要判**三值**:`code-`(含連字號)才算 code;`code` 開頭但沒連字號的算 `None`(不可判定),文件裡直接舉了兩個真實歷史迴圈編號當例子——`code側刪除傳播守衛`、`codestage`。`code-loop check` 的處置閘(scripts/lumos:17805-17808)還特別把 `None` 一律當**設計審**、fail-closed 處理,註解寫死原因:「免得取個 codeX 的編號就繞過(r2 外家席實跑抓到)」——這是之前外家審查真的抓到過的繞過洞,不是我自己假設的情境。

patch 自己的註解宣稱用的是同一套判法:

引句:「跟 doctor [I] 段與 code-loop 的既有判法同一個(code-<主題>)。」

但緊接著那一行程式碼並沒有照著「code-<主題>」(帶連字號)去比對:

引句:「if loop and str(loop).startswith("code") and not (report and snapshot):」

怎麼重現:在乾淨臨時 vault 跑(唯讀,不動正式 repo):

```
python3 /Users/enzo/harness/lumos-toolchain/scripts/lumos --vault /tmp/lumos-review-B/vault \
  canary record none --loop "codestage-測試題" --round r1 --auditor "架構對齊-sonnet" \
  --severity clean --findings 0 --report /tmp/lumos-review-B/vault/Projects/report.md
```
實際輸出(rc=2):
```
擋下:代碼審(codestage-測試題)的每一筆記帳都要帶 --snapshot——現在不擋的話,要到問處置閘才會發現,而那時帳本已經不能撤銷,只能整輪換編號重記
```
同時我直接呼叫 `_roster_kind("codestage-測試題")` 回傳 `None`(不是 `"code"`)——跟處置閘(`_roster_kind`/17805-17808)會把它當設計審放行「[disposal] 條款綁定」不同,新擋這裡卻把它當代碼審強制要求 `--snapshot`。

為什麼是 bug 而不是風格:作者在派工單與 PITFALL 筆記都明講「設計審不動(相容)」,這是這批改動自己宣告的相容承諾。但 `codestage`/`code側刪除傳播守衛` 這類迴圈編號是這支檔案自己文件記載過的**真實**歷史命名(`_roster_kind` 的 docstring 與 `docs/lumos-toolchain-knowledge/Projects/派工編制資料化_計劃.md` 都拿它們當現成測資),不是我編出來的邊界案例。這些原本會被既有 `_roster_kind`/處置閘判成「不可判定→當設計審」的迴圈,現在會被新擋誤判成代碼審,第一筆記帳就被要求帶 `--snapshot`,直接違反作者自己宣稱的相容鐵則,也跟同檔既有的「是不是代碼審」判法(這正是我這個鏡頭要看的東西)不同款。

file: `scripts/lumos:9639`(`_roster_kind` 三值判法定義)
file: `scripts/lumos:17739-17746`(既有作法:遇到 `_roster_kind` 回 None 的情況,是明講「編號 code 開頭卻不是 code-,看不出是哪一種審查」再照最嚴處理,不是悄悄用寬鬆比對吞掉)
file: `scripts/lumos:17805-17808`(處置閘把 None 當設計審 fail-closed,並註明是為了擋 r2 外家席抓到的繞過洞)
file: `docs/lumos-toolchain-knowledge/Projects/派工編制資料化_計劃.md:40`(`codestage` 是文件記載的真實歷史迴圈編號,非假設案例)

## F2 壓提交失效訊息的改善只接到「表態」那一條消費路徑,`code-loop pass` 留痕失效(作者自己講的另一半)那條路徑仍是舊的兩個 sha 訊息

severity: major
blocking: yes

觀察到什麼:patch 改的是 `_codeloop_record_valid()` 這支共用函式的回傳訊息:

引句:「return False, (f"記錄 sha {rec_sha[:8]} 不是目標 {marker_sha[:8]} 的祖先——多半是壓過提交或 rebase 改寫過歷史"」

但這支函式在全檔只有兩個呼叫點消費它的 `why`:
1. `scripts/lumos:28836`(表態/dispositions 有效性檢查)——把 `why` 塞進 `out["problems"]`,使用者看得到新訊息。
2. `scripts/lumos:29131-29147`(`_codeloop_guard_verdict` 裡驗 `code-loop pass/skip` 留痕是否還有效,也就是 `code-loop check` 真正會擋 push 的那條路)——`_vok, _vwhy = _codeloop_record_valid(...)` 只在 `_vok` 為 True(留痕仍有效)的分支才用到 `_vwhy`(組進「有效留痕」的成功訊息)；一旦 `_vok` 為 False(留痕因壓提交失效,正是這支 patch 想解決的場景),程式碼直接掉到既有的
```
reason = f"tier=high 且留痕 sha 過時(留痕={rec_sha[:8]} 目標={marker_sha[:8]};非純簿記增量)"
```
完全沒有讀 `_vwhy`。全檔搜尋 `_vwhy` 只出現在 29137(賦值)與 29141(True 分支使用)這兩行,29131-29147 的 False 分支一次都沒引用它。

怎麼重現:讀 `scripts/lumos:29136-29147` 即可看出控制流——`_vwhy` 變數在 `if _vok:` 區塊外沒有任何讀取點,Python 作用域上它在 False 分支就是被丟棄,這是靜態可判定的,不需要跑起來才成立(我也另外在臨時 repo 用 `code-loop pass` + 壓提交 + `code-loop check` 跑過一輪,拿到的仍是走 fail-open「merge-base == HEAD」那條分支,沒能在時限內湊出真正 tier=high 的臨時 fixture 去踩中這條路徑,但這不影響上面這段純讀碼就能確定的控制流結論)。

為什麼是 bug 而不是風格:作者在派工單第 2 點明講「壓過提交之後的失效訊息」這個改法的效果是「訊息直接點出多半是壓過提交或 rebase、並給重來的兩條指令」,派工單裡兩條重來指令一條是表態、一條是「審查留痕重跑 `lumos code-loop pass --note`」。但 `code-loop pass` 留痕失效這條路徑(29131-29147)正是 pre-push/CI 實際擋 push 時最常見的觸發點,而它讀不到新訊息,使用者在這條路上看到的仍是舊版「只丟兩個 sha」的訊息,跟作者宣稱的改善對不上。新增的測試 `t_codeloop_record_invalid_after_squash_says_why`(patch 內)是直接呼叫 `_codeloop_record_valid()` 本體驗證訊息內容,沒有經過 `_codeloop_guard_verdict`/`code-loop check` 這條真正的消費路徑,所以測試綠燈掩蓋了這個落差。

file: `scripts/lumos:29136-29147`(False 分支未讀 `_vwhy`,直接落回舊版 `reason` 字串)
file: `scripts/lumos:28836-28838`(唯一真正用到新 `why` 訊息的呼叫點,只涵蓋「表態」而非「審查留痕」)
