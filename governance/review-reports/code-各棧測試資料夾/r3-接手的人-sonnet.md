severity: major

### F1 Gradle/`src` 測試資料夾分支的「同副檔名」錨沒有限定回該棧自己的副檔名,任何語言的檔只要巧合落在 `src/androidTest`(或 `src/test`)且同模組 `src/main` 有同副檔名的檔,仍會被判成免家
severity: major
blocking: 是 — 直接違反這支函式自己文件宣稱的「過嚴、不漏」保證,讓程式檔悄悄逃過「每支檔有家」的提交前/推送前擋,跟第二輪邊界席判 major/blocking 的同一顆洞(D3)沒有真正關掉,只是縮小了觸發面。

1. `_nodehome_stack_test_dirs` 對 `dir_mode=="suffix"` 那半有把該棧的 `exts` 存進 `sufs`(`sufs.setdefault(d, set()).update(prof.get("exts", ()))`),但對 `rglob_under=="src"` 那半只收資料夾名、完全不收副檔名(`under_src |= names`)——這個不對稱是洞的根:任何未來加進 `TEST_PROFILES` 的 `rglob_under=="src"` 棧都會自動繼承同一個缺口,不是 kotlin 專屬。
2. `_nodehome_in_stack_test_dir` 第二段只驗「緊接在 src 下一層」+「同模組 `src/main` 有同副檔名的檔」,沒有再驗那個副檔名是不是屬於貢獻 `androidTest`/`test` 這兩個名字的棧(.kt/.java)——只要巧合命中,Go、Python、Shell 等任何語言都會被放行。
3. 第三輪新增的反例(`tools/src/androidTest/backdoor.py`、`backend/src/internal/androidTest/handler.go`)之所以能「照舊要家」,是因為它們的模組**沒有**同副檔名的 `src/main` 檔或深度不緊鄰——測試從沒真的造出「緊鄰 src + 同副檔名 src/main 都成立」這個組合,所以洞沒被釘住;逃逸帳與 Issue 筆記「反例都釘在測試裡」這句話對這個組合不成立。
4. 在 `/tmp` 隔離副本(未改動 repo 任何檔)以本輪 `scripts/lumos` in-process 載入重現,兩個獨立案例都成立:

```
python3 -c "
import importlib.machinery, importlib.util
l = importlib.machinery.SourceFileLoader('m', 'scripts/lumos')
s = importlib.util.spec_from_loader('m', l)
m = importlib.util.module_from_spec(s); l.exec_module(m)

paths = ['backend/src/main/handler2.go', 'backend/src/test/handler.go']
lay = m._nodehome_layout(paths)
print('Go 業務檔 backend/src/test/handler.go:',
      'testmap=', m._testmap_is_test('backend/src/test/handler.go'),
      'nodehome=', m._nodehome_is_test('backend/src/test/handler.go', lay))

paths2 = ['mod/src/main/build.sh', 'mod/src/androidTest/setup.sh']
lay2 = m._nodehome_layout(paths2)
print('Shell 腳本 mod/src/androidTest/setup.sh:',
      'nodehome=', m._nodehome_is_test('mod/src/androidTest/setup.sh', lay2))
"
```
輸出(已實跑):
```
Go 業務檔 backend/src/test/handler.go: testmap= False nodehome= True
Shell 腳本 mod/src/androidTest/setup.sh: nodehome= True
```
`_testmap_is_test` 單獨判是 `False`(.go/.sh 不在測試地圖清單裡),但整條 `_nodehome_is_test` 判 `True`——這兩支業務檔可以新增進 repo,「每支檔有家」提交前/推送前閘永遠不會要求它們有家。

5. 同一支 `/tmp` 副本裡跑既有測試 `python3 scripts/test_lumos.py -k stack_test_dirs`,14 個斷言全綠——測試綠不代表這個組合被擋住,只是沒人造過這個組合的 fixture。

引句:「elif prof.get("rglob_under") == "src":」

file: `scripts/lumos:17796-17797` `_nodehome_stack_test_dirs` 的 `rglob_under=="src"` 分支只做 `under_src |= names`,沒有把 `prof.get("exts", ())` 併進去,跟同函式 suffix 分支的寫法不對稱
file: `scripts/lumos:17851` `_nodehome_in_stack_test_dir` 的 Gradle 判準 `ext in main_exts.get(...)` 只比對「跟 src/main 同副檔名」,沒有再比對 `ext` 是不是屬於貢獻 `test`/`androidTest` 這兩個名字的棧
file: `scripts/test_lumos.py:36763` `④f` 這條斷言只造了「緊鄰 src 但 src/main 沒有同副檔名檔」的反例,沒有造「緊鄰 src 且 src/main 剛好有同副檔名檔」的反例,沒測到這個組合
file: `docs/lumos-toolchain-knowledge/Issues/各棧測試資料夾被當成要家.md:18` 「沒涵蓋」段只寫了 suffix 分支(Xcode/.NET)的「過鬆」殘留(Payment/PaymentTests),沒提到 Gradle/`src` 分支這個更寬的版本(不限語言)

## 逐項判定

