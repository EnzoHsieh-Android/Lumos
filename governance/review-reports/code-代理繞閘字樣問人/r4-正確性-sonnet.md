severity: major

審查範圍:程式組 r4-code.patch 逐 hunk 讀完。修補差異只用來對照兩版行為。實際載入修前 9b8ce146 與修後 465736e9 的 `bypass-ask-hook.py` 跑過。

## Findings

**1. 換行接續的條件式 `cd` 被當成一定會跑,修前會問、修後放行(修補造成的回歸)**
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
severity: minor
blocking: 否

引句:「        elif self.seg_conditional or p.endswith("||") or q.startswith("||"):」

- 輸入:`if [ -d /nope ]; then cd <暫存實驗repo>; fi; git commit -n -m x`。`f() { cd T; }; git commit -n -m x`、`for d in /nonexistent; do cd T; done; git commit -n -m x` 也同樣得到 `[]`。
- 錯在哪:`seg_conditional` 只認條件位置的 `if/elif/while/until/!`,`then`、`do` 和函式體裡的 `cd` 沒被當成條件式。條件為假時 `cd` 沒跑,提交落在真 repo。
- 兩版結果:都是 `[]`。
- 歸因:有證據的原有漏查。
- ⚠ 交編排者:計劃第 126 行寫「條件式與子殼層的 cd 一律保守」,但實際只涵蓋條件位置。這算 d2 接受的漏問,還是要補?我標 minor,因為需要同一條指令同時有條件式 cd 和 `-n` 才會漏。

**4. `env` 帶有值的選項時,後面的 `LUMOS_SKIP_*` 前綴認不出來**
severity: minor
blocking: 否

引句:「        while j < upto and (seg[j].startswith("-") or _ASSIGN.match(seg[j])):」

- 輸入:`env -u FOO LUMOS_SKIP_PUSH_GATE=1 git <推送>` 得 `[]`;`env -C /tmp LUMOS_SKIP_PUSH_GATE=1 git <推送>` 也得 `[]`。
- 對照:`env -i LUMOS_SKIP_PUSH_GATE=1 git <推送>` 得 `['lumos-skip']`。
- 錯在哪:迴圈碰到 `-u` 的值 `FOO` 時,它既不是 `-` 開頭也不是賦值,迴圈就停,後面的賦值沒被看到。
- 歸因:有證據的原有漏查(修前修後同為 `[]`)。

**5. 單引號或跳脫的 `$` 在拆詞後被還原,結果仍會展開變數**
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
