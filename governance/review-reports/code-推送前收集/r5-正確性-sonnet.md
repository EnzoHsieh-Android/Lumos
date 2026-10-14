severity: minor

本輪審查範圍:`_PP_OWN_PGRP` 啟動器的 runpy 分支與 setpgid 失敗分支、`_pp_kill_jobs` 的第二發 TERM 與 `sleep 0.2`。我讀了 patch 與 `scripts/hooks/pre-push` 的呼叫端(`pre-push:854`、`pre-push:858`)。我也用同一段啟動器程式實測了 runpy 路徑,把 `hasattr(os, "setpgid")` 換成 False 來模擬原生 Windows。實驗目錄已刪。

## Finding 1

severity: minor
blocking: 否 — 只有測試檔本身是符號連結時才會發生,目前呼叫端傳的是 `$REPO_ROOT/scripts/test_lumos.py` 這個真檔案,不影響任何現有路徑
引句:「sys.path[0] = os.path.dirname(os.path.abspath(p[1]))」

問題:直接執行 `python test.py` 時,`sys.path[0]` 是解析符號連結後的真實目錄。這行用的是 `abspath`,不解析符號連結。註解說「照舊跑測試檔」,在這一點上並不完全一致。

失敗情境:`lnk/t.py` 是指向 `real/t.py` 的符號連結。
- 直接執行時,`sys.path[0]` 是 `real`。
- 經 runpy 路徑時,`sys.path[0]` 是 `lnk`。
- 如果測試檔旁邊有同目錄的 import(例如 `import lumos_helpers`),這兩種路徑會找到不同的模組,或找不到。
- 改用 `os.path.realpath` 即可對齊。

佐證:``file: `scripts/hooks/pre-push:826-841` ``(patch 中 `_PP_OWN_PGRP` 區塊)

## 重點逐項

- **離開碼(已讀,無 finding)**:
  - 實測 `sys.exit(3)` 得 3,未捕捉例外得 1,`sys.exit("msg")` 得 1,`sys.exit(None)` 和正常結束得 0。runpy 與直接執行完全一致。
  - `SystemExit` 沒被吞掉,離開碼照實傳出。
- **`sys.argv` 與 `__main__`(已讀,無 finding)**:
  - 與直接執行比對,`sys.argv`(含 argv[0] 與附帶參數)和 `__name__ == "__main__"` 都一致。`__main__.__file__` 也有設。
  - `multiprocessing` 用 spawn 的子行程也正常。
  - 「啟動器的 `p[0]` 是直譯器自己、`sys.argv = p[1:]`」這個切法,對上 `pre-push:854` 與 `pre-push:858` 的呼叫形狀 `"$PY" -c CODE "$PY" test_lumos.py ...`。
- **setpgid 失敗分支(已讀,無 finding)**:
  - 失敗時吞掉 `OSError` 後照樣 `execv`。離開碼還是測試檔自己的。
  - 代價是這片不是群組組長,收的時候退回只送本人,這點註解已承認。
  - 這條路徑不會讓推送被擋或誤判綠。
- **第二發 TERM 在正常結束時被誤送(已讀,無 finding)**:
  - `_pp_kill_jobs` 只在 INT、TERM、HUP 的陷阱裡被呼叫(`pre-push:321-325`、`pre-push:850-851`)。EXIT 陷阱只做 `impact_done` 與 `rm -rf`。
  - 掛鉤正常結束或自然失敗時,第二發不會送出。
  - 陷阱觸發時 `jobs -p` 已空,會在 `[ -n "$_j" ] || return 0` 直接返回。
  - 陷阱觸發時工作已自行結束的情況,第二發對已不存在的群組送出會失敗,錯誤被吞掉。
  - 組號被回收到別的群組,需要 0.2 秒內該 pid 被重用並成為組長。這個機率實務上可忽略,註解也講了組長活著或群組非空時組號不會被重用。
- **`sleep 0.2` 對中斷回應(已讀,無 finding)**:
  - 每一層陷阱多等 0.2 秒再結束。掛鉤和 `run_group` 子殼兩層巢狀,最壞約 0.4 秒,可接受。
  - 等待期間再按一次 Ctrl-C 會殺掉 `sleep`,`|| true` 吃掉,不會卡住。
  - 掛鉤先 `exit 130`,EXIT 陷阱刪暫存目錄時,子殼可能還在它的 0.2 秒等待裡。子殼只剩送第二發 TERM,不再寫 log,無害。
- **資料狀態五問(已讀,無 finding)**:
  - 這輪修補沒有新增持久狀態。暫存目錄仍由 EXIT 陷阱收。
  - `sys.argv` 與 `sys.path[0]` 只改本行程。
  - 第二發 TERM 沒有寫入或刪除的資料副作用。
  - 一致性的缺口只有上面那條符號連結差異。

最高等級 minor,blocking 0 條。