- **風險掃描:`_NODEHOME_STACK_TEST_DIRS` 模組層級延遲快取無鎖**:誤報。`/tmp` 副本全檔搜尋 `threading`/`multiprocessing`/`concurrent.futures` 零命中,`lumos` 是單行程 CLI;`scripts/test_lumos.py` 裡所有讀 `TEST_PROFILES` 的地方都是 `dict(...)` 拷貝或原地比對,沒有任何測試就地改寫全域 `TEST_PROFILES`,不會有跨測試污染窗口;寫法跟同檔既有的 `_TESTMAP_DIR_RE = None # lazy`、`_STACK_GUESS_CACHE` 是同一款既有慣例,不是新引入的風險面。
- **第二輪 D1(副檔名沒轉小寫)**:已折。`_nodehome_in_stack_test_dir` 改用 `_testmap_ext(path)`(內建 `.lower()`),測試 ④h 用 `Fixture.SWIFT` 釘住,已在 `/tmp` 副本實跑確認回 `True`。
- **第二輪 D2(頂層資料夾清單自己另算一份、沒濾點開頭)**:已折。抽成共用的 `_nodehome_top_dirs`,測試 ④i 用 `.github/w/ci.yml` 釘住只留 `{"a"}`。
- **第二輪 D3(Gradle 分支不看副檔名、不看深度)**:部分折,見 F1——「緊接 src 下一層」與「有同副檔名 src/main 檔」兩道錨都補了,但沒有把副檔名收斂回該棧自己的清單,同一類洞縮小後仍在。
- **第二輪 D4(同名頂層資料夾只看名字存在,不看內容)**:已折。改成 `ext in top_exts.get(base, ())`,測試 ④e 用 `scriptsTests/inject.cs`(旁邊 `scripts/` 只有 `.py`)釘住仍要家。
- **第二輪 D5(兩道錨仍可能被命名巧合同時滿足,天花板沒寫進沒涵蓋)**:已折。Issue 筆記「沒涵蓋」段落新增了 `Payment/PaymentTests` 那句,並帶 `REVISIT:2026-10-12`;但如 F1 所述,這句只涵蓋 suffix 分支,沒有涵蓋 Gradle 分支的同類殘留。
- **第二輪 D6(裸名 `UITests/`、`IntegrationTests/` 被新錨誤擋要家)**:已折。`base` 為空字串時直接判為測試資料夾,測試 ④g 與 `bare` 兩個案例都釘住免家,已在 `/tmp` 副本實跑確認。
- **逃逸帳 `ESC-18f03ede`**:欄位齊全(`ts/token/loop/stage/severity/desc`),跟同檔前兩筆同形狀;`severity: major` 在值域內;`desc` 對症狀(平板 POS 截圖輔助檔、Android 儀器測試 Kotlin 檔被擋)與根因(測試地圖只認 `test`/`tests` 這幾個資料夾名,`<App>Tests`/`src/androidTest` 沒接起來)的描述跟 diff 實際行為一致,判正確。
- **「不動測試地圖」是否為真**:為真。diff 沒有修改任何 `_testmap_*` 函式或 `_TESTMAP_EXTS`;`/tmp` 副本跑 `python3 scripts/test_lumos.py -k testmap` 全過,行為未變。
- **「對照表多一個就自動跟著認」對每種棧都成立嗎**:計劃筆記與 Issue 筆記的措辭本身沒有誇大——只明寫「頂層比對模式的棧(Swift、C#)」與「限 src/ 底下的棧(Kotlin)」兩類會自動跟著認,`dir_mode=="rglob"` 且 `rglob_under` 不是 `"src"` 的棧(dart/python/node-jest/maestro/playwright)明文不推;讀碼與 `/tmp` 副本實測都跟這個措辭一致,不構成文件與行為不符。
- **有沒有別的圖譜筆記/skill 文件還留著測試檔判定的舊說法**:未找到。對整個 `docs/lumos-toolchain-knowledge` grep `androidTest` 只命中這次改的兩篇;`檔案測試依賴地圖_計劃.md`(測試地圖自己的規格)沒有提到 `androidTest`/`<App>Tests`,也沒有跟本次改動的敘述打架。
- **圖譜鏡頭固定席逐條判**(`r3-lens.txt` 列出的 8 篇帶 INVARIANT 內容的節點):diff 這次範圍只在 `_nodehome_stack_test_dirs`/`_nodehome_top_dirs`/`_nodehome_layout`/`_nodehome_in_stack_test_dir`/`_nodehome_is_test`/`_nodehome_required`/`_nodehome_refs` 與一支測試,逐篇核對合約敘述所管的程式路徑跟這次改動零交集:
  - `bound-tests-gate.md`:合約管 code-loop 綁定測試怎麼判紅/懸空/偽證據,diff 沒碰任何 code-loop 執行或判紅邏輯——不影響。
  - `canary-audit.md`:合約管 canary record/second 落盤與 rc,diff 沒碰 canary 任何函式——不影響。
  - `guard-kill.md`:合約管 guard kill rc 優先序與 `--json` 純淨度,diff 沒碰 guard kill——不影響。
  - `slim-get-一行安裝.md`/`slim-install-安裝器.md`/`slim-uninstall-一行卸載.md`:合約管 `.ps1` 編碼、CLAUDE.md 注入冪等/備份、manifest,diff 沒碰任何安裝/卸載函式——不影響。
  - `授權與歸屬.md`:合約管 `_VENDORED_TOOLKIT`/LICENSE 白名單,diff 沒碰 vendoring 邏輯——不影響。
  - `測試假綠形態.md`:合約管「翻紅釘要有前置斷言證明現場成立」,這次新測試(`t_nodehome_stack_test_dirs_not_required`)有照做(第一輪三席造反例、二三輪突變測試全殺)——但如 F1 所述,這條紀律沒有延伸到「Gradle 分支+同副檔名巧合」這個沒被造出來的現場,是覆蓋率缺口而非違反節點字面合約。
  - 其餘 16 篇超出上限只列名的節點:名稱上跟 `_nodehome_*` 無函式呼叫或資料交集,是 `scripts/lumos`/`scripts/test_lumos.py` 巨型共用檔被列為家造成的列名,不影響。

總結:最高 severity major,blocking 共 1 條
