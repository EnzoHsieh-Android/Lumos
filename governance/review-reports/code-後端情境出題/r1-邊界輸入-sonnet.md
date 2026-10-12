severity: major

我用 python3.14 載入 `scripts/lumos` 與 `qo_ablation.py` 實際餵了輸入,所有重現檔都在 `/tmp/lumos-seat-work/code-後端情境出題/邊界輸入-sonnet/`(t1 到 t8,共用 `h.py`)。

severity: major
blocking: 是
規格閘只信 `parse_pending_questions` 的精確比對,而且閘本身不跑 `pending_question_problems`。只要狀態或階段寫得差一點,標了 [阻塞] 的需求題就整題放行。實測 `[狀態：待查]`(全形冒號)得到 status=None,`[狀態:待查。]` 得到 '待查。',`[階段:需求/架構]` 得到 '需求/架構',三者都不在 `PQ_OPEN` 或 `("需求","架構")` 裡,`pending_questions_blocking_gate` 回空,閘直接過。能抓這些寫法的 lint 只在 `_lint_new_rules` 裡,不在閘的路徑上。
引句:「return [q for q in (qs or []) if q["blocking"] and q["stage"] in ("需求", "架構") and q["status"] in PQ_OPEN]」
重現:`python3.14 t3.py`,看 "fullwidth status"、"status trailing punct"、"stage combo" 三列。前兩列 `blocking=True` 但 status 不合法,第三列 status 合法但 stage 不合法,都不會被 `pending_questions_blocking_gate` 選中。

severity: major
blocking: 否
在這些輸入下,整題或整節會被靜默丟掉,閘和 lint 都不報(`parse` 回 `[]` 或 `None`,lint 見空就 `return []`):
- 清單寫成 `- [ ] [Q1]`、`1. [Q1]`、`- **[Q1]**`、`> - [Q1]`、`+ [Q1]`,或 `[Ｑ1]`。
- 標題寫成 `## 待決問題(v2)`、`### 待決問題`、`## 6. 待決問題`、`## 待決問題 ##`。
- 文件有兩節 `## 待決問題`,第二節整個被忽略。
- 節內有程式碼圍欄,圍欄裡的 `# note` 會被 `^#{1,2}\s` 當成節結束,它後面的所有題都丟掉。
- 圍欄裡的假題目行會被當真題收進來(實測 `[Q9] fake` 被收,圍欄後的 Q1 也被收,假題若帶 [阻塞] 會誤擋閘)。
引句:「_PQ_LINE_RE = re.compile(r"^\s*[-*]\s+\[Q(\d+)\]\s*(.*)$")」
引句:「if re.match(r"^#{1,2}\s", ln):」
重現:`python3.14 t3.py`,看 "checkbox"、"numbered"、"bold"、"heading level3"、"fence# comment"、"two sections"、"h2 in fence" 各列。

severity: minor
blocking: 否
題目內文含 ASCII 的「測試:」「理由:」「出處:」或「→」時,題目文字會被截斷,內文也會被當成欄位。
- `- [Q1] 單元測試:要補嗎 [類:a][階段:驗證][狀態:已驗] → #d1` 解析成 text='單元'、test='要補嗎'。
- `- [Q1] 從 A → B 的遷移 …` 的 text 變成 '從 A'。
- `[類:x]` 這類標籤出現在內文時,會被抽掉並留下空白,同一行出現兩個 [狀態:] 則後者靜默覆蓋前者(沒有重複偵測)。
- 全形冒號的「出處：…」不被認得,自答題會報「沒附出處」,訊息沒提是冒號問題。
- `出處: → #d1` 的 source 會變成 '→ #d1'(5 字),通過「至少 4 字」。
引句:「"text": re.split(r"\s*(?:→|出處:|理由:|測試:)", tail)[0].strip()})」
重現:`python3.14 t1.py`、`python3.14 t3.py`,看 "body 測試:"、"body arrow"、"body 理由:"。

