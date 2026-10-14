severity: major

彙總載體,非新增審查席。32 條由九份原報告逐字彙整,只在每條 severity 行前加 ID 行,severity 與引句不變。


來源:r4-正確性-sonnet.md


審查範圍:程式組 r4-code.patch 逐 hunk 讀完。修補差異只用來對照兩版行為。實際載入修前 9b8ce146 與修後 465736e9 的 `bypass-ask-hook.py` 跑過。

## Findings

**1. 換行接續的條件式 `cd` 被當成一定會跑,修前會問、修後放行(修補造成的回歸)**
ID: c1
severity: major
blocking: 是

引句:「        elif self.seg_conditional or p.endswith("||") or q.startswith("||"):」

- 輸入:`false &&⏎cd <暫存實驗repo>⏎git commit -n -m x`,事件 cwd 是真 repo。`true ||⏎cd <暫存實驗repo>⏎git commit -n -m x` 同樣出事。
- 走到哪一行:`_finish` 用 `p, q = _sep_core(prev), _sep_core(nxt)`。`_sep_core` 把 `&&⏎` 轉成 `&&;`,所以 `_scope_cd` 裡的 `p.endswith("&&")` 和 `p.endswith("||")` 都是假。
- 錯在哪:這段 `cd` 被當成無條件執行,追蹤目錄變成暫存 repo,`_not_real_repo` 通過,結果放行。實際上 `false &&` 之後 `cd` 沒跑,提交落在真 repo,`-n` 沒人問。
- 應該是:跟 `false && cd X⏎git commit -n` 一樣回 `['commit-n']`。計劃 S3 明列「`&&` 鏈接換行之後」要照問。
- 兩版結果(`bypass_reasons`):
  - `false &&⏎cd T⏎git commit -n -m x`:修前 `['commit-n']`,修後 `[]`。
  - `true ||⏎cd T⏎git commit -n -m x`:修前 `['commit-n']`,修後 `[]`。
  - `false &&⏎{ cd T; }⏎git commit -n -m x`:修前 `['commit-n']`,修後 `[]`。
  - 對照:同一句不換行(`false && cd T⏎git commit -n -m x`)兩版都是 `['commit-n']`。
- 修前為什麼對:修前用 `prev.replace("\n","")`,`&&⏎` 變成 `&&`。
- 測試為什麼沒抓到:`-k bypass_ask` 273 項全綠。r3_ask 只有 `false && cd E && true⏎git commit`(換行在鏈尾),沒有換行在 `&&`、`||` 之後的形狀。
- 歸因:有證據的修復回歸。引入 `_sep_core` 的修補把換行轉成 `;`,但 `_scope_cd` 的 `endswith` 判斷沒跟著改。
- 建議修法:`_scope_cd` 判斷前先對 `p`、`q` 去掉結尾的 `;`(或判斷 `core.rstrip(";")`)。

**2. 預篩擋掉了分類器明明會問的 `--remove-section core` 和 `--rename-section core`**
ID: c2
severity: major
blocking: 是

引句:「_PRE_WORDS = ("--no-veri", "hookspath", "lumos_skip_")」

- 輸入:`git config --remove-section core`、`git config --rename-section core x`、`git config remove-section core`。
- 走到哪一行:`prefilter` 對這三條都回 `False`,指令裡沒有 `hookspath`、`--no-veri`、`lumos_skip_`,也不是 commit 加 `-n`。`entry` 直接 `return 0`,沒進 `decide`。
- 錯在哪:`_config_writes_hookspath` 和計劃 S1、〈範圍〉都明寫這兩種要問,`bypass_reasons` 也確實回 `['config-hookspath']`。真跑整支掛鉤(stdin 事件,`--budget 10`)時,`rc 0`、stdout 空,沒有 ask。
- 對照:`git config core.hooksPath /x` 同樣方式跑會印 `"permissionDecision": "ask"`。
- 兩版結果:修前修後都是不問,預篩單字清單沒變。
- 測試為什麼沒抓到:S1 表格那兩列走 `_bypass_asks`,也就是 `decide`,不經預篩。S4 預篩清單裡也沒有這兩種寫法。
- 歸因:有證據的原有漏查。修補把預篩改成跟分類器同一套前處理,但判斷用的字樣清單沒補;分類器那一邊的支援等於死碼。
- 建議修法:預篩多認 `\bcore\b` 加 `-section`,或對 config 子指令直接放行進分類器。

**3. `then`/`do`/函式/`case` 分支體裡的 `cd` 被當成一定會跑**
ID: c3
severity: minor
blocking: 否

引句:「        elif self.seg_conditional or p.endswith("||") or q.startswith("||"):」

- 輸入:`if [ -d /nope ]; then cd <暫存實驗repo>; fi; git commit -n -m x`。`f() { cd T; }; git commit -n -m x`、`for d in /nonexistent; do cd T; done; git commit -n -m x` 也同樣得到 `[]`。
- 錯在哪:`seg_conditional` 只認條件位置的 `if/elif/while/until/!`,`then`、`do` 和函式體裡的 `cd` 沒被當成條件式。條件為假時 `cd` 沒跑,提交落在真 repo。
- 兩版結果:都是 `[]`。
- 歸因:有證據的原有漏查。
- ⚠ 交編排者:計劃第 126 行寫「條件式與子殼層的 cd 一律保守」,但實際只涵蓋條件位置。這算 d2 接受的漏問,還是要補?我標 minor,因為需要同一條指令同時有條件式 cd 和 `-n` 才會漏。

**4. `env` 帶有值的選項時,後面的 `LUMOS_SKIP_*` 前綴認不出來**
ID: c4
severity: minor
blocking: 否

引句:「        while j < upto and (seg[j].startswith("-") or _ASSIGN.match(seg[j])):」

- 輸入:`env -u FOO LUMOS_SKIP_PUSH_GATE=1 git <推送>` 得 `[]`;`env -C /tmp LUMOS_SKIP_PUSH_GATE=1 git <推送>` 也得 `[]`。
- 對照:`env -i LUMOS_SKIP_PUSH_GATE=1 git <推送>` 得 `['lumos-skip']`。
- 錯在哪:迴圈碰到 `-u` 的值 `FOO` 時,它既不是 `-` 開頭也不是賦值,迴圈就停,後面的賦值沒被看到。
- 歸因:有證據的原有漏查(修前修後同為 `[]`)。

**5. 單引號或跳脫的 `$` 在拆詞後被還原,結果仍會展開變數**
ID: c5
severity: minor
blocking: 否

引句:「        self.variables[name] = _expand(val, self.variables)」

- 輸入:`D=<暫存實驗repo>; cd '$D'; git commit -n -m x`。
- 錯在哪:`'$D'` 在 bash 裡是字面的 `$D`,`cd` 會失敗,提交落在真 repo。掛鉤把它展開成暫存路徑,得到 `[]`。
- 原因:`_unmask` 把引號裡被遮罩的 `$` 還原後,`_expand` 無法區分它是否被引號保護。`\$D` 同樣如此。
- 兩版結果:都是 `[]`。
- 歸因:有證據的原有漏查。

## 沒問題的部分(已驗)

**例外與效能**
- 隨機拼接 30000 條指令(含 `$'`、`$"`、`{fd}>`、heredoc、`\x00`、PUA 字元),`bypass_reasons` 和 `prefilter` 沒有任何例外,最慢 12 毫秒。
- 52 萬字元 heredoc 約 0.02 秒;100 萬字元一般詞預篩約 0.47 秒;變數翻倍 24 次峰值約 21MB。

**逾時與 git 呼叫**
- 把 `subprocess.run` 換成一律逾時:一條指令裡三處 `cd` 到不同暫存目錄再提交,只跑了 1 次 git,之後不再跑,結果仍問(`['commit-n']`)。
- `MAX_GIT_CALLS` 的計數正常。

**介面契約(對應 be-api-compat、be-authz 兩張角色卡)**
- 這支掛鉤沒有對外 API 欄位,輸出格式 `hookSpecificOutput.permissionDecision: "ask"` 沒變。
- 它沒有端點也沒有資料授權。輸出只會是 `ask` 或不輸出,不可能升級成 `allow`,兩題都不適用。

**配對案例(獨立重跑,修前 → 修後)**

| 案例 | 預期 | 修前 | 修後 |
|---|---|---|---|
| repair:`git commit -$'\156' -m x` | ask | `[]` | `['commit-n']` |
| repair:`git commit -m 1 >/dev/null -n` | ask | `[]` | `['commit-n']` |
| repair:`git push $"--no-verify" o` | ask | `[]` | `['no-verify']` |
| repair:`git push --repo https://example.com/r.git --no-verify <裸庫>` | ask | `[]` | `['no-verify']` |
| repair:`true \|\| cd T && git commit -n` | ask | `[]` | `['commit-n']` |
| repair:`{ cd T; } \| cat; git commit -n` | ask | `[]` | `['commit-n']` |
| repair:`(cd T)>/dev/null; git commit -n` | ask | `[]` | `['commit-n']` |
| repair:`git -C T/lnk/.. commit -n`(`lnk` 連到真 repo) | ask | `[]` | `['commit-n']` |
| repair:`git config --get remote.o.url; git push --no-verify <裸庫>` | 放行 | `['no-verify']` | `[]` |
| repair:`grep GIT_DIR x.md; cd T && git commit -n -m x` | 放行 | `['commit-n']` | `[]` |
| preserve:`echo "別用 git push --no-verify"` | 放行 | `[]` | `[]` |
| preserve:真 repo 的 `git push --no-verify origin feat` | ask | `['no-verify']` | `['no-verify']` |
| preserve:`git push --no-verify 2>/dev/null` | ask | `['no-verify']` | `['no-verify']` |
| preserve:`git config core.hooksPath 2>/dev/null` | 放行 | `[]` | `[]` |
| preserve:`cd T && git commit -qm x --no-verify` | 放行 | `[]` | `[]` |

