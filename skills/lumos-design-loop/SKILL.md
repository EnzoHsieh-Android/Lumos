---
name: lumos-design-loop
description: 寫完一份設計 spec/plan、進實作前用這個——派乾淨 agent 一輪輪對抗審計、每輪偷植 canary 驗審計員有沒有放水、修到 lumos loop status 收斂(連 2 輪 caught 且無 blocker/major)才放行實作。對齊「收斂=進實作綠燈」。trivial 改動(typo/一行/純機械)可跳並註明。觸發詞:設計審完了沒、spec 進實作前、loop 打磨、design loop、審計到收斂。
---

# lumos-design-loop:canary-護的設計審計 loop(進實作前的硬閘)

> **定位(2026-07-18 d4 使用者裁定)**:抬 spec 質量,**非保 spec 正確**——一輪 panel 抓便宜的(矛盾/未定義詞/缺失敗路徑)就放行;正確性歸下游 code-loop+測試+驗證,漏網進逃逸帳。**前置加重一律拒**(勿往本 loop 添新守衛;完整裁定見圖譜 [[design-loop]] d4)。

**Claude 編排,lumos 出原語。** 你(主對話)用 Agent tool 派審計員、判讀、修 spec;lumos 出 `canary record`/`loop status` 記錄與算收斂。lumos 不 spawn agent。

## 何時用 / 何時跳
- **用**:brainstorming 產出 spec/設計 doc 後、進 writing-plans/實作**前**。對象=設計/spec 的對抗審計(非圖譜自足性審計)。
- **硬閘(紀律強制,非技術鎖)**:`lumos loop status <id> --need 2 --gate --spec <計劃節點.md 路徑> --repo <repo根>` 回 exit 0(GATE PASS:K-streak ∧ G1 引用座標 ∧ G2 發現枯竭)前**不得進實作**。lumos 擋不住「不跑就實作」——靠你記得調用 + 誠實。**高風險 spec(金流/對外寄送/prod 不可逆/守衛面)建議 `--need 3`**(對齊自動 loop 的 risk-tiered-review 分級;手動 loop 無機械分級,靠你自判)。
- **trivial 可跳**:改 typo / 一行 / 純機械(rename、補欄位、連結修復)→ 跳 loop,但**寫一句為什麼跳**(commit message)。
- **light 檔(輕量路徑,小而不 trivial 的 spec)**:補「trivial 完全跳過」與「standard 完整 panel」中間的缺檔——小 spec(加個小 flag / 改個非金流小邏輯)便宜審。**進場兩道**:① **硬否決**(命中任一即**不給 light**、走完整 loop):碰金流/對外寄送/prod 不可逆/守衛面(risk-tiered 四類)、動到 ★INVARIANT★ 硬合約、或改動體積偏大;② 以上全沒中 + 體積小(**先驗暫用值:預估實作改動 ≲50 行且孤立——SDD 生態經驗值,2026-07-21 外審吸收;replay 校準後以數據值取代**)→ 走 light。忘了判 → **預設走完整 loop(fail-safe,永不更少)**。⚠ **M0 的硬否決靠你自核(honor-system),不比你誠實更可靠——M1 才機械化成 filter,別當它已自動擋**。跑什麼見下方〈light 檔〉。設計脈絡見圖譜 [[design-loop輕量檔_計劃]]。
- **★真相入口(2026-07-21 收編,見 [[全盤外審2026-07_調研]] finding 1)★**:被審 spec 的**唯一可寫真檔=圖譜計劃節點**(`docs/{project}-knowledge/Projects/<主題>_計劃.md`)——與 CLAUDE.md「計劃/設計也歸圖譜」對齊。**`docs/design/` 已降唯讀歷史,不再新增、不再折入**(舊 loop 的 docs/design 檔保留供考古)。loop 全程:工作副本從計劃節點複製、折入只回寫計劃節點、gate `--spec` 指計劃節點路徑。
- **loop id** = 計劃節點檔名去 `_計劃`/`_調研` 後綴、轉 kebab(`Projects/design-loop輕量檔_計劃.md` → `design-loop輕量檔`)。舊 docs/design 時代的 id 慣例只適用歷史紀錄。

## 每一輪(照做)

