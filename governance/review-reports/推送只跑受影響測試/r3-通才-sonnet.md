severity: major

兩條會擋,三條不會擋。

### F1 主線判定綁在遠端名上,直接推網址或換別名遠端推 main 會被當成功能分支
severity: major
blocking: 是。照字面實作,推 main 會漏掉「推 main 照舊跑全套」這條合約(S2、S3)。
spec 段落:做法 2(lumos 判主線)、做法 3、S4。
引句:「被推的 ref 對應的那條(`refs/remotes/<--push-remote>/<被推分支>`)等於其中任一 → true」
問題:
- 判法拿被推的 ref 組成 `refs/remotes/<遠端名>/<分支>`,再跟主線候選比。
- 遠端名來自掛鉤的第一個參數。直接推網址時,那個參數就是網址。
- 網址或別名遠端(指向同一網址、但沒有 fetch 過 `<別名>/main`)組出來的 `refs/remotes/<網址>/main` 對不上任何候選。
- 候選裡只有 `main@{upstream}`(解成 `refs/remotes/origin/main`)會存在,對不上。
- 結果是 `pushed_mainline` 回 false,不是「git 失敗 → true」。推 main 就被降成 light,只跑文件子集加關鍵字子集。
- spec 的失敗方向只處理了「算不出來 → true」,沒處理「算出來但是錯的」。
- S4 也沒有測網址或別名遠端的案例。
- 現有程式碼已經踩過這個坑,也有結論。`_note_reread_mainline_names` 明寫「不看 pre-push 給的遠端名」,改用固定名 main/master 加候選實際指到的分支名。原因是換遠端名或直接推網址會整段繞過核對。
- spec 說要「抽出共用候選清單」,卻沿用了被這個結論否決的遠端名綁定做法。
佐證:
file: `scripts/lumos:53737`
file: `scripts/lumos:65263`
file: `scripts/hooks/pre-push:166`(掛鉤自己註解:「直接推網址時是網址、手動跑時是空的」)
建議:改用分支短名比對。被推分支名屬於 {main, master} 加候選指到的分支名,就判 true。補一支網址或別名遠端的先紅測試。

### F2 「推功能分支就有 CI 全套」只在首推成立,後續推送只看增量範圍,合併前的等綠擋不住
severity: major
blocking: 是。中心承諾與 CI 現行行為矛盾,字面實作會讓合併前那一關形同虛設。
spec 段落:白話段、做法 1、做法 4、實務隱患「守衛面」。
引句:「prep 判範圍照現行(push 事件問 lumos,只改文件就文件子集,其他全套)」
引句:「合併前 `lumos ci-wait` 的判定要是 green(rc 0 不等於綠)」
問題:
- CI 的 prep 用 `github.event.before..sha` 判範圍,只看這一次推送新增的提交,不是分支對 main 的整段。
- 只有新分支首推(before 是 40 個 0)才一律全套。
- 功能分支先推一次程式提交,CI 全套跑著或紅了。接著推一個純文件的補提交(筆記修正、說明文字),這次 CI 範圍判成 docs,只跑文件子集,結果綠。
- `lumos ci-wait` 用 `gh run list --commit <HEAD sha>` 只查頭那個提交的 run,看不到前一個程式提交那次紅的全套。
- 沒開 PR 時,也沒有 PR 事件的全套補位。
- 於是「合併前 ci-wait 判定 green」可以在全套沒對最終程式碼跑綠的情況下成立。
- spec 把 Q2(分支保護)當作唯一缺口,沒看到這個缺口,也沒有任何驗收條款覆蓋它。
- 本機側同理。這類補提交本機早就只跑 docs,以前還有首推或合併時的全套兜底。
- 守衛檔(帳本提交)會判全套,所以不是所有補提交都漏,只有純文件那類。
- RETIRE-IF 只數紅率,也看不到這種被遮住的紅。
佐證:
file: `.github/workflows/ci.yml:83`(prep 的範圍判定,帶 `$BEFORE..$SHA`)
file: `scripts/lumos:62971`(`_ci_list_runs` 以 `--commit` 查單一 sha)
建議(擇一):
- 功能分支的 push 事件在 prep 改算「分支對主線」的整段範圍,只有整段都是文件才降級。
- 或明寫這個缺口,讓 ci-wait 同時檢查分支上最近一次判全套的 run。
- 再補一條驗收條款:先推程式提交、再推純文件提交,CI 範圍應判全套。

