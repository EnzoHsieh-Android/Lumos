severity: blocker

# mp-r1 正確性席審查(sonnet)

走一遍結果:
- #28(範圍 d0b24391..b0b48b7b、branch=main):`b0b48b7b` 母為 d0b24391、5dbb85e0;我在臨時 clone 跑 `git merge-tree --write-tree d0b24391 5dbb85e0` rc=0、樹 8cb3ec47 等於 `b0b48b7b^{tree}`;b0b48b7b 的治理帳裡 afb7115c 那筆 passed(branch=cap-retro)在最近 5 筆 pass/skip 內,afb7115c→5dbb85e0 只動簿記檔 → 照 spec 會放行。
- 「合進來那側根本沒審過」的合併:第二個母沒有有效紀錄 → 照舊擋,這格 spec 有寫。
- 但「合進來那側審過、第一個母沒審過」的合併(F1)照 spec 也會放行,這是洞。

## F1 只驗第二個母,沒驗第一個母(目標側)本身審過,可夾帶未審代碼放行
severity: blocker
blocking: 是 — 守衛放寬後,未審的高風險代碼可零留痕進線,等於繞過閘
spec 段落:範圍第二、三條與「守衛面」
引句:「若目標是上面那種合併提交,改在治理帳裡找「任何分支」的 pass/skip 紀錄」
引句:「目標版本是恰好兩個母的合併提交,而且 `git merge-tree --write-tree 母1 母2` 回傳碼是 0」
問題:spec 的信任模型是「第一個母=目標分支已驗過的既有線、第二個母=合進來那側已審」,但程式裡沒有任何一條要求第一個母是已驗過的。條件只有「樹 = 兩母自動合併」+「第二個母有有效紀錄」。
具體例 A(推主線一次推多個提交):本機 main 上先提交 A(高風險、未審),再 `git merge feature`(feature 頂端有有效 pass)得 M,母=(A, feature頂)。推 main,範圍 before..M,tier=high。`_codeloop_read(main)` 無有效紀錄 → 走新路徑:merge-tree(A, feature頂) rc0、樹等於 M 的樹、feature 頂端有效 → 放行。A 沒任何審查就進了主線。應該:要求第一個母等於診斷範圍起點(`diff_range` 左端,CI 即 `github.event.before`、pre-push 即 remote_sha),不等就回 None 並講「第一個母不是被推送的既有頂端」。#28 滿足這個條件(第一母 d0b24391 即 before),所以加了不影響它。
具體例 B(方向反過來,非主線分支):在 feature 分支上 `git merge main`(或 GitHub「Update branch」按鈕)得母=(feature 本機頂, main 頂)。第二個母=main 頂,主線上對它通常有有效紀錄;feature 本機新增的高風險提交沒審,推 feature 時 pre-push 對 refs/heads/* 都叫 check(file: `scripts/hooks/pre-push` 的 _rbranch 段),目標分支留痕過期 → 新路徑認 main 的紀錄 → 放行。repo 現況就有這種合併:`afb7115c` 母=(9fc5a4df, d0b24391)正是 main 合進 cap-retro。應該:同例 A 的第一母=範圍起點規則;或明講只在 branch 為主線時啟用並寫進驗收。
S1/S2 的測試格也沒有「第一母未審」這格,S1 要加。

## F2 「任何分支」+ 只看最近 50 筆:範圍不明,可能錯過 #28 型紀錄,也可能認到無關分支
severity: minor
blocking: 否 — 只會多擋或訊息不準,不會多放
spec 段落:範圍第二條、實務隱患「效能」
引句:「依帳本行序由新到舊、最多看最近 50 筆;找到就放行」
問題:「50 筆」是帳本所有行、還是只算 code-loop 的 passed/skipped 行?帳本在 b0b48b7b 有 120201 行,passed/skipped 且 gate=code-loop 共 403 筆。若算所有行,afb7115c 那筆之後就有別的帳(anchor、anchor-approve 等)擠進來,若再有幾十行非留痕事件,#28 型紀錄會掉出視窗而照舊擋。另「任何分支」也會認到無關分支的紀錄,只要 sha 對第二個母有效即可(有效性由祖先關係擔保,可接受,但應寫明這是刻意的)。要寫明:先過濾 gate=code-loop 且 kind 為 passed/skipped、再取 50,並照 `_codeloop_read_from_ledger` 的 kind 雙重驗證(file: `scripts/lumos:45517`)。

## F3 帳本是 append-only,兩邊都追加就必衝突,功能實際涵蓋面比敘述小
severity: minor
blocking: 否 — 衝突時 spec 已規定回 None 照舊擋,安全方向
spec 段落:天花板 1、範圍第一條
問題:我在臨時 repo 實驗:兩邊各對同一檔末尾追加一行,`git merge-tree --write-tree` 回 rc=1(CONFLICT)。`docs/.governance-log.jsonl` 每次 pass 都 append,只要主線在分支最後一次合入主線之後又有人記帳,合併就衝突、被迫手解,於是「乾淨合併」只在分支剛好合過主線(#28 就是 afb7115c 剛合入 #24–#27,其留痕詳述也寫「合併只有帳本與放行清單衝突」)時成立。天花板 1 只講「解過衝突的還是要補審」,沒講最常見的衝突來源是簿記帳本。建議:決定是否容許「只有簿記檔衝突」(spec 沒寫,也別暗示會涵蓋),或在天花板明寫此限制,免得下一個合併又紅、被當成新 bug。

## F4 判定插入位置、期限與判不了的處置沒講清
severity: minor
blocking: 否 — 實作時可補,不影響放寬方向的正確性
spec 段落:範圍第二條、實務隱患「效能」
引句:「整段給一個總預算(照表態閘既有的時間預算),超過就停、照舊擋並講原因」
問題:(a) `_codeloop_guard_verdict` 的審查留痕段(file: `scripts/lumos:47094`)在「留痕過期」分支之後才走 `_codeloop_marker_skipped` 與回 blocked;新路徑必須插在這兩者之前、且對「無紀錄」「紀錄過期」兩支都接,spec 只說「找不到有效紀錄時」沒寫位置。(b) `_codeloop_record_valid` 只回二元組、沒有 deadline;要共用預算得用 `_codeloop_record_valid_ex(…, timeout=剩餘預算)`(file: `scripts/lumos:46538`),其第三值 unsure=True(逾時、淺 clone 缺歷史)spec 沒說是跳過該筆繼續找還是整段停;淺 clone 時 merge-tree 也會出錯,走「git 出錯」格即可,但應寫測試。(c) 表態那關的預算 `_DISP_BUDGET=20` 秒是表態自己的,兩關各算一份還是共用,spec 沒定。
具體例:CI 淺 clone 下 afb7115c 找不到 → ex 回 unsure → 若被當「無效」繼續找最多 50 筆,每筆都 TimeoutExpired 級的慢,拖到預算才報,訊息會誤導成「沒有有效紀錄」。應該:unsure 一律中止並報「判不了(淺 clone/逾時)」。

## F5 表態那關「同一條規則」沒處理適用題範圍與讀帳函式
severity: minor
blocking: 否 — 錯在多擋,不會多放
spec 段落:範圍第三條、驗收 S2
引句:「目標分支的表態紀錄沒有或過期時,同樣去找對第二個母有效的表態紀錄。」
問題:(a) 既有 `_codeloop_read_dispositions` 只讀指定分支且最後一筆(file: `scripts/lumos:46486`),spec 只為留痕寫了「新寫一支讀帳函式」,表態要另一支(kind=dispositions、事件結構不同、要回 dispositions 欄),沒說。(b) 推主線時表態的適用題用推送範圍算(`_codeloop_guard_verdict` 的 disp_range),合進來那側的表態是針對該分支 merge-base..第二母 的題;推送範圍多出的題在對方紀錄裡「缺表態」→ 擋,安全但會讓「第一母有改動」的合併總是被擋,應在 S2 寫一格。(c) 表態有效性只驗 head_sha 座標,證據(test:/path:line)是對 at_sha=合併提交的樹驗,合併樹與第二母樹相同處沒問題,有手改處已被樹相等條件排除,這一點是對的。

## F6 驗收測試太薄:兩條件「各一格」之外缺關鍵格
severity: minor
blocking: 否 — 屬補測試
spec 段落:實務隱患「守衛面」、驗收條款 S1
引句:「兩個條件各有一格測試證明少一個就照舊擋(同一支測試的不同格)」
問題:列出的格是「手改/衝突/三母/無紀錄/舊紀錄」,缺:第一母未審(F1)、`merge-tree` 逾時/git 太舊(spec 範圍有寫行為但 S1 沒列)、紀錄是 skip 而非 pass、紀錄在別的分支但對第二母有效、unsure(淺 clone)、50 筆視窗邊界(F2)。另 merge-tree 會讀本機/CI 的 git 設定與屬性(merge driver、merge.renormalize、rename 偵測),本機與 CI 判定可能不同——不同只會讓某一邊多擋,不會多放,但驗收應寫明「CI 判紅而本機放行」是可能的、以 CI 為準。

## 逐節
- frontmatter/WHY/白話/依據/名詞/PRIOR-ART/RETIRE-IF:已讀,無 finding(交叉引用的 `Issues/code-loop-pass自失效追尾`、`Systems/bound-tests-gate`、`Systems/pitfalls-code-loop` 節點都存在;b0b48b7b 母、merge-tree rc0、樹相等、afb7115c 記在 cap-retro 皆實測屬實)。
- 範圍:F1、F2、F4、F5。
- 實務隱患:
  - 「信任誰的紀錄」一句「沒有新的外部輸入」不成立:新路徑讓「別的分支的紀錄」變成放行依據,信任面比「只認目標分支」寬,正是 F1 的來源。
  - 舊紀錄誤認:機制成立(afb7115c 之前的 866f3213 在程式變動後被 record_valid 判無效),無 finding。
  - git 版本:`git version 2.39.2` 支援 --write-tree,無 finding;<2.38 回非 0/非 1 的格 spec 有寫。
  - 效能:見 F2、F4。
  - 金流/對外送出/不可逆:已讀,同意排除(只改判定、不寫資料、不連網)。
  - 平行路徑:推送前掛鉤與 CI 呼叫同一支 `_codeloop_guard_verdict`,不需改腳本,這點對;但兩條路的「被推送分支」不同(F1 例 B)。本機 marker 檔 vs 治理帳:`_codeloop_read` 先看 marker 檔,新路徑只讀帳,與 CI 一致,無 finding。squash/章魚已明確排除。
- 驗收條款/回退/天花板:S1、S2 見 F6、F5;天花板 2(#28 紅燈不會變綠)屬實,因 CI 跑的是該提交當時的舊程式。

總結:最嚴重 severity 為 blocker;blocking 條數 1(F1)。
