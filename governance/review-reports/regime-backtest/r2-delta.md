# 審查報告:改制回測 r2(delta 席,折入回歸鏡頭)

sha256 已核對 = 51b418d7...ddf1。

## d-f1
severity: blocker
引句:「週跑另補漏(已收斂未凍結的自動凍)」
佐證:file: `governance/review-reports/regime-backtest/r2-snapshot.md:30`(S2:"--freeze"必帶`--spec`,見同段"凍結模式,--spec 必帶");file: `scripts/lumos:3532`(`rec["result_sha256"] = _sha256_file(spec)`——record 只把 spec 內容雜湊寫進帳,`spec` 這個路徑變數從沒被指派進 `rec`);file: `docs/.canary-log.jsonl`(現場 tail 抽樣欄位:`accepted_set/auditor/finding_kinds/findings/findings_set/folded_set/kind/loop/note/report_path/report_sha256/result_sha256/reviewed_sha256/round/scope_lines/severity/snapshot_path/snapshot_sha256/token/tokens/ts/wallclock_min`——無任何 spec 路徑欄)
說明:S2 為解 s3-f2(首批後入庫空白)新增「週跑另補漏:已收斂未凍結的自動凍」——這是本輪(r2)才出現的新機制,r1 五席從未討論過。但 S1 自己剛把 CLI 拆成兩模式時明講「`--freeze` 必帶 `--spec`」;而週跑掃描到「已收斂但還沒 `--freeze` 過」的 loop 時,它手上除了 loop_id 之外沒有任何管道能取得該 loop 對應的 spec 檔路徑——治理帳只存 spec 內容的 sha256(`result_sha256`),從沒存過路徑本身,`report_path`/`snapshot_path` 指的是審查報告/快照,不是被審的計劃書。照字面實作,這段「自動凍」程式碼寫下去的第一行就會卡在「這個 loop 該用哪個 `--spec` 路徑」——沒有資料來源可填,根本跑不動,只能靠人工維護一份額外的 loop→spec 對照表(spec 完全沒提這件事)。而「gate PASS 後跑 --freeze」這個立即凍結的路徑目前也不存在任何自動呼叫點(`--disposal` 在 `governance/autonomous-loop.sh` 裡完全沒被引用,是人/agent 收工時手動敲的),所以「自動凍」這個補漏機制正是「首批之後誰入庫不留空白」這句話唯一的兜底保證——而這個兜底本身無法執行。

## d-f2
severity: major
引句:「live 帳篩 loop==id 的集合≠凍結集合」
佐證:file: `governance/review-reports/regime-backtest/r2-snapshot.md:29`(S2 定義閉包內容為「該輪帳列逐行原文」,即只凍結被判定的那一輪);file: `scripts/lumos:10101`(`_loop_status_disposal` 的 `rounds` 參數已是全部傳入列,函式內部才 `groups.setdefault(rid_, []).append(r)` 按 round 分組);file: `scripts/lumos:10147`(`rid, latest = next(reversed(groups.items()))`——「latest」只是眾多分組裡的最後一組,證明同一 loop_id 常見有多組/多輪並存)
說明:S2 把 golden 閉包定義成「該輪」(只有被判定的那一輪)的帳列,但 S1 拿來跟即時帳本比對「帳被動/帳本長大」用的集合卻是「live 帳篩 `loop==id`」——沒有限制在同一輪。凡是走到第 2 輪以上才收斂的 loop(r1-s2-f1 自己實測過的 `selfaudit-loop` 就有 r1~r3 三輪並存),凍結當下 live 帳裡本來就已經有比「該輪」更多的行(前面幾輪的舊帳列)。照這條規則字面執行,凍結完的下一秒重放,「live 集合」與「凍結集合」就已經不相等——不是因為之後有人動了手腳或合法追加新輪,是因為兩邊「集合的定義範圍」從一開始就不同構。結果是「帳本長大」這個分類會對任何多輪才收斂的 loop 恆常觸發,即使什麼事都沒發生;S1 自己給的行為斷言「同 loop_id 追加新列(fixture)→列帳本長大」只驗證了「單輪 loop 之後被追加新輪」這一種情境,沒有測「凍結當下 loop 本來就有前面幾輪」這種常見情境,fixture 沒接住,severity 判斷會被這個永遠為真的雜訊淹沒,實質上讓「帳本長大」這個分類失去意義。

