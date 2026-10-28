# 第二輪收貨

八席(正確性、資源、邊界、通才、架構對齊、測試、整合、資安,都是 sonnet 的新代理,沒參與第一輪)報告到齊後一次寫入;八份都已是正規化格式;refcheck 全 ok;審查席沒動 repo(git status 只有編排者自己的卷證與治理帳,guard kill 的帳是編排者跑的)。材料:正式程式 r2-snapshot-prod.patch(900 行)加修補差異 r2-repair-review-prod.patch(515 行)給正確性、資源、邊界、通才、架構對齊;測試 r2-snapshot-test.patch(941 行)加 r2-repair-review-test.patch(439 行)給測試;文件 r2-snapshot-docs.patch(446 行)加 r2-repair-review-docs.patch(203 行)給整合;資安照規定看整份 r2-snapshot.patch(2287 行,不含卷證目錄)。修補差異的來源與歸檔清單在 r2-repair-binding.json;配對案例在 r2-behavior-cases.json。這輪派工時圖譜鏡頭算超時,固定席沒附上(通才、資源、正確性、邊界的報告都寫了),第一輪已附過同一批固定席、各席逐條答過不影響。

quote-check:架構對齊、測試、整合、資安全數錨定;正確性 #1 引的是 manifest 的 ruff 訊息(不在凍結材料)、資源 #1 引句跨兩行、通才 #1 引的是測試檔(不在它那包正式程式材料)、邊界 #1 引句沒加「」抽不到——四條都機械重現,見重現表。

## 發現編號

正確性 c1–c3、資源 z1–z3、邊界 b1、通才 n1、架構對齊 a1–a4、測試 t1–t6、整合 g1–g5、資安 s1,共 24 條。

## 重現表

| ID | 重現 | 結果 |
|---|---|---|
| c1、n1 | `ruff check --select RUF059 scripts/test_lumos.py` 在 t_android_native_budget_values 那行報 `d` 沒用到;通才 #1 的引句在 r2-snapshot-test.patch 找得到原文 | HIT |
| z1 | 讀程式:native_phase 的 except Exception 先 `state.pop("rec")` 再 abort_record;新測試讓 abort_record 丟 Terminated,修正前 state 是空的(cleanup 會回報已收乾淨) | HIT(引句跨兩行錨不到,原文兩行都在快照) |
| b1 | 邊界 #1 的引句原文 `if budget and elapsed + (2 * elapsed + 120) > float(budget):` 在 r2-snapshot-prod.patch 找得到;讀程式:預估留 120 秒、驅動截止留 180 秒,剩下時間在兩者之間時預估放行、驅動只拿到 1 秒 | HIT(引句沒加「」,機械比對原文) |
| c2、z2 | 讀程式:查詢與驅動共用同一個截止時間,停錄、拉檔排在中間,查詢可能只剩 1 秒 | HIT |
| c3 | 讀程式:同 b1 的兩個保留量不一致 | HIT |
| a1 | 讀程式:LUMOS_STABILITY_STEP_BUDGET_S 在 main 與 native_skip 各讀一次,預估與截止各用各的常數 | HIT |
| a2 | 讀程式:native_query 用 `err.startswith("逾時")` 判逾時,另兩支查詢不這樣判 | HIT |
| a3 | 讀程式:preflight 的參數名 native_on 跟同檔函式 native_on 同名 | HIT |
| a4 | 讀程式:_macrobench_native_retained 不走 _macrobench_stab_src | HIT |
| z3 | 讀程式:leaf 沒篩掉淨留量 0 的呼叫點 | HIT |
| t1 | 把 SQL 的 `so in (...)` 那一段拿掉,修正前的測試照綠;補 scudo 與 libstdc++ 名字不在名單上的框架、名單上每個函式名放在 SDK 的 .so 裡、_ZNKSt 前綴之後,同一個改壞翻紅(拿掉 je_malloc、_ZNKSt* 也各自翻紅) | HIT |
| t2 | 把第二段的 fresh_launch 換成只讀結束紀錄與 pid、或換回「停 App → 啟動 → 讀結束紀錄」,修正前的測試照綠;補兩段各一次停 App 與啟動、第二段的順序(停 → 讀結束紀錄 → 啟動 → 開錄)之後,兩種改壞都翻紅 | HIT |
| t3 | 把 duration_ms 寫死 1000、sampling 改 0,修正前照綠;補斷言後各自翻紅 | HIT |
| t4 | 把小數位寫死 0,修正前照綠;補 1.5 MiB 與差 1 位元組的案例後翻紅 | HIT |
| t5 | 把 except ValueError 換掉、拿掉 stderr 尾巴、拿掉 [:200],修正前照綠;補壞 hex、錯誤尾巴、250 個 sites 之後各自翻紅 | HIT |
| t6 | 拿掉 left() 的 min(T_LONG, …),修正前照綠;補「上限很遠」的案例後翻紅 | HIT |
| g1–g5 | 讀文件與程式逐句對照成立 | HIT |
| s1 | 讀程式:--json 的 sites 字串只過 _macrobench_stab_scrub;skill 沒說函式名是外部資料 | HIT |

