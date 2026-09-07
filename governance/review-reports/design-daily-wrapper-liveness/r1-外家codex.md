severity: blocker

1. severity: blocker｜blocking: 是  
   退出碼雖然變真，仍然沒有任何即時消費者；而完成戳記反而會把「五步都有跑、其中一步失敗」標成存活。  
   引句:「五個步驟的結果做『有任何一個非零就非零』的加總,當作整支的退出碼。」  
   位置: `docs/lumos-toolchain-knowledge/Projects/每日治理wrapper活著沒_計劃.md:33`

   現場 plist 只有 `StartCalendarInterval`，沒有 `KeepAlive`、`SuccessfulExit` 或失敗通知設定（`~/Library/LaunchAgents/com.enzo.lumos.daily-governance.plist:14-20`）；`launchctl print` 也顯示 `keepalive = 0`。因此非零只留下 `last exit code`，不會停止明日排程，也不會狂重試，但同樣不會主動通知任何人。Apple 文件將 `KeepAlive` 說明為「持續嘗試維持行程」，而 calendar job 只是按指定時間啟動；此 job 沒有前者。[Apple launchd 指南](https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/CreatingLaunchdJobs.html)

   更嚴重的是，計劃定義戳記為「我今天跑完了」（計劃:38），死人開關只查 36 小時 freshness（:40-41）。例如第 1 步 rc=1、後四步完成：戳記照樣更新，doctor 不提醒；launchd 只默默保存 rc。事故從「中途死無人知」縮小成「子步失敗無人知」，沒有真正閉環。

   應把戳記中的各步結果也納入 doctor 判定：逾時或任一步非零都提醒；或者另設失敗戳記並由獨立 watcher 消費。

2. severity: blocker｜blocking: 是  
   「通知那條腿斷了」與真碼相反，導致 S2 選錯接線方式，也低估現成通知路徑。  
   引句:「主通道是健檢的輸出,不是通知。通知那條腿現在是斷的(自主迴圈暫停中)」  
   位置: `docs/lumos-toolchain-knowledge/Projects/每日治理wrapper活著沒_計劃.md:42`

   `autonomous-loop.sh` 在派工暫停開關之前就執行 `run_nags`：工具鏈在 `governance/autonomous-loop.sh:282` 跑空轉週報，真正的 `LUMOS_AUTOLOOP_OFF` 判斷直到 `:302-305`。`run_nags` 本身會呼叫 `lumos gov --nags` 並透過 LINE 發送（`:232-247`）。註解甚至明說只有燒錢派工暫停，週期觀測照跑（`:295-301`）。

   不過現成 nags 要同一 gate/node 連喊至少 14 天才通知（`scripts/lumos:3782-3823`），拿來偵測 36 小時死亡太慢。因此不能只把新提醒當普通 soft nag 後宣稱接電；應新增立即通知路徑，或明文接受最長約 14 天的告警延遲。現在的設計兩者都沒有。

