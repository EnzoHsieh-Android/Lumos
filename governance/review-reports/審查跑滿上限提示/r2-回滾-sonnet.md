severity: major

## F1 「回退拿不回來的」給出的兩條補救路(loop rewrite / 另記更正)一條會扭曲統計、一條沒有機制支撐且違反本 repo 自己反覆聲明的帳本紀律
severity: major
blocking: 是(實作者會照這句話寫文件/教接手的人「判錯了就用這兩招之一補救」,但真的遇到誤記 cap-reached 時,兩條路都不能乾淨解決問題,而且會讓 `gov --stats` 的重寫率永久失真——這正是這份計劃自己拿來當 RETIRE-IF 判準依據的同一份報表)

引句:「判錯了要人工補記一筆 `loop rewrite` 或在治理帳另記更正」

查證:
1. **「另記更正」沒有對應機制,而且違反 repo 自己反覆講的帳本紀律**。`_loop_gov_mark` 目前只會被四種 kind 呼叫:`converged`/`cap-reached`/`rewrite`/`replay-refreeze`(逐一 grep `scripts/lumos` 的 `_loop_gov_mark(env, loop_id` 呼叫點,共 12 處,kind 只落在這四種),沒有任何「更正/correction」事件類型,CLI 子指令也沒有能寫這種事件的介面。要「在治理帳另記更正」,唯一手段是手改 `docs/.governance-log.jsonl`——但這正是這份計劃本身落點的節點明文禁止的做法:`docs/lumos-toolchain-knowledge/Systems/loop-convergence-recording.md` 第 149-153 行寫「帳是只能加不能撤的,所以記完帳之後再去動那些檔案,整輪的留痕就作廢,而且救不回來……唯一的處置是換編號重記(這篇別處已經寫過)」。同一份筆記整篇沒有出現任何「另記更正」這種寫法。計劃提出一個 repo 自己從沒用過、也違反自己紀律的補救選項,且是唯一入口(前一句只提到 gov --stats 與 loop list 會讀到誤記,沒有其他備援)。

2. **`loop rewrite` 能不能用在「不是要重寫的迴圈」上——查證結果是「用得上但語意和統計都會歪」**。`cmd_loop_rewrite`(scripts/lumos:813-851)硬性要求 `--successor` 是一個**新開的、跟原編號不同**的迴圈 id(818-820 行:「--successor 要給新開的迴圈編號,而且不能跟舊編號一樣——重寫=換新編號載新版,同號沒有『重寫』可言」,不符即 rc=2 擋下)。也就是說「補記一筆 loop rewrite」在字面上做不到「原地更正」,一定要真的開一個新編號。若只是想訂正「處置閘誤判成沒過」這件事(不是真的要重新設計),拿 `loop rewrite` 來用會有兩個連帶後果,計劃完全沒提:
   - `gov --stats` 的重寫計數 `rewrote = sum(1 for k in by.values() if "rewrite" in k and "converged" not in k)`(scripts/lumos:6762)會把這筆「訂正」算進「人裁判整份重寫收尾」(scripts/lumos:6763 印出的文字),永久誤導這份報表——而這份計劃的 `REVISIT:2026-10-26` 明寫要「回看跑滿或熔斷時印的建議,跟事後治理帳的走向(收斂/重寫/再跑)對得上幾次」,回看的依據正是這張會被污染的表。
   - `cmd_loop_rewrite` 會自動查「這個編號是不是已經是上一次重寫的產物」,若是則印「★這已是連續第二次判重寫……強制攤人,不得三開★」(scripts/lumos:847-848)。拿它做訂正用途,會在完全沒有真正重新設計的情況下觸發這個攤人警告,誤導後續接手的人。

3. **更關鍵的是:計劃沒提到的那條「不需要新機制、也不會污染統計」的路其實已經存在**——同一個 loop_id 不需要開新編號,只要繼續在原編號下補審查輪,一旦真的收斂並記下 `converged`,`gov --stats` 的 `capped` 計數公式本身就會自動排除它(`capped = sum(1 for k in by.values() if "cap-reached" in k and "converged" not in k and "rewrite" not in k)`,scripts/lumos:6761——只要同一 loop_id 的 kind 集合裡後來出現過 `converged`,就不算進 capped)。計劃只給了「loop rewrite / 另記更正」這兩個選項,兩個都比「原地繼續審到真收斂」麻煩且有副作用,卻沒提這條最貼近現況、成本最低的路,讓讀者以為那兩個是僅有的選擇。

已看,無:
- 「收斂記號只由處置閘寫,這一點跟今天一樣」這句話,若理解成「這份計劃改動所觸及的範圍(2026-08-26 後開、原本會在委派舊閘那步 rc=2 被擋下的迴圈)不會新增一個寫 converged 的入口」,查證是對的:這批迴圈在修正前根本走不到任何一處 `_loop_gov_mark(..., "converged", ...)`(舊閘先擋),修正後只會經過 `loop status --disposal` 既有的 `disposal gate PASS` 那一處(scripts/lumos:18584),沒有新增第二個 converged 寫入點。這句話沒有廣稱「全 repo 只有一處會寫 converged」(全 repo 實際有 9 處 `_loop_gov_mark(..., "converged", ...)` 呼叫點,是給 light/舊迴圈等範圍外路徑用的,S10 明文排除、這份計劃不動它們),在它自己界定的範圍內成立,不算誤導。
- LENS 問「新迴圈第一次寫出 cap-reached 對週報……的影響」:查了 `governance/autonomous_loop/replay_weekly.py` 的 `_converged_loops_with_specpath`(34-52 行),只認 `kind=="converged"`,不讀 `cap-reached`,所以週跑自動凍結不會被這份計劃新增的 cap-reached 記號觸發——計劃沒提這件事,但也不需要提,因為確實沒有影響。
- LENS 問「提示被照做後錯了,既有規矩擋不擋得住」:查了 `_disposal_clause_step`(scripts/lumos:18153-18392),`accepted` 必須為空的硬擋只對 blocker 全類型適用(18390 行)、對 major 只在 code-loop 適用(18392 行的註解明寫「散文設計審不受此限」)。也就是說 design-loop 的處置閘本來就沒有「major 不得附理由放行」的機械硬擋——但這是既有 disposal 閘的既有行為,不是這份計劃放寬或引入的(計劃 S8/S9 綁測試保證退出碼不變),而且這份計劃自己新增的 S12 要求「折入數在降而仍有 major 以上」時只能印「由人裁」而不是「建議再一輪」,沒有在字面上鼓勵繞過這道既有的鬆綁——所以這條不算這份計劃造成的新洞,只是既有 disposal 閘本身對 design-loop 的縱深天生比 code-loop 淺,計劃沒有讓它變得更淺。
- 「已排除:守衛面」段落聲稱的「提示只印不擋,不改處置閘與 loop next 的過關判定和退出碼」查了 S8(scripts/lumos 尚未實作,但條款文字綁 `[test:t_disposal_early_breaker_total_folded]` 要求「不改變過關判定與退出碼」)與現有 `_loop_status_disposal` 唯讀行為一致,是可信的字面承諾,沒有找到反例。

總結:最嚴重 severity 為 major,blocking 共 1 條。
