severity: major

鏡頭:接手(明天只拿第 2 輪凍結版實作;照提醒字樣實際改寫;8 週後量升級門檻;條款寫成測試)。
實驗環境:`git clone --shared` 到 /tmp/ngs/r(只讀原 repo),用 /opt/homebrew/bin/python3 跑 `lumos note-shape --staged`、`lumos drift scan`、`lumos drift check --diff`,並把量測程式 `classify_v3` 對 S1 全部例句跑過一次(S1 的 11 個「算」、10 個「不算」與程式逐句一致,無 finding)。
改寫實驗:對圖譜真句(`Systems/core-invariant-baseline.md` 摘要裡的 KEY「scripts/lumos 尚無 baseline 子指令」與 TEST「未寫測試」)照提醒字樣改寫成 `REVISIT:[when-symbol:…]`、`REVISIT:[when-test:…]`、`REVISIT:[when-file:…]`:摘要區塊內的條件式行 note-shape 放行、lint 0 問題、`drift scan` 與 `drift check` 判得動;寫錯的形狀(`[[ ]]`)被既有規則擋下。下面只列踩到洞的。

## F1 「上線提交」的指令列出的最新一筆不是「從無到有」那一筆
severity: major
blocking: 是
引句:「列出的提交裡最新、且該提交之後定義存在的那一個」
file: `scripts/lumos:26680`
1. 〈做法〉7 口徑要用 `git log -S _ns_negation_hints --format=%H -- scripts/lumos` 找上線提交。`-S` 列的是「出現次數有變」的提交,不是「定義從無到有」的提交:之後任何一個只多加一處呼叫、註解或引用該名稱的提交也會列進來。
2. 實測同形狀的既有函式:`git log -S_ns_revisit_violations -- scripts/lumos` 列出 02ea9745(9/30,只多了一處引用)與 a6207c3e(9/29,真的新增定義);`git log -S"def _ns_revisit_violations"` 只列 a6207c3e。照字面「最新、且之後定義存在」會選 02ea9745,起點晚一天。
3. `_ns_negation_hints` 有定義處、`_note_shape_eval` 呼叫處、測試與筆記(scripts/lumos 之外的不算,但 scripts/test_lumos.py 不在 `-- scripts/lumos` 範圍)——實作分幾個提交推上去,起點就會漂到最後一個動到這個名字次數的提交,8 週窗口與「上線後的提交」樣本數(≥30)都跟著算錯。
4. 改法方向:口徑要寫成「`-S'def _ns_negation_hints'` 或用 ast 判定義有無,逐提交找最近一次從無到有」,並寫明要不要納入回退再重上。

## F2 照做率、噪音、準度都是從「沒被照做的殘留」量的,倖存者偏誤沒寫進門檻
severity: major
blocking: 是
引句:「資料來源:重放的會提醒列。抽法:隨機抽 30 行,照報告第 5 節判真假。」
file: `governance/eval/negation-revisit/neg_revisit_measure.py:320`
1. 提醒的效果是「寫的人看到後當場改寫成條件式行」;改寫後那一行是 REVISIT 行,`scan_note` 直接 `continue`(只累加 `revisit_lines`),不會出現在「會提醒列」。所以重放的會提醒列只剩兩種人的句子:沒看到提醒的(`--no-verify`、沒裝掛鉤、agent 沒讀 stderr)與看到了決定不理的。
2. 後果一,第 3 條照做率:抽的 30 行全是殘留;當場就改好的(真正的照做者)不在分子也不在分母,量到的是「拖延或事後補」的比例,結構上偏低。RETIRE-IF ①「照做率不到兩成就撤」會因此被偏低的數字誤觸發;升級門檻 ≥50% 反而永遠難達到。
3. 後果二,第 2 條噪音:重放看到的「有提醒的提交」比實際印過提醒的少(被當場改掉的不算),而且門檻的對照數字(工具鏈 36%、rtb 32%)是上線前、沒有人被提醒過的歷史,兩者口徑不同,不能直接拿 35% 比。
4. 後果三,第 1 條準度:殘留裡「看一眼判斷是誤報所以不理」的比例被放大,準度抽樣被壓低;要 ≥70% 升級門檻更難。
5. 〈做法〉7 開頭只承認「歸因不了」,沒講這個方向性偏誤。需要在口徑補一句:用哪個資料來源補上「當場改掉」的那批(例如 note-shape 在提交前印提醒時本機留計數,但〈範圍〉不做③明講不寫帳;或改抽「提醒後 N 天內被改寫成條件式行的句子」用 git 歷史反推),否則 8 週後三個數字(準度、噪音、照做率)沒有一個能直接拿來裁。

