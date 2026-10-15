severity: major

以下用 `/tmp/lumos-seat-work/code-前端知識與風險詞/通才-sonnet/` 的實驗驗證。修後版本是 20df2187,修前版本是 f14f6808(`before_lumos`)。

1. 「給」留作單字去處,跟被拿掉的「對、向、至、往」是同一個根因(r2 通2 major)
severity: major
- blocking: 是
- 問題:修補以「前端日常句常含這幾個字」為由拿掉單字去處,卻留下「給」。前端日常句同樣常含「給」(傳給父元件、顯示給使用者、給出)。
- 具體例(輸入→預期→實際,修後):
  - 輸入「表單送出後把資料傳給父元件」「請求送出後回傳給呼叫端」「表單送出後給出錯誤提示」「請求送出後顯示給使用者」「請求送出後狀態交給 reducer」。
  - 預期:跟「表單送出後顯示對應的結果」一樣不算對外送出。
  - 實際:`_door_keyword_hits` 全部回 `對外送出`。
  - 這五句輸入我另外在修前版本只驗了其中一句,其餘四句沒有逐版對照。
- 佐證:修補自己的 S55 `t_door_keyword_send_frontend_everyday_not_hit` 清單裡一句「給」都沒有,所以測試照綠。S54 的 ① 反而要求「給」單字一定命中。
- 歸因:有證據的原有漏查。修前版本本來就把「給」列為去處;這個修補只拿掉其他單字,同類沒掃完。
- 嚴重度說明:這個例外只會比裸字少命中,所以這些誤報不比不加例外更糟。我仍判 major,理由是 r2 宣稱要解的前端日常句沒有解完。
- 引句:「前端日常句的對應、對話框、至少、往下、導向、跳到、回到、收不到都含這幾個字(代碼審 r2 通2 major、邊3、正4,編排者裁)」

2. 同一個送出子句規則,門與 pitfalls --check 對全形句點、全形冒號判斷不同(修補造成的新分歧)
severity: minor
- blocking: 否
- 問題:門先做 NFKC,「．」變成「.」,後面接英數就不切子句。`--check` 不做 NFKC,「．」(U+FF0E)在 `_PITFALL_SEND_STOPS` 裡,而 `[.:](?=[A-Za-z0-9/])` 的例外只認半形,所以照切。
- 具體例:
  - 輸入「送出請求向 a．b 給」。修後:門回 `對外送出`,`_pitfall_scan_classes` 不回 `external-send`。
  - 修前:兩邊都回命中。
  - 輸入「給 a．b 送出請求」「給 https：//x 送出請求」也是門命中、`--check` 不命中。
- 佐證:S58 `t_door_keyword_send_nfkc_stops_both_paths` 只驗三個「純標點」句,沒有「全形點後接英數」,所以宣稱「兩條路一致」沒被守住。
- 歸因:有證據的修復回歸(修前 `True True`,修後 `True False`)。
- 引句:「這樣兩條路才一致;t_door_keyword_send_nfkc_stops_both_paths 對全碼位驗);點與冒號後面緊接英數或斜線時不切(網址、主機名,代碼審 r2 邊4)。」

3. 只有程式檔副檔名才算「測試基礎設施」,e2e 資料夾下的 .sql、.yml 等檔重新被掃出 claims
severity: minor
- blocking: 否
- 具體例:
  - 在臨時 git repo 提交 `e2e/seed.sql`,內容 `DELETE FROM users;`。
  - 修前:`_pitfall_diff_collect` 的 claims 為 `[]`。
  - 修後:claims 為 `[('e2e/seed.sql','併發')]`。
  - `e2e/reset.py` 修前修後都跳過。
- 佐證:`_is_test_infra_file` 多加了副檔名條件,`_stack_changed_ok("e2e/seed.sql")` 為 True。S61 只為 .kt 寫了這個行為,沒涵蓋 .sql 等資料型副檔名。
- 歸因:有證據的修復回歸,但行為是作者刻意改的,所以交編排者 ⚠:註解把意圖寫成「e2e 腳本與 e2e 資料夾裡的 sh/py/ts/js 家族」,沒說明 .sql 為何要重新掃。
- 引句:「return Path(file_rel).suffix.lstrip(".").lower() in _INFRA_CODE_EXTS and bool(_TEST_INFRA_PATH_RE.search(file_rel))」

4. 「送出 + 表單/請求 + 至/向 + 外部目的地」不再命中(守衛放寬)
severity: minor
- blocking: 否
- 具體例:
  - 「送出表單至客服信箱」「送出請求向 api.x.com」:修前回 `對外送出`,修後 `set()`。
  - 「送出表單至客服信箱」是測試 S32 原本明列要照算的句子,被改成「送出表單到外部客服」(靠「外部」)。
  - 這種「送給外部卻沒寫外部名詞」的真送出,現在放行。
- 歸因:有證據的修復回歸,屬設計取捨。計劃已寫明接受,我只在此記下涵蓋範圍縮小。
- 引句:「(代碼審 r2:單字去處至、往、向、對、予與到拿掉)」

5. 沒找到問題的部分(已驗)
- xargs 新式 `_INFRA_CMD`:各種病態輸入(兩萬個 `-a`、兩萬組 `-a b`、兩萬個空白、四萬個 `-`)都在 0.1 秒內跑完;`kill` 選項變體由 S59 涵蓋。
- 送出子句視窗:十萬字、兩萬個送出,0.13 到 0.34 秒,線性。
- `_TEST_INFRA_PATH_RE` 與 `_is_test_infra_file` 的呼叫者:`scripts/lumos:30330`(`_stack_key_for_file`)與 `scripts/lumos:47373`(claims)。除了 helper 內部和註解,沒有其他地方直接用 `_TEST_INFRA_PATH_RE`,沒有漏掉的呼叫者。
- `e2e/lib/x.ts` 的路徑判斷:修前 `None`,修後 `infra`。

6. 修補深度(角度 7)
- 三輪下來送出例外一直在同一個正則上加特例,這一輪是收窄。比起繼續列去處字,更簡單的通用規則是只認外部名詞,連「給」也拿掉(即上面第 1 條)。

三個修補問題的答覆:
- ① 原問題的修復效果:單字去處「對向至往到」的前端日常句誤報已解,有 S55 與我自己的跑法為證。xargs 二次方已解,實測。e2e 內層 lib/src 已解,實測。
- ② 修補處的相鄰路徑:「給」未解(第 1 條)。門與 `--check` 一致性被打破(第 2 條)。e2e 非程式副檔名的 claims 行為改變(第 3 條)。
- ③ 同一案例的修前修後:第 2、3、4 條已附兩版結果。第 1 條在修前版本同樣命中,我只驗了其中一句(「表單送出後顯示結果給使用者看」),其餘四句沒有逐版對照。

我沒有跑測試套件(`test_lumos.py`)。S54 到 S62 的實際翻紅能力我沒有逐條做破壞驗證,未判定。

最嚴重 severity:major,blocking 共 1 條。
