severity: major

我把整份 spec 逐節讀完,並對照 `scripts/lumos`、`configs/ast-grep/kotlin-android/` 查證。下面每條 finding 都附程式碼佐證。

## 範圍 1:`review` 段放進 `.lumos/lint.json`

severity: major
blocking: 是(實作者會照字面做出與既有共識相反的設計,舊版讀新設定檔會整批判紅)
- spec 段落:〈範圍〉做 1、〈回退〉。
- 引句:「`.lumos/lint.json` 加選填的 `review` 段」
- 問題:程式碼與圖譜已有「不往 lint.json 塞非副檔名的鍵」的共識。依賴層因此另開 `lint-deps.json`,`lint-watch` 也是為同一理由另開檔。spec 沒提這個先例,也沒說明為什麼不另開檔或不放進 `.lumos/config.json`。
- 實際失敗輸入:消費專案貼了範本的 `review` 段,而機器上仍是舊版 lumos(vendored 副本或 CI 用的舊版)。舊版 `_lintcheck_validate` 會報「value 必須是命令列表」,doctor [F] 與 `lint-check` 對每個採用專案判紅。
- 〈回退〉只處理「退版後的新驗證器」,沒處理「新設定檔被舊版讀」。
- 佐證:
  - file: `scripts/lumos:41888`(「★不放 .lumos/lint.json★……這條共識程式註解與圖譜三處都寫過」)
  - file: `scripts/lumos:42010`
  - file: `scripts/lumos:39607`

## 範圍 2:分流點與例外隔離

severity: major
blocking: 是(該擋沒擋)
- spec 段落:〈範圍〉做 2。
- 引句:「結果放進另一份 `out`,再各自呼叫 `_lint_new_diff_claims` 算新增命中」
- 問題:覆核邏輯寫在 `_lint_new_tools`/`_lint_new_verdict` 同一條呼叫鏈裡,spec 沒要求把覆核的例外隔離成 `review_undone`。
- 實際失敗輸入:覆核命令吐出怪結果,或用 importlib 借 `check.py` 的 `main_rows` 時拋例外(檔不在、型錄壞)。例外會一路冒到 `_codeloop_lint_new_step` 的 `except Exception`,整道新增告警閘 fail-open,連「一般段」已算出的新增告警也一起被放行。
- 佐證:
  - file: `scripts/lumos:74561`(`except Exception as e: _gate_failopen(...); lv = None`)
  - file: `scripts/lumos:42592`
- spec 只講覆核「沒跑到」不擋,沒講覆核「跑壞了」不能拖垮一般段。

## 範圍 3、4:身分綁片段指紋,判定與放行不綁語境

severity: major
blocking: 是(語意覆核級的真假恰恰取決於片段以外的語境,判定卻永久綁在片段指紋上)
- spec 段落:〈用詞〉覆核命中、〈範圍〉做 3、5。
- 引句:「身分(材料與紀錄裡的 `seg`)就是新增告警閘的放行指紋」
- 問題:指紋只含(規則, 檔名, 命中行片段)。情境題的段身分「綁段材料內容,程式改過就要用新材料重判」,覆核命中沒有這層。判 `false` 後寫入的放行永久生效,ledger 又是「同一格只認第一筆」。
- 具體輸入:`ref.setValue(x)` 第一次判 false(`ref` 是 Firebase 的 `DatabaseReference`)。之後同檔宣告處改成 `MutableLiveData`,並在背景執行緒呼叫。命中行片段不變,指紋不變。它被視為已放行,永不重判、不再現身。
- 〈天花板〉1 只講「同檔同片段多處」,沒講「語境隨時間變」。
- 錯判 `false` 無法重判:帳撤不掉,只認第一筆,材料也不會變。
- 佐證:
  - file: `scripts/lumos:42219`(`_lint_new_key` 只取片段)
  - file: `scripts/lumos:74064`(情境題以 `sg["rows"]` 綁材料)
  - file: `scripts/lumos:73858`(第一筆為準)

## 範圍 5:`false` 的記帳與放行寫一半

