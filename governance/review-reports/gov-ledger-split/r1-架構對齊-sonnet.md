severity: major

# 架構對齊審查 r1:治理帳例行紀錄分流_計劃

白話:計劃的分流點(在寫入器決定路徑那一步)和既有分層一致;但「本機帳放 `.git/lumos/`」是專案裡第一個這種位置,而專案早有現成的「本機不進版控流水帳」做法(`docs/.ci-log.jsonl` + 根 `.gitignore` + `cmd_gov` 條件載入),計劃沒提也沒評比就另開了第二種。

## 問 1 分層與依賴方向

severity: minor
blocking: 否

結論:分流點的分層與既有一致,只有「讀者小工具」是多餘的新層。
- 四支寫入器各自直接開 `docs/.governance-log.jsonl` 寫,沒有共用的「決定路徑」函式:`_gate_event` 直開 `docs / ".governance-log.jsonl"`(`scripts/lumos:1358`)、`_append_governance_log` 用 `vault.parent / ".governance-log.jsonl"`(`scripts/lumos:1426`)、`_codeloop_gov_log` 用 `docs / ".governance-log.jsonl"`(`scripts/lumos:42423`)。計劃說「在四支決定路徑那一步分」與現況一致,沒有跨層直呼;但要在四處各改一次路徑,等於重複四份分流判斷,宜抽成一個路徑解析函式(計劃說「唯一定義放在一個常數」只管表,沒管路徑解析)。這點算結構小瑕疵。
- 計劃說的「兩本一起讀的小工具」:既有的合併讀帳器就是 `cmd_gov` 內的 `load(name, mapper)`(`scripts/lumos:8137`),它已把 bypass/governance/signoff/kill/canary/ci 多本帳逐本載入、合併、去重(`scripts/lumos:8158-8216`)。統計讀者只要再加一行 `load(<本機帳>, …)` 即可,不需要新工具。

引句:「統計類讀者(`lumos gov`、doctor 的 spec-gate 比例段、S18 度量、lint-new 自動放行計數)改用同一支「兩本一起讀」的小工具,依時間合併。」

## 問 2 命名與錯誤處理

severity: minor
blocking: 否

- 路徑常數:既有本機帳用「具名常數 + 一支取路徑函式」:`CI_LOG_NAME = ".ci-log.jsonl"`(`scripts/lumos:38432`)與 `_ci_log_path(env)`(`scripts/lumos:38526`)。計劃只寫了位置字串 `governance-local.jsonl`,沒定常數名與取路徑函式名,也沒對齊 `.xxx-log.jsonl` 的點開頭命名(帳檔一律 `.bypass-log` `.canary-log` `.ci-log`)。應命名成 `.xxx-log.jsonl` 風格。
- 寫不進去:計劃「兩條路各照現有行為」與現況一致——`_gate_event` 回 False(`scripts/lumos:1361-1362`)、呼叫端 `_gate_event_or_warn` 講 telemetry-write-failed(`scripts/lumos:1399-1401`)、`_append_governance_log` 靜默 `except OSError: pass`(`scripts/lumos:1431-1432`)。這點對齊。
- ⚠ 不一致:`.git/lumos/` 目錄不存在時要自己建;既有「家目錄下的本機目錄」建目錄一律走 `_mkdir_trusted_under_home` + `_trusted_private_dir`(`scripts/lumos:35191-35195`、`scripts/lumos:35677-35680`)。計劃沒說建目錄與權限(是否 `mkdir(parents=True)`、是否擋 symlink)怎麼處理;既有 `_ledger_append` 還用 `O_NOFOLLOW` 與滿寫驗證(`scripts/lumos:18517-18521`)。判不準本機帳要不要走這套,標 ⚠。
- ⚠ 退回語意:取不到共用資料夾就退回寫版控帳,是新增的語意;既有 `_append_governance_log` 取不到 HEAD 是「不寫」(`scripts/lumos:1423-1424`),`_gate_event` 沒 docs/ 回 None 不寫(`scripts/lumos:1334-1340`)。計劃自己在做法 6 承認並維持,算對齊,只是「退回」是新分支,測試 S5 已覆蓋。

引句:「寫不進去:兩條路各照現有行為,不新增語意——走 `_gate_event` 的回 False,呼叫端照舊講 telemetry-write-failed」

## 問 3 第二種做法

severity: major
blocking: 是

結論:是。`<git 共用資料夾>/lumos/governance-local.jsonl` 是專案裡第一個放在 `.git/` 底下的本機狀態檔,而專案已有三種既有位置,計劃的〈不選〉沒有逐一比較,只否決了其中一種(docs 下 .gitignore)。

