severity: major

# 回滾與時間鏡頭審查:照留表態要有期限或去處

## 範圍、做法、驗收條款各節
已逐節讀完。固定席(派工附的合約/事故節點):hook 沒有附節點給我;我自己查,只有 `_drift_load_acks` 對表態檔「多出來的鍵忽略」這一條行為與本案有關,判「不影響退回」,理由見 F4。

## F1 判斷用「今天」而不是被判斷那個提交的時間,同一提交會今天綠明天紅
severity: major
blocking: 是——主線後盾(CI 的 drift check)會在沒人改任何東西時變紅,屬行為缺口。
spec 段落:〈做法〉3(`今天(本機日期)晚於期限`)、〈範圍〉第 2 條、〈實務隱患〉「日期取本機」。
引句:「今天(本機日期)晚於期限 → 「已過期限 YYYY-MM-DD」」
問題:推送檢查與 CI 讀的是「被推送頂端提交」的表態檔與節點(`_drift_load_acks(root, tip)`,file: `/Users/enzo/harness/lumos-b1/scripts/lumos:35667`、`:36671`),但失效判斷用執行當下的時鐘。CI 觸發是 push 與 pull_request(file: `/Users/enzo/harness/lumos-b1/.github/workflows/ci.yml` 的 on 區段,用 grep 看到 push: main、pull_request),都帶 `--diff BEFORE..SHA`(`lumos:239` 附近),重跑 CI 或在長壽命 PR 上再推一次,都會用新的「今天」重判同一段 diff。
具體例:10-20 推一個新寫就成立的 retire 條件,補一筆舊格式照留(legacy,11-06 前有效)→ 當日綠。11-08 按「Re-run jobs」→ 同一提交、同一棵樹,legacy 已失效 → born_now 發現沒有綁去處的有效照留 → 擋下 rc1,CI 紅。沒有任何人改程式或筆記。同理 `--tracked-in` 以外的 `until` 照留:day 31 重跑就紅。
另:`lumos` 內沒有任何「今天」覆寫機制(`grep LUMOS_TODAY|LUMOS_NOW` 無結果),所以歷史重放(`governance/replay/*` 考卷)與測試都無法固定時鐘。
spec 把時間風險只當作「時區差一天」,沒碰到「重判舊提交」這條路。
處理方向(給作者判,我不收尾):期限比對基準改成頂端提交的 committer 日期(重跑與重放結果不變),本機未提交的 scan 才用今天;同時加一個可注入的今天(環境變數)讓測試與重放能固定。

## F2 2026-11-06 常數:上線日期寫死,晚上線就當天全部失效;日數也對不上
severity: major
blocking: 是——常數決定了舊表態在哪天集體失效,算錯或上線延後會直接讓 rtb 等消費專案的推送當天被擋。
spec 段落:〈範圍〉第 2 條與〈做法〉1。
引句:「舊表態(兩個欄位都沒有)在 2026-11-06(上線日 +30 天)以前照舊全部有效」
問題一:`_DRIFT_ACK_LEGACY_UNTIL = "2026-11-06"` 是原始碼常數,不是上線日算出來的。spec 建立日 10-06,10-06 + 30 天 = 11-05,不是 11-06;而比較用「晚於」,最後有效日是 11-06、11-07 才失效,實際是上線後 31 到 32 天。數字與「+30 天」矛盾。
問題二:若實作或審查拖過 11-06(此 spec 還在 design loop,尚未實作),合併當天所有舊 probe/retire 照留立刻全部失效,「從上線日起算 30 天」的裁定(Enzo 2026-10-06)失效,寬限期變 0 天。沒有條款檢查這點。
問題三:2026-11-06 當天會發生什麼:前一天所有 legacy 有效;11-07 起,凡是推送內含「新寫就成立」的行、或 drift scan 都會一次翻出 rtb 11 筆(spec 已承認)。但 F1 的重跑問題讓「11-07 前綠過的推送」也在重跑時紅。
問題四:測試 `t_drift_ack_routed_legacy`(S3)要驗「期限前有效」,沒有時鐘覆寫就只能寫死日期或 monkeypatch `date.today`;寫死的話 11-07 起全套測試、也就是推送前的閘(約 3700 案例)會突然紅,不是人改的。同樣,既有測試夾具裡凡有 probe/retire 的舊格式照留(例如 file: `/Users/enzo/harness/lumos-b1/scripts/test_lumos.py:32157` 附近的 drift scan 案例「已表態的不算要處理」)在 11-07 起會從已表態掉進要處理而翻紅。spec 驗收條款沒要求測試固定時鐘。
處理方向:常數改成「首次部署日 + 30」且讀自提交進版的檔案,或乾脆把 legacy 期限改成 ack 紀錄自己的 `date` 欄位 + 30 天(`cmd_drift_ack` 已寫 `date`,file: `lumos:34553`),就沒有全域懸崖;測試走注入時鐘。

## F3 時區那條隱患方向講反:CI 偏晚時是放行不是多列
severity: minor
blocking: 否——只影響邊界那一天,但 spec 寫的結論與實際方向相反,應改正文字。
spec 段落:〈實務隱患〉「日期取本機」。
引句:「只差邊界那一天,影響是多列一筆(不是放行),接受。」
問題:台北凌晨 0–8 點,本機日期 = D,UTC 日期 = D−1。期限 `until = D−1+…` 的最後一天:本機判「晚於」→ 失效、擋;CI(UTC)判還有效 → 放行。所以本機擋、CI 放行,CI 這個「後盾」在邊界日比本機寬鬆,恰好是「不是放行」的反面。反向(CI 時區在本機後面時)同理本機放、CI 擋。對 born_now 的推送檢查,這是放行 vs 擋下的差別,不是多列一行。
具體例:`until=2026-11-20`,本機台北 11-21 01:00:推送被擋;改在 UTC 11-20 的 CI 重跑:放行。
(若採 F1 的處理方向,以提交日期為基準,這條也一併消失。)

