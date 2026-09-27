severity: major

# 架構對齊審查(r2)——筆記內容審_計劃

被審:`governance/review-reports/筆記內容審/r2-work.md`(對照 r1→r2 差異:`governance/review-reports/筆記內容審/r2-delta.patch`)
對照 repo:`/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/clone-ns`(`scripts/lumos`)

## 問題 1:分層與依賴方向

沒查到跨層直呼或底層依賴上層的問題,但有一處方向未寫清楚。

- 共用函式抽取方向正確、有先例可循:`_note_shape_eval` 已經在呼叫 `_nodehome_golive`/`_nodehome_clamp_base`/`_nodehome_cat_blobs` 等「每支檔有家」的共用函式(`scripts/lumos:23793-23824`),而且 `Systems/每支檔有家.md` 自己就寫著「上線點與合併的兩支函式加了參數、拆出一支,這道自己的行為不變」(第 53 行)。r2 計劃要對同一批函式再加一個消費者(第二層),是同一個模式的第三次套用,方向是「共用基礎層被擴充參數」,不是新模組直接扒基礎層的私有實作。
- 治理帳寫入方向正確:`_gate_event`/`_gate_event_or_warn`(`scripts/lumos:856-935`)是全庫唯一的治理帳寫入端點,連 hook 都不准繞過去直接寫(見該函式自己的註解:2026-09-07 曾有人寫過不存在的 `lumos gov-event`,結論是「工具沒有給外部腳本寫治理帳的入口」)。第二層照樣走 `_gate_event_or_warn`、把 `note-audit` 登記進 `_KNOWN_GATES`(`scripts/lumos:6599-6615`,目前結尾就是 `"note-shape"`,方向一致),沒有另開一條寫入路徑。
- ⚠ 唯一沒寫清楚方向的地方:`code-loop pass` 要印「這個範圍還有待審筆記行」的提醒(做法第 8 點)。現有的「一個指令讀另一個模組的狀態」先例只有 `doctor` 讀 `_note_shape_doctor_lines`(`scripts/lumos:1001` 呼叫、`23862` 定義)——doctor 是頂層彙整者,讀哪個閘的狀態都不奇怪;但 `code-loop pass` 本身是同層的另一道閘,不是彙整者。全庫目前沒有「某道閘的指令處理常式直接讀另一道閘的判定狀態」這種先例。計劃沒寫清楚這個提醒是透過一個像 `_note_shape_doctor_lines` 那樣的共用狀態函式(對齊 doctor 的既有模式),還是 `code-loop pass` 直接匯入 note-audit 內部。因為只是印一行不擋、不改變 code-loop 自己的判定邏輯,風險低,交編排者裁是否要求計劃寫明實作機制。

## 問題 2:命名與錯誤處理

命名跟鄰居對得上。

- 子指令動詞:`prepare` / `record` / `check` / `skip` 分別對齊既有的 `loop next`(派工)、`canary record`(記一輪結果,`scripts/lumos:31862` 的 help 文字就是「記一筆…」)、`home check` / `code-loop check`(核對)、`code-loop skip`(跳過並留帳)——四個動詞在庫裡都各自有同名先例,不是自造詞。
- `--orchestrator claude|codex` 完全比照 `loop next`/`canary record` 既有的 `LOOP_ORCHESTRATORS` 機制(`scripts/lumos:7821-7837`、`10398-10414`),連錯誤訊息的語氣「只能是 X/Y 之一」都是同一套。
- `note_audit.gate` 的鍵名與 `block/warn/off` 三值,逐字對齊 `note_shape.gate`(`scripts/lumos:23479-23497`、`_NOTE_SHAPE_GATE_VALUES`)——連「從被檢查的版本讀」「不是 block 時 doctor 每次印一行」這兩句話都是原句照搬,不是另開一套語意。
- `file:` 證據驗證重用既有的 `_validate_repo_ref(repo_root, token, line, at_sha=None)`(`scripts/lumos:19819`),而且它本來就支援 `at_sha` 讀指定提交而非工作樹(既有用法見 `scripts/lumos:30419`),第二層照抄這個既有能力,沒有另刻一支路徑驗證器。
- `governance/note-verdicts/` 資料夾名沿用 `governance/` 下既有的 kebab-case 慣例(`rel-cascade`、`review-reports`、`replay`、`code-loop`、`eval`)。

## 問題 3:第二種做法

