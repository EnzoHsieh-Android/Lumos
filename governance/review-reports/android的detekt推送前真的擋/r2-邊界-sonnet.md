severity: blocker

說明:實驗用本機 detekt 1.23.8,JDK 11、17、21、25、26 各驗過,沒有 JDK 8,也沒有 Linux。我沒有 Gradle 實專案可跑,所以初始化腳本相關(F9)沒實跑。實驗暫存已刪。

**1.**
這份規格沒講消費專案自己的 CI 怎麼辦:CI 是全新 checkout,沒有 `build/lumos/detekt-typeinfo.args`,每次都會被 `typeinfo-missing` 擋。
引句:「新工作樹與 clean 之後必擋」
file: `skills/lumos-project-notes/commands/08-自動跑的.md:9`:CI 的行寫明「同 pre-push + `lumos code-loop check`」。
file: `scripts/lumos:68028-68031`:`code-loop check` 每次都呼叫新增告警閘,不看風險分級。
重現:消費專案宣告帶 `@build/lumos/detekt-typeinfo.args` 的 detekt 命令,在乾淨 checkout 跑 `lumos code-loop check --diff <範圍>`,結果必定是 `typeinfo-missing`。
- 規格的「刻意」只談本機新工作樹,沒寫 CI。
- `typeinfo-missing`、`typeinfo-broken`、`timeout` 都沒有針對性放行鍵,唯一出口是 `LUMOS_SKIP_LINT_NEW`(`scripts/lumos:39050`),整道閘都關掉。
- 要在 CI 補產參數檔得先跑完整 Gradle 建置,規格沒有任何一句涵蓋。
severity: blocker
blocking: 是
判準:採用這個設計,所有帶宣告的消費專案 CI 恆紅,而規格唯一的出口是整道關閉。

**2.**
規格要 `typeinfo-broken` 的訊息附 detekt 錯誤輸出末幾行,並且要區分「逾時」「沒產出」,但執行入口做不到這兩件事。
引句:「擋下,訊息附 detekt 錯誤輸出的最後幾行。」
file: `scripts/lumos:38393-38394`:`stdout=DEVNULL`、`stderr=DEVNULL`。
file: `scripts/lumos:38401`、`38407-38413`:逾時、讀不到檔、空檔、JSON 壞掉都回同一個 `([], False)`。
- 範圍的八點都沒列「改這支執行入口的回傳」。
- 這支函式有兩個既有呼叫點與七處既有測試依賴雙值回傳(見 `scripts/lumos:38361`)。
- 不補這一條,S12 的「附錯誤輸出末幾行」「型別宣告逾時擋、一般逾時放行」寫不出來。
severity: major
blocking: 是
判準:規格的驗收條款靠一個規格沒列入範圍的簽名變更才寫得出來。

**3.**
分批門檻寫「64 KB」,沒說算字元還是位元組,也沒說算 `shlex.quote` 之前還是之後。
引句:「逗號串超過 64 KB 時,新增告警閘把檔清單切成多批各跑一次」
- 規格自己說 Linux 單一參數上限 128 KB。`shell=True` 時整條命令字串就是 `sh -c` 的單一參數。
- 全中文路徑每字 3 位元組:64K 字元約 192 KB,超過上限。
- 含 `'` 的路徑經 `shlex.quote` 會膨脹成 `'"'"'`。
- 實測(macOS):`subprocess.Popen("echo "+"a"*2_000_000, shell=True)` 丟出 `OSError [Errno 7] Argument list too long`。
- `Popen` 沒包 `except OSError`(`scripts/lumos:38388`)。
- 上層 `except Exception` 就是整道閘放行(`scripts/lumos:67822-67826`,`_gate_failopen("lint-new", "新增告警閘出例外,這次放行")`)。
- Linux 上我沒跑,E2BIG 是依規格自述的上限推的,標 ⚠。
severity: major
blocking: 否
判準:分批本來就是為了防這個,量法不明就讓整道閘靜默放行,正好是規格要消滅的那種放行。

