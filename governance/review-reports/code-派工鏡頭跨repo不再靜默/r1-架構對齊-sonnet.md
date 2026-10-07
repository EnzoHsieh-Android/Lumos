severity: minor

## F1 說明句帶入的 {repo} 來自未驗證欄位,與鄰居只帶「範圍/鎖路徑」的做法不同
severity: minor
blocking: 否
引句:「FAIL_NOTE = ("LUMOS-LENS:這次沒附固定席節點(範圍 {what} 在會談專案 {repo} 算不出來:{why})。"」
引句:「repo=str(repo)[:300].replace("\n", " ").replace("\r", " "), why=why)」
佐證:``dispatch-lens-hook.py: `scripts/hooks/claude/dispatch-lens-hook.py:39-47` ``。鄰居 TIMEOUT_NOTE 只填 `what`(標記已驗證的範圍),LOCK_*/SPAWN_ERROR_NOTE 只填 `lock`(掛鉤自己算出的路徑)。新句填的 `repo` 來自 CLAUDE_PROJECT_DIR 或 payload cwd,沒有經過驗證,只做截 300 字與去換行。
說明:結構一致,只是專案規則「派工詞只附固定字彙與已驗證欄位」下,這是鄰居沒有的一種欄位來源。依規則屬 minor。

## F2 掛鉤端讀 lumos JSON 的解析重複一份,例外集合比 `_role_text` 少一項
severity: minor
blocking: 否
引句:「except (ValueError, IndexError):」
佐證:``dispatch-lens-hook.py: `scripts/hooks/claude/dispatch-lens-hook.py:194-201` ``。`_role_text` 的例外是 (ValueError, IndexError, AttributeError),而新的 `_lens_fail_why` 少了 AttributeError。`r.stdout or ""` 已擋掉 None,實際不會觸發,所以只是慣例不齊。同一段「取 stdout 最後一行 JSON」現在有兩份。

## 三問
1. 分層與依賴方向:對齊。
   - 掛鉤端:新增 `_lens_fail_why` 和 `_fail_note`,位置與 `_role_text` 同層,都放在 `main` 之前,由 `main` 的 `r.returncode != 0` 分支呼叫。
   - lumos 端:新增 `_dispatch_lens_fail`,放在 `_dispatch_lens_graph` 上方,只在該函式的三條失敗回傳路徑使用。
   - 沒有跨層直呼。lumos 端的 `_cmd_dispatch_lens_impl` 會把 role_text 併進 `_dispatch_lens_graph` 印出的 JSON,所以 lens_fail 這行 JSON 能照舊帶 role_text(``scripts/lumos: `scripts/lumos:45519-45526` ``)。
   引句:「_note = _fail_note(r, rng, repo)   # 範圍算不出來才有;說明在前、角色卡在後」
   引句:「return _dispatch_lens_fail(as_json, "not_git", 2)」

2. 命名與錯誤處理:對齊,僅有 F1、F2 兩個 minor。
   - 說明句常數命名為 `FAIL_NOTE`,以 `LUMOS-LENS:` 開頭,與 TIMEOUT_NOTE 等同組。
   - 記事件用 `_hookevent.mark("error", …)`,與 ``dispatch-lens-hook.py: `scripts/hooks/claude/dispatch-lens-hook.py:410-411,423-424` `` 的 SPAWN/LOCK 路徑同一種做法(內聯 import 加 try/except pass)。
   - 失敗時說明在前、角色卡在後,沿用 `_emit_updated`。
   - 筆記方面:WHY 行有 `[出處:]` 和 `[因:]`,也綁了 `[test:]`;`lands_in` 列了 Systems/codex-harness,而 DEP 行本就列有這支掛鉤,落點對得上。測試函式名 `t_dispatch_lens_hook_fail_reason_notice` 在 diff 內真的存在。
   引句:「_mark("error", "lumos dispatch-lens 範圍算不出來,附了說明行")」
   引句:「WHY:[2026-10-07 [[Projects/派工鏡頭跨repo不再靜默_計劃]]]派工鏡頭掛鉤在 lumos 回非零碼、JSON 帶認得的 lens_fail」

3. 第二種做法:沒有引入。
   - 溝通管道沿用「lumos --json 在失敗時仍印一行 JSON、掛鉤讀最後一行」,與既有 role_text 通道相同。
   - 只認三個固定代碼,對照字典 `LENS_FAIL_REASONS` 在掛鉤端轉成固定句,stderr 原文不轉進派工詞,與 TIMEOUT_NOTE 的固定句寫法一致。
   - 另有一點值得留意但不算不一致:這是第 4 份「內聯 import _hookevent.mark」的複本,沿用既有寫法,沒有另開新機制。
   引句:「LENS_FAIL_REASONS = {」
   引句:「print(_json.dumps({"lens_fail": code}))」

派工詞尾端有沒有「lumos 自動附加」或「圖譜沒有釘到節點」段:我只在 diff 內的 SKILL.md 說明文字(skills/lumos-code-loop/SKILL.md)裡看到這兩個詞,是文件敘述。我讀到的派工詞本身尾端沒有這兩段;「圖譜沒有釘到節點」只出現在派工詞中的機械反查說明裡,那是題目給的資料,不是 lumos 掛鉤附的段。

不對齊共 2 條,其中 major 0 條。
