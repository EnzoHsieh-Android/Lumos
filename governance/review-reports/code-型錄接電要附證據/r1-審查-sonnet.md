severity: major

審查範圍:code patch 完整讀過,catalog patch 讀了〈接電證據〉節、〈輸入與口徑〉、〈統計〉與 49 列被改的通電批次。`python3.14 scripts/test_lumos.py -k kt_catalog` 全綠(186 passed)。改壞實驗放在 `git archive` 出來的副本 `/tmp/lumos-seat-work/code-型錄接電要附證據/審查-sonnet/repo`,repo 本身沒動,臨時目錄留著。

## Findings

### 1. 新判定表有 5 條檢查分支,拿掉任一條測試都照綠

`_wiring_entry_problems` 與 `_wiring_source_problems` 的下列分支,改壞後 `-k kt_catalog` 仍是 186 passed。我在副本逐一做了改壞實驗,全都綠:

- **〔查證〕出處的理由前綴**:把 `return [] if why.startswith(_WIRING_NO_BUILD) else [...]` 改成 `return []`。
- **擋不到要寫理由**:把 `elif not why.strip():` 改成 `elif False:`。
- **欄位數 7**:把 `if len(c) != _WIRING_COLS:` 改成 `if False:`。
- **判定值只准「擋得到」「擋不到」**:去掉 `verdict not in _WIRING_VERDICTS`。真型錄實測,UI-54 的判定寫成「隨便」時,只有等級那一條規則會報。
- **候選要(標籤,檢查)成對**:改成只比檢查碼,也是綠。

為什麼會漏:

- 計劃 S4 寫了「出處是〔查證〕的每筆理由 應 以『樣本編不過』開頭」,並綁在 `t_kt_catalog_batch4_evidence`。但真型錄 210 筆全是〔真跑〕,測試也沒造過一筆〔查證〕,所以這條綁定沒有任何斷言。
- S2 寫了「固定值以外的值」,測試只驗了等級,沒驗判定值。

為什麼標 major:被保護的是守衛本身,依派工詞判準抓不到錯就是 major。

最小重現(副本內):

```
sed 的等價改動:把 return [] if why.startswith(_WIRING_NO_BUILD) else [...] 換成 return []
python3.14 scripts/test_lumos.py -k kt_catalog  →  186 passed, 0 failed
```

file: `configs/ast-grep/kotlin-android/check.py:447`、`configs/ast-grep/kotlin-android/check.py:427`、`scripts/test_lumos.py:129128`

引句:「    if _VERIFIED_RE.fullmatch(src.strip()):」

severity: major
blocking: 是

### 2. 通電批次的批四標籤只認「告警帶寫法=」之後,舊守衛沒有這個盲區

`_batch4_have` 從「告警帶寫法=」開始往後找第一個批四括號。舊的 `_batch4_problems` 是在整格通電批次裡找標籤。兩個漏洞,我都用真型錄 UI-54 實測:

- **批四寫在「告警帶寫法=」之前的子段,不會被點到。** 把 UI-54 的通電批次改成 `行為測試或正向約束=批四(CI 範本:Android Lint);告警帶寫法=未接(x)`,`wiring_problems` 回 `[]`。UI-54 的 Android Lint 判定是擋不到,這個宣稱會擋的標記因此放行。
- **同一格有兩個批四括號,只看第一個。** 多出的那個不受檢。

真型錄現在沒有這種寫法(掃過所有列,沒有「批四在告警帶寫法前」、「整格沒有告警帶寫法卻有批四」、「多個批四」的列),所以是守衛的洞,不是現存資料錯。計劃寫的是「其餘子段不管」,這是設計的取捨,但測試沒釘住,型錄也沒寫「批四只准出現在告警帶寫法值裡」。

為什麼標 minor:現有資料乾淨,只是守衛比舊版窄,要有人改型錄寫出新格式才會漏。

file: `configs/ast-grep/kotlin-android/check.py:387`

引句:「    m = _BATCH4_RE.search(batch, i) if i >= 0 else None」

severity: minor
blocking: 否

### 3. 〈天花板〉留著「(實作後補)」的空白承諾,現況其實是 0 筆

計劃〈天花板〉寫「樣本編不過的候選退回讀官方頁判……清單與筆數寫在這裡(實作後補)」。實作後 210 筆全是〔真跑〕,〔查證〕為 0 筆,這句沒更新。照做的人會去找一份不存在的清單。這也和 finding 1 呼應:〔查證〕分支在真資料裡沒有任何一筆。

為什麼標 minor:措辭精度,不會讓人做錯事。

引句:「- 樣本編不過的候選退回讀官方頁判,準確率沒有真跑那麼高;清單與筆數寫在這裡(實作後補)。」

severity: minor
blocking: 否

## 查證結果(沒有 finding 的部分)

### 鏡頭 1 正確性

