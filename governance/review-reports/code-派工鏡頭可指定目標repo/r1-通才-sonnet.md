severity: minor

整體上我沒找到會弄壞既有功能的問題,只有一條 minor。我跑了 `-k dispatch_lens`,237 個案例全過;`t_docs_command_count` 也過。

**Finding**

severity: minor
blocking: 否 — 只影響吞掉失敗時的記帳,還在「失敗一律放行」的政策內,不會弄壞派工
引句:「except (ImportError, SyntaxError, AttributeError, OSError, TypeError, ValueError):」
問題:`_mark_event` 取代了原本 `_fail_note` 裡的 `except Exception`,例外清單變窄。本檔其他兩處記帳(逾時、鎖錯誤)仍寬接 `Exception`。
具體失敗情境:`_hookevent` 載入時丟出清單外的例外(例如 `RuntimeError`、`KeyError`),原本會被吞掉,現在會一路往上丟。`_fail_note` 裡這個例外會跑出掛鉤,範圍算不出來時的說明行就附不上,派工詞也不會被改寫。`mark()` 本身只做字典賦值,實際上很難觸發。
佐證:file: `scripts/hooks/claude/dispatch-lens-hook.py:261` 附近的 `_mark_event`。

**已讀,無 finding**
- `_lens_git` 加 `env` 與 `check=False`:既有呼叫者不傳 `env`,`kw` 是空的,行為不變。
- `_dispatch_lens_fail` 代碼表:既有六個呼叫點用的代碼都在 `_LENS_FAIL_CODES` 裡,新加的 `ValueError` 不會誤傷。
- `cmd_dispatch_lens_spec` 把三個 `if` 改成 `if/elif/elif`:原本三個分支互斥,工作樹寫法的輸出分支沒變。
- 移除 `import io, contextlib` 後,ruff F821 無未定義名稱。
- 抓程式路徑的正規式多認反引號裡的路徑:先收 ASCII、後收反引號,重複的被 `seen` 擋掉,原本抓得到的檔仍在前面。
- 設計審加 `--arch-target`:`_dispatch_lens_spec_with_arch` 改用 `rd["vault_rel"]`(工作樹的 `slugs[0]`),原本是 HEAD 排序第一個。只有同時有多個圖譜資料夾,或圖譜資料夾只在工作樹不在 HEAD 時才會不同,我判斷不構成回歸。
- 失敗時 JSON 多了 `spec_source`:`_lens_emit_with_extra` 能處理失敗輸出。
- 掛鉤 `_fail_note(r, rng, repo, spec)`:範圍路徑不變,舊路徑在設計審失敗時原本回空字串,現在附計劃版說明。
- 指令總數 89:兩份文件與 argparse 實數一致。

最高等級 minor,blocking 0 條。
