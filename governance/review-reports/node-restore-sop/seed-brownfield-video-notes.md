# 種子材料:brownfield 教學影片逐段筆記(Enzo 2026-08-24 提供,TikTok @one.ai186,15:50)

> 這是節點還原SOP_計劃 的 PRIOR-ART 種子原文。取樣說明(筆記作者自述):全片 949 秒,以 10–12 秒間隔取樣約 90 個畫面,硬字幕無字幕檔,標「沒截到」處為取樣跳過。

## 01/06 改 A 壞 B 的困境(0:00–1:20)
- 用 AI 寫 side project,第 1 週很神,第 4 週只想改一個小地方;打開一看幾千行(示意 6,842 行)全是別人寫的。
- 兩種人遇到同一件事:自己的專案(vibe 出來的)/公司的專案(新人接手)→ 共同點:不熟悉的 codebase。
- 兩條崩壞路徑:Vibe Coder 改 A 壞 B → 認為 AI 不行 → 拋棄產品;工程師試 AI 進自己 codebase → 一樣炸。
- 論點:不是 AI 不夠強,是用法錯。目標=讓 AI 安全的修改有規模的專案。

## 02/06 認識 Brownfield(1:20–2:40)
- Greenfield=空地(AI 最好發揮);Brownfield=已蓋滿、有人住的房子(有寫好的 code、既有 pattern)。
- Greenfield 不會永遠是 Greenfield:vibe coding 一個月後(示意 Day 10)就是 Brownfield。
- 照教學都順、實戰就炸:教學=空地蓋新房;真實專案=在別人住的房子裡拆牆改管。

## 03/06 AI 為什麼會犯錯(2:40–4:36)
- 同一句「幫我加庫存狀態的篩選跟編輯功能」:Greenfield 沒問題,Brownfield 問題大了。
- 比喻:沒進過你家的師傅直接動流理台——你沒先講設計風格。
- 實例:專案已有 React Query pattern 管 API → AI 自己發明新寫法;最糟:改了 useProducts.ts,但這個 hook 訂單頁也在用 → 商品頁好了、訂單頁掛了。
- 每一步都合理,但它不認識這棟房子;手藝比你好不重要——不知道哪面是承重牆。
- 順序:先當「幫你讀專案的資深同事」,再當「照房子規矩施工的師傅」。先看懂,再動手。

## 04/06 看懂它(4:36–8:48)
- 兩條路線:🔍 AI 輔助(你主導,自己翻檔案貼給 AI,AI=放大鏡)/🎙 純指揮 Agent(Claude Code/Cursor 自己探勘)。
- 流程:2 階段 5 步驟(看懂它 1–2;安全的動它 3–5)。
- STEP 1 搞清楚「畫面上這一塊」是誰:
  - AI 輔助(最土炮但 100% 準):右鍵「檢查」→ 拿特徵關鍵字(例 product-inventory-table)⌘⇧F 全專案搜尋 → 找到 ProductTable.tsx → 貼給 AI 問:分析畫面結構、引入哪些子元件、有沒有全站共用的元件?
  - 純指揮:「畫面上商品列表這一塊是哪個檔案在渲染?找出來,分析元件結構」。
  - ⚠ 這階段重點是探索:只分析,不要改。
- STEP 2 搞清楚 Data Flow(更重要;最容易出事的從來不是畫面,是資料):
  - 開 package.json 看用哪些套件管資料(react-query、axios…);找寫入點:dispatch、mutate、setState。
  - 把「頁面檔+hook 檔」一起給 AI:請用白話文解釋這條 data flow(API 從哪來/哪套工具管/編輯時資料怎麼流回 server/中間 function 依序列出)。
  - 必做:網頁版 AI 看不到整個專案 → 編輯器全域搜尋 useProducts,發現 ProductPage/OrdersPage/CartSummary 三處在用 → 檔案一起貼,問「商品頁以外還有誰在用?」(純指揮:agent 直接 Grep 就能答)。
  - 作者最愛:叫 agent 把探勘結果做成一頁 HTML 架構導覽圖(頁面層/共用元件層/hooks·API 層)——哪根水管後面接著別的頁面,一目了然。

## 05/06 安全的動它(8:48–14:24)
- 前兩步=勞力活可外包;後三步=決策活沒有外包版(agent 可起草,拍板的是你)。
- STEP 3 規格+Guardrail(Brownfield 跟 Greenfield 差最多的一步):不能給 AI 空需求。範例 spec 檔用標籤把話講死:
  - task:在既有商品頁新增庫存狀態篩選;讓管理員可編輯庫存
  - read-first:負責商品資料的 hook/共用元件資料夾/型別定義檔
  - requirements:沿用既有 React Query pattern/重用現成 Table·Modal·Select/只准用 Tailwind
  - forbidden:全域 routing·權限控管/被商品頁以外用到的共用 hook
  - forbidden 那段=把前半場看懂的東西寫下來。
  - Clean Code 觀念:❌ 自己覺得漂亮的寫法;✅ Brownfield 的 Clean Code=跟前人一致的寫法。guardrails 第一條:照這個專案原本的樣子寫。
- STEP 4 小步+Review:順序=只出規劃不寫 code(確認方向)→ 只改 useProducts 加篩選參數 → 篩選畫面 → 最後才做編輯彈窗;每個箭頭之間用眼睛看過。
  - Brownfield Review 看的不是 bug,是:偏離既有寫法?命名/資料夾/抓資料位置跟前人不一致?偷改共用檔案?重複造輪子?
  - 可把 git diff 丟給 AI:「用資深前端工程師角度 review」:①偏離既有 React Query 寫法?②動到共用元件?③漏 loading/error 處理?
  - AI review=初審第一道防線;終審永遠是你。⚠ 不要在 production 環境這樣做——除非很熟這套 codebase 或有很好的 harness+context 管理。
- STEP 5 測試驗證「我改的東西有沒有弄壞別人的功能?」:
  - 5-1 先跑專案本來就有的測試(npm test → 12 passed 心裡有底);純指揮交代:「動手前先跑一次既有測試回報結果」「每完成一小塊就再跑」→ 跑測試變 agent 固定動作。沒測試?現在就是叫 AI 補幾條關鍵測試的最好時機。
  - 5-2 看懂別人的 error log:Brownfield 經典坑=包裝過的錯誤紀錄機制(custom error logging),部落知識沒寫在文件;叫 AI 讀 logger.ts 答:錯誤送到哪?一筆 log 長怎樣?(第三點取樣沒截到)。錯誤處理要說專案本來的語言:❌ console.error("update failed");✅ logger.error({errorCode:"INV_042", metadata:{productId,userId}})。
  - 5-3 回歸測試:「我動了商品資料的 hook,列出專案裡所有用到它的地方,逐一確認我的改動有沒有改變它原本的行為。回傳型別、參數、預設值有沒有變?既有測試有覆蓋的話告訴我該跑哪幾個。」=跟「改 A 壞 B」的正式和解。

## 06/06 總結(14:24–15:50)
- 同一個任務,現在會做:分清 Brownfield/選路線/拿到地圖標出危險共用水管/規矩寫成規格+guardrail/一小塊一小塊親自 review/跑測試驗證。同需求同 AI,差別只在你。
- 趨勢:總有一天沒人再手動貼檔案(「AI 輔助」淡出、「純指揮」主流);AI 原生工作者的關鍵能力=被丟進陌生專案時知道讓 agent 幫你探索帶你理解,而不是直接硬幹。Vibe Coder → Agentic Engineer 靠兩件事:context 管理、搭建專案架構的能力。
