severity: minor

我沒找到 blocker 或 major。本輪修補的核心行為(身分、分岔點、單行上限、關閘留帳、CI 呼叫判法)都跟程式對得上。下面是七條措辭或精度層級的不一致,另有 `lint`、`spec-trace`、manifest 指紋與去識別化的核對結果。

### F1 標準「抓不到」與工具輸出不是逐字同一份
severity: minor
blocking: 否 — 只是宣稱比實際強,不影響推送判定
引句:「標準那條由 `t_tq_guard_cli_contract` 釘成逐字同一份」
file: `scripts/test_lumos.py:121342`(測試用 `x.split(";候選要人裁")[0]` 切掉了工具最後一句的尾巴)
後果:工具的最後一條是「…不是解析器;候選要人裁」,標準那條只寫到「…不是解析器。」。計劃和標準都寫「逐字」,實際是「去掉一句尾巴後相同」。接手的人若照「逐字」去改任一邊,測試會紅。
重現:我比對了 `test-guard --json` 的 `limitations` 與標準那條。前 7 項都在標準全文裡,第 8 項因為多了「;候選要人裁」不在。
歸因:有證據的修復回歸(「逐字同一份」是這輪才加的說法)。

### F2 test-guard 筆記兩條 WHY 對「跳過類候選身分有沒有類別路徑」互相矛盾
severity: minor
blocking: 否 — 只有說法錯,放行仍照指紋運作
引句:「函式身分(類別路徑加函式名;類別層級的註記用所在檔)加那條規則的細節」
file: `docs/lumos-toolchain-knowledge/Systems/test-guard.md`(該 WHY 在本輪 repair-docs.patch 第 210 行)
後果:同一篇下一條 WHY 寫「不帶類別」,程式也是只用函式名。「改了哪條斷言」也只對 `tq/expected-changed` 成立,`tq/assert-weakened` 的身分是斷言數量(`len/強斷言/常值` 三個數字)。
重現:`ATest.t` 和 `BTest.t` 同名,只給 `BTest.t` 加 `@Ignore`,`test-guard --json` 回 `tq/skip-added  ident=t\x00跳過`,沒有 `BTest`。assume 那條的 ident 是 `u\x00跳過:assumeTrue(isEmu)`。
歸因:有證據的修復回歸(這輪新寫的身分說法,計劃〈次數差的身分〉那段寫對了,這條沒對上)。

### F3 `tq/ci-config` 規則欄寫「沒有任何指令再呼叫它」,程式是看次數
severity: minor
blocking: 否 — 程式比文件嚴,多出的候選可放行
引句:「改動前呼叫的 Gradle 測試或 check 任務,改動後沒有任何指令再呼叫它」
file: `scripts/lumos`(`_tg_ci_hits` 與 `_tg_diff_locs(chh, cb)`)
後果:文字讀起來像「只要還有別處呼叫就不列」,程式是任務名的呼叫次數變少就列。
重現:CI 檔有兩個 job 都跑 `./gradlew test`,改後只剩一個 job 跑它,另一個改成 `assemble`。`test-guard` 列 `tq/ci-config`,原因是「拿掉了呼叫測試的 Gradle 任務:test」。
歸因:有證據的修復回歸(該句是這輪才改成這個說法)。

### F4 「關閘留帳:有候選才記」在這輪沒掃到的幾處還是舊說法
severity: minor
blocking: 否 — 舊說法是少報,實際行為是多留痕跡
引句:「整道關掉是設定 off 或環境變數(有候選時留帳);比對工具自己出錯時擋下而不是放行」
file: `docs/lumos-toolchain-knowledge/Projects/Android測試防竄改檢查_計劃.md`(〈實務隱患〉與〈比對出錯擋下〉那條),`docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md:206`,`skills/lumos-project-notes/commands/06-代碼審與推送.md:15`,`docs/指令參考.md:174`
後果:〈比對出錯擋下〉那條寫單次出口 `LUMOS_SKIP_LINT_NEW=1(有候選時留帳…)`,正好是比對出錯的情境,現在這個情境也會留 `skipped-env` 帳。三個月後的人會以為比對壞掉時用環境變數繞過不留痕。
重現:`grep -rn "有候選" docs skills` 篩「留帳」。程式見 `_lint_new_off`,`g["error"]` 分支會寫 event。
歸因:有證據的修復回歸(這輪改了行為與計劃 S14,同族的其他說明沒掃完)。

### F5 健檢把「比對出錯」的 skipped 帳也標成「有候選沒判」
severity: minor
blocking: 否 — 只是標籤不準
引句:「關閘時作弊比對沒跑完:」
file: `scripts/lumos:4151`(標籤是「設定關掉時作弊比對有候選沒判」與「環境變數跳過時作弊比對有候選沒判」),事件由 `scripts/lumos` 的 `_lint_new_off` 寫入
後果:修前 `_lint_new_off` 出錯不寫帳,修後寫 `skipped` 或 `skipped-env`,健檢只按 `kind` 計數。出錯的紀錄會被印成「有候選沒判 N 次」,誤導。測試 `S15 r1` 釘的就是這個標籤。
重現:兩段原文對照(`_lint_new_off` 新增的 `kind` 事件,與 4151 行的標籤)。
歸因:有證據的修復回歸(修前路徑無此事件,是這輪新增事件造成)。

