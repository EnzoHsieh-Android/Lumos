severity: blocker

## 派工鏡頭固定節點逐條判(不是 F,先交代)

- `Issues/筆記把程式現況寫進脈絡而漂移_rtb實測回饋`:純決策/背景紀錄,沒有機械合約會被本計劃破壞。d1–d3 正是本計劃要落地的目標(現況描述收窄、`RULE:` 生命週期另案),不影響。
- `Systems/每支檔有家`:讀了整篇 KEY 行與 about_code。本計劃只「讀用」`_nodehome_code_kind`(是否程式檔的判定)與整套範圍演算法,不修改它們;該節點自己註記「判定改了要一起想小改動閘的擴散/落點與風險分級 light 這兩個既有消費者」——本計劃不改判定本身,只是新增一個呼叫端,不觸發那條警語,不影響。
- `Issues/治理帳多個寫入者都沒上鎖`:內容與本計劃〈治理帳寫入加鎖(移出)〉一節描述的移出理由、影響(「本計劃讓每次提交都寫一筆事件,頻率會變高」)完全對得上,那篇也確實記到了。不影響,而且是本輪唯一需要交叉核對的移出項,核對通過。

---

〈frontmatter〉已讀,無 finding

〈白話〉已讀,無 finding

〈依据〉已讀,無 finding

## F1 放行寫法的釘版本語法沒有對應的抽取邏輯,S1/S2 會互相打架

severity: blocker
blocking: 是 —— 不改,實作者會照 PRIOR-ART 字面把 `_node_code_ref_tokens` 當唯一抽取入口,寫出來的東西會讓所有「假放行」一律不擋,直接違反 S2。

引句:「不存在的路徑(舉例、別的專案)不擋,交給第二層。」

引句:「必須是至少 12 位的十六進位提交編號、在 repo 裡找得到、那個提交裡有這個路徑」

PRIOR-ART 只承認對 `_node_code_ref_tokens` 做兩個新增選項(認裸文字、認 `#L`),沒有第三個選項處理 `路徑@<提交>:數字` 這個新語法。我實際把該函式的核心邏輯抽出來對一個輸入跑了一次:

file: `scripts/lumos:19859` `_suffix_re = re.compile(r":([^/]+)$")` 只切掉整個 span 結尾的 `:數字`,不會處理中間的 `@`。

我用同一段邏輯(尾碼正則、`/` 判斷、top_dirs 過濾)對輸入 `` docs/foo/bar.py@1234567890ab:42 `` 實測,得到的 token 是 `docs/foo/bar.py@1234567890ab`(把路徑與提交黏成一個字串),不是分離的「路徑=docs/foo/bar.py,提交=1234567890ab」。

這代表:
1. 若照 S1 的「路徑在被檢查的版本裡真的存在」去查這個黏合後的字串,它永遠查不到(真實檔案不會叫 `bar.py@1234567890ab`),於是照 S1 明寫的「不存在的路徑…不擋,交給第二層」,這一整行會被判定為「不擋」。
2. 這對**合法**的釘版本引用沒有影響(反正不擋是對的結果),但對**不合法**的釘版本引用——例如作者寫 `docs/foo/bar.py@HEAD:42`(HEAD 會移動,S2 明文要求應照樣擋)——同一套邏輯一樣會把 `docs/foo/bar.py@HEAD` 當成「不存在的路徑」,一樣落入「不擋」。這直接違反 S2:「`HEAD`、分支名、標籤、相對寫法、找不到的編號應照樣擋」。
3. spec 只說「驗法寫死」,但驗法要先能從文字裡把「這是一次釘版本嘗試」抓出來,才有東西可驗——這一步的抽取邏輯完全沒有著落,PRIOR-ART 也沒有承認這是第三處新發明。

不能指出具體位置就不准臆測,所以我把可重跑的判定寫清楚:輸入含 `@`+疑似提交編號+`:數字` 且緊跟在一個含 `/` 的路徑後面時,現有抽取器不會拆開它,任何只依賴「擴充 `_node_code_ref_tokens` 兩個選項」的實作都會在這裡卡住。

## F2 CI 新分支首推「先抓所有遠端分支」在本 repo 沒有先例,且與 actions/checkout 預設行為衝突

severity: major
blocking: 是 —— 不改,實作者會誤以為這段可以照抄「每支檔有家」現成的邏輯,實際上那套邏輯從沒在 CI 跑過,直接搬只讀「這條 ref 自己」的 checkout 會讓演算法找不到任何遠端分支,S4 的 CI 分支要求無法成立。

引句:「前一版全零(新分支首推)時,那一步先把所有遠端分支抓下來、再用同一算法並排除這條分支自己的遠端參照。」

PRIOR-ART 聲稱「①「每支檔有家」的閘整套…新分支起點『不在任何遠端分支上的最早提交』」是全部借用的既有形狀,但這個演算法目前只在 pre-push(本機)跑過:

