severity: major

# 第 2 輪設計審:正確性-opus

鏡頭:項目指紋在 prepare/record/check 三處一致性、兩邊家對照與刪檔/移出/改名組合、`_note_audit_resolve` 選配參數與 `_notes_touched_in_range` 抽出對既有呼叫端的影響、條款能否寫成會翻紅的測試。
實驗目錄:`rr-r2-work-正確性-opus/`(clone --shared;NFD 探針在 `nfd/`,探針腳本 `probe.py`)。

逐節結論:
- 開頭、依據、PRIOR-ART、RETIRE-IF、REVISIT:已讀,無 finding(依據裡「35/37 落在同提交改過的家」我對 rtb 原 repo 逐篇驗過:實驗二 rtb 17 行真漂移全部在「同提交也改過」的 Systems 筆記上,只有 R10n5 那 1 行邊界落在沒改過的篇,所以 S10 的 14 行門檻在產品母體下構得到)。
- 範圍、〈做法〉0:已讀,見 F3、F8。
- 〈做法〉1:見 F3、F6、F7、F9。`_note_audit_resolve` 加選配參數、預設照舊:四個筆記內容審呼叫端與 drift check 呼叫端(`scripts/lumos:28844`)都不傳,行為不變,無 finding。`_notes_touched_in_range` 抽出:原碼 `_late()` 在 git log 之前、`touched is None → None`、`.md` 過濾+集合+排序都在抽出段內,只要共用函式保留「集合、排序」與 `surrogateescape` 解碼,S12 列的三種 None 都留在 `_notes_status_flipped` 或 `_note_flipped_one` 這邊,抽出本身不改行為,無 finding。
- 〈做法〉2:見 F1、F5、F8。
- 〈做法〉3:已讀,無 finding(record 不重算指紋、直接用檔頭的,跟 check 的比對只差在 check 重算——一致性問題都落在指紋定義本身,見 F1、F8)。
- 〈做法〉4:見 F2、F4。
- 〈做法〉5、6、回退、實務隱患、誠實界線、附錄:已讀,F1 補一處跟 skill 流程的矛盾;其餘無 finding。
- 條款:S1 見 F3;S3、S12、S13 寫得成會翻紅的測試(S12 翻紅抓得到「共用函式做了頂端過濾」「失敗不回 None」,抓不到「`_notes_status_flipped` 沒改呼叫、另外抄一份」,屬 minor,不另開條);S6 見 F1、F4;其餘能照字面寫成會翻紅的測試。

## F1 項目指紋含筆記 blob,作者照判定改了筆記,同一次推送就會被再提醒一次——不是「下次推送」
severity: major
blocking: 是
引句:「改了筆記下次推送會再被列一次(筆記內容變了),不想再對照就照推」
file: `governance/review-reports/守檔筆記對照改動/r2-snapshot.md:58`

