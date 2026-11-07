severity: major

我只讀了 spec 和程式碼,沒有改 repo 裡任何檔,也沒有把規則命中的實作跑起來。

## F1 時間預算對不上:表態核對只有 20 秒,新增告警的單條保底卻要 30 秒,這一題永遠算不出來
severity: major
blocking: 是(預算寫死後這道閘等於沒開,屬可執行性缺口)

範圍 2 要求 `_kt_rule_hits(..., deadline)` 在逾時時丟 `_KtSitOverBudget`,並走 fail-open。但 spec 沒有說這個 deadline 是多久。

- 推送前的表態核對給的期限是 20 秒:`_DISP_BUDGET = 20.0`,用在 `_dispositions_verdict(... deadline=_time.monotonic() + _DISP_BUDGET ...)`。
- 範圍 2 要呼叫的 `_lint_new_run_cmds` 有單條保底:剩餘預算少於 `per_cmd_floor_sec`(預設 30)就不跑,直接記成 `undone budget`。
- 20 秒少於 30 秒,所以第一條命令就被判「預算不足」,規則命中永遠算不出來。
- 若改用 pitfalls 收集的 `_KT_SIT_BUDGET = 30.0`,抽快照和 git 讀檔又會先吃掉幾秒,同樣過不了保底。
- 若借用新增告警閘的 300 秒(`budget_sec`),表態核對的 20 秒又被繞過,而且一整套 ast-grep 會卡住推送五分鐘。
- 結果是照 spec 實作後,這一題每次都 fail-open,還每次寫一筆治理帳。

S10 的「時間預算剩 0 → fail-open」測得到,但沒有任何正常路徑能把命中算出來。spec 必須明寫這一題用哪個預算、與 `per_cmd_floor_sec` 的關係,以及快取沒寫成時的重算上限。

引句:「超過時間預算(含參數太長、命令沒跑完)丟 `_KtSitOverBudget` 同型的例外」

file: `scripts/lumos:72905` `_DISP_BUDGET = 20.0`
file: `scripts/lumos:41794` `"per_cmd_floor_sec": 30`
file: `scripts/lumos:42674` 剩餘預算低於保底就 `out["undone"].append({"kind": "budget"...})`

## F2 「參數太長」改成 fail-open,大改動可以靜默繞過這一題
severity: major
blocking: 是(spec 為「只跑一次」「有上限」開了一條繞道)

spec 把「參數太長」跟逾時併成 fail-open。程式碼對這件事的立場正相反:`_lint_new_run_cmds` 註解明寫「參數太長不是環境問題……判成跟預算沒跑到同類(擋),不歸自動放行」。

- 範本命令是 `ast-grep scan --config … --format sarif {LINT_FILES} > {LINT_SARIF_OUT}`,用的是舊 `{LINT_FILES}`。
- 舊佔位符不分批,只有 `{LINT_FILES_CSV}` 才會對半切。
- 整條命令用 `sh -c` 交給 shell,Linux 上單一參數上限約 128KB。千支檔級的改動(重命名、搬套件)會因此跑不出來。
- spec 自己承認改檔名會讓命中換身分,所以這種改動正好是命中最多、最需要交代的時候。
- 理由「沒算出命中時沒有東西可以叫作者交代」不成立:算不出來是環境限制,不代表沒有命中。
- 新增告警閘對同一支命令是擋下,同一次推送會出現「一般告警擋、覆核題放行」兩套相反的政策。

建議:`too-long` 照新增告警閘擋,或改成分批。若維持 fail-open,spec 要寫理由,並說明為何不分批。

引句:「這一題是表態題,照表態閘與情境題既有的逾時規則走 fail-open 並記帳」

file: `scripts/lumos:42678` `kind == "too-long"` 的註解與處理
file: `docs/lumos-toolchain-knowledge/Systems/linter精選目錄.md:195` 範本命令用 `{LINT_FILES}`

## F3 S10「工具沒裝 → 無法驗證、擋」做不出來,而且跟既有政策相反
severity: major
blocking: 是(spec 內部矛盾,又描述了做不到的區分)

範圍 2 要求「逾時 fail-open、工具沒裝或 git 失敗丟無法驗證」。

- `_lint_new_run_one` 只回 `env`、`too-long` 兩種失敗。`env` 是「工具沒裝/逾時/拉不到規則」一個桶,呼叫端分不出工具沒裝和逾時。
- 範圍 2 說「算不出來(工具沒裝、git 失敗)丟無法驗證」,要先改底層函式才做得出來,spec 沒寫。
- 既有政策是工具沒裝放行並記帳。linter精選目錄:「沒裝時新增告警閘判環境不可用、照既有規則放行並記帳」。表態閘對型錄檔找不到也是「環境不可用、不擋」。
- S10 寫成擋,同一台沒裝 ast-grep 的機器上,新增告警閘放行、這一題卻擋推送。
- 這跟 spec 自己說的「同一道閘的題目要同一個逾時政策」相衝突。

