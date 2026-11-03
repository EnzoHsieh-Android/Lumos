severity: minor

# 紅燈版實跑三缺口 r1 正確性席報告

整份 spec 我逐節讀完,也都對程式碼實跑過。最高等級是 minor。做法 1 的退步我專門追了,在能通過 `_tg_functions` 的輸入下找不到比現況更差的案例。找到 6 條 minor,其中 4 條各給了可重現的輸入。我的臨時目錄已刪。

## 做法 1:切參數遮罩

我用 30 種 Kotlin/Java 寫法兩兩配對,拿現況與「遮罩與原文深度都為 0 才切」比。寫法包括雙引號字串、字元常值、三引號、反引號識別字、字串模板、巢狀引號等。新規則沒有比現況差的案例,字串逗號、`','`、三引號、反引號識別字都修到了。

我另試了「模板裡的巢狀字串含 `//`」與「模板裡的 `'"'`」。直接呼叫 `_tg_call_parts` 時,遮罩掃描會把該行後半吞成註解或字元常值,新規則因此一個逗號都不切,比現況退步。但這兩種輸入在進到它之前,`_tg_functions` 就已回 `ok=False`(括號配不平),整支測試檔被略過,所以不算 finding。

**finding 1:字面括號不成對的範圍比 spec 寫的大,而且沒有回頭條件**
severity: minor
blocking: 否——現況行為不變,不是退步,實作者不會因此做錯。
- 段落:做法 1 末句「已知不處理:字串裡有不成對的括號時(`"a(b"`)…」
- 問題:不成對的不只 `"a(b"`。字元常值 `'('`、`')'`,以及字串 `"("`、`")"`、`"{"`,放在被比對的逗號之前都會切不到。這些剛好是第一個參數(預期值)的位置,例如 `assertEquals(")", t.text)`。
- 佐證:
  - `_tg_call_parts('assertEquals(")", lexer.next().text)')` 回 `['")", lexer.next().text']`,只有一個參數。
  - `'('`、`"服務費 (含稅"`、`"共 3 項 :)"` 結果相同。
  - 一個預期值字串從 `")"` 改成 `"]"` 仍然漏報,只有一個參數時 `_tg_split_first_arg` 回 None。
- 補充:orig 深度檢查只是為了防 `${...}` 模板裡的巢狀引號。只對含 `${` 的字串才加這道檢查,就能收窄這個缺口。
- 缺漏:這句「已知不處理」沒有附回頭條件,違反 CLAUDE.md 鐵則 4。

**finding 2:鏈式呼叫那次切參數沒被點名,空白差異漏報**
severity: minor
blocking: 否——S1 的 assertEquals 路徑照樣修到,實作者最壞是漏改鏈式那一處。
- 段落:做法 1 全節;S1 只舉 `assertEquals`。
- 問題:`_tg_call_parts` 裡有第二處 `_rg_split_args(stmt[mm.end():en], angle=False)`,處理 `.isEqualTo(...)` 與 `.containsExactly(...)`。spec 沒說這處也要帶遮罩。
- 佐證(跑 `_tg_expected_changed(_tg_ident(old), _tg_ident(new))`):
  - `assertThat(x).isEqualTo("a, b")` 改成 `"a,b"`,回 False,漏報。原因是被切成 `['"a','b"']` 後用 `","` 接回,逗號後的空白丟了。
  - `"a,  b"` 改成 `"a, b"` 同樣回 False。
  - `file: scripts/lumos:48983`

## 做法 2:留痕記平台、推送前補平台

**finding 3:帶前綴的名字遇到平台未定義會直接崩潰**
severity: minor
blocking: 否——只在設定改名或刪平台之後才發生。
- 段落:做法 2、相依段「`_spec_gate_push_one` 解析 `[test:…]`,本來就認前綴」。
- 問題:`resolve_test_refs` 遇到未定義的前綴會丟 `_TestRefPrefixError`,而 `_spec_gate_push_one` 與 `_spec_gate_push_check` 都沒接。
- 失敗場景:
  - 完成後的計劃(`done` 且指紋不符)走寬待路徑。平台 `device` 之後改名或移除,舊裸名會降級成「留痕裡的測試找不到」提醒,不擋。新寫的 `device:Foo` 則直接崩出 traceback。
  - 只有預設平台的名字含 `詞:` 時,裸名同樣會崩。這是既有缺陷,spec 的「預設平台照舊寫名字」把它留著。
- 佐證:
  - 實測 `[test:fee: rounds]`(預設平台 android)丟 `_TestRefPrefixError`。
  - 實測 `[test:tablet:Foo]`(平台未定義)同樣丟錯。
  - file: `scripts/lumos:15939`,`scripts/lumos:6474`
- 補充:Kotlin/JVM 方法名不能含冒號,考場不會碰到。「舊讀者不受影響」這個理由也站不住,因為 spec 自己承認舊讀者本來就認前綴。

