severity: blocker

# 筆記內容審_計劃 r2 外部審查(鏡頭:資源併發)

範圍:逐節讀完 `r2-work.md`(凍結工作副本),對照 `r2-delta.patch` 確認本輪新增/改寫段落,並對照程式碼 repo(`scripts/lumos`、`scripts/hooks/pre-push`、`.github/workflows/ci.yml`)逐一核對引用的函式/常數/檔名是否存在、語意是否相符。主審鏡頭是資源併發(最壞時序安排者視角);同時完成一般性逐節核對。

## 逐節核對(未在下方列 finding 的部分)

- 開頭欄位、`related:`、PRIOR-ART、RETIRE-IF、REVISIT:交叉引用逐一開檔核對過(`Systems/筆記內容閘`、`Issues/治理帳多個寫入者都沒上鎖`、`Projects/筆記形狀擋_計劃`、`Issues/筆記把程式現況寫進脈絡而漂移_rtb實測回饋`、`Systems/外部對照-code衍生wiki`、`Systems/每支檔有家`、`Systems/pitfalls-code-loop`)都存在,內容與本篇的引用語意相符。已讀,無 finding(除下方 F1 對 PRIOR-ART/實務隱患段的併發缺口)。
- 〈判定者能不能用:小實驗〉一節:`governance/audits/2026-09-27-rtb-notes/judge-experiment/` 目錄存在,`judge_prompt.md`、`judge_input.md`、`judge_key.json`、`judge_opus.md`、`judge_sonnet.md` 都在。`judge_prompt.md` 的三類分類定義(CODE/CONTEXT/MIXED)語意與本篇「推得出/脈絡/一半一半」三類對應一致。已讀,無 finding(除下方 F3)。
- 〈做法〉第 1 節:核對 `scripts/lumos` 現況——`_ns_range_added`(23579 行)、`_note_shape_eval`(23763 行)、`_nodehome_golive`(22943 行)、`_nodehome_clamp_base`(22954 行)都存在,行為與本篇「以程式碼為準」段落描述相符;`_nodehome_golive` 目前確實寫死查 `scripts/hooks/pre-commit`(22947 行),`_ns_range_added` 內的逐提交上線判定(23596 行起)也寫死同一支檔——本篇「三處寫死的上線判定,兩處加參數、逐提交那一段第二層不用」的說法與程式碼現況吻合(逐提交那段傳 `mark=None` 就已經是「不過濾」,不需要再加掛鉤參數)。已讀,無 finding。
- 〈做法〉第 2 節內容編號、判定檔、`_write_lf`(14146 行,確認是暫存檔→`os.replace` 原子換名)、`_validate_repo_ref`(19819 行,確認有 `at_sha` 參數且會拒絕絕對路徑與 `..`)、`_BOOKKEEPING_DIRS`(20353 行)、`_KNOWN_GATES`(6599 行,目前未含 `note-audit`,與本篇「要登記」一致)都核對過,語意相符。已讀,無 finding(除下方 F2)。
- 〈做法〉第 3–5 節、〈條款〉S1–S17、〈回退〉、〈前身 r3 發現怎麼處理〉、〈審計修正紀錄〉:逐條讀過,條款編號與正文交叉引用一致,`r1-work.md`/`r1-snapshot.md`/`r2-delta.patch` 與 `governance/review-reports/筆記不存程式碼推得出的事/r1..r3-*` 卷證目錄確實存在(僅列目錄確認存在,未讀取內容,遵守審查範圍限制)。已讀,無 finding。

## F1 治理帳(docs/.governance-log.jsonl)是受版控的共用檔,兩條分支各自 record 後合併會真的衝突,誠實界線只寫了「同機即時寫」那一種丟線路徑

severity: major
blocking: 是 —— 這條路徑目前沒有任何緩解或警示文字,而且是設計本身鼓勵的常態操作(「幾乎每次推送都有 prepare、record 事件」),一旦發生,作者拿不到任何線索去正確處理,只能反覆試錯

`docs/.governance-log.jsonl` 是進版控的檔(本輪 git status 顯示 `M docs/.governance-log.jsonl`),`_gate_event` 用 `with open(docs / ".governance-log.jsonl", "a", ...)` 直接附加寫入(`scripts/lumos:928`,另一支既有寫入器在 `scripts/lumos:30295`)。本篇〈實務隱患〉段只討論「同一台機器上兩個行程同時寫、位元組黏成壞行」這一種併發(引句見下),完全沒有討論「兩條分支各自 commit 了新的治理帳事件、之後要合併(merge/rebase)時,git 對同一支檔案尾端的兩筆不同新增行,預設就是衝突,不是自動合併」這條路徑——而這條路徑在本篇自己描述的操作模式下(兩個會談各自在自己的分支/worktree 上 `record`,之後要合成一次推送)幾乎必然發生。

