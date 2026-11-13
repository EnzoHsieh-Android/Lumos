severity: major

## 1. 分層與依賴方向
大致對齊,有兩處標 ⚠。

- 新指令放在頂層,跟 `cmd_signoff`(`scripts/lumos:17572`)同一層。它先載圖譜,再拿 `_vault_write_lock`(`scripts/lumos:30642`),最後記治理帳,順序跟 `_cmd_signoff_expected`(`scripts/lumos:17625`)一致。
- 殺傷力驗證走 `cmd_guard_kill(..., recipes_override=, result_out=)`。`kill-add --try` 本來就這樣呼叫(`scripts/lumos:27113`),沒有跨層。
- 規格閘讀 situation-rule 事件走 `_gov_vc_gate_events`(`scripts/lumos:23524`),沒有直接碰指令內部狀態。
- 推送前核對只讀計劃,沒有改計劃檔。
- ⚠ 表態核對(`_kt_sit_spec_names_calc`)呼叫規格閘的 `_spec_gate_push_candidates`(`scripts/lumos:16489`),盲判縮減名單時又用到 `_spec_gate_touched_plans`、`_impact_home_map`。這是刻意共用同一支,但表態層往規格閘層伸手。鄰居沒有這種先例,所以不硬判,交編排者決定。
- ⚠ `_impact_home_map` 新增依 `env._texts` 分岔的記憶體分支(`scripts/lumos:67450` 一帶)。這是改既有函式的行為,不是新增並行做法,只提醒。

## 2. 命名與錯誤處理
大致對齊,有兩處不一致,記在 a3、a4。

- 命名:`cmd_situation_rule`、`_situation_rule_*`、`_kt_sit_spec_*` 都符合 `cmd_` 與 `_` 前綴慣例。
- 輸出:一律「擋下:…」加 `file=sys.stderr`,跟 `_cmd_signoff_expected` 一致。
- rc:0 成功、1 使用者答 n、2 拒絕,跟 `scripts/lumos:17625` 附近一致。
- ⚠ 治理帳寫失敗時,新指令回 rc 1 並印補記指令。`_cmd_signoff_expected` 同情況回 rc 2。但這裡計劃已經寫入,情境不同,所以不判不一致,只提醒。
- 其餘不對齊見 a3、a4。

## 3. 第二種做法
有兩處,記在 a1、a2。

- 原子寫:`_situation_rule_write` 另寫一套。
- 終端探測:`_tty_reachable` 另寫一套。

## a1 另寫一套原子寫檔,而鄰居已有 `_write_bytes_atomic`
severity: major
blocking: 是
引句:「整份正文原子寫(同 atomic_write_verify 的步驟)」
file: `scripts/lumos:30533`

- 專案的寫入原語是 `_write_lf` / `_write_bytes_atomic`。
- 後者的 docstring 明寫「要位元組逐一相同的寫入…直接用這支,不另寫一份原子寫入」。
- 新碼自己做了一遍:暫存檔名帶 pid 與 uuid、`O_EXCL`、`copymode`、`os.replace`、例外時 `unlink`。
- 新碼多做了一步「讀回比對」。這一步可以留在呼叫端,不必複製整套寫入。
- 連例外處理都不同:`_write_refusal_reason`(`scripts/lumos:30466`)在 `lstat` 失敗時 raise `WriteBlocked`。新碼沒有 catch 它,`cmd_situation_rule` 只 catch `RuntimeError`。鄰居(`atomic_write_verify`,`scripts/lumos:30553`)會擋下並轉成訊息。
- 結果是以後有兩套原子寫,修一套時會漏另一套。

## a2 另寫一套終端探測,而鄰居已有 `_confirm_tty` 的控制終端開法
severity: major
blocking: 是
引句:「問不問得到人(只看、不讀):標準輸入是終端,或控制終端」
file: `scripts/lumos:35692`

- `_tty_reachable` 複製了 `_confirm_tty_dev`(`scripts/lumos:35692`)的 `LUMOS_TTY` 加 `O_NOCTTY` 開法,再加上 `sys.stdin.isatty()` 的判斷。
- 它的用意是「沒有終端又沒帶 `--consent` 就在殺傷力之前拒絕」,這個需求合理。
- 做法應該是在 `_confirm_tty` 家族加一個「只探測」的共用函式,讓兩邊共用。現在改了 `LUMOS_TTY` 的語意,會有一邊漏改。

## a3 條款指紋的算法複製兩處,沒有共用函式
severity: minor
blocking: 否
引句:「"clause_sha": hashlib.sha256(nfc(body).encode("utf-8")).hexdigest()」
file: `scripts/lumos:14547`

- 寫入端(`cmd_situation_rule`)和讀取端(`_spec_gate_ruled_ids`)各自算一次 sha256。兩邊目前一致。
- 兩邊要永遠同步,卻沒有共用 helper。鄰居的指紋(例如 `_expected_table_sha`)都是單一函式。
- 結構上不算第二種做法,所以只判 minor。

## a4 讀 HEAD 版檔案自己用 `git show`,鄰居有 `_kt_sit_read_many`
severity: minor
blocking: 否
引句:「r = _sp.run(["git", "-C", str(rr), "show", f"HEAD:{sg['file']}"], capture_output=True, check=False)」
file: `scripts/lumos:39865`

- `_situation_rule_recipe_problem` 為了讀段所在檔的 HEAD 版,自己 `git show`。
- 同一功能群(`_cmd_codeloop_bj_template`)用 `_kt_sit_read_many(repo_root, at_sha, files)`,帶逾時並轉成 `_KtSitUnverifiable`。
- 新碼的錯誤訊息和逾時處理都因此跟鄰居不同。

不對齊共 4 條,其中 major 2 條
