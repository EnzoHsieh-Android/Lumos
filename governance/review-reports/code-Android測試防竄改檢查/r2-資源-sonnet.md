severity: major

# 資源席第 2 輪審查報告(外部第三方 reviewer 視角)

**一句白話:**這輪修補確實把幾個「每條斷言都從頭重算整個函式」的地方改成一趟算完,正常大小的推送沒問題。但「比對跟輸入大小成正比」的說法還不成立:有三處到現在還是每個命中就把整行或整份檔重掃一遍(平方級),而且這些段落一旦開跑,截止時間切不斷它們。另有兩處是這輪新改的程式把原本很快的輸入變慢了。

**怎麼量的:**我用 `lumos_before`(ce5256bd)和 `lumos_after`(ea1e0b8a)在臨時 repo 實跑 `test-guard --diff HEAD~1..HEAD`,秒數是整個指令的牆鐘時間;下面寫「>100s」是我設的 100 秒上限砍掉的。
- 暫存區在 `/tmp/lumos-seat-work/code-Android測試防竄改檢查/資源-sonnet/`;生成器是 `mk_kt.py`、`mk_excl.py`、`mk_ci2.py`、`mk_longline.py`。
- 記憶體是 `ru_maxrss`。這個模組載入後底線約 355MB,下面的數字沒有扣掉它。
- 歸因欄裡「兩版」指修前加修後各跑一次。

### F1 中綴斷言「一行收一次」的 `done` 在 O(行長) 的 rfind 之後,單行大量中綴仍是平方級
severity: major
blocking: 是 — 一支在上限內的測試檔(1.9MB、單行)讓比對跑 73 秒,按平方外推 5MB 約 500 秒,超過預設 300 秒預算,截止時間切不斷
引句:「if ls in done or len(out) >= _TG_MAX_STMTS:」
file: `scripts/lumos:48533`(`ls = sb.rfind("\n", 0, m.start()) + 1` 在 48533,`done` 檢查在 48534)

失敗場景:
- 每個中綴匹配都先做 `sb.rfind("\n", 0, m.start())`,要往回掃到行首,才檢查 `ls in done`。
- 一行有 N 個 `shouldBe`,就是 N 次各掃 O(行長)。
- 斷言數到 2000 的上限後用的是 `continue` 不是 `break`,所以上限也擋不住這個迴圈。
- 比對只在每支檔和每支函式開始前看截止時間,這段在 `_tg_fn_cands` 裡面,切不斷。
- 我用截止時間 2 秒呼叫 `_lint_new_guard`:實際跑 6.6 秒、`error=None`。意思是超時後不丟錯、繼續算完,閘跑得比宣稱的久。

重現:
1. `mk_kt.py infix 100000 <repo>` 產生 `app/src/test/java/x/FooTest.kt`:一支 `@Test fun a()`,本體單行是 `"; ".join(f"x{i%7} shouldBe {i}" for i in range(N)) + "; assertEquals(V,1)"`,base 的 V=1、head 的 V=2。
2. `python3.14 run1.py after <repo>`,另一次把 `after` 換成 `before`。
3. cProfile 在 N=30000 時 `rfind` 吃 6.06 秒(總 6.7 秒)。

量測:

| N(單行中綴數) | 版本 | 秒數 |
|---|---|---|
| 30000 | 修後 | 6.7 |
| 100000(1.9MB) | 修後 | 73.4 |
| 100000(1.9MB) | 修前 | >100 |

- N=30000 到 N=100000,時間隨匹配數的平方成長;5MB 約 263k 個,外推約 500 秒。
- 計劃 S11 只釘單行 4000 個(約 0.1 秒),看不出來。

歸因:有證據的修復回歸(宣稱修了但沒修乾淨)。修前這個迴圈每個匹配都建一次行區間,修後少做了內層工作(修前 >100s,修後 73s),但 `rfind` 這個平方項還在。

### F2 `_tg_line_of` 與 `_tg_ci_head` 每個候選重掃整份檔(CI 的「一趟算完」只做了區塊旗標那一半)
severity: major
blocking: 是 — 上限內的建置檔 12000 筆候選跑 216 秒,15000 筆外推超過 300 秒,截止時間切不斷
引句:「out.append(_tg_cand(rule, path, _tg_line_of(h, line), f"{blk}\x00{line}", nth))」
file: `scripts/lumos:49038`(`_tg_line_of` 本體,每次 `text.split("\n")` 加逐行 `_tg_norm`);`scripts/lumos:48906`(`_tg_ci_head` 往回掃兄弟行)

