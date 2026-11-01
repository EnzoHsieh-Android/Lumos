severity: major

以下對照的行號都來自 `/Users/enzo/harness/lumos-auto-device/scripts/lumos`(目前 HEAD 6607b7ccd)。被審的是 f6c8904 凍結版,兩者的差別我沒逐一比對。

## 1. 分層與依賴方向:大致對齊,有一處重複計算

- 對齊的部分:計劃把「judge 只記事實(`checks`)、推送檢查才判擋」分開,跟現有分法一致。
  - judge 只看 run 目錄和 steps.json,不碰主線:file: `scripts/lumos:40920`(`_e2e_judge_ui(e2e, steps)`)。
  - 主線與分岔點只有推送檢查拿得到:file: `scripts/lumos:41922`(`_e2e_gate_mainline`,內部呼叫 `_secev_mainline`)。
  - 計劃說「新情境」直接用推送檢查已算出的主線結果,沒有另寫挑主線的邏輯。判不出主線就擋,跟 `_e2e_gate_block("找不到主線…")` 同一條路:file: `scripts/lumos:41922`。
  - 新增的判定該接在 `_e2e_gate_body` 的 `_e2e_gate_by_feature` 前後:file: `scripts/lumos:42045`。計劃沒指明接在哪,但層次沒問題。
- 不對齊(minor):計劃要 judge 在終端預覽「有 accept 的情境裡沒對到的句子」,推送檢查之後又算一次同樣的逐句對照。
  - 現有 judge 只用 `notices` 印提醒,不做覆蓋判斷:file: `scripts/lumos:41029`(`_e2e_judge_macrobench` 的 notices)。
  - 如果預覽和推送檢查各寫一份對照邏輯,就會有兩份會漂移的實作。計劃沒說要共用同一支純函式。

severity: minor
blocking: 否 判準:結構分層對,但逐句對照可能被寫成兩份;實作時抽成一支共用函式即可。
引句:「只在終端多印一段預覽:零檢查的流程」

## 2. 命名與錯誤處理:新鍵命名格式與鄰居不同,紀錄驗證漏講

- 對齊的部分:
  - `accept`、`accept_review`、`one_way` 都是 snake_case,跟 `flows`、`visual` 同層。
  - 設定檢查回傳「錯誤訊息或 None」,訊息以 `{where}…` 開頭:file: `scripts/lumos:40597`(`_e2e_case_err`)。
  - 新增的設定檢查掛進同一條 `_e2e_cfg_err` 鏈:file: `scripts/lumos:40691`。
  - `--check-config` 的 rc 2 走原本出口:file: `scripts/lumos:39523`。
  - 判不清就擋、讀不懂記 `null` 加原因,跟現有一致:file: `scripts/lumos:41986`(`_e2e_gate_load` 的 `_e2e_gate_block`)。
- 不對齊(minor):`accept_review.by` 用 `"agent:<模型>"` / `"human:<名字>"` 前綴字串,現有同類欄位是純列舉。
  - 放行紀錄的 `by` 只收 `"human"` 或 `"ai"`,說明另放 `note`:file: `scripts/lumos:41713`(`_e2e_waiver_ok`)。
  - 同一份紀錄裡出現兩種「誰簽的」表示法。計劃沒說明為什麼不沿用,或是要不要把 `human:` 前綴判斷和 `_e2e_waiver_ok` 對齊。
- 不對齊(minor):計劃說「查證紀錄只多 `checks` 一欄」,但沒提 `_e2e_record_err` 要加型別驗證。
  - 注解寫明「判定會讀到的欄位型別也在這裡驗」:file: `scripts/lumos:40849`。
  - 推送檢查會直接讀 `checks.count`、`checks.labels`。這兩個欄位若不在 `_e2e_record_err` 驗,紀錄被手改或寫壞時,推送檢查會在判定內部崩掉,不會擋下並叫人修紀錄。
  - 另外 `checks_reason` 是平放的兄弟欄位,現有 judge 輸出用的是 `reason`:file: `scripts/lumos:40920`。這點只是名稱風格,我不單獨列。

severity: minor
blocking: 否 判準:鍵名和擋下方式基本對齊,但 `by` 格式與驗證落點跟鄰居不同,實作時補上即可。
引句:「{"by": "agent:<模型>" 或 "human:<名字>", "at": "YYYY-MM-DD"}」

severity: minor
blocking: 否 判準:新欄位沒說明由 `_e2e_record_err` 驗型別,跟鄰居「讀到的欄位都在這裡驗」的慣例不同。
引句:「查證紀錄只多 `checks` 一欄,舊紀錄沒有這欄照舊判」

## 3. 第二種做法:有兩處(都標 ⚠)

- 對齊的部分:計劃沒有自寫挑主線,也沒有自創紀錄格式。
  - 已有 `_e2e_load_json`(限深、清孤立代理字元)和 `_e2e_tree_json`:file: `scripts/lumos:40972`。計劃沒點名要用,但沒另外發明讀法。
  - 比對分岔點紀錄應沿用 `_e2e_tree_json` 加 `_e2e_record_err`,不要另寫讀紀錄的函式。

