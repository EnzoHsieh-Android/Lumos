severity: minor

邊界與輸入鏡頭的結論:沒有 blocker 或 major。引句錨在 diff 上,實測都用工作樹的 `scripts/lumos`(HEAD 600d7b02)。我的臨時目錄已刪。

## Findings

1. react-parallel 的 `min_lines: 2` 把「改一行 await」算成兩行,單一 await 也會亮
   - 輸入:根目錄 `package.json` 只有 react,`src/api.ts` 裡 `const user = await fetchUser(id)` 改成 `const user = await fetchUser(id, {cache: true})`,只改這一行。
   - 預期:只有一個 await,react-parallel 不亮。這是 S41「單一 await 不亮」想守的行為。
   - 實際:`lumos pitfalls --diff HEAD~1..HEAD --json` 的 meta 顯示 `react-parallel applicable=True`。
   - 原因:`changed_lines` 增行與刪行都算,同一行改動就是 `-`/`+` 兩行,`_n_hit` 數到 2。
   - 影響:亮了就要在表態閘補一題,多問但不漏問,所以降為 minor。
   - 測試缺口:S40、S41 只餵手寫的乾淨行,沒有餵過「同一行改動」的 diff。
severity: minor
   - blocking: 否
   - 引句:「_n_hit = sum(1 for i, n in enumerate(norm) if any(p.search(n) for p in pats)」

2. 新的跑過證據樣式在「不去色」的讀者那邊,對帶色碼的 jest 摘要不再命中
   - 輸入:`Tests:       \x1b[1m\x1b[32m1 passed\x1b[39m\x1b[22m, 1 total`,也就是 FORCE_COLOR 下 jest 的摘要行。
   - 舊樣式 `Tests:.*?[1-9]\d*\s+passed` 命中。新樣式 `Tests:?\s+[^\n]{0,200}?\b[1-9]\d*\s+passed` 不命中,因為色碼 `m` 和 `1` 之間沒有 `\b`。
   - 影響範圍:只有 `_kill_cap` 逐行用 `keep_re` 的那條路。輸出超過 256KB 被截斷、摘要行落在被砍的中段、而且帶色碼時,摘要行保不住。`_ran_evidence_check` 有先去色,不受影響。
   - 注解自己寫了「逐行 re.search 不去色」,但 S4、S35 都沒有測 `_kill_cap` 配帶色碼的行。
severity: minor
   - blocking: 否
   - 引句:「"re": r"Tests:?\s+[^\n]{0,200}?\b[1-9]\d*\s+passed",」

3. eslint 偵測漏掉 `package.json` 的 `eslintConfig`
   - 輸入:根目錄只有 `{"eslintConfig": {"root": true}}` 的 `package.json`。
   - 預期:`_linter_config_hits` 認得。
   - 實際:回 `[]`,doctor 照舊說「沒有接 linter」,init 不提醒。
   - 附帶:同一份改動把 `package.json` 列進 `_LINT_CONFIG_GLOBS`,表示它被當成 eslint 設定來源。`_ESLINT_LEGACY_CONFIGS` 沒有對應處理。
   - 其他變體都對:`eslint.config.mts`、`.eslintrc`(無副檔名)、`.eslintrc.yaml` 和 `.yml` 都命中;`.eslintrc.json5`、`.eslintrc.ts`、`eslint.config.jsx` 不命中,因為 eslint 本來就不支援這些。
severity: minor
   - blocking: 否
   - 引句:「_ESLINT_LEGACY_CONFIGS = (".eslintrc", *(f".eslintrc.{e}" for e in ("js", "cjs", "json", "yml", "yaml")))」

4. 只要有 `vite.config.*`,init 就給 vitest 指令,不看專案實際用 jest 還是 vitest
   - 輸入:根目錄有 `vite.config.ts`,`devDependencies` 只有 `jest`,沒有 vitest。
   - 預期:維持 node-jest。
   - 實際:`_uses_vitest` 回 True,骨架寫 `npx vitest run -t {method}`。沒裝 vitest 的專案第一次跑綁定測試就失敗。
   - 另一個過寬:glob `vite.config.*` 也吃 `vite.config.ts.bak`(實測 True)。
   - `_推測` 欄位有標「看到 vite/vitest 設定」,使用者看得到,所以降為 minor。
   - S1、S2、S3 都沒有「Vite 設定加 jest 依賴」這一格。
severity: minor
   - blocking: 否
   - 引句:「_VITEST_CONFIG_GLOBS = ("vite.config.*", "vitest.config.*")」

5. 測試檔判法:`test.tsx` / `spec.ts` 檔名本身不算,另有一份舊樣式沒跟著改
   - `src/test.tsx` 和 `src/spec.ts` 回 False。Jest 的 testMatch `?(*.)+(spec|test).[jt]s?(x)` 會認這兩種。
   - `src/Cart.tests.tsx` 回 False(少見)。
   - 另一份複製的舊樣式 `_TEST_PAT = re.compile(r"(test_|_test\.|\.spec\.|/tests?/)", re.I)` 在 `_scan_diff_for_irreversible_hints`(`scripts/lumos:6098`)沒更新。`src/App.test.tsx` 裡的 `DELETE FROM` 字樣仍會被當產品程式報成「疑似不可逆」。
   - S43 的反例清單沒有放 `test.tsx`,也沒有核對這份第二個樣式。
   - 其餘邊界都對:`Tests/`(re.I)、`src/__tests__/a/b/c.tsx`、`__Tests__`、`a/b.TEST.ts` 都 True;`__tests__.tsx` 和 `x__tests__/a.ts` 正確為 False。
severity: minor
   - blocking: 否
   - 引句:「_PITFALL_DIFF_TEST_PAT = re.compile(r"(test_|_test\.|\.spec\.|\.test\.|/tests?/|(?:^|/)__tests__/)", re.I)」

## 邊界檢查後判無問題

- Kotlin 的 `_KT_BUILD_ANDROID` / `_KT_BUILD_SERVER`:groovy 與 kts 寫法、`android{` 無空格、`libs.plugins.androidApplication`、CRLF、區塊註解裡的 `android {`、KMP 加 ktor 客戶端、空建置檔、最近建置檔停手,全部落在 android、server 或 None 的預期方向。
  - 註解裡寫 `org.springframework.boot` 的純 jvm 模組會判 server,但那種模組本來就沒有 Android 題,無害。
  - 判不出時都退回 Android 題,和 d2 的方向一致。
  - `libs.plugins.spring.boot` 這種別名判 None,偏安全。
  - 301 支上限的邊界 S34 兩側都有測。
- `_stack_applicability` 的 `norm` 與 `norm_raw` 過濾條件只看 `code.strip()`,兩份索引對齊,`min_lines` 的 `norm_raw[i]` 不會錯位。
- min_lines 恰好 1 與預設行為不變;`over` 路徑繞過 `min_lines` 與 S42 的描述一致。
- 新的 `Tests:?\s+[^\n]{0,200}?...` 樣式:實測 4 萬字長行 0.10 秒,沒有二次方回溯。
- react 觸發詞的詞界(`\buseEffect\b`、`monkey={i}` 不命中、`(?-i:...)`)沒有發現會誤亮或漏亮的輸入。

## 圖譜鏡頭(固定席)

我看了 diff 動到的 `scripts/lumos` 區塊,沒有碰到下列合約的行為:

- `lumos-cli-read` 的 search 排除 superseded:搜尋路徑沒動。
- `guard-kill`:rc 優先序與 `--json` 純度沒動。
- `lumos-cli-lifecycle` 的 re-inject:init 只在尾端加 `_init_lint_hint`,不碰 sentinel 之外的內容。
- `design-loop` 的處置閘:只在 `_dispositions_verdict` 尾端加一行提示,不改 blocked 判定。
- `測試假綠形態`:新增的 S34、S39、S43 都有可翻紅的前置或對照。

findings 以外的固定席節點都標「不影響」。

最嚴重 severity:minor;blocking 共 0 條。

相關檔案:
- `/Users/enzo/orca/workspaces/lumos-toolchain/web-react/scripts/lumos`
- `/Users/enzo/orca/workspaces/lumos-toolchain/web-react/scripts/test_lumos.py`
