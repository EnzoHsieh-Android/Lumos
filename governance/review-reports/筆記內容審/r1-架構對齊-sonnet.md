severity: major

### F1 判定檔存法不是連鎖帳本那支的實際寫法,是專案沒有的第三種

severity: major
blocking: 是 —— 引入了「第二種做法」:判定檔的檔案粒度、寫入時機、檔名規則都跟連鎖帳本實際實作不同,又不是既有的共用 jsonl 帳本家族,是第三種持久化方式

引句:「每次 record 或 skip 寫一個新檔 governance/note-verdicts/<時間>-<亂數>.json(新資料夾)」

file: `governance/review-reports/筆記內容審/r1-work.md:60`

連鎖帳本的實際寫法不是「一次判定一個檔」:一個 cascade 只在觸發當下由 `rel_cascade_create` 用 `O_CREAT|O_EXCL` 鑄造一次檔(`c-<UTC秒ts>-<sha1(root id)[:8]>(-<n>)?.jsonl`),之後每一次 confirm/prune 判定都是用 `_ledger_append`(`O_APPEND`、**不帶** `O_CREAT`,檔案必須已存在)把一行 `transition` 事件寫進同一個既有檔,見 `scripts/lumos:15016`(「每 cascade 一檔 governance/rel-cascade/<cascade-id>.jsonl;行帶 event 判別欄(header|transition)」)與 `scripts/lumos:15036`(`_ledger_append` 定義)、`scripts/lumos:15055`(`rel_cascade_create` 定義)。也就是「多筆判定共用一個檔、逐行 append」,不是「每筆判定各自開一個新檔」。本篇的 governance/note-verdicts/ 方案是每次 record/skip 呼叫都新開一個獨立的 `.json` 檔(而不是 `.jsonl` 逐行 append 進既有檔),檔名規則也不同(連鎖帳本是「UTC 秒時間戳+來源 id 前 8 碼 hash、碰撞遞增序號」,本篇是「時間+亂數」,且沒有寫明碰撞重試迴圈)。專案裡另一族「多寫入者、不上鎖」的先例是共用單一 append-only jsonl(`docs/.governance-log.jsonl`、`.escape-log.jsonl`、`.canary-log.jsonl` 等,見 `scripts/lumos:928` 的 `_gate_event` 寫入),同樣是「共用一個檔、逐行寫」而非逐筆開新檔。所以本篇的判定檔存法,既不是連鎖帳本的「一 cascade 一檔、append 多筆」,也不是既有 jsonl 帳本家族的「共用單一檔案」,是第三種持久化形狀。

### F2 「取最重、只有申訴能調輕」折疊規則,連鎖帳本沒有這個先例

severity: major
blocking: 是 —— 把一套專案裡查無先例的加權折疊規則,掛在「照連鎖帳本做法」的名義下,實際跟連鎖帳本的折疊規則相反

引句:「同一個內容編號在所有判定檔裡,★取最重的那次非申訴判定★」

file: `governance/review-reports/筆記內容審/r1-work.md:61`

連鎖帳本的折疊規則是「狀態折疊:同 (neighbor×edge_type×from_decision_id) 取物理序最後一筆」(`scripts/lumos:15109`-`15124` `_ledger_fold`),也就是單純的「最後寫入者贏」(last-write-wins,按檔內出現順序,不看事件內容的輕重),而且刻意不用 ts 排序(承接 canary-log 的慣例)。本篇要的是「推得出 > 一半一半 > 脈絡」的加權比較、且只有申訴批次能調輕的不對稱規則——這在連鎖帳本裡沒有對應機制,搜遍全庫也沒有查到「加權取重、單向調整」這種折疊先例(code-loop 的 pass/skip 讀取是「該分支最後一筆合法事件」,一樣是 last-write-wins,不是取重)。PRIOR-ART 段落把這條規則掛在「連鎖帳本」名下,但連鎖帳本本身的折疊語意剛好相反,是被拿來背書一個專案裡沒有先例的新設計,而不是真的借用它。

## 四問

**1. 分層與依賴方向**:第一層私有函式直呼的問題確實改掉了——文末〈前身 r3 發現怎麼處理〉與本篇〈做法〉第 1 節都不再出現第二層呼叫 `_ns_*`/`_note_shape_*` 私有前綴函式的寫法,改成抽一支兩層共用的函式,第一層與第二層各自呼叫它(`governance/review-reports/筆記內容審/r1-work.md:50`)。這個切法對照本 repo「共用低階層被多個閘呼叫、家留在原生產者」的既有先例是一致的:`_note_shape_eval`/`_ns_range_added` 本身就大量直接呼叫 `_nodehome_*` 家族(`scripts/lumos:23597` 的 `_nodehome_git`、`23603` 的 `_nodehome_cat_blobs`、`23792` 起的 `_nodehome_golive`/`_nodehome_clamp_base`),而 `_nodehome_*` 的家仍留在 `Systems/每支檔有家`——這正是本篇說「上線點與範圍起點那兩支函式的家照舊是 [[Systems/每支檔有家]]」(`r1-work.md:51`)想承接的模式,跟既有做法一致。唯一補不齊的地方:本篇沒有給抽出來的共用函式一個具體名字(只用敘述「範圍裡新寫、而且終點版本還在的筆記行」帶過),沒法直接核對是否符合 `_nodehome_*` 那種前綴一致、可辨識「誰的家」的命名慣例——⚠ 這點缺細節,不硬判為不一致,留給編排者在實作前補一個具體命名。

