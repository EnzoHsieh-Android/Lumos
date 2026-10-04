severity: minor

# 架構對齊審查 r3:治理帳例行紀錄分流_計劃

白話:r2 提的六條裡,「點名擴充 `_gov_metric_events`」「路徑函式吃 docs 資料夾」「加防漂移釘 S6」「追加忽略行抽小函式」都折對了;本機帳位置沿用 `.ci-log` 的做法也維持一致,沒有第二種做法、沒有跨層直呼。剩下是命名與落點沒寫死的小事:判定函式沒點名、取路徑函式沒命名、欄位對應與忽略清單內容沒說共用哪一份、兩份帳檔清單沒交代、`lands_in` 沒列使用紀錄帳那兩篇。結構對,無 major。

## 問 1 分層與依賴方向

結論:一致。分流只在寫入器決定路徑那一步,讀者在 `cmd_gov` 的 `load` 多讀一本,讀判定的函式不動,沒有新層、沒有反向依賴。
- 兩個寫入器現況就是各自直開檔:`_gate_event`(file: `scripts/lumos:1357-1362`)、`_append_governance_log`(file: `scripts/lumos:1426-1431`);計劃在這兩處的路徑決定點分流,層次不變。
- `load` 是 `cmd_gov` 內的合併讀帳器,檔不在就 return(file: `scripts/lumos:8137-8140`),`.ci-log` 是再多一行 `load(CI_LOG_NAME, …)`(file: `scripts/lumos:8216`),計劃「跟它讀 .ci-log 一樣」對得上。
- `_usage_log` 手上有 `env`(file: `scripts/lumos:16181-16186`),可由 `env.vault.parent` 取 docs 資料夾,不跨層。

severity: minor
blocking: 否

引句:「`_append_governance_log` 一次一批,在迴圈裡逐筆決定,兩本各自開檔、各自吞錯」

「逐筆決定」要在 `_gate_event` 與 `_append_governance_log` 兩處都做;計劃只講白名單規則(〈做法〉1),沒說判定寫成一支共用函式。兩個寫入器現在是兩份獨立的開檔碼(file: `scripts/lumos:1357-1362`、`scripts/lumos:1426-1431`),不點名就可能各抄一份「閘名+種類+hard」的判斷,日後兩處漂移。結構方向對,只差點名一支共用的判定函式(輸入事件、回傳走哪本)。

## 問 2 命名與錯誤處理

結論:`GOV_LOCAL_LOG_NAME`、`USAGE_LOCAL_LOG_NAME` 照 `CI_LOG_NAME = ".ci-log.jsonl"`(file: `scripts/lumos:38432`)的具名常數樣子;錯誤處理沿用現況(`_gate_event` 回 False,file: `scripts/lumos:1361-1362`;`_append_governance_log` 靜默 `except OSError: pass`,file: `scripts/lumos:1430-1431`;`_usage_log` 全吞,file: `scripts/lumos:16193-16194`),一致。`_GOV_LOCAL_PAIRS` 是「具名模組級 tuple 名單」,跟 `_KNOWN_GATES`(file: `scripts/lumos:7771`)、`_SLOT_METRIC_KINDS`(file: `scripts/lumos:3973`)同型。

severity: minor
blocking: 否

引句:「回傳同一層的本機帳。docs/ 不存在時跟現在一樣不寫」

取路徑的函式仍沒有名字,也沒說一支還是兩支:同一支吃檔名、還是治理與使用紀錄各一支。對照 `_ci_log_path(env)` 只吃 env、只回一個檔(file: `scripts/lumos:38525-38526`);本案改吃 docs 資料夾是合理的(兩個寫入器手上沒有 env,file: `scripts/lumos:1357-1358`、`scripts/lumos:1426`),但讀者端(`cmd_gov` 的 `docs`、doctor 的 `env.vault.parent`,file: `scripts/lumos:8137`、`scripts/lumos:3867`)與 `_usage_log` 手上是 env 或已有 docs,實作時容易再長出第二支取路徑碼。建議計劃寫明函式名、是否同時涵蓋兩個常數。

severity: minor
blocking: 否

引句:「`cmd_gov` 的 `load` 多讀本機帳(跟它讀 .ci-log 一樣,檔不在就跳過,欄位對應共用治理帳那一套)」

治理帳的欄位對應現況是 `load(".governance-log.jsonl", lambda d: …)` 內聯的一長串 lambda(file: `scripts/lumos:8161-8175` 一帶),`.ci-log` 則自帶另一個 lambda(file: `scripts/lumos:8216`)。「共用治理帳那一套」要做到,得把那個 lambda 抽成具名 mapper 再餵兩次;計劃沒說抽法,最省事的實作是複製貼上第二份 lambda(第二種做法的苗頭)。另外 `load` 以檔名推顯示標籤(file: `scripts/lumos:8142`),新檔名會得到 `governance-local`,不會壞,但 `--stats` 的「載入哪幾源」會多一個標籤,屬預期內。⚠ 判不準是否值得強制點名。

