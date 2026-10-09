severity: major

派工尾端沒有附固定席節點,這項不適用。

我只讀了 spec 與 repo,沒有改任何檔,實驗也沒跑。程式碼 repo 是 `/Users/enzo/orca/workspaces/lumos-toolchain/aspidochelone-reread-block`。

## 逐節結論
- 〈原問題與範圍〉:有 F9,其餘已讀,無 finding。
- 〈設計〉:有 F1 到 F8。
- 〈驗收條款〉S1 到 S13:S8、S9 的分法在現況程式做不到,見 F4。其餘已讀,無 finding。
- 〈實務隱患〉:有 F1。
- 〈回退〉:有 F3、F10。

## 回退節「留著無害」逐項核對
- **`drift-acks.jsonl` 裡 kind=reread 的表態**:舊版程式讀到會直接略過,無害。
  - file: `scripts/lumos:37232`,`_drift_load_acks` 回傳前以 `d.get("kind") in _DRIFT_KINDS` 過濾,不認得的種類被丟掉,不報錯。
  - file: `scripts/lumos:39652`、`scripts/lumos:39722`、`scripts/lumos:39836` 三個讀表態的地方都走這一支。
  - file: `scripts/lumos:39835-39839` 的 doctor 失效表態掃描只收 `_DRIFT_EXPIRING_KINDS`(probe、retire),不會碰到 reread。
- **`governance/reread-verdicts/` 判定紀錄**:spec 沒有改格式,舊版照讀。
  - file: `scripts/lumos:34324` 檔名規則不變。
  - 現有 5 份紀錄的每一列都已有 `text` 欄,新舊版讀法一致。
- **治理帳新增的 note-reread blocked / skipped-env 事件**:無害。
  - file: `scripts/lumos:1600-1608`,`_gate_event` 對事件種類沒有白名單驗證。
  - file: `scripts/lumos:46566`,代碼審留痕只認 gate=code-loop 的事件。
  - 這些事件不在本機帳白名單(file: `scripts/lumos:1363`),會寫進版控帳 `docs/.governance-log.jsonl`,擋人當下會弄髒追蹤檔。這和現有 drift-check blocked 行為相同。
- **只改設定退回 warn 是否完整退回**:不完整,見 F3 與 F10。

## Findings

### F1 合併進主線後才第一次被擋,而且 CI 那一步沒有單次略過
severity: major
blocking: 是(落地後會造成主線反覆紅燈,且 CI 上只能靠新判定或改設定解除)
- spec 段落:〈設計〉重讀第一層、〈設計〉掛鉤與 CI
- 引句:「CI 那一步拿掉 `|| true` 與 `continue-on-error`。」
- 引句:「對照指紋照舊不含筆記自己的內容:筆記改了不必重判,程式改了才要。」
- 場景:
  - 兩個並行分支(本專案常有多個 Claude 會談同時作業)都改了 `scripts/lumos` 與管它的筆記。
  - A 分支在本機推送時,已有判定紀錄涵蓋它自己的程式版本。
  - B 先合進 main。A 再合進 main,合併結果的程式檔 blob 跟 A 判定當時的 blob 不同。
  - 對照指紋的輸入是頂端 about_code 每個檔的 blob,所以指紋變了,舊紀錄全部對不上。
  - main 上 CI 的 reread-check 判成第一層「沒對照」,回 1,main 變紅。
- 壞在哪:
  - CI 的 `reread-check` 步驟有 `if: github.event_name == 'push'`,而 `push` 只觸發在 `branches: [main]`。PR 事件完全不跑這一步,合併前沒有任何訊號。
  - CI 上沒有 `LUMOS_SKIP_REREAD_CHECK` 這種單次略過。
  - 在 main 上修復只有兩條路:再派一次判定者產生新紀錄並提交,或提交一個把 gate 改成 warn 的設定。後者等於整道閘關掉。
  - 同樣的失效也發生在本機 rebase 或 merge 之後:判定者已跑過的紀錄作廢,必須重派。
  - spec 的〈實務隱患〉與〈回退〉都沒提到這個「別人動了同一個程式檔」造成的合併後失效。
