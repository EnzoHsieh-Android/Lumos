severity: major

我只在 `/tmp/lumos-seat-work/code-前端框架從vue分出/邊界-sonnet/` 下做實驗。修前版本是 `git show b9ff5494:scripts/lumos`,修後版本是 `git show 9591e609:scripts/lumos`,兩份都載入同一個測試程式比對。repo 的 HEAD 目前是 9508e5af,不是 9591e609,所以我沒有直接用工作樹。

## Findings

**1. Spring 外掛樣式有二次方回溯,`id` 後面接一大段空白就卡住**
severity: major
- blocking: 是
- 位置:`_KT_BUILD_SERVER` 的 `\bid\s*\(?\s*`。兩個 `\s*` 之間隔著一個可有可無的 `\(?`,同一段空白可以有 O(N) 種切法。
- 輸入:建置檔文字是 `plugins { kotlin("jvm") }\nval id` 後面接 N 個換行再接 `x`。
- 路徑:`_kt_flavor_at` 呼叫 `_kt_build_verdict`,再呼叫 `_KT_BUILD_SERVER.search`。
- 預期:判不出,瞬間回來。
- 實際:修後版本 N=10000 要 0.60 秒,20000 要 2.38 秒,40000 要 8.94 秒,二次方成長。N 換成 131072 約 90 秒以上(依 40000 線性外推,沒有實跑);`"id"` 後面接 512KB 空格我跑了超過 15 秒沒結束。
- 修前版本同一輸入是 0.00 秒。
- 限制:這不是 `_ROLE_BUDGET` 能攔的,單一 `re.search` 沒辦法中斷。512KB 讀檔上限也擋不住,這個檔在上限內。
- 同族:這正是 r2 資源席抓的「空行洪水」(13 萬空行 31 秒)。這輪的測試 `t_kt_build_android_regex_blank_lines_fast` 輸入裡沒有 `id` 這個字,所以測不到;`t_no_multiline_caret_whitespace_star` 只看 `^\s*`,也守不到。
- 歸因:有證據的修復回歸。
- 重現指令(修前、修後各跑一次):`python3.14 -c "…_kt_build_verdict('val id'+'\n'*40000)"`,載入方式見 `/tmp/lumos-seat-work/code-前端框架從vue分出/邊界-sonnet/p6.py`。
- 引句:「_KT_BUILD_SERVER = re.compile(r"""(?:\bid\s*\(?\s*|\bapply\s+plugin\s*:\s*)["']org\.springframework\.boot["']"""」

**2. 超限的 `.java` 原始檔,角色從「判不出」變成「backend」**
severity: major
- blocking: 是
- 位置:`_review_roles` 新的 `blobs` 建法。
- 輸入:Android 的 `app/src/Big.java`(有 `import android.app.Activity;`),大小 560KB,超過 `_ROLE_MAX_BYTES`。
- 路徑:大小查得到所以 `n` 不是 None,內容沒讀所以 `v` 是 None,結果 `content=""`。`_review_role_for` 的 java 分支只擋 `content is None`,`""` 通過後,`_ROLE_ANDROID_IMPORT.search("")` 沒命中,回 `"backend"`。
- 實際結果:修前版本 `{'app/src/Big.java': None}`,修後版本 `{'app/src/Big.java': 'backend'}`。我在 `/tmp/lumos-seat-work/code-前端框架從vue分出/邊界-sonnet/repo1` 建了小 git repo,兩版都跑 `_review_roles`。
- 原因:這次改動的本意只是讓「超限的建置檔」停在那一層。但同一個 `blobs` 也餵給被審的原始檔。`.kt`、`.swift`、`.dart` 碰到 `""` 還是判不出,只有 `.java` 變成後端。
- 另一個觸發面:整批 16MB 總量上限被超過時,排在後面的 `.java` 也會一樣被判成後端(沒實跑)。
- 沒有測試覆蓋:新增的測試只驗建置檔超限。
- 歸因:有證據的修復回歸。
- 引句:「blobs = {k: (v.decode("utf-8", "replace") if v is not None else ("" if n is not None else None))」

**3. 跑過證據的 `Tests:` 分支沒有錨定,標題含「Tests: 2 passed」還是能偽造證據**
severity: minor
- blocking: 否
- 輸入:輸出是 `  ○ skipped handles Tests: 2 passed case\nTests:       1 skipped, 1 total\n`。
- 預期:沒跑過。
- 實際:`re.search(spec["re"], …)` 命中(同型的 `✓ … Tests: 2 passed` 我實跑過,結果為真)。
- 原因:新樣式只把 `Tests\b` 那一支錨在行首,`Tests:` 那一支仍然可以出現在行中任何位置。測試 `t_ran_evidence_title…` 只測了沒有冒號的「Tests 2 passed」。
- 歸因:有證據的原有漏查。這個樣式修前就吃得下這種輸入,這輪只收窄了一半。
- 引句:「"re": r"(?:Tests:|(?:^|(?<=\n))[^\S\n]*(?:\x1b\[[0-9;]*m[^\S\n]*)*Tests\b)[^\n]{0,200}?(?<![0-9])[1-9]\d*[^\S\n]+passed",」

**4. 行首錨定後,摘要行前面有前綴(時間戳、工作區前綴)的真實輸出被判成沒跑**
severity: minor
- blocking: 否
- 輸入:`2026-10-15T10:00:00.123Z      Tests  1 passed (1)`、`10:42:11 AM       Tests  1 passed (1)`,或 `\x1b[2K` 這類非 SGR 的游標碼開頭。
- 實際:修前版本命中,修後版本不命中。
- 影響:方向是保守的,會誤擋推送,並建議使用者換 reporter。turbo、`pnpm -r` 這類工具會幫每行加前綴,我只有用時間戳實測,沒有實跑那些工具,所以降到 minor。
- 已確認正常的輸入:jest 與 vitest 的純文字、CRLF、結尾沒換行、tab 縮排、SGR 色碼夾空白都能認。「Tests 2 passed」開頭沒有 `Tests:` 的標題行確實被擋掉。
- 歸因:有證據的修復回歸(修前後各跑一次的結果見上)。
- 引句:「#   開頭錨在「Tests:」或行首(可帶色碼與空白)的 Tests:測試標題裡剛好有「Tests 2 passed」不算(r2 資安席)。」

**5. 「全面替換 `^\s*`」沒做完,守衛也漏了別名**
severity: minor
- blocking: 否
- 位置:`scripts/lumos:6761`(修後版本),`_mflag = _re_f.search(r"^\s*FLAG:(\S+)", summ, _re_f.M)`。
- 輸入:筆記摘要是 6 萬個空行加 `x`。
- 實際:同一條樣式直接跑,6.7 秒,二次方。
- 守衛漏洞:`t_no_multiline_caret_whitespace_star` 只認同一行出現字面 `re.M`、`re.MULTILINE` 或 `(?m)`。`_re_f.M` 不在其中,旗標換行寫也不在。
- 影響:筆記摘要是 AI 寫的一小段文字,現實觸發面很窄,所以只列 minor。
- 歸因:有證據的原有漏查。
- 引句:「行首空白一律只收空格與 tab:^\s* 搭多行旗標會吞換行,一大段空行二次方回溯(r2 資源席:13 萬空行 31 秒;t_no_multiline_caret_whitespace_star 全檔守)」

**6. 兩處文件還在寫「超限建置檔會往上一層找」,跟修後行為互相矛盾**
severity: minor
- blocking: 否
- 位置:`docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md` 第 265 行(已知限制:建置檔大到超過讀取上限時會往上一層找),以及計劃筆記 `Projects/前端框架從vue分出_計劃.md` 第 221 行。同一篇 pitfalls-code-loop.md 第 273 行說這輪已改成停在該層。
- 影響:照第 265 行做判斷會得到錯的預期,而且寫進去的限制已經不成立。
- 歸因:有證據的修復回歸(文件沒同步)。
- 引句:「# 物件在、但超過單檔或整批上限沒讀的 → 空字串(在但讀不了,停在這一層判不出),跟工作樹路徑 _worktree_text 同語意;」

**7. S43 條款字面「名字含 test 字樣的產品檔應照舊掃」仍不成立**
severity: minor
- blocking: 否
- 輸入:`src/contest_form.tsx`、`src/latest_items.ts`、`src/attest_signer.ts`。
- 實際:修前版本與修後版本都判成測試檔,不附棧別題。
- 原因:`test_` 沒有錨定邊界。條款的測試只用了 `latest.tsx`、`contest/x.ts`、`attest.ts` 這類不帶底線的名字,所以測不到。
- 歸因:有證據的原有漏查。
- 引句:「_PITFALL_DIFF_TEST_PAT = re.compile(r"(test_|_test\.|\.spec\.|\.test\.|(?:^|/)tests?/|」

## 已查過、沒問題(順帶紀錄,不算 finding)

**Kotlin 單一掃描器**
- 實跑的輸入:kts 的 `"""` 原始字串、groovy 單引號與 `'\''`、`'"'` 字元字面值、雙引號內的撇號、註解內的撇號、`"${foo("x")}"`、檔尾沒換行、只有註解的檔、沒閉合的 `/*`。
- `exclude '**/*.yml'` 加上註解裡的 Spring 回「判不出」,同樣情形加真的宣告回「伺服端」。
- 這些都沒有把 Android 判成伺服端:android 判定排在伺服端之前,掃描器的行內誤判也只會把伺服端藏成「判不出」。

**Spring 與建置檔寫法**
- 認得的寫法:`id("…") version "3" apply false`、`id '…'`、`apply plugin: '…'`、`libs.plugins.spring.boot`、`libs.plugins.springBoot`、Maven 的 starter-parent。
- 沒認出的寫法(都落在「判不出」,方向安全):Kotlin DSL 的 `apply(plugin = "…")`、groovy 的 `apply(plugin: '…')`、`libs.plugins.springframework.boot`。
- pom.xml 裡的 XML 註解不會被剝掉,`<!-- spring-boot-starter-parent -->` 會被判成伺服端。pom 不是 Android 專案的建置檔,所以影響很小。
- pom 同一行出現 `http://` 時,`//` 之後的整行被當註解吃掉,結果是判不出。

**其他修補點**
- 判定記憶:最多 64 份、每份 512KB,上限有效。
- 測試檔判定:`Test.tsx`、`Spec.tsx`、`test.py`、`test.d.ts` 不再算測試;根目錄的 `tests/`、`test/` 算;`latest.test.tsx`、`__tests__/`、`spec.mts` 都算。
- `eslintConfig`:`{}` 算,null、字串、陣列、false 不算。我把 `{}` 算進去對照過 ESLint 的行為:它只要求欄位存在而且是物件,所以這樣處理合理。

## 回答三個問題

**①原問題的修復效果**
有行為證據的有:
- Kotlin 掃描器的字串與註解處理。
- `Test.tsx`、`test.py` 不再算測試檔,根目錄 `tests/` 算測試檔。
- `eslintConfig` 要是物件。
- 超限的 Android 建置檔停住(我用的是 `_review_roles` 的測試案例,沒有另建 repo 重跑)。
- 判定記憶有界。

「Tests 2 passed」只收了沒冒號的那一半(finding 3)。

**②修補處的相鄰路徑**
有兩處壞掉:Spring 樣式的二次方回溯(finding 1),以及超限原始檔的角色翻轉(finding 2)。

**③新發現的修前與修後**
- finding 1:修前 0.00 秒,修後 8.94 秒(N=40000)。
- finding 2:修前 None,修後 backend。
- finding 4:修前命中,修後不命中。
- finding 3、5、7:修前修後都一樣,是原有漏查。
- finding 6:是這輪改完沒同步的文件。

**未驗範圍**
- `_stack_platform_excluded` 的「刪掉的 `.kt` 不算」我沒有單獨實跑。
- 沒測 Windows 路徑分隔符。
- 沒用真實的 turbo 或 pnpm 輸出驗證前綴行為。
- 整批 16MB 總量上限對 `.java` 的實跑沒做。

最嚴重 severity:major,blocking 共 2 條(finding 1、2)。
