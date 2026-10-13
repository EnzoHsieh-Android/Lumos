severity: clean

這輪我沒找到會擋推送的問題。我在 `b187b5e9` 的工作目錄和修前副本各跑了一遍;修前副本是 `/tmp/lumos-seat-work/code-後端情境出題/正確性-sonnet/b4`,測試檔換成修後版。

## 三問的回答

**① 原問題的修復效果**(repair)
- 修的是「〈待決問題〉正文解析整塊撤出」。撤出後 `scripts/lumos` 和 `scripts/test_lumos.py` 裡 `parse_pending_questions`、`pending_question*`、`_pq_*`、`_PQ_*`、`_nl_rule_pending_questions` 都沒有殘留或斷掉的呼叫。我用 `git grep -nE` 在 `b187b5e9` 的 `scripts/` 下查過。
- 剩下的 `PQ_STAGES`(`scripts/lumos:6902`、`:42919`)和 `_h2_section_lines`(`:6978`)都還有人用。`nested=` 參數也已一併拿掉,另兩個呼叫端(`:6997`、`:7101`)沒傳它。
- 同一個測試在兩版的結果不同:
  - 修前副本(`b4`)執行 `python3.14 scripts/test_lumos.py -k backend_qo`:5 過 4 敗。
    - `t_backend_qo_question_section_not_parsed` 的 ①②:規格閘仍印出「待決問題 ✗」,lint 仍報。
    - `t_backend_qo_stage_facets_only` 的 ②③:仍列出 Q1,JSON 仍帶 `questions` 和 `unreadable`。
  - 修後工作目錄同一指令:9 過 0 敗。
  - 所以新測試能抓到「又去讀正文」,不是照實作重寫一遍。
- 文件和程式對得上:
  - `Systems/情境出題.md`、`Systems/規格閘.md`、`Systems/pitfalls-code-loop.md`、skills 的 `SKILL.md` 和 `reference.md`、`HELP_WHEN` 的 `spec-gate` 與 `pitfalls`、`--stage` 的 help,都改成「工具不讀」。
  - `lumos lint "Projects/後端工程提問與證據擴充_計劃"` 結果是 0 問題。
  - `lumos spec-trace` 的 S1、S3、S4 綁到的是新測試名,7 條款懸空 0。
  - 舊的七支測試名在 `b187b5e9` 的非卷證檔案裡都沒有殘留。

**② 修補處的正常、錯誤與相鄰路徑**(preserve)
- 正常路徑:
  - `-k spec_gate` 修後 107 過 0 敗。
  - `-k stack_questions_kotlin` 修後 33 過 0 敗。
- 錯誤路徑:`pitfalls --stage` 在階段寫錯、與 `--diff` 並用、非 UTF-8 檔三種情況都回 2(`t_backend_qo_stage_facets_only` 的 ⑤⑥⑦ 修後綠)。
- 不帶 `--stage` 時,有沒有〈待決問題〉一節輸出一字不差(同一測試的 ④ 修後綠)。
- Kotlin 觸發詞放寬:
  - 修前副本 `-k stack_questions_kotlin` 跑 5 條新 ⑦ 斷言,全部敗,例如 `paymentWebClient.get()...`、`restTemplate?.exchange(...)`、`orderDatabaseClient.sql(...)`。修後全綠。
  - 我另外用自己的探針(`/tmp/lumos-seat-work/code-後端情境出題/正確性-sonnet/probe.py`)測 `webViewClient.get(` 和 `private val RestTemplate_x = 1`,兩版都沒亮,Android 誤觸發的對照組仍成立。

**③ 新發現的案例在兩版的結果**
- 無 blocking 級別的新案例。

## 低嚴重度觀察(不列為 finding,沒有造成實際失敗)
- `restTemplate!!.exchange(...)`(Kotlin 的 `!!.`)修前修後都不亮,放寬只加了 `?.`。
- `val x = AppWebClient.get().uri("/x")` 修前不亮,修後亮 `kt-springhttp`。放寬後「小寫字母或數字緊接 `WebClient`」就算命中。Android 專案若有叫 `XxxWebClient` 且有 `.get(` 的自訂類別會誤亮。測試 ⑧ 沒涵蓋這種寫法,我也沒找到實際例子,所以不標嚴重度。

## 固定席節點
- `bound-tests-gate`、`design-loop`、`guard-kill`、`lumos-cli-lifecycle`、`lumos-cli-read`、`授權與歸屬`、`測試假綠形態`:這次改動沒有碰它們 KEY 行所綁的行為。改動只動了待決問題解析、`pitfalls --stage` 和 Kotlin 觸發詞。
- `design-loop`:它的處置閘條款(計劃 `[SN]` 綁測試)沒動,`-k spec_gate` 107 條全綠。

## 角色鏡頭
- be-api-compat:`pitfalls --stage --json` 的輸出少了 `questions` 和 `unreadable` 兩個鍵。我只在 `scripts/lumos` 和 `scripts/test_lumos.py` 裡查過,沒有其他讀者,新測試已釘 `{"stage","facets"}`;repo 其他地方和外部消費者我沒查。
- be-authz:本次沒有新增或改動需要授權檢查的端點,不適用。

## 未驗範圍
- 我沒查 `r4-behavior-cases.json` 逐案的歸因。
- 我沒查 `scripts/scenario_probe.py` 和計分器,那是乙區。
- 我沒跑全套測試。

總結:最嚴重 clean;blocking 共 0 條。
