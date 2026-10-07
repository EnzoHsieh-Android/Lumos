# Lumos 10/1–10/7 更新與 README 核對

盤點時間：2026-10-07T12:30:08+08:00（Asia/Taipei）。
固定 main 來源：`9385ff960b8f52627a539613ecc11616b1bb4c22`。以 **committer 時間** 篩選 10/1 00:00 至盤點時間、且可從此 main 追溯的提交；合併提交、審查帳本和驗證文件都保留，避免把提交數當成功能數。原工作目錄未提交的探針改動、未合併分支不列為 main 更新。日期是提交時間，不代表部署或發版時間。

共 261 個提交；分類：Update README.md 1, chore 88, docs 42, feat 41, fix 30, merge 47, perf 1, test 11。完整清單見文末。

## 依使用者影響分組

| 更新方向 | 代表提交 | 核對入口 | README 處置 |
| --- | --- | --- | --- |
| 審查修補與回歸：修正紀錄、修補鏡頭、同案例修前紅修後綠、既有路徑保留、分段驗證、抓錯能力抽查與因果未知 | e8d839fd、681d1047、5c3732cd、5a9bcdca、d0ba4c03、97415c5f、21325767 | skills/lumos-code-loop/SKILL.md；skills/lumos-design-loop/templates.md §3.1 | 新增修復副作用說明，區分守則與只提醒的 fix-check |
| 滿輪人裁、回顧與歸族，繼續前記帳；修補證據接入回顧 | 023d694e、1274f643 | CLI loop cap-decision / retro / retro-stats | 修正「只提示」的過時描述，不宣稱自動人裁 |
| 收斂評測：完整觀察分母、固定案例成對比較，修好／保留／新增缺陷分開算 | 3e961dce | governance/eval/review_convergence.md | 增加入口；明說本機唯讀分析、尚非自動模型評測或成效證明 |
| 審查材料與證據拒收：計數、座標、快照、派工輸入、附件影響範圍、修正紀錄前置核對 | ffc6b428、99a230ef、cf53b1ad、f1142836、9f2419c6、532b32db、4fc74753 | scripts/lumos；對應提交與測試 | 補一段證據有效性，不逐一堆修復清單 |
| 分支／合併：首次推送範圍與主線認領分支審查留痕；額外測試家需固定、可驗證的來源 | dc8b8247、caa76fe0、bd9b826c、bbc07fa8、8d673a4f、75ae9279 | scripts/hooks/pre-push；scripts/lumos | 審查段增加分支留痕說明；內部測試家修復留在本盤點 |
| 筆記摘要格子、SEE、外部來源與驗證功能明列 | 50a8e7dd、2ce0da2d、d5d4aeba、9ab57541、83cb4f5a、b384cd5f | skills/lumos-project-notes/reference.md；scripts/lumos | 補維護入口，既有程式碼不抄入圖譜原則保留 |
| 漂移／結案：不存在條件、已結案、寫下時已成立、撤除條件、照留期限、數量、連帶收尾、摘要正文分歧、更新日期 | 6f498451、be365f37、6cf03cb6、0ab9bfb2、5b8afcc6、f1ef5f11、f96fd380、b0e7c1d5、22992b66、d3867054 | CLI drift scan / doctor / summary-line / updated-sync | 10/5 已涵蓋的保留；補 10/6–10/7 的期限與維護指令 |
| 殺傷力配方：短身分、移除、單條試跑、快取隔離、舊配方失效、綁定清單提醒 | 9e375f23、d517d88a、a5877e38、1312d73f、4964e00a、42e190f4 | CLI guard kill；code-loop 技術棧檢核 | 審查段概述抓錯能力，細項留指令／盤點 |
| Claude 外掛：事件帳與讀取端、搜尋／指令長度／席位欄位、壓縮交棒、具標記審查席白名單 | 0f2e8f13、1a8c6b0d、4ed36ff6、61a92f60、5b94ca17、5ff415f5 | mods/claude/；CLI events；安裝器 | 新增 Claude 專屬能力與限制，不暗示 Codex 同樣可用或 shell 隔離 |
| 工作樹推播、快取鎖與背景啟動：避免誤刪別人鎖、停止過期自動接手、失敗即時回報 | 5a67e231、96bf7296、30f73584、720e66c2、18160d10、82992ceb、79805770 | scripts/hooks/claude/；scripts/lumos | 不逐項寫入入門 README；作為可靠性維護列帳 |
| 安裝／更新／雲端／CI：dry-run、本機例行帳、雲端測試工具、8 路 CI 與慢機測試修正 | 71d99591、13738b80、34187bc6、be2a1b5d、f313f210、7bd01936 | get.sh；scripts/lumos；.github/workflows/ci.yml | dry-run 已有；補 main/release 邊界，CI 細節留盤點 |
| 文件、研究與驗證：README 重寫、手冊入口、後端角度／Claude 片段調研、會談編號實測、設計／審查／CI 證據 | 見完整清單 | README；docs/；governance/research/ | 不把研究提案、歷史量測當已實作或普遍成效 |

## 發布與核對邊界

GitHub clone 的 release 指向 `4a42dede02fea8c8468e8c29b23a06ed660f6b1d`（9/7）；get.sh 預設 LUMOS_BRANCH=release。README 介紹 main 的能力，不能由本盤點推論 release 安裝已含全部更新。本文不更新 release、安裝環境或 Windows 支援。既有 clone 設 LUMOS_BRANCH 不會自行換分支。

本盤點確認程式與文件入口；不重跑歷史每一項功能的完整驗證，也不量測真實模型的收斂改善。每筆原驗證、審查與來源可沿下方提交追溯。

## 完整提交清單

