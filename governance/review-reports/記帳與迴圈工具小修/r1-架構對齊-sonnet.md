severity: major

以下四問各一段,每條 finding 都附對照位置。

## 1. 分層與依賴方向

**finding 1(第 7 節拆包核對的派工單讀法,是第三套讀法)**
severity: major
blocking: 是
引句:「找 `governance/review-reports/<編號>/<--round>-dispatch.json`(repo 根底下,照手冊的固定位置;沒帶輪次或檔不在就跳過)」
- 專案裡已有兩套派工單讀法:
  - `_roster_dispatch_entries(loop_dir, rid)`:用 glob `rN-dispatch*.json`,認三種形狀(頂層 `auditor`、`seats` 陣列、頂層 list),壞檔跳過並計數。對照位置:``file: `scripts/lumos:14351` ``。
  - `cmd_seat_check`:只讀頂層 `materials`。對照位置:``file: `scripts/lumos:28802` ``。
- 計劃另寫一支讀法,有四處不同:
  - 只讀精確檔名 `rN-dispatch.json`,不用 glob。`_roster_observe` 與 `_fix_dispatch_base` 都用 `rN-dispatch*.json`,同一輪有 `r1-dispatch-2.json` 這類多份時,核對會漏看。對照位置:``file: `scripts/lumos:14444` ``、``file: `scripts/lumos:14806` ``。
  - 不認頂層 list 這種形狀。
  - 單席形狀多認一個 `seat` 欄位,`_roster_dispatch_entries` 只認 `auditor`。
  - 計劃寫「`seat-check` 既有讀法只讀頂層這一種」,但這句只對 `seat-check` 成立,`_roster_dispatch_entries` 另有讀法。
- 建議:擴充 `_roster_dispatch_entries`,讓它同時回每席的 `materials`,再讓 `canary record` 和 roster 對帳共用,不要再開第三支讀法。
- `loop_dir = root/"governance"/"review-reports"/loop_id` 的組法在 `_roster_observe` 已有(``file: `scripts/lumos:14423` ``),要共用,不要在 `cmd_canary` 裡再手寫一次。

**finding 2(輪次格式判法只收斂一處)**
severity: minor
blocking: 否
引句:「`cmd_loop_next` 開頭那道「有的帶輪次、有的不帶」守衛改呼叫它(條件與訊息都不變)」
- 帳上「有的帶輪次、有的不帶」的判斷現在有三份:
  - `loop status` 的 panel 模式守衛(``file: `scripts/lumos:13930` ``)。
  - `loop next`(``file: `scripts/lumos:16317` ``)。
  - 處置閘(``file: `scripts/lumos:28247` ``)。
- 計劃新增 `_loop_round_format`,只收斂 `loop next` 這一份,加上新的寫側,共五處,仍有兩份各自手寫。
- 處置閘那份,〈不做〉已明講不動。
- 13930 那份,計劃沒提。
- 建議:至少在〈不做〉補一句「13930 那份不動及其理由」。

## 2. 命名與錯誤處理

**finding 3(`--regression-set` 的「只給代碼審」判法,與計劃所稱的對照物不同)**
severity: minor
blocking: 否
引句:「照 `--finding-source` 的既有擋法,`_roster_kind(loop) == "design"` 時帶 `--regression-set` → rc2」
- `--finding-source` 的既有判法是 `str(loop or "").startswith("code-")`(``file: `scripts/lumos:11641` ``)。
- 計劃改用 `_roster_kind(...) == "design"`,「看不出種類」(編號是 `codeXreview` 這類)就放行。
- 兩者對 `codeXreview` 的結果相反:`--finding-source` 擋,新的 `--regression-set` 收。同一族「只給代碼審」的旗標有兩種判法。
- `_roster_kind` 自己的註解說這是全檔唯一的判法,所以計劃的選擇有依據。
- 但〈做法〉和 PRIOR-ART 都寫「照 `--finding-source` 的既有擋法」,字面不實。
- 建議:二選一。
  - 選項一:改成同一個判法。
  - 選項二:把「判法不同、為什麼」寫明。
  - 同時考慮順手把 `--finding-source` 也改成 `_roster_kind`,或在〈不做〉註明不動。

