severity: clean

對照過的既有寫法(都一致,沒有引入第二套):

## F1 推送前反查家改走唯一算法 _impact_home_map,不自己再掃 about_code
severity: clean
blocking: false
引句:「homes, _own = _impact_home_map(env)」
引句:「for srel in homes.get(_nodehome_key(f), []):」
這批:`_spec_gate_push_check` 裡 `homes, _own = _impact_home_map(env)` 取家對照表,再 `homes.get(_nodehome_key(f), [])` 查每支被改檔的家。
既有:`_impact_confirmed_homes`(scripts/lumos:24174-24175)同一組呼叫慣例:`homes, _own = _impact_home_map(env)` 接 `homes.get(_nodehome_key(rel_file), [])`。
兩處呼叫形狀逐字相同,不是第二套算法。

## F2 正文連結只認可見行,沿用 _visible_lines + _strip_inline_markup 兩段式規則
severity: clean
blocking: false
引句:「for _no, ln in _visible_lines(text.splitlines()):」
引句:「links += [link_target(m) for m in WIKILINK_RE.findall(_strip_inline_markup(ln)[0])]」
這批:`_plan_system_links` 給了 text 時,先用 `_visible_lines(text.splitlines())` 取可見行,再用 `_strip_inline_markup(ln)[0]` 剝行內程式碼才餵 `WIKILINK_RE.findall`。
既有:同檔其他掃描點(如 severity 行解析 scripts/lumos:6408)同款「行層級 `_visible_lines` + 行內層級 `_strip_inline_markup`」兩段式規則,沒有自建第二套 fence 判定。

## F3 門判定重用既有的實務隱患關鍵字表與合約行掃描,沒有另刻一份
severity: clean
blocking: false
引句:「for cls, pats in _PITFALL_COMPILED.items():」
這批:`_door_judge` 逐行掃描時直接迭代既有的 `_PITFALL_COMPILED`(定義在 scripts/lumos:17928,來自 `PITFALL_CLASSES`),並呼叫既有 `_contract_key_matches` 抓 ★IRREVERSIBLE★/★CHECKPOINT★。
既有:`PITFALL_CLASSES`/`_PITFALL_COMPILED` 是全檔既有唯一的關鍵字表,`_contract_key_matches` 是既有唯一的合約行掃描函式;這批沒有重新定義關鍵字或另寫合約行 regex。

## F4 留痕寫入沿用審查帳既有寫入口(鎖+驗證寫入),沒有繞過
severity: clean
blocking: false
引句:「with _vault_write_lock(env.vault):」
這批:`_spec_gate_record` 在 `with _vault_write_lock(env.vault):` 底下呼叫 `_jsonl_append_verified`,寫進同一份 `.canary-log.jsonl`。
既有:審查帳其餘寫入點(scripts/lumos 的 `_auto_escape`、code-loop pass 記帳)同樣是「先拿 `_vault_write_lock`、再走 `_jsonl_append_verified`」這組合,不是自己開檔 append。

## F5 推送閘裡的測試執行與逃逸自動記,呼叫既有函式不是另刻一份
severity: clean
blocking: false
引句:「results, rerr = _run_bound_tests(rr, items, tails=tails)」
這批:`_spec_gate_push_check` 裡的紅綠判定直接呼叫既有 `_run_bound_tests(rr, items, tails=tails)`,測試沒全綠時呼叫既有 `_auto_escape`/`_escape_auto_failed` 記逃逸。
既有:code-loop check 路徑(scripts/lumos:5379、5414、7131、7136)是同一組函式的既有呼叫者,呼叫形狀一致。

## F6 新增的 git 呼叫沿用全檔既有的 subprocess.run(["git", "-C", ...]) 慣例
severity: clean
blocking: false
引句:「r = subprocess.run(["git", "-C", str(rr), "-c", "core.quotePath=false", "diff", "--name-only", git_range, "--"],」
這批:`_spec_gate_push_check` 算改動範圍時用 `subprocess.run(["git", "-C", str(rr), "-c", "core.quotePath=false", "diff", "--name-only", git_range, "--"], capture_output=True, text=True, errors="replace")`。
既有:全檔幾十處 git 呼叫(如 `_git_head`)都是同一種「`-C` 指 repo 根、`capture_output=True, text=True, errors="replace"`」寫法,沒有另開新的 git 執行器或改用 shell=True。

## F7 回退節與實務隱患節找節邏輯合併成一支共用函式,不是各寫一套
severity: clean
blocking: false
引句:「fence 內不算;沒有那一節回 None。回退節與實務隱患節共用(雙向門放行_計劃 S9;r4 架構對齊席:找節邏輯不准長出第三套)。」
這批:把原本 `_rollback_section_chars` 裡手刻的找節迴圈抽成 `_h2_section_lines(text, h2_re)`,`_rollback_section_chars` 與新的 `_door_exclusions`(找「## 實務隱患」節)共用同一支。
既有:延續本檔「同一種掃描邏輯只寫一次」的既有原則,patch 本身的註解也點名這是接續代碼審 r2/r4 的收斂,不是新開平行邏輯。

## F8 pre-push hook 新增的 spec-gate --push-check 呼叫沿用既有 rc 判斷寫法
severity: clean
blocking: false
引句:「"$PY" "$GRAPHCTL" spec-gate --push-check "$_range" --repo "$REPO_ROOT" >&2 || sg_rc=$?」
這批:`sg_rc=0` 起手、`|| sg_rc=$?` 接住非零 rc、按 `sg_rc -eq 1` 才擋下 exit 1。
既有:同一段 hook 裡緊接著的 code-loop check 呼叫(`cl_rc=0` … `|| cl_rc=$?`)是同構寫法,兩段用同一種 rc 收集慣例,沒有引入新的錯誤處理風格。

沒發現引入第二種做法、跨層直呼、自刻已有工具函式、繞過既有寫入口、或跟同層對照檔慣例相反的情形。