**finding 4:做法 2 有兩處可執行性缺口**
severity: minor
blocking: 否——是缺口,不會讓實作者做出錯的行為。
- `_spec_gate_push_stale` 只回 `(原因, now)`,沒有帶出 `text` 與 `clauses`。S3「看現在計劃條款裡同名的引用」需要這兩樣,spec 沒說是改回傳值還是在 `push_one` 裡重讀。
- 現行 tests 來源 `names` 含所有條款的引用,`_spec_gate_items` 只含 `state=="bound"` 的。spec 沒說 tests 欄改從哪邊建。dangling 的名字在 `items` 裡沒有平台,可能被誤寫成裸名。
- 佐證:`scripts/lumos:14186`、`scripts/lumos:14887-14899`、`scripts/lumos:15544-15575`

## 做法 3:治理帳被忽略的判法

我拿暫存 repo 實測 git 行為:
- `-q` 對否定規則(`!`)回 1,對已追蹤的檔回 1。
- `-v` 對上層目錄規則(`docs/`)顯示 `docs/` 那一行,規則來源與行號都取得到。
- 先 `ls-files` 再 `-q` 再 `-v` 的順序判得對,spec 對這些情況的描述屬實。

**finding 5:git 呼叫沒走截止時間,失敗時的行為沒寫**
severity: minor
blocking: 否——只在 git 卡住時才多等,不會判錯。
- 段落:PRIOR-ART 與做法 3。
- 問題:spec 指定用 `_lens_git`,但比對工具這一帶一律用 `_lens_git_dl(…, deadline=deadline)`,例如 `_tg_rb_deleted`。三次呼叫各最多 20 秒,不受比對工具總截止時間約束。
- 另外三點 spec 都沒寫:
  - `check-ignore` 回 128 或 None 時沿用哪句提醒。
  - `_tg_rb_metas` 現在沒有 root 參數,要加上去。
  - 「一次推送最多問一次」要靠呼叫端傳快取,而不是在純函式裡記。
- 佐證:`scripts/lumos:64496`,`scripts/lumos:49733`
- 判得對的部分:ident 改固定字後,key 公式是 sha256(rule, file, ident, nth),message 不進 key,所以兩種措辭的指紋相同。紅燈版功能只在 `spec-snapshot-guard` 分支,帳裡也沒有 `redbase-unreadable` 的放行紀錄,「沒有既有放行」成立。

## 實務隱患

**finding 6:實務隱患節的排除理由,有一個沒涵蓋的使用情境**
severity: minor
blocking: 否——是理由不完整,不是行為錯誤。
- 段落:實務隱患的「已排除:不可逆」「對外送出」。
- 問題:兩條排除理由只講「改判讀、提醒文字、tests 欄前綴」,沒提做法 2 修好後推送閘真的會跑 `device` 平台的指令。
- 失敗場景:
  - 推送機器沒接平板時,verdict 是 weak 或 red。`_spec_gate_push_one` 對任何非 green 都呼叫 `_auto_escape`,所以仍會自動記假逃逸,和問題 2 抱怨的是同一種假逃逸。
  - 規格閘 KEY 第 34 行也白紙黑字寫「任一非綠擋並自動記逃逸」。
  - 平板上有 production 資料時,`connectedAndroidTest` 可能清掉 app 資料。
- 佐證:`scripts/lumos:16036-16049`

各風險類的結論:
- **金流**:排除成立,spec 只動判讀與提醒。
- **對外送出**:排除大致成立,但沒提到會對平板跑指令(見上)。
- **不可逆**:排除理由不完整(見上)。
- **併發**:無新增風險,新增的 git 呼叫只讀,留痕寫入路徑不變。
- **效能**:一趟線性掃描,遮罩長度我用 2 萬筆隨機字串驗過與原文一致。git 呼叫的逾時見 finding 5。
- **回滾**:新留痕帶前綴,舊程式讀得懂;回退後舊留痕仍可用。唯一的洞是 finding 3。
- **相容**:舊裸名走 S3 補平台。我驗證了 `_clause_block_sha` 對條款行去掉行內程式碼後仍保留 `[test:device:` 這段,所以平台前綴確實進指紋,「指紋相符 = 條款綁定沒變」成立。

## 其他節

- 名詞、問題與最小解、驗收條款 S1 到 S6、回退:已讀,無 finding。
- `lumos loop escape --withdraw`、`lint-waive`、`_spec_gate_low_not_red`、`_local_ledger_doctor_msgs`、`_lens_git`、`_redbase_attach`、`_tg_rb_bad` 的 ident 參數都存在,語意與 spec 描述一致。
- 「舊留痕實作完成後重跑不會被重寫」與 `_spec_gate_low_not_red` 的 (a) 路徑一致。

## 固定席

- `Systems/規格閘`:不影響。該節 20 行 KEY 沒有 ★INVARIANT★ 合約。KEY 第 34 行的推送前流程是「指紋對不上就擋 → 非綠擋並自動記逃逸」,S3 補平台發生在指紋比對通過之後,不改這個順序。第 50 行 WHY 的「測試身分是(平台、測試名)」與做法 2 的方向一致。
- `Systems/test-guard`:不影響。WHY 第 37、41 行要求孤兒檔仍拿內容比、訊息不叫人刪檔。做法 3 只換措辭和身分字,新措辭沒有叫人刪檔,仍會比內容。

最嚴重 severity 是 minor,blocking 共 0 條。

涉及檔案:
- `/Users/enzo/harness/lumos-redbase-realrun/scripts/lumos`
- `/Users/enzo/harness/lumos-redbase-realrun/governance/review-reports/紅燈版實跑三缺口/r1-snapshot.md`
