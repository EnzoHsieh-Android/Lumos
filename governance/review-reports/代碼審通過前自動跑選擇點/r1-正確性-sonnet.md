severity: minor

整份 spec 已逐節對照 `scripts/lumos` 讀完。我沒有找到照字面實作會記錯帳或誤放行的狀態,以下 5 條都是 minor。

**〈白話〉、〈WHY〉、〈驗收條款〉、〈回退〉、〈依據來源〉:已讀,無 finding。**
- 帳從哪讀:第一次判定與第二次判定都讀工作目錄那份帳,兩次一致。
- choice-kill 寫帳的時序:choice-kill 自己讀的也是工作目錄帳(`_choice_kill_ledger` 呼叫 `_gov_vc_gate_events`),所以它剛寫的紀錄,第二次判定讀得到。
- 放行檔:兩邊口徑相同。第一次判定從 HEAD 讀放行檔,choice-kill 讀工作目錄放行檔,但它要求除簿記檔外工作目錄乾淨,所以兩邊不會不同。
- 擋下後再 pass:使用者照指示處置、提交、再 pass,走得通。
- 預期值表 S1 到 S10 每一列都造得出來。S7 要求「擋缺紀錄」,測試固定裝置的 HEAD 必須已提交過一份治理帳,否則 `_choice_push_ledger` 回的是「帳不在」。這點見下面第 2 條。

severity: minor
blocking: 否
判準:實作者能自己補出來的精度問題,不影響行為。
**1. `choice_reasons` 取不到(〈做法〉判第二次、〈範圍〉④)。**
引句:「另加 `choice_reasons`(每種原因的行數)」
- spec 同時要求只多三個帶預設值的參數。
- `_choice_push_round` 只回 `_ChoiceBad` 清單,每條只有 `.lines` 加文字。
- 「原因名稱 → 行數」那份 `reasons` 是 `_choice_push_verdict` 的區域變數,沒有傳出來。
- file: `scripts/lumos:78899`(`_choice_push_verdict` 的 `reasons` 只拿去記事件)。
- 實作只能從文字開頭解析,或違反「只多三個參數」。
- RETIRE-IF 靠 `choice_reasons` 裡有沒有「缺紀錄」,這個欄位得明講怎麼產。

severity: minor
blocking: 否
判準:統計與回頭條件的可執行性問題,不是行為錯誤。
**2. 沒有任何讀者會數 `code-loop-pass` 的 choice 擋下(RETIRE-IF、REVISIT:2027-01-21、S9)。**
引句:「上線兩個月後,`code-loop pass` 因選擇點擋下的紀錄裡,過半是「沒跑完」」
- file: `scripts/lumos:17917` 起的 `_gov_choice_counts` 與 `_render_gov_choice` 只認 gate 為 `choice-kill` 的列。
- `code-loop-pass` 在 `scripts/lumos:17759` 只是閘名白名單,沒有任何統計讀它。
- 〈範圍〉⑤ 的同步項沒有要求 `gov --stats` 加一段。
- `record=False` 之後,pass 時被擋的缺紀錄與過期不會進「推送被擋 N 筆(過期 x/N)」,而 `gov --stats` 又不印 pass 擋下,所以到期時無從機械判斷。
- choice-kill 在「全部存活且守的測試沒變」時仍會寫一筆 `ran=0` 的 `run` 事件(`_choice_kill_report` 無條件寫)。
- 每次 pass 重跑都會稀釋 `gov --stats` 的「choice-kill 呼叫次數、耗時中位數」。S6 與 S9 允許這筆 run,但沒提它對統計的影響。

severity: minor
blocking: 否
判準:統計失真與無法回頭,不影響擋不擋。
**3. 「同一支判定、推送前本來就會擋同一批」只在範圍相等時成立(〈範圍〉①、②,〈實務隱患〉守衛面)。**
引句:「判定跟推送前那道同一支函式(推送前本來就會擋同一批)」
- pass 的範圍用 `_codeloop_default_range`,底層是 `_lens_default_base`,會把本機 main 當候選。
- 推送前用 `_push_range_start`,依遠端舊值與遠端主線算,增量推送時起點可能較晚。
- file: `scripts/lumos:79505`(`_codeloop_default_range`)與 `_push_range_start` 的說明。
- 兩者不同時,pass 可能要求推送前根本不看的行,或相反。
- spec 把兩者寫成等價,應註明差異是已知的、只會 pass 較嚴。

severity: minor
blocking: 否
判準:宣稱精度,誤差方向是 pass 較嚴,不漏放。
**4. 〈做法〉圖譜物件:沒處理 `_vault_in` 回 None(含 S5 情境)。**
引句:「生效日(`_choice_since()`)已過、而且範圍內有 `.kt` 改動時才建 `Env(_vault_in(repo_root))`」
- `code-loop pass` 與前兩道是 vault-free 的,`_codeloop_pass_mech` 沒有圖譜物件。
- file: `scripts/lumos:36664`(`_vault_in` 沒有 vault 就回 None)。
- `Env.__init__` 直接 `load_vault(vault)`,傳 None 會在記通過之前崩潰。
- 預先過濾只看 `.kt` 改動與生效日,沒先看有沒有 kotlin-junit 平台(`_choice_push_has_kotlin`)與有沒有 vault。
- 沒有 vault 又有 `.kt` 的 repo,會用 traceback 取代放行。
- 應補「沒有 vault 或沒有 kotlin-junit 平台就放行」。

severity: minor
blocking: 否
判準:邊緣專案配置,一行判斷即可補。
**5. 〈做法〉自動跑「有任何擋下原因就跑」與〈WHY〉「有可重跑的原因」不一致。**
引句:「有任何擋下原因 → 行程內呼叫 `cmd_choice_kill(env, diff=範圍, max_seconds=_CHOICE_PASS_SECONDS)`」
- 第一次判定的原因含 choice-kill 重跑解不掉的:表壞、無規格、帳讀不了、帳不在、只有不唯一。
- 這些情形下 choice-kill 會在前置檢查印自己的原因並回 rc 2,pass 再印一次同一批原因,使用者看到重複又不同口徑的訊息。
- 工作目錄除簿記檔外不乾淨時,例如剛 `lint-waive` 還沒提交,choice-kill 直接拒跑,第二次判定仍是缺紀錄。
- 使用者得到的指示是「處置後提交」,真正原因(未提交的放行檔)夾在 choice-kill 的訊息裡。
- 建議明定哪幾種原因才呼叫 `cmd_choice_kill`,以及 rc 2 的前置失敗要不要印一句話。

最嚴重等級 minor,blocking 共 0 條
