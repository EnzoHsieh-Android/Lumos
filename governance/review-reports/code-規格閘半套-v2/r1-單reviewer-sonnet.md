severity: major

以下針對凍結 patch(governance/review-reports/code-規格閘半套-v2/r1-snapshot.patch,指紋 0cd25113d1982bbe)逐 hunk 讀完並用臨時 worktree(`/private/tmp/.../scratchpad/loopcheck`,detached HEAD 895539a4,未動正式 repo 的 git)實跑驗證,findings 如下。

**F1 — W1「應」字切法會被條件段內常見雙字詞(反應/效應/因應等)提前吃掉,漏放真正的複合觸發**
`head = rest.split("應", 1)[0]` 用「第一個『應』字」當回應段起點,但中文條件句裡很常出現含「應」的詞(反應、效應、因應、適應…)。實測「當甲成立,在收到用戶反應,系統應回覆」與「當甲成立,在效應評估後,系統應回覆」——結構與測試⑤/⑦裡「當甲成立,在乙成立時,則系統應回丙」(判複合、應擋)完全同形,但因為「反應」「效應」裡先出現了一個「應」,`head` 被切在詞中間、切不到後面真正的逗號,結果兩者都回 `(True, 'trigger', '')`(判不複合、放行),等於複合觸發判準對這批輸入完全失效。已用 `_clause_grammar()` 直接呼叫驗證,不是臆測。
引句:「head = rest.split("應", 1)[0]」
severity: major
blocking: 是

**F2 — 「一條只准一個觸發子句」的意圖:「在乙成立且丙成立,系統應…」判複合是對的,不是誤擋**
task 提的這個例子結構上就是「在<條件>,<主體>應<回應>」——跟頂層要求的「觸發詞…,主體應回應」文法完全同形,只是條件內部用「且」接了兩個子條件。程式的既有前提是「頂層已經吃掉一個逗號」,`rest` 裡若自己又長成一份完整的「在X,Y應Z」,就是第二個觸發子句,按設計本來就該擋。實測 `_clause_grammar("當甲成立,在乙成立且丙成立,系統應回丁")` 回 `複合觸發`,與設計一致,非本次三處改動引進的問題。
(已讀,無 finding)

**F3 — W3 觸發詞子集只用在 `any()`,順序依賴其實不存在**
`hard = tuple(w for w in _TRIGGER_WORDS if w != "在")` 之後只餵給 `any(rest.startswith(w) for w in hard)`,`any()` 對每個元素獨立判斷、不像上面 `trig = next(...)` 那樣要「先比長的」。就算 `_TRIGGER_WORDS` 順序打亂,`hard` 的判斷結果也不變;真正吃順序的是頂層 `next((w for w in _TRIGGER_WORDS ...), None)`,W3 沒動到那行。
(已讀,無 finding)

**F4 — W2 `link_target` 對 None/空字串不會炸,DEP 抽出的連結沒過 `link_target` 但屬既有行為**
`as_list(None)` 回 `[]`,`link_target("")` 經 `strip_quotes/nfc` 一路走下來不拋例外(空字串照樣回空字串)。移除迴圈裡原本重複的 `lk.split("|",1)[0].split("#",1)[0].strip()` 對 `link_target()` 產出的項無影響(已經剝過);對 DEP 正則 `re.findall(r"\[\[([^\]|#]+)", ln)` 抽出的項也無影響,因為那個正則本身就排除了 `|`/`#`,從沒吃到別名或錨點——DEP 項一直沒走 NFC,這是修改前就有的既有行為,不是這次三處折入新引入的退化。
(已讀,無 finding)

**F5 — W1/W2 確有被測試⑦⑧鎖住(已實測)**
把 W1 的 `head` 切法還原成 r2 版 `(rest.startswith("在") and _CLAUSE_SEP_RE.search(rest))`,`t_spec_gate_code_review_r1_folds` 在臨時 worktree 裡跑出 ⑦ 翻紅(S1 被誤判複合);把 W2 的 `link_target(x)` 還原成 r1 版自寫 `re.sub` 剝括號,同一支測試 ⑧ 翻紅(別名連結字串抓不到)。兩處改動都有殺傷力,不是空殼測試。
(已讀,無 finding)

**LUMOS-IMPACT 固定席節點逐條判**
- Systems/design-loop.md(★INVARIANT★,處置閘第五步 .md 判定):本次三處改動沒碰 `_clause_check` 對審材型別/迴圈 id 的判斷,只動 `_clause_grammar` 內部的複合觸發子邏輯與 `_plan_system_links`。不影響——該 INVARIANT 管的是「審材必須是 .md 計劃」這一步,與觸發詞文法無關。但 F1 的漏判會透過共用檢查器同時影響 spec-gate 與處置閘第五步的條款文法判定(兩者共用 `_clause_check`/`_clause_grammar`),屬於品質退化而非破壞這條 INVARIANT 本身。
- Systems/guard-kill.md(★INVARIANT★ rc 優先序/json 純淨):本次 diff 未觸及 guard kill 相關程式碼路徑。不影響。
- Systems/lumos-cli-lifecycle.md(★INVARIANT★ re-inject sentinel):未觸及。不影響。
- Systems/lumos-cli-read.md(★INVARIANT★ search 排除 superseded):未觸及。不影響。
- Systems/授權與歸屬.md(★INVARIANT★ SPDX/LICENSE 白名單):diff 沒新增/改動任何被 vendor 的檔案清單。不影響。
- Systems/loop-convergence-recording.md、pitfalls-code-loop.md(★RISK★):diff 未觸及記帳/pitfalls 相關程式碼。不影響。

**總結**
最嚴重 severity:major;blocking 條數:1(F1)。
