# r2 收貨紀錄

固定版本:審材 14cf40143..e4190cab7f5a16636349a90149025d74c7b37950,修補差異 3b76b682d..e4190cab7。修後 086c68f1d(筆記)、6365cb906(程式)。
兩席都交回。單reviewer2 有一句引句引的是掛鉤現有程式、不在 patch 裡,同條另一句有錨;該席 R1 由編排者照它的改壞重現。載體改由全數錨定的架構對齊2 擔任。

## 分組與處置

| 組 | 發現 | 歸因 | 重現 | 處置 |
|---|---|---|---|---|
| G1 | R1 | 未判定:新測試的盲點,修前沒有同形比對 | HIT:測試改成三套範圍分家前,home 改用 _brange 與遠端名不加引號都綠 | 折入:push-range 回答故意跟 home 那條不同,逐道斷言自己那一套;加帶 & 的遠端名、兩個 ref 的案例 |
| G2 | R2 | 未判定:3b76b682d 就有 | HIT:純文件推送時實際帶 -k real_claude_md,印出來沒有 | 折入:自主迴圈照實帶參數;直譯器加引號;全套維持 --ff -x(跟同段第 1 條路一致,跑到第一支紅就停) |
| G3 | R3 | 新增行為,筆記已宣稱 | HIT:_door_linked_signals 修前回訊號、修後回空 | 折入:這是有意的,補測試釘住 |
| G4 | R4 | 未判定:設計層 | HIT:scratchpad 真跑 git push,掛鉤之後還印 error: failed to push some refs | 折入:筆記與註解改成「掛鉤輸出的最後一行」,另記 PITFALL;那行是 git 印的,改不了 |
| G5 | R6 | 有證據:修補新增的字句 | HIT:來源量的是 Sonnet 4.5,現用 5.5 | 折入:兩處改成推論語氣 |
| G6 | B1 | 未判定 | HIT:三個呼叫點傳入形狀不同,行為等價 | 折入:統一傳冒號後面的字 |
| — | R5 | 修補後狀態 | HIT:anchor verify 回 1 | 放行:簽名每次都要使用者親簽,定稿後由使用者簽;推送前閘會擋,不會漏 |
| — | B2 | 未判定 | HIT:作廢判斷在兩條讀取路徑各有一處 | 放行:extract_contracts 二十幾處呼叫靠它查合約帳,是否算作廢要逐處判,筆記已記不選理由 |

--regression-set 省略:R1、R2、R4、B1 的修補因果未判定。

## 編排者自查多抓到的

printf %q 在這個環境遇到中文路徑會逐位元組跳脫,輸出變成不合法 UTF-8。測試把直譯器路徑換成帶中文與空白時 EXCEPTION 翻紅。折入 G2:改用掛鉤自己的 pp_q,只在需要時整段包單引號。

## 配對案例

| 組 | 角色 | 行為 | 案例 |
|---|---|---|---|
| G1 | repair | 三套範圍分家時每道閘各對自己那一套 | t_prepush_next_step_is_the_call_the_gate_ran ② |
| G1 | repair | 遠端名帶 & 整行貼進 shell 不走樣 | 同一支 ③ |
| G2 | repair | 中文、分號、單引號的分支名不走樣 | 同一支 ③ |
| G2 | repair | 純文件推送的重跑指令帶 -k;直譯器有空白 | t_prepush_blocked_last_line_is_next_step ②③ |
| G3 | repair | 作廢的 IRREVERSIBLE 不算風險訊號,生效的照算 | t_superseded_contract_not_sent ④ |
| G1 | preserve | 一般推送各道閘、兩道都擋、兩個 ref | t_prepush_next_step_is_the_call_the_gate_ran ① |

改壞驗證原始輸出:r2-repro.txt,十三種全部翻紅。
