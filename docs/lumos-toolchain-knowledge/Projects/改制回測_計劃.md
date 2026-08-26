---
type: project
summary: |-
  FLAG:TECHNICAL
  KEY:地基盤點第 3 批案 C——08-25 收斂制大改(處置閘/d5 記帳)至今無回測基建:[S1] 回放 runner(判定核心抽純函式共用+readonly 不落帳;差異三分類:邏輯漂移紅/帳集合變化分長大與被動/制度版本過期指路重凍)[S2] 判定檔=完整輸入閉包(帳列逐行 sha+spec sha+engine_rev)入 governance/replay/(不混 golden/ 散文語料);凍結併入收斂流程,重凍走 anchor approve 模式留痕[S3] 新舊制同料對照:形狀先分類(單 carrier 可比/多席 rc2 不可比/無 carrier 必 FAIL),產物=圖譜驗證紀錄非裸檔[S4] 週跑=新凍結必跑+存量輪替抽 5 包,預算 5 分鐘,build_message 帶重查指令(r1 折入:2026-08-26 五席+外家 19 條全數有去向)
  DEP:[[Systems/design-loop]]｜[[Systems/loop-convergence-recording]]｜[[Projects/地基盤點2026-08-26_調研]]
status: doing
created: 2026-08-26
updated: 2026-08-26
tags:
  - type/project
  - status/doing
---

# 改制回測_計劃

> 白話:昨天把收斂判準整組換掉(處置閘),證據只有「上線當天十個迴圈跑得過」。這案把「重算一遍還是同樣判定嗎」變成可以每週自動問的問題:帳、報告、spec 的雜湊全部凍進判定檔(輸入閉包),判定是純讀側決定論——回放器對凍結輸入重算一輪,跟存好的標準答案比;差異還要分清楚是「邏輯壞了」「帳被動了」還是「世界正常往前走」,只有前兩種喊人。

PRIOR-ART: borrow——golden master testing(凍結輸出當標準答案,重算比對)是回歸測試教科書做法;決定論讀側重放=事件溯源(event sourcing)的 replay 慣例;governance/golden/ 已有 30 包快照素材與單次重放先例(2026-07-16)——但要講清楚:07-16 那次是「LLM 校準重放」(釘 worktree 派審計員重審,測模型判斷力),本案是「決定論算式重放」(讀凍結帳重算四合取,測程式與資料完整性),同名不同物;CLI 層的 golden 比對基建(存檔、比對、rc 語意)是本案新建,不是既有機制加個排程。

## 現況事實

- 處置閘判定=純讀側(canary 帳列+報告檔 sha+快照),`loop status --disposal` 決定論可重算;今日已收斂迴圈 10+ 個,素材齊(governance/review-reports/<loop>/ 各輪快照與報告全凍結入版控)。
- golden/ 30 包只有 {spec,findings} 散文快照,無判定檔、無 runner、無排程;歷史僅 2026-07-16 人工重放一次。
- 舊制 panel 迴圈的帳仍在(replay-only 通道活著),但從未被拿來與新制同料對照。

## 條款

