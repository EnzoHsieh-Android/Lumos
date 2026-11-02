severity: minor

## 一、修補效果:行為證據(已驗)

- **做法**:我把修前版(d5e8f27)與修後版(2fa806f)的 `scripts/test_quality.py` 各取出來,對同一批 XML 失敗文字比較。
  - 全部在 `/tmp/lumos-seat-work/code-收證認得Truth與裝置字串比較/單reviewer-sonnet/` 的複本裡做,沒改 repo。
- **原問題已修**:首個堆疊行是 `<init>`、連字號方法名、含空白方法名或模組前綴(`java.base/…`)時,若 `Assert` 堆疊只在 `Caused by:` 之後,修前判「是斷言」,修後判「不是」。
  - 我自己造的「含括號的方法名」「模組前綴」兩個輸入也是修前 True、修後 False。
- **須維持的行為,逐一確認沒壞**:
  - 字串比較、不帶訊息的 assert、Hamcrest。
  - 前導空行與 CRLF。
  - Tab 縮排的堆疊行(自己多造的)。
  - 一般例外訊息提到斷言名:仍判不是。
  - Truth 與陣列比較的本機型別:`test_truth_local_assertion_types_are_attributed`、`test_local_array_comparison_failure_is_attributed_device_text_is_not` 綠。
- **指紋表**:`_TEST_QUALITY_BUNDLE_DIGESTS` 三個檔的 sha256 都與 2fa806f 的檔案相符(自己重算)。
- **線性**:我量了十二種病態輸入,修前修後同量級,40 萬字元內都在 0.02 秒內:
  - 大量 `\n\tat x` 無括號行。
  - 單行 40 萬字元。
  - 大量 Tab。
  - 大量 `\n`+Tab。
  - `at at at …`。
  - 大量 Caused by。
  - 40 萬個左括號。
- **測試套件**:`python3.14 scripts/test_test_quality_cli.py` 為 64 個 OK。`test_lumos.py` 的 `-k t_secev_tq`、`-k t_test_quality_drill`、`-k t_test_quality_standard` 全綠。
- **變異(守衛真的會紅)**:
  - 拿掉 Truth 兩型別:`test_truth_local_assertion_types_are_attributed` 紅,`t_secev_tq_truth_*` 兩支也紅(我同步改了指紋表,避免因指紋不符而假紅)。
  - 改回舊 frame 規則、拿掉 Caused by 切分、拿掉 Hamcrest、收窄成只認 `Assert.assert*`、第一行放寬:都有測試紅。
  - 以下 F1 列的幾條變異活下來。
- **公開檔識別字**:新增的公開檔裡,我沒看到套件名、類別名、本機絕對路徑、裝置序號。
  - 只有核准保留的市售型號。
  - 公開卷證說明檔(`README.md`)的 sha256 與 `manifest.json` 相符,20 個檔,沒有漏列。
  - 我不知道真實識別字長什麼樣,這項只能判到「沒看到明顯外流」。
- **REVISIT**:新增的都是獨立一行、帶 2026-12-15 日期,寫法合規。

## 二、Finding

### 1. 裝置判定的幾道條件沒有測試釘住

引句:「b"java.lang.AssertionError: helper said at org.junit.Assert.fail(Assert.java:86)",」

**失敗場景(變異復現)**:
- 現有這個「訊息提到斷言名」案例整段只有一行,沒有堆疊行,走的是 `frame is None` 那條路。所以把 `own` 改成從文字開頭算(`own = text[:cause.start() if cause else len(text)]`),所有 CLI 測試照綠。
- 輸入 `java.lang.AssertionError: said at org.junit.Assert.fail(Assert.java:86)\n\tat com.example.Helper.check(Helper.kt:9)`:
  - 正確答案是 False(堆疊裡沒有 Assert)。
  - 變異後變成 True。
  - 這是第一行訊息自己假裝成斷言堆疊,而測試抓不到。
- 同一次變異跑下來,以下條件放寬或拿掉,`scripts/test_test_quality_cli.py` 也都不紅:
  - 堆疊行縮排 `[ \t]*` 改成不吃縮排:所有測試樣本的堆疊行都沒有縮排,與 AGP 報告的堆疊行通常縮排(我的推測,未見原始報告)不一致。
  - `first` 的 `.strip()`:不帶訊息的 `AssertionError` 加 CRLF 會被拒。
  - Assert 片語前的 `\b`。
  - `(?:fail|assert)\w*` 收窄成 `\w*`。
  - 這些條件都沒有一支測試釘住。

