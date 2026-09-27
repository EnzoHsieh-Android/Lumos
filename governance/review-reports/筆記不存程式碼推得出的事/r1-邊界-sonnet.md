severity: blocker

〈frontmatter / 標題 / 白話 / 依據〉已讀,無 finding

〈PRIOR-ART / RETIRE-IF / REVISIT〉已讀,無 finding

〈判定者能不能用:小實驗〉已讀,無 finding——已核對 `governance/audits/2026-09-27-rtb-notes/judge-experiment/judge_prompt.md` 確實存在且與正文描述的分類定義(CODE/CONTEXT/MIXED)一致,S10 引用屬實。

## F1 行號引用擋法漏了本 repo 被引用最多的無副檔名主程式

severity: blocker
blocking: 是 —— 不改,實作者會做出一個對本 repo 最高風險檔案完全失效的擋

引句:「行號只要有人改碼就錯位,抽樣 12/12 都是這類」

S1 與正文都把「程式行號引用」定義成「檔名.副檔名:數字」(必須有副檔名)或 `#L數字`。但本 repo 唯一的主程式 `scripts/lumos`(32,381 行,改動頻率最高)沒有副檔名。實測:

1. file: `docs/lumos-toolchain-knowledge/` —— `grep -roh "scripts/lumos:[0-9]\+\(-[0-9]\+\)\?" docs/lumos-toolchain-knowledge/` 命中 237 次,分布在至少 66 篇筆記(例如 `docs/lumos-toolchain-knowledge/Projects/收斂閘漏項敏感度v2_計劃.md:83` 的「`scripts/lumos:11774`」)。
2. 這種寫法完全符合「行號只要有人改碼就錯位」的風險描述(`scripts/lumos` 每次改動都可能讓這些行號全部錯位),卻因為檔名沒有副檔名,不落在 S1 定義的「檔名.副檔名:數字」形狀裡。
3. 若逐字照 S1 實作(要求正則裡有 `\.[A-Za-z0-9]+:`),新增一行「`scripts/lumos:99999` 這裡改了判斷邏輯」不會被擋;而新增一行「`scripts/lumos.py:99999`」(假設性,本 repo不存在但示範同形狀)才會被擋——兩者風險完全相同,只有副檔名有無之別。
4. 结论:S1 對「檔名.副檔名」的字面定義,漏掉本 repo 事實上引用密度最高、風險最典型的目標,而不是漏掉冷門邊界。

## F2 「## 現況」標題比對法對本 repo 95.6% 的已完成計劃無效

severity: blocker
blocking: 是 —— 不改,實作者會交付一個對現有已完成計劃幾乎不會觸發的擋(而這正是機制存在的理由)

引句:「且該節非空行超過一行,則提交應被擋下」

S2 的偵測條件綁死在標題字面「## 現況」上。實測本 repo:

1. `docs/lumos-toolchain-knowledge/Projects/*.md` 共 213 篇,`status: done` 113 篇。
2. 其中只有 5 篇含 `^## 現況` 標題,其餘 108 篇(95.6%)完全沒有這個標題——例如已核對過的 `docs/lumos-toolchain-knowledge/Projects/驗證層去模型化_計劃.md`(status: done),它的標題是「## 四件」「## 審計修正紀錄」「## 合約候選清單」「## 刻意不做」「## 實務隱患」「## 驗收線」,一個「## 現況」都沒有,但「## 驗收線」「## 合約候選清單」這類段落同樣可能留著會過期的現況細節。
3. 這代表 d4 想擋的問題(「做完的計劃還留著現況段」)在本 repo 現有 108 篇已完成計劃裡,只要作者(一直以來的實際寫法)不用「## 現況」四個字當標題,就完全不落在 S2 的偵測範圍——不是要故意規避才躲得掉,是本 repo 現有多數寫法本來就用別的標題。
4. 若這是要新開一個規定的「往後一律用『## 現況』」,spec 沒有這一句;若不是,S2 的機械偵測對本 repo 現有分布形同不存在。