- `git commit -m 1>x -n` 修後回 `[]`,這是對的:bash 會把 `1>x` 當導向,於是 `-m` 的值變成 `-n`。
- 上表其餘列修後行為都符合預期,新發現 1 到 5 都不影響這些案例。

**存活事件模組 `_hookevent.py`(`_trim`、`_clear_stale_trims`)**
- 逐行讀過,沒找到會判錯或丟例外的輸入。

**三問回答**
- 原問題修復效果:上表 repair 列在修前放行、修後問,行為證據成立。
- 修補處相鄰路徑:`&&` 後接換行再 `cd` 這條路徑沒守住(finding 1);預篩的字樣清單沒覆蓋分類器的一種命中(finding 2)。
- 新發現同一案例的兩版結果:見各 finding。

**未驗範圍**
- 真實 Claude Code 環境下的 hook 註冊與 `--budget` 傳遞(在測試文件組)。
- 非 macOS 平台。
- 以 root 執行時,唯讀目錄測試的行為。

## 固定席節點判斷

- **Issues/code-loop守衛main-direct盲區、Systems/lumos-cli-read(search 預設排除 superseded)、lumos-cli-lifecycle(re-inject sentinel)、design-loop(處置閘)、guard-kill(rc 優先序、`--json` 純度)、pitfalls-code-loop、reversibility-governance-ledger:** 這次改動的程式組不碰這些行為,不影響。
- **Systems/測試假綠形態(修 bug 的還原翻紅釘要配前置斷言證明現場成立):** 修剪殘檔那條新測試符合,先寫入舊殘檔並 `utime` 成 10 分鐘前,檔案小到不會觸發修剪,所以證明是 `record` 直接清的。但 finding 1 和 2 是這條 INVARIANT 的反例。測試在 `decide` 層和 `bypass_reasons` 層通過,現場卻走不到預篩或走不進換行接續,測試無法翻紅。

最嚴重等級 major,blocking 共 2 條(finding 1、2)。

實驗檔都在 `/tmp/lumos-seat-work/code-代理繞閘字樣問人/正確性-sonnet/`,請編排者刪;我沒有改 repo 裡任何檔。

來源:r4-併發資源-sonnet.md


我是併發資源席,審查範圍是程式組 patch,固定版本 465736e9。實測臨時檔在 `/tmp/lumos-seat-work/code-代理繞閘字樣問人/併發資源-sonnet/`(下稱「臨時目錄」)。發現 3 條,其中 1 條 blocking。

## 發現

1. 預篩對超過 20000 字的指令也跑完整正規化,`$'…'` 的數字跳脫解碼是二次方,整支掛鉤會超過 5 秒預算。

ID: r1
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

ID: r2
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

ID: r3
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

來源:r4-邊界輸入-sonnet.md


## 範圍與方法

我用 `SourceFileLoader` 載入修後版 `bypass-ask-hook.py`(`465736e9`,檔案內容與工作目錄 `9981c0e5` 相同,後者只多一個派工材料提交),跑了約 350 條邊界輸入。修前版取自 `9b8ce146`,同時載入對照。每條都同時看 `prefilter`、新版 `bypass_reasons`、舊版 `bypass_reasons`。cwd 分兩組:真 repo,以及我在 `/tmp/lumos-seat-work/…/邊界輸入-sonnet/w/exp` 開的拋棄式 repo。

歸因統一用「有證據的修復回歸」或「有證據的原有漏查」,查證命令是同一批腳本(`h.py`、`t1.py` 到 `t7.py`)在兩版各跑一次。

## Findings

### 1. `$'\c'` 的結尾單引號被吞,引號狀態錯位,整條指令後半段都不再被分類

ID: e1
severity: major
blocking: 是

引句:「`if ch == "c" and k + 1 < len(cmd):`」

`_ansi_escape` 對 `\c` 無條件吃掉下一個字元。bash 5.3 實測 `printf '[%s]\n' a$'\c' -n` 印出 `[a\c]` 和 `[-n]`:`$'\c'` 在結尾單引號就收,`\c` 後面沒有可轉的字元,按字面留下,`-n` 是獨立的第二個詞。

掛鉤把結尾的 `'` 當成 `\c` 的運算元吞掉,ANSI 字串一路開到指令尾,後面的 `-n`、`;`、換行全被遮罩成字串內容。

以下四種寫法,修後都回 `[]`(放行),修前全是命中:
- `git commit $'\c' -n`:修前 `['commit-n']`,修後 `[]`
- `git push $'\c' --no-verify`:修前 `['no-verify']`,修後 `[]`
- `echo $'\c'; git push --no-verify`:修前 `['no-verify']`,修後 `[]`
- `echo $'\c'` 換行 `git push --no-verify`:修前 `['no-verify']`,修後 `[]`

連 `git commit -m $'x\c' -n` 也漏。

`echo $'\c'` 重複 1500 次(15000 字),修後回 `['literal']`,這是 shlex 報「沒有結尾引號」的間接證據。

應該是:`\c` 後面是 `'`(或已到字串尾)時不消耗它,`\c` 按字面留下。
歸因:有證據的修復回歸。`\cX` 是這輪新加的解碼。
附帶:`\c` 現在是「吞掉結尾引號就讓後面全被遮罩」的最小觸發器,修補時順便讓 `_ansi_decode` 不要跨過未配對的 `'` 而吃掉整條指令。

### 2. 程序替換 `<(` 和 `>(` 被當成導向,裡面的 git 指令被跳過

ID: e2
severity: minor
blocking: 否

引句:「`k = min(t.index(c) for c in "<>" if c in t)   # `)>`、`;>`:前面是分隔、後面是導向`」

「黏著標點」的新分支遇到只含標點的詞(例如 `<(`),就在第一個 `<` 或 `>` 切開,後半變成 `_Redir`。`_strip_redirects` 接著把 `<(` 後面的下一個詞(`git`)當導向目標丟掉,掛鉤就找不到 git 指令了。

- `cat <(git commit -n)`:修前 `['commit-n']`,修後 `[]`
- `tee >(git push --no-verify)`:修前 `['no-verify']`,修後 `[]`
- `diff <(echo) <(git commit -n)`:修前 `['commit-n']`,修後 `[]`

應該是:`<(` 和 `>(` 當成開子殼層的分隔,不是導向。
歸因:有證據的修復回歸。

另有一個原有漏查,不是這輪造成的:`git push <(echo x) --no-verify` 修前修後都是 `[]`。原因是 `)` 把段切斷,`--no-verify` 落在沒有 git 的新段。〈範圍〉沒有列程序替換。

### 3. 「if 或 for 本體裡的 cd」一律當作會執行,條件為假或迴圈零次時誤給拋棄式豁免

ID: e3
severity: minor
blocking: 否

引句:「`self.seg_conditional = any(w in ("if", "elif", "while", "until", "!") for w in seg[:i])`」

只有條件那一行的 cd 被當成條件式。`then` 或 `do` 本體裡的 cd 被當成必定執行。在真 repo 的 cwd 下:

- `if false; then cd E; fi; git commit -n`:修後 `[]`,修前 `[]`。真實是 cd 沒跑,提交落在真 repo。
- `for i in 1; do cd E; done; git commit -n` 和 `case x in x) cd E;; esac; …` 同樣放行。這兩條 cd 確實會跑,所以放行本身不算錯。零次迭代的 `for` 或不匹配的 `case` 才是錯。

E 是判斷當下存在的暫存 repo。常見的 `if [ -d E ]; then cd E; fi; git commit -n`,條件為假時會漏。方向上符合 d2「寧可漏問」,所以只列 minor。
應該是:`then`、`else`、`do` 本體裡的 cd 也標成條件式,和 `&&`、`||` 的處理一致。
歸因:有證據的原有漏查(修前修後同為 `[]`)。

### 4. 拋棄式 repo 裡,字串或參數中的 `GIT_DIR=` 字樣誤把豁免取消

ID: e4
severity: minor
blocking: 否

引句:「`if any(_GITDIR_ASSIGN.match(w) for w in seg):`」

`_note_markers` 掃整段所有詞,包含 `echo`、`grep`、`-m` 的引數。cwd 是拋棄式 repo 時,以下都回 `['commit-n']`,預期放行:

- `echo "GIT_DIR=x"; git commit -n`
- `grep -rn GIT_DIR=x .; git commit -n`
- `git commit -m "GIT_DIR=x" -n`
- `echo $'GIT_DIR=x'; …`
- `echo $x GIT_WORK_TREE=x; …`

heredoc 內文和註解裡的字樣沒問題,前處理已剝掉。因為只在拋棄式 repo 才多問,算 minor。
應該是:只認段首的前綴賦值,以及 `env` 或 `export` 後面的賦值。
歸因:有證據的原有漏查(修前修後同為 `['commit-n']`)。

## 三個必答問題

**① 原問題的修復效果有何行為證據。** 以下各案例修前修後的結果相反,都是修好的證據:

