severity: clean

沒讀到 python-idioms 的專案適用條款,我只比鄰居。鎖 `.warming` 我沒有動它。

**1. 分層與依賴方向:對齊**
- 收集腳本裡,`NATIVE_QUERY_S` 和 `NATIVE_TAIL` 放在原本那一區常數(`scripts/templates/android-stability-collect.sh:25-38`),跟 `T_SHORT`、`STOP_WAIT`、`REAP` 同一處。
- `NATIVE_TAIL` 還是只被 `native_skip` 和 `native_run` 讀。呼叫方向沒變,也沒有新的跨層直呼。
- 組出 `NATIVE_TAIL` 用的 `STOP_WAIT`、`T_SHORT` 都在同一個檔的常數區,沒有跨檔取值。
- `scripts/lumos:40090` 的重組仍在 `_macrobench_native_retained` 裡,跟既有的 `_events_clean` 呼叫是同一個位置(`scripts/lumos:40089`)。
- 比對的鄰居是 `_macrobench_stab_heap`(`scripts/lumos:40115`)和 `_macrobench_stab_java_growth`(`scripts/lumos:40137`),兩者也在函式裡就地用推導式把外來資料重組。

**2. 命名與錯誤處理:對齊**
- `NATIVE_QUERY_S` 的格式是全大寫、單位後綴 `_S`、行尾註解以「秒:」開頭,跟 `T_SHORT`、`REAP`(`android-stability-collect.sh:25-29`)的寫法一樣。
- `NATIVE_FINISH`(`:38`)是同一組 `NATIVE_` 前綴。
- 逾時失敗仍走 `native_skip` 回傳 `(True, "failed", 原因)` 這個三元組,跟同函式其他分支一樣。原因文字多印了預估秒數,格式沒變。
- 中斷訊息仍走 `die`/`print(...,file=sys.stderr)` 加 `sys.exit(2)`,跟 `main()` 原本的寫法一樣。多列的 `perfetto-configs/` 目錄,和 `android-stability-collect.sh:322-323` 實際寫入的位置一致。

**3. 第二種做法:沒有**
- 組常數:`NATIVE_TAIL` 用既有常數相加,沒有另開一套設定來源。`T_SHORT` 和 `STOP_WAIT` 是 `:25`、`:28` 的既有常數。
- 清理外來字串:仍然只用既有的 `_events_clean`,參數是 `500`,跟 `scripts/lumos:40318` 等處的用法一致。
- 重組外來 JSON:改成固定六個鍵的字典組裝。專案裡沒有現成的鍵白名單工具,`_macrobench_stab_java_growth` 本來就是就地組字典,所以不算新做法。

不對齊共 0 條,其中會擋推送的 0 條
