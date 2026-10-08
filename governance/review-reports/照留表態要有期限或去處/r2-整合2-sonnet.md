severity: major

鏡頭:整合與知識同步(三個月後接手者視角)。對照碼:/Users/enzo/harness/lumos-b1(HEAD 40262dff)。

## 固定席(計劃牽連的合約/事故節點)
派工時沒有 hook 附上牽連節點,我自己查了 Systems/存量漂移守衛(無 ★INVARIANT★ 合約行)與 Projects/存量漂移防線_計劃 的 [S3]:
- 存量漂移防線_計劃 [S3](`[test:t_drift_ack_binds_path_text_kind]`,綁 c1)宣稱表態「同一路徑同一原文同一種類時不再擋」,沒寫期限。本案讓 probe/retire 的表態在 scan 會到期,這句對 probe/retire 不再全稱成立;測試綁的是 c1,所以不會翻紅,但句子變成半錯(見 F4)。判:不破壞合約,但留下過期句。

## F1 呼叫點清單名稱不準也不全:push 路徑沒有叫 cmd_drift_check 的 probe 路徑
severity: minor
blocking: 否 判準:實作者讀 spec 找不到要改的那一行,但 grep 就找得到,不會造成錯誤行為。
spec 做法第 7 點。
引句:「呼叫端:`cmd_drift_check` 的 probe 路徑、`_drift_retire_guarded` 不傳 today」
問題:
- `cmd_drift_check` 沒有獨立的 probe 路徑。probe 與 c1-c5 的發現一起從 `_drift_check_core` 出來,在 `_drift_check_c` 裡用同一組 `_drift_split_acked(must, acks, vault_rel)` 與 `_drift_split_acked(listed, …)` 扣表態(file: `scripts/lumos:35741-35743`)。status_of 要在那裡建 tenv(`_drift_check_c` 手上沒有 tenv,核心的 tenv 是 `_drift_check_core` 內部變數,file: `scripts/lumos:32719`),spec 只說「核心路徑…才建一次」,沒說建在 `_drift_check_c`。
- `_drift_split_acked` 還有三個 spec 沒列的呼叫點:m1 回報(file: `scripts/lumos:36672-36673`)、`cmd_drift_scan`(36739,有列)、doctor Z 段(file: `scripts/lumos:36801`)。新簽名 `today=None` 的預設語意是「推送模式」,doctor 與 m1 都會落進推送模式;它們現在只處理 c1-c6 與 m1 發現,不受影響,但 spec 沒寫這個結論,三個月後有人把 probe 發現接進 doctor 就會悄悄變成「照留永不到期」。
- m1 遞迴分支(file: `scripts/lumos:34381-34382`)重呼叫 `_drift_split_acked` 時沒轉傳新參數;混有 m1 與其他種類的清單,非 m1 那半會丟掉 today/status_of。現況 scan 不含 m1、push 的 m1 單獨一份,所以不會出事,但屬於改簽名必漏的點。
具體例:只照 spec 改 `cmd_drift_check`(找不到那條路徑),`_drift_check_c` 沒改 → S6 測試對「born_now 沒綁去處仍放行」翻不紅。
建議:做法第 7 點改寫成「呼叫端:`_drift_check_c`(帶 born_now 與 status_of)、`_drift_retire_guarded`;doctor、m1 報告維持不傳,並寫明理由」,m1 遞迴轉傳。