**歸因**:有證據的原有漏查。這些條件在修前版就同樣沒被釘(修前版也沒有帶縮排或帶堆疊行的案例),修補沒有造成它們,只是新增的四個案例也沒補上。

**查證命令**:`python3.14 /tmp/lumos-seat-work/code-收證認得Truth與裝置字串比較/單reviewer-sonnet/mut.py`。修前版與修後版的 `junit()` 對上面那個輸入都回 False,所以也不是修補回歸。

severity: minor
blocking: 否

### 2. 訊息自己含「堆疊樣」行加 `Caused by:` 行時,合法斷言被拒收

引句:「own = text[frame.start():cause.start() if cause else len(text)] if frame else ''」

**失敗場景**:
- 比較含堆疊文字的字串,例如測試在驗證崩潰報告的格式化結果。
- 輸入 `org.junit.ComparisonFailure: expected:<boom\nat com.example.Foo.<init>(Foo.kt:3)\nCaused by: x> but was:<ok>\nat org.junit.Assert.assertEquals(Assert.java:115)`。
- 訊息裡的 `at ...<init>(` 現在被當成第一個堆疊行,訊息裡的 `Caused by:` 把 `own` 切掉,真正的 `Assert.assertEquals` 沒進去,判成不是斷言,故障收據被拒。
- 計劃與標準寫「訊息自己帶 `Caused by:` 的字串比較照認」。這句只有在訊息裡沒有堆疊樣行時成立。
- 方向是寧可拒收,不會誤放行。

**歸因**:
- 帶點號的版本(`at com.example.Foo.bar(`)修前修後都是 False,是有證據的原有漏查。
- 非帶點號版本(例如 `<init>`)修前恰好 True(靠誤抓 Caused by 之後的 Assert 行),修後 False,是把兩種寫法判成一致,修補造成的差異。

**查證命令**:`probe` 兩版對這兩個輸入的結果。`<init>` 版修前 True、修後 False,帶點號版兩版都 False。

severity: minor
blocking: 否

### 3. 安全證據閘的「裝置字串比較」放行面宣稱被釘住,測試只釘 Truth 那半

引句:「是這次新增的放行面,由 `t_secev_tq_truth_fault_counts_like_assertion` 釘住」

**失敗場景**:
- `scripts/test_lumos.py` 的 `_sg_junit` 只有 `failure_truth`,走的是型別欄。
- 整條沒有裝置式(沒有型別欄的文字)的案例。
- 我把 `assertion_failure` 的裝置分支整個關掉(`if False:`),指紋表同步改過,再跑 `-k t_secev_tq`:7 個全綠。
- 所以驗證紀錄與計劃寫的「Truth 或裝置字串比較寫的故障收據……由該測試釘住」,實際只釘到 Truth;裝置字串那半由 CLI 單元測試間接守,安全證據閘這條路沒有直接釘。

**歸因**:有證據的修復回歸(措辭是這輪新寫的)。修前版沒有這個宣稱,修補的文字帶進了範圍。

**查證命令**:`python3.14 scripts/test_lumos.py -k t_secev_tq`,在 `if False:` 變異下 7 passed。

severity: minor
blocking: 否

### 4. 錯字「從從」兩處,另有一則測試註解過時

引句:「改成只吃空白與 Tab、從從第一個堆疊行起(含這一行)才找,大輸入測試釘住」

- 同樣的「從從」出現在驗證紀錄「第一版的切法在大輸入上是二次方」那條(snapshot 內)。
- 審材外查證:`scripts/test_test_quality_cli.py:284` 的註解還寫「要在第一個堆疊行之後才切」,與規則「從第一個堆疊行起(含這一行)」不一致。

**歸因**:有證據的修復回歸(修補改文字時漏改、手滑)。

**查證命令**:`git -C /Users/enzo/harness/lumos-unit-test-drill grep -n "從從" 2fa806f445b1ade4a5a7ba02fdd0296aff54ac11 -- docs`,兩處命中。

severity: minor
blocking: 否

### 5. 公開說明檔「兩層」與內容不符

引句:「剩下的 `com.example.pos.category`、`com.example.pos.drill` 兩層是代稱與演練新增的套件」

