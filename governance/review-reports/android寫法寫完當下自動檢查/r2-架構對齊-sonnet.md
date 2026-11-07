severity: major

這份是第 2 版修訂稿的架構對齊審查。對照過 `scripts/lumos`、`scripts/hooks/claude/check-graph-sync.py`、`impact-hook.py`、`memory-sweep.py`、`merge-claude-settings.py` 和相關 Systems 筆記。我沒有改 repo 裡任何檔。

## 問 1:分層與依賴方向

整體方向跟既有一致,沒有跨層直呼。
- 鉤子用子程序呼叫 `lumos lint-new`,跟 `check-graph-sync.py:750` 呼叫 `lumos impact` 同形。
- `lint-new` 呼叫 `_lint_new_verdict`。`code-loop pass` 內部呼叫 `_codeloop_guard_verdict(keep_going)`,沿用 `scripts/lumos:71456`。
- 鉤子沒有 import 主程式,主程式也沒有反向依賴鉤子。

分層本身沒問題,但有三處「同一件事兩個做法」,放在問 3。

## 問 2:命名與錯誤處理

F7 是新發現。命名方面,`lint-new` 與既有的 `lint-check`、`lint-waive`、`lint-watch` 同族。環境變數 `LUMOS_STOP_LINT_OFF` 對應既有的 `LUMOS_STOP_BLOCK_OFF`。設定鍵 `lint_new.gate` 與 `scripts/lumos:39920` 一致。標記目錄 `stop-turn/` 走既有的 `_cache_dir_under_home`(`check-graph-sync.py:768`)。`row-<D-n>` 沿用 `impact-hook.py:825` 的 `_voice_once` 寫法。這些都對齊。

### F7
severity: minor
blocking: 否
引句:「最多 10 條、整段最多 1500 字,結尾一行教放行指令」
- 既有擋下原因第一行固定是 `STOP_BLOCK_HEAD`(`LUMOS-STOP:改了程式碼但知識筆記沒跟著動`),見 `scripts/hooks/claude/check-graph-sync.py:766` 與 `:934` 的 `stop_block_reason`。
- 計劃只說「兩段接起來」,沒說新這道有沒有同形的固定標頭。
- 兩段併成一則訊息時,模型與測試要靠標頭分辨是哪一道。
- 建議條款寫明標頭,例如 `LUMOS-STOP:`。

## 問 3:第二種做法

