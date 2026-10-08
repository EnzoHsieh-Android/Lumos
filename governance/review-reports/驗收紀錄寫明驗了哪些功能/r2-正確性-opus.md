severity: major

# r2 正確性席(opus)——驗收紀錄寫明驗了哪些功能_計劃

實驗環境:`git clone --shared` 到 scratchpad/vr-r2/exp-correct-opus-r2/repo(HEAD da03ec07),臨時圖譜 exp-correct-opus-r2/vault、vault2(Systems/A、Systems/sub/B、Systems/無障礙設定支援、Projects/P,加幾份 Verification);以 SourceFileLoader 載入 `scripts/lumos` 直接呼叫 `parse_frontmatter` / `link_target` / `Env.resolve` / `fmt_list_item`,照做法第 1 點字面寫了一支模擬判法(sim.py:①整值 fullmatch → `link_target` → `resolve` → 落在 `Systems/` → 有斜線時 `link_target` 結果 == 解析結果去 `.md`;②`無` 照 `_slot_replacement_err` 先例);doctor 與 new 用 `--vault` 指臨時圖譜跑。repo 本身沒動。

## F1 `無 <理由>` 這條出口一定撞上 doctor 1/4 孤兒(硬 issue),1/4 的建議又叫人掛到 Systems,照做觸發新的「多掛」提醒、照提醒拔掉又回孤兒
severity: major
blocking: 是
引句:「這份沒驗任何功能、正文全是指路的,建好後 `lumos append <新紀錄> system_refs "無 <理由>"`」
file: `scripts/lumos:1414`(orphans = Verification 且 incoming 為 0、只豁免 superseded)
file: `scripts/lumos:1434`(沒帶 --suggest 時 1/4 走 `warn`,算 issue;建議句「找到它驗證的 Systems 並補進 verified_by」)
file: `scripts/lumos:19200`(`new verification --plan` 只在新紀錄自己寫 `plan_refs`,不在計劃那側寫任何回指)

1. 實測:Verification/2026-10-03_none `status: pass`、`system_refs:` 一項 `無 本篇沒有驗任何功能正文只是指路`、正文「現況見 [[Systems/A]]」,沒有任何筆記連到它 → 跑 `lumos --vault vault doctor`:1/4「有 2 份驗證紀錄沒被任何筆記引用」列出它,`doctor --ci` rc=1。1/4 的 incoming 跟 `system_refs` 無關,本計劃上線後照樣這樣。
2. 一份「沒驗任何功能」的紀錄,唯一會連進來的就是功能那側的 `verified_by`——而 `無` 正是宣告「沒有功能該掛它」。所以照 NEW_HINT 這句做(建檔不帶 `--systems`,或只帶 `--plan`)必定是孤兒。只有剛好用 `--systems Projects/P` 建檔(計劃掛 verified_by)才逃得掉,計劃全文沒提這條路。
3. 1/4 給的建議是「找到它驗證的 Systems 並補進 verified_by」;`--suggest` 現況實測推薦 `Systems/A.md [本篇正文連向(…可 sync-verified-by)]`(就是那條指路連結)。設計的 S11 只把第 1 種線索換成 `system_refs` 列的功能(`無` → 空),plan_refs 與 feature 兩種線索照舊,仍會推一篇 Systems。
4. 照建議做 `lumos append Systems/A verified_by "[[…none]]"` → 不再是孤兒,但命中做法 2 的新軟提醒「功能的 `verified_by` 列了某份有宣告的紀錄,而那份的 `system_refs` 沒列這個功能」→ 叫人 `lumos remove Systems/A verified_by …` → 拔掉又回到第 1 步的孤兒硬 issue。工具自己的三段訊息互相打架,而起點是工具自己教的寫法。
5. 預期:設計要定 `無` 紀錄在 1/4 怎麼算——例如有宣告 `無` 時 1/4 改叫人把計劃掛上(`--systems Projects/P` 或 `lumos append <計劃> verified_by`)、推薦改推 `plan_refs` 指的計劃而不推 Systems;或明定 `無` 紀錄豁免孤兒檢查(要寫理由)。NEW_HINT 那句要一起改,並補一條條款+測試釘住「`無` 紀錄照建檔提示做完,doctor --ci 不擋」。另外 NEW_HINT 是無條件印的:用 `--systems Systems/A` 建檔的人照它再 append `無` 會變成「`無` 跟連結混用」寫壞,提示句要限定「建檔沒帶任何 Systems 時」。

