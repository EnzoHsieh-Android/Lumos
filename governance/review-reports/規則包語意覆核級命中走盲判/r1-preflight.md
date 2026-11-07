# 前掃報告 r1:規則包語意覆核級命中走盲判_計劃

被審:rulepack-review-bj/docs/lumos-toolchain-knowledge/Projects/規則包語意覆核級命中走盲判_計劃.md(行號指該檔)。
程式:rulepack-review-bj/scripts/lumos(下稱 L<行號>)。ast-grep 本機沒裝,SARIF 實跑沒驗(標在對應條)。
只讀,沒改任何 repo 檔。

---

## ① 未定義的詞(6 條)

1. 「身分」「段」`seg`:L87「`{"seg": <身分>, ...}`」、L86「覆核命中的身分是 `_lint_new_key` 加『同指紋在這支檔裡第幾次出現』」。〈用詞〉沒有定義「身分」長什麼字串。程式裡有兩套:放行檔鍵=`_lint_new_key` 的 sha256 前 16 碼;情境段身分=綁段材料內容。計劃沒說 rule-hit 的 `seg` 是哪一套、序號怎麼編進字串(見③-1、④-4)。
2. 「型錄那一列」與「規則→列」對照:L87、L89、L148。〈用詞〉L78「型錄那一列名稱標了『出處不全』」只講標記,沒講一筆覆核命中(ast-grep 的 rule id,如 `kt-livedata-setvalue-background`)怎麼對到型錄列(STATE-16)。型錄沒有「規則 id 欄」,id 散在「實測狀態」欄的自由文字(`規則 kt-xxx:樣本實測…`)。
3. 「不適用時」:L87「型錄那一列的壞寫法、標準寫法、後果與不適用時」、L135 S6「型錄那一列四欄」。主型錄表表頭是「編號|名稱|壞寫法形狀|標準寫法|後果|現成規則|級|情境怎麼認|接電方式|通電批次|實測狀態|來源」(checks-catalog.md L147/L188/L225),沒有「不適用時」欄;「不適用時」(alt)只在 D-n 情境決策表。詞沒定義、對不上實際欄位。
4. 「規則判定」vs「判定」vs「盲判」:L77 定義規則判定為 real/false/unsure,但 L87 ledger 事件叫 `blind-judge` 加 `type`,既有情境票是 `applies/followed/reason`。兩種「判定」詞在〈用詞〉沒區分。
5. 「複查後判錯」:L94「經人 ack 複查過幾筆、複查後判錯幾筆」。〈用詞〉沒有「判錯」的定義,人在哪個動作上表態「盲判錯了」沒講(見④-7)。
6. 「第二個代理仲裁(沿用 `--arbiter`)」L91:「仲裁」對 rule-hit 的定義(誰是第一判、`--disagreements` 以什麼為分歧)沒講;情境題的分歧是「作者表態 vs 第一盲判」,rule-hit 沒作者(L87 自己說)。

## ② 壞引用(3 條,其餘都存在)

已驗存在:Projects/Android寫法語意情境表態與盲判_計劃、Projects/Android協程與API寫法機械檢查標準_計劃、Systems/kotlin規則包、Systems/pitfalls-code-loop、Systems/linter精選目錄、Systems/棧別提問表態閘(含 L126 路徑)、Systems/test-guard、Systems/doctor-irreversible-hint(含 d1);`sgconfig-review.yml`、`sgconfig-hints.yml`(configs/ast-grep/kotlin-android/)、`rules-review/`(12 條)、`rules-hints/`(50 條)=62 條 ✓;`lumos rejections`(L28596)、`lumos gov --stats`、`lint-waive --ack`、`--arbiter`、`--template` 都在。

1. L175「(Systems/test-guard、Android端到端驗收計劃)」:實際檔名是 `Projects/Android端到端驗收_計劃.md`(有底線)。`Android端到端驗收計劃.md` 不存在。
2. L86/L87/S1–S8 的 `[test:t_rule_review_*]`:八個測試名在 scripts/test_lumos.py 都 grep 不到。計劃狀態是 todo,屬預期,但驗收條款綁的是還不存在的測試,規格閘會問;列為記錄,不算錯。
3. L108「AI 放行清單已經累積 41 筆沒人看過」:本 repo `.lumos/lint-waivers.json` 共 414 筆、origin=ai 且未 ack 的有 62 筆,不是 41。若 41 指別的消費專案,計劃沒寫是哪個專案、何時量的(也不是 `[來源:生產]` 之類帶來源的寫法)。