引句:「每筆仍短;黏成壞行的後果是那筆事件讀不到——派出事件少算、或判定檔找不到對應事件而被當成不存在(多擋)。」

這句話描述的是同一機器上兩個行程真的同時 `write()` 才會發生的「黏成壞行」;但本篇緊接著承認治理帳的寫入器沒有鎖(見〈做法〉第 2 節「判定檔與治理帳互相對得上」段的措辭本身,以及 `scripts/lumos:928` 那支既有寫入器確實是裸 `open(...,"a")`,沒有鎖也沒有走 `_write_lf`)。真正會常態發生的是「git 層級的合併衝突」,不是位元組黏線——我用一個乾淨的 `/tmp` repo 重現過:兩個分支各自在同一份檔案尾端 append 不同的一行,`git merge` 一定給 `CONFLICT (content): Merge conflict in f.jsonl`,不會自動聯集:

```
$ git merge B --no-edit
Auto-merging f.jsonl
CONFLICT (content): Merge conflict in f.jsonl
```

這正是本篇要求推送前「先過筆記內容審、再做代碼審留痕」的常態場景下,兩個會談各自 `record` 並提交的下場:合併時 `docs/.governance-log.jsonl` 一定進入衝突標記,需要人(或 AI)手動解決;若圖省事用 `git checkout --ours`/`--theirs` 二選一(這是最常見的衝突解法,尤其對一支看起來「只是流水帳」的檔案),另一邊剛寫進去的指紋事件行會被整行丟掉——而判定檔本身(檔名帶亂數,見〈做法〉第 2 節)不會衝突,還在,於是變成「判定檔在、治理帳事件不在」,`check` 依照本篇自己的規則「對不上的判定檔當作不存在並列出來」會把這份本來合法的判定當空氣擋下(多擋,方向安全,但沒人告訴作者為什麼)。

值得注意的是,這個 repo 對「共用 append-only JSONL 檔合併會壞掉」這件事其實有前例、而且知道後果很嚴重——`_vendor_toolchain`/`bootstrap --pull` 那條路徑專門為 `docs/.usage-log.jsonl` 這類簿記檔寫了「取聯集合併」邏輯:先把本機獨有的行讀進記憶體、checkout 回 HEAD、pull、再把那些行補回去,理由寫在 file: `scripts/lumos:17049-17052`(直接點名 stash/pop 這種 naive 解法的下場是帳本直接壞掉、之後每次讀都炸,第一版真的踩到,實測留下 `<<<<<<<` 標記)。但那支邏輯只處理「本機 dirty + `git pull --ff-only`」這一種情境(給 `lumos update` 拉工具鏈上游用),不會被套用在「兩個獨立分支各自提交後要合併」這個本篇真正會用到的情境上——本篇完全沒有提出對等的機制(例如:合併判定檔目錄前先跑一次治理帳聯集合併、或至少在〈誠實界線〉裡把「合併衝突手動解錯會丟指紋事件」寫成獨立一條、給出正確解法)。

修法方向(不需要新機制,沿用既有形狀就夠):在〈誠實界線〉或〈做法〉第 2 節補一句「合併/rebase 前若 `docs/.governance-log.jsonl` 衝突,兩邊都要保留(比照 `_vendor_toolchain` 的聯集合併,不能二選一)」,或直接把 `_vendor_pull_source` 那段聯集合併邏輯抽出來給合併治理帳這個場景重用。

## F2 「同一個內容編號一生只准申訴一次」只在單一分支/工作目錄內可驗證,兩條分支各自對同一判定提申訴時,fold 演算法沒定義兩份申訴同時存在時要收斂到哪一邊——而且不同機器目錄列舉順序不保證一致,本機與 CI 可能各自收斂到不同結果

severity: blocker
blocking: 是 —— 這直接違反本篇自己宣告的核心不變量(同一判定一生只能申訴一次),而且演算法沒有給出任何處理規則,worst case 是本機與 CI 對同一顆推送給出不同的涵蓋結果

引句:「同一個內容編號一生只准申訴一次(不管申訴成不成立);第二次申訴 record 拒絕」

這個「只准一次」的不變量是靠 `record` 在寫入當下檢查達成的:

