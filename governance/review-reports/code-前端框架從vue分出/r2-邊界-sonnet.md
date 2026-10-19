severity: major

審查範圍:修後 b9ff5494 的 `scripts/lumos`。修前 600d7b02 另取成獨立檔,用 importlib 載入兩版,以同一組輸入對跑。臨時目錄已刪。

## Findings

**1. 區塊註解剝除會被行註解或字串裡的 `/*` 帶歪,能把 Android 建置檔判成伺服端**
severity: major
- blocking: 是
- 歸因:有證據的修復回歸。
- 位置:`_kt_strip_comments`。它先用 `find("/*")` 剝區塊註解,後才剝 `//` 行註解,也不認字串。
- 失敗場景:
  - 輸入是 Android 模組的建置檔:`plugins { id("io.ktor.plugin"); id("convention.android.library") }`。
  - 接著一行 `// skip **/*.kt in lint`,再來是 `android { namespace = "x" }`。
  - 最後一行 `tasks { exclude("**/generated/**") }`。
  - 行註解裡的 `**/*.kt` 被當成區塊註解開頭。它吞到後面 `**/generated` 的 `*/` 為止,`android {` 連同中間內容一起消失,只剩 ktor 外掛。
  - 命令:`_kt_build_verdict(S)`。修前版回 `android`,修後版回 `server`。
  - 去掉那行註解與 exclude 行後,修後版回 `android`,所以是註解造成的翻轉。
- 影響:這違反設計決策 d2「判錯的方向只准是判不出,不准把 Android 判成伺服端」。
  - 慣例外掛(`convention.android.*`)的 Android 模組只靠 `android {` 區塊被認出,最容易中招。
  - 吞到檔尾而沒有結尾 `*/` 時,結果退成 `None`,方向安全但失去伺服端判斷。
  - 例如 `// TODO remove /* hack` 後面接 `org.springframework.boot`,修前判 `server`,修後判 `None`。
  - `exclude '**/*Test*'` 在 `apply plugin: 'org.springframework.boot'` 之前時也是同樣結果(`None`)。
- 引句:「區塊註解用 find 逐段跳,不用正規式,大檔也是線性。」
- 修法:用單一從左到右的掃描器,同時認字串、`//`、`/* */`,不要分兩趟。
- 效能沒問題:51 萬字元的 `/*/` 重複、無結尾 `/*`、大量空行,都在 0.02 秒內回答。

**2. 內容比對仍是兩套口徑:改檔前推播把刪行與增行都算進 `min_lines`**
severity: minor
- blocking: 否
- 歸因:有證據的原有漏查(修前版同樣是 True,這輪只修了 pitfalls 路徑)。
- 失敗場景:
  - `Edit` 把 `const a = await f(1)` 改成 `const a = await f(2)`,一行改動。
  - impact-hook 的 `extract_delta_text` 把 `old_string` 與 `new_string` 合成 `delta_text`。
  - `_stack_applicability({"react": [old, new]}, 200)` 沒帶 `added_by_stack`,react-parallel 亮。結果:修前 True、修後 True。
  - pitfalls 路徑對同一改動帶 `added_by_stack={"react":[new]}`,結果 False。
- 影響:同一份改動,pitfalls 不亮、推播卻亮,不符 `_stack_applicability` docstring 寫的「同一行改動的刪行與增行不算兩行」。
- 引句:「added_by_stack:{棧: [增行…]};min_lines 只數增行(同一行改動的刪行與增行不算兩行),沒給就數全部改動行。」
- 修法:hook 路徑要嘛只用 `new_string` 的行算 `min_lines`,要嘛在文件明講 hook 刻意數全部。

**3. 測試檔判法:根目錄 `tests/`、`test/` 仍不算測試,而新加的 `test`/`spec` 檔名過寬**
severity: minor
- blocking: 否
- 歸因:`tests/`、`test/` 是有證據的原有漏查;`Test.tsx` 是修補新增。
- 失敗場景:
  - `_PITFALL_DIFF_TEST_PAT` 的 `__tests__` 與新檔名分支都改成 `(?:^|/)`,但 `/tests?/` 沒改。
  - git diff 的路徑是 repo 相對,所以 `tests/a.tsx`、`test/a.tsx` 在根目錄時都回 False,測試檔照樣被當產品碼附棧別題。修前同樣是 False。
  - 新分支 `(?:^|/)(?:test|spec)\.[^/]*$` 加 `re.I`:`src/components/Test.tsx`、`Spec.tsx`、`src/utils/test.ts`、`Spec.kt`、`src/test.d.ts` 都變 True,修前是 False。
  - 實際命令與輸出:對 23 個檔名用修前、修後 regex 各跑一次。
- 與驗收條款的關係:S43 只寫「`*.test.*`、`__tests__/` 是測試;`latest`、`contest`、`attest` 照舊掃」。
  - 裸 `test.tsx`、`spec.ts` 沒有任何條款,只靠修補測試裡的 `src/test.tsx` 斷言。
  - 它們被當測試的取捨沒進計劃。
- 引句:「|/tests?/|(?:^|/)__tests__/|(?:^|/)(?:test|spec)\.[^/]*$)」

