severity: major

## 發現 1:新加的 `rel-cascade visited` 動詞讓既有的機械枚舉測試翻紅(已實跑查證)

`main()` 把 `rel-cascade` 的 `verb` choices 從 `["confirm", "prune", "list", "resume"]` 擴成加了 `"visited"`,但沒有同步更新專案自己既有的 [S6] 交付閘測試 `t_slim_gate`——那支測試裡有一段「S6-3」機械枚舉檢查,逐字比對 `rel-cascade --help` 的 choices 字串必須恰好等於 `{confirm,prune,list,resume}`(見 `scripts/test_lumos.py:25512-25514`)。這個測試存在的目的正是「新子指令的 choices 要跟這套機械枚舉判準同步」,而這份 diff 是第一個踩上它的新 verb,卻沒有把它也列進去。

查證所得(非猜測):把這份 patch 套到它的 base commit(804e5695)上實際跑 `python3 scripts/test_lumos.py -k t_slim_gate`,結果:
```
✗ S6-3: rel-cascade verb 有 choices(→機械枚舉)  usage: lumos rel-cascade [-h] [--cascade-id RC_CID] [--from RC_FROM]
                       [--edge {verified_by,plan_refs}] [--by {ai,human}]
                       [--stale RC_STALE]
✗ FAILED t_slim_gate(1 條斷言)
```
同一份 patch 下 `-k rel_cascade`(30 支)與 `-k lint`(277 支)全綠,只有這一支既有的交付閘測試被打破——不是巧合的環境問題,是這份 diff 直接造成的回歸。

引句:「p.add_argument("verb", choices=["confirm", "prune", "list", "resume", "visited"])」

`scripts/lumos:27703`(依 patch hunk 行號;既有測試在 `scripts/test_lumos.py:25512`)

severity: major
blocking: 是

## 發現 2:其餘部分(lint 新檢查、cmd 分派、共用 helper、新測試寫法)都沿用既有慣例,沒有引入第二種做法

- `cmd_lint` 新增的兩欄檢查用 `warns.append(f"...")` 掛進既有的 `warns` 清單,跟同一支函式裡緊接在後的「開頭欄位鍵打錯」檢查是同一種寫法,結尾同樣交給既有的 `for w in warns: print(...)` 迴圈印出(`scripts/lumos:4544-4546`),沒有另開一套 warn 機制。
- `cmd_rel_cascade_visited` 對「帳本不存在 / header 損毀 / --from 不屬本 cascade」三種情況都用 `raise ValueError(...)`,跟同檔案 `cmd_rel_cascade_write`、`cmd_decision_supersede` 的既有寫法一致,交給 `if args.cmd == "rel-cascade": try/except (ValueError, RuntimeError, OSError)` 那層統一印 `擋下:{e}`(`scripts/lumos:12339` 附近、dispatch 段 `scripts/lumos:28348-28353`),不是自己另開一條輸出通路。對「還有待判鄰居」這個業務規則失敗改成直接 `print` 三段式後 `return 2`——這不是新樣式,`lumos loop list` 的現有程式碼已經是同樣「直接印三段式訊息 + return」的先例,而且比同一個 verb 家族裡 `cmd_rel_cascade_resume` 舊有的單行 `✗ ... 已放棄` 訊息更貼近 CLAUDE.md 明文的白話三段式標準。
- 抽出 `_rel_cascade_pending()` 給 `resume` 與新的 `visited` 共用,docstring 自己標了「★唯一實作★」,是避免「同一件事寫第二份」的正確做法。
- `_ledger_read` 把 `"visited"` 併進 `elif o.get("event") in ("transition", "visited")` 同一個收集分支,靠 `_ledger_fold` 既有的 `all(k)` 過濾自動排除 visited 事件(它沒有 neighbor/edge_type),經查證與程式碼行為一致,重用既有折疊機制而非另立一套。
- 新測試 `t_rel_cascade_visited_only_for_empty`、`t_lint_warns_empty_revalidate_when` 都用既有的 `mkvault()`/`write()`/`run()`/`check()`/`_lm()` 共用 test helper 建 fixture、下指令、斷言,手法跟同檔案裡其他 `t_rel_cascade_*` 與 lint 測試一致。

引句:「def _rel_cascade_pending(env, header, trans, quiet=True):」

`scripts/lumos:12480`(patch hunk 內新增函式)

severity: minor
blocking: 否
