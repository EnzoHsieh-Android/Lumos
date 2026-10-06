severity: minor

## 問一:分層與依賴方向

doctor U 段照 Z 段的做法:先 try 算、except 兜底、有東西才 section 加 warn_soft、不寫治理帳。`_updated_stale_notes` 放在寫入指令旁,只讀 env.notes 與 git_last_change_dates,doctor 與 updated-sync 共用,沒有跨層直呼。寫入走 cmd_set,沒有另開寫檔路徑。對照 Z 段:`scripts/lumos:2668`(try/except 兜底後 section + warn_soft)。
引句:「    # Check U: 筆記開頭的 updated 落後 git 上最後一次改動(Projects/提交時自動更新筆記日期_計劃):只提醒、不擋,」
結論:對齊。

## 問二:命名與錯誤處理

命名沿用 `_drift_str`、`_note_unreadable`、`_node_not_found(write_side=True)`、`_vault_repo_root`。本機日期寫法與既有 `scripts/lumos:3825` 同形。錯誤處理有一處不一致,見 F1。

## F1 updated-sync 的分派沒有 set/append/remove 那層 ValueError/RuntimeError 兜底
severity: minor
blocking: 否
既有寫入指令在 main 裡用 `except (ValueError, RuntimeError)` 轉成「擋下:…」並回 rc 2,見 `scripts/lumos:48315`、`scripts/lumos:48337`。updated-sync 的分派直接 return cmd_updated_sync,cmd_set 內部若拋 ValueError 或 RuntimeError(例如寫後自驗失敗、鎖相關錯誤),會變成未處理的堆疊,而不是 rc 2 加擋下訊息。批次裡一篇拋例外也會讓後面的篇都不改。
引句:「        return cmd_updated_sync(env, args.nodes, stale=args.us_stale, dry_run=args.us_dry)」

## 問三:第二種做法

沒有第二種做法。找不到節點用既有 `_node_not_found`,寫入走 cmd_set,日期取法同既有慣例,說明加進 HELP_WHEN 字典。git_last_change_dates 的修補是改原函式,不是另開一支。
引句:「            rc = max(rc, _node_not_found(env, nd, write_side=True))」

不對齊共 1 條,其中 major 0 條
