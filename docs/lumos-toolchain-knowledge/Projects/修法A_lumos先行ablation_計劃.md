---
type: project
status: done
created: 2026-09-02
updated: 2026-09-02
tags:
  - type/project
  - status/done
  - scope/governance
related:
  - "[[Issues/散文紀律沒有退場機制]]"
  - "[[Issues/嚴謹度分配偏向機械層]]"
  - "[[Projects/指令索引與情境測試_計劃]]"
  - "[[Projects/世界repo掃描2026-09-02_調研]]"
summary: |-
  FLAG:DECISION
  KEY:修法 A 提前開跑(Enzo 2026-09-02「好」,原排 09-20)——第一次對自家散文紀律做真 ablation:標的=CLAUDE.md「第一個工具呼叫是 lumos」那一小節+入口 hook 同句提醒;帶/不帶各跑同一組題,比情境探針的通過率
  KEY:兩組定義(預註冊,跑完不得改)——with=現況;without=沙盒 CLAUDE.md 砍「### 第一個工具呼叫是 lumos」到「### 三條鐵則」之前那一節+環境變數 LUMOS_ENTRY_HOOK_OFF=1 讓 SessionStart 不注入同句;★兩組都保留★ skill 說明文字、PreToolUse impact-hook(機械)、Stop hook、## 標題與兩行前提——量的精確是「那段程序性散文」的邊際貢獻
  KEY:題目集=commands.jsonl 23 題+answers.jsonl 5 題=28 題;每題每組跑 3 次(=每組 84 場);4 個沙盒平行(每組 4 shard);沿週抽查參數 --timeout 600 --max-turns 18;★第一輪實跑(09-02)推翻「$0 無約束」:真約束是帳號用量配額,4 路平行 35 分鐘就撞上限,每 5 小時窗口約 55 場;168 場要跨 2–3 個窗口★
  KEY:四個尺(預註冊)——M1 通過率(期望指令在禁做動作之前)/M2 整場有沒有敲過 lumos/M3 首次敲 lumos 的步數中位(只算有敲的場)/M4 答案題 5 題正確率;讀法寫死見正文,★差距門檻 5pp 與 15pp 在結果出來前定★
  KEY:儀器改動三件(最小)——scenario_probe 加 --runs/--arm 與 first_lumos_idx/ever_lumos 欄;lumos-entry-hook 加 LUMOS_ENTRY_HOOK_OFF 開關(兩行,預設行為不變);新 runner governance/eval/ablation_lumos_first.py 切 shard 平行跑+合併出對照表;純讀既有題庫、不動判準
  KEY:★結果(2026-09-02,見 [[Verification/2026-09-02_修法A_lumos先行ablation結果]])★——M1 通過率 with 79/84=94.0% vs without 49/84=58.3%,差 35.7pp ≥ 門檻 15pp → 那一節有效、留,本專案第一條被前後量過的紀律;M2 敲過率 100% vs 73.8%(拔掉後四分之一場次整場不敲、直接 grep 到底);答案內容正確率 15/15 vs 14/15(事後分析)=改的是路徑不是答案;失分主效應是「先查圖譜再 grep」行為本身,非對照表(只 s17-ci 屬表才有的對應)
  KEY:design-loop 跳過(小改動,計劃筆記註明):儀器改動 <100 行、判準不動、Enzo 口頭核准兩組定義與題數;預註冊即本案的「退場條件在結果前寫死」
decisions:
  - content: 兩組定義=拔散文兩處(CLAUDE.md 小節+入口 hook 同句)、保留 skill 與機械 hook;先跑 28 題(指令 23+答案 5)×3 次×2 組,4 平行
    id: d1
    context: 世界掃描給修法 A 三個實驗設計輸入(重跑/看第幾步/成對衝突)後,Enzo 問「9/20 的實驗有沒有辦法直接做」;評估儀器八成現成,缺三個小補丁;Enzo 回「好」
    why_chosen: 拔到 skill 層要動機器共用的 ~/.claude/skills,兩組會互染且改動面大;機械 hook 屬 D 方向(往機械化搬)非本案標的。28 題而非 51 題=先 3 小時拿到第一份數字,paraphrase/discipline/absence 三組題型不同(換句話說/紀律/查不到換詞)混進來會稀釋「第一刀」這個問題
    decided: 2026-09-02
    valid: true
