severity: minor

撤出本身乾淨,我沒找到斷掉的呼叫或殘骸。有兩條 minor 發現。

## 發現

severity: minor
blocking: 否
撤出留下沒人用的測試常數 `_QO_DEC`。
引句:「_QO_DEC = "decisions:\n  - content: 採用甲方案\n    id: d1\n    decided: 2026-10-12\n    valid: true」
- 位置:`scripts/test_lumos.py:56079`(b187b5e9)。
- 檢查:`git show b187b5e9:scripts/test_lumos.py | grep -n "_QO_DEC\|_qo_plan"` 只剩定義處,沒有任何引用。
- `_qo_plan` 的 `decisions` 參數也沒有呼叫端傳值,新測試只用到前兩個參數。
- 兩版對照:修前 `_QO_DEC` 被已刪的多支待決問題測試引用;修後只剩定義。
- 這段死碼不會影響行為。
- 歸因:有證據的修復回歸。撤出時漏刪。

severity: minor
blocking: 否
Kotlin 觸發詞放寬後,Android 自訂類別的帶前綴變數名也會亮 Spring 題,跟註解宣稱的不一致。
引句:「shape_only:只在真的寫到 Spring 寫法時才亮,不因行數門檻整組亮、也不進改檔前推播的整組清單(Android 專案看不到也不用答)。」
- 輸入:Android 專案裡自己寫的 `RestClient`、`WebClient` 類別,diff 只改呼叫行,例如 `val x = myRestClient.get(url)`、`apiRestClient.execute(call)`、`userDatabaseClient.update(x)`、`okWebClient.execute(req)`。
- 路徑:`scripts/lumos` 的 `kt-springhttp` 和 `kt-springdata` 的 `when` 現在是 `(?:\b|(?<=[a-z0-9]))[rR]estClient…\s*\??\.\s*(?:get|…|execute)\s*[(<]`,前綴和方法名都放行了。
- 結果:這些行會亮 Spring 外呼題或資料層題。
- 這與註解「Android 專案看不到也不用答」矛盾。
- 測試缺口:⑧ 的負例只有 `webViewClient`、`webClient.onPageFinished`、`AppWebClient()` 三種,沒有帶前綴的 Android 呼叫。
- 因此放寬到前綴,測試也不會翻紅。
- 可重現指令:`m._stack_applicability({"kt": ['val x = myRestClient.get(url)']}, 300)`。
- 兩版結果:
  - 修前(before4):`myRestClient.get(url)` 無命中,`apiRestClient.execute(call)` 無命中。
  - 修後(b187b5e9):兩行都回 `kt-springhttp`,`userDatabaseClient.update(x)` 回 `kt-springdata`。
- 影響只是多一題要答,不會擋推送。
- 歸因:有證據的修復回歸。是第 3 輪放寬(為了抓 `paymentWebClient` 這類 Spring 寫法)換來的取捨。
- 要不要接受,取決於你覺得多亮一題可不可以,但註解和測試應該跟著講清楚。
- 順帶一個漏亮:`webClient!!.get().uri("/x")` 不亮,regex 只認 `?.`,不認 `!!.`。
  - 修前也不亮,這條是原有漏查。
  - 實務上 `webClient` 通常是非空 val,我沒有給出具體失敗場景,所以只附記,不當發現。

## 回答三問

**①原問題的修復效果**
- 殘骸掃描:`git grep -E "parse_pending|pending_question|PQ_STATUSES|_pq_|_PQ_|nested="` 掃 b187b5e9 的 `scripts/`,`scripts/lumos` 與 `scripts/test_lumos.py` 都沒有任何殘留引用。
- 仍使用的名稱:`PQ_STAGES` 還在,`_pitfalls_stage` 在 `scripts/lumos:42919` 用它驗階段。
- 找節函式:`_h2_section_lines` 與合併基準 d919fadf 逐字相同。
  - 指令:`diff <(git show d919fadf:scripts/lumos | sed -n '/^def _h2_section_lines/,/^def _rollback_section_chars/p') <(git show b187b5e9:scripts/lumos | sed -n '/^def _h2_section_lines/,/^def _rollback_section_chars/p')`,輸出 SAME_AS_BASE。
  - 它已不再有 `nested` 參數,也沒有呼叫端傳 `nested=`。