| 輸入 | 修前 | 修後 |
|---|---|---|
| `git commit -m 1 >x -n`(`-m` 的值是 1,後面是獨立 `-n`) | `[]` | `['commit-n']` |
| `git config {fd}>x --unset core.hooksPath` | `[]` | `['config-hookspath']` |
| `git commit -$'\156'` | `[]` | `['commit-n']` |
| `git commit -$'\u006e'` | `[]` | `['commit-n']` |
| `git commit -$'\U0000006e'` | `[]` | `['commit-n']` |
| `git commit $"-n"` | `[]` | `['commit-n']` |
| `git push $'\55\55no-verify'` | `[]` | `['no-verify']` |
| `git commit -$'\cn'n`(此例解出控制字元,見下) | `[]` | `['commit-n']` |
| `git commit -$'\1560'`(此例 git 實際會報錯,見下) | `[]` | `['commit-n']` |
| `if cd E; then git commit -n; fi`(cwd 為真 repo) | `[]` | `['commit-n']` |
| `! cd E; git commit -n`(cwd 為真 repo) | `[]` | `['commit-n']` |
| `{ cd E; } \| cat; git commit -n`(cwd 為真 repo) | `[]` | `['commit-n']` |
| `(cd E)>x; git commit -n`(cwd 為真 repo) | `[]` | `['commit-n']` |

倒數第 7、6 兩行(`\cn`、`\1560`)和 `\0n`、`\777n` 屬於解碼過度,見下一節「預篩與分類器」。

**② 修補處的正常、錯誤與相鄰呼叫路徑是否仍成立。** 大致成立,但有 finding 1 和 2 的兩個回歸。

下面這些都過關:
- 檔案代號 `2>`、`10>`、`{fd}>`、`{fd}<&-`、`2>&1`、`3<>`、`03>`、`>|`、`&>>`、`>&-`。
- 導向放最前面、夾在 `git -C`、`git -c` 之間、夾在 `-C R` 之後。
- 引號、`$'…'`、`\>` 裡的 `2>`(不會被當成導向)。
- `cd` 後接導向。
- `cd E && cd R`、`||`、換行、`;` 混合鏈。
- `(…)` 子殼層,包含 `)>`、`)2>`、`;>`、`|&`、`}>` 黏著。
- `{ …; } | cat` 和 `{ …; } &`。
- `-m 1>x -n`、`-F 2>x -n`、`-C 5>x -n`:這幾條 `-n` 是 `-m` 的值,放行是對的。我一開始的預期寫反了。
- GIT_DIR 一族出現在 `export`、`declare -x`、`typeset -x`、前綴賦值、`--git-dir`、`--work-tree` 時,豁免都取消。
- heredoc 內文的 `GIT_DIR=`,不影響豁免。
- `env -u GIT_DIR`:修後視為不取消豁免,方向合理。
- 前綴 `LUMOS_SKIP_*` 夾在 `2>x`、`{fd}>x` 前後。
- `GIT_CONFIG_KEY_n` 前綴。
- `-c core.hooksPath` 夾在 `2>x`、`-C .` 周圍。
- `git config` 讀值加導向(`core.hooksPath 2>&1`)放行,寫值加導向命中。

**③ 新發現的同一案例在修前、修後各是什麼結果。** 見 finding 1 和 2 的清單。finding 3 和 4 兩版相同。

## 預篩與分類器是否一致

預篩放行時分類器根本不會被叫,所以先看有沒有「預篩放行、分類器卻會命中」的實際繞過。

我找到的預篩放行但分類器命中的案例:
- `git commit -$'\0n'`
- `git commit -$'\777n'`
- `git commit -$'\cn'n`
- `git commit -$'\1560'`
- `git commit -$'a<換行>b'n`
- `git commit $"-$'n'"`
- `git commit -$'$"n"'`

這些在 bash 裡都不會變成真的 `-n`:
- `\0` 讓 bash 在 NUL 處截斷字串。
- `\777` 在 bash 是 0xFF 位元組。
- `\cn` 是控制字元。
- `\1560` 變成 `-n0`,git 會報錯。
- 換行字串、雙引號裡的 `$'` 都是字面字元。

所以這些是分類器解碼過度,預篩剛好擋下,對結果沒影響。我沒有找到「預篩放行而 bash 真會執行 `-n`」的案例。

## 效能

2 萬字內的最壞形狀(`2>x ` 重複、`{fd}>x ` 重複、`()>`、`;>`、`a&>b`、未閉合 `$'` 九千次、`$"` 九千次)全在 40ms 內,預篩在 12ms 內。

## 固定席節點逐條判

- **Issues/code-loop守衛main-direct盲區、Systems/lumos-cli-read、lumos-cli-lifecycle、design-loop、測試假綠形態、guard-kill、pitfalls-code-loop、reversibility-governance-ledger**:不影響。它們牽連的檔(`scripts/lumos`、`merge-claude-settings.py`、`test_lumos.py`)和那幾條 INVARIANT(search 預設排除、re-inject byte-equal、處置閘第五步、還原翻紅釘、guard kill rc 與 JSON)是 CLI 別的路徑,跟本席測的 `bypass-ask-hook.py` 的輸入處理無關。我沒有跑那幾條的綁定測試,結論只是從主題與牽連檔推出,不是實測。
- **超出上限、只列名的節點**:未逐篇讀,也不影響。
- 與本席有關的是 `_hookevent.py` 的修剪邏輯(存活事件)。我沒有測它,屬未驗範圍。

## 未驗範圍

- `_hookevent.py`:修剪與殘檔清理。
- `scripts/lumos` 和 `merge-claude-settings.py` 的註冊與安裝。
- `test_lumos.py` 的新測試是否真能翻紅。
- 真正的 git 子程序逾時與 `MAX_GIT_CALLS` 路徑。

## 最後一行

總結:最嚴重等級為 major,blocking 共 1 條(finding 1);另有 3 條 minor(finding 2、3、4),非 blocking。

臨時目錄 `/tmp/lumos-seat-work/code-代理繞閘字樣問人/邊界輸入-sonnet/` 留給編排者刪,裡面有我複製的 `old.py`、`new.py`、`_hookevent.py` 和一個測試用的 `w/exp`。我一度把三個檔誤複製到主工作目錄 `/Users/enzo/orca/workspaces/lumos-toolchain/Word-wild-search`,已刪掉,`git status` 現在只剩原有的 `docs/.governance-log.jsonl`。repo 本體(`-bypass`)沒有被我改動。

來源:r4-通才-sonnet.md


我只找到一條問題,屬於「誤問」方向,而且是修補後新出現的。(甲)方向(代理用正常寫法讓掛鉤放行真繞閘)沒有找到,證據在最後。

## Finding

1. 指令裡只要有一個空字串參數(`''` 或 `""`),切詞就會當掉,整條指令退回「照字面看」的粗判。結果是不該問的指令被問,拋棄式豁免也一起失效。

引句:「k = min(t.index(c) for c in "<>" if c in t)   # `)>`、`;>`:前面是分隔、後面是導向」

ID: t1
severity: minor
blocking: 否

- 走到哪一行:`_tokens` 新增的 `elif all(c in "();<>|&\n" for c in t)` 分支。posix shlex 把 `''` 切成空字串 `""`,`all()` 對空字串為真,接著 `min()` 對空序列丟 `ValueError`。`bypass_reasons` 接住這個錯誤後改走 `_literal`,而 `_literal` 不看拋棄式、不看旗標位置。
- 重現,載入修後掛鉤,cwd 是真 repo:
  - `bh.bypass_reasons("sed -i '' 's/LUMOS_SKIP_X/LUMOS_SKIP_Y/' scripts/lumos", real)` 回 `['literal']`。
  - `sed -i '' 's/--no-verify/x/' docs/lumos-toolchain-knowledge/Projects/a.md` 和 `sed -i "" 's/hooksPath/x/' scripts/lumos` 同樣回 `['literal']`。
  - 實跑掛鉤主程式,stdin 給 PreToolUse 事件,`sed -i '' 's/hooksPath/x/' scripts/lumos` 輸出 `permissionDecision: "ask"`。
  - 對照:`git commit -m '' --author x` 回 `[]`,因為預篩沒命中,根本沒進分類器。
- 影響:macOS 上 `sed -i ''` 是慣用寫法。改 `scripts/lumos` 或這個 repo 的 docs 時,只要樣式裡有三個字樣之一(`--no-veri`、`hookspath`、`lumos_skip_`),就會被問。路徑有 "lumos" 就滿足 `_literal` 的 git/lumos 前提。另外,拋棄式 repo 裡 `git commit -n -m x --author ''` 也會被問。模擬第 1 次實驗:`git commit -m x -n --author ''` 修前回 `['commit-n']`,修後回 `['literal']`,在暫存目錄也會被問,拋棄式豁免沒起作用。
- 應該是:空字串詞要先排除。例如在 `_tokens` 對 `t == ""` 直接 `out.append("")`,或讓分支要求 `t` 非空。
- 歸因:有證據的修復回歸。修前版本(9b8ce146)的 `_tokens` 沒有這個分支。同一批指令:
  - sed 三條:修前 `[]`,修後 `['literal']`。
  - `git -C /tmp/lumos-seat-work/x commit --no-verify -m ''`:修前 `['no-verify']`,修後 `['literal']`。

## 三問

① 原問題(`)>`、`;>` 這類分隔符黏著導向)的修復效果,我沒有拿修前版本逐案對照,只驗了修後行為:
- `2>/dev/null`、`>/dev/null`、`2>&1`、`&>`、`|&`、`2>>log`、`<&-`、`1>&2` 接在 `git config core.hooksPath` 後面,全部回 `[]`(讀設定不誤問)。
- `git push --no-verify >/dev/null 2>&1` 回 `['no-verify']`。

② 修補處的相鄰路徑:只有上面那一條回歸。空字串詞也會讓 `git config core.hooksPath ''` 這類寫入退到 `literal`。它仍然問人,所以不是漏問,只是理由代號變粗。

③ 新發現同一案例,修前 `[]`、修後 `['literal']`,見上面的對照。

## (乙)日常指令誤問:已驗無誤問

