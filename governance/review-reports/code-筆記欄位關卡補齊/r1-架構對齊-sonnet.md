severity: major

## 問 1:分層與依賴方向

對齊。新碼的位置與呼叫方向都跟鄰居一樣:
- `_lint_new_rules`(scripts/lumos:5130)與 `_note_lint_config`(scripts/lumos:5089)緊接在 `cmd_lint`/`_lint_collect`(scripts/lumos:4817、5104 一帶)之後,是同一層(lint 判定層),不是硬塞進別層。
- `run_doctor` 的 L 段(scripts/lumos:1210 起)呼叫 `_note_lint_config`,跟既有 S10 段呼叫 `_nodehome_config(_vault_repo_root(env))["mode"]`(scripts/lumos:995)是同一種「健檢段呼叫某功能自己的 config reader」走法,不是跨層直呼私有細節。
- `_lint_new_rules` 呼叫既有的 `_about_code_path`(scripts/lumos:13792 一帶),`cmd_set` 呼叫既有的 `_nodehome_resp_ok`——這兩支本來就是「寫入端」判斷,lint 端呼叫它們是刻意共用同一支判法,不是另開一份重複邏輯,方向正確。

引句:「`lumos lint` 與 `doctor` 都呼叫它們」

## 問 2:命名與錯誤處理

對齊。`cmd_set` 新擋的訊息格式跟原本 `key not in SCALAR_KEYS` 那段(scripts/lumos:13701 一帶)同一套「擋下:…,檔案沒動」+ `file=sys.stderr` + `return 2`;`_note_lint_config` 裡「看不懂…已用 on」「是捷徑檔,不跟過去讀」這些措辭,逐字對照 `_nodehome_config`(scripts/lumos:21547 一帶,審查前既有代碼)幾乎是照抄同一句式;`DATE_RE`、`_lands_in_bad`、`as_list`、`parse_decisions` 全部重用既有符號,沒有另造一份。

引句:「擋下:負責範圍至少 {_NODEHOME_RESP_MIN_CHARS} 個字」

## F1 `_note_lint_config` 回傳形狀跟它自稱效法的 `_nodehome_config` 不一樣,另開一種讀設定檔的做法

severity: major
blocking: yes

這一帶讀 `.lumos/config.json` 子區塊、判 on/warn/off 閘、順便收警告清單的函式,在這次改動之前已經有三支同款:`_nodehome_config`、`_lint_new_config`、`_stack_questions_config`,三支的回傳形狀完全一致——單一個 dict,警告清單是 dict 裡的 `warnings` 鍵,呼叫端一律 `cfg["mode"]` / `cfg["warnings"]` 取值(例如既有的 `_nh_mode = _nodehome_config(_vault_repo_root(env))["mode"]`,scripts/lumos:995)。這支新開的 `_note_lint_config` 卻改回傳一個 2-tuple `(mode, warns)`,呼叫端變成 `_nl_mode, _nl_cfgw = _note_lint_config(...)`(scripts/lumos:1210)與 `mode, cfg_warns = _note_lint_config(...)`(scripts/lumos:4829)。

它自己的 docstring 明講「結構照 `_nodehome_config`」,但只抄了行為(捷徑檔當沒設、JSON 壞掉退預設、值看不懂當 on 且警告),沒抄回傳形狀——這是同一份 diff 內部自相矛盾的宣稱,不是判準模糊的情況。三支既有的都用 dict(+`warnings` 鍵),這支是唯一用 tuple 的一支,屬於「這個專案原本已經有一種做法,這次另開一種」。

引句:「結構照 _nodehome_config:設定檔不存在 → 用預設、不警告;讀不了、JSON 壞掉、是捷徑檔、note_lint 不是物件 →」
引句:「_nl_mode, _nl_cfgw = _note_lint_config(_repo_root_from_env(env))」

佐證:
- scripts/lumos:5089-5116(`_note_lint_config` 定義,回傳 `mode, warns` 這種 tuple)
- scripts/lumos:5090-5093(docstring 自稱「結構照 `_nodehome_config`」)
- scripts/lumos:1210(`run_doctor` L 段呼叫端,tuple 解包)
- scripts/lumos:4829(`cmd_lint` 呼叫端,tuple 解包)
- scripts/lumos:995(對照:既有 `_nodehome_config` 呼叫端用 `["mode"]` 取值,dict 形狀)
- scripts/lumos:21547-21609(對照:`_nodehome_config` 定義,回傳單一 dict 含 `warnings` 鍵——本次未改動,審查前既有代碼)
- scripts/lumos:19521-19548(對照:`_stack_questions_config`,同款 dict 回傳)
- scripts/lumos:20458-20489(對照:`_lint_new_config`,同款 dict 回傳,且 docstring 明寫「同 _stack_questions_config 慣例」)

不算致命,呼叫端目前只有兩處、都改對了,行為沒錯;但下一個要讀這四支同類函式的人(含 AI)會看到三個共識一個例外,且例外的自我描述還聲稱跟共識一樣——這正是「引入第二種做法」的典型形狀,判 major。

## 問 3:第二種做法

除了 F1 之外沒有再引入自創工具函式:`_note_date_ok` 重用既有 `DATE_RE`(scripts/lumos:13270,審查前既有)、`import datetime as _dt` 是全檔上百處的既定寫法(非本次新增慣例)、`_lint_new_rules` 裡的 `lands_in` 檢查重用既有 `_lands_in_bad`(scripts/lumos:18057,審查前既有)而不是重寫一份判斷、`about_code` 的圖譜路徑檢查沿用同函式裡上面幾行已經在用的 `target.relative_to(root)` + `except ValueError` 寫法,沒有另創比對方式。`_nl_vault()` 測試輔助函式(scripts/test_lumos.py)也不算第二種做法——這個測試檔本來就沒有統一的「建 vault+config」共用 helper,各處都是就地 `(root / ".lumos").mkdir()` + `write_text`(例如 scripts/test_lumos.py:3799-3800、6541-6542),新開一支局部 helper是同一種零散寫法的延續,不是新引入的第二套機制。

引句:「gate=None 且 raw_cfg=None → 不寫設定檔(沒設)」

不對齊共 1 條,其中 major 1 條。
