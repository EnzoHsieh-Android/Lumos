severity: major

我是併發資源席,審查範圍是程式組 patch,固定版本 465736e9。實測臨時檔在 `/tmp/lumos-seat-work/code-代理繞閘字樣問人/併發資源-sonnet/`(下稱「臨時目錄」)。發現 3 條,其中 1 條 blocking。

## 發現

1. 預篩對超過 20000 字的指令也跑完整正規化,`$'…'` 的數字跳脫解碼是二次方,整支掛鉤會超過 5 秒預算。

severity: major
blocking: 是

- 輸入與路徑:`entry` 呼叫 `prefilter`,`prefilter` 呼叫 `_Normalizer(text).run()`,正規化遇到 `$'` 時呼叫 `_ansi_decode`,再呼叫 `_ansi_escape`。`_ansi_escape` 每個跳脫都對「剩下的整串指令」做切片再比對。
- 後果:`MAX_LEN` 的閘只加在 `bypass_reasons`,預篩沒有。檔頭註解說 `MAX_LEN` 是為了把掃描壓在幾萬步內,預篩繞過了它。
- 應該:預篩對長指令走字面判斷,或不要先正規化。`_ansi_escape` 改用 `compiled.match(cmd, pos)`,不要切片。
- 引句:「m = re.match(pat, cmd[k + 1:])」
- 重現:整支掛鉤,`--budget 5`,stdin 餵 `git commit -n -m x; echo $'` 加上 N 個 `\n` 再加 `'`。
  - N=300000(約 0.6MB):修後 2.00 秒。
  - N=700000(約 1.4MB):修後 10.90 秒,超過註冊的 5 秒。掛鉤被宿主砍掉後,「問人」不會出現,等於放行。
  - 同一份 ev4.json 跑修前:0.17 秒,而且正確回 ask。
  - 預篩單獨量,`$'\n'` 2MB 要 24 秒;`$'\x41'` 4MB 要 51 秒;`$'\n' ` 重複 6MB 要 77 秒。
  - 2 萬字以內任何形狀都小於 0.1 秒。
- 歸因:有證據的修復回歸。修前 `prefilter` 沒有跑 `_Normalizer`(`git show 9b8ce146:...` 裡預篩不含它),`_ansi_escape` 也是新增的。

2. 整支掛鉤在 git 慢但不逾時時會超過 `--budget`。

severity: minor
blocking: 否

- 輸入:cwd 與 4 個 `-C` 目錄都是暫存底下的真 repo,指令是 4 條 `git -C <dir> commit -n`。假 git 讓 `rev-parse --show-toplevel` 睡 2.95 秒,其餘睡 0.75 秒。
- 路徑:`_root_from_cwd` 固定給 git 3 秒,而且在 `_inner_budget` 的帳外。`_inner_budget` 又有 1 秒下限。之後 4 次 `_git_out` 各自在 1 秒內完成,就不會觸發 `dead`。
- 後果:`--budget 5` 實測 6.28 秒,gitlog 顯示 root 加 4 次呼叫。超過 5 秒的註冊值,掛鉤被砍,ask 遺失。
- 應該:把 `_root_from_cwd` 的耗時算進預算,或讓 `_git_out` 的下限不超過剩餘預算。
- 引句:「timeout=_inner_budget(default=5.0))」
- 歸因:未判定。`_root_from_cwd` 的 3 秒是舊的。`dead` 與 `MAX_GIT_CALLS` 的上限修補沒有擋住這個形狀。
- 另有一條已驗:git 一直卡住時,整支 4.06 秒,在預算內,因為第一次逾時就設了 `dead`。

3. 掛鉤進場後 `_IN_HOOK` 不會復位,同行程之後的批次判斷會繼承過期的預算起點。

severity: minor
blocking: 否

- 輸入:同一行程先呼叫 `entry(...)`,等 3.6 秒,再呼叫 `bypass_reasons(...)`。
- 後果:`bypass_reasons` 不會重設 `_BUDGET_START`,`_inner_budget` 回 1.0,新行程是 3.5。第二次 `entry` 也不會重起算,因為進場只在起點為 None 時才設。批次重跑時,每次 git 只剩 1 秒,慢一點就誤設 `dead`,之後的暫存豁免判斷全部變成「照問」。
- 單一掛鉤行程不受影響。
- 應該:`entry` 結束時復位 `_IN_HOOK` 並清 `_BUDGET_START`,或進場時強制重設起點。
- 引句:「_IN_HOOK["on"] = True」
- 歸因:有證據的修復回歸。`_IN_HOOK` 是修補新增的,修前模組沒有這個名字。
- 補充:`dead` 本身沒有殘留。`bypass_reasons` 每次都重置 `_GIT_STATE`,我連呼叫兩次確認過。

