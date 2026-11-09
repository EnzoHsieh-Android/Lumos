severity: clean

總結:最高嚴重度 clean。我逐 hunk 走過路徑,沒找到會出錯的輸入。

**`_py314_old_interpreter` 擴充**
- 候選的第一個是 3.14 時會跳過去繼續找。函式只在探針印出 `False` 才回傳,在 Ubuntu 26 上 `/usr/bin/python3` 是 3.14,會被略過。
- glob 沒命中時回 `None`。三支呼叫它的測試以及掛鉤測試,都有「沒驗到」的明確分支,不會誤報紅。
- hostedtoolcache 有多版時,`sorted` 以字串排序,挑最低的 3.10。3.9 能解析的檔案 3.10 也能解析,所以比原本 Ubuntu 24 上用的 3.12 更保守,不會多出新失敗。
- 候選 glob 的範圍 `3.1[0-3]` 排除了 3.14,不會挑到新版。
- 符號連結的標準庫問題,我只能推論,沒在 Linux 上實測(本機是 macOS)。
  - 把 `python3` 連結到另一個目錄後,CPython 的 `getpath` 會解析真實路徑找標準庫。
  - `$ORIGIN` 也是以真實路徑為準。
  - `_py314_old_interpreter` 的探針本身就會執行該候選,跑不起來就回 `None`,測試落到「沒驗到」,不會紅。

**掛鉤測試的 PATH**
- `PATH` 是 `oldpy:nopy`,`LUMOS_PYTHON_SEARCH_DIRS` 指向不存在的目錄。我讀了掛鉤內嵌的找 python 段和 `scripts/lumos` 的 `_py_fixed_candidates`:
  - 找 `python3.14` 到 `python3.16` 在 PATH 上找不到,因為 `nopy` 過濾掉了所有 `py*` 開頭的檔。
  - 固定位置已被接縫換掉。
  - 最後的 `python3` 命中的是 `oldpy/python3`。
- 其他找 3.14 的出路也都封住了。
  - `uv` 不在 `/usr/bin` 和 `/bin`。
  - `/opt/hostedtoolcache` 不在任何候選裡。
  - 所以「只找得到舊版」成立。
- 本機實跑:`python3.14 scripts/test_lumos.py -k t_hooks_block_without_python314` 15 條全過,包含 ①。本機的舊版是 macOS 的 `/usr/bin/python3` 轉接殼,透過符號連結也能跑。
- `keep_python` 參數現在沒有任何呼叫端了,屬死參數。這是風格問題,歸架構對齊席。

**SIGINT**
- 我在父程序 `SIG_IGN` 下實跑 `-k t_lwt_r1_term_int_cleanup`:8 條斷言全綠。
- 我複製腳本到臨時目錄並拿掉 `preexec_fn`,同樣的環境下 SIGINT 那半紅 3 條:前置斷言「假工具開起來了」、「lint-new 結束、工具群組收掉」(`rc=3 tool=None`),加上收尾檢查。
- 所以修補確實對症,前置斷言也有擋住「現場走不到」的作用。
- 子程序 SIGINT 是預設時,Python 會自行裝上 `KeyboardInterrupt`,和終端機按 Ctrl-C 的子程序狀態一致。
- SIGTERM 那半沒受影響。`preexec_fn` 只動 SIGINT,SIGTERM 的 4 條照綠。
- 另一個差異是真實 Ctrl-C 會打整個前景行程群組,測試只對 `lint-new` 一個程序送訊號。SIGTERM 那半本來就是這樣,不是這次引入的。

**測試品質**
- 掛鉤測試的 ① 在找不到舊版直譯器時只印「沒驗到」,不算紅。這是這個檔案既有的做法,也不比原本弱:原本 Ubuntu 26 上 `old_py` 因 `/usr/bin/python3` 是 3.14 而為 True,但 `withpy` 是含 3.14 的目錄,走到的是錯的分支,斷言本身會假紅。現在要嘛真驗,要嘛明講沒驗到。
- 修補在 CI 上實際落到哪一支分支,取決於 Ubuntu 26 映像是否真的預裝 hostedtoolcache 的 3.10 到 3.13。這點我在這台機器上無法驗證,只能提醒收貨方看 CI 輸出有沒有「沒驗到」字樣。
- 有一個推論,沒有失敗場景:候選路徑寫死 `x64`,ARM 執行機會落到「沒驗到」。

**固定席節點**
- 這次改動只動 `scripts/test_lumos.py` 和 `測試執行器.md`,我逐條判過,沒有破壞任何一條。
  - 測試假綠形態的 ★INVARIANT★ 要求還原翻紅釘有前置斷言。`t_lwt_r1_term_int_cleanup` 保留了 `★前置★` 斷言,我實測拿掉修法會紅。
  - 授權與歸屬的 ★INVARIANT★ 管 LICENSE 與 SPDX 標示。這次沒有動白名單和檔頭,不受影響。
  - 其餘節點的 ★INVARIANT★ 各管 `search` 排除規則、`code-loop check` 的綁定測試、`canary` 落盤、`guard kill` 的 `rc` 優先序,與這次的測試輔助函式與子程序訊號設定無關。

實驗用的臨時目錄只剩 `ign.py`,位置在 `/tmp/lumos-seat-work/code-測試適應ubuntu26執行機-std/正確性-sonnet/`。測試留下的 `gctl-run-*` 現場和複製的腳本目錄我都已刪除。