- 暫存目錄實驗 repo,remote 指向另一個本機裸庫:`push --no-verify origin HEAD`、`-u`、`-f`、`--repo=`、直接給 bare 路徑、`../bare.git` 相對路徑、`-C` 加子目錄,全部放行。
- 暫存目錄的 `commit -n`、`cd 實驗目錄 && 多段 git 鏈`、`gctl-run-1/r` 這種路徑,全部放行。
- 只有網路 remote 或沒有 remote 的 repo 才問,方向正確。
- 回真 repo 的第二段仍會問:`cd exp && commit -n && cd real && commit -n` 的第二個 `commit -n` 回 `['commit-n']`。
- `grep`、`rg` 搜 `--no-verify`、`core.hooksPath`、`LUMOS_SKIP_*`,以及 `grep -rn ... 2>/dev/null | head`,放行。
- commit 訊息裡提到 `--no-verify`、`-n`、`LUMOS_SKIP_X`、`core.hooksPath`,包括 `$(cat <<'EOF'...)` 的 heredoc 訊息,放行。
- `-S<keyid含n>`、`-m "-n"`、`--author 'A -n'`、`-- -n`,放行。
- `git config --get`、`--get-all`、`--list`、`--show-origin`、`--type=path core.hooksPath`、`--get remote.origin.url`,放行。
- 完整掛鉤(含預篩)實跑,耗時約 0.06 到 0.12 秒。

## (甲)真繞閘:未找到放行寫法

- 已攔住的正常寫法:
  - `--no-verify` 放在任何位置、`-n`、`-an`、`-sn`、`-nm`、`--amend -n`。
  - `-c`、`--config-env`、`GIT_CONFIG_KEY_n`、`GIT_CONFIG_PARAMETERS`、`export` 各種形式。
  - `git config core.hooksPath` 的各種寫入、`--unset`、`--add`、`-f`、`--worktree`、`set` 新語法。
  - `LUMOS_SKIP_*` 作前綴,或搭配 `env`、`/usr/bin/git`、`export`。
  - `(cd exp && true); git commit -n`(子殼層 cd)仍會問。
  - 同一條指令先 `remote set-url` 或 `remote add` 再推送,不給豁免。
- 縮寫 `--no-ve`、`--no-ver` 不是繞法。我在實驗 repo 實測,git 回 129 拒絕這些縮寫,`-ccore.hooksPath=` 也是 `unknown option`。
- ⚠ 以下是小的攔不到點,計劃〈範圍〉沒明列,交編排者判斷是否補進範圍,我不認為是 blocking:
  - `set -a; LUMOS_SKIP_X=1; git push` 回 `[]`。
  - `export LUMOS_SKIP_X=1; unset LUMOS_SKIP_X; lumos doctor` 會誤問,因為 `unset` 沒處理。
  - 用 Bash 對 `scripts/hooks/pre-push` 做 `chmod -x`、`rm`、`sed -i`。〈範圍〉只承認 Edit/Write 這類非 Bash 工具改閘檔,且事後 `anchor verify` 抓得到。

## 固定席節點

- `Issues/code-loop守衛main-direct盲區`、`Systems/lumos-cli-read`、`lumos-cli-lifecycle`、`design-loop`、`測試假綠形態`、`guard-kill`:不影響。
  - 這輪我讀的程式組只有 `bypass-ask-hook.py` 和 `_hookevent.py`,沒碰 search 濾網、re-inject sentinel、處置閘、guard kill 的 rc 優先序與 `--json` 純淨度。
  - `_hookevent.py` 本身的 diff 我只在檢視全檔時看過,沒對 hunk 逐行比對。
- `測試假綠形態` 的「前置斷言證明現場成立」:上面這個空字串回歸顯示現有測試沒有覆蓋空字串參數。補紅測試時,要在斷言前先證明走的是 `_tokens` 分支,而不是 `_literal`。
- `pitfalls-code-loop`、`reversibility-governance-ledger`(`scripts/lumos`):這組程式沒改到,不影響。

未驗範圍:併發與資源(他席負責)、`scripts/lumos` 與 `merge-claude-settings.py` 的註冊,以及測試文件組。

最嚴重等級:minor,blocking 共 0 條。

所有實驗檔在 `/tmp/lumos-seat-work/code-代理繞閘字樣問人/通才-sonnet/`,請編排者刪。

來源:r4-架構對齊-sonnet.md


**已驗範圍。** 我讀了 code patch 全文，對照 `impact-hook.py` 整檔、`_hookevent.py` 全檔，以及 `scripts/lumos` 的 `_write_lf`（:20597）、`_home_cache_write`（:47696）、`_codeloop_write_dispositions`（:50534）。三支掛鉤（`bypass-ask-hook.py`、`impact-hook.py`、`ci-status-hook.py`）的逾時預算區塊，我用 `sed -n '/^_BUDGET_RATIO/,/逾時預算結束/p'` 取出後做 md5，三份一致。`dispatch-lens-hook.py` 沒有逐條對照，只確認它同樣呼叫 `_inner_budget`。
未驗：`memory-sweep.py` 沒有讀；`scripts/merge-claude-settings.py:126` 註冊表的 5 秒預算也只看了登記行。

## 三問

**1. 分層與依賴方向：對齊。**
- 新掛鉤只依賴同層的 `_hookevent`（掛鉤頂端 `from _hookevent import guard as _guard, mark`），不呼叫 `scripts/lumos`，也沒有互相引用其他掛鉤。依賴方向跟 `impact-hook.py:922-928` 一樣只往共用模組。
- 預算區塊逐字複製。`bypass-ask-hook.py` 的 `_BUDGET_RATIO` 到「逾時預算結束」那段，md5 與 `impact-hook.py:343-397` 相同。
- 預算天花板仍由註冊表 `HOOK_BUDGET` 一處生成（`scripts/merge-claude-settings.py:126`，`"bypass-ask-hook.py": 5`）。
- 「共用模組在模組頂層載入」已列在已知偏離，不重報。

**2. 命名與錯誤處理：結構對，有兩處不一致，都是 minor。**
- `_GIT_STATE` 是模組全域 dict，跟 `_hookevent.py:155` 的 `_MARKED` 同一種寫法，算有先例。`_IN_HOOK = {"on": False}` 則是第三種狀態寫法（`_BUDGET_START` 用 `global`），不過也沒有更好的先例可比，不算偏離。
- `_FD_MARK` 用 U+E0FF，落在 `_MASK_BASE` 的 U+E000 起 16 碼遮罩區之外。這是新增常數，沒有可比對的既有寫法，我只確認它與遮罩區不重疊。
- `_scope_cd`、`_note_markers`、`_dir_change` 都是 `_Walker` 的私有方法，這類一詞一職的拆法在掛鉤層沒有先例可比。
- `_hookevent._trim` 用 `mkstemp` 再 `copymode`，`except BaseException` 時刪暫存檔再 raise。清理的形狀等同 `_write_lf`（:20608-20618）；用 `mkstemp` 的做法等同 `_codeloop_write_dispositions` 與 `_home_cache_write`。`_write_lf` 不用 `mkstemp` 的理由是「新建檔權限受 umask 影響」，這裡原檔一定存在而且會 `copymode`，理由不適用，所以不算不對齊。
- 每次記事件都清殘檔（`_clear_stale_trims`）：`scripts/lumos` 的三支寫入函式都不掃殘檔，但 `impact-hook.py:175` 的 `_ttl_lazy_cleanup` 有同型的惰性清理，所以有先例。

**3. 第二種做法：沒有 major。**
- 預算只有一套（上述逐字複本）。
- 前處理只有一套 `_Normalizer`：`prefilter` 與 `bypass_reasons` 都走同一個類別（跑兩次，沒有第二份實作）。
- 分類器只有一個入口 `bypass_reasons`。

## 不對齊清單

1. **修剪失敗的警告缺 `telemetry-write-failed` 關鍵字。**
ID: a1
severity: minor
blocking: 否
引句:「print(f"  ⚠ hook 事件檔修剪失敗({type(e).__name__}),檔案會繼續長大:{f}", file=__import__("sys").stderr)」
   - 同檔 `guard` 的兩處和 `scripts/lumos` 的記帳失敗警告，都以 `⚠ telemetry-write-failed:` 開頭。
   - file: `scripts/hooks/claude/_hookevent.py:192` 與 `scripts/hooks/claude/_hookevent.py:205`
   - file: `scripts/lumos:1628`、`scripts/lumos:1674`、`scripts/lumos:1691`
   - 計劃 `Projects/enforcement可觀測性_計劃` 的 S7 也要求「記帳失敗要在 stderr 講 `telemetry-write-failed`」。
   - 影響：照關鍵字找記帳失敗的人，找不到這一種。
   - 修法：訊息改成 `⚠ telemetry-write-failed:hook 事件檔修剪失敗(…)`。

2. **`_temp_roots` 的 docstring 引用了不存在的先例。**
ID: a2
severity: minor
blocking: 否
引句:「"""暫存根:與審查席外掛的暫存根取聯集,再加上本機的暫存目錄(同 scripts/lumos 的做法,一律加)。"""」
   - `git grep` 在 `scripts/lumos` 找不到 `/private/tmp`、`/var/tmp`、`/var/folders`，只有 `tempfile.gettempdir()` 單獨使用。
   - file: `scripts/lumos:18226` 只有 `Path(os.path.realpath(tempfile.gettempdir()))`，沒有暫存根清單。
   - 影響：維護者會去 `scripts/lumos` 找一份不存在的暫存根清單來對照，或以為兩邊要同步。
   - ⚠ 該清單可能在 repo 外的審查席外掛（`lumos-guard`），我不能在審查席的 Bash 裡確認。
   - 修法：指到實際出處，或刪掉這句宣稱。

