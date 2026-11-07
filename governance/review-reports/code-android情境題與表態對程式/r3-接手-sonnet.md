severity: major

我在 `/tmp` 用真型錄搭一個最小 repo,實跑了推送前情境題。結果:證據樣式對不上只提醒、缺列擋、evidence 在段範圍外擋、`D-1` 選 `alt`(換列)擋,都照文件走。段放行後提醒消失,doctor 和 `code-loop check` 都印出新的 AI 放行計數。臨時目錄已用字面路徑刪掉,沒有改 repo。

## F1 重複記帳會灌水升擋條件的計數
severity: major
blocking: 是
引句:「REVISIT:2027-01-08 從治理帳數各列證據樣式提醒(scope kt-situation)經盲判或人工確認的真陽性與誤報;某一列真陽性至少 20 筆、誤報少於一成,才把那一列從提醒升成擋」
重現:同一個提交、同一份表態,先跑一次 `lumos code-loop check --diff HEAD~1..HEAD --at-sha <sha> --branch feat/sit`,再重跑三次。帳上 `gate: code-loop, kind: warned, scope: kt-situation` 同一組 seg 與列共 4 筆,沒有去重。
- 原因:`_kt_sit_reminder_lines` 每次核對都無條件寫一筆,pre-push、CI、手動 check 各算一次。
- 後果:文件要人去數「至少 20 筆」,但帳上筆數是核對次數,不是 (段,列) 數。
- 另一個隱憂:`warned` 事件不在 `_GOV_LOCAL_PAIRS`,會寫進受版控的 `docs/.governance-log.jsonl`。推送當下寫的事件是推送後才出現的未提交改動,升級依據的資料來源不可靠。
- 修法:REVISIT 與計劃寫明以 (seg,row) 去重計數,或寫帳時去重。

## F2 放行指令的確認訊息仍說「整段不核」
severity: minor
blocking: 否
引句:「WHY:情境題誤擋的出口是段放行,沿用新增告警閘的 lint-waive 與放行檔(指紋 kt-situation:<段身分>,理由門檻、origin、ack、doctor 計數全同一套);證據樣式提醒後面印好放行指令,有放行的段不再提醒並印 ⚠;缺段缺列照擋、不給放行出口」
重現:跑 `lumos lint-waive kt-situation:<seg> --rule kt-situation --file app/Screen.kt --note …`,輸出「已放行(情境段:推送前表態那一道整段不核)」。
- 該字串在 `scripts/lumos:39907`。人在終端互動時的確認提示也是「放行這個情境段(整段不核表態對程式)」,在 `scripts/lumos:39801`。
- 實際行為:放行後缺列照樣擋(我實測 `rc 1`,擋下「缺列 D-8」),只有證據提醒被關掉。
- 這兩處在人按 y 之前就講錯放行效力,屬舊說法殘留,本 diff 沒改到。

## F3 計劃的範圍 5 與 S4 還寫「整段放行」,跟新行為與同篇其他處矛盾
severity: minor
blocking: 否
引句:「- [S4] 當核對一段一列的三方票時,表態那一道 應 照多數決判:作者票與第一盲判票相同 應 放行」
- S4 後半寫「該段有段放行 應 整段放行(證據樣式不合也放)並印 ⚠」。範圍 5 的「原設計」也寫「範圍 3 的表態對程式(缺列、evidence、證據樣式)…都略過」。
- 同篇〈實務隱患〉已改成「只關掉那段的證據提醒、缺段缺列照擋」,所以計劃內部不一致。
- S4 綁的 `t_blind_judge_majority` 還沒實作,所以暫時沒有測試會紅。
- 範圍 5 還寫「擋下訊息印好這行」,現在是提醒印、擋下不印。

## F4 〈用詞〉證據樣式一條仍寫舊的放行與擋
severity: minor
blocking: 否
引句:「每列樣式附正例與反例,由規則包自檢經真的切段與核對程式跑過(正例放行、反例擋),壞寫法跟標準寫法只差在語意時那一段寫 `(無)`」
- 這句在計劃〈用詞〉的證據樣式條,diff 裡是未改動的上下文行。
- 改成只提醒之後,正例要對得上、反例要對不上才對。`check.py` 註解與規則包 WHY 都已更新,這句沒跟上。

## F5 依據來源網址的核對結果
severity: minor
blocking: 否
引句:「(https://kotlinlang.org/docs/classes.html#constructors )」
- Kotlin classes 頁沒有 `#constructors` 錨點,實際是 `#constructors-and-initializer-blocks` 和 `#primary-constructor`。
- 內容本身成立:帶註解或可見度修飾詞時要寫 `constructor`,頁面範例有 `class Person @Inject constructor(...)`。
- Semgrep policies 網址會 301 轉到 `docs.semgrep.dev/semgrep-code/policies`,內容仍在。頁面確有 Monitor、Comment、Block 三種模式。
- 該頁只暗示 Monitor、Comment、Block 的順序,沒有明說「新規則先 Monitor」,Monitor 的文字是「用來評估真陽性率」。
- 計劃與 `r2-intake.md` 寫成「官方建議」,措辭過頭。
- 本案實際做法是直接在本機印提醒(Comment 級)並同時記帳,沒有「先只記錄」的階段。
- ast-grep test-rule 的 valid/invalid 與 noisy/missing、Semgrep testing-rules 的 `ruleid:`/`ok:` 都核對成立。

## 其餘檢查的結論
- 逾時句子沒有舊說法殘留:棧別提問表態閘、計劃〈依據來源〉、程式註解都已改成照 `over_budget` 處理,搜不到「逾時 → 無法驗證擋下」的句子。
- 計劃綁的 `t_kt_situation_*` 測試名都存在。S3、S5、S6、S7 綁的盲判類測試名還不存在,是計劃本身寫明範圍 4、6、7 尚未實作,不算這一輪的問題。

總結:最嚴重是 F1 提醒帳重複寫入使升擋計數不可信(1 條 major),會擋 1 條。

主要檔案:
- `/Users/enzo/orca/workspaces/lumos-toolchain/android-situation-evidence/scripts/lumos`(39801、39907、`_kt_sit_reminder_lines`)
- `/Users/enzo/orca/workspaces/lumos-toolchain/android-situation-evidence/docs/lumos-toolchain-knowledge/Projects/Android寫法語意情境表態與盲判_計劃.md`