severity: minor
blocking: 否
條款側和題目側的測試名正規化不對稱,照條款原樣抄會被誤報。`_pq_clause_tests` 對 `[test: py:t_x]` 存的是去前綴的 't_x',但題目側 `測試: py:t_x` 解析出 'py:t_x',於是報「不在本篇任何一條驗收條款的 [test:] 裡」。另外 `[test: kt:com.x.Foo::bar]` 只存 'bar'。題目寫 `測試:t_a,t_b`(逗號清單)整串被當一個名字,也一定報錯。
引句:「elif q["test"] not in clause_tests:」
引句:「name = part.strip().split(":")[-1].strip()」
重現:`python3.14 t1.py` 最後幾列(test='py:t_x'),`python3.14 t2.py` 最後一段(`[S1] [test: pkg:Foo:t_dd]` → {'t_dd'})。

severity: minor
blocking: 否
`_PQ_FIELD_RE` 和 `_PQ_TAG_RE` 在單行輸入上是二次方時間。一行 Q 題尾巴貼 3 萬個空白,`parse_pending_questions` 花 5.6 秒,6 萬個花 22 秒。內文貼 4 萬個沒闔上的 `[類:` 花 50 秒。規格閘、lint 和 `pitfalls --stage` 三處都會呼叫它,貼進一行長表格或壓縮內容就卡住。(`fields` 重複 2 萬次只要 0.01 秒,所以問題在空白和未闔括號。)
引句:「_PQ_FIELD_RE = re.compile(r"(出處|理由|測試):\s*(.*?)(?=\s+(?:出處|理由|測試):|$)")」
重現:`python3.14 t8.py`。