- **[S1] 回放 runner**:`lumos loop replay <id> --golden <檔>`(回放模式,不需 --spec——spec sha 用閉包裡凍結的那份)/`lumos loop replay <id> --freeze --spec <計劃.md>`(凍結模式,--spec 必帶;帳裡沒有 spec 路徑欄,凍結當下由操作者給)。判定核心從 `_loop_status_disposal` 抽成純函式(給定帳列集+spec sha+repo 根→四合取結果),live 路徑與 replay 共用同一份(單一實作鐵則——另刻一份就正好違背「證明判定邏輯沒被改壞」的目的);replay 走 readonly:不呼叫 `_loop_gov_mark`、治理帳零寫入(現有 PASS 分支是無條件落帳、11 個呼叫點無「只算不寫」先例,所以 readonly 是新參數,fixture 釘「replay 前後治理帳行數不變」)。舊制迴圈(panel 定錨)自動走 --gate --panel 回放語意。輸出判定摘要 JSON;與 golden 比對時差異分三類白話列:①對凍結閉包重算≠golden 記載判定=**邏輯漂移**(紅,rc1)②live 帳篩 loop==id 的集合≠凍結集合——凍結列被改/刪=**帳被動**(紅,rc1);僅多出新列=**帳本長大**(列出,不紅——同 loop_id 事後合法追加輪次是常態)③closure 的 engine_rev≠當前制度版本=**golden 過期**(列出,不紅,指路重凍)。
- **[S2] golden 判定檔=完整輸入閉包**:`--freeze` 產 `governance/replay/<id>/verdict.json`(新目錄——golden/ 定義上是 LLM 校準用散文語料且從無機器格式檔,判定檔另立目錄不混語意;golden/ 不動)。內容:loop_id、判定輪 round id、該輪帳列逐行原文+逐行 sha256(排序集合,順序無關——共用帳本其他 loop 交錯寫入不影響)、spec sha(=窗末 result_sha256)、各席 report/snapshot path+sha、engine_rev(程式內制度版本常數,d5 判定語意改版就 bump)、凍結時間。首批=08-25 後全部 d5 迴圈(含本日十餘個);此後凍結併入收斂流程(gate PASS 後跑 --freeze),週跑另補漏(已收斂未凍結的自動凍)——「首批之後誰入庫」不留空白。重凍(制度合法演進後 golden 過期時)比照 anchor approve:`--freeze --note <理由>` 理由必填、寫治理帳留痕、舊 verdict 改名 `verdict-<日期>.json` 存檔不回改。
- **[S3] 新舊制同料對照(一次性分析)**:取 2026-08-06~08-25 間 panel 定錨迴圈,先按帳形狀分類——(a) 單席帶處置集合=d5 可比,跑四合取記「卡哪一關」(b) 多席各自帶處置集合=d5 結構性拒判(rc2「一輪只能有一筆」),記「形狀不可比」與原因,不硬折 (c) 無任何處置集合=②無處置帳必 FAIL,記為確定結果。可比的才進兩制對照(panel 語意 vs d5 語意/收斂輪次差);產物=圖譜驗證紀錄 `Verification/2026-08-26_新舊制同料對照_v0.md`(比照 07-16 校準紀錄同款容器,valid_under/revalidate_when 齊)——不放 governance/ 裸檔(golden/ 根目錄從無裸檔先例,且「分析產物+結論」本來就歸圖譜);結論寫回 [[Systems/design-loop]](給 08-25 改制補上遲到的對照證據)。
- **[S4] 週期接線**:autonomous-loop 週跑,範圍=**新凍結(從未回放過的)必跑+存量輪替抽樣每週 5 包**(輪完一圈重來)——不是全量:golden 只增不減,全量成本無上界,先驗過再說。首跑量測單包 wall time 記進驗證紀錄;總預算 5 分鐘,超時截斷並在通知講「本週跑了幾包/略過幾包」;升級全量的機械條件=實測「單包耗時×存量」≤60 秒。通知走 run_exam 家族 `build_message('regime-replay', MSG, None)`(不用 build_alert——那是「連兩天管線死」級素警示,週期任務家族三支全用 build_message);MSG 規格=哪個 loop、哪類差異(邏輯漂移/帳被動/golden 過期)、重查指令一行(`lumos loop replay <id> --golden governance/replay/<id>/verdict.json`)。fail-open 不阻斷主流程。
- 邊界:不改判定邏輯本身;verdict=判定快照非帳(帳不可撤原則不變);重凍走留痕路徑、歷史 verdict 不回改;replay 唯讀(fixture 釘);制度演進≠漂移(engine_rev 分流,不喊人只指路);舊制對照是分析非裁決。

## 行為斷言

