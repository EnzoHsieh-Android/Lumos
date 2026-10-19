severity: major

審查範圍:`r3-repair-tests.patch`,版本 9591e609,對照修前 b9ff5494。實驗都在 `/tmp/lumos-seat-work/code-前端框架從vue分出/通才-sonnet/` 的複本上做,收尾已刪。我另外跑了這批新測試和相關子集(`-k kt_`、`ran_evidence`、`review_roles`、`no_multiline`),全綠。

**一句人話:** 上一輪補的測試裡,有兩支跑起來全綠,但它們聲稱守的東西其實守不住。另外還有一個新寫的函式在特定輸入上會慢到卡死,對應的「線性」測試沒涵蓋那種輸入。

1. 剝註解掃描器在「引號加反斜線」輸入上是二次方,而 `t_kt_strip_comments_linear_on_hostile_input` 沒涵蓋
severity: major
   blocking: 是
   - **位置:** `_KT_SCAN_TOKEN` 的字串分支 `"(?:\\.|[^"\\\n])*"`。這是修補新增的,測試在 `t_kt_strip_comments_linear_on_hostile_input`。
   - **輸入與路徑:** 建置檔內容是 `"\` 重複(即 `"\"\"\"…`)。每個 `"` 都是一個起點,每個起點都掃到檔尾才失敗,整體二次方。測試只試了 `/*` 重複、`"a` 重複、未閉合 `'`、`//` 重複,這些要嘛成對閉合、要嘛只有單一起點。
   - **實測:**
     - 1.6 萬字 0.82 秒,3.2 萬字 3.25 秒,6.4 萬字 13.2 秒;推算 512KB 約 14 分鐘。
     - `'\` 重複、`"`+`a\"` 重複也一樣慢。
     - 經由 `_kt_build_verdict` 同樣 3.18 秒(1.6 萬 `"\` 重複)。
   - **歸因:** 有證據的修復回歸。修前版本(find 加行註解正規式)對同一個 `"\` × 262144 的 512KB 輸入只要 0.01 秒。
   - **為何測試抓不到:** 只要把引號分支寫成二次方,現在的 4 個輸入照綠。測試名稱和 docstring 宣稱「不二次方」,證據卻缺這個形狀。
   - 引句:「    for name, txt in (("/* 重複", "/*" * 262144), ('" 重複', '"a' * 262144), ("' 未閉合", "'" + "x" * 524288), ("// 重複", "//\n" * 174762)):」

2. `t_review_roles_total_cap_stops_not_climbs` 對「總量上限」是空測試,翻不紅
severity: major
   blocking: 是
   - **宣稱:** docstring 寫「翻紅:總量上限不生效…→ backend」。
   - **實驗:** 在複本把 `max_total_bytes=_ROLE_MAX_TOTAL_BYTES` 改成 `max_total_bytes=None`(上限完全不生效),`-k total_cap_stops` 仍是 2 passed。
   - **原因:** 上限拿掉後,app 子模組建置檔(約 400 位元組,低於單檔 512KB 上限)被讀到,判成 android,`Main.kt` 角色是 None。上限生效時也是 None,兩邊結果相同。
   - **對照組也一樣:** 對照斷言本身就寫「Android 非畫面檔本來就判不出」,所以它同樣分不出有沒有上限。
   - **缺的前置斷言:** 沒有證明 app 建置檔是因為超總量才沒被讀到。測試能證明的只有「不往上找到根的 Spring」。
   - **有效的是 M2:** 把 `("" if n is not None else None)` 換成 `None` 後,同一批 `stops_not_climbs` 兩支都紅(2 passed 2 failed),所以防爬層的語意有被守到。
   - **歸因:** 新測試的缺口,沒有修前對照。這項上限是 r2 之前就有的 `_ROLE_MAX_TOTAL_BYTES`。
   - 引句:「    check("通2 對照:總量夠時讀到 Android 建置檔 → 判不出(Android 非畫面檔本來就判不出)、不是 backend", res_ok["roles"].get("app/src/Main.kt") is None, str(res_ok["roles"]))」

3. `t_no_multiline_caret_whitespace_star` 號稱全檔守衛,換別名就繞過,而且現在就有一處違規照綠
severity: major
   blocking: 是
   - **位置:** 守衛條件 `re.search(r"\bre\.M\b|re\.MULTILINE|\(\?m\)", ln)`,而且 `^\s*` 與旗標要在同一行。
   - **已存在的違規:** `scripts/lumos:6761` 是 `_re_f.search(r"^\s*FLAG:(\S+)", summ, _re_f.M)`。`import re as _re_f` 的別名讓 `\bre\.M\b` 對不上。
   - **危害:** 這條規則的 docstring 和 `scripts/lumos:30487` 的註解都說「一律不准再出現」。我在 3 萬個空行上量到 1.58 秒。我用 AST 掃整支 `scripts/lumos`,帶 `^\s` 加多行旗標的 call 只有 6761 這一處,所以這項守衛現在實際漏掉的就是它。
   - **其他繞法:** `re.compile(\n r"^\s*x",\n re.M)` 跨行、`flags=_F` 變數,也都過得了。
   - **要翻紅的改壞:** 把 `^[ \t]*` 改成 `^\s*` 且旗標換行或換別名,測試照綠。
   - **歸因:** 守衛本身是新的,6761 是原有漏查,修前就在。兩版查證:修後版 `-k no_multiline` 1 passed,6761 仍在檔裡。
   - 引句:「           if "^\\s*" in ln and (re.search(r"\bre\.M\b|re\.MULTILINE|\(\?m\)", ln))]」

4. docstring 還在宣稱的檢查被拿掉了(minor)
severity: minor
   blocking: 否
   - **`t_stack_android_only_inside_applicability`:** docstring 仍寫「不再有事後過濾的小函式」,對應的 `hasattr` 斷言被整行刪掉,docstring 沒跟著改。
   - **`t_worktree_text_shared_reader`:** docstring 寫「package.json、建置檔、.kt 檔頭都走它;不另立第二套快取」,新增的快取斷言只用 `small.txt`,沒涉及 package.json 與建置檔共用。
   - **影響:** 這兩處不會讓測試出錯,但文字宣稱了沒人驗的事。
   - 引句:「-    check("架3b:事後過濾小函式已拿掉", not hasattr(m, "_stack_drop_excluded") and not hasattr(m, "_tension_drop_excluded"), "")」

**逐項驗收**
- **剝註解:** 6 條字串感知案例正確,例如 `**/*.yml` 在前、行註解裡的 `/*`、原始字串、未閉合區塊。這不抵銷第 1 條。
- **跑過證據中段限長:** 把 `{0,200}?` 改成 `*?` 後,`t_ran_evidence_bounded_middle_fast` 紅,22.39 秒。舊的 S35 在這個改壞下仍然 0.0 秒綠,所以新測試必要,且有效。
- **逐項翻紅:** 對修前版本跑,`t_kt_deleted_file_not_counted`、`t_ran_evidence_anchored_to_summary_line`、`t_test_pat_lowercase_test_ext_only` 在修前紅。`t_eslint_config_key_must_be_object` 與 `t_kt_build_verdict_cache_bounded` 在修前因缺少 `_WORKTREE_TEXT_CACHE`、`_KT_BUILD_VERDICT_CACHE` 這兩個名稱而例外失敗,不算行為上的翻紅證據。
- **虛擬時鐘改造:** `t_review_roles_classify_loop_respects_budget` 用 `now=` 後不依賴牆鐘;各個時間門檻餘裕都大(最緊的 `t_ran_evidence_bounded_middle_fast` 是 3 秒對 0.07 秒)。
- **刪掉的斷言:** `_NODE_FLAVOR_CACHE` 與 `_kt_build_verdict` 的 `hasattr` 檢查,保護已搬到快取行為斷言。`_stack_drop_excluded` 那條的行為保護在 `t_tension_candidates_skip_android_only` 與 `kt_*` 測試。
- **重用與慣例:** 沒有可逐字引規則的違反,除第 1 到 3 條屬於「實作測試品質」第 3、4、5 點的缺口。

**未驗範圍:** 沒有拿掉 `_KT_BUILD_VERDICT_MAX` 上限的變體實驗,只確認測試的 `<=64` 斷言邏輯;沒有在 6 個 CPU 滿載下重跑時間類測試。

最嚴重:major,blocking 共 3 條(第 1、2、3 條)。
