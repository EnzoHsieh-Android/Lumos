severity: major

我只查了 spec 和 `prepush-collect` 這個 repo,沒有跑任何測試。固定席節點:派工尾端沒附,所以不逐條判。「已讀,無 finding」的段落:緣起、PRIOR-ART、前提壞掉照舊立刻停(第 3 點)、S3,和前掃已折的 10 處(未推翻)。

**finding 1:新掛鉤搭舊版 lumos 時,代碼審那一道會被靜默放行**
- spec 段落:做法第 4 點、S6。
- 引句:「收集模式下,任何一道記下的擋下最後都應讓掛鉤回 1——沒有一條路徑能把擋下變成放行。」
- 問題:掛鉤改成帶 `--collect` 呼叫 `code-loop check`。舊版 lumos 不認得這個參數,會回 2。
  - file: `scripts/hooks/pre-push:488-512`。掛鉤只認 `cl_rc -eq 1` 才擋,註解寫明「rc≠0/1 … fail-open 放行」。呼叫是 `2>&1` 吞掉輸出,後面只 grep「提醒」,所以連錯誤訊息都看不到。
  - 同型的先例:file: `scripts/lumos:36976`。`core.hooksPath` 是絕對路徑,所有工作樹共用主工作目錄那份掛鉤,掛鉤和工具版本常常對不齊,`--gate` 就出過一次。
- 殘局:
  - 部分更新或回退時,代碼審留痕、表態、新增告警、合約測試四道一起放行,而且沒有任何痕跡。
  - S6 的測試只能在掛鉤和 lumos 同版時驗,抓不到這種版本錯位。
severity: major
- blocking: 是 — 擋下變放行的路徑真實存在,正面推翻 spec 自己的 S6 宣稱。

**finding 2:舊掛鉤搭新版 `push-preview` 會真的跑全套測試;`LUMOS_PUSH_PREVIEW` 漏進真推送會變成放行**
- spec 段落:做法第 5 點、S5。
- 引句:「掛鉤看到它,到統一判斷那一步就停:有擋下回 1,沒有回 0」
- 問題:預演完全靠掛鉤認得環境變數。
  - 掛鉤沒更新時(同 finding 1 的版本錯位),它不認得這個變數,會一路跑完約 8 分鐘全套測試。這違反 S5 的「不應跑任何測試」,指令卻照樣印結果,看起來正常。
  - 掛鉤更新後,真推送時只要環境裡有這個變數(shell profile、alias、AI 會談 export 都可能),掛鉤在測試前回 0,推送放行、測試沒跑,也沒有留痕。
- 殘局:
  - 沒有版本交握。spec 沒有要求預演確認掛鉤版本,也沒有要求掛鉤在非預演的情境(例如 stdin 不是 push-preview 組的)下忽略這個變數。
  - 退掉 `push-preview` 後,掛鉤裡這個「測試前回 0」的分支如果沒一起拿掉,它就變成永久殘留的無痕繞道。
severity: major
- blocking: 是 — 一個沒有痕跡的環境變數就能讓推送閘少跑全套,而 S6 聲稱沒有這種路徑。

**finding 3:預演會寫入版控帳與逃逸帳,spec 卻把它當成唯讀**
- spec 段落:實務隱患「已排除:對外送出」、做法第 5 點。
- 引句:「已排除:對外送出:預演不推送;只有真推送才連遠端,行為照舊。」
- 問題:預演帶著完整掛鉤路徑,有兩處會寫檔。
  - file: `scripts/lumos:1639`。`doctor --ci` 會往 `docs/.governance-log.jsonl` 追加,這個檔是版控的(本會談 git status 開場就顯示它已被改)。
  - file: `scripts/hooks/pre-push:460-470`。`loop escape --auto` 會寫 `.escape-log.jsonl`。
  - spec 做法第 4 點還特地規定「收集模式同時印出時各記一筆」,預演每跑一次就多記一輪。
- 殘局:
  - 預演把工作目錄弄髒。被弄髒的檔也在簿記清單裡,「簽名檔沒提交」和 `git status` 的判斷會因此多出雜訊。
  - 逃逸帳的筆數會被預演灌水。file: `scripts/lumos:3245-3246` 用這個帳的筆數當退回門的門檻(`push-gate-unreviewed ≥2` 就重審門判定),所以預演會推動別的機制退場。
  - 退掉 `push-preview` 後,這些殘留的帳要人工分辨哪筆是預演寫的。⚠ 寫側有 dedup(`scripts/lumos:504` 一帶),我沒驗它是否涵蓋重複預演。
severity: major
- blocking: 是 — 唯讀預演會污染決定其他機制去留的量測帳,收拾時分不出真假。

