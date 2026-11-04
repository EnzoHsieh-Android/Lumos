severity: minor

先講結論:做法 1(祖先過濾)在正常輸入上跑得對,git 回傳碼的行為也和 spec 寫的一致(0 是祖先、1 不是、被清掉的提交回 128)。但在極端輸入上有幾個沒擋到的洞。做法 2(改數次數)、做法 3(三引號常值)我實測過,都站得住,只剩一處既有條款被悄悄放寬。做法 4 對「只動考場分支」的宣稱不準。

派工尾端沒有附上合約或事故節點,固定席無從逐條判。我自己查了兩篇相關節點,結果寫在第 1、7 條和實務隱患鏡頭。

已讀各節:名詞、問題與最小解、做法 1 到 4、驗收條款 S1 到 S6、回退、實務隱患。交叉引用的 `[[Projects/紅燈版實跑三缺口_計劃]]`、`[[Projects/規格閘紅燈測試快照_計劃]]`、`Systems/規格閘`、`Systems/test-guard` 都存在。

1. 淺複製下,提交物件存在但歷史被截斷時,`--is-ancestor` 回 1,spec 會把真正的祖先丟掉。
severity: minor
   blocking: 否 這只在淺複製加上物件剛好存在的組合才發生,不處理也不會做出壞系統。
   引句:「查不到而且 repo 不是淺複製(`rev-parse --is-shallow-repository` 回 false)就丟(完整 repo 裡不存在的提交不可能在 HEAD 的歷史上);淺複製照舊留」
   重現:把 `--depth=1` 的複製再 `git fetch --depth=1 origin <main~2 的完整編號>`。該提交物件存在,`merge-base --is-ancestor <編號> HEAD` 卻回 1。在完整 repo 裡同一對提交回 0。
   壞在哪:spec 的淺複製保險只掛在「rc 非 0/1」(物件不存在)那條路,但淺複製下 rc 1 也不可信。這筆紀錄會被丟掉,而不是照舊留。
   file: `scripts/lumos:64679` `_lens_git_dl` 與 `scripts/lumos:64687` `_push_rev`,只能分出 rc 128 與物件是否存在,分不出「物件存在但歷史被截斷」。

2. 沒有出生提交的 HEAD(例如 `git checkout --orphan`)時,別條分支的紀錄照樣漏過來,等於修了等於沒修。
severity: minor
   blocking: 否 這是非典型操作,影響範圍小。
   引句:「其他回傳碼(提交物件不存在時是 128):再用既有的 `_push_rev` 問那個提交在不在——查得到但判不了照舊留」
   重現:有主線提交的 repo 裡 `git checkout --orphan x`,HEAD 沒有出生提交。此時 `merge-base --is-ancestor <別分支的提交> HEAD` 回 128(`Not a valid object name HEAD`),`rev-parse --verify <那個提交>^{commit}` 回 0。流程走到「查得到但判不了照舊留」,全部漏過。
   同一個狀態下,`_redbase_branch_rows` 先做 `head = _lens_full_sha(rr, "HEAD")` 會得到 None、fork 也是 None,等於把整本帳都當這條分支的。
   順帶一個定義不準:名詞節寫「git 叫不起來時不寫這欄」。實測沒有出生提交的 repo 呼叫 `_gate_event` 會寫入 `"head_sha": "HEAD"`(`commit` 欄也是 "HEAD")。這個情況靠 `_LENS_SHA_RE` 擋下照舊留,結果無害,但名詞節對不上程式。
   file: `scripts/lumos:1830` 附近 `_gate_event` 補 head_sha 的那段(`_sp_run_text` 不看回傳碼,rc 128 時 stdout 仍是 "HEAD")。

3. `head_sha` 不是字串(手改或別版本寫出 `123`、`null`、`["a"]`、`{}`)時,spec 沒規定怎麼辦,照字面實作會崩。
severity: minor
   blocking: 否 只有帳被手改或壞掉時才發生,但崩的位置在規格閘主路徑上。
   引句:「沒有 head_sha、不像提交編號(既有的 `_LENS_SHA_RE`)、git 叫不起來或過了截止時間,照舊留」
   重現:帳裡有一行 `{"kind":"spec-gate-green","head_sha":["a"],...}`。做法 1 要「把各筆的 head_sha 去重」,實測 `set([["a"]])` 會丟 TypeError。對 int、None、list、dict 呼叫 `_LENS_SHA_RE.match(...)` 也都丟 TypeError。
   壞在哪:呼叫點 `_redbase_attach` 只 `except OSError`,TypeError 會一路崩成 traceback,規格閘那次留痕就沒寫成。spec 要把「非字串」明寫成照舊留,並且先判型別再去重。
   file: `scripts/lumos:14510-14513` 是 `_redbase_attach` 對 `_redbase_branch_rows` 呼叫端的 `except OSError`。

