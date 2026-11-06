severity: major

審查範圍:`scripts/test_lumos.py` 預設切片(`_fanout_*`)、對應測試、CLAUDE.md、計劃與 Systems/測試執行器。我實際跑了 `--serial -k t_runner_default_fanout_green` 和 `-k t_runner_default_fanout_interrupt`,兩個都綠,跑完沒有留下 `--shard` 子程序。我沒有改任何檔案,也沒有對 `_fanout_wanted` 做真程序變異。

## 1. nohup 或 `trap '' HUP` 設的「忽略掛斷」被預設切片蓋掉
severity: major
blocking: 否
引句:「st["old"][sig] = _sig.signal(sig, _h)」
file: `scripts/test_lumos.py:49051`
- **失敗場景**:用 `nohup python3.14 scripts/test_lumos.py &` 在背景跑全套。nohup 會把 SIGHUP 設成忽略,單一程序版因此撐得過關終端機。
  - 現在 `_fanout_trap` 不看原本的處置,直接把 HUP 換成丟 `KeyboardInterrupt` 的處理器。
  - 關終端機後,母程序會把四片整組收掉,回 129,整輪全套作廢。
  - CLAUDE.md 新加的「在對話裡跑全套一律放背景」會讓這種用法變多。
- **重現**:同一個程序裡先 `signal.signal(SIGHUP, SIG_IGN)`,再呼叫 `_fanout_trap()`。`signal.getsignal(SIGHUP)` 從 `SIG_IGN` 變成 `<function _fanout_trap.<locals>._h>`。我實跑過這段,結果如此。
- **缺口**:S8 的三個訊號測試都不是在「原本就忽略」的環境下跑,所以抓不到。
- **修法**:`signal.signal(sig, ...)` 前先 `getsignal(sig)`;原本是 `SIG_IGN` 就不裝處理器。

## 2. 切片測試每支會同時開 4 個沙盒子程序,每個都載入整支測試檔,吃光記憶體的風險
severity: major
blocking: 否 ⚠(CI 或推送閘上的實際撞車沒有重現,交編排者裁定嚴重度)
引句:「box, runner, marks = _fan_box()」
file: `scripts/test_lumos.py`,測試 `t_runner_default_fanout_green` 等,`_fan_box` 把整份 test_lumos.py 複製進沙盒
- **失敗場景**:`_fan_box` 把整份 test_lumos.py(約 5.5MB)複製成沙盒執行器。
  - 預設切片測試、interrupt 測試每次要開 4 個沙盒子程序,每個都要載入整支檔。
  - 實測 `-k t_runner_default_fanout_green` 單獨跑時,所有 test_lumos.py 程序的總常駐記憶體峰值約 5.3GB,單一子程序峰值 762MB。
  - 推送前閘會四片同時跑,每片都可能同時在跑這類測試,最壞多出約 17GB。
  - CI 每台機器同時跑 2 份,最壞多出約 8.6GB,私有 repo 的 7GB runner 有被 OOM 殺的風險。
- **重現**:背景跑 `python3.14 scripts/test_lumos.py --serial -k t_runner_default_fanout_green`,每 0.25 秒加總 `ps -axo rss,command | grep test_lumos.py`,峰值約 5.3GB。
- **缺口**:測試沒有限制沙盒片數,它的假測試只有 4 支,用 `LUMOS_TEST_SHARDS=2` 可以降低,而判準 S1 要求的是預設 4 片,所以這是取捨題。

## 3. 開片與記下 pid 是兩個敘述,訊號落在中間會漏收一片
severity: minor
blocking: 否
引句:「procs.append((i, _sp.Popen(cmd, stdout=log, stderr=_sp.STDOUT, stdin=_sp.DEVNULL, env=env, **kw), log, time.time()))」
file: `scripts/test_lumos.py:49074`
- **失敗場景**:`Popen` 回傳之後、`procs.append` 之前收到 TERM 或 HUP,處理器丟出 `KeyboardInterrupt`,剛開的那片沒進 `procs`。
  - 它在自己的 session 裡,`_fanout_kill` 收不到,會跑完整片(幾分鐘)才結束。
  - [[Systems/bound-tests-gate]] 的 PITFALL 寫過同型的坑(「& 起片」與「記下 pid」之間漏收),pre-push 那邊已用 `jobs -p` 解掉,這裡沒有。
  - 視窗只有幾個位元組碼,機率低,但後果是真孤兒。

