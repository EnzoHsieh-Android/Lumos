severity: minor

# 架構對齊審查(第 3 輪/末輪)——r3-delta.patch

## 問 1:分層與依賴方向——修正有沒有繞過既有共用函式自己再刻一套?

沒有繞過既有共用函式另刻一套。具體核對:

- 範圍終點找不到的處理(`cmd_home_check`、`cmd_note_shape`)改成跟 `_note_audit_resolve` 一樣,先判 `_ZERO_SHA_RE.fullmatch(b)` 再回 rc2;`_ZERO_SHA_RE` 是既有共用常數(`scripts/lumos:29142`,`re.compile(r"0{40}")`,在 `_lens_push_base` 等處已在用),`_note_audit_resolve` 原本自己寫 `re.fullmatch(r"0{40}|0{64}", b)`,這次改成呼叫共用常數——方向是收斂成同一份,不是新刻一套。
- git 呼叫全部走既有包裝(`_lens_git`、`_ns_git`),decision-amend 的改名偵測只是把 `_ns_git(root, "diff", "--cached", ...)` 換成不帶 `--cached`,沒有繞過包裝直接呼叫 `subprocess`。
- `_ci_jobs_calling_without_full_history`(新函式,`scripts/lumos:24978`)是這輪唯一真正新增的處理路徑:逐工作項目切開 `.github/workflows/*.yml` 再各自查 `fetch-depth: 0`。用 grep 核對過 `scripts/lumos` 全檔,先前所有讀 `.github/workflows` 的地方(`scripts/lumos:19602`、`24022`、原本的 `25032` 一行)都只是把整份 yml 串成一個字串做子字串比對,沒有任何既有函式做「按工作項目切開」這件事,所以這不是繞過既有做法,是補一個原本不存在的能力。

判斷:這題沒有 finding。

## 問 2:命名與錯誤處理——rc 語意、訊息寫法、例外處理跟鄰居一樣嗎?

### F1 新函式讀 yml 用 try/except OSError,鄰居讀同一批檔案的那行完全沒有

severity: minor
blocking: 否 — 只是容錯姿態不一致,結構本身沒問題,不影響現有行為
引句:「try:
            lines = [l for l in p.read_text(encoding="utf-8", errors="replace").split("\n") if not l.lstrip().startswith("#")]
        except OSError:
            continue」
file: `scripts/lumos:24978-24986`(新函式,自己包了 try/except)
file: `scripts/lumos:24022`(`_note_shape_doctor_lines` 讀同一批 `ymls` 的 `body = "\n".join(p.read_text(...) for p in ymls)`,沒有 try/except)
file: `scripts/lumos:25032`(`_note_audit_doctor_lines` 讀同一批 `ymls` 的 `body = ...`,同樣沒有 try/except)

失敗場景:同一次呼叫裡,`ymls` 清單先被 `_note_shape_doctor_lines`/`_note_audit_doctor_lines` 用無防護的 `read_text` 讀一次組 `body`,幾行後又被新函式用有防護的 `read_text` 讀第二次——如果檔案在兩次讀取之間被刪掉或變成目錄(競態,或壞掉的 symlink),前者會整支 doctor 噴 `OSError` 中斷,後者只是靜靜跳過該檔繼續。同一支 doctor 函式裡,同一批檔案的容錯政策不一致,不是「結構不同故意分工」,是這輪新加的那段比鄰居更嚴謹但沒有回頭統一。

### F2 新訊息把清單截斷到前 5 筆,卻沒有比照鄰居寫法加「等 N 個」提示

severity: minor
blocking: 否 — 訊息內容仍然可用,只是截斷後讀者看不出還有更多沒列出來
引句:「+                   + "、".join(f"{f} 的 {j}" for f, j in shallow[:5]))」
file: `scripts/lumos:25901`(`_bound_tests_for_diff` 附近既有寫法:`"、".join(non_docs[:3]) + ("…" if len(non_docs) > 3 else "")`)
file: `scripts/lumos:6280`(既有寫法:`"、".join(outside[:5]) + (f" 等 {len(outside)} 支" if len(outside) > 5 else "")`)