3. severity: major｜blocking: 是  
   鎖不能照抄；來源實作的假設與 daily wrapper 不同，而且計劃對「60 分鐘接管」的描述不準確。  
   引句:「把自主迴圈那支已經審過的鎖抄進這支的函式開頭(含 pid、60 分鐘接管、以及那個競態的處理)。」  
   位置: `docs/lumos-toolchain-knowledge/Projects/每日治理wrapper活著沒_計劃.md:47`

   原鎖的非顯而易見細節是：

   - `mkdir` 是唯一原子取鎖點（`governance/autonomous-loop.sh:18`）。
   - 空 pid 不代表殘鎖，可能是持鎖者剛 `mkdir` 尚未寫 pid；年輕空鎖必須讓行（`:23-32`）。
   - 鎖齡量不出時也必須讓行，不能冒險搶鎖（`:27-31`）。
   - 60 分鐘只套用於「空 pid」；若 pid 非空且 `kill -0` 成功，即使鎖已數日仍直接讓行（`:19-33`）。PID 被系統重用時可能永久誤認為原持鎖者。
   - 接管是 `rm -rf; mkdir`（`:35`），兩個接管者之間仍有競態。來源腳本有 `set -e`，第二個 `mkdir` 失敗會退出；daily wrapper 只有 `set -uo pipefail`（`daily-governance.sh:12`），原樣抄過去時第二個接管者會在 `mkdir` 失敗後繼續跑，甚至覆寫 pid。重新取鎖必須顯式檢查成功。
   - 鎖後應立即安裝清理 trap；來源直到大量初始化之後才 `trap finalize EXIT`（`autonomous-loop.sh:37-43,110`），這段窗口也可能殘鎖，不能照搬。

   放在函式體內是對的：bash 會先讀完整個函式才執行，所以遭 curl／改檔截斷的函式不會先取鎖。放在函式外，前奏逐行執行，可能先建立鎖，後面才遇到截斷或語法錯誤，留下殘鎖。它不會改善檔案完整性，只會讓失敗多一個副作用。

4. severity: major｜blocking: 否  
   S4 把兩本不同帳混成同一個分檔理由；「四個整檔讀者」成立，但「逐行雜湊閉包」不屬於正在膨脹的帳。  
   引句:「這本帳有四個整檔讀者,加上判定回放要逐行算雜湊閉包。」  
   位置: `docs/lumos-toolchain-knowledge/Projects/每日治理wrapper活著沒_計劃.md:54`

   目前約 3.97 MB、與計劃數字吻合的是 `docs/.governance-log.jsonl`。它的四個整檔讀者可核到：

   - rewrite 血緣搜尋：`scripts/lumos:788-803`
   - `lumos gov` 彙整：`scripts/lumos:3842-3861`
   - code-loop 在 CI 的 marker fallback：`scripts/lumos:18579-18605`
   - weekly replay 的 converged loop 名單：`governance/autonomous_loop/replay_weekly.py:30-56`

   但判定回放的逐行原文與 SHA 閉包讀的是另一冊 `docs/.canary-log.jsonl`（`scripts/lumos:560-581,644-650`），目前約 0.9 MB。分割 governance ledger 不會直接破壞該閉包。  
   「先不分檔」仍可因四個全讀消費者、4 MB 尚小而成立，但計劃應刪掉錯帳的閉包理由，並把門檻明確綁到 `.governance-log.jsonl`。

5. severity: major｜blocking: 是  
   版控外戳記的機器局部性有說到，但新機／首次安裝時「檔案不存在」的語意完全未定義。  
   引句:「寫在版控外的話,換一台機器就沒有。裁定:寫在版控外的紀錄目錄」  
   位置: `docs/lumos-toolchain-knowledge/Projects/每日治理wrapper活著沒_計劃.md:77`

   若 missing 被當 overdue，新機安裝後會立刻假警報；若 missing 被跳過，腳本從未成功跑過的機器會永遠保持綠燈。若戳記路徑跟 repo 走，搬 repo、重 clone 或清理 logs 也會重置歷史。計劃需要定義：

   - missing 的判定；
   - 首次安裝寬限期從哪個可靠時間起算；
   - 搬機後由誰建立基準；
   - 戳記寫入是否 temp + atomic rename，避免半寫檔只靠 mtime 被判健康。

第三條路：把健康狀態做成一份原子寫入的 machine-local JSON，內容含 `started_at`、`finished_at`、各步 rc、總 rc、run id；由獨立的短程 launchd watchdog 定時讀取，逾時或總 rc 非零就立即通知。這把 watcher 與被監控 wrapper 真正拆成兩個 failure domain，也不會把高頻 `doctor --ci` 每次重複警告灌進治理帳。若不想新增 plist，次佳方案是沿用現存 `run_nags`/LINE 基建，但增加「wrapper-health」的立即事件通道，不等 14 天空轉門檻。
