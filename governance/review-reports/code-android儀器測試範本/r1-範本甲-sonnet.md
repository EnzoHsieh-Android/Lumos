severity: minor

我讀完整份 patch(1452 行),也對照了驗證紀錄。照抄會編不過、跑不起來、對照分不出好壞的 major 問題,我沒找到。

已查證的項目:
- KSP `2.2.21-2.0.5` 存在,見 Maven Central 的 maven-metadata.xml。
- Room 3 的 `room3` Gradle 外掛、`room3-testing:3.0.3`、`MigrationTestHelper` 具名參數、suspend 版 `Migration.migrate` 與官方遷移頁一致:https://developer.android.com/training/data-storage/room/migrating-db-versions
- T6 的 Room Gradle 外掛自動接 assets、升版後第一次建置會找不到最新版 json,與驗證紀錄 E10 一致。
- T8 的推進時序我手算過,取消前剛好 2 次 fetch,三個壞寫法各自只會紅它該紅的那一支。
- T7 DATA-58、DATA-60 的情境與驗證紀錄 E4、E8 對得上。

沒能用官方文件逐一查證的:Robolectric 4.17、WorkManager 2.11.2、Paging 3.5.3、Ktor 3.6.1 這些版本號,我只在驗證紀錄的 `valid_under` 裡看到,沒獨立查。

F1
severity: minor
blocking: 否
檔頭說 T0–T5 都在「純 JVM Gradle 專案」實跑過,但 T4 的 Ktor 小節是這次新加的,驗證紀錄寫的是照〈Android 實驗專案骨架〉組成 Android app 模組後,用本機單元測試(`testDebugUnitTest`,跑在 JVM 上)跑的。
引句:「T0–T5 每一格都在純 JVM Gradle 專案實跑過」
佐證:`docs/lumos-toolchain-knowledge/Verification/2026-11-06_Android儀器測試範本與架構測試實跑.md:16`(「把 T6–T13 與 T4 的 Ktor 小節每一格…組成一個 Android app 模組」)
失敗場景:有人在檔頭 `plugins`/`kotlin { jvmToolchain(17) }`/`useJUnit()` 那種純 JVM 專案抄 Ktor 小節,會以為已被驗證。其實純 JVM 組合沒有實跑紀錄,只有 Android 模組加 JDK 內建 `HttpServer` 的紀錄。建議檔頭改成「T0–T5 與 T4 Ktor 的實跑環境分開寫」,或補一次純 JVM 的實跑。

總結:最嚴重是 minor(檔頭實跑環境的說法跟驗證紀錄有落差),會擋 0 條。
