severity: minor

## F1 撤回逃逸帳「找不到 token」錯誤訊息直接把使用者輸入印到終端,沒過既有的 _esc_clean 清洗
severity: minor
blocking: no
誰:能執行 `lumos loop escape --withdraw` 的人,或代它組指令的自動化(例如從 Issue/PR 文字擷取 token 再轉呼叫的腳本、AI 代理)。
從哪個入口:`--withdraw <token>` 這個 CLI 參數。
送什麼:一個刻意帶 ANSI/控制字元、且不存在於帳本裡的字串(例如夾帶游標移動、清屏、變色的跳脫序列)。
拿到什麼:`_escape_withdraw` 在「帳裡沒有這個 token」的分支,把使用者原樣輸入的 `target` 直接塞進 `print(..., file=sys.stderr)`,沒有經過這支檔案自己定義、專門用來擋這類洞的 `_esc_clean`(同檔案裡逃逸帳其餘所有印出去的欄位——stage/desc/rule/reason/by——都會先過 `_esc_clean`,唯獨這條新加的「找不到」訊息漏掉)。程式裡緊鄰的另一處註解明講這正是兩天前才修過一次的同類洞(`_esc_clean` 定義處上方:「摘要與節點名過 _esc_clean(code-revisit r1 H-1:兩天前才在逃逸帳修過的控制碼穿透洞,勿三挖)」),而這條新路徑等於把同一種洞又開了一次;效果是可讓終端輸出被操控(隱藏前面內容、偽造後續文字/提示),屬於題目第 5 類「終端輸出注入」明確要看的情形。因為多數情況下操作者就是自己打指令、自己看終端,實際殺傷力有限,故評 minor、不擋。
引句:「print(f"擋下:逃逸帳裡沒有 token {target} 這一列,帳本沒動。看全帳:\n    lumos loop escape --list", file=sys.stderr)」

## F2 escape-stats 讀 loop 欄位去拼計劃檔路徑,含 `..` 時未阻擋,新增的讀檔路徑因此可能讀到帳本之外的檔案
severity: minor
blocking: no
（推論）
誰:能在 `.escape-log.jsonl`(git 追蹤檔)裡放進一列、或用 `lumos loop escape <loop_id> ...` 記帳成功的人——manual 記帳前雖有「編號要先存在於審查帳」的檢查,但審查帳裡的 loop 編號本身(`canary record --loop <任意字串>`)看不出有做字元白名單。
從哪個入口:逃逸帳一列的 `loop` 欄位,經 `lumos loop escape-stats` 觸發 `_escape_stats → _cats → _escape_plan_scopes → _plan_for_loop`。
送什麼:一個帶路徑跳脫片段的 loop 編號,例如 `../../../../somewhere/敏感筆記`。
拿到什麼:`_plan_for_loop` 用 `proj / cand`(`proj = env.vault / "Projects"`)直接拼路徑、`is_file()` 判斷,沒有擋 `..`;一旦組出的路徑真的存在(檔名恰好以 `_計劃.md` 或 `.md` 結尾),`_escape_plan_scopes` 會用 `(env.vault / rel).read_text(...)` 把該檔內容讀出來解析 frontmatter,再把 `scope/` 標籤印進 `lumos loop escape-stats` 的報表裡。`_plan_for_loop` 本身的路徑拼接手法是既有程式碼(這次只是加了 NFC 目錄比對的 fallback),但這次新加的 `_escape_plan_scopes` 是第一個真的去 `read_text` 該路徑內容的呼叫者——之前的呼叫者只拿它判斷檔案存不存在、不讀內容。可利用性偏弱(需要攻擊者同時控制 loop 字串、又要磁碟上真的有一個檔名恰好等於該跳脫路徑加上 `_計劃.md`/`.md` 尾綴的檔案),故評 minor、推論。
引句:「fm, _ = split_frontmatter((env.vault / rel).read_text(encoding="utf-8"))」

## F3 撤回紀錄的 --by 沒有任何身分驗證,任何人都能替別人簽撤回
severity: minor
blocking: no
（推論)
誰:任何能執行 `lumos loop escape --withdraw` 的本機使用者(在消費專案裡就是任何有 repo 寫入權的協作者)。
從哪個入口:`--by <誰>` 參數。
送什麼:別人的名字,例如 `--by "Enzo"`,而實際操作者不是 Enzo。
拿到什麼:一筆寫進 `.escape-log.jsonl`(git 追蹤)的撤回紀錄,`by` 欄位被冒名,之後 `lumos loop escape --list` 會把這個冒用的名字連同理由一起印出來(「撤回會讓統計數字變好看,一定要留得下為什麼」這句程式內註解正說明這欄是究責用的)。這條指令沒有比對 git 使用者、沒有任何簽章,純文字自報;跟同一套系統裡其他「誰做的」欄位(例如審查帳的 auditor)是同一種信任模型,不是這次新開的洞,但因為撤回這個新功能的價值主張就是「讓漏掉的統計說得清楚是誰、為什麼撤」,冒名直接打穿這個價值主張,故仍列出來、評 minor。
引句:「if not (by or "").strip():」

已看,無:
1 不可信輸入流到危險操作(路徑、命令、反序列化):沒有 `eval`/`exec`/`pickle`/`subprocess(shell=True)`,寫入用的是既有的 `_jsonl_append_verified`(open 'a' + 讀回自驗),沒有新的命令組裝或反序列化路徑。
3 密鑰與個資進 log/帳本/錯誤訊息:這次新增欄位(`loop_kind`、`sha`、`defect_ref`、`defect_ref_missing`、撤回的 `reason`/`by`/`target`)都是使用者自己輸入的一句話或提交雜湊,沒看到把系統密鑰、token、環境變數值寫進帳本或錯誤訊息的地方。
4 加密傳輸:本次改動全部是本機檔案讀寫與 CLI 輸出,沒有網路呼叫。
5 執行邊界(除 F1/F2 外):符號連結防護沿用既有 `_escape_log_guard`(擋 symlink、`O_EXCL|O_NOFOLLOW` 建檔),撤回與手動記帳都走同一支、且都包進 `_vault_write_lock`,沒看到繞過寫入鎖或符號連結檢查的新路徑;hook/CI 不會執行這次改動新增的任何檔案內容(都是資料列,不是可執行腳本)。
6 行動端:本次改動不涉及行動端程式碼。
