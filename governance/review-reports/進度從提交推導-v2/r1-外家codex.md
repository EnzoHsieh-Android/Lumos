severity: blocker

## F1　v2 沒解「做到哪」，只把輸出降級成當下測試觀測

引句:「不說「完成」,說「它宣告的證據現在是什麼狀態」。推論交給讀的人。」

severity: blocker  
blocking: 是  
原需求的消費者要回答「做到哪」，v2 卻明令不作這個判定；讀者仍須人工把測試狀態推論成進度，原本的漂移責任只是從作者移給讀者。這不是解掉六個 blocker 的共同根因，而是撤回原交付目標。

## F2　d3 被實質放棄，v2 沒有實現 Enzo 裁定

引句:「本案只碰得到「這個功能的測試綠不綠」,答不出「相依功能有沒有回歸」」

severity: blocker  
blocking: 是  
d3 明定完成判準為「功能級測試套綠＋相依功能無回歸」，v2 刪掉後半、又禁止宣告完成，因此沒有實現 d3，只交付較弱的任務測試查詢。把另一半留給推送閘與 CI 不構成同一查詢的功能級判準。

## F3　「讀工作樹」只解可見性，未解未提交態的歸屬與並行污染

引句:「未提交態解決——讀工作樹不讀提交歷史,session 做到一半還沒 commit 照樣看得見」

severity: blocker  
blocking: 是  
共用工作樹沒有 session 維度，當場綠或紅可能來自另一個 session，查詢既不能說是哪個任務造成，也不能產生一致時間點的快照；目前事故帳已記錄紅燈誤歸因與瞬時壞檔。file: `docs/lumos-toolchain-knowledge/Issues/同工作區多session並行改動.md:35`；file: `docs/lumos-toolchain-knowledge/Issues/同工作區多session並行改動.md:60`；file: `docs/lumos-toolchain-knowledge/Issues/同工作區多session並行改動.md:104`

## F4　提交夾帶沒有消失，只是不再看得見

引句:「提交夾帶不影響(不依賴提交歸屬)」

severity: major  
blocking: 是  
v2 不再錯讀 trailer 歸屬，但共用工作樹中的夾帶改動仍能令任務測試轉綠，查詢無法分辨成果由誰或哪個任務產生；它消除的是歸屬欄位，不是歸屬問題。既有事故已證實同一棵樹的內容與提交訊息能完全對不上。file: `docs/lumos-toolchain-knowledge/Issues/同工作區多session並行改動.md:40`

## F5　`-k` 實測證實可以借到整族測試的綠

引句:「跑法用既有的測試子集入口(`-k <關鍵字>`),不跑全套。」

severity: blocker  
blocking: 是  
當場以 `t_impact` 查選擇集合，原始碼中沒有名為 `t_impact` 的測試，卻因子字串規則命中 42 支 `t_impact_*`；若它們全綠，設計會把不存在的宣告報成「存在且綠」。執行器明寫子字串篩選而非精確匹配。file: `scripts/test_lumos.py:24828`；file: `scripts/test_lumos.py:24909`

## F6　三態會把「沒驗到」偽裝成綠或紅

引句:「回報三種狀態之一——「不存在 / 存在但紅 / 存在且綠」」

severity: blocker  
blocking: 是  
skip 在 `-k` 子集中只增加 `SKIP`、不增加 `FAIL`，最後仍可 rc0，因此會被三態模型誤報「存在且綠」；超時與環境例外則都增加 `FAIL`，會和斷言失敗一起被壓成「存在但紅」。file: `scripts/test_lumos.py:24945`；file: `scripts/test_lumos.py:24949`；file: `scripts/test_lumos.py:25011`；file: `scripts/test_lumos.py:25027`

## F7　「不存在」同樣混合兩種相反事實

引句:「測試名寫錯的輸出是「不存在」——看得見」

severity: major  
blocking: 是  
名字打錯與測試尚未實作都會得到同一輸出，但前者是計劃引用損壞，後者是正常的未提交進度；只把它顯示出來沒有使狀態變真。三態至少必須分成「未宣告／精確名稱不存在／skip／環境不可執行／超時／斷言紅／綠」。

## F8　立案證明了症狀，仍未證明這個產品形狀有消費價值

引句:「消費者:①接手的 session(現在只能讀散文猜)②Enzo 本人(問「做到哪」要人回答)③無人自跑的迴圈(未來)」

severity: major  
blocking: 是  
陳舊勾選框證明手寫進度會漂，但沒有實例證明接手者會用「逐項現跑測試」，且關鍵字一寬便需 23.4 秒、完整計劃還要逐名重複啟動。第三個消費者仍是未來式，前兩個要的是「做到哪」，而本案明說不回答它，因此尚未通過「症狀—消費者—最小層」的立案線。

## 第五條路

有：把實作改成結構化任務帳的原子轉移——由執行入口取得 task id、套用該任務的 changeset，成功落檔時在同一原子動作追加 receipt；進度從 receipt 帳本折疊，不用測試、trailer 或 CI。這條沿用審查迴圈「成果動作本身就是記錄」的形狀，但必須限制所有受管任務都經該入口，否則又退化成另一份靠自律維護的狀態檔。
hook: Stop
hook: Stop Completed
tokens used
96,632
severity: blocker