- **`batch4_expected_tags` 與 `batch4_candidates`**:對真型錄全部 168 列,兩者結果一致,沒有行為變化。
- **`_batch4_have` 對各種寫法**:
  - `批一、批四(L)` 不帶「告警帶寫法=」,回 None。
  - `批四(L;C)` 與帶空白的 `批四( L ; C )` 都解出兩個標籤。
  - 順序反過來或寫成「批四(現成規則)」,會因為 `have != want` 被點到,訊息是「要寫沒有批四」,這是合理的。
- **`_section`**:`_abbr_table` 從 `i+5` 改成 `i+1` 在行為上等價。起點字元是 `\n#`,`\n## ` 不可能在 `i+1` 開頭命中,所以節尾位置不變。`_pending_table` 的節尾現在是新的〈接電證據〉節,正確。
- **`_batch4_problems` 的呼叫端**:在 scripts/、configs/、skills/、docs 裡 grep,沒有任何遺留呼叫端或測試。`kotlin規則包.md` 裡舊 WHY 已標 superseded。
- **〈統計〉「接電證據 N 筆」**:改成 211 會被 `stats_problems` 抓到(`〈統計〉接電證據 寫 211,重數是 210`)。這條有守住。

### 鏡頭 2 型錄改動

抽查官方頁 https://googlesamples.github.io/android-custom-lint-rules/checks/<Id>.md.html,下列列的理由站得住:

- **ARCH-25 UseGetLayoutInflater**:官方範例是 DialogFragment。理由「只在 DialogFragment 檢查」與頁面一致。
- **ARCH-47 WifiManagerLeak**:官方頁寫「Android N(24)之前」。理由「minSdk < 24 才報」一致。
- **UI-92 ConflictingOnColor**:官方 Vendor 是 Jetpack Compose,Identifier 是 androidx.compose.material,對應 M2 的 `ColorsDetector`。樣本用 M3 沒報,合理。
- **DATA-32 WorkerHasAPublicModifier**:官方範例是 `private class`,型錄壞例是 `internal`。理由「不看 internal」合理。
- **DATA-78 SerializableUsage**:官方 Vendor 是 slack-lint,不是 Slack compose-lints。「範本版本沒有這條」合理。
- **TEST-10 TestLifecycleOwnerInCoroutine**:官方範例必須在 `runTest {}` 裡,樣本放 main 而且用 `runBlocking`,不報合理。
- **PERF-18 UseSparseArrays**:官方範例是 `SparseArray<Integer>`,與理由方向不矛盾。
- **ARCH-28 ValidFragment**:官方描述針對平台 `android.app.Fragment`,理由一致。

有疑慮但沒到可標的一組:

- **DATA-29 InvalidPeriodicWorkRequestInterval**:官方範例是 `PeriodicWorkRequest.Builder(TestWorker::class.java, 15L, TimeUnit.MILLISECONDS)`。型錄樣本用 ktx 的 `PeriodicWorkRequestBuilder<W>(5, TimeUnit.MINUTES)`,旁證改的也是 MINUTES 單位的建構子寫法,沒有用官方範例的 MILLISECONDS 試一次。
- **DATA-33 SpecifyForegroundServiceType**:官方範例是 `ForegroundInfo(0, notification, 1)` 帶明確型別。型錄壞例是沒帶型別的寫法,樣本也沒試官方形式。
- 這兩列都是往少宣稱的方向錯,風險低。不過旁證沒有驗到官方範例形式,「擋不到」的信心比理由欄寫的低一點。

另外三點:

- **ARCH-85**:壞寫法欄是 `android.…` 和 `hidden…` 的佔位寫法,「擋不到」是樣本寫不出真的隱藏 API 名的結果,不代表檢查擋不到。
- **「未接(登記的現成檢查擋不到這列壞寫法,見〈接電證據〉)」**:和型錄既有的「未接(規則在 rules-unwired/:型錄這列出處不全)」「未接(儀器批)」形式一致。〈輸入與口徑〉有交代「告警帶寫法因此變空時寫『未接』」。
- **「實跑命中」殘句**:只有 API-9 留了,而且已經改寫成「照這列壞寫法真跑沒報」。

### 鏡頭 3 測試

測試的改壞覆蓋(UI-24 的 6 種改壞、重複、環境行、樣本檔名與缺檔、等級矛盾)抓得住。這些改壞我也在副本做過:刪重複檢查、刪等級矛盾檢查都會翻紅。缺口見 finding 1。

### 鏡頭 4 與角色卡

- **併發**:依派工詞不考慮。
- **be-api-compat 與 be-authz**:這個變更沒有對外 API、端點或授權面,只改型錄文字、自檢腳本與測試,兩題不適用。
- **圖譜鏡頭**:這次沒附固定席節點,依派工詞不逐條答。

最高等級 major;blocking 1 條
