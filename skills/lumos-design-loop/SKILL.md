---
name: lumos-design-loop
description: 寫完一份設計 spec/plan、進實作前用這個——派乾淨 agent 一輪輪對抗審計、每輪偷植 canary 驗審計員有沒有放水、修到 lumos loop status 收斂(連 2 輪 caught 且無 blocker/major)才放行實作。對齊「收斂=進實作綠燈」。trivial 改動(typo/一行/純機械)可跳並註明。觸發詞:設計審完了沒、spec 進實作前、loop 打磨、design loop、審計到收斂。
---

# lumos-design-loop:canary-護的設計審計 loop(進實作前的硬閘)

**Claude 編排,lumos 出原語。** 你(主對話)用 Agent tool 派審計員、判讀、修 spec;lumos 出 `canary record`/`loop status` 記錄與算收斂。lumos 不 spawn agent。

## 何時用 / 何時跳
- **用**:brainstorming 產出 spec/設計 doc 後、進 writing-plans/實作**前**。對象=設計/spec 的對抗審計(非圖譜自足性審計)。
- **硬閘(紀律強制,非技術鎖)**:`lumos loop status <id> --need 2 --gate --spec docs/design/<id>.md --repo <repo根>` 回 exit 0(GATE PASS:K-streak ∧ G1 引用座標 ∧ G2 發現枯竭)前**不得進實作**。lumos 擋不住「不跑就實作」——靠你記得調用 + 誠實。**高風險 spec(金流/對外寄送/prod 不可逆/守衛面)建議 `--need 3`**(對齊自動 loop 的 risk-tiered-review 分級;手動 loop 無機械分級,靠你自判)。
- **trivial 可跳**:改 typo / 一行 / 純機械(rename、補欄位、連結修復)→ 跳 loop,但**寫一句為什麼跳**(commit message)。
- **loop id** = spec 檔名去 `docs/design/` 前綴、去 `.md`、去 `YYYY-MM-DD-` 日期前綴(`docs/design/2026-06-19-foo.md` → `foo`)。

## 每一輪(照做)

1. **複製** `docs/design/<id>.md` → 工作副本 `/tmp/<id>-rN.md`。**N = `lumos loop status <id>` 已有的輪數 + 1**(不靠記憶)。
2. **植一個 canary**(只進工作副本,**真檔永不含**):additive、**類型由 N 決定** `清單[(N−1) mod 4]`:
   - (a) 壞 §/章節交叉引用(指向不存在的 §N)
   - (b) 未定義旗標 `--xxx`(引入卻不在任何指令/簽名)
   - (c) 未定義欄位/常數(憑空的 frontmatter 欄位或常數名)
   - (d) 未定義產物/檔名(憑空的 `xxx.json`,不在 schema/它處)。**(d) 型保持裸檔名(勿帶 repo 路徑如 `configs/foo.json`)——裸檔名無 `/`,天然在 refcheck 抽取域外,canary 防線不受影響;帶路徑會被步驟 2.5 機械吃掉、canary 作廢**
   嵌唯一 token 定位。**canary 要「認真審就抓得到、但不一眼看穿」**——太細=不公平、太明顯=訊號弱(校準鐵則)。
