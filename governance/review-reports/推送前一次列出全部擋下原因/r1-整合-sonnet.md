severity: major

這份設計方向站得住。我不推翻前掃 10 處的裁定,也不重報已折的項目。下面 5 條是前掃沒涵蓋的整合與同步問題。

**1.**
- spec 段落:做法 4(`--collect`)與做法 1(掛鉤改帶 `--collect`)。
- 問題:掛鉤改帶 `--collect`,但掛鉤與 `scripts/lumos` 是分開 vendor 到消費專案的。新掛鉤搭舊 lumos 時,舊 lumos 的參數解析不認得 `--collect`,回傳碼 2。掛鉤對 code-loop check 只認 rc1 為擋下,其他非零一律放行。結果是新舊混用時,代碼審那一整道(合約測試、表態、新增告警、留痕)靜默失效。spec 的〈回退〉與〈實務隱患〉都沒提混用。S6 只保證「記下的擋下不會變放行」,管不到這條路。
- 撞牆點:
  - 引句:「不帶時行為與輸出不變(其他呼叫者如 CI 不受影響)」
  - file: `scripts/hooks/pre-push:476-480`。這段只在 `cl_rc -eq 1` 時擋下,rc2 會落到「rc≠0/1:fail-open 放行」。
  - file: `scripts/lumos:23886` 和 `scripts/lumos:25744` 是 vendor 白名單,`scripts/hooks/pre-push` 在其中。
  - file: `scripts/lumos:27478-27488` 的 `_enforcement_prepush_ungated` 已證明「舊掛鉤搭新工具」會發生,但沒有反方向(新掛鉤搭舊工具)的檢查。
- 缺少的設計:掛鉤要先探測 `--collect` 支不支援,不支援就退回不帶旗標;或把 rc2 當成這道工具壞了,維持擋下。要新增一支混用測試,用假的舊 lumos 回 rc2。
severity: major
blocking: 是 — 新掛鉤搭舊工具時代碼審閘靜默放行,是守衛被吞掉的路徑,而驗收條款 S1 到 S6 沒有一條覆蓋它

**2.**
- spec 段落:做法 5(預演指令)。
- 問題:預演模式用環境變數 `LUMOS_PUSH_PREVIEW=1` 讓掛鉤「到統一判斷那一步就停:沒有擋下回 0」。這是一個新的「跳過全套測試並放行」開關。
  - 任何 shell 或程序若匯出這個變數(例如 `export` 後忘了取消),之後每次真推送都會跳過全套測試,且掛鉤回 0。
  - 現有的略過開關(`LUMOS_SKIP_DRIFT_CHECK`、`LUMOS_SKIP_REREAD_CHECK`)都會記帳,這個不會。
  - spec 的 S5 只驗 `push-preview` 這條路徑,沒有驗「真推送時環境變數殘留」。
  - 這也違反 spec 自己的 S6:「沒有一條路徑能把擋下變成放行」。
- 撞牆點:
  - 引句:「帶環境變數 `LUMOS_PUSH_PREVIEW=1` 跑掛鉤;掛鉤看到它,到統一判斷那一步就停」
  - file: `docs/lumos-toolchain-knowledge/Systems/hook信任邊界.md` 是這類環境變數信任邊界的家,spec 沒有對照它。
- 缺少的設計:改用只有 `push-preview` 才能產生的、與子行程綁定的信號(例如額外參數,或掛鉤確認 stdin 是 `push-preview` 組出的)。至少要記帳。
severity: major
blocking: 是 — 新增無記帳的測試跳過放行開關,殘留環境變數即可繞過全套測試

**3.**
- spec 段落:做法 1(新增共用函式 `pp_record_block` 與陣列 `_PP_BLOCKS`)。
- 問題:掛鉤第 19 行是 `set -u`,shebang 是 `#!/usr/bin/env bash`,macOS 系統內建 bash 3.2 會落在這條路徑。在 bash 3.2 上,對空陣列做 `"${_PP_BLOCKS[@]}"` 展開會報 unbound variable。所以「沒有任何擋下」的正常路徑會在判斷點崩潰。掛鉤其他地方已用 `${_PP_LINES+"${_PP_LINES[@]}"}` 繞過這個坑,spec 沒要求新陣列照做。
- 撞牆點:
  - file: `scripts/hooks/pre-push:19`(`set -u`)。
  - file: `scripts/hooks/pre-push:66` 附近的 `${_PP_LINES+"${_PP_LINES[@]}"}` 是既有的繞法。
  - S2 的「沒有擋下就照舊跑全套」若在 CI 的 Linux bash 5 上跑,抓不到這個問題。
- 缺少的設計:`_PP_BLOCKS` 與 `${#_PP_BLOCKS[@]}` 的寫法要寫進 spec,測試要在 bash 3.2 下跑一次。
severity: major
blocking: 是 — 掛鉤在常見的 bash 版本上,無擋下的正常路徑會崩潰

