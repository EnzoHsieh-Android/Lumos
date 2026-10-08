# r3 收貨與處置(code-筆記格子第1步,末輪,修正差異,high 七席)

七席收齊才動碼。架構席報告開頭缺檔級行,`report-normalize --write` 補(純格式)。通才 R3U2 與架構 R3A4 的引句指的是這輪沒改到的行(不在修正差異的快照裡),下表機械重現。併發資源 clean;正確性 R3C4、R3C5 是它自己標 clean 的查證段,不算發現。

## 重現

| id | 做法 | 結果 |
|---|---|---|
| R3U2 | `git show HEAD:scripts/test_lumos.py` 搜引句 | HIT(1 筆):說明已過期,改寫翻紅釘 |
| R3A4 | `git show HEAD:scripts/lumos` 搜引句 | HIT(1 筆):依 ci 分流的理由已在計劃〈擋〉(r2 折入)與程式註解,維持 |
| R3C1 | HEAD `DEP:[[甲]]`,暫存後接續行 | HIT:修前 rc0;舊行比對改成「文字相同+舊連結全在新行裡」,只放連結的行不再另一條路;t_slots_old_line_edges ① |
| R3A1/R3A2 | 讀 `_NS_SLOT_LINK_RE`、`_NS_PTR_SEP_RE` | HIT:兩個都刪;連結用既有 WIKILINK_RE;分隔字抽成 _NS_PTR_PUNCT/_NS_PTR_WORDS 單一來源,_NS_POINTER_ONLY_RE 由它組成(行為逐例比對不變) |
| R3C2/R3B1/R3B2 | 別名裡塞字、連結間夾 and、文字行換連結 | HIT:同上一條規則收掉;②③④ |
| R3B3/R3G3 | `café au` 對 `caféau` | HIT:空白規則收窄到中日韓字區段;⑤;計劃用詞同步 |
| R3B4 | tab 縮排續行 | HIT:`_ns_indent` 展開 tab,兩處判續行共用;⑥ |
| R3B5 | 長 SEE 範本 | HIT:`_ns_tpl_core` 截在連結邊界;⑧ |
| R3U1/R3G1 | 推送:上線前單行舊句後接續行 | HIT:修前 rc0;`_ns_entry_head` 續行有新寫就不拿第一行比實體行來源;⑦ |
| R3U3 | 讀擋下訊息 | HIT:訊息講明改續行、換或刪連結整條算新寫 |
| R3A3 | check 兩處設定 | HIT:`_ns_slot_extra(mixed=)` 一處設定 |
| R3A5/R3S-1 | 舊違規的片段與 errs 原樣印 | HIT:片段、errs 也過 `_esc_clean`;t_slots_report_ledger_and_hygiene ② |
| R3G2 | shape+slots、清控制字元、別名反例沒測試 | HIT:補 t_slots_report_ledger_and_hygiene ①②與 ②(別名塞字) |
| R3C3 | 舊缺格條目改續行一字被擋 | HIT(設計):跟單行改字同標準,寫進計劃天花板 7 |

## 處置

全部折入:R3C1 R3C2 R3C3 R3B1 R3B2 R3B3 R3B4 R3B5 R3G1 R3G2 R3G3 R3U1 R3U2 R3U3 R3A1 R3A2 R3A3 R3A4 R3A5 R3S-1。無放行。
末輪之後的這批修正不再派席(high 上限三輪):每條都補了測試並逐項翻紅驗過(tab 那條改成直接驗縮排函式才翻得紅),新增告警比對只剩既有的 cmd_note_shape 簽名那條(推送時放行並留理由)。
