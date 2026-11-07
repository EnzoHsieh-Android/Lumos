severity: minor

最高只到 minor。我沒找到會讓閘做出錯誤行為的缺陷。一個旁證:我拿本計劃自己的 `## 依據來源` 表實跑 `lumos spec-gate 計劃依據來源必填_計劃 --no-run`,輸出「依據來源: ✓ 31 列」。

逐行與跨檔角度的檢查結果:
- 批次 git log 的改名接續邏輯和單篇 `_plan_first_day` 等價。
- 推送前改成 `bad, oks = … if plans else ([], [])` 後,bad 為 None 與 plans 為空兩條路徑,行為都跟舊版一致。
- `_validate_repo_ref` 已擋絕對路徑與 `..`。

F1 掛鉤的通用文案沒有任何測試綁著,圖譜裡卻掛了 `[test:]`
引句:「echo "推送前規格閘擋下,原因見上面列的每一條。" >&2」
severity: minor
blocking: 否
- 失敗情境:`scripts/hooks/pre-push` 把固定文案換成通用文案,`pp_record_block` 的理由也跟著換。我在 `scripts/test_lumos.py` 搜「原因見上面列的每一條」與「推送前規格閘擋下」,零命中。
- 後果:有人把這兩行改回舊的「風險低計劃的條款測試沒全綠」,沒有任何測試會紅,又會把缺〈依據來源〉講成測試沒綠。
- 圖譜問題:`bound-tests-gate.md` 新增的 WHY 行綁了 `[test:t_spec_gate_push_sources]`。那支測試只呼叫 `_hre_push` 與 `_spec_gate_push_bad_head`,看不到 pre-push 腳本印什麼,綁定名不副實。
- file: `scripts/hooks/pre-push:605`

F2 健檢 S22 把任何例外當成綠勾
引句:「ok(f"〈依據來源〉這段跳過({_e22.__class__.__name__})")」
severity: minor
blocking: 否
- 失敗情境:`_doctor_plan_sources_lines` 內部出任何例外(例如 `_plan_sources_problems` 對某篇怪文字炸掉),健檢會印綠勾式的 `ok(...)`,只在括號裡留一個例外類名。沒有行號,也沒有計入提醒段數。
- 後果:這段提醒會整段靜默消失,CI 日誌看起來是通過。同一個函式裡 S17 到 S21 都沒有這種包法,壞了就是壞了。
- 更簡單的做法:不包 try;要容錯就改用 `warn_soft` 印出例外訊息。

F3 「是不是新計劃」的判斷在 doctor 與規格閘各寫了一份
引句:「firsts, fetched, out = None, False, []」
severity: minor
blocking: 否
- 重複了什麼:`_plan_sources_is_new`(規格閘與推送前用)與 `_doctor_plan_sources_lines` 內聯的版本,都在做「created 與首次進 git 取較晚者,讀不到當今天,比生效日」。
- 後果:將來有人調整規則,例如生效日邊界改成大於、淺複製的處理,必須同時改兩處。
- 漂移守衛:只有 `t_doctor_plan_sources_batch_dates` 一支測試對得到,且只驗複製與改名兩種情境。
- 更簡單的做法:讓 `_plan_sources_is_new` 接受可選的預取首次加入日(`firsts` 字典),doctor 只負責預取。

F4 保險放在 vault 是 repo 根目錄時的批次日期整批失效(推論,未實跑)
引句:「first, day, pre = {}, None, (vrel + "/") if vrel else ""」
severity: minor
blocking: 否
- 失敗情境:`vrel` 由 `env.vault.resolve().relative_to(repo)` 算出。圖譜剛好在 repo 根目錄時,`str(Path('.'))` 是 `"."`,是真值。pathspec 變成 `./Projects`,前綴變成 `"./"`。但 git 印出的路徑是 `Projects/x.md`,`k.startswith("./")` 恆為假,函式回傳空字典。
- 後果:所有 `created` 早於生效日、但實際是複製舊計劃而來的計劃,批次這邊都判舊,漏列。單篇的 `_plan_effective_day` 走的是別條路,結果會不一致。
- 更簡單的做法:`vrel in (None, "", ".")` 時統一當成無前綴。

F5 批次 git 逾時或失敗時悄悄退回只看 created
引句:「capture_output=True, text=True, errors="replace", timeout=60)」
severity: minor
blocking: 否
- 失敗情境:大 repo 上 `git log --name-status -M` 掃整個 Projects 歷史,逾時就 `return None`,呼叫端 `(firsts or {}).get(rel)` 當作沒有 git 日期。
- 後果:該複製判新的計劃被判舊,不列。提醒會悄悄變少,沒有任何標示「這次沒查到 git 日期」。
- 計劃只寫了「淺複製只看 created」,沒寫逾時這條退路。

F6 出處的 `:行號` 被剝掉後完全不驗
引句:「tok = _PLAN_SRC_LINENO_RE.sub("", m.group(1).strip())」
severity: minor
blocking: 否
- 失敗情境:出處寫 `` `scripts/a.py:99999` `` 會放行。`_validate_repo_ref(Path(rr), tok, None)` 傳 `line=None`,只驗檔案存在。
- 對照:`_validate_repo_ref` 本身有 `line_out_of_range` 判定,這裡卻特意不用。skill 與計劃都寫「可帶 `:行號`」,讀者會以為行號有被查。
- 後果:行號超出檔尾的出處照樣放行,跟「讀者查得到」的目標不符。

總結:最嚴重是 minor,會擋 0 條。