file: `scripts/hooks/pre-push:225` `_hold="$(git rev-list --topo-order --reverse "$_lsha" --not --remotes 2>/dev/null | head -1)"` ——這條路完全依賴本機 git 已經抓好的 `refs/remotes/*`。

而工具鏈自己的 CI 從沒呼叫過 `home check`(我對 `.github/workflows/ci.yml` 全文搜尋 `home check` 沒有命中),也就是「每支檔有家」在 CI 語境下沒有任何先例可借;「先把所有遠端分支抓下來、再排除自己的遠端參照」是一段全新邏輯。而且目前的 checkout 設定:

file: `.github/workflows/ci.yml:14-16` `- uses: actions/checkout@v4` 搭配 `fetch-depth: 0`——這只抓「這次觸發的那條 ref 自己的完整歷史」,不會建出其他分支的 `refs/remotes/origin/*`(actions/checkout 預設只 fetch 觸發用的那個 ref)。同一支 workflow 裡遇到「前一版全零」的既有先例是直接退回空樹,不是抓遠端分支:

file: `.github/workflows/ci.yml:109` `EMPTY=4b825dc642cb6eb9a060e54bf8d69288fbee4904` 及其後 `case "$BEFORE" in 0000000000000000000000000000000000000000|"") BEFORE="$EMPTY";; esac`。

「排除這條分支自己的遠端參照」這句話本身在整個 repo 裡也搜不到任何既有寫法(`grep -rn "排除.*遠端\|refs/remotes" scripts/lumos scripts/hooks .github` 只命中 pre-push 那一行 `--not --remotes` 本身,沒有「排除自己」的既有實作)。這不是不能做,而是 PRIOR-ART 段落把它包裝成「借既有形狀」,實際上是要新寫一段 CI 專屬的 git 操作(至少多一步 `git fetch origin '+refs/heads/*:refs/remotes/origin/*'`),沒人在條款裡承認這是新東西,容易被實作者低估工作量、或誤植進「不需要驗證,反正是借來的」的心態裡漏測。

## F3 `lumos lint` 現有實作只掃 summary 欄位,S3 的「同一行同判定」在正文不成立

severity: major
blocking: 是 —— 不改,寫在正文的 `FACT:`/`FLOW:`/`DEP:` 行會被 note-shape 擋,但 `lumos lint` 完全看不到、永遠不會給出對應的警告,S3 的等價承諾對正文位置的行是假的,測試 `t_note_shape_current_state_prefix_requires_source` 若涵蓋正文情境會直接證偽這條款。

引句:「對整篇、note-shape 對新增行,判的是同一套。」

計劃在〈範圍與行〉明講新增行的範圍「落在正文、開頭欄位的 `summary` 區塊…算」——也就是 FACT:/FLOW:/DEP: 若寫在正文(不在 summary 欄位裡),note-shape 一樣要查。但既有的 `lumos lint` 呼叫鏈只把 `summ`(summary 欄位文字)餵給規則函式:

file: `scripts/lumos:5037` `warns.extend(context_marker_warnings(summ))` ——`summ` 是從 frontmatter 的 `summary:` 欄位切出來的文字。

file: `scripts/lumos:3002` `def context_marker_warnings(summary_text):` 這支函式的簽名與呼叫點都只認 summary,沒有第二個呼叫點去掃正文(`grep -n "context_marker_warnings" scripts/lumos` 全檔只有定義與這一處呼叫)。

所以如果作者把 `FACT:` 行寫進節點正文(工具目前並沒有機制禁止這麼做,`SYMBOL_RE`/`SYMBOL_NAMES` 本身不限制出現位置),note-shape 會照〈範圍與行〉的規則查核並可能擋下,但 `lumos lint` 對同一份檔案、同一行文字完全不會產生任何警告——兩者判定不一致,直接跟 S3「`lumos lint` 對同一行應給同樣判定」矛盾。要成立,`context_marker_warnings` 的呼叫點必須也涵蓋正文,但〈做法〉與〈紀律範本改寫〉都沒有提到要改這個呼叫點,只提到「改既有 `_CONTEXT_MARKER_RULES` 的 FACT 規則並加上 FLOW、DEP」——這只解決規則內容,沒解決掃描範圍。

## F4 skill 的 reference.md 已經有第二份定義,且範例本身示範了新規則要擋的寫法,計劃沒有排進同步範圍

severity: major
blocking: 是 —— 不改,新人照 skill 現有範例寫 `FACT:` 行,寫出來的第一句就會被剛上線的 note-shape 擋下,而且沒人知道要去改哪裡,直接製造誤擋抱怨、餵大 RETIRE-IF ① 的分子。

引句:「skill 裡只指路、不放第二份定義。」

計劃〈紀律範本改寫〉只提到改 `scripts/templates/graph-discipline.md` 一份檔,並宣稱 skill 不放第二份定義。但實際上 `skills/lumos-project-notes/reference.md` 現在就放著一份具體範例,而且這個範例正是新規則要淘汰的寫法:

file: `skills/lumos-project-notes/reference.md:410` `| \`FACT:\` | 現況描述(要求見上一節) | \`[以程式碼為準] 門檻 180 秒;查:grep FULL_SWEEP_SECONDS …\` |`——這一格範例完全沒有 `[來源:…]` 標記,是舊規則「以程式碼為準+查詢指令」的示範。

file: `skills/lumos-project-notes/reference.md:425` `- **Systems**: WHY + RULE + PITFALL 為主;FLOW/DEP 只寫指針,現況描述照〈寫筆記時〉標「以程式碼為準」`——這句話本身現在就是對的(指向紀律範本),但只要紀律範本改寫,這句「照〈寫筆記時〉標『以程式碼為準』」在字面上仍然成立(它沒寫死具體語法),真正會過期、變成錯誤示範的是 410 行那個具體範例格——`[以程式碼為準] …查:…` 這個具體形狀,新規則上線後(S3)會被 note-shape 擋下(缺 `[來源:…]`)。

計劃的 S10 只驗「紀律範本的 FACT/FLOW/DEP 那列」與「各專案注入的紀律區塊」是否與範本一致,完全沒有觸及 skill 本身既有的第二份範例——「散落的示範」不是「注入的紀律區塊」,S10 抓不到它,計劃全文也沒有一句提到要動 `reference.md`。

〈做法-範圍與行〉除 CI 子句(F2)外其餘已讀,無 finding

〈做法-兩條規則〉除規則一放行寫法(F1)、規則二 lint 等價性(F3)外其餘已讀,無 finding(回傳碼、開關與跳過、golive 標記字串、`_gate_event` 契約皆已對照程式碼核實:`scripts/lumos:22181` `_NODEHOME_GOLIVE_MARK = "home check --staged"` 印證同一套「掛鉤內找標記字串」手法可以無衝突地換一個新字串用在 note-shape 上;`scripts/lumos:856-932` `_gate_event` 的閘名白名單、`hard`/`head_sha` 參數、寫帳失敗回傳值行為都跟計劃描述一致;`scripts/lumos:22879` 起 `_nodehome_config(..., from_snapshot=True)` 印證「設定從被檢查版本讀、工作樹未暫存的 off 關不掉」的既有實作真的存在)

〈治理帳寫入加鎖(移出)〉已讀,無 finding(與 `Issues/治理帳多個寫入者都沒上鎖` 交叉核對一致,見上方節點逐條判)

〈紀律範本改寫〉見 F4

〈消費專案的 CI〉見 F2(同一套演算法在此重複出現,不重報)

## 條款逐條核對

- S1、S2:見 F1,兩條款字面上互斥(S1 的「不存在不擋」與 S2 的「假冒釘版本仍應擋」在共用同一套路徑抽取邏輯時無法同時成立)。
- S3:見 F3(`lumos lint` 等價承諾)、以及已驗證為真的部分——「帶 regen 的筆記寫 `[來源:部署]` 不應被重建守衛當成檔案路徑」這句我實測過:`scripts/lumos:4270` `SRC_REF_RE = re.compile(r"\[src:\s*([^\]]+?)(?::(\d+(?:-\d+)?))?\s*\]")` 只認半形 `[src:`,不會比對到全形前綴 `[來源:`,所以這句子成立,不算 finding。
- S4:除 F2 提到的 CI 子句外,推送前起點演算法(`_hold`/`_hold^`)與上線點截斷(`_nodehome_clamp_base`)兩段我都在 `scripts/hooks/pre-push:218-234`、`scripts/lumos:22864-22876` 核對過,行為與描述一致,無 finding。
- S5、S6、S7、S8、S9:核對 `_nodehome_merge_own_changes`(`scripts/lumos:22676`)、`parse_decisions`(`scripts/lumos:12904`,confirm `id`/`decided`/`valid`/`superseded_by` 確實是既有結構鍵,見 `docs/lumos-toolchain-knowledge/Projects/指令索引與情境測試_計劃.md` 的 `id: d1` 範例)、pre-commit 的 rc1-only 擋法(`scripts/hooks/pre-commit` Gate H 段 `[[ "$nh_rc" -eq 1 ]] && exit 1`)後,皆與描述一致,無 finding。
- S10:見 F4(範本本身的異動沒問題,但 skill 既有第二份範例被漏掉)。
- S11:已讀,無 finding。

〈回退〉已讀,無 finding(第 3 點「指令先留一版空殼、下一版再刪」與第 4 點「FLOW/DEP 判準與抽取器兩個選項留著但預設關閉不影響既有行為」都可執行,無矛盾)

〈實務隱患〉已讀,無 finding

〈誠實界線〉已讀,無 finding

〈審計修正紀錄〉已讀,無 finding

---

總結:最嚴重 severity 是 blocker(F1);blocking 共 4 條(F1 blocker,F2/F3/F4 major)。