---
# 修法A_lumos先行ablation_計劃

> 白話:我們有條家規「動手前第一件事先查知識庫」,寫在 CLAUDE.md 開頭,每次開對話 hook 還會再唸一次。這條規矩從沒被量過有沒有用。這次拿現成的情境探針,同一批題目跑兩組——一組照現況、一組把那段散文拿掉——比 Claude 有沒有照樣先去查。★在跑之前把怎麼讀結果寫死,跑完不得回頭改★(沿 `governance/eval/context-vs-full-preregistration.md` 慣例)。

PRIOR-ART: ① 最小解層級——既有情境探針(scripts/scenario_probe.py)加兩個旗標與兩個欄位,判準不動;② 世界解過沒——有,prompt ablation 是標準做法,官方 `claude plugin eval --ablation with-without` 同形狀但早期存取跑不了;skill-creator trigger eval 的「每題 3 次」直接抄;③ 裁定=borrow-design,零依賴原生實作。

## 為什麼是這一條

[[Issues/散文紀律沒有退場機制]] 修法 A 明寫首選標的=「動任何既有系統之前,第一個工具呼叫必須是 lumos」:最貴、最常載入、形狀最標準的程序性指示,與 TDAD 打中的「請照測試先行做」同型。挑無關痛癢的來打,這輪就白做。

## 兩組(預註冊)

| 組 | CLAUDE.md | SessionStart 入口 hook | 保留不動 |
|---|---|---|---|
| **with**(現況) | 原樣 | 注入「第一個工具呼叫是 lumos search / context…」 | — |
| **without** | 沙盒內砍掉「### 第一個工具呼叫是 `lumos`」起、到「### 三條鐵則」之前那一節(表格+四條實測+破口+hook 說明) | 環境變數 `LUMOS_ENTRY_HOOK_OFF=1`,hook 靜默退出 | ## 標題與兩行前提(圖譜是「為什麼」的唯一來源)、三條鐵則、白話回報、skill 觸發表、`~/.claude/skills` 全部、PreToolUse impact-hook、Stop hook |

**為什麼保留 skill 與機械 hook**:skill 的說明文字也寫「先用 lumos 查」,但它住在機器共用目錄,拔了兩組互染;機械 hook 是 D 方向(往機械化搬)的東西,不是本案要量的散文。這樣量出來的差=「那段散文在 skill+hook 之上多出的貢獻」。若差≈0,不代表「圖譜先行」沒用,只代表**那段散文**是死重量。

## 題目與次數

- 題庫:`governance/scenarios/commands.jsonl`(23 題,查指令)+ `answers.jsonl`(5 題,要答對事實)= 28 題。不含 paraphrase/discipline/absence(題型不同,另輪)。
- 每題每組 3 次 → 每組 84 場、共 168 場。
- 4 個沙盒平行(每組 4 shard,round-robin 分題),參數沿週抽查:`--timeout 600 --max-turns 18`。
- 估時:週抽查 8 題中位 150–400 秒/題,168 場 ÷ 4 路 ≈ 3 小時。錢:headless 走 OAuth,$0。

## 四個尺與讀法(★預註冊,結果出來前寫死★)

| 尺 | 定義 | 來源欄位 |
|---|---|---|
| M1 通過率 | 期望的 lumos 指令出現在任何禁做動作(Grep/Read/grep…)之前 | `passed` |
| M2 敲過率 | 整場有沒有任何一次 Bash 帶 `lumos` | `ever_lumos`(新欄) |
| M3 首次步數 | 第一次敲 lumos 是第幾個工具呼叫(只算有敲的場),取中位 | `first_lumos_idx`(新欄) |
| M4 答案正確率 | 5 題答案題 `answer_expect` 全中 | `passed`(answers 子集) |