r2 這版誠實承認判定檔存法是新的、也正確排除了治理帳 jsonl(取最後一筆)與放行檔(讀改寫上鎖)這兩種既有存法不適用的理由——這兩點跟程式碼核對過都站得住:`_ledger_append` 確實限制單筆 ≤4KB 且用 `O_APPEND`(`scripts/lumos:15036-15052`),跟 `_write_lf` 的「暫存檔→原子換名」(`scripts/lumos:14146-14171`)是兩種不同機制,r1 架構對齊席指出「原稿把新做法掛在連鎖帳本名下」的問題在這版確實改正了;`_lint_waivers_add` 也確實是單一 json、`_vault_write_lock` 上鎖的讀改寫(`scripts/lumos:21447-21462`),跟「幾乎每次推送都要寫」的判定檔用途不合。

但 PRIOR-ART 的先例普查漏了全庫裡最貼近「一次判定一個檔、進版本控制、還要防事後被刪改」這個問題的既有機制:`lumos loop replay --freeze`(`scripts/lumos:579` 起,`cmd_loop_replay`)。它做的正是同一類事——把某個審查迴圈的判定閉包凍結成 `governance/replay/<loop-id>/verdict.json`(單檔、進版控),回放時比對「凍結時的列帳在現帳裡消失或被改」(`scripts/lumos:764` 逐字寫著「帳被動:凍結時的 N 列帳在現帳裡消失或被改(append-only 帳不該少東西)」),而且凍結檔本體還會拿 git blob 比對防篡改(`scripts/lumos:744-751`)。這正好對上審查題目問的「『只准新增』檢查有沒有先例」——答案是有,而且比連鎖帳本更貼近,但 r2 的 PRIOR-ART 段與〈做法〉第 2 節完全沒提到它,也沒說明「判定檔只准新增+跟治理帳指紋對得上」這個新機制為什麼不沿用或借鑑 `loop replay` 已經在用的「雜湊清單 + git blob 錨定」做法,而是另外設計成「diff 範圍起訖兩個提交之間的判定檔資料夾」加「治理帳事件裡帶指紋」。這是計劃自己在防「存心偽造」時列出的機制(做法第 2 節「判定檔與治理帳互相對得上」),跟 `loop replay` 的防篡改機制解決的是同一類問題,卻是第三種寫法——而且是在沒有比較過、沒有說明取捨的情況下出現的,不是像另外兩種被排除的做法那樣有交代。

`_BOOKKEEPING_DIRS` 的語意核對過三個消費點(`_stack_changed_ok` `scripts/lumos:24723-24740`、`_pitfall_tier` `scripts/lumos:24743-24753`、另一處在 `24837`),常數自己的註解寫著「卷證目錄也是紀錄不是碼(三個消費者共用這一組)」(`scripts/lumos:20353`)——`governance/note-verdicts/` 裝的是判定紀錄不是程式碼,語意上跟既有三個目錄(`code-loop/`、`review-reports/`、`replay/`)同一類,加進去沒有走樣。

## 問題 4:落點

三個落點都合理,而且跟現有節點的 `responsibility` 欄位對得上,不是硬塞。

- `Systems/筆記內容審`(新家)裝第二層自己的程式,符合「每支檔有家」對巨型單檔多節點分工的既有慣例(`scripts/lumos` 本來就被拆給幾十個 Systems 節點各管一段)。
- `Systems/筆記內容閘` 目前的 `responsibility` 欄位本來就寫著「不管推送前 AI 審查員(第二層計劃)」(該篇 frontmatter 第 6 行),r2 提出的改法是把這句收窄成「不管第二層的判定與紀錄,但『哪些筆記行算新寫的』共用函式歸這裡」——跟該篇正文第 40 行「範圍、上線點、合併的算法本身的家是 `Systems/每支檔有家`」是同一種分工邏輯的延伸,不是新發明一種切法。
- 上線點/範圍起點函式留在 `Systems/每支檔有家`,核對過該篇確實是這兩支函式現在的家(`docs/lumos-toolchain-knowledge/Systems/每支檔有家.md:53`),沒有錯置。

## 結論

不對齊共 1 條,其中 major 1 條。

### F1 判定檔防篡改機制沒有比對過庫內最貼近的既有先例(`loop replay --freeze/--golden`)

severity: major
blocking: 是 —— PRIOR-ART 普查遺漏了全庫裡跟本案最相似的既有「單檔進版控 + 防篡改」機制,新設計的防篡改做法(範圍起訖 diff 判定檔資料夾 + 治理帳指紋比對)因此是在沒有比較、沒有交代取捨的情況下,對同一類問題另開的第三種寫法,不是像另兩種已排除的存法那樣經過交代。
引句:「寫法用既有的 `_write_lf`,折疊規則(取最重、申訴只換它指名的那筆)是新定的」
file: `governance/review-reports/筆記內容審/r2-work.md:27`
對照既有先例:`scripts/lumos:579`(`cmd_loop_replay`)、`scripts/lumos:744-764`(golden 列帳雜湊比對「消失或被改」+ git blob 防篡改,逐字寫著「append-only 帳不該少東西」)。
