severity: major

審的是文件那半(`r2-docs.patch`、`r2-repair-docs.patch`),拿修後 `b9ff5494`(工作樹 HEAD `3b6df14e`,只多一筆帳本提交)的 `scripts/lumos` 逐項對過。程式行為和家節點(棧別提問表態閘、lint-declaration-health、lumos-cli-lifecycle、bound-tests-gate、arch-alignment-lens)大致對得上,但計劃筆記還留著上一輪的舊說法。

用白話講,三個月後的人讀計劃筆記會以為「Ktor 伺服器依賴也算伺服端」,實際程式明確不這樣判。

1. **計劃裡的決策 d2 與〈做法〉B10 還寫著 `ktor-server` 判伺服端,跟程式和家節點相反**
severity: major
   - blocking: 是
   - 歸因:有證據的修復回歸。修前文件與程式一致(修前程式有 `ktor-server`),修補改了程式和「棧別提問表態閘」,沒改計劃。
   - 位置:`docs/lumos-toolchain-knowledge/Projects/前端框架從vue分出_計劃.md`
     - 開頭 `decisions:` 的 d2 `content`(`valid: true`)。
     - 〈做法〉B10 的「判伺服端的訊號」那條。
     - 同一條還寫「`android {` 區塊」(程式是行首 `android {`)、沒提先剝註解。
   - 為什麼是 major:`CLAUDE.md` 第 3 點給決策紀錄挑戰程式的效力。接手的人照 d2 會判定程式違反決策,把 `ktor-server` 加回去。
     - 那會打破 `t_kt_build_comments_and_ktor_dependency_not_server` 守的「判錯只准往判不出」。
   - 重現:用 `_kt_flavor_at("app/src/A.kt","package a\n",{"app/build.gradle.kts":'dependencies { implementation("io.ktor:ktor-server-cio:2.3.0") }\n'}.get)`。
     - 修前 `600d7b02` 回 `server`。
     - 修後回 `None`。
     - 只有 `// org.springframework.boot` 註解的建置檔也一樣:修前 `server`,修後 `None`。
   - 引句:「沒有 Android 跡象、而且有**伺服端外掛**(`org.springframework.boot`,或 Ktor 伺服端的 `io.ktor.plugin`、`ktor-server`)→ 伺服端」
   - 修法:改 d2 `content` 與 B10 訊號,對齊程式。程式碼是 `_KT_BUILD_SERVER`(`scripts/lumos:30373`),規則見「棧別提問表態閘」該段。

2. **〈做法〉B10 的「接線」與「讀法」還是舊設計**
severity: minor
   - blocking: 否
   - 歸因:有證據的修復回歸。
   - 「張力候選都傳同一份」:程式已改成 `_tension_candidates_into(..., applicable_ids=...)` 只出適用題(`scripts/lumos:46857`、`47572`)。
   - 讀法 ④「快取存建置檔文字,鍵含讀取來源」:程式是 `_kt_build_verdict` 的 `lru_cache(64)` 加 `_worktree_text` 共用快取。
   - 計劃的〈實作紀錄〉④已改寫,但〈做法〉本文沒同步。
   - 引句:「`_stack_applicability` 多收一個「要排除的題號集合」參數(預設空,既有呼叫照舊),集合由上面那支共用小函式算出;pitfalls --diff、改檔前推播、張力候選都傳同一份。」

3. **〈做法〉F1 與驗收條款 S1 沒反映「依賴優先」的 vitest 判法**
severity: minor
   - blocking: 否
   - 歸因:有證據的修復回歸。
   - 程式 `_uses_vitest`(`scripts/lumos:26528`):依賴有 vitest 才是;有 jest 沒 vitest 就不是;依賴看不出才看 `vite.config.*`。
   - 計劃寫的是「有 vite.config 或依賴有 vitest 就是」。
   - 實測:`package.json` 只有 jest、根目錄有 `vite.config.ts`,修前 `True`、修後 `False`。
   - 跑過證據的樣式也不同:計劃寫 `Tests:?\s+[^\n]{0,200}?\b[1-9]\d*\s+passed`,程式是 `Tests\b[^\n]{0,200}?(?<![0-9])[1-9]\d*[^\S\n]+passed`。
   - 這兩點只有家節點(lumos-cli-lifecycle、bound-tests-gate)更新了。
   - 引句:「repo 根有 `vite.config.*`(`.ts/.js/.mjs/.cjs/.mts/.cts`)或 `vitest.config.*`,或根 package.json 的依賴鍵(用 F2 那支共用小函式收三類)有 `vitest` → 是。」