## 已驗的正向主張

- **`MAX_EXPAND`:**
  - 擋得住所有展開路徑。`A=$A$A`、`${A}${A}`、帶雙引號的 `"$A$A"`、`B=$A;A=$B$B` 各重複 2500 次,新版 0.02 秒、19MB。
  - 修前版本只重複 24 次就吃到 274MB。
  - `A=$A$A` 三十幾次吃十幾 GB 的指數增長,這次沒直接重跑(只跑了 24 次)。
  - 4000 字的 A 複製 1500 次、`A=${A}${A}` 重複 3000 次、`A=x;B=y;A=$A$B;B=$B$A` 交叉重複 2000 次都在上限內。
  - 展開結果不會被二次展開(`re.sub` 搭配 lambda,字面的 `$B` 不會再展開)。
  - 上限是按每次出現計算,不是按變數種類。
- **2 萬字內的最壞形狀:**
  - 我試了 35 種形狀,涵蓋巢狀 `$(`、`(`、反引號、ANSI、檔案代號、heredoc、`_strip_redirects`、`cd` 鏈、管線、大括號等。
  - 全部小於 0.1 秒、小於 25MB。最慢的是 `commit -n;` 重複,約 0.08 秒。超過 20000 字的走字面,約 0.001 秒。
- **`_hookevent`(併發):**
  - 8 個行程同時記 3200 筆,`MAX_BYTES` 調到 30000,重複三次。
  - 每次都沒有例外、沒有 False、沒有殘檔,每行都是合法 JSON,0640 權限保留,沒有半行。
  - 剩餘行數只有 107 到 156 行,是預期的修剪結果,符合「掉的那行是已知接受」的註解。
- **`_hookevent`(失敗路徑):**
  - 目錄唯讀:追加仍成功,修剪印警告,檔案持續長大,沒有例外也沒有殘檔。
  - 寫暫存檔時 ENOSPC:印警告,暫存檔被清掉。
  - `os.replace` ENOSPC:同上。
  - 寫入中 `KeyboardInterrupt`:往上丟,但暫存檔已被清。
  - 過期暫存檔:超過 60 秒的被清,新的、連結、其他名字的檔不碰。
  - 事件檔是 0444:`record` 回 False,沒有例外。
  - 單行 500KB 與非 UTF-8 內容:修剪後各剩約 175 與 173 位元組。
- **環境缺失:**
  - 找不到 git 時,整支 0.05 秒,仍回 ask,fail-open。
  - 目錄權限 000 時,整支 0.09 秒,仍回 ask。

## 三問

1. **原問題的修復效果:**
   - `MAX_EXPAND` 已修好:同一案例修前 274MB,修後 19MB。
   - 修剪暫存檔獨立命名、`_clear_stale_trims` 與修剪失敗警告都有行為證據。
   - 逾時設 `dead` 的狀態在批次重跑時不會殘留。
2. **修補處相鄰路徑:**
   - 修補新引入了兩個問題:預篩的二次方(發現 1)與 `_IN_HOOK` 不復位(發現 3)。
   - 預算計算也有缺口(發現 2)。
3. **新發現在修前、修後的結果:**
   - 發現 1:修前 0.17 秒,修後 10.9 秒。
   - 發現 3:修前沒有這個名字,修後殘留。
   - 發現 2:未做修前對照。

## 未驗與範圍外備註

- **符號連結事件檔:** `_trim` 會把符號連結換成一般檔,原目標不被修剪。修前也是 `os.replace`,不算回歸,威脅模型下我沒當 finding。
- **磁碟真滿:** 只用 monkeypatch 模擬,沒有用真滿的卷。
- **多行程修剪中途被 SIGKILL:** 靠 mtime 超過 60 秒清除的路徑已驗(過期暫存檔),沒做真 SIGKILL 的時序實驗。

## 固定席節點

- `Issues/code-loop守衛main-direct盲區.md`、`Systems/pitfalls-code-loop.md`、`Systems/reversibility-governance-ledger.md`、`Systems/guard-kill.md`、`Systems/design-loop.md`、`Systems/測試假綠形態.md`:這次程式組只動 `_hookevent.py` 與新掛鉤,不碰這些節點管的 `scripts/lumos` 守衛、測試或處置閘邏輯,不影響。
- `Systems/lumos-cli-read.md`(search 不排除 stale 的 INVARIANT):程式組沒碰 search 與 superseded 濾網,不影響。
- `Systems/lumos-cli-lifecycle.md`(re-inject 只覆蓋 sentinel 之間):沒碰 re-inject 與 CLAUDE.md 寫入,不影響。
- 超出上限只列名的節點:沒逐條判,與我的併發、資源鏡頭無關。

最嚴重等級 major,blocking 共 1 條。
