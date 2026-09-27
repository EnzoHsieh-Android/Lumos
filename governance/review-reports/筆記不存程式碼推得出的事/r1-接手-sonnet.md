severity: blocker

〈frontmatter / 白話 / 依據 / PRIOR-ART / RETIRE-IF / REVISIT〉已讀,無 finding。

## F1 第一層擋行號引用,沒有豁免本 repo 既有、大量在用的出處引用寫法

severity: major
blocking: 是 —— 不改,任何人往 Verification/Issue 筆記寫新的一行「哪支檔哪一行改了什麼」出處紀錄都會被機械擋下,而這正是本 repo 現行、被鼓勵的留紀錄慣例,不是邊緣案例。

引句:「行號只要有人改碼就錯位,抽樣 12/12 都是這類」

S1 的豁免只列「程式碼圍欄裡的內容」與「引句:」行,沒有豁免「佐證/出處」型的 `檔名:行號` 引用——但這種寫法在本 repo 的知識圖譜裡是既有、大量、且被要求的慣例,不是意外殘留:
- file: `docs/lumos-toolchain-knowledge/Verification/2026-07-21_lumos-show讀取入口.md:28` ——「`reference.md:85` 44→49...`README.md:42` 44→49」,逐一交代改了哪個檔哪一行、改前改後行數,這是 Verification 筆記記錄「做完了、改了哪裡」的標準寫法。
- file: `docs/lumos-toolchain-knowledge/Verification/2026-06-23_check-t-sentinel.md:30` ——「`t_check_k`(`scripts/test_lumos.py:1300`)」,測試綁定用檔名:行號指出驗證位置。
- file: `docs/lumos-toolchain-knowledge/Verification/2026-07-05_pitfalls網搜補漏.md:31` ——反證通道明文要求「要 file:line」,`_impact_load_config:5573-5576`、`impact-hook.py:335` 是反證證據本身。
- 全庫粗算(`grep -rhoE '[A-Za-z_./-]+\.(py|md|json|sh):[0-9]+' docs/lumos-toolchain-knowledge/ --include="*.md"`):53 個檔命中此形狀,`Verification/` 底下就有 11 個檔在用。
- 這道審稿任務本身要求佐證行用 `file: `路徑:行號`` 格式(orchestrator 派工詞原文),`skills/lumos-code-loop/reference.md:570` 的席報告規則也明寫「審材外查證所得走佐證通道,格式 `file: `路徑:行號``」——本 repo 自己的審查慣例正在用 S1 打算擋掉的那個形狀。
S1 沒有替這類「出處/佐證」引用留門,等於同一個提交裡只要照現行慣例留一筆佐證紀錄就會被擋;真要照 d1 精神走,S1 至少要多一條豁免(像「引句:」行一樣),否則會逼著改寫這條在本 repo 已經穩定用了兩個多月的慣例,而 spec 通篇沒有提到這個代價或給替代寫法。

## F2 第二條件用字面比對「## 現況」判斷 done 計劃現況段,本 repo 目前幾乎不用這個標題

severity: major
blocking: 是 —— 機械閘會在本 repo 現有語料上大量漏抓,讓人誤以為「done 計劃現況段被收窄」已經被守住,實際上守不到大多數已完成計劃。

引句:「做完的計劃還留著現況段」

實測本 repo 語料(`docs/lumos-toolchain-knowledge/Projects/`):
- file: `docs/lumos-toolchain-knowledge/Projects/` ——113 個檔 `status: done`;其中標題「精確等於」`## 現況`(`grep -l "^status: done" ... | xargs grep -l "^## 現況$"`)是 **0** 個;連「以「## 現況」開頭」的寬鬆比對(`^## 現況` 前綴)也只命中 6 個。
- 相對地,同一批 done 計劃裡光是「## 進度」這個標題就命中 2 個(抽樣 15 個 done 檔裡,實際看到的標題是「## 進度」「## 落地」「## 落地紀錄」「## 落地後發現」「## 現況事實」「## 現況查證」「## 現況盤點」等十幾種變體,例如 `docs/lumos-toolchain-knowledge/Projects/Lumos定位_程式碼為主脈絡為輔_計劃.md` 用的是「## 落地進度與交棒」)。
- S2 的判準只講「「## 現況」那節」,沒有給一份可接受標題的清單或語意判定,對照 spec 自己引用的觸發依據——`docs/lumos-toolchain-knowledge/Issues/筆記把程式現況寫進脈絡而漂移_rtb實測回饋.md` 稽核的是 **rtb 專案**用「## 現況」的那 7 篇——這個標題字串是從 rtb 抄過來的,不是本 repo 的既有慣例。
本 repo 自己的圖譜裡已經記過同一種「字串清單擋不住還沒想到的說法」的失敗模式(`docs/lumos-toolchain-knowledge/Projects/Lumos定位_程式碼為主脈絡為輔_計劃.md` 檢討段:「這道守衛的形狀有隱憂...換句話說它擋得住已知說法,擋不住還沒想到的說法」)。S2 對「現況段標題」重犯同一個已經被記錄過的坑,而且是在自己 repo 的語料上就量得出來的落差,不是外部案例才會發生。

