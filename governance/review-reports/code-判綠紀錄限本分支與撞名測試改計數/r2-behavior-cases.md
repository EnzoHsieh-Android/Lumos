# r2 待驗案例(修前 409ab14f → 修後 d32dbe14)

案例只是待驗範圍,不是「已修好」的證據;新席自己核對、可補案例。修前與修後的改壞驗證原始結果在同目錄 r1-repro.txt。

| 組 | 角色 | 待驗行為 | 出處 | 案例 | 修前 | 修後 |
|---|---|---|---|---|---|---|
| G1 | repair | 淺複製裡真祖先被截斷、merge-base 回 rc 1 時照留並印一句 | 計劃 S8、做法 1 c | t_redbase_branch_rows_fallback_keeps「S8 淺複製:查不到的提交與回不是祖先的真祖先都照留」 | 修前沒有這個案例(r1 三席以改壞實測:rc 1 一律丟照綠) | 綠;改壞 H1 紅 |
| G1 | preserve | 完整 repo 裡不是祖先的提交照丟 | 計劃 S6 | t_spec_gate_redbase_green_other_branch「S6 同名重開」 | 綠 | 綠;改壞 G2 紅 |
| G2 | repair | 串接快取守衛被拿掉(每次重算)時測試紅 | 計劃 S3 | t_name_collision_scales ② | 修前綠(r1 兩席以改壞實測) | 綠;改壞 H5 紅 |
| G2 | preserve | 索引每名重建時測試紅 | 計劃 S3 | t_name_collision_scales ① | 改壞紅 | 改壞 H6 紅 |
| G3 | repair | 有同名 tag 時分支名照樣對得上,同一條分支的判綠照算 | 計劃 S2 | t_spec_gate_redbase_green_other_branch「S2 …另有同名 tag」 | 修前沒有案例(r1 邊界席以 git 2.39.2 實測 --short 回 heads/<名>) | 綠;改壞 H4 紅 |
| G3 | preserve | 分支名不同照丟、寫入端記分支名 | 計劃 S1 | 同支測試 S1 三條 | 綠 | 綠;改壞 G1、G9、G10 紅 |
| G4 | repair | 部分複製不為判祖先去連遠端、照留並印一句 | 計劃 S8、做法 1 d | t_redbase_branch_rows_fallback_keeps「S8 部分複製」三條(遠端抓取程式換成留記號腳本) | 修前沒有案例(r1 資源席以慢遠端實測抓取子程序殘留) | 綠;改壞 H2 紅 |
| G4 | preserve | 淺複製查不到的提交照留;完整 repo 查不到的提交照丟 | 計劃 S6、S8 | 同支測試淺複製、★對照★ 與 other_branch「S6 提交不存在」 | 綠 | 綠;改壞 G3、G4 紅 |
| G5 | repair | 截止時間在問祖先前一刻起算;超過上限先問最新的 | 計劃做法 1 e | t_redbase_branch_rows_fallback_keeps「超過上限」兩條 | 修前先問最舊(r1 通才席) | 綠;改壞 H3、G11 紅 |
| G5 | preserve | 過了截止時間照留並印幾筆 | 計劃 S8 | 同支「過了截止時間」兩條 | 綠 | 綠;改壞 G5、G13 紅 |
| G6 | repair | 測試不把回傳值塞進共用模組 | 架構對齊 | t_redbase_branch_rows_fallback_keeps 改用 redirect_stderr | — | 綠 |

未覆蓋:時鐘倒退、真實慢遠端(只用留記號的腳本代替)、`containing` 只慢不重做的退步(計劃 REVISIT 2027-05-03)。