severity: major
blocking: 是(寫一半、不可逆)
- spec 段落:〈範圍〉做 5。
- 引句:「記帳那一步(`lumos code-loop blind-judge <結果檔>`)替它寫一筆放行」
- 問題:同一步要寫兩處,一是 ledger 追加 `rule_hits`,二是 `lint-waivers.json` 逐筆 `_lint_waivers_add`。spec 沒定順序,也沒定冪等。
- 先 ledger、後 waiver 的失敗輸入:waiver 檔讀不了(`werr`)或第 N 筆失敗。
  - 結果:ledger 已記 `false`、放行缺席,`false` 的 d3「進複查清單」靜默落空。
  - 重跑會被「整份都是已有的格 → rc2」擋下,修不回來。
- 先 waiver、後 ledger 的失敗輸入:重試時 `_lint_waivers_add` 回「這個指紋已經放行過了」。
- 現有的盲判寫帳只有 ledger 一處,沒有這個問題;現在多了一處,spec 沒講怎麼收尾。
- 佐證:
  - file: `scripts/lumos:42297`(`if key in cur: return (False, ...)`)
  - file: `scripts/lumos:74209`
  - file: `scripts/lumos:74225`(帳追加無法撤回,見重判說明)

## 範圍 4:`rule_hits` 的 seg 沒有對照當次命中

severity: major
blocking: 是(可繞過擋停)
- spec 段落:〈範圍〉做 4 結果檔。
- 引句:「`_kt_bj_validate` 擴充認這個鍵,同一格已有判定不再收」
- 問題:既有 `_kt_bj_validate` 用 `by = {s["seg"]: s ...}` 擋掉不在材料裡的段。spec 沒說 `rule_hits` 的 `seg` 要對照「當次重跑覆核命令得到的新增命中」。
- 具體輸入:結果檔寫 `{"seg": <一般段某條會擋的告警指紋>, "verdict": "false", ...}`。依範圍 5,記帳步驟會替這個指紋寫一筆 `lint-waivers.json` 放行(origin ai)。
  - 放行檔與指紋空間跟一般段共用,所以那條一般段的擋下被放掉。
  - 即使不是惡意,抄錯一碼也會替任意指紋寫放行。
- 另外,結果檔只有 `rule_hits`、沒有 `segments` 時,既有檢查直接報「要有 segments 清單」。spec 說可單獨一份,沒說怎麼改驗證。
- 佐證:
  - file: `scripts/lumos:74064`(`by.get(sid) is None → 錯`)
  - file: `scripts/lumos:42297`(放行只認 key,不問來源)

## 範圍 4:治理帳新欄位 `rule_hits` 的讀端形狀

severity: major
blocking: 是(讀錯帳,炸成放行)
- spec 段落:〈範圍〉做 4 治理帳。
- 引句:「判定放在新欄 `rule_hits`(不放進舊的 `blind_judge` 欄)」
- 問題:既有慣例是讀端驗票形狀,形狀不對整筆跳過。理由寫在程式裡:內層壞掉炸成放行。
  - `_GOV_FIELD_TYPES` 對已知欄位做型別檢查,「型別錯會讓整個 gov 當掉」。
  - spec 沒要求把 `rule_hits` 加進該表。
  - spec 也沒要求新讀端寫 `_kt_bj_event_ok` 對應物。
- 具體輸入:治理帳被手動提交進一行 `rule_hits` 是字串或元素缺 `seg` 的事件。
  - `gov --stats` 的新統計段、推送前的讀判定會丟例外。
  - 這個例外接到上面「fail-open」那條路徑。
- 舊版讀帳略過 `rule_hits` 這點 spec 已想到。新版讀壞帳這個方向沒想到。
- 佐證:
  - file: `scripts/lumos:17499`(`_GOV_FIELD_TYPES`,含「型別錯會讓整個 gov 當掉」的註解)
  - file: `scripts/lumos:73831`(`_kt_bj_event_ok`)
  - file: `scripts/lumos:73810`(r1 正確性 F1 到 F3 的註解)

