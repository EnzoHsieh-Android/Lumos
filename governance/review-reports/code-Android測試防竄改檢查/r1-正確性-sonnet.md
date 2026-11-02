severity: major

以下每條重現都是我在 `/Users/enzo/harness/lumos-tq-android`(HEAD ce5256bdd)用建好的暫存 git repo 實跑的結果。暫存目錄已刪。

### F1 整檔重新縮排或換行尾改變,會讓沒動過的測試被列成 `tq/no-assertion`
severity: major
blocking: 是 — 計劃 S5 寫「本體沒變的舊測試不列」,程式卻照樣列,而且 `Systems/test-guard` 的 WHY 說重新縮排不該讓判定變動,兩邊都對不上。
引句:「if prev is not None and prev["sig"] == f["sig"] and prev["annot"] == f["annot"]:」
file: `scripts/lumos:_tg_fn_cands`(註記欄 `annot` 在 `_tg_functions` 裡取 `"\n".join(lines[s - 1:decl])`)
- 失敗場景:`annot` 是帶縮排、`\r`、註解的原文行,拿去逐字比。`sig` 已經去空白,但 `annot` 沒有。
- 觸發輸入:`@Test` 單獨一行、再下一行寫 `fun a() { checkIt(1) }`,這支測試靠自訂輔助函式、本身沒有斷言字。
- 走到哪:整檔縮排改了(4 格改 2 格)、CRLF 轉 LF、或 `@Test` 與 `fun` 之間改了一行註解。`annot` 不等,於是 `_tg_fn_cands` 不提早 return,往下跑 `_tg_has_assertion`,結果誤列 `tq/no-assertion`。
- 重現:
  - 範圍從 `kt(helper)` 到縮排減半後的同一份,輸出 `[tq/no-assertion app/src/test/java/x/CalcTest.kt 4]`。
  - CRLF 轉 LF 和 LF 轉 CRLF 也各列一條。
  - 直接呼叫 `_tg_fn_cands("p","CalcTest.a",head_fn,base_fn,False)`,回 `['tq/no-assertion']`。
- 測試為什麼沒抓到:`t_tq_guard_no_assertion` 只測「沒碰過的舊測試」,沒測縮排或換行尾。`t_tq_guard_skip_added` 的縮排案例只檢查 `skip-added`。

### F2 同一條斷言重複出現時,預期值被改會整個漏掉
severity: major
blocking: 是 — S4 要求「一個斷言的預期值被改」都要列,這個輸入列不出來,守衛的主要用途就落空。
引句:「for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, old, new, autojunk=False).get_opcodes():」
file: `scripts/lumos:_tg_pairs`
- 失敗場景:`SequenceMatcher` 會把重複的相同行對成「中間插入一條、結尾刪一條」,不產生 `replace`。`_tg_pairs` 只看 `replace`,所以沒有一對進得了 `_tg_expected_changed`。斷言數與強斷言數也沒變,`tq/assert-weakened` 一樣不亮。
- 重現:函式內每個斷言前夾一行 `cart.refresh()`,斷言為 `assertEquals(v, cart.total())`,把預期值列表改一遍:

| 改前 | 改後 | 結果 |
|---|---|---|
| `[88,88,88]` | `[88,90,88]` | 無候選 |
| `[88,88,88]` | `[90,88,88]` | 無候選 |
| `[88,88,88,88]` | `[88,90,90,88]` | 無候選 |
| `[88,88]` | `[88,90]` | 有 `tq/expected-changed` |
| `[88,88,88]` | `[88,88,90]` | 有 `tq/expected-changed` |
| `[88,88,88]` | `[90,90,90]` | 3 條 |

  - 直接呼叫:`m._tg_pairs(["assertEquals(88, t)"]*3, ["assertEquals(88, t)","assertEquals(90, t)","assertEquals(88, t)"])` 回 `[]`。
  - 1999 條一樣的 `assertEquals(1, f())`,把奇數位置改成 2(約 999 處預期值被改):候選為 0 條。