另:L106「2026-11-05 實測 nowinandroid 310 支檔掃出提示級命中的筆數要先量」句子殘缺(310 支檔後面沒有數字,同一句又說「要先量」),不是引用錯,但是未完成的陳述。

## ③ 範圍自相矛盾(5 條)

1. 〈範圍〉3 vs〈天花板〉1 vs 身分:L86「身分是 `_lint_new_key` 加同指紋第幾次出現」與「放行一處等於放行同檔同片段的每一處」並存。程式 L42244 `_lint_new_diff_claims`:同指紋的新增複本全都拿到**同一個** key(sha256 前 16 碼),放行檔也只認這個 key(L42533 `c.get("key") not in waivers`)。若 rule-hit 的 `seg` 帶序號,則 `lint-waive <seg>` 的 key 跟閘認的 key 對不上;若不帶序號,「第幾次」就沒用。〈範圍〉3 說「身分與放行用同一把鑰匙」,但身分(含序號)與放行鑰匙(不含序號)是兩把。S6「同檔同片段兩處時只印排在後面那一處」又假設材料只認一處,跟天花板 1「放行一處放行每一處」只在放行端一致,判定端(判一處是否適用於另一處)沒講。
2. 〈範圍〉5「出處不全規則判 real 只提醒不擋」vs〈天花板〉4「出處不全的 7 條判成真也不擋」vs d1「出處不全的 7 條判成真只提醒」:三處一致說不擋,但 L132 S3 與 L148 預期值表把「出處不全」當成型錄**列**屬性,而 7 是**規則**數(我用程式驗過:rules-hints 恰有 7 條規則對到「(出處不全)」列、rules-review 為 0)。一列可有多條規則、一條規則可對多列時(STATE-16 同列掛 review 與 hint 各一條)規則↔列的判法沒寫。目前 62 條規則各唯一對到一列,所以不衝突,但〈範圍〉沒寫這個前提,日後型錄一列多規則就會出歧義。
3.〈範圍〉7 vs 引用的出處:L94「門檻照情境題升擋的同一組數字(真陽性至少 20、誤報少於一成)」,但同一句前面的門檻是「準確率至少九成、real 佔七成以上、false 佔八成以上建議刪」。情境題(棧別提問表態閘 L64)只有「真陽性≥20、誤報<一成」,沒有「real 佔七成」「false 佔八成」兩個數字;這兩個是本計劃新立的,不是「同一組」。依據來源表 L126 也寫「升降門檻沿用情境題那組數字」。宣稱與實際不符。
4.〈範圍〉1/〈驗收〉S1 vs〈回退〉L161:S1 要求「沒有 `review` 段應照舊通過」;〈回退〉說舊版驗證器「當不認得的鍵報錯,要一併拿掉」。實際 L39616:舊驗證器對 value 不是 list 的任何鍵報「value 必須是命令列表」問題,而 `review` 的值是 dict,所以舊版會對有 review 段的 lint.json 報錯(說法對)。但回退節要求「一併拿掉」與〈做〉8「範本加 review 段兩條命令」並存:消費專案裝了範本後,回退本計劃提交等於讓所有消費專案 lint-check 變紅。回退節沒有講消費專案端的處置。
5.〈不做〉1「不在收工鉤子跑覆核命令」vs〈範圍〉2「`_lint_new_verdict` 跑 review 段」:程式 L42448 `_lint_new_verdict(worktree=True)` 會轉去 `_lint_new_wt_verdict`(L40914),收工鉤子走那條。計劃只說放在 `_lint_new_verdict` 一般路徑,沒說 `worktree=True` 那條要明確跳過 review 段;〈不做〉1 的保證是靠「沒改 wt 那支」隱含成立,沒寫成條款也沒測試(S1–S8 都沒有「收工鉤子不跑 review」的條款)。

## ④ 機械宣稱驗語意(最重要;計劃說/程式實際/相符或不符)

