severity: major

本席只查文件、筆記、公開卷證,以及條款、測試、程式三方是否一致。所有實驗都在我自己的暫存目錄跑,已刪除,沒動 repo。程式的深層正確性不在本席範圍。

## 發現

### F1 test-guard 筆記兩條 PITFALL 被削掉前綴與症狀,只剩一串孤兒欄位
severity: major
blocking: 是 — 圖譜摘要行格式被破壞,`lint` 與 `doctor` 都驗不出來,屬於照規範寫錯。
引句:「[出處:2026-11-02 實作時測試先紅] [根因:候選路徑取改動後路徑,改名成非測試檔時那支已經不是測試檔]」
file: `docs/lumos-toolchain-knowledge/Systems/test-guard.md:17`(另一條在第 23 行)
後果:
- 兩行都丟了 `PITFALL:<症狀>`。原本是 `PITFALL:測試檔改名成非測試檔時,被刪測試的候選記在新檔名上` 與 `PITFALL:建置檔 enabled = 換行接 false 時逐行比對看不到`。
- 現在只剩多縮排一格、沒有前綴的欄位串。三個月後的人搜不到這兩個坑,`[test:t_tq_guard_test_removed]` 與 `[test:t_tq_guard_build_config]` 也沒有掛在任何摘要行上。
重現:
```
cd /Users/enzo/harness/lumos-tq-android
git show ce5256bd:docs/lumos-toolchain-knowledge/Systems/test-guard.md | grep -n PITFALL   # 17、23 行各一條
grep -n PITFALL docs/lumos-toolchain-knowledge/Systems/test-guard.md                       # 無輸出
python3.14 scripts/lumos lint Systems/test-guard                                           # ✓ 0 問題
```
歸因:有證據的修復回歸。修前兩行都有 `PITFALL:`,修後被刪。

### F2 指紋與身分的描述還停在「函式名加本體簽名」,程式已改成「函式名加種類」
severity: major
blocking: 是 — 筆記、計劃、標準互相矛盾,而且照舊描述判斷放行會失效與否會判錯。
引句:「WHY:候選指紋用規則、檔案、函式名加本體簽名、第幾個,不帶行號」
file: `docs/lumos-toolchain-knowledge/Systems/test-guard.md:21`
後果:
- 同一篇筆記裡,新加的 WHY(第 25 行)寫「身分是函式名 + 跳過,不帶類別、本體與跳過種類」,跟第 21 行正面矛盾。
- 同樣的舊說法還在 `Systems/pitfalls-lint-adapter.md:20`(「作弊候選用規則、檔名、函式名加本體簽名」)。
- 計劃做法一〈次數差的身分〉(`Projects/Android測試防竄改檢查_計劃.md:132`)也還寫「函式名加本體簽名、正規化後的那一行」。
- 這個計劃是 test-guard 筆記與標準指定的逐條判法單源。
- 讀的人會以為改測試本體會讓舊放行失效,實際不會。
重現:同一個 `@Ignore` 測試,本體分別是 `assertEquals(1, f())` 與 `assertEquals(2, g(9))`,各跑一次 `test-guard --json`。
```
修後 兩種本體 key 都是 b67c5d9ef21ccbed
修前 本體 A: 6c4179c9a4294bc0   本體 B: a043cb2563b87f7e
```
修前的程式來自 `git archive ce5256bd scripts`。
歸因:有證據的修復回歸。程式在 r1 修補時改了身分,文件沒跟上。

### F3 `ignoreFailures` 被收窄到測試區塊內,條款 S7、計劃規則表、標準都沒改,點號賦值寫法漏列
severity: major
blocking: 是 — 條款說「列」、程式現在不列,而且標準的「抓不到」清單也沒補這一條。
引句:「S7 r1 detekt 的 ignoreFailures 不列」
file: `scripts/lumos:48759`(`_TG_IN_TEST_BLOCK`),對照 `docs/lumos-toolchain-knowledge/Projects/Android測試防竄改檢查_計劃.md:229`(條款 S7 寫「當建置檔新增 `ignoreFailures = true`」)
後果:
- 修補把 `ignoreFailures` 從全域規則搬進「測試區塊內才算」,條款、規則表(第 123 行)與標準都沒更新。
- 區塊外的點號賦值現在不列:`tasks.test.ignoreFailures = true`、`test.ignoreFailures = true`,頂層的 `ignoreFailures = true` 也不列。
- 這是一條沒有警告的新缺口,標準的「抓不到」也沒寫它。
重現(同一個提交對):
```
修前: tasks.test.ignoreFailures = true / test.ignoreFailures = true / ignoreFailures = true  -> 各 1 條 tq/build-config
修後: 以上三種 -> 候選 0 條
修後: tasks.withType<Test> { ignoreFailures = true } -> 仍列
```
歸因:有證據的修復回歸。收窄是為了 detekt 的同名設定誤報,代價沒寫進任何文件。

