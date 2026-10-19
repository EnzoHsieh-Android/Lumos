severity: major

我只讀了修補差異和 `scripts/lumos` 的現況,沒有跑 `pitfalls`。工作樹 HEAD 顯示 172db095,不是題目說的 5f8f8e48,但行內容跟修補一致。以下行號都指工作樹的 `scripts/lumos`。

上一輪三項要求的核對結果:

- **切法只剩 `_split_test_ref` 一支:** `run_doctor`、`_dispositions_split_test` 已改走它,做到了。但 `_kill_method_name` 和 `_bind_name_problem` 在它外面又手切一次(見 F1)。
- **剝註解不要第三套:** 做到了。舊的 `c-style-strings-kept` 整個拿掉,`c-style` 換成認得字串的 `_C_STRIP_RE`。
- **合法性訊息收成一個常數:** 只做了一半,有三處改用 `_TEST_NAME_RULE_ZH`,另有幾處仍是別的說法(見 F6)。

## 一、分層與依賴方向

新碼都放在原本的單檔 `scripts/lumos` 裡,各自靠近同類函式,沒有跨層直呼。

- `_split_test_ref` 在 `scripts/lumos:6090`,`_TestRefPrefixError` 在 `:6082`,緊貼 `resolve_test_refs`。呼叫端有 `run_doctor`(`:2148`)、`_dispositions_split_test`(`:55353`)、`_kill_method_name`(`:18285`),跟鄰居一樣。
- `_name_collision_reason` 在 `:54725`,由 `_run_bound_tests`(`:54779`)和 `cmd_guard_kill`(`:19820`)共用。`cmd_guard_kill` 本來就會呼叫這一帶的 `_run_cmd_expand`,方向相同。
- `_bind_name_problem`(`:18144`)被 `guard bind` 和 `guard settle` 共用,也沒問題。

分層上無不對齊。

## 二、命名與錯誤處理

命名都沿用 `_底線前綴`,擋下訊息格式「擋下:…」加 rc 2 也沿用。兩處不齊,見 F5、F6。

## 三、第二種做法

**F1:切法又出現兩處手切,沒有全走 `_split_test_ref`。**

- **`_kill_method_name`(`:18286-18288`):** 先接 `_TestRefPrefixError`,再用 `t.split(":", 1)[1]` 重切前綴。這是為了保留舊行為。
- **`_bind_name_problem`(`:18157-18159`):** 用 `re.match(r"\s*" + re.escape(plat) + r"\s*[:：]", m)` 自己判「前綴是不是明寫的」,而不是看 `_split_test_ref` 的回傳。
- **建議:** 讓 `_split_test_ref` 多回一個「是否明寫前綴」,兩處就不用自己切。
- ⚠ 保留舊行為是刻意的,是否容許由編排者裁。

severity: major
blocking: 是
引句:「rest = t.split(":", 1)[1] if ":" in t else ""   # _TestRefPrefixError 只在半形冒號時丟」
file: `scripts/lumos:18287`

**F2:`_clause_visible` 自己再掃一遍 `[test:` 欄位。**

- **既有做法:** `_slot_scan`(`scripts/lumos:4492`)的 docstring 寫明「掃描規則只有這一份」,要求別另寫第二套掃描器。
- **新碼:** `_clause_visible`(`:390`)用 `re.finditer(r"\[test\s*:", line)` 加 `_slot_value_end` 自己找欄位。
- **重複的輪子:** 後半段「把隱藏區段剔掉再接起來」的迴圈,跟 `_strip_inline_markup`(`:375-383`)幾乎一字不差。
- **建議:** 給 `_strip_inline_markup` 加一個 keep 參數,或改用 `_slot_scan`。
- ⚠ 它確實共用了 `_inline_hidden` 和 `_slot_value_end`,但 `[test:` 的掃描與保留邏輯是新寫的。

severity: major
blocking: 是
引句:「for m in re.finditer(r"\[test\s*:", line):」
file: `scripts/lumos:4492`、`scripts/lumos:8775`(後者的註解仍寫「沿用全檔唯一那兩份實作」)

**F3:`_raw_test_titles` 是第二套「列舉測試標題」的掃描器。**

- **既有做法:** 列舉標題一直走各 profile 的 `method_re`,再經 `_walk_test_files`、`_strip_test_comments`、`_test_name_of_match`(`discover_test_methods` 在 `:6431`)。
- **新碼:** 另寫硬編 `it|test|describe|testWidgets|group|xit|…` 的 `_RAW_TITLE_RE`(`:54707`)。它不看 profile,也不看使用者設的 `method_regex` 覆寫。
- **差異:** 註解說明這是為了放寬、寧可多數,而且剝註解有共用 `_strip_test_comments`,這部分沒有再長出第三套。但「列舉標題」這件事現在有兩條路。
- ⚠ 這是撞名判定特意要「看得比綁定寬」,我判不出該不該容許,交編排者。

severity: major
blocking: 否
引句:「def _raw_test_titles(root, profile):」
file: `scripts/lumos:6431`(`discover_test_methods`,對照組)

**F4:`regex_tail` 是第四種 `name_filter`,字面比對散在三處。**

- 它只在 `_name_filter_escape`(`:19470`)、`_name_filter_collisions`(`:54695`)和 profile 各用字面字串比對,沒有集中。
- 同一支 `_name_filter_escape` 裡,既有 `plain` 與 `ident` 是靠「不在 regex 集合裡」判斷,它自己又寫死 `("regex", "regex_tail")`。`_TITLED_FILTERS` 已存在卻沒被用來歸類 regex 族。
- `:5833` 的註解還寫著「name_filter=regex」,已過期。
- 結構還是對的,只是不一致。

severity: minor
blocking: 否
引句:「if name_filter not in ("regex", "regex_tail"):」
file: `scripts/lumos:19470`

**F5:`_anchor_migration_hint` 又複製了一份「走測試檔、剝註解、`method_re`、取名」的迴圈。**

- 同樣的迴圈已有 `discover_test_methods`(`:6431`)和 `_residual_test_files`(`:20384`),這是第三份。
- 結構一致,只是重複。

severity: minor
blocking: 否
引句:「for m in prof["method_re"].finditer(_strip_test_comments(txt, prof.get("comment_strip", "c-style"))):」
file: `scripts/lumos:20409`

**F6:合法性訊息常數沒收完,而且跟 `_test_name_ok` 的實際規則不一致。**

- **現況:** `_TEST_NAME_RULE_ZH` 定義在 `:18140`,離 `_test_name_ok`(`:6110`)很遠。
- **用到的地方:** 只有 `:18149` 與 `:55357`。
- **規則不一致:** `_test_name_ok` 這輪新增了 Windows 特殊字元一條,還有 200 字上限,常數的白話兩者都沒提。
- **形狀不齊:** 同一規則在 `:19815` 的 kill 路徑訊息是 `test 名不合法(拒注入): {method!r}`,在 `:18554` 又是另一種說法。

severity: minor
blocking: 否
引句:「_TEST_NAME_RULE_ZH = "不能是空的、不能以減號開頭、不能含方括號或半形逗號、不能有控制字元"」
file: `scripts/lumos:6110`

不對齊共 6 條,其中 major 3 條。
