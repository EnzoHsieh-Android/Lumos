severity: major

1. `spec-gate` 對「用节点短名叫」直接失灵——先用 `env.resolve()` 拿到 vault 相對路徑當成 CWD 相對路徑判存在,判不到才退回組 vault 絕對路徑,但退回時又直接拿原始短名接 `.md`(漏了 `Projects/` 這層),導致節點明明存在也回「找不到」。已用真倉庫重現:`python3 scripts/lumos spec-gate 規格落成可驗收條件_計劃 --no-run` 印「擋下:找不到計劃節點」rc=2,同一個名字 `spec-trace` 卻能正常吃(`env.find` 走法不同)。
引句:「p = env.resolve(node) if hasattr(env, "resolve") else None」
severity: major
blocking: 是

2. `_clause_grammar` 的「複合觸發」偵測把觸發子句拆完後,只要回應段開頭剛好是「在」這個常見介詞(不是第二個條件句)就誤判成複合觸發、整條判不合文法。已用函式直接驗證:`'當A時，在B情況應如何處理'` 與 `'若啟用開關，在收到請求時應回應 200'` 都被判 `(False, 'trigger', '複合觸發…')`,但這兩句都是單一觸發、語意正常的條款。此檢查會在 `_SPEC_GATE_SINCE`(2026-09-18)後套進處置閘第五步的 ★INVARIANT★,把寫法正常的條款當格式錯擋下。
引句:「if not any(rest.startswith(w) for w in _TRIGGER_STOPWORDS) and any(rest.startswith(w) for w in _TRIGGER_WORDS):」
severity: major
blocking: 是

3. `_plan_system_links` 讀 `lands_in` 時只認 `isinstance(li, list)`,若 frontmatter 把它存成純字串(YAML 單值,常見手改或舊筆記),整條值被靜默丟掉、不進 `_regress_sources`。同一個欄位在別處(`scripts/lumos:16280`、`:25714`)一律先過 `as_list()` 正規化,唯獨這支相依回歸的新函式沒有沿用,等於讓「機器產的回歸條款,作者不能挑」這個設計目的在這種輸入下悄悄失效、沒有任何提示。
引句:「li = note.fields.get("lands_in")」
severity: major
blocking: 否

4. `_rollback_section_chars` 只認 ATX 二級標題(`^##\s+回退…$`),不認 CommonMark 合法的 Setext 標題(`回退\n----`)。已用函式直接驗證:ATX 寫法量出 24 字,Setext 寫法同樣內容卻回 `None`(視同沒有回退節),會讓寫 Setext 標題但內容其實足夠的計劃被誤判擋下。此 repo 現存筆記一律用 `##` 慣例,實際觸發機率低,故降級為 minor。
引句:「_ROLLBACK_H2_RE = re.compile(r"^##\s+回退\s*(?:[(（][^)）]*[)）])?\s*$")」
severity: minor
blocking: 否

5. `_run_bound_tests` 對空行/只有 `[SN]` 標記行/全形逗號都有正確處理(空正文回「條款正文是空的」、`[S1] ---` 判「缺應」不炸、全形逗號 `，` 被 `_CLAUSE_SEP_RE` 正常辨識),已逐一函式呼叫驗證,無 finding。
severity: minor
blocking: 否

6. `_ran_count` 對 pytest 摘要「1 passed, 1 warning」「3 failed, 2 passed」「no tests ran」都各自給出合理結果,且 `_spec_gate_verdict` 的「支數 N 先於退出碼看」是文件明載的設計選擇(多支匹配一律判 weak、不管有沒有失敗),不是本次改動引入的缺陷,無 finding。
severity: minor
blocking: 否

7. `pre-push` 兩個新增的 `grep -q` 只決定要不要呼叫逃逸記帳,呼叫本身接 `|| true`;這是故意的 fail-open 設計(註解已明寫「記帳失敗不能變成擋推送的第二個理由」),不會把 `code-loop check` 本身的 rc1/rc2 吞掉——兩個 grep 在 `cl_rc -eq 1` 分支內部,原本的 `exit 1` 完全沒被動到,無 finding。
severity: minor
blocking: 否

8. `cmd_canary` 新增的 `_hit`/`_precision` 判定用「逐條 finding_severities」決定要不要記逃逸,但寫入 `_auto_escape` 時仍用輪級 `severity` 而非該條發現自己的等級;不過輪級 `severity` 本身文件明載是「整輪最高值」,不可能低於任一條發現,所以不會造成誤報等級偏低,無 finding。
severity: minor
blocking: 否

9. `_ci_step_is_test` 對步驟名裡出現的 `;`(而非作為多步分隔符)找不到具體會被誤判的真實步驟名輸入,只能推測;依抑噪原則不標。⚠
severity: minor
blocking: 否

10. LUMOS-IMPACT 固定席節點逐條判:①`Issues/code-loop守衛main-direct盲區.md`(事故)——這次改動只在 `code-loop check` 回傳 rc1 之後新增兩段觸發逃逸記帳的 grep,沒有動到 main-direct push 判斷本身,不影響。②`Systems/design-loop.md` ★INVARIANT★——`_disposal_clause_step` 改呼叫共用 `_clause_check`,原本「未標必擋/懸空只提醒/重複定義擋」的綁定判定邏輯原封搬過去未變,合約成立;但新掛的句式檢查帶 finding #2 的假陽性,會在 `_SPEC_GATE_SINCE` 之後波及此合約(已在 finding #2 計分,不重複開)。③`Systems/guard-kill.md`——這批完全沒碰 `cmd_guard_kill`/kill 相關程式碼,不影響。④`Systems/lumos-cli-lifecycle.md`——沒碰 re-inject/sentinel 邏輯,不影響。⑤`Systems/lumos-cli-read.md`——沒碰 `cmd_search` 的 superseded/stale 過濾,不影響。⑥`Systems/授權與歸屬.md`——沒碰 `_VENDORED_TOOLKIT`/deinit/vendor 白名單邏輯,不影響。
severity: minor
blocking: 否

尾行總結不再出現比檔首更高等級字樣:最嚴重 severity 為 major,blocking 為 2 條(finding 1、finding 2)。