- 對照實驗:
  - 工作目錄 `/tmp/lumos-seat-work/code-後端情境出題/邊界輸入-sonnet`。
  - 空檔、含「[Q1] … [阻塞]」的〈待決問題〉、帶 BOM 三種計劃,跑 `pitfalls <檔> --stage 需求` 與 `--stage 效能`,修前修後 rc 都是 0。
  - 修前輸出多一行「這一階段還沒結的待決問題(N 題…)」,修後該行消失,符合撤出意圖。
  - 修前 q.md 的需求階段共 6 行,修後 4 行。
  - 不帶 `--stage` 時兩版輸出行數都是 6,rc 都是 0。
- 測試:`python3.14 scripts/test_lumos.py -k backend_qo` 回 9 passed、0 failed;`-k kotlin_spring` 回 33 passed、0 failed。
- 新測試 `t_backend_qo_question_section_not_parsed` 和 `t_backend_qo_stage_facets_only` 的①②在檢查規格閘與 lint 輸出不含「待決問題」,是行為檢查,不是結構檢查。
- 抓錯證據(拿掉或放寬實作會不會翻紅)我沒有親手做,只看過 `r4-behavior-cases.json` 宣稱修前兩支紅,未判定。

**②修補處的正常、錯誤、相鄰呼叫路徑**
- `--stage` 的錯誤路徑和一般模式都不變:空檔、BOM、效能階段全部 rc 0。
- 錯誤階段、與 `--diff` 並用、讀不動的檔回 2,由新測試 ⑤⑥⑦ 涵蓋;我只跑了測試套件,沒另外手動重跑。
- 規格閘前段刪除後,`door = judged["door"]` 之後的流程在 diff 裡沒有改動。
- 效能:`kt-springhttp` 與 `kt-springdata` 的新 regex 在 10 萬與 100 萬字元的單行輸入下,耗時從 0.06 秒線性增加到約 1 秒。測的輸入包括全 `a`、一長串空白加 `webClient`、`webClient` 後接一長串空白、`restTemplate?` 後接一長串空白、`databaseClient` 後接一長串 `?`。沒有回溯爆炸。
- 修前 100 萬字元的完整數據我沒有跑完,只跑了 10 萬那一組作為對照。

**③同一案例在修前、修後的結果**
- 見上面兩條發現的對照,以及 `webClient!!.get()`(兩版都不亮)。
- 其餘 Kotlin 前綴案例的兩版結果:
  - `paymentWebClient`、`stockRestTemplate`、`this.restTemplate.postForLocation`、`restTemplate?.exchange`、`orderDatabaseClient.sql` 這幾條 r3 要修的案例,在修後版的測試 ⑦ 綠。
  - `$webClient.get()` 兩版都亮。
  - `webViewClient.get(x)`、`order_webClient.get()`、`WEBCLIENT.get(` 兩版都不亮,負例成立。
  - `1webClient.get(` 修前不亮、修後亮。這是數字前綴,不算實際問題。
- 沒驗到:`-k stack_question`(整組)、`-k spec_gate`、`-k pitfalls`、`-k help`、`-k command_index` 我沒跑,沿用 behavior-cases 宣稱的結果。

## 固定席節點

- 檢查範圍:bound-tests-gate、design-loop、guard-kill、lumos-cli-lifecycle、lumos-cli-read、授權與歸屬、測試假綠形態、codex-harness 這幾條帶合約的節點。
- 判定:這份 diff 都不影響,理由是這份 diff 沒碰它們的觸點。
  - 只動 `_lint_new_rules`、`_spec_gate_front`、`_pitfalls_stage`、kt 題組的 `when` 與說明文字。
  - 沒碰 guard kill 的 rc 優先序或 `--json`,沒碰 re-inject、`search` 的 superseded 濾網、授權白名單、code-loop 綁定測試的執行路徑。
- design-loop 的處置閘第五步在 `scripts/lumos` 裡,這個 diff 沒有改它。
- 測試假綠形態:新測試 ①② 檢查的是輸出行為,不是結構,這點符合「前置斷言證明現場成立」。
  - 但我沒有親手把規格閘改回讀正文去驗證它會翻紅,這部分未判定。

總結:最嚴重 minor;blocking 共 0 條。
