severity: major

我對這份 diff(甲丙,87c8256..cafcd3e)做了實跑與逐 hunk 閱讀。detekt 兩條宣告用一支標準 Compose 檔各跑一次,android.yml 那條的 6 項放寬都生效,compose.yml 那條只報外掛規則。`t_kt_catalog_batch4_wiring` 12 支、`t_lint_android_ci_advice` 38 支都過。CI 下載網址 HEAD 回 200,長度 69520099。本機 jar 的 sha256 與寫死的 `b8c73288…ddd6` 相同。

## F1
severity: major
blocking: 是
位置:`configs/detekt/android.yml` 的 `TopLevelPropertyNaming.constantPattern`;文件端是 `docs/lumos-toolchain-knowledge/Projects/Android現成檢查接上CI與推送前_計劃.md`(實務隱患「共用設定放寬六項」)和 `docs/lumos-toolchain-knowledge/Systems/linter精選目錄.md`(WHY 的 `[代價:…]`)。

引句:「constantPattern: '[A-Z][A-Za-z0-9]*'」
引句:「PascalCase 頂層常數不再報」

這一項不是放寬,是把慣例換掉。新 pattern 不含底線,Kotlin 官方慣例和 detekt 預設的 SCREAMING_SNAKE 頂層常數,會從沒事變成被報。文件卻寫成「PascalCase 不再報」,漏講了這個副作用。

具體失敗場景:任何專案(含非 Compose)在改到的檔案裡新寫 `const val MAX_ITEMS = 5`,推送前新增告警閘就會擋。S3 測試只用 PascalCase 常數 `Brand`,沒有 SCREAMING_SNAKE 案例,抓不到。

最小重現(`const val MAX_ITEMS`、`const val MaxPascal`、`private const val DEFAULT_TIMEOUT_MS` 三行的檔):
```
$ detekt --input Const.kt --build-upon-default-config --config configs/detekt/android.yml
Const.kt:1:11: Top level constant names should match the pattern: [A-Z][A-Za-z0-9]* [TopLevelPropertyNaming]
Const.kt:3:19: Top level constant names should match the pattern: [A-Z][A-Za-z0-9]* [TopLevelPropertyNaming]
$ detekt --input Const.kt --build-upon-default-config      # 預設設定
Const.kt:2:11: ... [A-Z][_A-Z0-9]* [TopLevelPropertyNaming]   # 只報 MaxPascal
```
建議把 pattern 改成 `'[A-Z][A-Za-z0-9_]*'` 讓兩種寫法都過,並補一個 SCREAMING_SNAKE 案例進 `t_detekt_compose_rules_shared_config`。

## F2
severity: minor
blocking: 否
位置:`scripts/lumos` 的 `_android_ci_has_lint_task`。

引句:「if name in ("lint", "check", "build"):」

只看字面的判法有兩個誤判,方向都是讓 A1 該印卻不印:
- 排除 lint 的寫法 `-x lint` 被當成有跑 lint。
- 註解裡的字樣也算數。

實測(`build.gradle.kts` 有 `com.android.application`、`.github/workflows/ci.yml` 只有一行):

| 那一行 | A1 次數 |
|---|---|
| `./gradlew assembleDebug -x lint` | 0 |
| `./gradlew detekt  # TODO add lint check later` | 0 |
| `sh ci/run.sh   # runs gradlew lintDebug` | 0 |
| `./gradlew ktlintCheck detekt` | 1(正確) |

計劃的〈實務隱患〉只承認「包在 shell 腳本」會多印提醒,沒提這個少印的方向。

## F3
severity: minor
blocking: 否
位置:`docs/lumos-toolchain-knowledge/Systems/linter精選目錄.md` 第 181 行(新增)。

引句:「A2(用 Compose 但三套 Compose 規則一套都沒接)」

Compose 規則只有兩套(Slack compose-lints、compose-rules)。計劃寫「兩套」,A2 的程式文字寫「Compose 規則哪裡都沒接」。同一句也沒提 A3,但同一份文件上面寫了 A3。

## F4
severity: minor
blocking: 否
位置:`docs/lumos-toolchain-knowledge/Systems/linter精選目錄.md` 第 160–185 行。

