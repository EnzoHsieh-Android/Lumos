severity: major

## s1 choice-kill 印出的「要放行」貼上即用指令，檔名沒加 shell 引號，檔名裡的 `$(...)` 會被執行
severity: major
blocking: 是(外來檔名進貼上即用的指令,貼上就執行任意指令;已實測重現)

- 攻擊路徑:
  - 誰:能提交 `.kt` 檔的人(外部 PR 作者),或任何檔名帶空白或 `$` 的一般檔。
  - 從哪:`lumos choice-kill` 對「不唯一」的行(前後各 2 行都相同、`old` 帶不出唯一一段)印出的放行建議行。`_choice_kill_report` 的 `nu` 清單走這裡。
  - 送什麼:檔名例如 `app/src/main/Foo$(touch PWNED).kt`,檔裡有連續相同的行與一個選擇點。git 允許這種檔名。
  - 拿到什麼:照派工詞與全域規則,AI 會把印出來的指令貼進 shell。
    - zsh 裡 `$(touch PWNED)` 先被執行,拿到任意指令執行。
    - 檔名只有空白時,參數被切開,放行指令壞掉。
- 壞在哪:`_kill_esc` 只跳脫控制字元,不處理 shell 特殊字元。同一份新碼的其他三處(`_situation_rule_test_platform`、`_situation_rule_point_next`、`lumos spec-gate …`)都用 `_sh_quote`。只有這一處漏掉,函式註解就寫著「印給人照貼的指令裡的一個參數加 shell 引號」。
- 預期:`lumos lint-waive 'choice:app/src/main/Foo$(touch PWNED).kt:12' --note …`。實際:引號都沒有。

引句:「f"lumos lint-waive choice:{_kill_esc(x['file'])}:{x['line']} --note \"不適用:<理由>\"")」

file: `scripts/lumos:78210`(24ec7896 版)
file: `scripts/lumos:468`(`_sh_quote` 的定義與用途)

最小重現(在臨時副本,已跑):用 importlib 載入 `scripts/lumos`,以 `nu=[{"file":"app/src/main/Foo$(touch PWNED).kt","line":12}]` 呼叫 `_choice_kill_report`。輸出:

```
app/src/main/Foo$(touch PWNED).kt:12  不唯一(…)——不跑;要放行:lumos lint-waive choice:app/src/main/Foo$(touch PWNED).kt:12 --note "不適用:<理由>"
```

歸因:這輪新加的 `_choice_kill_report`(第二段 choice-kill)。

## s2 `LUMOS_CHOICE_SINCE` 在正式推送也生效,而且不留帳
severity: minor
blocking: 否(縱深防禦;擋不住是靠一行提醒,不是靠記帳)

- 攻擊路徑:
  - 誰:使用者本人,或照常操作的 AI。
  - 從哪:shell 裡殘留的 `export LUMOS_CHOICE_SINCE=9999-12-31`。這就是測試總檔 `setdefault` 用的那一行值,從文件或腳本複製出來很容易。
  - 送什麼:一次 `git push`,範圍含 Kotlin 正式碼的改動。
  - 拿到什麼:`_choice_push_round` 在最前面回 `[]`,選擇點整道不跑。只印一行「被環境變數關掉」,而且只在專案有 kotlin-junit 平台時印。不記治理帳。
- 對照:同一支檔裡 `LUMOS_KT_CATALOG` 用 `_kt_under_test_runner()` 限定只在測試執行器生效。專案文件裡的 `LUMOS_SKIP_*` 都標「留帳」。`LUMOS_CHOICE_SINCE` 兩樣都沒有。

引句:「return v if _DAY_RE.fullmatch(v) else _CHOICE_SINCE」

file: `scripts/lumos:39534`(`if env and _kt_under_test_runner():`,對照組)
歸因:這輪新加的 `_choice_since` 與 `_choice_push_round`。

## s3 ⚠ ast-grep 解不到時推送那一道只提醒,圖形 Git 客戶端的短 PATH 會一步走過
severity: minor
blocking: 否(計劃明寫的取捨,且記了 unverified;嚴重度判不準,標 ⚠)

- 攻擊路徑:
  - 誰:用圖形 Git 客戶端(Android Studio、Fork 之類)推送的使用者。
  - 從哪:客戶端起的 pre-push 掛鉤,PATH 只有 `/usr/bin:/bin` 一類。
  - 送什麼:有未處置選擇點的 Kotlin 改動。
  - 拿到什麼:`_lint_wt_resolve_tool("ast-grep")` 只查 PATH,找不到就 `_ChoiceNoTool`,選擇點那一道回「只提醒不擋」。成功推送時多數客戶端不顯示掛鉤輸出。
