前掃結果：四類都有需要澄清之處，但未判定設計成敗。明確的新 API 提案未因尚未實作而列為壞引用。

## 1. 未定義詞

1. 「兩個命令／兩個真模型 runner／父派工器」沒有明確對應。

   修改前原文：

   > 「兩個命令均可用 `--attempt-ledger`」  
   > 「兩個真模型 runner……」  
   > 「父派工器 import 同一實作」

   建議澄清：直接寫成：

   - 探針命令：`scripts/scenario_probe.py`
   - 父派工命令：`governance/eval/ablation_lumos_first.py`
   - 真模型 runner：`run_one()`、`run_one_codex()`
   - 父派工入口：`run_job()`

   目前必要函式確實分布於 [scenario_probe.py](/Users/enzo/orca/workspaces/lumos-toolchain/aspidochelone/scripts/scenario_probe.py:711) 與 [ablation_lumos_first.py](/Users/enzo/orca/workspaces/lumos-toolchain/aspidochelone/governance/eval/ablation_lumos_first.py:232)。

2. 「首五小時」及「持久寫入時間」缺少時間錨點與邊界。

   修改前原文：

   > 「新建帳自動保守封住首五小時」  
   > 「既有帳從持久寫入時間計算」

   建議澄清：定義新帳五小時從哪個持久欄位開始，例如初始化交易寫入的 `initialized_at`；既有意圖則使用每筆 `claimed_at`。同時說明恰好滿五小時的紀錄是否已過期，以及時間使用 Unix epoch／UTC。

3. 「壞帳」「時計錯誤」「失效結果」涵蓋範圍不明。

   修改前原文：

   > 「缺模組、壞帳或鎖逾時均在模型前停止」  
   > 「初始化、時計與锁錯誤均記入失效結果」

   建議澄清：

   - 壞帳是否包括 SQLite corruption、缺表、schema/version 不符、非一般檔、唯讀及父目錄不可寫。
   - 時計錯誤是否只指 `now < max(claimed_at, initialized_at)`。
   - 失效結果具體是哪個 JSON、哪些欄位，以及是否必須 `fatal=true`、`inconclusive=true`、退出碼 3。

4. S1 的「上限五時」語意不完整。

   修改前原文：

   > 「已有四次啟動意圖且上限五時」

   建議改為「已有四筆啟動意圖且窗口上限為五筆」。

## 2. 壞引用

1. 「第三輪 G10、G11」沒有可解析來源。

   修改前原文：

   > 「第三輪 G10、G11 的同一原始反例為……」

   建議澄清：補上對應 Verification／Issue／父計劃節點，或直接標出 G10、G11 所在文件與條款。

2. 「父計劃 S18」沒有指出父計劃是哪一篇。

   修改前原文：

   > 「修改父計劃 S18 與 CLI 承諾後再移除」  
   > 「先裁決並修改 S18／CLI 說明」

   建議澄清：兩處都改為明確節點名稱及條款，例如「`[[Projects/…_計劃]]` 的 `[S18]`」。這項涉及既有裁定來源，交正式席確認實際父計劃。

3. 明確列出的三個本地圖譜引用與兩個產品檔均存在，未發現目標檔缺失。外部 SQLite／Python 網址依限制未連線驗證。`--attempt-ledger` 是新 API 提案，未列為壞引用。

## 3. 範圍自相矛盾

1. 「帳缺失即停止」與「新建帳自動初始化」互相衝突。

   修改前原文：

   > 「新建帳自動保守封住首五小時」  
   > 「當帳缺失、損壞、不可讀……派工器應在模型前停止」

   建議澄清：正式席需二選一：

   - 路徑不存在時原子建立新帳並進入五小時冷卻；只有建立或初始化失敗才停止。
   - 路徑不存在一律停止，另設明確初始化操作。