### F3 註記跟 `fun` 寫在同一行時,`expected =` 規則和 `no-assertion` 的「有斷言」判斷都失效
severity: major
blocking: 是 — S1 的「給既有測試加 `expected =`」和 S5 的「`@Test(expected = …)` 不列」都沒說只限註記單獨一行。
引句:「"annot": "\n".join(lines[s - 1:decl]),」
file: `scripts/lumos:_tg_functions`
- 失敗場景:`decl` 就是宣告所在那一行,所以註記與 `fun` 同一行時 `lines[s-1:decl]` 是空的。`_TG_EXPECTED_ANN.search(f["annot"])` 因此永遠看不到同行的 `expected =`。
- 重現一(假陽性):新增 `@Test(expected = IllegalStateException::class) fun c() { boom() }`,列出 `tq/no-assertion`。Java 的 `@Test(expected = X.class) public void c() { boom(); }` 一樣。
- 重現二(漏判):既有 `@Test fun b() { boom() }` 改成 `@Test(expected = IllegalStateException::class) fun b() { boom() }`,無候選。註記單獨一行的版本會正確列 `tq/skip-added`。
- 為什麼要緊:把紅測試改成「預期丟例外」是讓測試變綠最省事的一種,只要換成單行寫法就繞過。

### F4 重複的 `tq/expected-changed` 拿到同一個指紋
severity: minor
blocking: 否 — 只是放行粒度變粗、擋下訊息重複,不會做出錯誤判定。
引句:「out += [_tg_cand("tq/expected-changed", path, f["start"], f"{k}\x00{c}") for a, c in _tg_pairs(so, sn) if _tg_expected_changed(a, c, kt)]」
file: `scripts/lumos:_tg_fn_cands`
- 失敗場景:這裡沒傳 `nth`,`_tg_cand` 預設 `nth=1`。計劃寫的是「同一個身分第二次出現,指紋不同,放行第一個不會順帶放掉第二個」。
- 重現:同一個函式裡兩次 `assertEquals(88, total)` 都改成 90,輸出兩條,指紋都是 `b82f012a512248d4`。

### F5 `tq/skip-added` 候選記到錯的檔,指紋也跟著不穩
severity: minor
blocking: 否 — 候選照樣擋下,但擋下訊息和放行指令的檔名錯,放行紀錄對不上指紋。
引句:「path, ln = next(((p, _tg_line_of(h, line)) for p, _b, h, _fb, _fh, _kt in test_files if _tg_line_of(h, line)),」
file: `scripts/lumos:_tg_hit_cands`
- 失敗場景:跳過標記的次數是跨全部測試檔一起算,但候選記在「第一支其改動後內容含這行文字的檔」,不是新增那一處所在的檔。
- 重現:`ATest.kt` 原本就有類別上的 `@Config(sdk = [28])` 並新加一支測試;新增 `BTest.kt` 也帶同一行。輸出 `tq/skip-added app/src/test/java/x/ATest.kt 3`,新增的明明是 `BTest.kt`。
- 連帶:指紋含檔案,字母序更前面的檔再出現同一行,指紋就換,先前的放行失效。

### F6 設成 warn 時,比對工具出錯完全看不到
severity: minor
blocking: 否 — warn 本來就不擋,但「比對沒跑完」的事實被吞掉。
引句:「print(f"  提醒:新增告警閘只報不擋,有 {len(_lv.get('new') or [])} 條({'、'.join(_bits)})")」
file: `scripts/lumos:_cl_say_lint_ok`
- 失敗場景:`gate=warn`,`_tg_analyze` 丟 `RuntimeError`。`_lint_new_guard` 把它記成 `undone[kind=guard]`,但 warn 路徑只印小結,不印這條。
- 重現:輸出 `提醒:新增告警閘只報不擋,有 0 條()`,括號是空的,沒有任何一行說比對崩了。治理帳也沒記。

### F7 重複斷言多時 `_tg_pairs` 耗時暴增,且超過截止時間的檢查只在迴圈開頭
severity: minor
blocking: 否 — 要接近 2000 條重複斷言的函式才明顯。
引句:「for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, old, new, autojunk=False).get_opcodes():」
file: `scripts/lumos:_tg_pairs`、`_tg_test_rules`
- 失敗場景:`autojunk=False` 加上大量相同元素,耗時近似立方。
- 實測(單一函式,全部是 `assertEquals(1, f())`):

| 長度 | 改動處數 | 耗時 |
|---|---|---|
| 1999 | 10 | 1.2 秒 |
| 1999 | 100 | 10.9 秒 |
| 1999 | 300 | 32 秒 |
| 1000 | 隔一條改一條 | 7.9 秒 |
| 1999 | 隔一條改一條 | 62 秒 |

- 為什麼要緊:`_tg_test_rules` 在逐檔迴圈之後跑,沒有任何截止時間檢查。幾支這種函式就會超過新增告警閘的 300 秒預算而不被中斷。計劃寫的「判讀跟輸入大小成正比」不成立。

