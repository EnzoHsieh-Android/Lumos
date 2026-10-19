severity: major

**審查結論:找到 1 條 major 和 4 條 minor。** 我拿 b9ff5494 的 `scripts/lumos` 逐項實跑。修前版本用 `git show 600d7b02:scripts/lumos` 取出對照。

**固定席(LUMOS-IMPACT 那批節點)**
- 判「不影響」:`lumos-cli-read`(search 的 superseded 濾網)、`lumos-cli-lifecycle`(re-inject)、`guard-kill`(rc 優先序與 JSON 純度)、`design-loop`(處置閘第五步)。這份 diff 沒碰這些路徑,`_stack_applicability`、`_kt_*`、`_review_roles` 都不在它們宣稱的行為裡。
- `測試假綠形態`:這輪的「還原翻紅釘」多數附前置斷言,例如資2 的 `len(ticks) >= 1`。唯一例外是第 5 條,部分檢查只驗某函式不存在。
- `pitfalls-code-loop`、`loop-convergence-recording`、`reversibility-governance-ledger` 這三個 `★RISK★` 節點我只當參照,沒逐條審。

---

**1. `_kt_strip_comments` 把 glob 字串裡的 `/*` 當成區塊註解開頭,後面的外掛宣告被吃掉**
severity: major
blocking: 是
歸因:有證據的修復回歸(剝註解是這輪修補才加的)
- 輸入:舊式 Spring 建置檔,glob 在 `apply plugin` 之前:
  ```
  sourceSets { main { resources { include '**/*.yml' } } }
  apply plugin: 'org.springframework.boot'
  ```
- 走法:`find("/*")` 命中 `**/*.yml` 裡的 `/*`。之後找不到 `*/`,函式 `break`,剩下整份文字丟掉。
- 結果:`_kt_flavor_at("a/A.kt", …, {"build.gradle": gr}.get)`,修後是 `None`,修前是 `"server"`(`_kt_flavor_at` 是同一支,只有 `_kt_build_verdict` 對原文與剝註解後文字的差別)。
- 後果:伺服端模組拿不到「排除 Android 三題」,整個 Android 排除功能對這種建置檔失效。
- 方向是判不出,合乎 d2(判錯只准往判不出),所以不是最危險的方向。降到 minor 的唯一理由是方向安全,但失效範圍是「所有 glob 在宣告之前」的 Groovy 建置檔,而且 `// 註解 **/*.java` 也同樣觸發。
- 最小重現:上面 `gr` 一行呼叫即可。目前沒有任何測試涵蓋「字串或行註解裡含 `/*`」。
- 引句:「        j = txt.find("/*", i)」

**2. 角色路徑把「超過上限而沒讀」的建置檔當成「沒有這個檔」,往上找到父層,Android 模組被判成後端**
severity: minor
blocking: 否
歸因:有證據的原有漏查(修前已如此,修補多加的 `max_total_bytes` 多了一條觸發路徑)
- 輸入:根 `build.gradle.kts` 含 `org.springframework.boot`,`app/build.gradle.kts`(Android,>512KB)和 `app/src/A.kt`。
- 結果:
  - 角色路徑 `_review_roles(d,'HEAD~1','HEAD')` 回 `{'app/src/A.kt': 'backend'}`。
  - 工作樹路徑 `_kt_flavor("app/src/A.kt", d)` 回 `None`(`_worktree_text` 對超限檔回空字串,停住)。
  - 修前版本結果同為 `backend`。
- 原因:`_nodehome_cat_blobs_capped` 對超限或超總量的物件回 `None`,reader 把它當「檔不存在」,繼續往上找。
- 這違反檔頭自己寫的「不准把 Android 判成伺服端」。只影響審查員看的角色卡。
- 觸發條件:要超 512KB,或整批超 16MB 後輪到較大的建置檔,現實中很窄。
- 引句:「        got = _nodehome_cat_blobs_capped(root, want, _ROLE_MAX_BYTES, timeout=left, max_total_bytes=_ROLE_MAX_TOTAL_BYTES)」

**3. 伺服端判定自稱「只認外掛宣告」,但 `org\.springframework\.boot` 連依賴座標也算**
severity: minor
blocking: 否
歸因:未判定(沒有修前對照,r1 就是這個樣式)
- 輸入:`dependencies { implementation("org.springframework.boot:spring-boot-starter") }`,沒有 `com.android.`。
- 走法:`_KT_BUILD_SERVER` 第一個分支命中,判 `"server"`。
- 後果:這跟 r1 把 `ktor-server` 拿掉的理由(「手機端也有本機 ktor 伺服器」)同構。使用 convention plugin 的 KMP 共用模組若在 jvm 目標宣告 Spring 依賴,會被判伺服端並拿掉 Android 三題。
- 測試 `t_kt_build_comments_and_ktor_dependency_not_server` 只測 ktor 依賴,沒測 Spring 依賴。
- 引句:「_KT_BUILD_SERVER = re.compile(r"org\.springframework\.boot|io\.ktor\.plugin|libs\.plugins\.(?:spring[.\-_]?boot|springBoot|ktor)\b")」

