preflight-4: ran

# r1 前置掃描(四項)與收貨

## 前置掃描

派一個 sonnet 前置掃描員對照程式驗計劃,回報 15 條(①未定義 2、②壞引用 1、③矛盾 3、④語意 9)。①②③與存在類直接修真檔;語意類逐條列在下面(修改前 → 修改後)。沒有動到「核心裁定」(Enzo 裁定的「直接擋、兩層都擋」不變),第二層的判法改了,所以交審查席審。

| 項 | 修改前 | 修改後 |
|---|---|---|
| ④1 指紋 | 「判定紀錄的指紋含筆記內容,所以 `text` 就是那一行現在的原文」 | 對照指紋不含筆記自身內容(`_note_reread_contrast_fp`);`text` 是判定當時那版的原文。第二層改成「頂端版筆記還一字不差留著那一行才算沒處理」,改掉那一行就是出口 |
| ④2 隱患 | 「改了筆記就要再對照一次(第一層),這是刻意的」 | 刪除;改寫成「筆記改了不必重判,程式改了才要」 |
| ④3 新機制 | 「不新增機制」 | 第二層是新的小機制(讀已提交判定紀錄內容、判結構行、比對表態);同一指紋多份紀錄取聯集 |
| ④4 判不了分法 | 淺層 clone 回 0、git 失敗回 1,沒寫怎麼分 | `_NoteRereadStop` 帶種類:參數錯回 2、環境沒有可判的東西回 0、判不了 block 時回 1 |
| ④5 表態類別 | 只寫加 `--kind reread` | 補 `_DRIFT_KIND_NAMES`、`drift scan` 排除、`_drift_ack_line_err` 分支、讀表態用 `_drift_load_acks` 與 `_drift_ack_key` |
| ④6 判不了原則 | 「跟 drift check 同一原則」 | 註明 drift check 的 RULE 撤除條件判不了只列出,本案不照那條 |
| ④7 輸出文字 | 沒提 | block 擋下時不印「這只是提醒」結尾句;說明與 `--help` 改寫回傳碼 |
| ④8 預設 warn 散落處 | 只列 `_drift_old_sentence_config` | 加 `_drift_config` 說明、`drift check --help`、`_drift_old_sentence_doctor_lines` |
| ④9 帳的數字 | 37 次、19 次提醒 | 主線帳實數:35 次 passed;reminded 18、recorded 5、none 12 |
| ③1 表態失效 | 第二層說 `text` 是現在原文,與表態綁現在那一行互相打架 | 同 ④1 |
| ③2 條款缺口 | 壞設定、逾時、淺層 clone、warn 第二層沒條款 | 條款擴成 S1–S13 |
| ③3 回退漏列 | 漏說明文字、doctor 提示行、CHANGELOG、既有測試 | 回退節補齊;實務隱患節列出要改斷言的三支既有測試 |
| ①1 指紋未定義 | 「同指紋」沒說哪種 | 明寫對照指紋 |
| ①2 「要處理層」 | 未定義 | 改寫成「記成要處理(must)的發現」 |
| ②1 條款亂序 | S7 在 S6 前 | 重新編號 |
| RETIRE-IF `--no-verify` | 「用 `--no-verify` 繞過的次數」(本機不留痕,數不到) | 改成 skipped-env 事件加 CI 在這兩步擋下的次數 |

## 收貨

六席(正確性、邊界、接手、併發、回滾、架構對齊,皆 sonnet)全部交回後才一次寫進卷證,報告取自逐字稿。接手與架構對齊兩份用 `report-normalize --write` 做純格式搬移(等級標記移成獨立行)。引句錨定:五份全錨;邊界席第 5 條有一句「改對照指紋的組成」不足 10 字不採信,該條另一句引句錨定成功,且併發席第 1 條以實驗重現同一件事(兩個提交,`c1..c2` 沒有候選、`base..c2` 有候選且指紋不同),照收。引用路徑檢查六份全對得上。seat-check 對這份派工單判 vacuous(派工單材料寫在每席物件裡,工具讀頂層),不影響判讀。repo 沒被席位動過(`git status` 只有本編排者的卷證檔;reflog 最新一筆是本編排者的提交)。

## 處置(63 條;折 61、放行 2、駁回 0)

編號:COR=正確性、BND=邊界、HND=接手、CON=併發、RB=回滾、ARC=架構對齊,後接該席報告裡的序號。

