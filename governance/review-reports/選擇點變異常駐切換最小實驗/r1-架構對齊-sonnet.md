severity: major

## A1 實驗卷證存進審查卷證目錄,偏離專案既有的「實測寫成 Verification 筆記」做法
severity: major
blocking: 是
引句:「存進審查卷證(governance/review-reports/ 底下這份計劃的目錄)」

既有做法在哪:
- 加速計劃第二、三、四段的 `governance/review-reports/<計劃名>/` 只放席報告與收貨紀錄(r1-*-sonnet.md、r1-intake.md)。佐證:`docs/lumos-toolchain-knowledge/Projects/選擇點變異加速第四段_計劃.md:154`、`docs/lumos-toolchain-knowledge/Projects/選擇點變異加速第三段_計劃.md:139`、`docs/lumos-toolchain-knowledge/Projects/選擇點變異加速第二段_計劃.md:180`。
- 實測結果一律寫成 Verification 筆記。第四段 S5 驗收寫的是「讀治理帳寫進驗證紀錄」(`docs/lumos-toolchain-knowledge/Projects/選擇點變異加速第四段_計劃.md:101`),產物是 `docs/lumos-toolchain-knowledge/Verification/2026-11-26_選擇點變異加速第四段實驗專案實測.md`。同目錄還有 `2026-11-22_選擇點第三批上線前實測.md`、`2026-11-17_選擇點第二批上線前實測.md`。
- 專案鐵則也要求用 `lumos new verification … --plan … --systems …` 留紀錄。

差在哪:
- 本計劃 S1(拆帳表)和〈做法〉S5(平均秒數與比值)的證據都指定放審查卷證目錄。這等於立了第二種實驗卷證位置與格式。
- 它沒有進 Verification 節點,所以不受 `--plan`、`--systems` 綁定、lint、doctor 管轄。
- 後面的人想用「查 Verification」找這次的實測會找不到。
- 計劃自己的〈落點〉只說結論寫進 `Systems/guard-kill` 一行,沒提 Verification 筆記。
- 建議:拆帳表和比值寫成 `Verification/2026-11-28_選擇點變異常駐切換最小實驗實測`,S1、S5 改指那裡。審查卷證目錄維持只放席報告。

## A2 另寫一套牆上毫秒計時腳本,沒說明跟既有計時與治理帳怎麼對接 ⚠
severity: minor
blocking: 否
引句:「實驗自帶一份只在本實驗用的 Gradle 初始化腳本,在編譯任務開始結束、測試任務開始、每支測試開始結束各印一行牆上時間(毫秒)」

既有做法在哪:
- choice-kill 已有計時:`_kill_run` 回傳 elapsed(`scripts/lumos:28340`),基準耗時與逾時上限都靠它(`scripts/lumos:28654-28701`)。
- 事件用的初始化腳本是 `_CHOICE_MERGE_INIT`(`scripts/lumos:28902`),只開 `testLogging` 事件、不帶時間。
- 每個壞法的總秒數與 `merge_why`、`single_runs` 已進治理帳。

差在哪:
- 本計劃明講這份腳本只在實驗專案用、不改 lumos,而且說明了第四段那份不帶時間,所以不算跨層。
- 該算引入第二種做法的是:拆帳的「總時間」欄沒說用治理帳已有的 per-mutant 秒數當基準。S1 的「四段加總跟總時間差不到 10%」要對照的總時間來源沒寫。
- 若實驗另量一套總時間,會跟 choice-kill 自己記的時間對不上。
- 我判不準這算偏離還是單純省略,所以標 ⚠。
- 建議:一句話寫明總時間取自既有 `_kill_run` 或治理帳的紀錄,四段牆上時間只用來切分。

對照過、沒問題的部分:
- 結論寫回位置:落到 `Systems/guard-kill` 與第二段〈不做〉表,沿用既有落點,沒有新位置。
- 不改 lumos 程式、只用呼叫時帶的初始化腳本,符合第四段的做法和「不改消費專案 Gradle 設定」。
- 跟舊否決(第二段、存活回指條款〈不做〉)的關係已明講,並有使用者裁示。
- 停手條件接第二段那一列,沒有另立否決表。
- 第二步原型放實驗專案暫存分支,不進 Lumos。

總結:最嚴重 severity 為 major,blocking 共 1 條。