**finding 4(`none` 判法,與 `--regression-set` 現有判法的差異沒講清楚)**
severity: minor
blocking: 否
引句:「`_ids` 把整串去空白後不分大小寫等於 `none` 的值當成空集合(跟 `--refuted-set`/`--regression-set` 同一個寫法)」
- 現有 `--regression-set` 判法是 `str(regression_set).strip().lower() == "none"`(``file: `scripts/lumos:11581` ``)。
- 計劃說「`--regression-set` 那段原本自己判 `none`,改用同一支,行為不變」。這句大致成立。
- 但 `_ids` 把「未給」(`None`)與「明示空集合」(`""`)分成兩種語意。
- 加入 `none` 之後,「空字串」和「`none`」都回 `[]`,`--findings-set none` 因此改成走「不能是空的」那一句擋。計劃已寫出這個行為改變,這部分沒問題。
- 計劃沒交代 `--refuted-set` 的處理方式要不要一起歸到 `_ids`。
- 既然聲稱「同一個寫法」,建議列出 `--refuted-set` 的現有判法位置,確認三處一致。

**finding 5(新增擋下與提醒的訊息形狀,多處偏離三段式)**
severity: minor
blocking: 否
- 專案慣例是三段式:發生什麼、為何在意、指令獨立一行。
- 計劃擬的訊息有三處偏離:
  - 輪次格式擋下:一整句連寫,「照既有格式補上/拿掉 --round 再記」夾在句尾,沒有獨立指令行。
  - 留痕指紋提醒:「提醒:…要更正請另開一份檔…」是單行散文。
  - 拆包材料擋下:同樣一句帶過。
- 既有同族訊息(``file: `scripts/lumos:11442` ``、``file: `scripts/lumos:11852` ``)也多半是單行散文,「擋下:…」加一句話的形狀本身有先例。
- 所以這條只算 minor。
- 唯獨第 7 節和第 1 節「第一筆不帶輪次」兩條擋下,計劃說要「印補了 `--round r1` 的同一條指令提示」。這個做法是三段式,值得其他幾條跟進。

## 3. 第二種做法

- 派工單讀法已列為 finding 1,major。
- `_dispositions` 的型別檢查(第 4 節):計劃說「兩支共用一個小判斷」。
  - 這是新增一支共用小函式,方向對。
  - 但專案裡未見表態證據型別檢查的既有輔助函式,查無第二種做法的證據。
  - 這條沒有不對齊。
- `hints` 清單(第 8、9 節):`cmd_loop_next` 文字輸出目前沒有 `hints` 鍵。
  - 既有的提示是散在各處直接 `print`,例如 ``file: `scripts/lumos:16472` `` 的「提醒:這個審查編號從沒指定過分級…」,以及 `_LENS_SCOPE_TOOLCHAIN_LINE` 那行。
  - 新增一支「依種類、分級、輪次組提示」的函式,是新的結構,但計劃也講了為什麼:不各自散印。
  - 這屬設計選擇,不算第二種做法。
  - 只需確認文字輸出是在 `for k in (...)` 白名單那段加一個 `hints`,而不是另開一條輸出路徑。
- 路徑規範化與讀帳:計劃在寫側沿用 `_loop_records_checked`、`_ledger_rel_path`、`_gate_event_or_warn(..., hard=True)`,都是既有共用函式,一致。

## 4. 落點

**finding 6(拆包核對與 `seat-check` 的家)**
severity: minor
blocking: 否
- 計劃把「拆包核對」寫回 `Systems/loop-convergence-recording`。
- 但 `seat-check` 目前記在 `Systems/design-loop`。
- 若 finding 1 採「擴充 `_roster_dispatch_entries`」,實際碰的是 roster 對帳這塊。需要確認它記在哪一篇,再決定寫進哪一篇。
- ⚠ 交編排者:我只確認了 `design-loop` 提到 `seat-check`,沒有逐篇掃 roster 對帳的家。

**四個 lands_in 本身沒有問題**
- 四個 Systems 節點都已存在,每支程式檔都有家:`scripts/lumos` 同時掛在四篇上。
- 各節歸屬:
  - 輪次、`none`、`--regression-set`、留痕提醒、拆包核對、hints:`loop-convergence-recording`。
  - pitfalls 印要派誰:`pitfalls-code-loop`。
  - 表態證據型別:`棧別提問表態閘`。
  - 首輪順序提示與 `spec-freeze` 訊息:`design-loop`。
- 這幾項的歸屬都對,不需要另開新節點。

## 小結

不對齊共 6 條,其中 major 1 條。

- major 只有 finding 1:拆包核對另寫了一套派工單讀法,跟既有的 `_roster_dispatch_entries` 和 `cmd_seat_check` 並存。
- 其餘 5 條是 minor:
  - 輪次判法只收斂一處
  - `--regression-set` 的判法與 `--finding-source` 不同
  - `none` 判法的對照位置缺漏
  - 訊息形狀偏離三段式
  - 拆包核對的家待確認
