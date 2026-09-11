severity: major

## 逐節讀件記錄(要求1、2、3)

- **為什麼(這批的來源)**:已讀,有 finding → 見 F1、F2(舊案接軌與引用問題)。
- **名詞**:已讀,無 finding(家/家對照表/必推名單/可選名單/大檔/從程式重建的節點/組裝檔六個定義互相不矛盾)。
- **核心裁定甲(S1–S10)**:已讀,有 finding → 見 F4(S14 抽查腳本)。S1–S9 逐條核對函式/常數皆屬「本案要新增」或與現有 `_impact_knob`、`_impact_about_counts`、`pins` stable sort、`_LENS_KIND` 等既有錨點一致,無 finding。
- **核心裁定乙(S11–S13)**:已讀,無 finding——`_nodehome_parse_note` 現在確實不讀 `regen` 欄(spec 自陳「新增」,不算未定義);`node_home.gate`(on/warn/off)與 `_nodehome_resp_ok`(負責範圍 ≥10 字)在 `scripts/lumos:17707-17779` 已存在,S11 接的是既有原語。
- **收尾(S18)**:已讀,無 finding(見下方第二輪複核,已實跑覆核六篇數字)。
- **範圍外**:已讀,有 finding → 見 F3(壞連結)。
- **落點**:已讀,無 finding——`impact-hook.py` 現在確實掛在「棧別提問表態閘」與「codex-harness」兩篇(非講推筆記的),retrieval-ranking.md 現在確實是 0 about_code,加入合理;`retrieval-ranking`/`節點還原`/`每支檔有家` 三個落點各自對應甲/乙/S18 的改動範圍,無牛頭不對馬嘴。
- **實務隱患**:已讀,無 finding(見文末鏡頭作答)。
- **驗收怎麼跑**:已讀,無 finding——十五個 `-k` 關鍵字逐一核對 spec 內 `[test:]` 標記,無遺漏(上一輪 G12/H 系列已修正過的那條 `impact_diff_keeps_homes` 這次確實在清單裡)。
- **回頭條件**:已讀,無 finding——四條 REVISIT 都帶日期與可執行動作,符合鐵則四。
- **合約候選**:已讀,無 finding——四條候選逐一比對 S2/S4/S5/S7,語意一致。
- **審計修正紀錄**:已讀,無 finding(逐項機械複核見下方「第二輪折入複核」)。

## Findings

### F1 舊案 d4「無新證據不重提」未在來源節點標記翻案
severity: major
blocking: 是 — 不改,下一個查 `固定席扇出降權_計劃` decisions 的人會看到 d4 仍 `valid: true`、寫著「無新證據不重提」,不知道本案已經重開它,可能誤判本案依據站不住或重複另開一案。
引句:「★這是重開 Enzo 裁過的決定★:Enzo 2026-09-12 同意了本案方向」
- 全篇 18 條裁定與落點段都沒有任何一條指示對 `Projects/固定席扇出降權_計劃.md` 做 `lumos decision-add`/`decision-supersede` 或更新 d4——只在「為什麼」段的散文裡敘述,沒有機械寫回。
- file: `docs/lumos-toolchain-knowledge/Projects/固定席扇出降權_計劃.md:34-38` d4 目前原文仍是「丙(第四條保送)需先把 about 漏標率壓到零,無新證據不重提」,`valid: true`,frontmatter 沒有任何指向本案的欄位。
- 本案 frontmatter 也沒有 `related:` 欄位連回舊案(只在正文 wikilink 提到一次),查詢者要靠 backlinks 才會撞見,不是決策鏈本身講清楚。

### F2 壞交叉引用:`Issues/各棧測試資料夾被當成要家` 不存在
severity: minor
blocking: 否 — 這個連結只是「範圍外」段指向另一個尚未開的修復提交,不影響本案功能本身要不要做、怎麼做。
引句:「每支檔有家的漏洞,另一個提交修,見 [[Issues/各棧測試資料夾被當成要家]]」
- 全篇系統性核對六個 wikilink,只有這一個目標不存在(其餘 `固定席扇出降權_計劃`、`每支檔有家_計劃`、`retrieval-ranking`、`每支檔有家`、`節點還原` 都存在)。
- file: `docs/lumos-toolchain-knowledge/Issues/` 目錄下 54 篇無此檔,`grep -rl 各棧測試資料夾` 全庫只命中本篇自己與凍結副本,沒有第三方筆記記著這個坑——接手人想追這個「另一案」時無處可查。

