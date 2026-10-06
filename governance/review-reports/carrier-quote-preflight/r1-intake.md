# 設計第一輪處置
preflight-4: ran

首輪前掃與語意修正完整見 preflight-intake.md；PF1 只修測試前提，核心裁定沒有被前掃自行改寫。

| ID | 原席與觀察／判準 | 處置與證據 |
| F1 | integration-F1；HIT：合法 UTF-8 快照＋有引句且尾端 ff 的報告，writer rc0，完整 --spec 的 gate rc1/UnicodeDecodeError。 | 折入 S5 與報告編碼正反控制；r1-report-encoding-probe.json 為採信重現。r1-report-encoding-probe-incomplete-gate.json 缺 --spec，gate rc2，不能當編碼 gate 證據；原失敗留存。 |
| F2 | integration-F2、rollback-F1；HIT：引句驗證後、既有 hash 函式讀取前替換報告或快照，原 cmd_canary rc0，帳面 hash 匹配新版卻沒有有效引句。 | 折入 S6，同一份原始 bytes 與落帳 hash 核對；r1-material-race-probe.json 的兩種材料重現，expanded-counter-old 的實際函式 AST 普通/最佳化控制均翻紅。 |
| F3 | resources-F1；HIT：只檢查「沒有引句」無法鎖住兩條復原路徑。 | 負向測試補處置選項與改選載體兩段提示背書，S1 文字承諾保持。 |
| R1 | logic-F1、boundary-F1、architecture-F1；非 UTF-8 snapshot 裸例外觀察 HIT，擴張本案的 blocking 判準 MISS。 | 凍結核心限定有效 UTF-8 snapshot，原程式在引句判定前就中斷且不追加帳。採信 r1-defender-encoding-format.md 的單題反證，引句及引用核對通過；首次 r1-defender-encoding.md 的 blocking: MISS 非席位格式，不採作正式反證，原樣保留。正文釐清範圍與 REVISIT 2026-10-20 的明確入口。 |

原報 7 條、blocking 5；去重存活 3 條全折，無接受清單；駁回判準 1 項。每席原報告保持原等級與逐字內容。
正確前提初始反向控制 23 pass/24 fail；增加編碼、換檔及提示背書後，完整四項新測試 35 pass/50 fail。生產碼仍未修改，這是 test-first 翻紅，不是實作通過。
成功後材料變動照既有凍結規律與讀側重驗；本次機械控制明確測試的是驗引句後、落帳 hash 讀取前的替換，不宣稱消除所有時間點的跨程序修改。

鏡像複查：r1-mirror-raw.md 判 clean，核對全部原報及折入。fold-check rc1 的 reverse-omission 是正文 --report/--snapshot 對空 summary 的提示；正式 new project 骨架沒有 summary，工具規格明示訊號非 abort，不是本案規格矛盾。保留原 rc1 與人工裁定，未改工具或補不存在的必填欄位。