### F1
severity: major
blocking: 是
引句:「先剝掉 Kotlin 的註解與字串字面值(`_kotlin_strip`,新增,兩案共用」
- 既有的剝註解與字串掃描只有一支 `_strip_c_comments`,位置在 `scripts/lumos:6820`。
- 它的 docstring 明寫「全庫只有這一支……不留兩套掃描」,並有測試 `t_strip_c_comments_shared_and_linear` 釘著。
- 它已支援 `blank_strings`、`keep_newlines`、`keep_length` 三個參數,正好是「換成空白、換行保留」的語意。
- 計劃另寫 `_kotlin_strip`,理由是巢狀 `/* */` 與 `${…}`,卻沒說為什麼不擴充既有那支。
- 這是第二套掃描器,而且已被既有決策明確否決過一次。

### F2
severity: major
blocking: 是
引句:「再用 `_kt_trigger_re`(新增,兩案共用的觸發字比對)比」
- 「改 kt 檔時,把表裡命中的列推給模型」已經有既有做法,且已經在 Android 上線:
  - `cmd_impact` 在 `scripts/lumos:65256-65262` 收鉤子送的 `delta_text`,對棧別提問題表做適用性比對。
  - 比對函式是 `_stack_applicability`(`scripts/lumos:38530`),用 `_stack_norm_line` 先剝註解與字串。
  - 每題一組 pattern 的觸發規則是 `_STACK_TRIGGERS`。
- 計劃另起 `decision_rows` 這個回傳鍵、`_kt_trigger_re` 觸發比對、`pushed_rows` 同會談去重。
- 結果是同一次 `.kt` 編輯有兩條平行的「命中表列就推」通道,各有自己的剝字串與觸發語法。
- 計劃只把〈棧別提問表態閘〉列入 `lands_in`,沒說兩者的分工。
- 這條已經超出風格偏好。請編排者要求設計說明:為什麼決策表列不是 `_STACK_QUESTION_SPECS` 的一種,或兩條通道的觸發字語法如何不重疊。

### F3
severity: major
blocking: 是
引句:「而且檔案修改時間晚於這個會談的回合時間戳」
- 同一支鉤子 2026-09-18 已經裁過:清單改問版本控制,「核心代價=不再宣稱切得出『這一輪』,措辭改口成工作樹語意」。出處是 `docs/lumos-toolchain-knowledge/Systems/graph-sync-coverage.md:21` 與 `:52`,對應程式在 `check-graph-sync.py:330` 的 `_git_status_entries`。
- 計劃在同一支鉤子裡重新引入「這一回合碰過的檔」。做法是用 mtime 加 `stop-turn/` 回合時間戳,等於同一檔裡有兩套「要看哪些檔」的定義。
- 計劃有給理由:新增告警要分清是誰寫的。但它沒引用 09-18 那條決策,也沒說明為什麼這道不能用工作樹語意。
- 要求計劃補一句與既有決策的關係(承接或翻案)。並在 `graph-sync-coverage` 筆記寫清兩道的檔集定義不同。

### F4
severity: major
blocking: 是
引句:「收到 SIGTERM 時:結束自己開的每個檢查工具的程序群組」
- 既有收程序只有一種做法:`scripts/lumos:26638` 的 `_kill_proc_group`(`killpg` 加 SIGKILL、Windows 退回殺子程序)。`memory-sweep.py:936` 也是 `killpg` 加 SIGKILL。
- `lumos` 裡完全沒有 `signal.signal`,也沒有任何程式接 SIGTERM。
- `Systems/hook逾時預算.md` 的 KEY 還有一條「超時不殺子行程,到時間放手」。
- 計劃新增兩樣東西:
  - 鉤子送 SIGTERM,等 1 秒再送 SIGKILL。
  - `lint-new` 自己接 SIGTERM 並清快照。
- 孫程序需要先 TERM 讓中間層清理,這個需求成立。但計劃沒說在 SIGTERM 處理器裡重用 `_kill_proc_group`。
- 它也沒說這條與「超時放手」的分界是什麼:這道不快取,所以必須殺。
- 建議條款明寫重用 `_kill_proc_group`,並在 `hook逾時預算` 記這個例外。

### F5
severity: minor
blocking: 否
引句:「payload 多三個鍵:`delta_new`(只放寫入的新內容」
- `impact-hook.py:417` 的 `extract_delta_text` 與 `:439` 的 `extract_delta_query` 已經各自寫了一份相同的 Edit / MultiEdit / Write 分支。
- 新增 `delta_new` 會是第三份。差別只在去掉 `old_string`,上限改 2 MB 且超過就不放。
- 鉤子組 payload 的位置在 `impact-hook.py:1027`,已經送 `delta_text`。
- 較整齊的做法是抽出共用的取段函式,加一個「只要新內容」參數。

### F6
severity: minor
blocking: 否
引句:「沿用既有 `_handoff_files` 那一族的 `git --no-optional-locks status --porcelain=v1 -z --untracked-files=all` 解法」
- 既有各處(`scripts/lumos:72868` 的 `_handoff_files`、`:50943`、`:69205` 的 `_porcelain_z_paths`)都沒有 `--no-optional-locks`。
- 各自內嵌解析,沒有「回狀態碼加新舊路徑」的共用函式。
- 計劃說的「沿用」只對到 `-z` 與 `-uall`。`--no-optional-locks` 是新旗標,而「改名的舊路徑」解析又要再寫一份。
- 方向不衝突,但屬於第 4 份內嵌解析。建議抽共用函式,或把「沿用」措辭改準。

## 問 4:落點

- 〈改檔前推播〉有寫負責範圍,負責鉤子「印」。比對在 lumos 做,放進〈棧別提問表態閘〉(about_code 含 `scripts/lumos` 與 `impact-hook.py`)合理。前提是先處理 F2。
- 〈graph-sync-coverage〉管 `check-graph-sync.py`,放鉤子共用機制合適:`stop-turn/`、`_BUDGET_START` 改成開跑就記、55 秒。
- 〈hook逾時預算〉放 40 到 55 秒的調整合適。它 `about_code` 是空的,正好當單源。
- 新開〈回合結束寫法檢查〉合理。它不能在 `about_code` 用反引號寫別人的檔,要用連結指到〈graph-sync-coverage〉。
- ⚠ 交編排者:〈pitfalls-code-loop〉已有 312 行、20 行 KEY、沒寫負責範圍,而計劃說「新增告警閘本體的說明在」它那裡。
  - 計劃再塞進去的有:`lint-new` 指令、工作樹終點、自動執行白名單(含資安判斷)、`code-loop pass` 先查。
  - 這些超出該篇的負責範圍,而且 Systems 底下沒有任何「新增告警閘」專篇。
  - 我傾向建議另開一篇,例如「新增告警-工作樹檢查」,`pitfalls-code-loop` 只留連結。
  - 這是範圍判斷,我不硬判。

## ⚠ 判不準,交編排者

1. **鉤子放哪支檔。** 「寫法檢查」是另一種關注點,卻塞進名叫 `check-graph-sync.py` 的檔。
   - 既有慣例是一支鉤子對一個關注點,`HOOK_BUDGET` 也是一檔一值(`scripts/merge-claude-settings.py:110`)。
   - 計劃以「Claude 與 Codex 共用」與「預算共算」為由合併。
   - 是否拆成另一支 Stop 鉤子,要看兩支能否各自擋停、各自佔預算。我無法從既有做法判定。
2. **rc3 的語意。**
   - 既有 `env-unavailable` 在推送前閘是自動放行(rc0 並記帳),見 `scripts/lumos:40290` 的 `_lint_new_classify` 與 `:71413`。
   - 計劃的 `lint-new` 對同一狀態回 rc3。這是新指令自己的語意,沒有既有指令可對。
   - `scripts/lumos` 裡 rc3 另有「vault 找不到」的意思(`:21675`)。
   - 計劃在 S2 已寫明八種狀態對 rc 的對應,內部一致,所以不當 finding。

不對齊共 7 條,其中 major 4 條(F1、F2、F3、F4)。另有兩條 ⚠ 不計入。
