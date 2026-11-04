severity: major

以下逐條 finding。實測用的臨時檔都在 `/tmp/lumos-seat-work/Android的detekt規則說實話/邊界-sonnet/`,由編排者收貨後刪。

**F1:新判定函式一提到 `{LINT_FILES}`,現有守衛測試就翻紅,spec 沒交代怎麼處理**
severity: major
blocking: 是——spec 照字面實作,全套測試必紅,而且動測試檔要先簽名,這個步驟 spec 沒寫。
引句:「判定表寫成一支函式,lint-check 與健檢 F 段共用(不留兩份)。」
引句:「整條命令沒有 `{LINT_FILES}`」
- P1、P2 都要判「整條命令有沒有 `{LINT_FILES}`」,所以新函式必須碰到那個佔位符。
- `t_lint_files_substitution_has_one_implementation` 用語法樹掃整支 `scripts/lumos`,只准六支白名單函式碰這個佔位符。
  - 這條守衛的位置是 `scripts/test_lumos.py:17138`(`ALLOWED = {`)。
  - 名單外的函式碰到,第 17154 行那條 `check` 就紅,不管是用字面 `"{LINT_FILES}"` 還是常數 `_LINT_NEW_FILES_TOKEN`(定義在 `scripts/lumos:38287`)。
- 重現:我把 `def _lint_detekt_advice(cmd): return "{LINT_FILES}" not in cmd` 附加到 `scripts/lumos` 副本,再跑同一段語法樹邏輯。
  - 名單外的碰觸者回 `['_lint_detekt_advice']`,也就是測試會判紅。
- spec 的範圍、驗收、回退都沒提要改這份白名單。
  - 白名單在 `scripts/test_lumos.py`,改它要先簽名。
  - 正確做法有兩條:在白名單加新函式名並寫理由,或讓新函式改問白名單內既有的判斷。spec 兩條都沒選。

**F2:T1、T2 說「沒帶 `--classpath` 所以不會跑」,但命令列有好幾種寫法看不到完整參數,spec 只擋了其中一種,而且擋的方式用字面實作不出來**
severity: major
blocking: 是——提醒會斷言「不會跑」,宣告者卻沒有任何辦法消掉它(spec 自己寫了目前沒有現成修法),所以假提醒每次健檢都會出現。
引句:「detekt 指令列,參數裡沒有獨立的 `--classpath` 或 `-cp` 詞」
引句:「含 `$(`、反引號命令替換的段不判。」
- **`@argfile`**:detekt 1.23.8 會展開 `@檔名` 這種參數檔。
  - 實測:`printf -- '--bogus-opt\n' > args3.txt; detekt @args3.txt` 的錯誤是參數檔裡的 `--bogus-opt`,證明檔案內容被當參數解析。
  - 所以 `detekt @args.txt --input x`(檔裡有 `--classpath`)會被判 T1,實際型別是有的。
  - 這也是 Android 這種長 classpath 最自然的帶法,和 spec 說的「目前沒有現成取法」衝突。
- **未加引號的 `$(…)`**:spec 要求用 shlex「標點拆開」,也就是 `punctuation_chars=True`。
  - 實測 `detekt --classpath $(cat cp.txt) --input a` 的詞是 `['detekt','--classpath','$','(','cat','cp.txt',')','--input']`。
  - 不存在含 `$(` 的單一詞,「含 `$(` 的段不判」在詞層面不成立。只有加引號的 `"$(cat x)"` 才保持一個詞。
  - 例:`detekt $(cat args) --input a` 的參數在子命令裡,卻會被判 T1。
  - S1 的測試案例只列「命令替換」,沒分加不加引號。
- **`$VAR`、`${VAR}`、`"$@"`**:spec 完全沒提。標準樣板 `--config $HOME/…` 本身就用了變數。`detekt $DETEKT_OPTS --input x` 會被判 T1。
- **段首名叫 `detekt` 的自寫腳本**:`./scripts/detekt` 用檔名比對會被判成 detekt 指令列,腳本內部可能補了 classpath。
- 這四種是同一個根因:判「沒有某參數」的前提是看得到完整 argv。
  - 統一規則:段內有 `@` 開頭的詞、含 `$` 的詞、或 `$` 與 `(` 相鄰的詞,就不判「缺」類提醒(T1、T2)。
  - 否則每種各補一個洞,天花板那兩條(spec 〈天花板〉1、2)也沒有涵蓋。