| 台北提交時間 | 提交 | 類別 | 更新 |
| --- | --- | --- | --- |
| 10/01 00:17 | [f8ca86c2](https://github.com/EnzoHsieh-Android/Lumos/commit/f8ca86c29ac55d88e3ca8795ebfba1eb95a18693) | docs | docs: README 通篇精簡，句子變短、去掉重複的字，事實不變 |
| 10/01 00:20 | [67d3a2ef](https://github.com/EnzoHsieh-Android/Lumos/commit/67d3a2ef78c6b5ff0374c822c4f6151e0333e30a) | docs | docs: README 拿掉漂移檢查的成效數字與「更多：審查數據與跳過紀錄」 |
| 10/01 00:36 | [7260ffd6](https://github.com/EnzoHsieh-Android/Lumos/commit/7260ffd6be21dc17d2939df6a20b99b554f20a5b) | docs | docs: README 新增 evals 一章，說明這套工具怎麼每週自我檢查、持續改進 |
| 10/01 05:46 | [dcc0c900](https://github.com/EnzoHsieh-Android/Lumos/commit/dcc0c900979f913fb7d388b05800d0aec6d5e543) | feat | feat: 推送前提醒把「管這次改到的程式、這次也改過」的筆記交給判定者整篇重讀(只提醒) |
| 10/01 05:46 | [ec7b1619](https://github.com/EnzoHsieh-Android/Lumos/commit/ec7b1619ba1fe365c12c0e713979a7231ccae9bf) | chore | chore(lumos): 記錄代碼審通過 |
| 10/01 06:40 | [76be0d11](https://github.com/EnzoHsieh-Android/Lumos/commit/76be0d113239c23768266a4f399a91eb943d3e91) | docs | docs: 回頭重讀提醒補上線日,兩週與八週回頭日期改成 10-15、11-26 |
| 10/01 10:41 | [2cd2ba73](https://github.com/EnzoHsieh-Android/Lumos/commit/2cd2ba730128c5b8f6c49a9f04011322c21c14fe) | chore | chore(lumos): 記錄代碼審通過 |
| 10/01 10:41 | [42e190f4](https://github.com/EnzoHsieh-Android/Lumos/commit/42e190f4a02cea2fcd8e5d5b1212ae5851e0b615) | feat | feat: 併發與 N+1 類檢核題回答「已處理」時,提醒有沒有破壞測試背書 |
| 10/01 10:41 | [82aef028](https://github.com/EnzoHsieh-Android/Lumos/commit/82aef0288adf14b00bc4b9035dd9976dbfceb76e) | docs | docs: README 的防筆記過期一節補上推送前重讀守檔筆記的提醒 |
| 10/01 10:41 | [b0c34224](https://github.com/EnzoHsieh-Android/Lumos/commit/b0c3422472133c921502971aa78cb3b0e6c5cf0f) | chore | chore(lumos): 記錄代碼審通過 |
| 10/01 11:23 | [51f83721](https://github.com/EnzoHsieh-Android/Lumos/commit/51f837210b2a289db76d66371524ef8efcf33cff) | docs | docs: 更新工具要連紀律區塊一起推、消費專案 CI 直接呼叫回頭重讀不必吞錯 |
| 10/01 14:19 | [780a32a8](https://github.com/EnzoHsieh-Android/Lumos/commit/780a32a883f087efc5a61d178326a3381834ce3a) | docs | docs: README 開頭先講怎麼運作,提交被擋的實例移到防筆記過期一節之後 |
| 10/01 15:53 | [e077d690](https://github.com/EnzoHsieh-Android/Lumos/commit/e077d690abf397d4528e869b7cc54eb3e04bfb78) | Update README.md | Update README.md |
| 10/01 18:04 | [d517d88a](https://github.com/EnzoHsieh-Android/Lumos/commit/d517d88a1cc8c0d08ef2269a6ef407c2bcda9d8b) | feat | feat: 健康檢查列出原文已對不上程式的殺傷力配方,新增移除配方的指令(只提醒) |
| 10/01 18:05 | [96d51b62](https://github.com/EnzoHsieh-Android/Lumos/commit/96d51b6243b3fed07b56e9008a1a27bb6c97affe) | chore | chore(lumos): 記錄代碼審通過 |
| 10/01 19:00 | [5f8c84ff](https://github.com/EnzoHsieh-Android/Lumos/commit/5f8c84ffa04f6f45fec7d56baeb53cd9bfef460d) | docs | docs: 漂移防治路線圖第一項標成已上線,標籤一案記下交給另一個會談 |
| 10/01 20:39 | [30a3c8fe](https://github.com/EnzoHsieh-Android/Lumos/commit/30a3c8feec447a0bf4fe86d75c32142c4fa4d23b) | docs | docs: 筆記標籤與格子寫法兩份計劃,附調研、分類實驗與三輪設計審卷證 |
| 10/01 21:39 | [9e375f23](https://github.com/EnzoHsieh-Android/Lumos/commit/9e375f23c816d1ac7ce26fd9c0fb384d40fafbd1) | feat | feat: 殺傷力配方修補更順:範本不再抄舊壞法、每條配方都查得到短身分 |
| 10/01 21:39 | [d7314ecd](https://github.com/EnzoHsieh-Android/Lumos/commit/d7314ecdc65a4b296def8d28295f37d7ffecbdb7) | chore | chore(lumos): 記錄代碼審通過 |
| 10/01 22:05 | [996b5fad](https://github.com/EnzoHsieh-Android/Lumos/commit/996b5fad4fa44f8865fb992dfc438db23e052abf) | chore | chore: 記下殺傷力驗證那篇系統筆記的回頭重讀結果 |
| 10/01 22:39 | [d8b02331](https://github.com/EnzoHsieh-Android/Lumos/commit/d8b0233140ad8977b20e138b3d6cdbdebe3637a0) | docs | docs: 路線圖排定下一步順序,收進代碼審修正關卡提案 |
| 10/01 23:21 | [1b6310ae](https://github.com/EnzoHsieh-Android/Lumos/commit/1b6310ae1bb14c2ea2a433090d5ccc9d639be222) | docs | docs: 筆記格子寫法計劃定稿,附三輪設計審卷證,分類計劃與依賴欄位計劃同步 |
| 10/01 23:21 | [d5d4aeba](https://github.com/EnzoHsieh-Android/Lumos/commit/d5d4aebaa6ceb8923a324be5a61356bf0cd16ce5) | feat | feat: 摘要多認一個 SEE 前綴,只放連結的行改用它,計劃連到誰也算進去 |
| 10/02 00:46 | [50a8e7dd](https://github.com/EnzoHsieh-Android/Lumos/commit/50a8e7dd9cf9253f80b497bcda07e367f51d7607) | feat | feat: 筆記摘要改成格子寫法,lint 與提交時提醒照新表、舊寫法照舊 |
| 10/02 00:46 | [34c53ac9](https://github.com/EnzoHsieh-Android/Lumos/commit/34c53ac99c75f9288d045db92dc991f226d6b2fd) | chore | chore(lumos): 記錄代碼審通過 |
| 10/02 01:21 | [a5877e38](https://github.com/EnzoHsieh-Android/Lumos/commit/a5877e38f7c56157f23f4961b446296378b73484) | fix | fix: 殺傷力驗證不再沿用上一條壞法留下的編譯快取而判錯 |
| 10/02 01:30 | [e6003dfe](https://github.com/EnzoHsieh-Android/Lumos/commit/e6003dfe0f1b328ef3cfd194077316c23793b290) | chore | chore(lumos): 記錄代碼審通過 |
| 10/02 01:59 | [24f08d48](https://github.com/EnzoHsieh-Android/Lumos/commit/24f08d4858812ccc45f3cacba94ce133448fa866) | docs | docs: 路線圖標記殺傷力驗證編譯快取誤判已上線,下一個是代碼審修正關卡 |
| 10/02 04:35 | [2ce0da2d](https://github.com/EnzoHsieh-Android/Lumos/commit/2ce0da2d7a198dd623f8b0503ea6a5baf84b2780) | feat | feat: 筆記格子缺漏可以在提交時擋,掛鉤帶 --slots 才開 |
| 10/02 04:35 | [cbbdd46a](https://github.com/EnzoHsieh-Android/Lumos/commit/cbbdd46a8a344fea1112b1fe5a274700e81556b5) | chore | chore(lumos): 記錄代碼審通過 |
| 10/02 14:13 | [e8d839fd](https://github.com/EnzoHsieh-Android/Lumos/commit/e8d839fd27ce3f8f8c21829d04ae8bdd5afd68a7) | feat | feat: 代碼審派下一輪前先驗修正紀錄,只提醒不擋 |
| 10/02 14:17 | [accd0ffe](https://github.com/EnzoHsieh-Android/Lumos/commit/accd0ffebb43f4778228a958b1b93120029d2dc3) | chore | chore(lumos): 記錄代碼審通過 |
| 10/02 15:12 | [7d01800c](https://github.com/EnzoHsieh-Android/Lumos/commit/7d01800cab24104a41c508957b8e2a0376a319eb) | docs | docs: 路線圖標記代碼審修正關卡第 0 步已上線,下一個是 1a-3 |
| 10/02 16:24 | [0ab9bfb2](https://github.com/EnzoHsieh-Android/Lumos/commit/0ab9bfb2069f6cef2ff163ab5a62f6b649d6f656) | feat | feat: 推送時 RULE 的撤除條件成立就擋,判不了只列出 |
| 10/02 16:24 | [d1acf891](https://github.com/EnzoHsieh-Android/Lumos/commit/d1acf89198ae3ce87fecc2e4abd158b46f174da2) | test | test: 起點讀取時限那支測試不再隨機器快慢紅 |
| 10/02 16:24 | [dbb5883a](https://github.com/EnzoHsieh-Android/Lumos/commit/dbb5883ad496e0f374b631f77837a2630b00eb5c) | chore | chore(lumos): 記錄代碼審通過 |
| 10/02 17:22 | [cdb56813](https://github.com/EnzoHsieh-Android/Lumos/commit/cdb56813db80c4469aae9887e5d4c03fa2674759) | docs | docs: 記下後端審查角度的兩輪小實驗,結論是不加題目、不另寫 skill |
| 10/02 17:59 | [5a67e231](https://github.com/EnzoHsieh-Android/Lumos/commit/5a67e231e8545e17d7bd5d5a4645e2bcde8f6f21) | fix | fix: 在 worktree 裡改檔也推得到相關筆記 |
| 10/02 18:05 | [e0457ff5](https://github.com/EnzoHsieh-Android/Lumos/commit/e0457ff53a5b0d423aed1b7d44a46894e6821e97) | chore | chore(lumos): 記錄效能檢核表態 |
| 10/02 20:16 | [7a8a4813](https://github.com/EnzoHsieh-Android/Lumos/commit/7a8a4813be75f3464438d893e2ba0047474579df) | docs | docs: 殺傷力驗證編譯快取誤判計劃記下 rtb 提前回報的實測結果 |
| 10/02 20:27 | [1312d73f](https://github.com/EnzoHsieh-Android/Lumos/commit/1312d73f31072ffbacf0f2c14dd3cf2195bf848d) | feat | feat: 殺傷力配方能只跑一條、寫完當場試跑,健康檢查列出最近殺不掉的配方 |
| 10/02 20:27 | [86c579ba](https://github.com/EnzoHsieh-Android/Lumos/commit/86c579bae18dbbc9c3809767f28985e075afa025) | chore | chore(lumos): 記錄代碼審通過 |
| 10/02 20:53 | [3a9ccd13](https://github.com/EnzoHsieh-Android/Lumos/commit/3a9ccd1328a9b0944049853354cca9f326f94df4) | feat | feat: 健檢與漂移健檢提醒筆記格子過期,推送時撤除條件的邊角補齊 |
| 10/02 21:10 | [2e776ec7](https://github.com/EnzoHsieh-Android/Lumos/commit/2e776ec736b6283271a9073430cf6f8198778519) | chore | chore(lumos): 記錄代碼審通過 |
| 10/02 21:42 | [64f9c0f0](https://github.com/EnzoHsieh-Android/Lumos/commit/64f9c0f0bd986525284874aa0e34cf303b8d9d62) | docs | docs: 三篇系統筆記照新程式改正過期的說法,撤除條件遺留四項結案 |
| 10/03 02:49 | [65d1024d](https://github.com/EnzoHsieh-Android/Lumos/commit/65d1024dbcee926f854cca705a93f821c24b5a90) | feat | feat: 推送時碰到的筆記,測試綁定要指得到真測試 |
| 10/03 02:49 | [f1b64a49](https://github.com/EnzoHsieh-Android/Lumos/commit/f1b64a49df5afdc1d04357f20ca738be462ed57c) | chore | chore(lumos): 記錄代碼審通過 |
| 10/03 11:41 | [71deb7c5](https://github.com/EnzoHsieh-Android/Lumos/commit/71deb7c589de893b5f7f48d716827bd86396e183) | docs | docs: 記下「把外部回應碼的官方意思推給審查員」小實驗,有效、進接線設計 |
| 10/03 12:23 | [b384cd5f](https://github.com/EnzoHsieh-Android/Lumos/commit/b384cd5f16223858361ae8f1b5f9031067315e31) | fix | fix: 筆記檢查讀新行時,內容以 ++ 開頭的行和本機 diff 設定不再讓後面的新行漏查或行號錯位 |
| 10/03 12:29 | [83cb4f5a](https://github.com/EnzoHsieh-Android/Lumos/commit/83cb4f5afd24b40b12cab202dc0e61840932c3a9) | feat | feat: 舊筆記句尾補一段括號更正時,筆記檢查只看補上的那段 |
| 10/03 12:29 | [60a39f02](https://github.com/EnzoHsieh-Android/Lumos/commit/60a39f02ae0e2c620caf6ceadee8b0602f5ee26e) | chore | chore(lumos): 記錄代碼審通過 |
| 10/03 14:58 | [98a40ada](https://github.com/EnzoHsieh-Android/Lumos/commit/98a40adaf4277aee4fe0f6b0347a7c3d842fd92a) | feat | feat: 審查員現在看得到外部回應碼的官方意思,改到外部碼判斷時作者要指出碼表在哪 |
| 10/03 16:03 | [6f70efb6](https://github.com/EnzoHsieh-Android/Lumos/commit/6f70efb6985344d4d307341e68e7337f55ca77d3) | docs | docs: 外部回應碼接線計劃收案,三項已上線、CI 綠 |
| 10/03 16:28 | [be365f37](https://github.com/EnzoHsieh-Android/Lumos/commit/be365f37e3037c5c7648d201895da6f4e706a381) | feat | feat: 回頭條件寫在句中提交時擋下,加上結案標記讓不用再回頭的條件不再提醒 |
| 10/03 16:53 | [f369e9c7](https://github.com/EnzoHsieh-Android/Lumos/commit/f369e9c7fccb95089c13fe11dd80283c94fb1505) | chore | chore(lumos): 記錄代碼審通過 |
| 10/03 18:04 | [f74eddd0](https://github.com/EnzoHsieh-Android/Lumos/commit/f74eddd0c3eed81625cda0c2784fc6097d53e5a5) | fix | fix: 健康檢查不再把「裁定改寫」的條款當成撤除候選 |
| 10/03 18:04 | [dd3cf713](https://github.com/EnzoHsieh-Android/Lumos/commit/dd3cf71388f206c5e45df9fa477721d3d227bbcc) | chore | chore(lumos): 記錄代碼審通過 |
| 10/03 20:04 | [6f498451](https://github.com/EnzoHsieh-Android/Lumos/commit/6f498451e875aeb19529b775eb70d3db47f28ebb) | feat | feat: 回頭條件可以寫「等某支檔或某段程式不再出現」 |
| 10/03 20:04 | [e594a964](https://github.com/EnzoHsieh-Android/Lumos/commit/e594a9642c9b67e2ce9749abc67e6a2e4ec792d8) | chore | chore(lumos): 記錄代碼審通過 |
| 10/03 22:51 | [9ab57541](https://github.com/EnzoHsieh-Android/Lumos/commit/9ab57541291a36a0887a79f08742b18cc0334e46) | feat | feat: 驗收紀錄可以寫明驗了哪些功能,正文的指路連結不再被當成驗過 |
| 10/03 22:52 | [a89d384a](https://github.com/EnzoHsieh-Android/Lumos/commit/a89d384af4a211a7b6df850830c90d6a364a9bda) | chore | chore(lumos): 記錄代碼審通過 |
| 10/03 23:23 | [2c0f56c7](https://github.com/EnzoHsieh-Android/Lumos/commit/2c0f56c7ef0e11cb2acc7521341e9a7ae470760d) | docs | docs: 新增 10-03 交接筆記,列出已上線的、排隊中的事與 rtb 第三輪機制化提案 |
| 10/03 23:34 | [6cf03cb6](https://github.com/EnzoHsieh-Android/Lumos/commit/6cf03cb6ca39b09784bf15509cbb57dec2310d10) | feat | feat: drift scan 標出寫下時就已成立的回頭條件 |
| 10/04 00:04 | [611d1dba](https://github.com/EnzoHsieh-Android/Lumos/commit/611d1dba15eba9d50630fd511c59f9cc998151e6) | docs | docs: 寫下時就已成立的接手步驟補上確切的審查範圍與推送前常漏的檢查 |
| 10/04 00:19 | [224091dc](https://github.com/EnzoHsieh-Android/Lumos/commit/224091dca2e12d8c3d85d30ff1ae9332bd98ee73) | docs | docs: 交接筆記補上 rtb 已改回指路連結、另一個會談的代碼審接手入口,並記下「更新前先預覽規範檔變更」的建議 |
| 10/04 00:19 | [abcd1aa1](https://github.com/EnzoHsieh-Android/Lumos/commit/abcd1aa1f5ac4e2fc47ca46f0f334a159abd8017) | chore | chore: 補上主工作目錄累積沒提交的治理帳與記錄 |
| 10/04 00:52 | [f93cb440](https://github.com/EnzoHsieh-Android/Lumos/commit/f93cb440fe5ba244d7ed2fe214769a87c6f7f2f2) | fix | fix: 本機開了簽章顯示時,寫下時就成立不再追錯提交 |
| 10/04 02:22 | [f7f0f32b](https://github.com/EnzoHsieh-Android/Lumos/commit/f7f0f32b804642f6f9923c22e04e0314554f3aad) | chore | chore(lumos): 記錄代碼審通過 |
| 10/04 03:24 | [7bd01936](https://github.com/EnzoHsieh-Android/Lumos/commit/7bd01936de926c8d531652e0707bc437060c7d34) | fix | fix(ci): PR 的 CI 補上本機 main,找主線的測試不再整支紅 |
| 10/04 12:33 | [5b8afcc6](https://github.com/EnzoHsieh-Android/Lumos/commit/5b8afcc694617e5b73163678e6552374e4433f0f) | feat | feat: drift scan 檢查筆記裡的數量標記,對不上的一條指令改成現值 |
| 10/04 12:37 | [2fd46df1](https://github.com/EnzoHsieh-Android/Lumos/commit/2fd46df1e56a4a1e1358dc91b3cfc479ff69506c) | chore | chore(lumos): 記錄代碼審通過 |
| 10/04 12:47 | [e6e5069b](https://github.com/EnzoHsieh-Android/Lumos/commit/e6e5069bd50864cb2739e8fca197e93f74c99b8a) | merge | 合併 PR #1:寫下時就成立追錯提交的修正、PR 的 CI 補本機 main |
| 10/04 13:00 | [705c8fc3](https://github.com/EnzoHsieh-Android/Lumos/commit/705c8fc3ef511fd2bcc47d0cd319cfe3ac0e969f) | docs | docs: 手冊補上寫下時就已成立的標記怎麼看、表態前要先看它 |
| 10/04 13:06 | [c4de775f](https://github.com/EnzoHsieh-Android/Lumos/commit/c4de775f061dcb8043c66e22ece4558bc441ef7a) | docs | docs: 手冊入口補上回頭重讀、舊名稱檢查、漂移掃描時機與測試綁定規則 |
| 10/04 13:30 | [0dde4562](https://github.com/EnzoHsieh-Android/Lumos/commit/0dde4562a598628a0e7f60aded62fa42ae701e58) | docs | docs: 手冊教寫數量標記,讓檢查器有東西可查 |
| 10/04 14:09 | [4c577478](https://github.com/EnzoHsieh-Android/Lumos/commit/4c577478db6ad8540b753f1dbc2a9c4c90c18eda) | merge | 合併 PR #2:drift scan 檢查筆記裡的數量標記,手冊教寫法 |
| 10/04 14:12 | [f2eddbc7](https://github.com/EnzoHsieh-Android/Lumos/commit/f2eddbc771d06158910b2b1eb6f8a368ab2522e4) | merge | Merge remote-tracking branch 'origin/main' into claude/affectionate-curie-p97xs3 |
| 10/04 15:17 | [acac006e](https://github.com/EnzoHsieh-Android/Lumos/commit/acac006ef02df5efbc32000a4eee291f09f8e4ec) | test | test: 鏡頭暖快取測試改挑最小的單一提交,主線合併大 PR 後不再假紅 |
| 10/04 15:58 | [26669696](https://github.com/EnzoHsieh-Android/Lumos/commit/266696967c8a881d4a73359d748d74989aaa70cf) | merge | 合併 PR #3:手冊入口補齊、修主線合併大 PR 後鏡頭測試假紅 |
| 10/04 16:05 | [7029a656](https://github.com/EnzoHsieh-Android/Lumos/commit/7029a6563454169a5e20d657273cc3840b0d41ab) | test | test: 帳寫不進去的兩支測試改用換成資料夾造現場,root 身分下不再假紅 |
| 10/04 16:05 | [34187bc6](https://github.com/EnzoHsieh-Android/Lumos/commit/34187bc6bef8fb935506a2b03c003d4c51db6e35) | chore | chore: 雲端工作階段開場補齊測試工具,推送前的全套測試在雲端也能跑綠 |
| 10/04 17:11 | [91f4b29e](https://github.com/EnzoHsieh-Android/Lumos/commit/91f4b29e422c83f84be33504df342adcee5aeead) | merge | 合併 PR #4:雲端工作階段開場補齊測試工具,推送前的全套測試在雲端也能跑綠 |
| 10/04 21:41 | [13738b80](https://github.com/EnzoHsieh-Android/Lumos/commit/13738b806603e7da203279365a4ffa3c95fea280) | feat | feat: 例行檢查紀錄改寫本機帳,提交推送不再弄髒工作目錄 |
| 10/04 21:51 | [a354162c](https://github.com/EnzoHsieh-Android/Lumos/commit/a354162c78af2b085506d466192b2b893d65172b) | chore | chore(lumos): 記錄代碼審通過 |
| 10/04 21:55 | [17854bb0](https://github.com/EnzoHsieh-Android/Lumos/commit/17854bb0f45108587138a4ae5fe92c7faf364edd) | chore | chore(lumos): 記錄代碼審通過 |
| 10/04 22:59 | [128ffeb1](https://github.com/EnzoHsieh-Android/Lumos/commit/128ffeb1dd5b7777cb4aae5b5078b47739e379ab) | merge | 合併 PR #5:例行檢查紀錄改寫本機帳,提交推送不再弄髒工作目錄 |
| 10/04 23:38 | [619b4d1c](https://github.com/EnzoHsieh-Android/Lumos/commit/619b4d1cd8d4cac3f88aa9ebd1f5ca6cfe3f9461) | docs | docs: 記錄治理帳設計遭鎖競態擋下 |
| 10/05 00:35 | [779500b9](https://github.com/EnzoHsieh-Android/Lumos/commit/779500b9df9044b5ff3fdb357d2b9f21d5b9be2c) | fix | fix: loop next 帶 --spec 時新的審查編號改問處置閘,不再被已退役的關卡擋下 |
| 10/05 00:36 | [41fce9ff](https://github.com/EnzoHsieh-Android/Lumos/commit/41fce9ff1a0c4e8dced1314891da7fb0e5e391ad) | chore | chore(lumos): 記錄代碼審通過 |
| 10/05 00:46 | [96bf7296](https://github.com/EnzoHsieh-Android/Lumos/commit/96bf72965bc0f38cf95681d1682bb277c2a74d4d) | fix | fix: 停止過期鎖自動接手並釐清派工鎖狀態 |
| 10/05 01:04 | [30f73584](https://github.com/EnzoHsieh-Android/Lumos/commit/30f735846ed50d723f998224b1bd440a20fbe3b6) | fix | fix: 修正鎖錯誤留帳與非持有者刪鎖 |
| 10/05 01:12 | [720e66c2](https://github.com/EnzoHsieh-Android/Lumos/commit/720e66c2f4f1d57b3617725436adc496a5e10c99) | fix | fix: 快取命中不再刪除新持有者的鎖 |
| 10/05 01:26 | [930915bb](https://github.com/EnzoHsieh-Android/Lumos/commit/930915bbc1c4efabc317c393484b681d95e06d0c) | docs | docs: 記錄過期鎖代碼審未收斂與待修缺陷 |
| 10/05 01:54 | [9d0fd7f5](https://github.com/EnzoHsieh-Android/Lumos/commit/9d0fd7f5031111e42e0d7d446496000279dfd5d3) | merge | 合併 PR #6:loop next 帶 --spec 時新的審查編號改問處置閘,不再被已退役的關卡擋下 |
| 10/05 02:25 | [18160d10](https://github.com/EnzoHsieh-Android/Lumos/commit/18160d109b20ed85fb847be5d4b465ec67830dcb) | fix | fix: 背景快取早退也釋放本次暖機鎖 |
| 10/05 02:26 | [e5695c11](https://github.com/EnzoHsieh-Android/Lumos/commit/e5695c11f0beb8ed87ef700a33f72cd459ecb729) | chore | chore(lumos): 記錄代碼審通過 |
| 10/05 03:19 | [71d99591](https://github.com/EnzoHsieh-Android/Lumos/commit/71d99591f228d0eceb47cb52caee9dfc7345fa52) | feat | feat: lumos update 加 --dry-run,先預覽會改哪些規範檔與工具檔 |
| 10/05 03:19 | [89e87768](https://github.com/EnzoHsieh-Android/Lumos/commit/89e8776826c4837a7f12255bf0c9febcabd30508) | chore | chore(lumos): 記錄代碼審通過 |
| 10/05 05:07 | [4686668f](https://github.com/EnzoHsieh-Android/Lumos/commit/4686668fbba40eaa69d769178673feda3ef4e722) | merge | 合併 PR #7:lumos update 加 --dry-run,先預覽會改哪些規範檔與工具檔 |
| 10/05 11:01 | [f1ef5f11](https://github.com/EnzoHsieh-Android/Lumos/commit/f1ef5f1104bcf2339f3d48c9ba5ba57549920f0a) | feat | feat: 結案後揪出別處還寫待定的句子,結 Issue 時先處理待定決策與回頭條件 |
| 10/05 11:01 | [3d21e1e1](https://github.com/EnzoHsieh-Android/Lumos/commit/3d21e1e1a65e0722f9cd4a383e4248951d3da23b) | chore | chore(lumos): 記錄代碼審通過 |
| 10/05 12:00 | [82992ceb](https://github.com/EnzoHsieh-Android/Lumos/commit/82992ceb8bfe33148d804af8a35441fe3880c4cd) | fix | fix: 背景啟動失敗時即時回報並保護替代鎖 |
| 10/05 12:05 | [c2f3abee](https://github.com/EnzoHsieh-Android/Lumos/commit/c2f3abee8d6bc5de97b8f84a32c0fa32019d87fa) | chore | chore(lumos): 記錄代碼審跳過 |
| 10/05 12:10 | [c819decb](https://github.com/EnzoHsieh-Android/Lumos/commit/c819decb682dc2d49617b87ba1648faa79d077cf) | docs | docs: 記錄分支推送後尚無 CI 結論 |
| 10/05 12:15 | [6d3764c4](https://github.com/EnzoHsieh-Android/Lumos/commit/6d3764c470c578d13925f209c2199b03482f2efd) | chore | chore(lumos): 記錄代碼審跳過 |
| 10/05 12:19 | [3f62d02d](https://github.com/EnzoHsieh-Android/Lumos/commit/3f62d02d6424028b615f57f2108998a715f8eace) | chore | chore(lumos): 記錄合約測試結果 |
| 10/05 14:03 | [f313f210](https://github.com/EnzoHsieh-Android/Lumos/commit/f313f2105c6f7e03b1e003c6813eaef945ddee3c) | fix | fix: CI 機器較慢時推送閘子集測試不再超時誤判 |
| 10/05 14:03 | [33e3bf16](https://github.com/EnzoHsieh-Android/Lumos/commit/33e3bf16e89aa537989f4c0592869987d3a1e7a3) | chore | chore(lumos): 記錄代碼審跳過 |
| 10/05 14:37 | [6c7fbe6e](https://github.com/EnzoHsieh-Android/Lumos/commit/6c7fbe6e2ac95e0df8a16ad231fc07c67ab6308e) | merge | chore: 合併背景啟動失敗回報與鎖保護 |
| 10/05 14:39 | [fd942f54](https://github.com/EnzoHsieh-Android/Lumos/commit/fd942f5428f5f09413c6f0192740bdbe40f91ec0) | chore | chore(lumos): 記錄代碼審跳過 |
| 10/05 14:43 | [eeaa6162](https://github.com/EnzoHsieh-Android/Lumos/commit/eeaa6162c8e138183732553eb687eb4bac2f4136) | docs | docs: 記錄主線合併與 CI 待查結果 |
| 10/05 14:44 | [e1fd20ef](https://github.com/EnzoHsieh-Android/Lumos/commit/e1fd20ef484fefae7d5f0e2207ba4e07c4552ef7) | chore | chore(lumos): 記錄代碼審跳過 |
| 10/05 14:52 | [0b485e5f](https://github.com/EnzoHsieh-Android/Lumos/commit/0b485e5f87e0383d6b4a3d9969c87360e3365f20) | merge | chore: 合併主線(背景啟動失敗回報與鎖保護) |
| 10/05 14:58 | [4d20499b](https://github.com/EnzoHsieh-Android/Lumos/commit/4d20499b19b902748c9c22fbeb68280be773b010) | chore | chore(lumos): 記錄代碼審通過 |
| 10/05 16:37 | [79805770](https://github.com/EnzoHsieh-Android/Lumos/commit/7980577056fadcb98ee66c4acbb89d1965c7ef7e) | fix | fix: Linux 上啟動失敗的清理不再刪掉別人剛換入的鎖 |
| 10/05 16:37 | [333d16ee](https://github.com/EnzoHsieh-Android/Lumos/commit/333d16eefd063d8fd9e365fdab0380a5400b42fa) | chore | chore(lumos): 記錄代碼審通過 |
| 10/05 18:02 | [2aafdcb2](https://github.com/EnzoHsieh-Android/Lumos/commit/2aafdcb2740be8a4cab7093aefb161b6bae8ca44) | merge | 合併 PR #8:結案後揪出別處還寫待定的句子,結 Issue 時先處理待定決策與回頭條件 |
| 10/05 18:09 | [47f906e4](https://github.com/EnzoHsieh-Android/Lumos/commit/47f906e4d5323b092ff0a15f11c0569e6682c410) | docs | docs: README 補上結案連帶收尾、數量標記與推送前新增的檢查 |
| 10/05 20:00 | [b6490dd0](https://github.com/EnzoHsieh-Android/Lumos/commit/b6490dd0976aa25c8c4139fe294b936aecce6596) | test | test: 舊句檢查超長行那支測試不再因兩筆紀錄落在同一秒而假紅 |
| 10/05 20:00 | [0b86ba8a](https://github.com/EnzoHsieh-Android/Lumos/commit/0b86ba8a057a608418a32139694230e0efdd2fc2) | chore | chore(lumos): 記錄代碼審跳過 |
| 10/05 21:33 | [ce2a961f](https://github.com/EnzoHsieh-Android/Lumos/commit/ce2a961fbd8706c627c2b25beeead6b7a4e2644c) | merge | 合併 PR #9:README 補上結案連帶收尾、數量標記與推送前新增的檢查 |
| 10/05 22:57 | [73e584b4](https://github.com/EnzoHsieh-Android/Lumos/commit/73e584b4bb9d1528f1dd301293a28df26847a781) | fix | fix: 只換測試綁定的筆記改動不再被當成寫說明擋下 |
| 10/05 22:59 | [db1d100c](https://github.com/EnzoHsieh-Android/Lumos/commit/db1d100c4e5526a499b9aa70c3f48d54b04fa380) | chore | chore(lumos): 記錄代碼審通過 |
| 10/06 01:26 | [522591a5](https://github.com/EnzoHsieh-Android/Lumos/commit/522591a5f70fe9a1411b91a4a360945350f4df27) | merge | 合併 PR #10:只換測試綁定的筆記改動不再被當成寫說明擋下 |
| 10/06 02:33 | [be2a1b5d](https://github.com/EnzoHsieh-Android/Lumos/commit/be2a1b5de700168d60f6d0269ae41770cdfbbc85) | perf | perf: CI 的全套測試分給 8 台機器同時跑,不再擠在一台快逾時 |
| 10/06 02:33 | [0f9c4a11](https://github.com/EnzoHsieh-Android/Lumos/commit/0f9c4a11c7c89c07ba7d7c2a4e2b415fc28100fa) | chore | chore(lumos): 記錄代碼審通過 |
| 10/06 03:19 | [56f38db9](https://github.com/EnzoHsieh-Android/Lumos/commit/56f38db9446a65a7fb7f0ef9da4073f2f3bb83b9) | merge | 合併 PR #13:CI 的全套測試分給 8 台機器同時跑,不再擠在一台快逾時 |
| 10/06 05:51 | [532b32db](https://github.com/EnzoHsieh-Android/Lumos/commit/532b32db5f8fbec3059ae86f6fbb956c68d681b3) | fix | fix: 審查附件不再干擾程式影響分析 |
| 10/06 06:31 | [fa4e916e](https://github.com/EnzoHsieh-Android/Lumos/commit/fa4e916ea1a3379d94efe2f7e812361337e70e86) | chore | chore(lumos): 記錄代碼審通過 |
| 10/06 06:46 | [74d9d1c8](https://github.com/EnzoHsieh-Android/Lumos/commit/74d9d1c842131d82222f0f304ae33d15c012d8b3) | merge | Merge pull request #15 from EnzoHsieh-Android/fix/review-artifact-impact-inputs |
| 10/06 07:48 | [4fc74753](https://github.com/EnzoHsieh-Android/Lumos/commit/4fc747538388a8cd631e665300047dfd7ac778fe) | fix | fix: 修正紀錄有錯時提早回報測試未執行 |
| 10/06 07:52 | [225cae41](https://github.com/EnzoHsieh-Android/Lumos/commit/225cae417bf67d90a8f4156495584588b07f9e7c) | chore | chore(lumos): 記錄代碼審通過 |
| 10/06 08:05 | [48c7d58e](https://github.com/EnzoHsieh-Android/Lumos/commit/48c7d58ed673ffb7b04f1002672e335366d5b9f3) | merge | Merge pull request #16 from EnzoHsieh-Android/fix/review-fix-check-preflight |
| 10/06 09:14 | [99a230ef](https://github.com/EnzoHsieh-Android/Lumos/commit/99a230efdecd7afc01c8565e3bc73f8e45558394) | fix | fix: 特殊字元不再讓不存在的引用行號過關 |
| 10/06 09:19 | [f05c473c](https://github.com/EnzoHsieh-Android/Lumos/commit/f05c473cd5237395ea9691fbf4b3424a060d0f3a) | chore | chore(lumos): 記錄代碼審通過 |
| 10/06 09:30 | [d0504279](https://github.com/EnzoHsieh-Android/Lumos/commit/d0504279eb7dd5ceff9e5c0e3d42b54b32f06eeb) | merge | Merge pull request #17 from EnzoHsieh-Android/fix/review-source-coordinates |
| 10/06 10:57 | [f1142836](https://github.com/EnzoHsieh-Android/Lumos/commit/f11428367e4a76e67beeaba17fc05f2777636463) | fix | fix: 派工單格式錯誤時明確回報原因 |
| 10/06 11:04 | [5ee4a618](https://github.com/EnzoHsieh-Android/Lumos/commit/5ee4a6180d7cc77ab8d26a98094d1ccb23c6df40) | chore | chore(lumos): 記錄代碼審通過 |
| 10/06 11:16 | [d09da591](https://github.com/EnzoHsieh-Android/Lumos/commit/d09da5916f3fc4907a30fdb01cb5ebb6e68e10ab) | merge | Merge pull request #19 from EnzoHsieh-Android/fix/review-seat-input-validation |
| 10/06 11:40 | [31550133](https://github.com/EnzoHsieh-Android/Lumos/commit/31550133cecdfe9b755988fa3545e65a56108400) | test | test: 派工鏡頭的兩支認領測試不再因當下分支改了什麼而逾時 |
| 10/06 11:40 | [65a2e2d3](https://github.com/EnzoHsieh-Android/Lumos/commit/65a2e2d3fdb9277265a09aee0554abe182947cee) | chore | chore(lumos): 記錄代碼審通過 |
| 10/06 12:23 | [57374edb](https://github.com/EnzoHsieh-Android/Lumos/commit/57374edbd0af98ed84873edfba004c1821db5721) | merge | Merge pull request #18 from EnzoHsieh-Android/fix-lens-test-range |
| 10/06 12:24 | [9f23acf5](https://github.com/EnzoHsieh-Android/Lumos/commit/9f23acf5e14fba283ee8691e00ec9f9b8373c859) | docs | docs: 記下 CI 拆成 8 台後的實測耗時與排不到機器的風險 |
| 10/06 12:43 | [023d694e](https://github.com/EnzoHsieh-Android/Lumos/commit/023d694e0a8dc3cb6987c122b1e0af5f299d0c77) | feat | feat: 審查跑到上限時記下人裁、寫回顧再繼續 |
| 10/06 12:54 | [50dc27a4](https://github.com/EnzoHsieh-Android/Lumos/commit/50dc27a4b09fad4ef9af7125309e2d8f7966229a) | merge | Merge remote-tracking branch 'Lumos/main' into cap-retro |
| 10/06 13:04 | [0f5e7e0f](https://github.com/EnzoHsieh-Android/Lumos/commit/0f5e7e0ffe9d1f925e67c6fee382e14ae6a04225) | chore | chore: 跑滿回顧新增告警逐條附理由放行 |
| 10/06 13:04 | [7d910fab](https://github.com/EnzoHsieh-Android/Lumos/commit/7d910fab3a51a357e1909a128ecb945bc6dbaa1c) | chore | chore: 凍結跑滿回顧代碼審的判定 |
| 10/06 13:05 | [babc63a3](https://github.com/EnzoHsieh-Android/Lumos/commit/babc63a34825947f1cb3b7c3f0b97149202c05ca) | chore | chore(lumos): 記錄代碼審通過 |
| 10/06 13:08 | [1da3b5eb](https://github.com/EnzoHsieh-Android/Lumos/commit/1da3b5eb5e8346ccafb9698ae42e8885f1879dd3) | merge | Merge pull request #14 from EnzoHsieh-Android/ci-speedup-notes |
| 10/06 13:08 | [9f2419c6](https://github.com/EnzoHsieh-Android/Lumos/commit/9f2419c6bdcdedd0e6b7236b26d856fef8fbc975) | fix | fix: 審查證據不完整或驗證後換檔時先拒收 |
| 10/06 13:09 | [3e704aaf](https://github.com/EnzoHsieh-Android/Lumos/commit/3e704aaf80609f8d7ec01ced7aac1282c62ea7ff) | chore | chore(lumos): 記錄代碼審通過 |
| 10/06 13:13 | [1a042f1e](https://github.com/EnzoHsieh-Android/Lumos/commit/1a042f1efffb4999c6ad3fba6e3665766518fc95) | chore | chore(lumos): 記錄代碼審通過 |
| 10/06 13:24 | [8292a1d8](https://github.com/EnzoHsieh-Android/Lumos/commit/8292a1d8f7aa15a4b05a78f86ae28d85be7db579) | merge | Merge pull request #20 from EnzoHsieh-Android/fix/review-carrier-quote-preflight |
| 10/06 14:40 | [ffc6b428](https://github.com/EnzoHsieh-Android/Lumos/commit/ffc6b42827679d2eebb751c66999657c71426106) | fix | fix: 記帳前拒絕負數發現計數 |
| 10/06 14:45 | [e540fb9e](https://github.com/EnzoHsieh-Android/Lumos/commit/e540fb9e55178768ad983add41cd5728a0a82b56) | chore | chore(lumos): 記錄代碼審通過 |
| 10/06 14:55 | [53d1c458](https://github.com/EnzoHsieh-Android/Lumos/commit/53d1c458eda3aec370695d4e05012e2be6c05ed3) | merge | Merge pull request #21 from EnzoHsieh-Android/fix/review-findings-count-preflight |
| 10/06 15:08 | [f96fd380](https://github.com/EnzoHsieh-Android/Lumos/commit/f96fd380132738b5f25b2abf0a7a676243b7c76e) | feat | feat: 回頭條件成立後的照留要有期限或綁去處 |
| 10/06 15:08 | [ec72935b](https://github.com/EnzoHsieh-Android/Lumos/commit/ec72935b7b9dfec43ca63326ba66a8c0e1b70f5b) | chore | chore(lumos): 記錄代碼審通過 |
| 10/06 15:50 | [ba62b614](https://github.com/EnzoHsieh-Android/Lumos/commit/ba62b614e57942e4385f72ee76ef18a150c51496) | merge | Merge pull request #22 from EnzoHsieh-Android/revisit-ack-expiry |
| 10/06 15:52 | [1a8c6b0d](https://github.com/EnzoHsieh-Android/Lumos/commit/1a8c6b0d57119927905980b3c4e4effe1e3addcc) | feat | feat: 新增 Lumos 事件帳的讀取端,並讓安裝流程自動裝上 Claude 事件帳外掛 |
| 10/06 15:52 | [0f2e8f13](https://github.com/EnzoHsieh-Android/Lumos/commit/0f2e8f13ee2990069d88090654f861cff377e2aa) | feat | feat: 新增 Claude 事件帳外掛,會談的回合、工具呼叫與子代理會寫進事件帳 |
| 10/06 15:52 | [f34ee0a9](https://github.com/EnzoHsieh-Android/Lumos/commit/f34ee0a9836f8c9534170b40d70e3aadd272dd5f) | chore | chore(lumos): 記錄代碼審通過 |
| 10/06 15:52 | [1fca9d5b](https://github.com/EnzoHsieh-Android/Lumos/commit/1fca9d5b8abbd79d0b38b3581db980c58fae53df) | chore | chore(lumos): 記錄代碼審通過 |
| 10/06 15:52 | [58f89869](https://github.com/EnzoHsieh-Android/Lumos/commit/58f89869de99c3b6cec6359f91cd616ef38a6b17) | chore | chore(lumos): 記錄代碼審通過 |
| 10/06 15:52 | [d566c820](https://github.com/EnzoHsieh-Android/Lumos/commit/d566c8202df47a78fa189614d6fd54525357fce2) | chore | chore(lumos): 記錄代碼審通過 |
| 10/06 15:52 | [ef319668](https://github.com/EnzoHsieh-Android/Lumos/commit/ef319668a108d1cb84745e21a6341b5055dc21f6) | chore | chore(lumos): 記錄代碼審通過 |
| 10/06 15:52 | [9d181ff1](https://github.com/EnzoHsieh-Android/Lumos/commit/9d181ff1e7cbfe8be6ab29aa382ac9642e2c8d02) | chore | chore(lumos): 記錄代碼審通過 |
| 10/06 15:57 | [5213dd84](https://github.com/EnzoHsieh-Android/Lumos/commit/5213dd845d5ea5a8d220e99bc956efbf32ddfd33) | chore | chore(lumos): 記錄代碼審通過 |
| 10/06 16:39 | [70ffba32](https://github.com/EnzoHsieh-Android/Lumos/commit/70ffba327960cfcca9043a5d190f131220878f98) | merge | Merge pull request #11 from EnzoHsieh-Android/mod-event-ledger |
| 10/06 17:03 | [dc8b8247](https://github.com/EnzoHsieh-Android/Lumos/commit/dc8b8247839de30fd73fba8ee968906eeb6f90d2) | fix | fix: 推遠端還沒有的新分支時,推送前的閘不再把整個 repo 當成新改動 |
| 10/06 17:03 | [07377aa7](https://github.com/EnzoHsieh-Android/Lumos/commit/07377aa717bcee089b3ce2308bc9cca1c23193c3) | chore | chore(lumos): 記錄代碼審通過 |
| 10/06 18:09 | [cc032633](https://github.com/EnzoHsieh-Android/Lumos/commit/cc0326335c69891a6af8ef8293b9576d3ecddb13) | merge | Merge pull request #23 from EnzoHsieh-Android/fix-first-push-range |
| 10/06 18:10 | [b8ee67fb](https://github.com/EnzoHsieh-Android/Lumos/commit/b8ee67fba63fda40f426128d95377be1ad949912) | chore | chore(lumos): 記錄代碼審通過 |
| 10/06 18:11 | [866f3213](https://github.com/EnzoHsieh-Android/Lumos/commit/866f3213190be9e823d6351f7f9c518ce7de2863) | merge | Merge remote-tracking branch 'Lumos/main' into cap-retro |
| 10/06 18:22 | [5bd78f33](https://github.com/EnzoHsieh-Android/Lumos/commit/5bd78f330781ebbd55268970ac9ecf7f00536225) | chore | chore(lumos): 記錄代碼審通過 |
| 10/06 18:44 | [d3867054](https://github.com/EnzoHsieh-Android/Lumos/commit/d3867054d2d9f177397c511905d505d3928d9793) | feat | feat: 新增 lumos summary-line,改摘要裡的一行不用再手改開頭欄位 |
| 10/06 18:44 | [8ef3de35](https://github.com/EnzoHsieh-Android/Lumos/commit/8ef3de3524dcc98fc9d8006709582d53f5360c3e) | chore | chore(lumos): 記錄代碼審通過 |
| 10/06 19:28 | [c6be52e1](https://github.com/EnzoHsieh-Android/Lumos/commit/c6be52e1e1e6ad5cc3610d85736b2b75bd2deed2) | merge | Merge pull request #24 from EnzoHsieh-Android/summary-line-cmd |
| 10/06 19:43 | [22992b66](https://github.com/EnzoHsieh-Android/Lumos/commit/22992b665dfea6bd8a8080a6f5ac1fd8a2091ee3) | feat | feat: doctor 列出開頭 updated 落後的筆記,lumos updated-sync 一次改成今天 |
| 10/06 19:43 | [8b0d90ff](https://github.com/EnzoHsieh-Android/Lumos/commit/8b0d90ffbe3145b587208ccde6e5ff8c7bd049a0) | chore | chore(lumos): 記錄代碼審通過 |
| 10/06 20:16 | [bd9b826c](https://github.com/EnzoHsieh-Android/Lumos/commit/bd9b826c013df9bb3bdceeefd4c99fd012b69834) | fix | fix: 允許已宣告測試家的同次寫回 |
| 10/06 20:18 | [cf53b1ad](https://github.com/EnzoHsieh-Android/Lumos/commit/cf53b1ad4aa377c806787b8d5da518a9035c0409) | fix | fix: 在記帳前拒收不可驗證的快照 |
| 10/06 20:28 | [c150ac43](https://github.com/EnzoHsieh-Android/Lumos/commit/c150ac43a3fefb40177d62b7d31cddc92f54b398) | merge | Merge pull request #25 from EnzoHsieh-Android/updated-autobump |
| 10/06 20:35 | [9d9f1ff3](https://github.com/EnzoHsieh-Android/Lumos/commit/9d9f1ff3ff1c764ce4210957f5658f8a557f71d3) | fix | fix: 存量漂移檢查不再把連結標題裡的「還沒做」當成這句還在待定 |
| 10/06 20:35 | [6d9da03a](https://github.com/EnzoHsieh-Android/Lumos/commit/6d9da03a6c10c846ff1c527aea7d2c3d0e66f36f) | chore | chore(lumos): 記錄代碼審通過 |
| 10/06 20:48 | [29595b94](https://github.com/EnzoHsieh-Android/Lumos/commit/29595b9476d84c50004314176775cf4867e644d7) | docs | docs: 調研每輪修復造成回歸的驗證方式 |
| 10/06 21:21 | [b4637da0](https://github.com/EnzoHsieh-Android/Lumos/commit/b4637da0fb67a01a476ac672d564b4a918d753cd) | merge | Merge pull request #26 from EnzoHsieh-Android/c6-link-title |
| 10/06 21:24 | [681d1047](https://github.com/EnzoHsieh-Android/Lumos/commit/681d104791cdcfaf3eb7210cb7a7cbf799bdf6bc) | feat | feat: 讓修訂輪審查核對修補造成的副作用 |
| 10/06 21:28 | [82d5e6a4](https://github.com/EnzoHsieh-Android/Lumos/commit/82d5e6a497a50c23dcfc09b7a4a635c9e73b1a4b) | chore | chore(lumos): 記錄代碼審通過 |
| 10/06 21:28 | [9fc5a4df](https://github.com/EnzoHsieh-Android/Lumos/commit/9fc5a4df509a5c97305efff60ea8e014c1e90e94) | merge | Merge remote-tracking branch 'Lumos/main' into cap-retro |
| 10/06 21:29 | [beb73ba2](https://github.com/EnzoHsieh-Android/Lumos/commit/beb73ba22d8f3e139dabab6dc64158038afa7d1c) | merge | chore: 整合最新主線並保留兩邊審查紀錄 |
| 10/06 21:36 | [61a92f60](https://github.com/EnzoHsieh-Android/Lumos/commit/61a92f60e41cc50de5bf285e6d4fb80d07cf27c4) | feat | feat: 對話壓縮前叫摘要保住交棒狀態 |
| 10/06 21:36 | [73226af5](https://github.com/EnzoHsieh-Android/Lumos/commit/73226af599230ad7bc8100737fad4676649c9108) | chore | chore(lumos): 記錄代碼審通過 |
| 10/06 21:36 | [98d0b6b4](https://github.com/EnzoHsieh-Android/Lumos/commit/98d0b6b42cfb84de865713bd5cd26f3e6cb0dd94) | chore | chore(lumos): 記錄代碼審通過 |
| 10/06 21:38 | [d91511f7](https://github.com/EnzoHsieh-Android/Lumos/commit/d91511f71be817f1b2cfde88d8427ccfbf8d1cef) | docs | docs: 核對修前版本來源並記錄主線整合驗證 |
| 10/06 21:59 | [5c3732cd](https://github.com/EnzoHsieh-Android/Lumos/commit/5c3732cdcb197a727e9b898364447db6309cbca6) | feat | feat: 修訂輪用同一案例核對修復與路徑保留 |
| 10/06 22:00 | [ec020397](https://github.com/EnzoHsieh-Android/Lumos/commit/ec020397a44169456d9bc2feff213d673ceade28) | chore | chore(lumos): 保存同一案例設計審判定 |
| 10/06 22:26 | [d0b24391](https://github.com/EnzoHsieh-Android/Lumos/commit/d0b2439191f4f16b1a35dcc04fbfd2cf9df83736) | merge | Merge pull request #27 from EnzoHsieh-Android/mod-batch2 |
| 10/06 22:30 | [afb7115c](https://github.com/EnzoHsieh-Android/Lumos/commit/afb7115cd7fff911c38b34c0f6aa726e6a1ae228) | merge | Merge remote-tracking branch 'Lumos/main' into cap-retro |
| 10/06 22:38 | [5dbb85e0](https://github.com/EnzoHsieh-Android/Lumos/commit/5dbb85e0f3e0ef62ca7e68e7e2fa4f91de931dc3) | chore | chore(lumos): 記錄代碼審通過 |
| 10/06 22:41 | [5a9bcdca](https://github.com/EnzoHsieh-Android/Lumos/commit/5a9bcdcac0381acb09e0e3c30f6c951304bea67f) | feat | feat: 每個修復根因配對既有行為保留案例 |
| 10/06 23:00 | [d0ba4c03](https://github.com/EnzoHsieh-Android/Lumos/commit/d0ba4c03550966130c7e855b076f9f03a6815f04) | feat | feat: 修補與重構保留完整版本分段驗證 |
| 10/06 23:23 | [97415c5f](https://github.com/EnzoHsieh-Android/Lumos/commit/97415c5fdf3a5428cd3b6d5a5e7158096b41e968) | feat | feat: 高風險修補抽查測試能否抓到退化 |
| 10/06 23:24 | [161984a0](https://github.com/EnzoHsieh-Android/Lumos/commit/161984a09291f46425b8da0608edd070fc0e3fe4) | chore | chore(lumos): 保存測試有效性設計審判定 |
| 10/06 23:39 | [b0b48b7b](https://github.com/EnzoHsieh-Android/Lumos/commit/b0b48b7bda44769205eca2658644d539e73db107) | merge | Merge pull request #28 from EnzoHsieh-Android/cap-retro |
| 10/06 23:50 | [45c23da7](https://github.com/EnzoHsieh-Android/Lumos/commit/45c23da78fde964fbffef194a6ffca243162f78f) | test | test: 用歷史修復驗證保留案例能抓到新錯誤 |
| 10/07 00:02 | [5b4daae0](https://github.com/EnzoHsieh-Android/Lumos/commit/5b4daae054e3396f56770255ec4c344b6dcf8616) | chore | chore(lumos): 記錄代碼審通過 |
| 10/07 00:06 | [21325767](https://github.com/EnzoHsieh-Android/Lumos/commit/213257670fb2d43bf6312ab924acffb456e05762) | feat | feat: 同類提醒分開核對根因與修補因果 |
| 10/07 00:08 | [4964e00a](https://github.com/EnzoHsieh-Android/Lumos/commit/4964e00a9f0e89a421aa353b23fe395c8cbb0876) | feat | feat: 殺傷力配方綁的測試不在合約清單時提醒 |
| 10/07 00:08 | [0f05ba7c](https://github.com/EnzoHsieh-Android/Lumos/commit/0f05ba7c79735f7b44fe2af8e52c6df8794df541) | chore | chore(lumos): 記錄代碼審通過 |
| 10/07 00:09 | [eefcde22](https://github.com/EnzoHsieh-Android/Lumos/commit/eefcde22946479554b4d98be5cf7df68db4db125) | chore | chore(lumos): 記錄代碼審通過 |
| 10/07 00:23 | [4390f609](https://github.com/EnzoHsieh-Android/Lumos/commit/4390f6091efbac52bfa8cf6b4c2c74f2c5e81ddb) | merge | chore: 整合主線回顧流程並驗證修補證據 |
| 10/07 00:29 | [1274f643](https://github.com/EnzoHsieh-Android/Lumos/commit/1274f643b5cc9014847a8c0cfcde5e63fcb7ca2d) | feat | feat: 跑滿回顧沿用修補證據並保留未知 |
| 10/07 00:40 | [d832a57d](https://github.com/EnzoHsieh-Android/Lumos/commit/d832a57d4dfe9f3089a154d9caa0154eba4eca0f) | chore | chore: 校正修復紀錄並保留因果查證界線 |
| 10/07 00:57 | [c4f2b0cf](https://github.com/EnzoHsieh-Android/Lumos/commit/c4f2b0cf479ccdff5823524c0b6954113819496b) | merge | Merge pull request #29 from EnzoHsieh-Android/kill-test-not-bound |
| 10/07 01:02 | [1864fb19](https://github.com/EnzoHsieh-Android/Lumos/commit/1864fb19186c892784fe80b89da781604bf003c8) | test | test: 驗證整合後修復紀錄與回顧流程 |
| 10/07 01:02 | [b31337db](https://github.com/EnzoHsieh-Android/Lumos/commit/b31337db6095cb40a4d4147213b1e3008535e88e) | docs | docs: 對照 Claude 審查片段與收斂風險 |
| 10/07 01:15 | [90137667](https://github.com/EnzoHsieh-Android/Lumos/commit/90137667a3de9e7a475300e19acec6dd7843922d) | docs | docs: 依歷史缺陷校正修訂輪降噪方向 |
| 10/07 01:21 | [f97f776b](https://github.com/EnzoHsieh-Android/Lumos/commit/f97f776bc4dd4a49667cdd8effb88467f2f8496b) | merge | chore: 整合主線配方提醒並保留修補驗證 |
| 10/07 01:27 | [5ff415f5](https://github.com/EnzoHsieh-Android/Lumos/commit/5ff415f57f91d84b00aeddf05b8fd49f9acf3e08) | fix | fix: 事件帳記子代理派孫代理時,發起方不再是空的 |
| 10/07 01:27 | [5b94ca17](https://github.com/EnzoHsieh-Android/Lumos/commit/5b94ca173e3fd96b5f470e082257fbbd463d9608) | feat | feat: 審查員子代理改用白名單,不能改 repo、開 PR 或偷看別席報告 |
| 10/07 01:27 | [668f310f](https://github.com/EnzoHsieh-Android/Lumos/commit/668f310f1ffc171d12e8dadb831b6af73ae01acc) | chore | chore(lumos): 記錄代碼審通過 |
| 10/07 01:32 | [fa54668c](https://github.com/EnzoHsieh-Android/Lumos/commit/fa54668c13d7ae216ec013f71cb69108ad72857e) | chore | chore(lumos): 記錄代碼審通過 |
| 10/07 01:35 | [ba82b236](https://github.com/EnzoHsieh-Android/Lumos/commit/ba82b2368d86d8b11b8be5d601089ac91043c77b) | test | test: 記錄整合版本修正關卡通過 |
| 10/07 02:26 | [e80705c4](https://github.com/EnzoHsieh-Android/Lumos/commit/e80705c4b3c1d8acf677100b5495ca54cedac0bc) | merge | Merge pull request #30 from EnzoHsieh-Android/mod-seat-guard |
| 10/07 02:49 | [caa76fe0](https://github.com/EnzoHsieh-Android/Lumos/commit/caa76fe0fd8c15f13065bd0dd54c3cc76f6195cb) | fix | fix: 合併請求合進主線時認分支上的審查留痕 |
| 10/07 02:49 | [21590293](https://github.com/EnzoHsieh-Android/Lumos/commit/215902936e5c195617baddfd78452623a8e2b5ed) | chore | chore(lumos): 記錄代碼審通過 |
| 10/07 04:06 | [49edc402](https://github.com/EnzoHsieh-Android/Lumos/commit/49edc4024a73c5b1e10b6c5b8aa6718fccc462ae) | test | test: 寫入點檢查不再受函式長度影響 |
| 10/07 04:18 | [01edc749](https://github.com/EnzoHsieh-Android/Lumos/commit/01edc749a42da603c3d2f3f09e32b91a3e9194fa) | test | test: 未附角色卡時允許說明原因並保留拒卡檢查 |
| 10/07 04:38 | [60ad34cb](https://github.com/EnzoHsieh-Android/Lumos/commit/60ad34cb0ef886bdec63b4f8cb43ee7fd1dbf9a2) | merge | Merge pull request #32 from EnzoHsieh-Android/merge-pass-recognize |
| 10/07 04:43 | [bbc07fa8](https://github.com/EnzoHsieh-Android/Lumos/commit/bbc07fa8b01d03c41036931a8a1179c61e1c38b5) | fix | fix: 額外測試寫回只採信固定索引來源 |
| 10/07 04:54 | [825f2f62](https://github.com/EnzoHsieh-Android/Lumos/commit/825f2f620c332246793cb28e246e0928989ea7ab) | docs | docs: 審材保留可還原來源並核算完整閱讀量 |
| 10/07 04:55 | [8d673a4f](https://github.com/EnzoHsieh-Android/Lumos/commit/8d673a4ff431164412ac2dd2700f94e6096f844a) | fix | fix: 不讓其他測試家替本篇假宣告背書 |
| 10/07 04:56 | [8d1bdb71](https://github.com/EnzoHsieh-Android/Lumos/commit/8d1bdb7156a22c2bba9ee470a19b516c138491b1) | merge | Merge remote-tracking branch 'Lumos/main' into merge/review-convergence-main |
| 10/07 05:06 | [b0e7c1d5](https://github.com/EnzoHsieh-Android/Lumos/commit/b0e7c1d56a2b607ef6c66b25e0c77ca05de7a5cf) | feat | feat: 結案時摘要沒跟著改會提醒,舊帳列進存量漂移 |
| 10/07 05:06 | [04436ad2](https://github.com/EnzoHsieh-Android/Lumos/commit/04436ad20348fdb268b069e67144ebcedda39b44) | chore | chore(lumos): 記錄代碼審通過 |
| 10/07 05:51 | [64eeed11](https://github.com/EnzoHsieh-Android/Lumos/commit/64eeed11eba51e5f8073378866ad1b1e6e785313) | docs | docs: 保存審材自足來源並明定回退載入版本 |
| 10/07 05:51 | [d9f28e3b](https://github.com/EnzoHsieh-Android/Lumos/commit/d9f28e3b44d8617ea2313c2f306f7c05ca0d37f5) | merge | Merge pull request #33 from EnzoHsieh-Android/summary-body-drift |
| 10/07 05:51 | [75ae9279](https://github.com/EnzoHsieh-Android/Lumos/commit/75ae9279c95f049e53107896689151a404ceb710) | fix | fix: 補助驗證分別固定變更與設定並限制宣告讀取 |
| 10/07 05:52 | [d1b8af0b](https://github.com/EnzoHsieh-Android/Lumos/commit/d1b8af0be00e202c8e62c1e4a961423bb926ef42) | merge | chore: 整合主線合併留痕修正 |
| 10/07 05:54 | [c09d1203](https://github.com/EnzoHsieh-Android/Lumos/commit/c09d12037d1f0d5a5ce92bd09ccda1ed048a2319) | test | test: 核對主線留痕整合與補助入口未改動 |
| 10/07 06:33 | [5d6dbe6e](https://github.com/EnzoHsieh-Android/Lumos/commit/5d6dbe6e71434a25f0af8fb164f0e20f4d211e24) | docs | docs: 補齊交付審查紀錄與提醒邊界 |
| 10/07 06:44 | [25683c65](https://github.com/EnzoHsieh-Android/Lumos/commit/25683c65991e3602335462406893cfa2099b5746) | merge | chore: 整合主線的結案摘要提醒並驗證修補入口 |
| 10/07 07:02 | [fbb758f5](https://github.com/EnzoHsieh-Android/Lumos/commit/fbb758f593fe03b357daec93f7f702361a3b4adb) | docs | docs: 記錄完整測試與主線提醒的驗證界線 |
| 10/07 07:40 | [f2e4cda7](https://github.com/EnzoHsieh-Android/Lumos/commit/f2e4cda75dcf3999a023b592d7bbd04584148b63) | docs | docs: 保留審查原件並更正整輪版本記帳 |
| 10/07 07:40 | [755abe38](https://github.com/EnzoHsieh-Android/Lumos/commit/755abe38ee8e31813296cc3c94efa1afe35fe7b6) | chore | chore(lumos): 記錄代碼審通過 |
| 10/07 07:56 | [cfe9e922](https://github.com/EnzoHsieh-Android/Lumos/commit/cfe9e922aefe96e6071f981de6dd45d654e55976) | docs | docs: 記錄主線全套驗證與審查證據界線 |
| 10/07 07:56 | [ce4c30f9](https://github.com/EnzoHsieh-Android/Lumos/commit/ce4c30f98fe3573b4f8946653ccf1c2d4d6d75da) | chore | chore(lumos): 記錄代碼審跳過 |
| 10/07 09:39 | [4ed36ff6](https://github.com/EnzoHsieh-Android/Lumos/commit/4ed36ff6c25c62cef29b7473adde7300b4d6ab6d) | feat | feat: 事件帳多記搜尋條件、指令長度、派工的工作目錄與席位 |
| 10/07 09:39 | [85fbcfcc](https://github.com/EnzoHsieh-Android/Lumos/commit/85fbcfcc57bca1fb8bf278f50f844aff42875f23) | chore | chore(lumos): 記錄代碼審通過 |
| 10/07 09:39 | [f00d3509](https://github.com/EnzoHsieh-Android/Lumos/commit/f00d35091f2435f4b26df4cd9706756190470f70) | chore | chore(lumos): 記錄代碼審通過 |
| 10/07 09:39 | [ced1a9bc](https://github.com/EnzoHsieh-Android/Lumos/commit/ced1a9bc33bd4a108f1910bbbefc8afa848c3d68) | chore | chore(lumos): 記錄代碼審通過 |
| 10/07 10:45 | [de1fb54f](https://github.com/EnzoHsieh-Android/Lumos/commit/de1fb54f40d248778e37e202c161bc5496ccfa1b) | merge | Merge pull request #31 from EnzoHsieh-Android/ledger-fields |
| 10/07 11:04 | [46b644a2](https://github.com/EnzoHsieh-Android/Lumos/commit/46b644a2d4fda0419dd034b02e3ea47f54d5b480) | docs | docs: 記下 Claude Code 2.1.292 的 mod 異動與後續優化方向 |
| 10/07 11:23 | [bbf965d6](https://github.com/EnzoHsieh-Android/Lumos/commit/bbf965d6cecca7ec03098edb418ef805bc66ba71) | merge | Merge pull request #35 from EnzoHsieh-Android/cc292-notes |
| 10/07 11:40 | [a79f8bd4](https://github.com/EnzoHsieh-Android/Lumos/commit/a79f8bd49d53a09d435182747a3b8ef6db0a8834) | docs | docs: 會談編號在 /clear、壓縮與接續後的實測結果 |
| 10/07 11:56 | [244a2e0c](https://github.com/EnzoHsieh-Android/Lumos/commit/244a2e0c927652926c16d39bc797391d027f585b) | merge | Merge pull request #36 from EnzoHsieh-Android/sid-findings |
| 10/07 11:58 | [3e961dce](https://github.com/EnzoHsieh-Android/Lumos/commit/3e961dceff824eed5354be490a48756c03b8d135) | feat | feat: 把審查回顧整理成可比較的修復與回歸評測 |
| 10/07 12:03 | [f0297576](https://github.com/EnzoHsieh-Android/Lumos/commit/f0297576826da8725210b409dde9a5664bc81fab) | chore | chore(lumos): 記錄代碼審通過 |
| 10/07 12:08 | [17af2010](https://github.com/EnzoHsieh-Android/Lumos/commit/17af2010e18438dbf3f3cf27dfc8a485eaa33276) | chore | chore(lumos): 記錄代碼審通過 |
| 10/07 12:12 | [9385ff96](https://github.com/EnzoHsieh-Android/Lumos/commit/9385ff960b8f52627a539613ecc11616b1bb4c22) | chore | chore(lumos): 記錄代碼審通過 |

## 尚未合入固定 main 的更新

下列是盤點時遠端分支或原工作樹可追溯、但不在固定 main 的提交。只是留存更新線索，不代表已發布，也未拿來擴張 README 功能聲明。遠端分支沒有拉取未推送工作；原工作樹未提交檔案另列，未逐項驗證其內容。

| 來源 | 台北提交時間 | 提交 | 更新 |
| --- | --- | --- | --- |
| 遠端其他分支 | 10/07 11:44 | `a304bcb8` | chore(lumos): 記錄代碼審通過 |
| 遠端其他分支 | 10/07 11:44 | `de9da667` | fix: ci-wait 給短版 sha 時先換成完整的再查 |
| 遠端其他分支 | 10/07 11:44 | `6c3de88d` | docs: 記下正文反引號裡的測試名沒人查(實測誤報多,先不做) |
| 原工作樹 | 10/04 14:12 | `86dcb404` | docs: 記錄合約檢查與新版表態 |
| 原工作樹 | 10/04 14:05 | `454fa427` | docs: 補記命令列測試假綠案例 |
| 原工作樹 | 10/04 14:05 | `074e91ba` | fix: 探針事故後停止派工並保留失敗紀錄 |
| 原工作樹 | 10/04 13:17 | `5ed04382` | docs: 凍結探針停派設計審判定 |
| 原工作樹 | 10/04 13:17 | `5fcdf6ce` | test: 釘住探針事故停派與失敗留痕缺口 |
| 原工作樹 | 10/04 12:49 | `e8801749` | chore(lumos): 記錄代碼審通過 |
| 原工作樹 | 10/04 12:48 | `5090d4ff` | docs: 凍結探針第四輪審查判定 |
| 原工作樹 | 10/04 12:46 | `70e9ff16` | docs: 記錄探針第四輪驗證與外部對照 |
| 原工作樹 | 10/04 12:28 | `79d3f371` | fix: 不完整探針結果讓整批維持失效 |
| 原工作樹 | 10/04 12:17 | `1b9d8fe1` | fix: 舊事故檔與不完整結果都停止探針批次 |
| 原工作樹 | 10/04 12:01 | `9f8f39d4` | docs: 記錄第四輪送審前的邊界驗證 |
| 原工作樹 | 10/04 11:59 | `d13b52b8` | fix: 拒收健康不可判的探針批次 |
| 原工作樹 | 10/04 04:47 | `87b39887` | docs: 記錄探針第三輪未收斂與驗證結果 |
| 原工作樹 | 10/04 04:28 | `cfe7a703` | fix: 擋住工作樹外指與真身分滲入探針 |
| 原工作樹 | 10/04 04:02 | `730b06fe` | fix: 補齊探針副本邊界與逐場紀錄 |
| 原工作樹 | 10/04 03:21 | `2854d961` | fix: 隔離每場探針並在清理失敗時停批 |
| 原工作樹 | 10/04 02:54 | `88752a29` | docs: 訂清探針副本隔離與失敗處置 |
| 原工作樹 | 10/04 01:37 | `13e077c4` | docs: 記錄第四輪審查未通過與圖譜驗證 |
| 原工作樹 | 10/04 00:09 | `8922c3c9` | fix: 排除不完整讀碼紀錄並封住副本Git寫入逸出 |
| 原工作樹 | 10/03 23:47 | `637989b1` | docs: 記錄探針修復三輪未收斂與隔離缺口 |
| 原工作樹 | 10/03 22:50 | `4a60b231` | fix: 以成功工具回傳確認探針讀碼 |
| 原工作樹 | 10/03 22:36 | `9d91cee3` | docs: 設計以實際回傳內容驗證探針讀碼 |
| 原工作樹 | 10/03 22:01 | `1c91755a` | fix: 探針統計排除異常場次 |
| 原工作樹 | 10/03 21:11 | `19c55711` | docs: 試行代碼審修復驗證並記錄回顧條件 |

原工作樹未提交清單（原樣保留，未改動）：

```text
 M AGENTS.md
 M docs/.canary-log.jsonl
 M docs/.escape-log.jsonl
 M docs/.governance-log.jsonl
 M docs/.usage-log.jsonl
 M "docs/lumos-toolchain-knowledge/Projects/\344\273\243\347\242\274\345\257\251\344\277\256\345\276\251\347\251\251\345\256\232\346\200\247\350\251\246\350\241\214_\350\250\210\345\212\203.md"
 M "docs/lumos-toolchain-knowledge/Projects/\346\216\242\351\207\235\351\232\224\351\233\242\350\210\207\346\270\205\347\220\206\346\224\266\346\226\202_\350\250\210\345\212\203.md"
 M docs/lumos-toolchain-knowledge/Systems/ablation-lumos-first.md
 M docs/lumos-toolchain-knowledge/Systems/autonomous-iteration-loop.md
 M docs/lumos-toolchain-knowledge/Systems/codex-harness.md
 M docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md
 M "docs/lumos-toolchain-knowledge/Systems/\346\270\254\350\251\246\345\201\207\347\266\240\345\275\242\346\205\213.md"
 M "docs/lumos-toolchain-knowledge/Verification/2026-10-04_\346\216\242\351\207\235\345\201\234\346\264\276\350\210\207\345\244\261\346\225\227\347\225\231\347\227\225.md"
 M governance/eval/ablation_lumos_first.py
 M governance/review-reports/review-repair-pilot/roster-alerts.log
 M scripts/scenario_probe.py
 M scripts/test_autonomous_loop.py
 M scripts/test_lumos.py
?? "docs/lumos-toolchain-knowledge/Projects/code-loop\345\210\206\346\224\257\347\225\231\347\227\225\344\270\200\350\207\264_\350\250\210\345\212\203.md"
?? "docs/lumos-toolchain-knowledge/Verification/2026-10-04_\344\273\243\347\242\274\345\257\251\346\224\266\346\226\202\346\240\271\345\233\240\347\233\244\351\273\236.md"
?? "docs/lumos-toolchain-knowledge/Verification/2026-10-04_\344\273\243\347\242\274\345\257\251\346\224\271\351\201\223\347\224\237\346\225\210\351\251\227\350\255\211.md"
?? "docs/lumos-toolchain-knowledge/Verification/2026-10-04_\346\266\210\350\236\215\346\264\276\345\267\245\346\255\243\345\274\217\345\257\251\346\237\245\344\277\256\346\255\243.md"
?? governance/review-reports/code-probe-postreview-dispatch-ledger/
?? governance/review-reports/design-codeloop-pass-branch/
?? governance/review-reports/probe-postreview-dispatch-rebook/
?? governance/review-reports/probe-postreview-dispatch/r1-formal-architecture-v2.md
?? governance/review-reports/probe-postreview-dispatch/r1-formal-architecture.md
?? governance/review-reports/probe-postreview-dispatch/r1-formal-boundary.md
?? governance/review-reports/probe-postreview-dispatch/r1-formal-concurrency.md
?? governance/review-reports/probe-postreview-dispatch/r1-formal-correctness.md
?? governance/review-reports/probe-postreview-dispatch/r1-formal-data.md
?? governance/review-reports/probe-postreview-dispatch/r1-formal-dispatch.json
?? governance/review-reports/probe-postreview-dispatch/r1-formal-external-finder.txt
?? governance/review-reports/probe-postreview-dispatch/r1-formal-external-veto-v2.txt
?? governance/review-reports/probe-postreview-dispatch/r1-formal-external-veto.txt
?? governance/review-reports/probe-postreview-dispatch/r1-formal-intake.md
?? governance/review-reports/probe-postreview-dispatch/r1-formal-security.md
?? governance/review-reports/probe-postreview-dispatch/r1-formal-snapshot.patch
?? governance/review-reports/probe-postreview-dispatch/r1-formal-spec-conformance-v2.md
?? governance/review-reports/probe-postreview-dispatch/r1-formal-spec-conformance.md
?? governance/review-reports/review-repair-pilot-decouple-slim/
?? governance/review-reports/review-repair-pilot-decouple/
```

## Claude／Codex 共用手冊接線核對

從9月底固定起點 ecbb5d3d 比較 main 的 argparse 定義，新增12個parser均已有情境教學；名稱出現不是唯一判準，另核對時機、用法與結果判讀。

| 新入口 | 原本教學路由 | 本次處置 |
| --- | --- | --- |
| events | INDEX → 01進場 | 已有session/json/prune與Claude來源限制，保留 |
| summary-line、updated-sync | INDEX → 03寫回／04自檢 | 已有，保留 |
| fix-check | code-loop入口 → 06代碼審 | 已有骨架、背景執行與結果，保留 |
| cap-decision、retro、retro-stats | 05設計審與code-loop上限步驟 | 補INDEX曝光與README；不重造定義 |
| kill-rm | INDEX → 06配方修補 | 已有列ID、移除、重加與重驗，保留 |
| push-range | INDEX → 06／08自動跑 | 已有自動接線與手動排查，保留 |
| reread-prepare、reread-record、reread-check | INDEX → 06完整步驟 → 08提醒 | 已有兩家派法與範圍，保留 |
| note-shape --slots（新增選項） | 原本只教格子寫法 | 補INDEX／03診斷／07正式啟用與回退；沒有自動替專案開擋 |
| review_convergence.py cohort/template/compare（獨立入口） | 原本僅同目錄說明文件 | 補INDEX／06與code-loop深入路由；來源repo專用、離線，不是每週模型執行器 |
| --regression-set | code-loop短版與完整範本教法不同 | 對齊未知省略、intake留原因，none只代表已核對零回歸 |

另修正06手冊「standard/light不用審」與唯一code-loop來源矛盾，以及CI只看rc0就算綠的教法。未更改任何CLI、hook、安裝器或專案開關。

全現況路由另掃133個固定parser名稱與links/backlinks迴圈入口：正式CLI在共用skills都有文字曝光，但名稱命中不代表逐項功能驗證。補強兩個只有全覽枚舉、情境教學偏薄的舊入口：04自檢加入drift exam的考卷來源與歷史重放，05設計審加入decision-refs list/prune查詢與撤回誤填，INDEX同步路由。