## F4 回退節:退回提交的說法對,但缺「退回後再前進」與「表態寫入端」兩個缺口
severity: minor
blocking: 否——舊程式讀得懂新紀錄,資料不會壞;缺的是退回後的沉默放寬,屬可接受但應寫下。
spec 段落:〈回退〉。
引句:「表態檔的新欄位舊程式不讀(多出來的鍵忽略),舊程式照舊把所有照留當永久有效」
驗證:`_drift_load_acks` 只要求 `path` 與 `kind`,其餘鍵原樣丟給 `_drift_split_acked`,probe/retire 不在 `_DRIFT_BOUND_KINDS` 走 `keys.add` 分支(file: `/Users/enzo/harness/lumos-b1/scripts/lumos:34353`、`:34384`),新欄位確實被忽略,舊程式不會崩。「不影響」。
缺口:(a) 退回後新欄位那些「綁了去處」的照留變成永久消音,等於把使用者原本設的「那篇收尾就失效」靜默放寬,spec 沒寫退回期間的這個後果,也沒寫退回後再上線時是否重算 legacy(依 F2,已過 11-06 就全失效)。(b) 退回發生在已寫入帶 `until` 的紀錄之後再上線新版本,舊紀錄的 `until` 仍有效,沒問題。(c) 回退節沒提 `drift ack` 新旗標被腳本或文件呼叫的情形(`--tracked-in` 在舊版 argparse 報 unrecognized,rc2),退回後依賴新旗標的操作手冊會失敗,屬小事。

## F5 兩個工作樹各自追加表態:缺合併規則,同日多筆與「最新一筆」未定義
severity: minor
blocking: 否——不會放行錯誤的東西,只影響失效理由顯示與衝突處理。
spec 段落:〈做法〉4(`dead_ack` 取最新一筆)、〈範圍〉不做「表態檔只追加」。
引句:「沒算上的發現若有對得上(同路徑同原文同種類)的照留,帶 `dead_ack={reason, why}`(取最新一筆)」
問題:probe/retire 的表態沒有 `seq`(只有 c2/c3 有,`_drift_ack_seq` 在 `lumos:34413`),只有日粒度的 `date` 與檔案順序。兩個工作樹各自追加後合併:`governance/drift-acks.jsonl` 沒設 merge=union(`git check-attr merge -- governance` 回 unspecified),兩邊都在檔尾追加會產生文字衝突,這是既有行為但本案提高了追加頻率(到期重貼)。解衝突後順序任意,「最新」可能選到舊的。更實質的:同一發現有「一筆綁去處(已失效)」與「一筆 legacy(11-06 前還有效)」並存時,spec 的 born_now 規則是「有 tracked_in 且未失效,或未失效的 legacy」,legacy 那筆仍讓它放行,使用者剛綁了去處而去處已收尾,仍被舊的 legacy 蓋過放行,直到 11-06。spec 沒寫兩者並存誰優先。
具體例:工作樹 A 對 X 補 `--tracked-in Issue1`(之後 Issue1 結案),工作樹 B 沒動;合併後 legacy 紀錄與 A 的紀錄並存 → X 在 11-06 前仍判已表態,A 的「結案就失效」沒生效。
處理方向:規定同鍵多筆時以綁去處的那筆(最新 date、同日取檔案後者)為準,蓋過 legacy。

## F6 `until` 沒有上限與壞時鐘防護
severity: minor
blocking: 否——寫入端本機時鐘錯誤只讓自己的紀錄偏差,但 spec 稱「固定 30 天」、不可選天數,實際取決於本機時鐘。
spec 段落:〈做法〉2。
引句:「沒帶就記 `until` = 今天 + 30 天」
問題:`until` 由 `date.today()` 算(同 `lumos:34553`),本機時鐘快一年則 `until` 變一年後;時鐘慢則剛寫就過期。判斷端只驗格式,不驗「`until` 不得晚於(紀錄 `date` + 30)」。表態檔是可手改的 JSONL,手寫 `until: 2099-01-01` 也永久有效,等於 `--until` 繞回來,與「不做:讓 `--until` 可以自己選天數」矛盾。
處理方向:判斷時要求 `until − date ≤ 30`,或乾脆不存 `until`、只存 `date`,期限一律 `date + _DRIFT_ACK_DAYS` 算。這同時解 F2 的 legacy 常數問題。

## 實務隱患逐類(回滾與時間範圍)
- 時鐘/時區:有缺口,見 F1、F3、F6。
- 退回/回滾:資料向前相容,見 F4;靜默放寬那點需寫下。
- 重跑舊提交(CI re-run、PR 再推、歷史重放):有缺口,見 F1。
- 固定日期懸崖:見 F2。
- 多工作樹合併:見 F5。
- 並行鎖:`cmd_drift_ack` 寫入在 `_vault_write_lock` 內(`lumos:34570` 附近),同機並行沒問題;跨工作樹是 F5。無新 finding。

severity 總結:最高 major,blocking 2 條(F1、F2);minor 4 條(F3、F4、F5、F6)。