**F3:shlex 預設把 `#` 當註解、把換行當空白,和 sh 不同,spec 沒指定 `commenters`**
severity: minor
blocking: 否——都是少見寫法,且影響只是假提醒或漏判。
引句:「每條命令用 shlex 以 posix 模式、標點拆開切成詞;拆詞失敗(引號沒配對)就整條不判。」
- 要用 `punctuation_chars` 就得直接建 `shlex.shlex(...)`,而它的 `commenters` 預設是 `'#'`。
- 實測 `detekt --report html:r#1.html --classpath x --jdk-home y` 的詞只剩 `['detekt','--report','html:r']`,後面全被吃掉,結果是假 T1。
  - sh 裡詞中間的 `#` 只是普通字元。關掉註解(`commenters=''`)就正常。
- 換行:`detekt --input a\ndetekt --classpath x` 合成一段 `['detekt','--input','a','detekt','--classpath','x']`。spec 的切段只認 `; & |`。
  - 第一條 detekt 沒 classpath,卻因為第二條有而不出 T1。
- 反斜線換行:`"detekt \\\n--classpath x"` 的詞是 `['detekt','\n--classpath','x']`。`--classpath` 黏在換行字元上,不算獨立詞,會出假 T1。
- 這是整類問題:spec 應寫死 `commenters=''`,並把 `\n` 列為切段詞。

**F4:輸出形狀沒定義,「一段」與標準樣板的實際提醒數對不上,也沒說提醒會不會回顯命令**
severity: minor
blocking: 否——先釘規格比事後補測試便宜,但不會讓現有測試翻紅。
引句:「有提醒時印一段,提醒函式帶空清單,不計入問題」
- 標準樣板 `detekt --input <src> --report sarif:{LINT_SARIF_OUT} …` 一條就同時命中 T1 與 P1,至少兩則提醒。
- `warn([], head, advice)` 一次呼叫只算一段(`scripts/lumos:2045-2056`:`_soft["segs"] += 1`),也印不出逐條清單。逐條清單一放進 `lines`,就會 `issues += len(lines)`,改掉問題數與 `--ci` 退出碼。
  - 所以只有兩條路:全塞進 `advice` 字串,或每則提醒各呼叫一次 `warn([])`。後者「多算一段」就變成「多算 N 段」。
  - 現有 `t_doctor_summary_admits_soft_reminders`(`scripts/test_lumos.py:60599` 附近)要求「⚠ 行數 == 另有 N 段」,兩條路在這條測試下的表現不同。
- `warn()` 的 `cap` 只封頂 `lines`。把提醒塞進 `advice` 就沒有封頂。
  - 上百條命令(例如 kt、kts 兩個棧宣告同一條)不跨命令去重,因為 spec 只說「同一條命令同一種只印一次」。
  - 我實測 2 萬條 `detekt {LINT_SARIF_OUT}` 的 lint-check 靜態層 0.74s,沒有效能問題,問題只在輸出量。
- ⚠ 交編排者:spec 沒說提醒文字會不會帶出是哪個棧、哪條命令。
  - 不帶:`kt` 底下多條命令、或多個棧時,使用者分不出是哪一條。`--json` 的 `advisories` 字串清單同樣沒有辨識。
  - 帶:既有慣例是原樣回顯,`print(f"  [{pr['stack']}] {pr['issue']}")`(`scripts/lumos:37804`)。
    - 實測 `{"kt":[1,"detekt"],"\ud800\u001b[31mX":"no"}` 讓 `lint-check` 與 `lint-check --json` 都以 `UnicodeEncodeError` 崩潰,這是既有行為。
    - 若新提醒回顯命令片段,健康分支(目前不印任何命令文字)會多一條同樣的崩潰路徑,而 doctor F 段沒有 try/except。
  - 這份 spec 沒有一句寫到消毒;既有可用的函式是 `_esc_clean`(`scripts/lumos:19360` 起)。

**F5:S1 的測試案例清單漏掉「缺值、空段」這類最容易丟 IndexError 的退化形狀**
severity: minor
blocking: 否——spec 已有「不丟例外」要求,缺的是把它落成測試。
引句:「宣告格式壞掉時新判斷要自己防型別,健檢 F 段沒有包例外,一出錯整支健檢就斷。」
- S1 列舉:「含 java -jar 之前的 -cp、Gradle 的 detektMain 與 :app:detekt、sh -c 包一層、&& 串兩段、引號沒配對、命令替換」。
- 按 spec 字面取值會越界的形狀都沒在清單裡:
  - `java -jar`(結尾沒有下一個詞)
  - `sh -c`(結尾沒有下一個詞)
  - `FOO=bar`(環境變數剝完整段是空)
  - `env`(包裝詞剝完整段是空)
  - `detekt &&`(結尾分隔)
  - `; detekt`(開頭分隔)
  - `''`(空字串詞)
