severity: minor

**1. 分層與依賴方向**

- 這一輪的修補沒有新增跨層直呼。
  - `_platform_compile_flag` 改呼叫 `_choice_compile_cmd`,與實際做不做合批編譯同源,符合上一輪的指示。
  - `_choice_unit_variant`、`_choice_task_swap` 由 `_choice_compile_cmd` 和 `_choice_cov_analyze_cmd` 共用,取模組變體的邏輯回到一份。
- `_KillCompile.units()` 補了 `_kill_old_issue` 和 `_kill_new_issue`,與 `_kill_merge_apply`(`scripts/lumos:30003`)及序列路徑(`scripts/lumos:28624`、`scripts/lumos:28633`)對齊。
- `_choice_cov_pkg_of` 改用 `_strip_c_comments(text, keep_length=True, kotlin=True)`,與 `scripts/lumos:42214` 的呼叫寫法一致,是對齊。
- `units()` 新增了 `.git` 底下的檔不收這道檢查,只做在 `_KillCompile` 裡。
  - 既有同類路徑圍欄只有 `startswith(wt_real + os.sep)`:`_kill_merge_apply` 在 `scripts/lumos:30006`,序列路徑在 `scripts/lumos:28608` 附近。
  - 全庫對 `.git` 底下的判法另有一種寫法,見 `scripts/lumos:14933`。
  - 這道防護沒有進共用判法,所以合批編譯擋 `.git`,實際跑測試的合併與序列路徑不擋。結構上仍是同一層,所以只算 minor。

severity: minor
blocking: 否
引句:「if not target.startswith(self.c.wt_real + os.sep) or ".git" in Path(os.path.relpath(target, self.c.wt_real)).parts:」

**2. 命名與錯誤處理**

- 哨兵常數 `_CHOICE_COMPILE_UNVERIFIED = ("unverified",)` 的寫法與專案不同。
  - 既有的 sentinel 是 `scripts/lumos:23945` 的 `_RETRO_NO_BAD = object()`,註解寫「哨兵」。
  - 新常數是一個和真實回傳值(`(rc, 輸出, 逾時)`)同形的 tuple,靠 `is` 比較區分。
  - 若有呼叫端漏了 `is` 檢查就直接下標,會拿到字串而不是報錯。
  - 命名前綴 `_CHOICE_COMPILE_` 與鄰近的 `_CHOICE_*` 常數一致。

severity: minor
blocking: 否
引句:「_CHOICE_COMPILE_UNVERIFIED = ("unverified",)   # apply_compile 這次沒驗」

- 新測試的 `_sh_quote_t` 是新寫的小包裝,內部 `import shlex`,測試檔本來就有 `_shlex` 的別名(`scripts/test_lumos.py:28028`),也有既有的 quote 用法。
  - 其他同族測試輔助以 `_ck` 或 `_ckc` 為前綴,新的 `_ckcc_unit` 前綴一致。
  - 造樣板用 `tempfile.mkdtemp(prefix="gctl-ckcc-")` 再 `_ck_cleanup(tmp)`,與既有 `gctl-ck-` 的寫法一致。

severity: minor
blocking: 否
引句:「def _sh_quote_t(x):」

- `exhausted` 狀態的錯誤表在 `_situation_rule_point_target` 與 `_choice_waive_target` 各寫一份字典與文案,措辭不同(「沒有可用壞法(候選都編不過)」與「沒有可用壞法(候選都編不過,不擋)」)。原本兩處也各自寫過,不算新增的不一致。

**3. 第二種做法**

- 未發現新的第二種做法。
  - 判斷 Android 單元測試的 `_PLATFORM_ANDROID_UNIT_RE` 已刪除,改成單一來源。
  - 剝註解改回全庫的 `_strip_c_comments`,`_CHOICE_COV_BLOCK_COMMENT_RE` 已刪。
  - 合批編譯的檔案收集仍是 `_KillCompile` 自己的一份,但它已補齊 `_kill_merge_apply` 的兩道檢查。
- 還原路徑是第三份,上一輪已放行延後,這輪不重複計。

不對齊共 3 條,其中 major 0 條