4. 截止時間與 200 個上限的說明,和逐筆「照舊留」的規則互相矛盾;200 個上限在最需要修的情境反而會讓修法失效。
severity: minor
   blocking: 否 都是只出聲、不改判定的降級,但行為沒說清楚會被實作者各自詮釋。
   引句:「過了截止時間或超過 200 個時印一句說明,講這一批照舊沒過濾。」
   矛盾點:做法 1 前一條是逐筆處理(沒時間的那一筆照舊留),這句卻說「這一批」沒過濾。實作成逐筆時,截止前已經丟掉的紀錄和說明講的對不上,而且結果取決於機器快慢。
   200 上限:實務隱患寫「一條分支的判綠紀錄通常不到十筆」,但這是帳進版控時的算法。bug 發生在帳被忽略時,工作目錄的帳是所有分支累積的。本 repo 現有帳裡規格閘留痕有 74 筆、56 個不同的 head_sha,而且只增不減。帳被忽略的專案累積到超過 200 個不同 head_sha 後,過濾整批停用,等於 bug 回來。
   file: `scripts/lumos:14367-14393` 是 `_redbase_branch_rows`,在帳被忽略時 fork 為空樹,讀整本工作目錄的帳。

5. 做法 4 說「只動考場本機分支」,回退也只寫「git 還原 lumos 那幾支檔」,這兩句與 `lumos update` 實際寫的範圍不符。
severity: minor
   blocking: 否 考場主目錄的未提交改動確實不會被碰,但回退說明不完整。
   引句:「考場本機分支跑 `lumos update`,照 S5 的判準看 `lumos loop escape --list`;不推、不併,也不碰 mOrangePos 主目錄(那裡有別人的改動)。」
   事實:`_vendor_toolchain` 會做三件不在分支上的事:
   - `git config core.hooksPath scripts/hooks`,寫的是共用的 repo 設定。
   - `_sync_global_from_project` 覆寫 `~/.claude/hooks`、`settings.json` 與 `~/.codex`,整台機器所有專案都受影響。
   - 對來源 repo 做 `git pull`。
   `git` 還原考場分支的檔案,救不回這些全域改動。spec 的回退節要補上「怎麼把全域 hooks 還原」,或把宣稱改成「分支檔案之外還會動全域 hooks 與 core.hooksPath」。
   file: `scripts/lumos:32786`(`_vendor_toolchain`)、`scripts/lumos:32800` 呼叫 `_set_hooks_path`、`scripts/lumos:32827` 呼叫 `_sync_global_from_project`,後者定義在 `scripts/lumos:34020`。

6. S5 的「★已撤回★」字面對不上程式輸出。
severity: minor
   blocking: 否 人看得懂,但這是 manual 條款,字面比對會失敗。
   引句:「那兩筆原列尾端有 ★已撤回★」
   重現:實際輸出是 `★已撤回(理由;人,日期)★`,中間有括號和內容,逐字搜「★已撤回★」搜不到。標頭「其中 N 筆已撤回(統計不算)」和「問號列」的判準與程式一致。
   file: `scripts/lumos:20113-20115` 與 `scripts/lumos:20100`。

7. 改寫 `t_name_collision_scales` 會悄悄放寬既有條款 [S79],spec 沒處理那條條款。
severity: minor
   blocking: 否 守衛仍有效(個數檢查比時間更能抓「重建」),但條款文字和測試內容分叉了。
   引句:「牆上時間 60 秒內只當安全網(本機實測 0.29 秒)」
   事實:`Projects/測試名收自由字串_計劃` 的 [S79] 寫「當 1000 個綁定名對 22000 個標題判撞名時,應在 15 秒內做完」,綁這支測試。改寫後測試只驗個數與 60 秒。`Systems/test-profile-multiplatform` 也綁同一支測試。spec 的 `lands_in` 與做法都沒列這兩篇,也沒說要改或標明 S79 被取代。
   我也實測過:標題索引只建一次、但 `containing` 退化成逐筆線性掃描,1000 個名字約 3.3 秒,個數檢查與 60 秒安全網都抓不到。這不是原測試的覆蓋範圍,所以不算新退步,只是安全網的實際效力要寫清楚。
   file: `scripts/test_lumos.py:108165`、`docs/lumos-toolchain-knowledge/Projects/測試名收自由字串_計劃.md:252`、`docs/lumos-toolchain-knowledge/Systems/test-profile-multiplatform.md:85`。

