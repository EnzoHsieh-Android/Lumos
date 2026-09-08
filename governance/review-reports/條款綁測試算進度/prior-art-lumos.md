# 自家調研:Lumos 現在有沒有「條款清單→認領→完成勾選」(2026-09-08)

> 來源:乾淨 agent(無本專案脈絡,只用 lumos search/context/show/spec-trace/decisions 查主樹圖譜,未讀原始碼),題目逐字:「Lumos 現在有沒有『設計審查產出條款清單 → 實作時認領某一條 → 實作完成後勾掉那一條』這樣的機制?…若沒有,最接近的零件是哪些?另外讀『進度從提交推導_計劃』,逐一列出四版各自的核心做法與被打掉的具體理由。」派工者:handoff-view session。以下為報告原文。

## 一、現在有的零件

**1. `[SN]` 條款標記 + `lumos spec-trace`(條款級輕量 RTM)**
- 做什麼:計劃節點正文規格條款標 `[S1]`、`[S2]`…;「認領」= 回指該計劃(`plan_refs`)的 Verification 節點正文**提及** `[SN]`。指令 `lumos spec-trace <計劃節點> [--json]` 唯讀掃描,列每條 ID 認領狀態。
- 狀態存哪/誰更新:**沒有獨立帳本**,狀態散落在 vault 文字裡——條款標記由寫規格的人手動打,認領由寫 Verification 筆記的人手動提及,**沒有任何機械寫入或驗證這一步**。
- 防不同步機制:**沒有**。opt-in(不標=不追溯)、rc0/rc1 僅供人工判讀、**不掛 pre-push、doctor v1 刻意不加 check**。
- 出處:`Projects/條款認領追溯_計劃.md`;實測 `lumos spec-trace Projects/結清式收斂_計劃` → `✓[S1][S2][S3]` 全認領;`lumos spec-trace Projects/接手視圖_計劃` → 「(opt-in 未啟用)無 [SN] 條款標記」。

**2. `★INVARIANT★` + `[test:]` + doctor Check T(更硬、範圍更窄的軌道)**
- doctor 靜態驗每條 `★INVARIANT★` 綁了真實存在 + 經審計的 `[test:名]`,收工/pre-push 會擋。
- 引原文(`Systems/check-t-sentinel.md`):「Check T 現狀:doctor 靜態驗每條 ★INVARIANT★ 綁了真實存在 + 經審計的 `[test:名]`,但只驗「綁了測試」。測試是 proxy」。
- 邊界(`條款認領追溯_計劃.md` 原文):「計劃節點的規格條款**只有升格成 ★INVARIANT★ 的被 Check T 管**,其餘「要做 A/要處理 B」做沒做靠腦袋記」——spec-trace 為補這個空隙而做,但只把「靠腦袋記」換成「靠人跑指令查」。

**3. `lumos handoff <計劃節點>`(2026-09-07 新產物)**
- 唯讀接手視圖,**不造新狀態**,只讀既有三個可信來源(git 工作樹狀態、逐字稿、計劃點名的檔案)。出處:`Projects/接手視圖_計劃.md`、`Systems/lumos-cli-read.md`。

**現況實測數字**(執行DAG_調研.md 引文):「spec-trace 在本 repo 實測幾乎沒餵資料——三篇實跑:6/6 無人認領、8/8 無人認領、1 篇「opt-in 未啟用」」;`進度從提交推導_計劃.md` 另引「spec-trace 158 篇 126 篇從未使用」。

## 二、「進度從提交推導_計劃」四版設計

| 版 | 核心做法 | 被打掉的理由(原文摘引) |
|---|---|---|
| v1 | 提交掛 git trailer + 讀 CI 判完成 | 「載體靜默丟資料(squash/revert/格式/夾帶;CI 綁 push 頂端)」;r1「兩條地基裁決被打穿(識別碼粒度、判準論證)→ Enzo 裁整份重寫」 |
| v2 | 當場跑計劃宣告的測試,回報「不存在/紅/綠」 | 「載體不為此設計(單檔寫到一半癱瘓/撞名 664 支裡 95 對/skip 靜默變綠/單測 132 秒/蓋推送閘 test-cache)」;r1「共同根=拿 test_lumos.py 當即時查詢後端」 |
| v3 | 改檔工具跑完由 PostToolUse hook 往帳追加 {session,時間,檔案},重播帳算「做到哪」 | 「Edit/Write 只佔本 repo 改檔呼叫個位數%(886 vs 43,481)/檔案路徑對 scripts/lumos 不分辨(150 篇)/活動不攜帶意圖」;無消費入口(spec-trace 158 篇 126 篇從未使用即前例) |
| v4 | agent 明確記意圖(`lumos task record`)+ 工具量事實(git diff)+ 收工 hook 當強制入口 | r1「不收斂;三條腿全倒」——入口:「擋一次是每 session 一次…第二輪起不存在」;「git diff HEAD 看不到 untracked 新檔」「`task record` 拿不到 session_id」「帳版控後合併實測 100% 衝突」;「files↔任務無語意驗證(動 Task 9 的檔嘴上說 Task 7,rc0 放行)」 |

四版共同結論(原文):「每一次「造一個新的狀態源」都在這個 repo 被實測打穿——提交、測試、hook 事件、自報帳;能可靠讀到的只有既有三源:git 工作樹、逐字稿、審查帳。「同步任務狀態」在這裡不能靠造,只能靠**讀**。」

## 三、決策欄裡仍有效的決定

- **d3**:完成判準掛實作端,看功能級測試套綠 + 相依功能無回歸;不做散文級判準。
- **d9**:分界線不是「誰在記」,是「有沒有驗過的證據 + 有沒有人需要它才能前進」;審查帳不爛是因為①寫入驗證②入口綁定。
- **d10、d11**:frontmatter 仍 valid,但描述的是 v4 設計本身,已被 r1 五席判「不收斂」——技術上有效但方向已否決。
- **d12**:Enzo 裁「先造」——改立 `Projects/接手視圖_計劃`,只讀既有三源、不造新狀態。
- d1、d2、d4、d5、d6、d7、d8 已 superseded。

## 四、沒查到的

- doctor Check T 的完整程式邏輯/確切位置(只讀圖譜摘要,未 show 全文)。
- spec-trace「6/6、8/8 無人認領」的三篇具體是哪三個節點、量測時間。
- `lumos task record` / `docs/.task-log.jsonl` 是否已寫進 `scripts/lumos`——圖譜顯示停在設計階段、未落地;未讀原始碼確認。