severity: minor
blocking: 否

引句:「S18 度量改用擴充後的 `_gov_metric_events` 讀兩本,「最舊一筆」取兩本的最小時間」

點名沿用現成的 `_gov_metric_events` 是對的(r2 已折入)。但它現況吃單一 `path` 並回 `(事件, 最舊)`(file: `scripts/lumos:3822-3840`),呼叫端還有 `not gl.is_file()` 就整段 return 的前置判斷(file: `scripts/lumos:3867-3870`);改讀兩本時,簽名要怎麼變(收清單、還是呼叫兩次再合併)與「只有本機帳存在」那個分支要不要放行,計劃沒寫。方向對,細節缺一句。

## 問 3 第二種做法

結論:位置、讀法、錯誤處理都沒有第二種做法;防漂移釘 S6 也比照既有 `t_gov_stats_gate_drift`(file: `scripts/test_lumos.py:6458`)的「模組名單對 `_KNOWN_GATES`」慣例。新程式不會新增 `"gate": 非字面值` 的動態寫點,該釘「最多 2 處」不受影響(file: `scripts/test_lumos.py:6480-6487`)。

severity: minor
blocking: 否

引句:「抽成一支小函式,只加不改既有行。」

追加缺行的小函式是新邏輯,不算第二種做法(r2 已確認),但仍有兩個小處沒寫死:(1) 寫檔該走原子的 `_write_lf`(file: `scripts/lumos:17605`)做讀改寫,不要另用 `open("a")`;(2) 「內容同新建 vault 的那份」會讓忽略行清單存在兩份——`_scaffold_project` 內嵌的字串(file: `scripts/lumos:20877-20881`)與 `_init_additive_setup` 的新建分支(對照既有先例,file: `scripts/lumos:20897-20899`)——專案對這類清單向來要求單一源(file: `scripts/lumos:24188-24190` 的白名單註解就是同類教訓)。建議計劃寫明:忽略行抽成一個模組常數,scaffold 與補行函式共用。

severity: minor
blocking: 否

引句:「本 repo:根 `.gitignore` 加 `docs/.governance-local.jsonl` 與 `docs/.usage-local.jsonl`。」

r2 提的「專案另有列出帳檔名的清單,為什麼不加要寫一句」r3 沒有交代:`_BOOKKEEPING_FILES`(file: `scripts/lumos:24193-24197`)與共改排除清單(file: `scripts/lumos:36521-36525`)都列了舊的 `docs/.usage-log.jsonl` 與治理帳。舊使用紀錄帳照舊追蹤、凍結,所以留在清單裡沒問題;新兩本被忽略、不會出現在 diff,不加多半也沒事,但計劃該寫一句理由,免得下一個人當成漏改。⚠ 判不準是否會有掃描走到被忽略的檔。

## 問 4 落點

結論:治理帳這半 `lands_in: Systems/reversibility-governance-ledger` 合理,該節點 about_code 列 `scripts/lumos`(file: `docs/lumos-toolchain-knowledge/Systems/reversibility-governance-ledger.md:66-67`),主題本來就是治理帳寫入與 `cmd_gov` 彙整,不必另開。

使用紀錄帳那半:該列落點。〈做法〉7 已把它們列成「同步範圍」(r2 已折入),但 frontmatter `lands_in` 仍只有一篇,CLAUDE.md 鐵則 5 要求計劃的 `lands_in` 寫「現況落在哪幾篇」。實際要改的現況句在:`Systems/lumos-cli-read`(file: `docs/lumos-toolchain-knowledge/Systems/lumos-cli-read.md:37`、`:58`、`:117`、`:140`,about_code 含 `scripts/lumos`,`:107-108`)與 `Systems/retrieval-ranking`(file: `docs/lumos-toolchain-knowledge/Systems/retrieval-ranking.md:67`,about_code 含 `scripts/lumos`,`:53-54`)。`_usage_log` 本身(file: `scripts/lumos:16181`)沒有 Systems 節點專門點名,實際的「家」是這兩篇。

severity: minor
blocking: 否

引句:「[[Systems/retrieval-ranking]]、[[Systems/lumos-cli-read]] 與 [[Verification/2026-08-21_工具鏈體檢修復批]] 裡使用紀錄帳的檔名」

建議 `lands_in` 補上 `Systems/lumos-cli-read` 與 `Systems/retrieval-ranking`;Verification 是歷史紀錄,不必列落點。

不對齊共 7 條,其中 major 0 條
