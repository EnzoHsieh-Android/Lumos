# r2 收貨紀錄(code-零命中量測修正)

- 為什麼有這輪:r1 11 條全折後,修正本身(recount.py 約 80 行、兩條編排者自找)沒有席位看過(code-loop 手冊步驟 5)。只掃修正差異 r2-delta.patch,全貌 r2-snapshot.patch。
- 派三席:單reviewer-sonnet、架構對齊-sonnet、外家否決-codex(gpt-5.6-sol)。r1 的教訓照做:席位在跑時先到的報告存 repo 外、全部交回才搬進卷證;派工詞寫明不讀別席報告。外家席過程紀錄只讀了派工單給的 r1-intake.md(背景),沒讀別席報告——三席獨立。
- 外家席報告用 1–6 編號,帳上記 X1–X6。
- 三份報告已正規化;quote-check 三份全數錨定 r2-snapshot.patch;refcheck 三份 missing 0。
- 兩組獨立撞在一起:通才 D2 = 外家 X1(引號裡的 <<EOF 被當 heredoc);通才 D3 = 架構 E1(_committable 叫 git 沒接錯誤)。

## 機械重現表(修前,對 r1 折完的碼、在 repo 外暫存副本跑新測試)

| id | 怎麼試 | 結果 |
|---|---|---|
| X1 / D2 | `printf '%s\n' '<<EOF'` 換行接真搜尋;`lumos search "heredoc <<EOF pattern test"` 換行接第二個搜尋 | HIT(後面的真搜尋整筆消失) |
| X2 | `printf` 印假 JSON(candidates 0)再跑有命中的 `lumos search README \| head -1` | HIT(判 zero,壓過看得到的命中行) |
| X3 | `…search __NO_HIT_1&python3 scripts/lumos search __NO_HIT_2` | HIT(黏成一筆) |
| X4 | `…search __NO_HIT__ --pa Systems --to 3` | HIT(查詢詞混進 Systems 3) |
| X5 | `…search \$LITERAL_X` | HIT(當成變數、查詢詞抹掉) |
| X6 | `…search __NO_HIT__ --json # verify lumos search no hit` | HIT(註解併進查詢詞) |
| D1 | `_search_segments('bash -c "lumos search x"')` | HIT(回 [],r1 改引號內不拆之後的退步) |
| D3 / E1 | 讓 subprocess.run 丟 FileNotFoundError 後呼叫 `_committable` | HIT(整支丟例外) |
| E2 | 讀 recount.py:`_HEREDOC_START_RE` 跟既有 `HEREDOC_RE` 幾乎逐字重複 | HIT(第二份 heredoc 判斷) |

新測試 t_lens_recount_search_r2(①–⑦)、t_lens_recount_search_nested_shell 在修前的碼上全紅。

## 修法

- E2/X1/D2:heredoc 起點改用既有 HEREDOC_RE(加兩個捕捉群組,classify_bash 只用 .search 判有沒有、不受影響),只認引號外的 `<<`;拿掉 _HEREDOC_START_RE。
- X6:`_drop_comment` 去掉引號外、行首或空白後的 # 起到行尾(引號裡的 # 照留)。
- X2:單一搜尋的計數是 0 但看得到命中結果行 → 判不出。
- X3:單一 & 的判斷拿掉「前面不能是數字」。
- X4:值旗標也認 argparse 接受的縮寫(--pa、--to…)。
- X5:判變數前先剝掉反斜線跳脫的 `\$`。
- D1:`bash`/`sh`/`zsh`/`dash`/`ksh` 帶 `-c`(含 -lc 等)那串字遞迴當指令解析;`echo "…"` 照舊不算。
- E1/D3:`_committable` 叫 git 包 try/except、10 秒逾時:判不出在不在工作樹 → 當不在(照寫);在工作樹裡但判不出有沒有 ignore → 當會進版控(不寫)。

## 翻紅驗證(對修後的碼一次只拿掉一條修正)

| 拿掉的修正 | 測試 | 結果 |
|---|---|---|
| heredoc 不看引號 | t_lens_recount_search_r2 ① | 翻紅 |
| 拿掉矛盾檢查 | 同上 ② | 翻紅 |
| & 前數字排除加回 | 同上 ③ | 翻紅 |
| 只認完整旗標 | 同上 ④ | 翻紅 |
| 拿掉反斜線剝除 | 同上 ⑤ | 翻紅 |
| 拿掉註解剝除 | 同上 ⑥ | 翻紅 |
| 拿掉巢狀 shell 遞迴 | t_lens_recount_search_nested_shell | 翻紅 |
| git 例外(修前) | t_lens_recount_search_r2 ⑦ | 修前紅、修後綠 |

修後在 repo 裡 -k lens_recount 104、-k lens 203、-k codex_s3 19 全綠(暫存副本裡 -k lens 有 4 條派工鏡頭逾時測試紅,副本的 lumos 本體是舊版,搬回 repo 重跑全綠,判定環境造成)。

## 處置

- 本輪有 major,依 d2 同輪不得放行:11 個 id(D1、D2、D3、E1、E2、X1–X6)全折;其中 D2/X1、D3/E1 各是同一件事、兩席各自找到,各記 id。重現不到 0。
