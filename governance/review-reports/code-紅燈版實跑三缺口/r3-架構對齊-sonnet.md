severity: minor

**1. 分層與依賴方向:對齊**
- `_spec_gate_push_match` 放在 `_spec_gate_push_fill` 的正下方(`scripts/lumos:15609`、`scripts/lumos:15622`)。它是純函式,不讀檔、不呼叫別的函式,只被 `_spec_gate_push_one` 呼叫。呼叫方向跟鄰居 `_spec_gate_push_fill`、`_spec_gate_push_stale` 一樣,由上往下,沒有跨層直呼。
- 參數名 `split`、`fill` 沿用鄰居的叫法。
- `_tg_expected_cands`(`scripts/lumos:49758`)抽在 `_tg_fn_cands` 正下方,是鄰近 `_tg_*_cands` 家族(`_tg_hit_cands`、`_tg_redbase_cands`)的同型 helper。它呼叫既有的 `_tg_pairs`、`_tg_expected_changed`、`_tg_statements`,沒有新依賴。
- `prev["isig"]` 改成直接取值。我查了 `_tg_functions` 的建構處(`scripts/lumos:49009`~`49010`),`sig` 和 `isig` 同時產生。紅燈版的 `fn` 也走 `_tg_rb_chain` 這條路進 `_tg_fn_cands`(`scripts/lumos:50111`),所以直接取值跟 `prev["annot"]` 一樣安全。
- `_env_missing_why` 放在 `_ENV_MISSING_EVIDENCE` 表旁,跟 `_ran_evidence_re`、`_ran_evidence_check`(`scripts/lumos:68630`、`scripts/lumos:68636`)的「表加存取函式」形狀一致。它去色碼的寫法也跟 `_ran_evidence_check`(`scripts/lumos:68646`)相同。
- 唯一的小落差:存取函式在 `_ANSI_RE`(`scripts/lumos:68604`)之前定義,執行時能解析,只是讀起來順序反了。我當純風格,沒列。

**2. 命名與錯誤處理:大致對齊,有兩處落差**
- 新名字 `_spec_gate_push_match`、`_tg_expected_cands`、`_env_missing_why` 都符合鄰居的前綴家族。欄位 `re`、`why`、`measured` 對應 `_RAN_EVIDENCE` 的 `re`、`measured`,具名字典的形狀一致(`scripts/lumos:68562`)。
- 錯誤處理都沒有新增例外路徑,`_spec_gate_push_match` 比不到就回 `(t, None)`,交給既有的 `resolve_test_refs`。
- 落差一:表裡每格都有 `why`,但讀取端 `_spec_gate_push_one` 仍拿全域常數 `_ENV_MISSING_WHY` 去比(`scripts/lumos:16047`),判紅改弱證據那邊卻走存取函式(`scripts/lumos:14967`)。同一個原因字串有兩條讀法;之後表裡加第二種樣式、`why` 不同時,推送前會把它當成「真的紅」。見下方 finding 2。
- 落差二:`_spec_gate_push_match` 裡的冒號後綴比對。見下方 finding 1。

**3. 第二種做法:有一處判不準,標 ⚠ 交編排者**
- 這輪修補確實拿掉了上一輪的 `t.split(":", 1)`,方向正確。
- 但取而代之的 `t.endswith(":" + m)`,仍然是在讀「`平台:名字`」這個留痕格式,而且是第二處。第一處是 `_split_test_ref_ex`(`scripts/lumos:6482`),全庫的切法;寫入端則在 `_spec_gate_record`(`scripts/lumos:14213`)。
- 兩者的差別:
  - `_split_test_ref_ex` 同時認半形和全形冒號(`[:：]`);新的比對只認半形。
  - 它也不拆反引號(`_unwrap_backticks`)。
  - 它也沒有「前綴長得像平台名」(`_TEST_PLAT_LIKE_RE`)的限制,任何前綴文字都收。
- 有利的一面:它是對「現在條款的名字」這個封閉集合做查表,不是切字串,實際行為上不會切錯。因此我不敢直接判成引入了第二種做法,標 ⚠。

**Finding 1 ⚠(判不準)**
severity: minor
引句:「cand = [m for m in fill if t.endswith(":" + m)]」
佐證:file: `scripts/lumos:15622`(對照 `scripts/lumos:6482`、`scripts/lumos:14213`)

**Finding 2**
severity: minor
引句:「_ENV_MISSING_WHY = _AGP_DEVICE_MISSING["why"]」
佐證:file: `scripts/lumos:16047`(對照 `scripts/lumos:68555`、`scripts/lumos:14967`)

**測試補充(不列為不對齊)**
- 新增的 Java 案例在測試裡自建 repo(`mkvault().parent.parent / "mp4java"`)。`_rb_sg_repo`(`scripts/test_lumos.py:123532`)寫死 kotlin-junit,所以自建有理由。這個寫法在該檔其他地方很常見,例如 `_mk_spec_gate_repo(mkvault().parent.parent / "sg1")`(`scripts/test_lumos.py:73812`)。
- 含冒號測試名的新案例用了 `_mp_repo`、`_sg_plan2`、`_sg_commit`、`_mp_push`,都是既有 fixture。

不對齊共 2 條
