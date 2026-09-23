severity: major

## F1 短名的字元規則跟舊的自動檔名規則另刻了一份,不是共用同一個 pattern

severity: minor
blocking: no

`_guard_plan_slug` 原本用取代型正則篩字元;新加的 `_GUARD_NAME_OK_RE` 為了逐字元檢查,把同一套字元規則又寫了一次,兩個正則字面各自維護,沒有共用一個常數或函式當單一事實來源。註解自己承認「跟舊的一套」,但沒有真的重用它——之後只要有人改動其中一個(例如放寬允許的符號),另一邊不會跟著動,也沒有測試會發現兩邊已經不同步。

引句:「_GUARD_NAME_OK_RE = re.compile(r"[\w一-鿿-]")   # 跟舊的自動檔名同一套字元規則」
引句:「s = re.sub(r"[^\w一-鿿-]+", "-", text.strip())[:40].strip("-")」

## F2 doctor 新段落的收尾判斷沒把新段落算進去,複製了同一區塊剛修過的「假乾淨」問題

severity: major
blocking: yes

這段自檢原本已經有一個明確的既有寫法:每加一種會 `warn_soft` 出來的情況,收尾那行「沒有逾期或快到期的預告合約」的判斷式就要跟著把那個變數也算進去——旁邊的註解就是在講這件事,而且明講出處是「代碼審 r1 通才席」曾經因為同一形狀的問題擋過一次(當時是 `_gover_other` 沒被算進收尾判斷)。這次新加的 `_gtrunc`(檔名截斷)區塊插在 `_gsoon` 之後、收尾判斷之前,但收尾的 `if/elif` 條件式只列了 `_gover`/`_gsoon`/`_gover_other` 三個舊變數,完全沒提到新的 `_gtrunc`。結果是:當這次改動沒有任何逾期或快到期的預告合約、但確實有守衛節點檔名被舊規則截斷時,畫面會先印一段 `⚠` 警告列出截斷的檔名,緊接著印一行 `✓ 沒有逾期或快到期的預告合約`——跟旁邊註解描述的「上面剛列完提醒,這裡再印沒事會讓人誤信沒事」是同一種讀法上的陷阱,只是換了一個變數沒被納入。全域收尾統計(`_soft`)有算到 `_gtrunc`(因為它照樣呼叫了 `warn_soft`),所以不是完全沒有安全網,但這個區塊自己的收尾行,沒有跟著同一段既有的寫法把新分支併進去。

引句:「if not _gover and not _gsoon and not _gover_other:」
引句:「warn_soft(_gtrunc, f"有 {len(_gtrunc)} 篇守衛節點的檔名是舊規則從合約原文截斷出來的(斷在句子中間):",」

## F3 `--name` 的必填檢查沒併進既有「一次列出所有缺項」的機制,跟 `guard plan` 自己其他必填參數的處理方式不一樣

severity: major
blocking: no

`guard plan` 既有的 `--plan`/`--phase`/`--due`/`--why`/`--owner` 都不是用 argparse 的 `required=True`,而是集中在 `_guard_plan_check` 裡用同一個 `missing` 清單一次收集所有沒填的欄位,缺兩項就一次講兩項(`scripts/lumos:10794`,`missing = [(v, lbl) for v, lbl in ((plan, "計劃參照"), (phase, "階段"), (due, "最遲日期"), ...`)。這次新加的 `--name` 同樣是「必填」,但走的是獨立的 `_guard_name_problem(name)` 檢查,擺在 `missing` 檢查之後才判斷,錯誤訊息也是單獨一組(不會跟其他缺項合併成一則)。結果是:如果使用者同時漏掉 `--plan` 又漏掉 `--name`,第一次執行只會被告知缺「計劃參照」,補上之後重跑才會再被告知缺短名——跟既有「缺什麼一次全講」的設計不一致,新參數自己另開了一條檢查路徑。

引句:「return "預告合約要給一個短名(--name)——不給的話,檔名只能拿合約原文截斷,會斷在句子中間"」

## 已驗過沒問題的部分(供對照)

- `--name` 的 argparse dest 命名(`gp_name`)、help 文字風格,跟同指令其他參數(`gp_plan`/`gp_phase`/`gp_due`/`gp_why`/`gp_owner`)一致,且 `guard plan` 自己的必填參數本來就不是靠 `required=True`,所以 `--name` 不用 `required=True` **不算**跟同指令內其他參數不一致(只是跟另一個不同指令 `guard settle` 的 `--test required=True` 不同,但那不在這條合約的比較範圍內)。
- `_gtrunc` 掃描不分「這次改動有沒有碰到」就全部列出來,乍看跟 `_gover`/`_gover_other` 的本機收窄設計不一樣;但因為它跟 `_gsoon` 一樣走 `warn_soft`(不影響退出碼、本來就不擋推送),`_gsoon` 本身也沒做本機收窄,所以這點跟同段既有寫法(非阻擋提醒不用收窄)是一致的,不算問題。
- 用 `grep -n '"guard", "plan"' scripts/test_lumos.py` 核對全部呼叫點(19+ 處):所有未經 `_gp` 包裝、直接用 `run(...)` 呼叫 `guard plan` 的地方都手動帶了 `--name`,沒有漏掉會在新規則下失敗的呼叫點。
- `_gp` 測試輔助定義在使用點附近(而非檔案最上方),跟本檔既有的 `_ledger_patch_last` 之類「就近定義測試輔助函式」的慣例一致,不算離題。
- 新的截斷偵測正則 `r"^預告的合約:(.+)$"` 跟檔案裡另外 4 處既有的同一條正則字面一致(`scripts/lumos:2327,10852,11091,11154,11192` 皆同),沒有另創一套解析邏輯。
