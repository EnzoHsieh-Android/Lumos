severity: major

## 問 1 分層與依賴方向

新碼整體跟鄰居對得上,沒有跨層直呼。

- **放的層**:新函式全放在 `scripts/lumos` 的 `_e2e_*` 一族,緊貼 `_e2e_judge_cmd`、`_e2e_precheck` 之後。
  - 挑主線走 `_secev_mainline`,比照既有用法,如 ``file: `scripts/lumos:11690` ``。
  - 跑 git 走 `_nodehome_git`,記錄寫入走 `_e2e_record_update`,讀 JSON 走 `_e2e_load_json`。
- **子指令分派**:`_android_e2e_dispatch` 是有先例的掛法,不算第二種,對照 ``file: `scripts/lumos:68520` `` 的 `_guard_dispatch` 與 `_tq_dispatch`(``file: `scripts/lumos:67883` ``)。
- **範本腳本呼叫 lumos**:`select()` 呼叫 `lumos("android-e2e", "select", …)`,失敗時 `die(… .removeprefix("擋下:") …)`。這跟既有的 `preflight` 呼叫 `judge --precheck` 完全同一套。
- **`dirty` 欄位**:`Steps.__init__` 再叫一次 `judge --precheck` 取髒不髒。這是沿用既有子指令、方向正確,只是拿 precheck 的 rc 當布林用。
- **`--history`**:`judge` 每次都帶 `--history`,方向上沒問題。

## 問 2 命名與錯誤處理

- **命名全部對得上**:
  - 函式 `_e2e_*`。
  - 環境變數 `LUMOS_STABILITY_SCENARIO` 跟既有的 `LUMOS_STABILITY_SETTLE`、`LUMOS_E2E_*` 同族。
  - 子指令 `select`、`history` 跟 `judge` 同層。
  - 設定欄位用小寫底線,跟 `stability`、`e2e` 一致。
- **錯誤回傳對得上**:`_e2e_select_cmd` 印 `擋下:…` 到 stderr 回 2,跟 `_e2e_judge_cmd` 一樣。寫不進去只印「提醒:」不改判定,跟 `_e2e_feature_record` 一樣。

下面 A4 是欄位處理的小不一致。

## 問 3 第二種做法

## A1 本機總表 history.jsonl 另起一種追加寫法
severity: major
blocking: 是

`_e2e_history_append` 用裸 `open(p, "a")` 加 `fh.write`,沒走專案已有的追加 helper。

- 本機帳的既有做法是 `_local_ledger_append`:``file: `scripts/lumos:1698` ``。它用 `_regular_own_fd` 擋捷徑、管線和別人的檔,單次 `os.write` 並核對長度。
- 追加前還要先過 `_ledger_tail_needs_newline`,免得黏在半行後面:``file: `scripts/lumos:1840` ``(`_gate_event`)和 `scripts/lumos:1973`(`_append_governance_log`)。
- 這份總表在 `.lumos/artifacts/` 底下,是被 git 忽略的本機檔,性質等同「本機帳」。新碼卻既沒補斷行,也會跟著捷徑走,屬於「第二種做法」。

引句:「        with open(p, "a", encoding="utf-8") as fh:」

## A2 總表的讀取另寫一套切行與解析
severity: minor
blocking: 否

`_e2e_history_cmd` 用 `read_text(...).splitlines()` 加 `json.loads` 加 `continue`。

- 專案已把帳檔切行收斂成 `_ledger_lines`:``file: `scripts/lumos:20301` ``。它的註解明講 `splitlines` 會把含 U+2028 的一列劈開。
- 另有 `_drift_jsonl_iter`(``file: `scripts/lumos:51017` ``)。
- 總表寫入端同樣用 `ensure_ascii=False`,可能撞上同一個問題。

引句:「    for ln in p.read_text(encoding="utf-8", errors="replace").splitlines():」

## A3 工作目錄的 macrobench.json 讀取加驗證手寫了兩份
severity: minor
blocking: 否

`_e2e_select_cmd` 和 `_e2e_judge_partial` 各自重複同一段:`_e2e_load_json`、取 e2e、`_e2e_cfg_err(...)`。

- 專案已有讀工作目錄設定並驗證的入口 `_macrobench_config(repo)`:``file: `scripts/lumos:39402` ``。`macrobench --check-config` 走的就是它。
- 它會連 `stability` 段(`_macrobench_stab_cfg_err`)一起驗,手寫版沒驗。
- 提交樹那條 `_e2e_judge_target` 走 `_e2e_config_at` 是對的,因為既有 judge 本來就這樣。

引句:「    full, err = _e2e_load_json(root / ".lumos" / "macrobench.json")」

## A4 stability_scenarios 的併入位置與驗證次數跟鄰居不同
severity: minor
blocking: 否

- `_macrobench_config_fields` 的註解是「選填欄位驗型別並併進 cfg」,慣例是欄位在才寫入。新碼不管有沒有都寫入,缺的時候寫成 `None`。
- 同一份 `stability_scenarios` 在 `_macrobench_config_fields` 和 `_e2e_cfg_err` 各驗一次。
- 錯誤前綴也不同:一個是「macrobench.json 的 stability_scenarios…」,一個是「macrobench.json 的 e2e 段:stability_scenarios…」。同一個毛病會有兩種說法。

引句:「    cfg["stability_scenarios"] = raw.get("stability_scenarios")」

## A5 情境覆蓋欄位清單在範本腳本內聯,沒有漂移守衛
severity: minor
blocking: 否

收集腳本內聯 `("scenario", "driver", "warmup", "cycles")` 這份欄位清單。lumos 端 `_e2e_scenarios_err` 又獨立寫了一份驗證規則。

- 既有做法是,範本和 lumos 各留一份的規則,要用測試抽出兩邊比相等。
- 例子是 ``file: `scripts/test_lumos.py:19071` `` 附近的 `t_android_e2e_preflight_stability_tools`(兩支範本的 `get("test_data")` 那行比相等)。
- 這次新增的 `t_android_memstab_collect_scenario` 只測收集腳本單邊的行為,沒有抽出比對。

引句:「        st = dict(st, **{k: scen[k] for k in ("scenario", "driver", "warmup", "cycles") if k in scen})」

不對齊共 5 條,其中 major 1 條

沒有判不準、需要交編排者的項目。