## F2 「新寫就成立」在推送模式的失效原因與 prev_ack 內容沒定義,gate 路徑有未規格化分支
severity: major
blocking: 是 判準:S6 要的「照擋並印提示」在推送模式缺必要資料來源,實作各自發明,而且這是擋推送的閘。
spec 做法第 3、5 點。
引句:「沒算上、但有同鍵照留的發現帶 `prev_ack={reason, dead}`(取 seq 或檔內順序最後一筆)」
問題:
- `_drift_ack_live(a, today, status_of)` 需要 today(沒綁去處那支用期限);推送模式「不傳 today」。所以 born_now 發現遇到(a)一筆沒綁去處的照留、(b)一筆綁了但那篇已收尾或不在的照留時,`dead` 字串由誰產生沒寫:(b) 的原因文字在 `_drift_ack_live` 的 tracked_in 分支裡,但推送模式不能整支呼叫(會走到期限分支或需要 today);(a) 的「沒綁去處」原因根本不在第 3 點任何一條裡。
- 現行 `_drift_prev_ack_line` 一開頭就取 `pa["related"]`(file: `scripts/lumos:34455`),新形狀 `{reason, dead}` 沒有 related;spec 只說「對有 dead 的印…」,沒說沒有 related 也沒有 dead 的(推送模式 born_now 的情況)怎麼辦。實作者漏一個分支就是 KeyError 或印出 None。
- 這個函式在 `_drift_report_must` → `_drift_print_findings`(file: `scripts/lumos:35595`)裡呼叫,位於 `_drift_check_c` 內且沒包 try;例外往上丟,pre-push 掛鉤把「其他非零」當成「這次沒檢查」放行(file: `scripts/hooks/pre-push:474`)——也就是這個漏洞會讓整道閘靜默放行。
具體例:推送新寫 `REVISIT:[when-file:src/a.py] 排程中`(src/a.py 已在)+ 同推送補裸 `drift ack --kind probe`(寫 until)。spec 5 第一點:born_now 不認裸照留 → 發現留在 must,同鍵有照留 → 帶 prev_ack;dead=? → 無定義。
建議:推送模式另寫一條明文規則:born_now 且有同鍵照留卻沒算上 → `prev_ack={reason, dead}`,dead 固定兩種字串(「沒綁去處」/ 從 status_of 取的「綁的 X 已收尾…」),`_drift_ack_live` 拆出只看 tracked_in 的內層函式讓兩邊共用;`_drift_prev_ack_line` 分三種形狀(related、dead、都沒有)並各加一支測試。

## F3 到期後「重新列出」沒有任何自動出口:scan 沒人定期跑,doctor 與 CI 都不看 probe/retire 照留
severity: major
blocking: 是 判準:本案要修的就是「照留等於永久消音」,到期後仍要靠人想到才會重新出現,修的是帳面、不是行為。
spec 白話段與天花板第 2 點。
引句:「要嘛不說,30 天後自動失效、重新列。」
問題:找 `drift scan` 的呼叫者:hooks、CI(file: `.github/workflows/ci.yml:216-242` 只跑 drift check)、doctor(Z 段 `_drift_doctor_lines` 只用 `_drift_state_findings`,file: `scripts/lumos:36801`,不評估 when-* 條件)、技能與 INDEX 的文字說明,全都是「人想到才跑」。所以到期的照留不會出現在任何自動畫面上;推送檢查又照 spec 刻意不看日期。「重新列」的唯一時機是有人手動跑 scan。天花板 2 講了「每月出現一次」,沒講這一次也要有人去跑。
具體例:rtb 11 筆舊照留 2026-11-05 到期,沒有人跑 scan → 2027-01-05 RETIRE-IF 量測日時,檔案裡一筆都沒變,量法(數「連續兩筆以上的裸照留」)得到 0,會被誤判成「期限有效、沒人再貼」。
建議:至少讓 doctor Z 段只讀表態檔、數「已過期限、或綁的那篇已收尾的 probe/retire 照留」幾筆(不評估條件,符合既有「doctor 不評估 when-*」決定,只讀 acks 與筆記狀態);或把 RETIRE-IF 的量法改成同時要求 scan 在量測日前被跑過。三選一,spec 要明講選哪個。

