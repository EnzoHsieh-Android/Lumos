severity: major

- 開頭 frontmatter／決策(d1–d3):已讀,無 finding——d1/d2/d3 與正文 S3/S4/S5/S9 用語一致,決策脈絡與下方條款對得上。
- 為什麼(這批的來源):已讀,無 finding——關鍵數字已抽查:`docs/lumos-toolchain-knowledge/Systems/客人端決策層.md` 實地核對,about_code 確實只有 1 支(`src/core/state.js`)、plan_refs 掛了 2 份計劃(spec 稱 3 份,含另一份桌邊送單前端計劃,數字對得上);mOrangePos/Citrus_KDS 的「40 篇/30 篇全數沒填 about_code」經 `grep -rl "^about_code:"` 實測為 0/40、0/30,與 spec 決策 d3 的引用數字一致。
- 世界上怎麼做的(PRIOR-ART):已讀,無 finding——CODEOWNERS/diff-cover/Nx 三個形狀是外部事實主張,不在本 repo 可查證範圍,且「零依賴自建」與 CLAUDE.md 的 `python3 零依賴` 慣例一致。
- 名詞:見 F4(程式檔判定「同一份清單」的宣稱)。其餘定義(家、別人的檔、新違規)已核對 `_about_code_key`/`_about_code_path` 實作,一致。

### F1 lumos home check 沒有專案層級停用開關,只能逐次 --no-verify
severity: major
blocking: 是 — 不改的話,消費專案想「先關掉這道閘、等圖譜整理完再開」時無路可走,只能每個提交手動繞過。
引句:「逃生說明跟既有那幾道一樣」
file: `scripts/lumos:16211` `_STACK_QUESTIONS_GATE_VALUES = ("all", "high-only", "off")` ——同一支工具鏈對另一道效能檢核閘(`stack_questions.gate`)明文提供 `.lumos/config.json` 層級的 off 開關,`node_home.*` 卻只定義 `ignore`/`max_files`,沒有等價的 gate/off 鍵。
本案新提出的唯一逃生路是逐次 `--no-verify`,跟既有「一次性繞過」閘同天花板,但沒有像 `stack_questions` 那樣「整案先關掉」的選項——對正在趕工、想先跳過這整套規則的消費專案是真實缺口。

### F2 繞過零留痕,關掉之後無法跟「舊帳」區分
severity: major
blocking: 是 — 不改的話,沒人能事後判斷這道閘是「在擋」還是「被 --no-verify 繞過很久了」,治理帳對這個問題是啞的。
引句:「這跟既有那幾道閘同一個天花板」
`--no-verify` 跳過整支 git hook,S27 承諾的「擋下與放行都記進治理帳」在此情境下完全不會執行(hook 本體沒被呼叫,不是 hook 內部判斷放行)。而 S28 的「舊帳」提醒與「新違規被繞過後累積的違規」在 doctor 輸出裡長得一模一樣(都只是「沒有家的檔」清單變長),兩種情況無法區分——d3 已經預期舊帳會很長(兩個 Android 專案 100% 無家),這正好讓「閘被繞過」的訊號被「本來就有的舊帳」蓋掉,是本案獨有的疊加風險,不是既有閘單純的「零留痕」問題重複。

### F3 S4 與 S12 對「status 欄位改動」的風險分級互相矛盾
severity: major
blocking: 是 — 照字面實作,例行把某節點標成 stale(REVISIT 到期的正常動作)會在該節點是唯一家的情況下擋下提交,這正是決策 d1/d3 想避免的誤擋。
引句:「家那篇被刪或改成作廢／過期」
S12 明文把 `status` 列為規則三豁免的「簿記欄位」(「只動 verified_by、plan_refs、related、tags、aliases、updated、status 這些簿記欄位的不算」),但 S4 把「改成作廢／過期」(即 status 改成 superseded/stale)列為規則一的硬擋觸發條件之一,而名詞「家」的定義本身就是「狀態不是作廢或過期」。同一個 status 欄位變動,規則三判它是無害簿記、規則一判它是要擋的家被拔除——這條路徑(節點被 REVISIT 標成 stale,而它剛好是某些檔唯一的家)沒有被 S4/S12 任何一條特別排除。CLAUDE.md 鐵則 4 本身就要求 REVISIT 到期要能被機械處理,是這個工具鏈的常態操作,不是邊緣案例。