## F3 「開頭欄位」排除範圍語意不清,若照本 repo 既有用法理解會把 summary/decisions 一併排除,正好放過稽核指出的頭號漏洞位置

severity: blocker
blocking: 是 —— 若照這個歧義的其中一種合理讀法實作,第二層審查會完全看不到摘要行(WHY:/RULE:/PITFALL:/FACT:/KEY:)與 decisions 欄位裡的新增內容,而稽核 Issue 明講這兩處正是漂移最集中的地方,整套機制的核心目的就落空。

引句:「應排除開頭欄位裡的結構欄位與程式碼圍欄」

`lumos note-audit prepare` 只舉四個排除例子「連結、標籤、日期、狀態」,沒有明講 `summary:` 與 `decisions:` 是否算「開頭欄位裡的結構欄位」。這不是我臆測的邊界情形——CLAUDE.md 鐵則 2(本次會談系統提示裡逐字附上的專案規範)寫的是:「**開頭欄位用指令改**(`lumos set` / `append` / `decision-add`),別手改」,而 `lumos append` 就是用來加 WHY:/RULE:/PITFALL:/FACT:/KEY: 摘要行到 `summary:` 欄位、`decision-add` 是用來寫 `decisions:` 欄位——換句話說,在本 repo 自己的用語裡,「開頭欄位」這個詞本來就**包含** summary 與 decisions,不是只指 tags/日期/狀態這種簡單 metadata。而稽核 Issue 自己給的數據是:
- file: `docs/lumos-toolchain-knowledge/Issues/筆記把程式現況寫進脈絡而漂移_rtb實測回饋.md` ——「掛 WHY/RULE/PITFALL 標籤、內容其實是現況的摘要行 | 隨機 30 條約一半 | 其中 3 條已漂移 | 標籤讓讀者當成決策脈絡,不會去程式碼核對」,以及「rtb 摘要行前綴:WHY 184、RULE 91、PITFALL 142、FACT 1」——這篇稽核明白把「summary 摘要行」列為三個漂移熱點之一。
若 `note-audit prepare` 依循本 repo 「開頭欄位=frontmatter 整塊(含 summary/decisions)」的既有用語把它們當結構欄位剔除,第二層審查就只剩下正文與已完成計劃現況段可以看,恰好放過稽核指出佔比最高的那一類(WHY 417 行 vs FACT 1 行的失衡正是稽核裡「規則沒有減少現況描述,只是把它們改名成脈絡」那句話講的現象)。這個歧義不是我在猜——是 spec 用的詞跟 CLAUDE.md 自己定義的詞撞在一起,implementer 兩種讀法都說得通,但其中一種會讓整個第二層失去意義,spec 沒有明講要選哪一種。

## F4 判定者的校準樣本是乾淨、已切好句的單一斷言,跟推送時真正要餵給它的原始筆記行(常是夾雜多個斷言的長複合句)不是同一種輸入

severity: major
blocking: 是 —— 小實驗量出來的準度(opus 55/55、sonnet 54/55)是在「一句一個斷言」的輸入上量的,production 的 `note-audit prepare` 是逐行取原始筆記行,而本 repo 的摘要行慣例本來就是多斷言塞進一行,兩者不是同一個任務,準度不能直接套用。

引句:「改動它要重跑那 68 句的小實驗」

實際核對 `governance/audits/2026-09-27-rtb-notes/judge-experiment/judge_input.md`:68 句裡每一句都是稽核員手動抽出的「單一、已切好的短斷言」(例如「6. 錄製模式時限放寬,整段不超過 60 秒」「28. 花費上限每次展示 1 美元、每月 20 美元」),不是從筆記裡逐行原樣複製。而 S5 定義的 `note-audit prepare` 輸出是「範圍內新增的筆記行」,也就是原始 markdown 行——本 repo 摘要行的實際長相是一行塞多個子句、多種斷言類型混寫,例如:
- file: `docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md:linewise KEY 條目` ——單一 `KEY:` 行同時混寫「現況數字(檔案掃描 1446 條)」「決策理由(對齊時只有 3 條…)」「機制說明(分級問的是這次改動有多危險)」三種不同性質的子句,用分號串成一整行。
spec 自己在小實驗段也承認「真正難的是『一句話裡理由跟現況混在一起』,這類樣本太少」,但只把它記成誠實界線,沒有處理後果:S6 對「一半一半」的補救是「刪掉程式碼那部分,留理由」,這個補救動作預設一行只有兩段;本 repo 真實的複合行常常是三段以上交錯,單一「推得出/脈絡/一半一半」三分類貼在整行上,判定者要嘛把整行判成一半一半、要求作者手動切開(切開的判準 spec 沒給),要嘛在校準沒覆蓋到的輸入形狀上直接沿用校準時量到的準度——這兩種結果都跟 68 句實驗量到的數字對不上。

