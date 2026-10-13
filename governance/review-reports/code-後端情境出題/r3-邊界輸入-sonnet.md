severity: minor

審查範圍:修補差異 112ad15f → 46bc93c3(主程式待決問題解析與規格閘、Kotlin 觸發詞、計分器、探針與對應測試和筆記)。我把修前樹和修後樹各匯出一份,放在 `/tmp/lumos-seat-work/code-後端情境出題/邊界輸入-sonnet/{before,after}`,用 `python3.14` 載入 `scripts/lumos` 直接呼叫 `parse_pending_questions` 和 `pending_questions_blocking_gate`。重現腳本都在同目錄(`probe*.py`)。找到 3 條 minor,都是修補新增的「寧可擋」造成的誤擋,不是漏擋。

**finding 1:節外、寫法像題目的普通文字,會讓沒有〈待決問題〉的計劃被規格閘擋下**

severity: minor
blocking: 否

歸因:有證據的修復回歸(修前無此行為)。

引句:「題目定義的形狀:Q<n> 開頭、後面帶標記」

file: `scripts/lumos:6919`(`_PQ_DEF_RE`;標記關鍵字後不要求冒號)
file: `scripts/lumos:7942`(規格閘對每份計劃都跑解析)

- 輸入:`# 計劃\n\n## 時程\n- Q4 上線 [階段一:灰度]\n- Q1 回顧 [狀態更新]\n`。這份計劃沒有〈待決問題〉節。
  - 修前:`parse_pending_questions` 回 None,閘門 0 題。
  - 修後:回 2 筆「像題目,但解析讀不到它」,閘門 2 題,規格閘回 1。
- 同類輸入也中:`Q3 [階段性交付]`、`- [ ] Q1 通過 [類別A]`。
- 這違反 `Systems/規格閘.md` 寫的「沒有〈待決問題〉一節的計劃判定與輸出不變」。
- 範圍:掃描本 repo 870 篇筆記,修後 0 篇誤中,所以目前沒有現存受害者,只是形狀上會發生。
- 最小重現(在 `after/` 目錄):`python3.14 probe2.py $PWD/after` 看「roadmap Q4 階段」那行。
- 兩版對照:修前 `GATE 0`,修後 `GATE 2`。

**finding 2:節內以 `#` 開頭但不是標題的行,會提早結束〈待決問題〉節**

severity: minor
blocking: 否

歸因:有證據的修復回歸(修前正則要求 `#` 後接空白,只有真標題才切節)。

引句:「lv = len(ln) - len(ln.lstrip("#"))」

file: `scripts/lumos:7187`(`_h2_section_lines` 在 `nested=True` 時,任何 `#` 開頭的行都算標題)

- 輸入:`## 待決問題\n- [Q1] a [類:需求][階段:實作][狀態:已決] → #d1\n#d1 見決策\n- [Q2] b [類:需求][階段:實作][狀態:已決] → #d1\n`。`#d1` 是這套筆記慣用的決策指標。
  - 修前:Q1、Q2 都讀到,閘門 0 題。
  - 修後:Q2 掉出節外,被當成「讀不到」的看不懂行,閘門 1 題,規格閘回 1;`pitfalls --stage` 也列不到 Q2。
- 一個合法的問題被誤擋,而且訊息把原因指向「標題寫法」,會誤導使用者。
- 最小重現:`python3.14 probe3.py $PWD/after` 的「hash-line mid-section」那行。
- 修前輸出 `[('Q1', None), ('Q2', None)] 0`,修後輸出 `[(None,'第 4 行像題目…'), ('Q1', None)] 1`。

**finding 3:題目文字或連結裡剛好含「[阻塞…]」「[不可逆…]」的字樣,整題被當成看不懂**

severity: minor
blocking: 否

歸因:有證據的修復回歸(修前這些輸入都正常解析、閘門 0)。

引句:「_PQ_FLAG_LOOSE_RE = re.compile(r"[\[【](阻塞|不可逆)[^\]】\n]{0,20}[\]】]")」

file: `scripts/lumos:6920`(比對範圍是整行 `rest`,連題目內文和欄位值都掃)

