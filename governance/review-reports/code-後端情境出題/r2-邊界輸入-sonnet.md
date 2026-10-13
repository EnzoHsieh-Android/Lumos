severity: major

審查範圍是甲區的待決問題解析、規格閘擋法、`pitfalls --stage` 和 Kotlin Spring 觸發詞。我在 `/tmp/lumos-seat-work/code-後端情境出題/邊界輸入-sonnet/` 把修前(c960f6de)和修後(112ad15f)的 `scripts/lumos` 各取出一份,用同一批輸入跑解析函式和 CLI 對照。

repo 裡 `python3.14 scripts/test_lumos.py -k backend_qo` 是 57 項全過,`-k kotlin_spring` 是 20 項全過。下面的洞都不在這些測試覆蓋內。

## Finding 1:Kotlin Spring 觸發詞收太窄,常見的小寫變數呼叫不再亮題
severity: major
blocking: 是
歸因:有證據的修復回歸

- 引句:「(?-i:\\bRestTemplate\\b)', '(?-i:\\bWebClient\\b)'」
- file: `scripts/lumos:26766`
- 修補把 `RestTemplate`、`WebClient`、`RestClient`、`DatabaseClient` 改成區分大小寫,還要求 `RestClient.create` 這類呼叫形狀。
- 結果是 diff 只動呼叫行、宣告不在 diff 裡時(最常見的情形),`kt-springhttp` 和 `kt-springdata` 都不亮。
- 重現:在 `/tmp/lumos-seat-work/code-後端情境出題/邊界輸入-sonnet/` 執行 `python3.14 k.py before/lumos` 和 `python3.14 k.py after/lumos`,內容是 `_stack_applicability({"kt":[行]}, 300)`。
- 修前和修後對同一行的結果:

| 輸入行 | 修前 | 修後 |
|---|---|---|
| `val r = restTemplate.exchange(url, HttpMethod.POST, entity, String::class.java)` | kt-springhttp | 不亮 |
| `return webClient.post().uri("/pay").bodyValue(req).retrieve().bodyToMono<Res>()` | kt-springhttp | 不亮 |
| `val res = restClient.get().uri("/x").retrieve().body<String>()` | kt-springhttp | 不亮 |
| `val rows = databaseClient.sql("select * from t").fetch().all()` | kt-springdata | 不亮 |

- 這是用精準度換召回:修後確實擋掉了 `AppWebClient`、`MyWebClient` 這類 Android 自訂類名的誤亮,但連 Spring 呼叫行本身也一起丟了。
- 測試 ② 只靠同一份輸入裡的 `RestTemplate()` 那行才過;`webClient.get()` 那行在修後單獨看是不亮的。測試 ⑥ 只覆蓋大寫型別和 `.create`、`.builder` 寫法。
- 建議把變數名形狀也收進來,例如 `\b(?:rest|web)Client\.(get|post|put|delete|exchange)`,Android 的 `webView.webViewClient` 仍然排除。

## Finding 2:新增的「像題目」判斷 regex 對長空白行是二次方時間
severity: minor
blocking: 否
歸因:有證據的修復回歸