2. `--max-per-window 0` 與新帳封鎖沒有說明優先順序。

   修改前原文：

   > 「`--max-per-window 0` 仍明示不設限制」  
   > 「新建帳自動保守封住首五小時」

   建議澄清：明定上限為 0 時是否完全不執行帳本 claim／冷卻。若仍封鎖，就不能同時稱為「不設限制」。這是 CLI 合約，交正式席裁定。

3. 「保守等待」與「不再等待 300 秒」容易讀成相反行為。

   修改前原文：

   > 「新帳首五小時只保守等待」  
   > 「且不再先等待300秒」

   建議澄清：若設計是立即拒絕，改成「五小時冷卻期間每次呼叫立即拒絕，不在程序內 sleep；五小時後重新呼叫才可 claim」。若真要程序等待，需明列 S4 的例外條件。

其餘範圍邊界一致：帳本只代表同一路徑、本機使用者／機器的啟動意圖，不宣稱供應商帳務或跨機全域用量。

## 4. 機械宣稱驗語意

1. 子探針如何取得「五小時上限」尚未形成完整介面。

   修改前原文：

   > 「每個實際 launch 前仍在同一交易重驗」

   現有父派工器的 `--max-per-window` 只先計算餘額，再把它傳成 `--max-attempts`；探針的 `--max-attempts` 則是程序內總啟動數，不是持久窗口上限。[父派工現況](/Users/enzo/orca/workspaces/lumos-toolchain/aspidochelone/governance/eval/ablation_lumos_first.py:232)、[探針現況](/Users/enzo/orca/workspaces/lumos-toolchain/aspidochelone/scripts/scenario_probe.py:954)

   建議澄清：為探針另定持久窗口上限參數，父派工器必須原值轉交；`--max-attempts` 保留為單批上限。只有帳路徑、沒有上限值，交易無法判斷是否准予 claim。

2. 「帳本錯誤停止整批」需要接到既有 fatal 語意。

   修改前原文：

   > 「初始化、時計與锁錯誤均記入失效結果並停止派工」

   現有探針只把特定例外判成 fatal；一般 runner 例外可能只形成單題儀器例外後繼續。[例外分類位置](/Users/enzo/orca/workspaces/lumos-toolchain/aspidochelone/scripts/scenario_probe.py:1061)

   建議澄清：定義帳本專用 fatal 例外或等價結果，要求：

   - 探針停止後續題目與重試；
   - 結果標記 `fatal`、`inconclusive`；
   - 探針退出碼為 3；
   - 父派工器設 stop 並停止後續 job。

3. S4 的「零新增 launch-intent」無法區分首次呼叫與重試。

   修改前原文：

   > 「同批已耗盡啟動意圖額度且撞用量上限時，應零新增 launch-intent」

   撞到供應商上限的首次模型啟動本身已應留下 launch-intent；真正應為零的是其後被本機額度拒絕的重試。

   建議改為：「首次撞上限的啟動意圖保留；本機窗口已滿後不得為重試再新增一筆，且 `sleep` 呼叫數為零。」現有等待入口在 [scenario_probe.py](/Users/enzo/orca/workspaces/lumos-toolchain/aspidochelone/scripts/scenario_probe.py:1115)。

4. `BEGIN IMMEDIATE` 的宣稱方向合理，但需把可驗證交易契約寫完整。

   修改前原文：

   > 「以一個 BEGIN IMMEDIATE 交易核對窗口並寫入一次 launch-intent。commit 成功才啟動模型。」

   建議補成可直接測試的順序：

   1. `BEGIN IMMEDIATE`；
   2. 驗 schema、初始化時間及時鐘回撥；
   3. 以同一個 `now` 計算未過期意圖；
   4. 已達上限則 rollback／結束，不啟動模型；
   5. 未達上限則插入一筆並 commit；
   6. commit 成功後才呼叫模型 subprocess。

   另應固定鎖等待上限及逾時結果，否則「鎖逾時」測試無法穩定重放。

本次約讀取 1,200 行工具輸出，未超過 1,800 行；未讀其他審查報告、未執行模型或 paid calls、未修改任何檔案。