replay 對今日任一已收斂 loop=判定與當日 gate 輸出一致且治理帳行數不變;--freeze 產檔含完整閉包(帳列逐行 sha+spec sha+engine_rev);竄改凍結列(fixture)→rc1 標「帳被動」;同 loop_id 追加新列(fixture)→列「帳本長大」不紅;engine_rev 不符(fixture)→列「golden 過期」不紅;spec 檔事後被編輯→回放不受影響(G3 用凍結 sha);舊制 loop 走 panel 語意不誤用 d5;多席各自帳形狀→S3 記「不可比」不炸;週跑 wrapper 在 replay/ 空時跳過不炸。

## 實務隱患

- 守衛面:runner 唯讀不進閘(advisory);週跑漂移=喊人不擋。對外送出:僅 LINE 喊人,走 build_message('regime-replay') 模板(與週期任務家族一致),測試打樁。已排除:金流/不可逆。
- 誠實邊界:回放證的是「同輸入同判定+凍結帳未被動」=真帳整合回歸,不證判定正確(正確性歸當時審查)——golden 由同一份邏輯 --freeze 自產,不是獨立 oracle,本案不宣稱「判定正確性回測」;[S3] 對照受「舊帳欄位語意與 d5 不全同構」限制,對不上的欄位與形狀明列「不可比」不硬折。
- 回頭條件:週跑首月(至 2026-09-26)若「帳本長大」類列出佔比>一半=閉包邊界劃太窄(追加輪次太常見),重審凍結時機;engine_rev 首次 bump 時,重凍流程要真走一遍並留痕,走不通=本案 S2 設計失敗,開 Issue。

## 審計修正紀錄

- r1(2026-08-26,五席+外家,19 條全數有去向零放行——含外家 1 條「否決不成立」附限定,以誠實邊界折入;5+2+4+5+3 逐席機械數):
  - s1-f1/f2/f4+s2-f2+s3-f1(輸入閉包未定義,3 blocker 2 major)→ S2 重寫:verdict=完整閉包(帳列逐行 sha 排序集+spec sha+engine_rev),回放對閉包重算,live 差異三分類(邏輯漂移/帳被動/帳本長大)。
  - s1-f3(blocker:CLI 無 --spec、帳無 spec 路徑欄,照字面跑不動)→ S1 拆兩模式:--freeze 必帶 --spec,回放模式用凍結 sha 不需 spec。
  - s1-f5+arch-f1(唯讀宣稱 vs 算=寫耦合,2 major)→ S1 明文:抽純判定核心共用(不開第二份實作)+readonly 參數,fixture 釘治理帳零寫入。
  - s3-f3+ext-f2(golden 合法過期無重凍路徑,blocker+major)→ engine_rev 分流+重凍比照 anchor approve 留痕。
  - s3-f2(首批後入庫空白,major)→ 凍結併入收斂流程+週跑補漏。
  - ext-f3+s3-f4+arch-f5(週跑成本無界+通知無內容規格+build_alert 錯用,2 major+minor)→ S4 重寫:新凍結必跑+輪替抽 5 包+5 分鐘預算+build_message 帶重查指令。
  - s2-f1(panel 多席形狀 rc2 拒判,major)→ S3 加形狀分類,不可比明列。
  - arch-f2/f3(golden/ 語意污染+裸檔違圖譜鐵則,2 major)→ 機器檔改 governance/replay/ 新目錄;對照產物改圖譜驗證紀錄。
  - arch-f4(PRIOR-ART 講小新穎度,minor)→ 補「07-16=LLM 校準重放,本案=決定論重放,基建新建非延伸」。
  - ext-f1(否決不成立但附限定)→ 誠實邊界補「golden 自產非獨立 oracle,不宣稱正確性回測」。
  - refcheck 備註:arch 席引 `governance/golden/regime-comparison-2026-08.md` 為 missing——該路徑是原 spec 規劃要新建的檔(本就不存在),非壞引用;折入後該產物已改為圖譜驗證紀錄。
