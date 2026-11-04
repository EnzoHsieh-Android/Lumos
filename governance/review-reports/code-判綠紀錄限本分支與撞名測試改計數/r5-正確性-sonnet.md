severity: clean

第 5 輪(正確性席,範圍是 `b245517b`)**沒有找到會做出錯行為的問題,零條 finding。**

## 已驗(證據)

| claim | input | expected | case_source | 修前 `ae9c4d82` | 修後 `b245517b` | 歸因 |
|---|---|---|---|---|---|---|
| 帳被忽略、完整 repo,要照舊減分岔點 | 主線那版帳有舊判綠、分支上才改成忽略 | 舊判綠被減掉 | `t_redbase_branch_rows_fallback_keeps`「S8 帳曾進版控後改成忽略」 | 紅,舊判綠 `67896d5b` 漏進來 | 綠 | 有證據的修復效果 |
| SHA-256 repo、帳進版控、沒有分岔點,空樹照 repo 格式算 | `git init --object-format=sha256` | 判綠照算 | 同支「SHA-256 … 帳進版控」 | 紅,印「讀不出起點那一版」並回空 | 綠 | 有證據的修復效果 |
| 帳被忽略、完整 repo,有去算分岔點 | 同上 | `_lens_fork_point` 被呼叫 | 同支「S8 帳被忽略、完整 repo」 | 紅,呼叫 0 次 | 綠 | 有證據的修復效果 |
| `_git_bool` 整數判讀 | `0k` 判假;`0_0`、`0b0` 判真 | 照 git | `t_git_partial_clone_keys` | 紅三條 | 綠 | 有證據的修復效果 |
| 撞名測試改用留住物件再比 | `t_name_collision_scales` | 不變 | 同名測試 | 綠 | 綠 | 修前本來就綠,不是修復證據,屬 preserve |
| 部分複製、帳被忽略,直接讀工作目錄 | 真的 `--filter=blob:none` 與 `--filter=tree:0` 複製(git 2.39,我自己跑的) | 不連遠端,判祖先照留 | 我補的案例(用會留記號的 uploadpack 腳本偵測抓取) | 未測 | 帳被忽略時 2 筆照留,三種 `ignored` 值都沒抓取 | preserve,通過 |
| 部分複製、帳進版控或判不了有沒有被忽略 | 同上 | 回空並印說明 | 我補的案例 | 未測 | 如預期,沒抓取 | preserve,通過 |

**`_git_bool` 逐值對照 git。**
- 我用 `git config --type=bool` 對 50 個值逐一比,包含 `0x`、`08`、`0kk`、`-0`、`+0`、全形數字、`0x8000000000000000`。
- 結果沒有「git 判真、我們判假」的危險值。git 拒絕的寫法一律判真,是寧可多小心的方向。

**本案特定鏡頭四。**
- `_note_reread_branch` 搬家後行為不變:`_git_current_ref` 的內容跟原本內聯的 `symbolic-ref -q HEAD` 加 `_note_reread_show` 逐字相同。
- 我跑了 `-k note_audit_reread`,131 條全綠。
- 另外 `-k name_collision`、`-k drift_born`、`-k tq_guard_string`、`-k redbase_branch_rows_fallback`、`-k git_partial_clone_keys`、`-k spec_gate_redbase`(61 條)都全綠。
- 帳被忽略且不是部分複製時,改回減分岔點後,我沒找到結果變錯的輸入。
  - 分岔點那版沒有帳:`_residual_blob_at` 靠 `ls-tree` 判成 `missing`,得到整本帳,跟上一版相同。
  - 分岔點那版有帳:減掉的是主線的列,跟帳進版控的語意一致。
  - 分岔點等於 HEAD 且在 main 或 master 或分離 HEAD:不算分岔點,減空樹,跟上一版相同。

**測試抓不抓得到。**
- 我在自己的複本上把 `_git_current_ref` 改成 `--short` 加手補前綴:`-k note_audit_reread` 仍全綠,只有 `t_spec_gate_redbase_green_other_branch`(同名 tag 的 S2)翻紅。
- 這是回頭重讀那側本來就沒有「同名 tag」的案例,不是這輪修補造成的,而且共用函式有被規格閘那側的測試守住,所以不另標。

**我試過、沒打穿的邊界。**
- 分離 HEAD。
- 還沒有提交的 HEAD。
- 淺複製。
- 上限 200。
- 截止時間用完。
- 型別不對的 `ref`、`head_sha`、`loop` 欄位。
- 同一列逐位元組相同的重複列(靠計數相減)。
- 舊紀錄沒有 `ref` 欄。

## 未驗範圍
- 全套測試:我跑了約 30 分鐘,機器很慢,中途停掉。已跑的 1022 條沒有任何一條失敗,但沒有跑完,不能算全套綠。
- 新增的 git 以外的版本(只測 git 2.39.2)、Windows、時鐘倒退。
- `_drift_empty_tree` 在 SHA-256 repo 遇到 `hash-object` 暫時逾時時,會永久退回 SHA-1 空樹(同一個行程內快取)。這只讓判綠觀測少一次、方向是少存判綠,CLI 是一次性行程,我判為不值得標。

## 順帶看到、不標等級(給不出失敗輸入)
- `t_redbase_branch_rows_fallback_keeps` 裡「替換 `_lens_fork_point`」後立刻還原的那段(`real_fork = ...` 到 `finally`)是空殼,沒有任何斷言夾在中間。
- `docs/lumos-toolchain-knowledge/Systems/規格閘.md` 的 WHY 與 `Projects/規格閘紅燈測試快照_計劃.md` 寫「治理帳被忽略時分岔點那一版沒有帳」。這輪之後程式碼是「通常沒有、有也要減」,措辭略舊,但計劃本文已寫對。
- `Systems/測試假綠形態` 的 ★INVARIANT★(還原翻紅釘要有前置斷言):新增測試都有 ★前置★ 或等效證明,**不受影響**。
- 圖譜固定席其餘節點:`lumos-cli-read` 的 search 合約、`guard-kill` 的 rc 合約、`design-loop` 處置閘、`bound-tests-gate` 的綁定測試真跑,都跟本改動無關,**不影響**。
- 其餘節點本改動沒有觸及它們的合約行。

最嚴重等級是乾淨,blocking 共 0 條。

(暫存已清:我建的兩個複本、`fz` 暫存目錄都已刪。)
