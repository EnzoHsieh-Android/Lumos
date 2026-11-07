severity: major

F1
severity: major
blocking: 是
引句:「同會談 `.lint-` 開頭的已有 3 個 = 不再擋」
說明:標記檔 `stop-block/<會談>.lint-<batch>` 是整個會談共用,不分回合,所以「三批上限」會被一個長會談用光。
- 具體例子:同一個會談第 1 回合擋了 3 批(AI 分三次修,每修一點批次雜湊就換)。第 20 回合寫出全新的 `GlobalScope.launch`,第 4 批就不擋了。
- 整個回合結束檢查在這個會談剩下的時間都是死的,推送前閘才會補上。
- `claude --resume` 接續同一個 session_id 時也一樣,標記檔要等 7 天才清。
- 同一批告警(批次雜湊相同)在別的回合重現,也因為 O_EXCL 建檔失敗而不擋。
- 決策 d1 的目的是防止卡死,但字面做法把「同一回合的續做迴圈」和「整個會談的壽命」混成同一個計數。
- 建議:上限與去重改綁 `prompt_id`(回合),或在每次 `UserPromptSubmit` 記起點時清掉本會談的 `.lint-*`。

F2
severity: major
blocking: 是
引句:「status 是 blocked 時,用既有記帳路徑(`_gate_event_or_warn`)寫一筆 `stop-lint` 擋下事件」
說明:記帳發生在 `lint-new` 裡,鉤子還沒決定要不要擋。
- 鉤子隨後可能因為「這批擋過」或「已三批」而不擋,但治理帳已經多了一筆「擋下」。
- 例子:`stop_hook_active` 那次同一批再查一次,`lint-new` 回 blocked 並記帳,鉤子卻沒擋,所以一次真擋下會記成兩筆。
- 超過三批之後,每次收工都會繼續記「擋下」。
- RETIRE-IF 寫的是「連續三個月治理帳零筆 `stop-lint` 擋下事件」。這個量被灌水之後幾乎不會是零,撤除條件失效。
- 治理帳 `docs/.governance-log.jsonl` 在消費專案裡是被追蹤的檔(本 repo 起始狀態就顯示為 M),每次記帳都會弄髒工作樹。
- 建議:由鉤子在真的擋下後,再用獨立旗標或另一個呼叫記帳。

F3
severity: major
blocking: 是
引句:「沒有知識圖譜的專案、冷卻窗內的同一支檔,不推決策列。」
說明:冷卻窗是為了省掉昂貴的完整影響推播,但決策列比對只是對 `delta_new` 做一次本機正規式。
- 字面做法讓冷卻窗內的快速路徑完全不推列。AI 改同一支 kt 檔通常是幾分鐘內反覆編輯。
- 例子:t=0 第一次 Edit 沒有觸發字,t=5 分鐘第二次 Edit 才加進 `flatMapLatest`。這次落在 20 分鐘冷卻窗內,走 `--incidents-only`,不推 D 列。
- 結果是「寫入當下推相關列」只對每支檔 20 分鐘內的第一次編輯生效,S9 的預期行為在最常見的使用情境下做不到。
- 天花板 6 把這點當已知限制,但它抵銷了機制的主要價值,不只是邊角。
- 建議:決策列比對獨立於冷卻窗,或冷卻窗只擋影響推播、不擋 `decision_rows`。

F4
severity: minor
blocking: 否
引句:「而且 payload 有 `prompt_id` 時要跟紀錄相同」
說明:條件寫的是「有 `prompt_id` 才比對」,沒說 payload 缺 `prompt_id` 時怎麼處理。
- 字面解讀是缺了就略過比對,直接採用 `stop-turn/<會談>` 裡的舊起點。
- 例子:Codex 的 Stop 若沒帶同名欄位(S12 自己承認未實測),起點可能是好幾回合前的。
- 後果是「這回合碰過的檔」變成前面所有回合,已被忽略的舊告警又被重新算進來。
- 另一個失敗情境:`UserPromptSubmit` 在沒有 `.lumos/lint.json` 的主 repo 不寫起點,之後用 `EnterWorktree` 切到有 lint.json 的工作樹,Stop 會得到「沒記到起點」而靜默不檢查。
- 建議:缺 `prompt_id` 視為對不上,不檢查。起點是否記錄與 repo 無關,改成每個提示都記。

F5
severity: minor
blocking: 否
引句:「`UserPromptSubmit` 在每次送出提示(含 Claude Code 自己起的回合)時觸發、帶 `prompt_id`」
說明:實驗 E1 只測了 `claude -p` 與 `--resume`,沒有量測背景任務通知或 cron 自動起的回合是否觸發 `UserPromptSubmit`。
- 若不觸發,這類回合的 Stop 帶新的 `prompt_id`,會落在「對不上,不檢查」,靜默漏檢。
- 這是依據表裡未驗證就寫成「採用」的前提。
- 建議:補一個實驗,或在 S12 加一個自動起回合的案例。

總結:最嚴重是會談級上限與批次去重讓長會談中途失去檢查、記帳灌水使撤除條件失效、以及冷卻窗讓決策列只在每檔第一次編輯生效,會擋 3 條。

重判說明:F1、F2、F3 照計劃字面實作都會做出錯的行為,所以維持 major,把 `blocking` 改成「是」,與規則一致。F4、F5 維持 minor、blocking 否。