讀法(以 M1 的兩組差、單位=百分點 pp;84 場中 1 場≈1.2pp):

1. **差 ≤ 5pp**(≤4 場):那段散文在 skill+hook 之上**無可量貢獻**→ 成為 [[Issues/散文紀律沒有退場機制]] 修法 B 窄門的**第一個候選**(附本量測)。★不自動刪,Enzo 裁★。
2. **差 ≥ 15pp**(≥13 場):有效,留;記為本專案第一條**被量過**的紀律,Issue 的「零條被量過」清零。
3. **5–15pp**:不下結論。看 M3——若 without 組首次步數明顯後移(中位 +2 步以上)=「會敲但不是第一刀」,那段散文的作用是提前而非有無;決定要不要加 paraphrase 12 題重跑。
4. **M4 若 without 更高**(答案題正確率反而升):TDAD 型訊號(程序散文讓結果變差),不論 M1 如何都寫進 Issue 當獨立發現。
5. **儀器噪音**:with 組同題三次結果不一致的題數 ÷ 28 = 抖動率。**>30% 則本次結論只算「初步」**,要加次數重跑才准進 B 窄門。
6. 任一組因限流/超時損失 >10% 場次(>8 場)→ 補跑該 shard 一次;仍缺則結論降級為「初步」,缺的場次明列。

## 退場 / 失敗處置

- 儀器改動若讓週抽查(`--runs 1 --arm with` 預設)行為改變 → 立即回退;預設路徑必須與改前逐位元同輸出(測試釘)。
- 實驗跑不完(限流連續失敗)→ 記部分結果與失敗 shard,只補跑一次;不無限重試。
- 結果不論方向都寫 Verification 節點,`plan_refs` 回指本篇;原始 JSON 存 `governance/eval/ablation-lumos-first/<日期>/`(不入 git,節點記數字)。

## 儀器改動(三件,最小)

1. `scripts/scenario_probe.py`:`--runs N`(預設 1,每題重跑並記 run 序)、`--arm with|without`(預設 with;without 在 make_sandbox commit 前砍 CLAUDE.md 小節、run_one 帶 `LUMOS_ENTRY_HOOK_OFF=1`)、結果多兩欄 `first_lumos_idx`/`ever_lumos`;`strip_lumos_first_rule()` 抽純函式可測;找不到小節邊界→炸(實驗無效比靜默跑完好)。
2. `scripts/hooks/claude/lumos-entry-hook.py`:main 開頭 `LUMOS_ENTRY_HOOK_OFF=1` → return 0;同步 cp 到 `~/.claude/hooks/`(安裝的是複本,已 diff 確認相同)。
3. `governance/eval/ablation_lumos_first.py`:切 shard、平行呼叫探針、合併四個尺出對照表(json+md);可 resume(已有輸出的 shard 跳過)。★同日第二版改逐題補缺(見〈第一輪實跑〉)★。
4. (09-02 傍晚,Enzo「照你建議」)runner 加**題目鑑別力分類**(`classify_question`:區分/不區分都過/不區分都不過/反向/弱;借 skill-creator analyzer 抓「不管有沒有都過」的斷言)——本案 28 題:區分 10、都過 13、都不過 1、反向 1、弱 3;13 題「都過」對這條規矩不具鑑別力,是之後「每條規矩綁自己的題」的起點。
5. runner 加 `--max-per-window`(預設 50):五小時內開滿就不再開新工作,之後重跑補缺——事前上限,對應 SWE-agent per-instance / bmad per-story 的窗口版;配合 `--wait-on-limit` 兩道。
6. `governance/eval/rule_conflict_scan.py`:規矩成對衝突**字面級初篩**(切句→留指令性句→按關鍵詞分群→同詞下正負並存或數字不一致列候選)。首跑:433 句指令性句、45 個候選群;候選交乾淨 agent 回原檔逐群判真衝突/同面/過期並存,結論記 [[Issues/散文紀律沒有退場機制]]。

