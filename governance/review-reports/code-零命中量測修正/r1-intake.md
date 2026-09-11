# r1 收貨紀錄(code-零命中量測修正)

- 派三席:單reviewer-sonnet、架構對齊-sonnet、外家否決-codex(gpt-5.6-sol)。分級 standard,三席都到。
- ★外家席的獨立性破了一半★:Codex 跑到一半 `sed -n '1,260p' governance/review-reports/code-零命中量測修正/r1-單reviewer-sonnet.md`(過程紀錄第 2152 行)——編排者在它還在跑的時候把先到的通才席報告存進了 repo 裡的卷證目錄。它交回的五條跟通才席三條都不重疊,照常逐條重現採信;但「多席一致」不能拿它當佐證。之後席位在跑時報告先存 repo 外(已記進記憶)。
- 外家席報告自己的編號是 B1–B5,跟架構席的 B1 撞號;帳上記成 C1–C5(C1=它的 B1,以此類推)。
- 三份報告都已正規化;quote-check 三份全數錨定 r1-snapshot.patch;refcheck 通才/架構 missing 0;外家 missing 2 是 C5 重現步驟裡當例子的路徑(預設的 local/ 目錄被 gitignore、這裡沒建過;另一個是假設的自訂位置),不是在宣稱檔案存在,C5 另用 git check-ignore 重現。

## 機械重現表(修前,對 HEAD 3fd9e764 的 recount.py 跑)

| id | 怎麼試 | 結果 |
|---|---|---|
| A1 | `for q in "$terms"; do lumos search "$q"; done; grep -n "\"candidates\": 0" scripts/test_lumos.py`,輸出=1 行零命中+1 行 grep 到的治具 | HIT(zero_unattributed=2,實際 1) |
| A2 | `printf "foo\nbar\n" \| xargs -I{} lumos search {}`,輸出零命中+有命中 | HIT(query '{}'、整段判 zero,另一次消失) |
| A3 | `lumos search "x" & lumos search "y"` | HIT(一筆、query 'x & lumos search y') |
| B1 | 讀 recount.py:SEARCH_COUNT_ANY 抄了 SEARCH_RANKED/SEARCH_LEGACY、JSON 用正規式;_search_verdict 另一套 | HIT(同一件事兩套判法) |
| C1 | `f(){ python3 scripts/lumos search "$1" --json; }; f __NO_HIT__` | HIT(query '1') |
| C2 | `python3 scripts/lumos search '$ZZZQXJ_NO_HIT_9F38B7' --json` | HIT(query ''、判不出) |
| C3 | `python3 scripts/lumos search __NO_HIT_FLAG__ --path Systems --top 2 --json` | HIT(query '__NO_HIT_FLAG__ Systems 2') |
| C4 | 外家席原指令真跑:`sed -n 5572p governance/review-reports/design-cjk-nospace-fallback/r1-codex-raw.txt; python3 scripts/lumos search "推播 miss" --json` | HIT(計數 [0, 141],判 zero;編排者先用模擬輸出沒重現,因為判法先看 JSON 行,改用原指令真跑才重現) |
| C5 | `git check-ignore -q` 預設 local/ 與自訂 governance/review-reports/recount-smoke/local/… | HIT(預設被忽略、自訂沒被忽略,write_archive 照寫) |
| O1 | 折完用真資料重跑,零命中清單出現整段 python 程式碼;追到外家席自己的實驗指令(heredoc 內 python 組搜尋指令給 subprocess) | HIT(heredoc 內容被逐行當殼層指令) |
| O2 | 同上,另一條是 `python3 -c '…cmd="…lumos search…"…'`;另試 `git commit -m "fix: lumos search 零命中…"` | HIT(共用切詞把引號內整段拆成單字,引號裡「提到」也算搜尋,提交訊息也中) |

## 修法(全部進真碼,先紅後綠)

- B1/A1:計數單源 `_search_counts`——JSON 只認整行 JSON 真的解、排序與舊模式沿用 SEARCH_RANKED / SEARCH_LEGACY 只認行首;`_search_verdict` 改從它取;拿掉 SEARCH_COUNT_ANY。grep 到的檔案內容(行首帶檔名或行號)不再算。
- A2/C1:查詢詞不確定就回 None:`$x`、`${x}`、`$1`、`$@`、`$(…)`、反引號,xargs 餵的、`{}`。
- C2:判變數前先剝掉單引號字串(單引號裡的 $ 是字面)。
- A3:單一 & 當分隔(不碰 &&、2>&1、&>、|&);拆成各一筆但不依序配對。
- C3:`--path`、`--top` 的值略過;清單跟 `lumos search -h` 對得上有測試(防漂移)。
- C4:單一搜尋但輸出有兩行以上計數 → 判不出。
- C5:`write_archive` 發現查詢字串檔的位置在 git 工作樹裡又沒被 gitignore → 不寫、stderr 講明、回 None;lens_weekly 的 LOG 跟著改。
- O1:`_shell_lines` 先用原始行拿掉 heredoc 內容再做其餘前處理。
- O2:`_safe_tokens` 加 `flat=False`(引號內整段一個詞、不剝 $)給搜尋判斷用;讀取判斷照舊。

## 翻紅驗證(對修後的碼一次只拿掉一條修正)

| 拿掉的修正 | 測試 | 結果 |
|---|---|---|
| JSON 改回不錨定行首的正規式 | t_lens_recount_search_multi_r1 ① | 翻紅 |
| 拿掉 xargs 判斷 | 同上 ② | 翻紅 |
| 拿掉單一 & 拆分 | 同上 ③ | 翻紅 |
| 變數判斷改回只認字母開頭 | t_lens_recount_search_multi_r1_codex ① | 翻紅 |
| 拿掉單引號剝除 | 同上 ② | 翻紅 |
| 拿掉旗標值略過 | 同上 ③ | 翻紅 |
| 單一搜尋改回拿第一行計數 | 同上 ④ | 翻紅 |
| 拿掉可提交位置檢查 | 同上 ⑤ | 翻紅 |
| heredoc 內容略過(修前) | t_lens_recount_search_heredoc_body | 修前紅、修後綠 |
| 拆單字的切詞(修前) | t_lens_recount_search_quoted_mentions | 修前紅、修後綠 |

修後 -k lens_recount 95、-k lens 194、-k codex_s3 19 全綠。

## 處置

- 本輪有 major,依 d2 同輪不得放行:11 條(A1–A3、B1、C1–C5、O1、O2)全折。重現不到 0。架構席標 ⚠ 的「新欄位有才寫 vs 永遠有」鄰居兩種都有、它自己不列條,不處置。

## 修後真資料重跑(本機 W33–W37)

- 搜尋 969 次、零命中 48 次(配得到 28、配不到 20)、判不出 43%;乾淨 agent 人工數約 71 次(推送前 13 次)。配得到的零命中查詢不再有整段程式碼。
