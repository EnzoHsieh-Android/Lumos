# r1 收貨紀錄(code-存量漂移防線甲)

凍結材料:r1-snapshot.patch(3ba5eef5..b9ca00bb,scripts/ 與 Systems、Issues 筆記,2097 行,sha256 a1e1d8e1…);超過 1800 行,拆成 r1-snapshot-code.patch(scripts/lumos,1501 行)與 r1-snapshot-tests-notes.patch(測試與筆記,596 行),每席兩份都給。記帳的 reviewed 用整份的指紋。
分級:pitfalls 判 standard;計劃〈實務隱患〉寫明守衛面照 high 審,本迴圈定錨 high(多一席資安、一席外家)。
7 席:正確性 opus;併發、邊界、圖譜一致、架構對齊、資安 sonnet;外家 finder Codex(gpt-5.6-sol xhigh,唯讀沙盒,從 clone 目錄啟動)。

## 席位收貨

- 7 席全交,等完成通知、ls 確認後才讀;clone 與 rtb 唯讀複本的 reflog 只有編排者自己的提交,席位沒動 repo。
- report-normalize 7 份皆已正規化。quote-check:6 份全錨定;資安席 3 句有 2 句錨不到——那兩句是它在「已看,無 finding」段拿來佐證的既有程式碼(不在 diff 裡),它唯一一條 finding 的引句有錨定,不影響採信。
- 發現 25 條(正確性 8、外家 9、邊界 2、併發 2、架構對齊 2、資安 1、圖譜一致 1),沒有 blocker。
- 規則:本輪有 major,accepted 必須是空的,25 條全折。

## 機械重現

| 發現 | 做法 | 結果 |
|---|---|---|
| 外家 F1(正式行掃到摘要以外) | 呼叫 _guard_formal_line,valid_under 裡放同一句正式行 | HIT:回 True |
| 正確性 F1 / 外家 F2(原文帶方括號標籤) | 呼叫 _guard_formal_line,合約原文含 [status:manual] | HIT:回 False |
| 外家 F5(guards 空欄) | Env.from_texts + _drift_state_findings,guards: [] | HIT:列成 c3 |
| 架構對齊 F2(同名 plan_refs) | _drift_plan_followups,[[退款]] 同名 Issues/退款 與 Projects/退款 | HIT:env.resolve 取到 Issue |
| 外家 F4(圖譜改名後讀舊提交) | _drift_tree_env 用現在的圖譜位置讀 67b75fd6^ | HIT:0 篇(那時在 docs/kg-knowledge,讀得到 2 篇) |
| 邊界 F1、F2(考卷形狀) | 新回歸測試 ⑦ 三種壞考卷 | HIT:KeyError、TypeError、AttributeError |
| 併發 F1(預算) | time lumos drift check --diff 87d43a50..HEAD | HIT:席位量 67.6 秒;修後 28.4 秒 |

## 判讀與處置

- 全部折進程式與筆記,先寫回歸測試 t_drift_code_review_r1_regressions(在舊碼上紅 12 條,修後綠),再修。
- 觀察與判準分開驗:
  - 正確性 F2 的現象屬實(settle 對 pass 紀錄直接回「已轉正」),它的判準「錯的是提示句」也對——只改提示,沒讓 settle 去改寫已 pass 的紀錄。
  - 架構對齊 F2 的現象屬實,但它給的重現其實是「同名時漏列」;修法照它的判準改走 build_typed_index,並把猜不準的另列一項(不是照舊不列),回歸測試 ⑤ 分得出修前修後。
  - 外家 F8(開關提醒只在接線後才印)與架構對齊 F1(閘提醒的呈現位置)一起處理:閘提醒搬到 doctor 開頭、一律印;c1–c5 的發現留在 Z 段。
  - 資安 F1(開關讀推送頂端的設定)是威脅模型本來就接受的「防疏忽不防繞過」,折法是寫進 Systems/存量漂移守衛 的 RULE 行並附撤除條件。
  - 併發 F2(表態檔沒跟治理帳共用鎖)已在 Issue 揭露;折法是表態追加改拿筆記庫寫入鎖。
  - 圖譜一致 F1(--probes 是死參數)拿掉旗標,乙做的時候再加。
- refuted 無;accepted 無。
