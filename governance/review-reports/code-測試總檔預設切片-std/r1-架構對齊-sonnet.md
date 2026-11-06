severity: minor

**1. 分層與依賴方向**
新碼放在 `_isolate_environment` 之後、`main()` 之前,由 `main()` 在參數解析完、`_isolate_environment()` 之前分流。呼叫關係單向(`main` → `_fanout_main` → `_fanout_spawn`/`_fanout_wait`/`_fanout_report`)。子程序重跑自己的 `--shard`,這跟推送前閘開片的方向一致。
- 引句:「    if _fanout_wanted(_args):   # 不帶條件跑全套:預設切片同時跑(Projects/測試總檔預設切片_計劃)」
- 對照:`scripts/test_lumos.py:48540`(`_shard_by_duration`)、`scripts/test_lumos.py:48821`(`_isolate_environment`)、`scripts/test_lumos.py:49111`(`main`)、`scripts/hooks/pre-push:850`。
- 無跨層直呼,沒有 finding。
- 一處順帶重構:把 `_baseline_applies` 抽成 `_skip_baseline_applies` 讓單一程序和切片共用,方向正確。原測試 regex 已同步改。

**2. 命名與錯誤處理**
- 環境變數沿用 `LUMOS_TEST_SHARDS`,新增 `LUMOS_FANOUT_CHILD`,都是 `LUMOS_` 前綴。
- 訊號離開碼 130/143/129 跟 `scripts/hooks/pre-push:340-344` 一致。
- 輸出的「N passed, M failed」沿用既有格式。
- 摘要欄位沿用 `--json-summary`。
- `os.setpgid` 偵測跟 `scripts/hooks/pre-push` 的 `_PP_OWN_PGRP` 同一套。
- 兩處不齊,見 finding 1、2。

**3. 第二種做法**
有兩處,都是小偏離。

**Finding 1:收子程序的 TERM、等 5 秒、再 KILL,是第三種收法**
severity: minor
blocking: 否
引句:「    for sig in (_sig.SIGTERM, getattr(_sig, "SIGKILL", _sig.SIGTERM)):」
- 對照:
  - `scripts/lumos:26278`(`_kill_proc_group`):只送 SIGKILL,並在 `AttributeError` 時退回 `proc.kill()`。
  - `scripts/hooks/claude/memory-sweep.py:930`(`_kill_tree`):只送 SIGKILL 的 `killpg`。
  - `scripts/hooks/pre-push:330`(`_pp_kill_jobs`):TERM 兩發。
- `start_new_session` 開子程序的寫法是一致的。
- 收法本身不同:新碼是 TERM、等 5 秒、再對每組 KILL。
- 計劃做法 2 和家筆記都寫明理由:要讓孫程序有機會優雅結束,又不能讓忽略 TERM 的孫程序漏網。
- 但 `test_lumos.py` 沒有 import `scripts/lumos`(單檔零依賴,會被複製進消費專案),所以不能直接重用 `_kill_proc_group`。
- ⚠ 交編排者:這是計劃寫明理由的刻意偏離,我判 minor。是否要在計劃裡補一句「為何不用 `_kill_proc_group` 的直接 KILL」,由編排者裁。

**Finding 2:母程序工作目錄的前綴 `lumos-fanout-` 不在既有清理約定內**
severity: minor
blocking: 否
引句:「    work = Path(tempfile.mkdtemp(prefix="lumos-fanout-"))」
- 對照:
  - `scripts/test_lumos.py:48850` 的 `_isolate_environment` 用 `gctl-run-` 前綴,並在「修剪舊殘骸」(`scripts/test_lumos.py:48893` 附近)清掉標記結束或超過一天的舊根。
  - 測試沙盒用 `gctl-fanout-`(patch 的 `_fan_box`)。
  - `scripts/hooks/pre-push` 把片的 log 放 `$_PP_TMP`,由 `trap ... rm -rf "$_PP_TMP"` 收。
- 新碼的目錄不在 `_isolate_environment` 之前建,也不在它的修剪範圍內。
- 紅、中斷或帶 `--keep-tmp` 時目錄會留下,沒有任何機制回收。
- 這跟全域規則的暫存清理方向相反,也跟 `gctl-` 前綴的慣例不一致。
- 計劃有寫「紅了才留」,但沒寫誰來刪。

**Finding 3:新測試用內聯 lambda 裝回 SIGINT,同檔已有具名輔助函式**
severity: minor
blocking: 否
引句:「                      preexec_fn=lambda: _sig.signal(_sig.SIGINT, _sig.SIG_DFL))」
- 對照:`scripts/test_lumos.py:84194`(`_ppc_sigint_default`)。
- 它的 docstring 說的坑,跟家筆記 PITFALL 寫的是同一個坑。
- 新碼用 lambda 重寫一遍。
- 該輔助函式叫 `_ppc_` 前綴,屬於推送前掛鉤測試群,位置在新測試之後,所以不是明顯可直接重用。
- 嚴重度只能算 minor。
- 同理:`_fan_alive`、`_fan_wait_gone`、`_fan_reap` 是新寫的程序存活判斷。同檔 `scripts/test_lumos.py:23348` 和 `:85002` 也各自在函式內定義 `_alive`,鄰居本身沒有共用版,所以這部分不列。

**4. 落點(每支檔有家)**
- 新家 `Systems/測試執行器` 的 `about_code` 只列 `scripts/test_lumos.py`,`responsibility` 寫明負責和不負責什麼,符合「新開用 `lumos new system`」的形狀。
- 引句:「responsibility: 負責 scripts/test_lumos.py 的執行入口:參數解析、子集挑選(-k、--suite)、分片(--shard、耗時表)」
- `scripts/test_lumos.py` 本來就有多個家(`Systems/測試假綠形態`、`Systems/test-quality-handbook` 等,見 impact.txt),多家是現況。新家只管執行入口,不跟既有家搶責任。
- 家筆記正文沒有用反引號寫別人的檔,只用 `[[連結]]`。
- 沒有不對齊。
- 唯一的小提醒是 `Systems/測試執行器` 把 `main()` 之前的區段都劃進來,而測試函式區段(`t_runner_*`)的責任歸屬沒有寫。不影響合規,不列。

不對齊共 3 條,其中 major 0 條

總結:全份最高 minor
