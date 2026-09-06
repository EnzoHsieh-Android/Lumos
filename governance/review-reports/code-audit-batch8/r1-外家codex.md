severity: major
- [major] 放手後保留 `PIPE` 卻沒有任何讀者，輸出較大的鏡頭會永久卡在寫入，並留下持續存活的背景行程；新增測試因慢工完全不輸出而漏掉此分支
  引句:「kw = {"stdout": _sp.PIPE, "stderr": _sp.PIPE, "text": True}」
  位置:`scripts/hooks/claude/dispatch-lens-hook.py:193`
  blocking:是
  why:實測 `_run_lens_keep_warming()` 執行會輸出 1 MiB 的子行程，0.1 秒後如期回 `(None, True)`；再等 0.7 秒，子行程 `poll()` 仍是 `None`，直到父行程呼叫 `communicate()` 排空 1,048,576 bytes 才結束。此機 macOS 探針 65,536 bytes 可完成、131,072 bytes 已阻塞，臨界確在約 64 KiB 級。真實快取命中鏡頭本次輸出 6,072 bytes，但渲染允許 400 行、單行合約截至 200 字元，最壞可超過 64 KiB。diff 模式目前是在最後 `print()` 前寫快取，所以可能「快取已寫但程序永不退出」；不能宣稱它會自行跑完。測試的 `slow.py` 只睡眠和寫記號檔，stdout/stderr 都是 0 bytes，因此現場的 PIPE 堵塞分支走不到。應在超時後持續 drain 並 `wait()`，或由獨立 supervisor 接管；單純改 `communicate(timeout=…)` 仍需處理超時後的持續排空。

- [major] 共用公式只限制「單次呼叫」，三支串行執行多個子程序的 hook 沒有扣累計 elapsed，總內層上限仍可超過外層天花板
  引句:「現在:天花板由註冊表一處生成,用 --budget 傳進來;內層一律取「天花板 × 0.7 減掉已耗」」
  位置:`scripts/hooks/claude/check-graph-sync.py:407`
  blocking:是
  why:逐點核對五支 hook：impact-hook 唯一正確傳入 `elapsed=time.monotonic()-t0`；dispatch-lens 只有一個主要等待點，42/60 秒成立；但 check-graph-sync 最多先做 5×2 秒 Obsidian 查詢，再給 impact 21 秒，合計可達 31 秒而外層只有 30；lumos-entry 先給 git 7 秒、後給 enforcement 7 秒，合計 14>10；ci-status 先後兩次 git 各給 10.5 秒，合計 21>15。新增測試只在每個模組載入後呼叫一次 `_inner_budget(elapsed=0)`，所以全部會綠，卻沒有驗完整 `main()` 的總時間。

- [major] `--budget` 接受零、負數及無上限值，會打破「內層永遠小於外層」並可實質關閉 timeout
  引句:「★永遠小於外層★,所以逾時走的是自己的 fail-open 分支,不是被外面砍掉。」
  位置:`scripts/hooks/claude/impact-hook.py:466`
  blocking:是
  why:直接載入現場函式測得：沒帶、後面沒值或非數字均退回 default 30→21 秒；`--budget -2` 得 outer=-2、inner=1；`--budget 0` 得 outer=0、inner=1，均違反 inner<outer；`--budget 1e300` 得 7e299 秒；`--budget=inf` 得無限 timeout；`nan` 偶然被 `max()` 收成 1。註冊表目前只產生正整數，但 hook 的公開 argv 解析沒有有限正數驗證，測試也只涵蓋缺參數與 elapsed=999，未涵蓋題目要求的 0／負數／超大值。