## F3 摘要行(FACT:/WHY:/RULE:/PITFALL:)實際寫在 frontmatter 的 summary 區塊,S1/S3/S5 都沒有處理這個位置

severity: blocker
blocking: 是 —— 不改,兩層閘可能對本專案「摘要行」這個最主要的斷言載體整段失效,或者兩層閘的「開頭欄位排除」邏輯自相矛盾

引句:「且應排除開頭欄位裡的結構欄位與程式碼圍欄」

1. 本 repo 的 KEY:/FACT:/WHY:/RULE:/DECISION: 這類「摘要行」,依 CLAUDE.md 與紀律範本的定義是寫筆記的主戰場,但實際上它們不在 body,而是寫在 frontmatter 的 `summary: |-` 區塊裡。已讀的 `docs/lumos-toolchain-knowledge/Issues/筆記把程式現況寫進脈絡而漂移_rtb實測回饋.md` frontmatter 第 21 行起就是「summary: |-」接著整段 `FLAG:`/`KEY:`/`DECISION:`/`WHY:` 行。
2. `scripts/lumos` 裡至少 15 處(例如 `scripts/lumos:3770`、`scripts/lumos:4913`、`scripts/lumos:11961`)明確把 `n.fields.get("summary")` 當成獨立於「結構欄位」(tags/連結/日期/狀態)的一等公民內容去解析、驗證合約標記與宣稱——這個 repo 自己的既有工具鏈把 summary 當「正文」對待,不是當「結構欄位」。
3. 再實測:`summary:` 區塊裡已經有 18 篇筆記、共 33 處含「檔名.副檔名:數字」形狀的引用(例如可重跑 `grep -n "^summary:" docs/lumos-toolchain-knowledge/**/*.md` 後檢查各檔 summary 區塊)——這正是 S1 想擋的東西已經活生生存在於這個位置。
4. spec 對 S1/S3(行號引用、FACT: 來源標籤)完全沒說是否掃描 frontmatter;S5 只講「排除開頭欄位裡的結構欄位」,沒有講 summary 這種「frontmatter 裡的多行散文欄位」算不算「結構欄位」。兩種讀法都出問題:整段 frontmatter 一律排除 → 兩層閘對本 repo 最主要的斷言載體(summary 區塊)完全失效;summary 算正文要掃 → S2「## 現況」這種以 markdown 標題辨識段落的邏輯,套用到 YAML block scalar(沒有 markdown 標題結構)上要怎麼切分段落,spec 沒有講。

## F4 S3 的機械閘只認 `FACT:`,但範本與稽核證據都指出 FLOW:/DEP:/WHY:/RULE:/PITFALL: 同樣會裝現況、也真的漂移過

severity: major
blocking: 是 —— 不改,實作者會交付一個只覆蓋一小部分「程式碼推得出的現況」標籤的機械閘,卻讓紀律範本與稽核報告都證明過的其餘標籤(FLOW/DEP/WHY/RULE/PITFALL)無機械擋

引句:「類別之一,則提交應被擋下」

1. file: `scripts/templates/graph-discipline.md:44` —— 現行範本把 `FACT:`、`FLOW:`、`DEP:` 三個前綴列在同一列,要求同一套規矩(現況描述、能查到就別抄)。
2. S1 第 3 條與 S3 的偵測範圍字面只寫「新增的 `FACT:` 行」,完全沒提 `FLOW:`/`DEP:`。這代表同一列裡本該同等對待的三種前綴,只有 `FACT:` 有機械擋,`FLOW:`/`DEP:` 繼續套用舊的「以程式碼為準+查詢」出口,沒有 `[src:]` 要求也不會被擋。
3. file: `docs/lumos-toolchain-knowledge/Issues/筆記把程式現況寫進脈絡而漂移_rtb實測回饋.md` 的「掛 WHY/RULE/PITFALL 標籤、內容其實是現況的摘要行」一列寫明:隨機抽 30 條,其中 3 條已漂移——即稽核自己的資料就證明漂移不限於 FACT: 標籤。
4. S9 也只寫「紀律範本的 FACT 那列應寫 d3 的收窄說法」,同樣沒提 FLOW:/DEP: 那半列要不要跟著改——若照字面只改 FACT 半句,範本會變成同一列裡 FACT 用新規矩、FLOW/DEP 用舊規矩,但視覺上仍是「同一列」,人類讀者會混淆哪一半才是現行規定。

