severity: major

審查結論:做 6 的指紋(算法、材料、讀法)沒寫清楚,照字面實作會做出永遠不命中的比對。做 5、做 2 的字面做法本身可行,但有三處銜接缺口。我只讀程式碼、沒改任何檔,也沒跑測試。主線 `scripts/lumos`、`check.py`、`test_lumos.py` 是用 `git show Lumos/main:…` 取到暫存檔讀的。

## F1 做 6 說「用 `_lint_new_key` 算指紋」,但它算出來的不是放行檔裡的格式
severity: major
blocking: 是。照字面實作會讓放行比對永遠不命中,功能靜默失效;S4 的正向案例才會抓到,反向案例照綠。
- spec 段落:做 6「指紋(用新增告警閘同一支 `_lint_new_key` 算)在放行檔裡的不算進分級」。
- 問題一:`_lint_new_key(claim, text_by_file)` 回的是 `(以 \x00 串起來的 規則/檔名/片段字串, 弱比對旗標)`。放行檔存的 key 是 `sha256(k)[:16]`,這個雜湊在 `_lint_new_diff_claims` 裡才做。`_lint_new_key` 的輸出直接拿去比放行檔,一筆都不會中。spec 沒要求抽出共用函式。
- 問題二:`_lint_new_key` 要 `text_by_file`(檔名對應行清單)。`pitfalls --diff` 的 lint 命中在 `_pitfall_diff_collect` 裡,由 `_lint_run_and_parse` 對工作樹的檔案跑出來。該處沒有任何 `text_by_file`,spec 沒說去哪讀。
- 問題三:讀不到檔、行號超出時,`_lint_new_key` 會退成弱 key(規則、檔名、`~msg~訊息`)。弱 key 對不上強 key 放行,結果是照舊全算,也不報錯。
- 問題四:只有「`_lint_aligned` 為真」(右端 ref 等於 HEAD 且工作樹乾淨)時,工作樹的檔案內容才等於閘比對用的頭版內容。不對齊時讀工作樹算出的指紋跟閘的不同。spec 沒限定只在對齊時套用。
- 命中版本:`pitfalls` 的命中來自頭版(工作樹)那一次掃描,沒有基準版。放行檔路徑 `.lumos/lint-waivers.json` 與讀法 `_lint_waivers_load`(壞檔回 `({}, 錯誤)`)現成可用。「壞掉照舊全算」靠 `{}` 自然成立,spec 沒寫明。
- 引句:「指紋(用新增告警閘同一支 `_lint_new_key` 算)在放行檔裡的不算進分級;放行檔讀不了就照舊全算」
- 佐證:`file: `scripts/lumos:42830` 的 `_lint_new_key``、`file: `scripts/lumos:42855` 的 `_lint_new_diff_claims``(有 `c["key"] = _hl.sha256(k.encode("utf-8")).hexdigest()[:16]`)、`file: `scripts/lumos:65166-65230` 的 `_pitfall_diff_collect``(沒有 text_by_file)。

## F2 「被逼代碼審」的前提只對手動執行成立,自動路徑本來就不算 lint 命中
severity: minor
blocking: 否。多做一件無害的事,但 spec 說它「解了」某個問題,這個說法站不住。
- spec 段落:做 6 括號「`pitfalls --diff` 也逐條跑 lint 宣告……作者已放行仍被逼代碼審」。
- 問題:所有自動路徑都帶 `--no-lint`,包括 code-loop 判定第 3 步的分級,以及 pre-push 的 advisory。只有手動 `lumos pitfalls --diff`(不帶 `--no-lint`)和 `loop capture-counts --from-pitfalls` 會把 lint 命中算進去。所以真正決定要不要過審的分級,從來不受 lint 命中影響。做 6 只改手動顯示的分級,以及 capture-counts 收割的 finder 來源。
- 修法建議:S4 與「為什麼要做」改寫成「手動顯示的分級」。
- 引句:「放行過的命中不推高審查分級(解 r1 正確性 F1:`pitfalls --diff` 也逐條跑 lint 宣告,不看放行檔,任何一筆新命中就判高風險,作者已放行仍被逼代碼審)」
- 佐證:`file: `scripts/lumos:75202`、`75350`、`75316`` 都帶 `--no-lint`;`file: `scripts/lumos:4177`` 的註解寫「所有自動路徑都帶 --no-lint」;`file: `scripts/lumos:20341`` 的 capture-counts 用 `no_lint=False`。

## F3 做 6 沒說「不算」是只從分級拿掉,還是連輸出清單、capture-counts 一起拿掉,另有兩處跟閘判新增不一致
severity: minor
blocking: 否。實作者能自己選,但不同選法會改變 `claims` 輸出與 capture-counts。
- spec 段落:做 6。
- 問題一:程式裡分級用的是 `_tier_claims`,輸出是 `all_claims = lint_claims + claims`,capture-counts 讀的是 `data["claims"]`。spec 沒指定從哪個清單拿掉。
- 問題二:不對齊時,gate-covered 的 lint 命中本來就不進分級,放行比對只在對齊分支有意義。
- 問題三:`pitfalls` 的「新增」判定是命中起始行落在新增行上。閘的「新增」判定是指紋差集(基準版出現幾次、頭版出現幾次)。兩者互不蘊含。例如搬動區塊後閘判舊、`pitfalls` 判新;閘不會給出放行指令,所以這種命中放行不了,分級仍會升高。spec 的「放行過的不算」覆蓋不到這一類。
- 引句:「`pitfalls --diff` 收 lint 命中時,指紋(用新增告警閘同一支 `_lint_new_key` 算)在放行檔裡的不算進分級」
- 佐證:`file: `scripts/lumos:65200-65240`` 的 `_tier_claims` 與 `all_claims` 分支。

