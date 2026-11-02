severity: major

# Android單元測試標準實機演練 r1 設計審(正確性席,sonnet)

總覽:我逐條對過程式。`assertion_failure` 的改動沒有把「不是斷言失敗的失敗」認成斷言失敗;新增的放行面也只在計劃寫明的範圍。只有第 1 條是實際會出事的缺陷,是新加的正規式在不可信輸入上會卡死。其餘是計劃跟程式現況對不齊的地方。

有實際核對的項目:
- 三份指紋 sha256 與 `scripts/test_quality.py` 實算值一致(`a0995951…`)。
- 計劃交叉引用的三個節點存在。
- S5 列的七支測試在 `scripts/test_test_quality_cli.py` 都存在,數量對得上。
- 舊的原生消費者與三平台卷證裡所有 capture 三件組,在新版工具下重算 `fault_check` 仍是 detected,沒有舊收據因本次改動被拒。

## 各節

### 問題與最小解、名詞
已讀,只有第 6 條一處措辭不精確。其餘宣稱經核對都與程式一致:
- 現況一段:舊報告在時 `capture` 於跑之前拒絕且不產生收據,零選中時 `capture` 於讀報告時判 invalid,`--target` 擋包裝案例。
- 配套指紋表載入時逐檔比對。
- 收據不記工具版本,重算不同時回 `recorded test outcomes differ from raw report`,錯誤碼是 `receipt_hash_mismatch`。

### 做法 1–6
已讀,無 finding。

### 做法 7(收證工具修補)
有 finding,見第 1、2、3、5 條。

### 驗收條款
有 finding,見第 4 條。

### 回退
已讀,無 finding。還原後舊工具重算會得到 `receipt_hash_mismatch`,與計劃寫的「回到判無效、要重收」一致。

### 實務隱患
有 finding,見第 1 條。

### 審計修正紀錄
已讀,無 finding。

## Findings

**1. 裝置那路新加的 `Caused by` 切分正規式在大量換行輸入上是二次方,安全證據閘的時間預算擋不住**

severity: major
blocking: 是(同一個不可信報告能讓推送前閘或 `capture`/`check` 卡數分鐘到數十分鐘,而且一行修法就能解)

引句:「效能:考場一次本機測試約一兩分鐘、一次儀器測試含安裝約數分鐘;故障證明每個錯要跑三次。」

file: `scripts/test_quality.py:134` 是 `own = re.split(r'\n\s*Caused by:', text, maxsplit=1)[0]`。

重現:
- 做一份 JUnit XML,`<failure>` 不帶 `type` 屬性,內容是 `java.lang.AssertionError: x` 後面接 N 個連續換行,再接任意字。
- 因為 `\s` 也吃換行,每個 `\n` 起點都會掃完整段空白才失敗。
- 實測用 `junit()` 解析:N=10000 約 0.17 秒,N=20000 約 0.67 秒,N=40000 約 2.66 秒。單獨量這條正規式,N=100000 要 16.6 秒。
- 照二次方外推,1MB 的換行約 28 分鐘。報告上限是 `_SECEV_FILE_MAX` 16MB,不是 1MB,實際上限更高。
- 這條正規式在 `if not kind` 分支裡無條件先算,連第一行根本不是兩型別的文字也會算。舊版只有 `startswith` 加一次線性 `search`,沒有這個成本。

影響:
- `junit()` 被 `capture`、`load_receipt_data`、安全證據閘的 JUnit 宣告路都呼叫。
- 閘的 60 秒預算(`_SECEV_BUDGET_SEC`)只在 git 呼叫之間用 `_SecevTimeout` 協作式檢查(`scripts/lumos:9658`、`9666`)。單次正規式跑起來不會被打斷,所以不會變成 `evaluation_timeout`,pre-push 直接卡住。
- 計劃的實務隱患只談測試耗時,沒談對不可信報告的效能;全域規則也要求修補後對大輸入跑效能檢查。

修法方向:`\s*` 改成 `[ \t]*`,或逐行掃到第一個 `Caused by:` 行。我試過 `\n[ \t]*Caused by:`,N=100000 只要 0.001 秒。

**2. 裝置規則的「Assert 堆疊只算 `Caused by` 之前」計劃沒寫,而且會讓舊收據被拒**

severity: minor
blocking: 否(寧可拒收的方向,不會放行錯的證據;只是計劃的描述比程式寬)

引句:「改成同一條規則:第一行剛好是這兩個型別之一(可接冒號加訊息),而且要有 JUnit `Assert` 的堆疊。」

file: `scripts/test_quality.py:133-135`。

差異:
- 程式要求 Assert 堆疊落在 `own`(第一個 `Caused by:` 之前)。舊版是整段文字任何位置有就算。
- 標準(`skills/lumos-project-notes/commands/test-quality-standard.md`)、驗證紀錄和 `Systems/test-quality-cli` 的 PITFALL 都寫了「Caused by 之前」。計劃的做法 7 與 S5 都沒有,S5 的反例清單也沒有「Assert 堆疊只在 Caused by 之後」這一項,雖然測試 `test_device_runtime_around_comparison_failure_is_not_attributed` 的最後一組樣本在釘它。
- 這是 True 變 False 的收窄。舊工具認過、堆疊只在 `Caused by` 之後的裝置故障收據,新版重算會得到 `receipt_hash_mismatch`。
- 計劃講「換版後舊收據被拒」時,舉例只談 Truth 型別(False 變 True)。回退一節也沒提這個方向。

**3. `Suppressed:` 段的 Assert 堆疊仍被算進去,計劃沒寫**