- 輸入 A:`- [Q1] 是否 [阻塞性能] 問題 [類:需求][階段:實作][狀態:待人]`。
- 輸入 B:`... [狀態:自答] 出處:[[阻塞策略]]`。內層的 `[阻塞策略]` 被比到,而 `[[阻塞處理]]#d1` 這種寫法不被比到,因為 `[[` 後直接是節點名。
  - 修前:題目正常解析,閘門 0 題。
  - 修後:整題變成「旗標寫法看不懂」(輸入 B 的訊息是 `[阻塞策略]——只認 [阻塞]、[不可逆]`),閘門 1 題。
- 這是 fail-closed 的取捨,但訊息指向使用者沒寫的「旗標」,且只能靠改字繞過。
- 最小重現:`python3.14 probe.py` 和 `probe2.py`,各看「text mentions…」和「link ref bare node」那幾行。

**三問的回答**

1. 原問題的修復效果(repair)
   - 圍欄沒關、中文編號標題、粗體標題、寫在節外的題目行:修後都變成「看不懂」並擋下。
     - 修前:`tilde fence unclosed at tail inside section` 回 `[]`、閘門 0。
     - 修後:同一輸入回 1 筆 bad、閘門 1。
   - 阻塞旗標變體:`[阻塞 ]` 在修前是 `GATE 0`,修後是 `GATE 1`。
   - 標了阻塞又重複寫狀態或階段:修後閘門擋下。
   - 變異驗證(在修後匯出的整樹 `full/` 上):
     - 拿掉 `or q["dup_tags"]`,`t_backend_qo_unreadable_questions_fail_closed` 紅 2 條。
     - 把 `_PQ_FLAG_LOOSE_RE` 的過濾改成 `if False`,紅 3 條。
     - 拿掉計分器 `_valid` 的 calls 型別檢查,`t_qo_ablation_scorer_suite` 紅,但這條沒有確認是否因其他原因本來就紅,所以只當作「有紅」、不當作有效的抓錯證據。
   - 效能(修後,`perf.py`):
     - 20 萬行文字 0.16 秒。
     - 5 萬題 0.33 秒。
     - 100 萬字元單行、30 萬個 `[ `、50 萬組 `1 ` 都不到 0.05 秒。
     - 沒有回溯問題。

2. 修補處的正常、錯誤與相鄰路徑
   - 合文法的題、關好的圍欄範例、CRLF、全形標記、`[[Systems/阻塞處理]]#d1` 連結:修前修後結果相同。
     - 關好的圍欄範例:兩版皆不算,回 None、閘門 0。
     - CRLF:兩版皆讀到 Q1 並照舊擋下。
   - 共用的找節函式 `_h2_section_lines` 在 `nested=False` 的分支沒動,回退節與實務隱患節沿用。
   - `-k backend_qo` 72 passed(修後樹);`-k kotlin_spring` 28 passed。
   - Kotlin 新觸發詞:`webView.webViewClient = …`、`val webClient = AppWebClient()` 不亮,這部分成立。
     - 未驗範圍:自訂的 Android `restClient.get(` 呼叫會亮 `kt-springhttp`,我沒找到具體失敗場景,所以不報。
   - 計分器:
     - 壞檔(`null`、`[]`、calls 為 null)列為無效場:我只讀了程式與測試,沒另外執行。
     - 重產盲評包只清 `packet-*.json`:`--dest` 與 `adjudication-packet.json` 不在同一目錄,不會誤刪。
     - `calls` 裡的非清單元素會被默默丟掉,影響「先寫程式」的機械計分,但實驗已跑完且人工核對過,我沒標它。

3. 新發現案例在修前、修後各是什麼
   - 見各 finding:三條在修前都是 `GATE 0`、正常解析,修後都變成誤擋。
   - 未判定:我沒有重跑完整規格閘命令列,只呼叫解析與閘門函式。端到端是否同樣回 1,依 `_spec_gate_front` 的程式推得是,但沒有實測。
   - 未驗:全套測試與 `-k door`、`-k rollback`。
   - 圖譜鏡頭沒有固定席節點,不逐條判。

總結:最嚴重 minor;blocking 共 0 條。
