# r3 收貨與去向(2026-10-27)

材料:r3-snapshot.patch(0701350..bf9dac49,3684 行)加修補鏡頭 r3-repair.patch(ce46398a → bf9dac49,1472 行)與 r3-repair-binding.json。7 席全新代理:正確性(C)、邊界(B)、資源(P)、合約與文件(K)、通才(G)、架構對齊(A)、資安(S)。七份報告從逐字稿存檔;架構對齊席只做了 report-normalize --write 的純格式搬移。quote-check:四席全數錨定;邊界 2 句(B3、B5)、資源 1 句(P2)、合約 3 句(K2、K6、K8)錨不到——引的是這次改動以外的既有程式或文件,審材只含改動附近的上下文;照規定不直接採信,下表逐條機械重現。

這輪有 major,照代碼審規則 accepted 必須為空:39 條全折(修正前 bf9dac49 → 修正後見 r3-fix.json)。

## 重現(觀察與判準分開驗)

| id | 重現 | 結果 |
|---|---|---|
| S1、K3 | app_dirs 一項帶換行與 ESC:check 的原因原樣帶控制字元;補 t_android_e2e_gate_output_clean 第一組,修前紅 | HIT |
| G1 | feature_runs 鍵名帶換行與 ESC:原因與 bad_cases 原樣帶;補同一支第二組,修前紅 | HIT |
| C1、B2、K1、G3、P4 | 501 份紀錄、最舊那份有待看的 AI 放行:waive --list 印沒有任何放行、--ack <它> 印沒有待看;補 t_android_e2e_waive_all_records,修前紅 | HIT |
| P1 | 150 支深一萬層的檔:歸屬判斷 56.4 秒;補 t_android_e2e_scope_perf 第一條,修前紅 | HIT |
| P2 | 三萬條 flows 的重複檢查 9.7 秒;補同一支第三條,修前紅(引句錨不到,改以這條重現採信) | HIT |
| P3 | 兩萬支範圍外的檔對一萬條 flows 的範圍判斷 13.2 秒;補同一支第二條,修前紅 | HIT |
| G2、C5 | --changed 五十支檔建了 50 次查表;補同一支第四條,修前紅 | HIT |
| G4 | schema=99 的紀錄:接下來叫人修好或刪掉;補 t_android_e2e_record_unreadable ①,修前紅 | HIT |
| K4、C6 | runs.ended=garbage:waive 寫得進去、判定照擋;補 ②,修前紅 | HIT |
| B5 | runs.ran 是清單、skipped 是整數、items 不是清單:各走到不同的錯誤(含判定內部出錯);補 ③三條,修前紅(引句錨不到,改以重現採信) | HIT |
| P7 | 提交裡的紀錄 20 萬個 [:判定內部出錯(RecursionError);補 ④,修前紅 | HIT |
| P6 | 單份超過 2MB 的紀錄,waive 照樣整份讀進來寫回;補 ⑤,修前紅 | HIT |
| G5 | 合併衝突標記的紀錄,錯誤訊息只剩 JSONDecodeError、沒有位置;補 ⑥,修前紅 | HIT |
| C2 | 整套 pass 在 10:00+08:00、按功能 fail 在 05:00+00:00(較晚):現在擋;把 _e2e_ts 改成字串比,原有測試照綠(席位改壞實測);補 t_android_e2e_gate_r3_paths ① | HIT(守衛缺口) |
| C3 | flow 改名、設定跟著改、整套跑新的那支:現在放行;拿掉 f in have 原有測試照綠(席位改壞實測);補 ② | HIT(守衛缺口) |
| C4 | 主線分岔後才開記憶體、分支整套跑沒有記憶體結果:接下來只叫人整套重跑;補 ③,修前紅 | HIT |
| B4 | 舊分支(兩端都沒有 e2e 段)只改記憶體設定:訊息說 App 程式不一樣;補 ④,修前紅 | HIT |
| B1 | waive --commit deadbeef:現在回 2;把解析後那道改成 if False 原有測試照綠(席位改壞實測);補 ⑤第一條 | HIT(守衛缺口) |
| B6 | 建分支 beef,--commit beef:存成分支指的提交;補 ⑤第二條,修前紅 | HIT |
| K7 | 拿掉 waive 的 except KeyboardInterrupt,原有測試照綠(席位改壞實測);補 ⑤第三條 | HIT(守衛缺口) |
| K2 | app_dirs=["app"]、shared_paths=["core"]、改 core/N.kt:not-required;補 t_android_e2e_config_r3 第一條,修前紅(引句錨不到,改以重現採信) | HIT |
| B3 | shared_paths 寫 .//app/src/main/A.kt:check-config 回 0;補同一支第三條,修前紅(引句錨不到,改以重現採信) | HIT |
| S2 | 查主線候選失敗、被推送提交刪掉整份 macrobench.json:回 none;補 t_android_e2e_gate_uses_unclear,修前紅 | HIT |
| S3 | 主線分岔後 app_dirs 加 lib、分支改 lib 底下的檔:not-required;補 t_android_e2e_gate_mainline_wider,修前紅 | HIT |
| S5 | 最新一份紀錄超過 2MB:佔名額、不算進沒讀的份數 | HIT(讀碼;t_android_e2e_record_scan ②兩邊一致的斷言守) |
| P5 | 開場掛鉤的 3 秒沒扣前面幾段已用的時間(席位造 enforcement 卡住加 500 份大紀錄,整支 10.07 秒) | HIT(席位量測) |
| K5 | S41 寫三處都是 3 秒,--ack 實際 60 秒 | HIT(讀碼) |
| K6 | pitfalls-code-loop、棧別提問表態閘、lumos-code-loop skill、scripts/lumos 的說明與 --help 還寫五道;計劃做法 4 的治理帳沒列 ci;句子正本兩處日期不同 | HIT(grep;引句錨不到,改以 grep 採信) |
| K8 | 拿掉驗收設定、紀錄讀不懂這幾種擋下不印放行指令,README 與 pre-push 逃生路寫「照它印的放行指令」;驗證筆記的重驗條件已成立仍標 pass | HIT(讀碼;引句錨不到,改以讀碼採信) |
| G6 | _e2e_ai_pending 與 _e2e_ai_pending_one 各寫一套同樣的條件 | HIT(讀碼) |
| A1 | 複本一致性測試寫死兩個路徑、只取第一份同名函式,沒照既有複本守衛掃全部 | HIT(讀碼) |
| S4 | 沒有互動終端時 AI 一步放行 | HIT(計劃明講的設計取捨) |

## 去向(根因分組,一條規則補一組)

1. 外來文字進擋下訊息:S1、K3、G1 → 折。改在結果出口 _e2e_gate_out 統一清原因與清單裡的字串,不再逐點補(r2 只清了檔名,r3 又找到兩處,換形狀)。
2. 人明著下的指令套了看一眼用的名額:C1、B2、K1、G3、P4、K5、S5 → 折。--list 與 --ack 讀全部紀錄、只留時間上限(--ack 60 秒)、用完講沒讀到幾份;太大的紀錄算進沒讀的份數;條款 S41 改寫成兩處 3 秒、兩個指令不設份數上限。
3. 平方工作量:P1、P2、P3、G2、C5 → 折。查表只查到功能路徑最深那一層(P1 是 r2 修補引入的);範圍判斷的 flows 用集合;重複檢查用計數;--changed 只建一次查表。
4. 讀不懂的判斷寫入與判定各一套:G4、K4、C6、B5、P6、P7、G5 → 折。寫入端用跟判定同一套(紀錄格式、欄位型別、結束時間),單份超過 2MB 不寫;判定讀樹時接 RecursionError;schema 較新叫人更新 lumos、git 暫時讀不出不叫人刪;讀不懂的訊息保留位置。
5. 判定路徑的守衛缺口與訊息:C2、C3、B1、K7 → 折(補測試,實作本身正確);C4、B4、B6 → 折(主線較新時叫人先合主線、舊分支只改記憶體設定時訊息講記憶體、--commit 解出的提交要以給的那串開頭)。
6. 判不清就擋的漏洞:S2、S3 → 折。查主線失敗、被推送提交刪掉整份設定時看上一版;主線分岔後改了驗收設定時,另用主線設定算兩端指紋,不同就擋並叫人先合主線。
7. 跟鄰居的做法:A1、G6 → 折。複本一致性測試照 t_ci_latest_attempts_copies_identical 掃主程式加所有 hook、偵測重複;_e2e_ai_pending 改成呼叫 _e2e_ai_pending_one,補兩者算出一樣的斷言。P5 → 折:開場掛鉤的 3 秒跟 _inner_budget 取小。
8. 文件:K2(README 中英、skill 寫明 shared_paths 要在 app_dirs 底下,設定檢查擋)、K6(五道改六道、治理帳補 ci、日期統一 2026-10-27)、K8(README 中英與 pre-push 逃生路補「這幾種不印放行指令」、驗證筆記改 stale)→ 折。
9. 設計取捨:S4 → 折成計劃的回頭條件(2026-12-31 看 AI 放行的筆數與看過的比例,過高就改成沒有互動終端時不准放行)。

## 修補因果(載體帶 --regression-set)

- 有證據的修復回歸:P1(r2 改的前綴查表,修前 0.7 秒、修後 64.8 秒,席位兩版實跑)、G4(r2 加的 bad_record 範圍太寬)、G5(r2 為接 RecursionError 把其他例外的訊息也砍了)、G6(r2 為逐字複本手抄了一份條件)、B1(r2 新增的 _e2e_waive_commit 只守了一半)、K5(r2 加的 60 秒跟條款不符)、P4(r2 引入名額,--ack 沒接上份數)。
- 原有漏查(修前修後同樣):S1、K3、G1(r2 只清了檔名)、C1、B2、K1、G3、C2、C3、C4、C5、G2、B3、B4、B5、B6、K2、K4、K6、K7、K8、P2、P3、P5、P6、P7、S2、S3、S5、A1。
- C6:「放行與重跑都不會覆蓋它」那句是 r2 新加的、對結束時間讀不懂這一類不成立;底層的寫入與判定不一致是原有漏查。判原有漏查,措辭這一半併進 r2 修補的責任寫在這裡。
- S4:設計取捨,不分回歸。

## 上限

這是 high 的第三輪(上限)。這一輪的修正差異沒有再給全新席看;處置閘只判每條有沒有去向。後續的決定與回顧另記(cap-decision、retro)。
