severity: minor

我逐 hunk 讀完,也實跑了自檢和新測試,沒找到會做出錯行為的洞。真規則包自檢結果是「規則 228 條,問題 0 個」。`t_kotlin_rulepack_good_cross_rule` 的 5 項斷言全綠。

**路徑比對、blocking 範圍、_sample_owner**
- 路徑比對沒問題。`scan` 在 `cwd=HERE` 下跑,ast-grep 回相對路徑 `samples/good/...`。`rel`、`h == rel`、`endswith("/"+rel)`、絕對路徑 `h == str(f)` 四種寫法都對得上。cross- 檔放在 `src/test`、巢狀子目錄也一樣(`_sample_owner` 只取 `parts[2]`)。
- 只算會擋規則(blocking)的行為也對。覆核級、提示級、不接閘規則命中非 cross- 的好例不報,命中 cross- 檔則算「有被命中」,符合設計。
- `_sample_owner` 回空字串時,跨規則與 cross- 兩條路徑都不處理,只會少報,不會誤報。
- `good_cases` 排除 cross- 後,真規則包沒有任何規則因此只剩一段。
- 去重案例搬走後,原規則對 cross- 檔「零命中」仍有驗。cross- 檔照樣被好例掃描掃到,原規則命中它會走既有的 `hits[("good",owner,owner)]`,報「好例誤報」(測試 ④ 驗了)。

**13 處樣本修改**
- 我對照了規則檔(`kt-paging-source-reused`、`kt-vm-channel-event`、`kt-public-mutable-holder`、`kt-vm-fun-returns-stream`、`kt-nonatomic-state-update`),每處改後仍在示範原規則的標準寫法。
- `dao.pagingSource()` 改 `repo.pagingSource()`,對規則來說形狀一樣(`S` 要符合 `^\w+$`,兩者都不符合),誤報防線沒掉。
- 改名 `events`/`toasts` 為 `ticks`/`uploads`,只是避開 `kt-vm-channel-event` 的名稱比對,本條要示範的形狀還在。

**變異驗證(複製到臨時目錄逐道改壞,跑單支測試)**

| 改壞的位置 | 結果 |
|---|---|
| 拿掉 `elif rule_id in blocking_ids`(不報跨規則命中) | ① 紅 |
| cross- 檔不略過 | ② 紅 |
| 拿掉「cross- 沒被命中」檢查 | ③ 紅 |
| `good_cases` 不排除 cross- | ⑤ 紅 |
| cross- 檔不計入自己的好例誤報 | ④ 紅 |
| 命中的規則不限 blocking | ② 紅,且真規則包報 19 個問題 |

四道新檢查各自拿掉,都有對應斷言翻紅。下面 F2 說明哪一種改壞測試抓不到。

---

F1
severity: minor
blocking: 否
引句:「+        launch { flowOf(1, 2).collect { values += it } }   // 有限流;不用 toList(會撞會擋的 TEST-5)」
失敗場景:`review-fp-finite-flow.kt` 的第二例原本是 `launch { flowOf(1, 2).toList(values) }`。它同時被覆核級規則 `kt-runtest-launch-collect-forever` 的 `$F.toList($$$)` 分支,和會擋的 `kt-test-tolist-not-background`(`rules/testing.yml`)命中。後者是 warning 等級,有限流在 launch 裡根本不會卡住,所以這是會擋規則的真實誤報。
- 改成 `collect` 後,這個誤報形狀不再被任何樣本記錄。第二例也變成和第一例相同的 launch+collect 形狀,覆核級規則 `toList` 分支的誤報紀錄跟著消失。
- 結案筆記寫「沒有規則誤報」,和這處矛盾。
- 這只是覆蓋與紀錄的缺口,規則行為沒變,所以標 minor。

F2
severity: minor
blocking: 否
引句:「                if kind == "good" and Path(f).name.startswith(REVIEW_FP_PREFIX) and rule_id in review_ids:」
失敗場景:`review-fp-` 檔被「別條會擋規則」命中時,應走 `cross_hits` 報問題。這正是 F1 那處修補要解決的情境。
- 新測試沒有釘這個情境。我把 `elif rule_id in blocking_ids:` 改成 `elif rule_id in blocking_ids and not Path(f).name.startswith(REVIEW_FP_PREFIX):`,也就是 review-fp 檔一律豁免跨規則報告,5 項斷言仍全綠,真規則包也是 0 問題。
- 日後有人把 review-fp 整檔豁免,測試不會紅。
- 既有的 `review-fp-sneaky` 測試只釘「本條規則命中自己」,不是「別條會擋規則命中」。
- 建議補一條:review-fp 檔內放別條 blocking 壞寫法,預期報「好例被會擋規則」。

總結:最高嚴重度 minor。

圖譜鏡頭:這次沒附固定席筆記,沒有可逐條判的項目。我只看到 `Systems/kotlin規則包` 新增的那條 WHY 和 `[test:t_kotlin_rulepack_good_cross_rule]` 對得上,而且新增那條 WHY 說的「17 處全是樣本問題」與 F1 有出入。

角色卡:`be-api-compat`、`be-authz` 都不適用。這份改動沒有端點、對外 API 或授權路徑,只動規則包自檢和測試樣本。

我建的 `gctl-run-*` 暫存和 clone 都已用字面路徑刪除。臨時目錄只剩變異腳本 `/tmp/lumos-seat-work/code-規則包好例跨規則檢查/正確性-sonnet/mut.py`。
