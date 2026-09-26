severity: major

## F1 逃逸率統計指令放在 gov 底下,踩到 gov 自己劃定的「六帳」邊界,也繞開既有的單帳統計慣例(loop <帳>-stats)
severity: major
blocking: 是
引句:「一個唯讀指令(暫定 `lumos gov --escape-rates`)」

`cmd_gov` 的 docstring 白紙黑字寫死自己彙整的範圍是「六帳(bypass/governance/canary/kill/signoff/ci;rot-queue 2026-08-22 拆出)」,程式碼裡 `load(...)` 也確實只掛這六本(`scripts/lumos:6901-6935` 一路是 bypass-log/governance-log/signoff-log/kill-log/canary-log/ci 六個 `load()` 呼叫),`.escape-log.jsonl` 從沒被 gov 讀過(全庫 grep `escape-log` 只出現在 `cmd_loop_escape`、`_auto_escape` 與白名單,見 `scripts/lumos:7401,9324,9412,19780,20226`,沒有一處在 `cmd_gov` 裡)。`gov --stats` 現有輸出也只是「每道閘的筆數/nodes/commit/起訖日」計數(`scripts/lumos:6680-6682` 的 help 字串),不做依類別分組、更沒有信賴區間估計。

而專案已經有「單一帳本的跨輪統計彙總」該放哪裡的先例:`.canary-log.jsonl` 的讀取面不是掛在 `gov`,而是獨立子指令 `lumos loop canary-stats`(`scripts/lumos:8925-8929`,docstring 明寫「[d4 承諾的讀取面]……跨輪 canary 累積帳彙總」)。逃逸率統計要做的事(依類別分組、算比率、附 95% 信賴區間)形狀跟 canary-stats 一樣,只是換一本帳(escape-log)、換一個維度(分級×範圍類),照專案自己的分層應該是 `lumos loop escape --stats`(或同級新子指令),不是硬塞進 gov 的旗標——塞進去等於把 gov 的「唯讀彙整六帳、不做判定」邊界,悄悄擴成第七帳+做統計判定,而且要嘛破壞 gov docstring 寫死的六帳清單,要嘛讓 `--stats` 這個旗標身兼兩種完全不同的輸出形狀(逐閘計數 vs. 分類信賴區間)。

file: `scripts/lumos:6871-6876`(cmd_gov docstring,六帳邊界)
file: `scripts/lumos:8925-8929`(cmd_loop_canary_stats,既有單帳統計彙總的落點慣例)

## F2 新的抽查帳沒有走「簿記檔單一源白名單」登記,重演過一次的死結
severity: minor
blocking: 否
引句:「抽查帳:抽了哪些提交、各報了幾條、確認幾條、未確認幾條、用了哪個家族。」

計劃會新增一本追加寫的帳(抽查帳,愈讀愈像 `.audit-sample-log.jsonl` 這類新檔),但通篇沒提到要把它加進 `_BOOKKEEPING_FILES`——這是 repo 現成的「簿記檔白名單,單一源、兩個消費者:pitfalls --diff 掃描排除 + code-loop 留痕失效豁免」(`scripts/lumos:19774-19782`)。清單裡已經收了 governance-log/usage-log/ci-log/canary-log/bypass-log/escape-log/kill-log/signoff-log 這八本同類帳,註解直接寫著歷史教訓:canary-log/bypass-log 一開始漏登記,審查記帳在 loop 中發生時會讓 code-loop 的留痕被自己寫的帳弄「失效」而擋推(`scripts/lumos:19783-19786`,對應 `Issues/簿記白名單漏canary與bypass帳`)。抽查帳同樣是工具在 loop 過程中自己追加寫、之後要提交進 repo 的帳,不登記就會複現同一種死結。這不是引入新做法,是既有慣例(新帳本要登記單一源白名單)沒被接到,屬命名/收尾動作跟鄰居不一致、結構本身沒問題。

file: `scripts/lumos:19774-19786`(_BOOKKEEPING_FILES 單一源白名單與歷史死結註解)

已看,無:
- 決定性抽樣(用提交編號雜湊決定抽不抽,S5)不是新做法——`_panel_probe_verdict`(`scripts/lumos:8267-8274`)已有幾乎同形狀的 `sha256(...) % N` 決定性抽查判定(雖然該機制本身 2026-08-25 已退場僅供回放,但手法本身是既有慣例,計劃只是換個場景重用,不算另開一套)。
- capture-recapture 之類的殘餘估計沒有被重新引入——計劃 WHY 段落自己交代了 08-14 降級的決定(`[[Projects/收斂閘殘餘估計降級_計劃]]`)並改走直接抽樣,方向正確,跟既有裁定一致。
- 盲審席記帳(S10/S11)延用 `.canary-log.jsonl` 既有的「選配欄位追加,不影響舊記錄」慣例(如 `--loop`/`--severity`/`--tier` 等鍵的加法),沒有另開一本帳,跟 canary record 一路以來加欄位的方式一致。
- 落點:`lands_in: Systems/loop-convergence-recording` 與現況相符——同範疇的兩份姊妹計劃(`Projects/逃逸自動記_計劃`、`Projects/代碼審跑滿上限的判斷依據_計劃`)都落在同一篇,且都是「消費既有逃逸帳/審查帳、不新增機制核心」的性質,跟本計劃形狀一致;不必另開新 Systems 節點。
- 讀帳失敗處理(實務隱患段「讀的一側遇到寫一半的最後一行要略過不報錯」)與 `cmd_loop_escape --list`(`scripts/lumos:9444-9458`)、`cmd_loop_canary_stats`(壞行跳過註記)既有做法一致。
- 對外送出風險(消費專案預設關閉抽查、盲審照既有外家席規矩)符合既有「外家席一律 Codex」與消費專案隱私邊界的既定做法。

不對齊共 2 條,其中 major 1 條。
