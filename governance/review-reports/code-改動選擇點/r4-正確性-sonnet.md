severity: clean

我在 `/Users/enzo/harness/lumos-near-miss` 的臨時副本裡,對 24ec789 跑了新增測試和兩種改壞,沒找到會做出錯行為的缺陷。前面列的是已驗的正向主張,後面是尚未驗到的範圍。臨時副本已刪。

沒有 finding。最嚴重:clean;blocking 共 0 條。

## 原問題修復效果的證據

**整批掃描不套忽略規則(J2)**
- 修後(24ec789):`python3.14 scripts/test_lumos.py -k choice_scan_batch` 全綠,共 5 條,含真 ast-grep 0.51.2 那條。
- 修前:把 `scripts/lumos` 換成 dbdc038、保留新測試,`-k choice_scan_batch_no_ignore` 為 0 passed、2 failed。
- 另做獨立重現:暫存目錄放在 `.gitignore` 寫 `*.kt`、`.ignore` 寫 `src` 的 repo 底下。修後掃 1、2、3 支檔,每支都是 1 個命中,沒有退化成零命中。
- 舊版 ast-grep 若不認六個 `--no-ignore` 值,整批會非零退出,走 `_choice_scan_each` 逐檔,逐檔路徑沒帶這幾個旗標,結果仍對。

**`類別.方法` 測試名找不到所在檔(J1)**
- 修後:`-k test_blobs` 6 條全綠,其中 `t_choice_test_blobs_name_shape` 的 expected 用 `git rev-parse HEAD:<檔>` 取得,不是照抄實作。
- 修前:同一組測試 3 passed、3 failed,`FooTest.bar` 回傳 `?`,對得上原缺陷。
- 句子名(`parses 1.5 values`)照整串找、只含尾段的檔不算,這兩條在修前修後都綠。這是保護條件,不是修復證據。
- 「所在檔」固定(`FooTest.kt`)的斷言都有。
- 副檔名不屬於平台的檔(`cases.md`)改了,雜湊不變,修後成立。

**整批只用一半時限(J2)**
- 把 `_CHOICE_BATCH_SHARE` 改成 1.0,`t_choice_scan_batch_share` 翻紅(0 passed、1 failed)。還原後翻綠。

**拿掉推送前多算的時限底線(J3)**
- `-k spec_gate_push_choice` 共 42 條全綠。
- 拿掉底線之所以安全:`_choice_requirement` 已用同一份 `cache` 算過碰到的計劃(`_choice_spec_calc`),`_choice_guard(..., cache=cache)` 一定命中。
- 沒有別處接 `_choice_push_scan` 的三元組(grep 只有 `_choice_push_round` 和一條測試)。
- 呼叫 `_choice_guard` 時不帶 `cache` 的兩處(`_choice_ledger_status`、`choice-kill`)不在推送前路徑。

**rc 2 與 doctor 計數(J4)**
- 這兩個行為修前就有:dbdc038 的 `scripts/lumos` 已經有 `or res.get("unverified")`,doctor 的 `_lint_waivers_split` 也已存在。這輪只補了測試。
- `-k choice_kill_partial_unverified_rc` 與 `-k lint_waive_choice_ai_summary` 全綠(2 條、5 條)。
- 我沒有對這兩條做變異翻紅,只靠讀程式與跑綠。

## 相鄰路徑與新舊互讀
- 一般名與兩平台同名:`-k choice_kill_rerun_rules` 11 條全綠。
- 一般名的 `term == name`,所以修前寫的帳的 `tests_sha` 不變。
- 修前寫的、帶 `?` 標記的 `tests_sha`(`FooTest.bar` 這類):`_choice_push_stale_tests` 遇到標記就跳過,所以不會誤報。choice-kill 那邊則當成「變了」,存活的行重跑一次。
- `anchor-baseline.json` 記的 `test_lumos.py` 雜湊,與 24ec789 的實檔 sha256 一致。

## 看過但不成立的疑慮
- 常見方法名(例如 `X.init`)取最後一段後會比對很多檔,`tests` 欄可能變得很大。我造了 3000 個測試檔、每檔 60 個 `init`,實測 0.47 秒、簽名字串約 123KB。
- `_choice_gate_event` 搭配 `list_key="tests"` 會縮小事件,`S20` 測試證明事件上限 4096 位元組,不會寫失敗。所以不報。
- 裸名(不帶類別)本來就有同樣的行為,不是這次修補新增的。

## 未驗範圍
- 沒跑真 Android 專案的端到端。
- 沒跑 ast-grep 舊版(不認 `--no-ignore` 值)的實機,只憑讀程式推論會退回逐檔。
- 沒有對 J4 兩條新增測試做變異翻紅。
- 圖譜鏡頭:這次沒附固定席節點,無從逐條判斷。
- 角色鏡頭:be-api-compat 已走過,見上面「新舊互讀」,帳的欄位與雜湊對舊帳向下相容,沒有改名或刪欄。be-authz:這個 repo 是本機命令列工具,沒有端點,不適用。
- 全程只跑了 `-k` 子集,沒跑不帶 `-k` 的全套。
