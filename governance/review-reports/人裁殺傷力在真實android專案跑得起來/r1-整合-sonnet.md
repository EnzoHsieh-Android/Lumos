severity: major

## g1 壞法輸出只留最後 400 字,對 Gradle 失敗幾乎全是結尾樣板,看不出失敗原因
severity: major
blocking: 是 因為範圍 6 要解的缺口(帳本看不出失敗原因)換成真 Gradle 輸出後仍然解不掉,而 S8 的預期值只靠假輸出驗得過。
- 對應段落:〈範圍〉6、〈預期值表〉S8、〈不做〉第 3 點(別名與 Java 照舊,訊息印摘錄讓人看懂)。
- 問題:Gradle 失敗時,編譯錯誤行(`e: file:///…:12:5 Unresolved reference`)印在 `FAILURE: Build failed with an exception.` 之前。最後 400 字依序是 What went wrong 的兩三行、`* Try:` 區塊(`Run with --stacktrace…`、`--info`、`--scan`、`Get more help at https://help.gradle.org`)、`BUILD FAILED in Ns`。最多只剩 `compileDebugUnitTestKotlin` 這個任務名,看不到哪個參照解不開。人裁被拒時印的「最後 5 行」會是純樣板。
- 同一個洞也在 abort(基準非綠)。這是缺口 2(`Unknown command-line option '--tests'`)的現場。現況只存 `b_tail[-200:]`,也是樣板。spec 沒說被拒訊息的摘錄對 abort、error、drifted 要不要印。
- 查證:`_kill_run` 回傳的是完整輸出(上限 256KB,`_kill_cap` 保留頭尾),所以改成「保留匹配行」有料可用。目前只裁尾巴,是 spec 自己的選擇。
- 建議:摘錄改成先抓 `^e: `、`error:`、`What went wrong` 區塊與 `FAILED` 行,抓不到才退回尾端;S8 加一條用真 Gradle 樣式輸出(錯誤行在 FAILURE 之前)的測試。
- 附帶:帳本 `docs/.kill-log.jsonl` 在本 repo 進版控,原文會帶工作樹絕對路徑。〈實務隱患〉寫的「不含祕密」沒有查證依據。
引句:「kill-log 那筆 tail 是壞法那次輸出最後 400 字(含編譯錯誤)」
file: `/Users/enzo/harness/lumos-srl-android/scripts/lumos:27636`
file: `/Users/enzo/harness/lumos-srl-android/scripts/lumos:27993`

## g2 init 與 S6 把一條 run_cmd 當整個專案共用,但 Gradle 任務是每模組、每 flavor、每測試種類各一條
severity: major
blocking: 是 因為 S6 會硬擋(rc 2)並「印出正確寫法」,對這個團隊實際的專案形狀,那個寫法本身就跑不起來。
- 對應段落:〈範圍〉3、〈範圍〉4、〈預期值表〉S5 與 S6、〈實務隱患〉第 3 點。
- 問題一,flavor:本 repo 的 Issue 記了 mOrangePos 有 dev/prod 兩個 flavor。這種專案沒有 `testDebugUnitTest`,只有 `testDevDebugUnitTest` 之類。〈天花板〉與〈用詞〉都沒提 flavor。
- 問題二,androidTest:kotlin-junit 與 java-junit 的 profile 把 `androidTest` 列在 behavioral 與 state 目錄。mOrangePos 考場實測的是 connected 測試。`testDebugUnitTest --tests '*{method}'` 對 androidTest 裡的方法會得到 No tests found,baseline 非綠。
- 問題三,模組:現代 Android 專案是「一個 `:app` 加一堆 library 模組」,合約測試多半在 library 模組。S5 的「恰好一個 application」會選 `:app`,測試不在 `:app` 就會找不到。〈實務隱患〉雖承認「要人手改」,S6 卻在這種情況照樣擋並印錯的指令。
- 問題四,模組來源:正確的模組應從綁定測試所在檔往上找最近的 build 檔,不是從 application 模組。測試檔位置在 kill 時已可由測試索引算出,spec 沒用。
- 問題五,替代指令:Android 專案偵測到卻不能確定時(多個 application、只有 library、自訂 convention plugin),init 仍照舊寫一條已知會報 `Unknown command-line option` 的指令,而且沒有提示。spec 的提示只給「Gradle 根在子目錄」那一種。
- 問題六,S6 子字串比對漏洞:S6 用 `gradlew test --tests` 子字串判斷,漏掉 `:app:test --tests`(同樣是總任務、同樣報錯)、`gradlew clean test --tests`、`gradlew --offline test --tests`。
- 問題七,偵測起點:S6 的「算得出模組」沒說從 repo 根還是平台根起算。平台根是子目錄時可能與 init 的判斷不一致。
引句:「kotlin-junit 與 java-junit 兩個 profile 的 run_cmd 都給 `./gradlew <模組>:testDebugUnitTest --tests '*{method}'`」
file: `/Users/enzo/harness/lumos-srl-android/docs/lumos-toolchain-knowledge/Issues/多平台設定下測試指令被默默略過.md:53`
file: `/Users/enzo/harness/lumos-srl-android/scripts/lumos:6239`

