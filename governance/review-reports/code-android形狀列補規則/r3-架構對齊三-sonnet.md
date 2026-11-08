severity: minor

我沒有建任何暫存路徑,`/tmp/lumos-seat-work/code-android形狀列補規則/架構對齊三-sonnet/` 底下沒有東西要刪。

## 1. 分層與依賴方向

結論:對齊,沒有跨層直呼。

- **規則檔的家**:新規則放進既有的 `rules/api.yml`、`rules/architecture.yml`、`rules-unwired/architecture.yml`。這三處原本就按主題分檔、用 `---` 接在後面。
- **`rules-unwired/compose.yml`**:這支是新檔,但目錄由 `sgconfig-unwired.yml` 整層載入,不用另外登記。上一批移出規則包時刪過它,同一個位置重建不算第二種做法。
- **共用判斷**:`utils/has-registration-call.yml` 抽出給 UI-32 和 UI-33 共用。這跟 `utils/debug-only.yml` 同一套做法,四份 sgconfig 都用 `utilDirs: [utils]` 掛整個目錄。只在單檔用的判斷留在檔內 `utils:`(ARCH-59 的 `plain-provider`、ARCH-62 的 `entry-point-not-in`),符合規則包 WHY 寫的「跨檔才放 utils/」。
- **`check.py`**:`scan()` 回傳多帶一個行號,兩個呼叫端(`check.py:1044`、`check.py:1076`)和測試端都同步改成三元組,沒有漏的。
- **圖譜歸屬**:`has-registration-call.yml` 加進 `Systems/kotlin規則包` 的 `about_code`,跟 `debug-only.yml` 一樣掛在這個家。

## 2. 命名與錯誤處理

結論:結構對齊,有一條語意不一致要請編排者看。

- **規則 id 與訊息**:id 用 `kt-` 加主題;訊息是 `[型錄編號]…;改用/改成…`,沒有 `$`,跟 `message_problems` 的要求一致。
- **`ignores:`**:八項路徑排除跟 `rules/api.yml:253` 等既有規則逐字相同。
- **樣本**:放 `samples/{bad,good}/<id>/src/main/kotlin/<id>.kt`,有 `package bad/good`,壞例用 `// BAD`,好例用「容易誤報:」註解,跟鄰居一致。
- **測試表**:`_KTSEC_PLACE` 照 `(目錄, 檔, 編號)` 的寫法補四筆,選填欄還是 `_KTSEC_PLACE` 既有的位置欄,docstring 的翻紅釘照既有格式。第五欄預期行號、型錄不做規則列的實測欄寫理由,r2 已放行,我看過 `r2-intake.md`,理由成立,不重報。
- **型錄**:「現成規則」欄寫「自寫 ast-grep <id>」,跟 API-1、API-7 同形。「通電批次」欄寫「規則在 rules-unwired/:樣本外誤報超過一成或量不夠」,跟 DATA-99 逐字同句。
- **圖譜摘要行**:兩條 WHY 都有 `[出處:][因:][不選:][test:]`,格式對。

不對齊 1 條:ARCH-59 把規則放在 `rules/architecture.yml`,等級是 `warning`,卻在規則檔註解、型錄和計劃裡寫成「只列出不擋」。

⚠ 我沒能完全確定。規則包圖譜節點寫「`rules/` 底下 error 與 warning」都是會擋的規則,`rules/architecture.yml:23` 這類既有 warning 規則也照這個意思用;新增告警閘讀 SARIF 時 warning 也算命中(`scripts/lumos:9272`)。型錄這列通電批次寫「告警帶寫法=批一」,也是會擋的口徑。所以「不擋」跟同一包其他 `rules/` 的 warning 說法不同,真要不擋就該放 `rules-unwired/`。我沒有實跑閘去確認新增告警閘最後擋不擋 warning,請編排者裁。

引句:「只列出不擋(樣本外 68 處抽 40 處誤報 0;出處是建議語氣 As a best practice … error-prone,只放 warning)」

severity: minor
blocking: 否

## 3. 第二種做法

結論:沒有引入新機制。

- **掃描與讀取**:行號直接從 `scan()` 既有的 ast-grep JSON 輸出取,沒有另寫解析器。型錄主表用既有的 `main_rows()`,測試註解也寫明這點。
- **逐例表**:擴充既有的 `_KTSEC_CASES` 和 `_KTSEC_PLACE`,沒有另開一張表。
- **共用判斷**:沒有手抄 UI-32 的註冊字表,UI-32 和 UI-33 引用同一份 `has-registration-call`。
- **新常數**:`_KTSHAPE_CATALOG_IDS` 是新常數,但只是一個 tuple 加一段迴圈,讀的是 `_KTSEC_PLACE` 和 `main_rows()`,不算第二種做法。

不對齊共 1 條,其中 major 0 條
