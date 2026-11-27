# r2 收貨紀錄(選擇點挑法易混淆寫法優先)

材料:r2-snapshot.md(第 2 版修訂稿,123 行)。四席全數交回後才一次從逐字稿存檔。正確性席 F4、邊界席 B9 的引句不到 10 字,架構對齊席總結句寫了「無 major」被讀成更高等級,三席退回原席只改那幾行,存最後一版。全數正規化、引句全數錨定。修補因果:B1、F3、I2(存活行沿用)是 r1 改寫〈白話〉時新寫出的不準宣稱,與 r1 的 b1、i1 同一類(帳上既有紀錄在新挑法下怎麼走)——r1 修補沒把這類講完整;不是程式回歸,--regression-set none。

## 發現與去向

| id | 席 #條 | 原報 | 一句 | 去向 |
|---|---|---|---|---|
| p1 | 正確性 F1 | major | 既有釘值測試上線後會紅 | 折:〈做法〉列出 8 行與新值,補 S10 |
| p2 | 正確性 F2 | major | S6 測的函式不看挑法,翻不紅 | 折:S6 改走 _choice_kill_pick 完整路徑、五種狀態 |
| p3 | 正確性 F3 | major | 依測試雜湊沿用的存活,帳與畫面壞法錯位 | 折:沿用要比 new_sha,不同就重跑;補第二條 WHY 與 S9 |
| p4 | 正確性 F4 | minor | RET 與等級表落地順序 | 折:〈做法〉寫明本計劃先上、第四批兩常數同一提交加 |
| q1 | 邊界 B1 | major | 同 p3 | 折:同 p3 |
| q2 | 邊界 B2 | major | 同 p2 | 折:同 p2 |
| q3 | 邊界 B3 | major | 等級值沒驗證 | 折:自檢加「值必須是 int 1 到 3」,S3 補值壞案 |
| q4 | 邊界 B4 | major | tiers 空字典與順序來源沒定 | 折:None 或空字典當一級;順序一律照 categories;S5 補空字典 |
| q5 | 邊界 B5 | major | 第 1 級全空時要退到下一級 | 折:〈做法〉寫明串接後往下取;補 S8(排除與跳過兩案、全空回用盡) |
| q6 | 邊界 B6 | major | S7 的空帳本複本做不出來 | 折:S7 改成 clone 複本跑新舊版 choice-points 比對,加一次性腳本數帳上會重跑的存活行;不跑殺傷力 |
| q7 | 邊界 B7 | minor | 改挑後變不唯一的行數沒量 | 折:S7 加這個計數 |
| q8 | 邊界 B8 | minor | 落點與既有 WHY 原文 | 折:〈落點〉補有效處置 WHY 的 survived 句 |
| q9 | 邊界 B9 | minor | 同 p4 | 折:同 p4 |
| s1 | 整合 I1 | major | 同 p1 | 折:同 p1 |
| s2 | 整合 I2 | major | 存活行重跑與判讀作廢沒寫 | 折:〈白話〉分四種講、〈實務隱患〉寫第一次推送的代價 |
| s3 | 整合 I3 | minor | 落點漏列兩處同類文字 | 折:〈落點〉補規格閘 choice-points 那條 WHY、第二批計劃那句 |
| s4 | 整合 I4 | minor | 論文沒有 11% | 折:改成照原文(85% 判沒用、抑制推到 89% 有用),11% 標明是換算 |
| s5 | 整合 I5 | minor | 轉型列描述不符 | 折:改成 toIntOrNull→toInt 這類失敗時從回 null 改成丟例外 |

## 機械重現

| id | 做法 | 結果 |
|---|---|---|
| p1 s1 | 正確性席在複本照新挑法改 _choice_pick_iter,`t_choice_points_batch2_stable` 與 `t_choice_points_batch3_stable` 各紅一條,列出 8 行 | HIT(席位實跑) |
| p2 q2 | 讀 scripts/lumos 的 _choice_disposition:參數只有帳、放行檔、bound,不吃挑法 | HIT |
| p3 q1 s2 | 讀 _choice_kill_pick:survived 且 tests_sha 相同進 carried,不比 new_sha | HIT |
| q3 | 推演:等級值 0 或 4 時串接只走 1 到 3,該類不被交出 | HIT |
| 其餘 | 讀快照與對照檔即可確認現象 | HIT |

## 先查世界

- PRIOR-ART:舊結果要不要沿用(p3 q1 s2)——StrykerJS 增量模式比對上次與這次的程式碼與測試,只沿用比對得上的壞法的舊結果 https://stryker-mutator.io/docs/stryker-js/incremental/ ;PIT 增量分析以歷史檔記每個壞法的結果 https://pitest.org/quickstart/incremental_analysis (確切的沿用條件我沒查到原文,未確認)。採用:存活要壞法相同、守的測試也沒變才沿用。
- 方向:對 — 同類(帳上既有紀錄在新挑法下怎麼走)連兩輪有 major,但兩輪的修法方向一致(照既有有效處置、只補講清楚與補比對),同類工具也是「壞法對得上才沿用」:StrykerJS 與 PIT(上兩個網址)。
- PRIOR-ART:等級值驗證(q3)——同檔 check.py 對詞表外的值報問題、整張表判壞的既有慣例。採用。