引句:「報告席名要跟被申訴那份判定檔的席名不同;那一行之前沒申訴過」

問題是「那一行之前沒申訴過」這個檢查只能看到「這次呼叫端當下看得到的判定檔」——也就是這個工作目錄裡已提交(可達歷史)加上剛 `record` 還沒提交的那些檔。兩個會談各自在自己的分支/worktree 上,對同一個原始判定(同一份 `--disputes <判定檔>`)各自獨立提出申訴,是本篇明確允許、也是設計正常運作模式的情境(「幾乎每次推送都有 prepare、record 事件」)——雙方各自呼叫 `record --dispute` 時都看不到對方,各自都會通過「之前沒申訴過」這道檢查,各自寫出一份合法的申訴判定檔。這兩份判定檔的檔名是各自的 `<UTC 時間>-<32 位亂數>`,彼此不會撞名,git 合併這兩個分支時**不會**衝突(跟 F1 的治理帳不同,這裡反而是「太順利地都合併進去了」)。

合併後,`governance/note-verdicts/` 裡就存在兩份都指名同一份原始判定檔的申訴,而〈做法〉第 2 節的 fold 演算法只寫了:

引句:「每一筆如果被某個申訴檔指名申訴,就換成申訴的結果」

——完全沒有定義「被兩份申訴檔指名」時要用哪一份的結果。這不是可以事後用「取最重」蓋過去的情境:「取最重」的三步驟算法(1. 套申訴取代;2. 對取代後的集合取最重;3. 都沒有才用略過)在步驟 1 本身就是未定義的(「換成申訴的結果」——換成哪一份?),不是步驟 2 那種「多筆判定取 max」的良定義運算。若實作用某種迭代順序(例如檔名字典序、或檔案系統 `readdir` 順序)決定「最後套用哪一份申訴」,這個順序**不保證跨環境一致**——本機（macOS,HFS+/APFS 目錄列舉順序)與 CI(ubuntu-latest,ext4)對同一組檔名的 `readdir` 順序沒有保證相同,`.github/workflows/ci.yml` 目前對 `note-shape`/未來的 `note-audit` 都是重新 `git fetch`/`checkout` 出同一個提交的樹來跑(`.github/workflows/ci.yml:131-136`),但檔案系統層的列舉順序仍可能與觸發推送的本機不同。也就是說:同一顆被推上去的提交,本機 `check` 可能收斂到「這行判成脈絡,涵蓋」,CI 的 `check` 可能收斂到「這行仍是推得出,不涵蓋」——這正好命中本輪審查鏡頭要求的「CI 與本機讀到的頂端提交」這條時序,而且比單純的範圍差異更隱蔽:兩邊讀的是完全同一個提交、同一批判定檔,結果卻可能不同。

〈做法〉第 3 節第 5 點對申訴收件的描述也印證了這個缺口只在單次呼叫內處理過(「同一次呼叫裡兩份非申訴報告對同一編號判得不同 → 兩筆都照收(取最重自然生效)」是講「非申訴」判定,對「申訴」判定完全沒有等價的一句)。條款 [S8] 同樣只測了「同一行第二次申訴應被拒絕」這種單一 `record` 呼叫內的循序情境(對照條款測試名 `t_note_audit_fold_rules`),沒有涵蓋「兩份分別合法通過檢查、事後合併」這個併發情境——這正是本輪要求安排的時序:「兩個會談同時 record 並各自提交判定檔與治理帳」。

修法方向:fold 演算法需要對「同一目標判定檔被多於一份申訴指名」定義明確、跨環境確定性的規則(例如:多於一份時視為衝突、兩份都不算數、原判定維持,並要求人工用 `decision-amend` 等機制之外的方式介入;或用治理帳事件的時間戳排序而不是檔名/檔案系統順序決定「先到者有效」),並補一條條款測試覆蓋「兩份獨立合法申訴指名同一原始判定」這個狀態。

## F3 S13「三類分類定義逐字沿用」與 judge_prompt.md 第 12 行的證據要求句在同一段落,邊界沒說清楚,容易連同 rtb 路徑一起複製

severity: minor
blocking: 否 —— 是 S13 自己的驗收條款會抓到的實作細節,不影響本篇設計本身能不能運作,頂多是實作階段多一輪返工

引句:「prepare 產生的派工詞應逐字含 `judge_prompt.md` 的三類分類定義與本計劃六句,專案路徑與技術棧應換成被審 repo 的、不得出現 rtb 的路徑」

