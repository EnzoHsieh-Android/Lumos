severity: blocker

## F1 逃逸帳一行「怪值」(超深巢狀 JSON)能讓 `escape-stats` 整個爆炸,不是設計說的「只跳過壞行」
severity: blocker
blocking: yes
引句:「只跳過壞行與非物件行」
file: `scripts/lumos:7508-7527`(`_escape_raw_rows`,唯一一支 raw 讀帳的函式,docstring 自己講「含撤回紀錄、只跳過壞行與非物件行」)、`scripts/lumos:7519-7522`(`try: d = json.loads(ln) except ValueError: continue`)、`scripts/lumos:9900-9902`(`_escape_stats` 呼叫它)、`scripts/lumos:9973-9975`(`cmd_loop_escape_stats`)

`_escape_raw_rows` 對每一行只用 `except ValueError` 接住壞行,理由是「壞行、非物件行跳過」。但 Python 的 json 解碼器(C 加速版)在輸入是超深巢狀陣列時,不是拋 `json.JSONDecodeError`(`ValueError` 的子類),而是拋 `RecursionError`——它繼承的是 `RuntimeError`,不是 `ValueError`。這種行完全符合「壞行/怪值」的定義(語法上合法的 JSON,只是深度離譜),但因為例外型別不對,`except ValueError` 接不住,整支函式連帶把呼叫它的 `_escape_stats`、`cmd_loop_escape_stats` 一起炸掉。

`loop escape-stats` 這支指令的文件明講「唯讀」,是巡帳、算逃逸率用的日常指令(治理帳週報、`lumos gov --stats` 都會呼叫到同一支 `_escape_rows_for` / `_escape_raw_rows`);設計初衷是「一行壞就跳過那一行,其他照算」,這裡整支指令連 rc 都不是乾淨的 2(擋下),而是 rc=1 外加一大串 Python traceback 直接印到終端機——巡帳的人看到的不是「逃逸率依類別」,是一坨 stack trace,自動化管線(cron、CI)接這支指令的話會直接判成執行失敗。

重現(在 exp3-邊界/ 下用複製的 repo,不動正式 repo):
```
PARENT=<任一 vault 的上一層>
python3 -c "n=200000; print('['*n + ']'*n)" > "$PARENT/.escape-log.jsonl"
: > "$PARENT/.canary-log.jsonl"
: > "$PARENT/.governance-log.jsonl"
python3 scripts/lumos --vault "$PARENT/vault" loop escape-stats
```
實跑結果:
```
RecursionError: Stack overflow (used 16352 kB) while decoding a JSON array from a unicode string
```
rc=1,不是「擋下:…」的白話訊息,是原始 Python traceback。

附帶一提:`loop escape --list` 走的是 `cmd_loop_escape`,它在 `main()` dispatch 那層外面另外包了 `except (ValueError, RuntimeError) as e: print(f"擋下:{e}")`(scripts/lumos:9784`_escape_stats`外的呼叫路徑;實際包裹點在 `main()` 的 `if args.lcmd == "escape":` 分支)——`RecursionError` 是 `RuntimeError` 的子類,所以 `--list` 這條路徑「意外」被接住、印成「擋下:Stack overflow (used 16352 kB) while decoding a JSON array from a unicode string」、rc=2,沒有真的崩潰,但訊息是沒清洗過的 Python 內部字串,不是專案自己的白話格式。這條算 minor(訊息不合規格,但沒有崩潰、沒有寫錯帳),不是 blocker,寫在這裡是因為跟 F1 是同一個根因(`except ValueError` 沒蓋到 `RecursionError`),修的時候應該一起處理:`_escape_raw_rows` 的 per-line try/except 應該也接 `RecursionError`(或直接接 `Exception`,反正只是跳過這一行、不改變其他語意)。

已看,無:
- `escape --withdraw` 混用 `--repo`(r3 新加進 `others` 的欄位)給空字串或非空值都會被擋,跟其餘 `others` 欄位同一條路徑,行為一致。
- `--withdraw` 撞號(同一個 token 在帳上出現兩次以上,不論是兩筆逃逸還是逃逸配撤回紀錄)一律先擋在「帳本損毀或撞號」那條、不會撤到錯的一列。
- 一般惡意/損毀的壞行(截斷的多位元組 UTF-8、非物件 JSON、控制字元、超長字串)`_escape_raw_rows`、`--list`、`escape-stats` 三條路徑都如設計所說只跳過那一行,不影響其他列;UTF-8 解碼錯誤(`log.read_text(encoding="utf-8")` 在 `--list` 少了 `errors="replace"`)這個型別不一致點,因為 `UnicodeDecodeError` 也是 `ValueError` 的子類,意外被外層 `except (ValueError, RuntimeError)` 接住,沒有變成真的崩潰,只是訊息一樣沒清洗(同 F1 附帶的根因,不獨立算一條)。
- `--withdraw` 空 token、純空白 token、NFD/控制字元 token、`--repo`/`--sha` 等欄位空字串混用,行為與 r2 報告記錄的一致,沒有退化。

共 1 條。