file: `scripts/lumos:42685` `fail` 只分 `env` 與 `too-long`
file: `docs/lumos-toolchain-knowledge/Systems/linter精選目錄.md:192` 沒裝時放行並記帳

## F4 快取鍵漏了影響結果的輸入,而且沒寫淘汰上限
severity: major
blocking: 是(漏鍵會讀到舊結果,沒上限會讓快取目錄一直長)

範圍 2 說快取鍵含「範圍、版本、規則包指紋」。對照 `_kt_sit_cache_key`,幾項缺失:

- **宣告命令本身**:命中題的命令來自 `.lumos/lint.json`。`_lint_load_config(repo_root)` 讀的是工作目錄版,不是 `at_sha` 版。同一個 sha,未提交改過 lint.json(換 `--config`、加旗標)會命中舊快取。
- **ast-grep 版本**:規則語法以 0.51.1 為準。換版本後同一份規則的命中集合可能不同,但鍵不變。
- **「規則包指紋」沒定義**:要涵蓋 `sgconfig-review.yml`、`sgconfig-hints.yml`、兩個 `rules-*` 目錄的所有規則檔。只算兩個 yml,改規則檔不會失效。
- **設定值**:`include_test_paths`、`max_file_lines`、`max_file_bytes` 與 `_vendored_skip` 會改變被掃的檔集合,也沒進鍵。
- **schema 常數**:情境段有 `_KT_SIT_CACHE_SCHEMA`,命中題沒有對應的常數,結果形狀改了無法失效。
- **淘汰與保鮮期**:情境段在寫入前呼叫 `_home_cache_evict(..., ttl, max_files=200)`。spec 沒說 `kt-rule-hits/` 要不要照做。

另外,算不出來(over_budget、無法驗證)時不寫快取,所以 pitfalls 收集、`code-loop check` 和推送前三個呼叫端會各重算一遍。F1 的情形會變成三倍耗時。

file: `scripts/lumos:39326` `_kt_sit_cache_key` 與 `_home_cache_evict(..., max_files=_KT_SIT_CACHE_MAX)`
file: `scripts/lumos:42628` `_lint_load_config(repo_root)` 讀工作目錄,不讀 `at_sha`

## F5 `_kt_rule_hits` 的內部描述與現有函式不符,漏掉兩道前置檢查
severity: major
blocking: 是(照字面實作會漏掉既有的防護)

範圍 2 說 `_kt_rule_hits` 「內部呼叫新增告警閘跑命令與比對新增的那一組函式(`_lint_new_run_cmds` 那一支,抽兩份快照、只回新增)」。實際上:

- `_lint_new_run_cmds` 只跑命令,回 `(base_claims, head_claims)`。
- 抽快照在 `_lint_new_tools`(`_lint_new_extract`、`_lint_new_support`,建 `.lumos/lintbase-*`),比差集在 `_lint_new_diff_claims`。
- 照字面實作要自己組出這三段,而 `_lint_new_tools` 同時負責 `_lint_new_oversize`(單檔 60000 行、5MB 上限)與 `_lint_new_sep_split`。
- 只拼 `run_cmds` 的話,超大檔(含已被放行、不檢查的)會被塞進 ast-grep,跳過單檔上限;`rmtree` 清理也要重寫一份。
- spec 沒寫快照要不要跟新增告警閘共用同一個暫存目錄。不共用就是同一次推送多抽兩份快照和多跑 ast-grep:每次推送最多 3 條命令 × 2 邊 = 6 次掃描,而不是現在的 2 次。
- 掃描次數可能超出預算(見 F1),spec 也沒說命令順序與誰先被預算截斷。
- 簽名沒有 `out`/`cfg`,spec 沒說 `undone` 的種類怎麼傳回(F2、F3 都靠它)。

file: `scripts/lumos:42664` `_lint_new_run_cmds`
file: `scripts/lumos:42596` 抽快照與大檔檢查在 `_lint_new_tools`

## F6 治理帳沒有大小上限,新欄位會讓每次檢查多讀更多
severity: minor
blocking: 否(目前帳已大,但 spec 只開了一個月後回頭看的 REVISIT,沒有數字門檻)