**失敗場景**:
- `governance/eval/results/android-unit-standard-drill-20261101` 裡實際還有 `com.example.pos.drill.bad` 與 `com.example.pos.drill.samples` 兩個再下一層。
- 另外 `Systems/test-quality-cli.md` 的 WHY 仍寫「子套件攤平」,與說明檔改後的說法(保留 category 與 drill 兩個子層)不全相符。
- 這是措辭精度,沒有洩漏。

**歸因**:有證據的修復回歸(這輪新寫的句子)。

**查證命令**:`grep -rhoE 'com\.example\.pos[a-z.]*' governance/eval/results/android-unit-standard-drill-20261101`,出現 `.drill.bad`、`.drill.samples`。

severity: minor
blocking: 否

## 三、圖譜鏡頭

- **`lumos-cli-read`、`lumos-cli-lifecycle`**(搜尋排除、re-inject 的 ★INVARIANT★):不影響。這次沒動搜尋與 re-inject 的路徑。
- **`測試假綠形態`**(還原翻紅釘需前置斷言):不影響。新增的 `t_secev_tq_*` 有前置斷言,先確認「一般斷言失敗不是 invalid」,再做 Truth 對照。
- **`design-loop`、`bound-tests-gate`、`guard-kill`**:不影響。
  - 這次只改 `assertion_failure` 與兩支測試改名。
  - 計劃 S5 的 `[test:…]` 名稱與測試檔現況一致,沒有懸空。
- **`test-quality-cli`**(家):PITFALL 防回歸清單的十支名稱與 `t_test_quality_drill_cli_cases_present` 的清單相同,都存在。
  - 該測試是寫死名單,不會讀 PITFALL,名單和 PITFALL 分叉時不會紅(措辭小事,併入 F1 的覆蓋面類別)。
  - 既有的 `REVISIT:[when-file:scripts/test_quality.py][by:2026-11-08]` 本就會在這次推送被點名,是既有機制,不算新增。
- **「這次新增的殘留」段**:派工單沒附,不需逐條答。

## 四、角色卡

派工時沒附卡,略過。

## 五、三問

1. **原問題的修復效果有何行為證據?**
   - 有。非帶點號首行(`<init>`、連字號方法名、`$$Lambda$`、含空白方法名、模組前綴)加 `Caused by:` 之後才有 Assert 堆疊的輸入:修前 True、修後 False。
   - 陣列比較近似型別名:修後 False,由 `test_truth_lookalike_types_are_not_attributed` 守,並確認拿掉該項會紅。
   - 舊 frame 規則的變異會讓 `test_device_runtime_around_comparison_failure_is_not_attributed` 紅。
2. **修補處的正常、錯誤與相鄰呼叫路徑是否仍成立?**
   - 成立,有 F2(訊息帶堆疊樣行加 Caused by)這個範圍很窄的例外。
   - 裝置那路、本機型別那路、安全證據閘兩條路都還能用。
   - 沒有型別的「無括號堆疊行」仍會繞過切分:`at com.example.H.check` 後面接 `Caused by:` 再接 Assert,修前修後都是 True。
   - 真實 Java 堆疊行一定帶括號,所以我沒當成 finding,只記為未驗範圍。
3. **新發現的同一案例在修前、修後各是什麼結果?**
   - F2 的 `<init>` 版修前 True、修後 False,帶點號版兩版都 False。
   - F1 提的「訊息假裝成斷言」輸入兩版都 False,是變異才會 True。

## 六、未驗範圍

- 真實 AGP 報告的堆疊行縮排(我沒有原始報告檔,只能憑測試樣本推測)。
- `_secev_judge_tq` 的收據新舊互讀細節(只確認錯誤字串 `recorded test outcomes differ from raw report` 存在於 `scripts/test_quality.py:388`)。
- 其他棧(C#、iOS、Node、Laravel)的歸因。
- 我留在 `/var/folders/tc/xmllmxtn4q5704lsy80wc1kw0000gn/T/` 下的測試暫存:已刪一份我確認是自己建的 `gctl-run-e5fpfrm4`。我另外跑紅的幾輪是否還有別的 `gctl-run-*` 現場,我無法辨識哪個是我的,留給編排者處理。
- 我的臨時複本與探針都在 `/tmp/lumos-seat-work/code-收證認得Truth與裝置字串比較/單reviewer-sonnet/`,收貨後請編排者刪(`repo`、`a`、`b`、`m`、`probe.py`、`perf.py`、`mut.py`、`tq.orig`、`lumos.orig`)。

總結:最嚴重等級 minor,blocking 0 條