- 掛鉤自己的註解承認「圖形用戶端的 PATH 很短」,但只為 python 補了固定位置,ast-grep 沒有。CI 也不接這一道(`.github` 裡沒有 spec-gate),沒有第二道補。
- 已跑 `t_choice_no_ast_grep`,6 項全綠,確認這個行為是設計內的。

引句:「return "unverified", _choice_push_unverified(rr, at_sha, f"ast-grep 不在({e})", hint=f"裝 ast-grep 後再推:{_CHOICE_INSTALL}")」

file: `scripts/hooks/pre-push:215`(固定位置排在 python3 前面,承認圖形用戶端 PATH 很短)
歸因:這輪新加的 `_choice_push_scan`。

## 逐類結論
- ① 提示注入:
  - 檔名與 `decl` 進輸出時都過 `_kill_esc`;帳本欄位型別檢查在 `_GOV_FIELD_TYPES`。
  - 命令行裡的外來字串只有 s1 那一處。
  - gov --stats 印的 no_result 原因取冒號前那段,是固定字串。
- ② 讀寫與執行越界:
  - ast-grep 走 `_lint_wt_resolve_tool`(拒 repo 內與相對 PATH 項)、參數清單不開 shell、設定檔限定在 `configs/ast-grep/` 內、暫存檔名用序號;已看,無。
  - `git grep` 的測試名走 `-e`、`-F`,不會被當成選項;已看,無。
  - 壞法寫檔有 realpath 圍欄(`cmd_guard_kill`),已看,無。
  - 密鑰與信箱:已看,無;安裝腳本與下載來源:沒有改動。
  - sgconfig 沒有 customLanguages 或 libraryPath。
- ③ 非刻意繞過:s2、s3。其餘已看,無:
  - Ctrl-C:`_choice_sg_run` 與 `_ChoiceKillRun` 兩段式訊號。
  - 檔名帶空白或中文:`rpartition` 切放行鍵、`nfc`、`-z` 解析。
  - 新分支首推:`_push_range_start`。
  - 舊版工具:`_SG_PR` 探測。
  - 單檔超過 4MB 時 `res["big"]` 在推送那一道不印也不擋;這是邊緣情況,找不出一般操作會碰到的場景,沒標。
- 圖譜鏡頭:這次沒附固定席節點,無可逐條判。
- 備註:`governance/anchor-baseline.json` 和 `.lumos/lint-waivers.json` 的自簽與 AI 放行,都引了使用者 2026-11-14 的睡前授權原話,屬使用者自己的裁定,不當發現。

## 實際讀過的檔
- 逐行讀完:
  - `scripts/lumos`:快照 8479–12225,即全部 hunk,含新的選擇點三段、`cmd_guard_kill` 選用參數、`lint-waive`、`situation-rule --point`、gov --stats。
  - `scripts/hooks/pre-push`:新增的 hunk。
  - `.lumos/config.json`:無問題。
  - `.lumos/lint-waivers.json`:新增一筆 AI 放行(C901),屬使用者授權。
  - `configs/ast-grep/kotlin-android/check.py`:快照 55–560,新增的 `choice_tables` 讀表與 `scan_ranges` 的 `config_path` 參數,無問題。
  - `configs/ast-grep/kotlin-choice/sgconfig.yml`、`rules-arid/arid.yml`、`rules-syntax/error.yml`:無問題。
  - `r4-repair-code.patch` 全部程式 hunk:無新增洞。
- 只做樣式掃描,沒有逐行讀:
  - `configs/ast-grep/kotlin-choice/rules-choice/*.yml`:掃 `fix:`、`url`、`transform`,無。
  - `configs/ast-grep/kotlin-choice/samples/*.kt`:未讀內容。
  - `scripts/test_lumos.py` 新增的約 2500 行:掃 `shell=True`、`os.system`、`eval`、網址、密鑰、信箱、`LUMOS_*`、`rmtree`、`/tmp`。
  - docs、skills、`governance/replay`、`governance/review-reports` 的散文:掃密鑰、信箱、網址、`rm -rf`、`curl`。
  - 這幾類只判到「模式掃描無異常」,沒有逐行確認。
- 截圖與機械結果:`lumos lint-new` clean 沿用派工詞,沒自己跑。

最嚴重:major;blocking 共 1 條
