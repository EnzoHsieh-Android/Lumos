severity: minor

## 結論

這一輪的五項修補,我沒找到會擋推送的問題。我只找到一條新的 minor,是修補範圍旁邊原本就有的漏洞。

## Finding

severity: minor
blocking: 否
歸因:有證據的原有漏查(修前修後同樣失敗,不是這輪修補造成的)

引句:「樣式補上三引號那段(同剝字串掃描的寫法),5 處一起生效」

- **位置:** file: `scripts/lumos:49067`(`_TG_CONST_PAT`,三引號補丁沒涵蓋到)。這個樣式只認單行字串,而它是 `_TG_LIT_PAT` 的同族,用來判斷常值斷言(`_tg_const_stmt`)。
- **會出錯的輸入:** 把測試裡的 `assertEquals(1, f())` 換成 `assertEquals("""a""", """a""")`。`_tg_const_stmt` 走到 `fullmatch(_TG_CONST_PAT)`,三引號字串不被認成常值,回 False。
- **相鄰比較:** 同一個改法換成 `assertEquals("a", "a")` 或 `assertEquals(1, 1)`,會被列 `tq/assert-weakened`。
- **為什麼只標 minor:** 這個檢查本來就是啟發式的,三引號常值斷言又少見,所以我只標 minor。
- **修前修後都一樣:** `_tg_const_stmt('assertEquals("""x""", """x""")')` 在 374e7751 和 04de0941 都回 False。
- **管線實測:** 用 `_tqg_rules` 跑 `assertEquals(1, f())` 換成各種常值,結果如下。

  | 換成 | 結果 |
  |---|---|
  | `assertEquals("a", "a")` | 列 `tq/assert-weakened` |
  | `assertEquals(1, 1)` | 列 `tq/assert-weakened` |
  | `assertEquals("""a""", """a""")` | 空清單(沒列) |

## 修復驗收

**① 原問題的修復效果**

- **三引號樣式(`_TG_LIT_PAT`):** `assertTrue("""\n assertEquals x\n """, f())` 的字串被清空,不再算強斷言(修前不清空)。
  - 單行字串、字元常值、空字串、跳脫引號、`""""a"` 和未收尾的三引號,兩版輸出一致。
  - 效能:1e6 個引號、1e6 組 `"""a"` 和 1e6 組 `"""x"""` 都在 0.1 秒內,沒有二次方退化。
  - 三引號訊息參數現在能被正確認成訊息:JUnit 的 `assertEquals("""msg\nline""", 1, f())` 取到預期值 1。修前把它當成容差,誤取 `"""msg\nline"""|delta=f()`。
- **共用掃描迴圈(`_tg_ident` 的 fold 參數):** 我用 60000 組隨機組合(引號、註解、空白、反斜線)比對 `_tg_ident` 和 `_tg_ws_keep_strings` 的新舊輸出,差異為 0。預設行為和其他呼叫端沒有變。
- **擋下訊息的兩條路:** 我在 `_mp_repo` 情境(多平台改單平台)照訊息實際走了一遍。
  - **實作未綠:** 重跑規格閘會寫新留痕,訊息說得對。
  - **實作已綠:** 重跑回 rc0「不用重跑」,留痕數不變,和訊息「重跑不會寫新留痕」一致。
  - **換回空殼補跑:** 把 `green_fee_jvm` 標記拿掉再跑規格閘,留痕變 2 筆、`tests=['fee_jvm']`,補回標記後推送前 rc0。
  - **`plan_risk: high`:** 推送被擋,改走設計審,這是既有出口。
  - 擋下訊息約 400 字,完整印出,沒有被截。

**② 修補處的正常、錯誤與相鄰呼叫路徑**

- **新增的三個測試案例:** `-k tq_guard_string` 29 項全過,`-k spec_gate_record_keeps` 13 項全過。
- **改壞驗證:** r4-fix-mutation.md 的 R1–R4 都各自翻紅。
- **覆蓋缺口(minor,不單獨列為 finding):** 三引號樣式的改壞驗證 R2 只由「強斷言」那一個案例抓到。另外四處(容差、訊息參數、恆真條件、方向互換)沒有獨立案例,但五處共用同一個樣式,這是單一故障點,所以風險低。
- **trimIndent 已知多報:** 我實測整段重新縮排會列一條 `tq/expected-changed`,是多報、不漏擋,和計劃寫的一致。

**③ 新發現的修前修後結果**

- **三引號常值斷言漏判:** 修前和修後都回 False,管線都不列(見上面的 finding)。
- **其餘行為差異:** 上面比較出的差異都只出現在三引號字串,方向正確。

**圖譜鏡頭:** 我沒發現這份 diff 破壞固定席節點宣稱的行為或合約。diff 動到的是 `test-guard` 和規格閘的內部行為。`Systems/規格閘.md` 的 WHY 說「照擋並講明設定改了」,和新訊息一致。其他固定席的 INVARIANT(search、guard kill、reinject、還原翻紅釘、處置閘第五步)和這些函式無交集。

**未驗範圍:**
- 沒跑全套測試。
- 沒跑 `lumos lint` 和 `lumos doctor`(repo 只讀)。
- 沒實測 Java text block 的 `\"""` 跳脫,三引號掃描和 `_C_STRIP_PAT` 的行為一致,只有未收尾的三引號會不同:`_C_STRIP_PAT` 讀到結尾,`_TG_LIT_PAT` 要求收尾,而斷言片段已配平括號,實務上幾乎碰不到。

暫存:我只刪了自己測試失敗留下的兩個 `gctl-run-*`。`/tmp/lumos-seat-work/code-紅燈版實跑三缺口/單reviewer-sonnet/` 留給編排者收貨後刪。