### 相符(5 條)
- A1 `_lintcheck_validate` 「照既有命令規則驗」:計劃說加 `review` 段並照規則驗;程式 L39607 現在逐 key 要求 value 為 list,會把 `review: {kt: [...]}` 報成「value 必須是命令列表」。**現況不認 review**,計劃是新增要改它。相符(計劃寫的是將改,不是現況)。注意:L39616 迴圈是 `for stack, cmds in config.items()`,新增 `review` 必須在這裡特判並遞迴驗,同時 `_lint_detekt_advisories`(L40075)、`--smoke`(L41068)、`_lint_android_ci_advisories`(只看 `kt`)都是以 isinstance(list) 跳過非 list,所以不會崩;但 smoke 不會冒煙驗 review 段命令(計劃沒提)。
- A2 表態那一道「沒有適用題時提早返回」:程式 L73…`_dispositions_verdict` 內 `if not app: out["blocked"]=bool(out["problems"]); return out`。**相符**。但「刻意不跑檢查命令」這半句:scripts/lumos 找不到任何「刻意不跑檢查命令」的註解或程式依據(grep 無);表態閘本來就沒有跑檢查命令的碼,不是「刻意」。理由欄有一句沒出處的歷史陳述,只當線索。
- A3 `doctor` 數 AI 放行:L4189–4213 與 `_lint_waiver_ai_unacked`(L41170 附近):`origin=="ai" and acked is not True` 才算;`lint-waive --ack --all` 需互動終端答 y(`_lint_waive_ack`)。**相符**;`_lint_waivers_ai_pending` 排除 `kt-situation:` 前綴,rule-hit 自動放行的 key 若不帶該前綴就算進一般清單 ✓。
- A4 `lint-waivers.json` 的 `origin` 欄:`_lint_waivers_add`(L42297)寫 `origin`、`acked=(origin=="human")` ✓;可直接傳 `origin="ai"` 寫入,不必經終端。**相符**。但 `_lint_waivers_add` 沒有「規則判定理由 ≥10 字」檢查(那在 `cmd_lint_waive`),自動放行要自己守,計劃沒講。
- A5 `_lint_new_key` 指紋語意:L42219 key=(rule, 檔名, 命中行片段正規化);工具沒附片段時自己讀;讀不到才降「~msg~」弱比對。**相符**於「同檔同片段同規則同指紋」的說法。

### 不符或有落差(11 條)

