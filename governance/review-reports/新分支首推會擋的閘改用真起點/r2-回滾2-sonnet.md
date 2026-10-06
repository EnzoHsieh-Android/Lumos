severity: major

# 第 2 版審查:回滾與時序鏡頭(Sonnet)

派工沒有附牽連的合約/事故節點,所以沒有固定席可逐條判;這份只對照程式碼現況。
實驗在 mktemp 的 clone 做(`/Users/enzo/harness/lumos-firstpush` 唯讀)。

## F1 守衛面說「功能分支推送時 CI 也跑 code-loop check」,跟 CI 設定不符
severity: major
blocking: 是——spec 拿一個不成立的後盾事實,來證明「掛鉤範圍變小」不會放鬆守衛。
spec 段落:實務隱患的「守衛面」、「標籤推送」兩條。
引句:「功能分支推送時 CI 也跑 code-loop check,對全零起點從跟主線的分岔點算」
引句:「發版標籤打在已推過、CI 跑過的提交上,接受;寫進天花板。」
問題:`.github/workflows/ci.yml:3-6` 的觸發只有 `push: branches: [main]` 與 `pull_request`。code-loop gate 那步(`.github/workflows/ci.yml:176`)條件是 `github.event_name == 'push'`。所以:
1. 新分支首推時 CI 根本不會對它跑 code-loop check;PR 事件也跳過這步。後盾只在合進 main 之後才跑,而且是事後(紅了程式已進主線)。
2. 標籤推送沒有任何 CI 觸發。「CI 跑過的提交」只有在標籤指到已在 main 上的提交時才成立。
具體例:新分支首推、範圍從空樹縮成分岔點之後,本機閘看到的內容變少;spec 以為 CI 會用同一個分岔點起點再查一次,實際沒有,風險分級與表態在合併前只有本機掛鉤一道。`--no-verify` 推出去的分支,到 PR 合併前沒人補查。
要改:守衛面照實寫成「後盾只有合進 main 的 push 事件」,並把「縮小範圍後合併前只有本機一道」寫進天花板;標籤那條拿掉「CI 跑過」的說法,或改成「標籤指到 main 上的提交才有 CI 背書」。(消費專案的 CI 可能不同,spec 只能講本 repo 查得到的。)

## F2 一般增量推送的「舊值..頂端」在重定基底後 force-push 時照樣誤擋,spec 的天花板沒點名
severity: minor
blocking: 否——跟今天行為一樣,沒退步;但本案動機(誤擋 715 條)在這條路上還會重現,要寫進天花板。
spec 段落:範圍第 2 條、驗收條款 S4、天花板 1。
引句:「遠端舊值不是全零而且本機有那個物件 → `舊值..頂端`(一般增量,同今天)」
問題:force-push 蓋掉舊頂端時,舊頂端通常還在本機(reflog 裡),`git cat-file -e` 成立,掛鉤走 `舊值..頂端`。天花板 1 只寫「合過主線時的多算」,沒寫「重定基底」。
實驗:主線 a,feat 加 f 並推出去;主線再加 m1 m2 m3;feat 重定基底到主線。掛鉤範圍 `舊值..頂端` 的檔案是 `m1 m2 m3`(不是作者改的);同一組輸入拿 `_push_range_start`(`scripts/lumos:41864`,經 `_push_pick_base` 判「分岔點不是舊值祖先」)算,起點是新主線頂端,檔案只有 `f`。也就是 `_push_range_start` 已經會處理這型,是掛鉤的判斷條件(物件在不在)把它擋在門外。
預期 vs 實際:重定基底後 force-push,預期只算 `f`;實際算出主線新增的三個檔,主線有 700 條會被當新增告警的提交時就是同一種誤擋。
修法選擇題,擇一寫明:(a) 判斷多加一條「舊值不是頂端的祖先也走 push-range」,S4 與天花板 1 跟著改;(b) 維持現狀,天花板 1 加「重定基底後 force-push」並指向收斂 Issue。

## F3 舊版 lumos 的錯誤文字會原樣印給推送的人,spec 沒說掛鉤要吞掉
severity: minor
blocking: 否——只是誤導,不影響放行與擋下。
spec 段落:範圍第 2 條、實務隱患「舊版 lumos」。
引句:「舊版 lumos 沒有這個指令、失敗、印出怪東西)退回 `空樹..頂端`(同今天)」
問題:舊 lumos 跑 `push-range` 實測印出以「擋下:沒有「push-range」這個指令。」開頭的兩行、rc2(clone 裡的現行 lumos 還沒有此指令,可直接重現)。掛鉤若沒有 `2>/dev/null`,每個新分支 ref 會印這句兩次(`pp_touched_file` 一次、迴圈一次),推送的人讀到「擋下」會以為被擋了。成功時 spec 又要求說明印到 stderr,所以不能一律丟掉。
要改:在做法第 2 點寫明:失敗路徑(rc 非 0)的 stderr 不顯示、只在成功時轉印;或兩種都吞。並在 S5 補一個斷言「舊版 lumos 時 stderr 不含『擋下』」。

