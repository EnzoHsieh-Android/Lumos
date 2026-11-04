severity: minor

這份 diff 的過濾邏輯本身走得通。我另外做了三件事:
- 跑了相關測試:`t_spec_gate_redbase_green_other_branch`、`..._tracked_unfiltered`、`t_redbase_branch_rows_fallback_keeps`、`t_name_collision_scales` 與整組 `-k tq_guard`(410 支)全綠。
- 把過濾關掉做了一次翻紅:`_redbase_attach` 改傳 `"not"` 後,S1、S6(兩處)、S9 都翻紅,而且 S6 的兩個情境在沒有明寫「前置」斷言時也確實成立。
- 把 `_TG_CONST_PAT` 的三引號那段拿掉:`t_tq_guard_string_comma_args` 的 S4 翻紅。

沒找到會做出錯行為的 major。以下 4 條都是 minor。

1. 撞名測試放寬後,只慢不重做的退步抓不到
引句:「標題索引只建 1 次、每種串接最多 1 次;牆上時間 60 秒只當安全網」
severity: minor
blocking: 否
- 失敗情境:原本的 15 秒門檻改成 60 秒的安全網,而正式路徑實測只要 0.5 秒。
- 我在副本把 `containing` 改成逐筆線性掃描,1000 個名字對 22000 個標題要 4.98 秒,新測試的 ①②③ 全過。
- 所以多數倍的退化、甚至 20 到 60 秒的退化,都不會紅。
- 驗收條款 S79 也從「15 秒內做完」改成只數建構次數,效能面等於沒有條款守。
- 計劃與測試的註解都承認這個洞,但沒有指出誰來接手(見第 2 條)。
- 重現:副本裡 `_TitleIndex.containing` 改成 `[i for i,it in enumerate(self.items) if it[0]==kind and needle in (it[2] if fold else it[1])]`,再照測試的迴圈量時間。
- file: `scripts/test_lumos.py:108156` 附近 `t_name_collision_scales`。

2. 承認「沒有機械守衛」卻沒有獨立的回頭條件行
引句:「只慢不重做的退步(例如查詢退化成逐筆掃描),留給代碼審」
severity: minor
blocking: 否
- 違反的是全域 CLAUDE.md 與專案 CLAUDE.md 鐵則 4:「寫『沒機械守衛 / 只提醒不擋 / 單次量測 / 還沒有 X』這種會過期的話,把那一句本身搬成獨立一行回頭條件」。
- 這句和 `Systems/test-profile-multiplatform.md` 新增的「只慢不重做的退步抓不到」,都把這個缺口寫在正文裡。
- 計劃檔只有一條 RETIRE-IF,針對的是過濾本身。
- 計劃裡的「天花板一到四」和這個缺口都沒有 `REVISIT:` 行。
- 代價:沒有任何事件或日期會把人帶回這裡,「留給代碼審」就變成永久放行。
- file: `docs/lumos-toolchain-knowledge/Projects/判綠紀錄限本分支與撞名測試改計數_計劃.md:69`。

3. 祖先查詢的上限先花在舊紀錄上,最新的反而不過濾
引句:「if len(verdict) >= _REDBASE_ANC_CAP:」
severity: minor
blocking: 否
- 失敗情境:`rows` 是帳序(舊到新),`verdict` 照順序填滿到 200 個不同的 `head_sha` 後,之後的 sha 一律當「判不了」照留。
- 也就是第 201 個之後、最新幾筆的紀錄不過濾,別條分支的判綠又會漏進來,這正是本分支要修的錯。
- 這個行為已被 `t_redbase_branch_rows_fallback_keeps` 的 S8(上限設 1)釘住,所以是設計選擇。
- 但判不了時的方向偏向最不該放行的那一端,而且只會印一句「超過 200 個」。
- 同一份計劃要累積 200 個不同 HEAD 的紀錄,現實上少見,所以只列 minor。
- 判不準:這是依機制推出來的,沒有真實帳可重現。
- file: `scripts/lumos:14432`。

4. 逾時預算從過濾開始前就起算
引句:「dl = _t.monotonic() + _REDBASE_ANC_BUDGET_SEC」
severity: minor
blocking: 否
- `dl` 設在 `_gov_ledger_ignored` 與 `_redbase_branch_rows` 之前。
- `_redbase_branch_rows` 內的 `_lens_full_sha`、`_lens_fork_point`(內部多次 git 呼叫)、`_gov_rows_delta` 都沒帶 deadline,仍照 20 秒一次的上限跑。
- 失敗情境:這幾步合計超過 10 秒(例如 Spotlight 拖慢 git、網路磁碟),進到 `_redbase_on_branch` 時 `_lens_git_dl` 已拿到 `t<=0` 而回 None。
- 後果:每個要問 git 的 sha 都判不了而照留,過濾失效,舊錯在慢機器上重現,只印一句「git 沒回應或逾時」。
- 計劃自己說要避免「結果看機器快慢」,預算起點應該放在祖先迴圈之前。
- 判不準:沒有造出慢的 git,屬 ⚠ 機制推論。
- file: `scripts/lumos:14573`。

已確認沒問題的地方:
- `_redbase_branch_rows` 只有 `_redbase_attach` 一個呼叫端會傳新參數;`test_lumos.py` 裡的舊式呼叫(預設參數)行為不變。
- `ref` 欄位沒有任何治理帳讀者拿來判斷規格閘留痕,`extra` 排除 `ref` 是多餘的保險,不影響結果。
- `_TG_CONST_PAT` 新增的三引號那段與 `_TG_LIT_PAT` 逐字相同,有佔有式量詞,不會回溯。
- 兩處註解屬實:`_tg_ws_keep_strings` 確實傳 `_tg_ws_collapse`,`_C_STRIP_PAT` 的差別描述也對得上。
- 計劃檔 `[test:]` 綁的 5 支測試都存在。

固定席筆記逐條判定:
- `lumos-cli-read` 的 ★INVARIANT★(search 排除 superseded):不影響,diff 沒碰 search。
- `測試假綠形態` 的 ★INVARIANT★(還原翻紅釘要配前置斷言):不影響,新測試的情境確實成立。
  - 有明寫「前置」的:S9、淺複製、三引號對照、撞名。
  - 沒明寫的:S6 的 gb3、gb4,我關掉過濾實測確實翻紅,證明情境真的走到。
- `loop-convergence-recording`、`pitfalls-code-loop`、`reversibility-governance-ledger`(★RISK★):不影響。diff 只讓規格閘留痕與判綠事件多一個選填欄位 `ref`,帳仍是只追加,不改判定。
- `design-loop`(處置閘第五步):不影響,diff 沒碰處置閘。
- `guard-kill`(rc 優先序、JSON 純度):不影響。`_name_collision_reason` 只被測試改成走它,程式沒變。
- `bound-tests-gate`(合約綁的測試逐支真跑):不影響,新綁定的測試都存在且全綠。

最嚴重等級是 minor,blocking 共 0 條。
