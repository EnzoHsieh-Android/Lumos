# code-room3轉換器 r1 收貨

席報告:r1-正確性-sonnet.md(severity major,2 條)、r1-架構對齊-sonnet.md(severity clean,0 條;⚠ 一處交編排者:兩處各寫一次 `(?:Column)?TypeConverter`,原本就分兩處、鄰居沒有共用常數,判不另立常數)。
兩席初交格式不合(正確性席第 2 條沒有獨立 severity 行、檔尾多一行 severity;架構對齊席沒有引句),退回該席自己重交,內容沒改;卷證存的是重交版,從子代理逐字稿取。
收貨四道:兩份 quote-check 全錨定、refcheck 全對得上、report-normalize 已正規化;seat-check 兩席都只標 unreported 計劃筆記(只觀測)。正確性席自述曾在 repo 改 `_RG_TRIGGER_RE` 做翻紅實驗後還原,收貨時 `git status`、`git diff HEAD` 只有治理帳兩行(工具自動記),程式沒被留下改動。

## 重現表

| id | 席 | 嚴重度 | 重現 | 結果 | 去向 |
|---|---|---|---|---|---|
| F1 | 正確性-sonnet #1 | major | 載入 scripts/lumos 呼叫 `_rg_spans`,Java 檔 `@ColumnTypeConverter` 下一行 `@SuppressWarnings("x")` 再接 `public static Long fromDate(Date d)`;另跑舊名 `@TypeConverter` 同形、與夾 `@Nullable`(無括號)對照 | HIT:新舊名都回 `[('SuppressWarnings', 2, 3)]`,無括號那支回 `fromDate`;原有缺陷,本次條款 [S43] 寫成已涵蓋 | 折:改成先用 `_rg_annotations` 跳過整串註記、再用 `_rg_methods` 同一條取名規則;同族順手把範圍算到本體結束(`_rg_balanced` + `_rg_method_end`)。測試 `t_room_column_typeconverter_warns` 補 Java 夾註記的 `toDate` 與只改多行本體一行的情境,改前紅(2 條、後補的本體情境 1 條),改後綠;拿掉跳過註記那一步 3 條斷言紅 |
| F2 | 正確性-sonnet #2 | minor | 對照計劃 [S45] 原文「每個情境應得到跟 Room 2 相同」與驗收筆記:轉換器情境推送時用修正前守衛、沒提醒 | HIT:[S45] 照字面不成立 | 折:[S45] 改成照實寫轉換器情境推送時用修正前守衛、修正後改在 clone 手動跑;驗收筆記補一句 clone 那次是 r1 之前的版本 |

## 處置

- F1、F2 全折;沒有放行、沒有重現不到的。
- 同族掃描:找函式名的比對在 scripts/lumos 只剩轉換器這一處用 `[^;{]*?\b(\w+)\s*\(`,DAO 方法本來就走 `_rg_annotations`;改後兩者同一套切法。切法的既有限制(Kotlin `=` 換行接續的本體只算到 `=` 那一行)寫進計劃〈誠實界線〉。