## F3 第 4 條的資料來源「重放時新增行裡回 cond 的行」量測程式不會輸出
severity: major
blocking: 是
引句:「抽法:上線後新寫的條件式回頭條件行(重放時新增行裡 `_revisit_split` 回 `cond` 的行)」
file: `governance/eval/negation-revisit/neg_revisit_measure.py:320`
1. 〈做法〉7 口徑把重放定義成「量測程式 `scan --renames` … 取 `funnel_v3` 的會提醒列」。`scan_note` 遇到 REVISIT 行(cond/date/bad 任一種)只做 `stats["revisit_lines"] += 1` 就 continue,輸出檔的列裡沒有任何 REVISIT 行,`funnel_v3` 也沒有。
2. 所以 8 週後的人要量第 4 條「綁錯事件 < 10%」,第一步(列出上線後新寫的條件式行)量測程式做不到;要另寫程式(用 `_revisit_split` 對每個上線後提交的新行列出),而 spec 說的是用現有重放。接手的人要自己猜要新增什麼、輸出格式是什麼、跟 `drift scan --at` 的哪一欄對(路徑加原文?)。
3. 另外 `drift scan --at <主線頂端>` 列出的是「整份圖譜」所有已成立的條件,不是上線後新寫的那批;要有「取交集」步驟(路徑+行文對得起來嗎?行被搬移或改字後對不上),spec 沒寫。
4. 改法方向:在量測程式加 `--emit-revisit`(或在 `scan` 輸出加一種列)並把交集口徑寫進〈做法〉7 第 4 條。

## F4 「綁錯事件」只量得到誤成立的,永遠不成立的看不見
severity: major
blocking: 是
引句:「綁 symbol 常會永遠不成立或誤成立」
file: `scripts/lumos:26310`
1. 〈做法〉8 自己承認綁 symbol 常會永遠不成立。但第 4 條的抽法是「用 `lumos drift scan --at` 列出條件已成立的,逐條判是不是真的發生」——只看已成立的;永遠不成立的條件(名字猜錯、路徑寫錯、綁的事件本來就不會在該檔出現)`drift scan` 根本不會列。
2. `[by:]` 到期由 doctor E5 唸,但 E5 不區分「事還沒發生」與「條件永遠不成立」,量測那天沒人算這一類。
3. 後果:綁錯比例被系統性低估;RETIRE-IF ③「綁錯事件超過一半就撤」與升級門檻「綁錯 < 10%」兩個方向都不可信(撤的門檻很難觸發、升級門檻很容易過)。
4. 需要補一個抽法:對上線後新寫的條件式行(全部,不論成立與否)逐條人工判「這個條件綁的是不是那句講的事件」,或至少對「已過 [by:] 仍未成立」的那批單獨計數並判。

## F5 `when-symbol` 只有 Python 判「定義」,其他語言只判「名字有出現」;字樣例子偏偏用 .tsx
severity: major
blocking: 是
引句:「判的是**有沒有定義**——函式、類別或模組層指定,不是名字有沒有出現」
file: `scripts/lumos:27144`
1. `_DriftProbeTree._defines`:非 Python 檔(`_drift_probe_is_py` 為假)在名稱整字出現於全文時就直接回 True,不管是不是定義、是不是註解或呼叫。只有 .py 與 python shebang 檔才走 ast 判定義。
2. 實測:建 `web/a.ts` 內容只有 `// getFooBar is not implemented yet`,筆記寫 `REVISIT:[when-symbol:getFooBar][by:2026-12-31] …`,`lumos drift scan` 立刻列成「[probe] 條件已經成立」(推送時會被 drift check 擋)。
3. 「X 尚未實作」這類句子,X 常已被別的檔呼叫、引用或寫在 TODO 註解裡——在非 Python 專案,條件寫下去就成立,當次推送被擋(誤成立);提醒字樣第四行的「寫完先 drift scan」能救一半,但作者只會得到「條件成立了」的訊息,不知道是因為名字出現而不是被定義。
4. 提醒字樣舉例是 `web/src/pages/x.tsx`(TypeScript),消費專案多是 Kotlin/Swift/TS,〈做法〉8 的語意描述對它們不成立。需要把語意寫成「Python 檔判定義,其他語言判名字整字出現」,並在字樣裡建議非 Python 專案改用 `when-file` 或 `when-test`。
5. 〈做法〉7 第 4 條抽樣、S8 之類都沒考慮這一類,綁錯樣本會被這條汙染。