## 實務隱患 / 範圍:62 條裡有 8 條在這條路徑上永遠不會響

severity: major
blocking: 是(「62 條一起處理」的前提不成立,統計與 RETIRE-IF 會量到假零)
- spec 段落:〈白話〉、〈實務隱患〉盲判成本。
- 引句:「兩級共 62 條,現在既不擋、也不量、也沒人看」
- 問題:`rules-review/testing.yml` 的 1 條與 `rules-hints/testing.yml` 的 7 條,`files:` 都限定 `**/src/test*/**` 等測試目錄。新增告警閘預設把測試路徑從 `code_pairs` 濾掉(`include_test_paths` 預設空集合)。
- 具體輸入:任何 `src/test/...Test.kt` 的改動,覆核命令根本沒被餵到那支檔,這 8 條規則永遠 0 命中。
- spec 只提醒要實測命中筆數,沒提 `lint_new.include_test_paths: ["kt"]` 這個設定。範本與〈範圍〉8 也沒要求加。
- 佐證:
  - file: `configs/ast-grep/kotlin-android/rules-hints/testing.yml:6`
  - file: `configs/ast-grep/kotlin-android/rules-review/testing.yml:5`
  - file: `scripts/lumos:42610`
  - file: `scripts/lumos:63861`
  - file: `scripts/lumos:41805`
  - file: `scripts/lumos:39483`

## 範圍 4:`--template` 介面不明

severity: major
blocking: 是(實作者必須自己決定介面,而現有 howto 會直接撞牆)
- spec 段落:〈範圍〉做 4 材料。
- 引句:「`lumos code-loop blind-judge --template` 多印一份 `rule_hits`(跟情境段分份印、各派一席,不同時給一個代理)」
- 問題:
  - 既有 howto 是 `--template > /tmp/bj.json`,stdout 只能有一份 JSON。
  - spec 沒說兩份怎麼選(旗標?兩份連印?),也沒說 `--part` 是兩種材料共用一套編號還是各自編號。
  - `--missing`、`--disagreements` 與 `--unsure` 三種模式要怎麼互斥,也沒講。
- 具體失敗:`_cmd_codeloop_blind_judge` 開頭遇到情境型錄錯誤 (`_KT_DT_ERR`) 直接 `return 2`。`segs is None` 也 return 2。一個只想判覆核命中的呼叫,會被情境側的環境問題擋住。
- 佐證:
  - file: `scripts/lumos:74188`
  - file: `scripts/lumos:74195`
  - file: `scripts/lumos:73892`(`_kt_bj_howto` 以單檔輸出為前提)

## 範圍 5:擋停條件有缺口(`unsure` 未仲裁、閘的模式)

severity: major
blocking: 是(同一輸入,實作者可能擋也可能放)
- spec 段落:〈範圍〉做 5。
- 引句:「`--template --unsure`(本案新增)只印第一判是 `unsure` 的那幾筆」
- 問題:
  - 第一判 `unsure`、仲裁還沒跑時,要擋還是放?「還沒判:擋」與「`unsure` 交仲裁」兩句都適用。
  - 若這時擋,第一判 `unsure` 的那幾筆沒有明講怎麼放行。
  - 若不擋,仲裁就不用跑(pass 前的一次性核對會漏)。
- 閘的模式也沒講:新增告警閘有 `block`、`warn`、`off`,另有 `LUMOS_SKIP_LINT_NEW`。覆核的 `real` 與還沒判,在 `warn` 或 `off` 下要不要擋?`_lint_new_classify` 照 `cfg["mode"]` 降級,spec 只說「一般段」。
- 佐證:
  - file: `scripts/lumos:42401`(`hard and cfg["mode"] == "block"`)
  - file: `scripts/lumos:42448`(`skip_env`、`mode == "off"` 走 `_lint_new_off`)

## 範圍 2、6:覆核「沒跑」的原因表不完整