8. 祖先過濾的設計和既有決策紀錄的 `[不選:]` 同一個弱點,spec 沒引用也沒說為什麼這次可以;而且沒比較用分支名的做法。
severity: minor
   blocking: 否 spec 已把壓提交寫成天花板,實際傷害小,但脈絡有缺口。
   引句:「代價:本 repo 推送前要把本機提交壓成一個,壓掉的提交上的判綠紀錄之後就不算數」
   事實:`Systems/規格閘.md` 第 51 行的 WHY 已記「[不選:記寫入當下的版本編號跟測試首次提交比(壓提交後原提交不在、空殼與實作在檔案層分不出)]」,`Projects/規格閘紅燈測試快照_計劃.md` 第 143 行同理。本案用的正是「記寫入當下的 head_sha」,而推送前壓提交在本 repo 是必經流程,所以天花板一在正常流程裡必定發生。
   天花板二(同一個 HEAD 開新分支重來)用分支名就解得掉。`_gate_event_build` 已支援 `ref` 欄位(`scripts/lumos:1595`)。spec 的 PRIOR-ART 沒評估過「同時記分支名」。
   另外在紀錄進版控的設定下,fork 相減本來就精確,祖先過濾只剩壓提交與 rebase 的副作用,spec 的 RETIRE-IF 也承認這點。

極端輸入逐項核對,沒有 finding 的:
- `head_sha` 等於 HEAD:`--is-ancestor` 回 0,留。
- 大小寫不同或短編號:`_LENS_SHA_RE` 只收 40 或 64 位小寫,不符的照舊留,等同現況。
- 提交已刪除分支但還沒 gc:回 1,丟(正確)。gc 之後回 128,再用 `_push_rev` 回 1,完整 repo 裡丟(正確)。
- 提交編號其實是 tree 或 blob:回 128,`^{commit}` 查不到,丟。
- 在 main 上或分離 HEAD:fork 為 None,整本帳照祖先過濾,行為合理。
- git 沒裝或逾時:`_lens_git_dl` 回 None,留。
- 三引號常值(S4):我把 `_TG_CONST_PAT` 的字串段換成 `_TG_LIT_PAT` 實測。`assertEquals("""a""", """a""")`、跨行、空三引號 `""""""` 都判成常值,`assertEquals(1, f())` 不變。spec 對 `_tg_ident` 說明和三處 fullmatch 的描述與程式一致。`_TG_LIT_PAT` 是佔有式、線性,沒有回溯風險。
- 名稱撞名測試(S3):走 `_name_collision_reason`、`name_filter: regex_tail`、替換 `_raw_test_titles` 和 `_TitleIndex` 子類,我實測建構次數為 1,耗時 0.27 秒。測試是循序跑的,模組單例的替換沒有競態。

實務隱患鏡頭:
- 效能:無熱路徑風險。`_redbase_branch_rows` 只在規格閘有紅燈素材要寫時呼叫一次,而且在 `_vault_write_lock` 之外(`scripts/lumos:14230`)。最壞 10 秒,不是無界。
- 回滾:第 1 到 3 項沒有持久狀態,純程式回退即可。第 4 項見第 5 條。
- 併發:同一個工作目錄被別的會談切分支時,200 次連續詢問用字面 `HEAD`,可能前後看到不同 HEAD。單人使用下可忽略,我沒有重現,不標 finding。
- 其他風險類(金流、對外送出、不可逆):spec 已排除,我同意。

我的暫存放在 `/tmp/lumos-seat-work/判綠紀錄限本分支與撞名測試改計數/邊界-sonnet/`,請編排者收貨後刪除。

最嚴重 severity 是 minor,blocking 共 0 條。
