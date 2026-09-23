severity: blocker

## F1 新擋的 `_roster_kind()` 用法跟同檔既有的 fail-closed 慣例方向相反,原地驗證可繞過

severity: blocker
blocking: yes

這條擋(`cmd_canary` 裡「代碼審從第一筆就要留痕」)判「是不是代碼審」改走 `_roster_kind()`,但只在回傳恰好等於 `"code"` 時才生效:

引句:「if (loop and _roster_kind(str(loop)) == "code" and outcome is None」

`_roster_kind()` 對「code 開頭但沒有連字號」(例如既有帳裡的 `codestage`、`code側刪除傳播守衛`)回傳 `None`——這批 patch 自己的註解也承認這種情況「照舊不強制」:

引句:「那種照舊不強制,這裡只擋明確的代碼審。」

問題是:這個 repo 對「`_roster_kind()` 回 None(看不出是代碼審還是設計審)該怎麼處理」早有三處established 慣例,而且方向都是**把不確定的一律當成最嚴的那一種、不讓人靠取一個怪編號繞過**:

- `scripts/lumos:17812`:「_roster_kind 回 None(code 開頭但不是 code-)一律當設計審:fail-closed,免得取個 codeX 的編號就繞過」
- `scripts/lumos:17744`:訊息原文「編號 code 開頭卻不是 code-,看不出是哪一種審查,照最嚴的當代碼審」
- `scripts/lumos:17866` 同一支 `_disposal_landing_step` 沿用同一個判法

這三處全部是「看不出是哪一種 → 當成需要更嚴格檢查的那一邊」。而這次新加的擋恰恰相反:看不出是哪一種 → 當成不需要檢查的那一邊(不強制帶 `--report`/`--snapshot`)。方向整個反過來,而且反過來的後果就是重新打開這一輪 patch 本來要關掉的那個洞(代碼審第一筆記帳漏帶 `--snapshot` 安靜通過)。

我在 /tmp 建了乾淨 repo + 臨時 vault 實測(唯讀,沒碰這個 repo 的 git):

```
lumos canary record none --loop codeXreview-sonnet-C --round r1 --auditor tester \
  --severity clean --findings 0 --report <帶 severity: clean 的報告檔>
→ rc=0,寫入成功(沒帶 --snapshot 也放行)

lumos canary record none --loop code-review-sonnet-C --round r1 --auditor tester \
  --severity clean --findings 0 --report <同一份報告檔>
→ rc=2,擋下:「代碼審(code-review-sonnet-C)的每一筆記帳都要帶 --snapshot……」
```

同一份操作,只因為迴圈編號少了一個連字號(`codeXreview-sonnet-C` vs `code-review-sonnet-C`),這一輪 patch 要修的漏洞就原封不動地重現——而這正是那三處既有 fail-closed 慣例特別點名要擋的取名繞過方式。既然同一支分類器在同一支檔案裡已經有三個呼叫點示範了「不確定就從嚴」的接法,這裡沒有照抄,是跟同檔既有做法不一樣。

## F2 新測試沒有沿用全檔共用的模組載入 helper,自己重複一份 loader 樣板

severity: minor
blocking: no

引句:「loader = importlib.machinery.SourceFileLoader("lumosmod_sq2", GRAPHCTL)」

`scripts/test_lumos.py:5169` 已經有共用 helper `_import_lumos()`,專門做「把 scripts/lumos 當模組載入供單元測試內部函式」這件事,全檔已有 7 處呼叫點在用。新加的 `t_codeloop_check_after_squash_says_why()` 沒有呼叫它,而是自己手寫一整段 `SourceFileLoader`/`spec_from_loader`/`module_from_spec`/`exec_module`(命名成 `lumosmod_sq2`)。

這不是全新的寫法——它是照抄緊鄰的同一份修正差異裡、round 1 就有的姊妹函式 `t_codeloop_record_invalid_after_squash_says_why()`(用 `lumosmod_sq`)的手法,所以跟「隔壁那支」一致;但跟全檔更通用的 `_import_lumos()` 慣例不一致,屬於選了近的先例、沒選共用 helper,影響小,列 minor。

## 我驗過哪些路徑

- 讀了整份凍結 patch(189 行)逐段比對 `scripts/lumos` 現行檔案裡 `_roster_kind`、`_codeloop_record_valid`、`_codeloop_guard_verdict`、`_disposal_clause_step`、`_disposal_landing_step` 的既有呼叫慣例(`grep -n "_roster_kind("` 全部 9 個呼叫點都看過)。
- 讀了 `scripts/test_lumos.py` 裡 `_import_lumos()` 定義處與其餘 `SourceFileLoader`/`spec_from_loader` 用法(約 20+ 處),確認 F2 的先例判斷。
- 讀了 `git merge-base --is-ancestor` 在本檔另外三處(`_nodehome_clamp_base`、testmap `affected`、push-lens `_mainline_ref` 一段)的 returncode 處理慣例,跟新加的「非 0/1 → 講成找不到」比對,沒有發現足以構成 finding 的不一致(既有慣例本身也不統一:有的把任何非零一律當非祖先、有的把 rc≠1 當「略過該訊號」),不列為發現。
- 在 /tmp 建臨時 git repo + 臨時 vault,實跑 `lumos canary record` 兩種迴圈編號(`codeXreview-sonnet-C` vs `code-review-sonnet-C`)對照,機械驗證 F1 的繞過確實可重現(全程只動 /tmp,沒有對 /Users/enzo/harness/lumos-toolchain 跑任何會改動的 git 指令,結束後已清掉臨時目錄)。
- 沒有讀 `governance/review-reports/` 底下任何 rN-*.md,沒有派子代理。