## d-f3
severity: major
引句:「readonly 是新參數」
佐證:file: `governance/review-reports/regime-backtest/r2-snapshot.md:29`;file: `scripts/lumos:10101`(`_loop_status_disposal` 內建 `_roster_tail()` 幫手函式);file: `scripts/lumos:10296-10309`(`_roster_tail()` 在 `roster` 參數為預設值 `False` 時仍會呼叫 `_roster_observe(..., anomalies_only=True)`,若回傳非空,接著 `_ldir.mkdir(parents=True, exist_ok=True)` 建目錄、`open(_ldir / "roster-alerts.log", "a", ...)` 追加寫檔)
說明:S1 說判定核心「抽成純函式」「live 路徑與 replay 共用同一份」,而「readonly」這個新參數的作用範圍,照 S1 自己的描述只鎖在「不呼叫 `_loop_gov_mark`、治理帳零寫入」,fixture 也只釘「治理帳行數不變」。但要重用的這份 `_loop_status_disposal` 本體裡,除了 `_loop_gov_mark` 之外還有第二個既有寫入路徑——`_roster_tail()`:只要呼叫時 `roster` 參數維持預設的 `False`(spec 沒說 replay 要傳 `roster=True`,傳了也會改變輸出行為、不是無痛選項),且該輪剛好命中六種異常之一(外部審查員不夠、單家族、真兼任等——這在歷史帳裡是真實會發生的狀況,S3 對照就記錄過「單家族」案例),就會建目錄、追加寫入 `governance/review-reports/<loop_id>/roster-alerts.log`。這是貨真價實的檔案寫入,只是不算進「治理帳」(`.governance-log.jsonl`/`.canary-log.jsonl`),所以 spec 講的「readonly」「治理帳零寫入」跟它釘的 fixture 全部答對、卻沒堵住這條路——回放器(尤其是 S4 週跑,每週要掃過「新凍結必跑+存量抽 5 包」這麼多筆)會在使用者毫無所知的情況下持續往 `governance/review-reports/` 底下寫檔案,跟「回放 advisory、不進閘、不留副作用」的定位不符。

## d-f4
severity: major
引句:「存量輪替抽樣每週 5 包」
佐證:file: `governance/review-reports/regime-backtest/r2-snapshot.md:32`;file: `governance/autonomous-loop.sh:138-233`(`run_exam` 靠 goldset 歷史裡最後一筆 `ts` 算「距上次幾天」補跑;`run_probe` 靠 `history.jsonl` 裡有沒有本週 `seed` 字串判斷跑過沒;`run_nags` 靠 `governance/nags-last-week.txt` 存一個週戳記)——三支既有週期任務全是「距上次多久」或「本週跑過沒」這種無狀態/單一戳記判斷,沒有一支做「在一批固定名單裡輪流各抽幾個、輪完從頭來過」這種需要記住「上次抽到哪裡」的排程
說明:「輪完一圈重來」是一個具體的承諾——保證存量裡的每一包遲早都會被抽到、不會有包永遠沒被抽過。要兌現這個承諾,系統必須在每週執行之間記住「這一圈已經抽過哪些包」這件事,但 S1~S4 沒有一條講這個游標/記錄要存在哪裡、用什麼格式。本專案目前所有週期任務(`run_exam`/`run_probe`/`run_nags`)都不需要這種狀態,沒有現成模式可以照抄;而 S1 又把「readonly、不寫治理帳」講得很滿(見 d-f3),如果 implementer 順著這個氣氛把「輪替抽樣」寫成無狀態的 `random.sample(existing, 5)`,「輪完一圈重來」這句承諾就永遠兌現不了——會有包長年抽不到、也會有包被重複抽中,S4 自己定義的行為就不成立,但表面上程式碼「跑得動」、也不會報錯,是那種容易被漏掉的邏輯洞。

## 掃過但乾淨的面

- 卷證完整性:核對 `shasum -a 256` = `51b418d78389a8b5d36e77d9b47dc98f4f42ee389c2bf70c44ffc90cfd02ddf1`,與題目給定值相符,審查基礎成立。
- 抽查 6 條以上折入是否真的落進條款本文(而非只停在「審計修正紀錄」段落):s1-f2(spec sha 併入閉包)、s1-f3(`--freeze`/`--golden` 兩模式分拆)、s1-f4(閉包存「該輪帳列逐行」而非讓 replay 重新抓「latest」)、s2-f1(S3 新增 a/b/c 三形狀分類)、arch-f2/arch-f3(機器檔案改立 `governance/replay/` 新目錄、對照產物改成圖譜驗證紀錄)、ext-f2/s3-f3(`engine_rev` 分流 + 比照 `anchor approve` 的重凍留痕流程)——六條全部確認寫進 S1~S4 條款本文,不是只停留在修正紀錄的一句話總結。
- `governance/replay/` 目錄現場確認尚不存在(不會跟既有東西撞),`governance/golden` 根目錄現場確認 0 個裸檔(`find -mindepth 1 -maxdepth 1 -type f` 回傳 0)——arch-f2/f3 的折入描述跟現況一致,沒有落空。
- 「readonly」跟「`--freeze` 要寫檔」表面像矛盾,但細讀範圍是分開的:readonly 限定在「不進治理帳」,`--freeze` 寫的 `verdict.json` 在 S2 裡明文定義成「判定快照非帳」——這條邏輯本身自洽,真正的洞是 d-f3 那個沒被兩邊都提到的第三個寫入點(`roster-alerts.log`),不是 readonly/`--freeze` 兩者互打。
- `scripts/lumos` 裡 r1 五席引用的行號(4277 spec hash、4666 `cmd_loop_status` 簽名、10101 `_loop_status_disposal` 簽名、10325 `_loop_gov_mark` 呼叫、10661 `cmd_anchor_approve`)在本次複查時全部原封不動——r1 的證據鏈仍是本次 delta 審查可靠的基線,程式碼沒有在兩輪之間漂移。
- G3 hash 鏈在 replay 模式下確實會變成永遠為真的比較(因為 S2 把「spec sha」定義成「窗末 result_sha256」,跟 `_hash_chain_check` 比對的目標值同源)——這符合行為斷言「spec 檔事後被編輯→回放不受影響(G3 用凍結 sha)」的明文設計意圖,是刻意的、非漏洞。
