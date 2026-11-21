# code-pass選擇點預判 r1 收貨紀錄

## 席報告收貨

standard 級:正確性一席加架構對齊一席(sonnet),同輪全部交回後從逐字稿存檔;兩份都已正規化,quote-check 全數錨定。

發現編號:正確性 c1–c3、架構對齊 a1–a4(共 7 條)。

## 判讀與去向(7 條全折;本輪有 major 席)

| id | 席 | 等級 | 去向 |
|---|---|---|---|
| a2 | 架構對齊 | major | 折:取分支名改用共用的 `_redbase_branch_name`(不用 `--short`) |
| c1 | 正確性 | minor | 折:同 a2(同名 tag 時 `--short` 回 `heads/<名>`) |
| a3 | 架構對齊 | major | 折:拿掉 `_CHOICE_PASS_WORDS`、`_choice_site_words`、`_CHOICE_PASS_FIX`;照鄰居 `_codeloop_pass_mech` 印推送前原文,再補 `_CHOICE_PASS_TAIL` 一句出口;計劃與系統筆記同步改 |
| a1 | 架構對齊 | minor ⚠ | 折:判為不是跨層直呼——`_choice_push_round` 就是加了 `site` 參數供 pass 呼叫,跟 `_spec_gate_push_check` 呼叫它同一層;理由寫進系統筆記 pitfalls-code-loop 那一節(接點與呼叫關係) |
| a4 | 架構對齊 | minor | 折:「模擬推送輸入」是設計審 r2 定的(起點只交給 `_push_range_start` 一處算,pass 只負責給遠端舊值),理由已在計劃〈做法〉範圍;不另改 |
| c2 | 正確性 | minor | 折:新增 `t_codeloop_pass_choice_range` 一案:feat/sit 已推過、再加一行 → 只列新的那一行(修前把遠端舊值改成全零會紅,見 r1-mutation-after-fix.txt「遠端舊值」) |
| c3 | 正確性 | minor | 折:測試拆成四支(最慢 50 秒,餘裕 4 倍以上) |

重現不到:0 條。修補因果:第一輪,不適用。

## 先查世界

- PRIOR-ART: 訊息寫法(a3)——查 repo 內鄰居:`_codeloop_pass_mech` 的說明寫明「每道印推送前同一段擋下訊息,再印 pass 自己的出口」;專案沒有事後換字串的先例。採用鄰居做法。不另查網路。
- PRIOR-ART: 取分支名(a2/c1)——repo 內 `_redbase_branch_name` 的說明寫明不用 `--short` 的理由(同名 tag);git 官方文件 `symbolic-ref --short` 說明它會縮成「不含糊」的名字(https://git-scm.com/docs/git-symbolic-ref),所以撞名時會帶 `heads/` 前綴。採用共用函式。
- 首輪,不必查方向。

## 修補後自我變異

r1-mutation-after-fix.txt:17 處改壞,16 處被測試抓到;「Kotlin 判斷」那處活下來,判為等價變異(拿掉它,後面那一圈本來就會判「不要求」並安靜放行,只是多做一次 git 範圍運算)。
