# r1 收貨與處置(code-筆記格子第1步,high:5 席+架構對齊+資安)

七席收齊才動碼;報告從逐字稿原樣抽出,架構席的 severity 寫在列表項裡,用 `report-normalize --write` 做純格式搬移。七份引句全錨定。

## 重現

| id | 做法 | 結果 |
|---|---|---|
| C1/G1 | 上線前寫 `WHY:舊的一句話`、加格子記號、再補 `[出處:…]`,跑 `--diff base..tip` | HIT:修前 rc1;`_notelines_range_added` 另收沒帶記號的提交寫的行(pre2)進舊行,測試 t_slots_push_old_lines ① 翻紅驗過 |
| C2/B1 | 舊版有 `DEP:[[甲]]`,新增 `DEP:[[全新乙]]` | HIT:只放連結的鍵帶連結集合,舊連結是新連結子集才算舊行;④翻紅驗過 |
| C3/G2 | 舊句斷成兩行;有續行的舊條目搬到別篇 | HIT:比對鍵去掉所有空白;刪掉的行接回續行;另加「第一個實體行對上也算」;②③翻紅驗過(②要兩道一起拿) |
| K1/K2/K3 | 讀程式:推送時起點版本逐篇 git show、沒篩摘要;讀失敗當「沒有舊版」 | HIT:只讀摘要有新寫行的篇、`_nodehome_cat_blobs` 一次批次讀;批次讀失敗回 None 走 fail-open;單次跳過的成本隨之縮小 |
| A1/G3 | 讀 `_ns_skip_slot_extra` 寫死第一個圖譜 | HIT:抽 `_ns_vault_rel` 跟主流程共用 |
| A2/B2/U6 | `_ns_slot_extra` 對三選一回 {} | HIT:slot_check 多一支 slot_check_keyed 帶格名,帳照它數;ledger 測試三選一入帳翻紅驗過 |
| A3/U5 | 只因格子擋時印筆記形狀擋的收尾句 | HIT:那句只在形狀違規時印;格子段自己的收尾句加推送時的說明(U8) |
| A4 | 讀治理帳 extra | HIT:加 `check: slots` |
| S1 | 讀 `_ns_slots_format` 與 doctor 那行的路徑 | HIT:路徑也過 `_esc_clean` |
| U3 | 掛鉤寫 `--staged --repo x --slots` 跑 doctor --ci | HIT:doctor 偵測「帶了 --slots 但沒緊接 --staged」並講推送認不出上線點;t_slots_switch ⑦ |
| U4 | `doctor --ci` 每次唸「沒帶 --slots」 | HIT:這句只在完整 doctor 講;⑥ 驗 --ci 不唸 |
| U1/U2/U7 | 推送路徑舊行、改名、doctor 事後掃描、20 條上限沒測試 | HIT:補 t_slots_push_old_lines ①⑤⑥、t_slots_doctor_bypass_scan,各自翻紅驗過 |
| B3 | 合併中單次跳過也算格子 | HIT:跳過前遇 MERGE_HEAD 不算(沒另補測試,邏輯同主流程的合併跳過) |

## 處置

- 折入:C1 C2 C3 K1 K2 K3 B1 B2 B3 G1 G2 G3 U1 U2 U3 U4 U5 U6 U7 U8 A1 A2 A3 A4 S1。
- B1 的延伸(整行複製一條已存在的缺格舊句也算舊行):寫進計劃天花板 7——複製的是既有舊帳,沒有新寫法進來。
- 放行:S2(minor)——被推送的版本自己能把 note_shape.slots 設 off 或拿掉掛鉤記號,這是計劃天花板 4 已承認的既有設計(閘的開關讀被推送版本,只防疏忽),格子是內容品質閘不是權限邊界。
