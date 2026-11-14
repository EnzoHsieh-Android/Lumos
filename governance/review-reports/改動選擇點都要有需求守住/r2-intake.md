# r2 收貨紀錄(改動選擇點都要有需求守住)

六席(正確性、邊界、整合、資源、通才、架構對齊;皆 sonnet)全到後才一次從逐字稿存進卷證;收貨前沒動被審材料。quote-check:正確性 27 句錨 26、邊界 30 句錨 29,其餘四席全錨(錨不到的兩句見重現表)。共 73 條(c 16、b 14、i 17、z 11、t 12、a 3),blocking 31。

## 分組(依根因)

| 組 | 根因 | 發現 | 最高 | 處置 |
|---|---|---|---|---|
| H1 | 沒有語法樹、用文字近似:運算元範圍、SBR 陳述位置、乾節點跨行與函式本體範圍、UOI 布林判定 | b1、b2、b5、b6、b7、c3、c9、c16、i4、t2、z10、b12 | major | 折(換形狀):使用者 2026-11-14 裁改用 ast-grep 語法樹;運算元用後設變數、SBR 限 statements 直接子節點並排除參數與 lambda 結果、乾節點以節點為單位(論文公式 1);乾節點形狀收窄(裸呼叫、接收者名、引數節點) |
| H2 | 一行一個壞法的挑法與唯一性:篩選條件與往外帶行互相矛盾、「已知編不過」沒有實體、候選攤平洗牌偏離 Listing 2 | c1、b3、i8、t7、c2、b4、i11、t4、t1、z11 | major | 折:唯一性只在身分段定義、不唯一可判;刪「已知編不過」改成型別前提事前擋(論文 3.2.1);照 Listing 2 先洗類別再取節點與候選 |
| H3 | 殺傷力批次的執行面:每壞法跑全部測試沒提前停、中斷丟光、abort 與 killed 優先序衝突、缺列被當 survived、多計劃身分 | z1、z2、z3、c5、c6、c7、i1、i16、t5、z6、z7 | major | 折:cmd_guard_kill 加 stop_group_on_kill 與 on_row、工作樹登記;abort 的測試拿掉、缺結果記 no_result;守的測試取聯集、按相關度排序;--max-mutants;開跑前印估計與逾時上限 |
| H4 | 回報上限與型錄改動讓帳失效:B 當種子一提交就重抽、型錄一改挑法全換 | t3、z9、c12、i2、t6、i3 | major | 折:種子改用「曾經存活的行」集合;有效處置改以行為單位,型錄改動不讓舊帳失效、帳記型錄雜湊 |
| H5 | 推送閘接線與讀版本:掛鉤版本探針、碰到的計劃與狀態讀工作目錄、算不出來擋與規格閘 fail-open 衝突、超大檔永久擋、兩套主線 | i6、i7、c13、t11、z8、i14 | major | 折:掛鉤探 dest 字樣才帶參數;碰到的計劃用 _drift_tree_env 在 B 的樹建圖譜;算不出來放行記 unverified、單檔超限跳過列出;choice-points 預設範圍也用 _push_mainlines |
| H6 | situation-rule --point 內部零件、point 條款免預期值表 | i5、i15 | major | 折:抽平台與檔解析、事件欄位、結尾提示三塊;point 事件不免預期值表 |
| H7 | API 列編不過、缺 import、會掛住 | c4、c8、b9 | major | 折:需補 import 欄並自動帶;拿掉 first/last、take/takeLast、drop/dropLast、collectLatest/collect、coroutineScope/supervisorScope |
| H8 | 帳量:test_blobs 物件縮不了、kill-log 每配方一列 | z4、z5、i13 | major | 折:每筆只存 tests_sha、對照放 run 一次;choice-kill 不寫殺傷力帳本;S20 釘 ≤4096 |
| H9 | 對論文的引用不實 | t10、b10、c10、i9、i10、b11 | minor | 折:表 1 候選補齊(ROR 補 <=、AOR 補 * / %)、差異清單補 UOI 與種子、3.2.4 不再當種子出處、A.1.6 改 A.3.2、乾節點第一版補 A.1.11/13/16/20/22/24 |
| H10 | 其他:輸出與排版、測試輔助路徑通則、定位解析、judge 讀哪一版、無規格的出口訊息、manual 計劃、RETIRE-IF 召回與樣本、環境變數旁路、old 子字串唯一 | i12、b8、b13、c14、i17、c15、t12、t8、t9、b14、c11 | minor | 折:每種原因最多 20 行、source set 通則、定位從右切、judge 讀 HEAD 與同一套範圍、訊息提示補 lands_in、RETIRE-IF 加樣本下限與 run 的行數、唯一性照 count(old);c15、t8 放行(規格閘 manual 裁定與既有環境變數慣例,天花板已寫) |
| H11 | 架構對齊 | a1、a2、a3 | minor | a2 折(choice-judge 拆成獨立子指令,同 guard kill-add 形狀);a1、a3 放行:推送那一道要跟預期值表合在同一次輸出所以放規格閘、situation-rule 的人裁寫回流程共用所以加 --point,形狀差異寫在計劃 |

