severity: minor

# 通才-sonnet 第 2 輪:測試是否真守住第 1 輪修法

做法:在自己的 `git clone --shared` 上,把每處修法單獨改回去(每次先清 __pycache__、跑完還原),跑對應 `-k` 子集;再做一份「消費專案」副本(刪 skills/、governance/eval/、CLAUDE.md、AGENTS.md)跑全部新測試。沒跑全套。

## 還原實驗表(改了什麼 → 結果)
| 修法 | 改回去的方式 | 結果 |
|---|---|---|
| s1 safe_dir 迴圈內符號連結檢查 | 拿掉 | 紅(3+3 條;但是靠第二層「解析後不在 repo 外」接住,只有訊息字樣「符號連結」對不上才紅,行為仍被擋) |
| s1 safe_dir 尾端 is_symlink/inside 檢查 | 拿掉 | 沒紅(第一層已擋,兩層冗餘,非缺口) |
| s1 清檔跳過符號連結檔 | 拿掉 | 沒紅(unlink 符號連結只刪連結本身,無實害,非缺口) |
| s3 `_note_audit_write_verdict` 不過 safe_dir | 改回直接 mkdir | 紅(3 條:reread 與筆記內容審兩邊都紅) |
| s2 cands 不剔除 ctrl | 改回 | 紅(2 條) |
| s2 `_note_reread_show` 不過濾 | 改回 | 紅(2 條,ESC/BEL 流出) |
| s2 項目檔頭重複欄位照收 | 拿掉判斷 | 紅(③) |
| s2 check 不印控制字元那句 | 拿掉 | 紅 |
| b1 寫帳 nodes 不過濾 / 摘要不過濾 | 各改回 | 各紅(非 UTF-8 測試 1 條) |
| s4 簿記判法拿掉 --no-renames | 改回 | 紅(①) |
| s4 拿掉 -z | 改回 | 紅(3 條) |
| s4 拿掉副檔名檢查 | 改回 | 紅(③) |
| k1 `_nodehome_side` 不看 deadline | 拿掉 | 紅(②③) |
| k1 scan 不把 deadline 傳給頂端那次 | 改回 | 紅(③) |
| k1 scan 不把 deadline 傳給起點那次 | 改回 | ★沒紅★(見 F2) |
| c1 prepare 不略過已對照 / --all 失效 | 各改回 | 各紅(⑨) |
| S1 頂端存在篩選 | 拿掉 | 紅(⑧,t2 新測試有效) |
| S7 none 改 skipped(刪除分支處、頂端已在主線處各一次) | 各改回 | 各紅(⑬ 單獨守「頂端已在主線」,t1 新測試有效) |
| g1 CLAUDE.md 戳記降回 v1.1 | 改回 | 紅 |
| a1 record 丟掉前綴參數 | 改回 | 紅(7 條) |
| skill 文件 codex 派法 | 改回舊形 | 紅(④) |
| reread-prepare 腳本印的 codex 派法 | 改回舊形 | ★沒紅★(見 F1) |

## 消費專案(沒有 skills/、governance/eval/、CLAUDE.md、AGENTS.md)
`-k note_audit` 281 過 0 敗 1 略過;`-k note_audit_reread` 106 過 0 敗 1 略過(skill_section 走 `_need_src` 記略過);`discipline_block_stamp` 整條略過(走 `_need_src`);其餘新測試只用 scripts/lumos 與臨時 repo,全綠。新測試不會讓消費專案全套紅(我只跑子集,未跑全套)。

## F1 腳本印出的 Codex 派法沒有測試守住
severity: minor
blocking: 否
引句:「Codex 編排:codex exec -m {model} --sandbox read-only -o <報告檔> - < <項目檔>(從 repo 目錄裡跑)」
佐證行:scripts/lumos: `scripts/lumos:27167-27175`(reread-prepare 印派工指令處;行號為 repo 根 HEAD 約略位置)
1. 資安席 F1 順手修的是兩處:skill 文件與 reread-prepare 印出的指令。測試 `t_note_audit_reread_skill_section` ④ 只讀 skill 文件。
2. 重現:把腳本那句改回 `-o <報告檔> \"<項目檔內容>\" < /dev/null`,`-k note_audit_reread` 110 條全綠,沒有任何一條紅。使用者實際照貼的是腳本輸出,這一處可悄悄退回有 `$(…)` 被 shell 執行的舊形。
3. 建議:在 prepare 測試加一條對 stdout 的斷言(含 ` - < ` 且不含 `內容>"`)。

## F2 起點那一側的截止時間沒有測試守住
severity: minor
blocking: 否
引句:「bside = _nodehome_side(root, base, vault_rel, share=tside, changed=set(changed), deadline=deadline)」
佐證行:scripts/lumos: `scripts/lumos:26776-26779`
1. `t_nodehome_side_deadline_reread` ③ 的慢速讀取只讓 `/Systems/` 的讀取變慢,起點那邊只讀「有變動的」筆記(該測試只動 A 一篇),在 0.5 秒上限內根本碰不到。
2. 重現:把 `, deadline=deadline)` 從起點那行拿掉,`-k nodehome_side_deadline` 3 過 0 敗。修法字面說「兩邊都傳」,起點一側沒有測試。
3. 建議:測試讓範圍內改到多篇(例如十幾篇 about 不同檔的家都在範圍內被改),使起點一側的讀取量足以超時。

最高等級:minor