- 查證佐證:
  - file: `.github/workflows/ci.yml:4-7`(on.push.branches 只有 main,另有 pull_request)
  - file: `.github/workflows/ci.yml:247-264`(reread 步驟 `if: github.event_name == 'push'`)
  - file: `scripts/lumos:34459-34469`(`_note_reread_contrast_fp` 以頂端 blob 雜湊)
  - file: `scripts/lumos:34969-34971`(`left = [... if fps[rel] not in done]`)

### F2 舊句檢查的新預設無視專案原本調低的總開關 gate
severity: major
blocking: 是(升級後第一次推送就可能誤擋已明確關掉或調成 warn 的專案)
- spec 段落:〈設計〉名稱消失檢查開關、〈設計〉對消費專案的影響
- 引句:「要暫緩的專案在 `.lumos/config.json` 寫 `drift_check.old_sentence` 或 `note_reread.gate` 為 warn。」
- 場景:
  - 某消費專案以前把 `drift_check.gate` 設成 warn 或 off,表示「存量漂移檢查我不要擋」。
  - `lumos update` 之後,`old_sentence` 沒寫,新預設是 block,與 gate 各管各的。
  - 該專案第一次改程式就會被舊句檢查擋下。
- 壞在哪:
  - 同族的 `drift_check.retire` 開關已有明確先例:沒寫時跟總開關 gate,理由是「專案設 gate=warn 只提醒的,升級後不會被新檢查擋」。
  - spec 對 `old_sentence` 反其道而行,卻只用 CHANGELOG 補救,沒有說明為什麼這個開關不照先例。
  - 現有測試已釘住 gate=off 時 m1 仍會跑、仍能擋的行為,所以 gate=off 的專案也會被擋。
  - 逃生路有:改 config 或 `LUMOS_SKIP_DRIFT_CHECK=1`。但這些是事後補救,不是升級前的告知。
- 查證佐證:
  - file: `scripts/lumos:38503-38526`(`_drift_retire_config` 沒寫照總開關 gate)
  - file: `scripts/lumos:38533-38550`(`_drift_old_sentence_config` 各管各的)
  - file: `scripts/lumos:38836-38846`(`_drift_check_c` 在 gate=off 時仍提示 m1 照跑)
  - file: `scripts/test_lumos.py:68364`(gate=off 加 old_sentence=block 回 1)

### F3 「只改設定退回 warn 就完整退回」不成立:終點找不到會回 2,與設定無關
severity: minor
blocking: 否(幾乎只在 git 暫時失敗時發生,單次略過環境變數仍可用)
- spec 段落:〈設計〉判不了的分法、〈回退〉
- 引句:「參數錯(推送參數只給一個、範圍格式錯、終點找不到):回 2(跟 drift check 參數錯一樣)。」
- 引句:「兩道都只要把設定改成 warn 就回到提醒。」
- 場景:
  - `_lens_full_sha` 對任何 git 失敗(逾時、鎖檔、子行程錯)都回 None。
  - 現況的 reread-check 把這種情況當 `_NoteRereadStop`,記 skipped、回 0。
  - spec 把它改歸為參數錯,回 2,而且發生在讀設定之前。
  - 掛鉤對 2 擋下,gate=warn 或 off 都救不了。
- 壞在哪:
  - 暫時性的 git 失敗被當成「參數錯」,擋下訊息會誤導人。
  - 設定退不回去。唯一出路是 `LUMOS_SKIP_REREAD_CHECK=1`,而它的提示 spec 只在「判不了」那一類要求要印。
- 查證佐證:
  - file: `scripts/lumos:44833-44838`(`_lens_full_sha` 在 git 非零或失敗時回 None)
  - file: `scripts/lumos:34931-34934`(現況 tip0 找不到是 `_NoteRereadStop`)
  - file: `scripts/hooks/pre-push:534-537`(掛鉤把標準錯誤丟掉)

