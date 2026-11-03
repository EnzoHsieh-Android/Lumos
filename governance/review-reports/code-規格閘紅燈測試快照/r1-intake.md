# r1 收貨紀錄(code-規格閘紅燈測試快照)

## 收貨

- 三席(單reviewer、架構對齊、資安,全 sonnet;資安是 standard 分級之外編排者自願加派)報告從逐字稿原樣存檔,沒有改字。
- `report-normalize`:三份都已正規化。`quote-check`:三份全數錨定。`refcheck` 找不到的只有報告裡舉例的路徑(`governance/redbase/...`、`docs/x.json`、`governance/redbase/甲/x.json`)。
- 三席交回期間 repo 工作樹沒有被席位改動(`git status` 只有編排者自己的卷證)。
- 席位重現腳本在 `/tmp/lumos-seat-work/code-規格閘紅燈測試快照/`,報告存檔後整個目錄刪掉。

編號:單reviewer F1–F9 記成 C1–C9、架構對齊 A1–A7、資安 S1–S4,共 20 條;major 2 條(C1、C2),其餘 minor。輪內有 major 席,照代碼審規則全數折入,沒有放行,沒有重現不到的。

## 根因分組與處置(全部 folded)

| 組 | 根因 | id | 折法 | 先紅的測試 |
|---|---|---|---|---|
| 1 | 寫入端用測試名當身分,兩個平台同名時第二個被靜默併掉或被另一平台的判綠擋掉 | C1 | 身分改成(平台、測試名);判綠事件多帶 `items`(平台、測試名),判定照平台 | `t_spec_gate_redbase_written_on_red`〈跨平台同名兩支都紅〉〈一綠一紅〉〈判綠記到平台〉 |
| 2 | 驗收條款沒有斷言守住(ts 寫反只驗 any、5 MB、只看本分支、路徑子條件、`redbase_skipped_n`、中間份無斷言、S11 只測 .py) | C2、C8 | 逐條補斷言:ts 寫反只准第一份那一步命中;JSON 跳脫後超過 5 MB 那一支不存、其他照存;主線上早就有的判綠不算;路徑 `..`/反斜線/控制字元/空段/非 .json 各一例;`redbase_skipped_n`;中間份沒斷言不列「沒有斷言」;S11 加 .kt。S8 是回歸釘(該路徑本來就對)照實記。 | 同左各條 |
| 3 | 大小量法:5 MB 量原文不是 JSON;補讀測試檔另算一份 200 MB | C3、C7 | 寫入端照 JSON 跳脫後的長度累計並在寫前再驗整份;`_tg_read` 多一個 `max_total`,補讀時傳這次推送剩下的額度 | 〈JSON 跳脫後超過 5 MB〉 |
| 4 | 同一支檔每支測試都重切一次 | C4 | 讀取端 `_tg_rb_entry` 帶快取(同路徑同文字只切一次),`_tg_rb_load` 每份看截止時間;寫入端同一支檔只讀、只切一次 | 〈單檔 800 支紅燈測試 5 秒內〉〈寫入端同檔 800 支 3 秒內〉 |
| 5 | 訊息與救法:紅燈版路徑被忽略時 git add 救不回、孤兒檔救法不對、兩樣都沒提交整段靜默、寫入端讀不出帳不出聲、比對引擎裡印訊息 | C5、S3、A2、A3 | 寫入前查紅燈版路徑有沒有被忽略(被忽略就不寫、講原因);還沒提交的救法改「git add 並提交(被忽略時 -f)」;孤兒檔講「刪掉它,或把留痕一起提交」;推的就是工作目錄頂端時,紅燈版資料夾裡還沒提交的檔列 unreadable;寫入端讀不出帳印一句;拿掉引擎裡的 print(空樹起點由新增告警閘既有的 no_baseline 那句講) | 〈紅燈版路徑被 git 忽略〉〈救法講提交與 -f〉〈孤兒檔講刪掉〉〈都還沒提交〉〈寫入端讀不出治理帳印一句〉 |
| 6 | 寫入端的安全與重複解析:讀上一份紅燈版跟隨符號連結、不驗版本與指紋;建資料夾沒走共用守衛;內嵌測試檔路徑沒驗;補讀測試檔沒套前置處理 | S1、S2、A5、A6、A7 | 讀上一份走 `_repo_path_unsafe` 逐層擋符號連結、用比對端的 `_tg_rb_doc` 驗大小、指紋、版本;建資料夾走 `_note_audit_safe_dir`;`_tg_rb_entry` 只收 repo 相對的 .kt/.java;`_tg_rb_fill` 抹超長行、配不平列 unmatched、斷言訊息位置看兩端 | 〈紅燈版資料夾是符號連結〉〈上一份是符號連結〉〈上一份版本不認得〉〈內嵌路徑出界〉〈補讀的測試檔配不平〉 |
| 7 | 命名跟鄰居不一致 | A4 | 常數改 `_TG_RB_*`;測試改 `t_tq_guard_redbase_*`、`t_spec_gate_redbase_*`(計劃條款與筆記的綁定同步改) | 無(改名) |
| 8 | 文件與依賴說明:計劃指紋公式措辭、`redbase_skipped_n` 沒寫、pitfalls-code-loop 那條同步項、寫入端借比對工具內部函式的理由、紅燈版把整支檔固定進提交 | C6、C9、A1、S4 | 計劃改指紋公式與同步項、補 `redbase_skipped_n` 與平台身分;Systems/規格閘補欄位;Systems/test-guard 補一行 WHY(寫入端共用切函式與格式驗證是刻意的單一來源);寫紅燈版時印一句「存的是整支測試檔,檔裡其他內容也會跟著提交」;判綠排在不存清單最後 | 〈redbase_skipped_n〉〈講明整支會提交〉〈判綠很多時又被改的原因照記〉 |