1. 指紋 = 雜湊(筆記路徑、**筆記在頂端的 blob**、about_code 各檔 blob、範本版本)。record 用項目檔頭的指紋(prepare 當時的筆記 blob n1)命名紀錄檔。
2. 照〈做法〉6 skill 寫的流程:「推送前看到提醒(或自己先跑 reread-prepare)→ 派一席 → reread-record → 照點出的行改筆記 → `git add governance/reread-verdicts && git commit` → 推」。改筆記那個提交跟改程式的提交在**同一個推送範圍**裡。
3. 推送時 reread-check 對同一篇重算:筆記在這次範圍裡被改過(是候選)、程式也改過(是家),指紋用的是改過後的 blob n2 ≠ n1 → 找不到同指紋紀錄 → 列成「沒對照」、記 `reminded`。
4. 結果:照判定改掉漂移行、做了該做的事的作者,每次都在同一次推送被提醒「沒對照」;要消掉只能再派一席判(再花一份錢)。只有「判定說沒問題、不動筆記」或「不理判定」的人不會被再提醒——提醒打在最配合的人身上。引句說「下次推送」不對,是這一次。
5. 兩週量測也跟著偏:〈做法〉5「提醒後真的去對照的占比 = `reminded` 列的指紋之後出現在 `recorded` 的比例」——先對照、改筆記、再推的作者,`reminded` 列的是 n2 的指紋,之後不會有人去 record 它,算成「沒去對照」。RETIRE-IF 第一條「提醒沒人用」看的是點出行有沒有被改,不受影響,但「提醒後對照占比」會系統性偏低。
6. 同一形狀的第二個觸發:代碼審迴圈在 reread 之後修 `scripts/lumos`(工具鏈 39 篇家都列它),about_code 的 blob 變了,所有已對照的篇重列。這一條語意上是對的(判定者看的是舊 diff),只是 skill 那句「建議放在代碼審留痕之前」會讓它常態發生,值得在 skill 裡講一句。
7. 建議改法:比對「是否已對照」只用程式那半(筆記路徑+about_code 各檔 blob+範本版本),筆記 blob 只記進紀錄檔、不參與比對。候選已要求「筆記這次被碰過」,程式那半沒變就代表判定者看過的 diff 還是同一份;〈誠實界線〉那條「筆記改了又改回」的例外也跟著消失。S6 加一句:「prepare、record 之後照點出的行改筆記並提交,check 應不再列那篇」。

## F2 reread-prepare 沒有 `--orchestrator`,但項目檔名與檔頭都要編排者;check 印的指令照貼會壞或無從決定
severity: major
blocking: 是
引句:「沒有的列出來(最多 10 篇,其餘給篇數)並印 reread-prepare 指令(原樣帶這次的 `--diff`、`--push-remote`、`--pushed-ref`)」
file: `scripts/lumos:39296`

1. 〈做法〉2:項目檔名 `reread-<項目指紋>-<編排者>.md`,檔頭要寫「編排者、判定者模型」;判定者模型要照編排者分 sonnet/`_CODEX_SEAT_MODEL`。所以 prepare 一定要知道編排者。
2. 〈做法〉1 列 reread-prepare 的參數只有 `--diff [--push-remote --pushed-ref]`;〈做法〉4 的提醒指令也只「原樣帶這次的」這三個。整份 spec 沒寫 reread-prepare 收 `--orchestrator`、預設是什麼。
3. 照同家族的 `note-audit prepare`(`--orchestrator` 是 `required=True`)做,提醒印出來的指令照貼就是 argparse rc2;照 spec 字面不加這個參數,檔名與檔頭的「編排者」沒有來源。兩種都是照字面做出錯的行為,而這條指令就是提醒唯一的行動路徑。
4. 建議:明寫 `--orchestrator claude|codex` 必填(或寫預設值與理由),提醒印的指令裡帶 `--orchestrator <claude|codex>` 讓人填;S6 的「印帶同一組參數的指令」改成「印出的指令照貼跑得起來」。

## F3 NFD 檔名的筆記經 `_nodehome_side` 讀不到,不會成為家——S1 的「NFD 照樣認得」用 spec 指定的建材做不到
severity: major
blocking: 是
引句:「NFD 路徑的筆記照樣認得」
file: `scripts/lumos:23816`

