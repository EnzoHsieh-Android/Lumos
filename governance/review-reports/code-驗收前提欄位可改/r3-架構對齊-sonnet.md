severity: minor

## F1 清單項改用 fmt_scalar(key, v),沒沿用現成的 fmt_list_item
severity: minor
blocking: no
引句:「else [f"{key}:"] + [f"  - {fmt_scalar(key, v)}" for v in vals])」

`_set_conditions_locked` 寫多個值時,`- ` 清單項是用 `fmt_scalar(key, v)` 格式化,但全工具原本的慣例是:純量單行用 `fmt_scalar`、`  - x` 清單項一律走 `fmt_list_item`(既有呼叫點如 `scripts/lumos:13518` 的 `fmt_list_item(sval)`)。這支 patch 本身把 `fmt_scalar` 與 `fmt_list_item` 都改成共用 `_yaml_plain_ok`/`_yaml_quote`,所以目前輸出行為剛好一樣;但 `fmt_scalar` 多帶了 `DATE_KEYS` 分支與「拿 key 當錯誤訊息主詞」的語意,`fmt_list_item` 沒有。之後如果有人把 `COND_KEYS` 併進或誤判成日期欄位、或單純照現有命名慣例去讀這段程式,會被「純量欄位用清單項寫法」這件事誤導。建議清單項那一行改回 `fmt_list_item(v)`,跟其他清單寫入點一致。

## F2 插入位置邏輯用內嵌 slice 手刻重現一次,沒有重用/抽出共用函式
severity: minor
blocking: no
引句:「else:   # 插的位置照 edit_fm_scalar:第一個清單或多行區塊欄位之前,都沒有就放最後」

現有 `edit_fm_scalar`(scripts/lumos:13442)已經是「欄位存在就用 struct 位置蓋掉、不存在就插在第一個 list/block 欄位之前、都沒有放最後」的同一套邏輯,而且是被 `_cmd_set_locked` 既有路徑呼叫的共用函式。`_set_conditions_locked` 沒有重用或延伸它(它卡在 `edit_fm_scalar` 內部會對 `kind != "scalar"` 拋錯,COND_KEYS 換掉後可能是 list/block 型態,直接呼叫會不合用),而是自己重新手刻一次「找第一個 list/block 起點插入」的邏輯,連程式裡的自評註解都寫「插的位置照 edit_fm_scalar」,等於承認是複製慣例而非共用實作。之後 `edit_fm_scalar` 的插入規則改了,這裡不會跟著動,兩處會悄悄分岔。建議把插入位置判斷抽成一支小函式讓兩邊共用,或至少留一條測試/註解釘住兩邊要同步改。

已看,無:COND_KEYS 的宣告位置、命名風格(tuple,跟既有 LINK_KEYS 同款,附 spec 出處註解)與 SCALAR_KEYS/LIST_KEYS 相鄰擺放一致;`_yaml_plain_ok`/`_yaml_quote` 抽成共用白名單後,`fmt_scalar`、`fmt_list_item`、`_fmt_decision_value` 三個呼叫點都改走它,沒有漏改任何一處手刻 YAML 引號判斷(全檔搜尋沒有殘留舊的 `replace('"', '\\"')` 或裸手刻正則);`_cmd_set_locked` 對 COND_KEYS 與一般欄位的分流、對「給多個值但不是 COND_KEYS」的擋法訊息,跟既有「擋下:...檔案沒動」的錯誤訊息風格一致;`cmd_set` 對內部呼叫者(如 `cmd_set(env, rel, "status", "pass")` 傳純字串)向後相容,沒有因為 CLI 端 argparse 改成 `nargs="+"` 而破壞既有非 CLI 呼叫路徑;測試命名 `t_set_condition_fields_*`、`t_decision_add_standard_yaml_safe` 跟鄰近 `t_set_status_syncs_tag` 等既有 `t_set_*`/`t_decision_*` 風格一致,單元測試裡的 `_conds_of`/`_cond_shape_runs` 輔助函式也是就地新增、沒有跟既有測試輔助函式撞名或重複造輪;圖譜筆記(計劃節點與 Systems/lumos-cli-write 摘要行)前綴用法、`[test:]` 綁定、PRIOR-ART/RETIRE-IF/條款/回退/誠實界線章節齊全,跟同目錄其他計劃節點寫法一致;`skills/lumos-project-notes/commands/03-寫回圖譜.md` 新增的一行查表格式跟表格既有欄位對齊。
