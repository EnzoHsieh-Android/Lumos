severity: minor

## Findings

1. decision-amend、guard bind、guard audit 在鎖被占住時印出裸 traceback,不再回「擋下:」
severity: minor
   blocking: 否
   - 輸入:筆記庫的寫入鎖被另一個程序占著(或留著殘鎖),再跑 `decision-amend Sys1 d2 --field context --text z`、`guard bind Sys1 x foo` 或 `guard audit Sys1 x`。
   - 路徑:`@_vault_locked` 的 `_w` 進 `_vault_write_lock`,等滿 60 秒拋 `RuntimeError`。`decision-amend` 的分派段只接 `ValueError`(`scripts/lumos:53002` 附近)。`guard bind` 和 `guard audit` 的分派段(`scripts/lumos:52827`、`52830`)外面沒有 try。三者都沒接住,所以印出 traceback,回傳碼沒有走專案約定的 2(我只看到 traceback,沒另外量回傳碼)。
   - 修前:同樣的鎖狀態下,這三支不拿鎖,照常執行(輸出「擋下:決策 d2 沒有欄位 context」「找不到合約 KEY 行」這類正常訊息)。
   - 修後:三支等 60 秒後印出 `RuntimeError: 等了 60 秒還輪不到寫入...` 的 traceback。同一時間 `set` 和 `decision-refs prune` 行為跟修前一樣。
   - 計劃筆記只承認「鎖殘留時會等 60 秒才回『擋下』」。這三支實際不是回「擋下」。
   - 判定理由:只在鎖被占滿 60 秒(殘鎖或長時間並行)時才出現,寫入本身沒有被錯誤拒絕,也沒有丟「沒拿寫入鎖」,所以不擋合併;但訊息形式與回傳碼偏離專案約定,應補一道例外接住。
   - 引句:「+@_vault_locked def cmd_guard_bind(env, node, invariant_substr, method, platform=None):」(patch 此處實際分成兩行,引句取自 `+@_vault_locked` 與其下一行,見 patch 的 cmd_guard_bind hunk)
   - 引句:「+def _vault_locked(fn):」
   - 佐證:file: `scripts/lumos:602`、file: `scripts/lumos:53002`、file: `scripts/lumos:52827`
   - 最小重現:建 `~/.cache/lumos/vault-lock/<sha256(realpath(vault))[:32]>.lock`,內容寫 `1`。再跑 `lumos decision-amend Sys1 d2 --field context --text z`。等 60 秒後印 traceback。對照命令 `python3.14 $W/before/lumos ...` 與 `$W/after/lumos ...`,結果如上。
   - 歸因:有證據的修復回歸。這三支原本不拿鎖,修補才加上。

2. decision-amend 把整段 git 網路操作包進全庫寫入鎖,其他寫入跟著等
severity: minor
   blocking: 否
   - 輸入:有遠端的 repo,`git fetch --all` 很慢。
   - 路徑:`cmd_decision_amend` 整個函式被 `_vault_locked` 包住,其中的 `_lens_git(root, "fetch", "--all")`(單次逾時 20 秒)與逐個遠端參照的 `git diff`、`cat-file` 都在鎖內(`scripts/lumos:41596` 以後)。
   - 修前:`amend` 跑 6 秒,同時下 `set Sys1 status active`,`set` 立刻回(waited=0s)。
   - 修後:`set` 等到 `amend` 結束(waited=6s)。遠端參照多或網路更慢時,可能把別的寫入拖過 60 秒而失敗。
   - 引句:「+def _vault_locked(fn):」
   - 佐證:file: `scripts/lumos:41596`、file: `scripts/lumos:602`
   - 最小重現:`git config remote.o.uploadpack` 指向先 `sleep 6` 再 `exec git-upload-pack "$@"` 的腳本,加一個遠端,一邊跑 `decision-amend`,一邊跑 `set`,比兩版。
   - 歸因:有證據的修復回歸。

3. `_write_lf` 的說明文字過期,與新規則相反
severity: minor
   blocking: 否
   - 該說明仍寫「其他寫入指令仍是 last-write-wins」。修後所有走 `atomic_write_verify` 的入口都要拿鎖,這句話已經不成立,patch 沒更新它。
   - 引句:「讀改寫開頭欄位的入口一律包 `_vault_locked`,`atomic_write_verify` 沒拿鎖就不寫」
   - 佐證:file: `scripts/lumos:19896`
   - 歸因:有證據的修復回歸(修補讓舊說明變錯)。查證:`grep -n "last-write-wins" scripts/lumos` 兩版對照,修前這句成立,修後不成立。
   - 另一個圖譜缺口:Systems 筆記「T1 寫後自驗」四步沒加上「先檢查鎖」這一步,與新的 `atomic_write_verify` 開頭檢查不同步。