1. **複製**計劃節點檔 → 工作副本 `/tmp/<id>-rN.md`。**N/型別/席數/記帳模板一律問 `lumos loop next <id> [--tier ..] [--spec ..]`**(M1包 2026-07-21:帳本吐唯一下一動作,不靠記憶手算;phase=escalate 表 light 已 ratchet 須升級、gate-pending 表資訊不足補參數)。**同時 `sha256sum <計劃節點>` 留存本輪 reviewed hash**(記帳 `--reviewed` 用——雙 hash 鏈的派工快照)。
2. **植一個 canary**(只進工作副本,**真檔永不含**):additive、**類型由 N 決定** `清單[(N−1) mod 4]`:
   - (a) 壞 §/章節交叉引用(指向不存在的 §N)
   - (b) 未定義旗標 `--xxx`(引入卻不在任何指令/簽名)
   - (c) 未定義欄位/常數(憑空的 frontmatter 欄位或常數名)
   - (d) 未定義產物/檔名(憑空的 `xxx.json`,不在 schema/它處)。**(d) 型保持裸檔名(勿帶 repo 路徑如 `configs/foo.json`)——裸檔名無 `/`,天然在 refcheck 抽取域外,canary 防線不受影響;帶路徑會被步驟 2.5 機械吃掉、canary 作廢**
   嵌唯一 token 定位。**canary 要「認真審就抓得到、但不一眼看穿」**——太細=不公平、太明顯=訊號弱(校準鐵則)。
   **生成硬化三條(2026-07-10,borrow FLAWS arXiv 2511.21843 / IBIR ACM TOSEM 2022;設計見 [[canary生成硬化_計劃]])**:
   - **載重錨定**:植入位置不隨機挑段——先掃 spec 抽 3-5 條載重最高的可證偽 claim(演算法定義/門檻數字/整合接點),canary 植在其中一條的失效變體上。canary 測「有沒有讀懂核心」,不是「有沒有掃過周邊」。
   - **難度探針(FLAWS difficulty filter 反向適配)**:植完、派審計員前,派一個 **haiku 探針**(只給被植段落 ±20 行,prompt「這段有沒有內部不一致/未定義引用?」):haiku 一眼抓到 → 太明顯,重植更藏的變體再探(上限 2 次);沒抓到 → 難度合格。探針結果記入該輪 canary note(`probe:pass|recraft×N`)。理由:FLAWS 實測生成者自己抓得到的錯 61-93% 被過濾——不濾,caught 會灌水(mutation score 冗餘教訓同源)。
   - **事故反轉(IBIR 模式,機會性)**:型別輪替前先查事故語料(`lumos search --path Issues` + `pitfall_when` 命中 spec 主題域):有匹配 → 把該事故的「修法」反轉成 canary(標 `type=incident-inv`),取代該 slot 的通用型別;無匹配 → 照舊輪替。事故驅動的植錯比盲 mutation 寫實且有區分力(IBIR 實證)。
