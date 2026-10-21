severity: clean

我逐 hunk 讀完整份 diff 與修補差異,沒有找到會做出錯行為的缺陷。

**編排者列的待驗行為,逐項核對**

1. **只有核可過的 risk_accepted 格子時不必蓋 not_applicable_sound:成立。**
   - 格子的狀態字串在已驗核可鏈時是 `not_applicable` 或 `risk_accepted`。`_seccell_compute` 回傳的待決清單只收以 `not_applicable` 結尾的格子,所以 risk_accepted 進不去 `ctx.na_surfaces`。
   - 我做了破壞實驗:把 `ctx.na_surfaces` 改成「狀態是 not_applicable 或 risk_accepted 的格子」,`t_secev_s69_not_applicable_conditional` 的 ③' 馬上翻紅(`['missing:review_record_missing']`)。這條斷言抓得住退化。
2. **撤銷兩道判定收成 `_secapr_signer_revoked`,行為不變:成立。**
   - 逐筆判用 `retro=False`,等於原本的 `signer in revoked`。
   - 回溯用 `retro=True`,只對 `expires_on` 為 null 的 human_review 生效。形狀檢查已保證只有 human_review 能寫 null,所以回溯不會碰到其他型別。
   - 只回溯狀態為 `ok` 的筆,不會把 `approval_expired` 之類改寫。
   - 主線鏈的遞迴驗證也走同一支。回溯只會改掉不設期限的人審,`init` 之類永遠不受影響,所以「曾經有效」判斷與分岔判斷不變。
   - 被撤的主體是 principal。`_secapr_apply` 對已撤銷的 principal 不會重新加金鑰,所以撤銷之後不能靠重新加入而復活。
3. **函式改名搬位置後所有呼叫點都換到:成立。**
   - `_secev_expiry_null_ok` 有三個呼叫點:證據圍欄(`_secev_ip_review`)、核可形狀(`_secapr_entry_shape`)、payload 命令(`cmd_security_approvals`)。
   - `_secapr_signer_revoked` 有兩個呼叫點:`_secapr_entry_status` 與回溯迴圈。
   - 舊名已無殘留。
   - 其他讀 `expires_on` 的地方已逐一核對:`_secapr_entry_dates`、`_secapr_verify` 的過期判斷、`_secev_judge_review` 的三處、`_secev_chain_reminders`,都有 None 守衛。
   - 另外兩處只吃 consideration 與 exception,那兩型仍強制要日期。
4. **preserve 各項:成立。**
   - 撤銷之後用被撤金鑰新簽的任何型別,仍走逐筆判,結果是 `approval_signer_revoked`。
   - 寫日期的人審在撤銷前簽的,回溯不碰它,仍是 `ok`。
   - `approvers_*` 的金鑰過期與撤銷邏輯沒動:`_secapr_apply` 與 `pool` 的 `v[2] >= ap` 篩選原樣。
   - S68、S69 其餘各例我都跑過:`t_secev_s68_review_no_expiry` 40 條斷言全過,`t_secev_s69_not_applicable_conditional` 9 條全過。
   - payload 命令對另外 9 種型別不帶 `--expires-on` 仍回 rc2。
   - 傳 `""` 或字串 `"null"` 給 human_review 的 `--expires-on` 也被擋(它們不是真正的 None)。

**程式碼細節**
- **`_secev_kind_verdict`**
  - 新式 `need_h` 對 `manual_check_scope`、`threshold_meaningful`、`calibration_representative`(三項都要人)與舊式等價,只有 `not_applicable_sound` 不再被當成要人。
  - `(base | extra) - anyone` 與舊的 `base - anyone` 加「extra 由人蓋」的組合等價,因為 human 集合是 anyone 的子集。
- **算格子提前**
  - 提前不改變 `ctx._facts` 與額度的使用順序,因為額度預掃仍在它之前。
  - `ctx.remind` 的提醒順序會改變,但沒有測試或合約依賴這個順序。
  - `_secev_judge_control` 只有 `_secev_stage_judge` 兩個呼叫點(護欄與候選),都在 `na_surfaces` 填好之後,沒有漏填的路徑。

**圖譜鏡頭(固定席節點逐組判)**
- `lumos-cli-read`、`測試假綠形態`、`design-loop`、`guard-kill`、`bound-tests-gate` 這幾組 ★INVARIANT★ 談的是 search 濾網、還原翻紅釘、處置閘、guard kill 的回傳碼、綁定測試。這份 diff 沒碰那些行為,只動安全證據閘的期限與判斷項條件,所以不影響。
- `pitfalls-code-loop`、`loop-convergence-recording`、`reversibility-governance-ledger` 是 ★RISK★ 節點。這份 diff 沒改它們的規則,所以不影響。
- 超出上限、只列名的節點與「圖譜沒有釘到節點」備援段,我沒有逐條答。

**計劃一致性(d21、S68、S69)**
- 計劃正文與程式行為對得上。
  - 規格表、核可鏈型別表、驗證步驟、`payload` 的寫法都已同步。
  - 〈四〉的 `expires_on` 欄位說明也標明只有 human_review 可寫 null。
- 沒有發現「照做會做錯」的舊句。
  - 計劃 512 行的「90 天對齊一季」保留的是寫日期時的舊規則,緊接著 513 行有 d21 補述,上下文清楚。
  - S62 的「not_applicable_sound 由 ai 紀錄蓋到應算數」依然成立。
- 兩處措辭瑕疵,不影響行為,不值得標 finding。
  - S68 條款中間有一個 `。;` 標點。
  - S69 沒寫明「格子要經核可鏈算數」才算數,這一點寫在 Systems/安全證據閘 的筆記裡,測試 ③ 也已綁定。

本輪沒有 finding,我的實驗只有上面那一次破壞實驗,已刪除臨時目錄。