### F4 「擋下後用 `LUMOS_SKIP_LINT_NEW=1` 繞過會留帳」在它描述的情境下不成立
severity: major
blocking: 是 — 標準與筆記的「代價」都靠這句當補償,實際不留帳。
引句:「這一次要先過用 `LUMOS_SKIP_LINT_NEW=1`(留帳)」
file: `skills/lumos-project-notes/commands/test-quality-standard.md:42`(同樣的話在 `Systems/test-guard.md:16` 的 [代價:…(留帳)])
後果:
- 情境是「比對自己壞了」。`_lint_new_off`(`scripts/lumos:38991`)只在 `g["cands"] and not g["error"]` 時才記帳。比對出錯時 events 為空,繞過沒有任何痕跡。
- 計劃第 146 行寫「它自己出錯也不擋,也不寫帳」,跟標準和筆記互相矛盾。
重現:載入 `scripts/lumos` 模組,把 `_tg_analyze` 換成丟例外,設 `LUMOS_SKIP_LINT_NEW=1`,呼叫 `_lint_new_verdict`。
```
正常: status=off events=[('skipped-env', '關閘時作弊比對有 1 條候選沒判')]
比對出錯: status=off events=[]
```
歸因:有證據的原有漏查。修前版本結果相同(events=[]),不是這輪造成。

### F5 公開 repo 追蹤的審查卷證仍含考場提交編號與私有分支名
severity: major
blocking: 是 — 去識別化漏出真實識別字。派工詞只豁免本機絕對路徑,沒有豁免提交編號與分支名。
引句:「mOrangePos 本機演練分支 drill/test-guard(起點 c66c81b、卷證 436dad6)」
file: `governance/review-reports/code-Android測試防竄改檢查/r1-snapshot.patch:851`
後果:
- 活的筆記與評測摘要這輪確實清乾淨了,但凍結的審材原樣重新公開了同一批識別字。
- 範圍內已追蹤的檔案包括 `r1-snapshot.patch`、`r1-docs.patch`、`r1-合約-sonnet.md`、`r1-資安-sonnet.md`,以及 `r2-repair*.patch`、`r2-snapshot.patch` 的刪除行。
- 舊的設計審材 `governance/review-reports/Android測試防竄改檢查/r1-snapshot.md:61` 與 `r2-snapshot.md:67` 還有 `drill/android-unit-test-standard`。
- 識別字有 `436dad6`、`drill/test-guard`、`c66c81b`、`65f05c0`(`r1-snapshot.patch:807`)、`drill/android-unit-test-standard`。
- `r1-合約` 與 `r1-資安` 的席報告是原文引句,不能改。
重現:
```
cd /Users/enzo/harness/lumos-tq-android
git ls-files governance/review-reports | grep -F "code-Android測試防竄改檢查"
grep -rIn "436dad6\|drill/test-guard" governance/review-reports/code-Android測試防竄改檢查/
```
`436dad6` 與 `drill/test-guard` 在範圍底版 047031883 找不到,是這個分支新增的洩漏。
歸因:有證據的原有漏查。r1 清理漏了凍結卷證,這輪的修補差異又把刪除行再複製進新的 patch。

### F6 標準說「完整清單在工具輸出」,但輸出的清單比標準少
severity: minor
blocking: 否 — 只是說明不完整,不會讓推送擋下或做錯操作。
引句:「完整清單在 `lumos test-guard` 輸出的最後與 `--json` 的 `limitations`」
file: `skills/lumos-project-notes/commands/test-quality-standard.md:39`
後果:
- 標準的清單有「catch 裡只印出例外而 try 沒有斷言」,`_TG_LIMITS`(`scripts/lumos:49263`)沒有這一條。
- 計劃第 136 行的完整清單還多出幾項:CI 的 `timeout-minutes`、巢狀區塊註解、版本目錄、lint 與 detekt 基準檔、同指紋沿用舊放行。這些在標準與工具輸出都沒有。
- 修補後新增的兩個取捨(同名測試互抵、測試檔整支改名會把類別層級跳過列一次)只在 WHY 裡,標準沒寫。
- 「本體有改的改名(會列成刪除加新增)」實際只列刪除,新增本身不是候選,措辭不精確。
歸因:有證據的修復回歸,屬於這輪補清單時沒補齊。