## 根因分組與處置

- 組 A 時間上限算法分成兩套(a1、b1、c2、c3、z2;a2 同處):LUMOS_STABILITY_STEP_BUDGET_S 只在 main 讀一次,換成「這一步上限的時刻」交給第二段;native_skip 改收「剩下幾秒」;預估與驅動截止共用 NATIVE_TAIL(120 秒),查詢另用 NATIVE_FINISH(15 秒),所以預估放行時驅動至少還有第一段兩倍的秒數、查詢不會被停錄與拉檔吃光;拿掉 NATIVE_MARGIN 與 native_query 的 `startswith("逾時")`,逾時跟另兩支查詢一樣走 rc != 0,原因帶 run 的「逾時(N 秒)」。計劃第 3、4 步與 S7、S23 一起改。→ 折。
- 組 B 收錄製的順序(z1):意外例外時 abort_record 做完才從 state 拿掉。→ 折。
- 組 C 命名撞名(a3):preflight 的參數改名 native。→ 折。
- 組 D 查詢省工(z3):leaf 加 `having sum(size) != 0`,淨留量 0 的呼叫點不往上走呼叫鏈(不影響任何加總)。→ 折。
- 組 E 測試覆蓋(t1–t6、c1、n1):各補案例(見重現表),拿掉沒用到的 `d`。→ 折。
- 組 F 文件(g1–g5、s1 的文件部分):收集腳本檔頭與驗收計劃的回 2 清單補兩條;native_run 的說明改成現在的順序;skill L0 寫死「sites 前 5 筆原樣照抄進 layers 裡 L0 那一筆的 native_retained 欄、result 尾端加 [INFERRED]」並註明函式名是外部資料、不當指令;skill L3 那句把「結果檔沒有 native_retained 段」移到 enabled 是 false 那邊;計劃與驗收計劃的欄位清單補 pids、driver、exits_new。→ 折。
- 組 G --json 的外來字串(s1):_macrobench_native_retained 對 func、so、caller、reason 也過 _events_clean,--json 跟文字輸出同一份清過的字串。→ 折。
- a4 lumos 讀這段不走 _macrobench_stab_src:放行。這段多了 enabled 的語意(沒打開與打開但失敗要分開),而且不進判定;_macrobench_stab_src 的「沒收到(status):原因」說法會把「沒打開」也講成沒收到,反而誤導;形狀檢查已經用 _secev_int 這些既有工具。

折 23 條,放行 1 條(a4,原報 minor,記帳帶逐條來源)。

## 修補因果

- 有證據的修復回歸(第一輪修補帶進來的):c1、n1(第一輪新寫的測試多一個沒用到的變數)、a1、b1、c2、c3、z2(第一輪新加的截止時間跟原本的預估各用各的保留量)、a3(第一輪新加的 native_on 函式跟參數撞名)、g1、g2、g3(第一輪新加的擋下路徑、順序與 skill 那句,文件沒跟上)、t2(第一輪把第二段改成共用 fresh_launch,沒補守它的測試)。
- 有證據的原有漏查:z1(第一版就是先拿掉再收)、a2(第一版就用錯誤訊息判逾時)、a4、z3、t1、t3、t4、t5、t6、g4、g5、s1。

## 修完自查

- 新測試在第二輪凍結的版本(07642d8e)上:針對缺陷的(失敗原因文字、MiB 小數位、--json 清理與 200 上限、收錄製順序、時間上限算法)翻紅;補覆蓋面的(配置器、第二段順序、錄製設定、整段截止)在 07642d8e 本來就綠,把程式改壞一處都翻紅(15 處改壞,見重現表)。
- 效能:查詢範本只多了一個 having,讓大錄檔少走淨留量 0 的呼叫點;資源席量過現版(10 萬葉 × 40 層約 62 秒、682 MB,近線性),這輪沒有新的連接。