- 引句:「_PQ_LOOKS_RE = re.compile(r"^[\s>*+\-\d.、)）|\[\]xX]*\s*[QＱ]\s*\d」
- file: `scripts/lumos:6921`
- 節內一行只有 N 個空白加一個 `y`(或純空白行),`_PQ_LINE_RE` 不符,就會走到這支 regex。`[\s…]*` 吃光後再回退,每退一格 `\s*` 再試一次,整體 O(N²)。
- 實測 CLI:

| N | `spec-gate --no-run`(修前) | `spec-gate --no-run`(修後) | `pitfalls --stage` 需求(修後) |
|---|---|---|---|
| 20000 | 1.0s | 2.7s | 2.5s |
| 40000 | 0.6s | 8.4s | 8.3s |

- 直接呼叫解析函式,N=80000 要 30.7 秒。
- 測試 ⑮ 的長行都是 `- [Q1]` 開頭的行,不經過這支 regex,所以沒測到。
- 建議去掉 `[\s…]*\s*` 的重疊,改成 `[\s…]*` 後直接接 `[QＱ]`。

## Finding 3:節內漏關的圍欄會把阻塞題藏起來,規格閘放行
severity: minor
blocking: 否
歸因:有證據的修復回歸(修前這個輸入會擋,修後放行)

- 引句:「哪些行看得見走 _visible_lines(全檔唯一的圍欄判定);節結束=同級或更淺的下一個標題。」
- file: `scripts/lumos:4898`(`_visible_lines`),`scripts/lumos:6928`(`_pq_sections`)
- 輸入:`## 待決問題`,下面一行 ``` 但忘了關,再接 `- [Q1] … [階段:需求][狀態:待人][阻塞]`。
- 修前 `python3.14 lumos spec-gate Projects/c_計劃 --no-run` 是 rc=1,列出 Q1。
- 修後是 rc=0,Q1 看不見;`lint` 的輸出也沒有任何提示。
- 原因:`_visible_lines` 把漏關的圍欄之後整段當程式碼。這和條款側的行為一致,但跟這次修補宣稱的「寧可擋」方向相反。
- 建議:節內圍欄沒關時,至少讓 lint 報一條。

## Finding 4:阻塞標記或節標題寫差一點,閘和 lint 都靜默放行
severity: minor
blocking: 否
歸因:有證據的原有漏查(修前修後同樣放行)

- 引句:「_PQ_TAG_RE = re.compile(r"\[(類|階段|狀態)\s*[:：]([^\[\]\n]*)\]|\[(阻塞|不可逆)\]")」
- file: `scripts/lumos:6922`
- 阻塞標記只認完全相同的 `[阻塞]`。`[阻塞 ]`、`[阻塞:是]`、`【阻塞】` 都被當成非阻塞,題目照常解析成功,所以 `_PQ_LOOKS_RE` 的「看不懂」也不觸發。
- 節標題只認 ATX 標題:`**待決問題**` 或 `待決問題` 加底線這種寫法,`parse_pending_questions` 回 None,整節的題都不被看。
- 重現:這四種輸入(`[阻塞 ]`、`[阻塞:是]`、`【阻塞】`、`**待決問題**`)跑 `spec-gate --no-run`,修前修後都是 rc=0,`lint` 沒有 `待決` 相關訊息。`pitfalls --stage 需求` 對 `[阻塞 ]` 和 `[阻塞:是]` 兩個寫法,仍把題列出來但不標「阻塞」。
- 建議:節內出現 `[阻塞…` 開頭但不是精確 `[阻塞]` 的標記時,算「看不懂」。節外出現 `- [Q<n>]` 行時,至少讓 lint 提醒。

## Finding 5:同一行重複寫了階段或狀態,閘用最後一個,lint 才報
severity: minor
blocking: 否
歸因:有證據的原有漏查(修後 lint 會報 `dup_tags`,但閘仍放行)

- 引句:「tags[t.group(1)] = t.group(2).strip()」
- file: `scripts/lumos:6960`
- `[階段:需求][階段:實作][狀態:待人][阻塞]` 這一行 `spec-gate --no-run` 是 rc=0。
- `[狀態:待人][狀態:已決][阻塞]` 這一行也是 rc=0。
- 修前修後相同。修後 lint 新增「重複寫了兩次」的報告,但沒進 `pending_questions_blocking_gate`。
- 同一個修補已把「標阻塞卻寫錯狀態或階段」納入擋下,這裡也該一併納入。

## 三問的答案

1. **原問題修復效果**
   - 解析函式的輸入對照:`- Q2`、`1.`、`> `、`Q 全形`、`(Q1)`、`Q1) `、`| [Q1] |` 這幾種看不懂的題目行,修前回 `[]`,修後都留成 `bad` 項並擋規格閘。
   - 標題變體:`(v2)`、`（v2）`、`:` 結尾修前是 None,修後都認得。
   - 全形冒號、空 `[狀態:]` 標記:修前不擋,修後擋。
   - 沒闔上的標記造成的長行卡頓:修前 `"[阻塞]"*50000` 要 15.5 秒,修後 0.02 秒。
   - 讀不動的計劃(非 UTF-8):`_pitfalls_stage` 回 2,訊息帶「擋下:」。
2. **修補處的相鄰路徑**
   - 這些路徑維持正確:正常的 `- [Q1]` 解析、`spec-gate` 擋阻塞待查或待人題、`pitfalls --stage` 排序。
   - 這幾項還沒查:CRLF、BOM、tab 縮排、`Q１` 全形數字,解析結果修前修後相同。
   - 有回歸或漏查的路徑:上面 Finding 1、2、3。
3. **同一案例兩版結果**:都附在各 Finding 裡。這些案例我是直接對 CLI 跑修前修後兩版,不是只讀 diff。

未驗範圍:`Q` 編號超過 4300 位數時 `int()` 丟 ValueError(修前修後都有,情境過於人造所以沒列);乙區的計分器和探針完全沒碰;固定席的各個合約節點沒有逐條判讀,這次改動動到 `scripts/lumos` 和 `scripts/test_lumos.py`,但我只驗了待決問題、規格閘和 Kotlin 觸發詞這幾條路徑,其餘合約是否被牽動沒有證據,記為未判定。

總結:最嚴重 major;blocking 共 1 條。
