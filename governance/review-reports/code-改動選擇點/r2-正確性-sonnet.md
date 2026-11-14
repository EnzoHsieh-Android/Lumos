severity: major

## c1 守的測試雜湊拿「第一支含測試名的檔」當測試檔,常常撈到計劃筆記,補強測試不重跑、改筆記反而誤重跑 (be-api-compat、be-authz 皆不適用)
severity: major
blocking: 是(修補要保證的行為「補強測試後重跑」在常見目錄排列下不成立,測試只釘住 `app/` 排在 `docs/` 前面的排列,抓不到)

- 輸入:測試名 `alphaCase` 同時出現在計劃筆記 `docs/p/plan.md`(`[test:alphaCase]` 綁定條款一定會寫測試名)與測試檔 `feature/ui/src/test/VmTest.kt`。
- 路徑:`_choice_test_blobs` 用 `git grep -l -F -e <名>` 取第一個命中的檔。git 依路徑排序,`docs/` 排在 `feature/`、`lib/`、`ui/`、`shared/` 之前,命中的是筆記。
- 預期:補強 VmTest.kt 內容後,`_choice_tests_sha` 改變,存活的行重跑。
- 實際:雜湊算的是筆記的物件編號。測試檔改了雜湊不變,存活行被當成「測試沒變」帶過去不重跑。改計劃筆記一個字(例如 `situation-rule --point` 會改計劃)雜湊就變,存活行被誤重跑,推送端也會誤報「另一組守的測試」。
- 該行為在 `app/` 排在 `docs/` 前面的專案(單模組 `app`)恰好成立,所以現有 `t_choice_kill_rerun_rules` 的 fixture 照綠。

引句:「+    for n in sorted(set(names)):」
引句:「+        r = _lens_git_dl(rr, "grep", "-l", "-F", "-e", n, at_sha, "--", deadline=deadline)」
file: `scripts/lumos:77863`、`scripts/lumos:77642`

重現:我在臨時副本(已刪)建 `docs/p/plan.md` 加 `feature/ui/src/test/VmTest.kt` 兩檔的 repo,三個提交依序是初始、補強 VmTest.kt、改 plan.md,逐版跑 `_choice_test_blobs` 與 `_choice_tests_sha`:

| 版本 | 修前 `_choice_tests_sha(t)` | 修後 `_choice_tests_sha(t, blobs)` | 修後撈到的 blob |
|---|---|---|---|
| HEAD~2(初始) | 01b37735… | 397af41e… | cef70c09(plan.md) |
| HEAD~1(補強測試) | 01b37735… | 397af41e…(沒變) | cef70c09 |
| HEAD(只改筆記) | 01b37735… | 93a2d31d…(變了) | cadbd93a |

歸因:兩件事分開。
- 「補強測試不重跑」:有證據的原有漏查,修前雜湊只看名字,修後在這個排列下仍沒修好。
- 「改筆記就變雜湊」:有證據的修復回歸,修前雜湊不隨筆記變,修後會變。

## c2 AI 放的選擇點放行從程式碼審小結消失,放行指令卻仍說「推送前小結會一直列出來」 (be-authz:放行是推送閘的繞過入口,AI 放行的人工覆核提醒屬同一類)
severity: minor
blocking: 否(doctor 仍會列;提醒類功能缺一處,不致損壞資料)

- 輸入:放行檔有一筆 `choice:A.kt:abcd`,`origin: ai`、未 ack。
- 路徑:`_codeloop_lint_new_step` 填 `lv["ai_pending"]` 與 `lv["ai_pending_situation"]`,兩者都走 `_lint_waivers_ai_pending`。修補後它只數新增告警與情境段,選擇點兩邊都排除。`_cl_say_lint_waive_notes` 只印這兩個數。
- 預期:小結列出「有 N 筆 AI 放行還沒人看過」,或選擇點有自己的一行。實際:小結完全不提。
- 同時 `cmd_lint_waive` 對 AI 放行仍印「推送前小結與 lumos doctor 會一直列出來」,對選擇點放行這句已不成立。
- 現有 `t_choice_gate_stats_dedup` 只釘住計數函式 `(1,1)`,沒有測小結輸出與這句提示。