## F6 噪音門檻 35% 低於自己列的現況 36%,且沒列 401 提交那一欄
severity: minor
blocking: 否
引句:「有提醒的提交 ≤ 改到圖譜的提交的 35%,每個有提醒的提交中位數 ≤ 1 行」
file: `governance/eval/negation-revisit/report-2026-09-30.md:25`
1. 報告第三版表:工具鏈 300 是 63/174=36%、rtb 182 是 55/173=32%、rtb 593 全量是 146/401=36% 且中位 2、最多 10。spec 的「現況:工具鏈 36%、rtb 32%,中位 1。」只列兩欄,漏了中位 2 那欄。
2. 門檻 ≤35% 剛好卡在現況之下,意思是升級要求提醒真的改變了寫法;可以,但 spec 沒寫這個意圖,接手的人不知道 36% 是「現況已超標」還是「湊門檻」。RETIRE-IF 也沒有對應這條的撤除。
3. 需要一句話:門檻低於現況是有意的(要靠提醒把比例壓下去),並把 401 那欄的中位 2 列上。

## F7 S5「逐字印」的路徑跟現有 note-shape 的路徑寫法不同
severity: minor
blocking: 否
引句:「當提醒有 2 行(一行正文、一行表格列),工具應逐字印〈做法〉3 那段字樣」
file: `scripts/lumos:25414`
1. 〈做法〉3 字樣印 `Systems/任務流程領域模型.md:34`(去掉 `docs/<vault>/` 的圖譜相對路徑)。現有 `cmd_note_shape` 印違規用的是 `_note_shape_eval` 裡的 `p`,實測是 repo 相對全路徑 `docs/lumos-toolchain-knowledge/Systems/…md:80`。
2. `_ns_negation_hints(p, text, rows)` 收到的 `p` 就是後者,照字面實作會印全路徑,S5 依字樣寫的逐字測試會紅;要短路徑就得另外去掉 vault 前綴,spec 沒寫。
3. 另外「表格的格子與標題不能寫成回頭條件」那行(字樣第五行)是只有出現表格或標題形狀時才印,還是每次都印?S5 只給了含表格的例子,純正文提醒的字樣沒有定義。

## F8 幾個要被測試或替身引用的函式沒有簽名與名稱
severity: minor
blocking: 否
引句:「把 `_ns_negation_hints`、`_note_shape_negation_config`、組字樣的函式分別換成會丟例外的替身時」
file: `scripts/lumos:25379`
1. S4 要求把三個函式換成丟例外的替身,其中「組字樣的函式」沒有名字;〈做法〉3 也說讀設定、組字樣、印出三步「包在同一個 try 裡」,沒說三步是不是各自一個函式。測試要 monkeypatch 得有名字。
2. `_ns_negation_hits` 的輸入(單行?一篇的 rows?)與回傳(布林?命中位置?)沒定義;S1 的例句是單行、S8 要「把新行與終點全文直接餵給」它,兩邊的介面不同。`_ns_negation_hints` 的形狀怎麼判(`table`/`heading`/`prose`)也沒定義(量測程式 `_shape` 還會回 KEY 等前綴名,跟 spec 三值不同);heading 是以 `#` 開頭嗎?
3. 都是實作者要自行決定、且自行決定後 S1、S8 的測試才寫得出來的東西,寫進〈做法〉1、3 最簡單。

## F9 改寫成日期式的路徑仍會進內容審;日期式前綴也能靜音提醒
severity: minor
blocking: 否
引句:「所以提醒教的改法不會跟內容審打架」
file: `scripts/lumos:25719`
1. 〈做法〉6 與〈做法〉2 講內容審會跳過條件式行。程式裡跳過的只有 `cond`;註解明寫「日期式照審」。提醒字樣說觀測類「只能寫日期 REVISIT:YYYY-MM-DD …」(真句 12 行裡 1 行),照那樣改寫的行,內容審仍會判它(「there is no X」這類仍會判成推得出,被要求刪)。
2. 同時,〈做法〉1 第 1 點把日期式 REVISIT 行整行不看,因此任何否定句前面加 `REVISIT:2026-12-31 ` 就靜音(RETIRE-IF ③ 只抽條件式行,量不到)。〈做法〉2 第一句說「已配」只認條件式,跟這個規則不一致(日期式行雖然不算配,但也不被提醒)。
3. 需要把〈做法〉6 那句限縮成「條件式」,並在〈誠實界線〉補一行日期式前綴可規避。