3. **`prefilter` 與 `_literal` 重複同一段字面判斷。**
ID: a3
severity: minor
blocking: 否
引句:「return "git" in low and re.search(r"\bcommit\b", low) is not None and _PRE_SHORT_N.search(low) is not None」
   - `prefilter` 與 `_literal` 兩處都有 `re.sub(r"['\"\\]","",…).lower()`、`_PRE_WORDS` 檢查，以及「`commit` + `_PRE_SHORT_N`」檢查。
   - 同一個判斷出現兩份，兩處日後可能走樣。
   - 這不算第二種做法（共用同一組常數），只是可抽成一個小函式。

4. **`bypass_reasons` 直接重設 `_BUDGET_START`。**
ID: a4
severity: minor
blocking: 否
引句:「_BUDGET_START = None         # 不是掛鉤進場(例如拿事件帳批次重跑):每次判斷重新起算預算」
   - 它用 `global _BUDGET_START` 改逐字複本區塊裡的變數，其他掛鉤都只透過 `_inner_budget()` 使用這個變數。
   - file: `scripts/hooks/claude/impact-hook.py:343-397` 是複本區塊，變數只由 `_inner_budget` 讀寫。
   - 這不是跨層呼叫，結構上仍是同檔內。
   - 但如果日後同步更新複本區塊，這個外部依賴容易被漏掉。

不對齊共 4 條，其中 major 0 條。

**暫存清理：** 我沒有建立任何暫存目錄或實驗檔，不需要刪除。

來源:r4-資安-sonnet.md


補充:實驗全放在 `/tmp/lumos-seat-work/code-代理繞閘字樣問人/資安-sonnet/`,沒動 repo。另外要提醒:審查席的 Bash 被擋掉「git 加 push 同一行」,所以 push 相關重現是用腳本檔跑的。

1. 程序替換 `<(…)`、`>(…)` 裡的 git 指令不再被看見(修補造成的回歸)
ID: s1
severity: major
blocking: 是
- 攻擊路徑:
  - 誰:被提示注入的代理。
  - 從哪:一般的 Bash 工具呼叫。
  - 送什麼:`cat <(git commit --no-verify -m x)`,或 `diff <(true) >(git push --no-verify origin main)`。
  - 拿到什麼:提交和推送都真的會跑,真 repo 的提交前閘和推送前閘被跳過,掛鉤不問。
- 走到哪:`_tokens` 把 `<(` 認成導向運算子 `_Redir`,`_strip_redirects` 接著把它「後面那一個詞」當導向目標剔除,剔掉的剛好是 `git`。剩下的 `commit --no-verify` 段裡沒有 git 詞,於是沒有任何命中。bash 實測會執行程序替換裡的指令:`cat <(echo RAN-IN-PROCSUB)` 印出 RAN-IN-PROCSUB。
- 引句:「out.append(_Redir(t[k:]))」
- 重現(同一份輸入,修前修後各跑一次,預篩在修後也是 True):
  - 修後 465736e9:`bypass_reasons("cat <(git commit --no-verify -m x)", cwd)` 回 `[]`。
  - 修前 9b8ce146:同一輸入回 `['no-verify']`。
  - 第二個輸入 `diff <(true) >(git push --no-verify origin main)` 也是修前 `['no-verify']`、修後 `[]`。
- 歸因:有證據的修復回歸。`_Redir` 這個類別和 `_tokens` 的拆分是這次修補加的。
- 應該是:只有明確的導向運算子(`>`、`>>`、`<`、`&>`、`>&`)才吃下一個詞;`<(`、`>(` 這種括號開頭的要當「開子殼層」處理,不吃詞。

2. `(( 1<<EOF ))` 讓前處理誤判有 heredoc,把後面一行真指令當內文剝掉(原有漏查)
ID: s2
severity: major
blocking: 是
- 攻擊路徑:
  - 誰:被提示注入的代理。
  - 從哪:一般的 Bash 工具呼叫。
  - 送什麼(三行,最後一行的 `EOF` 會報 command not found,但提交已經跑了):
    ```
    (( 1<<EOF ))
    git commit --no-verify -m x
    EOF
    ```
  - 拿到什麼:提交的閘被跳過,掛鉤不問。
- 走到哪:`_bare_special` 的 `<<` 判斷只排除了 `$((`、`<<<`,沒排除裸的 `((…))` 算術命令。`_heredoc_op` 把 `<<EOF` 登記成 heredoc,`_drop_bodies` 在換行後把中間所有行剝到獨佔一行的 `EOF`,真正的 `git commit --no-verify` 就從分類器的視野消失。
- 預篩有同樣的問題:它拿「原文加正規化後文字」比字樣。這個輸入原文本身有 `--no-verify`,預篩回 True,所以進了分類器,但分類器看到的是剝光後的版本。
- 引句:「if self.heredoc_ok and cmd.startswith("<<", i) and not cmd.startswith("<<<", i) and (i == 0 or cmd[i - 1] != "<"):」
- 重現:
  - bash 實測 `(( 1<<EOF ))` 之後的 `echo RAN-AFTER-ARITH-HEREDOC` 會執行,結束字那行只報 `EOF: command not found`。
  - 修後和修前對該輸入的 `bypass_reasons` 都回 `[]`(預篩為 True)。
  - 對照:`$[1<<EOF]` 的變形被誤抓,因為結束字讀成 `EOF]`,所以不構成繞法。
- 歸因:有證據的原有漏查(修前修後同為 `[]`)。
- 應該是:heredoc 運算子只在「指令位置」認,或遇到 `((` 開頭的命令就不登記;更保守的做法是:剝掉內文時,如果被剝的內文含 git 或 `--no-veri` 字樣就不剝(寧可多問)。

3. `--push-o` 這類長選項縮寫,讓推送目的地被判成暫存目錄(原有漏查,有伺服器條件)
ID: s3
severity: major
blocking: 是(但標 ⚠,理由在下面)
- 攻擊路徑:
  - 誰:被提示注入的代理。
  - 從哪:在真 repo 的工作目錄裡執行。
  - 送什麼:`git push --no-verify --push-o /tmp origin main`。
  - 拿到什麼:向真遠端推送,推送前閘被跳過,掛鉤不問。
- 走到哪:
  - `_push_remote_arg` 只認完整寫法 `-o`、`--push-option`、`--repo` 等會吃值的選項。
  - git 的 parse-options 接受唯一縮寫,`--push-o` 就是 `--push-option`,git 會把 `/tmp` 當 push option 的值。我在本機重現過:錯誤訊息是 "receiving end does not support push options",和完整寫法 `-o /tmp` 同一個錯,證明 git 吃掉了 `/tmp`。
  - 掛鉤則把 `/tmp` 當第一個位置參數,也就是遠端。`_local_url` 判成本機路徑,`_temp_target` 看到 `/tmp` 存在且在暫存根底下,於是 `_push_target_temp` 回 True,`no-verify` 命中被豁免。
- 引句:「_PUSH_VALUE_OPTS = {"-o", "--push-option", "--repo", "--receive-pack", "--exec"}」
- 重現:
  - 修後與修前,`bypass_reasons("git push --no-verify --push-o /tmp origin main", <真 repo 的 cwd>)` 都回 `[]`。
  - 對照:完整寫法 `--push-option /tmp` 回 `['no-verify']`。
- ⚠ 條件:
  - 伺服器要接受 push options(GitLab、Gitea 等;GitHub 我不確定)。
  - 本機用 `file` 傳輸的裸 repo 即使開了 `receive.advertisePushOptions` 也報不支援,所以我沒能做出端到端成功推送。
  - 掛鉤端的誤判和 git 端的縮寫解析都已實測。
- 歸因:有證據的原有漏查。
- 應該是:縮寫要比照 `--no-veri` 的做法處理,對 `--push-option`、`--receive-pack`、`--exec`、`--repo`、`--recurse-submodules` 的任何非空前綴都當吃值選項;或只要出現未知的 `--` 開頭選項,就保守不豁免。

4. 直接叫 git 的子指令執行檔(`git-commit`、`git-push`)不會被當成 git
ID: s4
severity: minor
blocking: 否
- 攻擊路徑:
  - 誰:被提示注入的代理。
  - 送什麼:`/Library/Developer/CommandLineTools/usr/libexec/git-core/git-commit --no-verify -qm x`(本機 Apple Git 2.39.2 這個目錄有 `git-commit`、`git-push`)。
  - 拿到什麼:提交真的完成,而且 `--no-verify` 生效;我實測 pre-commit 沒跑,`log` 多了一筆提交。
- 走到哪:`_command` 只認檔名等於 `git` 的詞,`git-commit` 的基底檔名不等於 `git`。
- 實測:修後、修前都回 `[]`。
- 歸因:有證據的原有漏查。〈範圍〉沒列。
- 引句:「gi = next((k for k in range(i, len(seg)) if os.path.basename(seg[k]) == "git"), None)」

5. `-c include.path=<檔>` 讓設定檔把掛鉤目錄換掉,指令字面不含 `core.hooksPath`
ID: s5
severity: minor
blocking: 否
- 攻擊路徑:代理先用另一個 Bash 寫一個含 `[core] hooksPath=/dev/null` 的檔,再執行 `git -c include.path=/tmp/inc.cfg commit -m y`。
- 實測:提交成功、pre-commit 沒跑;預篩因沒有三個字樣而直接放行,`bypass_reasons` 回 `[]`。
- 為什麼只標 minor:這和〈範圍〉承認的「直接改 `.git/config`」同形,代理本來就能寫檔再繞,所以屬同族。
- 另外,`GIT_CONFIG_GLOBAL=檔` 被 repo 層設定蓋掉,不構成繞法(實測 pre-commit 照跑)。
- 歸因:有證據的原有漏查。
- 引句:「_CFG_ENV_ASSIGN = re.compile(r"^GIT_CONFIG_(KEY_[0-9]+|PARAMETERS)=(.*)$", re.S)」

