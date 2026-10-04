severity: minor

# 架構對齊審查 r2:治理帳例行紀錄分流_計劃

白話:r1 的 major(本機帳放 .git/lumos/ 是第二種位置)改得對——現在的 `docs/.governance-local.jsonl` 加根 `.gitignore`、常數加取路徑函式、讀者走 `cmd_gov` 的 `load`,跟 `docs/.ci-log.jsonl` 完全同一套,沒有新的第二種做法。剩下的都是命名沒寫死、少一條防漂移釘、沒說清楚要沿用哪支現成函式這類小事,結構是對的。

## 問 1 分層與依賴方向

結論:一致。分流放在寫入器(決定路徑那一步)、讀者在 `cmd_gov` 的 `load` 多讀一本、doctor 段另抽模組層級函式,沒有跨層直呼。
- 寫入器現況就是各自直開檔:`_gate_event` 開 `docs / ".governance-log.jsonl"`(file: `scripts/lumos:1358`)、`_append_governance_log` 開 `vault.parent / ".governance-log.jsonl"`(file: `scripts/lumos:1426`),所以在這兩處的路徑決定點分流,層次不變。
- `load(name, mapper)` 是 `cmd_gov` 內的合併讀帳器(file: `scripts/lumos:8137`),`.ci-log` 就是再多一行 `load(CI_LOG_NAME, …)`(file: `scripts/lumos:8216`),檔不在就 `return`,計劃「跟它讀 .ci-log 一樣,檔不在就跳過」對得上。

severity: minor
blocking: 否

引句:「doctor 的 spec-gate 比例段與 S18 度量改成讀兩本(抽一支模組層級的小函式給它們共用,`cmd_gov` 的 `load` 不搬)」

doctor 那幾段現況是各自寫死 `env.vault.parent / ".governance-log.jsonl"`(file: `scripts/lumos:2238`、`scripts/lumos:2869`、`scripts/lumos:3867`),S18 已有讀檔核心 `_gov_metric_events(gl)`(file: `scripts/lumos:3867` 一帶呼叫)。計劃寫「抽一支小函式」,沒說是擴充這支現成的、還是另開一支;另開就會出現兩支功能相近的讀者。另外 `load` 內對治理帳的欄位對應(file: `scripts/lumos:8161`)本機帳也要用同一份 mapper,計劃沒提要共用。方向對,只差點名沿用哪支。

## 問 2 命名與錯誤處理

結論:大方向一致。`GOV_LOCAL_LOG_NAME` 照 `CI_LOG_NAME = ".ci-log.jsonl"`(file: `scripts/lumos:38432`)的樣子(無底線開頭的具名常數、點開頭檔名),兩本各自吞錯對齊 `_gate_event` 回 False(file: `scripts/lumos:1359-1360`)與 `_append_governance_log` 靜默 `except OSError: pass`(file: `scripts/lumos:1427-1431`)。

severity: minor
blocking: 否

引句:「取路徑的函式跟版控帳同一個資料夾(`<docs>/.governance-local.jsonl`),照 `CI_LOG_NAME`/`_ci_log_path` 的樣子寫」

兩處小差異:
- 函式名沒定。`_ci_log_path(env)` 吃的是 env(file: `scripts/lumos:38525-38526`),但兩支寫入器手上拿的是 `repo_root`(`_gate_event`)與 `vault`(`_append_governance_log`),不是 env,取路徑函式的參數形狀得跟這兩邊對上,計劃沒寫。⚠ 判不準要不要拆兩支。
- 檔名 `.governance-local.jsonl` 不是既有帳檔的 `.xxx-log.jsonl` 形(`.bypass-log`、`.canary-log`、`.ci-log`,見 file: `scripts/lumos:24193-24197`);`load` 用 `name.lstrip(".").replace("-log.jsonl", "")` 取標籤(file: `scripts/lumos:8143`),這個檔名會得到 `governance-local`,不會壞,只是跟其他帳不同型。

## 問 3 第二種做法