**3a. 單向門關鍵字比對(⚠)**
- 計劃說「用 `PITFALL_CLASSES` 只取三類,以子字串比對」。但現有關鍵字比對有以下特性:
  - 詞表是 `PITFALL_CLASSES` 的 regex 表,英文詞用前後非英數的界線:file: `scripts/lumos:36543`。
  - 唯一的掃描函式是 `_door_keyword_hits(text, skip, only)`:file: `scripts/lumos:13974`。
    - 它的 `only` 參數是行號集合,不是類別過濾,而且四類一起回。
    - 它比對前先過 NFKC、去零寬字元、壓空白等一整套 `_door_scan_text`。
  - 「只取三類」目前沒有現成參數。實作者可能直接拿 `_PITFALL_COMPILED` 自己跑 regex,繞過正規化。
  - 結果是專案裡有兩條路比對同一張表,正規化不一致:不可見字元、全形字會讓同一句驗收句在規格閘算單向門、在這裡算不是。
  - 計劃的「子字串比對」說法也跟實際(regex 加詞界)不符,是文字上的誤導。
- 較妥的做法:共用 `_door_keyword_hits`,再用 `hit[1]`(中文類名)或 `_DOOR_CLASS_ZH` 把 self-governance 篩掉:file: `scripts/lumos:13747`。
- 另外 `PITFALL_CLASSES` 的注解寫「改這張表要升 `_DOOR_RULE_VERSION`」:file: `scripts/lumos:36550`。這條新用法讓這張表多一個消費者,計劃沒提醒同步。

severity: major
blocking: 是 判準:有可能長出第二套關鍵字比對(繞過 `_door_scan_text` 的正規化),違反「規格閘關鍵字單一來源」。
引句:「用規格閘的關鍵字表(`PITFALL_CLASSES`)只取 payment、external-send、prod-irreversible 三類比對」

**3b. flow 的名字從哪來(⚠)**
- 計劃讀 `<dir>/debug/<flow 的 name:>/commands.json`,也就是 YAML 裡的 `name:`。但計劃自己的 Q3 說 lumos 沒有 YAML 解析器。
  - 現有唯一的 flow 名規則是 `_e2e_flow_name`(路徑去副檔名、`/` 換 `__`):file: `scripts/lumos:40472`。注解寫明範本腳本 `android-e2e-run.sh` 的 `accept()` 有同一套,兩邊要一起改。
  - 計劃沒說 judge 怎麼從 flow 檔拿 `name:`,也沒說沒有 `name:` 時怎麼辦。
  - 一旦用 `name:`,就多了第二種 flow 識別法。
- 較妥的做法:讓範本腳本(碰裝置的一方)把 debug 目錄路徑寫進 steps.json。judge 只讀路徑,不猜名字。這跟「範本碰裝置、lumos 只判定與記帳」的分工一致。

severity: major
blocking: 是 判準:引入第二套 flow 名來源(YAML `name:`),跟 `_e2e_flow_name` 並存,且 lumos 沒有 YAML 解析器、計劃沒說怎麼拿。
引句:「從 steps.json 那次的 `evidence.dir` 讀 `<dir>/debug/<flow 的 name:>/commands.json`」

## 4. 落點:`lands_in` 偏了一個,另有遺漏(⚠)

- `Systems/android-e2e-acceptance`:對。它管 e2e 段格式、judge、推送前檢查、指紋,新判定和新設定鍵都屬於它。寫進這篇,不另開。
- `Systems/lumos-cli-write`:不對。這篇是圖譜寫入原語(set/append/new/decision-*)。
  - 它的 `about_code` 只列 `scripts/lumos`,沒寫負責範圍(參考資料也說「沒寫負責範圍」)。
  - 計劃改的是 macrobench 設定檢查與 e2e 判定,跟圖譜寫入無關。大概是誤把 `reference.md` 的格式鐵則連到這裡。
  - 計劃本文沒提要改 `reference.md`。若真要改,先說明要改什麼。
- 遺漏:要改的 skill 檔沒有 Systems 家。
  - 我 grep 過 `docs/lumos-toolchain-knowledge/Systems/*.md`,沒有任何 `about_code` 列 `skills/lumos-android-evidence/SKILL.md`,也沒有節點列 `skills/lumos-project-notes/reference.md`。
  - 只有 `Systems/macrobenchmark-adapter` 的正文提到 lumos-android-evidence 和它的兩支範本。
  - 只有 `每輪修補差異派工` 一篇的 `about_code` 列了 `skills/…` 的檔。
  - 規則 5 不一定要求 skill 檔有家,所以這點標 ⚠。至少要把「寫驗收句的程序」該落哪一篇說清楚。我建議 `Systems/macrobenchmark-adapter`,或在 `Systems/android-e2e-acceptance` 加一節並把 skill 檔寫進 `about_code`。
- 另外,3a 把規格閘的詞表加了一個消費者,`Systems/規格閘` 也該列進 `lands_in` 或 `related`。計劃有連它,但 `lands_in` 沒有。

severity: minor
blocking: 否 判準:`lands_in` 列了不相干的 `Systems/lumos-cli-write`,又漏了 skill 檔的家和規格閘的反向註記;屬寫回位置問題,不是做法衝突。
引句:「  - Systems/lumos-cli-write」

severity: minor
blocking: 否 判準:計劃要改的 skill 檔沒有任何 Systems 節點管,`lands_in` 沒說寫驗收句程序落在哪一篇。
引句:「寫進 lumos-android-evidence 與產 flow 的派工要求」

不對齊共 7 條,其中 major 2 條
