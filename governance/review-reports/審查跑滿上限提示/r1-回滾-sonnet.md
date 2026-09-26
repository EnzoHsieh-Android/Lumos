severity: major

## F1 「已排除:不可逆」不成立——誤記的 converged 記號進治理帳後不可乾淨回退,還會被週跑自動凍成 golden 基準
severity: major
blocking: 是(實作者會照這句話判斷「出問題大不了revert code」就夠,結果治理帳與 golden 基準已經永久帶著錯資料,gov --stats 收斂計數與「開著哪些迴圈」都會一直算錯,没有任何後續動作能修正)

引句:「不寫新帳欄位,回退就是還原兩處呼叫與判定段」

這句只算「新加的欄位/呼叫」要不要搬資料,沒算到:這份計劃的「出口修正」本身就是讓 `_loop_gov_mark(env, loop_id, "converged", …)`/`_loop_gov_mark(env, loop_id, "cap-reached", …)` 這兩個★既有★呼叫(scripts/lumos:10673、10677)第一次真的對 2026-08-25 後開的迴圈觸發到——修正前這批迴圈全部在委派舊閘那一步就 rc=2 被擋下(intake 已重現,`擋下:panel 閘自 2026-08-25 甲裁後僅供舊迴圈回放`),根本走不到這兩行。出口修好之後,如果處置閘判錯(LENS 設的前提:把沒過的迴圈判成收斂),這兩行就會把一筆錯的 `kind=converged` 寫進 `docs/.governance-log.jsonl`——append-only 帳本,程式碼裡自己講的規矩是「帳不可撤,已誤記就換編號重記」(scripts/lumos:8288 同類錯誤訊息原文)。事後回退程式碼只能讓「以後」不再誤判,救不回已經寫進去的那一筆。

這筆錯記號接下來會被兩個既有消費者吃下去、且都沒有機制認得「後來被人工訂正過」:

1. `gov --stats` 的收斂計數(scripts/lumos:6760-6762):`conv = sum(1 for k in by.values() if "converged" in k)` 只要那個 loop_id 的所有 kind 集合裡出現過一次 `"converged"` 就永遠算進 conv,不管後面有沒有再記一筆 `rewrite`(人裁判整份重寫的正規訂正方式)——對照下面兩行 `capped`/`rewrote` 都特別寫了 `"converged" not in k` 去排除,唯獨 conv 沒有對稱的排除條件。也就是說:就算之後照規矩走 `lumos loop rewrite` 補一筆訂正,`gov --stats` 印出來的收斂率報表仍然永遠把這個編號算成「閘過了」。
2. `governance/autonomous_loop/replay_weekly.py` 的週跑補漏凍結(`_converged_loops_with_specpath` 於 34-52 行:只要 `.governance-log.jsonl` 裡出現過 `kind=="converged"` 就收進清單;89-101 行:只要 `governance/replay/<id>/verdict.json` 還沒建過,就自動跑 `loop replay <id> --freeze --spec <帳上記的 spec_path>`,無人工審核)。`autonomous-loop.sh` 每週自動跑這支模組。這代表:錯記的 converged 一旦寫進帳,最快一週內就會被自動凍成 `governance/replay/<id>/verdict.json` 這份「golden 基準」——之後所有回放比對都拿它當參照點,而它本身可能就是凍住了那次誤判的結果。`_converged_loops_with_specpath` 同樣只認「出現過 converged」,不會因為後來多了一筆 `rewrite` 就跳過(它甚至不去讀後續行)。

`lumos loop list` 也一樣:`LOOP_CLOSE_EVENTS`(scripts/lumos:8660)把 `("design-loop","converged")` 算進「已關門」,錯記的迴圈會從「還開著的迴圈」清單消失,不會再被人回頭盯——這是本來設計給接手/巡檢用的視圖(見該行上方註解「執行DAG_調研 排第一順位的缺口」)。

三個消費者(gov --stats、週跑自動凍結、loop list)全部只認「帳上出現過 converged」這個事實本身,沒有一個會因為人工訂正(`rewrite` 記號)而改判。計劃的「已排除:不可逆」建立在「沒寫新欄位=沒有回退成本」這個前提上,但實際的回退成本不在欄位,在這三個既有讀側的行為——這件事計劃全文(一句話/做法/回退/誠實界線)都沒有提到,也沒有在「回退」段給出「萬一已經誤記了 converged 該怎麼辦」的處置指引。

已看,無:
- 「只印,不改任何閘的判定與退出碼」這句對「建議文字本身會不會被誤信而放行不該放的東西」這條風險是守住的——S7/S8 綁測試保證 disposal 閘與 loop next 的 rc/過關判定不因建議文字改變,而且我查過寫入端: `code 迴圈輪內有 major 以上的席,accepted 必須為空——major 一律折,不得附理由放行` 這條硬擋(scripts/lumos:18392,`_disposal_clause_step` 讀帳重算,不信寫側)跟這份計劃無關、獨立生效——就算編排者照抄「建議 3:附理由放行」誤用在 code 迴圈上,只要那輪真的有 major 以上的發現,disposal 閘寫入端重算照樣會判 `處置集合: ✗` 而 rc≠0。所以 LENS 問的「附理由放行」建議被誤信這條,在 code-loop 場景下有既有硬規矩擋著,這份計劃沒有削弱它。
- 併發/效能/金流/對外送出四項計劃自己排除的理由(只讀帳、只數這個編號的列、不呼叫外部服務)跟程式碼現況一致,我沒找到反例。
- S9(舊迴圈判定路徑不變)這條本身就是這份計劃唯一明著顧到「別波及既有帳」的地方,但它顧的是「判定邏輯」,顧不到上面 F1 講的「判定一旦算錯,寫出去的帳要怎麼收拾」這件事——那本來就不是 S9 的職責範圍,只是連帶說明為什麼 F1 不能靠 S9 解決。

總結:最嚴重 severity 為 major,blocking 共 1 條。