## g3 母 Issue 要的是 application 與 library 都修,spec 只做恰好一個 application
severity: minor
blocking: 否 因為退回的是現況,不是新退步,但與母 Issue 的修好條件不一致、spec 沒解釋。
- 對應段落:〈範圍〉3、〈預期值表〉S5 與 S6 第二列、〈天花板〉3。
- 問題:Issue 的「什麼條件算修好」第 2 條寫「偵測到 Android(com.android.application / library 外掛)時給 testDebugUnitTest 版本」。spec 只認 application。library 模組一樣有 `testDebugUnitTest`,用 `<模組>:testDebugUnitTest` 可以直接給,不必猜 `:app`。
- 問題:S6 第二列規定「只有 library 時不擋」,等於承認 library-only 專案繼續吃壞指令。
- 建議:要嘛照 Issue 的條件做 library,要嘛在 spec 明寫為何收窄,並在 Issue 補一句「第 2 點只修 application」。
引句:「零個或多個 application 模組、只有 library 模組、或 `settings.gradle` 不在 repo 根(Gradle 根在子目錄)時不猜」
file: `/Users/enzo/harness/lumos-srl-android/docs/lumos-toolchain-knowledge/Issues/人裁殺傷力在真實Android專案跑不動的四個缺口.md:52`

## g4 `<模組>` 從 settings.gradle 原樣抄進會被 shell=True 執行的 run_cmd,沒有字元白名單
severity: minor
blocking: 否 因為 settings.gradle 本來就是 Gradle 會執行的碼,信賴邊界沒變,但這條新增了一條「檔案文字進 shell」的路,要有一道字元檢查。
- 對應段落:〈範圍〉3「`<模組>` 照 `settings.gradle` 的 `include` 原樣」。
- 查證:`_kill_run` 用 `subprocess.Popen(cmd, shell=True)`,`{method}` 有 shlex.quote 但模組名沒有。
- 另一個實務問題:`include` 常見多行、Groovy 與 Kotlin 兩種寫法、`project(':x').projectDir = …` 改目錄、動態 include。spec 只給了 `:app` 這一種例子,沒寫解析規則,也沒寫「解析不了就不猜」。
- 建議:模組名限定 `^:[A-Za-z0-9_.-]+(:[A-Za-z0-9_.-]+)*$`,不合不猜。
引句:「(`<模組>` 照 `settings.gradle` 的 `include` 原樣,例 `:app`)」
file: `/Users/enzo/harness/lumos-srl-android/scripts/lumos:27649`

