severity: clean

# 架構對齊席(sonnet)第 1 輪報告

結論:沒有引入第二種做法,也沒有跨層直呼。以下是逐項核對。

核對 1:待填字樣常數與擋法
引句:「_KILL_PH_OLD = "<照現在的程式填原文>"      # kill-rm 範本的兩個待填欄(kill-add 看到整欄等於它們就擋)」
佐證行:file: `scripts/lumos:13492`
範本產生(`_kill_add_template`)與 kill-add 的擋法(`_kill_is_placeholder`)共用同一組常數,沒有各寫一份字面字串。擋法放在 `cmd_guard_kill_add` 鎖外、緊接 `old == new` 那個同類輸入檢查之後,同樣印「擋下:…」到 stderr、回 2,跟既有擋法一致。常數定義在使用它的 `cmd_guard_kill_add` 之後(執行時才取值,不會出錯),只是位置風格,不列。

核對 2:kill-rm 選填 --id 與 argparse、HELP_WHEN
引句:「gkr.add_argument("--id", dest="gkr_id", default=None,」
佐證行:file: `scripts/lumos:40806`、`scripts/lumos:41747`
dest、help 寫法與同層 gka 一致;分派只有一處呼叫 `cmd_guard_kill_rm(env, args.node, args.gkr_id)`,沒有別的呼叫端會被 None 影響。HELP_WHEN 的 kill-rm 那行同步改了。None 與空字串走不同分支(None 列出、空字串仍擋 rc2),跟既有「--id 驗十六進位 8 到 64」的擋法沒有衝突。

核對 3:guard kill 旁路欄 `_rid` 與既有 `_logged`
引句:「print(json.dumps({"results": [{k: v for k, v in r.items() if k not in ("_logged", "_rid")}」
佐證行:file: `scripts/lumos:14025`
`_rid` 沿用 `_logged` 的做法(底線前綴旁路欄、只在唯一的 --json 輸出點濾掉);kill-log 寫入是逐欄明列,不會夾帶。結果的每個建構點(13868 到 13978)都是 `{**r, ...}`,所以 `_rid` 一路帶到,不會出現空 id。`_rid` 與既有 `recipe_id` 並存:格式正常的配方兩者同源(`_kill_recipe_id` 內部呼叫 `_kill_recipe_key`),格式壞的配方只有 `_rid` 有,理由站得住,不算第二套身分。

核對 4:列出時的跳脫與截字
引句:「return f"lumos guard kill-rm {_kill_node_arg(rel)} --id {_kill_recipe_id(str(rel), elem)[:12]}"」(既有 `_kill_fix_hint`)
佐證行:file: `scripts/lumos:13228`、`scripts/lumos:13315`
`_kill_list_cell` 與格式壞那行都走既有 `_kill_show`(引號加控制字元跳脫),先截字再跳脫,跟 doctor P2 的 `_kill_show(inv[:30])` 是同一種做法;身分都取前 12 字元,同 `_kill_fix_hint`。差別只有截斷時多加「…」,是呈現細節。短身分的 `[:12]` 在新程式多寫了兩處(列出、guard kill 結果行)而沒抽共用,是風格偏好,且測試逐項對 `[:12]` 斷言,不列 finding。

核對 5:新測試寫法
引句:「r = _kr_lum(root, v, "guard", "kill-rm", "Systems/Limit")」
佐證行:file: `scripts/test_lumos.py:59966`、`scripts/test_lumos.py:60635`
新測試沿用既有 `_mk_kill_env`、`_kr_recipe`、`_kr_lum`、`_kr_commit` 與 `check("①…")` 編號句式,命名是 `t_guard_kill_*` 前綴,跟 `t_guard_kill_rm` 同款,放在它前面;對 t_guard_kill_rm 的改動只是加斷言。`-k guard_kill` 能一起撈到。

不列的雜項:pitfalls 的 `[lint:ruff] lambda` 告警(test_lumos.py:60542 的 `rid = lambda ...`)只是風格,測試檔內既有同類寫法常見,不算架構不一致。

最高等級:clean
