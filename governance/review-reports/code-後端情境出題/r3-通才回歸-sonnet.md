severity: major

審查範圍:修前 `112ad15f` 到修後 `46bc93c3` 的差異(`r3-repair-review.patch`)。我只讀了本輪的 r3- 材料,沒讀 r1、r2 的檔。修前、修後各自 clone 到 `/tmp/lumos-seat-work/code-後端情境出題/通才回歸-sonnet/{before,after}`,探針腳本放在同目錄的 `probe*.py`,沒動 repo 根。解析函式用 `python3.14 probeN.py <目錄>` 在兩邊各跑一次,退出碼都是 0。

白話說明:這輪的修補把「讀不到的題目行一律擋」做出來了,新增的測試也抓得到錯。但「怎麼認出像題目的行」那條新正規式,在題目節以外遇到特定長行會卡數十秒,修前不會。另外兩種阻塞旗標寫法和圍欄寫法仍然漏網。

## Findings

severity: major
blocking: 是
標題:`_PQ_DEF_RE` 掃全檔每一行,「Q 加數字後面接一長串空白或數字」會 O(n²),修前沒有。
引句:「P("## 待決問題\n" + " " * 60000 + "x\n")」
歸因:有證據的修復回歸。
- 走到哪:`parse_pending_questions` 呼叫 `_pq_unreachable`,對每個不在節內的行跑 `_PQ_DEF_RE.match`。在 `Q\s*\d+\s*\]?.*?[\[【]...` 這段,`\d+`、`\s*` 與 `.*?` 互相回溯,一行就是 O(n²)。
- 輸入:`"# p\n" + "Q1" + " "*N + "x"`(節外),以及 `"- Q" + "1"*N + "x"`。
- 兩版對照,工作目錄為各自 clone,指令是 `python3.14 probe2.py $PWD/after` 與 `$PWD/before`:

| 輸入 | N | 修後 | 修前 |
|---|---|---|---|
| `Q1` + 空白 | 20000 | 1.78 秒 | 0.0 秒 |
| `Q1` + 空白 | 60000 | 16.24 秒 | 0.0 秒 |
| `-Q` + 數字 | 20000 | 1.75 秒 | 0.0 秒 |
| `-Q` + 數字 | 60000 | 15.91 秒 | 0.0 秒 |

- 為什麼測試沒抓到:新測試 ⑦ 只測沒有 `Q` 開頭的六萬空白行,而且放在節內。節內的行不會進 `_PQ_DEF_RE`,所以這個測試對本次新增的路徑沒有約束力。
- 影響:`parse_pending_questions` 在 `scripts/lumos:6852`、`:7942`(規格閘)、`:43118` 被呼叫。任何筆記只要有一行這種長行,規格閘就卡 16 秒以上。
- 現實性:要有人寫出數萬字元的 Q 開頭空白或數字行,不常見,但這正是上一輪「六萬空白 17.3 秒」同一類問題換了形狀。
- 最小重現已附(上面兩條輸入)。

