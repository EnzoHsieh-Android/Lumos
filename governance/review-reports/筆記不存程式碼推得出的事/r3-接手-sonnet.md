severity: major

# 審查對象
- Spec:`governance/review-reports/筆記不存程式碼推得出的事/r3-work.md`(第 3 版,凍結工作副本)
- Delta:同目錄 `r3-delta.patch`(r2→r3)
- 程式碼:clone-ns(scripts/lumos note-shape 家族、scripts/hooks/pre-push、.github/workflows/ci.yml)
- 鏡頭:整合/知識同步(三個月後接手會在哪裡撞牆)

以下依 spec 原文順序逐節記錄,無 finding 的節直接寫「已讀,無 finding」。

## 逐節閱讀記錄

### frontmatter(type/status/tags/lands_in/related)
見 F1。

### 白話 / 依據
已讀,無 finding。`[[Issues/筆記把程式現況寫進脈絡而漂移_rtb實測回饋]]`、`[[Projects/Lumos定位_程式碼為主脈絡為輔_計劃]]` 都存在。

### ★2026-09-27 拆分★ / ★第一層已上線★
已讀,無 finding。查證:`git cat-file -e ebb44369` 存在,`git log --oneline -5` 顯示 `ebb44369 docs: 筆記形狀擋收案,記下 CI 第一次跑綠` 緊接 `2bc14297 feat: 筆記新寫程式行號或沒寫來源的現況描述時,提交與推送會被擋`,跟 spec 說的「r3 前編排者把本篇改寫」時序一致。

### PRIOR-ART / RETIRE-IF / REVISIT
已讀,無 finding。三個借用對象都查證存在且語意相符:
- `lumos lint-waive`(`file: scripts/lumos:20572`)確實是「一條一個內容指紋、不綁版本」,`_lint_waivers_add` 簽名沒有版本欄位。
- `[[Systems/pitfalls-code-loop]]` 存在;`_gate_event` 的「寫失敗不改判定」契約查證屬實(`file: scripts/lumos:927-932`)。
- `[[Systems/筆記內容閘]]` 存在,`_ns_range_added`/`_ns_regions` 確實是 spec 說的「範圍裡每個提交各自新增的筆記行」與「行落在哪一區」的兩支函式(`file: scripts/lumos:23579`、`file: scripts/lumos:23500`)。
- `[[Systems/外部對照-code衍生wiki]]` 存在且內容與 spec 引用的論點(新鮮≠正確、無 oracle)一致。

### 判定者能不能用:小實驗
已讀,無 finding。`governance/audits/2026-09-27-rtb-notes/judge-experiment/judge_prompt.md` 存在,內容確認:CODE/CONTEXT/MIXED 三類定義、寫死 `/Users/enzo/rtb-mainwt`(Python)路徑——跟 spec S14「不能照抄、要換成被審 repo 的路徑與棧」的描述一致。

## F1 lands_in 指向的家明文排除本計劃

severity: major
blocking: 是 —— 違反 CLAUDE.md 鐵則 5(「改到的每支檔都得先有家」),而且目標節點的 `responsibility` 明文把本計劃排除在外,不是「還沒寫」而是「寫了說不管」,下一個實作者無法直接沿用,必須先解掉這個矛盾才能落筆說明。

Spec frontmatter 把落點指到 `Systems/筆記內容閘`:
引句:「Systems/筆記內容閘」

但這篇家節點的 `responsibility` 欄位原文是:
file: `docs/lumos-toolchain-knowledge/Systems/筆記內容閘.md:6`
（原文:「...不管程式檔歸屬（那是每支檔有家）、不管推送前 AI 審查員（第二層計劃）"）

`note-audit` 的 `prepare/record/check/decision-amend` 都要加進 `scripts/lumos`(同一支已有 37 篇節點聲稱管它的檔,`file: docs/lumos-toolchain-knowledge/Systems/*.md`(grep 命中 37 篇)),機械閘(`_home_map_from_notes`,`file: scripts/lumos:22666`)只認檔案路徑、不驗 responsibility 語意,所以不會被機械擋下——這正是風險所在:沒有機械擋,三個月後的人只會看着「這篇說『不管』」而不知道該不該直接改這篇的 responsibility、還是照 CLAUDE.md 鐵則 5 另開一篇新節點。Spec 全文沒有任何一句處理這個矛盾(對照〈做法〉〈回退〉〈實務隱患〉都沒提 home 節點怎麼辦)。

## F2 條款區開頭的舊條款編號對照寫錯,且原 S10 的保證被悄悄放棄、沒有替代條款

