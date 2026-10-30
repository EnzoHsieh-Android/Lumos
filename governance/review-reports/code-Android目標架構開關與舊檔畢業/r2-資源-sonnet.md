severity: minor

本席的立場是把機器資源用光的人。逐 hunk 走過大輸入,沒找到會做出錯行為的資源問題,只有一條 minor。所有量測都在固定提交 44b0044da 的副本上做。

## Finding

### 1. 代碼審判定說明行在有畢業檔時多叫一次「列改動檔」,在消費專案約多 1 秒
severity: minor
blocking: 否

- 輸入:消費專案(不是工具鏈本體),起點版有宣告、舊檔清單少了行,也就是 `keep` 非空。
- 走到的位置:`_arch_legacy_check_lines` 的 `_arch_target_changed_files(root, base, head)`。這一呼叫沿 `_review_role_changed_files` 走到 `_vendored_skip`,再到 `_vendored_state`。後者對每支工具檔各叫一次 `git show`,終點與起點各一輪。
- 引句:「targets = _arch_target_split(_arch_target_changed_files(root, base, head), rules)」
- 量測:`_VENDORED_ALL` 有 31 支,一次呼叫花 65 次 git、約 0.97 秒。
- 這一呼叫是為了印一行說明才重算。這一輪推送前分級已經算過同一份改動檔。
- 為什麼只標 minor:`code-loop check` 本來就要 6 到 25 秒,多 1 秒不會把正常操作擋下。我也沒找到造成失敗的場景。
- 歸因:有證據的修復回歸。修前的 `_arch_legacy_check_lines` 同樣有這一呼叫,所以是「原有漏查」。判成回歸是因為修補把它搬進共用路徑,但行為沒變。我把它判為未判定:兩版都有,沒有獨立的修前紅。
- 兩版命令:`git show 006c398b:scripts/lumos | grep -n "_arch_target_changed_files(root, base, head)"` 與 `git show 44b0044da:scripts/lumos | grep -n "_arch_target_changed_files(root, base, head)"`。兩版在 `_arch_legacy_check_lines` 裡都出現,各一處。

## 資源問題逐項(都沒成立)

- **子程序收尾:** 新增的 git 呼叫全走 `_lens_git`,有 timeout(`git show` 10 秒,其餘 20 秒),也都用 `subprocess.run`。逾時與 Ctrl-C 時由 `subprocess.run` 收子程序,沒有新的孤兒程序路徑。
- **派工鏡頭 5 秒預算:** `_arch_legacy_apply` 在預算迴圈之後執行,本身不受那 5 秒限制。我拿 300k 行(5.5MB)的舊檔清單,起點與終點不同,量到 apply 約 0.20 秒。清單少一行也是同樣量級。這個量級放得進預算外的呼叫。
- **大檔與二次方:**
  - `_arch_legacy_apply` 對改動檔是線性,清單用 set 查。
  - 300k 行清單讀入約 127MB 峰值記憶體,可接受。
  - 畢業判定在 head 等於 ref 時只讀一份(0.08 秒)。
- **doctor 重複比對:** `_arch_legacy_doctor_lines` 的 `stray` 迴圈對每個清單項各跑一次 glob 比對。同函式的 `hits` 迴圈對每個追蹤檔也跑一次,兩者重複。這是線性,不是二次方。
  - 輸入:300k 追蹤檔、300k 清單行、40 條宣告。
  - 量測:各約 7 秒,doctor 總計約 14 秒。
  - 現實規模(清單 2 萬行以下)約 0.5 秒。doctor 不是閘,所以只記錄、不標 finding。
- **doctor 在沒用這功能的專案:**
  - 做法:拿一個沒有 `.lumos/` 的 repo,比較修補前後的 `_arch_target_doctor_lines`。
  - 300k 檔的 repo:0.04 秒變 0.18 秒,git 呼叫從 2 次變 5 次。
  - 本 repo 16.5k 檔:0.021 秒變 0.094 秒,git 呼叫從 1 次變 4 次。
  - 多出的是一次 `ls-files`、建 NFC 集合、讀一次舊檔清單(最多 2 次 git)。
  - 結論:約 0.1 秒、沒有宣告也沒有清單時不做 glob,不構成擋人理由。若要省,可以等 `_arch_legacy_at` 回 `missing` 再叫 `ls-files`。
- **迴圈裡重複叫 git:** 同一支畢業測試有 496 次 `git show`,來自 `_vendored_state`,見 finding 1。這是原有行為,不是這份 diff 新增。

## 本案特定鏡頭:四支新測試跑時