失敗場景:
- 每個候選呼叫一次 `_tg_line_of`,它把整份檔 split 後逐行正規化到找到為止,所以 K 個不同命中等於 K × 檔案行數。
- CI 那邊 `_tg_ci_blocks` 已經是線性了,但每個命中另外呼叫的 `_tg_ci_head` 仍往回掃所有同縮排的兄弟行,還是平方級。

重現(建置檔,`mk_excl.py N <repo>`):
- base 是 N 行 `implementation(...)` 加空的 `tasks.test {}`。
- head 在 `tasks.test {}` 裡加 N 行 `filter.excludeTestsMatching("a.b.C{i}")`。

| N | 版本 | 秒數 | 備註 |
|---|---|---|---|
| 6000 | 修後 | 56.3 | cProfile:`_tg_norm` 被呼叫 5400 萬次,`_tg_line_of` 累計 106 秒 |
| 6000 | 修前 | 55.9 | |
| 12000 | 修後 | 215.8 | 4 倍,平方級 |

CI(`mk_ci2.py N <repo>`):同一個 Gradle 步驟下重複 N 行 `continue-on-error: true`。

| N | 版本 | 秒數 |
|---|---|---|
| 8000 | 修後 | 4.3 |
| 8000 | 修前 | 8.0 |
| 40000 | 修後 | 79.8 |
| 40000 | 修前 | >100 |

- S11 的 8000 個放寬鍵過關(4.3 秒),但 5 倍輸入是 18.6 倍時間。
- 這裡 8000 行是完全相同的兄弟行;`_tg_line_of` 因為第一行就找到才快,換成不同的行(建置檔那組)就慢。

歸因:CI 部分是有證據的修復回歸(宣稱「區塊一趟算完」,只修了 `_tg_ci_block_has_gradle`,`_tg_ci_head` 與 `_tg_line_of` 原樣,8000 時快一倍,40000 仍 80 秒);建置檔部分是有證據的原有漏查(兩版 56.3 對 55.9)。

### F3 `_tg_timeout_raised` 用 list 做成員測試,建置檔行數或單支函式行數平方級
severity: minor
blocking: 否 — 兩版相同的老缺口;上限內單檔約 150 秒,低於預設 300 秒預算,結果仍是對的
引句:「for line in _tg_timeout_raised(ol, nl)]」
file: `scripts/lumos:48931`(`s not in new_lines` 與 `s not in old_lines` 對 list 做成員測試)

失敗場景:
- 一支 9 萬行的 `app/build.gradle.kts` 改一行,比對跑 119 秒。
- 一支 2 萬行的測試函式本體改一行,6.2 秒,其中 4.5 秒在這個函式。
- 計劃第 261 行(`Projects/Android測試防竄改檢查_計劃.md`)寫「病態輸入不會讓判讀變成平方級」,這裡不成立。
- 計劃第 135 行寫「單一檔案跑到一半不會被打斷(單檔有 5 MB 上限)」,前提是單檔時間跟 5MB 成正比,這裡也破了。

重現:`mk_build.py 90000 <repo>` 加 `lumos_after test-guard --repo <repo> --diff HEAD~1..HEAD`。

| 版本 | 秒數 |
|---|---|
| 修後 | 119.05 |
| 修前 | 122.88 |

歸因:有證據的原有漏查(兩版相同,這輪沒碰這支)。

### F4 `_tg_hit_cands` 的 `x not in fresh` 對同一擁有者的大量命中仍是平方級
severity: minor
blocking: 否 — 比修前好一截,要有同一擁有者的上萬個跳過標記才痛
引句:「picks = (fresh + [x for x in reversed(locs) if x not in fresh])[:extra]」
file: `scripts/lumos:49225`

失敗場景:
- `fresh` 是 list,`x not in fresh` 對每個 `locs` 元素線性掃,全部都是 fresh 時也要掃到它所在的位置。
- 同一個擁有者(同名函式或檔層級)的命中越多越慢。
- 我是在一支函式裡放 N 行 `assumeTrue(true)`,量到:

| N | 版本 | 秒數 |
|---|---|---|
| 20000 | 修後 | 4.9(其中 `_tg_hit_cands` 3.3) |
| 20000 | 修前 | 22.4 |
| 60000 | 修後 | 31.3 |
| 60000 | 修前 | >100 |

- 3 倍輸入是約 8 倍時間,仍是平方級。
- S11 的 1500 個標記只要幾十毫秒。

重現:`mk_kt.py ignore 60000 <repo>`。

歸因:有證據的修復回歸(修補新寫的程式,取代修前更慢的 `_tg_line_of` 路徑,所以是淨改善)。改成 `set` 或在 `fresh` 足量時提早結束就線性了。

### F5 `_tg_class_has_body` 為了判斷有沒有大括號本體,每個沒本體的類別宣告都往後 find 到檔尾
severity: minor
blocking: 否 — 修補自己引入的回歸,慢 4 倍但上限內仍低於 30 秒
引句:「brace = stripped.find("{", j)」
file: `scripts/lumos:48451`

失敗場景:
- 接在類別名後的是 `:` 或字母(例如下一行的 `data class`),就往後找下一個 `{`,檔案裡沒有 `{` 時掃到檔尾。
- 一支測試檔放 N 個沒本體的 `data class AI(val a: Int)`,每個宣告 O(檔案大小)。
- 只在整檔大半沒有大括號時才痛;有本體的正常檔案,下一個 `{` 很近。

重現:`mk_kt.py dataclass 99000 <repo>`(檔案約 3MB)。

| 版本 | 秒數 |
|---|---|
| 修後 | 9.3 |
| 修前 | 2.1 |

- 60000 個類別時修後 4.4 秒,修前 1.5 秒。
- 5MB 外推約 15 秒。

歸因:有證據的修復回歸(`_tg_class_at` 新增的 `_tg_class_has_body` 造成)。

