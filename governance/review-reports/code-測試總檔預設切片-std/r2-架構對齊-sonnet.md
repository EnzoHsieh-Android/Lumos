severity: major

## 1. 分層與依賴方向

修補放的位置和呼叫關係都和鄰居一樣,這一問沒有不對齊。

- `_fanout_hush`、`_fanout_trap`、`_fanout_untrap` 是同一組訊號小函式,全放在 `_fanout_main` 旁邊,由 `_fanout_main` 單向呼叫。`_fanout_hush` 沿用 `_fanout_trap` 的 `st` 字典,收尾還原也走原本的 `_fanout_untrap`,沒有跨層直呼。
  - 引句:「+def _fanout_hush(st):」
  - 對照 file: `scripts/test_lumos.py:49140`(`_fanout_trap`)
- 中斷測試的 SIGINT 還原改成呼叫既有的 `_ppc_sigint_default`。
  - 引句:「+                      preexec_fn=_ppc_sigint_default)」
  - 對照 file: `scripts/test_lumos.py:84318`(定義)、`scripts/test_lumos.py:84333`(同樣用 `preexec_fn=_ppc_sigint_default`)
- 計劃裡寫明不借 `scripts/lumos` 的 `_kill_proc_group`,理由是測試總檔零依賴,符合 python-idioms 的零依賴單檔慣例。
- `pthread_sigmask` 在整個 repo 沒有先例,`scripts/lumos` 裡也沒有。pre-push 掛鉤用的是 bash `trap`(`scripts/hooks/pre-push:339-344`),不是 Python 遮罩。因為沒有既有做法可對照,我不算它「第二種」。

## 2. 命名與錯誤處理

### 1. 記錄檔資料夾前綴,命名對齊(無 finding)

`gctl-run-fanout-` 以 `gctl-run-` 開頭,`_isolate_environment` 的修剪(`startswith("gctl-run-")`)會收到它。測試裡的暫存檔用 `gctl-fansig-`,和 `gctl-test-`、`gctl-gate-repo-` 等 `gctl-<用途>-` 命名一致。
- 引句:「+    work = Path(tempfile.mkdtemp(prefix="gctl-run-fanout-"))」
- 對照 file: `scripts/test_lumos.py:48997`(修剪條件)

### 2. 原本忽略的訊號照舊忽略,慣例對齊(無 finding)

`_fanout_trap` 新增的 `getsignal(sig) == SIG_IGN` 就跳過,和 `_ppc_sigint_default` 註解描述的「進場就忽略的訊號不能再接」是同一個考量。`_SrcOnly` 的用法(`scripts/test_lumos.py:129`、`:644`)也一致。

### 3. `preexec_fn` 在 `_fanout_spawn` 裡用 lambda,不算 finding

這裡的 `preexec_fn` 要還原的是動態的 `old` 遮罩,不能套用固定的 `_ppc_sigint_default`,所以用 lambda 合理。

## 3. 第二種做法

### 1. 測試裡換掉模組函式用 `globals()["_fanout_kill"] = ...`

severity: major
blocking: 否
引句:「+        globals()["_fanout_kill"] = spy」
對照 file: `scripts/test_lumos.py:11324`(註解寫「patch.object 是本檔通篇的猴子補丁寫法」)、`scripts/test_lumos.py:15143`(`mock.patch.object(...)`)、`scripts/test_lumos.py:15145`(`mock.patch.object(m, "_deinit_unbar_gate", ...)`)

說明:本檔換掉函式的既有做法是 `mock.patch.object`,這個寫法本檔通篇都用,第 11324 行的註解還明講了這是慣例。修補在兩處新增了另一套:直接改寫 `globals()["名字"]`,再用 `finally` 手動還原。

- 位置:`t_runner_default_fanout_spawn_error`(`scripts/test_lumos.py:30957`、`:30965`)和新測試 `t_runner_fanout_signal_handling`(`scripts/test_lumos.py:31039`、`:31048`)。
- 證據:我用 `grep -n 'globals()\["' scripts/test_lumos.py` 查,整支檔只有這 4 行。
- 對應做法:要換掉的函式在同一支檔裡,可以寫成 `mock.patch.object(sys.modules[__name__], "_fanout_kill", spy)`。

### 2. `_sp.Popen = fake` 直接賦值再還原,不算 finding

這是 `t_runner_default_fanout_spawn_error` 原本就有的寫法。新測試只是沿用,`scripts/test_lumos.py:114084` 的 `_sock.socket, _sp.Popen = _deny, _deny` 也是同一種直接賦值,所以不算引入新做法。

### 3. `_fanout_trap`、`_fanout_hush`、`_fanout_untrap` 的組合,不算 finding

三個函式都走同一個 `st` 字典,沒有另一套訊號處理機制。

不對齊共 1 條,其中 major 1 條

總結:全份最高 major
