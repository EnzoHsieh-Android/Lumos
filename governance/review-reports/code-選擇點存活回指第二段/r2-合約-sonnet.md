severity: major

**發現 1:新寫的 REVISIT 一寫下就已成立,推送閘會擋**

severity: major
blocking: 是

位置:`docs/lumos-toolchain-knowledge/Systems/規格閘.md:119`,這是補修差異新增的 REVISIT 行。

引句:「REVISIT:[when-symbol:scripts/lumos::_CHOICE_COV_ANALYZE][by:2027-03-01] 改了覆蓋分析的 Groovy 初始化腳本(_CHOICE_COV_ANALYZE)時」

- **失敗場景:** `_CHOICE_COV_ANALYZE` 是 `scripts/lumos:80087` 的模組層指派,早就存在。`[when-symbol:…]` 的意思是「那個符號出現就成立」,不是「那個符號被改了才成立」。所以這行寫下的當下條件就已成立,推送時漂移檢查會擋(`_note_shape_negation_format` 的說明也寫明「推送時條件已經成立,這次推送會被漂移檢查擋下」)。
- **最小重現:** 在 `/Users/enzo/harness/lumos-reach2` 跑 `python3.14 scripts/lumos drift scan`。輸出第 3 行點名 `Systems/規格閘.md:119`,第 5 行寫「寫下時就已成立:這組條件從 ac5203b(2026-11-27)起連續出現在這篇」。這個 ac5203b 就是本輪補修提交。
- **想表達的條件也寫不出來:** 他想守的是「改了腳本時」,但這個語法沒有「被改動」這種條件。`when-symbol` 判的是定義存在與否。
- **建議:** 改成不會生來成立的形狀,例如帶日期的 `REVISIT:2027-03-01 …` 加手動驗法。或者把它改寫成 PITFALL/RULE 一類的現況說明,綁 `[test:t_choice_cov_groovy_dep]`,再配一個真的會翻動的條件,例如 `when-test` 指向一個新增的測試。
- **為什麼擋:** 上一輪補修的是「規格閘補 REVISIT when-symbol」。這個修補自己引入了新的推送擋點,就是你要我找的「修補自己引入的問題」。

**其餘逐項檢查結果,都沒有新問題**

- **`_CHOICE_COMPILE_UNVERIFIED` 的讀者:** 共 `scripts/lumos:29458`、`29474`、`29509`、`29519` 四處,另在 `29556` 回傳。`apply_compile` 只有 `one_batch`(兩處)與 `probe`(兩處)呼叫,都已先判這個哨兵值再解包,沒有漏掉的讀者。
- **三個既有呼叫端的行為:** `_choice_compile_cmd`、`_choice_cov_analyze_cmd`、`_choice_cov_exec_path` 改成共用 `_choice_unit_variant` 與 `_choice_task_swap`,字面邏輯與原本相同。
- **`_platform_compile_flag` 預設改成 `_choice_compile_cmd(run_cmd) is not None`:** 這是有意的行為變動。原本只要出現 `:test…UnitTest` 字樣預設就是 true;現在非合併形狀會變 false。這兩處筆記已同步:`Systems/規格閘.md` 的 WHY 與函式說明。
- **`units()` 新增的 `_kill_old_issue`、`_kill_new_issue` 檢查:** 與 `_kill_merge_apply` 用同一組判法。`.git` 路徑段的排除也成立。
- **`_choice_cov_pkg_of` 改用 `_strip_c_comments(keep_length=True, kotlin=True)`:** 簽名存在,參數都有。
- **`[test:]` 名稱:** 新增筆記引用的 `t_choice_exhausted_status_readers`、`t_choice_cov_pkg_comments`、`t_choice_compile_probe`、`t_choice_cov_audit`、`t_choice_compile_batch`、`t_choice_cov_groovy_dep` 都存在於 `scripts/test_lumos.py`。
- **筆記與程式一致:** `Systems/guard-kill.md` 的合批編譯 WHY、`Systems/規格閘.md` 的探針與抽查 WHY,與程式行為一致。

總結:最高等級是 major