## F2 `無` 的判法沒定「無」後面要不要分隔、理由要不要有實字;照引用的先例實作,開頭是「無」的純文字功能名會被當成合法的「沒驗任何功能」宣告,靜默關掉檢查
severity: minor
blocking: 否
引句:「②整份清單只有一項、是 `無` 加至少 4 個字的理由」
file: `scripts/lumos:3894`(`_slot_replacement_err`,即計劃引用的 `[被取代:無 <理由>]` 先例:`v.startswith("無")` 且後面非空就收,不要求分隔)
file: `scripts/lumos:26052`(`_nodehome_resp_ok`:既有「至少 N 字、要有實字」的判法)

1. 照先例 `startswith("無")` + 去空白後 ≥4 字模擬:`無障礙設定支援`(圖譜裡真有 Systems/無障礙設定支援,作者忘了加 `[[ ]]`)→ 判成 `無` 合法、理由「障礙設定支援」→ 不要求任何反向登記、也不進「寫壞」標題。這正是本輪要消滅的「寫壞的形狀被默默當成沒驗」,只是換成功能名以「無」開頭的那一類(無障礙、無痕、無人機、無線…)。若改用「純文字路徑」那條判,同一個輸入就會報寫壞——兩條規則對同一輸入給相反結論,設計沒定先後。
2. `無 ....`、`無 TODO`、`無 待補理由` 都過「至少 4 個字」;既有 `_nodehome_resp_ok` 有「要有實字」的判法,這裡沒沿用。
3. `無　本篇只是指路`(全形空白)、`無:本篇只是指路`、`無本篇只是指路` 在先例寫法下都收;如果實作者改用 `startswith("無 ")` 則全部判壞。設計要明寫一種。
4. `無 見 [[Systems/A]] 只是指路`(理由裡點名哪條是指路,非常自然的寫法;`fmt_list_item` 寫入、`parse_frontmatter` 讀回都是單一項,實測)算不算「`無` 跟連結混用」沒定——S3 的「`無` 跟連結混用」可讀成「同清單另有連結項」或「這一項裡有連結」。
5. 預期:定成「`無` 後接至少一個空白(含全形)、理由 ≥4 字且有實字;理由內可提連結」之類一條規則,並在 S3 測試列 `無障礙設定支援`→寫壞、`無 ....`→寫壞、全形空白→收、理由含連結→收(或反之,但要寫死)。

## F3 「路徑要跟解析結果一致」沒定比法:大小寫、Obsidian 的部分路徑、`.md` 都會兩種實作兩種結果;照字面相等比,裸名大小寫不同收、路徑大小寫不同卻判壞
severity: minor
blocking: 否
引句:「而且連結有寫路徑時路徑要跟解析結果一致(防 `[[Projects/A]]` 被檔名救成 `Systems/A`)」
file: `scripts/lumos:626`(`resolve`:有斜線時先精確比 `t + ".md"`,找不到就退回取最後一段、用 `by_stem`(小寫鍵)找)