## g5 新寫法觸發字的套件直接借舊寫法的套件,沒有任何資料依據
severity: minor
blocking: 否 因為猜錯的結果是編譯失敗、回到現況的弱證據被拒,但〈實務隱患〉聲稱已限定「同一套件」,實際沒有機制保證。
- 對應段落:〈範圍〉1、〈用詞〉連帶替換、〈實務隱患〉第 2 點。
- 問題:型錄〈情境決策表〉的觸發字欄只有名字,沒有套件。`import <T_old 的套件>.T_new` 只在同套件兄弟(如 flow 套件裡的 flatMapLatest 與 flatMapConcat)才對。
- 反例(型錄現有觸發字):D-7 與 D-16 的 `Channel`(channels 套件)對 `MutableSharedFlow`、`conflate`、`buffer`(flow 套件);D-12 的 `Mutex`(sync 套件);D-17 的 `viewModelScope`(androidx.lifecycle)對 `applicationScope`(專案自訂)。
- 後果:產生一行不存在的 import,編譯錯,判 killed_unattributed。這會讓人誤以為「連帶 import 是對的、是測試弱」,tail 又見 g1。
- 建議:只對型錄裡明列「同套件兄弟」的列啟用連帶替換,或在型錄補一欄套件。
- 另外:S1 預期值表只有 flatMapLatest 對 flatMapConcat 一組,沒有跨套件的反向案例。
引句:「在 `--old` 含的該列觸發字裡,找檔頭有一整行剛好是 `import <套件>.<T_old>`(沒有 `as` 別名)的那一個」
file: `/Users/enzo/harness/lumos-srl-android/scripts/lumos:39178`

