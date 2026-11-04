severity: blocker

整體而言,審計修正紀錄 r1、r2 與正文一致,決策 d3 與正文各處互相對得上。但 `E2E_SCHEMA` 升版這一條照字面做會讓判定全壞,是 blocker。

**1. `E2E_SCHEMA` 升到 2 會讓 judge 拒絕消費專案手上現有範本腳本寫的 steps.json**

引句:「紀錄格式版本 `E2E_SCHEMA` 從 1 升到 2」

file: `/Users/enzo/harness/lumos-auto-device/scripts/lumos:40433`:`E2E_SCHEMA` 是查證紀錄與 steps.json 共用的同一個常數。

file: `/Users/enzo/harness/lumos-auto-device/scripts/lumos:42640`:judge 檢查 `steps.get("schema") != E2E_SCHEMA`,不符就設 `serr`,等於整個 judge 讀不了這份 steps.json。

file: `/Users/enzo/harness/lumos-auto-device/scripts/templates/android-e2e-run.sh:427`:範本腳本寫死 `"schema": 1`。

重現:
- 把常數改成 2。
- 用舊範本腳本跑一次驗收,steps.json 的 schema 是 1。
- judge 回「steps.json 的 schema 是 1,這版 lumos 只認 2」,拒絕寫紀錄。

後果與矛盾:
- 所有還沒跑 `lumos update` 的消費專案,升版當天整條驗收都壞。
- S3 與〈做法〉第 4 條都假設「舊版範本腳本」會走到 `checks: null` 加原因,但那一支在 steps.json 就被擋掉,永遠走不到。
- spec 只談紀錄的 schema(`_e2e_record_err` 已接受 1 到 `E2E_SCHEMA`,見 `scripts/lumos:40854`),沒有把 steps.json 的 schema 拆開。
- 落點只列要改 `android-e2e-acceptance`,沒列 `Projects/Android端到端驗收_計劃` 裡「steps.json schema 第一版是 1」的描述,也沒列它的 S7、S46。
- 還有一個同源缺口:舊的 schema 1 紀錄被新 lumos 重寫時,schema 欄會維持 1。spec 沒講 judge 寫入 `checks` 時是否同時把 schema 設成 2,所以「舊版 lumos 不會覆寫成沒有 checks 的形狀」這句保證沒有落到實作。

severity: blocker
blocking: 是,照字面實作會讓所有沿用舊範本腳本的專案驗收整條失效。

**2. 決策 d2 原文寫 `human:`,正文與 S13 寫 `by` 是 `human`**

引句:「單向門類型的情境(金流、對外送出、不可逆資料三類,定義同規格閘的計劃風險表)驗收句要人點頭:accept_review.by 必須是 human:」

- d2 是決策紀錄,依專案規則比正文更有挑戰程式碼的效力。d2 的 `human:` 是 r1 的前綴格式,r2 改成 by/who 時沒回頭改這條。
- 正文與 S13 是 `{"by": "human"|"agent", "who": ...}`。
- 〈待決問題〉那段只說 Q1、Q2 的 accept_required、risk 沒採用,沒提 `human:`。接手的人讀 d2 會實作成前綴比對,跟 S13 的格式檢查打架。
- Q2 的題目文字有同一個 `human:`。

severity: minor
blocking: 否,正文與綁定測試比 d2 具體,不會讓人實作錯,只是決策欄位仍留著過期寫法。

**3. 「位置」那一句同時能讀成放行之前和放行之後**

引句:「也就是接在整套通過、放行之前那一刻」

file: `/Users/enzo/harness/lumos-auto-device/scripts/lumos:42067`:`_e2e_gate_body` 先檢查 waiver(`_e2e_waiver_ok`)就回 `waived`,之後才進 `_e2e_gate_full_note`,整套通過的判定在後者裡。

- 照字面把新規則放在「放行之前」,waiver 就蓋不過它,違反 d3。
- 實際只能放在 `_e2e_gate_full_note` 裡 `_e2e_gate_done("pass")` 之前,也就是 waiver 檢查之後。
- 同一段後面的「放行蓋得過新規則」才是真意,但前一句沒寫死。
- 第 8 條要求在「放行」路徑也印舊項目清單與檢查變少。但 waiver 路徑現在在讀分岔點、算新舊之前就 return。waiver 路徑沒有整套 `runs` 時要印什麼,spec 沒定。

severity: minor
blocking: 否,真意可從 d3 與 S9 推出,措辭與路徑細節補一句即可。

**4. reference.md 第 5 段的改寫會讓那句話不實**

引句:「新流程零檢查會被擋、新情境要逐句對到;舊流程照舊」

file: `/Users/enzo/harness/lumos-auto-device/skills/lumos-project-notes/reference.md:1182`:這一節存在,第 1、4、5 段也都在,落點不是空的。

- 第 5 段原句是天花板清單的一項:「`[kill:]` 第三階在 UI 層走不通(斷言被刪掉不會有任何機械檢查翻紅)」。
- 照 spec 把括號內容換掉,句子變成「`[kill:]` 第三階走不通(新流程零檢查會被擋…)」,前後不連貫。
- 原句描述的限制仍然成立:有檢查的流程被刪掉一條檢查仍不翻紅,舊流程更不翻紅。新規則只擋整支零檢查,所以不該用改寫取代,而是在原句後補一條。

severity: minor
blocking: 否,只是文件措辭,但會讓三個月後的人以為斷言被刪現在會紅。

**5. 擋下訊息「不附放行指令」靠 `_cl_say_e2e_next` 分派做不到**

引句:「擋下報告帶一個新旗標,`_cl_say_e2e_next` 照它分派(跟既有的 `bad_record`、`newer_schema` 同一種做法),不走整套重跑那一行」

file: `/Users/enzo/harness/lumos-auto-device/scripts/lumos:68470`:放行指令是 `_cl_say_e2e_block` 在 `_cl_say_e2e_next` 之後另外印的,條件是 `rep.get("fp") and not rep.get("bad_record") and not rep.get("newer_schema")`。

- `bad_record` 與 `newer_schema` 是靠這個排除條件才不附放行指令,不是靠 `_cl_say_e2e_next`。
- 只加分派的話,「驗收句沒對到」和「單向門」兩類會照樣印「確定是誤擋才放行」,違反 spec 自己說的「不附放行指令」。
- 「讀不到執行紀錄」那支要附放行指令,同一份報告混多類時是否附,spec 沒定。
- S5、S12 的測試沒有覆蓋這個行為。

severity: minor
blocking: 否,只影響訊息,放行指令印出來也有效(放行蓋得過新規則,d3 認可)。

最嚴重 severity:blocker,blocking 共 1 條。
