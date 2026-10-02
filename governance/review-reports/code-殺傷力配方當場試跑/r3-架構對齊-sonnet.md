severity: minor

# r3 架構對齊-sonnet(只審 r2 修正差異)

## 三問

1. 分層與依賴方向:修正方向對。`_guard_kill_pick` 改呼叫 `_kill_recipe_judge(_kill_check_ctx(repo_root), r)`,跟 kill-add 提醒 `_kill_add_warn` 與 doctor P2 `_kill_p2_one` 走同一條「建 ctx、一條判一次」的路,r1 另寫的 `_kill_recipe_shape_bad` 已整支拿掉,第二種判法消除。仍在同一支 scripts/lumos 內、同層呼叫,沒有跨層直呼。對照:file: `scripts/lumos:14209`、`scripts/lumos:14358`、`scripts/lumos:15331`。修正關卡那行說明(`_fix_recipe_rerun_notes` 回一行字串而非靜默)與同函式族 `notes.append(f"平台 {name} 釘不住版本:…")` 的寫法一致,呼叫端 `scripts/lumos:12081` 仍有 try/except 兜底。
2. 命名與錯誤處理:輸出措辭跟 P2 同一套(「第 N 條{detail}」+ kill-rm 修法),一致。差異在例外處理:兩個鄰居呼叫 judge 都包 try/except(kill-add 提醒 `scripts/lumos:14209` 起、P2 `scripts/lumos:14358` 起),pick 沒包(F1)。另 pick 自己建一份 ctx,cmd_guard_kill 後面又 `load_platforms` 一次(F2)。
3. 第二種做法:格式壞判法已統一成一種。只剩設定讀取在 guard kill 一條命令內有兩條路(`_kill_cfg_load` 與 `load_platforms`),屬小處(F2),不到 major。

## F1 `_guard_kill_pick` 呼叫 judge 沒有 try/except,跟 kill-add 提醒、P2 兩個鄰居不同
severity: minor
blocking: 否
引句:「+    ctx = _kill_check_ctx(repo_root)
     for i, (r, rid) in enumerate(zip(recipes, ids), 1):
+        res = _kill_recipe_judge(ctx, r) if rid in want else None」
佐證行:file: `scripts/lumos:14209`(`_kill_add_warn` 在 try 裡呼叫,出錯印一行不崩潰)
佐證行:file: `scripts/lumos:14358`(`_kill_p2_one` 把 judge 包在 try/except Exception,記成「這條判不了」)
1. 兩個既有鄰居都假設 judge 可能丟未預期例外(讀 blob、git 子程序、設定),各自兜底成一行訊息;pick 直接呼叫,judge 若丟例外會變成 Traceback,而這條路原本就是要「不讓人踩進既有崩潰」。
2. 未能重現(我沒造出會讓 judge 丟例外的配方;judge 對 platform 清單、file 非字串、NUL 都已先判 malformed)。屬一致性問題、非實測失敗,故 minor。建議跟鄰居同寫法包起來,例外時印「判不了」並擋下(回 None)或放行。

## F2 `--id` 路徑上設定被讀兩次、repo 根算兩次
severity: minor
blocking: 否
引句:「+        recipes = _guard_kill_pick(rel, recipes, id_prefixes, _repo_root_from_env(env))」
佐證行:file: `scripts/lumos:15056`(後面同函式又 `repo_root = _repo_root_from_env(env)` 與 `load_platforms(repo_root)`)
佐證行:file: `scripts/lumos:13959`(`_kill_check_ctx` 註解自述「設定只讀一次」,P2 用 st["ctx"] 共用)
1. P2 為了「設定只讀一次」把 ctx 放進共用狀態;guard kill 現在一條命令內由 pick 讀一次(`_kill_cfg_load`,警告被吞)、主流程再讀一次(`load_platforms`,警告照印、壞 JSON 時照舊退回預設)。兩份對壞設定的反應不同:pick 判成 cfg(不擋),主流程另有自己的擋法,結果不衝突但是兩條讀法。
2. 無實際錯誤行為(我核對過 cfg 壞時 pick 不會誤擋、後面照舊報「設定檔讀不了」);僅是未共用 repo_root/ctx。可把 repo_root 算一次後傳入,minor。

不對齊共 2 條,其中 major 0 條
最高等級:minor,blocking 共 0 條
