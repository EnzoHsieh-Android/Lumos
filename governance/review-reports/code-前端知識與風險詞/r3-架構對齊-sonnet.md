severity: major

我只審結構,沒跑 `pitfalls --diff`,也沒跑測試。我讀了兩份 patch(`r3-code.patch` 與 `r3-repair-code.patch`),並對照 `scripts/lumos` 在 20df2187 的既有寫法。

## 1. 分層與依賴方向:對齊

- **依賴方向**:新常數 `_PITFALL_SEND_*`、`_PITFALL_PAYMENT_WHEN` 放在 `PITFALL_CLASSES` 正上方,由它引用,再由 `_PITFALL_COMPILED` 統一編譯。門(`_door_keyword_hits`)與 `_pitfall_scan_classes` 都只從 `_PITFALL_COMPILED` 取詞表,沒有新增跨層直呼。
  - file: `scripts/lumos:29921`(`_PITFALL_SEND_WHEN`)
  - file: `scripts/lumos:29934`(`_PITFALL_COMPILED`)
  - file: `scripts/lumos:8284`(門的消費端)
  - file: `scripts/lumos:47612`(`pitfalls --check` 的消費端)
- **前端面**:`_REQ_FE_WHEN` 與 `_req_frontend_hit`、`_req_frontend_facets`、`_req_frontend_hint` 緊接 `_REQUIREMENT_FACETS` 之後。三個入口(`--stage`、計劃模式、`--check`)都比全文,方向是「入口呼叫小函式」,跟鄰居一致。
  - file: `scripts/lumos:29970`
  - file: `scripts/lumos:29984`
  - file: `scripts/lumos:47887`(`_pitfalls_check_print` 抽出)
- **infra 題組**:`_STACK_QUESTION_SPECS["infra"]` 沿用 `_STACK_QUESTION_SPECS[_stk]` 的 `when`/`when_raw` 形狀。
  - file: `scripts/lumos:30247`
  - file: `scripts/lumos:30095`(既有 `when_raw` 用法)
  - 鍵由 `_stack_key_for_file` 第一條規則給(`scripts/lumos:30330`),符合該函式「兩個消費者都走這一支」的註解。
- **跳過名單**:`_arch_alignment_hints(..., skip=frozenset())` 沿用 `_stack_changed_ok(cur_file, vend_skip)` 的 `vend_skip`,不是另一套名單。
- **`_is_test_infra_file`**:r2 後棧別鍵與 claims 跳過共用這一支,已收斂。

## 2. 命名與錯誤處理:大致對齊

- **命名**:`_WHEN`(字串,給 `PITFALL_CLASSES` 統一編譯)照 `_EXTCODE_WHEN` 慣例(`scripts/lumos:30029`)。
  - `_INFRA_B` / `_INFRA_E` 是新增的詞界常數,但各自語意明確(含底線),不衝突。
  - 題目 id 的 `<階段>-<主題>` 形式(`req-fe-*`、`arch-fe-*`、`impl-fe-*`、`perf-fe-budget`、`verify-infra-script`)跟 `scripts/lumos:29946` 的 `req-success` 等一致。
  - 測試名 `t_door_keyword_*`、`t_infra_*` 依既有 `t_` 前綴。
- **訊息形狀**:`_pitfalls_check_print` 保留原有的 `✗ pitfalls --check: 命中風險類 …` 與 `✓ pitfalls --check: …` 兩行,rc 仍是 1 或 0,只在後面追加提醒。
- **回傳碼**:沒有新增回傳碼。
- **前端提醒開頭**:用「提醒:…」,對應 `pitfalls` 既有的「擋下:」與「提醒」兩種前綴。
- **不算違規但值得知道**:`role: "frontend"` 的前端面(`scripts/lumos:29970`)與 `_ROLE_CARDS["frontend"]` 的 fe-race、fe-unmount、fe-states(`scripts/lumos:30344`)問題內容部分重疊。兩者階段不同(計劃期與代碼審期),`role` 值也對得上,所以我只在此記一筆,不列為不對齊。

## 3. 第二種做法:2 條(都標 ⚠ 交編排者)

**finding 1:門與 `pitfalls --check` 兩條路對 NFKC 差異的處理方式,跟既有做法不同**

severity: major
blocking: 否
引句:「# 這樣兩條路才一致;t_door_keyword_send_nfkc_stops_both_paths 對全碼位驗);點與冒號後面緊接英數或斜線時不切(網址、主機名,代碼審 r2 邊4)。」

- 既有做法:NFKC 與字元折疊只在 `_door_scan_text` 一處做。
  - file: `scripts/lumos:8238`(NFKC、`_DOOR_DASH_FOLD`)
  - 連字號變體也是折在門那一側,表另有全碼位測試守。
  - `pitfalls --check` 的 `corpus` 本來就不做 NFKC(`scripts/lumos:47858`)。
  - 專案裡其他詞(全形 `ｐａｙｍｅｎｔ` 等)是接受兩條路在 NFKC 上有差。
- 本修補的做法:`_PITFALL_SEND_STOPS` 把「NFKC 後含基本邊界字」的全部 BMP 碼位手列進正則的字元類,讓不做 NFKC 的 `--check` 路徑也一致(`scripts/lumos:29918`、`scripts/lumos:29919`)。
  - 這是專案裡原本沒有的第二種方式,而且只對「送出」一個詞生效。
  - 其他詞的兩條路 NFKC 差異沒有被同樣處理,因此兩種處理並存。
- 若要回到單一做法,有兩個方向:
  - 讓 `_pitfall_scan_classes` 也走 `_door_scan_text`;
  - 或接受 `--check` 不 NFKC,不做這張表。
- 要不要放行是設計裁量,所以標 ⚠。
- 另一個既有的子句邊界表是 `_NOGO_CLAUSE_SPLIT_RE`(`scripts/lumos:8076`,`[,,;;。:：]` 加關鍵字)。新表跟它並存,用途不同(不做節切子句,對 vs 送出去處窗口),我不單獨列。

**finding 2:e2e 與測試路徑多一支判斷**

severity: minor
blocking: 否
引句:「# 認 e2e、測試路徑的有四處,用途不同、不共用(代碼審 r2 架1,編排者裁放行):_PITFALL_DIFF_TEST_PAT 把測試檔整支排除;_testmap_is_test 是測試對照表認測試檔;」

- 既有的測試路徑判斷已有三支:
  - file: `scripts/lumos:30703`(`_PITFALL_DIFF_TEST_PAT`)
  - file: `scripts/lumos:48043`(`_testmap_is_test`)
  - file: `scripts/lumos:32831`(`_nodehome_is_test`)
- 新增的 `_TEST_INFRA_PATH_RE` 加 `_is_test_infra_file`(`scripts/lumos:30711`、`scripts/lumos:30715`)是第四支。
- 這一點 r2 已經由編排者裁放行,補丁也在註解裡寫明分工,並且讓棧別鍵與 claims 共用同一個入口(`_is_test_infra_file`)。
- 所以我只標 minor ⚠:若編排者想嚴格按「不准第二套路徑判斷」,可升為 major。

不對齊共 2 條,其中 major 1 條