### F4 spec 要求的分法,現況的範圍解析函式給不出來
severity: minor
blocking: 否(S8、S9 有測試守,實作時會踩到,但 spec 沒給解法)
- spec 段落:〈設計〉判不了的分法,以及 S8、S9
- 引句:「環境沒有可判的東西(不是 git 專案、沒有圖譜、淺層 clone、範圍沒有新東西、頂端已在主線)」
- 場景:
  - 淺層 clone 與沒有圖譜要回 0。
  - 「讀不到頂端檔案清單(git 失敗)」要在 block 時回 1。
  - `_note_audit_resolve` 的 `reasons` 把這三種都標成同一個種類 `skipped`,只有說明文字不同。
- 壞在哪:
  - 現行檢查把「非 none」全部丟成 stop。
  - 若實作只看種類,要嘛把淺層 clone 的本機開發者全擋住,要嘛把 git 失敗全放掉。
  - 要靠比對說明字串,或改動被三道閘共用的 `_note_audit_resolve`。spec 都沒提。
- 查證佐證:
  - file: `scripts/lumos:33701-33780`(`reasons` 中 skipped 涵蓋淺層 clone、讀不到檔案清單、沒有圖譜)
  - file: `scripts/lumos:34940-34948`(`if kind != "none": raise _NoteRereadStop(why)`)

### F5 擋下當下的逃生提示只涵蓋「判不了」那一類
severity: minor
blocking: 否(出路存在,只是沒有被印出來)
- spec 段落:〈設計〉重讀第一層、第二層、掛鉤與 CI
- 引句:「應回 1 並印原因與 LUMOS_SKIP_REREAD_CHECK」
- 場景:
  - 第一層擋下時只印清單、prepare 指令與一句擋下。
  - 第二層擋下時只印行與照留指令。
  - 兩者都沒有要求印單次略過的寫法,也沒有要求印設定回 warn 的寫法。
- 壞在哪:
  - 沒有判定者可派(額度用盡、離線、純人工貢獻者)的人,看不到不靠 `--no-verify` 的出路。
  - 現有 drift check 的掛鉤在 `exit 1` 前有「逃生:…」整段說明,reread 的新擋下沒有對應。
  - 實際上手寫一份帶 `[]` 的報告就能讓 `reread-record` 過關,但沒有任何說明提到這條路。
- 查證佐證:
  - file: `scripts/hooks/pre-push:493-499`(drift check 擋下時的逃生說明)
  - file: `scripts/hooks/pre-push:530-542`(reread 段目前只有放行訊息)

### F6 工具自己印的建議和第二層矛盾
severity: minor
blocking: 否(擋下後仍有照留指令可走)
- spec 段落:〈做法〉項目⑥「說明文字一起改」的列舉
- 引句:「說明文字、doctor 提示行、`--help`、CHANGELOG 一起改」
- 場景:
  - 記完判定後,`reread-record` 印「確認是誤判就不動——這一版不需要表態」。
  - 照著做的人,碰到被點出的 `RULE:` 行,推送就被第二層擋下,必須額外表態。
- 壞在哪:
  - spec 的清單只寫「寫死預設 warn 或任何情況都回 0」的文字。
  - 這句「不需要表態」不屬於這兩種,容易漏改。
- 查證佐證:
  - file: `scripts/lumos:34899`
  - file: `scripts/lumos:49364`、`scripts/lumos:50288`(`--help` 與指令說明寫「只提醒、恆回 0」)

### F7 第二層何時執行,spec 自己前後不一
severity: minor
blocking: 否
- spec 段落:〈設計〉重讀第二層
- 引句:「候選全部對照過之後才跑。」
- 引句:「第一層與第二層同時成立時兩層都印,記一筆 `blocked`。」
- 壞在哪:
  - 兩句互相矛盾。
  - 若第二層真的要等 `left` 為空才跑,作者補完判定、推送,才會遇到第二層,多一輪提交與推送。
  - 若只對「已對照的那幾篇」先跑,「同時成立」才有意義,但 spec 沒寫。
- 查證佐證:現況 `left` 為空才走 covered 分支(file: `scripts/lumos:34972-34975`)。

### F8 照留表態沒有綁指紋也沒有到期
severity: minor
blocking: 否(設計取捨,但弱於同族的 probe 與 retire)
- spec 段落:〈設計〉照留表態
- 引句:「不收 `--tracked-in`(reread 不在會到期的種類裡)」
- 場景:
  - 作者對 `RULE: X` 表態照留,因為這一版程式判成誤判。
  - 之後程式再大改,新的判定紀錄又點出同一行,而那一行文字沒變。
  - 表態以路徑加原文加種類比對,舊表態繼續生效,第二層不擋,只印出來。
