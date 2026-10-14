severity: minor

我跑過實驗的範圍:`_load_durations_table`、`cmd_test_durations_refresh`、簿記檔清單的副作用、新測試的偵測力。實驗在 `/tmp/lumos-seat-work/code-推送與CI提速/正確性-sonnet/repo`(0cdfc7cc 的複本)。

未發現 blocker 或 major。`_shard_by_duration` 本身的分法(聯集、不重複、確定性、中位數、權重下限、平手規則)我找不到失敗輸入。它是依 (-權重, 名字) 排序再逐支丟給最輕的一份,和輸入順序、`--ff`、`--seed` 都無關。

我另外在複本裡確認三件事:
- 提交的耗時表現在能用:`--shard i/4 --list` 四份各分到 512、512、512、513 支,印出同一個表雜湊。
- `--shard 2/4 -k shard --list` 先分片、後套 `-k`,行為和舊版一致。
- `ci.yml` 的 concurrency 表達式:PR 事件用編號分組並取消進行中的,push 事件用提交編號分組、不取消。cancelled 的結論在 `scripts/lumos` 已走「未定」不判綠(file: `scripts/lumos:46151`),所以不影響閘。

以下是 findings。

severity: minor
blocking: 否
- `_load_durations_table` 對超大整數會直接崩潰,不是 rc2。耗時表放 `{"t_x": 1` 後接 400 個 0 時,`math.isfinite(v)` 丟 `OverflowError`。這個例外既不是 `ValueError` 也不是 `OSError`,`main` 的 `except (OSError, ValueError)` 接不住。每一份都帶 traceback 崩潰,不是那條「表壞了每一份都 rc2 擋下」的訊息。
- 實測:`python3.14 scripts/test_lumos.py --shard 1/2 --list` 輸出 `OverflowError: int too large to convert to float`。
- 每一份結論仍一致,都是失敗,沒有混用兩種分法,所以只是訊息品質與例外類別的問題。
- 應該是 `except` 加上 `OverflowError`,或改成 `isinstance(v, float) and not isfinite(v)`。
- `t_runner_shard_by_duration` 的壞法清單沒有這一種。
- 這類壞表的另一個來源是巢狀過深導致 `RecursionError`,同樣接不住。我沒實測,⚠。
引句:「if isinstance(v, bool) or not isinstance(v, (int, float)) or not _md.isfinite(v) or v < 0:」

severity: minor
blocking: 否
- `cmd_test_durations_refresh` 遇到 run 檔的 `tests` 不是物件時會崩潰,而不是「略過讀不懂的檔」。例如 `{"version":1,"tests":["a"]}` 的 `tests` 是 list,`.items()` 丟 `AttributeError`。
- 實測:`lumos test-durations refresh --repo .` 輸出 traceback。這發生在寫表之前,所以表沒被毀,但 run 檔留著,下次還會崩潰。
- `isinstance(d, dict)` 只擋了最外層,沒擋 `tests`。
- `float(v)` 對超大整數也會丟 `OverflowError`,同一條路徑。
- 應該是 `tests` 不是 dict 就當讀不懂、略過。
引句:「for k, v in (d.get("tests") or {}).items() if isinstance(d, dict) else ():」

severity: minor
blocking: 否
- 簿記檔清單加了耗時表,但沒有任何測試或閘檢查已提交的耗時表格式。這會讓壞表繞過 CI。
- 步驟:
  1. 一次只改 `governance/test-durations.json`(例如合併衝突標記、手改壞)的推送,被判成簿記、`suite: docs`(新測試自己就釘了這個行為)。
  2. CI 於是只跑文件子集,綠燈。
  3. 下一個改程式的推送要跑全套,所有 shard 全部 rc2。
- 計劃寫「表錯只會分得不平均、不會漏跑」,但格式錯誤的表是整批擋下(每份 rc2),不是分得不平均。壞表等到下一次全套才被抓。
- 應該是文件子集裡含一條「已提交的耗時表能被 `_load_durations_table` 讀成功」的測試,或讓動到這支檔的推送至少跑一次格式檢查。
引句:「_BOOKKEEPING_FILES = (_TEST_DURATIONS_REL, "docs/.governance-log.jsonl", "docs/.usage-log.jsonl",」

severity: minor
blocking: 否
- `t_test_durations_refresh` 的「執行器真的寫 run 檔」那段偵測力不足,還會污染真 repo。
- 它在真 repo 的 `.lumos/` 跑巢狀子集,寫出 `test-durations-run.json` 且不清掉。
- 驗證只看 `wrote[0]` 裡有沒有那個測試名,不比對 `before` 快照,也不比 mtime。
- 還原翻紅釘不成立:把寫 run 檔的整段拿掉,只要 `.lumos/` 裡已有舊的 `test-durations-run.json`(含該名字,例如前一次跑過),`names` 讀的是舊檔,斷言照綠。第一次 refresh 之前的整套跑兩次就能出現這個狀況。
- 前置斷言只證明子集跑過,沒證明檔是這次寫的。
- 殘留的單支 run 檔也會被之後的 `refresh` 合進去,值是冷啟動單跑的秒數。
- 對應固定席節點 `測試假綠形態` 的 ★INVARIANT★:前置斷言必須證明被測那條路真的被執行到。這裡 `wrote` 沒證明寫入發生在此次呼叫,條款在這段不成立。
- 應該是測試前先刪掉該檔,或比對 mtime 大於起跑時間;最好把巢狀執行放進臨時 repo,不寫真 repo。
引句:「wrote = [p for p in after if p.name == "test-durations-run.json"]」

固定席節點逐條判:
- `測試假綠形態`(★INVARIANT★ 前置斷言):新增的 `t_runner_shard_by_duration` 有「★前置★ 現場成立」,證明輪流分在該組資料下確實不平均,合格。`t_test_durations_refresh` 的前置見上面第 4 條,不成立。
- `lumos-cli-lifecycle`、`lumos-cli-read`、`guard-kill`(re-inject、search、guard kill 的不變量):不影響。diff 沒有碰到這些程式路徑,新增的只有 `test-durations` 子指令與 `HELP_WHEN` 條目。
- `design-loop`:不影響,沒動處置閘。
- `pitfalls-code-loop`、`loop-convergence-recording`、`reversibility-governance-ledger`(★RISK★):只有簿記檔清單新增一項。副作用是只動耗時表的提交不讓代碼審留痕失效、也不被 pitfalls 掃描,這是設計意圖,但見第 3 條。

總結:最高等級 minor,blocking 共 0 條(minor 共 4 條)。