1. 〈做法〉1 的家:「起點與頂端兩邊各用 `_nodehome_homes`……前置(設定、`_nodehome_side`)照……那一串」。`_nodehome_side` 用 `_nodehome_list` 取 NFC 路徑,再用 `s._reader(p)`(`scripts/lumos:23761` 的 `git show <where>:<NFC 路徑>`)讀內容;樹裡存 NFD 位元組時這個讀法查不到,筆記不進 `s.notes`,也就不進家對照表。
2. 實測(`rr-r2-work-正確性-opus/nfd/`):用 `update-index --cacheinfo` 放一篇 NFD 檔名的 `Systems/執行が.md`(type system、status doing、about_code 列 `src/a.py`),對那個提交跑 `_nodehome_side` → `notes: []`、`homes: {}`;同一個提交的 `git log --name-only` 照樣列出這篇(NFD 位元組)。`core.precomposeunicode` 開或關結果一樣。
3. 只有「頂端就是 HEAD、而且磁碟上有 NFC 可讀的同名檔」(macOS APFS)才會從磁碟讀到——所以 S1 的測試在 macOS 上用 HEAD 當頂端可能是綠的,在 Linux CI 或頂端不是 HEAD 時是紅的,或更糟:測試剛好寫成 HEAD、兩邊都綠,產品在 CI 上對 NFD 的家整批漏掉。「只留頂端讀得到的」那一步用同一支 reader,同樣會把 NFD 筆記濾掉。
4. 要做到 S1 得改 `_nodehome_side`/`_nodehome_reader` 改用內容編號讀(`_nodehome_list(oids=…)` 已經有 NFC→編號對照)。那兩支是每支檔有家推送閘共用的,spec 沒把這個改動列進範圍、也沒說每支檔有家的行為會不會跟著變(它現在同樣看不到 NFD 的家)。建議:〈做法〉1 明寫「家對照與頂端可讀判斷改用 blob 編號讀」,範圍寫明也動到每支檔有家的共用函式,S1 的 NFD 案例寫明頂端不是 HEAD。

## F4 紀錄資料夾在頂端樹裡不存在時,`ls-tree <頂端>:governance/reread-verdicts` 回非 0,容易被當成 git 失敗而永遠不提醒
severity: minor
blocking: 否
引句:「只列目錄、不讀內容、不組 diff」
file: `scripts/lumos:26052`

1. 既有讀法 `_nodehome_git(root, "ls-tree", "-z", "--name-only", f"{where}:{dir}")` 在目錄不存在時 git 回 128,包裝函式回 None——跟「git 跑不起來」同一個值。筆記內容審那邊把 None 當「沒有判定檔」,是對的。
2. 〈做法〉4 同時寫了「git 失敗……一律印這次沒提醒、記 skipped」。照這句把這個 None 當 git 失敗,新專案(還沒有任何紀錄、資料夾不存在)每次推送都是 skipped、從不提醒,也就沒人去 record、資料夾永遠不會出現,自我鎖死。
3. 建議一句話:「資料夾不存在 = 沒有紀錄,照常比對」;S6 補「頂端沒有 `governance/reread-verdicts/` 時照樣列出」。

## F5 填入材料跟實驗兩處不同,S10 沒過時會被誤判成範本的問題
severity: minor
blocking: 否
引句:「`{{OTHERS}}` = 這次另外改到、沒放進 diff 的檔名用」
file: `governance/eval/home-check/tune/scripts/build_prompt.py:117`

1. 實驗的 others 只收程式檔(`is_code`:`src/`、`tests/`、`scripts/` 開頭),問法原文也寫「這次提交另外改到的程式檔只列檔名」。產品的「改到的檔」沒經過任何過濾,照字面 OTHERS 會把筆記(包括正在判的這篇)、`governance/` 帳本等全列進去,放在「程式檔」這個標題下。
2. 實驗的筆記行號格式是 `f"{i+1:4d}| {l}"`;spec 寫 `{{NOTETEXT}}` 每行「行號: 內容」,換了格式(開頭欄位 `type: system` 會變成 `3: type: system`)。
3. 這一節標題寫「照實驗逐字」,實際有兩處不同。S10 會把它們一起量進去,這沒問題;但 S10 不過時規定「回頭改範本」,原因其實可能在填入組法。建議 OTHERS 照實驗只列程式檔(或明寫刻意不同、交給 S10 量),NOTETEXT 照實驗格式。

