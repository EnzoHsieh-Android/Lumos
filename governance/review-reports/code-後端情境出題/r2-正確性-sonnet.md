severity: major

審查範圍是甲區(待決問題解析、規格閘擋法、`pitfalls --stage`、Kotlin Spring 題組觸發詞)。我讀完了 `r2-甲-full.patch` 和 `r2-甲-repair.patch`。修前是 `c960f6de`(複本在 scratchpad 的 `before/`),修後是 `112ad15f`。實驗都在 `/tmp/lumos-seat-work/code-後端情境出題/正確性-sonnet/` 下,用 `git archive` 取檔和 `git clone --shared` 建複本,沒動原 repo。

## Findings

**1. 規格閘:沒關的程式碼圍欄會讓阻塞題整個消失,閘門放行(修補引入)**

severity: major
blocking: 是

歸因:有證據的修復回歸。

引句:「哪些行看得見走 _visible_lines(全檔唯一的圍欄判定);節結束=同級或更淺的下一個標題。」

- **輸入:** 計劃筆記裡 `## 待決問題` 底下有一個 ``` 圍欄,打開後忘了關,後面接著 `- [Q1] … [階段:需求][狀態:待人][阻塞]`。
- **原因:** 修補把 `parse_pending_questions` 改成走 `_pq_sections`,再經 `_visible_lines` 取行。沒關的圍欄會把後面所有行都藏起來,Q1 就讀不到。
- **後果:** 如果圍欄開在 `## 待決問題` 標題之前,`parse_pending_questions` 直接回 `None`,規格閘照樣放行,也沒有任何警告。
- **對照:** 修前逐行讀原文,這種筆記會被擋。
- **最小重現:** 筆記內容是 `---\ntype: project\nstatus: doing\n---\n# p\n\n## 待決問題\n\n```\n範例寫到一半忘了關\n- [Q1] 訂單成功的定義 [類:需求][階段:需求][狀態:待人][阻塞]\n\n## 回退\n\n退回上一版。`。
- **命令:** `bash e2e.sh <lumos路徑>`,內容是建臨時 git repo,在 `docs/x-knowledge` 下跑 `python3.14 <lumos> spec-gate Projects/p_計劃 --no-run`。
- **修前** `before/lumos`:輸出「待決問題: ✗ — 1 題標阻塞…」,`rc=1`。
- **修後** `after/scripts/lumos`:沒有待決問題那一段,只印「條款綁定: —」,`rc=0`。
- **探針比對:** 用 `p2.py` 對兩版同一份筆記做 `parse_pending_questions`。
  - 圍欄開在節內:修前回 `[Q1]`,閘擋;修後回 `[]`,閘不擋。
  - 圍欄開在標題前:修前回 `[Q1]`;修後回 `None`。
- **為什麼算 blocker 級的退步:** 這次修補的主旨就是「寧可擋」,但漏掉的恰好是最常見的手誤。現有 57 條測試沒有一條涵蓋沒關的圍欄,所以全綠。
- **修法方向:** 圍欄收尾還開著時,直接當「看不懂」擋下,或這一節改讀原文。

**2. Kotlin 題組:小寫變數的呼叫行不再亮 kt-springhttp(修補引入,漏亮)**

severity: minor
blocking: 否

歸因:有證據的修復回歸。

引句:「撞 Android 自訂類名的字用 (?-i:…) 局部分大小寫並加字詞邊界,或只認 Spring 專屬的呼叫形狀」

- **輸入:** 一個只改呼叫行的 diff,例如 `webClient.get().uri("/stock").retrieve()`、`restTemplate.getForObject(url, String::class.java)`、`restClient.post().uri("/pay")`。
- **原因:** `(?-i:\bWebClient\b)`、`(?-i:\bRestTemplate\b)` 把小寫開頭的變數名排除了。`\b` 夾在字母之間不成立,所以 `webClient`、`restTemplate` 不會被匹配。
- **對照(`p3.py` 逐行跑 `_stack_applicability`):**
  - 修前:這三行都回 `['kt-springhttp']`。
  - 修後:這三行都回 `[]`。
- **相鄰路徑:** 宣告行 `class Foo(private val restTemplate: RestTemplate)` 與 `RestClient.create()` 兩版都亮。
- **測試被遮住:** 測試 ② 有兩行輸入,第一行 `val body = webClient.get()…` 其實已經不亮了,全靠第二行 `RestTemplate()` 才綠。這條測試沒能驗到它想驗的呼叫行。
- **影響範圍:** 只影響這個建議性的提問,沒有資料受損。

**3. 題目行把標記寫在問題文字前面時,題目文字變空字串(修補引入,顯示退步)**

severity: minor
blocking: 否

歸因:有證據的修復回歸。

引句:「題目文字只取第一個方括號標記之前;連結與欄位只在標記之後找(題目內文的「測試:」「→」不當欄位)。」

- **輸入:** `- [Q1] [類:需求][階段:需求][狀態:待人][阻塞] 訂單怎麼算`。
- **對照:**
  - 修前 `text='訂單怎麼算'`。
  - 修後 `text=''`。
