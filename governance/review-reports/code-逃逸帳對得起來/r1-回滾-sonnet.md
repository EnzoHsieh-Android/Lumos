severity: major

## F1 計劃承諾「在說明裡寫明要 lumos update」沒兌現,已實跑證實舊版讀新帳會靜默算錯數字
severity: major
blocking: yes
引句:「撤回紀錄永遠不回;被撤回的列預設不回,include_withdrawn=True 才回」
file: `docs/lumos-toolchain-knowledge/Projects/逃逸帳對得起來_計劃.md:64`——這一行是計劃自己(上一輪「回滾席」)寫下的殘留風險與承諾:「舊版 lumos 讀到撤回紀錄:還沒更新的消費專案跑舊版 `--list`,會把撤回紀錄當成欄位不標準的可疑列印出來(不會壞,只是吵);在說明裡寫明要 `lumos update`。」

重現步驟(已實跑,不是推測):
1. `git show HEAD~1:scripts/lumos > exp-回滾/old/lumos`(HEAD~1 就是本次改動之前的版本,對照 patch 的 `-` 段確認一致)。
2. 用新版 lumos 建一個審查帳(迴圈「甲」有審查紀錄)、記一筆逃逸(`loop escape 甲 --stage CI --severity major --desc 測試缺陷 --sha abc1234`),再撤回它(`loop escape --withdraw <token> --reason "重現後確認是誤判" --by tester`)。
3. 用舊版 lumos(`exp-回滾/old/lumos`)對同一份 `.escape-log.jsonl` 跑:
   - `loop escape --list` → 印出「逃逸帳:2 筆」,多出一列幽靈條目:`?:1 筆(最重 非標準值 None(手改帳?))` / `[?None@?] [沒標該抓的規則]`——因為舊版 `_escape_rows_for` 沒有 `isinstance(d, dict)` 之外的任何過濾,`kind=withdraw` 那筆因為 `loop_id is None` 直接被當成一般逃逸列吞進去,`d.get("loop")`、`d.get("severity")` 都是 `None` 印出可疑格式。
   - `gov --stats` → 「審查有沒有用」段印「逃逸帳 2 筆(最重 major)」,實際只有 1 筆真逃逸(已撤回不該算),多算了 100%。
4. 兩個指令 rc 都是 0,不會報錯,只是數字跟畫面吵而已——跟計劃自己預期的「不會壞,只是吵」完全吻合。

問題在於:計劃已經預見這件事、也承諾了緩解(在說明裡寫明要 lumos update),但整份 diff(`grep -n "lumos update" r1-snapshot.patch`)找不到任何一處新增這句提醒——不在 `skills/lumos-code-loop/SKILL.md`、不在 `skills/lumos-design-loop/SKILL.md`、不在 `skills/lumos-project-notes/commands/06-代碼審與推送.md`,這三份說明檔這次確實都改了逃逸帳那一段(補了 `--sha`/`--withdraw`/`escape-stats` 的用法),卻唯獨漏了這句「舊版消費專案要 lumos update」的提醒。這正是這次改動自己在「相容性」上留的洞,而且是**這一輪的回滾席自己記下的待辦、卻沒有被實作方接住**——換句話說,這條改動本身就是逃逸帳想抓的那種案例:設計期就該看出來、卻漏到交付時才發現沒兌現。

影響範圍:任何還沒 `lumos update` 的消費專案(這是這個 repo 常見的真實場景,version skew 在 worktree/多 session 情境下反覆發生過,見專案記憶 `worktree 推送時 pass 記錯分支`、`探針來源必須自己有 git 目錄` 等記錄),在別人已經開始用撤回功能之後,會拿到看似正常(rc0)但數字偏高、且清單裡混進一條看不懂的「?」列的逃逸帳畫面,而且完全沒有線索指向「要更新工具」。

建議:在本次改動已經動到的三份說明檔(或至少 `skills/lumos-project-notes/commands/06-代碼審與推送.md` 那張表)裡,補一句「舊版 lumos 看到撤回紀錄會顯示可疑列、統計會偏高,`lumos update` 之後才會正確跳過」,把計劃裡已經寫好的緩解真的落地。

---

## 已看,無:
- `_escape_rows_for` / `_plan_for_loop` 的既有呼叫者逐一核對過:
  - `_escape_rows_for(env)`(doctor S14 撤除條件分子,`scripts/lumos:2303`)、`_sc_history` 小改動閘歷史檢查(`scripts/lumos:6305`)、`_render_gov_stats` 治理帳統計(`scripts/lumos:7084`)、`_review_yield_line` 問閘尾漏斗(`scripts/lumos:19005`)——四處都是計劃 WHY 行明講要「不算撤回」的讀者(問閘尾漏斗、治理帳統計、健檢撤除條件分子、小改動閘歷史),行為改變是設計內的,不是意外。
  - `_auto_escape` 的去重讀法改用 `include_withdrawn=True`(`scripts/lumos:9539`),confirm 撤回過的同觸發不會悄悄補回,S5 測試 `t_escape_withdrawn_not_resurrected_by_auto` 已覆蓋。
  - `_plan_for_loop` 現有唯一呼叫者(`scripts/lumos:8192`,代碼審自動記逃逸掛勾)自己已經先手動去掉 `code-` 前綴才傳進去,不受這次新加的前綴/NFC 修正影響——跟計劃「回退」段落第二點(`既有唯一呼叫者自己已經先去掉 code-,不受影響`)一致,已實跑核對過呼叫點程式碼確認。
- 舊版 lumos 讀到新欄位(`loop_kind`、`sha`、`defect_ref_missing`)本身:舊版 `cmd_loop_escape`/`_escape_rows_for` 對未知欄位一律用 `.get()` 取值,多出來的欄位不會讓舊版崩潰,純粹是新資訊被忽略,沒有相容性問題。
- 自動記錄(`--auto`,CI/push-gate 用)路徑完全繞過本次新增的「手動記帳要 --sha/--defect-ref」門檻(那段檢查在 `if auto:` 分支的 `return 0` 之後才執行),grep 過 `scripts/hooks/` 與現有文件裡所有 `loop escape` 呼叫點,程式化呼叫全部走 `--auto`,不會被新規則擋下,pre-push hook / CI / 規格閘現有寫法不受影響。
- 既有測試 `t_loop_escape_ledger`、`t_doctor_escape_by_door` 在 diff 裡已同步補上 `--defect-ref`,跟新規則一致,沒有漏改造成本地測試假紅或假綠的情況。

共 1 條(major)。