2.5. **機械核對(refcheck,對工作副本)**:`lumos refcheck /tmp/<id>-rN.md --repo <repo根> --json`。missing/line_out_of_range=機械 finding,直接修**真檔 spec**(記入審計修正紀錄、標「機械 refcheck」);manifest(ok 宣稱+excerpts)留存、步驟 3 餵審計員。refcheck 只驗 spec→repo 指涉、不驗 spec 內部一致性——內部一致性是 canary 保留地、審計員責任田。
2.6. **pitfalls 核對(派審計員前)**:`lumos pitfalls docs/design/<id>.md --check`;rc 1(缺「## 實務隱患」節)→ 先在**真檔 spec** 補「## 實務隱患」節再繼續。`lumos pitfalls docs/design/<id>.md`(不帶 --check)的提問清單附給步驟 3 的審計員當鏡頭之一。
3. **派乾淨審計員**:Agent tool、`model: sonnet`(連 2 次 missed 後升 opus)、**不告知有 canary**、指向工作副本、**refute framing(把工作副本當外部第三方的投稿審,不是你/本系統寫的——挑出投稿者沒看到的洞)**:要它逐節讀、主動找洞(未定義詞/壞引用/不一致/矛盾/可執行性 gap),逐條標 severity;**附步驟 2.5 的 refcheck manifest**——manifest 內宣稱的存在性/行號已機械驗訖,查證力氣聚焦語意;manifest 非宣稱全集,散文裡的現況假設仍要自己查。**第一次 missed 起就加碼 framing**:「逐節讀,你一定找得到至少一個未定義的詞/壞引用/不一致;沒找到就是你沒讀仔細」。
4. **判讀**:
   - ① **canary 抓到 = 審計員清楚且正確點出那個植入瑕疵的「性質」**(如「§N 不存在」「`--xxx` 未定義」);光 token 出現、或泛泛說「引用怪怪的」不算。
   - ② **最嚴重真 finding**(`clean`=排掉 canary 後無真 finding / `minor` / `major` / `blocker`)= 審計員標的 max。**剝「審計員誤判」要克制**:只有能**指出該 finding 客觀錯在哪**(被實際 spec/code 反證)才剝,**判不準就保留**(寧可高估),剝除理由記進 note。
   - ③ **辯方 refute(對 ②標為 ≥major 的每條 finding)**:用 Agent tool 派 1 個獨立 opus 辯方(乾淨脈絡、**不傳 auditor 報告結論**),framing=「預設這條 finding 假/嚴重度高估,構造反駁證據。必須附 file:line(grep/Read 實際代碼),光說『沒問題』不算;若該 finding 真無任何查證行(因此鎖 major),你也得拿反證 file:line 才能降,拿不出則維持」。辯方回「真(維持原 severity)」或「假(降到 minor/clean)+file:line」。被駁倒(假)→ 該 finding 降級、**不折**、在審計紀錄標「辯方反證:<file:line>」。
   - ④ **該輪 severity = 辯方裁決後存活 findings 的最高**(編排者機械取 max,取代 ② 自剝;辯方帶證據裁、同 judge-severity-gate 精神)。辯方只買 code 層假陽性,業務層留人。
5. **記錄**:`lumos canary record caught|missed --loop <id> --severity <worst> --findings <M> --auditor sonnet --note "r<N> type=<a-d> <caught|missed> [誤判剝除理由]"`。`<worst>` = ④ 辯方重算後的存活 max(非 ② 原評);`<M>` = ④ 辯方裁決後存活折入的真 finding 條數(canary 不計;missed 輪不折記 0)——供收斂閘 G2 枯竭錨機械讀取。
6. **漏抓 → 該輪判決不採信**(仍是一筆 missed record、仍算進 cap):**不折 findings**,直接下一輪(N+1、自動換 canary 類型、framing 加碼)。
7. **抓到 → 只折辯方存活的真 finding 進 `docs/design/<id>.md`**(被辯方駁倒的不折、已在審計紀錄標「辯方反證:<file:line>」);**commit 前 `grep -c '<canary token>' docs/design/<id>.md` 必須為 0**(確認 canary 沒混進真檔)再 `git commit`(message 記該輪 canary+severity)。折時把該輪寫進 spec 的審計修正紀錄。
8. **問收斂**:`lumos loop status <id> --need 2 --gate --spec docs/design/<id>.md --repo <repo根>`(K=2;證據閘=K-streak ∧ G1 引用座標 refcheck ∧ G2 發現枯竭)→ **exit 0(GATE PASS)出 loop**;exit 1 → 回 step 1(逐錨明細指出斷在哪)。

## 護欄
- **連 2 次漏抓**(canary-log 最近 2 筆都 missed;中間一筆 caught 即重置)**→ 升級**:① sonnet→opus;②(soft、人工判斷)把 spec 切小,獨立子段各自開 loop(v1 不自動化)。
- **max cap = 6 筆 record**:到頂仍未收斂 → **停、把現況攤給人**、記一句「達 cap 未收斂」。別無限燒。

## 誠實天花板(收斂後務必向人提醒,別讓 CONVERGED 被當「絕對沒問題」)
1. **完整性**:收斂只證「連 2 輪醒著的審計員沒找到 blocker/major」,不證沒有更深的問題。完整性靠多輪 + 多視角,不靠把門檻調嚴。
2. **整合性**:canary-caught / severity / 哪些是「誤判」三個都由植入者(你)自己判、無外部檢查——是**沒閉合的迴歸**,不 tamper-proof。loop 是**可觀測 + 摩擦 + 地板**,不是 oracle。

## 收斂後
`lumos loop status` exit 0 → 向人**回報收斂 + 上述天花板** → 交 **writing-plans** 出實作計畫 → 實作。

> 設計全文見 `docs/design/2026-06-19-design-loop-skill.md`(B)與 `…-convergence-recording.md`(A 原語)、`…-canary-audit.md`(canary 機制)。