## g6 舊否決 d1 的比對只比了「不生成變異」那一軸,漏了它的另一半理由
severity: minor
blocking: 否 因為結論(可行)站得住,但〈舊否決比對〉的論證不完整,而且應該記一筆決策。
- 對應段落:〈舊否決比對〉第 1 點。
- 原文:d1 的 context 是「零依賴跨語言(C#/Kotlin/E2E/python)工具不內建語言知識;自動生成變異有等價變異不可判定問題」。why_chosen 是「人宣告的壞法保證語意有變」。
- 判斷:
  - 第二軸(等價變異)確實不碰。補一行未用到的 import 不改語意,spec 說「不生成新壞法」成立。
  - 第一軸(工具不內建語言知識)被碰到:Kotlin import 語法、`com.android.application` 外掛 id、version catalog 別名正規化,都是語言與建置知識進工具核心。
  - 另一點:這行 import 由工具依型錄觸發字產生,不是人宣告的,第二個理由「人宣告」也不完全成立。
  - 緩解:工具已經內建 Kotlin 知識(情境決策表、Kotlin 剝註解)。所以結論是站得住,但理由要改寫成「d1 第一軸已被情境決策表的 Kotlin 知識先行鬆動」。
- 建議:在 spec 補這一軸,並 `lumos decision-add` 一筆對 d1 的窄化(只在 recipes_override 路徑、只補 import)。
- 同段落另外兩條否決(另抽共用函式、從 import 猜功能歸屬):對照 guard-kill 第 45 行的 [不選] 與 android-e2e-acceptance 第 74 行的 [不選],引用屬實。
引句:「連帶 import 不是生成新壞法——壞法照舊由人在 `--old`/`--new` 宣告」
file: `/Users/enzo/harness/lumos-srl-android/docs/lumos-toolchain-knowledge/Projects/guard殺傷力驗證_計劃.md:12`

## g7 人點頭時看不到 also,而且 S9 與修好條件要的端到端驗證只有人工
severity: minor
blocking: 否 因為不影響判定正確性,但影響「人裁」這個名字背後的知情同意,以及三個月後能否重現。
- 對應段落:〈範圍〉1、2、〈驗收條款〉S9。
- 問題一,確認畫面:`cmd_situation_rule` 的確認畫面只印段、列、計劃、條款、測試,沒印壞法,也沒印 also。使用者同意的是一個他看不到的檔案改動。
- 問題二,審計:also 不進治理帳,也不進 kill-log 的欄位,事後無法證明驗過的壞法含了哪一行 import。
- 建議:殺傷力開跑前印 also 那行,並寫進 kill-log 的 `note`。
- 問題三,S9:Issue 的修好條件 1 明寫「有逐一 import 的端到端測試」。S9 是 `[manual:…]`,而且指向一份「暫存副本」,三個月後多半不在了。
- 問題四,單元測試:S1 到 S4 若用沒有編譯器的假平台,測不出「少一行 import 就編不過」這個核心因果。
- 建議:加一個 fake run_cmd 腳本,檢查被改檔裡有沒有 T_new 的 import,沒有就回非零,當作自動化端到端測試。
引句:「[S9] 當在真實 Android 專案以逐一 import 的檔跑人裁(flatMapLatest 換 flatMapConcat、綁連送兩次值的測試),人裁指令 應 判 killed 並寫回條款」
file: `/Users/enzo/harness/lumos-srl-android/scripts/lumos:76071`

## g8 `--diff` 沒限制終點必須是 HEAD,段身分可能與推送時對不上
severity: minor
blocking: 否 因為只有在 `--diff` 的終點不是 HEAD 時才會發生。
- 對應段落:〈範圍〉5、S7。
- 查證:`_situation_rule_target` 以 HEAD 為終點切段,`_kt_bj_segments` 把 `diff_range` 傳給 `_kt_situation_segments(repo_root, rng, at_sha…)`。範圍終點若不是 HEAD,段與列算在別的版本上。
- 後果:段身分綁 hunk 內容。人裁寫回的條款對的是一個推送閘永遠不會出題的段。
- S7 第一列的範例本身矛盾:例子是「沒有主線分岔點的 repo,帶 `--diff main..HEAD`」,但沒有主線的 repo 通常也沒有 `main` 這個 ref。
- 建議:`--diff` 的右端要解析成 HEAD,否則拒絕。S7 的例子改成可重現的範圍。
引句:「`lumos situation-rule --diff <A..B>` 跟 `code-loop check --diff` 同一套規則(`_codeloop_disp_range`)」
file: `/Users/enzo/harness/lumos-srl-android/scripts/lumos:75379`

## 其餘各節、既有合約與其他讀者
- 〈白話〉、〈用詞〉、〈範圍〉2 與 7、〈不做〉、〈回退〉、〈依據來源〉:已讀,無 finding。其中〈範圍〉2 要求「判法跟 cmd_guard_kill 共用同一支」,方向正確,與既有 `_kill_old_issue`、`_kill_new_issue` 的先例一致。
- `cmd_guard_kill` 回傳多 `tail` 的其他讀者逐一查過:
  - `cmd_guard_kill_add` 的 `--try` 只讀 `rows` 的 `verdict` 與 `weak`。
  - `_backing_kill_rows` 對 `source: situation-rule` 的列直接略過,doctor P2、表態背書、資安背書都走它。
  - gov 第 5 源的 mapper 只用 verdict、invariant、test、note。
  - `_SECEV_KILL_CODES` 只看 verdict。
  - 結論:不影響。
- 固定席判定:這份設計不破壞 guard-kill 的兩條 ★INVARIANT★。
  - rc 優先序:also 不合判 `error`,屬 drifted、abort、error 同桶,rc 2,與現行一致。
  - `--json` 純度:`tail` 是字串,`json.dumps` 會跳脫控制字元,成功路徑仍恰一行。
  - 但實作要補一條測試,釘住「`--json` 帶 weak 的 tail 仍是單行合法 JSON」。
- test-profile-multiplatform 的 KEY 行:不衝突。`_SKELETON_RUN_CMD` 字典照留當預設,既有斷言(只查含 `{method}`)不變。`t_init_*` 對骨架的斷言要逐條確認 Android 路徑沒有被這些測試的假檔案誤觸發。
- 實務隱患逐類:
  - 金流:無,不碰付款與金額。
  - 對外送出:無,只在本機隔離工作樹改檔跑測試。
  - 不可逆:無,工作樹用 `git checkout` 整支還原,條款與帳本語意不變。
  - 資安:見 g4。
  - 併發:無新增,臨時配方不落共享狀態,清殘骸沿用 `sweep_repo`。
  - 新舊版本混用:無風險。臨時配方的 `also` 不落帳。新版 `tail` 欄位舊版照讀。舊版讀不到 `--diff` 只是少一個旗標。
  - 回滾:還原提交即可。已寫進 `.lumos/config.json` 的新 run_cmd 只是字串,舊版照樣跑。

最嚴重:major;blocking 共 2 條