失敗場景:一個專案有 6 個以上的工作項目都呼叫 `note-audit check` 但都沒設 `fetch-depth: 0` 時,`_note_audit_doctor_lines`(`scripts/lumos:25033-25037`)印出的訊息只列前 5 個,句尾沒有任何「還有更多」的提示,讀的人會誤以為只有列出來的那幾個要修——這正是專案自己已經在兩處(`scripts/lumos:6280`、`25901`)寫好的截斷慣例特別要避免的情況。

### F3 同一支新函式被「第一層」與「第二層」doctor 各呼叫一次,但訊息詳細度不對稱

severity: minor
blocking: 否 — 兩層各自的訊息都能動作(叫人去查 CI),只是資訊量不同,不影響正確性
引句(note-shape,只判真假不取值):「elif _ci_jobs_calling_without_full_history(ymls, "note-shape --diff"):
            out.append("專案 CI 呼叫了 note-shape,但那個工作項目沒抓完整歷史(fetch-depth: 0):淺層 clone 算不出範圍,每次都會跳過")」
引句(note-audit,取值列出工作項目名稱):「shallow = _ci_jobs_calling_without_full_history(ymls, "note-audit check")
    if shallow:
        out.append("專案 CI 呼叫了 note-audit check,但那個工作項目沒抓完整歷史(fetch-depth: 0):淺層 clone 算不出範圍,每次都會跳過——"
                   + "、".join(f"{f} 的 {j}" for f, j in shallow[:5]))」

失敗場景:同一份 CI 設定裡,`note-shape --diff` 那個工作項目跟 `note-audit check` 那個工作項目都沒設 `fetch-depth: 0`——note-audit 的提醒會講出是哪個檔、哪個工作項目(方便直接去改),note-shape 的提醒卻只講「那個工作項目」,不指名。這份修正的說明自己寫「第一層 doctor 同族一起改,共用一支」(見計劃節點裡的審計修正紀錄),兩層共用同一支函式、拿到的是同一組 `(檔名, 工作項目名)`,卻只有一層把這組資訊印出來,另一層丟掉——跟這輪明講的「兩層一致」目標不對齊。

## 問 3:第二種做法——修正有沒有引入專案裡原本沒有的做法?

- `_ci_jobs_calling_without_full_history` 用「按縮排切區塊」的手刻小型解析器讀 GitHub Actions 的 `jobs:` 結構。專案本來就有「零依賴、不能拉 YAML 套件」的家規,而且前端 frontmatter/decisions 的解析(`parse_decisions`、`decisions_items`、`cmd_decision_amend` 裡的 `_ind`)本來就是同一種手刻縮排解析風格,只是這次把同樣的技法第一次套用到 `.github/workflows` 這個新領域——這不是「新引入一種做法」,是既有做法（手刻縮排解析）延伸到一個先前沒人做過按區塊切分的地方,而且先前也沒有任何函式做這件事可以被繞過。判斷:不算引入第二種做法。
- decision-amend 的欄位形狀檢查(`if not head_val or head_val.startswith(("[", "{")):`)本身沿用 r1 就有的「不呼叫 `parse_decisions`、自己在原始 frontmatter 行上判斷形狀」寫法,這輪只是多加 `[`/`{` 開頭判斷,沒有換成新的判斷路數,也沒有新增到別處——算既有做法的延伸,不是新開一套。附帶一提(不佔額度、不算 finding):註解寫「欄位形狀照 `parse_decisions` 的判法」,但 `parse_decisions`(`scripts/lumos:12926`)其實沒有對 `[`/`{` 開頭做任何特殊處理(`val` 不是空字串時一律當成一般字串存,見 `scripts/lumos:12978` 的 `cur[key] = strip_quotes(val)`);這句註解對未來要改 `parse_decisions` 的人有點誤導,但不影響這輪測試綠燈,沒有可翻紅的失敗場景,所以沒有另開一條 finding。

不對齊共 3 條,其中 major 0 條
這輪修正沒有繞過既有共用函式、沒有跨層直接呼叫,也沒有在專案裡開出新的做法路線——三處落差都是「這次新加的程式碼比旁邊的舊程式碼更講究或更粗略,兩邊沒有互相看齊」這種局部細節,最高等級是 minor。