## F6 reread-prepare 碰到起點算不出(`_PUSH_START_UNKNOWN`)沒定義;prepare 要不要記 skipped 前後矛盾
severity: minor
blocking: 否
引句:「reread 用這個參數,原因由自己印、事件由自己記一筆」
file: `scripts/lumos:26129`

1. `_note_audit_resolve` 帶推送參數、起點查不出來時不是提早結束,而是把 base 換成 `(判不了, 說明)` 這個 tuple 回給呼叫端。〈做法〉4 只替 reread-check 定義了這種情況;reread-prepare 也收推送參數(提醒印出來的指令就帶著),照字面把 tuple 當起點傳進 `_nodehome_changes` 會在 f-string 或 git 參數那一步出錯。
2. 同一節說「事件由自己記一筆」(兩個子指令都用這個參數),又說「prepare 不記」。建議寫明:prepare 碰到提早結束與起點算不出都只印原因、rc0、不記帳。

## F7 「前置照每支檔有家那一串」會把 `node_home.gate=off` 的提早結束一起抄進來
severity: minor
blocking: 否
引句:「前置(設定、`_nodehome_side`)照每支檔有家的 `_nodehome_evaluate` 那一串」
file: `scripts/lumos:24655`

1. 那一串的「設定」是 `_nodehome_config`,後面接的就是「node_home.gate=off → 印一行、回 0」。reread 用不到那份設定(不經 `_nodehome_required`),但照字面抄就會讓關掉每支檔有家的專案悄悄沒有回頭重讀提醒,而且不記任何事件,S7、S13 都測不到。
2. 建議寫明只需要 `_nodehome_side` 兩邊與 `_nodehome_homes`,不讀 `node_home` 設定;開關只看 `note_reread.mode`。

## F8 指紋的輸入口徑沒寫死,prepare 與 check 各算一份時容易對不上
severity: minor
blocking: 否
引句:「雜湊(筆記路徑、筆記在頂端的 blob 編號、那篇 about_code 列的每支檔在頂端的」
file: `scripts/lumos:23861`

1. 筆記路徑可以是 git 原樣(`_notes_touched_in_range` 回的)或 NFC 加圖譜前綴(家對照表來的);about_code 項目可以是原字串或 `_nodehome_key` 正規化後的;blob 可以查 `_nodehome_list(oids=…)`(只收一般檔,連結檔與子模組會變成「已刪」)或直接 `ls-tree`。任一項 prepare 與 check 取法不同,指紋就永遠對不上、提醒消不掉——這正是第 1 輪要解的形狀。
2. 建議:明寫「一支共用函式算指紋,prepare 與 check 都呼叫它」,輸入寫死成 NFC 圖譜前綴路徑、`_nodehome_key` 後的 about_code 集合、`_nodehome_list(oids)` 的編號;S6 加一個 NFD 筆記的案例(要先解 F3)。

## F9 改名的筆記加上起點那邊才有的家,交集永遠落空
severity: minor
blocking: 否
引句:「一支改到的檔,頂端那邊列它的家、以及起點那邊列它的家(刪檔、從 about_code 移出時只剩起點那邊有)都算」
file: `scripts/lumos:23877`

1. 起點那邊的家對照表給的是起點當時的筆記路徑;`_notes_touched_in_range` 對改名只回新路徑。同一次範圍裡「筆記改名」加「那支檔刪掉並從 about_code 移出(或只移出)」時,起點那邊的家是舊路徑,不在被碰過的清單裡、也不在頂端 → 不是候選。S1 寫的「含刪檔與從 about_code 移出」在筆記改名時不成立。
2. 〈做法〉2「那篇(頂端或起點那邊)about_code 列了」也要把改名的新舊筆記對起來,spec 沒說怎麼對。
3. 組合少見,建議在〈誠實界線〉寫一句,或寫明用 `git diff -M --name-status 起點 頂端 -- 圖譜` 把起點路徑對到頂端路徑。

最高等級:major;blocking 共 3 條