### F6 新加的 `_TG_TEST_NAMED_LINE` 在「開了引號沒收尾、中間有很多 test」的長行上是平方級回溯
severity: minor
blocking: 否 — 要單行幾十 KB 以上且引號沒收尾,現實輸入很少
引句:「_TG_TEST_NAMED_LINE = re.compile(」
file: `scripts/lumos:48757`

失敗場景:
- 這條正規式 `["'][^"'\n]*test[^"'\n]*["']` 在沒有收尾引號的長行上,對每個「test」字樣各回溯一次。
- 同一組改動裡 `_TG_TEST_BLOCK` 的 `named ... [^"']*test[^"']*["']` 在 `named("` 之後也是同一形狀,只是要有這個前綴。
- 單獨量正規式:`x = "` 後面接 "test" 乘 N,N=40000(160KB)搜一次 2.5 秒,N=160000 搜一次 40 秒。
- 建置檔有這樣一行時,base 與 head 各搜一次。

重現:`mk_longline.py 20000 <repo>`,建置檔 `app/build.gradle.kts` 有一行 `val s = "` + "test" × 20000(80KB)沒有收尾引號,base 與 head 都有這行。

| 版本 | 秒數 |
|---|---|
| 修後 | 20.5 |
| 修前 | 1.1 |

- 這一行再放大 4 倍(320KB)約 5 分鐘。

歸因:有證據的修復回歸(「Android 測試任務」「tasks.matching」這組新增的測試任務辨識引進)。

### F7 整次推送的測試檔內容與函式資訊全部同時駐留記憶體,峰值約為輸入的 17 倍
severity: minor
blocking: 否 — 兩版相同的設計限制;要在上限邊緣才到幾 GB
引句:「test_files.append((path, b, h, fb, fh, kt))」
file: `scripts/lumos:49109`

失敗場景:
- 每支測試檔的前後文字加兩邊所有函式的 `raw`、`mbody`、`annot`、`sig` 都留到 `_tg_test_rules` 才釋放。
- 輸入是 22 支各 4.4MB、各 9 萬個 `@Test fun` 的檔,前後兩邊合計 193MB,低於 200MB 上限。
- 峰值 RSS 約 3.3GB,耗時 82 秒;修前 3.55GB、64.8 秒。
- 密度低的真實測試檔遠不到這個倍率。

重現:`mk_many.py 22 90000 <repo>` 加 `run1.py after|before`。

歸因:有證據的原有漏查(修補沒有改變記憶體,也沒有惡化)。

## 圖譜鏡頭

- **`Systems/test-guard`:** 它記了三條跟資源有關的取捨,現況都對得上程式。
  - 「比對花的時間不算進預算,最壞整道閘是兩倍」:程式是 `tools_deadline = deadline + 比對耗時`。
  - 「off 的專案仍付比對成本」,測試 `t_lint_new_warn_off_and_relax` 有綁。
  - 「閘關掉時比對照樣在背後跑」。
  - 我實跑 `LUMOS_SKIP_LINT_NEW=1` 呼叫 `_lint_new_verdict`:status=off,仍花 6.8 秒跑完整個比對。擋下訊息建議「比對本身壞了就設這個變數再推」,但比對若是因為超時被擋,這個逃生門還要再付一次比對時間。這是節點裡寫明接受的代價(判定屬 WHY 的 `代價:`),不當缺陷,但那句建議在超時情境下省不了時間。
- **`Projects/Android測試防竄改檢查_計劃` 第 261 行**(「病態輸入不會讓判讀變成平方級」)和第 135 行(「單檔跑到一半不會被打斷」)是並列的主張,F1、F2、F3、F4 證明前者不成立。
  - 這些是 `FACT`/`KEY` 型的現況句,對不上時照程式為準,筆記要改成說明線性只涵蓋哪些路徑。
- **`Projects/新增告警閘_計劃` S10**(第 87 行)「時間預算要能真的中斷」:比對這一半與它衝突。比對只在每支檔和每支函式開始前看一次,函式內是不可中斷的。計劃兩邊各寫一種,讀者要自己對起來。
- `lumos impact` 列出的 `Systems/bound-tests-gate`(INVARIANT)等節點跟這輪資源面無直接衝突。

## 三問

1. **子程序或暫存目錄在逾時、Ctrl-C、例外時有沒有被收掉**
   - 沒看到洩漏。
   - `_lens_git` 與 `_nodehome_cat_blobs` 都是 `subprocess.run(..., timeout=...)`,逾時或例外時 Python 會殺子程序。
   - 比對本身沒有開自己的暫存目錄。
   - 新增告警閘另一半的 `.lumos/lintbase-*` 在 `finally` 做 `rmtree`,強殺的殘骸由 24 小時清掃處理,這輪沒動。
   - `_tg_retry_ok` 的 `git grep` 已帶截止時間,整次只查一次(`retry` 快取),逾時時快取成 `False` 變成候選、方向是多擋。
2. **時間預算有沒有擋錯、放錯,或讓整道閘比宣稱久**
   - **預算加倍:**最壞整道閘 = 比對時間 + 剩下的預算。比對最多用到 `deadline`,工具那半從比對結束時的「比對開始時剩下的預算」再算起。程式與計劃的「最壞兩倍」一致。
   - **漏掉的長迴圈:**截止時間只在每支檔和每支函式開始前檢查,F1、F2、F3、F4 的平方段在它們裡面,所以「最壞兩倍」不成立:單一輸入就能讓比對遠超預算(F1 在 5MB 外推約 500 秒,F2 在 15000 筆候選外推超過 300 秒),而且超時後不丟錯、繼續算完。
   - **有沒有超時後放行:**沒有。截止時間發生在檔與檔之間時丟 `TimeoutError`,記成沒跑完並擋;原子段跑完後結果照出。
   - **有沒有正常推送被擋:**沒有量到。一般大小的推送(5000 個測試函式 1.8 秒、2000 條重複斷言 1.4 秒、2000 條斷言反轉 40 個函式 9.4 秒)都遠低於預算。
3. **有沒有一次讀進整份大檔、整個推送的全部檔、整本治理帳或深層巢狀,或做二次方以上的工作**
   - **整個推送的全部檔:**有,見 F7(兩版相同,上限內約 17 倍)。
   - **二次方以上:**見 F1 到 F6。
   - **分組配對:**`list.remove` 的成本可接受。40 個函式各 2000 條相同簽名斷言、順序反轉,`remove` 累計 0.9 秒,整體 9.4 秒(修前 6.4 秒)。
   - **整本治理帳、深層巢狀:**這輪修補沒碰。
   - **字串常值正規式:**改成佔有式後,2MB 沒收尾的字串常值 0.07 秒內完成。

F1、F2 兩條主要發現都是修補宣稱「改成線性」卻仍有每個命中重掃整行或整份檔的平方項,且截止時間切不斷;F3 到 F7 為次要或原有缺口。
