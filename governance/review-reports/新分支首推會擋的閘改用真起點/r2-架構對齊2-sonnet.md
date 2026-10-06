severity: minor

## 問 1 分層與依賴方向
結構對齊:掛鉤(bash)只經 CLI 呼叫 lumos,lumos 端由新指令包既有 `_push_range_start`,沒有掛鉤自己算起點、沒有跨層直呼。對照 drift check 呼叫段 `scripts/hooks/pre-push:477`(掛鉤經 `"$PY" "$GRAPHCTL"` 帶 --push-remote/--pushed-ref)與 `scripts/lumos:35764`(cmd_drift_check 把起點交給 `_push_range_start`)。
引句:「呼叫 `_push_range_start`,stdout 印一行範圍」
唯一偏差見 F3(起點由誰判的分層)。

## 問 2 命名與錯誤處理
指令名 push-range、參數 --push-remote/--pushed-ref 必帶且少一個 rc2,與 `scripts/lumos:35781`(只給一個回 2)及 `scripts/lumos:47182`(參數名、dest 前綴、metavar)一致。「其他非零放行」也對得上 `scripts/hooks/pre-push:488-492`。不一致處見 F1、F2。
引句:「少一個 rc2),同 `drift check` 的參數規矩」

## 問 3 第二種做法
沒有引入第二套起點演算法(r1 已改走 `_push_range_start`),不算 major。僅有兩處小的並行寫法:F3、F4。
引句:「起點由存量漂移檢查已在用的那支算,失敗一律退回空樹(多擋)」

## 問 4 落點
新指令放 `scripts/lumos`、掛鉤改 `scripts/hooks/pre-push`,落點合理。唯一小處見 F5。
引句:「寫回:`push-range` 指令的家(`scripts/lumos` 的家,先查是哪篇)」

## F1 pp_block_range_for 的失敗退回沒走「128 以上停」
引句:「其他情況(舊版 lumos 沒有這個指令、失敗、印出怪東西)退回 `空樹..頂端`(同今天)」
材料把 rc 非 0 一律退回空樹,沒提 rc 128 以上。既有規矩是被訊號殺掉(多半 Ctrl-C)不能當放行往下跑,要走 pp_stop_if_signaled(`scripts/hooks/pre-push:49-55`、drift 段 `scripts/hooks/pre-push:478-479`)。此處是退回空樹(更嚴,不是放行),方向安全,但 Ctrl-C 後掛鉤會繼續跑後面的閘;而且 `$(...)` 子 shell 內不能直接 exit,要寫明怎麼把 128 以上帶出來(例如回傳碼存變數、呼叫端再 pp_stop_if_signaled)。
severity: minor
blocking: 否

## F2 push-range 指令列沒列 --repo,不存在 git 專案的退出寫法也沒講
引句:「新指令 `lumos push-range --diff <遠端舊值>..<頂端> --push-remote <遠端名> --pushed-ref <遠端 ref>`」
掛鉤所有 lumos 呼叫都帶 `--repo "$REPO_ROOT"`(`scripts/hooks/pre-push:477-478`),cmd_drift_check 有 repo 參數並用 `_note_audit_root` 處理不在 git 專案(`scripts/lumos:35772-35775`、argparse `scripts/lumos:47181`)。做法一的函式簽名有 repo,但指令列與參數規格沒列 --repo,也沒說 root 為 None 時的 rc 與印出(這個指令的 stdout 契約是一行範圍,不在 git 專案時該印什麼要定)。
severity: minor
blocking: 否

## F3 「新分支首推才呼叫」由掛鉤判,跟 drift check 的「一律交給 lumos」是兩種分工
引句:「遠端舊值不是全零而且本機有那個物件 → `舊值..頂端`(一般增量,同今天)」
既有 drift/reread-check 對所有推送一律原樣交 `$_rsha..$_lsha`,由 `_push_range_start` 自己判增量或首推(`scripts/hooks/pre-push:470-471` 註解:掛鉤不自己算)。本案在掛鉤複製了一份「全零或舊值找不到」的判斷(與 `pp_range_for` 的條件 `scripts/hooks/pre-push:39-45` 又重複一次)。材料已承認並掛 RETIRE-IF 收斂,屬已知暫時並行,結構上沒有第二套起點演算法,所以不升 major。建議 pp_block_range_for 的判斷條件與 pp_range_for 共用同一小函式,避免兩處條件各自漂移。
severity: minor
blocking: 否

## F4 空樹有兩個來源
引句:「空樹照本 repo 的雜湊算法,`_drift_empty_tree`」
掛鉤端用 `_EMPTY_TREE`(`scripts/hooks/pre-push:34`)當退回值,lumos 端用 `_drift_empty_tree`(`scripts/lumos:33342`),兩邊同值(同 repo)但各算;材料也沒寫掛鉤端的形狀檢查正則是否涵蓋 SHA-256 之外的情形(已寫 40 到 64 位,尚可)。⚠ 判不準是否算不一致,僅提示。
severity: minor
blocking: 否

## F5 lands_in 與寫回清單不一致
引句:「寫回:`push-range` 指令的家(`scripts/lumos` 的家,先查是哪篇)、[[Systems/每支檔有家]](掛鉤範圍推導那一段)、[[Systems/bound-tests-gate]]」
frontmatter 的 lands_in 只列 Systems/每支檔有家,但做法第 6 點還要寫進 scripts/lumos 的家與 bound-tests-gate。專案規矩是計劃寫 lands_in 列出現況落點(CLAUDE.md 鐵則 5)。
severity: minor
blocking: 否

不對齊共 5 條,其中 major 0 條