## F1　v2 沒解「做到哪」，只把輸出降級成當下測試觀測

引句:「不說「完成」,說「它宣告的證據現在是什麼狀態」。推論交給讀的人。」

severity: blocker  
blocking: 是  
原需求的消費者要回答「做到哪」，v2 卻明令不作這個判定；讀者仍須人工把測試狀態推論成進度，原本的漂移責任只是從作者移給讀者。這不是解掉六個 blocker 的共同根因，而是撤回原交付目標。

## F2　d3 被實質放棄，v2 沒有實現 Enzo 裁定

引句:「本案只碰得到「這個功能的測試綠不綠」,答不出「相依功能有沒有回歸」」

severity: blocker  
blocking: 是  
d3 明定完成判準為「功能級測試套綠＋相依功能無回歸」，v2 刪掉後半、又禁止宣告完成，因此沒有實現 d3，只交付較弱的任務測試查詢。把另一半留給推送閘與 CI 不構成同一查詢的功能級判準。

## F3　「讀工作樹」只解可見性，未解未提交態的歸屬與並行污染

引句:「未提交態解決——讀工作樹不讀提交歷史,session 做到一半還沒 commit 照樣看得見」

severity: blocker  
blocking: 是  
共用工作樹沒有 session 維度，當場綠或紅可能來自另一個 session，查詢既不能說是哪個任務造成，也不能產生一致時間點的快照；目前事故帳已記錄紅燈誤歸因與瞬時壞檔。file: `docs/lumos-toolchain-knowledge/Issues/同工作區多session並行改動.md:35`；file: `docs/lumos-toolchain-knowledge/Issues/同工作區多session並行改動.md:60`；file: `docs/lumos-toolchain-knowledge/Issues/同工作區多session並行改動.md:104`

## F4　提交夾帶沒有消失，只是不再看得見

引句:「提交夾帶不影響(不依賴提交歸屬)」

severity: major  
blocking: 是  
v2 不再錯讀 trailer 歸屬，但共用工作樹中的夾帶改動仍能令任務測試轉綠，查詢無法分辨成果由誰或哪個任務產生；它消除的是歸屬欄位，不是歸屬問題。既有事故已證實同一棵樹的內容與提交訊息能完全對不上。file: `docs/lumos-toolchain-knowledge/Issues/同工作區多session並行改動.md:40`

## F5　`-k` 實測證實可以借到整族測試的綠

引句:「跑法用既有的測試子集入口(`-k <關鍵字>`),不跑全套。」

severity: blocker  
blocking: 是  
當場以 `t_impact` 查選擇集合，原始碼中沒有名為 `t_impact` 的測試，卻因子字串規則命中 42 支 `t_impact_*`；若它們全綠，設計會把不存在的宣告報成「存在且綠」。執行器明寫子字串篩選而非精確匹配。file: `scripts/test_lumos.py:24828`；file: `scripts/test_lumos.py:24909`

## F6　三態會把「沒驗到」偽裝成綠或紅

引句:「回報三種狀態之一——「不存在 / 存在但紅 / 存在且綠」」

severity: blocker  
blocking: 是  
skip 在 `-k` 子集中只增加 `SKIP`、不增加 `FAIL`，最後仍可 rc0，因此會被三態模型誤報「存在且綠」；超時與環境例外則都增加 `FAIL`，會和斷言失敗一起被壓成「存在但紅」。file: `scripts/test_lumos.py:24945`；file: `scripts/test_lumos.py:24949`；file: `scripts/test_lumos.py:25011`；file: `scripts/test_lumos.py:25027`

## F7　「不存在」同樣混合兩種相反事實

引句:「測試名寫錯的輸出是「不存在」——看得見」

severity: major  
blocking: 是  
名字打錯與測試尚未實作都會得到同一輸出，但前者是計劃引用損壞，後者是正常的未提交進度；只把它顯示出來沒有使狀態變真。三態至少必須分成「未宣告／精確名稱不存在／skip／環境不可執行／超時／斷言紅／綠」。

## F8　立案證明了症狀，仍未證明這個產品形狀有消費價值

引句:「消費者:①接手的 session(現在只能讀散文猜)②Enzo 本人(問「做到哪」要人回答)③無人自跑的迴圈(未來)」

severity: major  
blocking: 是  
陳舊勾選框證明手寫進度會漂，但沒有實例證明接手者會用「逐項現跑測試」，且關鍵字一寬便需 23.4 秒、完整計劃還要逐名重複啟動。第三個消費者仍是未來式，前兩個要的是「做到哪」，而本案明說不回答它，因此尚未通過「症狀—消費者—最小層」的立案線。

## 第五條路

有：把實作改成結構化任務帳的原子轉移——由執行入口取得 task id、套用該任務的 changeset，成功落檔時在同一原子動作追加 receipt；進度從 receipt 帳本折疊，不用測試、trailer 或 CI。這條沿用審查迴圈「成果動作本身就是記錄」的形狀，但必須限制所有受管任務都經該入口，否則又退化成另一份靠自律維護的狀態檔。