## F5 非 UTF-8 內容的失敗模式沒有規定,本 repo 已有兩筆同類真事故

severity: major
blocking: 是 —— 不改,遇到非 UTF-8 的新增筆記檔時,兩層閘可能整支靜默跳過(閘失效)或整支中斷(擋住所有推送),兩種都沒人決定要哪一種

引句:「推送被擋是本機行為,不送任何內容到外部服務」

1. `實務隱患` 只列了「守衛面」「對外送出」「不可逆」「金流」四類,漏了「非法輸入讓機制本身當機或靜默跳過」這一類——這正是本 repo 已經踩過的坑。
2. file: `docs/lumos-toolchain-knowledge/Issues/風險掃描遇到非UTF-8內容整支中斷.md` —— 既有風險掃描工具遇到非 UTF-8 內容整支中斷的真實事故記錄。
3. file: `docs/lumos-toolchain-knowledge/Issues/主程式讀取路徑漏接UnicodeDecodeError.md` —— 主程式讀取路徑漏接 `UnicodeDecodeError` 的另一筆真實事故記錄。
4. 具體場景:某篇筆記新增一行貼上了終端機輸出裡帶壞位元組的內容(例如貼了非 UTF-8 編碼的 log),S1/S3 的「提交時擋形狀固定的東西」若照現有多數程式碼的寫法(`scripts/lumos` 裡 320 處 `except (OSError, UnicodeDecodeError)`)去讀取 staged 內容,若擋在 pre-commit gate 的實作沒把這個例外也接住,會整支中斷擋下所有提交(含完全不相關的改動);若接住但走 fail-open(`|| true`,本 repo 既有慣例,如 pre-commit Gate CC/DG 都是這樣),則對那一支檔的所有新增筆記行——不管是不是行號引用或沒帶 `[src:]` 的 FACT——整段悄悄不檢查,兩層閘一起失效。spec 沒有選邊。

## F6 done 計劃的「舊狀態」比對沒講清楚改名檔怎麼算,本 repo 對 rename 的偵測本來就不一致

severity: major
blocking: 是 —— 不改,把「改狀態成 done」跟「改名」放進同一次提交,S2 有沒有擋得住取決於實作抄哪一段既有程式碼,結果可能無法預期

引句:「只改到同一篇其他節的提交不應被擋」

1. S2 的判定需要知道「這次提交把某計劃的狀態改成 done」,意味著要比對同一篇筆記「這次提交前」與「這次提交後」的 `status` 值——這要求能在 git diff 裡認出「同一篇」。
2. 本 repo 現有程式碼對「改名要不要當同一篇」處理並不一致:file: `scripts/lumos:22630` 用 `git diff --cached --name-status -z -M`(認 rename);file: `scripts/lumos:23217` 用 `git diff --cached --name-only -z --no-renames`(刻意關掉 rename 偵測)。
3. 具體場景:一次提交裡同時把 `Projects/舊名_計劃.md`(status: doing)改名成 `Projects/新名_計劃.md`,並在新檔裡把 `status` 改成 `done`、且沒有收攏「## 現況」段。若 S2 的實作抄的是 `--no-renames` 那一套寫法(跟它在 pre-commit 裡緊鄰的 Gate H 用的是同一種思路),diff 會顯示成「刪除舊路徑、新增新路徑」,新路徑在這次提交之前不存在,找不到「先前的 status」可比對,S2 判斷不出「這次把狀態改成 done」這件事發生過,現況段收攏檢查就不會被觸發。spec 全文沒有一句提到 rename 情形下 S2 要怎麼找到「同一篇」的舊值。

