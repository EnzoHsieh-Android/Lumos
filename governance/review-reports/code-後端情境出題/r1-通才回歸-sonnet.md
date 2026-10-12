severity: major

我在 `/tmp/lumos-seat-work/code-後端情境出題/通才回歸-sonnet/repo` 的副本裡做了破壞測試,沒有動 repo。每次只改一處,跑相關測試,再還原。既有行為大致不變,但新測試有明顯漏洞。

**既有行為不變的核對結果**
- 沒有〈待決問題〉一節的計劃,規格閘與 lint 沒有變。`parse_pending_questions` 沒這一節會回 None,閘的判斷式也只吃 `(qs or [])`。repo 裡有這節標題的三篇(後端工程提問與證據擴充、情境出題、規格閘)lint 都是 0 問題。
- `pitfalls` 不帶 `--stage` 沒有變。我用 d919fadf 與 c960f6de 各跑一次同一份含〈待決問題〉的計劃,輸出逐字相同。
- 探針多出的 `answer_len` 欄位沒有影響既有讀結果的程式。`ablation_lumos_first.py` 只驗它認得的欄位型別,不拒絕多出來的欄位。`historical_handbook_trial.py` 只讀 `answer`。預設上限仍是 1500。
- `judge` 在 expect 為空時原本會對空集合拋例外,而舊的 `_validate_scenario` 本來就擋掉空 expect,所以這條路不是既有行為。
- 既有測試的期望值:kt 整組維持 7 題,meta 8 改 10,id 集合加兩題。我跑了 `-k stack_question`(88 支)、`-k pitfalls`(142 支)、`-k spec_gate`(113 支)、`-k backend_qo`、`TestScenarioProbeAblation`、`TestQoAblation`,全部通過。這些改動是對的,沒有放掉原本要守的東西。
- 固定席節點:
  - 授權與歸屬:不影響。`governance/eval/` 既有檔本來就沒有 SPDX,`-k license` 11 支全過。
  - design-loop 處置閘:不影響。這次只加規格閘前段的擋法,沒碰審材格式判斷。
  - bound-tests-gate、guard-kill、lumos-cli-read、lumos-cli-lifecycle:不影響。diff 沒碰它們宣稱的行為。
  - 測試假綠形態:這次的新測試違反它的精神,見下面各條。

severity: major
blocking: 否
`qo_ablation.py` 的 `_summarize`、`cmd_final`、`cmd_agree` 一支測試都沒有。把配對差的方向 `xb-xa` 改成 `xa-xb`,18 支 `TestQoAblation` 全綠。把 noise 或 code 累加到錯的組,也全綠。主指標方向反了,PASS 和 FAIL 會對調,測試看不出來。
引句:「diffs.append(sum(xb) / len(xb) - sum(xa) / len(xa)); complete.append(sid)」
重現:用 python 替換該行後跑 `python3.14 scripts/test_autonomous_loop.py TestQoAblation`,輸出 `Ran 18 tests ... OK`。

severity: major
blocking: 否
規格閘的新測試只抓得到「全擋」或「全放」,抓不到擋的條件被放寬。把閘裡的 `q["blocking"] and` 拿掉,變成沒標 `[阻塞]` 的待人題也擋,`-k backend_qo` 仍是 22 passed。把階段限制從「需求/架構」縮成只有「需求」,也全綠。跨筆記決策連結 `[[x]]#dN` 一律當成本篇,也全綠。測試只用了標阻塞的題,從沒放過一題沒標阻塞的需求階段待人題,階段也只用過需求與效能。
引句:「return [q for q in (qs or []) if q["blocking"] and q["stage"] in ("需求", "架構") and q["status"] in PQ_OPEN]」
重現:替換後跑 `python3.14 scripts/test_lumos.py -k backend_qo`,輸出 `22 passed, 0 failed`。

severity: minor
blocking: 否
盲評的測試守不住盲評本身。拿掉 `rnd.shuffle(order)` 全綠,代價是盲評編號 R001… 會照 key 排序,甲乙組一眼看得出來。測試只驗了同種子同結果,沒驗順序被打亂。把遮罩正規式裡的 `order-svc-[ab]`、`arm` 和「甲乙組」整段拿掉,也全綠,因為測試只用了 Codex、Claude、AGENTS.md、`/qo/b/`、GPT 這幾個詞。
引句:「rnd.shuffle(order)」
重現:兩個破壞各跑一次 `TestQoAblation`,都是 OK。

severity: minor
blocking: 否
`kappa` 與 `delivery_rate` 的期望值太退化。kappa 只測了「完全一致得 1」與「對半分得 0」。把實作換成 `2*po-1`(兩個案例下數值與正確公式相同)仍全綠。`delivery_rate` 把 absent 也算進交付也全綠,因為測試完全沒放 absent。kappa 是無效判定的門檻(< 0.6),交付率是主指標。
引句:「return 1.0 if pe == 1 else (po - pe) / (1 - pe)」
重現:替換 `kappa` 回傳為 `2*po-1`,`TestQoAblation` 為 OK。

severity: minor
blocking: 否
兩題新 kt 題因為比對不分大小寫(re.I),在 Android 專案會誤亮。`class AppWebClient : WebViewClient()` 或自訂的 `RestClient` 就會亮 `kt-springhttp`。測試 ③ 只放了 Room 與 Retrofit,沒涵蓋這類常見命名。另外,把 `kt-springhttp` 的觸發詞縮成只剩 `RestTemplate`,`-k stack_questions_kotlin` 仍全綠,所以八個觸發詞裡只有一個被驗到。
引句:「"when": ['RestTemplate', 'WebClient', 'RestClient', '@FeignClient'」
重現:
- 用 `m._stack_applicability({"kt":['class AppWebClient : WebViewClient() {']},300)`,結果 `['kt-springhttp']`。
- 用 `['class RestClient(private val api: Api) {', ...]`,結果含 `kt-springhttp`。

severity: minor
blocking: 否
⚠ 「不帶 `--stage` 輸出逐位元不變」這條,測試 ⑤ 比的是兩次都在新版跑的輸出,不是和舊版比。我用 base 與 head 手動比對確實相同,所以現況沒問題,但這條斷言抓不到「不帶 `--stage` 也多印一行」。這點我只是推論,沒跑破壞。
引句:「check("⑤ 不帶 --stage 時輸出不變(不出現待決問題清單)", plain_before.stdout == plain_after.stdout」

severity: minor
blocking: 否
`效能檢核目錄.md` 的第 201 行還寫「全表 kt=8」。加兩題後實際是 10,測試裡的 meta 數字已經改成 10。這行自己註明「這串數字每次加棧都要跟著改」。這是筆記漂移,不影響行為。
file: `docs/lumos-toolchain-knowledge/Systems/效能檢核目錄.md:201`
引句:「meta 列全表:kt 七題+Spring 後端兩題+extcode」

總結:最嚴重 major;blocking 共 0 條