## F5 「已排除:對外送出」的理由跟本 repo 明文照抄的審查席派法(可派 Codex/Gemini 外家)互相矛盾

severity: major
blocking: 是 —— 這條判斷直接寫進「已排除」清單,等於宣告不用再回頭檢查;但它照抄的派工機制本身就包含把內容送到外家 CLI 的路徑,如果 note-audit 的判定者沿用同一套派法,「不送任何內容到外部服務」這句話當場不成立。

引句:「已排除:對外送出:推送被擋是本機行為,不送任何內容到外部服務(判定者是對話內派的審查席)」

PRIOR-ART 段自己講「判定者照抄無脈絡審查席的派法(乾淨 agent、只給原始問題不給結論)」——這是照抄 `lumos-code-loop` 的審查席機制,而那套機制明文允許、甚至在 tier=high 時要求外家 CLI 參與:
- file: `skills/lumos-code-loop/SKILL.md:40` ——「派辯方(預設 Codex `codex exec --sandbox read-only`;不可用退 opus...`scripts/external-seat.sh`(Gemini)只當備援」。
- file: `skills/lumos-code-loop/reference.md:101` ——「派 1 個 Codex 辯方...乾淨脈絡、不傳 reviewer 報告結論」。
note-audit 的判定者要讀的正是「筆記內容全文」(WHY:/RULE: 摘要行,含法規/人工核可/否決方案這類業務敏感理由——恰是 CLAUDE.md 定義圖譜該裝的那一層),如果比照被抄的機制把判定者派到 Codex(OpenAI 側 CLI)或 Gemini,這些內容就會離開本機送到外部供應商。spec 沒有明講「判定者這一席一律用同帳號內建模型、不得比照 code-loop 派外家」這個限制,只是籠統寫「已排除」——在它自己照抄的機制早就有外家派法先例的情況下,這句排除沒有交代清楚邊界,不能直接算「已排除」。

## F6(minor)第二層沒有比照第一層豁免「引句:」行,可能逼作者刪改逐字引述的證據

severity: minor
blocking: 否 —— 只影響少量引用他人原話又剛好涉及現況描述的筆記行,不會讓整套機制判錯方向,但會製造「為了過閘而竄改逐字引句」這種次要摩擦。

引句:「那是當時的輸出或別人的話,不是指路」

S1 明確豁免「引句:」行(理由是「那是當時的輸出或別人的話,不是指路」),但 S5 的 `note-audit prepare` 排除清單、以及第二層判定者的分類指令(判定者派工詞照抄 `judge_prompt.md` 的 CODE/CONTEXT/MIXED 定義),都沒有對「引句:」行給同樣的豁免。判定者只看內容類型,不看是不是逐字引述——若一段引句剛好轉述了程式現況(例如引述某人講「這支函式目前只處理曝光」),判定者會判成推得出/一半一半,S6 的補救「刪掉程式碼那部分」套用在逐字引句上就是竄改別人的原話,跟本 repo 自己的 quote-check 慣例(逐字引句不可改動,只能整句留或整句丟)衝突,spec 沒有處理這個交集。

〈規範文字跟著改(S9)〉已讀,無 finding——S9 要求的收窄措辭與現行 `scripts/templates/graph-discipline.md`、`CLAUDE.md` 現行 FACT 列(仍是舊版「以程式碼為準+查詢」開口)確實不一致,S9 正確指出了要改的地方,方向與 Issue 的 d3 裁定一致。

〈回退〉已讀,無 finding。

〈誠實界線〉已讀,無 finding(F4 已涵蓋校準樣本與生產輸入形狀不同這條,誠實界線段本身承認了樣本不足但沒有再往下推衍到 S6 補救動作失效這一步,已在 F4 裡補上)。

---
總結:整份 spec 最嚴重 severity 為 blocker(F3);blocking 共 5 條(F1、F2、F3、F4、F5),非 blocking(minor)1 條(F6)。
