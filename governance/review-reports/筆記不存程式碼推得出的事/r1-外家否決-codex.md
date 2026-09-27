severity: major

## F1 留痕指令沒有足夠座標驗證報告完整性

severity: major
blocking: 是 —— 不補 immutable prepare manifest 與 diff 座標，實作者無法可靠判斷漏判、申訴或應綁哪批內容。
引句:「工具機械驗(每一行都有判定;附的程式位置那支檔真的存在、行號沒超出檔長」

1. 具體輸入：對 A..B prepare 出 10 行；審查員依規定回傳編號 1–9 的完整表格與合計 9。
2. record 只收到報告路徑，沒有 A..B、prepare 產物、原始行清單、目標 SHA 或第二席報告；它不知道原本還有第 10 行，也無法重算修改後的新增行集合與指紋。
3. 申訴同樣無法驗證：命令只有一個報告參數，沒有第二席卷證的輸入或其獨立性座標。
4. 照字面實作只能三選一：接受不完整報告、猜一個預設範圍，或依賴未定義的「最近一次 prepare」可變狀態；三者都會放錯或在平行會談中綁錯批次。
file: `governance/audits/2026-09-27-rtb-notes/judge-experiment/judge_prompt.md:14` 驗過的輸出格式只有編號、分類、信心、位置與理由，不含 diff range、輸入原文或 prepare 指紋。
file: `scripts/lumos:29969` 既有 code-loop 判定明確接收 diff range、目標 SHA 與分支。
file: `scripts/lumos:30342` code-loop check 把 diff、at-sha、branch 一併送進判定式；投稿宣稱照抄此機制，卻漏掉這些座標。

## F2 新分支與缺遠端物件時會把全庫舊筆記當成本次新增

severity: major
blocking: 是 —— 不另定 note-audit 的歷史基準，新分支推送會違反 d2 清整庫舊帳並卡住推送。
引句:「推送前與 CI 用同一支指令對整段範圍再跑一次」

1. 具體輸入：執行首次遠端分支推送，pre-push 收到 remote SHA 全零。
2. 現有 hook 對新 ref 或本機沒有 remote object 的情形，範圍固定為 empty-tree..local SHA；因此所有既有筆記都呈現為新增。
3. 在目前 HEAD 實跑同一範圍，得到 562 篇知識筆記、57,474 行新增內容，另有 146 個行號引用語法候選。第二層會要求審完整庫，第一層也會開始檢查舊行。
4. 治理帳沒有這個全庫指紋時，步驟五必擋；這不是投稿宣稱的每次幾十到幾百行，而是首次推分支即重審全部舊帳。
5. 相同失效也發生在 force-push 分岔且本機拿不到 remote SHA 的路徑。
file: `scripts/hooks/pre-push:36` 現行範圍函式明寫新 ref 或 remote object 不存在時掃全部引入內容。
file: `scripts/hooks/pre-push:40` 該分支實際回傳 empty-tree..local SHA。
file: `docs/lumos-toolchain-knowledge/Issues/筆記把程式現況寫進脈絡而漂移_rtb實測回饋.md:33` d2 明定舊筆記不回頭清，不做全庫清理。

## F3 程式碼圍欄是完整繞道

severity: major
blocking: 是 —— 不改排除規則，任何程式碼可推得的內容都能包進圍欄而避開兩層檢查。
引句:「列出範圍內新增的筆記行(去掉開頭欄位裡的連結、標籤、日期、狀態這類結構欄位,去掉程式碼圍欄)」

1. 具體輸入：新增一篇筆記，正文只有合法閉合的 text 圍欄，內文寫「目前有 53 個子命令，推送閘只在高風險執行」。
2. 該行不是程式行號引用、不是 done 計劃現況段，也不是 FACT 行，第一層三條全不命中。
3. prepare 明定去掉程式碼圍欄，因此第二層看見零行；步驟五依「沒有新增筆記行直接放行」通過。
4. 這是穩定、無需格式破壞的繞道，直接違反 d1、d5、d6 的內容級機械擋目標。
file: `docs/lumos-toolchain-knowledge/Issues/筆記把程式現況寫進脈絡而漂移_rtb實測回饋.md:27` d1 的目標是不留存程式碼推得出的內容，沒有圍欄例外。
file: `docs/lumos-toolchain-knowledge/Issues/筆記把程式現況寫進脈絡而漂移_rtb實測回饋.md:51` d5 要求新寫入的此類內容機械擋下。
file: `scripts/lumos:3218` 現有共用可見行解析器會完整辨識並排除圍欄內容，故此繞道可直接照既有 parser 穩定重現。

## F4 行號形狀會誤擋非程式證據

severity: major
blocking: 是 —— 不限定真正的程式檔，常見的文件佐證會被硬擋，作者只能刪掉證據或繞過 hook。
引句:「這種指向程式某一行的寫法。行號只要有人改碼就錯位,抽樣 12/12 都是這類」

1. 具體輸入：新增 Verification 行「前次錯誤見 reference.md:18」，該行不在圍欄、也不是引句行。
2. 投稿定義的形狀是任意檔名加副檔名再加數字，沒有要求路徑經 `_is_code_file` 或副檔名屬於程式碼；reference.md:18 因而被當成程式行號硬擋。
3. 這類位置記的是審查卷證或規範來源，不是程式碼可推得的現況。硬擋它擴張了目標，也會移除 PITFALL、Verification 所需的來源證據。
file: `docs/lumos-toolchain-knowledge/Verification/2026-07-31_接手者演練複審修復.md:5` 現有驗證紀錄以 reference.md:18 定位文件矛盾。
file: `docs/lumos-toolchain-knowledge/Verification/2026-07-31_slim-skill與readme落地.md:40` 現有驗證紀錄同樣用 reference.md:340 記錄已審查假陽性。

## F5 驗過的審查輸出無法滿足新 record 的位置契約

severity: major
blocking: 是 —— 不補負面與集合證據格式，record 會拒收驗過的報告，或逼審查員填無關位置才能過。
引句:「推得出與一半一半必須附一個程式位置。行數多就切批平行派。」

1. 判定定義明列「沒有 X」與「只有 N 種」為 CODE；這兩類需要全庫搜尋或集合計數，沒有一個單獨 file:line 能證明不存在或總數。
2. 驗過的 prompt 明許真搜後找不到位置時回報無位置並降低信心；投稿的新流程卻要求 CODE/MIXED 必附一個位置。
3. 實驗的真實輸出已出現目錄 glob、全庫 grep 0 筆與模組集合等證據，不符合「檔案存在且行號不超長」的單點驗證器。
4. 照字面實作會在主目標案例上卡住；若只驗任意 file:line 存在，審查員填一條無關位置也能通過，證據檢查變成假閘。
file: `governance/audits/2026-09-27-rtb-notes/judge-experiment/judge_prompt.md:8` CODE 定義明列不存在與數量主張。
file: `governance/audits/2026-09-27-rtb-notes/judge-experiment/judge_prompt.md:12` prompt 明許真搜後找不到位置時如實回報並降低信心。
file: `governance/audits/2026-09-27-rtb-notes/judge-experiment/judge_sonnet.md:6` 已驗輸出用整個 analyzer 目錄的 import 缺席作證，沒有單一行號。
file: `governance/audits/2026-09-27-rtb-notes/judge-experiment/judge_sonnet.md:27` 已驗輸出用全庫 grep 0 筆證明不存在。

## F6 對外送出的風險排除與實際資料流相反

severity: major
blocking: 是 —— 不釐清模型供應商信任邊界，功能會把私有筆記與程式碼強制交給外部模型。
引句:「已排除:對外送出:推送被擋是本機行為,不送任何內容到外部服務」

1. 具體輸入：私有專案新增含客戶名稱、法規限制或生產事故的筆記行。
2. prepare 把原文寫進派工檔；預設 Opus 審查員收到該內容，並依 prompt 讀取本機 repo 的程式碼。
3. hook 本身在本機不等於資料沒有外送；雲端模型取得 prompt 與讀檔結果就是外部資料流。
4. 消費專案若未授權把原始碼或事故筆記送給該模型供應商，這個必跑閘會造成未經核可的揭露。設計必須明列供應商、資料範圍與可用的本機通道，不能把此類風險標成已排除。
file: `governance/audits/2026-09-27-rtb-notes/judge-experiment/judge_prompt.md:3` 實驗 prompt 直接授權審查員讀取指定本機程式碼 repo。
file: `governance/audits/2026-09-27-rtb-notes/judge-experiment/judge_prompt.md:12` 審查員必須開檔核對並回傳程式位置，確認資料流不只包含筆記行。

## F7 外部審查員不可用時沒有合規逃生口

severity: major
blocking: 是 —— 不加有留痕的離線或人工出口，模型逾時、限流或服務中斷會卡死所有含筆記行的合規推送。
引句:「範圍內有新增筆記行、卻找不到指紋對得上的通過紀錄,就擋。」

1. 具體輸入：新增一行合法 CONTEXT；Opus 派工因限流、逾時或服務中斷無法產出報告。
2. 沒有報告就不能 record，pre-push 必擋；使用 no-verify 只能把未留痕提交送上遠端，CI 仍依同一條規則標紅。
3. 申訴不是出口，因為申訴還需要第二席外部審查員。
4. 投稿宣稱照抄的 code-loop 已有帶理由的 skip 留痕；本設計把 AI 閘擴到每次新增筆記，卻刪掉同型逃生口，形成服務可用性的硬依賴。
file: `scripts/lumos:30325` 既有 code-loop 同時提供 pass 與 skip。
file: `scripts/lumos:30332` code-loop 明講留痕有效範圍及重新記錄條件。
file: `scripts/hooks/pre-push:318` 現行推送閘向使用者提供帶理由的 code-loop skip 出口。
file: `.github/workflows/ci.yml:113` CI 會重跑留痕檢查並在 rc1 時使工作失敗。

〈開頭欄位、白話、依據、PRIOR-ART、RETIRE-IF〉已讀；對外服務與可用性問題見 F6、F7。

〈判定者能不能用:小實驗〉已讀；實驗輸出與新驗證契約的不相容見 F5。

〈第一層:提交時擋形狀固定的東西〉已讀；範圍與誤擋問題見 F2、F4。

〈第二層:推送前的筆記內容審〉已讀；留痕座標、繞道、證據與服務依賴問題見 F1、F2、F3、F5、F7。

〈規範文字跟著改〉已讀,無 finding。

〈條款〉已讀；S4–S8 無法覆蓋的失敗見 F1、F2、F3、F5、F7。

〈回退〉已讀,無 finding。

〈實務隱患〉已讀；錯誤排除與漏列風險見 F6、F7。

〈誠實界線〉已讀；一般延遲與樣本限制有揭露，服務完全不可用的硬阻塞未揭露，見 F7。

〈交叉引用〉逐一核對完成；目標與被引用章節均存在，judge prompt 的語意不相容已列 F5，無額外壞引用 finding。

相關節點核對：

1. `Issues/筆記把程式現況寫進脈絡而漂移_rtb實測回饋`：F2 直接破壞 d2 的舊帳不追；F3 直接破壞 d1、d5、d6 的內容級機械擋。
2. `Projects/Lumos定位_程式碼為主脈絡為輔_計劃`：F3 讓正文仍可保存程式碼現況，破壞檢討段要求的正文全範圍內容判定；F2 重開已明文排除的全庫舊帳。
3. `Systems/pitfalls-code-loop`：新閘若使用獨立 gate kind，不會覆寫既有 code-loop 判定；但投稿宣稱照抄時漏掉既有的 diff/SHA/branch 座標與 skip 出口，分別見 F1、F7。

實務隱患逐類核對：

- 守衛面：有，F1–F5 會造成放錯、擋錯或穩定繞過。
- Git topology：有，F2 覆蓋新 ref、缺 remote object 與 force-push 分岔。
- 對外送出與機密：有，F6。
- 外部服務可用性：有，F7。
- 效能與額度：一般推送成本已揭露並有 RETIRE-IF；新分支的全庫放大未涵蓋，已列 F2。
- 併發與多會談：無獨立 finding——spec 尚未定義共享暫存狀態；F1 要求改成顯式 immutable manifest 後可避免此風險。
- 不可逆：無——筆記刪改可由 git 取回，移除閘即可停止新阻擋。
- 金流：無——功能不讀寫付款、帳務或計費狀態。

總結:最嚴重 severity 是 major,blocking 共 7 條。