## F7 圍欄豁免沒有指名沿用既有的單一實作,本 repo 對這件事有過真實的資安等級教訓

severity: minor
blocking: 否 —— 不是必然做錯,是若不特別提醒,历史上已經出過同類 bug 的地方少了一道提醒

引句:「且不在程式碼圍欄內、也不是引句行」

1. file: `scripts/lumos:3223` 起的註解明講:本 repo 過去有四處各自用 `FENCE_RE = re.compile(r"^```.*?^```", re.S|re.M)` pairwise 正則判斷圍欄,「未閉合的圍欄看不見」曾造成幽靈圖譜連結被索引、偽合約佐證進入 `guard trace`——這是 code-loop r2/r4 抓到的真實資安等級 bug,後來統一收斂成 `_visible_lines()`(`scripts/lumos:3223`)逐行 toggle 的單一實作。
2. S1「不在程式碼圍欄內」與 note-audit prepare(S5)「排除…程式碼圍欄」都沒有指名沿用 `_visible_lines`/`_strip_code_text`,也沒有提到「未閉合圍欄」这个已经在本 repo 出过事故的边界。PRIOR-ART 段只寫「機制層照抄本 repo 的代碼審留痕閘」,沒提圍欄判定要照抄哪一支既有實作。
3. 若實作者重新手刻一個簡單的 pairwise 正則(而不是搜出 `_visible_lines`),會重蹈本 repo 自己文件裡明寫過的同一個坑;由於這只是「沒指名」而非「保證做錯」(CLAUDE.md 的零依賴/優先用既有解法家規會促使認真的實作者去找既有工具),列為 minor。

## 條款 S1–S10 逐條檢視小結

- S1、S3、S5:對應 F1、F3、F4、F7 已個別展開。
- S2:對應 F2、F6。
- S4:「推送前或 CI 對範圍重跑第一層,結果應跟逐次提交時一致」——本身可執行,但其正確性繼承 S1/S2 的既有缺口(F1/F2/F6 若不修,S4 驗的是「兩處都一樣漏」而非「兩處都對」)。
- S6、S7、S8:機械驗證條件描述明確(逐行判定齊全、程式位置存在且行號不超檔長、申訴需第二席獨立判 CONTEXT、指紋綁定语义),讀完没有另外找到新的可執行性缺口;S8 的指紋綁定方向(只綁新增筆記行内容、code-only 提交不失效)與既有 code-loop 留痕(綁 HEAD sha、任何後續提交都會使其失效,見 `scripts/lumos:30275` 印出的「之後再改任何程式碼…它就失效」)语义相反——但 spec 在「做法」正文裡已經自己講清楚這是刻意的設計差異(「之後只改程式、不動筆記的提交不用重審」),不是誤稱抄襲到走樣,只是 PRIOR-ART 段「機制層照抄」這句話容易讓人誤以為連綁定語义都照抄,建議 PRIOR-ART 段補一句講清楚指紋綁定方式跟 code-loop 不同,但這只是文字精確度問題,不到開 finding 的門檻。
- S9:對應 F4(FLOW:/DEP: 半列沒有跟著改)。
- S10:已核對 judge_prompt.md 存在且分類定義與正文一致,無 finding。

## 回退

已讀,無 finding——三段回退敘述與各自機制的新增狀態(commit-time gate、governance ledger 通過紀錄、範本行)對應得上,沒有找到「回退會留下無法解釋的殘留狀態」的情形。

## 誠實界線

已讀,無 finding。

---
總結:整份 spec 最嚴重 severity 為 blocker(F1/F2/F3);blocking 共 6 條(F1、F2、F3、F4、F5、F6),non-blocking 1 條(F7)。
