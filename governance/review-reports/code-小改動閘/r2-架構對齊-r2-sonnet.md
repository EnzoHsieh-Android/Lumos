severity: clean

對照過的既有寫法:

- 折入①(簿記檔判準):新碼 `path in _BOOKKEEPING_FILES or path.startswith(_BOOKKEEPING_DIR) or Path(path).suffix.lower() in _PITFALL_DIFF_SKIP_EXT` 跟既有 `_stack_changed_ok`(scripts/lumos:22135-22138)`ext not in _PITFALL_DIFF_SKIP_EXT and cur_file not in _BOOKKEEPING_FILES and not cur_file.startswith(_BOOKKEEPING_DIR)` 是同一套判準、同一種寫法,真的走單一源,沒有自開第二份正則。
  引句:「哪些檔不算程式改動」沿用既有單一源:簿記檔 _BOOKKEEPING_FILES/_BOOKKEEPING_DIR + 非代碼副檔名 _PITFALL_DIFF_SKIP_EXT + 圖譜筆記(代碼審 r1 架構席:自開正則=第二套判準會漂)

- 折入②(錨點基準檔路徑與解析):新碼 `_j.loads((rr / _ANCHOR_BASELINE_REL).read_text(encoding="utf-8")).get("anchors")` 跟既有三處讀基準線的寫法(scripts/lumos:17769 `bp = root / _ANCHOR_BASELINE_REL` … `data.get("anchors")`;17852、17963 同樣 `bp = repo_root / _ANCHOR_BASELINE_REL`)一致,常數也是同一顆 `_ANCHOR_BASELINE_REL = "governance/anchor-baseline.json"`,不是手寫路徑猜格式。
  引句:錨點清單走既有路徑常數與解析寫法(代碼審 r1 架構席:別再手寫路徑、別再猜形狀)

- 折入③(逃逸帳時間戳比對):新碼改用 `_loop_ts_key` 算 UTC 秒數再比,None 就整筆跳過(fail-open),跟既有呼叫端(scripts/lumos:5290-5302 記 first ts 那段、7988 `_loop_ts_newer`)同一種「k is None 就不採信」的處理方式,沒有另開一套裸字串比對。
  引句:時間戳一律換算 UTC 再比(代碼審 r1 兩席:字串比對在時區位移不同時會靜默反過來)

其餘掃過的面向,沒發現「引入第二種做法/跨層直呼/自刻已有工具函式/繞過既有寫入口/跟同層對照檔慣例相反」:

- git 呼叫慣例:`subprocess.run(["git", "-C", str(rr), "-c", "core.quotePath=false", "diff", "--numstat", "--no-renames", git_range, "--"], capture_output=True, text=True, errors="replace")` 跟同檔其餘 `git -C … diff --name-only` 呼叫(scripts/lumos:5762、8549)同一套旗標與收尾 `--` 慣例。
- `_small_change_check` 內部全部借用既有入口:`_plan_system_links`、`_impact_home_map`/`_nodehome_key`、`_escape_rows_for`,沒有自己再走一套解析或查表。
- idx 元組多塞第 5 個欄位(`git_range`)延用檔內本來就有的「元組尾巴加欄位」慣例(scripts/lumos:5478 已經是 5 元組 `(split, default, methods_for, plats, names)`),不是新形狀;`_spec_gate_push_one` 的 docstring 沒同步改成 5 元組(還寫「idx=(split, default, methods_for, plats)」),這是文件跟不上,不算架構分歧,已記下但不列 severity。
- `_TIER_ROSTER[("code","light")]` 的「架構對齊」設 `occupies_w=True`:乍看跟 code/standard、design/standard 裡的「架構對齊」一律 `False`(不佔 W)不一樣,但對照 `mode: "single"` 的既有慣例(design/light 的「通才」單席正是 `occupies_w=True`),light 這裡是唯一一席、走的是 single 模式的既有規則,不是另開一套判法。
- 留痕欄位命名(`n_manual`、`manual_only`、`small_change_rule`)跟既有 `n_clauses`/`n_red`/`n_keeps` 同一種 snake_case、`n_` 前綴計數慣例。
- `[manual:]` 狀態判斷 `b["state"] == "manual"` 跟既有 `b["state"] == "bad-name"`(scripts/lumos:4945)同一種寫法,沒新開狀態機。

