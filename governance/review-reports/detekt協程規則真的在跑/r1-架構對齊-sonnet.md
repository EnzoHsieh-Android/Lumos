severity: major

這份設計把「換掉 linter 檢查對象」做了第二種做法,另有兩處規劃含糊(見四問)。我讀了被審材料,並對照 `scripts/lumos`、`scripts/test_lumos.py` 與兩篇家節點。我沒有改任何檔,也沒有建暫存目錄。

## 問 1 分層與依賴方向:大致對齊

- **新碼位置對齊**:冒煙探針接在 `cmd_lint_check` 的 `--smoke` 迴圈(`scripts/lumos:37758`),緊鄰 `_lintcheck_smoke_cmd`(`scripts/lumos:37737`)。計劃預期呼叫 `_lint_run_and_parse`(`scripts/lumos:38130`)。這跟冒煙、`cmd_rule_check`(`scripts/lumos:37963`)的依賴方向一致,沒有跨層直呼。
- **F 段位置對齊**:靜態提醒放在 F 段既有 if/elif 鏈之後、新增告警閘兩個數字之前(`scripts/lumos:4093` 起)。這個位置跟鄰居一致。
- **不對齊(minor)**:計劃寫「lint-check 與健檢 F 段都印一段提醒」,卻沒承諾兩處共用同一個判斷函式。這兩個入口既有的做法是共用 helper:`_lint_load_and_validate`(`scripts/lumos:37714`)的 docstring 明寫「不留兩份會漂移的複本」。

severity: minor
blocking: 否
引句:「lint-check 與健檢 F 段都印一段提醒;不改退出碼、不計入健檢問題。」
修法:計劃要明寫「偵測 + 提醒文字」只有一支函式,兩處呼叫。

## 問 2 命名與錯誤處理:大致對齊,三處規格含糊

- **對齊的部分**:
  - 測試名 `t_lintcheck_*` 跟 `t_lintcheck_cli`(`scripts/test_lumos.py:36086`)同族。
  - 探針缺規則記成 `{stack, issue}` 問題並回 rc1,跟 `cmd_lint_check` 的 problems 流程一致(`scripts/lumos:37786-37790`)。
  - 提醒不改 rc、不計問題,跟 `skipped_stacks` 的處理一致(`scripts/lumos:37803-37807`)。
  - 提醒用空清單的 `warn([])`,是 F 段既有形狀,見 `warn()`(`scripts/lumos:2045`)與 `scripts/lumos:4107`。

- **不對齊(minor):`--json` 輸出沒講**。
  - `cmd_lint_check` 在 `as_json` 時只輸出 `{"problems","declared"}` 就 return,人讀提醒(skipped_stacks)一律不進 JSON 模式(`scripts/lumos:37792-37795`)。
  - S2、S3、S4 都只描述人讀輸出。若實作時在 JSON 模式也印提醒,會污染 stdout,跟 `_lint_run_and_parse` 把 linter 輸出丟 DEVNULL 的理由(`scripts/lumos:38161`)衝突。
  - 修法:計劃寫明「提醒只在非 JSON 路徑」,或加欄位。

severity: minor
blocking: 否
引句:「S4] 當 kt 命令是 detekt 指令列且沒帶 `--classpath` 或 `-cp` 時,`lumos lint-check`(不帶冒煙)應 印型別資訊提醒而退出碼照舊」

- **不對齊(minor):探針規則 id 的比對方式沒講,會長出第二份比對邏輯**。
  - 鄰居 `cmd_rule_check` 用「完全相同,或以點分隔的最後一段相同」的規則(`scripts/lumos:38010-38012`)。註解說明了原因:不能用字尾,工具會加命名空間。
  - detekt 的 SARIF ruleId 帶前綴,計劃只說「比對探針五條有沒有響」。
  - 修法:計劃指定沿用同一規則,最好抽成共用小函式,不要在探針端再手寫一份。

severity: minor
blocking: 否
引句:「比對探針五條有沒有響」

- **⚠ 判不準,交編排者**:F 段用 `warn([])` 只能印一句標題,講不出是哪個棧、哪條指令。若提醒要點名指令,鄰居的作法是 `warn_soft(lines, …)`(新增告警閘放行狀況,`scripts/lumos:4150` 附近)。非空 `warn(lines)` 會把 `issues` 加上條數,違反「不計入問題」。計劃要先定提醒帶不帶逐條,再選函式。

## 問 3 第二種做法:有,且是 major

