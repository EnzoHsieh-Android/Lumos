severity: minor

## 問 1:分層與依賴方向

對得上,沒有新的不一致。

- 新函式 `_fanout_*` 放在 `_isolate_environment` 和 `main()` 之間,是檔內執行器入口區。測試放在 `t_runner_shard_*` 旁邊。
- 引句:「+    if _fanout_wanted(_args):   # 不帶條件跑全套:預設切片同時跑(Projects/測試總檔預設切片_計劃)」
- 呼叫順序是參數解析完、`-k` 位置參數併入之後、`_isolate_environment()` 之前。母程序自己不隔離環境,各片子程序各自跑 `_isolate_environment`。這和推送前閘一樣,母程序只負責分派。
- 對照:`scripts/test_lumos.py:48705`(`_isolate_environment`),`scripts/hooks/pre-push:853-905`(殼只分派,測試在子程序裡跑)。
- 跳過基準線的判斷抽成共用的 `_skip_baseline_applies`,單一程序那條路徑也改成呼叫它(patch 內 `_baseline_applies = _skip_baseline_applies()`)。沒有複製貼上,也沒有跨層直呼。

## 問 2:命名與錯誤處理

環境變數、摘要欄位、跳過判法都對得上,有兩處小不一致。

### 1. 暫存資料夾的位置、前綴和清理跟 `_isolate_environment` 不同
severity: minor
blocking: 否
引句:「+    work = Path(tempfile.mkdtemp(prefix="lumos-fanout-"))」
對照:`scripts/test_lumos.py:48736` 的 `_isolate_environment` 用 `prefix="gctl-run-"`,放在 `real_tmp` 下,有「一輪最多清 200 個舊的」的修剪(約 48795 行起)。檔內其他測試暫存都用 `gctl-` 開頭。
說明:`lumos-fanout-` 目錄在紅燈或帶 `--keep-tmp` 時會保留,但沒有任何修剪機制,也不在 `gctl-` 命名族裡。保留現場的做法本身和鄰居一致(`--keep-tmp` 語意相同),差別只在前綴與修剪。這是結構對、做法不同,所以列 minor。

### 2. TERM 的離開碼是 130,推送前閘是 143
severity: minor
blocking: 否
引句:「+        prev_term = _sig.signal(_sig.SIGTERM, _sig.default_int_handler)   # TERM 跟 Ctrl-C 走同一條收尾」
對照:`scripts/hooks/pre-push:340-341`,`trap '_pp_kill_jobs; exit 130' INT` 配 `trap '_pp_kill_jobs; exit 143' TERM`。`scripts/test_lumos.py:84845` 的測試也斷言 SIGTERM 對 143、SIGINT 對 130。
說明:既有慣例是 INT 回 130、TERM 回 143。新碼把兩者合成一條路,TERM 也回 130(計劃 S8 白紙黑字寫「母程序回 130」)。推送前閘的 `pp_stop_if_signaled` 是「128 以上都停」,不受影響。這是刻意的偏離,但沒在計劃裡說明為什麼不跟 143。
- 其他維度一致:`LUMOS_FANOUT_CHILD` 對上 `scripts/hooks/claude/memory-sweep.py:870` 附近的 `_CHILD_ENV = "LUMOS_MEMORY_SWEEP_CHILD"` 的同族寫法。
- 片數判法 `_fanout_shards` 對上 pre-push 的 `[[ "$_shards" =~ ^[0-9]+$ && "$_shards" -ge 1 ]] || _shards=1`。
- 機讀摘要欄位照搬 `scripts/test_lumos.py:49258` 既有的 `passed/failed/skipped/failed_names/skipped_names/shard`。
- 結尾行 `N passed, M failed` 的格式沿用。
- 跳過的處理沿用 `_SrcOnly`。

## 問 3:第二種做法

### 3. 又多一份「開子程序、整組收」和「分派各片」的實作
severity: minor
blocking: 否
引句:「+    for sig in (_sig.SIGTERM, getattr(_sig, "SIGKILL", _sig.SIGTERM)):」
對照:
- `scripts/lumos:26278`(`_kill_proc_group`):`os.killpg(proc.pid, SIGKILL)`,失敗退回 `proc.kill()`。
- `scripts/hooks/claude/memory-sweep.py:930` 的 `_kill_tree`。
- `scripts/hooks/pre-push:330` 的 `_pp_kill_jobs`(TERM、等 0.2 秒、再 TERM)。
- 還有 pre-push 殼裡自己的一套切片、收片和摘要(讀 log 加 rc 0/3/1)。
說明:
- 這是專案的第 4 份收行程群組寫法,而且是第一份「先 TERM、等 5 秒、再 KILL」的兩段式。
- 同一個 patch 裡,開子程序用 `hasattr(os, "setpgid")` 判斷,收程序用 `hasattr(os, "killpg")` 判斷,探測的函式不一致。
- 但這裡有既有先例可以辯護:memory-sweep 也是各自一份(它不 import `scripts/lumos`),`_kill_proc_group` 在 `scripts/lumos` 裡也不是測試檔可直接用的公用函式。
- 計劃已經承認分派有兩份,並寫了 `REVISIT:2027-02-05 推送前閘跟執行器各有一份分派與收片`。
- 不算 major:沒有跨層直呼,有書面回頭條件,附不出需要當場重現的證據。
- ⚠ 交編排者:這份「兩份分派並存」的取捨是否可接受,是設計裁量。我只確認它被明講了。

## 問 4:落點(每支檔有家)

合慣例。

- 引句:「+about_code:」下列的 `scripts/test_lumos.py`(patch 內 `Systems/測試執行器.md` 的 frontmatter)。
- 對照:以下 5 篇 Systems 節點的 `about_code` 已經列了 `scripts/test_lumos.py`:`Systems/測試假綠形態.md`、`Systems/授權與歸屬.md`、`Systems/test-quality-handbook.md`、`Systems/arch-alignment-lens.md`、`Systems/陌生棧不變量簡報評測.md`。
- 這支檔本來就是多家共管。新節點用 `responsibility` 切出「執行入口那一段」,另一方面明寫「不負責個別測試的內容與判準」,切法和既有先例一致。
- 另外,`Systems/bound-tests-gate` 管的是推送前閘怎麼挑子集,新家筆記用 `[[連結]]` 指過去,沒有用反引號寫別人的路徑。
- 沒有發現另一篇已經專管「執行入口」的家,所以不是重複開家。

不對齊共 3 條,其中 major 0 條

總結:全份最高 minor