## 各節審查

### 範圍
已讀:見 F2、F3。另核對:`pp_touched_file` 在迴圈外先跑一次(`scripts/hooks/pre-push:63`),迴圈裡再算一次,同一 ref 各一次 push-range;做法第 3 點說「迴圈裡每個 ref 算一次」沒涵蓋 `pp_touched_file` 那份,是兩次獨立呼叫。實測單次 lumos 啟動約 0.6 秒、`_push_range_start` 約 0.2 秒,一個 ref 兩次約 1.6 秒,可以接受(`git push --all` 推 N 個新分支約 1.6N 秒)。無 finding。

### 做法
已讀:見 F3。核對:`cmd_push_range` 呼叫的 `_lens_full_sha`(`scripts/lumos:41965`)用 `^{commit}` 剝標籤物件,註記標籤推送的頂端是 tag 物件時也能轉成提交 sha。`_drift_empty_tree`(`scripts/lumos:33342`)存在。`_lens_range_ok`(`scripts/lumos:41757`)左端全零合法。無其他 finding。

### 實務隱患(逐類)
- 版本錯位:新掛鉤+舊 lumos → rc2 退回空樹,同今天(實測,見 F3 的訊息問題)。舊掛鉤+新 lumos → 掛鉤根本不呼叫,無影響。`lumos update` 一起 vendor 掛鉤與 `scripts/lumos`(`scripts/lumos:20687`、`22302` 兩處清單都有 `scripts/hooks/pre-push`),所以兩者錯位只發生在手動拷貝或只更新其一。無 finding。
- 回退:退回提交後掛鉤與 lumos 同步回到舊版(都在同一提交裡),不會留下「掛鉤會呼叫、lumos 沒有」的半套;就算錯位也走 rc2 退回空樹。錨點基線 `governance/anchor-baseline.json` 追蹤掛鉤與測試檔(`scripts/lumos:22298` 的 ANCHOR_FILES),要跟本案同一提交更新,退回時才一起還原——做法第 6 點沒列,但屬一般提交紀律,無 finding。
- fetch 與推送之間主線變了:掛鉤吃的是 git 傳來的遠端舊值(推送當下剛問過遠端),起點吃本機遠端追蹤 ref。追蹤 ref 過期只會讓分岔點比真實的早(範圍多算、偏嚴),不會少算;頂端落在過期主線上才回「沒有新東西」,而這種情形頂端本來就在主線歷史裡。無 finding。
- force-push:見 F2。舊值本機找不到(S7)那條,實測 `_push_range_start` 取分岔點、不退到空樹,正確。
- 代碼審留痕與表態閘:留痕綁 `head_sha` 與分支(`scripts/lumos:44885` 起的 `_codeloop_record_valid`),不綁範圍,新範圍下留痕仍對得上;表態核對只迴圈「範圍內適用的題」(`scripts/lumos:44885` 的 `_dispositions_verdict`),範圍變小只會少題、多餘的表態不被挑剔。擋下訊息裡印的樣板範圍用實際傳入的 `diff_range`,跟掛鉤一致。無 finding。
- 空範圍:`頂端..頂端` 實測 `pitfalls`(tier light、suite docs)、`code-loop check`(OK)、`spec-gate --push-check`(無輸出 rc0)、`impact`(空結果)都正常處理,不會因空範圍崩潰。無 finding。
- 時間:見範圍節實測。極端情況(git 卡住)`_lens_git` 單次 20 秒上限、`_push_range_start` 內 `--is-ancestor` 逾時不中止,最壞約 6 次逾時,我沒有造出這種環境,⚠ 未量測;無具體失敗輸入,不算 finding。
- 守衛面:見 F1。
- 金流/對外送出/不可逆:同意 spec 的排除(只改掛鉤與唯讀指令,不連網)。

### 驗收條款
已讀:S1–S7 與範圍一致。S4 的「一般增量」範圍見 F2。S5 建議加 F3 的 stderr 斷言。無其他 finding。

### 回退
已讀,無 finding(見實務隱患「回退」)。

### 天花板
已讀:見 F1、F2,需補寫兩點。

### 審計修正紀錄
已讀,無 finding。

最嚴重 severity: major;blocking 1 條(F1)。