## F4 同步清單漏了既有句子與印出點,且「指令照貼」與固定句有一處會直接錯
severity: minor
blocking: 否 判準:都是文字與提示不一致,不影響判定;其中一處照貼會 rc2,但屬提示文字、不是閘行為。
spec 範圍與做法第 8、9 點。
引句:「改法提示與說明:`_drift_fix_hint` 的 probe/retire 兩句、`drift check` 擋下時印的照留指令」
問題(逐點,均已開檔驗):
1. `drift check` 擋下時印指令有兩處:`_drift_report_must` 對所有種類印同一個模板 `--kind {k}`(file: `scripts/lumos:35768-35771`,c1-c5、probe 共用),`_drift_retire_print` 另印一條 retire(file: `scripts/lumos:35722`)。`--tracked-in` 只收 probe/retire(做法第 2 點,其他種類 rc2),所以 35771 不能整個模板加旗標,要按種類分;spec 只寫一句,沒點出這個陷阱。
2. spec 沒列的第三處 probe 照留文字:`_drift_fix_args_err` 對 `--kind probe` 的錯誤訊息「照留就 lumos drift ack … --kind probe --reason …」(file: `scripts/lumos:34819-34820`)。測試 `drift fix --kind probe` 只斷言含 drift ack(test_lumos.py:61176),不會翻紅,但文字會跟新規則不一致。
3. 掛鉤與 CI 的逃生文字:`scripts/hooks/pre-push:483`、`.github/workflows/ci.yml:242` 都寫「lumos drift ack 表態照留」,同屬 Systems/存量漂移守衛的 about_code。若改了 `scripts/hooks/pre-push`,CHANGELOG 慣例(v1.1、v1.2 都寫「掛鉤跟著改,所以升版,讓還沒更新的專案被提示 lumos update」)要求評估升版;spec 沒講改不改這兩處、要不要升版。又本案是閘收緊加消費專案集體到期(rtb 11 筆),版本與 CHANGELOG 沒提。
4. `_drift_fix_hint` 只收 (kind, path, line, names),拿不到發現是不是 born_now(file: `scripts/lumos:34685`);做法第 8 點與範圍 34 行要「推送新寫就成立的改法提示直接寫照留要帶 --tracked-in」,簽名沒說怎麼改(`_drift_hint_key` 去重鍵也要加)。最省的做法是 probe/retire 句子一律講兩種寫法,但那就不是「直接寫」。另外 36835 行用 `[0]` 取第一條提示當例子,若新增第二條字串會改變例句,測試 32538、32627 同類(c6、c3,不受影響)。
5. doctor Z 的通用 advice(file: `scripts/lumos:2674`)講「某一行確定照留就表態」,不用改,但三個月後的人會問為什麼沒改,spec 該寫一句「不改」。
6. 技能面:`skills/lumos-project-notes/SKILL.md:78` 也提到 drift ack(只說「照它印的指令處理」,可以不改);`commands/04-自檢與健康.md` 第 13 列是要改的那一列(已核對存在),`commands/03-寫回圖譜.md:52` 是第二處。spec 說「兩處」與實際相符,但沒寫 SKILL.md:78 的結論。README 與 assets/drift-guard-zh.svg 沒有「照留」字樣(已 grep),不用動。
建議:同步清單改成逐檔逐函式表(含上面 1-5 點),並把升版與否寫成明確決定。

## F5 舊句修訂不夠:Systems 要改的是既有句,不只新增;防線計劃 [S3] 需註記
severity: minor
blocking: 否 判準:知識圖譜內部不一致,下一個接手者可能以舊句為準,但不影響行為。
spec 做法第 9 點。
引句:「寫回 [[Systems/存量漂移守衛]]:照留失效規則、兩個新欄位、推送不看日期的理由」
問題:Systems/存量漂移守衛現有三處會跟新行為矛盾,spec 只說「寫回」(新增),沒說修改:第 38、39 行的 WHY 寫「已表態的照 scan 慣例列在已表態」(沒有期限前提);第 122 行指令說明 `lumos drift ack <節點> <行號> --kind <種類> --reason "…"`,「提交進去才算;那一行一改就失效」沒提 30 天與 `--tracked-in`;frontmatter 的 responsibility 沒提表態期限判斷歸誰。Projects/存量漂移防線_計劃 [S3] 與第 68 行也寫成永久有效。依專案規則,PITFALL/WHY 行寫回要帶 `[出處:]` 等鍵、舊句不能留成「程式說了算」的線索卻被當事實。
建議:做法第 9 點列出要改的現有行號(或「全文搜 表態 逐一對照」),並在防線計劃 [S3] 加「probe/retire 見本案」註記。

