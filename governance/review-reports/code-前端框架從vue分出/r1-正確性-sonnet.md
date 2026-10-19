severity: minor

我逐 hunk 走了輸入。新增的 25 支 react 測試、19 支 kt 測試、10 支 vitest 測試在工作樹上全過。以下 5 條都是小問題,沒有 major。

**1. 跑過證據的樣式放寬後,會跨行誤判**
severity: minor
- blocking: 否
- 位置:`_RAN_EVIDENCE["node-jest"]["re"]`,即 `Tests:?\s+[^\n]{0,200}?\b[1-9]\d*\s+passed`。
- 問題:冒號變成可有可無,`\s+` 又能吃掉換行,所以「某行以 Tests 結尾、下一行出現 N passed」會被當成有跑過。舊樣式要求 `Tests:` 且 `.` 不跨行,沒有這個洞。這道閘本來就是擋「跑 0 支卻回 0」的假綠。
- 輸入 `"Running Integration Tests\n   ✓ handles 2 passed items\n Tests  1 skipped (1)\n"`,預期 `(False, hint)`,實際 `_ran_evidence_check("node-jest", …)` 回 `(True, '')`。
- 修法:`\s+` 改成 `[^\S\n]+`。測試沒有跨行的負向案例,S5、S7 只用乾淨的摘要。
- 引句:「"re": r"Tests:?\s+[^\n]{0,200}?\b[1-9]\d*\s+passed",」

**2. 帶色碼時,逐行讀者認不出摘要**
severity: minor
- blocking: 否
- 位置:同一條樣式。`_kill_cap` 裡 `re.search(keep_re, l)` 讀的是沒去色的原始行。
- 問題:新樣式要求 `Tests` 後面緊接空白,`\b` 又要求數字前是非字元。實測 `"\x1b[1mTests:\x1b[22m       \x1b[1m\x1b[32m1 passed…"` 的 jest 彩色行,舊樣式命中、新樣式不命中。vitest 彩色行新舊都不命中。
- 影響:輸出超過 256KB、摘要落在被砍的中段、又帶彩色時,摘要行不會被保留。
- 測試:S4 只測 `_ran_evidence_check`(它會先去色),沒測逐行讀者。
- 引句:「①不錨行首、不加旗標——兩個讀者共用這條字串(_ran_evidence_check 去色後對整段 re.search、_kill_cap 逐行 re.search 不去色),」

**3. Kotlin 伺服端判定會被註解或字面依賴字串騙到,把 Android 模組判成伺服端**
severity: minor
- blocking: 否
- 位置:`_KT_BUILD_SERVER = re.compile(r"org\.springframework\.boot|io\.ktor\.plugin|ktor-server")`。它是對整份建置檔做 `search`,沒有排除註解。
- 問題:註解裡的字串或字面的 ktor-server 依賴也算命中。
- 輸入 A:`app/build.gradle.kts` 是 `plugins { alias(libs.plugins.app) }` 加一行註解 `// migrate from org.springframework.boot later`。
- 輸入 B:`plugins { id("myorg.android.application") }` 加 `implementation("io.ktor:ktor-server-cio:2.3.0")`。這種 convention plugin 加手機端本機 ktor 伺服器的寫法,模組裡沒有 `com.android.`,也沒有 `android {` 區塊。
- 預期:判不出(`None`)。實際:兩個輸入的 `_kt_flavor_at("app/src/A.kt", "package a\nclass A\n", reader)` 都回 `"server"`,`_kt_role` 回 `"backend"`。
- 影響:沒有 android 匯入的純 Kotlin 檔(repository、mapper)會被拿掉 Android 三題,角色卡也改發後端卡。
- 與設計的衝突:這違反程式註解自己寫的「判錯的方向只准是判不出」。
- 測試:S25、S31 沒有涵蓋這兩種。
- 引句:「_KT_BUILD_SERVER = re.compile(r"org\.springframework\.boot|io\.ktor\.plugin|ktor-server")」

**4. 用版本目錄 alias 寫 Spring 外掛時,判不出**
severity: minor
- blocking: 否
- 輸入:根目錄 `build.gradle.kts` 是 `plugins { alias(libs.plugins.spring.boot) }`。
- 預期:判伺服端。實際:`_kt_flavor_at` 回 `None`,Android 三題照舊列出。
- 說明:這是漏判,不是誤判,方向合乎「寧可判不出」。但 alias 是新專案的主流寫法,B10 這個功能對這類專案不會生效。S31 只測了 Android 這邊的 alias,伺服端的 alias 沒有測試。
- 引句:「return "server" if _KT_BUILD_SERVER.search(txt) else None」

**5. 張力候選不看 `min_lines`,出了不適用題的候選**
severity: minor
- blocking: 否
- 位置:`_tension_candidates_into` 對 `_STACK_TRIGGERS[sk]` 逐題只比 `when`。`_stack_applicability` 現在多了 `min_lines`,兩邊的判法分歧了。
- 輸入:React 專案新增 `src/New.tsx` 只有一行 `const u = await f()`,對照檔 `Other.tsx` 沒有。
- 預期:候選只含適用題。實際:`tension_candidates` 有 `['react-race', 'react-parallel']`,同一輸入的 `_stack_applicability` 只讓 `react-race` 適用。
- 影響:`pitfalls` 的人讀輸出會多印一條「可能撞」,指到一題不在表態表、沒人能答的題。`_dispositions_template` 只對適用題帶 hint,所以不會擋推送,只是雜訊。
- 與註解的衝突:程式註解「候選的題必在 stack_questions_applicable」不再成立。這次新增的 `_tension_drop_excluded` 只處理 android_only,沒處理 `min_lines`。
- 引句:「_need = spec.get("min_lines", 1)」

**確認沒問題的項目**
- 混合依賴、只有 devDependencies、壞 JSON:`_pkg_dep_keys` 解析失敗回 `None`、`_node_flavor_of` 回 `None`,沿用舊行為,沒有新洞。S38 涵蓋 react 與其他框架並存。
- min_lines 超過整組門檻的路徑:`min_lines` 區塊在 `else` 內,超過門檻時不會被誤殺。S42 有釘住。
- 舊表態遇題組換名:S39 的提示用 `(_stack_spec_by_id(q)[0] or None) not in meta` 判斷。題號不存在時也歸為舊題,同棧缺題不多印這行。
- Kotlin 混合 repo 與 monorepo:以最近的建置檔為準,「全部判伺服端才拿掉題」。只要有一支判 Android 或判不出,就不拿。
- 超過 300 支 `.kt`:收手不拿題,S34 有測。
- `ESLINT_USE_FLAT_CONFIG=false` 前綴:`_lint_run_and_parse` 用 `shell=True`,環境變數前綴能執行。
- 測試判法:`_PITFALL_DIFF_TEST_PAT` 的 `.test.` 與 `__tests__/` 不會誤吃 latest、contest、attest。本 repo 內受影響的是三支 `mods/**/*.test.ts`,它們本來就是測試。
- 其他測試:S41、S42 的翻紅釘成立。

最嚴重 severity:minor;blocking 共 0 條。