- [minor] `poll()+sleep(0.05)` CPU 成本很低，但完成路徑最多多等約 50ms，且它正是無法排空 PIPE 的原因
  引句:「while _time.monotonic() < deadline:」
  位置:`scripts/hooks/claude/dispatch-lens-hook.py:201`
  blocking:否
  why:迴圈每秒最多約 20 次 `poll()`，單支 hook 的 CPU 代價可忽略；精度是約 0–50ms 額外延遲，實測 0.1 秒預算於 0.122 秒返回。既有 `Popen.communicate(timeout=…)` 能同時等待並排空輸出，避免正常等待期間堵管；但超時後仍需 supervisor/thread 繼續 drain+wait，否則只是把堵塞延後。

- [clean] `start_new_session=True` 能抵抗 POSIX 的「殺父 hook 行程組」，macOS 實測成立，Linux 的 session／process-group 語意相同
  引句:「kw["start_new_session"] = True      # 自己一組,不跟著 hook 一起被收掉」
  位置:`scripts/hooks/claude/dispatch-lens-hook.py:195`
  blocking:否
  why:實測建立獨立 session 的父 hook，再由它建立 `start_new_session=True` 子行程；對父 hook 的 process group 發 SIGTERM 後，父行程退出而子行程仍可由 `kill(pid,0)` 確認存活。Linux POSIX 下 `setsid()` 對 process group 信號亦相同。它無法抵抗按程序樹、cgroup/systemd scope、容器或 Windows Job Object 的整體清理，但目前作者描述的 SIGKILL process-group 情境成立。

- [clean] 放手本身通常不會形成永久殭屍，但目前會形成更糟的「PIPE 寫滿後仍活著」行程
  引句:「# 時間到:★不呼叫 kill/terminate★,直接放手。它會把快取寫完。」
  位置:`scripts/hooks/claude/dispatch-lens-hook.py:206`
  blocking:否
  why:若子行程正常退出，hook 很快退出後會由系統的 reaper 收養並回收；若父 Python 尚存，`Popen` destructor 會把未完成程序放入 subprocess 的 active 清理集合。因此單純「未呼叫 wait」不等於永久 zombie。實測真正持續存在的是被未讀 PIPE 卡住、尚未退出的 sleeping 狀態，屬第一條 blocking 問題。

- [minor] Stop hook 的 30 秒上限確實擴大互動尾延遲，但正常無 code diff 的實際成本很小
  引句:「"check-graph-sync.py": 30,   # ★從 10 提到 30★:它內層要跑圖譜同步檢查(實測需 25s),」
  位置:`scripts/merge-claude-settings.py:73`
  blocking:否
  why:以本 repo 的 Stop payload 真跑 `check-graph-sync.py --budget 30`，實際 0.042 秒、rc=0。只有存在 code diff 且進入同步 impact 慢路徑時，使用者才可能多等到約 21–30 秒；這是 Stop 事件，會直接延後回合結束。提高外層有合理依據，但應記錄有 code diff 的 p50/p95，而不是只用一次約 25 秒樣本定 30 秒；第二條修正成總 deadline 後也能確保不吃滿外層。

- [major] 兩支新增測試具備「還原整段功能會紅」的表面殺傷力，但對本次最危險的現場分支是假綠
  引句:「這支驗行為不是驗寫法:真的起一支慢工,設一個會超時的預算」
  位置:`scripts/test_lumos.py:11316`
  blocking:是
  why:推演還原方式一：把 impact 單檔 timeout 還原為 30，既有 `t_codex_s1_r1_fixes` 的新斷言要求 ≤22.5，會翻紅；把 `_inner_budget`／`_run_lens_keep_warming` 整段還原，兩支新測試也會因屬性不存在而紅。可是更貼近現場的局部退化——保留 helper，但讓慢子行程輸出超過 pipe buffer——新增 warming 測試仍綠，因其慢工零輸出；實際 1 MiB 探針則在預期完成時間後仍 `poll() is None`。此外 timeout 測試只驗一次公式，不會抓到三支 hook 的串行總預算超標。因此它們能抓「整段被刪」，抓不到本投稿真正新增的資源與 deadline bug。
