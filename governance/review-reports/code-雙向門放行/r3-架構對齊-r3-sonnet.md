severity: clean

對照過的既有寫法(都一致,沒有引入第二套):
- 推送前反查「被改檔的家」:折入後改呼叫全檔唯一的 `_impact_home_map(env)` 取得 `homes, _own`,再用 `homes.get(_nodehome_key(f), [])` 查——跟 `_impact_confirmed_homes`(scripts/lumos:24174-24175)同一個呼叫慣例(`homes, _own = _impact_home_map(env)` 接 `homes.get(_nodehome_key(rel_file), [])`),沒有自己重掃 about_code。
- 正文連結只認可見行:`_plan_system_links` 改用 `_visible_lines(text.splitlines())` 取行、`_strip_inline_markup(ln)[0]` 剝行內反引號/註解才餵 `WIKILINK_RE.findall`,跟同檔其他可見文字掃描點(scripts/lumos:4889-4892 已排除行解析、5127-5128 掃描主迴圈、6408 severity 行解析)同一套「行層級 `_visible_lines` + 行內層級 `_strip_inline_markup`」兩段式規則,沒有自建第二套 fence/inline 判定。
- `_door_judge`/`_door_linked_signals` 重用既有的 `PITFALL_CLASSES`/`_PITFALL_COMPILED`(scripts/lumos:17922-17928)、`IRREVERSIBLE_RE`/`CHECKPOINT_RE`(scripts/lumos:3962-3963)、`_contract_key_matches`(scripts/lumos:25223)——沒有另刻一份關鍵字表或合約行掃描。
- 留痕寫入 `_spec_gate_record` 呼叫 `_vault_write_lock(env.vault)` + `_jsonl_append_verified(...)`,跟審查帳既有寫入口(scripts/lumos:7111/7218/8494/8656、`_auto_escape` 內部 8465)同一支,沒有繞過鎖或自己 open(path,"a")。
- `_spec_gate_push_check` 裡呼叫 `_run_bound_tests(rr, items, tails=tails)`、`_auto_escape(env, "push-gate", "major", ...)`、`_escape_auto_failed(...)`,跟 code-loop 既有呼叫點(scripts/lumos:5379/5414、7131/7136)同一組函式、同樣的呼叫形狀。
- 新增的 git 呼叫(`_plan_first_commit`/`_test_exists_before`/`_spec_gate_push_check` 裡的 `git diff --name-only`)都用 `subprocess.run(["git", "-C", str(rr), ...], capture_output=True, text=True, errors="replace")`,跟全檔既有幾十處 git 呼叫慣例(如 `_git_head` scripts/lumos:8380-8392)同款,沒有另開 shell=True 或包一層新的 git 執行器。
- `_h2_section_lines` 把原本 `_rollback_section_chars` 裡手刻的找節迴圈抽成共用函式,給回退節與新的實務隱患節共用,而不是複製一份改章節標題 regex——延續本檔「同一種掃描邏輯只寫一次」的既有原則(patch 內註解本身也點名 r4 架構席這條)。
- pre-push hook 新增的 `spec-gate --push-check` 呼叫沿用既有 rc 判斷與 `>&2`/`exit 1` 寫法,跟同一段既有的 code-loop check 呼叫(`cl_rc`)同構,沒有引入新的錯誤處理風格。

沒發現引入第二種做法、跨層直呼、自刻已有工具函式、繞過既有寫入口、或跟同層對照檔慣例相反的情形。
