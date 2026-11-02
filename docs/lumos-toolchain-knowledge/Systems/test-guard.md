---
type: system
status: doing
created: 2026-11-02
updated: 2026-11-02
responsibility: 負責 lumos test-guard 測試防竄改比對:改動清單與三類檔(測試檔、正式程式檔、截圖基準圖)的分類、讀兩端內容、測試函式切法與斷言判讀、各條 tq/ 規則與指紋、比對起點(跟主線的分岔點),以及它接進新增告警閘的那一層(作弊候選併進新增告警、比對出錯擋下、放寬照起點判、關閘留帳、lint-waive 的 AI 放行標記);不負責建置檔與 CI 的比對(移到計劃第二批)、新增告警閘既有的檢查工具那一半與 SARIF 解析(pitfalls-lint-adapter)、Room 守衛的方法切法本身(room-guard)、測試品質標準的內容(test-quality-cli)
aliases: []
about_code:
  - scripts/lumos
tags:
  - type/system
  - status/doing
  - scope/guards-gates
summary: |-
  WHY:比對從跟主線的分岔點起算,不從推送範圍的起點 [出處:[[Projects/Android測試防竄改檢查_計劃]] 做法一] [因:合過主線之後推送,主線上別人刪的測試不該算到推送者頭上;同一條分支先前推送的候選不是改掉了就是已在放行檔] [不選:照推送範圍的起點比(合主線後誤擋)] [test:t_tq_guard_cli_contract]
  WHY:比對自己出錯(程式錯、逾時、git 算不出改動)記成沒跑完並擋下,不照新增告警閘「環境不可用就自動放行」 [出處:[[Projects/Android測試防竄改檢查_計劃]] 〈二〉] [因:Android 端到端驗收否決過出錯就放行;自動放行是已知的繞道向量] [不選:fail-open] [代價:比對程式錯時那一次推送要用 LUMOS_SKIP_LINT_NEW(留帳)] [test:t_lint_new_test_guard_failure_blocks]
  PITFALL:測試檔改名成非測試檔時,被刪測試的候選記在新檔名上 [出處:2026-11-02 實作時測試先紅] [根因:候選路徑取改動後路徑,改名成非測試檔時那支已經不是測試檔] [修法:改動後不是測試檔就記在原本那支] [test:t_tq_guard_test_removed]
  SEE:[[Projects/Android測試防竄改檢查_計劃]] [[Systems/pitfalls-lint-adapter]] [[Systems/room-guard]] [[Systems/test-quality-cli]]
  WHY:設定 off 或 LUMOS_SKIP_LINT_NEW 時比對照樣在背後跑、有候選或比對自己出錯才記一筆帳(出錯也記是代碼審 r2 改定:比對壞了被擋、用環境變數繞過那次要留得下痕跡),跟 Room 守衛、筆記形狀擋的 off 等於不執行刻意不同 [出處:[[Projects/Android測試防竄改檢查_計劃]] 〈二〉關閘留帳] [因:讓「關閘放過了什麼」有痕跡] [代價:off 的專案仍付比對成本] [test:t_lint_new_warn_off_and_relax]
  WHY:推送範圍本身把 lint_new.gate 放寬時,這一次照起點那一版的值判 [出處:[[Projects/Android測試防竄改檢查_計劃]] 〈二〉] [因:不然同一次推送就能先關閘再帶進作弊改動] [不選:一律照工作目錄(只在沒提交時保留這個既有行為)] [test:t_lint_new_warn_off_and_relax]
  WHY:候選指紋用規則、檔案、函式級規則用函式鍵(類別路徑加函式名),跳過註記、assume 與門檻用函式名(不帶類別;類別層級的註記用所在檔;新增 @Test(expected=…) 那條照函式鍵),再加那條規則的細節(跳過註記一律記成「跳過」、不分註記種類,assume 與比對門檻帶整個敘述,另有斷言數、改後那一句)、第幾個,不帶行號(代碼審 r1–r3 改定) [出處:[[Projects/Android測試防竄改檢查_計劃]] 做法一] [因:上下文位移、整檔重新縮排、原樣搬家不該讓放行失效] [test:t_tq_guard_cli_contract]
  WHY:AI 放的放行(沒有互動終端)只讓它事後可見、不擋推送,判法照搬 Android 端到端驗收 [出處:[[Projects/Android測試防竄改檢查_計劃]] 〈二〉] [因:AI 照抄擋下訊息的放行指令仍推得出去,能做到的是人一定看得到它放了什麼] [不選:AI 放行一律擋(無人看顧流程整個卡住)] [test:t_lint_waive_ai_marking]
  PITFALL:建置檔 enabled = 換行接 false 時逐行比對看不到 [出處:2026-11-02 實作時測試先紅] [根因:建置檔規則逐行比對] [修法:行尾是 = 的把下一行接上來一起判] [repro:計劃第二批原 S7 的 test 區塊 enabled = 換行 false] [status:superseded] [被取代:代碼審 r4 使用者裁定縮範圍,建置檔與 CI 規則移到 [[Projects/Android測試防竄改檢查_計劃]] 第二批]
  WHY:跳過註記的身分是「函式名 + 跳過」,不帶類別、本體與註記種類;類別層級的註記另以所在檔區分(改名或搬家時兩邊都用新路徑);assume 呼叫與比對門檻改帶整個敘述、字串外的空白整理過(字串常值原樣,代碼審 r5;代碼審 r2:條件改成永遠跳過、門檻調高原本不算新增;r3:只取一行時多行寫法漏抓、換行重排與改同一行斷言被誤列) [出處:[[Projects/Android測試防竄改檢查_計劃]] 代碼審 r1 正確性、通才、邊界、資源四席] [因:帶本體簽名時只改本體就把早就跳過的測試列成新增、@Ignore 換 @Disabled 也列;類別層級註記跨檔合算會一支拿掉一支加上互抵] [代價:不同類別裡同名的兩支測試一支拿掉跳過、另一支加上會互抵(寫進抓不到清單)] [test:t_tq_guard_skip_added]
  WHY:比對花掉的時間不算進檢查命令的時間預算,最壞情況整道閘的時間是預算的兩倍 [出處:代碼審 r1 資源席] [因:共用預算時比對先跑會讓調小預算的專案被判「時間預算沒跑到」而誤擋] [不選:比對另設比例預算(多一個設定鍵)] [代價:慢機器上整道閘最多跑到預算的兩倍] [test:t_lint_new_includes_test_guard]
  WHY:測試檔裡超過 2 萬字的行抹掉不比、那支檔另列一條可放行的 tq/too-large(正式程式檔的判讀是逐行一條正規式,不設這道;建置檔與 CI 這一批不比) [出處:代碼審 r2 資源、邊界、正確性三席] [因:規模那一族連兩輪被病態單行輸入打穿平方級,逐點補線性補不完;外層看門不靠逐條判斷,判錯的代價從推送卡到超時變成多一條要人放行的候選] [不選:繼續逐點補(第三輪仍會有漏網的那一處);整支不解析(r3 資安席:加一行長註解就把同檔作弊壓成一條)] [代價:壓縮檔、產生的程式一行很長時每次都要人放行] [test:t_tq_guard_cli_contract]
  WHY:比對起點的分岔點先只看遠端主線,沒有遠端主線才退回本機 main [出處:代碼審 r2 資安席] [因:本機 main 上還沒推出去的提交沒有任何一次推送比對過,算進主線就把那段改動從比對範圍扣掉;回頭重讀的分岔點同一個理由不收本機主線] [不選:照 Room 守衛手動跑的寫法連本機主線一起算] [test:t_tq_guard_cli_contract]
  WHY:建置檔的 ignoreFailures 不限在測試區塊,只排除外層或同一行開的區塊是靜態檢查外掛或報表(而且不是測試任務)的;點名測試任務看引號裡是不是整個含 test 的任務名形狀(報表外掛的任務名不算) [出處:代碼審 r2 正確性、通才、邊界、合約四席] [因:第一輪把 ignoreFailures 收窄到測試區塊,點號寫法與重試區塊全漏;「引號裡含 test 就算」又把 JaCoCo 的 exclude 誤擋] [不選:只看區塊開頭(漏同一行寫完的);要有 named、matching 這類呼叫字樣(r3:漏 findByName、tasks[…]、getByPath)] [status:superseded] [被取代:代碼審 r4 使用者裁定縮範圍,建置檔與 CI 規則移到 [[Projects/Android測試防竄改檢查_計劃]] 第二批]
  WHY:LUMOS_SKIP_LINT_NEW 只認 1,設成 0 或 false 照常判 [出處:代碼審 r3 資安席] [因:同族的 LUMOS_SKIP_ROOM_GUARD、LUMOS_SKIP_NOTE_SHAPE 都只認 1;殘留或照字面設成 0 的環境變數會無聲關掉整道閘連同作弊比對] [不選:有設就關(原寫法)] [test:t_lint_new_test_guard_failure_blocks]
  WHY:建置檔與 CI 檔這一批不比,移到計劃第二批另做 [出處:代碼審 r4 使用者裁定縮範圍] [因:四輪代碼審裡這兩類的 major 佔大宗,用正規式猜 Gradle DSL 與 shell 的寫法每輪都被新寫法打穿(字串模板任務名、一行開兩個區塊、鏈結換行、路徑形式的 gradle、病態長行回溯)] [不選:再補一輪字表] [代價:這一批推上去之後,建置檔與 CI 讓測試不跑或失敗不算的改動不會被列,寫在標準的抓不到清單] [test:t_tq_guard_cli_contract]
  REVISIT:2026-12-15 建置檔與 CI 的作弊比對(計劃第二批)開計劃了沒;沒開就重新排程,並確認標準的抓不到清單還寫著這個缺口
  PITFALL:單行上限之內仍有三種乘積形狀讓比對跑過 30 秒(catch 型別括號掃到很遠的右括號、類別名後接大段空白、測試宣告找不到名字時泛型角括號沒上限) [出處:代碼審 r5 邊界、資源席] [根因:每個命中各自往後掃同一段很遠的文字,外層的單行上限擋不到] [修法:catch 括號用共用的括號對應表、換行後第一個非空白字與一行最後一個非空白字每個位置只找一次、角括號最多看 _TG_MAX_GENERIC_CHARS 字] [test:t_tq_guard_cli_contract]
  WHY:catch 吞斷言照 Error Prone 的 AssertionFailureIgnored 只看結構(try 有斷言或 fail、catch 接得住 AssertionError、catch 不重丟就列),不看 catch 裡寫了什麼檢查;try 沒 fail 而 catch 有斷言那半,should 開頭的字寬判成斷言 [出處:代碼審 r5 正確性、邊界、資安三席;r6 正確性、邊界兩席] [因:寬判法讓名字以 should 開頭的變數或方法算成檢查,吞掉斷言的 catch 不列;r5 改成只認中綴形狀,又把點號呼叫的真檢查排除,該列的漏列、正常的被誤列] [不選:繼續補名字字表(r5 寬、r6 窄、r7 前綴白名單,三輪各被一步改名打穿或誤列)] [代價:catch 裡真的檢查例外型別的寫法也列,要附理由放行或改用 assertThrows/shouldThrow] [test:t_tq_guard_catch_no_fail]
  REVISIT:2026-12-15 一次推送的測試檔總量接近 200 MB 時峰值記憶體約為內容的 16 到 23 倍(代碼審 r5 資源席量測,原有設計);第二批評估逐檔放掉原文與切段
  WHY:catch 接不接得住斷言失敗照型別名字的字尾認(…Error、…Failure、Throwable),不逐一列各框架的子類別 [出處:代碼審 r8 資安、正確性兩席] [因:四個字的字表漏掉 JUnit 4 字串比對失敗丟的 ComparisonFailure、opentest4j 的 MultipleFailuresError 這類 AssertionError 子類別,AI 照失敗訊息抄型別名寫 catch 就躲過;各框架的子類別都以 Error 或 Failure 結尾] [不選:把子類別逐一列進字表(照樣會漏新框架)] [代價:自訂的 Result.Error 這類型別也會列,多一條可放行的候選] [test:t_tq_guard_catch_no_fail]
verified_by:
  - "[[Verification/2026-11-02_Android測試防竄改檢查實跑]]"
---
# test-guard

比對一段範圍改動前後兩版,列出讓測試變得不會紅的改動(作弊候選)。程式在 `scripts/lumos`(比對本體的函式以 `_tg_` 開頭,入口 `cmd_test_guard`;接進新增告警閘的那一層在 `_lint_new_verdict` 一帶,檢查工具那一半的家是 [[Systems/pitfalls-lint-adapter]])。

- 測試函式的切法借 Room 守衛的 `_rg_methods`,那套切法的家在 [[Systems/room-guard]]。
- 規則一覽、抓不到什麼、怎麼放行寫在測試品質標準的〈推送前的防竄改檢查〉節(家在 [[Systems/test-quality-cli]]);逐條判法與取捨在 [[Projects/Android測試防竄改檢查_計劃]] 做法一、二;代碼審 r1 修掉的判讀缺口與取捨在卷證 `governance/review-reports/code-Android測試防竄改檢查/`。
