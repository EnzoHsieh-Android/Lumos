severity: minor

**① 分層與依賴方向**

依賴方向沒有問題。
- `_android_ci_lint_evidence` 收的是 `_ci_workflow_texts` 去註解後的行,`_ci_workflow_texts` 在 `scripts/lumos:60298`。呼叫端 `_lint_android_ci_advisories` 沒有自己讀檔,走的是既有方向。
- `_android_build_texts` 沿用 `_stack_scan_skip`(`scripts/lumos:33926`)和 `_kt_strip_comments`。TOML 檔改用 `_ci_strip_comment`(`scripts/lumos:60284`)剝 `#` 註解。這是跨領域借用 CI 設定檔的去註解函式,但程式裡有註解說明理由,也沒有既有的 TOML 讀法可對照(`scripts/lumos` 沒有其他讀版本目錄的地方),所以不列。
- 測試端 `t_kt_catalog_batch4_wiring` 改用 `_ktpack()` 和 `_ktpack(copy=True)`(`scripts/test_lumos.py:125451`)。口徑留在 `check.py` 的 `catalog_problems`,測試只呼叫它。沒有跨層直呼。

**② 命名與錯誤處理**

- 提醒標法對齊。A3 的 `[kt 第 {idx} 條] A3:` 和 detekt 逐條提醒同形(`scripts/lumos:39225`),`[CI] A1:`、`[CI] A2:` 和 `[CI] T4:`(`scripts/lumos:39227`)同形。
- `_ANDROID_ADVICE_ORDER = ("A1","A2","A3")` 的排序寫法和 `_DETEKT_ADVICE_ORDER`(`scripts/lumos:38804`)一致。
- 讀檔失敗跳過、序號用 `enumerate(…, 1)`、不回顯命令內容,這幾項都對齊。
- 命名小差異:`_CI_WORD_SPLIT` 用 `_CI_` 前綴,同一區塊的其他 Android 常數用 `_ANDROID_`。它只被 Android 的 A1 用,但沒列入 minor,因為純命名且不影響結構。

**③ 第二種做法**

上一輪指出的三項,這輪確認都已共用:
- `_detekt_walk_segments` 真的被兩處呼叫:`_detekt_command_codes` 和 `_detekt_plugin_values`。續行、切段、剝前綴、`sh -c` 只展開一層這個骨架只剩一份。
- `_detekt_plugin_values` 不再自己遞迴,也不再帶 `depth`。
- 測試的 `has()` 改成寫暫存檔、經 `_ci_workflow_texts` 去註解,不再自己重寫整行註解與行尾註解的切法。
- check.py 載入改用 `_ktpack`,新增的 `_kt_pack_check_module` 已刪。
- 變異改用 `_ktpack(copy=True)` 的複本。複本會把 `m.CATALOG` 改指向複本(`scripts/test_lumos.py:125466`),不再手動換 `ck.CATALOG` 再還原。
- 環境變數與工作目錄的暫改再還原,是測試檔常見寫法(`os.chdir` 約 35 處、`os.environ[` 約 104 處),不算第二種做法。

`_CI_WORD_SPLIT` 跟既有切詞不重複。既有的是 `_detekt_split_segments`(`scripts/lumos:38839`),用 shlex 解析命令;A1 刻意不解析命令,只切詞找跡象,目的不同。

仍有三處小的重複或分叉:

F1
severity: minor
blocking: 否
引句:「dirnames[:] = [] if depth >= 3 else [d for d in dirnames if not _stack_scan_skip(d) and not d.startswith(".")]」
- `_android_lint_config_evidence` 為了找 `lint-baseline.xml` 又走了一次 `os.walk`,剪枝條件(層數、`_stack_scan_skip`、不進隱藏資料夾)和 `_android_build_texts` 是同一套寫法,各抄一份(`scripts/lumos:38981-38985`、`39041-39044`)。
- 兩者的層數上限和檔數上限各自獨立,日後改一邊容易漏另一邊。
- 比上一輪的走訪器複本輕,所以只列 minor。可併進 `_android_build_texts` 一起收集。⚠ 判不準,交編排者。

F2
severity: minor
blocking: 否
引句:「        if _pp.basename(seg[0]) in ("gradlew", "gradlew.bat", "gradle"):」
- `_detekt_plugin_values` 用這個三元組判斷 gradle 開頭,`_detekt_segment_codes` 裡也有一份相同的(`scripts/lumos:39166` 附近)。
- 走訪器共用了,但這個判斷詞表還各寫一份。

F3
severity: minor
blocking: 否
引句:「            text = p.read_text(encoding="utf-8", errors="replace")」
- 上一輪的 `_ci_config_texts` 已移除,但 T4 的 `_detekt_ci_has_typed_task` 改成自己內嵌 `read_text` 加 `try/except OSError`,A1 則走 `_ci_workflow_texts`。CI 檔還是有兩條讀法:T4 讀原文,A1 去註解。
- `_ci_config_paths` 的 docstring 現在寫明兩邊口徑不同(T4 讀原文、A1 去註解),所以是有意識的分歧。
- T4 是更早的程式,只列 minor。⚠ 判不準,交編排者。

不對齊共 3 條,其中會擋的 0 條。
