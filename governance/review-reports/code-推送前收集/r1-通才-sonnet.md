severity: major

已讀兩份 patch,實測三件事:新增告警閘直接重跑、不帶 `--keep-going` 的輸出前後對照、相關測試子集。

### finding 1
severity: major
blocking: 是 — 新增告警閘在這批改動上判擋下,作者照現狀推送會被自己的 pre-push 和 CI 攔住
引句:「def cmd_code_loop(subcmd, note=None, repo=None, as_json=False, diff_range=None, at_sha=None」
問題:兩支既有的複雜函式都被改了簽名(各加一個 `keep_going` 參數)。新增告警閘認指紋,指紋對到的是 `def` 那一行,簽名一變,舊的 C901 告警就被當成「這次新帶進來的」。
- 此外 `_codeloop_guard_verdict` 的複雜度真的變高:35 變 40。patch 說所有 return 都經 `_fin` 收尾,但分支數沒降,反而加了 `keep_going` 的分流。
- `cmd_code_loop` 是 53 變 26,實際下降,卻因簽名變動照樣被點名。
具體失敗情境:在 `a9362d4c` 的 `--shared` clone 裡跑 `code-loop check --diff e0da694b..a9362d4c --skip-bound-tests --note x`,輸出如下,rc 為擋下:
```
擋下:這次改動帶進了新的問題(2 條新增告警)
  - scripts/lumos:51283 [C901] `_codeloop_guard_verdict` is too complex (40 > 10)
  - scripts/lumos:51803 [C901] `cmd_code_loop` is too complex (26 > 10)
```
作者沒有帶 `lint-waive` 紀錄,也沒有把函式再拆小。這份 patch 本身通不過它新增的功能所在的閘。
佐證:ruff 設定來自 ``file: `.lumos/lint.json:3` ``。在 base 與 head 各跑 `ruff --select C901 --config 'lint.mccabe.max-complexity = 10'`,得到 35→40 與 53→26。

### finding 2
severity: minor
blocking: 否 — 逃逸帳一次推送可能多記一筆,不影響擋不擋,只影響統計口徑
引句:「記幾筆:rc1 時不論那一行在不在、解析出幾筆,至少一筆;每個種類各一筆」
問題:掛鉤的逃逸自動記帳是對 `_cl_out` 各 grep 一次:「受波及合約的測試沒過」記一筆 `push-gate`,「tier=high 且」記一筆 `push-gate-unreviewed`。
- 原本合約測試先紅就提早 return,只會印第一道,所以只記一筆。
- 現在 `--keep-going` 四道都跑完並全部印出,同一次推送「合約測試紅且高風險缺留痕」會兩句都在,兩筆都記。
- 原註解特意避免這種雙記(r2 回滾席),patch 沒更新那段判斷。
具體失敗情境:合約測試紅加上高風險無留痕,一次 rc1 就記兩筆 major 逃逸。使用者修好測試重推後,缺留痕那筆會再記一次,`push-gate-unreviewed` 的筆數會高於實際的下游抓漏次數。這是我從程式推演的,沒有實跑掛鉤驗證。
佐證:``file: `scripts/hooks/pre-push:560-568` ``(grep 兩段在 `if [[ "$cl_rc" -eq 1 ]]` 內)。

### 已讀,無 finding
- 不帶 `--keep-going` 的 `code-loop check` 輸出:用 base 版 `scripts/lumos` 與 head 版在同一個 clone、同一個 repo 內容下對照三種範圍,輸出逐行相同,只差測試耗時的秒數。已確認「一字不差」成立。
- 逃逸自動記帳的 `grep` 句型、`LUMOS-BLOCKS:` 行的濾除、rc=0 時的提醒行輸出,都未壞。
- `_fin` 的各個 return 站點、`pf_fail` 時新增告警閘照跑,與 `_codeloop_review_block` 回 `reason_kind: review` 都對得上掛鉤的對照表。
- 回頭重讀的呼叫行仍含 `note-audit reread-check` 且帶 `--gate`。新增的註解與函式沒有出現會干擾上線標記的字串,`lumos enforcement` 的接線檢查沒受影響。
- 錨點驗證、doctor、home、note-shape、spec-gate、drift、reread 改記下後,中間沒有 `exit 0` 會把已記的擋下吃掉(檢查過 `exit 0` 的位置),彙總在全套測試前統一 `exit 1`。
- 子集測試全綠:`-k prepush` 250 passed,`-k enforcement` 68 passed,`-k golive` 17 passed,`-k keep_going` 34 passed,皆 0 failed。
- 暫存的實驗目錄已刪除。

最高等級 major,blocking 共 1 條。
