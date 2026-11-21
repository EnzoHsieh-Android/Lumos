severity: minor

這份 diff 沒有 blocker 或 major。我逐 hunk 走過邊界、None 處理、新舊帳互讀、字樣替換與統計,只找到三條 minor。`t_codeloop_pass_choice` 我實際跑過,25 項全過。

### Findings

severity: minor
blocking: 否
file: `scripts/lumos:73413`(`_codeloop_pass_choice` 取分支名處)
引句:「r = _lens_git(rr, "symbolic-ref", "-q", "--short", "HEAD")」
失敗場景:repo 裡有一個和分支同名的 tag(例如分支 `feat` 與 tag `feat`)。我在暫存 repo 實測,`git symbolic-ref -q --short HEAD` 印出 `heads/feat`。`name` 因此是 `heads/feat`,後面的追蹤分支查詢變成 `refs/remotes/origin/heads/feat`,查不到就退成全零,被推 ref 也變成 `refs/heads/heads/feat`。結果是已推過的分支被當成新分支首推,範圍多看已推過的提交,pass 可能多擋。這是多擋、不是少擋,而且需要同名 tag 才會觸發。建議改用 `symbolic-ref -q HEAD` 再去掉 `refs/heads/` 前綴。
重現:在暫存 repo 建分支 `feat` 與 tag `feat`,執行 `git symbolic-ref -q --short HEAD`,輸出 `heads/feat`。

severity: minor
blocking: 否
file: `scripts/test_lumos.py`(`t_codeloop_pass_choice`,S10 與 S2 區段)
引句:「_cpc_git(r6, "update-ref", "refs/remotes/origin/main", _cpc_git(r6, "rev-parse", "HEAD"))」
失敗場景:預期值表 S10 的「已推過的分支(增量)」與分支名帶斜線,測試沒有逐項鎖住。
- 遠端舊值有值的路徑只在 `main` 上測過;`feat/sit` 分支從頭到尾沒有建 `refs/remotes/origin/feat/sit`,走的都是全零的新分支首推。
- 把 `refs/remotes/{remote}/{name}` 改成只取最後一段(`sit`),所有斷言仍會是綠的。
- S10 第一案也分不出舊值取追蹤分支與取全零:`origin/main` 本身就是主線候選,算出的起點相同。第二案才會對全零紅。
- 建議補一案:`feat/sit` 已推過、再加一個缺紀錄的提交,預期只擋新增的那幾行。

severity: minor
blocking: 否
file: `scripts/test_lumos.py`(`t_codeloop_pass_choice`)
引句:「def t_codeloop_pass_choice():」
失敗場景:這支測試實測 138.3s,超時上限 180s,測試工具自己標「餘裕不足 3 倍」。CI 機器稍慢就會因逾時變紅,而不是因為判錯。建議把 S4 到 S6、S12 這些不需共用的案例拆成獨立測試。

### 其餘審查點的結論(不成 finding)

- **site 預設值與推送前行為**:`_choice_site_words` 在 `site != "pass"` 時原樣回傳。所有 `site="push"` 的呼叫路徑,輸出字串與事件欄位都不變。事件只在 `site != "push"` 時才多帶 `site`,所以推送端不產生新欄位。
- **去重鍵**:`(e.get("site") or "push") == site`。舊帳沒有 site 的事件算推送,所以舊帳與推送端的比對不變;pass 與推送在同一頂端、同一組原因各記一筆,和 S9 一致。
- **推送前讀到 site=pass 的事件**:不會影響它的判定。`_choice_ledger_index` 只收 `kind == "choice-kill"` 的判定事件,blocked 與 unverified 列整列略過。
- **字樣替換**:
  - 替換是依序進行,長的在前。替換後的字串不會被後面的規則再次命中,連續套兩次也穩定。
  - `_CHOICE_PUSH_FIX` 中存活、跑不出結果、不唯一、過期四條沒有推送字樣,不經替換也不會留下錯字。
  - `_choice_bad` 前綴 `[選擇點] ` 沒有推送字樣。
- **None 與例外**:`_lens_git` 回 None 與 `_lens_full_sha` 取不到,都落到「沒有分支」那一行並放行。detached HEAD 與沒有遠端同樣放行。
- **統計**:
  - `ck` 白名單已加 `site`,`pass_blocked` 是 blocked 的子集,所以「推送 = 總數 − pass」成立。
  - 舊的「推送被擋」字樣只有該測試用到,測試已同步更新,沒有其他讀者。
- **寫一半**:pass 被擋時只寫治理帳,即一筆 `choice-kill` blocked 與一筆 `code-loop-pass` blocked。照指示補 `choice-kill` 後再 pass,會讀工作目錄帳並放行。被擋時寫的 blocked 事件不影響之後的判定,因為帳索引不收它們。

### 固定席逐條判定

- `Systems/pitfalls-code-loop.md`:不影響。新增的一節與 `_codeloop_pass_gate` 實際順序(mech、choice、verify)一致,也沒動 `code-loop check` 的原因種類。
- `Systems/bound-tests-gate.md`(★INVARIANT★ check 對固定席綁的測試真跑):不影響。pass 預判不跑任何測試,沒有碰 check 路徑。
- `Systems/loop-convergence-recording.md`、`Systems/reversibility-governance-ledger.md`:不影響。只在 pass 擋下時多寫治理帳,沒有改留痕、凍結或收斂邏輯。
- `Systems/lumos-cli-read.md`、`Systems/guard-kill.md`、`Systems/測試假綠形態.md`、`Systems/design-loop.md`:不影響。分別涉及 search 排除、guard kill 的 rc 與 JSON、還原翻紅釘的前置斷言、設計審處置閘,這份 diff 都沒碰。
- 其餘「超出上限只列名」的節點:不影響。diff 沒有改它們管的檔案或行為。
- 表態記錄:推送前掛鉤的資料量、熱路徑類答案與這份 diff 無關,我沒有發現矛盾。

最嚴重等級 minor