2.5. **機械核對(refcheck,對工作副本)**:`lumos refcheck /tmp/<id>-rN.md --repo <repo根> --json`。missing/line_out_of_range=機械 finding,直接修**真檔 spec**(記入審計修正紀錄、標「機械 refcheck」);manifest(ok 宣稱+excerpts)留存、步驟 3 餵審計員。refcheck 只驗 spec→repo 指涉、不驗 spec 內部一致性——內部一致性是 canary 保留地、審計員責任田。
2.6. **pitfalls 核對(派審計員前)**:`lumos pitfalls <計劃節點.md> --check`;rc 1(缺「## 實務隱患」節)→ 先在**真檔 spec** 補「## 實務隱患」節再繼續。`lumos pitfalls <計劃節點.md>`(不帶 --check)的提問清單附給步驟 3 的審計員當鏡頭之一。
2.7. **pre-flight 排乾(cascade;2026-07-16 提效 M1,設計見 [[design-loop提效_計劃]];首輪前跑一次,r2+ 不重跑)**:派 1 個便宜 agent 拿固定 checklist 掃**真檔 spec**——未定義旗標/欄位/檔名、章節交叉引用、範圍刀自違(「明確不做」被其他段偷偷違反)、CLI touchpoint(白名單/Check 字母撞名/函式簽名)、測試策略與本文條目一一對應。命中直接修真檔(記入審計修正紀錄標「pre-flight」,不算 loop findings)。理由:實測 r1 大宗是清單型缺陷(fromscratch-m1 r1 九條裡五條此型),先機械排乾讓 panel 從高起點審,一輪收斂(K=1)才從理論變可能;cascade=便宜先掃、貴的審剩下(ICML 2025 cascade 文獻)。
3. **派乾淨審計員**:Agent tool、`model: sonnet`(連 2 次 missed 後升 opus)、**不告知有 canary**、指向工作副本、**refute framing(把工作副本當外部第三方的投稿審,不是你/本系統寫的——挑出投稿者沒看到的洞)**:要它逐節讀、主動找洞(未定義詞/壞引用/不一致/矛盾/可執行性 gap),逐條標 severity;**附步驟 2.5 的 refcheck manifest**——manifest 內宣稱的存在性/行號已機械驗訖,查證力氣聚焦語意;manifest 非宣稱全集,散文裡的現況假設仍要自己查。**第一次 missed 起就加碼 framing**:「逐節讀,你一定找得到至少一個未定義的詞/壞引用/不一致;沒找到就是你沒讀仔細」。
4. **判讀**:
   - ① **canary 抓到 = 審計員清楚且正確點出那個植入瑕疵的「性質」**(如「§N 不存在」「`--xxx` 未定義」);光 token 出現、或泛泛說「引用怪怪的」不算。
   - ② **最嚴重真 finding**(`clean`=排掉 canary 後無真 finding / `minor` / `major` / `blocker`)= 審計員標的 max。**剝「審計員誤判」要克制**:只有能**指出該 finding 客觀錯在哪**(被實際 spec/code 反證)才剝,**判不準就保留**(寧可高估),剝除理由記進 note。**severity 錨(防 refute framing 通膨,派工模板同句)**:major=照 spec 字面實作會做出**錯的行為**或漏掉合約;文件精度/測試枚舉完整性/措辭=minor,除非漏的是合約級(2026-07-16 提效 M1)。
   - ③ **辯方 refute(路由制,2026-07-16 提效 M1)**:存活 ≥major 先分流——(i) **機械證實免辯方**:有可執行證據且編排者已自核 file:line 為真(regex 實跑/行號實查)→ 直接折入;(ii) **多席一致+各自獨立證據 → 直接折入**;(iii) 只有**低共識**(單席獨有/席間 severity 分歧/證據座標缺失)才派辯方——用可觀測訊號路由,不用模型口頭 confidence。對 (iii) 派 1 個獨立**辯方,預設 Codex**(`codex exec --sandbox read-only`,乾淨脈絡、**不傳 auditor 報告結論**;2026-07-18 S5——判決單點最怕同門盲點,外家反證價值最高;成本中性替換,d4 合規;Codex 不可用退 opus 並於 note 註記偏離),framing=「預設這條 finding 假/嚴重度高估,構造反駁證據。必須附 file:line(grep/Read 實際代碼),光說『沒問題』不算;若該 finding 真無任何查證行(因此鎖 major),你也得拿反證 file:line 才能降,拿不出則維持」。辯方回「真(維持原 severity)」或「假(降到 minor/clean)+file:line」。被駁倒(假)→ 該 finding 降級、**不折**、在審計紀錄標「辯方反證:<file:line>」。
   - ④ **該輪 severity = 辯方裁決後存活 findings 的最高**(編排者機械取 max,取代 ② 自剝;辯方帶證據裁、同 judge-severity-gate 精神)。辯方只買 code 層假陽性,業務層留人。
5. **記錄(M1包 2026-07-21 時序裁定:caught 輪的 record 移到步驟 7 收尾之後——「fold→fold-check→grep=0→record」連續序列,record 帶 `--spec <計劃節點> --reviewed <步驟1 快照>` 使 hash=post-fold 版;missed 輪無 fold,當場 record 即收尾)**:`lumos canary record caught|missed --loop <id> --severity <worst> --findings <M> --auditor sonnet --spec <計劃節點.md> --reviewed <sha256> [--tier <t>] --note "r<N> type=<a-d> ..."`。**中斷恢復(第二帳)**:log 無該輪 record 但 spec 審計修正紀錄有該輪條目 → 人工補 record 再繼續(防「折了沒記」窗:重派已折輪+ratchet 訊號蒸發)。`<worst>` = ④ 辯方重算後的存活 max(非 ② 原評);`<M>` = ④ 辯方裁決後存活折入的真 finding 條數(canary 不計;missed 輪不折記 0)——供收斂閘 G2 枯竭錨機械讀取。
6. **漏抓 → 該輪判決不採信**(仍是一筆 missed record、仍算進 cap):**不折 findings**,直接下一輪(N+1、自動換 canary 類型、framing 加碼)。
7. **抓到 → 只折辯方存活的真 finding 進計劃節點**(被辯方駁倒的不折、已在審計紀錄標「辯方反證:<file:line>」);折時把該輪寫進 spec 的**審計修正紀錄**。寫完紀錄後:**跑 `lumos fold-check <計劃節點.md>`** → 讀每個 flag、逐段勾「鏡像段與 body 一致」(summary/json fence/審計修正紀錄/誠實天花板)、解掉每個 drift → 確認一致。**再派一個便宜 agent 只看本輪折入 diff 做 fold 迷你核對(2026-07-16 提效 M1)**:「動了規則的段,鏡像段(測試策略/摘要/他章)跟了嗎?新句與既有句打架嗎?新引入的詞/旗標/欄位有定義嗎?」——r3 型『補丁沒同步』findings 幾乎全是此型,5 分鐘核對換一整輪。之後 **`grep -c '<canary token>' <計劃節點.md>` 必須為 0**(canary 未混進真檔)再 `git commit`(message 記該輪 canary+severity;圖譜節點 commit 天然過 pre-commit gate)。
8. **問收斂**:`lumos loop status <id> --need 2 --gate --spec <計劃節點.md> --repo <repo根>`(K=2;證據閘=K-streak ∧ G1 引用座標 refcheck ∧ G2 發現枯竭)→ **exit 0(GATE PASS)出 loop**;exit 1 → 回 step 1(逐錨明細指出斷在哪)。
   - **`[NEEDS CLARIFICATION]` 慣例(borrow:spec-kit)**:spec 內任何未解的 `[NEEDS CLARIFICATION: 問題]` 標記 = **視同 blocker,不得收斂**(gate 前自查 `grep -c 'NEEDS CLARIFICATION' <spec>` 必須 0)。含糊之處寫成這個標記而不是含糊帶過——把「還不確定」變機械可擋。

> **派工模板**:審計員/辯方的完整 dispatch prompt(輪次語境加碼、查證義務、反駁路線客製)見本 skill 目錄 `templates.md` §1-2(2026-07-07 Landmark 實戰抽取)——派工以模板為準,本文 framing 是摘要。

## 護欄
- **連 2 次漏抓**(canary-log 最近 2 筆都 missed;中間一筆 caught 即重置)**→ 升級**:① sonnet→opus;②(soft、人工判斷)把 spec 切小,獨立子段各自開 loop(v1 不自動化)。
- **max cap = 6 筆 record**:到頂仍未收斂 → **停、把現況攤給人**、記一句「達 cap 未收斂」。別無限燒。
- **實質收斂 early-exit(2026-07-07 Landmark 實戰調參)**:連 K 輪 caught 且無 blocker/major、**且新 findings 全為文件精度級 minor** 時,編排者可**提前向人攤牌請裁「實質收斂」**,不必跑滿 cap——「你一定找得到」framing 保證每輪必交 minor,G2 數字枯竭天生壓不到底,這是誠實出口(人裁、留痕記入 loop note)。⚠ 僅限手動 loop;自主 loop 無人可攤牌,其對應機制=unconverged requeue 留人,不適用此條。

## 平行 panel 模式(≤3 輪壓縮,2026-07-09;取代 6 輪同族循序,設計見 [[loop三輪壓縮_計劃]])
6 輪同族循序=相關信號(「9 judge 2 票」)且 framing 對抗 G2 收斂逼跑滿 cap。壓縮=**買獨立廣度不買相關深度**:
- **一輪 = 平行派 W 個多樣審計員**(W 由 tier:`difficulty.params` 的 `panel_width`,standard=3/high=5),不同 canary 型別(跨 slot 輪替 a/b/c/d)+ 不同鏡頭(正確性/邊界/整合)。**r1 其中一席改無鏡頭通才席(2026-07-16 replay baseline 實證:窄鏡頭隧道視野漏掉的洞被通才一發抓走——首輪買廣度;r2+ delta 輪恢復鏡頭分工買深度;見 [[Verification/2026-07-16_replay校準baseline_v0]])**+ ≥1 跨家族(外家模型:**Codex CLI** `codex exec --sandbox read-only`(2026-07-10 起本機可用)或 qwen(自主 loop);不帶 canary、只作否決)。每審計員各自 canary → 注意力檢查平行做。**同輪 W 個 canary 不得同型同段——「殺 A 必殺 B」的重複難度 canary 不算獨立注意力票**(冗餘灌水 caught-rate;冗餘識別不可判定 → 靠紀律,borrow mutation score 教訓 2026-07-10)。
- **判定(編排者一次做)**:①逐同族審計員判 canary caught/missed,missed 者 findings 剔除 ②去重(嚴格合一同段同性質)③對存活 ≥major 派辯方 ④算 capture-recapture:各 distinct 缺陷被幾人找到 → `capture_counts`。

### reviewer 結構紀律(2026-07-10 研究明文化;實證出處見 [[reviewer結構明文化_計劃]])
1. **禁互辯(硬規則)**:reviewer 互不通訊、不得看彼此輸出迭代辯論;分歧交編排者裁,不回饋重辯。實證:multi-agent debate 第一輪即劇烈放大 position/verbosity/CoT/bandwagon 偏誤且後續輪不自癒(EMNLP 2025)。範圍限定:實證測的是偏誤軸(另有研究稱 debate 提升準確率軸)——lumos 審計場景選抗偏誤。
2. **編排者=meta-judge**:判讀段(canary 判定/去重/severity max/辯方裁決聚合)是 meta-judge 聚合——只聚合一級判決、不重審內容;judgment pool 越大越抗偏誤(W 寬 panel 的理據;meta-judge position consistency 0.793→0.854)。
3. **關鍵單點判決 ≥3 run 多數決**:「單一判決要當終局」的窄集合(cap 攤牌前的最後裁定、blocker 級辯方裁決有爭議)→ ≥3 獨立乾淨 run 取多數決。誠實限定:同 judge 同輸入跨 run α 最好僅 0.563(<0.8 可靠線)——多數決**只壓 stochastic 變異、不壓 correlated 系統性盲點**,後者靠異家族 panel,兩者不互替。跨家族 slot:≥3 run 中**至少 1 run 用 Codex CLI**(qwen 次選);皆不可用才退異型號同門並於 note 註記偏離。**家族否決保護(2026-07-18 S5)**:任一家族 run 提出 blocker,**不得僅以他家族的同門多數推翻**——降級須具備可執行反證(真跑)或第二外家族確認,拿不出則 blocker 維持(fail toward safety;防同門 2:1 壓掉唯一外家正確意見=重現同門盲點)。
- **記錄**:一輪 W 筆共享 round-id:`lumos canary record caught|missed --loop <id> --round <rid> --severity <s> --capture-counts "2,2,1"`(counts 記在該輪一筆即可)。
- **問收斂**:`lumos loop status <id> --gate --panel --repo <root>`。**兩種帳(2026-07-21 修 skill 漂移,對齊 M2 現碼;見 [[design-loop提效_計劃]] M2)**:①無-cluster 舊帳=**三條合取**:輪有效(caught≥2 且 0 missed,near-perfect)∧ 存活 max≤minor(只算 caught)∧ capture-recapture 殘餘<門檻(**無 counts=fail-closed**);②cluster 帳(首個有效輪帶 `--clusters` 定錨)=**兩條合取**:輪有效 ∧ fold 後無 disputed-major——capture-recapture 與新生 cluster **降 advisory**(非定態目標下封閉族群前提偏弱,不當硬閘)。一個乾淨 panel 輪即收斂(K=1);存活 ≥major → fix → **下一輪嚴格 delta-scoped(2026-07-16 提效 M1,Codex「若只能改一件」)**:審計員**物理上只餵**「折入 diff + 被改 claim 的上下游合約段 + 前輪爭議清單」,**不給整份 spec**(給整份+叮嚀「重點審 delta」無效——審計員照樣全文翻,且折入的新文字持續污染輪間可比性=非定態目標病);另留 **1 席便宜全局哨兵**掃全文防 delta 外漏(弱檢查器,advisory);cap=3。
- **混用守衛**:panel 記錄(帶 round)與 legacy 記錄不可混用,`--panel` 要求全帶 round、否則 rc2(防 None phantom 輪偽過)。
- **收斂判準理據(散文收斂 without 干擾信號)**:framing 汙染 count 不汙染結構 → capture-recapture 讀重疊、ODC 讀 class、AC 讀 coverage;三者繞開被汙染的 count,framing 不動。詳見 [[loop三輪壓縮_計劃]]。

## light 檔(輕量路徑,小 spec;M0 落地 2026-07-21,設計見 [[design-loop輕量檔_計劃]])

補「trivial 完全跳過」與「standard 完整 panel」中間的缺檔。**進場資格見上方〈何時用/何時跳〉的 light 檔條**(硬否決三訊號任一中→不給 light;M0 honor-system 自核、M1 才機械化)。

**跑什麼(壓縮,一輪):**
1. **pre-flight 排乾**(步驟 2.7 照跑)——清單型缺陷機械掃掉,讓單席從高起點審。
2. **派 1 席通才審計員**(§1 模板、**無鏡頭通才 framing**:不指定正確性/邊界/整合某一軸,要它全份逐節挑洞——踩平行 panel 的 r1 通才席實證:窄鏡頭漏的洞通才一發抓走)。canary 照植、refute framing 照舊。
3. **判讀**:canary caught 且辯方裁決後**無存活 ≥major** → 這一輪乾淨。
4. **收斂(M1包 2026-07-21 機械化,取代 M0 人裁出口)**:`lumos loop status <id> --light --gate --spec <計劃節點.md> --repo <root>` → **K=1 機械謂詞**:單席 caught ∧ 存活 max≤minor ∧ 欄位互證 ∧ hash 雙欄鏈驗訖(light 強制 fail-closed)→ rc0 收斂,**不再攤牌人裁**。FAIL 分因:`retryable`(missed,cap=2 內重試一輪)/`ratchet`(任一 caught 輪≥major——**永久**,升 standard 開新 panel loop id(原 id+`-std` 後綴)承接,乾淨輪不洗回)。

**★向上 ratchet(誤判自癒,別跳過)★**:這一輪只要冒出**存活 ≥major**(辯方沒駁倒)→ **light 誤判、立即升 standard**,改走完整 panel 從頭審(tier=standard)。這是「無訊號≠簡單」漏網時的接球手。

**天花板(誠實)**:light 用深度換速度是設計本意;單通才席漏的細微 bug 靠 ratchet + 下游 code-loop/測試 + 逃逸帳兜。M0 進場硬否決是 honor-system,不比 maker 誠實更可靠(M1 才機械化)。light 檔 spec 下游逃逸率該留意(逃逸帳=調價器):偏高=收緊訊號。

## 誠實天花板(收斂後務必向人提醒,別讓 CONVERGED 被當「絕對沒問題」)
> **回報用白話(CLAUDE.md「對人回報用白話」)**:向人講收斂結果與天花板時,少專有名詞——canary/severity/G2/fold/tier 這些第一次出現給一句人話(如 canary=偷埋的假錯,驗審計員有沒有認真看),或乾脆換人話。術語細節留圖譜,別堆進給人看的摘要。目標:人少花一層理解成本。
1. **完整性**:收斂只證「連 2 輪醒著的審計員沒找到 blocker/major」,不證沒有更深的問題。完整性靠多輪 + 多視角,不靠把門檻調嚴。
2. **整合性**:canary-caught / severity / 哪些是「誤判」三個都由植入者(你)自己判、無外部檢查——是**沒閉合的迴歸**,不 tamper-proof。loop 是**可觀測 + 摩擦 + 地板**,不是 oracle。

## 收斂後
`lumos loop status` exit 0 → **收斂即凍結(borrow:Giskard meta-evaluation)**:凍進 `governance/golden/<loop-id>/`——**spec 不再複製第三份**(2026-07-21 真相入口收編:多一份副本=多一個漂移源),改寫 `spec-ref.txt` 一行「`<git commit sha>:<計劃節點路徑>`」(replay 時 `git show <sha>:<路徑>` 即還原凍結版);findings.md 照舊(辯方裁決後存活 findings 清單,這是 golden 獨有數據)。**存活未修的 finding 逐條附一句「接受理由」進 findings.md**(文件精度級/成本不值/延後至何時)——沒理由的未修 finding 不得收斂留痕,防「說有問題就無限改」與「拖著不裁」兩頭(2026-07-17 外部評審吸收,見 [[GPT外部評審吸收_計劃]])——golden 語料是 auditor 校準的時間資產(語料累到 10+ 份即可做 replay 校準:拿凍結 spec 重跑審計、對照已知 findings 算各模型接住率,決定哪類 spec 直接上 opus)。→ 向人**回報收斂 + 上述天花板** → 交 **writing-plans** 出實作計畫 → 實作。

> 設計全文見 `docs/design/2026-06-19-design-loop-skill.md`(B)與 `…-convergence-recording.md`(A 原語)、`…-canary-audit.md`(canary 機制)——**docs/design/ 全目錄已降唯讀歷史(2026-07-21),僅供考古,新設計一律寫圖譜計劃節點**。