| 測試 | 實測 |
|---|---|
| `t_arch_target_graduate_same_branch` | 約 50 秒(作者量 42 秒) |
| `t_arch_target_graduate_check_note` | 約 35 秒 |
| `t_arch_target_legacy_doctor_lines` | 約 7.8 秒 |
| `t_arch_target_spec_lens_reads_legacy` | 約 3.4 秒 |

啟動本身約 1.3 秒。

- `same_branch` 的時間分布:496 次 in-process `git show`(約 15.6 秒)、4 次子程序 `dispatch-lens` 與 `pitfalls`(約 20 秒)、提交約 1.5 秒。
- `check_note` 的時間分布:5 次 `code-loop check` 子程序佔約 29 秒,每次約 6 秒;提交與切分支不到 2 秒。
- 測試跑時沒降到作者聲稱的水準,但也沒再出現 r1 說的「每個情境各起一次 lumos 子程序」。

## 修補鏡頭三問

1. **原問題的修復效果:**
   - 資源席 r1 指的是畢業測試每個情境各起一個 `lumos` 子程序。修後 `same_branch` 的子程序縮到 4 次(A、B、I 三個接線案例再加對照)。
   - 命令:`python3.14 scripts/test_lumos.py -k t_arch_target_graduate_same_branch`。結果:17 項檢查全過,約 50 秒。
   - 修前沒有存下結果,我沒有重跑修前版本。修前跑時沒有獨立量測可比,記為未判定。
2. **修補處的正常、錯誤與相鄰路徑:**
   - doctor:
     - 列檔失敗傳 `None` 時,「已不存在」寫「算不出」。
     - `git-failed` 回「讀不到」提醒。
     - 沒宣告但有清單時,照樣印清單行。
     - 這幾條我是讀碼確認,沒有逐一造輸入。
   - 派工鏡頭與推送前分級:改接 `_arch_legacy_graduation` 後,`head == ref` 與 `head is None` 都回空畢業集合。
   - 設計審鏡頭:`_dispatch_lens_spec_arch_text` 傳 `head=None`,不讀終點。
   - 這些分支我只量過資源,沒有逐一驗行為對錯。
3. **新發現同一案例的修前修後:**
   - finding 1 兩版皆有同一行 `_arch_target_changed_files`,所以不是修補新增。
   - doctor 多叫 `ls-files` 是修補新增:修前沒宣告時提早返回。修後約多 0.1 秒,不構成 finding。

## 固定席(來源 impact --diff)逐條判定

- **Issues/code-loop守衛main-direct盲區:** 不影響。這份 diff 不碰守衛的 main-direct 判斷,只在判定說明行與分流上加讀舊檔清單。
- **Systems/lumos-cli-read(含 INVARIANT:search 預設排除 superseded 但不排除 stale):** 不影響。diff 沒動 search 的濾網順序。
- **Systems/pitfalls-code-loop(RISK):** 不影響。分級那一行只換成 `_arch_legacy_apply`,分流結果由 `same_branch` 的 A、B 以子程序守住,測試綠。
- **Systems/arch-alignment-lens:** 不破壞。diff 只在舊檔清單上扣檔與畢業放回,宣告與目標節點讀法沿用。
- **Systems/design-loop(INVARIANT:處置閘第五步):** 不影響。diff 沒動處置閘判定。
- **Systems/測試假綠形態(INVARIANT:還原翻紅釘要配前置斷言):** 不影響。新測試是新增,沒修改既有 bug 的釘。
- **Systems/guard-kill:** 不影響。diff 沒動 `guard kill` 的 rc 優先序與 `--json` 輸出。
- **Systems/reversibility-governance-ledger(RISK):** 不影響。diff 沒碰可逆性帳本。
- **其餘「超出上限只列名」的節點:** 不逐條判。

## 已驗與未驗

- **已驗:**
  - 子程序都有 timeout。
  - 大清單(300k 行)、大 repo(300k 檔)下,doctor、畢業判定與 apply 的跑時。
  - 四支新測試的跑時與子程序、git 呼叫分布。
  - doctor 在沒宣告、沒清單的專案多出的成本。
- **未驗:**
  - 修前版本四支測試的跑時。
  - 慢磁碟或慢機器下 5 秒預算與 45 秒掛鉤逾時的實際邊界。
  - 病態輸入,例如清單巢狀超深或單一路徑極長。
- **清理:** 我的臨時目錄 `/private/tmp/lumos-seat-work/code-Android目標架構開關與舊檔畢業/資源-sonnet` 已用字面絕對路徑刪除。

最嚴重等級為 minor