- **後果:** 規格閘輸出「• [Q1] (第 N 行,狀態 待人)」,`pitfalls --stage` 也列「[Q1] 」,都沒有題目內容。閘仍然擋,lint 也沒有提醒題目文字缺失。
- **性質:** 這個寫法不在文法範圍內,只是顯示上的退步。

**4. 阻塞標記寫成變體時,閘靜默放行(原有漏查)**

severity: minor
blocking: 否

歸因:有證據的原有漏查。

引句:「規格閘只看狀態:標阻塞的需求/架構題沒結、標阻塞卻寫錯狀態或階段、看不懂的題目行,一律擋(寧可擋;代碼審 r1 邊界席、合約圖譜席)。」

- **輸入:** `[ 阻塞 ]`、`[阻塞:是]`、`[blocking]`。
- **走到哪:** `_PQ_TAG_RE` 只認精確的 `[阻塞]` 和 `[不可逆]`,其餘方括號整段忽略,`blocking=False`。
- **對照:** 兩版都是 `gate []`,規格閘不擋,lint 也不報。
- **與修補的關係:** 這跟修補的「寧可擋」不一致,但不是這次修補造成的。

## 三問

**① 原問題的修復效果:**
- 看不懂的題目行改成留下並擋閘。例如 `1. [Q1]`、`- Q2`、`> - [Q5]`、`[Ｑ7]`、表格行,修後都回 `bad` 並讓閘擋下;修前這些行被靜默丟掉。
- 標阻塞卻寫錯狀態或階段,修後閘會擋。例如 `[狀態:待查。]`、`[階段:需求/架構]`。
- 標題變體(`待決問題:`、`(v2)`、編號、層級)修後認得,「待決問題清單」不誤認。
- `pitfalls --stage` 的非 UTF-8 讀檔回 rc 2。
- 全形冒號、多測試名、測試名句尾標點、長行效能(兩秒內解完)都有測試。
- `python3.14 scripts/test_lumos.py -k backend_qo` 在修後是 57 passed、0 failed。
- 我做了 3 個變異實驗,每個都讓對應測試翻紅,測試有抓錯力:
  - 閘不擋「標阻塞但狀態或階段認不得」→ `t_backend_qo_gate_fail_closed` 與 `t_backend_qo_parser_robust` 翻紅,共 3 條失敗。
  - `已驗` 的多個測試名不逐個檢查 → `t_backend_qo_question_line_shape` 翻紅,2 條失敗。
  - 拿掉「阻塞卻延後」檢查 → `t_backend_qo_question_line_shape` 翻紅,1 條失敗。
- 第 4 個變異(`pending_questions_for_stage` 不排除 `bad`)沒套上,等價於無變異,未驗。
- 修復效果成立,但被 finding 1 局部抵銷。

**② 修補處的正常、錯誤與相鄰路徑:**
- 正常路徑仍成立:合法阻塞題、已決題、跨篇決策連結、CRLF、tab 縮排、全形冒號、前置 frontmatter 都正常。
- `bad` 行不混進 `--stage` 清單,而是另列「⚠ 像題目但看不懂」,不影響退出碼。
- 錯誤路徑有兩個破口:finding 1 的圍欄和 finding 3 的標記在前。
- 相鄰路徑裡,`_nl_rule_pending_questions` 改用 `env_text` 沒問題。它回 `None` 時 `parse_pending_questions` 會回 `None`,lint 不會崩。

**③ 同一案例兩版結果:** 上列每條都附修前與修後的對照,沒有「只見修後失敗」的結論。

## 其餘鏡頭

**圖譜固定席:** 判不影響。
- 這份 diff 沒碰 `search` 的過濾、`re-inject`、`guard kill` 的 rc 優先序、授權檔白名單、`bound-tests` 的執行流程。
- 新測試是加在 `test_lumos.py` 與 `test_autonomous_loop.py` 的新函式,沒改既有被綁測試。
- 新增的 `--stage` 旗標沒有動 `lumos pitfalls` 在不帶 `--stage` 時的輸出;測試 ⑤ 比對有沒有〈待決問題〉一節的輸出一字不差。

**角色卡:**
- be-api-compat:`pitfalls --stage --json` 新增 `unreadable` 鍵,題目物件的 `test` 欄位改成 `tests` 清單,並多了 `bad`、`dup_tags`。我在 repo 內 grep 找不到其他讀這些欄位的程式,沒有發現舊消費端會壞。repo 外的消費端未查。
- be-authz:這份 diff 沒有新增或改動端點,不適用。

**未驗範圍:**
- 超過 4300 位數的題號 `[Q…]` 會讓 `int()` 拋 ValueError。這在修前就存在,屬於荒謬輸入,沒標成 finding。
- `~~~` 圍欄、`\u2028` 換行造成的行號偏差,兩版行為相同,沒報。
- `lumos lint` 在圍欄沒關時是否另有警告,沒查。
- `r2-manifest.json` 是 0 條 claims,我沒另外依它導向。

總結:最嚴重 major;blocking 共 1 條。