**4.**
參數檔檢查沒寫讀不了的情況怎麼辦,例外會走整道閘放行。
引句:「不存在、是空的、沒有 `--classpath`、classpath 裡有任何一個路徑不存在、或任何一行含空白字元」
- 輸入一:`build/lumos/detekt-typeinfo.args` 是目錄(例如 `mkdir -p` 誤建)。
- 輸入二:檔案不是 UTF-8(Windows 的 `>` 寫出 UTF-16)。
- 輸入三:沒有讀取權限。
- 這三種都會讓新寫的檢查函式丟 `IsADirectoryError`、`UnicodeDecodeError` 或 `PermissionError`。
- 例外沒人接,就落到 `scripts/lumos:67825`,整道閘放行並記帳。
- 這正是「宣告了要型別卻安靜放行」,規格沒有一個類別接它。
- 補充:BOM 開頭的檔 detekt 本身就失敗(實測 rc=1、無 SARIF),可以走 `typeinfo-missing`,但前提是有解碼成功。
severity: major
blocking: 否
判準:fail-closed 的核心訴求有三個已知輸入穿得過去。

**5.**
`typeinfo-broken` 判「第一個詞找得到執行檔」不可靠,而且沒有放行鍵。
引句:「第一個詞找不到執行檔時照舊算環境類、自動放行(工具沒裝)。」
- 輸入:命令 `env detekt @a --input {LINT_FILES_CSV} …`,或 `java -jar /missing/detekt-cli-1.23.8-all.jar @a …`,或 `cd android && detekt @build/lumos/x.args …`。
- 字面判定都認得這些是 detekt(`scripts/lumos:37836-37862`,包裝詞剝除、`java -jar detekt-cli*.jar`)。
- 第一個詞是 `env`、`java`、`cd`,永遠找得到執行檔。
- 沒裝 detekt 的機器上,命令跑不出結果,被判成 `typeinfo-broken` 而擋下。
- 訊息說型別資訊壞了,其實是工具沒裝,而且沒有針對性放行鍵。
- 第三個輸入還有一個後果:`cd android &&` 之後,`@build/...` 相對 `android/`,規格卻相對專案根檢查存在。這個專案永遠 `typeinfo-missing`。
severity: major
blocking: 否
判準:規格自己定義的「工具沒裝就放行」對常見包裝寫法失效,而且沒有針對性出口。

**6.**
手寫的合法參數檔會被 `typeinfo-missing` 擋,且無放行鍵。
引句:「或任何一行含空白字元,就不跑、擋下,訊息給重新產生的指令。」
實測:
- 單行 `--classpath <jar> --jdk-home <JDK>`:detekt 正常輸出,RedundantSuspendModifier 與 SleepInsteadOfDelay 都響。
- classpath 結尾帶 `:`:detekt 同樣正常。
- CRLF 行尾:detekt 正常。
- 結尾多餘空行:detekt 正常。
- 規格的檢查把前三種判成「含空白」或「路徑不存在」(空字串)。
- 非 Gradle 專案、或手寫並提交參數檔的專案,永久被擋,而且「重新產生的指令」是 Gradle 初始化腳本,幫不上忙。
severity: minor
blocking: 否
判準:誤擋有解法(改成一行一個),但訊息指向的修法不適用。

**7.**
`--jvm-target` 的「夾在 1.8 到 22 之間」不是 detekt 接受的集合。
引句:「夾在 detekt 1.23.8 支援的 1.8 到 22 之間」
- 實測 detekt 1.23.8 的合法值只有 `[1.6, 1.8, 9, 10 … 22]`。
- `8`、`1.7`、`6`、`JVM_1_8` 全都 rc=1、沒有 SARIF(`Invalid value (8) passed to --jvm-target`)。
- Java 工具鏈或 `JavaVersion` 若回報 `8`,腳本照抄就會讓 detekt 拒跑,變成 `typeinfo-broken`。
- 規格要寫明映射:8 與 1.7 都對到 1.8。
- Gradle 實際回報什麼字串,我沒實測,標 ⚠。
severity: minor
blocking: 否
判準:規格的描述與實測集合不符,錯一次就卡住整個專案。