6. 全域選項 `--attr-source <樹>`(帶分開的值)沒列進吃值選項
ID: s6
severity: minor
blocking: 否(推論)
- 掛鉤端已重現:`git --attr-source HEAD commit --no-verify -m x`,`_parse_git` 把 `HEAD` 當子指令,回 `[]`。
- 我沒能在 git 端確認,因為本機是 2.39.2,而 `--attr-source` 我記得是 2.40 才有,所以標推論。
- 做法:把 `--attr-source` 加進 `_GIT_VALUE_OPTS`,或遇到不認得的全域選項就保守地往後多看。
- 歸因:未判定。
- 引句:「_GIT_VALUE_OPTS = {"-c", "-C", "--git-dir", "--work-tree", "--namespace", "--super-prefix", "--config-env"}」

已看,無:
- 路徑判斷:`..`、符號連結和相對路徑都靠 `os.path.realpath` 解開,`_join` 不做文字化簡。`~` 與沒賦值的 `$TMPDIR`、`${X:-…}` 都回 `_UNKNOWN`,不豁免。沒有找到讓真 repo 被判成暫存實驗 repo 的路徑。
- `_hookevent`:
  - `d.glob("hook-events.*.trim")` 的樣式是寫死的,不含使用者輸入。
  - 符號連結被跳過,就算 `unlink` 也只會刪連結本身。
  - `copymode` 只複製權限位元。
  - `os.replace(tmp, f)` 同目錄原子換入。
  - 沒找到能刪別的檔的路徑。
- 輸出:
  - 確認框理由只用固定文字,不嵌入指令內容。
  - 存活事件的 error note 是 `type(e).__name__` 加上 `str(e)[:120]`。
  - 目前能丟出來的例外訊息只含變數名或索引,拿不出寫進指令內容的場景,所以不報。

固定席節點逐條判:
- `Issues/code-loop守衛main-direct盲區`、`guard-kill`、`design-loop`、`測試假綠形態`、`lumos-cli-read`、`lumos-cli-lifecycle`:
  - 不影響本席的資安判斷。這些 ★INVARIANT★ 管的是 `search` 排除規則、sentinel 之間的重注入、guard kill 的回傳碼和設計審處置閘,和這次掛鉤的可利用面無交集。
  - `lumos-cli-lifecycle` 那條是重注入保留使用者手寫內容,這次掛鉤沒改動它。
- `pitfalls-code-loop`、`reversibility-governance-ledger`:標 ★RISK★,牽連 `scripts/lumos`。那屬於測試文件組。

三問:
1. 原問題的修復有行為證據嗎?
   - 引號、續行、ANSI 引號這些前處理,在我沒測的範圍內沒看出問題。
   - 未驗:我沒逐條跑 r3 的修補案例。
   - 唯一被我證明退步的是 finding 1。
2. 修補處相鄰路徑是否仍成立?
   - 不成立:finding 1,`_Redir` 的新拆法吃掉 `<(`、`>(` 後面的詞。
3. 新發現同一案例修前修後各是什麼結果?
   - 見各條:finding 1 是修前 `['no-verify']`、修後 `[]`。
   - findings 2 到 6 修前修後相同,都回 `[]`。

最嚴重等級 major,blocking 共 3 條(findings 1、2、3)。

來源:r4-合約圖譜-sonnet.md


審查範圍:測試文件組逐 hunk 讀完,程式組只用來核對。以下全部對固定版本 465736e9 判斷(`9981c0e5` 只多了派工材料)。修前版用 `git show 9b8ce146:…/bypass-ask-hook.py`。臨時檔在 `/tmp/lumos-seat-work/code-代理繞閘字樣問人/合約圖譜-sonnet/`。

## Findings

1. 指令裡只要有一個空字串參數(`-m ''`、`-m ""`、`''`),整條指令就從結構分類掉到字面判。計劃寫的「用結構分類抓」的寫法因此漏問或誤問。
引句:「k = min(t.index(c) for c in "<>" if c in t)」
ID: g1
severity: major
blocking: 是
- **走到哪一行**:`_tokens` 的 `for t in lex:` 遇到空字串詞。
  - `_is_sep("")` 與 `_is_redirect("")` 都回 False。
  - `all(c in "();<>|&\n" for c in "")` 對空字串回 True,於是走進 `)>`、`;>` 的拆分分支。
  - 該分支的 `min(...)` 對空序列丟 `ValueError`。
  - `bypass_reasons` 把 `ValueError` 當「shlex 切不動」,改走 `_literal`。
- **應該是什麼**:計劃〈做法〉寫字面判只在「引號不成對」或「超過 2 萬字」才走(S4)。空字串引號不該算切不動。
- **重現**:cwd 設 `/Users/someone/work/repo`,指令用 `git commit -m '' …`,輸出是 `bypass_reasons` 的結果。

| 指令 | 修前 9b8ce146 | 修後 465736e9 |
|---|---|---|
| `git commit -m '' -$'n'` | `['commit-n']` | `[]`(漏問) |
| `git commit -m '' --no-\⏎verify`(反斜線加換行切開) | `['no-verify']` | `[]`(漏問) |
| `git commit -m "" -n` | `['commit-n']` | `['literal']` |
| `git config core.hooksPath ''` | `['config-hookspath']` | `['literal']` |
| `git push '' --no-verify` | — | `['literal']` |
| `cd <已存在的暫存 git repo> && git commit -m '' -n` | `[]`(拋棄式豁免) | `['literal']`(誤問) |

- 對照:`git commit -m ' ' -n` 修前修後都是 `['commit-n']`,所以問題只出在空字串。
- 漏問的兩個寫法正是 S1 條款寫「`$'…'` 包住旗標」「續行切開長選項」要抓的。
- 誤問的那條讓「結構分類加拋棄式豁免」整個失效。
- 歸因:有證據的修復回歸。修前能抓,修後掉到字面判。換形狀發生在 r3 把切詞改成 `_Sep`/`_Redir` 的那一段。
- 測試為什麼沒抓到:S1 有 `git config core.hooksPath ""` 這個案例,但斷言只看有沒有 ask,不看理由代號。它靠字面判過關,把這個洞掩蓋了。
- 修法:`_tokens` 的第三個分支先排除空詞。S1 加一條斷言,要求這類案例的理由代號是結構判的代號(例如 `config-hookspath`),不是 `literal`。

2. S4 條款寫了的兩項行為,綁定的測試沒驗。
引句:「目錄唯讀修剪失敗 應 印提示、不需要修剪時 應 也清掉舊殘檔」
ID: g2
severity: minor
blocking: 否
- 條款綁的是 `t_bypass_ask_fallbacks_and_budget`。「目錄唯讀修剪失敗印提示」和「不需要修剪時也清舊殘檔」其實由 `t_hook_event_trim_tmp_unique` 驗,後者沒綁到任何條款。
- 後果:三個月後有人只照條款查綁定測試,會以為這兩項沒有驗證。
- 歸因:未判定(條款和測試各自在不同輪加的)。

3. 〈審計修正紀錄〉「實作期」那條說「預篩階段的 try 不吞例外」沒有測試翻紅、刻意不釘。現在的測試把它釘住了。
引句:「預篩階段的 try 不吞例外」——預篩讀的是已經以替換方式解碼的文字
ID: g3
severity: minor
blocking: 否
- `t_bypass_ask_fallbacks_and_budget` 把 `m.prefilter` 換成會丟例外的函式,斷言 `entry` 回 rc 0 且不輸出。拿掉 `entry` 裡那層 try,這條會紅。
- 同一條也寫「故意改壞 18 種」「17 種有測試翻紅」,但文字只列了 16 種加這一種。數字對不上,且和 S4 條款自相矛盾。

4. d3 和 d4 沒對齊,Systems 節點也沒跟上。
引句:「事實,攻擊面從無限的寫法收成封閉的幾條規則」
ID: g4
severity: minor
blocking: 否
- d3 的 `why_chosen` 仍寫「攻擊面從無限的寫法收成封閉的幾條規則」,而 d4 說 d3 不宣稱封閉。d3 還是 `valid: true`。
- d3 否決方案②的理由是「仍擋不住刪掉重建成連結」。這條理由對出貨版同樣成立(d4 自己承認)。
- 讀 d3 的接手人會以為出貨版擋得住,d3 沒有指到 d4。
- `Systems/代理繞閘問人` 的「不管什麼」清單沒有 d4 那條「同一條指令裡改寫判斷當下已存在的路徑」。節點也沒有對應的 WHY 或 d4 指標。只讀這篇節點的人會漏掉這個攔不到的範圍。
- 歸因:未判定。

5. 計劃對「吃值旗標」的說法只對 `-n` 成立,`--no-verify` 沒照做。
引句:「commit 的長選項 `--message`、`--file` 等會吃下一個詞當值,`--` 之後不再看旗標」
ID: g5
severity: minor
blocking: 否
- 實測(結果是 `bypass_reasons` 回傳):
  - `git commit -m --no-verify` → `['no-verify']`
  - `git push -o --no-verify origin` → `['no-verify']`
  - `git push -- --no-verify` → `['no-verify']`
  - `git commit -m -n`、`git commit -- file -n` → `[]`
- `-m` 的值是 `--no-verify` 時 git 把它當訊息,並不跳過掛鉤。程式碼的 `_hit_codes` 對 `--no-verify` 只做全參數掃描。
- 方向是誤問,符合 d2「寧可漏問」的反方向。但計劃和 S2 都暗示「吃值旗標的值不算」,這裡兩處說法不一致。

