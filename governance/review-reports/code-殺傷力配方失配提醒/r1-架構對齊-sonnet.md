severity: minor

# 架構對齊席(sonnet)第 1 輪報告

比對結果:新子指令、鎖、原子寫入、設定讀取、repo 根的取法都沿用既有做法,沒有引入第二種做法或跨層直呼。只有一處小的形狀差異。

## F1 doctor P2 的整段例外兜底只 print,既有各段是 warn_soft
severity: minor
blocking: 否
引句:「except Exception as _e:        # 整段兜底:這一段壞掉不讓 doctor 整支中斷」
佐證行:file: `scripts/lumos:2627`(S 系列段的兜底寫成 `warn_soft([], f"這一段算不出來(...),先跳過")`,2677、2748 同形)

1. 既有 S13/S14/S15 等段的整段例外保護,統一用 `warn_soft([], "這一段算不出來(類別: 訊息),先跳過")`,讓這個狀況進 doctor 的提醒計數與 --ci 輸出。
2. P2 的兜底改成裸 `print("  (殺傷力配方這一段算不出來:…)")`,不經 warn_soft,所以整段壞掉時 doctor 的提醒計數不增、也不落 `check-p2` 事件;「判斷壞了」會比「判出失配」更安靜。
3. 這是同一件事的第二種寫法,不是兩層直呼,後果只是提醒變安靜,所以列 minor。改成沿用 `warn_soft([], ...)` 即可。

## 已核對、與既有一致(不列為 finding)
- 子指令:`kill-rm` 的 argparse(`node` 位置參數、`--id` 加 `dest="gkr_id"`)、`HELP_WHEN` 條目、`main()` 分派、`rc 2` 擋下並印到 stderr、`rc 0` 成功,跟 `kill-add` 同形;`reference.md`、`06-代碼審與推送.md` 也已同步。
- 鎖:`kill-add` 與 `kill-rm` 都用既有的 `_vault_write_lock(env.vault)`,沒另起一套鎖。
- 寫入:`kill-rm` 走既有的 `atomic_write_verify`,輸出的 `kill_recipes: |-` 兩行格式與 `kill-add` 相同。
- 配方身分:重用既有的 `_kill_recipe_key`;`_kill_read_recipes` 也是既有讀法。
- repo 根:`_kill_add_warn` 用既有的 `_repo_root_from_env(env)`,與 `cmd_guard_kill` 同一支;doctor 用段內既有的 `repo_root`(與 C、P 段同來源)。
- 設定:呼叫既有 `load_platforms(..., cfg=)`(該參數本來就有);`_kill_cfg_load` 只是前置包裝(多一道解析以分辨壞 JSON),沒複製 load_platforms 的邏輯。
- doctor 段形狀:`section`、`warn_soft`、`ok`、`gov_events.append({"gate": ..., "kind": "warned", "hard": False, "nodes": [...]})`、`_KNOWN_GATES` 加 `check-p2`,與既有段同形;跳過 verification 與 superseded/stale 的條件逐字照 P 段。
- `cmd_guard_kill` 本身未改,符合計劃。

最高等級:minor