### F4「程式檔判定跟改程式要動圖譜那道閘同一份清單」與現況不符
severity: major
blocking: 是 — 若實作者照字面找「那一份清單」直接 import,會發現沒有單一可 import 的來源,容易誤用另一份不同的清單、或另開第五份副本,重蹈本案自己在 S7 警告的「兩套算法一定分岔」。
引句:「那道閘同一份副檔名清單加首行」
file: `scripts/test_lumos.py:7591` `t_code_exts_four_lists_agree` ——「改程式要動圖譜」目前不是「一份清單」,是四份各自維護、靠測試釘住一致的副本(`scripts/hooks/pre-commit`、`scripts/hooks/post-commit`、`scripts/hooks/claude/check-graph-sync.py`、`scripts/hooks/claude/impact-hook.py`),四份都不在 `scripts/lumos` 裡、也互不 import。
file: `scripts/lumos:3278` `CODE_EXTS_T = {".cs", ".py", ... ".dart"}` ——`scripts/lumos` 裡唯一現成的副檔名常數是給 Check Y 符號查核用的 `CODE_EXTS_T`,跟 CODE_EXTS_RE 內容不同(少 `.sh`/`.ps1`/`.c`/`.cpp`/`.h`,多 `.dart`/`.cjs`/`.mts`/`.cts`),不是同一份清單,誤用會讓 `lumos home check`(必須活在 scripts/lumos 裡,因為是新 CLI 子指令)判準跟 Gate 2 悄悄不同。

### F5 doctor 新增三段的插入位置未指定,與剛發生過的同源事故正面相撞
severity: major
blocking: 是 — 不指定插入位置,照現有測試的切法,插進錯的區段會讓既有的軟段截斷測試翻紅或悄悄把新段內容算進舊段計數。
引句:「健檢多三段提醒（不擋、rc 不變、照既有軟提醒的截斷）」
file: `docs/lumos-toolchain-knowledge/Systems/節點範圍與索引守衛.md` KEY 行「這三段★必須排在 [E3] 之後、[H] 之前★:既有那支『軟段預設只印三條』的測試切的區段是『[S] 到 [E1]』,插在中間會讓它把新段的內容也數進去而翻紅」——這正是本案引用的同一篇姊妹計劃(2026-09-10,寫在本案前一天)踩過並記錄下來的事故,而 S28 完全沒提插入位置。
file: `scripts/test_lumos.py:6105` `t_doctor_soft_sections_truncate_by_default` ——就是姊妹節點提到的那支測試,S28 若不對齊這個位置限制,大機率重踩同一顆雷。

### F6 規則撤回時,已寫入的 about_code/responsibility/lands_in 沒有回滾路徑
severity: major
blocking: 是 — 不寫清楚的話,規則三被證明誤擋過多而「改回提醒或放寬」時,那些為了通過檢查而硬塞進 about_code 的檔案關聯會變成永久污染,而且沒人知道哪些是真的、哪些是被逼出來的。
引句:「後者比例高就代表誤擋多,改回提醒或放寬」
回頭條件段自己承認規則三「這案最沒把握」,且驗收方式是去數「有幾次是把檔加進 about_code 而不是改寫回位置」——換句話說,spec 自己預期會有一批 about_code 是「為了過閘硬加」而非「這篇真的在講這支檔」。`固定席扇出降權_計劃` 明文 about_code 是「未來語意欄位的基礎」,這批灌水資料會污染那個下游用途,而 `about_code revert`(`scripts/lumos:11345` `cmd_about_code_revert`,「整批撤銷某天的 about_code 預標」)只處理批次預標寫入,不處理「人為了通過 home check 而手動加」這種來源,規則被撤時沒有對應的清理/降級手段;`responsibility`、`lands_in` 兩個新欄位同樣沒提規則撤回後要不要清掉或允許留白過期。

落點段(contract-check,依 LUMOS-SPEC 指示對節點 `Systems/節點範圍與索引守衛` 逐條判):不影響其宣稱合約。該節點的 ★INVARIANT★ 明文「範圍判準只看一篇有幾條合約(門檻 10)……不看提到幾個檔」,本案「範圍外」一節明確保留這條合約不變,規則四(about_code 支數上限)是另立的獨立判準,兩者作用的欄位/合約互不重疊,本案自己也只打算在該節點補一條決策說明分工——不改其合約行、不改其測試。

- 邊界(S31–S32):已讀,無 finding——`-z`/`errors=` 的處理慣例有最近提交(`b4926d9c`/`1f28cd6b`)實證存在,不是空話;S32 的 2 秒門檻是可重跑的 manual 驗收,合理。
- 讓規則被看見(S30):已讀,無 finding——`NEW_HINT`(`scripts/lumos:12309`)、`scripts/templates/graph-discipline.md` 均存在,是可編輯的真實目標。
- 驗收怎麼跑:已讀,無 finding——逐一核對 30 個 `[test:...]` 標記命名,`scripts/test_lumos.py` 內目前均不存在(非重複宣稱),且 `-k` 關鍵字子字串比對均能命中對應測試名。
- 審計修正紀錄:留白,已讀,符合「設計審後補」慣例,無 finding。

總結:最高 severity major,blocking 共 6 條