- B1 「`_lint_new_verdict` 在跑完一般段之後跑 review 段」(L85):程式 L42448 `_lint_new_verdict` 本身不跑命令,它呼叫 `_lint_new_tools`(L42584)→`_lint_new_run_cmds`(L42664)。命令清單來自 `_lint_new_cmd_targets`(L41979),只認 `lint_cfg[副檔名]`,不認 `review`。要改的是 `_lint_new_tools`/`cmd_targets`,不是 verdict 外層。計劃指的函式層級不對,但意圖可實作。**不符(落點)**。
- B2 「同一個時間預算與開關(`lint_new.gate`)」:`_lint_new_run_cmds` 內預算是 `budget_end - now < per_cmd_floor_sec` 就記 `undone kind=budget` 並**擋**(L42672)。review 命令若與一般段共用預算,review 段沒跑到預算會被歸成「擋」(hard_undone),而計劃 S7 與〈範圍〉6 說「覆核跑不出結果印『覆核沒跑』」。兩者對預算耗盡的處置(擋 vs 只講出來)不一致,計劃沒講預算耗盡走哪條。**落差**。
- B3 「review 命令的結果另放,不進『新增告警就擋』」(L84):`_lint_new_run_cmds` 把所有命令的 claims 併到 `base_claims/head_claims`,`_lint_new_diff_claims` 產生 `new`,`_lint_new_classify` 的 `hard = bool(out["new"])...` 一有 new 就擋(L42401)。要「另放」必須分開呼叫 `_lint_new_diff_claims` 並維持兩份;現況沒有這個分流點。**不符(現況無分流,需新建)**,計劃用「另跑、結果另放」一句帶過,實作面積被低估。
- B4 `_lint_new_verdict` 純函式假設:L42448 docstring「★這裡不寫帳★:要寫的治理帳放進 events,由 _codeloop_lint_new_step 寫」。計劃〈範圍〉5 `false` 要「自動記一筆 AI 放行(lint-waivers.json)」,若在 verdict 內做就破壞「判定函式只回傳」慣例;且 `_lint_new_wt_verdict`/`lint-new` CLI 也呼叫 verdict(L40217/L40253),會在唯讀預覽時寫放行檔。計劃沒指定寫放行檔的位置。**不符(慣例)**。
- B5 `blind-judge --template` 的材料結構:計劃說「多印一節『規則命中』」(L87)。程式 `_cmd_codeloop_bj_template`(L74121)材料=`_kt_bj_material(chunk, texts)` 的 `segments`;`_kt_bj_segments`(L74154)從 `_kt_situation_segments` 取情境段,**完全不跑 ast-grep**。要印規則命中,template 必須自己重跑 review 命令(兩份快照 + 時間預算 + 指紋比對)或從前一次 check 取結果;計劃沒講資料從哪來,也沒講 `--part`(每份 30 段 `_KT_BJ_PART_MAX`)是否把兩種材料混份(〈不做〉4 說分份印各派一席,但 `--template` 是一個旗標、一次印一份,沒有「只印規則命中/只印情境」的旗標設計)。**不符(現況無此資料路徑)**。
- B6 結果檔格式:計劃 L87「盲判交回 `{"type":"rule-hit","judgments":[{"seg","verdict","reason"}]}`」。程式 `_kt_bj_validate`(L74064)最外層只認 `segments`(`extra=set(doc)-{"segments"}`→報錯),每筆只認 `{seg, rows}`、rows 的票只認 `applies/followed/reason`。舊驗證器對計劃格式整份拒收。計劃要新增分支,但沒說是否共用 `_cmd_codeloop_blind_judge` 的「同一格已有值不算數」重複防護(L74205 skipped)與「整份都已有就回 2」。**不符(格式)**。
- B7 `--arbiter` 現況:`_kt_bj_validate` 對 role=arbiter 要求該格已有 `first`(L74100),`--disagreements`(L74121)的分歧來源是「作者表態 vs 第一盲判」。rule-hit 沒作者表態(計劃自己說),所以 `unsure` 的「交第二代理仲裁」要的挑格條件是「first 判 unsure」,不是現有的分歧判法;`_kt_bj_pick_rows(sg, mode, cells, author_rows)` 沒有這個模式。**不符(沿用不成立,要新增挑格模式)**。
- B8 治理帳讀寫:計劃 L87「記成治理帳 code-loop 閘、種類 blind-judge、多一個 type 欄;讀帳分流照 type,舊事件沒有這欄的照情境段讀」。程式:`_kt_bj_read`(L73867)→`_kt_bj_fold`→`_kt_bj_event_ok`(L73831)要求 `blind_judge` 為 `{seg:{rows:{列:票}}}` 且票只有 applies/followed/reason;不合整筆跳過。`_gov_situation_collect`(L17119)與 `gov --stats` 同樣只吃合格事件。所以:(a) 若 rule-hit 事件另用別的欄名,舊讀取會安靜跳過 ✓(〈回退〉說「會因欄位不合被丟掉」成立);(b) 但 `_GOV_FIELD_TYPES`(L17511)有 `blind_judge` 必須 dict、`role/seg/row` 必須 str、`origin` 必須 str——rule-hit 事件若要放 `judgments` 清單,是未登錄鍵(不驗,不崩);若沿用 `blind_judge` 欄放 verdict 結構則不過 `_kt_bj_vote_ok`。**部分相符**:回退說法成立,但「舊事件沒有 type 的照情境段讀」是描述將寫的新碼,不是現況。
- B9 `lumos gov --stats`:計劃 L94「每條規則列:判定幾筆、real/false/unsure 各幾筆、經人 ack 複查過幾筆、複查後判錯幾筆」。程式現況 `_gov_situation_collect` 只算情境題三方票(author/first/arbiter)與放行 origin 計數;**沒有任何「規則」維度**,也**沒有任何欄位記「人複查後判錯」**:`lint-waive --ack` 只把 `acked=True, acked_by, acked_at` 寫進放行檔(L41222),沒有 verdict 欄,而且 `--ack --all` 是整批標看過。因此「複查後判錯幾筆」與「判定準確率」從現有資料**算不出來**:人只能 ack「看過」,無法表達「這筆盲判錯了」。S8 的測試 `t_rule_review_stats_suggestion` 用「治理帳有規則判定與人 ack 紀錄」造資料,等於假設一個還不存在的紀錄欄位。**不符(最嚴重之一,見摘要)**。另外 `real` 判決的人複查更無路:real 的出口是 lint-waive(人放行)或改碼,計劃的升降規則「real 佔七成以上」只用判決分佈,但「準確率九成」只可能由 `false` 的 ack 結果算出,與 `real` 無關,所以「準確率≥九成且 real≥七成」把兩個不同母體混成一個門檻。
- B10 `sgconfig-hints.yml` 內容:計劃說兩份 sgconfig 是 review 段命令的目標(L75)。實際 `sgconfig-hints.yml`=`ruleDirs: [rules-hints]`、`sgconfig-review.yml`=`ruleDirs: [rules-review]` ✓;rules-hints 50 條全 `severity: hint`,rules-review 12 條全 `info`。但 lumos 的 `_lint_run_and_parse`(L41633)解 SARIF 時**不看 level**,全收;而 ast-grep 對 `hint` 級是否出現在 `--format sarif` 輸出**我無法驗**(本機沒裝 ast-grep)。計劃整個〈範圍擴大到 50 條提示級〉的前提是 hint 級有進 SARIF,需要一個實跑樣本證據。**未驗(標記風險)**。
- B11 型錄「出處不全」判定入口:計劃假設 lumos 可判「對應列標出處不全」。程式 `scripts/lumos` 對「出處不全」字串 0 處命中;只有 `configs/ast-grep/kotlin-android/check.py` 有 5 處。lumos 目前只經 `_kt_decision_table`(L38xxx)讀 D-n **決策表**,不讀主型錄表(STATE-16 等)。所以規則 id→型錄列→(壞寫法|標準寫法|後果)→出處不全,整條讀取路徑在 lumos 端不存在,要新寫型錄主表解析。我用腳本驗證了對得上:62 條規則各唯一對到一列、其中 hints 7 條對到「(出處不全)」列(與計劃 7 條相符)。**語意數字相符,現況程式無此能力**。