severity: minor
blocking: 否(要第一行就是 `java.lang.AssertionError` 才成立,情境窄;驗證紀錄已承認「Suppressed 段落沒切,照舊」,計劃本體卻沒有)

引句:「反例測試釘住沒型別欄的 Truth、`Expect` 規則的型別、訊息提到型別名、Caused by 包著、型別名後面多字這幾種不放行。」

重現:
- 無型別的 `<failure>` 文字:第一行 `java.lang.AssertionError: unexpected call in fake`,接一行 `\tat com.example.Fake.add(Fake.kt:9)`。
- 再接 `\tSuppressed: java.lang.IllegalStateException: late` 與 `\t\tat org.junit.Assert.fail(Assert.java:86)`。
- `junit()` 對它回傳 `assertion_failure=True`。
- `own` 只切 `Caused by`,同一份堆疊追蹤裡另一種附屬段(Suppressed)沒切,「只看自己的堆疊」這條界線有洞。
- 計劃的守衛面一段列了「放行面」的反例,這一項不在其中,也沒有反例測試。

**4. 計劃宣稱的行為變更,有一半沒有測試釘住;七支測試的綁定也釘不住「七支都在」**

severity: minor
blocking: 否(宣稱本身經程式核對是對的:JUnit 宣告路確實從 invalid 變成 failed:assertion_failed,兩者都不放行;缺的是回歸守衛)

引句:「JUnit 宣告那條從「無效:不是斷言失敗」變成「失敗:斷言失敗」,兩者都不放行。」

file: `scripts/test_lumos.py:114399` 的 `t_secev_fault_truth_assertion_counts_like_assertion` 只走 `fault_sensitivity` 路。

差異:
- `failure_truth` 這個測試輔助型別只被 fault 路的測試用到(`scripts/test_lumos.py:113856`、`113974`),`_secev_junit_declared`(`scripts/lumos:8846`)沒有任何用 Truth 型別的測試。
- 回退時 JUnit 宣告路的行為變化就沒有守衛會跟著紅。
- S5 綁 `t_test_quality_cli`(`scripts/test_lumos.py:106792`)只檢查整份測試檔的退出碼,條款寫「七支」。刪掉或改名其中任何一支,這個綁定仍然綠。

**5. 「當掉」的防線靠例外型別,這次放寬後,假實作用 Truth 的斷言丟的例外會被算成抓到錯**

severity: minor
blocking: 否(同一個缺口對 `Assert.fail`、本機的 `AssertionError` 早就存在,這次只是擴大到 Truth;⚠ 沒有找到把它變成誤放行的專案內樣本,是從判定函式的結構推出來的)

引句:「測試因為丟了不是斷言的例外而紅,例如假實作(記憶體裡的假資料來源)遇到沒排好的呼叫就丟例外;收證不把這種紅算成抓到錯。」

file: `scripts/test_quality.py:115-118` 與 `434-435`。

情境:
- 假實作在遇到沒排好的呼叫時,用 Truth 的 `assertThat(...)` 或 `assertWithMessage(...).fail()` 自我檢查,丟出 `AssertionErrorWithFacts`。
- 該測試在故障版因此紅,型別名單現在認它,`fault_check` 判 detected,安全證據閘的 `fault_sensitivity` 也合格。
- `fault_check` 只看型別、不看誰丟的,所以名詞定義的承諾(假實作丟的例外不算抓到錯)在這種寫法下不成立。
- 計劃的守衛面一段只談「型別名單多認兩個」,沒把這種情境列為放行面的已知邊界。

**6. 名詞「判無效」裡 `check` 回拒收碼的說法不精確**

severity: minor
blocking: 否(措辭差異,不影響判定)

引句:「`check` 回拒收碼(例如目標測試的失敗不是斷言失敗)」

file: `scripts/test_quality.py:469-471`。

差異:
- `check` 遇到 `ReceiptRejected` 時,被 `dispatch` 的 `except ValueError` 接住,印的是 `{'verdict':'not_assessed','complete':False,'reason':<訊息>}`,退出碼 2,沒有印原因碼。
- 原因碼(`nonassertion_failure` 等)只有安全證據閘用 `e.code` 讀得到。
- 計劃把它跟閘記成「invalid:…」的說法放在同一句,容易讓人以為 CLI 也輸出碼。

## 實務隱患鏡頭

- **守衛面(誤放行)**:無新的誤放行。
  - 本機路的 Truth 精確型別比對和 `Truth$SimpleAssertionError` 排除經反例確認。
  - 裝置路第一行完全比對加 Assert 堆疊,我試了前導空白、CRLF、`assertThrows` 包裝、訊息裡有 `Caused by`,沒有得到誤認。
  - 邊界情境見第 3、5 條。
- **效能與資源**:有,見第 1 條。
- **併發 / 版本不同步**:無。
  - 指紋表與檔案一致,載入走已驗位元組。
  - 消費專案副本沒更新時,指紋對不上,`test-quality` 與閘回「部署不完整,請 lumos update」,拒跑而不是誤判。計劃已寫這個窗口。
- **金流、對外送出、不可逆**:無。計劃已排除,而且改動只在判定函式和測試,不碰網路與資料。
- **舊證據相容**:無。已用重算確認現有 Android、C#、iOS、Laravel、Node 的 capture 三件組在新版下仍是 detected。

## 固定席節點(`Systems/test-quality-cli`)

- 該節點 0 條合約。
- 判定:不影響,理由是既有 PITFALL「原生 reporter 抹掉型別」是本次改動的同族,新增的 PITFALL 與計劃做法一致。
- 該節點的新 PITFALL 已寫「Caused by 之前」,但計劃本體沒有,見第 2 條。

總結:最嚴重等級 major,blocking 1 條