severity: major
blocking: 是 —— 對照表本身是錯的(可驗證的事實錯誤,不是判斷分歧),而且它掩蓋了一個真的被拿掉的保證(並行 record 兩筆都要完整落帳),新 S1–S17 清單裡找不到任何一條頂替它,〈實務隱患〉只用散文帶過、沒有 [test:],不符合本計劃自己「能寫成規則的走測試先行」的紀律。

條款區開頭寫:
引句:「原 S1–S4、S10、S13 已移到 [[Projects/筆記形狀擋_計劃]] 的 S1–S4、S7、S8」

逐一核對 `r3-delta.patch`(r2 版本的舊條款,即「原」)與 `筆記形狀擋_計劃.md` 現有條款:

1. 舊 S1(行號引用)→ 新 S1(`file: docs/lumos-toolchain-knowledge/Projects/筆記形狀擋_計劃.md:64`)概念相符,OK。
2. 舊 S2「FACT/FLOW/DEP 沒帶 `[src:]`」(`file: .../r3-delta.patch:84`)——實際內容對得上的是新 S3(`file: .../筆記形狀擋_計劃.md:66`,講 `[來源:…]`),不是新 S2(新 S2 是「釘版本寫法」,`file: .../筆記形狀擋_計劃.md:65`,跟 FACT/FLOW/DEP 無關)。
3. 舊 S3「新分支起點=分岔點」(`file: .../r3-delta.patch:85`)——對得上新 S4(`file: .../筆記形狀擋_計劃.md:67`),不是新 S3。
4. 舊 S4「新增行範圍含 summary/decisions,排除引句行」(`file: .../r3-delta.patch:86`)——對得上新 S6(`file: .../筆記形狀擋_計劃.md:69`),不是新 S4。
5. 舊 S10「兩個行程同時 record,兩筆通過紀錄都應完整落在治理帳且讀得回」:
   引句無法用(這句在 delta 檔,不在凍結工作副本內),改用 file 佐證:`file: .../r3-delta.patch:90`(原文:「兩個行程同時 record 時,兩筆通過紀錄都應完整落在治理帳且讀得回 [test:t_note_audit_record_concurrent_writes_land]」)。
   這條講的是**第二層 `record` 指令**的並行寫入保證,`筆記形狀擋_計劃`(第一層)完全沒有 `record` 這個概念,S7(`file: .../筆記形狀擋_計劃.md:70`,講「擋下訊息格式、不得改動筆記與暫存區、寫帳失敗不改判定」)講的是 note-shape 自己的擋下行為,兩者主題不同,不是同一件事「搬過去」。
6. 舊 S13「紀律範本 FACT/FLOW/DEP 那列寫 d3 收窄說法」(`file: .../r3-delta.patch:93`)——對得上新 S10(`file: .../筆記形狀擋_計劃.md:73`),不是新 S8(新 S8 講的是 `note_shape.gate` 設定來源與 doctor 提醒,`file: .../筆記形狀擋_計劃.md:71`)。

結論:六個「原→新」對應裡,只有第 1 條(S1→S1)號碼真的沒變,其餘四條(S2/S3/S4/S13)號碼都錯位,而舊 S10(並行寫入保證)在新的兩份計劃裡都**沒有著落**——它既不在 `筆記形狀擋_計劃` 的 S1–S12(那邊沒有 `record` 概念),也不在本計劃現在的 S5–S17 清單裡(本計劃現在的 S7 是「record 應自己重算待審集合...拒絕時不寫帳」,`file: .../r3-work.md:85`,講的是驗證邏輯而非並行寫入完整性)。

同時,r3 版本已經把 r2 版本原本的「加鎖」設計拿掉(見〈做法〉第二層第 5 點:「不另加鎖」),等於**在拿掉舊 S10 保證的同一次改寫裡沒有明講「這個保證被放棄了」**——`審計修正紀錄` r2 段落只說「治理帳寫入走讀回自驗加鎖(併發)」是 r1 折入的東西(`file: .../r3-work.md:127`),沒有一句說「r3 把這個加鎖拿掉、原本 t_note_audit_record_concurrent_writes_land 這條保證不再成立」。這正是題目要求盯的「補丁與原文銜接處的新不一致」。

## F3 併發風險段低估了單一寫入器被重用於大幅變大訊息的炸裂半徑

severity: major
blocking: 是 —— 這是〈實務隱患〉自己承認要面對的場景(「兩個會談同時...寫治理帳」),但描述的後果(「只會讓那筆紀錄讀不到、check 多擋一次」)跟被重用的既有寫入器的真實行為對不上,會影響到跟本功能無關的其他閘的紀錄。