**finding 4:RETIRE-IF 的量測沒有資料來源,撤除條件是空的**
- spec 段落:RETIRE-IF。
- 引句:「RETIRE-IF: 上線 8 週內,被擋的推送裡」
- 問題:條件要數「被擋的推送裡一次列出兩個以上原因的次數」,但現有帳量不到。
  - file: `scripts/lumos:9379` 前後的 `_STATS_ABSENT_DISCLAIMER` 寫明:本帳看不到硬擋事件,`anchor verify` 擋下 push 時不寫任何帳。簽名檔沒提交、`home check`、`note-shape` 等的擋下同樣沒有事件。
  - spec 沒有要求新增「某次推送(`LUMOS_PUSH_ATTEMPT`)的擋下數」事件。彙總只印到 stderr,不落帳。
  - 也沒定義分母:預演會不會算,`--no-verify` 繞過的算不算。
- 殘局:
  - 8 週後無人能回答「次數是 0 嗎」。「帳裡沒有」和「沒發生」分不出來,條件永遠不會被判成立,收集邏輯也撤不掉。
  - 照 CLAUDE.md 鐵則 4,寫不出可量測的撤除條件就是還沒想清楚。
severity: major
- blocking: 是 — 撤除條件沒有可量的資料來源,等於沒有撤除條件。

**finding 5:S6 的守衛只驗兩道閘,其餘每個替換點被吞掉時沒人發現**
- spec 段落:實務隱患「守衛面」、S1 與 S6。
- 引句:「所以只用一個共用函式記、一處判(S6),每一處原本的 `exit 1` 都換成同一個呼叫,測試拿兩道真的閘驗。」
- 問題:替換點有 9 道閘,另有逐 ref 迴圈裡的多個點(`spec-gate` rc1 還夾在 `_suite_this` 的判定中間)。測試只拿兩道真的閘驗,其餘 7 處某一處漏換或換錯,就是一道閘被吞掉。
- 殘局:
  - 上線後發現「某道閘被吞掉放行」時,掛鉤本身不寫帳(同 finding 4),只能靠使用者發現「本該被擋的推送進去了」,再事後比對。
  - 沒有逐閘的紅綠測試,也沒有「每個閘各自擋得下」的對照,回退的觸發訊號根本沒有。
  - 這是同族缺口,應逐閘各一支測試,不能只驗兩道。
severity: major
- blocking: 是 — 守衛面的核心風險只驗了 9 分之 2 的路徑。

**finding 6:回退段只講還原提交,沒講消費專案怎麼拿回舊版**
- spec 段落:回退。
- 引句:「還原提交即可回到遇錯就停;」
- 問題:消費專案的掛鉤是 `lumos update` 用逐位元組比對複製過去的。
  - file: `scripts/lumos:24158-24170`(`_vendored_pending`)。
  - file: `scripts/lumos:25744`。`scripts/hooks/pre-push` 在 `ANCHOR_FILES` 裡,消費專案如果有 `governance/anchor-baseline.json`,掛鉤位元組一變,`anchor verify` 就不符。
- 殘局:
  - 上線時要重新簽名一次,回退時又要簽一次。簽名檔沒簽就 push 會被擋。
  - 這件事沒寫進回退步驟,也沒提醒「還原後要在每個消費專案重跑 `lumos update`,再 `anchor approve`」。
  - `core.hooksPath` 指向主工作目錄時,別的工作樹會長期停在新舊錯位狀態(同 finding 1)。
  - 實務隱患的「已排除:不可逆」只涵蓋 lumos repo 本身,沒涵蓋這條消費專案的路。
severity: major
- blocking: 是 — 回退流程缺漏,消費專案會被簽名檔擋住,且處理步驟沒寫。

**finding 7:退掉後留下的文件與習慣殘留,沒有清單**
- spec 段落:舊裁定的第二段。
- 引句:「實作時在 #12 那段旁註記被本計劃取代。」
- 問題:
  - 撤掉本機制後,`全repo審視_計劃` #12 那段旁邊的「被本計劃取代」註記仍在,和程式現況相反。
  - `push-preview` 如果已被使用者養成習慣,也會留下「預演回 0 就等於推得上去」的錯誤印象。spec 有說「回 0 不代表測試綠」,但退掉預演時沒有對應的清理項。
  - `lands_in` 的 `bound-tests-gate` 與 `pitfalls-code-loop` 兩個家,同樣沒有「撤除時一併改回」的清單。
  - CI 本身不受影響:file: `.github/workflows/ci.yml:186` 不帶 `--collect`,輸出維持第一個原因,兩邊在退回時不會互相不一致。
severity: minor
- blocking: 否 — 只是文件殘留,不影響閘的行為。

最嚴重 severity:major,blocking 共 6 條(finding 1 到 6)。
