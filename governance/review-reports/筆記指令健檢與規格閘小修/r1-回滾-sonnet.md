severity: major

我用回滾鏡頭逐條看了寫入入口:summary-add、summary-line、append lands_in、治理帳 spec-gate-record、筆記裡的「(新增)」寫法、紀律範本與版本號、推送閘多查 done 計劃。其中兩條會讓退回或上線後的狀態出問題(1、2),一條是文件漏講(3)。前掃已修的項目沒有重報。

**1. 第 10 節 B2:舊的 done 計劃被改到就被擋,而且沒有出路**
severity: major
blocking: 是(照字面實作,推送閘會對沒犯錯的人擋下,補救步驟又走不通)
- 段落:〈做法〉10 的 B2、〈實務隱患〉守衛面 (c)、B1 (b)。
- 引句:「只限這次改到計劃檔本身的,而且條款沒變時指紋不變、照跑測試即可」
- 問題:這句假設「條款沒變就照跑測試即可」,但有兩條路不成立。
  - 路一,測試已不存在:留痕裡的測試名在實作後被改名或刪除,`_spec_gate_push_one` 會把它判成 dangling,回「留痕裡的測試沒全綠」。
  - 路二,條款區塊動過:在 done 計劃的條款區塊裡改一個字,`_spec_gate_push_stale` 就判留痕過期,要人「重跑 lumos spec-gate」。但計劃已實作完,重跑會落到 B1 (b),測試全綠所以照擋。唯一的出路是照擋下訊息把實作檔換回舊版,而實作可能早就是很多個提交之前的事。
- 具體例:一份上個月 done 的風險低計劃,留痕列了 t_old_name,該測試後來改名。本次推送只為了在計劃正文補一句「回退」,範圍改到了計劃檔,B2 新規則把它收進候選,推送被擋。要退回這個行為,只能還原整個提交 ⑦,等於連 B3 一起拿掉。
- 佐證:`file: scripts/lumos:9750-9780` 的 `_spec_gate_push_scan` 現在只對 doing 做 `full`。`file: scripts/lumos` 的 `_spec_gate_push_one` 對 `dangling` 回非綠。
- 缺的東西:候選裡 done 計劃的處理要寫明,至少要涵蓋「留痕測試找不到」和「指紋過期」兩種情形。可行做法是只提醒不擋,或指紋過期時整份略過。

**2. 回退節:還原提交 ① 會讓消費專案一直拿著不存在的指令,而且沒有提示**
severity: major
blocking: 是(照字面做回退,消費專案的 AI 會被紀律區塊指向已移除的 summary-add)
- 段落:〈做法〉1 第 7 點的 `LUMOS_VERSION` bump、〈回退〉。
- 引句:「七個提交各自獨立,還原哪一個就回到那一節原本的行為。」
- 問題:正向上線時 bump 版本,消費專案跑 `lumos update` 後,CLAUDE.md 的紀律區塊版本 v(N+1) 列出 summary-add。照「還原提交」,版本常數也回到 v(N)。
  - 版本檢查規則是 CLAUDE 版本 ≥ 來源版本就不提示,`file: scripts/lumos:25500` 附近的 `ct >= st` 回 None。
  - 結果:已更新的消費專案不會再被提示刷新,CLAUDE.md、AGENTS.md 永遠留著 summary-add。
- 具體例:消費專案已更新到 v1.4。工具鏈還原 ① 後版本回到 v1.3,消費專案的 `lumos update` 提示靜默,紀律區塊仍叫人用不存在的指令。
- 回退節只講了本 repo 要重注入,沒講消費專案;回退時版本要再往前 bump,不能回到舊值。

**3. 〈回退〉的「設定與既有帳本格式都沒有改」不完整**
severity: minor
blocking: 否(退回後只是 refcheck 多報幾條,不會做出壞系統)
- 引句:「設定與既有帳本格式都沒有改。」
- 問題:⑤ 上線後,計劃正文會出現「(新增)」標記。退回 ⑤ 後,舊版 refcheck 把這些路徑當 missing 並回 rc1,設計審手冊步驟 2 的 refcheck 在這些計劃上變紅。
- ⑦ 的回退句有講治理帳事件留著無害,⑤ 在回退節沒有對應的一句。
- 補一句「還原 ⑤ 後,已標『(新增)』的計劃在舊 refcheck 會列 missing,需手動拿掉標記或接受警告」即可。

**其餘入口,已讀無 finding**
- 提交 ① 的 summary-add 寫入、summary-line 的寫前形狀檢查:只改 .md 本文,舊工具讀得懂。
- 提交 ② 的 append 正規化 lands_in:寫出的是舊工具本來就收的純字串。
- 提交 ④:只是 lint 提醒。
- 提交 ⑥ 的 B8、B9、W6:不寫入任何帳或筆記。
- 提交 ⑦ 的 B3 治理帳寫入:
  - `("spec-gate", "spec-gate-record")` 不在 `_GOV_LOCAL_PAIRS`,依 `hard` 為 False 的判定走版控帳;「spec-gate」已在 `_KNOWN_GATES`,不會被拒寫。
  - 退回後,舊工具只把這筆當成多一個 kind 的事件,`gov` 統計與 doctor S14 都以 kind 篩選,不受影響。
- B11 relabel、W10 警告去重:只改輸出,沒有持久格式。

最嚴重 severity:major;blocking 共 2 條(第 1、2 條)。