### F3 「合約候選第 5 條」引用錯誤,對不上「about 不是第四條入口」
severity: minor
blocking: 否 — 同一句已經正確點名「現行測試 ⑨」,實作者照測試名就找得到真正要改的東西,候選編號錯不會讓人做錯決定。
引句:「舊案實作說明與合約候選第 5 條;現行測試 ⑨ 釘著」
- file: `docs/lumos-toolchain-knowledge/Projects/固定席扇出降權_計劃.md:525-526` 合約候選第 5 條原文是「about 判定不覆寫 results 的 `hit` 欄」,講的是別的事;真正對應「about 不是第四條入口」的敘述在候選第 1 條(「有欄無命中的節點,pinned 判定與現況逐 byte 相同」)與「讀側怎麼用」段的散文,不是第 5 條。
- file: `scripts/test_lumos.py:913` 測試 ⑨ 本身引用正確(`★⑨free 候選 about 命中 → 仍 free(不是第四條入口)★`),已核對存在。

### F4 [S14] `home_audit.py sample` 沒有樣本數旗標,「全部 46 對」與「隨機 20 對」無法從介面分辨
severity: minor
blocking: 否 — 實作者遇到這個空白通常會自己補一個 `--n`/`--all` 之類參數把功能做出來,不會因此做出錯的系統,只是三個月後的接手人照著驗收段落的指令逐字打會卡住。
引句:「抽出配對、每對附那篇的摘要 KEY 行與那支檔開頭 40 行」
- [S14] 與「驗收怎麼跑」段給的 `sample` 介面只列 `--vault` 與 `--seed`(驗收段用「…」帶過其餘參數),沒有任何欄位能表達「這次要全部 46 對」vs「這次要隨機抽 20 對」。
- REVISIT(2026-11-12)寫「換一個種子再抽一次同樣規模」,「規模」這個詞本身依賴一個目前沒有名字的參數,介面若各自實作者各自命名,會跟這條回頭條件對不上。

## 固定席逐條判(r3-lens.txt)

- **Systems/retrieval-ranking.md**(計劃連結+直接相依,牽連 `governance/eval/retrieval_eval.py`):不破壞——全篇無 ★INVARIANT★/★IRREVERSIBLE★ 標記,S1–S10 是在它既有「impact ranked 固定席」敘事上加一條入口,方向與既有 FLOW 行一致,只是落地後那行「固定席=事故+合約」字面要跟著更新(這是鐵則一「同一次工作內寫回」的份內事,不算本案破壞它)。
- **Systems/每支檔有家.md**(計劃連結):不破壞——S11–S15 全部是在 `_nodehome_evaluate`/`_nodehome_config` 既有殼子裡加一種新違規與新提醒,沒有動既有五種違規的判定邏輯,`node_home.gate`/`ignore` 兩個既有開關原樣可用。
- **Systems/節點還原.md**(計劃連結):不破壞——現有 SOP 第 4 步已經在用 `--code`,本案只是把它從「隱含慣例」明講成「必要條件」,不推翻任何現有文字。
- **Issues/canary-record未落盤事件.md / code-loop守衛main-direct盲區.md / hook卸載殘留註冊.md / init-force-slug誤用basename.md / vendored測試套件在消費端假紅.md**(五篇事故,皆因計劃提到 `governance/eval/retrieval-goldset.json` 而牽連):不影響——五篇分別講 canary 落盤驗證、code-loop main-direct 盲區、hook 卸載殘留註冊、init --force slug 誤用、vendored 測試假紅,內容都跟 about_code/每支檔有家/固定席排序無關,本案不碰這幾支機制,牽連純屬「同一支檔案被提到」的表面關聯。

## 第二輪折入複核(指定重點:S2/S6/S8/S11/S14/S16/S18)