**4.**
- spec 段落:做法 1 與「既有守衛要一起更新」。
- 問題:spec 只列了 `t_prepush_gates_stop_on_signal` 與 `t_prepush_cheap_gates_run_before_expensive_suite` 兩支守衛。實作後要同步的檔與測試清單不全。
- 具體要改的檔:
  1. `scripts/hooks/pre-push` 是 anchor 管轄檔(ANCHOR_FILES,file: `scripts/lumos:25744`),`scripts/test_lumos.py` 也是。改它們後要跑 `lumos anchor approve --note`,並提交 `governance/anchor-baseline.json`。spec 對這個排序沒有任何一句話,而這正是掛鉤第一道閘會擋的事。
  2. `_enforcement_prepush_ungated`(file: `scripts/lumos:27476-27488`)逐行找含「note-audit reread-check」的非註解行,並要求那一行有 `--gate`。若實作把呼叫包進 `pp_record_block ... "$PY" ... reread-check`、讓 `--gate` 掉到別行,會被誤判為沒接線。
  3. 掛鉤裡 `# lumos drift check` 與 `# lumos note-audit reread-check` 兩串「上線標記」註解,lumos 用 `git log -S` 靠它找上線點(file: `scripts/lumos:31405-31440` 與 `35159`、`35413`)。改寫那一段時不能動到這兩串。
  4. 測試 `t_prepush_gates_stop_on_signal` 用 regex 數 `pp_stop_if_signaled` 行,要求恰好 8 行(file: `scripts/test_lumos.py:63788-63830`)。實作若新增或搬動這個函式的呼叫,這個數字就會變。
  5. 表驗證「某道擋下後不會再呼叫後面的閘」的測試要先全數盤點:`t_prepush_and_ci_wire_drift_check`(file: `scripts/test_lumos.py:63838`)、`t_prepush_hook_calls_spec_gate_push_check`、drift 與 reread 各自的接線測試。收集模式下,前一道擋下後,後面的閘照樣會被叫到,若有測試斷言「沒被叫」就會翻紅。spec 沒要求先做這個盤點。
- 缺少的文件更新:
  - file: `skills/lumos-project-notes/commands/06-代碼審與推送.md:8` 第 8 列寫「四個獨立判定序列早退」,要改成說明 `--collect` 與預設的行為。
  - file: `scripts/lumos:51074` 的註解「序列早退,先中的先報」同步改。
  - file: `docs/lumos-toolchain-knowledge/Systems/棧別提問表態閘.md:31` 與 `Projects/棧別提問表態閘_計劃.md:96` 的相同敘述同步改。
  - file: `skills/lumos-code-loop/SKILL.md:13` 講「四個獨立判定各自擋」,其實與新舊都相容,但要補一句掛鉤改用 `--collect`。
  - `bound-tests-gate.md` 第 34 行寫「六道閘都先過 pp_stop_if_signaled,擋下後不跑全套」,要加一句收集語意。
  - 同一份節點第 111 行寫回頭重讀「排在存量漂移檢查之後」,順序描述要改。
  - `存量漂移守衛` 與 `筆記內容審` 兩篇各自記錄了自己那一段掛接,也要更新。
- 撞牆點:
  - 引句:「既有守衛要一起更新:`Systems/bound-tests-gate` 綁的 `t_prepush_gates_stop_on_signal`」
  - 驗收條款完全沒有「文件與既有測試清單」這一項。
severity: major
blocking: 是 — 漏列 anchor 簽名順序,會讓實作者推送時被第一道閘擋下;漏列既有測試的盤點,會讓守衛翻紅而 spec 沒有交代

**5.**
- spec 段落:`lands_in` 與〈實務隱患〉的「對外送出」。
- 問題一:`lands_in` 只列 `Systems/bound-tests-gate` 與 `Systems/pitfalls-code-loop`。
  - 新子命令 `push-preview` 沒有家。
  - 收集邏輯的家在掛鉤,`bound-tests-gate` 的 about_code 列有 `scripts/hooks/pre-push`,這點合理。
  - 但 `--collect` 改的是 `scripts/lumos` 的 `_codeloop_guard_verdict`,而 `pitfalls-code-loop` 的 about_code 沒有列 `scripts/lumos`(我讀到的檔頭沒有 about_code 條目,此點 ⚠ 需實作時以 `lumos home check` 覆核)。
  - 鐵則 5 要求改到的每支檔都有家,實作前要先 `lumos home check` 確認。
- 問題二:〈已排除:對外送出〉寫「預演不推送;只有真推送才連遠端」。但做法 5 又要「遠端查不到那個分支就當新分支,遠端提交填全零」,這要查詢遠端(`git ls-remote` 類),是對外連線。兩句互相矛盾。
- 撞牆點:
  - 引句:「已排除:對外送出:預演不推送;只有真推送才連遠端,行為照舊。」
  - 引句:「遠端查不到那個分支就當新分支,遠端提交填全零」
severity: minor
blocking: 否 — 屬文件與歸屬的不一致,不改變守衛行為,實作時補上即可

**CI(`.github/workflows/ci.yml`)**
- CI 在 `ci.yml:186` 呼叫 `code-loop check`,不帶 `--collect`,行為不變,不受影響。
- 已讀,無 finding。

**固定席節點**
- 派工尾端沒有附固定席節點,所以沒有逐條判。

**實務隱患逐類**
- 守衛面:見 1、2、3。
- 金流:已讀,無 finding。
- 不可逆:已讀,無 finding。

最嚴重 severity: major,blocking 共 4 條(finding 1、2、3、4)。
