severity: minor

我只讀了凍結 patch 和既有對照檔,沒改任何檔。工作樹已是 ff4e9ebdd,所以行號都對這個版本。

**1. 分層與依賴方向:對齊。**
- 新驗證紀錄放在 `Verification/`,開頭有 `plan_refs` 與 `system_refs`。對照 `Verification/2026-11-08_detekt的CI型別檢查範本實跑.md:1-16`,欄位一樣。
- 範本改寫都落在範本的家 `Systems/linter精選目錄.md`,並用 `verified_by` 連回驗證紀錄。
- 計劃只補了一行〈審計修正紀錄〉的「實測更正」和一個 REVISIT 的 `[closed:]`,沒有把範本內文塞進計劃。
- 別人的檔(`lint-baseline.xml`、`gradle.properties`)是消費專案的檔,不在圖譜節點的家內。反引號寫法跟既有的 `baseline-debug.xml`、`app/build.gradle.kts` 一樣。
- 計劃那行寫的是 `[[Systems/linter精選目錄]]` 連結,不是搬內容。沒有放錯層。

**2. 命名與寫法:大致對齊,有兩處小差異(A1、A2)。**
- 檔名 `2026-11-09_<主題>`、`> 白話:` 開頭、`## 怎麼跑 / ## 結果 / ## 範本與實測對不上的`,跟 `Verification/2026-11-08_detekt的CI型別檢查範本實跑.md:16-37` 一致。
- 摘要行一致:
  - PITFALL 帶 `出處`、`根因`、`repro`(三選一),另有選填的 `修法`,縮排兩格,位置對照 `Systems/linter精選目錄.md:164-167`。
  - REVISIT 是日期寫法。
  - 關掉舊 REVISIT 用 `[closed:日期 一句]`,跟 `Projects/Android儀器測試範本與架構測試_計劃.md:59` 的 closed 寫法相同。
  - 計劃的「實測更正(日期,S5)」跟同節「實作更正」「推送閘更正」同型。
  - `verified_by` 加了一行。

**3. 第二種做法:沒有。**
- 範本第 1 步說「版本跟本機 CLI 同一版 1.23.8」,AGP 9 段改成 2.0.0-alpha.6,兩者並存。但它掛在 AGP 9 的條件下,有寫明理由,還交代共用設定為何仍用 1.23 的鍵名,所以不算另一套挑版本法。
- Slack 版本仍用「建置 lint 不高於專案 lint(AGP 加 23)」一條規則,新增的 1.5.2 預設關屬於「預設值」說明,沒有另立挑法。
- 回頭條件仍是 `REVISIT:日期` 與 `[closed:]`,沒用別的寫法。
- 計劃收尾是改 `status` 加審計修正紀錄一行,跟 `277977ea5` 同一套。

## 發現

A1 四篇計劃改成 done,但沒有更新 `updated`。
severity: minor
blocking: 否
引句:「updated: 2026-11-06」
file: `docs/lumos-toolchain-knowledge/Projects/Android的detekt推送前真的擋_計劃.md:4`
- 上一次收尾(提交 `277977ea5`)把該計劃從 `status: doing` 改成 `done` 時,同時把 `updated` 改成 2026-11-08(`created` 是 11-04)。
- 這次四篇(儀器測試、行為測試、語意情境、現成檢查)全都只改了 `status` 與 `tags`。patch 的 hunk 裡 `updated` 仍是 2026-11-06(語意情境那篇是 11-06,`created` 是 11-05)。
- 現成檢查那篇連內文都改了,`updated` 也沒動。

A2 驗證紀錄用的錯誤寫法,跟計劃預期值表指定的不同,也沒說明。
severity: minor
blocking: 否
引句:「(會發出畫面卻沒有 modifier 參數)」
file: `docs/lumos-toolchain-knowledge/Projects/Android現成檢查接上CI與推送前_計劃.md:107`
- 計劃 S5 的預期值表指定的是「沒包 remember 的 `mutableStateOf`」,依據是 compose-rules 的 RememberMissing。
- 驗證紀錄改用「缺 modifier 參數」(ModifierMissing,Slack 的 `ComposeModifierMissing`),卻沒有在〈範本與實測對不上的〉或〈怎麼跑〉交代為何換。
- 鄰居 `Verification/2026-11-08_detekt的CI型別檢查範本實跑.md:34-38` 的做法是:實測跟預期不同就列進「對不上的」。⚠ 這可能是刻意簡化,但紀錄裡看不出來。

不對齊共 2 條,其中 major 0 條