4. **`lumos-cli-lifecycle` 那段句子被插入的括號弄斷**
severity: minor
   - blocking: 否
   - 歸因:有證據的修復回歸。
   - 「依賴有 jest 沒有 vitest 的照舊給 jest(…) 與 `npx vitest run -t {method}`」,讀起來像 jest 對應 vitest 指令。
   - 引句:「依賴有 jest 沒有 vitest 的照舊給 jest(代碼審 r1 折入,測試 t_init_skeleton_vite_with_jest_stays_jest) 與 `npx vitest run -t {method}`」

5. **效能檢核目錄(題目內容源)沒同步兩處**
severity: minor
   - blocking: 否
   - 歸因:未判定。效能檢核目錄第 229、234、235 行的 kt-compose / kt-leaks / kt-startup 列沒提 `android_only`,這是 r1 就有的缺口。`min_lines` 只數增行是修補新增,修前也沒寫。
   - 第 110、252 行 `min_lines` 仍寫「改動行」,但推送前分級只數增行(家節點已更正)。
   - 引句:「`min_lines: 2`:至少兩行改動行命中才算適用」

6. **`lint-waivers.json` 第一條放行理由歸因不準**
severity: minor
   - blocking: 否
   - 歸因:有證據的原有漏查。
   - 理由寫「複雜度 11→13 來自把 android_only 排除…放進這一處」。我用 ruff C901 實測:主線版 11、修前 `600d7b02` 已是 13、修後仍是 13。
   - 修補本身沒讓它變複雜,13 主要來自 min_lines 那一段。
   - 張力候選那條「15→16」屬實。
   - 兩條放行的 `by` 填 `enzo`,理由卻寫「編排者裁定」。這是既有慣例,不另報。

三問
- **原問題修復效果**:
  - 文件那半的行為宣稱,下面五項核對一致,出處都在家節點:
    - android_only 排除:`_stack_applicability`(`exclude` 參數)和 `_stack_whole_group` 兩處消化。
    - 三個呼叫點:pitfalls、改檔前推播、張力候選。
    - Kotlin 判法:先剝註解、行首 `android {`、`libs.plugins.spring.boot/springBoot/ktor` alias、記憶 64 份。
    - 測試檔判法:`_PITFALL_DIFF_TEST_PAT` 與不可逆提示掃描共用。
    - 全表題數:修前 60、修後 68,九棧。
  - 「infra 回 None」:`_review_role_for` 沒有 infra 分支,infra 鍵不在前端或後端鍵集合,自然回 None,宣稱成立。
  - 反例是上面第 1 到 4 項。
- **修補處的正常、錯誤與相鄰路徑**:
  - 建置檔讀取:工作樹路徑的超大建置檔回空字串、判不出;角色批次讀取路徑會往上一層找。文件已分開寫明。
  - eslint 偵測:`eslintConfig`、新舊設定、mts/cts 的描述與程式一致。
  - `lumos lint` 八個相關節點全部 0 問題,`doctor` 沒有指向本分支節點的新 issue。
  - 引用的測試名我用 `def t_…` 逐個對過,只有 `t_infra_before_react_stack_key` 找不到。它是計劃預先留給另一個分支的條款。
  - `Projects/前端知識與風險詞_計劃` 在本分支不存在,只在 `web-fe-knowledge` 分支;`related:` 與正文的連結在本分支是懸空的,`lint` 沒報。
- **新發現同一案例的修前修後**:第 1 項、第 3 項已附兩版實測。第 2、4、5 項是文字對照,沒有可執行的修前修後。

未驗範圍:`skills/react-idioms`、`templates.md`、`ONBOARDING.md`、`ARCHITECTURE.md`、`target-arch-frontend-template` 的內文;角色預算與虛擬時鐘的程式行為;order-web 實地驗收(S30)。

我的臨時目錄已刪。

最嚴重 severity:major;blocking 共 1 條(第 1 項)。