**8.**
用 wrapper 腳本包 detekt 的專案不在型別宣告範圍內,規格沒講。
引句:「被 [[Projects/Android的detekt規則說實話_計劃]] 那套字面判定認成 detekt 指令列、而且帶逗號佔位符的命令」
file: `scripts/lumos:37852-37863`:`head` 必須是 `detekt`、`detekt-cli`,或 `java -jar detekt-cli*.jar`。
- `sh scripts/run-detekt.sh @a --input {LINT_FILES_CSV}` 不算 detekt。
- 它會被換進逗號串、照舊跑,但沒有探針,也沒有 fail-closed。
- S7 把這情形規定為「行為跟改動前一樣」,所以是設計內的,但沒寫進天花板。
- 專案以為接好了,其實跟現在一樣安靜放行。
severity: minor
blocking: 否
判準:漏洞是已知範圍內,但天花板沒記。

**9.**
初始化腳本替含空白的路徑建符號連結,沒講連結怎麼命名。
引句:「在 `build/lumos/links/` 建一個不含空白的符號連結指過去」
- 輸入:家目錄含空白,classpath 有上千個 Gradle 快取 jar。
- AGP 轉換出的 AAR 內容慣例都叫 `classes.jar`(我沒開實專案核對,標 ⚠),放在不同目錄。
- 連結若用檔名當名字會互相覆蓋,後寫的蓋掉前寫的。
- 蓋掉的依賴會從 classpath 悄悄消失。
- 路徑存在檢查與探針都照過,因為標準庫與協程 jar 還在,這正好落在天花板 2。
severity: minor
blocking: 否
判準:規格沒定連結命名,覆蓋是可預見的實作陷阱。

**10.**
全部 kt 檔都被 `separator-path` 放行後,整次結果判成「乾淨」。
引句:「放行後那支檔不送進 detekt、在結果裡列成沒檢查」
file: `scripts/lumos:39133`:`if not targets: continue`。
file: `scripts/lumos:39019-39024`:`ran` 空、`report_only` 也空時走 else,回 `status="clean"`、reason「沒有新增的告警」。
- 輸入:這次推送只動一支路徑含逗號且已放行的 kt 檔。
- 命令沒進 `ran` 也沒進 `undone`,結果印「沒有新增的告警」。
- 沒有東西檢查過,卻講乾淨,跟 `scripts/lumos:39019` 那段註解自己禁止的「一條都沒跑就不准說乾淨」同形。
- 規格說「列成沒檢查」,卻沒說列在哪個欄位、狀態是什麼。
severity: minor
blocking: 否
判準:放行是人裁的,但最終狀態說「乾淨」就是假綠。

**11.**
探針結果的判定順序與辨識方式寫得不夠確定,可以讀出兩種相反的行為。
引句:「跑完拿掉探針結果,再看該響的規則有沒有響」
- 讀法一(字面):先刪掉探針結果,再看規則有沒有響。剩下的只有真檔的結果,幾乎必定缺規則,恆為 `probe-missing`。
- 讀法二:先判規則有沒有在探針檔上響,再刪。
- 實測(含探針檔與真檔同一次執行):真檔 `a/X.kt` 與探針 `probe/P.kt` 都各自出一條 SleepInsteadOfDelay,SARIF 沒有區分來源,只有路徑能分。
- 辨識寫的是「靠路徑落在暫存目錄的 `probe/` 底下認出來」。若實作成子字串 `/probe/`,專案裡 `com/x/probe/Foo.kt` 這樣的套件目錄會被當探針,真告警被吃掉(`scripts/lumos:38463-38466` 的前綴剝除會把路徑還原成 `…/probe/Foo.kt`)。要寫成以 `.lumos/lintbase-<隨機>/probe/` 完整前綴比對。
severity: minor
blocking: 否
判準:措辭兩種讀法都說得通,選錯的後果一個恆擋、一個漏報。