實地讀 `governance/audits/2026-09-27-rtb-notes/judge-experiment/judge_prompt.md`:CODE/CONTEXT/MIXED 三類定義在第 7–10 行,語意通用、不含 rtb 路徑;但緊接在第 10 行之後、屬於同一段落語境的第 12 行是「For CODE and MIXED you must cite at least one file:line in /Users/enzo/rtb-mainwt that confirms or refutes the code part」——這句把證據要求(file:line)跟寫死的 rtb 絕對路徑綁在一起。本篇〈做法〉第 3 節第 2 點自己新增的第③句(「推得出的部分附證據——`file:line`,或 `search: <字串> in <repo 內相對路徑> => <命中數>`」)明顯是用來取代第 12 行、同時把路徑改成通用寫法,但正文「三類分類定義逐字沿用」這句話沒有明講「逐字沿用」的範圍到底止於第 10 行還是含第 12 行——如果實作時把「分類定義」直覺理解成整段(含第 12 行的證據要求),就會把 `/Users/enzo/rtb-mainwt` 這個硬路徑一起複製進去,直接違反同一條款自己那句「不得出現 rtb 的路徑」。

## F4 doctor 對消費專案 CI 的檢查只給了「印一行並給要貼的步驟」這句籠統描述,沒有像 note-shape 一樣附上實際可貼的 CI 步驟範本,執行期只能各自猜

severity: minor
blocking: 否 —— 不影響核心判定邏輯正確性,只是交付文件缺一塊,實作時另外補就好

引句:「doctor 檢查專案 CI 有沒有呼叫 `note-audit check`,沒有就印一行並給要貼的那一步」

對照第一層的既有落地:`.github/workflows/ci.yml` 裡 `note-shape` 已有完整可抄的步驟(第 121–143 行,含 `git fetch`、`git branch --track main origin/main`、`BEFORE`/`SHA` 的推導與例外處理)。本篇對 `note-audit check` 要貼進 CI 的那一步完全沒有給出等價的具體片段(用什麼事件觸發、`BEFORE`/`SHA` 怎麼取、要不要跟 note-shape 一樣先 `fetch` 主線)——條款 [S16] 也只測 doctor「有沒有印出提醒」,不測提醒內容是否給得出可直接貼上去、行為正確的 CI 片段。鑑於 note-audit 的檢查邏輯(依「被推送頂端提交」讀判定檔與治理帳,範圍算法涉及上線點截斷)比 note-shape 更複雜,這塊留白在實作期容易各專案各自兜出不一致的 CI 寫法。

## 隱患鏡頭逐類作答

- **守衛面**:本篇已有 skip/申訴/開關三條逃生路,關閉或跳過都寫帳;但 F2 顯示核心不變量(一生只申訴一次)在多分支情境下並非機械保證,屬於守衛面的併發缺口,已計入上方 F2。
- **對外送出**:判定者跟編排會談同一家、不派外家,沒有新增供應商暴露面——已讀,無新 finding。
- **資源併發**(本輪主鏡頭):見 F1(治理帳合併衝突無聯集合併對策)、F2(申訴不變量跨分支失守、可能導致本機/CI 判定分歧)。其餘既列出的時序——「prepare 派出事件與 record 之間當機」(prepare 明講會重讀工作目錄裡的判定檔與治理帳,能正確重派,已讀無 finding)、「判定檔與治理帳分兩次推」(靠指紋比對,查不到就當不存在,方向安全,已讀無 finding)、「代碼審帳本提交與判定檔提交的先後」(`governance/note-verdicts/` 併入 `_BOOKKEEPING_DIRS`、`docs/.governance-log.jsonl` 本來就在 `_BOOKKEEPING_FILES` 裡,`scripts/lumos:20340`、`20353` 核對過,方向正確)——都核對過,沒有另外的 finding。
- **可用性**:模型限流/服務中斷走 skip,留理由進帳,已讀無 finding。
- **容量**:每份報告一個檔,壓縮要求保留申訴關係,已讀無 finding(F2 若成立,「保留申訴關係」在有雙重申訴時具體怎麼壓縮也會需要重新定義,但那是 F2 的下游,不重複計)。
- **不可逆 / 金流**:本篇〈實務隱患〉已排除,查核無誤(擋在推送前、本機提交都還在;decision-amend 只改未推上去的決策)。

## 總結

檔級 severity 為 blocker,共 2 條 major/blocking(F1、F2),2 條 minor 不阻擋(F3、F4)。F2(申訴不變量跨分支失守、可能導致本機與 CI 判定分歧)是最嚴重的一條。