severity: major
blocking: 是
標題:阻塞旗標的全形括號 `［阻塞］` 和中間夾空白的 `[阻 塞]` 仍判成「沒標阻塞」,規格閘放行。
引句:「_PQ_FLAG_LOOSE_RE = re.compile(r"[\[【]\s*(阻塞|不可逆)」
歸因:有證據的原有漏查。修前同樣放行,修補只補了 `[阻塞 ]`、`[ 阻塞]`、`【阻塞】` 這幾種,同一類換形狀的漏洞還在。
- 輸入:`## 待決問題\n- [Q1] a [類:需求][階段:需求][狀態:待人]［阻塞］`,另一條把 `［阻塞］` 換成 `[阻 塞]`。
- 走到哪:`_pq_parse_line` 先看寬鬆旗標正規式,它只認半形 `[` 或 `【` 開頭;`_PQ_TAG_RE` 也不認這兩種寫法,所以 `blocking=False`。這題沒有 bad,也不被規格閘持有。
- 結果:

| 版本 | 輸入 | 解析結果 | 規格閘 |
|---|---|---|---|
| 修後 | `［阻塞］` | `('Q1', bad=False, blocking=False)` | 放行 |
| 修後 | `[阻 塞]` | `('Q1', bad=False, blocking=False)` | 放行 |
| 修前 | 兩者 | 同上 | 放行 |

- 對照:`[ 阻塞]`、`[ 不可逆]`、`[阻塞 ]`、`【 阻塞】` 在修後都變成 bad 並被擋,修前全部放行。這是本輪真正修好的部分。
- 影響:作者想擋的需求或架構題,只要旗標打成全形,規格閘不會擋。這和修補自己宣稱的「寧可擋」不一致。
- 最小重現已附(指令 `python3.14 probe1.py $PWD/after`)。

severity: minor
blocking: 否
標題:「圍欄沒關」的偵測只看最後一行長不長得像圍欄標記,圍欄種類或長度不合時會誤判成已關。
引句:「unclosed = tail < len(lines) and not re.match(r"^\s*(```|~~~)", last)」
歸因:有證據的原有漏查。修前同樣讀不到,這個檢查是本輪新增,但漏洞形狀在修前就存在。
- 輸入一:`## 待決問題\n````\n- [Q1] ... [阻塞]\n```` ——開了四個反引號、最後一行只有三個,實際沒關。
- 輸入二:`## 待決問題\n```\n- [Q1] ...[阻塞]\n~~~` ——反引號圍欄、結尾是波浪線,也沒關。
- 結果:兩者修後都是 `parsed=[]`、`gate=False`,阻塞題被藏起來。修前同樣 `parsed=[]`。
- 對照:最後一行不是圍欄標記的未關圍欄,修後變成 bad 並被擋,修前 `parsed=[]`,這部分有修好。
- 最小重現已附。

severity: minor
blocking: 否
標題:Kotlin 只改呼叫行時,變數名帶前綴或呼叫方法不在清單內就不亮題。
引句:「小寫變數名只認 Spring 用戶端的請求方法」
歸因:有證據的原有漏查。
- 修後(修前一律不亮):`webClient.get().uri(...)` 這種正好叫 `webClient` 的會亮 `kt-springhttp`。
- 修後仍不亮的輸入(兩版都不亮):
  - `val r = paymentWebClient.get().uri("/x").retrieve()`
  - `stockRestTemplate.exchange(url, HttpMethod.GET, null, String::class.java)`
  - `this.restTemplate.postForLocation(url, body)`
  - `orderDatabaseClient.sql("select 1").fetch().all()`
- 原因:`\b` 前置加上方法清單沒有 `postForLocation`、`headForHeaders`。
- 這是啟發式觸發詞的覆蓋缺口,不是回歸。

## 三問

**①原問題的修復效果**

我在修後 clone 逐支真跑,全綠:

| 指令 | 修前(材料宣稱,我沒重跑) | 修後 |
|---|---|---|
| `test_lumos.py -k backend_qo` | 57 | 72 passed |
| `-k stack_questions_kotlin` | 未提供 | 28 passed |
| `test_autonomous_loop.py TestQoAblation TestScenarioProbeAblation` | 未提供 | 66 tests OK |

我用突變測試驗證新測試抓得到錯。每一刀我都在修後 clone 的暫存副本上做,清掉 `__pycache__` 後跑:

| 突變 | 結果 |
|---|---|
| 拿掉 `q["dup_tags"]` | 2 條紅 |
| 寬鬆旗標檢查改成 `if False` | 3 條紅 |
| 外層看門 `lost = []` | 7 條紅 |
| 題目文字回補改成永遠空字串 | 1 條紅 |
| 拿掉新增的 Kotlin 呼叫行觸發詞 | 4 條紅 |
| 拿掉重產時清舊包 | 1 條紅 |
| 遮罩改回舊例外 | 1 條紅 |
| Codex 路徑不傳 `**extra` | 1 條紅 |
| 拿掉 `calls` 結構檢查 | 1 條紅 |

我另外在當前節點跑了 912 份 `docs/**/*.md`,外層看門沒有誤報任何既有筆記;只有本計劃自己有題目,規格閘 0 條持有。

**②修補處的正常、錯誤與相鄰呼叫路徑**

- 正常路徑:精確 `[阻塞]` 與一般合文法題,兩版解析與規格閘結果相同。
- 共用找節函式 `_h2_section_lines` 的既有呼叫端行為不變:`-k spec_gate` 115 passed、`-k rollback` 5 passed、`-k door` 15 passed。
- 錯誤路徑:上面兩條 major 是修補沒蓋住或新引入的錯誤路徑。
- 相鄰:`packet-*.json` 清除的 glob 與 `cmd_adj` 讀取 glob 一致,不會誤刪仲裁包。這部分已驗。
- `_result_row` 壞檔結構(`null`、`[]`、`results:[1]`、`calls:null`)我只靠既有測試和突變間接驗,沒另補案例。

**③新發現同一案例的兩版結果**

| 案例 | 修前 | 修後 |
|---|---|---|
| 節外 `Q1` 加六萬空白 | 0.0 秒 | 16.24 秒 |
| `［阻塞］` | 放行 | 放行 |
| `[阻 塞]` | 放行 | 放行 |
| 四個反引號開、三個結尾 | 讀不到 | 讀不到 |
| 反引號開、波浪線結尾 | 讀不到 | 讀不到 |
| `paymentWebClient.get()` | 不亮 | 不亮 |
| `webClient.get()` | 不亮 | 亮 |

**未驗範圍**
- 計分器人工重算 `rating/`、`rating-mini/` 逐位元相同的宣稱,我沒重算。
- 文件組(家筆記、預先登記補註)的「場次 72 更正為 54」只看了 patch 內容,沒逐篇對照。
- 全套 `test_lumos.py` 沒跑,依專案規定留給推送前的閘。

總結:最嚴重 major;blocking 共 2 條。