### F8 合法 Kotlin 原始字串以引號結尾,會讓整支檔變 `tq/unparsable`
severity: minor
blocking: 否 — 可放行,而且是 `_C_STRIP_PAT` 共用的既有限制。
引句:「ok = all(stripped.count(o) == stripped.count(c) for o, c in ("()", "{}")) and "\0" not in text」
file: `scripts/lumos:_tg_functions`(剝字串的 `_C_STRIP_PAT:6756`)
- 失敗場景:`parse(""""k":"v"""")`(內容的最後一個字元是引號)是合法 Kotlin。剝字串的樣式在第一個 `"""` 就收尾,剩下的 `"` 吃掉後面的 `)`,括號配不平。
- 重現:含這一行加另一支測試 `b`,`_tg_functions` 回 `ok=False`,而且函式表只剩 `a`,`b` 也丟了。比對輸出 `tq/unparsable`。
- 實際影響:我掃本機 171 支真實 `*Test.kt`,有 2 支中招,包括 `Citrus_KDS-e2e` 的 `OrderBuzzerTest.kt`。放行後這支檔的函式級規則整個失效,要等人看。

### F9 類別路徑追蹤:`::class` 吃掉換行、獨立宣告的類別會附到下一個大括號
severity: minor
blocking: 否 — 兩邊本體相同時靠簽名配對能補回來,只有簽名也變時才變成誤列。
引句:「for m in re.finditer(r"\n|\{|\}|\b(?:class|object|interface)\s+(?:`[^`\n]*`|[A-Za-z_]\w*)", stripped):」
file: `scripts/lumos:_tg_class_at`
- 失敗場景一:`val k = Foo::class` 加換行,`class\s+` 把換行連同下一個識別字一起吞掉,後面的行號整體差一。
  - 重現:兩個類別各有一支 `a`,函式鍵是 `['A.a','B.a']`;在 A 裡加一行 `val k = Foo::class` 後變 `['a','a#2']`。
- 失敗場景二:`data class Row(val a: Int)` 沒有本體,`pending` 留著,下一個 `{` 被當成它的本體。
  - 重現:`@Test fun t1() {` 的鍵變成 `FooTest.Row.t1`,拿掉那行宣告就回到 `FooTest.t1`。

## 圖譜鏡頭
- `Systems/test-guard`:有三處宣稱跟程式對不上。
  - 「整檔重新縮排不該讓放行失效」那條 WHY:指紋本身不變,但 F1 會讓縮排變動冒出新候選。
  - 「候選指紋用…第幾個」:`tq/expected-changed` 沒帶序號(F4)。
  - 「候選記在那一行出現的那支檔」:實際記在第一支含該文字的檔(F5)。
- `Systems/pitfalls-lint-adapter`:新增的例外條文(兩種指紋算法並存、off 時比對照樣在背後跑)跟程式一致。`gate=off` 與 `LUMOS_SKIP_LINT_NEW` 都走 `_lint_new_off`,有候選才記帳。放行檔壞掉而有候選時擋下、不記自動放行,我實跑過是對的。不破壞既有合約,但檢查工具那一半在 `waiver_err` 為真時會把 `autopass` 清掉,是新行為。
- `Systems/pitfalls-code-loop`:「判定函式不寫帳、由 `_codeloop_lint_new_step` 寫」成立,我實測 `no-baseline` 帳是那一步寫的。`events` 的合併與擋下訊息拆分沒有破壞既有行為。warn 小結的括號可能是空字串(F6)。
- `Systems/room-guard`:`_rg_split_args` 預設行為不變;Room 的 48 支 `room_dao` 測試全綠。`_rg_method_end` 的運算式本體擴充確實讓範圍變大,但只會多要求測試,符合節點寫的代價。
- `Systems/測試假綠形態`:新增測試大多有前置斷言,但 F1(縮排)、F2(重複斷言)、F3(單行註記)三個輸入沒有對應測試,正是這類「樣本沒走到被測分支」的缺口。
- `Systems/bound-tests-gate`:這次綁定的測試名稱都存在,`-k tq_guard` 114 支全綠。綁定機制本身不受影響。
- 配套指紋:`test_quality_semgrep.py` 的 sha256 與 `_TEST_QUALITY_BUNDLE_DIGESTS` 一致。
- 計劃條款:S1、S4、S5 在上述輸入下與程式不符(F1 到 F3)。S12 到 S16 的閘整合行為我實跑都符合,包括放寬偵測三種情況、放行檔壞掉的擋法、off 時背後跑比對的帳、空樹起點只印不擋。

整份最嚴重等級是 major,blocking 共 3 條(F1、F2、F3),minor 共 6 條。
