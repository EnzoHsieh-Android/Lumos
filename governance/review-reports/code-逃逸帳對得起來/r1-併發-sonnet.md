severity: minor

## F1 `escape-stats` 對同一迴圈的每一列逃逸都重算一次計劃檔分類,讀大帳時是不必要的重複磁碟 I/O
severity: minor
blocking: no
引句:「return [(kind, tier, sc) for sc in _escape_plan_scopes(env, lid)]」
file: `scripts/lumos:9903`(`_escape_stats` 內的 `_cats` 閉包)、`scripts/lumos:9920-9933`(`for r in rows: ... for c in _cats(lid):`)

問題:`_cats(lid)` 在 `_escape_stats` 裡被呼叫兩輪——先對每個 `released` 迴圈呼叫一次(建初始 `cats`),再對**逃逸帳裡每一列**各呼叫一次(算 leaked/next)。`_cats` 內部呼叫 `_escape_plan_scopes(env, lid)` → `_plan_for_loop` → 對 vault 的 `Projects/` 目錄做檔案存在檢查、找到後再開檔讀 frontmatter、parse tags。這個結果對同一個 `lid` 在同一次 `_escape_stats` 呼叫裡是常數(不隨列變化),但沒有任何記憶化——同一個迴圈如果在逃逸帳裡有 N 筆列(例如同一迴圈長期被 CI/人工記到多筆缺陷,或大量歷史帳),就會重複開檔讀同一份計劃筆記 N 次。這不是本次 `## S1`/`## S4` 條款要求的行為,純屬實作沒省下的成本,不影響正確性(結果仍對),但跟提示裡的「escape-stats 讀大帳的耗時」直接相關:帳越大、同一迴圈重複記錄越多,`escape-stats` 就線性變慢,而理論上只需要對「不重複的 lid」算一次。

實測(在唯讀複製的 repo 上跑,不影響原 repo):
```
cd /private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/ba2fc358-b2c4-4fe8-b8cf-9883c1468562/scratchpad/escimpl/exp-併发
python3 perf_test.py
```
結果(4 核 macOS 本機):
```
n_rows=   200 n_loops=   200 -> 0.364s
n_rows=  2000 n_loops=     1 -> 0.425s
n_rows= 20000 n_loops=     1 -> 1.190s
```
20000 筆逃逸列全部落在同一個迴圈時,`escape-stats` 花 1.19 秒,其中對同一份 `Projects/loop0_計劃.md` 重複開檔讀了 20000 次(理論上只需要 1 次)。目前真實帳(`docs/.escape-log.jsonl`)只有 25 筆,遠遠不到會有感的量級,所以現在不影響任何人;但這是這次新加的 `escape-stats` 自己的成本模型,不是既有問題,往後帳變大(尤其是同一個長壽迴圈)會線性拖慢——不是 O(n²),但常數項比它該有的高。

建議(不要求本輪就改):在 `_escape_stats` 開頭把 `_cats(lid)` 的結果快取成 `{lid: [...]}` 的 dict,兩輪都查表而不是重算。

已看,無:
- 撤回的「確認目標→寫入」與手動/自動記帳是否共用同一把 `_vault_write_lock`、會不會互踩:三條路徑(`_escape_withdraw`、`cmd_loop_escape` 手動記帳、`_auto_escape`)都把「讀既有帳→判斷→寫入」整段包在同一把 `_vault_write_lock(env.vault)` 裡,鎖鍵只看 vault 路徑,三條路徑會拿到同一把鎖,彼此完全序列化。實跑 12 個行程同時 `--withdraw` 同一個 token:只有 1 個成功、11 個因為「已經撤回過了」被擋下,帳本裡只多了 1 筆撤回紀錄,沒有重複撤回、沒有帳本壞掉(`concurrency_test.py::test_concurrent_double_withdraw`)。
- 手動記帳(這次新上鎖)跟 hook 觸發的自動記(舊本來就上鎖)會不會互等出死鎖:鎖是同一把互斥鎖、不是多把鎖按不同順序拿,結構上不可能循環等待;鎖對「同一個程序」是可重入的(`_VAULT_LOCK_HELD` 用 pid 級計數,見 `scripts/lumos:14224-14230`),但檢查過四個呼叫 `_auto_escape` 的入口(`cmd_loop_escape --auto`、`cmd_canary_record` 代碼審自動記、`_spec_gate_push_one` push-gate、`_ci_red_escape`),沒有一個是在已經持有這把鎖的情況下再去呼叫 `_auto_escape`——重入分支目前用不到,但也沒有反例會卡住。實跑 16 個行程同時手動記帳(等同「手動+自動同一時間敲同一份帳」的最壞情形,因為兩者用的是同一把鎖):0.78 秒內全部完成,沒有行程卡住,帳本剛好 16 行,沒有遺失寫入(`concurrency_test.py::test_concurrent_manual_and_auto_no_deadlock_no_loss`)。
- 鎖逾時(等 60 秒搶不到鎖拋 `RuntimeError`):這次補的 `try: cmd_loop_escape(...) except (ValueError, RuntimeError) as e: print(f"擋下:{e}"); return 2`(`scripts/lumos:32143-32147`)是新增的,補的正是「以前 `loop escape` 逾時會整個沒接住、直接把 traceback 噴出來」這個洞——沿用了同檔案裡另外十幾處相同寫法的既有慣例,不是這次獨創、也沒有漏掉哪個分支:`--auto` 分支本身在 `cmd_loop_escape` 內部直接呼叫 `_auto_escape`,靠外層那道新加的 try/except 接住;另外三個呼叫 `_auto_escape` 的地方(代碼審記帳、push-gate、CI)各自本來就有 `except Exception`,涵蓋 `RuntimeError`,四條路徑都不會讓鎖逾時變成未接住的例外。
- 讀的一側(`--list`、`escape-stats`)遇到寫一半的最後一行:讀帳一律逐行 `json.loads` 包 `try/except ValueError: continue`,壞行直接跳過,不會讓整個讀取炸掉。實跑 4 個行程不斷寫、4 個行程同時不斷跑 `--list` 與 `escape-stats --json` 共 8 秒(期間寫入 88 筆):0 個例外、`escape-stats` 輸出的 JSON 全部能正常解析、帳本落盤後 88 行全部是合法 JSON,沒有半行損毀(`reader_race_test.py`)。這與計劃筆記 119 行「讀的一側遇到寫一半的最後一行略過」的描述一致。
- 逃逸帳檔是符號連結時,自動記(hook 觸發)沒有跟手動記帳、撤回一樣過 `_escape_log_guard`:確認過計劃筆記第 58 行明寫「★帳本檔是符號連結就擋下的那道檢查不在這支函式裡,在 `cmd_loop_escape` 手動記帳那段★……撤回要先過同一道檢查」,範圍只講手動記帳與撤回共用,沒有要求自動記路徑也要過——讀碼結果(`_auto_escape` 直接呼叫 `_jsonl_append_verified` 沒過 `_escape_log_guard`)跟這個範圍界定一致,是既有設計取捨,不是這次改動漏掉的洞。