〈實務隱患〉原文:
引句:「同時寫治理帳 → 沿用既有寫入器、不加鎖,黏成壞行時只會讓那筆紀錄讀不到、check 多擋一次」

`_gate_event` 的寫入是單次 `open(...).write(json.dumps(...) + "\n")`,沒有鎖(`file: scripts/lumos:927-931`)。這支寫入器原本服務的訊息都很短(一句話理由、幾個節點名),但 note-audit 通過紀錄要「列出這次判成脈絡的所有內容編號」,每個編號 12 個十六進位字(見〈做法〉第二層第 4 點與〈實務隱患〉「治理帳變大」段:「一次推送幾十到幾百個」「計劃轉 done 時可能上千行」,`file: .../r3-work.md:109` 與 `:121`)。一千個編號的單行 JSON 輕鬆超過幾 KB,遠超過作業系統對常規檔案 `write()` 的原子性保證範圍(該範圍通常只到單一頁/管線緩衝區大小);兩個行程同時各寫一筆這種大小的紀錄,交錯寫入不只會讓「那一筆」讀不到,還可能把兩筆內容切開重組,連帶波及**同時間任何其他閘**(anchor、code-loop、每支檔有家…都共用同一支 `docs/.governance-log.jsonl` 與同一支 `_gate_event`,`file: scripts/lumos:24033`、`:6599` 起的 `_KNOWN_GATES`)寫進去的那一行——也就是說,受害的不一定只是 note-audit 自己那筆,可能是隔壁一個完全不相干的閘的紀錄被拖下水。這個「炸裂半徑不只自己」的後果,spec 全文沒有評估。

## F4 第二層的推送前工作流沒有被放進 CLAUDE.md 的技能路由表,跟同量級的 code-loop 待遇不對稱

severity: major
blocking: 是 —— 這是本次審查明確要求的鏡頭(「skill 與紀律範本要改哪裡才會有人照做」),而 spec 給的答案(只在既有 skill 裡加一行)明顯輕於這個機制本身的重量,會直接影響三個月後的人會不會照著做。

〈規範文字跟著改〉原文:
引句:「lumos-project-notes 的收工與推送步驟加一行」

對照 CLAUDE.md 現有的技能路由表(`file: CLAUDE.md:75-80`):四行分別對應「理解既有系統/寫筆記」「跨專案業務規則」「設計 spec 審查」「分支要推之前、`pitfalls` 出 `tier: high` 的代碼審」→ `lumos-code-loop`。`note-audit` 跟 `lumos-code-loop` 是同一個量級的東西:都是**推送前會擋人、需要派一個獨立審查員、審完才能記帳放行**的機制(參照〈做法〉第二層 1–5 步跟 `lumos-code-loop` skill 描述幾乎同構)。但 `lumos-code-loop` 在 CLAUDE.md 拿到自己專屬一行(觸發條件是「分支要推之前」「pitfalls 出 tier: high」「指名 code loop」),`note-audit` 卻只被塞進 `lumos-project-notes` skill 內文裡的一行提示。三個月後的一個新會談被 `note-audit check` 擋下時,CLAUDE.md 的路由表(對話一開始就會讀到、是"必讀"的第一層資訊)裡沒有任何一行直接對到「note-audit 擋下」這個情境,而 `lumos-project-notes` 是一篇涵蓋範圍很廣的技能(讀懂系統、排查、對外支援、查 DB、寫筆記、巡檢、綁合約測試都在裡面),埋在其中一行不容易被「擋下訊息 → 該調用哪個 skill」這條路徑直接命中——這正是 CLAUDE.md 自己「遇到這些情境就調用對應 skill」表格存在的理由,note-audit 沒有進這張表,是機制重量與可發現性不對稱的落差。