## 4. 收片途中第二次訊號會中斷收尾,各片留成孤兒
severity: minor
blocking: 否
引句:「_fanout_kill(procs)」
file: `scripts/test_lumos.py:49025`
- **失敗場景**:第一個 TERM 進了 `except KeyboardInterrupt:` 區塊,在 `_fanout_kill` 裡等最多 5 秒。
  - 此時 `_fanout_trap` 的處理器還裝著,第二個 TERM(例如外層工具重送、或使用者再按一次)會在 except 區塊內再丟 `KeyboardInterrupt`。
  - 收尾半途中斷:各片可能只吃到 TERM、沒吃到 KILL。它們在獨立 session,母程序離開後就是孤兒,會跑完自己那一片。
  - 計劃 S8 只驗單一訊號。

## 5. 紅的或出錯的預設切片留下 `lumos-fanout-*` 暫存資料夾,沒有任何清理
severity: minor
blocking: 否
引句:「work = Path(tempfile.mkdtemp(prefix="lumos-fanout-"))」
file: `scripts/test_lumos.py:49016`
- **失敗場景**:
  - 有紅、有片沒過、Ctrl-C、開片出例外(`BaseException` 分支只 `raise`),`work` 都留著,裡面是每片完整輸出。
  - 這個資料夾不在 `_isolate_environment` 的 `gctl-run-*` 修剪範圍,也沒有任何地方清理它。
  - 每次紅燈就多一份,正好是全域規則「暫存清理」想避免的累積。
  - 計劃只寫了「紅了才留」,沒有後續清理條件。

## 圖譜鏡頭
- **Systems/測試執行器**:這是這個 diff 新建的節點,沒有舊合約可破壞。
  - 它的 WHY 行寫「帶 -x 照舊單一程序」「片數上限 16」,與程式一致。
  - 它的 PITFALL 寫「preexec_fn 把 SIGINT 設回 SIG_DFL」,測試裡有照做。
- **Systems/bound-tests-gate**:
  - 推送前閘與 CI 都自帶 `--shard`,不受預設切片影響。
  - 閘用的 `run_cmd`(`.lumos/config.json`)是 `-k {method}`,仍是單一程序。
  - 推送前閘在 `LUMOS_TEST_SHARDS=1` 時不帶 `--shard`,這時 runner 也判成 1 片、單一程序,兩邊的片數判法一致(閘用 `^[0-9]+$`,runner 用 `fullmatch("[0-9]+")`)。
  - 它那條 ★INVARIANT★(code-loop check 對綁定測試逐支真跑)只看 `-k` 路徑,沒被動到。
  - 但上面第 1 點的處理器蓋掉 SIG_IGN,與它記的「背景程序 SIGINT 被忽略會繼承」同屬訊號處置繼承的一族,測試只補了 SIGINT 那一邊。
- **Systems/測試假綠形態**:
  - 唯一的 ★INVARIANT★ 是「還原翻紅釘必須配前置斷言證明現場成立」,新測試都有 `★前置★` 檢查,沒違反。
  - 子程序沒寫摘要或摘要形狀不對算紅、跳過數有上限判紅,都是在補假綠。我另外檢查了這幾處,沒發現新的假綠路徑。
- **沒有發現問題的地方**:
  - 退出碼:全綠 0、有紅 1、被訊號中斷 128+訊號編號,與推送前閘一致。
  - 摘要壞掉或缺欄位、布林當數字,都有處理。
  - 非主執行緒呼叫時,`signal.signal` 的 `ValueError` 被吞掉,不會當。

總結:全份最高 major