- 壞在哪:
  - 同族的 probe 與 retire 有 30 天到期或綁開著的計劃。reread 完全沒有,表態永久有效。
- 查證佐證:
  - file: `scripts/lumos:37235-37236`(`_drift_ack_key`)
  - file: `scripts/lumos:37543-37559`(`_drift_ack_route` 只對 probe、retire 加 until 或 tracked_in)

### F9 spec 引用的「全是 passed」實際沒有出現過任何候選
severity: minor
blocking: 否(⚠ 這項是證據強度問題,不是行為缺陷)
- spec 段落:〈原問題與範圍〉
- 引句:「名稱消失檢查 35 次跑完、全是 passed,沒有 warned 或 blocked」
- 壞在哪:
  - 我數了 `docs/.governance-log.jsonl` 裡 `check: old-sentence` 的那 35 筆 passed。35 筆的 `candidates` 與 `handle` 都是 0。
  - 這代表檢查在生產上從沒找到過任何候選。
  - 因此這 35 筆既不支持也不反對「改成預設擋」的誤報率,第一次真有候選時才會知道。
  - RETIRE-IF 有「抽樣人工判誤報超過一半」,這是補強,但上線前沒有基線。
- 查證佐證:file: `docs/.governance-log.jsonl`,筆數在這份 repo 的 HEAD 工作目錄實數。

### F10 退回只到 toolchain,消費專案各自仍是舊行為,而且 CI 不隨 `lumos update` 發出
severity: minor
blocking: 否
- spec 段落:〈設計〉對消費專案的影響、〈回退〉
- 引句:「`lumos update` 之後兩道都變預設擋」
- 場景:
  - `lumos update` 只複製 `scripts/lumos`、`scripts/hooks`、`scripts/templates` 與少數工具檔。
  - 不碰 `.github/workflows/*.yml`,也不碰 `.lumos/config.json`。
  - toolchain 即使 revert 了,每個已升級的消費專案要重跑一次 `lumos update`,或各自改設定。
  - 反過來,「CI 照回傳碼擋」只改了本 repo 的 ci.yml。消費專案若有貼 doctor 給的 drift check 步驟,它會因 F2 變紅。消費專案沒有 reread 的 CI 範本,所以 reread 在消費專案只有本機掛鉤那一道。
- 壞在哪:
  - spec 把〈回退〉寫成單一 revert 提交,沒有講消費專案這端要怎麼收。
- 查證佐證:
  - file: `scripts/lumos:22305-22343`(`_VENDORED_TOOLKIT` 與 `_VENDORED_TREE_FILES` 清單)
  - file: `scripts/lumos:22701-22743`(`_vendor_toolchain`)
  - file: `scripts/lumos:39909-39925`(doctor 給消費專案的 CI 步驟只有 drift check)

## 實務隱患鏡頭逐類
- **金流**:無。只動本機與 CI 的檢查回傳碼。
- **對外送出**:無。閘只讀已提交的判定紀錄與表態檔。判定者由編排者另派,不在推送當下。
- **不可逆**:無。擋下只讓推送失敗;表態檔與判定紀錄只追加。
  - 唯一例外是 F1 的「新判定要花判定者額度」,屬成本,不屬不可逆。
- **守衛面**:有。這案本身就是改擋放行為,風險在 F1、F2。
- **並行會談**:有。F1 的合併後失效在並行作業下最容易發生。
- **版本不同步**:有,見 F10。
  - 掛鉤與工具同批複製、同路徑,正常升級不會單獨錯位。
  - 但 `_vendored_pending` 是逐檔 `copy2`,中途中斷或手動衝突解決才可能錯位。我沒有找到具體會錯位的日常場景,所以沒有單獨標出。

最嚴重的是 F1(合併後主線第一次被擋,CI 沒有單次略過)與 F2(舊句檢查新預設無視專案原本調低的總開關),blocking 共 2 條。
