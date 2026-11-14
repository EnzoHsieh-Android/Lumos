severity: major

## c1 CI 回流帳的 no-run 與 timeout-waiting 事件(run_id 為 null)仍被 gov 整行跳過,只修了一半
severity: major
blocking: 是 — 會讓 gov 與 gov --stats 靜默少算 CI 事件,正是這份修補要修的那類錯。
輸入是 `ci-wait` 寫進 `docs/.ci-log.jsonl` 的 no-run 或 timeout-waiting 事件。`_ci_record` 的呼叫端傳 `"run_id": None`,`rec` 照寫 `"run_id": rid`,帳上就是 `"run_id": null`。

`cmd_gov` 的 `load` 對每行先呼叫 `_gov_event_types_ok`。新表是 `"run_id": (str, int)`,`None` 不是 str 也不是 int,所以整行 `continue`。

我載入 `scripts/lumos` 實測 `_gov_event_types_ok`:
- run_id 為 `None`:False。
- run_id 為 `123`:True。
- run_id 為 `"abc"`:True。

預期是 CI 回流帳的每種事件都讀得到,實際上有兩種事件讀不到。上游改動前 `run_id` 沒登記,這兩種事件讀得到,所以這是改動選擇點功能帶進來的退步,本次修補沒補完。

我在 /tmp 的 clone 改試了一次:
- 把 `(str, int)` 改回 `(str,)`,`t_ci_status_and_gov` 紅。
- 把 `(str, int)` 改成 `(str, int, type(None))`,`t_ci_status_and_gov` 照綠。

所以測試只釘整數與字串,沒釘 null,補上 null 也不會被發現。

引句:「+    "run_id": (str, int),」
file: `scripts/lumos:67093`(no-run 寫帳,run_id=None)
file: `scripts/lumos:67102`(timeout-waiting 寫帳,run_id=None)
file: `scripts/lumos:18342`(`_gov_event_types_ok` 逐欄 isinstance)

建議是改成 `(str, int, type(None))`,並補一支餵 no-run 帳行的 gov 測試,先紅再綠。

## c2 型別表接受 bool 當 run_id,與同表其他欄位一致但沒擋
severity: minor
blocking: 否 — 讀者 `_render_gov_choice` 沒有拿 run_id 做算術或切片,混算沒有實際出錯路徑。
`{"run_id": true}` 因為 bool 是 int 的子類而通過。我只核對了 run_id 的讀者,沒有逐行走過 `_render_gov_choice`。choice-kill 那一行(`scripts/lumos:18421`)只是原樣取出 run_id。`scripts/lumos:46827` 的 `_e2e` 側會先轉字串。

這與同表 `attempt`、`ran` 等 `(int,)` 欄位的既有行為一致,不是這次引入的新風險。
引句:「+    # run_id 兩本帳同名不同型:choice-kill 帳是字串隨機碼,CI 回流帳是 GitHub 的整數編號」
file: `scripts/lumos:78097`(choice-kill 的 run_id 恆為 `uuid4().hex[:12]` 字串)

## c3 INDEX 把選擇點整列刪掉,改成 `choice-*` 簡寫;完整性測試因此照綠
severity: minor
blocking: 否 — 屬路由退化,不是行為錯誤。
`t_command_index_complete` 的 corpus 是 `commands/*.md` 全部子檔。只要 `06-代碼審與推送.md` 有 `lumos choice-points` 與 `lumos choice-kill` 就過,我實跑 `-k t_command_index_complete` 是 16 passed。

被刪的那列才有「什麼時候用」(改動選擇點的情境、接著跑什麼、存活怎麼處置)。現在 INDEX 只剩 `choice-*(改動選擇點)` 一個詞。

4.5k 的上限也靠這樣擠出來:`wc -m` 為 4491,只剩 9 字元餘裕,下一個新指令又會紅。照做不會出錯,只是 AI 從任務表找不到進入點。
引句:「+| 代碼要推、要過高風險審 | `commands/06-代碼審與推送.md` | pitfalls --diff / loop fix-check / code-loop pass·skip·check·blind-judge / situation-rule(人裁寫回) / choice-*(改動選擇點)」
file: `skills/lumos-project-notes/commands/INDEX.md:38`

## 其餘逐項對照(乾淨)
- **preexec_fn 與既有呼叫端一致**:`_ppc_sigint_default` 在 `scripts/test_lumos.py:85512`,其他呼叫端(31137、85527、139078)同樣用 `preexec_fn=`。新增那行與它們同形。
  - 引句:「+                             stdin=subprocess.DEVNULL, preexec_fn=_ppc_sigint_default)   # 分片在背景跑時繼承「忽略 SIGINT」」
- **非 POSIX**:測試開頭已有 `_os_mod.name == "nt"` 就 `raise _SrcOnly`,所以走不到 `preexec_fn`(Windows 的 Popen 帶 preexec_fn 會丟 ValueError)。
- **變異驗證**:`(trap '' INT; python3.14 scripts/test_lumos.py -k t_choice_kill_interrupt)` 拿掉 `preexec_fn` 是 1 passed、2 failed,補回是 3 passed。測試能抓回歸,但只在 SIGINT 被忽略的環境才紅。正常前景跑拿掉也全綠,必須靠 CI 與推送前閘的背景分片才抓得到,這是環境特性,不扣分。
- **其他 run_id 讀者**:`scripts/lumos:46827` 一帶轉字串比對,`_ci_latest_attempts` 以 `None` 判斷「沒有 run_id」,都不受 int 影響。
  - 引句:「+    "run_id": (str, int),」
  - file: `scripts/lumos:67186`
- **同名不同型欄位**:我對 `docs/.*.jsonl` 各帳逐行核對 run_id,只有 `.ci-log.jsonl` 有一筆,型別為 int,其餘帳都沒有 run_id。
  - 但帳檔裡現存的那一筆是整數,不是 null,所以 c1 的 null 事件在這份帳檔裡看不到,只能從 `_ci_record` 的寫法推出。我另外用 `_gov_event_types_ok` 直接餵 null 驗過。
- **圖譜筆記**:兩篇新 PITFALL 帶 `[出處:]` 與 `[根因:]`,`[test:]` 指向存在的測試。`測試執行器.md` 那條與既有兩條同族,不影響節點合約。
  - 對 impact 固定席:`guard-kill`、`bound-tests-gate`、`design-loop` 等的 ★INVARIANT★ 談的是 rc 優先序、綁定測試與 JSON 純度,本次改動沒碰到。
  - 引句:「+  PITFALL:新功能把欄位登記進 _GOV_FIELD_TYPES 時,另一本帳有同名但不同型的欄位,那本帳每一行都被整行跳過、gov 靜默少算」
- **新 PITFALL 的措辭**:它寫的修法是「新增欄位前把本 repo 各帳逐行跑過新舊兩版型別表」。這次的 null 漏洞正是沒做到這條,c1 因此成立。

臨時目錄的 clone 與兩個 `gctl-run-*` 現場已刪。

最嚴重:major;blocking 共 1 條