結論:位置不再是第二種(沿用 `.ci-log` 的做法,已確認)。兩個常數也不算新做法:專案本來就有「模組級 tuple 名單 + 旁邊驗證」的慣例,`_KNOWN_GATES`(file: `scripts/lumos:7771`)與 `_SLOT_METRIC_KINDS`(file: `scripts/lumos:3973`,在 file: `scripts/lumos:4041-4044` 被拿去驗閘名與種類)。觀察型閘名單是 `_KNOWN_GATES` 的子集、留痕種類是另一個角度的分類,語意不同,不必併進同一張,並列即可。

severity: minor
blocking: 否

引句:「兩份名單是唯一定義,各放一個常數,寫入器查它們決定路徑。」

觀察型閘名單裡的閘名(如 note-shape、note-reread、drift-check、nodehome-check、spec-gate,確實都在 `_KNOWN_GATES`,file: `scripts/lumos:7783-7800`)沒有機械方式保證永遠是 `_KNOWN_GATES` 的子集。既有先例是 `t_gov_stats_gate_drift`(file: `scripts/test_lumos.py:6458`)這類漂移釘。名單裡打錯字,後果只是照舊進版控(偏吵不偏丟),所以不到 major;但驗收條款 S1-S5 沒有一條守這個。建議加一條同類漂移釘或在條款裡寫明。

severity: minor
blocking: 否

引句:「既有 vault 由 `_init_additive_setup` 補——`docs/.gitignore` 存在而缺這一行就在尾端追加」

專案裡沒有現成的「對既有 .gitignore 追加缺行」工具。最接近的只有「不存在才建」:`_init_additive_setup` 的 `if not gov_ignore.exists()`(file: `scripts/lumos:20897-20899`)與 file: `scripts/lumos:30659-30660`;寫檔原語是原子的 `_write_lf`(file: `scripts/lumos:17605`)。所以「追加」是新邏輯(讀、判斷缺行、補、寫),不算第二種做法,但該明講走 `_write_lf` 做讀改寫、不要另用 `open("a")`,並抽成一支小函式(以後再補別的忽略行可沿用)。

severity: minor
blocking: 否

引句:「本 repo 在根 `.gitignore` 加 `docs/.governance-local.jsonl` 與 `docs/.usage-log.jsonl`」

專案有好幾份「列出所有帳檔名」的清單:`_BOOKKEEPING_FILES`(file: `scripts/lumos:24193`)、共改排除清單(file: `scripts/lumos:36523-36525`)、scaffold 的 docs/.gitignore 內容(file: `scripts/lumos:20878-20881`)。計劃只提到改 scaffold 的註解與忽略行,沒說本機帳與「使用紀錄帳已不追蹤」要不要進另兩份清單。被忽略的檔不會出現在 diff 裡,所以不加多半沒事(⚠ 判不準),但計劃該寫一句「為什麼不加」,免得下一個人以為漏了。

## 問 4 落點

結論:`lands_in: Systems/reversibility-governance-ledger` 合理。該節點 about_code 列 `scripts/lumos`(file: `docs/lumos-toolchain-knowledge/Systems/reversibility-governance-ledger.md:66-68`),主題本來就是治理帳的寫入、`cmd_gov` 彙整與閘名單,分流屬同一條線,不必另開。分流表的唯一定義留在程式常數,節點只寫 WHY 與限制,不複製表。

severity: minor
blocking: 否

引句:「`Systems/reversibility-governance-ledger` 裡「來源幾本」「唯一寫者」「帳檔都進版控」的說法、手冊提到治理帳寫在哪裡的段落、scaffold 的註解,一起改。」

使用紀錄帳的部分沒有落點:停止追蹤的是 `docs/.usage-log.jsonl`,它的寫者 `_usage_log`(file: `scripts/lumos:16181-16186`)與「查閱即 append usage-log」的說法住在 `Systems/lumos-cli-read`(file: `docs/lumos-toolchain-knowledge/Systems/lumos-cli-read.md:37`、`:58`、`:140`)與 `Systems/retrieval-ranking`(file: `docs/lumos-toolchain-knowledge/Systems/retrieval-ranking.md:67`)。這幾句沒寫「版控與否」,不一定要改,但計劃的 `lands_in` 與〈做法〉6 應寫明「檢查過這兩篇,不需改」或把需要改的一句寫進去。

不對齊共 6 條,其中 major 0 條
