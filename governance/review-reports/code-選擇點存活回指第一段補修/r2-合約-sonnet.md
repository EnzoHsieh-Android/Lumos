severity: minor

審了補修差異(`r2-repair.patch`,對照 `scripts/lumos` 與 `scripts/test_lumos.py`)。程式與圖譜之間沒有破壞合約的地方,只有兩條措辭與綁定上的小問題。

我自己跑了 `-k t_choice_cov_src_pkgs_edges`(通過)與 `-k t_choice_cov_base_read`(4 passed、0 failed)。

已確認沒問題的角落:
- **共用跳過清單 `CODE_SKIP_DIRS`**:`scripts/lumos:79795` 在模組載入時用 `frozenset(CODE_SKIP_DIRS | {".gradle"})` 複製一份,定義在更前面的 6059 行,順序沒問題。其他三處讀者(4055、6733、6807)不受新程式影響。
- **`_choice_cov_read` 多一個呼叫者**:`_choice_cov_base_read` 現在先讀進記憶體(上限 8MB)再檢查 64KB。呼叫端 `scripts/lumos:29267` 本來就收 `None`,行為不變。
- **基準檔錯誤處理**:`ValueError`(含 `UnicodeDecodeError` 與 `JSONDecodeError`)與 `OverflowError` 都接到。我另外試過 6 萬層 `[` 的巢狀輸入,拋的是 `JSONDecodeError`,不會崩。
- **`--json` 純淨**:新的上限提醒只寫標準錯誤,而且因為每個平台根只掃一次,同一次只會印一行。
- **`_KillPrep._src_pkgs`**:是實例層級的快取,只在 `_measure` 用到。
- **`SdkEnvironment`**:`_CHOICE_COV_ROBO_ENV` 本來就有它,新增的測試案例對得上。
- **`[test:]` 名稱**:`t_choice_cov_rerun_edges`、`t_choice_cov_resume_old_cache`、`t_choice_cov_proj_pkgs`、`t_choice_cov_resume`、`t_choice_cov_breaker` 在 `scripts/test_lumos.py` 都存在。

severity: minor
blocking: 否
`docs/lumos-toolchain-knowledge/Issues/選擇點存活回指第一段末輪小問題第二段先修.md:15` 的議題 summary 與同檔進度節對不上。summary 寫「剩第 5、7、8 條」,進度節與「什麼條件算修好」這節寫剩第 5、7、8、9、10 條。三個月後只讀 summary 的人會漏做第 9、10 條。
引句:「2026-11-27 第一段補修已修,剩第 5、7、8 條見進度節」

severity: minor
blocking: 否
`scripts/test_lumos.py:150411` 與 `scripts/test_lumos.py:150453`,新測試 `t_choice_cov_src_pkgs_edges` 與 `t_choice_cov_base_read_rejects` 沒有被任何筆記用 `[test:]` 綁定。我在 `docs` 底下找不到它們。它們守的是這次修的 `_choice_cov_src_pkgs` 與 `_choice_cov_base_read` 兩條行為,綁定列表只有 `t_choice_cov_proj_pkgs` 與 `t_choice_cov_resume_old_cache`。測試在,但哪天被改掉或刪掉時,圖譜沒有任何一條會連到它。
引句:「第一段放行後實測:專案用 Robolectric 時每支測試的覆蓋資料都有」

總結:最高等級是 minor