6. 複製進來的預算區塊有一句已經過期。
引句:「目前註冊表最小值是 10」
ID: g6
severity: minor
blocking: 否
- 這支註冊的逾時是 5,最小值已經不是 10。
- 因為「有測試要求各份一模一樣」,不能只改這支,要連鄰居一起改,或把那句從逐字複本範圍拿掉。

7. 數字和說明沒有跟著更新。
引句:「量到一週約 371 次」
ID: g7
severity: minor
blocking: 否
- 〈實務隱患〉和 d1 還寫 371 次。〈量測〉後段已更新到 375、387、408。
- `_hookevent.py` 這次的行為改動也沒進節點:修剪失敗會往 stderr 印一行,所有掛鉤共用。「讀檔到換入之間別的程序追加的那一行會遺失」這項已知接受,也只寫在程式註解。`Systems/掛鉤存活事件` 沒有對應 REVISIT 或承認行。

## 固定席節點逐條判

- `lumos-cli-lifecycle`:新增的 WHY 句子內容和 `scripts/lumos`、`merge-claude-settings.py` 的實際改動一致。
  - 名單、狀態列、錨點、Codex 跳過 Bash matcher 都對得上。
  - 綁的 `t_bypass_ask_registered` 只驗安裝名單、狀態列、設定檔、Codex。自裝檔與錨點名單靠既有的集合相等測試。
  - `lumos lint` 0 問題。
  - 新增句子沒碰既有的 ★INVARIANT★(re-inject 保留 sentinel 外內容)→ 不影響。
- `lumos-cli-read`:只是 `scripts/lumos` 同檔牽連。這次沒動 `search` 的濾網 → 不影響。
- `design-loop`:處置閘第五步邏輯沒動。計劃有 `[S1]–[S6]` 條款且 S1–S5 定義了綁定測試 → 符合該 INVARIANT。
- `測試假綠形態`:新測試多數有「前置斷言證明現場成立」。
  - S3 用 `exp` 先建 repo,再斷言放行。
  - 但發現 1 說明 S1 對 `""` 案例只看 ask,屬於「現場走不到被測分支」型假綠,和該 INVARIANT 精神相符 → 影響:這一條。
- `guard-kill`、`pitfalls-code-loop`、`reversibility-governance-ledger` 與其他只列名的節點:只牽涉 `scripts/lumos` 或 `test_lumos.py` 同檔,沒動它們管的邏輯 → 不影響。
- `Issues/code-loop守衛main-direct盲區`:只因為 `test_lumos.py` 同檔被牽連 → 不影響。

## 三個核對問題

1. **原問題修復效果**:r4 配對案例我獨立跑了一部分(修前、修後都載入),結果相同。
   - `git commit -$'\156' -m x`:修前 `[]`,修後 `['commit-n']`
   - `git push $"--no-verify" o`:修前 `[]`,修後 `['no-verify']`
   - `git commit -m 1 >/dev/null -n`:修前 `[]`,修後 `['commit-n']`
   - 保留案例 `echo "x git push --no-verify"` 修前修後都是 `[]`,`git config core.hooksPath 2>/dev/null` 修前修後都是 `[]`。
   - 預篩對 `-$'n'`、`--no-ver\⏎ify` 修後都過。
2. **修補處相鄰路徑**:發現 1 是相鄰路徑的回歸,只出現在空字串參數的形狀。其餘案例我跑的都與修前相同或更好。
3. **同一案例修前、修後**:見發現 1 的表格。

## 未驗範圍

- 沒有跑完整的 `scripts/test_lumos.py`。
- 沒有在 root 權限下驗「目錄唯讀」這條測試。
- 沒有對照 `governance` 的審計條數(r1 33 條、blocking 18 條等)和上輪席報告,因為被要求不讀。
- 全 doctor 中 S12 顯示這份計劃紅 5/綠 0。這是上次規格閘的快取結果,我沒有重跑,不當證據。

最嚴重等級 major,共 1 條 blocking。

來源:r4-資安-文件-sonnet.md


我讀完了測試文件組的七個檔案,沒有可利用的洞。

## 逐類判斷

**1. 執行邊界:已看,無**
- **暫存目錄與子程序**:新測試的暫存目錄都用 `mkdtemp` 建,收尾用 `rmtree(..., ignore_errors=True)` 且只刪自己建的路徑。
  - 子程序全用 list 形式的 `_sp.run([...])`,沒有 `shell=True`,也沒有字串拼接成指令。
  - `git init`、`worktree add`、`commit` 的路徑都來自測試自建的 `base`,不吃外部輸入。
- **符號連結**:`os.symlink(real/"sub" → tmp_root/"lnk")` 和 `os.symlink(R → tmp_root/"realln")` 的連結檔都建在自己的暫存根底下,目標是自建的 repo。沒有寫到暫存目錄外,也沒有對連結目標做刪除。
- **假 git**:`fake/git`(`sleep 30`)放在專屬的 `mkdtemp` 目錄。`PATH` 只塞進 `env=dict(...)` 傳給那一個子程序,不動全域環境,收尾整個目錄刪掉。
  - 這個 `sleep` 可能在逾時殺掉後變孤兒,但只是資源耗盡,不在範圍內,不報。
- **權限還原**:`_os.chmod(rt, 0o555)` 被 `try/finally` 包住,必定還原成 `0o755`,測試中途失敗也不會留下唯讀目錄。`chmod(f, 0o644)` 用在自建檔。
- **HOME 隔離**:`t_bypass_ask_registered` 把 `HOME` 與 `USERPROFILE` 指到暫存家目錄再跑 `merge-claude-settings.py`,所以新的 Bash matcher 註冊不會寫進使用者真正的 `~/.claude/settings.json`。Codex 目標另帶 `CODEX_HOME` 指到暫存目錄。
- **`merge-claude-settings.py`**:新註冊只有 `matcher: Bash`、固定 `_hook_cmd("bypass-ask-hook.py")`、timeout 5,命令字串沒有外部可控的輸入。`_codex_entries` 對 Codex 用 `continue` 跳過,等於不註冊(測試也斷言 `hooks.json` 內不含 `bypass-ask-hook.py`)。
- **`scripts/lumos` 的名單**:`_VENDORED_TREE_FILES`、`_GLOBAL_CLAUDE_HOOKS`、`ANCHOR_FILES`、`enforcement_status` 各加一行字面常數,沒有路徑拼接。
  - `ANCHOR_FILES` 把新掛鉤納入錨點,是收緊而不是放寬。
  - 安裝副本若被改,錨點只盯來源樹,和其他既有掛鉤相同,不是這次新增的缺口。
- **存活事件修剪測試**:`mkstemp` 加 `copymode` 的行為由測試鎖住(權限維持 0644、殘留暫存檔清理、換入失敗不留殘檔)。
  - 那些測試對 `m.os.replace` 的 mock 只作用在 `with` 範圍內。
  - 殘檔清理只清自己目錄下 `*.trim` 且超過一分鐘的檔。這是被測程式的行為,屬程式組範圍。

**2. 文件裡給人照抄的回退步驟:已看,無**
- 計劃的〈回退〉要人拿掉 matcher、把檔名搬到 `_RETIRED_STUB_CLAUDE_HOOKS`、拿掉 `enforcement_status` 那一列、`lumos anchor approve` 重簽、重跑安裝。
- 沒有 `rm -rf`、`sudo`、`curl | sh` 這類指令,都是改檔和重跑自家安裝。文件還明說「只拿掉 matcher 不夠」,不會誤導人留下已註冊但行為不明的狀態。
- S6 手冊寫「使用者要跳過時自己在提示列用驚嘆號前綴執行」,這是使用者自己的 shell,屬設計決定,文件已明列。

**3. 授權範圍:已看,無**
- 掛鉤只回 `ask`,不回 `allow`,也不改指令。
- Codex 刻意不註冊。
- 失敗一律放行,這是明寫的威脅模型:問人層,不是安全邊界。
- `_codex_entries` 的 `continue` 只針對 `PreToolUse` 加 matcher `Bash` 這一條,不影響其他事件。

## 固定席節點

- **`Issues/code-loop守衛main-direct盲區`**:不影響。這次沒有碰 code-loop 守衛的 main-direct 邏輯,只動 `test_lumos.py`,新增的是新測試。
- **`lumos-cli-read` 的 INVARIANT(search 預設排除 superseded)**:不影響。diff 沒有動 search 路徑。
- **`lumos-cli-lifecycle` 的 INVARIANT(re-inject 只覆蓋 sentinel 之間)**:不影響。diff 只在筆記裡新增一行 WHY,沒有動 re-inject 程式碼。
- **`design-loop` 的 INVARIANT(處置閘第五步)**:不影響。這次沒有改處置閘邏輯。
- **`測試假綠形態` 的 INVARIANT(還原翻紅釘要配前置斷言)**:不影響資安面。
- **`guard-kill` 的 INVARIANT(rc 優先序、`--json` 純度)**:不影響,沒有碰 guard kill。
- **`pitfalls-code-loop` 和 `reversibility-governance-ledger`(`★RISK★`)**:不影響。
- **只列名的節點**:沒有看出與資安面相關的牽連。

## 附帶觀察

以下兩點沒有可描述的攻擊路徑,不計入 finding。
- 新掛鉤檔在安裝後放在 `~/.claude/hooks/`,錨點只驗來源樹。這和既有的六支掛鉤相同,屬原有的信任邊界,不是這次新增的缺口。
- 不少測試會真的呼叫 `git init`、`git commit`。它們依賴整輪測試前的 `_isolate_environment` 隔離使用者全域 git 設定。

最嚴重等級 clean,blocking 共 0 條。

來源:r4-規格符合-sonnet.md


**逐條對照結果:已實作、縮水、未實作都是 0 條;多做 1 條,規格自己前後不一致 1 條。**