severity: minor
blocking: 否(不改,覆核會在特定宣告形狀下靜默不跑,但不會誤擋)
- spec 段落:〈範圍〉做 2、6。
- 引句:「覆核命令沒跑到(預算用完、工具沒裝、逾時)記進 `review_undone`,只講出來、不擋」
- 問題:實際還有更多沒跑的路徑,spec 的三種原因蓋不住。
  - 一般段沒有對應副檔名的命令時,`_lint_new_tools` 在 `if not cmd_targets` 就早退 `no-files`,`review` 段不可能被跑到。例:只宣告 `review`、沒宣告一般 kt 段。
  - 覆核命令沒帶 `{LINT_FILES}` 或 `{LINT_FILES_CSV}` 時,`_lint_new_run_cmds` 把它降到 `report_only`,既不跑也不記為未跑。
  - 範本與 `_lintcheck_validate` 都沒有擋這個。
- 〈範圍〉6「沒有 `review` 段就印覆核沒跑」會讓純 Python 專案、沒有 lint.json 的專案每次推送也印一行。
- 佐證:
  - file: `scripts/lumos:42623`(`if not cmd_targets:` 的早退)
  - file: `scripts/lumos:42664`(`_lint_gate_covers` 為否就 `report_only`)

## 範圍 7:`--verdict` 複查的設計

severity: minor
blocking: 否(只影響準確率統計與升降建議,不影響擋停)
- spec 段落:〈用詞〉人複查、〈範圍〉做 7。
- 引句:「不帶 `--verdict` 的 ack 照舊只記看過、不進準確率」
- 問題:
  - doctor 現行提示的就是不帶 `--verdict` 的 `--ack --all`,而 `_lint_waive_ack` 只處理「還沒 ack」的目標。第一次整批 ack 後,誤報永遠補不回 `--verdict`,準確率分母累積不起來,RETIRE-IF 的九成永遠量不出來。
  - 「`--verdict` 搭 `--all`」沒定義。一個值蓋給全部,會把原有的 62 筆一般 AI 放行與 `real` 判定後放行的項目一起記成 `agree`。
  - `overturn` 只進統計,對放行本身沒有任何作用。人推翻了盲判,那筆命中仍然被放行。
- 佐證:
  - file: `scripts/lumos:41194`(`_lint_waive_ack` 的 `targets` 只取未 ack 項,並接受 `ack_all`)

## 逐節結論

- 〈用詞〉、〈範圍〉做 8 與不做、〈依據來源〉、〈預期值表〉:已讀,無 finding。
  - 「62 條各唯一對到一列」與「出處不全:提示級 7 條、語意覆核級 0 條」我用 `main_rows` 與規則檔實際核對,成立。
  - `sgconfig-review.yml` 與 `sgconfig-hints.yml` 存在,規則數 12 與 50 與 spec 一致。
- 〈驗收條款〉:S1 到 S9 已讀。
  - S9 的現況行為(工作樹模式用 `_lint_new_cmd_targets(pairs, [], lint_cfg, ...)`)天然不含 `review`,條款成立但容易空轉。
  - 沒有針對上面各條的失敗輸入設條款。

## 資料狀態五問

- 新舊版互讀:舊版讀新帳沒問題(`_kt_bj_event_ok` 在 `blind_judge` 缺席時跳過整筆)。舊版讀新 `lint.json` 會判紅(見第一條)。
- 寫一半:見第四條。
- 衍生資料與源頭不一致:見第三、五條。放行檔與判定帳可以彼此不一致。
- 時間:判定綁片段指紋而非版本或語境(見第三條)。
- 不可逆:放行檔與治理帳追加後撤不掉。spec 的「已排除:不可逆」只覆蓋「退提交」,沒覆蓋「寫錯的放行」。

## 實務隱患逐類

- 守衛面:見第二、五、八條(例外 fail-open、可繞過擋停、模式缺口)。
- 資料不一致或不可逆:見上面五問。
- 金流、對外送出:無。只讀本機檔、跑本機 ast-grep,不連網,同意 spec 的排除。

最嚴重 severity: major,blocking 共 9 條(minor 2 條,不擋)。
