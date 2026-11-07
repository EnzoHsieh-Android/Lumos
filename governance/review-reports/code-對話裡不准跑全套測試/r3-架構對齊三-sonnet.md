severity: minor

審查範圍是 r3-snapshot.patch 全量和 r3-repair.patch 修補差異。鎖檔 `.warming` 不存在,所以沒有可刪的鎖。這次只做讀檔對照,沒有跑測試,也沒有建實驗目錄,沒有暫存要清。

**問 1　分層與依賴方向:跟既有一樣。**
- 新函式 `_home_cache_append_line`(patch 內 scripts/lumos 的 `@@ -69265` 區塊)現在放在 `_home_cache_write` 正後方、`_home_cache_evict` 前面。它跟既有的家目錄快取函式同在一處,上一輪放在 `_drift_m1_*` 旁的做法已被修掉。對照:`scripts/lumos:69222` 是 `_home_cache_write`。
- 它用到的 `_mkdir_trusted_under_home`(`scripts/lumos:70116`)和 `_trusted_private_dir`(`scripts/lumos:70036`)定義在它後面。Python 呼叫時才解析名字,所以沒有問題。
- 開檔改走 `_regular_own_fd`,對照 `scripts/lumos:1657`。它的 docstring 本來就寫明由 `_drift_m1_ledger_miss` 那段抽出,現在回到共用函式。
- 測試執行器呼叫 scripts/lumos 的做法沿用既有的 `_load_lumos_inproc()`,不自己另載。對照 `scripts/test_lumos.py:240`,該檔 `:71`、`:91`、`:104` 也是同樣用法。執行器沒有直接寫檔,也沒有重抄信任檢查。
- 呼叫端只有兩個:`_drift_m1_ledger_miss` 和 `_chat_guard_log`,都是轉呼叫。
- 依賴方向對,沒有跨層直呼。

**問 2　命名與錯誤處理:跟既有一樣,有一處小差異(見下方第 1 條)。**
- 回傳 bool、失敗回 False 不丟例外,跟 `_home_cache_write`(`scripts/lumos:69222`)和 `_local_ledger_append`(`scripts/lumos:1698`)一致。
- 寫入段(`_regular_own_fd`、單次 `os.write` 核對長度、`finally os.close`)跟 `_local_ledger_append` 的結構一樣。
- `_chat_guard_log` 用 `except Exception: pass` 包住載入。這是因為執行器端載入 scripts/lumos 本身可能出錯,不是鄰居的 bool 慣例。載入失敗略過計數是計劃寫明的盡力而為,所以列為 minor。
- 守衛測試改盯共用函式:`t_private_dir_trust_shared_across_four_sites`(`scripts/test_lumos.py:28852`)用「函式名抓區段」盯 `_lens_cache_write` 轉呼叫 `_home_cache_write`。新增的兩條檢查照同一個寫法,分別驗 `_drift_m1_ledger_miss` 和 `_chat_guard_log` 轉呼叫 `_home_cache_append_line`。site 清單裡的 `_drift_m1_ledger_miss` 換成 `_home_cache_append_line`,也符合「信任檢查搬到共用函式、守衛跟著搬」的先例。
- 新增的真子程序案例(快取目錄是連結)放在既有的 `t_runner_chat_full_suite_block_process`(`scripts/test_lumos.py:30912`)裡,沿用該測試的檔案層級做法。

**問 3　第二種做法:各只剩一種。**
- 家目錄附加寫入:`_home_cache_append_line` 是唯一一份。舊的內聯版已從 `_drift_m1_ledger_miss` 前移除,執行器也不再自己開檔。
- 開檔確認(非捷徑、非管線、自己的一般檔):`_home_cache_append_line` 裡原本自抄的 `O_NONBLOCK`、`S_ISREG` 加 uid 檢查已刪,改走 `_regular_own_fd`。
- ⚠ 觀察,不算本 diff 造成:`scripts/lumos:17489` 的簽核帳寫入用 `os.open(... O_NOFOLLOW ...)` 自己開檔。它在 repo 內、不在家目錄、不在這份 diff 裡,是先前就有的,不計入。

不對齊共 1 條,其中 major 0 條。

**1. 執行器 `_chat_guard_log` 用 `except Exception` 包住載入失敗,鄰居函式靠回傳值表示失敗**

計劃寫明計數是盡力而為,所以只是風格差異。

severity: minor
blocking: 否
引句:「    except Exception:   # 計數是盡力而為:scripts/lumos 讀不到或載入出錯都不該讓擋下判斷跟著壞」
`scripts/lumos:1698`