**2. 命名與錯誤處理**:子命令 `note-audit`(`prepare`/`record`/`check`/`skip`)是多動詞群組,對照 `scripts/lumos:32471` `code-loop` 群組(`pass`/`skip`/`dispositions`/`recall-miss`/`check`)與 `scripts/lumos:32454` `home` 群組(單一 `check` 子命令)的「單一動詞扁平、多動詞群組」慣例(`scripts/lumos:32499` 那行★扁平頂層指令★註解)是一致的分法。`skip --note "<理由>"` 記 `skipped` 的形狀,直接對照 `code-loop skip --note`(`scripts/lumos:32488`)與 `bound-tests --skip --note`(`scripts/lumos:32517`)兩個既有先例,是同一套「顯式跳過、必填理由、事件種類=skipped」的慣例,一致。環境變數 `LUMOS_SKIP_NOTE_AUDIT=1` 記 `skipped-env`,對照 `LUMOS_SKIP_NOTE_SHAPE`(`scripts/lumos:23955`-`23958`)一致。設定鍵 `note_audit.gate`(block/warn/off、從被檢查版本讀、非 block 時 doctor 印一行)逐字對照 `note_shape.gate` 的設計(`scripts/lumos:23479`-`23497` `_note_shape_config`、`23862`-`23880` `_note_shape_doctor_lines`),一致。「沒違規/涵蓋齊全不寫治理帳」這條也明講「事件種類照第一層」(`r1-work.md:81`),對照 `cmd_note_shape` 的 docstring「有違規...與跳過才寫治理帳,沒違規的放行不寫」(`scripts/lumos:23942`)一致。`decision-amend` 這個複合詞命名對照既有 `decision-add`(`scripts/lumos:32218`)的扁平單詞慣例,一致。唯一沒寫清楚的地方:record 成功寫入判定檔時,治理帳要記哪一種 kind(passed?還是新種類?)本篇只說「治理帳只記事件與筆數」(`r1-work.md:63`),沒給出具體 kind 值——⚠ 留給編排者在動筆前補,不足以判一致或不一致。

**3. 第二種做法**:見上方 F1、F2——「一次判定一個檔」跟連鎖帳本「一 cascade 一檔、多筆 append」的實際寫法不同,是查無先例的第三種存法;「取最重、只有申訴調輕」的折疊規則也跟連鎖帳本「物理序最後一筆」的實際折疊規則相反,專案裡查不到加權折疊的先例。至於「判定檔從被推送頂端提交讀」這件事,本篇自己標明是「照第一層設定從被檢查版本讀的做法」(`r1-work.md:78`),這個確實有先例——`_note_shape_config` 與 `_note_shape_doctor_lines` 本來就是用 `_nodehome_reader(root, tip_where)` 讀被檢查版本的 `.lumos/config.json`(`scripts/lumos:23996`),而不是讀工作目錄;`_nodehome_list` 也已經有「列出某個版本下所有檔案」的能力可供延伸去列一整個資料夾。這一小點跟既有做法一致,不是問題;真正不一致的是判定檔本身的存法與折疊規則(F1、F2)。

**4. 落點合不合理**:`lands_in: Systems/筆記內容審` 這個新家目前圖譜裡還不存在(已確認 `docs/lumos-toolchain-knowledge/Systems/` 底下沒有這篇),不會撞到既有節點的排除聲明,這一點確實修掉了前身 r3「落點節點明文排除本案」的問題——前身舊稿 `lands_in` 直接寫 `Systems/筆記內容閘`(見 `docs/lumos-toolchain-knowledge/Projects/筆記不存程式碼推得出的事_計劃.md:10`),而那篇節點現在的 `responsibility` 明文寫著「不管推送前 AI 審查員(第二層計劃)」(`docs/lumos-toolchain-knowledge/Systems/筆記內容閘.md:6`),兩者正面衝突,本篇換成開新家後這條衝突對整個計劃來說解除了。但本篇仍把「抽出的共用函式與區塊判定」的說明留在 `Systems/筆記內容閘`(`r1-work.md:51`「說明寫進 [[Systems/筆記內容閘]](它本來就管「哪些筆記行算新寫的」)」),而這篇節點的 responsibility 剛好就是那句「不管推送前 AI 審查員(第二層計劃)」。⚠ 這裡兩種讀法都有站得住的理由:一種讀法是「共用函式本來就是第一層原有邏輯抽出來的,家留在原產地、被第二層呼叫」,跟 `_nodehome_*` 被 note-shape 呼叫但家留在 `Systems/每支檔有家` 是同一種模式,合理;另一種讀法是節點的 responsibility 明文排除「第二層計劃」,把跟第二層直接相關的共用函式說明寫進去,字面上就是自相矛盾,需要編排者判斷是要在落地前順手改一下 `Systems/筆記內容閘` 的 responsibility 措辭(把「不管第二層的判定邏輯」和「共用給第二層呼叫的行判定函式仍歸這裡」分清楚),還是把那段說明搬到新家。這點判不準,不開成正式 finding,交編排者裁。上線點與範圍起點兩支函式留在 `Systems/每支檔有家` 這條沒有疑義,跟既有「這兩支函式本來就是 nodehome 家族、被 note-shape 借用」的事實一致(`scripts/lumos:23792`-`23794` `_note_shape_eval` 直接呼叫 `_nodehome_golive`/`_ns_range_added` 傳入 `_NOTE_SHAPE_GOLIVE_MARK`)。

不對齊共 2 條,其中 major 2 條。