1. 模擬結果(Systems/A、Systems/sub/B 存在):
   - `[[a]]` → 收(by_stem 不分大小寫)。`[[systems/A]]` → 解到 Systems/A.md,但寫的路徑 `systems/A` ≠ `Systems/A` → 判壞。同一篇、同樣大小寫打錯,有沒有寫資料夾結果相反;現行 3/4 兩者都認。
   - `[[sub/B]]` → 解到 Systems/sub/B.md,`sub/B` ≠ `Systems/sub/B` → 判壞。⚠ Obsidian 對帶斜線的連結是比路徑結尾,這種部分路徑在 Obsidian 是有效連結(判不準 Obsidian 版本差異,但至少 lumos 的 2/4 不報它)。
   - `[[Systems/B]]`(功能後來被搬進 Systems/sub/)→ 判壞;現行 3/4 靠 stem 退回照認。這個判壞可以接受,但它會讓「搬資料夾」這種操作一次把所有宣告它的紀錄變成 doctor --ci 擋推,計劃的「誤擋」段沒列這種情境。
   - `[[Systems/A.md]]` → `link_target` 去掉 `.md` 後才相等;若實作者拿 `fm.group(1)` 原文比就判壞。
2. 預期:明寫比法——「`link_target` 結果去 `.md` 後,與解析出的 rel 去 `.md` 逐字相等(分大小寫)」或「是解析結果的路徑結尾」二選一,大小寫與裸名一致處理(裸名也查 `by_stem` 是否只有大小寫不同的命中);S5 測試列 `[[systems/A]]`、`[[sub/B]]`、`[[Systems/A.md]]` 的預期。

## F4 `new verification --systems` 寫進 `system_refs` 的字串與「落在 Systems/」怎麼判沒定;macOS 上大小寫不同的路徑會建檔成功,寫出的項被 F3 的規則自己判壞
severity: minor
blocking: 否
引句:「只把其中落在 `Systems/` 的寫進新紀錄自己的 `system_refs`(走 `cmd_append`,照 `plan_refs` 那段)」
file: `scripts/lumos:19122`(`_norm_rel` 只去 `.md` 再補 `.md`,不正規化大小寫)
file: `scripts/lumos:19148`(存在檢查用 `(env.vault / rel).exists()`,在不分大小寫的 APFS 上會過)

1. 實測(本機 macOS):`lumos --vault vault2 new verification 2026-10-03_case --systems systems/A` → rc 0,`Systems/A.md` 多了 `verified_by: [[Verification/2026-10-03_case]]`。
2. 照設計「照 `plan_refs` 那段」,寫法會是 `[[{rel 去 .md}]]` = `[[systems/A]]` → 依做法 1 路徑要一致 → 判壞、算 issue、下一次 push 被 `doctor --ci` 擋。工具剛回 rc 0 就產出自己會擋的狀態(r1 F3 同一型,換了入口)。
3. 若實作者改用 `rel.startswith("Systems/")` 判「落在 Systems/」,`systems/A.md` 不算 → 不寫 `system_refs` → 紀錄回到從正文推,使用者以為宣告了其實沒有,零訊息。
4. Linux CI 上 `exists()` 會擋,所以只有本機建得出來、CI 才炸。
5. 預期:定成「每個 `--systems` 先 `env.resolve`(或比對 `env.notes` 的真實 rel),用解析出的正規 rel 判是否在 `Systems/`,寫進 `system_refs` 的也用正規 rel」;S8 補一個大小寫不同的輸入。

## F5 孤兒推薦改用共用函式,但共用函式對 stale/fail 回 None,而 1/4 的孤兒名單刻意包含 stale/fail;None 時推薦怎麼走沒定
severity: minor
blocking: 否
引句:「(doctor 1/4 的 `--suggest` 那段)對有宣告的紀錄改用它列的功能」
file: `scripts/lumos:1413`(註解:superseded 豁免孤兒,「stale/fail 不豁免:待重驗,orphan 提醒仍有用」)
file: `scripts/lumos:1423`(對每個孤兒呼叫 `_suggest_systems_for_orphan`)

