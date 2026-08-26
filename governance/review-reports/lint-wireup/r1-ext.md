否決成立。消費 repo 的接線存在可達性缺口，PATH 檢查另有假紅／假綠雙向反例；smoke 則仍未形成可執行責任鏈。

### ext-f1

severity: blocker

引句:

> 此檢為消費 repo 服務

佐證:file: `scripts/hooks/pre-push:159`

佐證:file: `scripts/hooks/pre-push:164`

佐證:file: `scripts/hooks/pre-push:166`

佐證:file: `scripts/lumos:9463`

說明:

消費 repo 的 vendored pre-push 在呼叫 `doctor --ci` 前，會先檢查是否存在 `docs/*-knowledge` 或 `docs/knowledge`；沒有 vault 就在第 164 行直接成功退出。另一方面，lint adapter 本身可在 vault-free repo 使用，但 spec 沒要求 `.lumos/lint.json` 存在時繞過這個提前退出。

因此存在致命反例：消費 repo 有 `.lumos/lint.json`、沒有知識 vault；push 時整支 doctor 根本不執行，新 `[LINT]` 段永遠不可達。工具鏈自己的 GitHub workflow 不能補洞，vendor 清單只複製工具與 hooks，沒有證據顯示會把 `.github/workflows/ci.yml` 安裝到消費 repo。

### ext-f2

severity: blocker

引句:

> schema 必填鍵、宣告的 linter 指令存在於 PATH 的提示級檢查

佐證:file: `scripts/lumos:10880`

佐證:file: `scripts/lumos:10884`

佐證:file: `docs/lumos-toolchain-knowledge/Systems/lint-declaration-health.md:20`

佐證:file: `docs/lumos-toolchain-knowledge/Systems/lint-declaration-health.md:21`

說明:

「指令存在於 PATH」沒有可成立的一般判定：

- `java -jar /tmp/missing.jar ...` 的首指令 `java` 在 PATH，靜態檢查會綠，但真正 linter 已不存在；repo 記錄的 KDS 真實事故正是這型。
- `./gradlew lint ...`、repo-local wrapper 或絕對路徑工具可以正常執行，卻不屬於 PATH，會在 CI 假紅。
- shell 組合、環境變數前綴及 pipeline 也無法安全等同於「第一個 token 可由 PATH 找到」。

現有合約明定靜態層只驗格式，工具、task、jar 是否存在只能由 smoke 判斷。spec 新增 PATH 判定，卻未定義 shell 解析規則、repo-local executable 規則及 advisory 如何與「紅=CI 擋」相容，也沒有任何 PATH 假紅測例。依目前文字無法實作成可靠 gate。

### ext-f3

severity: major

引句:

> smoke 裁維持手動

佐證:file: `docs/lumos-toolchain-knowledge/Systems/lint-declaration-health.md:21`

佐證:file: `docs/lumos-toolchain-knowledge/Systems/lint-declaration-health.md:43`

佐證:file: `docs/lumos-toolchain-knowledge/Systems/lint-declaration-health.md:54`

佐證:file: `docs/lumos-toolchain-knowledge/Systems/lint-declaration-health.md:71`

說明:

repo 證據已記錄同一易失 jar 事故在 2026-07-17 發生後，又於 2026-07-27 重演；同一份證據也明說 smoke 是唯一能抓到工具、task 或 jar 實際不存在的守衛。

本案只寫「KDS 下次真機驗證必跑」，沒有排程、hook、CI job、setup 指令、責任人或能驗證「下次確實跑過」的 gate。這不是接線，只是把「smoke 無排程」改名為「維持手動」。而 S1 的 PATH 檢查又無法取代 smoke，故已知真實失效模式仍原封不動。