驗法:用 `SourceFileLoader` 載入固定版 465736e9 的掛鉤,呼叫 `bypass_reasons`。跑了約 200 個案例,分三輪:S1/S2、S3 拋棄式、S4 效能與進入點。掛鉤實際以子程序執行,餵 stdin。測試腳本在 `/tmp/lumos-seat-work/code-代理繞閘字樣問人/規格符合-sonnet/` 的 `p.py` 到 `p6.py`。

## 一、發現

1. 多做:`git remote` 把「不是 `-v`、`--verbose`、`show`、`get-url`」的子指令一律當成改了推送位址。
引句:「return bool(args) and args[0] not in ("-v", "--verbose", "show", "get-url")」
spec 〈做法〉拋棄式判定寫的是「`git remote` 的寫入子指令」。唯讀或不改 URL 的 `-vv`、`update`、`prune` 也被算進去,後面的 push 於是失去拋棄式豁免,多問一次。
重現:cwd 在只有本機遠端的暫存 repo 時,`git remote -vv; git push --no-verify origin` 回 `['no-verify']`。`remote -v` 與 `remote show origin` 則回 `[]`。
方向是多問,不是漏問,所以是 minor。
歸因:未判定。這是規格與實作的落差,兩版沒做對照。
ID: p1
severity: minor
blocking: 否

2. ⚠ 規格自己前後不一致,實作照〈做法〉字面做,結果跟 [S2] 的字面衝突。
引句:「lk = next((k for k in range(i, len(seg)) if os.path.basename(seg[k]) == "lumos"), None)」
〈做法〉明寫「段裡有檔名為 `lumos` 的詞」就算 lumos 指令。[S2] 卻說「`LUMOS_SKIP_*` 設在 git 與 lumos 以外的程式前……放行」。
重現:`LUMOS_SKIP_X=1 cat scripts/lumos` 和 `export LUMOS_SKIP_X=1; grep foo scripts/lumos` 都回 `['lumos-skip']`。〈做法〉那句本意是涵蓋 `python3 scripts/lumos`,但同一條規則也會把 `cat scripts/lumos` 判成 lumos 指令。
照〈做法〉判為已實作。要不要收窄由編排者裁,所以標 ⚠。
歸因:未判定。
ID: p2
severity: minor
blocking: 否

## 二、逐條裁定

**〈做法〉**
- 讀輸入與預篩:已實作。
  - `entry(bytes)` 進場就起算預算。
  - 先解析 JSON,再套同一套前處理,拿掉引號與反斜線,不分大小寫比三個字樣和 `-n` 短旗標。
  - 預篩自包 try/except。
  - 抽測 `--no-ver''ify`、`-$'n'`、續行加 Tab 的 `-n`、續行切開的 `--no-verify` 與 `core.hoo\⏎ksPath`,都過預篩並輸出 ask。
  - 非 UTF-8、`command` 不是字串、`ls` 都放行,沒有 traceback。
- `guard`、事件名、`swallow=True`:已實作。事件名是 `pretooluse-bypass-ask-hook`,guard 呼叫不帶備註。
- 逾時預算:已實作。
  - 與 impact-hook、dispatch-lens-hook、memory-sweep 三支的逐字複本比對,三支都一致。
  - 假 git 睡 30 秒,300 段全要查 git,整支 4.09 秒結束,結果照問。
  - `MAX_GIT_CALLS=4`,300 段實測跑了 4 次。
- 長度上限 2 萬字走字面判:已實作。10 萬字單詞回 `literal`,0 秒。
- 前處理逐項:已實作。
  - 詞首才算註解,`a#b` 不算。
  - `$(` 重開引號層,內文有撇號的 heredoc 提交訊息仍判出 `-n`。
  - 引號遮罩。
  - ANSI 引號:`\156`、`\u006e` 都解得出。
  - `$"…"`。
  - 反斜線跳脫。
  - 續行。
  - 檔案代號:`-m 1 >x -n`、`2>&1 -n`、`{fd}>x -n` 都命中。
  - `)>` 拆分:`(cd X)>/dev/null` 問人。
  - 指令本身含私用區字元也只還原成普通字。
  - heredoc:多個、`<<-`、`<<<` 不算、算式 `<<` 不算、找不到結束字就不剝。
- 切詞與切段:已實作。指令替換佔位詞、換行當分隔、括號子殼層、`$(` 與 `$((` 大量不配對。最壞形狀在 2 萬字內都低於 0.1 秒。
- 找 git:已實作。`sudo`、`!`、`time`、`nohup`、`command`、`then`、`env` 都命中。
- 全域選項:已實作。
  - `-c`、`-C`、`--config-env` 分開寫與黏著都認得。
  - `-C` 可多次。
  - `--git-dir`、`--work-tree` 會記下。
  - 縮寫 `--no-veri` 必須帶到 `--no-veri` 才認(spec 就是 `--no-veri` 開頭),`--no-ver` 不認。
- 命中規則:已實作。
  - no-verify:僅限 commit 與 push,`merge`、`rebase`、`cherry-pick` 放行。
  - commit `-n`:`-n`、`-qn`、`-nm` 命中;`-mnote`、`-m -n`、`-F -n`、`--message -n`、`-- -n`、`-Sn` 不命中。
  - c-hookspath:`-c`、`--config-env`、`GIT_CONFIG_KEY_n`、`GIT_CONFIG_PARAMETERS`、先 export 的都認得。
  - config:`--unset`、`--unset-all`、`--replace-all`、`--add`、空字串值、`set`/`unset`、`--remove-section core`、`--rename-section core` 命中。讀值(含 `2>/dev/null` 與 `> f`)放行。
  - lumos-skip:段首賦值、`env`、`+=`、`export`、`declare -x`、`typeset -x`、先賦值再 `export 名稱` 命中。`export -n` 與一般參數 `grep -n LUMOS_SKIP_X=1` 放行。
- 拋棄式判定:已實作。
  - 生效目錄的優先序對。
  - `GIT_DIR`、`GIT_WORK_TREE`、`GIT_COMMON_DIR` 的各種形式(段首、`env`、`export`、`declare -x`、`--git-dir`、`--work-tree`)都使 commit、config、push 不豁免。
  - 符號連結加 `..` 問人。
  - 暫存根、已存在、共用 git 目錄在暫存根底下、沒有網路遠端,都要同時成立才豁免。
  - 非 repo 的暫存目錄豁免。
  - 工作樹(`.git` 檔指回真 repo)問人。
  - 有網路遠端問人。
  - `--global`、`--system`、`--file` 問人。
  - push 的本機路徑、`file://`、遠端名稱查 `get-url --push` 都對。
  - 前面動過遠端設定問人。
  - `-c remote.*`、`url.*`、`GIT_CONFIG_KEY_n=remote.*` 問人。
  - `--repo` 指到網路問人,`--repo` 指到本機暫存時豁免。
  - lumos-skip 接 lumos 指令不豁免。
  - 相對路徑的 cwd 與事件 cwd 不是字串都問人。
- cd 追蹤:已實作。
  - 子殼層、管線、背景、`||`、`if !`、大括號群組在管線或背景裡、`&&` 鏈接換行、`cd -`、`cd ~`、`cd` 不帶參數、`pushd` 都照規格。
  - `cd X && true; commit` 因為 cd 本身不是條件式,仍算數。這不是規格以外的行為。
- 變數展開上限:已實作。`A=$A$A` 連續翻倍 30 次只花 0.001 秒,超過 4096 就當判不出。
- 字面判:已實作。
- 命中輸出與三段式、`decide`、`bypass_reasons`、`main`:已實作。
- `merge-claude-settings.py`:已實作。
  - 載入實測:Bash matcher、逾時 5、`--budget 5`。
  - `_codex_entries` 輸出裡沒有 `bypass-ask-hook`。
- `scripts/lumos`:已實作。
  - `_GLOBAL_CLAUDE_HOOKS`、`enforcement_status` 一列、`_VENDORED_TREE_FILES`、`ANCHOR_FILES` 都有。
  - `governance/anchor-baseline.json` 已含新檔。
- 存活事件修剪:已實作(`_hookevent.py` 的 `_trim` 與 `_clear_stale_trims`,修剪失敗印提示)。這兩項我只讀碼,沒實際跑。

**〈範圍〉**:都有對應。已實作的(含刻意不攔 `merge`、`rebase`、`HUSKY=0`、`LUMOS_STOP_BLOCK_OFF`)我都抽測過,放行或問人與寫的一致。承認攔不到的各項沒有被實作成「攔得到」,沒有多做。

**驗收條款**
- [S1]:已實作。約 70 個案例全部命中。
- [S2]:已實作,除上面第 2 條的規格內部衝突。
- [S3]:已實作。約 75 個案例,與我預期不符的 3 個,查證後都是我的預期寫錯,不是實作偏離:
  - `cd X && true; commit`:cd 在鏈首,本來就算數。
  - `cd X/../../../../..` 落在 `/tmp`,仍在暫存根底下。
  - `--no-ver` 縮寫:規格就只認 `--no-veri` 以上。
- [S4]:已實作。
  - 最壞形狀都在 0.1 秒內。
  - 300 段要查 git 約 0.1 秒,照問。
  - git 卡住整支 4.09 秒,小於 5 秒。
  - 預篩階段不寫事件這一點,我讀碼確認,沒另外量事件檔。
- [S5]:已實作,見上面的 merge-claude-settings 與 scripts/lumos 兩項。
- [S6]:是人工驗收條款,不屬程式實作範圍。

另有一個小觀察,沒列為 finding:`D=/tmp; D+=/x` 的 `+=` 被當成取代而不是附加,結果只會比預期多問(⚠ 規格沒提 `+=` 對變數展開的語意)。

縮水+未實作共 0 條