引句:「### Android Lint 與 Compose lint 標準接法(2026-11-06 立,[[Projects/Android現成檢查接上CI與推送前_計劃]])」
引句:「- 接完跑 `lumos lint-check --smoke` 驗宣告真跑得動」

新章節插在 detekt 標準接法中間。原本屬於 detekt 的三條(「這個樣板拿不到型別資訊」「自有設定要跟共用設定疊加」「接完跑 lumos lint-check --smoke」)現在掛在 Android Lint 標題底下。

接手的人會以為「用逗號疊加 --config」「--smoke 冒煙」是 Android Lint 的步驟。這三條實際只適用 detekt,Android Lint 走 Gradle,冒煙不適用。應把新章節移到那三條之後。

## F5
severity: minor
blocking: 否
位置:`docs/lumos-toolchain-knowledge/Systems/linter精選目錄.md`,外掛下載指令。
可信度低:`gh` 在我這個席被攔,指令本身沒能實跑。

引句:「gh release download v0.4.28 -R mrmans0n/compose-rules -p 'detekt-compose-0.4.28-all.jar'」

- 文件指令用 `gh`,同一版 CI 步驟用 `curl`,用 `curl` 的 GitHub 網址我實測可下載。
- 文件沒寫 `gh` 要先裝、要先登入這個前提。
- 檔案已存在時重跑,`gh` 預設會失敗(沒帶 `--clobber`)。

建議改成和 CI 同樣的 `curl -sSfL -o … "https://github.com/mrmans0n/compose-rules/releases/download/v0.4.28/detekt-compose-0.4.28-all.jar"`。

## 各鏡頭結論(未列成 finding)
- **Gradle 片段**:`lint { baseline; warningsAsErrors; checkDependencies; sarifReport }`、`lintChecks(...)`、`detektPlugins("io.nlopez.compose.rules:detekt:0.4.28")` 和 `config.setFrom(files(a, b))` 的寫法,對照官方 DSL 沒找到錯誤。Slack 外掛版本表(AGP 加 23)我沒能獨立驗證,計劃已掛 REVISIT:2026-12-15。
- **型錄〈統計〉**:數字未受影響,該節沒有批次欄的計數。改標後 176 列批四拆成 75 現成規則、75 Android Lint、19 兩者、7 compose-rules,合計與改前的 176 一致。
- **句子變假**:SKILL.md 的「32 條」和「加掛 compose-rules 補整組」已改。linter 目錄 KEY 與 FACT 提到的「共用設定開的五條」仍然成立,因為六項是放寬而不是新開。
- **舊 lumos 讀新 lint.json**:第二條宣告對舊版只是又一條 detekt 命令。外掛檔不在時,新增告警閘照既有行為判環境不可用並自動放行。`--json` 的 `advisories` 只在 `lumos` 內部被輸出,沒有別處消費。
- **已照舊範本接 detekt 的消費專案**:拿到新 android.yml 後,推送前會少擋 MagicNumber 的屬性宣告、有預設值的長參數、Composable 命名、Preview 沒被呼叫、Preview 函式數,這幾項計劃有承認。多擋的只有 F1。
- **圖譜鏡頭**:五篇 Systems 筆記(lint-declaration-health、linter精選目錄、kotlin規則包、bound-tests-gate、pitfalls-code-loop)沒有行為或合約被破壞。
  - 新加的 WHY 與 PITFALL 摘要行,必有鍵齊全,`[test:]` 指到的 `t_*` 在 `scripts/test_lumos.py` 都存在。
  - 唯一弱點是 PITFALL 的 `[根因:…(推測:…)]` 自承是推測。
  - pitfalls-code-loop 不受影響,因為 diff 沒碰風險分級程式。
- **LUMOS-IMPACT 範圍**:派工詞附的範圍算不出,我改讀指定的五篇筆記,已在上面逐篇判過。

## 總結
總結:最嚴重是 major,會擋 1 條(F1),另 4 條不擋(F2–F5)。

審查用的臨時目錄是 `/private/tmp/lumos-seat-work/code-android現成檢查/接手-sonnet`,收貨後請編排者刪。repo 沒有被我改動。