## F6 綁定的計劃收尾時,收尾連帶清單不提醒「N 筆照留跟著失效」
severity: minor
blocking: 否 判準:資訊缺口,不影響判定,最壞是人晚一步發現。
spec 範圍與做法第 1-3 點(未提)。
問題:c2/c3/c6 的照留綁「當時連著的已收尾計劃」,計劃收尾時 `lumos set … done` 會當場列連帶待辦;本案的 probe/retire 照留綁一篇計劃,那篇收尾時沒有任何輸出講「有 N 筆照留綁在這篇、現在失效」。結果是計劃一結,照留靜默變死,要等 F3 說的 scan 才看到。spec 沒寫這是刻意不做還是遺漏。
具體例:`Projects/X_計劃` 被三筆 probe 照留的 `--tracked-in` 綁著;`lumos set Projects/X_計劃 status done` 輸出沒提三筆。
建議:範圍「不做」加一行明講,或在收尾連帶列出時掃表態檔(只讀、算 `tracked_in` 等於這篇的)。

## 已查證且成立的宣稱(無 finding)
- 「考試與歷史重放不扣表態」成立:`_drift_check_core` 只有四個呼叫者——`_drift_check_c`(推送,有扣)、考試兩處(file: `scripts/lumos:36960`、`36991`)、歷史重放(file: `scripts/lumos:37150`),後三處都只讀 must/listed 的種類、路徑、行號算分,不碰表態檔。born_now 是多一個鍵,不改這些計分。spec 內「先 grep 確認」是未完成的動作字樣,已完成,應從 spec 拿掉改寫成結論。
- `_DRIFT_OPEN_ISSUE`(open、doing)、`_DRIFT_CLOSED`(done、superseded)、`_STATUS_ENUM["project"]`(todo、doing、done、superseded)都存在且內容與 spec 相符;`_drift_str`、`_note_unreadable`、`_drift_probe_old`/`_drift_probe_judge`/`_drift_prev_ack_line`/`_drift_split_acked` 皆在。PRIOR-ART 提到沿用 `split_frontmatter`/`parse_frontmatter`,但做法第 4 點說不另解析;兩者不衝突(沿用的是 env 內既有解析),只是 PRIOR-ART 字面容易讓人以為新碼要呼叫它們。
- 2026-10-06 + 30 天 = 2026-11-05 算術正確;REVISIT 2026-11-06 的日期與 [S5] 一致。
- 既有測試會不會翻紅:搜了所有對 probe/retire 做 `drift ack` 的測試(test_lumos.py:32013、32025、32163、32331、57724、58496、58498),都是先「既有條件成立」或只做 scan/表態、不是「新寫就成立+裸照留+check」;31956-32012 的 `check` 斷言只認字串前綴 `lumos drift ack <節點> <行號> --kind retire`,即使加了 `--tracked-in` 也還含它。所以收緊不會翻既有測試;唯一的時間地雷是 2026-11-05 之後,手寫無 until 的 probe/retire 表態會失效——現有測試沒有這種(已 grep),新 [S5] 測試要用固定日期參數,不能讀今天。
- 消費專案舊版讀新欄位:`_drift_load_acks` 只過濾 `path` 與 `kind`(file: `scripts/lumos:34353-34369`),多出的 `until`、`tracked_in` 原樣忽略,舊版把所有照留當永久有效 = spec 回退段寫的放寬,成立。新版讀舊表態走 legacy 寬限,也成立。推送起點算不出來走既有「判不了」分支,不碰本案。
- 空樹起點:`_push_range_start` 在「找不到主線或沒有共同祖先」且舊值全 0 時從空樹算(file: `scripts/lumos:41671` 起),不只是「全新 repo」;天花板 4 說的「全新 repo 的第一次推送」略窄,但在所有路徑下結論一致(照留都要綁去處),不另標。

## 實務隱患逐類
- 時區/日期:已讀,無 finding(期限只在 scan、推送不看日期;已核對 push 路徑不傳 today)。
- 並行會談/兩工作樹各自追加表態:已讀,無 finding(同鍵多筆取任一筆活著;seq 排序沿用既有)。
- 回退:已讀,無 finding(表態檔只追加、舊版忽略新欄位)。
- 效能:已讀,無 finding(推送時只有 born_now 且有同鍵 tracked_in 才多建一次 tenv)。

最嚴重 severity: major;blocking 2 條(F2、F3)。
