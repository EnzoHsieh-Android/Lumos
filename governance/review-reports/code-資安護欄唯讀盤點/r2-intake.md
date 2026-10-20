# code-資安護欄唯讀盤點 r2 收貨與處置

## 修補鏡頭配對案例(待驗範圍,不是已修好的證據)

§3.1 第0步原應修前選例;r1 修補前沒做,以下為修後補列。preserve 的修前成功證據一律未判定(未在固定修前版本 20293afe 執行),新席可自行在 git -C 臨時副本跑。

| 組 | findings | repair(原問題) | 修補處與守護測試 | preserve 候選 | 修前證據 |
|---|---|---|---|---|---|
| G1 | 正1,邊1,邊2,整1,外1 | 壞型別讓整份盤點崩潰:驗成非法的值仍被拿去查字典、進集合;統一成先驗型別(含拒孤立代理字元)才查表 | _sc_source→t_seclist_g1_field_type_fuzz; _secinv_inv_items→t_seclist_g1_field_type_fuzz; _secinv_inventory_problems→t_seclist_g1_field_type_fuzz; _secinv_is_text→t_seclist_g1_field_type_fuzz | 正常登記(全合法欄位)照列、rc0;既有 v1 鍵規則反例仍 rc2 | 未判定 |
| G2 | 正2,邊3,邊6,安2,外4 | JSON 遇孤立代理字元編碼失敗、雙向控制原樣輸出、選圖譜失敗沒有 JSON;文字模式自由欄位無上限、沒有資料框 | cmd_security_list→t_seclist_g2_output_contract; _secinv_failed_report→t_seclist_g2_output_contract; _secinv_show→t_seclist_g2_output_contract; _secinv_rec_lines→t_seclist_g2_output_contract; _secinv_names→t_seclist_g2_output_contract; _json_text_escaped→t_seclist_g2_output_contract | 純 ASCII 正常輸出逐字不變;非錯誤路徑 --json 形狀不變 | 未判定 |
| G3 | 安1,外2,外3,通3 | 缺口被藏:空塊算已登記、引用無效的控制項仍算入口映射、inventory 驗證沒有測試 | _secinv_build→t_seclist_g3_gaps_not_hidden; _secinv_check_row→t_seclist_g3_gaps_not_hidden,t_seclist_integration_gaps; _secinv_surface→t_seclist_g3_gaps_not_hidden,t_seclist_integration_gaps; _secinv_inventory→t_seclist_g3_gaps_not_hidden | 合法控制項照常映射入口;active/candidate 區分不變 | 未判定 |
| G4 | 通1,通2,安3,邊4,安4 | 讀取守衛沒有測試或可繞:中間目錄換捷徑、深層巢狀、圖譜根是捷徑、--vault 不像圖譜 | _vault_safe_open_rel→t_seclist_g4_read_guards; _vault_safe_descend→t_seclist_g4_read_guards; _vault_safe_enumerate→t_seclist_g4_read_guards; _secinv_parse_block→t_seclist_g4_read_guards; load_vault_safe→t_seclist_g4_read_guards; _secinv_vault_problem→t_seclist_g4_read_guards | 正常目錄樹(無捷徑)照讀;自動找 docs/*-knowledge 照舊 | 未判定 |
| G5 | 架1,架2 | 第二套讀圖譜與找圖譜:改成 load_vault 同家族的第二種模式、選圖譜共用 _vault_in | load_vault_safe→t_seclist_g4_read_guards,t_seclist_s03_read_boundary; _vault_in→t_seclist_s08_incomplete_read_exit,t_seclist_g4_read_guards; _secinv_select_vault→t_seclist_s08_incomplete_read_exit,t_seclist_g4_read_guards | load_vault 其他指令行為不變(既有 load_vault 測試照綠) | 未判定 |
| G6 | 架3,正3 | 錯誤種類詞彙與既有管道沒有對照:家節點補對照表;not_utf8 確認只記一次;正3 是核對紀錄、無需修改 | 錯誤種類對照→t_seclist_s02_registration_errors | 退出碼 0/2 契約不變 | 未判定 |
| G7 | 資1,資2,資3 | 覆蓋是入口數×控制項數、來源核對每條重算合約、列舉只限 .md 數;修正後效能檢查另抓到 inventory ID 集合 | _secinv_coverage→t_seclist_g7_scale; _secinv_claim_counts→t_seclist_g7_scale; _secinv_check_links→t_seclist_g7_scale; _vault_safe_list_dir→t_seclist_g7_scale | 小規模輸出與大規模輸出結果相同(只變快) | 未判定 |
| G8 | 通4,通5,通6 | 測試判準與命名:鍵規則缺反例、S10 斷言名不符、整合反例沒真的建模 | t_seclist_g8_key_rules→t_seclist_g8_key_rules; t_seclist_g8_read_request_bound→t_seclist_g8_read_request_bound,t_seclist_s10_size_caps; t_seclist_integration_gaps→t_seclist_integration_gaps | 既有 S1–S13 綁定測試照綠 | 未判定 |
| G9 | 整2,整3,整4 | 文件:母計劃正文照 d8、d9 改成現況並寫明閘門未上線;子計劃標明凍結後新增項;驗收紀錄補型別畸形的未驗與已驗 | 接手先讀→t_seclist_integration_gaps; 凍結版本→t_seclist_s01_concern_sections; 欄位值型別畸形→t_seclist_g1_field_type_fuzz | 母計劃 d8/d9 決策內容不變,只改正文現況句 | 未判定 |

## r2 收貨

同門七席(正確性、邊界、資源、整合、通才、架構對齊、資安)加外家 Codex 一席全部交回後一次存檔。共用派工詞檔(code-seat-common.md)派工時已遺失,七席第一次交回的格式不合(嚴重度寫 low/nit、等級放圍欄、檔首無檔級行);編排者補回共用詞後請正確性、資源、整合、通才四席只重排格式、內容不改,邊界與架構對齊由 report-normalize 補檔級行。資安席派工詞原指 r1 材料,派後一刻更正為 r2-snapshot.patch;Codex 席同樣指錯,停掉改正後重派(第一次輸出未採用)。八份引句全數錨定。共 30 條(正1–3、邊1–3、資1–3、整1–4、通1–8、架1–3、安1–3、外1–3)。

多席獨立一致:stderr 原樣印路徑(安1、邊1);文字缺 invalid_reference_control_ids(正1、通6、外3);inventory 重複檢查二次方(資2、正2);docs 捷徑讀到 repo 外(安2、外1);50000 項邊界無測試(通8、邊3)。

## r2 根因分組與處置

| id | 組 | 處置 | 一句 |
|---|---|---|---|
| 安1 | R1 | folded | 三處 stderr 錯誤訊息經同一顯示函式跳脫 |
| 邊1 | R1 | folded | 同安1 |
| 架2 | R1 | folded | 顯示函式帶 hidden=True |
| 正1 | R1 | folded | 文字覆蓋缺口補 invalid_reference_control_ids,加文字與 JSON 對照測試 |
| 通6 | R1 | folded | 同正1 |
| 外3 | R1 | folded | 同正1 |
| 通5 | R1 | folded | id、inventory、claim 等欄位一起套長度上限 |
| 安2 | R2 | folded | 從起點到圖譜逐段不跟捷徑,自動找與 --vault 共用 |
| 外1 | R2 | folded | 同安2 |
| 外2 | R3 | folded | evidence_refs 指到非 Verification 算引用錯誤 |
| 安3 | R3 | accepted | 只掛 not_applicable/defect 的入口已另列在 applicability_pending 與 defect 清單,屬子計劃 d1 的呈現,不改 mapped 語意 |
| 資1 | R4 | folded | 錯誤清單每節點最多 50 筆,超出併一筆 |
| 資2 | R4 | folded | 重複檢查改 set |
| 正2 | R4 | folded | 同資2 |
| 資3 | R4 | folded | 決策解析與路徑索引每次盤點快取一次 |
| 通1 | R5 | folded | _sl_vault 改名並加「不得有重複頂層 def」守衛測試 |
| 通2 | R5 | folded | 補 not_utf8 測試 |
| 通3 | R5 | folded | READ_KINDS 每成員都有 read_complete=false 斷言 |
| 通4 | R5 | folded | 補 unknown_evidence_status 測試 |
| 通7 | R5 | folded | 整合⑤ 補 declared_only 與限制句斷言 |
| 通8 | R5 | folded | 50000/50001 兩側測試 |
| 邊3 | R5 | folded | 同通8 |
| 架1 | R6 | folded | 有界讀共用既有函式;在既有「dirfd 邊際價值低」決定旁與子計劃寫明本處例外理由(換形狀,不再只改名) |
| 架3 | R6 | folded | 改用 env_text |
| 整1 | R7 | folded | 子計劃補 50000 與新上限 |
| 整2 | R7 | folded | 照實寫輸出契約新增項與位置 |
| 整3 | R7 | folded | Verification 舊段落標取代並更新數字 |
| 整4 | R7 | folded | 母計劃過期句與 updated |
| 正3 | R7 | folded | 重列舉去重改以節點為鍵 |
| 邊2 | R7 | accepted | tags 行內清單寫法認不到是全工具 frontmatter 讀法的既有限制,不只本指令;另案處理 |
