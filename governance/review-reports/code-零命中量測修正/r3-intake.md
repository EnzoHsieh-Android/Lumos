# r3 收貨紀錄(code-零命中量測修正)——standard 上限的最後一輪

- 為什麼有這輪:r2 11 個 id 全折後的修正(heredoc 引號判斷、註解剝除、巢狀 shell 遞迴、旗標縮寫、反斜線 $、矛盾檢查、git 錯誤處理)沒有席位看過。只掃 r3-delta.patch(r2 的修正差異),全貌 r3-snapshot.patch。
- 派三席:單reviewer-sonnet、架構對齊-sonnet、外家否決-codex(gpt-5.6-sol);報告先存 repo 外、全部交回才搬進卷證;外家席過程紀錄沒讀別席報告,三席獨立。
- 外家席報告用 1–6 編號,帳上記 Y1–Y6。通才 F1 = 外家 Y2(-c 前有選項漏算),兩席各自找到。
- 三份報告已正規化;quote-check 三份全數錨定 r3-snapshot.patch;refcheck 三份 missing 0。

## 機械重現表(修前,對 r2 折完的碼、在 repo 外暫存副本跑新測試 t_lens_recount_search_r3)

| id | 怎麼試 | 結果 |
|---|---|---|
| Y1 | `bash -c 'python3 scripts/lumos search README & python3 scripts/lumos search __R3_NO_HIT__; wait'`,輸出計數 [0, 85] | HIT(README 判 zero、另一個判 hit——內層 & 被外層引號藏住) |
| Y2 / F1 | `bash -o pipefail -c '…lumos search __OPT__'`、`bash -x -c "lumos search __NO_HIT_ABC__ --json"` | HIT(回 [],整筆消失) |
| Y3 | `printf '%s\n' bash -c 'lumos search fake'; python3 scripts/lumos search __R3_NO_HIT__` | HIT(多算一筆 fake,真的零命中降成配不到) |
| Y4 | `…search __R3_COMMENT__;# lumos search fake` | HIT(註解裡的 fake 算成搜尋) |
| Y5 | `…search \\$HOME`(偶數個反斜線,$HOME 會展開) | HIT(當成字面查詢判 zero) |
| Y6 | 讓 subprocess.run 丟例外,查詢檔位置在 .git 底下 | HIT(當不在工作樹、照寫——隱私放行) |
| G1 | 讀 recount.py:`_heredoc_start` 回 tuple 或 None 卻沒標型別,鄰居都標 | HIT |

## 修法

- Y1:`_search_segments` 改由 `_search_parse` 回 (查詢詞, 有沒有進過巢狀 shell);進過巢狀 shell 就不依序配對。
- Y2/F1:`_shell_script` 往後找 -c,中間允許 -e、-x、-l、--noprofile、-o pipefail、+o x、-O opt 這類選項。
- Y3:shell 名稱要在指令位置(跳過 X=1 這種指定與 env/time/sudo 等包裝)才算巢狀 shell;`printf … bash -c …` 不算。
- Y4:`_drop_comment` 的 # 也認 ; & | ( ) 後面緊貼的。
- Y5:判變數前只剝「前面奇數個反斜線」的 $(偶數個=反斜線本身被跳脫,$ 照樣展開)。
- Y6:`_committable` 叫 git 失敗或 rev-parse 不成功時,看位置在不在某個 .git 底下,在就當會進版控(不寫);在工作樹裡但 check-ignore 失敗照舊當會進版控。
- G1:`_heredoc_start` 標 `-> tuple[str, bool] | None`。

## 翻紅驗證(對修後的碼一次只拿掉一條修正)

| 拿掉的修正 | 測試 | 結果 |
|---|---|---|
| 巢狀 shell 照樣依序配對 | t_lens_recount_search_r3 ① | 翻紅 |
| 只認緊接的 -c | 同上 ② | 翻紅 |
| 不看指令位置 | 同上 ③ | 翻紅 |
| 只認空白後的 # | 同上 ④ | 翻紅 |
| 不數反斜線 | 同上 ⑤ | 翻紅 |
| git 失敗當不在工作樹 | 同上 ⑥ | 翻紅 |

修後在 repo 裡 -k lens_recount 110、-k lens 209、-k codex_s3 19 全綠。

## 處置

- 本輪有 major,依 d2 同輪不得放行:8 個 id(F1、G1、Y1–Y6)全折。重現不到 0。
- ★到上限★:standard 上限 3 輪,這是第三輪;這輪的修正(約 50 行)沒有第四輪可以審,照手冊到頂就停、攤給人裁,不開第四輪。三輪下來每輪都還在殼層語法邊角找到新洞(r1 11、r2 11、r3 8),這支儀器對殼層語法的解析是「盡量」不是「完整」,零命中數要當下限看(計劃 S3 已寫明)。