**4. `eslintConfig` 為 `null`、`false`、`[]`、字串時也當成舊式設定**
severity: minor
- blocking: 否
- 歸因:修補新增,修前根本不認 `eslintConfig`。
- 失敗場景:
  - `{"eslintConfig": null}` 或 `"react-app"` 時,`_linter_config_hits` 回 `eslint` 命中。
  - 範本指令因此帶上 `ESLINT_USE_FLAT_CONFIG=false`。
  - 判法只看 `pkg_key in _pkg`,不看值的型別。
- ⚠:ESLint 實際怎麼處理 `null` 值,我沒在本機驗過,不確定。
- 對照:`{}` 與 `{"root":true}` 判命中,合理。BOM、非 dict 的 package.json、壞 JSON、巢狀鍵都正確回空。
- 引句:「if isinstance(_pkg, dict) and pkg_key in _pkg:」

## 已驗無問題的主張

- **Kotlin alias**
  - `libs.plugins.springBoot`、`spring.boot`、`springboot`、`spring_boot`、`ktor`、`ktor.server` 修後都判 `server`;修前都是 `None`。
  - `springBootStarter`、`springframework.boot`、`ktorPlugin`、`spring.dependency.management` 單獨出現時是 `None`,方向安全。
  - Groovy `apply plugin:` 與 kts `id()` 都判 `server`。
  - 純註解裡的 `org.springframework.boot` 判 `None`,修前判 `server`。
  - Android 標記被註解掉、外掛是 Spring 時判 `server`,合理。
  - CRLF 正常。
- **字串裡的 `/*`**
  - 字串裡的 `"/*"` 把後續整段吞掉,Android 與 Spring 都變 `None`,方向安全,但偵測力下降(修前 `server`/`android`)。
  - 這和 finding 1 是同一個根因。
- **512KB 邊界**
  - 建置檔 524287、524288 位元組讀到並判 `server`,524289 判 `None`,符合「超過才不讀」。
  - 無 `.kt` 內容、已刪除的 `.kt` 都落在判不出,方向安全。
- **跑過證據比對(`Tests\b[^\n]{0,200}?(?<![0-9])[1-9]\d*[^\S\n]+passed`)**
  - jest 29、vitest 一行、帶色碼的 vitest 與 jest、`10 passed`、`1 failed | 2 passed`、CRLF、`Tests` 行在最後一行沒換行,都判跑過。
  - `Tests  34 skipped`、`0 passed`、`10 skipped | 0 passed`、`Test Files  1 passed`、數字與 `passed` 跨行、只有 todo、只有 failed,都判沒跑過。
  - 對 `_kill_cap` 的逐行不去色讀法,色碼不影響這幾例。
  - 效能:4 萬位數字 0.001 秒,4 萬個 `Tests ` 重複 0.15 秒。
  - 殘留細節:數字被色碼單獨包起來(`Tests  <色>1<重設> passed`)時,只有去色讀法會判跑過,逐行不去色讀法判不過。vitest、jest 的預設輸出不會這樣切,沒有實例。
- **vitest 判定**
  - 依賴有 `vitest` 就判是;有 `jest` 沒有 `vitest`(含 `peerDependencies`)就判否。
  - 依賴看不出時,`vite.config.{ts,js,mjs,cjs,mts,cts}` 與 `vitest.config.*` 判是,`.bak`、`.json` 不算。
  - 壞 JSON 的 package.json 退回看設定檔。
  - 只在 `scripts` 裡提到 vitest、沒有依賴也沒有設定檔,會判 jest。這是修前就有的行為。

## 驗收條款能不能寫成會紅的測試

- S35(4 萬個數字,1 秒內)可以。實測 0.001 秒,離門檻有三個數量級,不會時紅時綠。
- S40 與 S41 的 pitfalls 路徑可以寫成會紅的測試,但 finding 2 的 hook 路徑沒有對應條款。
- 以下三處沒有條款:
  - 註解或字串內含 `/*` 的建置檔(finding 1)。
  - 裸 `test.tsx` 與 `spec.ts`(finding 3)。
  - `eslintConfig` 的值型別(finding 4)。

## 回答修補鏡頭三問

1. **原問題的修復效果有何行為證據**
   - 已驗(修前、修後對跑):alias 辨識、註解剝除、色碼數字邊界、vitest 判定、`eslintConfig` 辨識、`added_by_stack` 在 pitfalls 路徑生效。
   - 未驗:各條款綁定的測試本身是否抓得到錯,我沒有翻紅。
2. **修補處的正常、錯誤與相鄰呼叫路徑是否仍成立**
   - 正常路徑成立。錯誤路徑有 finding 1:剝註解本身造成 Android 判成伺服端。
   - 相鄰路徑(impact-hook)沒套用同一套 `min_lines` 口徑,即 finding 2。
3. **新發現的同一案例修前、修後各是什麼結果**
   - finding 1:修前 `android`,修後 `server`。
   - finding 2:修前 True,修後 True。
   - finding 3:`tests/`、`test/` 修前、修後都是 False;`Test.tsx`、`Spec.tsx` 修前 False,修後 True。
   - finding 4:修前不認,修後認。

未驗範圍:ESLint 對 `eslintConfig: null` 的實際行為,以及全套測試。

最嚴重 severity:major;blocking 共 1 條。