另外:舊測試 S10「工作目錄多一行沒提交的留痕不採計」跟組 5 的新行為衝突;那條真正要守的是「不拿工作目錄的內容來比」,改成驗「不列改弱、只提醒還沒提交」,計劃 S10 與 S4 同步改寫。修 C8 的「只看本分支」時發現寫入端在「分支剛開、還沒有自己的提交」時把分岔點當成沒有(沿用比對端 `_tg_start` 的語意),整本帳都算進來;改成分岔點等於頂端照樣減,只有直接在 main/master 或分離頂端上工作時才看整本帳。

## 先查世界(r1 修補前,2026-11-03)

- PRIOR-ART: 組 5。git 官方文件 `git check-ignore`:預設不報已追蹤的檔(要 `--no-index` 才看);`git add -f` 才能加進被忽略的路徑(https://chromium.googlesource.com/external/github.com/git/git/+/cacab0c8566084901cd0f8ed6c9e1c4a5dc63677/Documentation/git-check-ignore.txt)。採用:寫入端查測試檔維持現狀(已追蹤的照存),另查紅燈版自己的路徑;救法寫明 `-f`。
- PRIOR-ART: 組 6。只檢查最後一段的 `O_NOFOLLOW`、`follow_symlinks=False` 擋不住中間層的符號連結,逐層 lstat 有時間差,較強的是逐層 `dir_fd` 加 `O_NOFOLLOW`(https://users.rust-lang.org/t/how-do-i-read-a-file-without-following-symlinks-including-symlinks-further-up-the-path/141321 、https://discuss.python.org/t/support-file-descriptors-in-os-readlink/109101)。採用:沿用本專案既有的逐層檢查 `_repo_path_unsafe`(單一來源,架構對齊席也點名它);逐層檢查之間的時間差屬多程序同時改路徑,照工具鏈威脅模型(單人、依序操作)在範圍外。排除:另寫一套 dir_fd 讀法(第二種做法)。
- 組 1、2、3、4、7、8 是本專案內部的身分鍵、測試覆蓋、量法、快取與文件問題,以既有程式與計劃為準,沒有外部做法要比。

## 改壞驗證

修完把新舊守衛逐一改壞(新程式 50 道),結果見同目錄改壞紀錄。