**12.**
Windows 路徑與 classpath 分隔字元沒有交代。
引句:「classpath 裡有任何一個路徑不存在」
- 輸入:`C:\Users\x\a.jar;C:\Users\x\b.jar`(Windows 用 `;` 分隔)。
- 若檢查按 `:` 切,會得到 `C` 和 `\Users\x\a.jar;C`,恆為「路徑不存在」。
- 規格沒說要用 `os.pathsep`,也沒說不支援 Windows。
- 而且新增告警閘走 `shell=True`、`/bin/sh`(`scripts/lumos:38388-38391`),Windows 本來就未必能用,至少該寫進天花板。⚠ 判不準是否在支援範圍。
severity: minor
blocking: 否
判準:規格沒有宣告平台邊界,影響取決於是否支援 Windows。

**逐節與風險類**
- 〈用詞〉與〈範圍〉各節:各 finding 已涵蓋。已讀,其餘無 finding。
- 實務隱患(風險類):
  - 金流、資安、對外送出:規格寫「不碰」,已讀,無 finding。
  - 不可逆:退提交即回原狀,無 finding。
  - 效能與記憶體:classpath 一萬個 jar 的實測見下一段,另外 F3 是命令長度類。
  - 併發:跟主計劃改同一道閘,規格已列,無 finding。
- 回退、天花板、REVISIT:已讀,F8 與 F12 要補進天花板,其餘無 finding。

**已實測且無問題**
- 一萬個 jar:參數檔 869 KB 單行 classpath,detekt 8.5 秒內正常產出,兩條基本規則都響,數量本身不是問題。
- 相對路徑的 classpath 項目:detekt 相對它自己的工作目錄解析,`cwd=repo_root` 時沒問題。
- 指向不存在位置的符號連結(懸空連結):detekt 照跑,所以靠路徑存在檢查擋是對的。檢查要用會跟隨連結的判法。
- `--jdk-home` 用 JDK 11、17、21、26:正常。JDK 25 的路徑含空白時失敗,符號連結後正常。
- JDK 25 搭配 `--jvm-target 25`:不行,這就是規格已寫的夾範圍。
- `--jdk-home` 指向不存在的路徑:Sleep 規則不響、基本探針判缺,抓得到。
- 逗號串帶空白、中文、單引號的路徑:detekt 正常。
- 相對路徑輸入與探針放在 `.lumos/lintbase-x/probe/` 底下:detekt 照掃,SARIF 回報絕對 `file://` URI。

**對每個附加節點的判斷**
- `Issues/推送閘對Android的detekt只記錄不擋`:本案就是為了結案它,不破壞。
- `Systems/pitfalls-lint-adapter`:第 53 行寫「不改擋不擋……擋了會讓那個專案立刻推不動」。
  - 這針對「宣告寫法不對」,不是合約行。
  - 本案的擋是「宣告了型別卻壞掉」,類別不同,不衝突。
  - 但 F1 的 CI 恆紅會同樣讓專案「推不動」,需要裁。
- `Systems/linter精選目錄`:沒有合約行,新檔登記進這篇的 about_code,不影響。
- `Systems/android-e2e-acceptance`:只有舊否決(佔位符加引號)。本案新佔位符靠格式檢查,不衝突。
- `Systems/pitfalls-code-loop`:第 41、42 行說「執行入口對沒換掉的佔位符 fail-closed」。本案 S2 延伸到 `{LINT_FILES_CSV}`,是同向。
- `Systems/lint-declaration-health`:第 19-21 行的白名單守衛,本案範圍 1 明寫要一起改,不影響。有一個提醒:規格要兩個佔位符各一處替換,若實作成兩次連續 `str.replace`,第二次會重掃第一次換進去的路徑文字。

總結:最嚴重 severity 是 blocker;blocking 共 2 條(F1、F2)。