- **[S2]**:已讀無 finding——實跑確認測試 ⑨(`scripts/test_lumos.py:913`)目前斷言「free 候選 about 命中 → 仍 free」,fixture 裡 `Free.md` 的 about_code 命中 `src/svc.py` 且無合約,S2 改寫後它會變成家並升為必推,測試需要且可以照 spec 改法調整,邏輯自洽。
- **[S6]**:已讀無 finding——`cmd_dispatch_lens` 差異模式(`scripts/lumos:22910`)確實直接呼叫 `cmd_impact_diff`,S6 第一小項落地後自然吃到;計劃模式(`scripts/lumos:23113` 起)確實是子行程呼叫 `impact --file --json` 且未帶 `--ranked`,只讀 `direct/indirect/incidents`,跟 r1 機械重現一致,S6 第三小項要加的「家」頂層鍵有既有「lane」鍵(`scripts/lumos:21720`)當先例可循。
- **[S8]**:已讀無 finding——`scripts/lumos:19523` 與 `:23150` 兩處措辭「帶硬合約或出過事故的一定要看」「沒牽到任何帶合約/事故的節點」逐字存在,`_LENS_KIND` 目前確實只有 direct/indirect/incident 三種,S8 要補的「家」標記與種類表項目都是待新增,不是幻覺。
- **[S11]**:已讀無 finding——`run_doctor` 目前 S8/S9/S10 三段(`scripts/lumos:2113-2151`)存在且「S11」段名未被佔用,S11 計畫「S10 之後新開一段」不會撞號;`check-j-regen-guard.md` 確實記著「不蓋 regen 章完全繞過」這個天花板,S11 的「實務隱患」段落有照實承認同一件事。
- **[S14]**:見 F4——抽查程序的可重跑性本身沒問題,但樣本數參數缺失。
- **[S16]**:已讀無 finding——`impact-hook.py` 的單檔過濾(`scripts/hooks/claude/impact-hook.py:147` 起)目前只認副檔名/首行 `#!`,沒有任何找圖譜位置的邏輯,S16 把非程式檔觸發挪到另案、只留 lumos 那層認家,跟 r2 H1 的機械重現一致,沒有走回頭路。
- **[S18]**:已讀無 finding,且**已實跑覆核**——`python3 scripts/lumos --vault docs/lumos-toolchain-knowledge stale --candidate --match 固定席` 在唯讀暫存副本上跑出 5 筆,4 筆 `[pass]`(標籤結構收編落地、edit面查詢品質閘落地、標註刷新落地、about_code讀側四項落地)+1 筆已是 `[stale]`(受波及合約測試真跑閘落地,不必再標);加上兩篇指令掃不到的「檢索排序v1」「檢索goldset評測」(逐字核對這兩篇 `revalidate_when` 確實沒有「固定席」字樣),點名三篇+指令三篇=6 篇,跟 [S18] 宣稱的六篇數字對得上。

## 實務隱患鏡頭(要求5)

- **效能(Edit 前推筆記在熱路徑上)**:無新增隱患——`_nodehome_*` 現有行程內快取模式(鍵 `str(env.vault)`)是既有慣例,S1 沿用同一套,沒有引入新的子行程或 git 呼叫;spec 自報的 30 秒/20 秒預算數字跟 `scripts/hooks/claude/impact-hook.py:61/64` 的 `timeout=30.0` 對得上。
- **噪音與召回的取捨**:有隱患但已被 S4(大檔整批不認家)+S14(上線前抽查)+S15(寫入當下提醒)三道夾住,天花板是「正文順帶提到但其實不是在講它」那型錯家,S14 抽查目前唯一缺口是 F4 的樣本數介面問題,不影響設計本身站不站得住。
- **舊專案相容**:無新隱患——`node_home.gate`(on/warn/off)與新旋鈕 `LUMOS_IMPACT_HOME` 兩層開關都已在程式碼裡有原語(`_nodehome_config`/`_impact_knob` 既有函式),沒跑 `lumos update` 的專案不受影響,跟 spec 宣稱一致。
- **回滾(關掉旋鈕能不能完全回到原樣)**:無新隱患——`LUMOS_IMPACT_HOME=0` 這個旋鈕目前確實不存在(spec 自陳新增),但 knob=0 分支要退回的舊行為(三軸排序、about_hit 判定)程式碼都還在,測試 fixture 已經有 `knob=0` 分支的既有斷言可以延伸,不是要重建一套死碼。

總結:最高 severity major,blocking 共 1 條