專案既有的本機狀態位置:
1. `docs/` 下被 `.gitignore` 忽略的流水帳——**最直接的先例**:`docs/.ci-log.jsonl`,規則在根 `.gitignore:10`,檔名常數 `CI_LOG_NAME`(`scripts/lumos:38432`),路徑 `env.vault.parent / CI_LOG_NAME`(`scripts/lumos:38526`),且 `cmd_gov` 已「條件載入」它與其他帳合併(`scripts/lumos:8214-8220`)。這就是「一本進版控、一本本機、統計讀者兩本合併」的現成範式。
2. `governance/runtime/`,根 `.gitignore` 忽略(`.gitignore` 的 `governance/runtime/` 行);寫 `hook-events.jsonl`(`scripts/lumos:8015`、`scripts/lumos:19908`)。
3. `~/.cache/lumos/<子目錄>/`,每個使用者一份、可信目錄檢查:vault-lock(`scripts/lumos:17679`)、drift-defs(`scripts/lumos:35194`)、drift-m1 的 `ledger-miss.jsonl`(`scripts/lumos:35675-35680`,是「治理帳寫不進去時的留痕」,跟本案性質最像的快取區先例)、dispatch-lens(`scripts/lumos:40854`)、bound-filter(`scripts/lumos:42673`)。
4. 第二種(計劃新增):`.git/lumos/`。全檔搜 `git-common-dir` 零命中;最接近的只有 `rev-parse --git-dir` 當「是不是 git 專案」的判斷(`scripts/lumos:33372`、`scripts/lumos:36606`),沒有任何地方把狀態檔寫進 `.git/`。計劃 PRIOR-ART 引的是 git 本身和 pre-commit 的做法,沒引本專案內的先例。

計劃〈不選〉的理由是「本機帳放 docs/ 再用 .gitignore 忽略(本 repo 與舊消費專案都出過 .gitignore 寫錯位置,且要靠 lumos update 補規則才生效)」。對照:`docs/.ci-log.jsonl` 正是這個做法且在運作;`.gitignore` 位置風險計劃自己提過但沒舉本 repo 的出事紀錄,不能當否決依據。另外 `.git/lumos/` 要新增 `git rev-parse --git-common-dir` 呼叫與 worktree 語意,是新機制,而現行做法不需要。

建議:要嘛沿用 `docs/.xxx-log.jsonl` + `.gitignore`(最小改動,讀者靠 `cmd_gov` 的 `load` 加一行);要嘛把 `.git/lumos/` 位置正式寫成專案新慣例並說明為何前三種都不適合(例如消費專案不用補 `.gitignore` 的理由已有,但需註明這是新增第二種位置、並更新一處取路徑函式供全部本機狀態日後沿用)。現在這樣是隱性地開第二種位置。

「兩本一起讀」的小工具:已有可沿用的,就是 `cmd_gov` 內的 `load`(`scripts/lumos:8137`),見問 1。但注意它是 `cmd_gov` 的內部巢狀函式,doctor 的 spec-gate 比例段、S18、lint-new 計數各有自己的讀法;若要共用,應把 `load` 的讀檔核心(`_drift_jsonl_parse` `scripts/lumos:33549`、`_gov_event_types_ok` `scripts/lumos:8109`)抽成頂層函式,而不是另寫第二支讀帳器。

引句:「**本機帳的位置**:`<git 共用資料夾>/lumos/governance-local.jsonl`,共用資料夾用 `git rev-parse --git-common-dir` 取(worktree 共用同一份)。」

引句:「本機帳放 docs/ 再用 .gitignore 忽略(本 repo 與舊消費專案都出過 .gitignore 寫錯位置,且要靠 lumos update 補規則才生效)」

## 問 4 落點

severity: minor
blocking: 否

- `Systems/reversibility-governance-ledger` 約 15 KB、110 行,about_code 只列 `scripts/lumos` 與 `scripts/hooks/post-commit` 兩支(該節點 frontmatter),主題含「cmd_gov 唯讀彙整、六本帳來源、`_gate_event_fit`、gate 名單」。治理帳寫入與讀取本來就是這篇的責任(含 `cmd_gov`、`_KNOWN_GATES`、`.governance-log.jsonl` 寫者),分流屬同一條寫帳/讀帳線,**該寫進它,不必另開**。
- 小提醒:該篇摘要已是長串 KEY/WHY 行,新增分流表(約 25 種「閘名+種類」)若整張貼進摘要會讓它更肥;分流表唯一定義應留在程式常數,節點只寫 WHY 與限制,不複製表。
- ⚠ post-commit hook(bash)也在 about_code 內,若它會寫例行跳過帳,計劃〈盤點〉只列四支 Python 寫入器,沒說 bash 路徑(本次搜尋 `scripts/hooks` 未直接命中 `governance-log` 字串,判不準它是否經 `lumos` 子命令寫入),標 ⚠。

引句:「不拆版控帳本身(〈全repo審視〉#18 裁定不分檔,理由是四個整檔讀者,這裡不推翻」

## 彙總

不對齊共 4 條,其中 major 1 條
