severity: major

## g1 文件叫人在 run_cmd 前面加 `cd <平台根> &&`,照做後推送前的合約測試閘會整批變紅
severity: major
blocking: 是
引句:「平台根不在 repo 最上層時前面加 `cd <平台根> && `」
file: `scripts/lumos:73336`(合約測試閘 `_run_bound_tests` 用 `(pentry.root, cmd)` 當鍵,在平台根目錄執行)
file: `scripts/lumos:28015`(殺傷力用 `_kill_run(cmd, wt, …)`,在工作樹最上層執行)

1. 平台根是子資料夾(例 `root: "android"`)時,殺傷力和合約測試閘共用同一條 `run_cmd`,但執行目錄不同。殺傷力在 repo 最上層跑,所以要 `cd android &&`。合約測試閘已經站在 `android/` 裡,`cd android` 會失敗。
2. 人裁的拒絕訊息(`_situation_rule_android_cmd_problem`)和下列三處文件都只叫人加 `cd`,沒有一處提到合約測試閘:
   - 棧別提問表態閘的人裁條列
   - SKILL.md
   - `06-代碼審與推送.md`
3. 三個月後的接手者照做,人裁可以過。之後每一次推送的合約測試閘,凡是綁到該平台的合約測試都判紅。紅燈訊息只寫 `cd: android: No such file or directory`,看不出是 run_cmd 格式造成的。
4. 重現:建一個臨時 repo,`.lumos/config.json` 設 `platforms.kotlin = {profile: kotlin-junit, root: "android", run_cmd: "cd android && echo \"1 test completed\" && test -d ."}`,`android/` 資料夾存在。用 importlib 載入 `scripts/lumos`,呼叫 `_run_bound_tests(Path(repo), [("N","kotlin","fooTest","real")])`。
   輸出:`('N', 'kotlin', 'fooTest', 'red', 'rc=1 /bin/sh: line 0: cd: android: No such file or directory', …)`
5. 文件至少要寫明:這個 `cd` 寫法只適用殺傷力,合約測試閘從平台根跑會壞。另要給出兩邊都能跑的寫法,或承認目前沒有。這個衝突是計劃本身的盲點,不是實作筆誤。

## 其他逐項查證(沒有 finding)

- **行為描述**:新增的 `--import`、`--diff`、Android run_cmd 檢查、`fail_excerpt`、`also`、init 骨架,文件寫的行為都跟程式一致。
  - `--import`:形狀、名稱要在 `--new` 裡、檔頭已有就拒絕、插入點、`imports` 欄、kill-log 的 note。
  - `--diff`:入口驗證、沒採用時印一行。
  - Android run_cmd 檢查:兩種擋法、設定鍵、模組候選、flavor 提示。
  - `fail_excerpt`:弱證據判定才存、遮路徑、每行 200、總共 800、挑不到退回結尾。
  - `also`:只認臨時配方、筆記配方不理。
  - init 骨架:單平台與多平台路徑都改。
- **筆記格式**:三篇新 WHY 的 `[出處:]`、`[因:]`、`[test:]` 齊全。`lumos lint` 對 guard-kill、棧別提問表態閘、lumos-cli-lifecycle 三篇都是 0 問題。
- **`[test:]` 對應**:計劃 S1 到 S9、新 WHY 引的測試、既有 WHY 引的測試,名稱全都在 `scripts/test_lumos.py` 裡。我用 `python3.14 scripts/test_lumos.py -k` 跑了 import、also、init_android、android_run_cmd、diff、fail_excerpt 六組,共 91 個全過。
- **計劃範圍 7**:`lands_in` 三篇都寫回了要求的內容。
- **文件之間的說法**:SKILL.md、06、棧別提問表態閘、guard-kill 對 `--import`、`--diff` 的說法一致。06 和 SKILL.md 沒提「Android 模組的 `:模組:test`」也會被擋,只是少列一種情況,我不算問題。

## 附:圖譜鏡頭

這次沒附固定席節點。派工指令提到的鎖檔 `…dispatch-lens/3e6c2aa7…json.warming` 不存在,所以沒有鎖要處理。

我另外看了這份 diff 牽連的四篇筆記,結論是不破壞它們宣稱的行為或合約:
- **guard-kill**:新增的 `also` 只走 `recipes_override`,其他呼叫端不傳、行為不變,跟既有 WHY 一致。
- **棧別提問表態閘**:人裁流程多了前置檢查和旗標,段與列、寫回、記帳的既有順序沒動。
- **lumos-cli-lifecycle**:init 的改動只影響 Android 專案的骨架。
- **治理帳欄位型別**:`_GOV_FIELD_TYPES` 只加了 `imports` 一欄,不影響既有欄位。

最嚴重 severity: major,blocking 共 1 條。
