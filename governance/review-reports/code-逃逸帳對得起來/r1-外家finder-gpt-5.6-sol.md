severity: major

## F1 統計忽略已落帳的 loop_kind，歷史逃逸會被事後改類
severity: major
blocking: yes
引句:「if _escape_loop_kind(lid, review_ids) == "plan":」
file: `scripts/lumos:9931` `_escape_row_bucket` 完全不讀 `r["loop_kind"]`，而是依目前審查帳重新推導。
file: `docs/lumos-toolchain-knowledge/Projects/逃逸帳對得起來_計劃.md:41` 要求新列保存 `loop_kind`；下一行只要求「舊列」在讀取時推導。

因此原本以 `loop_kind=plan` 入帳的逃逸，只要同名計劃日後加入審查紀錄並收斂，就會被搬進 design 類的漏網分子；而且 `_escape_shared_evidence` 也會讓它參與歸因不明判定。歷史統計不再對應事件發生時的迴圈種類。

實跑重現：
```sh
PYTHONDONTWRITEBYTECODE=1 python3 -c 'import runpy; m=runpy.run_path("scripts/lumos",run_name="lumos_review"); g=m["_escape_stats"].__globals__; row={"loop":"甲","loop_kind":"plan","sha":"s","stage":"CI"}; g["_escape_rows_for"]=lambda env:[row]; g["_review_loop_ids"]=lambda env:{"甲"}; g["_escape_review_rows_by_loop"]=lambda env:{"甲":[{"tier":"standard"}]}; g["_escape_released_loops"]=lambda env,ids:{"甲"}; g["_escape_plan_scopes"]=lambda env,lid:["測試類"]; g["_escape_raw_rows"]=lambda env:[]; print(m["_escape_stats"](object()))'
```

實際輸出把該列算成 `kind: design`、`leaked: 1`、`plan: 0`。應先使用合法的已存 `loop_kind`，只有舊列缺欄位時才呼叫推導函式。

## F2 撤回要求 token，但所有公開輸出都不顯示 token
severity: major
blocking: yes
引句:「le.add_argument("--withdraw", dest="esc_withdraw", metavar="token", help="撤回一筆逃逸(追加撤回紀錄,不改舊列);要一起給 --reason 與 --by")」
file: `scripts/lumos:9726` `--list` 每列只印日期、嚴重度、站名、描述、`defect_ref`、規則與撤回標記，不印 `token`。
file: `scripts/lumos:9799` 新增成功訊息同樣不印剛鑄造的 token，只叫使用者執行 `--list`。

這使文件宣告的「看全帳→拿 token 撤回」無法透過 CLI 完成；使用者只能手動打開內部 JSONL 猜取操作鍵。新建列甚至連當下成功輸出也拿不到 token。

實跑重現：
```sh
set -o pipefail
python3 scripts/lumos loop escape --list | rg -n 'ESC-[0-9a-f]+'
```

實際退出碼為 1；現有 27 筆帳沒有任何一筆在 `--list` 顯示 token。應在成功訊息及每筆清單列印經消毒的 token；清單最好同時顯示新規定的 `sha` 佐證。

## F3 --withdraw 的混用檢查漏掉 --repo
severity: minor
blocking: no
引句:「others=(loop_id, stage, severity, desc, defect_ref, rule, git_range, sha, missing_ref),」
file: `scripts/lumos:9651` 傳給混用守衛的參數清單漏了 `repo`。
file: `docs/lumos-toolchain-knowledge/Projects/逃逸帳對得起來_計劃.md:107` [S19] 要求 `--withdraw` 與記帳參數混用時擋下。

`--repo` 是 `--auto` 的記帳參數，但目前與 `--withdraw` 同給時會被靜默忽略。若目前帳本剛好有相同 token，使用者即使以為 `--repo` 指向另一個 repo，仍會撤回目前帳本的列。

唯讀實跑以無操作鎖及不存在 token 呼叫：
```sh
PYTHONDONTWRITEBYTECODE=1 python3 -c 'import runpy,contextlib,types,pathlib; m=runpy.run_path("scripts/lumos",run_name="lumos_review"); g=m["cmd_loop_escape"].__globals__; g["_vault_write_lock"]=lambda _v: contextlib.nullcontext(); env=types.SimpleNamespace(vault=pathlib.Path("docs/lumos-toolchain-knowledge")); print(m["cmd_loop_escape"](env,withdraw="ESC-does-not-exist",reason="理由已經足夠",by="reviewer",repo="/另一個repo"))'
```

實際進入 token 查找並回報「沒有 token」，而不是在混用守衛擋下，證明 `--repo` 已被忽略。

測試狀態：`-k escape`、`-k rule_gap`、`-k plan_for_loop` 均已逐一啟動，但唯讀沙箱沒有可用暫存目錄，三者都在 `tempfile.gettempdir()` 以 `FileNotFoundError` 結束，尚未進入測例，不能宣稱通過。上列失敗場景均已用不落盤方式實跑。

已看,無: 撤回重複偵測、符號連結守衛、非物件 JSON 過濾、撤回後自動去重、Wilson 區間、NFC 計劃查找及 rule-gap 撤回過濾未再發現可具體重現的問題。