| finding | 重現 | 根因組 | 去向 |
|---|---|---|---|
| BND5、RB1、CON1 | HIT(三席獨立;CON1 實驗重現) | G-CIFP 合併讓對照指紋變,CI 主線紅 | 折:第一層只在本機擋、CI 只印;第二層改依筆記路徑讀紀錄 |
| COR1、BND4、CON3、HND2、RB8 | HIT(`_drift_ack_key` 只含路徑原文種類) | G-ACK 表態永久有效、可事先表態 | 折:表態綁點出它的判定紀錄指紋;沒有判定點出不准表態 |
| COR2、CON6 | HIT(真實紀錄 quote 皆為 text 子字串) | G-EXIT 改一字就放行 | 折:改比對 `quote` 是否還在頂端版 |
| COR3、BND12、CON7 | HIT(`reread-record` 對錨點不符只警告照收) | G-PROV 空紀錄也算已對照 | 折:第一層只認 provenance_ok 為真 |
| COR4、BND3、CON2、HND7、RB4、ARC8、RB3 | HIT(三種原因同為 skipped) | G-UNDEC 判不了與環境沒東西分不開 | 折:`_note_audit_resolve` 多一種 `undecidable`;終點找不到歸判不了;讀設定前的例外照 block |
| BND1、COR7、ARC6 | HIT(實數:`[test:` 1735 行、正文提到標記的說明句) | G-STRUCT 結構行太寬、另造判法 | 折:只認摘要區規則類行,用 `INVARIANT_RE`、`_notelines_regions`、`_ns_summary_logical`,收成一支共用函式 |
| COR5、BND2、CON4、RB7、HND6 | HIT(spec 兩句互斥) | G-ORDER 兩層先後矛盾 | 折:第二層不論第一層都跑 |
| RB2、COR10、HND4、ARC5、BND10 | HIT(`_drift_retire_config` 先例) | G-OSDEF 子開關不看總開關 | 折:old_sentence 沒寫照總開關 |
| HND1 | HIT(存量漂移守衛的 RULE 欄位齊、半年內確認) | G-DOCS 被弄成說謊的條款 | 折:列入〈要一起改的說法〉並標 superseded |
| HND3、RB6 | HIT(`reread-record` 收尾句、手冊三處) | G-DOCS | 折:列出要改的手冊與說明,改收尾句 |
| HND4(CI 與版本)、ARC9、RB10 | HIT | G-CONSUMER 消費專案 CI 與版本號 | 折:升 v1.3、CHANGELOG 寫明、消費專案 CI 另案 |
| COR9、BND6、CON5、HND5、ARC2、RB5 | HIT(掛鉤只特判 130、丟標準錯誤) | G-HOOK 掛鉤回傳碼與逃生段 | 折:照鄰居閘處理回傳碼、印逃生段、不丟標準錯誤;CI 照 drift check 那步 |
| ARC3 | HIT | G-HOOK 訊息走向 | 折:擋下原因走標準錯誤「擋下:」、判不了共用 `_drift_unknown_hint` |
| ARC7 | HIT | G-ACK | 折:比對走 `_drift_ack_buckets` 的綁定類別(加進 `_DRIFT_BOUND_KINDS` 那一類) |
| ARC1 | HIT(`_note_reread_check` 已被複雜度放行) | G-SPLIT | 折:照 m1、retire 拆三段 |
| COR8、BND11、HND8 | HIT | G-TESTS 既有測試清單不全 | 折:列出十支並寫怎麼找其餘 |
| COR6 | HIT(現行不讀紀錄內容) | G-ORDER | 折:改寫成新行為、不稱「照舊」 |
| BND7 | HIT | G-STRUCT 同一行出現兩次 | 折:含引句的每一行都判,表態以行原文綁 |
| BND8 | HIT(無大小上限) | G-READ 壞檔大檔 | 折:用 `_nodehome_cat_blobs_capped`,單檔 256 KB、總 8 MB,壞檔判不了並講怎麼修 |
| BND9、CON9、HND10 | HIT(既有 `_note_reread_show`) | G-OUT 輸出跳脫與上限 | 折:一律過 `_note_reread_show`、`shlex.quote`、上限 `_NOTE_REREAD_LIST_MAX`;表態要求判定紀錄點出那一行,行號錯就回 2 |
| BND13、RB9 | HIT(35 筆候選皆 0) | G-EVID 證據強度 | 折:原問題節寫明 m1 沒有誤報率實測 |
| HND9 | HIT | G-CIFP about_code 增減與合併讓指紋變 | 折:訊息與隱患寫明 |
| HND11 | HIT(drift skipped-env 沒有 check 欄) | G-MEASURE | 折:RETIRE-IF 改成 reread 的 skipped-env 與逐筆人工看 drift 的;blocked 事件記要處理的行;REVISIT 隨上線日順延 |
| HND12 | HIT | G-EXPORT 對外送出 | 折:隱患節改寫,不再列為已排除 |
| BND6(消費專案 CI 後盾)、RB10 | HIT | G-CONSUMER | 折:同上 |
| ARC4 | HIT | 事件名 reminded 與鄰居 warned 不同 | 放行:既有 18 筆 reminded,改名會斷掉統計連續性;minor |
| CON8 | HIT | 同一提交改開關可自我解除 | 放行:所有閘共有的既有性質,不是本案引入;已寫進隱患節;minor |

`refuted-set`:none。
