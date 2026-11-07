severity: minor

**r1 十一條核對**:全部修到位,沒有修壞或修出新問題。
- ArchUnit 手冊 8.6.2 逐字確認:`allowStoreCreation` 預設 false、`allowStoreUpdate` 預設 true、可設 false 禁止更新。範本的引文與驗證紀錄 E13 一致。
- 在複本跑 `-k kotlin` 是 362 passed。
- 我改壞了兩處,只有一處紅。把建清單片段的 `allowStoreUpdate` 那行加行尾註解,守衛紅(符合預期)。把 `if (project.hasProperty("archunitFreezeInit"))` 改成 `if (true)`,守衛照綠(見 F2)。
- 範本丙-F1、測試-F1、F2、F3、F4、範本甲-F1、範本乙-F1/F2、範本丙-F2、架構對齊-F1/F2 都已折入且對得上。
- 骨架補 `AndroidManifest.xml`、T10/T11 附完整 Manifest 的說法屬實(範本內三處 Manifest 圍欄)。

F1
位置:T12〈紅綠矩陣〉末四格與前導句。
說明:前導句寫清單是〈好寫法〉加一筆舊違規 `TagRepository` 建的,但新增前三格的「被測程式小節」欄卻都寫「好寫法」。
- 第一格:好寫法沒有 `TagRepository`。舊違規消失時,`data_layer_does_not_hardcode_dispatchers` 會因為清單要縮小而紅 `StoreUpdateFailedException`,跟同一格寫的「其他綠」相矛盾。
- 第三格:「測試+修掉舊違規」其實改的是被測程式,不是〈測試〉。
- 同一段前面還寫「每一格先用〈好寫法〉……建凍結清單(零違規)」,跟 `TagRepository` 那句也互相矛盾。
- E13 的實際基準是程式裡帶 `TagRepository`。
- 照矩陣重跑的人會得到跟格子不符的結果。
引句:「新那支紅 `StoreUpdateFailedException`(不是靜默凍結成綠);其他綠。」
severity: minor
blocking: 否

F2
位置:`test_lumos.py` 的 `_kt_instr_template_problems` 與範本 T12 建清單的 `build.gradle.kts` 片段。
說明:守衛只比對兩行 `systemProperty(…, "true")` 在不在 kotlin 圍欄裡,不管有沒有被 `-ParchunitFreezeInit` 條件包住。我在複本把條件改成 `if (true)`,兩個 `systemProperty` 變成常駐 true,整套守衛仍是 362 passed。也就是「不常駐 true」這個核心前提沒有守衛。
引句:「systemProperty("archunit.freeze.store.default.allowStoreUpdate", "true")」
severity: minor
blocking: 否

F3
位置:T12「舊違規凍結」三步與「清單只能縮小」。
說明:範本把「改了規則描述」列為帶 `-ParchunitFreezeInit` 的正規流程,但 E13 實驗已證實舊描述的清單行與檔案會留著、新描述另存一份。
- 沒有說要清掉舊條目,「清單只能縮小」的說法在改名後就不成立。
- 改名同時新加的違規,在帶屬性那一跑會被整批凍結,等於把靜默凍結換成「靠代碼審才看得到」。
- 同一段只寫了「清單的改動跟程式一起過代碼審」,沒提醒改名要連同舊檔一起刪、要特別看新增的違規。
引句:「清單只能縮小,新增一筆要在代碼審說明理由」
severity: minor
blocking: 否

F4
位置:計劃與驗證紀錄跟新措辭沒對齊。
- 計劃 file: `docs/lumos-toolchain-knowledge/Projects/Android儀器測試範本與架構測試_計劃.md:121` 的 T4 補 Ktor 列仍寫「純 JVM(前半骨架)」。新檔頭說 Ktor 小節在 Android app 模組實跑,不是純 JVM。
- 驗證紀錄 file: `docs/lumos-toolchain-knowledge/Verification/2026-11-06_Android儀器測試範本與架構測試實跑.md:27` 寫 61 格、T12 7 格,同檔 `:57` 寫 T12 7 格連跑 20 次;範本矩陣現在是 11 格。多的四格只在 E13 提到,沒回補總數。
- 沒有守衛會抓到這種計數或環境描述的不一致。
引句:「Ktor 小節是本機單元測試,沒在純 JVM 專案跑過」
severity: minor
blocking: 否

總結:最嚴重是 minor,會擋 0 條。我的臨時目錄已刪。
