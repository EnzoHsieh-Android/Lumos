preflight-4: ran

# 人裁殺傷力在真實android專案跑得起來 r1 收貨紀錄

## 前掃四項(派工前,便宜代理逐句開程式碼驗語意)

①未定義詞 3 筆、②壞引用 0、③自相矛盾 2 筆、④語意 7 筆;全部直接修進計劃真檔(修前版本另存編排者暫存,本節逐條留修前→修後)。沒有「核心裁定」節,④-3、④-4 前掃標核心,屬事實更正(程式現況與計劃字面不符),照實改寫、同步交席位審。

| # | 類 | 修前 | 修後 |
|---|---|---|---|
| ①-1 | 未定義 | 沒定義逐一 import / 整包 import、觸發字 | 〈用詞〉補三條(觸發字沿用母計劃) |
| ①-2 | 未定義 | T_old 與 T_new 多對多時怎麼配沒寫 | 範圍 1:`--old` 的觸發字裡檔頭恰好一個同套件 import 的才用,零或多個不產生 |
| ①-3 / ③-2 | 未定義、矛盾 | 「否則取第一個 library 模組」沒排序規則、也沒條款 | 只認恰好一個 application 模組;只有 library、零個或多個都不猜 |
| ③-1 | 矛盾 | 天花板 3 說 version catalog 偵測不到又說實作時補 | 〈用詞〉Android application 模組含 `alias(libs.plugins.<名>)` 寫法、補預期值列;天花板 3 改成 convention plugin 偵測不到 |
| ④-1 | 語意 | 「不合就判 error、不套用、不跑」 | cmd_guard_kill 先跑基準再檢查 old/new:改成「不套用壞法、不跑壞法那一次」,另加人裁在跑殺傷力前先驗一次 also |
| ④-2 | 語意 | 「原本只有 survived 存基準輸出」 | 現況 survived 與 abort 存基準輸出 200 字、壞法輸出一律沒存;改成兩種弱證據判定存壞法輸出 400 字,result_out 每列多 tail |
| ④-3 | 語意(核心) | 「預設平台是 kotlin-junit」 | 多平台制平台鍵是使用者取的(init 產 `kotlin`),改看 load_platforms 的 profile_name |
| ④-4 | 語意(核心) | 「--diff 用那個範圍算情境段」 | `_codeloop_disp_range` 找得到分岔點時一律用分岔點;改寫成同 code-loop check 規則、只在算不出分岔點時生效,補「有分岔點時不生效」預期值列,不改共用函式 |
| ④-5 | 語意 | 範圍 3 只改 kotlin-junit | java-junit 骨架是同一條壞指令;範圍 3、4 都涵蓋兩個 profile、單平台與多平台兩條骨架路徑 |
| ④-6 | 語意 | 「偵測到 Android 模組」沒說怎麼掃 | 讀 repo 根的 settings.gradle(.kts) 的 include,模組名照原樣;Gradle 根在子目錄不猜、實務隱患補一條 |
| ④-7 | 語意 | 「old 恰好一次」用子字串計數會被更長的 import 行命中 | 範圍 2 改成整行比對 |

## 派工與收貨(r1)

- 快照 r1-snapshot.md(124 行,sha256 5be8b6c2…6d3,spec_commit 9eccaaa1);4 席同門 sonnet(正確性、邊界、整合、架構對齊),外家未派(單家族視角)。
- 4 份從逐字稿存檔,全部已正規化;quote-check 三份全錨,正確性席 #10「不改那支共用函式。」不到 10 字下限——機械重現:這句逐字出現在快照〈範圍〉5,HIT。

## 分組(依根因)與處置——29 條全部折入

1. **工具猜 import 套件**(c1 c2 b1 b2 g5 g6;c4 部分):型錄觸發字混著成員名、點號寫法、跨套件名稱,依舊 import 的套件補新觸發字會產生不存在的 import;多個舊 import 的規則前後矛盾;d1 的「工具不內建語言知識」軸被碰到。→ **換形狀**:`--import` 由人明寫,工具只驗形狀與名稱是新寫法觸發字;壞法全由人宣告,d1 兩軸都不碰。
2. **工具推 Gradle 模組與任務**(b3 b4 b5 c6 g2 g3 g4 a1 a2):application 模組不是測試所在模組、flavor 改任務名、include 與外掛寫法解析未定義、偵測起點、模組名進 shell。→ **換形狀**:只判「是不是 Android」(沿用 `_android_build_texts` + `_KT_BUILD_ANDROID`,從平台根),init 給 `:YOUR_MODULE:testDebugUnitTest` 佔位加 flavor 說明,人裁偵測到頂層 test 任務或佔位就拒絕並印格式與從 `--file` 推的模組候選(白名單字元)。
3. **失敗摘錄只取結尾**(c3 g1 b7 a3 c8):Gradle 失敗結尾是固定提示,錯誤行在前;tail 欄語意混用;帳本進版控。→ 新欄 `fail_excerpt` 挑錯誤行(取不到才退回結尾)、遮工作樹路徑、abort 也存、`tail` 不改;實務隱患照實寫可能含測試輸出。
4. **also 驗證**(c4 b8 g7):判類、位置、子字串替換、人看不到 also。→ 共用 `_kill_also_issue`(照 `_kill_old_issue` 先例)、記憶體內逐行整行比對、判 error 並寫明為什麼不是 drifted;確認畫面印補 import、治理帳 imports 欄、kill-log note 帶上。
5. **--diff**(b6 c5 g8):被忽略沒提示、`-` 開頭沒擋、右端不是 HEAD。→ 印「沒採用」、入口驗兩項。
6. **環境隱患**(c7):隔離工作樹沒有 gitignored 檔、daemon、冷建構。→ 實務隱患補三條。
7. **測試覆蓋與端到端**(b9 g7):單一條款扛多列、端到端只有人工。→ 條款拆成 10 條,加 S9 假平台自動化端到端(缺 import 就編譯失敗的假 run_cmd)。
8. **落點**(a4):init 骨架的家是 Systems/lumos-cli-lifecycle。→ lands_in 換過去。

## 先查世界

- PRIOR-ART:組 2——查「Android Gradle product flavors unit test task name testFreeDebugUnitTest」。變體是 flavor 加建置類型,任務名 `test<Variant>UnitTest` 跟著變(https://android-developers.googleblog.com/2015/12/leveraging-product-flavors-in-android.html );AGP 9 起預設只建受測建置類型的單元測試任務(https://slack-chats.kotlinlang.org/t/33344942/i-m-upgrading-to-agp-9-from-8-are-testreleaseunittest-not-go )。採用「工具不猜任務名、說明格式要人照專案填」。
- 組 1、3 照實測(型錄觸發字表、實驗副本 Gradle 輸出)與既有函式先例修,不另查。
