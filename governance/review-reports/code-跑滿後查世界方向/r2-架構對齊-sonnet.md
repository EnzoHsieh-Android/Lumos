severity: minor

## 一、分層與依賴方向

這一輪沒有不對齊,三點都對得上既有分層。

- **判定函式沒有寫帳或印訊息。** `_cap_retro_status` 只多了 `res` 初值的 `"world_case": None` 和把 `res["world_case"]` 改成先收進區域變數 `case` 再填,仍然只回 dict。`_cap_world_case(decision)` 沒動,仍是純函式。對照:`file: scripts/lumos:22617`(`@531463257`,`_cap_retro_status` 說明)、`scripts/lumos:22406`(`_cap_world_case`)。
- **共用判定沒有反過來依賴呼叫端。** `_cap_retro_fix_cmd` 只吃 `(root, loop_id, state, case)`,「要不要接 `_CAP_WORLD_FILL`」仍只在它一處決定(`scripts/lumos:22682-22699`)。doctor、retro-stats、`--template --write` 補上的是呼叫端自己帶 `_cap_world_case(...)`,跟既有的擋下訊息、處置閘、`_cap_retro_next_lines` 同一種傳法(`scripts/lumos:22810`、`22852`、`22907`)。
- **`cmd_loop_cap_decision` 讀回帳再判情況,這一步留在命令層。** 這跟 `cmd_loop_retro` 先讀帳、挑最新人裁、再判情況的分層一樣(`scripts/lumos:22988-22992`、`23078`)。

## 二、命名與錯誤處理

**改名 `_cap_retro_fix_cmd_body`:對齊。** 專案裡「外殼加本體」的後綴是 `_body`(`_e2e_gate_body`,`scripts/lumos:43365`,外殼在 `43405` 呼叫;另有 `_secev_evaluate_body`、`_secapr_payload_body`)或 `_inner`(`_testmap_build_inner`,`62442`)。上一輪的 `_base` 不在這兩種裡,這輪改掉了。我在 repo 裡沒找到殘留的 `_cap_retro_fix_cmd_base`,只剩上一輪的卷證檔提到。

**各呼叫端帶情況值:對齊。** doctor 和 retro-stats 用 `.get('decision')` / `.get("decision")`,因為那兩處的 `st` 可能是帶 error 的列,同函式內本來就用 `.get`(`scripts/lumos:23126`)。其餘用 `st['decision']`。`cmd_loop_retro` 的 `--template --write` 兩處用已經驗過非 None 的 `dec`,沒問題。

**測試端兩個新 helper:對齊。**
- 命名:`_cap_since_last_change_day`、`_cap_since_fresh` 沿用同區既有的 `_cap_` 前綴 helper(`scripts/test_lumos.py:50804`、`50822`)。
- 讀 git:都用 `_sp.run(["git","-C",...], capture_output=True, text=True)`,跟原本內嵌的寫法一樣。
- 建臨時 repo:用 `GIT_AUTHOR_DATE` / `GIT_COMMITTER_DATE` 加 `-c user.email=...` 提交,跟 `scripts/test_lumos.py:68073`、`71641` 一樣。
- 換掉模組函式或常數:用 `try/finally` 還原,跟 `scripts/test_lumos.py:50886-50904`、`78780-78785` 一樣。

### A1 記完人裁後讀回帳,讀帳錯誤被丟掉,跟其他呼叫端不一樣
severity: minor
blocking: 否 — 結構對(同一支讀帳函式、同一種挑最新人裁的寫法),只有錯誤處理比鄰居鬆:帳讀不動時安靜退成沒人裁,只會少印補 world_check 的提醒,不會誤放行
引句:「evs, _gerr = _retro_gov_events(root, loop_id)」
file: `scripts/lumos:22222-22224`(`_retro_gov_events` 說明寫明「呼叫端要當成帳壞(fail-closed),★不得當成沒有人裁紀錄★」)、`scripts/lumos:22988-22991`(`cmd_loop_retro` 拿到 `gerr` 就擋下)、`scripts/lumos:68639-68641`(`_codeloop_pass_accept_risk` 拿到 `err` 就回)

其他 `_retro_gov_events` 的呼叫端都會處理第二個回傳值。`15842` 把它放進 ctx,`22622` 和 `22744` 交給 `gov_err` / `gerr` 處理,`22988` 擋下,`68639` 回錯誤。只有新寫的這一處把它存進 `_gerr` 就不用了。帳讀不動時 `evs` 是 `[]`,`dec` 是 `None`,`_cap_world_case(None)` 回 `"ignored"`。這等於把「帳壞」當成「沒有人裁紀錄」,正是 `_retro_gov_events` 說明要求呼叫端不能做的事。這一刻剛由 `_gate_event` 寫成功,而且寫前已過 `_retro_gov_path_err`,所以實際很難碰到。但專案裡其他人都會顯式處理它。這裡的 `_gerr` 也不是未使用變數的慣例命名,同檔 `1484`、`35527` 的 `_gerr` 後面都有被用到。

## 三、第二種做法

沒有引入第二種做法,不構成 major。

- **讀最新人裁:** 新碼是「`_retro_gov_events(root, loop_id)` 加 `next((e for e in reversed(evs) if _retro_is_decision(e)), None)`」。這跟 `cmd_loop_retro`(`scripts/lumos:22988-22992`)逐字同形。它是已有寫法的又一處使用,不是另一套。(舊的 `evs[di]` 掃法在 `_cap_retro_status` 內部,`decisions[-1]` 在 `_codeloop_pass_accept_risk`,都是之前就有的,這輪沒新增。)
- **不另讀時鐘:** 拿掉 `_dt.datetime.now()` 後,情況值只由帳上那筆人裁的 `ts` 經 `_cap_world_case` 決定,沒有第二個時間來源。
- **新鮮度守衛讀 git:** 仍是內嵌 `git log -1 ... --format=%cs -- scripts/lumos`,只是 `-S` 換成 `-G` 並抽成 helper。這是同一種讀法,不是另一套。
- **新測試改常數:** `m._CAP_WORLD_CHECK_SINCE` 的暫時替換沿用「存原值、`try/finally` 還原」的做法。

不對齊共 1 條,其中 major 0 條