## 核心問題:有沒有「修前能寫、修後丟沒拿寫入鎖」的路徑

沒找到。

- **靜態**:用 AST 列出所有含 `atomic_write_verify` 呼叫的函式,逐條查呼叫鏈。每條都經過 `_vault_write_lock` 或 `@_vault_locked`。涵蓋 guard plan/settle/abandon、kill-add/rm、summary-line、set 條件欄位、set/append/remove、drift fix 的 `_drift_fix_write`、question-add/set、dref 各支與 `rel-cascade`。
- **動態**:把 `atomic_write_verify` 的 raise 換成「寫入未持鎖的紀錄後繼續」,在臨時副本裡用 `lumos init` 起的新專案跑下列指令,紀錄檔一直沒出現:
  - `new`、`set`、`append`、`remove`、`self-audit`、`signoff`
  - `guard bind/audit/kill-add/kill-rm/plan`
  - `decision-add/reindex(含 --all)/supersede/amend`
  - `decision-refs add-ai/promote/prune`、`question-add`
  - `archive --apply`、`doctor`、`drift scan`
- **修前對修後**:同樣流程逐條比 stdout/stderr/rc,除時間戳和路徑外完全相同,例外見下一節。
- **未涵蓋**:`guard settle` 和 `guard abandon` 沒跑通(我的測試輸入被擋在前面),`drift fix` 與 `doctor --fix` 也沒實跑。這幾條只靠靜態查證。
- **全套測試**:我在副本裡跑了全套 `test_lumos.py`,約 20 分鐘仍未跑完,我把它終止了。已跑的部分一直沒有未持鎖紀錄,但這不等於全套通過。

## 分派段還原

`decision-supersede/add/reindex` 的分派段與 `6c740a70`(第一輪之前)的原版逐字相同。差異用 `difflib` 比,零差異。輸出與回傳碼一致。額外差別:鎖逾時的 `RuntimeError` 現在由原有的 `except (ValueError, RuntimeError, OSError)` 接住,回 2,這是好的。

## 修後多出的輸出

`HOME` 不可寫時,因為鎖的位置改用筆記庫內的退路,`decision-refs add-ai` 和 `decision-reindex --all` 現在多印一段「提醒:放寫入鎖的資料夾用不了…」到 stderr。寫入照常成功,rc=0。這是新增的 stderr 雜訊,沒有功能影響。

## 圖譜鏡頭

- `lumos-cli-write.md`:「鎖殘留時這些指令會等 60 秒才回『擋下』」對 amend、bind、audit 不成立(見 finding 1)。
- `lumos-cli-write.md`:T1 四步缺鎖檢查(見 finding 3)。
- `lumos-cli-read.md`、`規格閘.md`:本輪改動是 lint 與連結比對,與寫入鎖無關,我沒在這兩篇找到與程式不符的句子。
- `bound-tests-gate.md`:本輪沒動它,也沒讀到與本鏡頭有關的矛盾。

## 三問

1. 原問題(決策、決策引用、守衛綁定與審計沒鎖,會蓋掉同一份開頭欄位)的修復證據:`atomic_write_verify` 在未持鎖時拒寫,我在副本裡直接驗證過,持鎖路徑全部放行。同時,`reindex --all`、`amend`、dref、bind、audit 現在確實拿鎖(`set` 在鎖被占住時與這幾支一起等)。
2. 修補處三類路徑:
   - 正常呼叫:修前修後輸出一致。
   - 錯誤呼叫(找不到節點、參數錯):一致。
   - 鎖被占住的相鄰路徑:`decision-add/supersede/reindex` 回 2,`amend/bind/audit` 變成 traceback(finding 1)。
3. 新發現的同一案例:
   - finding 1:修前正常執行,修後等 60 秒後 traceback。
   - finding 2:修前 `set` 立即回,修後等 `amend` 的 6 秒。
   - finding 3:修前說明正確,修後說明過期。

總結:沒有「沒拿寫入鎖」的合併阻擋回歸,但 `decision-amend`、`guard bind`、`guard audit` 在鎖被占住時改成 traceback,這點應在合併前或之後補一道例外接住。

臨時目錄 `/tmp/lumos-seat-work/code-待決問題改存開頭欄位/r3-通才回歸-sonnet/` 裡有 `inst/` 副本(gctl 暫存也在 `/var/folders/.../gctl-run-*`),請收貨後刪。