### F3 同一個提交推功能分支又推 main,兩次 CI 共用同一個 concurrency 群組
severity: minor
blocking: 否。只影響合併後那次 CI 的時機,不影響功能分支的合併前驗證。
spec 段落:做法 1。
引句:「push 事件以提交編號分組、不取消,之後再推的帳本提交不會取消功能提交那一次。」
問題:
- 群組鍵是 `ci-push-<sha>`,不含 ref。
- 現行 main 路徑是「每個提交各自一組」。改成推分支後,同一個 sha 會先在功能分支跑一次,快轉合併後在 main 又跑一次。
- 兩次落在同一組。後來的那次會排隊等第一次跑完。
- 若又有第三次同 sha 的推送(推到另一個分支、補推),排隊中的 main 那次會被取代,PRIOR-ART 說的「合併後那一次」就沒跑到。
- spec 只論證了「帳本提交不會互相取消」,沒處理同 sha 多 ref。
佐證:
file: `.github/workflows/ci.yml:20`
建議:群組鍵加上 `github.ref`,或在 S6 補一條同 sha 兩個 ref 各自一組的斷言。

### F4 回退只還原了範本,做法 5 的其他五處說明改動不在回退裡
severity: minor
blocking: 否。只影響回退後的文件一致性,程式行為不受影響。
spec 段落:回退、做法 5。
引句:「範本那句改回原文、`lumos update` 重新注入、刪 S7 的測試。」
問題:
- 做法 5 列了六處要改:範本、專案 CLAUDE.md、08-自動跑的.md、bound-tests-gate 那一行、`_suite_word`、父計劃的 `[closed:]`。
- 回退只提範本一處。
- 回退掛鉤、CI 之後,其餘五處仍寫「功能分支只跑子集、CI 推分支跑全套」,跟實況相反。
- 回退段也沒有「回退後 CI 又不跑功能分支」的提醒。
- S7 只守 CLAUDE.md 與 AGENTS.md,沒有測試守另外五處。
建議:回退段把五處逐一列入。

### F5 RETIRE-IF 的紅率沒有基準,分子也混了與本機改動無關的紅
severity: minor
blocking: 否。資料量得到,但判讀會失真,不影響本次實作。
spec 段落:RETIRE-IF。
引句:「功能分支推送觸發的 CI 全套紅的次數超過這類推送次數的三成」
問題:
- 「三成」沒有基準。現行 PR 與 main 的 CI 紅率沒有量。
- 功能分支每次推送的 CI 還會跑 gates 工作,例如 code-loop gate 在中途推送缺留痕就會紅。
- 這些紅不代表「本機少跑全套造成的」,會讓比例被灌高,誤觸發撤除。
- 數法也沒說明排除 cancelled 和 skipped。
建議:分母與分子限定在 shards 工作(全套)的 conclusion,並先記一個現況紅率當比較基準。

### 逐節結論
- 白話與 PRIOR-ART:已讀。引用的外部做法與實際做法一致,但「合併前那一次」的前提有 F2 的缺口。
- 舊否決對照:已讀,無 finding。
- 現況:已讀。CI 觸發、PR 全套、concurrency 鍵、守衛檔提早回 full 且 `affected_keys` 為空、`_suite_this` 與 `_AUTOLOOP_FULL` 的讀取範圍,都跟程式碼相符。
- 範圍:已讀,無 finding。
- 做法 3(掛鉤):降級條件沒有要求 `light_ok`、也沒有要求 spec-gate 判 light。這是刻意的「功能分支一律降級」。守衛檔情境降到只剩文件子集,訊息已照實講,無 finding。
- S1 到 S7:S1 與 S5 共用同一支測試名,可以接受。覆蓋缺口是 F1 的網址與別名案例,以及 F2 的連續推送案例。
- 實務隱患:風險類逐項查過(守衛、算不出來、機器時間、併發、版本錯開、金流、對外送出、不可逆)。守衛面的缺口記在 F2,併發面在 F3。其餘無新增隱患。

整份最高等級為 major,會擋的問題 2 條(F1、F2),不會擋的 3 條(F3、F4、F5)。