### F7 驗證紀錄前提寫「這次推送的功能提交」,三個月後無法對上版本
severity: minor
blocking: 否 — 只影響重跑與核對,不影響現行行為。
引句:「工具鏈這次推送的功能提交(Android 測試防竄改檢查)」
file: `docs/lumos-toolchain-knowledge/Verification/2026-11-02_Android測試防竄改檢查實跑.md:5`
後果:
- 改寫前至少還有分支名可查,現在沒有任何可定位的版本線索。
- 這份紀錄的對照表與 776 個提交的歷史是修補前的執行結果。修補後重跑「差異 0」只出現在收貨紀錄指到的會談暫存區,公開紀錄沒有。
- 另有數處測試說明已過期:`t_tq_guard_cli_contract` 的說明寫「四種大輸入 30 秒內」(`scripts/test_lumos.py:121056`),現在是八種大輸入加截止時間與控制字元;S13、S14 的說明也沒提新增的行為。
歸因:有證據的修復回歸。改寫前有分支名可查,改寫後沒有。

## 驗證了沒問題的部分
- 兩個 manifest 的指紋實算全部對得上(`android-test-guard-drill-20261102` 的 9 個檔、`android-unit-standard-drill-20261101` 的 20 個檔)。
- `history.json` 的數字與驗證紀錄一致:44 條、27 個提交、判錯 2 條。Semgrep 的 21 = 6+7+4+4 也對。
- 節點 `lint` 全部 0 問題。`spec-trace` 23 條款中懸空 0、壞名 0。
- 公開筆記與評測摘要沒有真實套件名、類別名,也沒有本機路徑。
- 筆記對程式的取捨描述查證屬實:
  - 同名測試互抵:跑出 0 候選,與筆記一致。
  - 測試檔整支改名時類別層級的跳過會列一次:跑出 1 條,與筆記一致。
  - 比對時間不算進預算:拿掉那行後 S12 r1 轉紅。
- 把新測試的受測邏輯各改壞一次,測試都會轉紅:
  - 註記正規化拿掉:S5 r1 三條轉紅。
  - 身分改回帶本體簽名:S1 r1 兩條轉紅。
  - 類別層級不分檔:S1 r1 一條轉紅。
  - 斷言字表拿掉 `awaitComplete`、`expectNoEvents`、`confirmVerified`:S5 r1 轉紅。
- 快照副本實跑 `-k tq_guard` 163 條、`-k lint_new` 71 條、`-k lint_waive` 27 條,全綠。

## 圖譜鏡頭
- `lumos impact --diff 047031883..ea1e0b8a6` 給出固定席:`Systems/test-quality-cli`、`Systems/pitfalls-code-loop`、`Systems/測試假綠形態`(★INVARIANT★)等。
- `Systems/測試假綠形態` 的合約要求翻紅釘必須配「前置斷言證明現場成立」。這輪新測試有補前置斷言的是 S12、S13 的新案例;S5、S1 的「不列」類案例沒有獨立前置,但上面的改壞實驗證明它們不是空轉。
- `Systems/pitfalls-code-loop` 的新增段落(放行檔讀不了時有候選就擋、關閘照跑留帳)與程式一致。
- F1 的缺行造成 test-guard 的測試綁定掉線。F2 讓 test-guard、pitfalls-lint-adapter、計劃三處對指紋算法的描述互相矛盾,這三篇都在固定席周邊。
- `lumos search` 搜 `[test:t_tq_guard_build_config]` 時,命中的是那串孤兒欄位,而不是 PITFALL。

## 三問
1. 原問題的修復效果有何行為證據?
   - 時間預算(拿掉延伸就轉紅)、跳過身分、類別層級分檔、斷言字表、註記正規化,都有「改壞就紅」的行為證據。
   - 文件側的去識別化在活的筆記與評測摘要上成立,但凍結卷證沒清(F5)。「抓不到」清單補了,仍不齊(F6)。
2. 修補處的正常、錯誤與相鄰路徑是否仍成立?
   - 成立:正常案例、同名互抵、檔案改名的取捨,實測與筆記一致。
   - 不成立:`ignoreFailures` 的點號賦值寫法漏列(F3),文件的指紋描述與程式脫節(F2),兩條 PITFALL 損毀(F1)。
3. 新發現的同一案例在修前、修後各是什麼結果?
   - F3:修前列 1 條,修後 0 條。
   - F2:修前本體不同會產生不同 key,修後相同。
   - F1:修前兩行都有 `PITFALL:`,修後被刪。
   - F4:修前修後都不留帳。
   - F5:修前活的筆記有識別字,修後只剩卷證有,識別字本身沒消失。

另外要交代:我為了找洩漏,用過一次全 review-reports 的 grep。輸出順帶帶出上一輪席報告的約 100 字引句,我的判斷沒有依賴它。

severity 最高為 major:5 條 major(F1 到 F5)、2 條 minor(F6、F7)。