- **換 `--input` 有沒有繞過「全程式只准一處替換佔位符」的測試?**
  - 字面上沒有。`t_lint_files_substitution_has_one_implementation`(`scripts/test_lumos.py:17108`)的白名單制(`scripts/test_lumos.py:17138`)只看哪些函式提到 `_LINT_NEW_FILES_TOKEN` 或字面 `"{LINT_FILES}"`。新函式只要不提到它,測試不會紅。
  - 精神上算分叉。這條規矩的出身是「同一件事(把檢查對象換進指令)散在多處,有一處漏了」(`scripts/lumos:38293-38298`)。計劃新寫一套「改寫指令檢查對象」的程式(含引號與 `--input=x` 解析),也承認「這段換參數的程式是新寫的」。
  - 最危險的接點計劃沒定義:`--input` 的值正好是 `{LINT_FILES}` 時(推送閘合格的寫法,見 `scripts/lumos:38887-38891`),整段改寫會在 `_lint_cmd_with_files` 之外吞掉佔位符。冒煙若先走 `_lintcheck_smoke_cmd` 展開,值會變成多個以空白相接的引號檔名,「整段換掉值」會留下孤兒參數。

- **PRIOR-ART 自相矛盾**:計劃寫「不新建機制」,正文卻新建一套換參數程式。

- **既有的正樣本驗證**:`cmd_rule_check` 用「宣告的 cmd 含 `{LINT_FILES}` + 樣本檔 + `_lint_cmd_with_files` + `_lint_run_and_parse` + 比對規則 id」(`scripts/lumos:37993-38012`)。計劃的 PRIOR-ART 說「同一形狀」,實作卻是另一條路:探針寫死在本體裡,改寫指令,另有自己的暫存目錄。

severity: major
blocking: 是
引句:「這段換參數的程式是新寫的,既有冒煙只會換 `{LINT_FILES}` 佔位符。」
建議對齊方向(給編排者裁):
1. 改寫函式與 `_lint_cmd_with_files` 放一起,標成同族的唯一入口。
2. 計劃明寫 `--input` 值含 `{LINT_FILES}` 時走 `_lint_cmd_with_files(cmd, [探針檔])`,不另外替換。
3. 把新函式名與理由登記進那條測試的 ALLOWED 或加一條守衛。

- **暫存目錄不對齊(minor)**:
  - 計劃只說「暫存目錄…跑完刪掉」,沒講位置,也沒講強殺後的殘骸清理。
  - 鄰居的作法是 `tempfile.mkdtemp(prefix="lintbase-", dir=<repo>/.lumos)`、`finally: shutil.rmtree`(`scripts/lumos:38870`、`scripts/lumos:38922`),並有開跑前清過期殘骸的 `_lint_new_clean_stale`(`scripts/lumos:38726`)。
  - 理由寫在 `_LINT_NEW_BASE_PREFIX` 旁(`scripts/lumos:38282`):放系統暫存區,檢查工具往上找不到專案規則設定。
  - 探針要放哪裡、是否沿用這套清理,計劃要先選一個。

severity: minor
blocking: 否
引句:「冒煙時寫進一個暫存目錄當 detekt 的輸入,跑完刪掉。」

- **規則清單漂移守衛(minor)**:
  - 探針硬編的五條規則,跟 `configs/detekt/android.yml` 開了哪些規則,是兩處要一起改的清單。
  - 本專案對這類清單的作法是配一條名單相符的測試,例如 `t_lint_files_substitution_has_one_implementation` 的「名單裡的函式都還在」前置檢查(`scripts/test_lumos.py:17136`)。
  - 計劃的條款 S1~S5 沒有這類守衛。

severity: minor
blocking: 否
引句:「探針驗的五條**(都是 detekt 1.23.8 正式版的協程規則)」

## 問 4 落點:合理,不用另開一篇

- **`Systems/lint-declaration-health`**:`about_code` 是 `scripts/lumos`,內容已含 `cmd_lint_check` 的冒煙 FLOW、F 段兌現、佔位符守衛三個 KEY。探針與 F 段提醒都是這篇的延伸,放進去對。
- **`Systems/linter精選目錄`**:`about_code` 是 `configs/detekt/android.yml`,內容已含 detekt 標準接法樣板。共用設定補開兩條,以及樣板改帶型別參數,放這篇對。
- **建議在 lint-declaration-health 補一行 WHY**:說明為什麼探針沒有走 `cmd_rule_check` 的樣本索引。這就是上面 major 該被回答的問題,寫進圖譜才不會下個 session 又問一次。同時連到 `pitfalls-lint-adapter`,它是 `cmd_rule_check` 的家。
- **`skills/kotlin-idioms/SKILL.md`**:`.md` 不在程式檔副檔名清單(`_NODEHOME_CODE_EXTS`,`scripts/lumos:42755`),不需要 Systems 家。

不對齊共 6 條,其中 major 1 條。(minor 5 條:共用偵測函式、`--json` 輸出、規則 id 比對方式、暫存目錄位置與清理、清單漂移守衛。)另有一個 ⚠ 交編排者:`warn([])` 與 `warn_soft` 的選擇。
