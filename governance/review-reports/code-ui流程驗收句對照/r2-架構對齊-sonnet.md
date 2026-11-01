severity: minor

**1. 分層與依賴方向:結構對齊,只有命名有一點偏。**
- e2e 去呼叫安全證據閘的 `_secinv_names`,技術上是跨子系統。但這個專案有先例:e2e 區本來就呼叫規格閘的 `_door_keyword_hits`,也呼叫 `_esc_clean`。
  - 呼叫處:`scripts/lumos` 的 `_e2e_one_way`
  - 定義處:`_door_keyword_hits` 在 `scripts/lumos:13975`,`_esc_clean` 在 `scripts/lumos:19361`
- 修補沒有新增第二套做法,反而刪掉 e2e 自己那支一模一樣的 `_e2e_cap`,收斂回既有的 `_secinv_names`(file: `scripts/lumos:7227`)。
- 那 7 處安全證據閘呼叫者都用兩個位置參數,新增的 `width=40` 預設值不改變它們的行為(file: `scripts/lumos:7251`、`7253`、`7339`、`7341`、`7516`、`7874`、`8665`)。
- 不一致的只有名稱。e2e 區其他清單 helper 是 e2e 自己的前綴,例如 `_e2e_cov_names`(file: `scripts/lumos:42878`)。修補後 e2e 的提醒行卻直接呼叫 `_secinv_` 前綴(file: `scripts/lumos:42337`)。這是命名問題,放第二問。

**2. 命名與錯誤處理:新錯誤訊息對齊,命名有一條不對齊。**
- 新增的 `accept` 沒有 `flows` 錯誤訊息,寫法跟鄰居一致:`{where} 寫了 … 卻沒有 …:原因(修法)`,回傳 `str`,不丟例外。
  - 對照:`_e2e_case_err` 的「`{where} 列了記憶體情境,e2e 段要 stability 是 true`」(file: `scripts/lumos:40601`)
  - 同一支函式 `_e2e_case_accept_err` 內,前面的 `accept` 檢查也是回傳字串。
- 提醒行的格式沿用原本的「提醒:…」。
- 不對齊:e2e 區的 helper 用 `_e2e_*` 前綴,這次改成直呼 `_secinv_names`,讀的人會以為是安全登記專用。

severity: minor
blocking: 否
判準:命名跟鄰居不一致(`_e2e_cov_names` 與 `_e2e_cap` 是 e2e 前綴,現在改叫安全前綴 helper),但結構對,而且 e2e 呼叫跨區 helper 有先例。判不準是否該改成中性名稱,標 ⚠。
引句:「Android 端到端驗收的舊項目清單也用這一支(width 給到放得下 flow 路徑)。」

另外有一個小差異不算 finding:`_secinv_names` 不做 `_esc_clean`,但被刪掉的 `_e2e_cap` 本來也不做,所以沒有退步。

**3. 第二種做法:加選填參數與測試 helper 拆法都對齊。**
- 選填參數:`_secinv_names(keys, limit=10, width=40)` 在尾端加關鍵字風格的預設值,跟 `_nogo_words(sk, n=6)` 的「尾端帶預設的上限參數」一致(file: `scripts/lumos:14195`)。
  - e2e 提醒行的呼叫用位置參數 `(legacy, E2E_ACCEPT_SHOW, E2E_PATH_LIST_MAX)`。可讀性稍差,但不算第二種做法。
- 擋下條目的上限沿用 `E2E_ACCEPT_SHOW` 常數(file: `scripts/lumos:42223`、`68877`、`68880`)。`_cl_say_e2e_cases` 是寫死的 10,但那是既有的舊寫法,不是這次修補造成的。
- 測試 helper:`_e2ea_judge` 拆出前半 `_e2ea_steps`。
  - 拆法跟鄰居一樣:同前綴、docstring 寫明是誰的前半、`_e2ea_judge` 簽名不變。
  - 對照:`_e2e_steps` / `_e2e_judge` 在 `scripts/test_lumos.py:19690`、`19729`,`_e2ea_judge` 在 `scripts/test_lumos.py:23404`。
- 新測試 `t_android_e2e_checks_preview_and_history` 命名沿用 `t_android_e2e_*`。它用 `_e2eg_proj`、`_e2ea_rec`、`_e2eg_cl` 這些既有 helper,沒有自己再寫一套。

不對齊共 1 條,其中 major 0 條
