severity: minor

我只讀不改,沒有改 repo。工作樹 `/Users/enzo/orca/workspaces/lumos-toolchain/android-situation-evidence` 已是修補後的樣子,行號以它為準。

上一輪的 F5(逾時語意分岔,會擋)已收掉。逾時現在是 `_KtSitOverBudget`,在 `_kt_sit_verdict_one` 與 `_dispositions_verdict` 裡照 over_budget 處理:已查出問題照擋,沒有問題就放行並由呼叫端記 fail-open 帳(`scripts/lumos:72462`)。F6 也收掉:讀檔改走 `_nodehome_cat_blobs_capped`,單次 git 逾時取 `_git_timeout` 的剩餘預算。快取清理也抽成共用,沒有再出現第二套寫法。剩下兩處小偏差,都不擋。

## ① 分層與依賴方向

讀檔那層改得對:先問大小、再走有上限的批次讀取、逾時取剩餘預算,三步跟其他呼叫端的寫法一致。`_nodehome_cat_sizes` 搭 `_git_timeout(deadline, cap=…)` 在 `scripts/lumos:10117`、`:11129` 已有同樣的用法。

引句:「sizes = _nodehome_cat_sizes(repo_root, specs, timeout=_git_timeout(deadline, cap=_disp_git_timeout()))」

引句:「blobs = _nodehome_cat_blobs_capped(repo_root, specs, _KT_SIT_READ_MAX, timeout=_disp_git_timeout(), deadline=deadline, sizes=sizes)」

`_nodehome_cat_blobs_capped` 的簽章(`scripts/lumos:46132`)本來就有 `sizes=` 參數,明說「呼叫端已查好大小就不再問第二次」,這裡的呼叫正是那個用法。

**F1** `_home_cache_evict` 放的位置分散。
severity: minor
blocking: 否
引句:「_home_cache_evict(_kt_sit_cache_path(key).parent, _KT_SIT_CACHE_TTL)   # 寫之前清掉過期的」
- 共用函式定義在 drift 區(`scripts/lumos:59451`),新呼叫端在情境段區(`scripts/lumos:39129`)。
- 同家族的 `_home_cache_read` 與 `_home_cache_write` 在 `scripts/lumos:66925`、`:66955`。
- 只是位置不集中,沒有跨層直呼,也沒有第二套實作。

## ② 命名與錯誤處理

`_KtSitOverBudget` 繼承 `_KtSitUnverifiable`,命名跟既有 `_KtSit*` 例外同家族,繼承關係合理:pitfalls 收集時那個 `except (_KtSitUnverifiable, …)`(`scripts/lumos:39174`)仍照「算不出來」提醒,推送前才分流。

`_over(out)` 抽出來給迴圈頂端和收尾共用,跟 `scripts/lumos:72462` 的 fail-open 記帳接得上。

提醒事件的欄位:`scope` 與同一功能的 `waived` 事件(`scripts/lumos:39906`)同鍵同值,一致。`seg`、`row`、`variant` 是新鍵。`pending` 在治理帳事件裡沒有先例,是新詞彙,但內容是自描述的標籤,不算結構分岔。

引句:「extra={"scope": _KT_SIT_QID, "seg": r["seg"], "row": r["row"], "variant": r["variant"], "pending": "blind-judge"})」

**F2** 「沿用既有 warned 事件」只對了一半:kind 是既有的,但 gate 加 kind 的組合是新的。
severity: minor
blocking: 否
⚠ 判不準:這是刻意選擇,還是沒注意到分流規則,請編排者裁。
引句:「_gate_event_or_warn(repo_root, "code-loop", "warned", r["text"][:120], hard=False,」
- 既有的 `warned` 全都來自 `check-*`、`fix-check`、`room-guard`、`note-shape`、`drift-check` 這類閘(例如 `scripts/lumos:22575`、`:50409`、`:52177`),`code-loop` 閘從沒寫過 `warned`。
- 治理帳分流表在 `scripts/lumos:1625-1631` 註明「code-loop 永遠不准出現在本機帳白名單」。所以每條提醒都落進版控帳,每次推送有提醒就會動到 `docs/.governance-log.jsonl`。
- 該表的初衷是「例行觀察不要動版控檔」,而這條提醒是觀察性質。
- 結構上沒有第二套寫法,所以只列 minor。

## ③ 第二種做法

我沒找到新的第二種做法。
- 逾時語意:全部回到 over_budget 一條路。
- 讀檔:`_nodehome_cat_blobs_capped` 是既有函式,沒有另寫。
- 快取清理:`_drift_m1_cache_evict` 委派給 `_home_cache_evict`,兩邊共用,沒有再抄一份。
- 引句:「_home_cache_evict(d, _DRIFT_M1_DEFS_TTL)」(drift 端改成委派,這是上一輪第二種快取清理做法的收斂。)
- lint-waive 計數:`_lint_waivers_ai_pending(repo_root, situation=False)` 用旗標分開數,沿用同一支讀檔與判斷函式,沒有複製。
- `_gate_failopen` 不再放進判定函式裡,改由呼叫端記(`scripts/lumos:72462`),跟 `_gate_failopen`(`scripts/lumos:71118`)的既有分工一致。上一輪 F3 也順帶收掉。

不對齊共 2 條,其中會擋的 0 條