## 做法各節其餘部分(範圍與行重用、逐行綁定機制本身、prepare/派審/作者處理/record/check/skip/消費專案 CI)
已讀,無 finding(除 F1、F3、F5 已列出的部分)。查證重點:
- `_ns_range_added`/`_nodehome_golive`/`_nodehome_clamp_base` 目前都硬寫死 `scripts/hooks/pre-commit`(`file: scripts/lumos:23603`、`:22946`),spec 說的「加一個掛鉤路徑參數」精準對到這三個呼叫點,不是漏項。
- `_ns_regions` 對 decisions 的「文字子欄 vs 結構欄」判定(`_NS_STRUCT_KEY_RE`,`file: scripts/lumos:23459`)是通用 key 白名單(僅 id/decided/valid/superseded_by/ended/decided_by/replaces 算結構),跟 spec 現在「decisions 的文字子欄」這種不列舉欄名的寫法(`file: .../r3-work.md:48`)一致;沒有沿用 r1/r2 那版列舉 `content/context/why_chosen/alternatives/trade_offs` 的舊寫法,是對的收斂。
- `code-loop` 既有的 `_codeloop_read_from_ledger` 是讀「工作目錄現在的檔案」(`file: scripts/lumos:29364`),不是讀某個 sha 的 git blob;note-audit 的 `check` 要求「只認被推送頂端提交裡的治理帳」(S9)是比 code-loop 現有模式更嚴格的新設計,不是照搬——但這是刻意的加強(避免「本機過、CI 紅」),`_nodehome_reader` 一類的按 sha 讀檔基礎設施已經存在(`_note_shape_eval` 就是這樣用,`file: scripts/lumos:23765`),可行。
- `lint_new.gate`/`note_shape.gate` 的值域都是 `(block, warn, off)`(`file: scripts/lumos:21015`、`:23456`),`node_home.gate` 其實是 `(on, warn, off)`(`file: scripts/lumos:22257`)——spec 說「值照鄰居…的叫法」把三個鄰居當同一套引用,實際上 `node_home` 的叫法不同;但 spec 自己選的值(`block`)跟另外兩個鄰居一致,不影響實作,只是引用不夠精確,夠不上獨立列 finding 的門檻(找不到會導致失敗的具體場景)。

## 上線前校準
已讀,無 finding。

## F5 prepare 的「已提交」用詞未釐清是否含未提交的本機紀錄,可能造成重複派審而非資料遺失

severity: minor
blocking: 否 —— 最壞後果是同一批內容被重派一次判定(浪費一次審查、多等一輪),不會漏審、不會誤放行,屬於「浪費但安全」的方向。

〈做法〉第二層第 1 點原文:
引句:「算出上面那批行,扣掉已經被已提交通過紀錄(或 skip)涵蓋的」

「已提交」若嚴格理解為「已經進了 git 歷史的提交」,則 `prepare → 派審 → record`(寫進 `docs/.governance-log.jsonl` 但尚未 `git commit`)之後,若同一個會談在 commit 之前再跑一次 `prepare` 想確認還剩什麼,`record` 剛寫入、尚未提交的那幾行仍會被列為「待審」,導致重新派一次判定者——不是資料遺失,只是多跑一輪。Spec 沒有明講 `prepare` 讀的是「目前磁碟上的 `docs/.governance-log.jsonl`」還是「HEAD 提交裡的版本」,兩者只有在這個「record 完但還沒 commit」的窗口期不同,值得在實作前把這一句的語意講清楚(改成「已寫進治理帳(不論是否已提交)」)。

## 條款 S5–S17
除 F2 指出的編號對照錯誤外,已讀,逐條核對條款文字與〈做法〉描述一致,測試名格式(`t_note_audit_*`、`t_note_lines_*`、`t_decision_amend_*`、`t_doctor_note_audit_*`)跟既有 `t_note_shape_*` 家族命名慣例一致,無 finding。

## 回退
已讀,無 finding。「note-audit 指令改成只印『已撤除』並回 0、永久保留」有既有前例可循(`file: scripts/lumos:17728` 附近的「已撤除 hook 的相容期空殼」寫法,雖然那是給 shell hook 用,概念可直接套用到 CLI 子指令上,沒有技術障礙)。

## 實務隱患
除 F3 已列出的併發低估外,其餘鏡頭已讀,無 finding:
- 守衛面:有申訴/skip/專案開關且都寫帳,方向正確。
- 對外送出:限定同家、不派外家席,查證跟既有「外家一律 Codex、判定者派無脈絡審查席」的模式一致,沒有多出的資料外流路徑。
- 可用性:走 skip,不用 `--no-verify`,方向正確。
- 治理帳變大:數字量級合理(約 300 KB 上限估計跟 25,282 行 × 12 hex 字元的量級對得上,沒有明顯算錯)。
- 已排除(不可逆、金流):合理,推送前擋、不碰金流。

## 誠實界線 / 審計修正紀錄
已讀。誠實界線裡沒有任何一句承認 F2 指出的「並行 record 完整性保證被拿掉」這件事,跟 CLAUDE.md 鐵則 4「承認風險要附回頭看的條件」的精神不合——這不是新增風險,是刪掉一條原本要測的保證卻沒有在檢討段落留下痕跡,補強了 F2 的嚴重性判斷,不獨立算一條 finding。

---

## 總結
最嚴重 severity:major。blocking(是)的 finding 共 4 條(F1、F2、F3、F4);另有 1 條 minor/不擋(F5)。
