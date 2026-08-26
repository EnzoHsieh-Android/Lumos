### arch-f1 spec 的驗證內容是第三套邏輯,違反「共用驗證函式」既有做法
severity: major
引句:「宣告的 linter 指令存在於 PATH 的提示級檢查」
佐證:file: `scripts/lumos:10880`
佐證:file: `docs/lumos-toolchain-knowledge/Systems/lint-declaration-health.md:71`
說明:_lintcheck_validate 現有四種 problem 無必填鍵無 PATH;該筆記待辦明文「靜態層併入 doctor --ci」=複用非重寫;doctor 對已驗過的東西慣例=共用函式(Check J 例)。spec DEP 漏列該筆記。

### arch-f2 [LINT] 用完整單字破壞 doctor 段落單字母代號慣例
severity: minor
引句:「doctor --ci 加 [LINT] 檢」
佐證:file: `scripts/lumos:690`
說明:既有代號一律單字母/字母+數字。

### arch-f3 revalidate_when 寫進 Systems 筆記=lumos stale 掃不到,回頭條件形同沒掛
severity: major
引句:「速度理由的刻意裁定寫進 [[Systems/pitfalls-code-loop]](現況只在 hook 註解)」
佐證:file: `scripts/lumos:6701`
佐證:file: `scripts/lumos:8555`
說明:stale --candidate 硬過濾只掃 Verification/;system 範本無 revalidate_when 欄。鐵則四靠這條指令機械掃——寫錯位置=架空。

### arch-f4 [S2]「寫進筆記」沒指明形狀(decisions/KEY/散文)
severity: minor
引句:「pre-push --no-lint 明文入 pitfalls-code-loop 筆記+revalidate_when」
佐證:file: `docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md:38`
說明:該筆記裁定慣例=decisions 結構化(decision-add);落散文=偏離。

## 對齊良好的面
無宣告跳過語意同 Check C/D 慣例;紅=CI 擋吃 run_doctor 既有 strict 機制;[S3] 與 lint-declaration-health 既有邊界字面一致;三不動邊界尊重模組界線。
