severity: clean

已看,無:這份 patch 的兩處修法都跟專案既有做法一致,沒看到引入第二種做法或跨層直呼。

- `except (ValueError, RecursionError)` 這個窄範圍多例外元組已是專案既有寫法:`scripts/lumos:4411` 的 `_py_declared_methods` 早就用 `except (SyntaxError, ValueError, RecursionError)` 包 `ast.parse`,本次 8 處新增(`scripts/lumos:7521,8206,9496,9517,9694,9754,9855,9872`)是同一種「窄元組、跳過那行/那筆」的形狀,沒有換成 `except Exception` 或裸 `except:` 這種更寬的第二種做法。
- `_esc_clean(v, limit=200)` 的呼叫改法(`scripts/lumos:20728,20749`)跟函式既有簽名與其他呼叫點(`scripts/lumos:1968,2311,9611` 等)完全同形狀 `_esc_clean(值, 上限)`,函式內部本來就 `str(v)` 轉型,所以吃非字串(`desc=12345`)不會崩,符合既有合約,沒有另開一套清洗邏輯。
- 兩處補丁都在原本讀取/印出的同一層直接呼叫既有共用函式(`json.loads`/`_esc_clean`),沒有繞過已有的包裝層或新增跨層直呼。
- `_jsonl_append_verified`(`scripts/lumos:8186`)與 `_door_for_loop`(`scripts/lumos:9484`)這兩處共用函式確實如計劃筆記所述一起補了,補法跟同函式家族其他讀帳點寫法一致。
- 新增測試 `t_escape_review_r3_fixes`(`scripts/test_lumos.py:33101`)沿用既有測試 fixture(`_mk_escape_fixture`/`_esc_row`/`_esc_cat`,定義於 `scripts/test_lumos.py:33016,33046,33053`)與 `run(...)`/`check(...)` 慣例,沒有另立一套測試骨架。

共 0 條(全「已看,無」)。