### 其他現況核對
- `lint-waive` 指紋語意:key 對 `(rule, file, 片段)` 的 sha256 前 16 碼;放行一個 key=同檔同片段每一處 ✓(對應天花板 1)。`lint-waive` 理由需去空白後 ≥10 字且有實字(L41254)——自動放行要自己守同一條,計劃沒提。
- `lint-waive` 的 origin 由 `_waive_origin_tty` 判:沒有互動終端=ai。意味著 AI 代理在 `real` 判決被擋時可以直接跑 `lint-waive`,得到一筆 origin=ai 的放行並通過閘(只留下 AI 放行待看記錄)。計劃 S3「判 real 用 lint-waive 放行後放行」把「真問題也能由 AI 自己放行」寫成預期值,沒有討論;與〈範圍〉5「real:擋」的強度不符(擋的是沒人放行前)。屬設計取捨,列給審查者。

---

## 最嚴重三條

1. ④-B9:`gov --stats` 的「人複查後判錯/準確率/升降建議」資料不存在。`lint-waive --ack` 只記「看過」,沒有判對錯欄位,且 real 判決沒有複查路徑;RETIRE-IF 與 S8、準確率九成門檻全建在這份不存在的資料上。
2. ④-B5/B6/B7/B11:盲判 `--template`、結果檔格式、`--arbiter` 與型錄「那一列」讀取,現況都只服務 D-n 情境決策表與 `{segments:[{seg,rows}]}`;rule-hit 要新增資料來源(要重跑 review 命令)、新格式、新的仲裁挑格條件、新的型錄主表解析。計劃寫成「多印一節」「沿用」,實作面積被低估。
3. ③-1 + ④-B3/B4:身分含序號 vs 放行鑰匙不含序號(同一批複本共用同一個 key);再加 review 段結果「另放」在現況 `_lint_new_diff_claims`/`_lint_new_classify` 沒有分流點、自動放行寫檔會破壞 `_lint_new_verdict` 不寫帳的慣例。

（次要但值得一提:②-3 的「41 筆」跟本 repo 實際 62 筆不符;②-1 壞連結 Android端到端驗收計劃;①-3「不適用時」欄不存在。）
