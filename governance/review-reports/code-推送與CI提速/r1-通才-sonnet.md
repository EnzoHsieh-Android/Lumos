severity: minor

我逐 hunk 讀了 patch,也在臨時 clone(頂端 0cdfc7cc)跑了 `t_runner_shard_by_duration`、`t_test_durations_refresh`、`t_ci_yml_speed_shape` 和 `-k push_summary`,全部通過。找到兩條小問題,都不影響分片聯集等於全部這條主要不變式。

severity: minor
blocking: 否
**1. `cmd_push_summary` 被插入的新函式吃掉結尾的 `return 0`。**
- 新函式 `cmd_test_durations_refresh` 插在 `cmd_push_summary` 最後一行 `_gate_event_or_warn(...)` 之後,原本屬於前者的 `return 0` 被後面的新函式接走。
- 在頂端版本用 `ast` 檢查,`cmd_push_summary` 的最後一個敘述不是 `Return`,回傳值變成 `None`。
- 兩個函式之間也少了兩行空行(E302/E305)。
- `main()` 直接 `return cmd_push_summary(...)`,最後 `sys.exit(None)` 等於 0,所以 `-k push_summary` 的 10 支都過,沒有可見的壞處。
- 風險是這個函式的回傳契約被改了:日後有人在行程內用 `== 0` 判斷,或把 `_cli` 的結果往上傳,就會得到 `None`。
- 應該是把 `return 0` 補回 `cmd_push_summary`,再補兩行空行。
- 嚴重度降為 minor,原因是沒有可觀察的 rc 變化,也沒有翻紅的測試。
引句:「_gate_event_or_warn(root, "prepush-summary", "blocked", f"推送前擋下 {n} 筆({len(gates)} 道閘)", hard=True, extra=extra)」

severity: minor
blocking: 否
**2. 某一份測試紅了的時候,ci.yml 的「第 i 份耗時 N 秒」那行不會印出來。**
- GitHub 的 `run:` 預設 shell 是 `bash -e {0}`,子殼層會繼承 `-e`。
- 子殼層裡 `python ...` 一回非 0,就在 `rc=$?` 之前結束,後面的 `echo "第 i 份耗時..."` 沒機會跑。
- 我用 `bash -e -c '( ...; false; rc=$?; echo 耗時; exit $rc )'` 重現:rc 保留為 1,但 log 是空的,耗時行沒印。
- 紅掉的那一份正是需要看耗時的時候,例如被 `LUMOS_TEST_TIMEOUT` 打斷、分片不平均。
- 應該是 `python ... || rc=$?` 再 `echo`,或把 `rc=0` 放在前面,用 `python ...; rc=$?` 之前先 `set +e`。
- 這一條會讓 ci.yml 新增的撤除條件(量每份耗時)在紅燈時缺資料。
引句:「( s=$(date +%s); python scripts/test_lumos.py --shard "$i/$SHARD_TOTAL"; rc=$?; echo "第 $i 份耗時 $(( $(date +%s) - s )) 秒"; exit $rc )」

**固定席節點逐條判**
- `Systems/測試假綠形態.md`(★INVARIANT★ 還原翻紅釘要配前置斷言):不影響。新測試 `t_runner_shard_by_duration` 和 `t_test_durations_refresh` 都有 `★前置★ 現場成立` 的斷言,也就是輪流分確實不平均、子集確實跑了。
- `Systems/lumos-cli-lifecycle.md`(re-inject 保留 sentinel 之外內容):不影響。patch 沒碰注入或 CLAUDE.md。
- `Systems/lumos-cli-read.md`(search 預設排除 superseded):不影響。patch 沒碰 search。
- `Systems/guard-kill.md`(guard kill 的 rc 優先序與 `--json` 純度):不影響。patch 沒碰 guard kill,新增的 `test-durations` 是獨立的子指令分派。
- `Systems/design-loop.md`(處置閘第五步):不影響。patch 沒碰審查迴圈的閘。
- `pitfalls-code-loop`、`loop-convergence-recording`、`reversibility-governance-ledger`(★RISK★,牽連 `scripts/lumos`):
  - 這三篇只是 `scripts/lumos` 被改到才被牽連。
  - 簿記檔清單加入耗時表,是 `pitfalls` 掃描排除和代碼審留痕豁免共用的單一來源。我跑 `t_test_durations_refresh`,只改耗時表的推送判成 `docs` 子集,沒有問題。
- 其餘「超出上限、只列名」的 Systems、Projects 節點:我沒有逐篇讀,未判。

**檢查後確認沒有問題的地方**
- `_shard_by_duration` 是純函式,同輸入同結果。各份獨立算出的聯集等於全部,且不重複,這點有測試覆蓋。
- 耗時表壞了時每一份都 rc2 擋下,不會混用兩種分法。
- 耗時表裡沒有的測試用中位數補,權重有 0.05 秒下限。
- 耗時表壞掉時,`refresh` 會從空表開始,可能把只含一次 `-k` 子集的結果寫成新表。這只會讓分片不平均、不會漏跑,而且計劃明講表錯只影響平均度,所以沒有列為 finding。

最嚴重等級 minor,blocking 共 0 條。