引句:「+    lint, sit, _choice = _lint_waivers_split(cur)」
引句:「        print("  這筆是 AI 放的(沒有互動終端):推送前小結與 lumos doctor 會一直列出來,直到人用 lumos lint-waive --ack --all 看過。")」
file: `scripts/lumos:80321`、`scripts/lumos:42534`

歸因:有證據的修復回歸。修前與修後對同一個放行檔各跑一次 `_lint_waivers_ai_pending(R)`,修前回 1,修後回 0;`situation=True` 兩版都是 0。

## 三問
**①原問題的修復效果**
- G1 回報上限(放行不重洗抽中集合)、G2 弱證據、G4 字串串接鏈、G7 重疊唯一、G5 逐檔掃描,對應子集全綠:`t_choice_push_cap_waive_stable` 5/5、`t_choice_kill_weak_evidence` 7/7、`t_choice_points_str_concat_chain` 9/9、`t_choice_unique_overlapping` 7/7、`t_choice_scan_per_file` 7/7。
- G3 見 c1:只在特定目錄排列下生效,不是一般性的修好。
- 以上只證明修後測試通過,沒有逐一用修前版本跑同一案例比對,因此「問題已解決」只算這些測試所涵蓋的輸入。

**②修補處的正常、錯誤與相鄰呼叫路徑**
- `sbr.yml` 改成雙重否定:400 個本機 `.kt` 檔,新舊規則各掃一次,命中集合 10563 筆,兩邊差集皆 0。
- `_choice_scan` 改成逐檔各跑一次:單檔輸出的檔名對映與批次一致(單檔 5 筆命中,對映成功);100 個小檔逐檔共約 1.4 秒,不會吃光推送閘 30 秒時限。
- `_count_overlapping`:`_kill_judge_file`、`cmd_guard_kill`、`_situation_rule_recipe_problem`、`_choice_identity` 四處改用它。實際替換的是 `replace(old, new, 1)`,「重疊算入後恰好一次」時第一處就是唯一一處。我 grep 範圍內沒有漏掉的 `.count(old)` 同族。
- `_choice_identity` 的視窗化:行索引與視窗邊界逐項核過,沒找到差一。
- `_choice_iv_cover`、`_choice_err_cover` 的二分加合併區間邏輯,我推演過正確。
- G8 的 rid_map 加平台對映:`cmd_guard_kill` 的 `plat` 取自 `r.get("platform")`,與配方一致。
- 未驗:兩個平台同名測試的端對端行為(只讀碼與跑 `t_choice_kill_same_name_two_platforms` 的名稱,沒獨立造案例)。

**③新發現在修前、修後各是什麼**:見 c1、c2 兩個表。

## 圖譜鏡頭
這次沒附固定席節點(鏡頭計算超時),無法逐條判固定席。

## 規格與角色卡
- be-api-compat:
  - `choice-points` 在有檔算不出來時多回 rc 3,計劃本來就把 rc 3 定給「ast-grep 不在」,語意相近。
  - 舊帳的 `tests_sha` 沒有物件編號,新程式讀到會讓全部存活行重跑一次、推送端多一行提醒(不擋)。這是預期的新舊互讀,不算缺陷。
- be-authz:除 c2 外,沒找到任何新增端點或授權檢查的改動。
- 未驗範圍:S26 真 Android 專案端到端耗時;`situation-rule --point` 與 `choice-kill` 在 `docs/` 目錄不存在的 repo 的寫帳語意(`_gate_event` 回 None 不再算寫失敗,實際上這種 repo 也沒有計劃筆記,我判斷不可達)。

最嚴重:major;blocking 共 1 條