## F10 `when-status` 的字樣在本圖譜慣用寫法下會踩 `[[ ]]`,且只寫 `=done`
severity: minor
blocking: 否
引句:「講的是一個流程或一份計劃,用 [when-status:計劃節點=done]」
file: `scripts/lumos:26310`
1. 本圖譜的節點引用都寫 `[[Projects/x]]`;照字樣把 `計劃節點` 換成 `[[Projects/x]]` 實測被既有規則擋:「條件寫錯 … when-status 要寫成 <節點>=<值>;沒帶期限」——訊息指向的原因(其實是 `]` 提早結束標記)不直觀。字樣要明講「節點不加 [[ ]],寫 `Projects/名稱`」。
2. `=done` 只認 done。`_DRIFT_CLOSED` 是 done 與 superseded,Projects 現有 12 篇 superseded(約 9%);計劃被取代而不是做完時,句子還是過期,條件永遠不成立。字樣可寫 `=done|superseded`(文法支援 `|`),並在〈做法〉8 說明 superseded 算不算事件發生。

## F11 計劃自己的 REVISIT 會擋住實作那次推送
severity: minor
blocking: 否
引句:「實作上線了:這裡補一行上線後第 8 週的日期式 REVISIT」
file: `scripts/lumos:26837`
1. 計劃第 50 行是條件式 `[when-symbol:scripts/lumos::_ns_negation_hints]`。這一條在實作提交把函式加進 scripts/lumos 的那次推送,依 `_drift_probe_check`(條件標記這條終點成立、起點不成立)會被 drift check 擋(預設 block);spec 〈做法〉6 自己也說「同一次推送裡後面的提交才把東西做出來,照樣擋」。
2. 這行的動作文字是「補一行日期式 REVISIT」,沒寫同一次提交就要把該行改掉或表態;實作的人若先寫程式、最後才改計劃,推送被擋一次。〈下一步〉或 S-條款加一句「實作提交要同時處理這一行」即可。

## F12 8 週量測的母體與提交清單沒寫
severity: minor
blocking: 否
引句:「= 量測程式 `scan --renames`(用 `-M` 取新行,跟 note-shape 提交前一致)對上線後的提交跑、取 `funnel_v3` 的會提醒列」
file: `governance/eval/negation-revisit/neg_revisit_measure.py:338`
1. 量測程式 `scan` 要 `--repo`、`--vault`、`--tag` 與 `--commits`(或 `--n`);spec 沒說對哪個 repo 量。工具鏈自己有 scripts/lumos 歷史,「上線提交」的 `git log -S … -- scripts/lumos` 只在工具鏈算得出;消費專案(rtb)用符號連結裝、沒有這串歷史。母體是不是只有工具鏈?樣本 ≥30 與 8 週的預期量(9/13–9/30 就 174 個提交,量夠)是照哪個 repo 算的?
2. 提交清單怎麼產(`git log --no-merges <上線提交>..<主線頂端>`?要不要限制改到圖譜的)沒寫;改「squash 後才推」的專案慣例(CLAUDE.md 提交規矩)下,推上主線的提交跟本機提交前提醒印出來時的提交不是同一批,也沒講。

## 已讀,無 finding 的節
- 〈上線門檻〉:12/30 對過 `labels-2026-09-30.json`(v3 池 T=12、共 30),95% 區間約 25%–58% 對得上。
- 〈做法〉1 第 2–6 點與 S1、S9:對照 `classify_v3`、`excluded_v3`、`FIELD_RX`(量測程式的鍵清單是 `when-[a-z]+`,spec 寫「`when-` 開頭的任何鍵」,差別只在含數字或連字號的鍵,實際沒有這種鍵,不算 finding)。S1 全部例句逐句一致。
- 〈做法〉3 的 hints 出參、早退條件、不寫帳、`--diff`/doctor 不傳:程式碼結構(`_note_shape_eval` 的 rows 迴圈、`cmd_note_shape` 早退)對得上,兩個舊呼叫端確實只取兩個回傳值。
- 〈做法〉4 開關與 doctor 的插入位置:`_note_shape_doctor_lines` 讀到的 `txt` 與 `if ci: return out` 位置對得上。
- 〈做法〉5、〈回退〉、〈實務隱患〉:未見程式面問題。

最高等級:major;blocking 共 5 條
