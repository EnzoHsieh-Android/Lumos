# code-選擇點存活回指條款第一段 r1 收貨

- 派八席(正確性、資源、邊界、合約、通才、架構對齊、資安、規格符合,sonnet)。正確性、資源、邊界、合約、架構對齊審 r1-pack-code.patch(程式與文件,1791 行);通才、資安、規格符合審 r1-snapshot.patch(完整一份,2431 行)。記帳 --spec 與 --reviewed 一律填整份快照。
- 八席全部交回後一次存檔;格式都過 report-normalize。規格符合席兩句引句引的是計劃原文(不在 patch),編排者核對計劃確有該句,機械重現 HIT;資安席判 clean、零引句(非載體)。
- 編號:正確性 c1–c4、資源 s1–s4、邊界 b1–b6、合約 k1–k2、通才 g1–g5、架構對齊 a1–a6、規格符合 p1–p2,共 29 條;major 6 條(c1 c2 s1 b1 b2 k1 g1 重疊成三組)。輪內有 major,全部折入。

## 依根因分組(修正提交 87e706d42)

| 組 | 根因 | 發現 | 折法 |
|---|---|---|---|
| F1 | via cov 帶過去與 reach 有效沒守不明標記 | c2 b2 k1 g1 | `_choice_cov_sha` 遇不明回 None,帶過去與 reach 有效都判不同;t_choice_cov_carry 補案例 |
| F2 | Robolectric 辨識靠原始碼字串 | c1 b1 | 改看 exec 有無 `org/robolectric/` 類別;新增 t_choice_cov_robo_exec |
| F3 | 掛覆蓋才紅沒有斷路、預估漏算、重跑沒標記與上限 | s1 s2 b6 | 連續 3 支斷路、兩趟秒數進預估、重跑帶標記並照剩下時限;新增 t_choice_cov_red_breaker |
| F4 | 全部命中快取時樹上沒有類別 | c3 g2 | 分析任務依賴編譯、沒類別記暫時性「分析失敗」 |
| F5 | 分析輸出缺鍵當沒經過 | c4 | 缺鍵或型別不對記不明 |
| F6 | 分析沒替壞法留時間 | s3 | 門檻加一個壞法的預估 |
| F7 | 沒開覆蓋也查樹、cov_sha 讀寫重複 | s4 g4 a4 | 共用 `_choice_cov_sha_fn`、只在需要時算 |
| F8 | judged 計數對不上 | k2 g3 | judged cov、run 多 cov_judged,三者相加等於 ran |
| F9 | 假 Gradle 不讀 init script | g5 | 新增 t_choice_cov_init_scripts 釘住腳本關鍵片段 |
| F10 | 讀不出來的快取永不重量 | b3 | 刪掉重量 |
| F11 | 專案套件靠資料夾正規式 | b4 | 改讀 package 宣告 |
| F12 | 覆蓋基準沒走名稱檢查 | b5 | 走 `_test_name_ok` 與撞名檢查 |
| F13 | 架構對齊六處 | a1 a2 a3 a5 a6 | init 路徑與寫入共用、拿不到資料夾印原因、改名搬位、help 寫明、on_signal 共用 |
| F14 | 規格符合兩處 | p1 p2 | 清快取每次開頭做、母計劃標記 |

## 重現表

c1、b1 HIT(兩席各自寫實驗重現 AndroidJUnit4 與基底類別判成非 Robolectric);c2、b2、k1、g1 HIT(四席各自重現帶不明標記時被帶過去);s1 HIT(席位重現 40 支全紅不斷路);其餘由編排者讀程式確認 HIT;p1、p2 引句在計劃原文,HIT。無 MISS。

## 先查世界

PRIOR-ART: F2 判斷測試是不是 Robolectric——不靠原始碼字面(註解、基底類別、runner 別名都會漏),改看執行時實際載入了 Robolectric 的類別;JaCoCo agent 對所有載入的類別記執行資料(https://www.jacoco.org/jacoco/trunk/doc/agent.html ),所以 exec 裡有 `org/robolectric/` 類別即代表那支測試在 Robolectric 下跑。同一個判讀第二輪被打穿前就換成不靠字面的做法。
PRIOR-ART: F1 不明標記——沿用本 repo `_choice_kill_pick` 既有規則(代碼審 r2 H1:雜湊帶不明就當成變了),不另訂。
PRIOR-ART: F3 斷路——沿用合併快篩既有的連續失敗斷路形狀(`_CHOICE_MERGE_BREAKER`)。