1. 輸入:Verification/2026-10-03_stale `status: stale`、`system_refs: [[Systems/A]]`,沒人連它。現況實測 `doctor --suggest` 把它列為孤兒並推薦 Systems/A。
2. 照做法 1,`_verification_system_targets` 對它回 None(「呼叫端跳過」)。照做法 3「對有宣告的紀錄改用它列的功能」:直接解包 `(declared, targets, bad) = …` 會 TypeError,整個 `doctor --suggest` 崩;寫成「None 就跳過」則 stale/fail 孤兒失去推薦,違反 1/4 註解要保留的用途;寫成「None 就退回 `n.targets`」又會推正文指路連結。三種實作都說得通,結果三種。
3. S11 只測有宣告的孤兒,沒涵蓋 stale/fail。
4. 預期:明寫推薦端「判宣告與否看 `system_refs` 鍵、不看 status」(或共用函式拆成「狀態判斷」與「目標判斷」兩支),並在 S11 加一筆 stale 孤兒的預期。

## F6 「跳過哪些狀態只留這一份」不成立:1/4 孤兒豁免與 E1 失效背書各有自己一份、而且分大小寫;共用函式轉小寫後,同一個 `Fail` 在 3/4 算失效、在 E1 算有效
severity: minor
blocking: 否
引句:「兩邊與孤兒紀錄的推薦都改用它,跳過哪些狀態也只留這一份」
file: `scripts/lumos:1416`(1/4:`status_of(...).strip() != "superseded"`,不轉小寫)
file: `scripts/lumos:2147`(E1:`vst in ("stale", "fail", "superseded")`,不轉小寫)

1. 輸入:V `status: Fail`、`system_refs: [[Systems/A]]`,A 的 `verified_by` 列了 V。改後:3/4 經共用函式判 V 失效、不構成義務;多掛提醒也因 None 跳過;E1 用 `"Fail"` 比 → 不算死背書、不報。結果 A 掛著一份失效驗收當背書,沒有任何一段講——3/4 註解寫的「跟 E1 打架」換了個方向發生。
2. 輸入:V `status: Superseded`、沒人連它 → 共用函式判作廢(3/4、sync 都跳過),1/4 用分大小寫比 → 仍列孤兒、算 issue。
3. 預期:把 status 正規化(去空白、轉小寫)與跳過集合收成一個小函式,1/4 豁免、E1、共用函式三處都用;或在「做」裡老實寫只統一了三處、另兩處留著,並在條款 S10 補 E1 與 1/4 的大小寫預期。

## F7 多掛提醒的改法字串會對不上既有登記;紀錄的項寫壞時,同一個功能還會被唸「多掛」,叫人拔掉真的登記
severity: minor
blocking: 否
引句:「改法給 `lumos remove <功能> verified_by "[[紀錄]]"` 或把它補進紀錄的 `system_refs`」
file: `scripts/lumos:17339`(`edit_fm_remove` 用 `link_target` 逐字比,保留路徑,`[[X]]` 與 `[[Verification/X]]` 不相等)

1. 實測:Systems/C `verified_by: ["[[2026-10-03_none]]"]`(裸名寫法;本 repo 291 筆裡有 1 筆,消費專案比例未知),跑 `lumos remove Systems/C verified_by "[[Verification/2026-10-03_none]]"` → rc 2「裡沒有」。多掛提醒若照 sync-verified-by 的慣例印解析後的完整路徑,改法照抄就失敗。要印功能那側的原文項。
2. 輸入:V `system_refs: ["[[systems/A]]"]`(F3 判壞)、A 的 `verified_by` 列了 V。宣告集合是空的 → 同一次 doctor 同時印「system_refs 寫壞了」(issue)與「Systems/A 多掛了 V,`lumos remove Systems/A verified_by …`」。後者叫人拔掉一條其實正確的登記;先照它做的人,修好 `system_refs` 後又變成 3/4 漏登記。
3. 預期:多掛提醒的改法印原文項;紀錄有寫壞項、且某寫壞項解析得到這個功能時,不列多掛(或標「先修寫壞那段」)。S6 補這兩個輸入。

最高等級:major,blocking 共 1 條