- 治理帳現況是 22MB、約 12.5 萬行,單行最長約 15KB。
- 答案的 `hits` 沒有筆數上限,每筆理由最多 500 字。每次重新表態,`--carry` 都把整份答案再追加一筆事件,所以大小是推送次數乘命中筆數乘每筆理由長度。
- 抽查事件帶 `rule_hits`,一份最多 30 筆也沒問題,但表態事件沒有對應上限。
- `_codeloop_gov_append` 只做 `open(..., "a")`,沒有上限檢查。
- 讀取端(`_kt_bj_read`、表態讀取、`gov --stats`)是整檔掃,帳越大,每次推送前檢查越慢。
- 建議在 spec 訂答案筆數上限(例如超過 N 筆要求分批或改答 `risk` 整批),REVISIT 寫成帳大小的量化門檻。

引句:「每筆答案理由與抽查理由進版控治理帳;REVISIT 看帳的大小。」

file: `scripts/lumos:73202` `_codeloop_gov_append` 無大小檢查

## F7 同一個身分出現多次時,答案對不上
severity: minor
blocking: 否

範圍 2 說「同檔同片段多處共用一個身分」,但 `_lint_new_diff_claims` 回的是逐筆的 `new` 清單,同一個 `key` 可出現多次。命中清單 `[{seg, rule, file, lines, message}]` 因此有重複的 `seg`。答案 `hits: [{seg, answer, ...}]` 以 seg 為鍵時,「每筆都要有答案」的檢查單位沒定義:一個 seg 答一次算幾筆?統計與「多答 N 筆」的算法也沒說。

file: `scripts/lumos:42256` 多次出現同一 key 都進 `new`

## F8 誤報樣本回流讓自檢的掃描次數隨樣本檔數增加
severity: minor
blocking: 否

`--fp-samples` 不覆寫同名檔,但沒有筆數上限。`samples/good/` 目前約 2.3MB 的規則包目錄,`--fp-regress` 與好例檢查逐規則逐檔掃描,每次最多 `SCAN_TIMEOUT` 120 秒。樣本越多越慢。spec 沒訂每條規則的樣本檔數上限或去重(兩個專案寫出同一段程式、不同 `seg`)。

file: `configs/ast-grep/kotlin-android/check.py:30` `SCAN_TIMEOUT = 120`

## 各節與引用核對
- 範圍 1、4、5、6、7、驗收條款、預期值表:已讀,除上面幾條外無 finding。
- `code-loop blind-judge --template --part` 已存在(`scripts/lumos:77659`、`77664`)。`--rule-hits`、`code-loop rule-hits --fp-samples`、`check.py --fp-regress` 是新增項,spec 標明了新增。
- `_KT_BJ_PART_MAX = 30` 與 spec 的「一份最多 30 筆」一致。
- `_kt_bj_event_ok` 對缺 `blind_judge`/`role` 的事件回 `False` 並略過,與 spec 的「照缺欄略過」一致。
- 材料的 ±8 行、5 處、40 行上限是有界的:最壞 30 筆 × 5 處 × 40 行約 6000 行,不是資源問題。

## 實務隱患
- **時間**:見 F1、F2、F4、F5。每次推送多跑 4 次 ast-grep(review 與 hints 各兩邊),預算和快取行為 spec 沒訂。
- **記憶體**:大檔上限靠 `_lint_new_oversize`,F5 說明若不呼叫就沒有。
- **檔案大小**:治理帳見 F6,樣本目錄見 F8。
- **子程序與暫存**:快照暫存是 `.lumos/lintbase-*`,由 `_lint_new_tools` 的 `finally` 清掉。新函式若自己抽快照,spec 沒寫要同樣用 `finally` 清、也沒寫強殺後交給 `_lint_new_clean_stale`。
- **快取一致性**:見 F4。

## 固定席逐條判
- `Systems/棧別提問表態閘`:**會影響**。其核對期限 `_DISP_BUDGET` 與 over_budget 規則被這份設計直接觸及,見 F1、F2、F3。情境題「型錄找不到不擋」的政策與 S10 的「工具沒裝擋」不一致。
- `Systems/pitfalls-code-loop`:**影響** `pitfalls` 的收集預算(30 秒)與 `code-loop check` 呼叫,見 F1 與 F4 的三個呼叫端各重算。
- `Systems/kotlin規則包`:**不影響合約**。兩份 `sgconfig-*.yml` 與 `check.py` 改的是註解與自檢模式,筆記說明該級「不擋」的句子隨本案更新即可。
- `Systems/linter精選目錄`:**不影響合約**,但範本那句「提示級規則預設不接」要照範圍 7 改,且 F2 提到範本用的是不分批的 `{LINT_FILES}`,值得在這篇一併註明限制。

總結:最高等級為 major,blocking 共 5 條。