放行:c15(只提醒不擋是規格閘既有 manual 裁定)、t8(環境變數關閉沿用 LUMOS_HIGH_RISK_EVIDENCE_SINCE 慣例並印一行)、a1、a3(理由同上表)。其餘全折。

## 修補因果(r1 折入造成的)

regression:c1、b3、i8、t7(r1 新增一行一個壞法的唯一性寫法)、c2、b4、i11、t4(r1 新增「已知編不過」)、t3、z9、c12、i2(r1 新增回報上限種子)、t6、i3(r1 新增重算壞法比雜湊)、z3、c6(r1 新增 abort 規則)、z2、c7、i1(r1 宣稱中斷照記但沒改 cmd_guard_kill)、i6(r1 新增 --push-check 參數)、t10、b10、c10、i9(r1 對論文的轉述)。其餘是 r1 沒折完或新角度。

## 先查世界

- H1 PRIOR-ART:論文 2.2 在語法樹上產生壞法、3.1 公式 1 乾節點以節點為單位(https://arxiv.org/pdf/2102.11378);Trail of Bits mewt/MuTON 用 tree-sitter 做跨語言變異(https://blog.trailofbits.com/2026/04/01/mutation-testing-for-the-agentic-era/);ast-grep 以 tree-sitter Kotlin 文法剖析(https://github.com/ast-grep/tree-sitter-kotlin),節點名照 https://github.com/fwcd/tree-sitter-kotlin 的 grammar.js(已下載核對 comparison_expression、conjunction_expression、statements 等)。排除:剝註解字串後的文字比對(r1 b2/c7、r2 b1/b2/b5/c3 連兩輪打穿)。
  方向:要換 — 同一根因(沒有語法樹)連兩輪 major;論文與 mewt 都在語法樹上做(https://arxiv.org/pdf/2102.11378、https://blog.trailofbits.com/2026/04/01/mutation-testing-for-the-agentic-era/);攤給人裁,使用者 2026-11-14 選「改用 ast-grep 語法樹」。
- H2 PRIOR-ART:論文 4.1 Listing 2 先洗運算子類別、3.2.1 編不過事前用規則擋(https://arxiv.org/pdf/2102.11378)。
- H3 PRIOR-ART:論文 2.1 每個壞法只跑覆蓋那一行的最小測試集、2.3 批次(https://arxiv.org/pdf/2102.11378);沒有覆蓋率,用排序加殺掉就停近似。
- H4 PRIOR-ART:論文 2.3 上限是限制人要看的量(https://arxiv.org/pdf/2102.11378);種子改用不受帳本提交影響的集合。
- H5、H6、H8、H10、H11:內部接線,沿用既有零件(_drift_tree_env、_kt_sit_spec_names_calc、pitfalls 掛鉤探針、guard kill-add 的子指令形狀)。
- H7、H9:對照論文表 1、附錄 A 原文(已讀 PDF 第 4、14–22 頁)。

## 重現

| id | 重現 | 結果 |
|---|---|---|
| c5 | 引句是欄位清單,快照該處寫法是「`file`、`line_sha`(…)、`old_sha`…」帶括號說明,席位拼成一串;讀快照〈用詞〉壞法身分確認不含計劃 | HIT |
| b4 | 引句與快照「同一個 (列號, 壞法) 在 `--stats` 累計,累計 3 次以上列為」差兩字;讀快照確認「已知編不過」沒有資料結構 | HIT |
| z1、t5 | 讀 cmd_guard_kill:每條配方一次 _kill_run、無提前停 | HIT |
| c7、z2、i1 | 讀 cmd_guard_kill:result_out 與 kill-log 在迴圈後才寫;_situation_rule_signals 第一個訊號 raise | HIT |
| i6 | 讀 pre-push:pitfalls 那行先 grep dest 探針才帶 --pushed-ref | HIT |
| t10、b10、c10、i9 | 讀論文 PDF 第 4 頁表 1、第 7 頁 Listing 2、第 6 頁 3.2.4 | HIT |