- 實測 shlex 對這些都正常回詞(未丟例外),危險點在 spec 要求的「後面那一個詞」「段首詞」取值。
- 一個測試案例不夠:需要逐條各寫一個。
- NUL、非 ASCII 都能正常拆詞,不會丟例外。我試了 `detekt\x00 --input a`、全形空白、NBSP。
- 非 ValueError 的例外我找不到:引號沒配對丟 `ValueError: No closing quotation`,結尾反斜線丟 `ValueError: No escaped character`,都在 spec 的「拆詞失敗」範圍內。

**F6:Gradle 的「不以 `-` 開頭、名字恰好是 detekt 的詞」會把「排除 detekt」當成「跑 detekt」**
severity: minor
blocking: 否——寫在 lint.json 裡的場景少,但機制確定。
引句:「某個不以 `-` 開頭的詞,取最後一個 `:` 之後的名字恰好是 `detekt`」
- `./gradlew ktlintCheck -x detekt`(同一個專案另宣告 ktlint,並排除 detekt 避免重跑)會判 G1 與 P1,說這條命令會跑 detekt。
- `-p detekt`(專案目錄剛好叫 detekt)也一樣。
- 同族的另一個洞:P1 寫「整條命令沒有 `{LINT_FILES}`」。`detekt a && foo {LINT_FILES}` 裡 detekt 那段沒有佔位符,卻因為整條有而不出 P1。
- 統一規則:佔位符與任務名都改成「按段判」,並跳過帶值選項(`-x`、`-p`、`--project-dir`)的值。

**實務隱患鏡頭(逐類)**
- 解析外來字串:有 F2、F3、F5。
  - 只拆詞、不執行,所以沒有命令注入面。這份 spec 完全沒有 `eval` 或 subprocess。
  - 零依賴的 shlex 本身有二次方行為:`detekt …` 單一詞 10 萬字 0.4 秒、100 萬字 18 秒(Python 3.14 實測)。lint.json 是使用者自己的檔,不構成問題,記錄在此。
- 輸出量與污染:有 F4。
  - `--json`:S2 規定提醒只進 `advisories`,不另外印字。我查了 `cmd_lint_check` 的 `--json` 分支(`scripts/lumos:37792` 附近),它在 `problems` 之後一次 `print`,沒有第二個出口,規定可行。
  - 沒宣告那條路徑 spec 也寫了「不加欄位」,與 `scripts/lumos:37772` 現狀一致。
- 退出碼:無問題。
  - `warn([])` 的 `issues += 0`,`doctor` 尾端 `return 1 if strict else 0` 只在 `issues` 非 0 時走到。
  - `--ci`、`--strict` 在空清單下都不變,也不影響 `lint-check` 的 0/1/2。
  - `--ci` 治理帳 `doctor-run` 的 `soft=` 會多算,是 spec 說的預期。
  - 已讀,無 finding。
- 極端宣告:空物件 `{}`、`{"kt": []}`、頂層 `null` 與頂層清單。
  - `_lintcheck_validate` 已報格式問題,新判斷只要照 spec「頂層不是物件就整份不判」就不會碰到。
  - `config` 在 `parse_error` 時不存在,spec 已限定「讀得出來才判」。
  - 已讀,無 finding。
- 併發、金流、對外呼叫、不可逆:無。spec 不寫檔、不呼叫外部、不執行命令,與其「已排除」三條一致。

**圖譜節點逐條判**
- `Issues/推送閘對Android的detekt只記錄不擋`:不影響。
  - 它宣稱的根因(沒佔位符只記錄、有佔位符多檔拒跑)與 spec 的 P1、P2 一致。
  - P2 依據的「空白相接」確實出自 `_lint_cmd_with_files`(`scripts/lumos:38302`)。
- `Systems/lint-declaration-health`:受影響,見 F1。
  - 「佔位符只剩一份實作」那條 KEY 綁的測試就是 F1 的守衛。
  - 其餘 rc 0/1/2、「壞 = 紅擋 CI」不受影響,因為提醒不計問題。
- `Systems/linter精選目錄`:不影響行為,屬文件同步。標準接法樣板(第 125 行)用 `$HOME`,F2 的 `$VAR` 問題對它成立,會出 T1 與 P1。這正是 spec 要講的實話,不是副作用。
- `Systems/效能檢核目錄`:不影響,純文件。
- `Systems/pitfalls-lint-adapter`:不影響,spec 明寫不改新增告警檢查。

最嚴重 severity:major;blocking 共 2 條(F1、F2)。
