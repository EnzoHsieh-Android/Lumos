# r1 收貨紀錄(code-推播漏網量測)

- 派三席:單reviewer-sonnet、架構對齊-sonnet、外家否決-codex(gpt-5.6-sol)。分級 standard(`lumos pitfalls --diff` 算出;不要求資安席),三席都到。
- 三份報告都已是正規化格式;quote-check 三份全數錨定凍結快照;refcheck 三份 missing 0 / out_of_range 0;seat-check 派工單沒列材料(vacuous)。
- 席位報 16 條(單reviewer 3、架構 5、外家 8),major 8 條(A1、B1、B2、C1–C5)。外家 C3 與架構 B2 的副作用是同一件事(Codex 版本閘被繞過),C8 與 A3 同一個函式的兩種寫法,各自記 id、一起修。
- 編排者重現 C2 時自己多找到一條(O1):hook 在冷卻窗內還會推一份「只看事故」的快速版(impact-hook 冷卻中走 --incidents-only、不重設冷卻記號),原程式遇到那次有真推播就不沿用開窗那次,把 agent 已經看過的筆記算成漏網。

## 機械重現表(修前,對 HEAD 959403f2 的 recount.py 唯讀跑)

| id | 怎麼試 | 結果 |
|---|---|---|
| A1 | 一則訊息裡先 Edit src/a.py 再 Read Systems/x.md,relate 回有關 | HIT(misses=[],讀取消失) |
| A2 | 測試檔找真 Existence 的案例 | HIT(只有 lambda 替身,改名與「之後才提交」兩條驗收沒有真 git 測試) |
| A3 | about_code: [src/a.py, src/b.py] 餵 _about_map | HIT(讀不到) |
| B1 | 讀 recount.py | HIT(自訂 _CHAIN_RE 與借來的 _segment_command 並存) |
| B2 | cli_version 999.0 的 Codex 稿餵 run_misses | HIT(照樣建列 rows=1) |
| B3 | 讀 recount.py | HIT(兩個 class,同檔其餘純函式) |
| B4 | 讀 _atomic_json 與 refresh_labels._atomic_write_json | HIT(暫存檔命名不同) |
| B5 | 讀 run_lens_weekly | HIT(註解寫完全照 run_replay,少原始 JSON 那行;不發 LINE 是刻意,補註解講明) |
| C1 | 推 p.md、之後讀 p.md,看列的欄位 | HIT(只有 pushed_n,沒有推了哪些、讀了哪些) |
| C2 | 01:00 改 a.py 推 A;01:05 同一 patch 改 a.py 與 new.py、無推播 | HIT(new.py zero_push=False、cooldown_inherited=True) |
| C3 | 同 B2(外家獨立指出) | HIT(stderr 沒有「不在認得的表」) |
| C4 | Codex 稿尾端補一行寫到一半的 JSON | HIT(rows=0、broken_files=1,整份丟掉) |
| C5 | budget=0,5 支檔 impact、5 篇筆記 existence,git 包一層計數 | HIT(impact 停了,git 照叫 5 次) |
| C6 | `lumos search "zero"` 換行 `lumos search "hit"` | HIT(段數 1,兩個查詢黏成一段) |
| C7 | 前一行有時間、Edit 那行缺時間 | HIT(ts=None,不沿用) |
| C8 | about_code: scripts/lumos 餵 _about_map;掃真圖譜 | HIT(讀不到;真圖譜 2 篇這樣寫) |
| O1 | 01:00 改 a.py 推 A;01:05 窗內再改、hook 推事故快速版 I;之後讀 A | HIT(A 被算成漏網) |

重現腳本與輸出在編排者本機暫存(不放卷證目錄:卷證目錄不准放腳本)。

## 修法(全部進真碼,先紅後綠)

- A1:事件先後改成(行序, 同一則訊息裡第幾個工具呼叫);Codex 用(行序, 在呼叫程式碼裡的位置)。
- A2:新測試用真 git(改名、之後才提交、還沒提交三種)驗 existed。
- A3/C8:about_code 改借 lumos 本體的 parse_frontmatter + as_list(跟 impact 讀到的同一份,清單與單值都認),單行 [a, b] 多拆一步;路徑正規化同本體 _posix_norm。
- B1/C6:_search_segments 改用借來的 _segment_command 與 _safe_tokens,先逐行再切段;引號內的 ; & | 換行先換佔位字元。拿掉 _CHAIN_RE 與 _strip_quoted_keep。
- B2/C3/C4:抽出 _read_jsonl(壞行只跳那行)、_claude_in_repo、_codex_meta(含版本白名單、同一句 stderr),scan_file / scan_codex_file / run_misses 共用。
- B3:Relater / Existence 改成閉包 _make_relater / _make_existence。
- B4:暫存檔命名改成 refresh_labels 的 pid 尾碼;保留讀回自驗,註解寫為什麼多這一步。
- B5:補「推播漏網週跑原始:」那行 log;註解改寫,講明不發 LINE 的理由。
- C1:列上加 pushed(看得到的推播節點)與 used(推了、之後讀了)。
- C2/O1:冷卻窗逐檔記;窗內看得到的=開窗那次 ∪ 窗內快速路推的;快速路推播不延長窗。
- C5:一把總預算管掃描、impact、git;掃描用完不再開新檔(files_unscanned),分類用完不再叫子行程;git 沒問的筆記一律當存在(不讓漏網整批掉進事後才有)。計劃 S4 條款正文同步改寫。
- C7:_effective_ts 沿用前一行時間;摘要多 edits_without_time。

## 翻紅驗證(對修後的碼一次只拿掉一條修正,跑對應測試)

| 拿掉的修正 | 測試 | 結果 |
|---|---|---|
| A1 事件先後只比行號 | t_lens_recount_code_review_r1 ① | 翻紅 |
| A2 git log 拿掉 --follow | 同上 ② | 翻紅 |
| A3/C8 about_code 只認清單 | 同上 ③ | 翻紅 |
| C3 拿掉版本擋 | 同上 ④ | 翻紅 |
| C4 壞行整份丟 | 同上 ⑤ | 翻紅 |
| C1 不記 used | t_lens_recount_code_review_r1_rows ① | 翻紅 |
| C2 冷卻窗整次編輯共用 | 同上 ② | 翻紅 |
| O1 窗內有推播就不併 | 同上 ③ | 翻紅 |
| C5 git 不看預算 | 同上 ④ | 翻紅 |
| C5 掃描不看預算 | t_lens_recount_weekly_archive ⑦ | 翻紅 |
| C6 不先逐行切 | t_lens_recount_code_review_r1_rows ⑤ | 翻紅 |
| C7 缺時間不沿用 | 同上 ⑥ | 翻紅 |
| B5 拿掉原始 JSON 記錄 | 同上 ⑦ | 翻紅 |

B1/B3/B4 是寫法對齊,行為由既有測試守(-k lens 171 項、-k codex_s3 19 項全綠)。

## 處置

- 本輪有 major,依 d2 同輪不得放行:17 條(16 條席位 + O1)全折。重現不到 0。

## 修後真資料重跑(本機 W36)

- 掃 2521 份逐字稿、45 秒、沒碰預算;編輯 100 列(零推播 35、冷卻窗沿用 46)、漏網 2(規則內 1、判不出 1)、事後才有 2。
- 新看得到的:壞行 2 行(修前是整份丟)、Codex 版本不認得跳過 13 份(修前照讀、會猜格式)。
- 推了之後有讀 0 次:用另一支不走 build_miss_rows 的腳本直接數,W36 有推播的逐字稿只有 1 份、裡面 Read 圖譜 0 次,兩邊一致。
