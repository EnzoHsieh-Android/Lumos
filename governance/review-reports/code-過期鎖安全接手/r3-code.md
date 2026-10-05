severity: major

## F1 背景程序命中快取時不會清掉自己持有的暖機鎖

severity: major

blocking: yes

file: `scripts/lumos:34078`

引句:「正常背景工作會核對啟動者再清自己的鎖;等待端不能按舊取得狀態刪路徑。」

觸發：hook 取得 `.warming` 鎖並啟動背景程序後，另一個不帶 `--deadline` 的正常 `dispatch-lens` 呼叫先算完同一篩圍並寫入快取。背景程序啟動後在 `_dispatch_lens_graph` 的早期快取分支直接 `return 0`，永遠到不了 34194–34204 的持有者核對與清鎖；等待端又因本輪修補刻意不再刪鎖。

後果：快取 20 分鐘 TTL 到期後，後續呼叫永遠看見殘留鎖、不再啟動背景程序，只能持續回 `lock_uncertain`，直到人工刪鎖。這是本輪「等待端不刪鎖」修補自身的新可用性洞；驗證紀錄所稱「背景程序寫完快取並清鎖」沒有覆蓋背景程序一進場就命中快取的分支。

最短重現：

```python
# 載入 scripts/lumos 為 m，將下列依賴換成固定成功結果：
m._lens_git = lambda *a, **k: SimpleNamespace(returncode=0, stdout="/repo\n")
m._git_commit_exists = lambda *a: True
m._lens_full_sha = lambda *a: "a" * 40
m._mainline_ref = lambda *a, **k: ("main", "a" * 40)
m._codeloop_read_dispositions = lambda *a, **k: None
m._codeloop_git_branch = lambda *a: "review"
m._lens_cache_path = lambda *a, **k: Path("/review/cache.json")
m._lens_cache_read = lambda *a, **k: {"text": "ready"}

calls = []
old_unlink = Path.unlink
Path.unlink = lambda self, *a, **k: calls.append(str(self))
try:
    rc = m._dispatch_lens_graph("a..b", repo="/repo", as_json=True, deadline=1)
finally:
    Path.unlink = old_unlink

assert rc == 0
assert calls == []  # 背景持有的 /review/cache.json.warming 未清
```

已執行同一路徑，結果為 `rc=0`、`cache_hit=true`、`unlink_calls=[]`。

建議：把「背景持有者釋放鎖」抽成單一 helper；當 `_LENS_WARM_ENV=1` 且鎖內容符合 `LUMOS_LENS_LOCK_OWNER` 時，在早期快取命中及正常寫完兩條出口都呼叫。等待端仍不得清鎖。新增屏障測試固定「背景尚未讀快取→直接呼叫先寫快取→背景恢復」並驗鎖消失。

## F2 Popen 失敗被誤報成鎖狀態未知與 timeout

severity: major

blocking: yes

file: `scripts/lumos:33920`

引句:「鎖由本次取得時啟動背景計算；啟動失敗只清本次取得的鎖。」

觸發：`_excl_lock_try` 成功，但 `_sp.Popen` 因程序數上限、執行檔或資源錯誤拋出 `OSError`。`_lens_spawn_warmer` 清鎖後吞掉例外且不回狀態；呼叫端仍等待完整 deadline，最後因鎖已不存在而回 `rc 5 + lock_uncertain=true`。hook 隨後把事件記成 `timeout`。

後果：系統明知背景程序根本沒有啟動，卻要求使用者檢查不存在的殘留鎖；hook 可能白等接近整份預算，事件帳也失去「啟動錯誤」與「真正逾時」的分流。本輪測試在 Popen 失敗後立刻由 `_lens_cache_read` 建新鎖並回快取，因此只驗了不刪新鎖，掩蓋了單純 Popen 失敗的實際出口。

最短重現：

```python
m._excl_lock_try = lambda *a: True
m._lens_cache_read = lambda *a: None
subprocess.Popen = lambda *a, **k: (_ for _ in ()).throw(
    OSError(11, "injected spawn failure")
)

rc = m._lens_wait_or_warm(
    Path("/review"), Path("/review/cache.json"),
    "a..b", Path("/review"), True, 0
)
```

已執行，輸出為：

```text
rc=5
{"timed_out":true,"still_warming":false,"lock_uncertain":true,
 "lock_path":"/review/cache.json.warming"}
```

建議：讓 `_lens_spawn_warmer` 回傳成功或原始 `OSError`；啟動失敗應立即回獨立的 `spawn_error` JSON 與 rc 2，hook 顯示「背景程序無法啟動」並 `_hookevent.mark("error", ...)`。補一條沒有替代持有者、沒有快取的 Popen 失敗測試，驗立即返回且不標 timeout。

## F3 fstat 失敗會留下本次剛建立的零位元組永久鎖

severity: minor

blocking: no

file: `scripts/lumos:33855`

引句:「正常競爭者不會刪半成品;若檔名已被換成別人的,不能清掉對方。」

觸發：`os.open(O_CREAT|O_EXCL)` 已成功建立鎖，但緊接著的 `os.fstat(fd)` 拋出 `OSError`。此時 `identity` 仍為 `None`，例外清理會關閉 fd，卻跳過 `unlink`。

後果：vault 之後每次寫入都等待 60 秒才失敗；lens 則永久進入狀態未知，均需人工清除。S3 的測試只注入 `os.write` 與 `os.open` 失敗，未覆蓋取得 fd 後、取得 identity 前的失敗；驗證紀錄對「半成品清理」的涵蓋範圍因此過寬。

最短重現：

```python
# os.open 回傳有效 fd；以 fake lock 記錄 unlink 是否發生
m.os.fstat = lambda fd: (_ for _ in ()).throw(
    OSError(5, "injected fstat failure")
)
m._excl_lock_try(lock, 900)
```

已執行此控制流，結果為：

```text
error=('OSError', 5) half_lock_exists=True unlink_called=False
```

建議：若無法取得 inode 身份就不能安全按路徑刪除，應改用每次取得皆唯一、可回讀核對的 owner token，或採可在名稱層安全辨識本次 acquisition 的建立方式；至少補上 fstat 故障注入，並在圖譜明列「無法取得身份時會留下鎖」這個人工復原邊界。