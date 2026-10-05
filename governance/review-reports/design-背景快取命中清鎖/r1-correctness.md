severity: major
severity: major
blocking: yes
file: `governance/review-reports/design-背景快取命中清鎖/r1-snapshot.md:20`
引句:「本小修將背景程序從算得出快取路徑後的所有出口一起包住」
finding: 背景程序重新解析原始 `diff_range`，並未繼承派工端已鎖定的完整 SHA 或快取路徑。若 symbolic ref 在派工與背景啟動間移動，背景會從新的 SHA 算出另一把鎖；照設計加上的 `finally` 只能清新路徑，會漏掉自己原先的鎖。更糟的是，同一派工程序可連續啟動兩個範圍，兩把鎖都只寫同一個派工 PID；舊背景改算到新路徑後會把第二個工作的鎖誤認成自己的並刪除，S2 的「PID 不符」反例抓不到同 PID、不同 acquisition。
file: `scripts/lumos:33909`
file: `scripts/lumos:33916`
file: `scripts/lumos:34053`
file: `scripts/lumos:34076`
file: `scripts/test_lumos.py:16331`
最小重現: 在暫存 git repo 建 C1、C2，讓同一 Python 派工程序以 `main~1..main` 建立 A 的 `.warming` 後用屏障延遲背景 A；把 `main` 推到 C3，再由同一程序派 B，故 A、B 鎖內 PID 相同；放行 A。A 重新解析為 C2..C3，按設計的 PID+暖機標記 finalizer 會刪 B 的鎖，而 A 原本 C1..C2 的鎖仍存在。應斷言 `A_lock.exists() is False` 且 `B_lock.exists() is True`；照目前設計兩項都相反。
建議: 派工端在取得鎖前固定完整 `base_sha..head_sha`，背景只接收這組不可變 SHA，或直接傳入已決定的快取／鎖路徑；若仍允許同 PID 多次 acquisition，鎖內容另加每次取得唯一 token，清理時核對 token。把上述 ref 移動屏障加入 S1/S2 測試，且須走 `_lens_spawn_warmer` 的真實參數傳遞，不能只直接設定環境變數呼叫 `_dispatch_lens_graph`。

回退：已讀，無 finding。  
實務隱患：除上述同 PID、不同 acquisition 缺口外，無獨立 finding。  
驗證順序：除上述缺少 ref 移動紅燈外，無獨立 finding。

總結：最嚴重 severity: major；blocking: 1。