## 誠實界線

- 兩組共用同一份 skill 文字,所以「圖譜先行」這個理念本身沒被拔乾淨——本案量的是**CLAUDE.md 那段+hook 那句**的邊際貢獻,不是理念的總效果。
- 探針判準是「敲對指令」,不是「任務做對」;只有 5 題答案題碰到結果面。
- 每週抽查歷史不能當抖動基線(每週不同題),抖動只能從本次 with 組同題三次估。
- 模型版本=跑當天 `claude -p` 預設;跨日重跑要記版本。

## 第一輪實跑(2026-09-02 10:51–11:30)——★成本不是錢,是帳號配額★

- **發生什麼**:4 路平行、8 個 shard 跑 168 場,35 分鐘後撞到帳號用量上限(`You've hit your session limit · resets 12:10pm`),之後每場 4 秒回、零工具呼叫,探針原判準記成「沒敲到期望指令」——168 場裡 **115 場是假失敗**,只有 **53 場有效**(帶 27、不帶 26)。「headless 走 OAuth 所以 $0」這句在本案是錯的框架:**每 5 小時窗口約 50–55 場探針**是硬約束,而且是跟 Enzo 互動 session 共用的配額(本 session 期間仍可運作,是否擋到終端機沒驗)。
- **儀器修正(同日)**:①探針 `is_limit_hit`(零呼叫+上限訊息)→ 記 `limit_hit`、reason 標儀器例外、不算分;②探針 `--wait-on-limit N`(撞到每 300 秒重試同一場,預設 0 週抽查不受影響);③runner 改逐題工作單位:每題數「有效」場次只補缺的、輸出一檔一次不覆蓋、舊 shard 檔補標;預設 2 路(瓶頸是配額不是機器)。測試 +3 條(`test_is_limit_hit`/`test_needed_counts_only_valid`/merge 排除)。
- **有效 53 場的初步數字(★未達預註冊門檻的完整性,不下結論★)**:M1 帶 27/27=100%、不帶 21/26=80.8%;M2 帶 27/27、不帶 25/26;M3 兩組首次步數中位都是 1(第 0 步幾乎都是調 skill);M4 答案題零場有效。差全集中兩題:`s17-ci`(帶 3/3、不帶 0/3)與 `s06-impact`(帶 3/3、不帶 1/3);其餘 8 題兩組全過。
- **觀察(不改判準,結果讀時要記得)**:被拔掉的那一節不只是「第一刀先 lumos」的勸告,還帶著**「你心裡想的是…→先敲這個」對照表**——`s17-ci` 期望 `lumos ci-wait/ci-status`,那個對應關係只寫在表裡(skill 索引也有,但 Claude 沒翻到)。所以 without 組的失分可能有一部分是**丟了指令索引**而非丟了程序性勸告;全量出來後要拆看:失分題的期望指令在被拔的表裡有沒有專屬那一列。若多數失分題都是「表裡才有的對應」,結論要寫成「那一節的價值在索引表,不在勸告句」——這本身就是可執行的修法(把表留著、勸告句拿掉再量一次)。
- **下一步待 Enzo 裁**:剩 115 場,以每窗口 ~55 場算要跨 2–3 個 5 小時窗口;runner 現已能自動等重置補缺。選項=現在接著跑(2 路,會吃掉下午的互動配額)/ 指定晚上開跑 / 先把每題降到 1 次拿全題覆蓋再補。

## 結果(2026-09-02)

跑完、門檻對完,數字與解讀全在 [[Verification/2026-09-02_修法A_lumos先行ablation結果]]。一句話:差 35.7pp,那一節有效、留;它改的是「先查圖譜還是先 grep」的路徑,不是答案對不對。後續兩件掛在 [[Issues/散文紀律沒有退場機制]] 的 09-20 REVISIT:①要不要拆「表留、勸告句拿掉」再量第三組;②修法 B 窄門怎麼寫。