## F4 做 5 只寫「對 `--config` 值是……的命令回不執行」,沒說比對的是原字串、真實路徑還是 samefile
severity: minor
blocking: 否。常見寫法都能擋住,邊角寫法會漏。
- spec 段落:做 5、S3。
- 問題一:`_lint_wt_allow` 先把 `$HOME/`、`${HOME}/` 換成家目錄,再 `realpath`,最後才是在工具鏈目錄內的判斷。新拒絕若放在 `realpath` 之後、只比 basename,`$HOME/`、絕對路徑、`..`、符號連結(指向的真實檔是 hints/review)都能擋到。若比的是原字串 basename,指向 hints 的符號連結會漏。
- 問題二:macOS 預設檔案系統不分大小寫,而 `realpath` 不校正大小寫。檔名寫成 `SGCONFIG-HINTS.YML` 時,basename 比對漏掉,ast-grep 實際打開的卻是同一個檔,於是每回合照跑。現有程式為目錄那段寫了 `samefile` 救濟,檔名這段沒有。
- 問題三:spec 寫的是只擋兩個名字,不是「只留 `sgconfig.yml`」。同目錄將來新增的設定(包括 spec 做 1 新增的 `sgconfig-unwired.yml`)若被消費專案宣告,收工會每回合跑,且 AI 是主要放行人。做 4 範本不宣告它,但沒機制擋。
- 回報行為:混合情況(`sgconfig.yml` 照跑、兩條被拒)下,`status` 是 `clean`。人讀輸出先印「✓ 沒有新增的告警」,最後才印「工作樹模式不跑:…」。`--json` 最後一行沒有 `wt_rejected`,鉤子看到的是 pass。這不是 fail-open,也不是擋下,只是靜默;這個行為既有,不是新問題。
- 引句:「對 `--config` 值是規則包 `sgconfig-review.yml` 或 `sgconfig-hints.yml` 的命令回「不在工作樹模式自動執行」,只留會擋的 `sgconfig.yml`」
- 佐證:`file: `scripts/lumos:41184-41280`` 的 `_lint_wt_allow`(`expanduser`、`realpath`、`commonpath`、`samefile`)、`file: `scripts/lumos:41559-41570``、`40874` 的 `wt_rejected` 輸出。

## F5 做 2 漏列會被新增的第四目錄打紅的既有測試
severity: minor
blocking: 否。實作時測試會紅,但 spec 的改動清單、錨簽範圍沒列。
- spec 段落:做 2、驗收條款(只列新測試)。
- 問題:既有 `t_kotlin_rulepack_samples` 有一段「規則目錄全空不准判通過」,只刪 `rules`、`rules-review`、`rules-hints` 三個目錄的 yml,再斷言要報「一條規則都沒讀到」。`rules-unwired/` 一旦有 8 條規則,這段斷言會變紅,必須把第四個目錄加進去。這要改 `scripts/test_lumos.py`,也就要走改測試檔的簽名流程。
- 其他既有案例我逐項核對過,不受影響:`t_kotlin_rulepack_messages_cite_catalog` 的 `kt-w`(沒有 `dir`、`severity: error`)、`kt-j`(info 放 `rules-hints`)、`kt-f`、`kt-i` 在新規則下仍報。
- 已核對:8 條出處不全規則(API-36、ARCH-3、UI-103、CO-37、FLOW-14、STATE-9、TEST-16、TEST-33)都在 `rules-hints/`、都是 hint 級,分佈 7 支檔(testing 兩條),與 spec 相符。
- 好例檢查:現行 `review-fp-` 豁免條件是 `rule_id in review_ids`。改成「覆核加 unwired」需要同步擴充 `review_ids`;`good_cases` 本身只看檔名前綴,不受影響。
- `_DIR_SEVERITY["rules-unwired"] = ("hint","info")` 後,嚴重度檢查的原因句要改,否則會誤導。spec 已列。
- 引句:「另外兩句寫死三個目錄的訊息(嚴重度與目錄不符那句、「一條規則都沒讀到」那句)把第四個目錄補進去」
- 佐證:`file: `scripts/test_lumos.py:126457`` 的 `for d in ("rules", "rules-review", "rules-hints")`;`file: `configs/ast-grep/kotlin-android/check.py:664-665`、`749`、`776``。

## 固定席逐條判
- `Systems/kotlin規則包`:不破壞宣告的行為。WHY「查不到的列標(出處不全),引用它的規則只准提示級」綁 `t_kotlin_catalog_rows_wired`,spec 說同一行改成「只准放 rules-unwired/」並保留該測試綁定。該測試只在一處提到「出處不全」(`shp2_i` 排除用),沒有驗「只准放 unwired」。新語意的守衛是 S1 的 `t_kt_rulepack_unwired_dir`,所以改字後該 WHY 的 `[test:]` 應補掛新測試。這是漂移,不是破壞,歸入 F5 的測試面。
- `Systems/linter精選目錄`:不影響。第 198 行「提示級規則預設不接……要用就另加一條宣告」是文字,spec 做 4 已明列改寫。

## 風險類逐類答
- 做 5 回報:既有的 `wt_rejected` 機制,不會變成擋下、也不會記成 fail-open,維持 clean(混合)或 `not-checked/deliberate`(全拒絕);不會誤印提醒讓人以為檢查過(後面會補印不跑的行)。路徑漏判見 F4。
- 做 6:見 F1、F2、F3。既有測試與推送前閘:放行檔不存在時 `{}`,分級完全不變。既有測試不帶放行檔,會維持原行為。
- 做 2:見 F5。

總結:最高等級為 major,blocking 共 1 條
