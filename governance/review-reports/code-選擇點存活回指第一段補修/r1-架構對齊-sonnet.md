severity: major

**問 1 分層與依賴方向:對齊。**
- `_KillPrep._measure` 呼叫模組層的 `_choice_cov_src_pkgs`,`_KillCovBase.cached` 寫 `self.c.baselines`。這兩條都跟既有路徑同一層、同一方向。`_kill_measure_singles` 本來就寫同一份 `c.baselines`,見 `scripts/lumos:29581`。
- `cached()` 用 `_run_cmd_expand(self.c.run_cmd, ..., name_filter=self.nf)` 組基準鍵,跟讀端 `scripts/lumos:29674` 是同一個組法。
- `_choice_cov_base_path` 和 `_choice_cov_base_read` 放在 `_choice_cov_*` 這一族,存檔走 `_write_bytes_atomic`(`scripts/lumos:32315`),也跟 `store` 既有寫法一致。
- 沒有跨層直呼,這問沒有不對齊。

**問 2 命名與錯誤處理:大致對齊,有一條小差異(放在問 3 的第三條)。**
- 命名跟 `_choice_cov_proj_hits`、`_choice_cov_read`、`_choice_merge_*` 同一套。
- 讀不到就略過或回 None 的處理,跟鄰居 `_choice_cov_read`(`scripts/lumos:79975`)一致。
- 新程式直接用模組層的 `json`(`scripts/lumos:67789` 有 import),而鄰居 `_choice_cov_parse` 是函式內 `import json`。這只算風格,不列。
- 測試端 `_ckc_cb_stub` 改走真建構子、`_ckc_repo` 加 `extra` 參數、`check` 和 `_ck_cleanup` 的用法,都跟 `_ckc_repo`、`_ck_run` 既有寫法一致。

**問 3 第二種做法:走訪是第二套(major),XML 解析與 JSON 小檔讀取各有一個 minor。**

1. 走訪原始碼樹另立了跳過清單。專案已有共用的 `CODE_SKIP_DIRS`(`scripts/lumos:6059`),三處 `os.walk` 都用它:`scripts/lumos:4055`、`scripts/lumos:6733`、`scripts/lumos:6807`。`_walk_test_files`(`scripts/lumos:6795` 起)的註解還明講「走檔只有這一份……不留兩套」。新的 `_choice_cov_src_pkgs` 自己寫一份 `os.walk`,配自己的 `_CHOICE_COV_SRC_SKIP`。
   - 這份清單跟 `CODE_SKIP_DIRS` 重疊在 build、.git、.idea、node_modules,卻多了 `.gradle`,少了 bin、obj、dist、vendor、`__pycache__`。哪天改共用清單,這份不會跟著變。
   - 符號連結的處理也是自己的:用 `os.path.islink` 逐資料夾判。同類的 `scripts/lumos:42394` 是明寫 `followlinks=False`。
   - 它要多排除測試目錄,所以不能直接用 `CODE_SKIP_DIRS`,但可以 `CODE_SKIP_DIRS | {...}` 疊上去。這是我的判斷,⚠ 交編排者:要不要把「平台主程式檔走訪」併進共用那份,是設計取捨。
   - 重判結果:維持 major(引入第二套走訪與跳過清單,且專案明文有單一走檔規則),所以 blocking 改成「是」。

severity: major
blocking: 是
引句:「_CHOICE_COV_SRC_SKIP = frozenset(("build", ".gradle", ".git", ".idea", "node_modules", "test", "androidTest", "testFixtures"))」

2. 空殼結果檔另用 `ElementTree.fromstring` 整棵樹重剖。既有讀法是 `_secev_junit_facts` 走 `test_quality.junit`(`scripts/test_quality.py:250`),那是邊讀邊數深度、遇 DTD 拒收的串流剖析。`_choice_merge_ghost_suite` 又照同一個檔重剖一次,還把 `suite_error` 的判準(tests、failures、errors 為 0,沒有 error 或 failure 元素)自己再寫了一份。
   - 因為 `zero_cases` 是在 `tq.junit` 讀完整份之後才丟的,所以深度和 DTD 都已被前面擋過,安全上站得住。但這是第二套 JUnit 解讀,日後 `test_quality` 改了判準會分岔。

severity: minor
blocking: 否
引句:「root = _ET.fromstring(raw)」

3. 讀快取旁存的基準檔(小 JSON),大小上限與讀檔步驟另寫一套。同一族的 `_choice_cov_read`(`scripts/lumos:79975`)已經有「不是一般檔、超過上限、讀不到就回 None」的有界讀法,`_choice_cov_parse` 也是拿它的位元組再解 JSON。新的 `_choice_cov_base_read` 自己再做一次 isfile、getsize、open、`json.load`,上限寫成魔術數 65536,沒有像鄰居那樣用具名常數(`_CHOICE_COV_OUT_MAX`)。
   - 可以改成 `_choice_cov_read` 的位元組加 `json.loads`,上限另取具名常數。

severity: minor
blocking: 否
引句:「if not os.path.isfile(p) or os.path.getsize(p) > 65536:」

不對齊共 3 條,其中 major 1 條