**4. 同族漏網:`_ROLE_ANDROID_IMPORT` 的 `^\s*import` 在 .kt 檔頭空行上二次方回溯**
severity: minor
blocking: 否
歸因:有證據的原有漏查(修前後都是 7.6 秒)
- r1 資源席抓到建置檔那條 `^\s*android\s*\{`,修成 `[ \t]*`。同一個結構的 `_ROLE_ANDROID_IMPORT` 在 `_kt_flavor_at` 對前 64KB 掃描時沒一起修。
- 輸入:前 65536 個字元是換行的 `A.kt`。
- 結果:`_stack_platform_excluded(["A.kt"], d)` 修後 7.57 秒、修前 7.60 秒;只用 `_ROLE_ANDROID_IMPORT.search` 量:32768 個換行 1.87 秒,65536 個 7.61 秒。
- 一次最多判 300 支。`_ROLE_UI_IMPORT` 與 `_ROLE_UIKIT_IMPORT` 的 `^\s*` 也是同形狀。
- 觸發條件:要有一長串純空白行,現實罕見。
- 引句:「    if _ROLE_ANDROID_IMPORT.search(content[:_KT_HEAD_BYTES]):」

**5. 加了刪除檔的 diff,Android 排除整個失效;兩條測試只驗結構**
severity: minor
blocking: 否
歸因:有證據的原有漏查
- 輸入:伺服端 `src/New.kt` 新增,同一個 diff 還刪掉 `src/Old.kt`。
- 走法:`changed_lines` 的鍵含已刪檔,`_kt_flavor` 讀工作樹得 `None`,`all(... == "server")` 為假。
- 結果:`kt` 的 meta 回到含 `kt-compose`、`kt-leaks`、`kt-startup`(`HEAD~2..HEAD` 實跑)。純新增的 `HEAD~1..HEAD`(排除生效,只列 `kt-coroutines` 等)是對照。
- 方向是多問,表態閘會要求回答這三題。
- 另外,`t_stack_android_only_inside_applicability` 最後一條與 `t_worktree_text_shared_reader` 最後一條只驗 `hasattr`,抓不到行為錯。同函式的前幾條有行為檢查,所以只算小問題。
- 引句:「    if all(_kt_flavor(f, repo_root) == "server" for f in kts):」

---

**三問回答**

1. 原問題的修復效果有行為證據的:
   - 張力候選只出適用題。實跑 `_pitfall_diff_collect`,`tension_candidates` 只剩 `kt-coroutines`,沒有 Android 三題。
   - `min_lines` 只數增行。測試樣本改的是同一行 await,翻紅路徑成立。
   - `exclude` 在 `_stack_applicability` 內消化。meta 少了 `kt-compose`、`kt-leaks`、`kt-startup`,整組清單剩 4 題。
   - jest/vitest 的證據樣式。我另外驗了 `Tests  34 skipped` 與 `Tests: 12 skipped, 0 passed` 都不算跑過,同行 `10 failed, 2 passed` 算,4 萬次 `Tests ` 重複輸入 0.15 秒。
2. 修補處的相鄰路徑:除第 1 條外,`_stack_applicability` 的兩個呼叫端(`_pitfall_diff_collect`、`cmd_impact`)都成立。`applicable_ids=None` 的預設保持舊行為。題號跨棧不重複,實查過。`_worktree_text` 的新鍵型沒有其他讀取端,`grep` 確認。
3. 第 1 條同一案例:修前 `server`,修後 `None`;第 2、4 條修前修後相同。

**未驗範圍**
- `_worktree_text` 的進程級快取沒有失效機制。測試得手動 `.clear()`;`_linter_config_hits` 與 `_uses_vitest` 這輪改成走快取,同一進程內先後改 `package.json` 會讀到舊值。我沒找到會觸發的真實流程。
- `_uses_vitest` 的 docstring 寫「依賴看不出來時才看設定檔」,實作在依賴解析成功但沒有 vitest 與 jest 時也會看設定檔。我沒找到會誤判的真實專案。
- 沒有跑 `test_lumos.py` 的任何子集,也沒對測試做破壞性還原。
- 我的臨時目錄 `/tmp/lumos-seat-work/code-前端框架從vue分出/正確性-sonnet/` 已清空,它本身(空目錄)留給編排者刪。

最嚴重 severity:major,blocking 共 1 條。
