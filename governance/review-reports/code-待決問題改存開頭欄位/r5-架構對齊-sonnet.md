severity: minor

整體判斷:這輪沒有新的第二種做法或跨層直呼。上一輪點名的兩項都收掉了。剩下兩條只是放的位置跟鄰居不同。我用 `git grep` 對照了 `scripts/lumos` 的現況,沒有跑測試。

**1. 分層與依賴方向**

- `main()` 的其他子指令群(canary、loop、decision 等)全部直接寫在 `main()` 裡,只有 guard 搬成 `_guard_dispatch(env, args)`。整支檔裡沒有第二個 `_xxx_dispatch(env, args)` 形狀的函式。
- `_guard_dispatch` 放在 `main()` 後面。`main()` 前面的輔助函式都在它之前,例如 `scripts/lumos:51449` 的 `_test_quality_load_bundle`,`main()` 在 `scripts/lumos:51476`。`_guard_dispatch` 在 `scripts/lumos:53137`,是檔尾 `if __name__` 之前唯一的函式。它由 `main()` 單向呼叫,沒有跨層,結構是對的。但它是第一個也是唯一被搬出 `main()` 的群,註解沒寫為什麼只有 guard 搬。
- `_PQ_CF_OK` 在 `scripts/lumos:6937`,定義在用它的 `_pq_bad_char`(`scripts/lumos:6923` 一帶)之後。同一區的常數如 `_PQ_ID_RE`、`_PQ_CUT_RE` 都放在函式之前(`scripts/lumos:6908` 到 `scripts/lumos:6914`)。
- `_pq_blank`(`scripts/lumos:6953`)和 `_pq_flag_run_ok`(`scripts/lumos:6944`)放在 `_pq_bad_char` 之後、`_strict_scalar` 之前,離呼叫處近,跟區內其他 `_pq_*` 一致。

**2. 命名與錯誤處理**

- `_guard_dispatch` 外層只接 `(RuntimeError, OSError)`,理由寫在 `main()` 裡那行註解:`guard kill` 讀到非 UTF-8 檔會丟 `UnicodeDecodeError`(是 `ValueError` 的子類),rc1 是既有約定,並由 `t_kill_recipe_check_matches_guard_kill` 釘住。
- 這個差異有寫清理由,不算不一致。鄰居也不全是三種:`scripts/lumos:15535` 用 `(OSError, RuntimeError)`,`scripts/lumos:13970` 用 `(OSError, ValueError, RuntimeError)`,decision 那段(`scripts/lumos:53125`)才是三種都接。
- `_decision_amend_locked(env, rel, path, did, field, text)` 現在對齊了。其他鎖內函式(`_cmd_set_locked`、`_summary_line_locked`、`_guard_plan_locked`)也都是 `env` 當第一個參數。不過函式體裡其實沒用到 `env`,這只是形狀一致,不構成問題。

**3. 第二種做法**

- 自寫的 `_is_commit` 已換成共用的 `_lens_full_sha`(`scripts/lumos:46689`,帶 `--end-of-options`),收掉了。
- 字元級例外還在 `_pq_bad_char` 裡,但現在是「共用類別 `_PATH_SPECIAL_CATS`(`scripts/lumos:35300`)加一個題目專用的放行字串 `_PQ_CF_OK`」。`_pq_cf_ok` 函式已改成 `_PQ_CF_OK` 常數。
- `_pq_bad_char` 要回傳第一個違規字元,而 `_path_special_chars`(`scripts/lumos:35303`)只回布林,所以不能直接換。
- 標籤字要整串判旗幟序列,這是題目文字專有的需求。這份理由寫在 `_pq_flag_run_ok` 的 docstring 裡,算已寫明。
- 這輪沒有新的第二種做法。
- 有一處殘留:`_pq_bad_char` 的 docstring(`scripts/lumos:6918`)還寫著「扣掉 _pq_cf_ok 放行的那幾個」,但這個名字已經不存在。這是文字殘留,不影響結構。

severity: minor
blocking: 否
引句:「+def _guard_dispatch(env, args):」
對照處 file: `scripts/lumos:51476`(`main()` 其餘子指令群都內聯;`main()` 前面的輔助函式在它之前,如 `scripts/lumos:51449`)

severity: minor
blocking: 否
引句:「# 放行的格式字元:零寬連接字與不連接字(emoji 組合、印度文字)、軟連字號」
對照處 file: `scripts/lumos:6908`(同區常數 `_PQ_ID_RE`、`_PQ_CUT_RE` 放在函式之前;`_PQ_CF_OK` 在 `scripts/lumos:6937`,定義在用它的 `_pq_bad_char` 之後;`scripts/lumos:6918` 的 docstring 還寫舊名 `_pq_cf_ok`)

不對齊共 2 條,其中 major 0 條