severity: minor
blocking: 否
程式裡的註解寫「要查決策或測試的檢查只放規格閘與 lint」,但規格閘的 diff 只呼叫 `pending_questions_blocking_gate`。`pending_question_problems` 只有 `_nl_rule_pending_questions` 一個呼叫端(grep 確認)。所以把 [狀態:已決] 改成沒附 `→ #dN`、或指到不存在、已作廢決策的題,規格閘照過。閘的提示文字叫人「改成已決(→ #dN 指到決策)」,但沒有任何東西檢查。⚠ 這可能是刻意設計,只是註解寫錯。
引句:「要查決策或測試的檢查只放規格閘與 lint。」
重現:`python3.14 t2.py` 證明 `_pq_decision_state` 本身對 missing 和 superseded 判得對,問題在閘不呼叫它。

severity: minor
blocking: 否
Android 專案用到自己命名的類別或通用字,就會誤觸發 `kt-springhttp` 和 `kt-springdata`。
- `class RestClient(private val api: Api)` 和 `MyRestClient()` 都亮 `kt-springhttp`(觸發詞 'RestClient')。
- `val c: DatabaseClient = get()` 和 `@Lock("x")` 亮 `kt-springdata`。
- 沒誤觸發的有 Room(@Entity、@Dao、@Query、@Transaction)、Retrofit、OkHttp、Ktor client 與 server、Compose、WebViewClient。
- 漏的有 `@get:Transactional`(use-site 寫法)、`JdbcClient`、`@HttpExchange`、`MongoTemplate`。
- `jakarta.persistence` 只在 import 那一行改到才亮,只改 @Entity 類別內部不亮。
引句:「'RestTemplate', 'WebClient', 'RestClient', '@FeignClient'」
重現:`python3.14 t4.py`。

severity: major
blocking: 是 ⚠
`code_start` 的「看不出路徑就保守算、任一路徑不是文件就算」會把純文件或唯讀指令算成先寫程式。這會直接灌高預先登記的 `code_b > code_a` 門檻。實測回 True 的有:
- 用 heredoc 寫 `docs/plan.md`,內容含 `e.g.`、`https://example.com/x`、`v1.2` 或 `src/main/OrderService.kt`(內容被當路徑 token)。
- `echo "see src/x" > docs/a.md`。
- `sed -i 's/foo/bar/' docs/x.md`(`s/foo/bar` 被當路徑)。
- `echo '== step > 1 =='`。
- `grep -rn 'a > b' docs/`。
- `tee docs/a.md < in.txt`。
- `cp src/a.kt /tmp`。
引句:「paths = _PATH_TOKEN.findall(summ or "")」
引句:「_PATH_TOKEN = re.compile(r"(?<![\w/])(?:[\w.-]+/)+[\w.-]+|[\w-]+\.\w{1,8}\b")」
重現:`python3.14 t5.py`、`python3.14 t6.py`。正確的 False 有 `git log --format='%h > %s'`、heredoc 寫 docs 且內文無點無斜線、`python -c` 唯讀。

severity: minor
blocking: 否
v2 的 `_BUILD_CMD` 只認行首或 `; & |` 之後的建置指令,第 1 版本來抓得到的真實執行會被漏掉。實測 v2 回 False(v1 為 True)的有 `FOO=1 gradle test`、`time ./gradlew test`、`sudo gradle test`、`env JAVA_HOME=x ./gradlew test`、`if true; then ./gradlew test; fi`、`bash -c './gradlew test'`、`docker run gradle:8 gradle build`。另外兩版都漏掉 `curl -o src/A.kt`、`patch -p1 < fix.diff`、`git checkout -- src/A.kt`、`dd of=src/A.kt`、`rsync`、`&> out.kt`。
引句:「_BUILD_CMD = re.compile(r"(?:^|[;&|]\s*)(?:\./)?(?:gradle|gradlew|mvn|mvnw)\b(?!\s+--version)")」
重現:`python3.14 t6.py`、`python3.14 t5.py`(看 v1 與 code_start 兩欄的差異)。

severity: minor
blocking: 否
`_is_doc` 的判斷太寬也太窄。
- 太寬:路徑裡任何一層叫 `docs`,程式碼也算文件。`src/main/kotlin/com/acme/docs/DocController.kt` 的 Edit 回 False(沒算先寫程式)。以 document 為領域的 Spring 後端很容易有 `docs` 套件,這樣會漏算。
- 太窄:大小寫敏感加副檔名只認 `.md`。`.MD`(例如 `a.MD`)、`notes.txt`、`plan.markdown`、`CHANGELOG`、`/tmp/scratch.txt` 的 Write 都算程式。
引句:「return p.endswith(".md") or "/docs/" in f"/{p}" or p.startswith("docs/")」
重現:`python3.14 t5.py` 與 `t6.py` 最後的 Write 和 Edit 列。

severity: minor
blocking: 否
`mask_leaks` 實測沒有遮到 `armor`、`firearm a`、`opuses`、`claudette`。有四個實際偏差:
- `甲乙組合` 變成 `甲⟨遮罩⟩合`,`乙組織` 變成 `⟨遮罩⟩織`(`[甲乙]組` 吃到中文詞)。
- `GPT. 下一句` 的句號被 `[\w.-]*` 一起吞掉。
- `CLAUDE_CODE`(底線是詞字元)和 `cd qo-a`(無前導斜線)不遮,是身分洩漏的漏洞。
- 英文 `can arm a trap` 這種句子會被 `arm a` 遮掉。
引句:「r"AGENTS\.md|CLAUDE\.md|/qo[/_-][ab]\b|order-svc-[ab]\b|\barm[\s_-]?[ab]\b|[甲乙]組")」
重現:`python3.14 t7.py`。

固定席影響判斷(都只看 diff,沒有跑 `lumos impact`):
- `lumos-cli-read` 的 INVARIANT 是 search 預設排除 superseded 但不排 stale,diff 沒動 search,不影響。
- `bound-tests-gate`、`design-loop`、`guard-kill`、`lumos-cli-lifecycle` 的合約都在 code-loop check、處置閘、guard kill、re-inject 上,本 diff 的新增只在待決問題的解析與檢查、`cmd_pitfalls` 的 `--stage` 分支(`stage is None` 時行為不變),不影響。
- `授權與歸屬` 的主程式檔頭 SPDX 與 MIT 全文,hunk 都在檔案中段,不影響。
- `測試假綠形態` 要求還原翻紅釘配前置斷言。本鏡頭沒有逐條檢查新增測試是否滿足,這條不能判。
- `codex-harness` 對應 `scenario_probe.py` 的 `collect_only` 放行空 `expect`。我只確認 `judge` 在空 `expect` 時 `first=len(calls)`,不會再拋 `min()` 例外,其餘沒有實測。

總結:最嚴重 major;blocking 共 2 條(其中 1 條標 ⚠)