### F6 計劃 S14 條款說 off 與環境變數都會在比對出錯時留帳,測試只釘了環境變數那一半
severity: minor
blocking: 否 — 程式本身正確,缺的是測試鑑別力
引句:「off 或環境變數跳過時比對照樣在背後跑,有候選或比對出錯才各寫一筆 `skipped`/`skipped-env` 治理帳」
file: `scripts/test_lumos.py`(`t_lint_new_test_guard_failure_blocks` 的 `S13 r2` 只用 `env={"LUMOS_SKIP_LINT_NEW": "1"}`)
後果:設定 off 加比對出錯這條路沒有測試。
重現:我在 `git archive` 副本把 `_lint_new_off` 的出錯分支改成 `if g["error"] and skip_env:`,跑 `-k lint_new`,結果 73 passed, 0 failed,改壞沒被抓到。
歸因:有證據的原有漏查(同批改壞中,另 13 個改壞都被新測試抓到)。

### F7 計劃與筆記說 ignoreFailures 只排除「外掛區塊」,程式是逐行比對外掛字樣
severity: minor
blocking: 否 — 只對刻意單行寫法有影響
引句:「只排除上面那幾種靜態檢查外掛的區塊」
file: `scripts/lumos`(`ignore_fail = _TG_IGNORE_FAIL.search(joined) and not _TG_NOT_TEST_PLUGIN.search(head + " " + line)`)
後果:該句的「上面」其實指同一格後面才列的名單(前向參照)。程式的排除名單還多了 `coverage`、`jacoco*`、`kover*`、`lintOptions`,而且是看區塊開頭加上當行文字。
重現:`tasks.test { ignoreFailures = true; finalizedBy("jacocoTestReport") }` 單行,`test-guard` 回 0 條。同一行去掉 `finalizedBy(...)` 就回 1 條 `tq/build-config`。
歸因:有證據的修復回歸(排除機制與說法都是這輪新增)。

## 圖譜鏡頭
- `lint` 跑了 `Systems/test-guard`、`Systems/pitfalls-lint-adapter`、`Projects/Android測試防竄改檢查_計劃`、`Systems/pitfalls-code-loop`、`Projects/新增告警閘_計劃`,都是 0 問題。
- 被補回的兩條 PITFALL 都有 `[出處:]`、`[根因:]`、`[test:]`。新增的三條 WHY 都有 `[出處:]`、`[因:]`,也有 `[不選:]` 或 `[代價:]`。
- 筆記沒有抄到別家的檔名。新增的 WHY 引用的是常數值(2 萬字),沒有抄函式內容。
- `spec-trace` 結果:23 條款、懸空 0、壞名 0。
- 影響範圍內 `Systems/pitfalls-code-loop.md:206` 還是舊說法,見 F4。

## 去識別化與 manifest
- 兩個 manifest 我逐檔重算 sha256:`android-test-guard-drill-20261102` 的 9 個檔、`android-unit-standard-drill-20261101` 的 20 個檔全部相符,沒有缺漏也沒有多餘。
- 我拿考場 repo(mOrangePos)做比對,檢查整份 snapshot 公開檔的新增行:
  - 823 個提交(含所有分支)的 7 到 40 碼十六進位字串,命中 0。
  - `com.citrus`、`morangepos`、本機路徑、分支名,命中 0。
  - 考場 403 個類別或檔名與 2232 個函式名,命中 0。
  - 只有 `mOrangePos` 專案名出現,這是計劃〈六〉已寫明可寫的範圍。
- `cases.json`、`history.json`、`semgrep/` 全是代稱(`F01`、`c01`)與合成樣本。

## 三問
1. 原問題的修復效果有何行為證據? 有。我在副本對 14 處關鍵判斷逐一改壞,13 處被這輪新測試抓到(8 處翻紅條目對得上旁邊說明的子情況),只有 F6 那處沒被抓到。本輪新增的 S1 到 S15 說明所述的子情況,實測都由對應測試驗到。
2. 修補處的正常、錯誤與相鄰路徑是否仍成立? 大致成立。唯一失衡點是 F5:新增的 `skipped` 事件讓健檢標籤失準。另外 F3 顯示 CI 判法比文件描述的嚴(次數而非存在)。
3. 新發現的同一案例在修前、修後各是什麼結果?
   - F4 / F5:修前比對出錯不寫帳,修後寫 `skipped` 或 `skipped-env`;文字與健檢標籤沒跟上。
   - F2:修前 WHY 寫「函式名加本體簽名」,修後寫「類別路徑加函式名」,但程式實際從修前到修後都是只用函式名,沒有類別路徑。
   - F1、F3、F7:修前沒有這些說法,是這輪新寫的,修後說法與程式有落差。

本輪沒有 blocker 或 major,找到的七條(F1 到 F7)都是措辭與精度層級。
