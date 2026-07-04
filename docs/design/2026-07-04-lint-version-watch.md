# lint-version-watch 設計(pitfalls-lint-integration 第②塊)

> 計劃節點:[[Projects/pitfalls-lint-integration_計劃]] 第②塊「每日 linter 版本/新規則偵測」。地基=第①塊 lint-adapter(已 merge)。

## 目標(一句)

每日排程機械偵測「專案宣告的社群 linter 有沒有新的穩定版」→ 落後即產「該升級 X」候選 → 走輕量放行紀律(暫存 + LINE 通知 + 人放行),**只做版本偵測、不自建規則差異比對**。

## 動機 / 定位

第①塊讓 pitfalls 吃社群 linter(SARIF),但 linter 會出新版、新版常帶新規則(= 新的偏科坑覆蓋)。專案鎖定版一旦落後,就吃不到新規則、也可能有已修的誤報。第②塊補這個「維護面」:機械盯 registry 最新穩定版 vs 專案鎖定版,落後就提醒人升級。

**核心認知**:版本偵測是**機械任務**(registry JSON API → semver 比較),符合本專案「機械 > LLM」「composition over invention」哲學。**「新規則」不自己逐工具比對**——那要 per-tool 解 changelog/rule-registry,高工、易腐化(正是第①塊「規則庫讓給社群」的教訓)。新版本**本身就是信號**:候選叫人去審該版 changelog。做「新版偵測」,不做「新規則 diff」。

## 為什麼需要新宣告檔(不能重用 lint.json)

第①塊的 `.lumos/lint.json` 是 `{副檔名: [含 {LINT_SARIF_OUT} 的 shell 指令]}`——指令是**不透明字串**(可能是 detekt jar 路徑、`npx eslint`、`dotnet build`)。**無法可靠從任意 shell 指令抽出「工具身分 + 鎖定版 + 該查哪個 registry」**。所以第②塊需要一份**顯式 watch 清單**,把「查什麼」講清楚(宣告是專案責任,同 lint.json 哲學)。

## 架構

兩層,沿本專案既有分工(機械核心在 `scripts/lumos`、排程/通知在 `governance/`):

1. **機械核心**:`scripts/lumos` 新增 `lint-watch` 子命令(vault-free、可測、rc 語意,同 `refcheck`/`pitfalls`)。讀 watch 清單 → 查各 registry 最新穩定版 → semver 比較 → 落後者輸出候選 manifest(`--json`)。HTTP 抓取層可注入(測試用 fixture,不打真網路)。
2. **治理排程層**:`governance/lint-watch-check.sh` 掛進 `daily-governance.sh` wrapper 第 3 步(單一喚醒窗)。跑 `lumos lint-watch` → 對新候選(seen-ledger 去重,每個新版只通知一次)LINE 通知 + 暫存到 `governance/lint-upgrades/`。人放行。去重比對本體在可測的 python helper(見〈治理排程層〉),shell 只做接線。

### 為什麼不走既有 backlog→orchestrator→design-loop 管線

升級候選是**操作型**(「把 detekt 1.23.7 → 1.24.0」),不是**設計 gap**。既有自主 loop 管線(`gap_select`→orchestrator→design-loop)是拿來 brainstorm **設計 spec** 的——對「bump 版本」用錯工具(不需要 design-loop、不需要 spec)。第②塊**重用「放行紀律」的形狀**(暫存 + 人放行 + LINE),**不重用 design-spec orchestrator**。獨立輕量路徑。

## 產出物清單(本 spec 建立)

- `scripts/lumos` 新增 `lint-watch` 子命令 + helper(`_semver_parse`/`_is_prerelease`/`_semver_behind`/`_registry_latest`/`_http_get_json`)。
- `governance/lint-watch-check.sh`(治理排程 shell,掛 wrapper 第 3 步)。
- `governance/autonomous_loop/lint_watch_dedup.py`(seen-ledger 去重 helper,可單元測)。
- `governance/lint-upgrades/`(暫存目錄:`pending-<DATE>.json` + `seen.jsonl`)。
- 測試:`scripts/test_lumos.py`(機械核心)+ `governance/autonomous_loop` 既有 test harness(去重 helper)。

## 資料契約

### 宣告檔 `.lumos/lint-watch.json`(專案根,選配;缺 = 無 watch)

```json
[
  {"name": "detekt", "registry": "github:detekt/detekt", "current": "1.23.7"},
  {"name": "eslint", "registry": "npm:eslint",            "current": "8.57.0"},
  {"name": "ruff",   "registry": "pypi:ruff",             "current": "0.4.2"},
  {"name": "sonar",  "registry": "maven:org.sonarsource.scanner.cli:sonar-scanner-cli", "current": "5.0.2.4997"}
]
```

- `name`:人可讀識別(通知/候選顯示用)。
- `registry`:`<type>:<coord>`。type ∈ `{pypi, npm, maven, github}`:
  - `pypi:<pkg>` → `GET https://pypi.org/pypi/<pkg>/json` → `info.version`。**注意 `info.version` 可能是 PEP 440 prerelease**(如 dev/nightly 通道無穩定版時),見〈prerelease 處理〉。
  - `npm:<pkg>` → `GET https://registry.npmjs.org/<pkg>/latest` → `version`(latest dist-tag = 最新穩定)。
  - `maven:<group>:<artifact>` → 查 Solr,**q 參數值必須 `urllib.parse.quote`**(雙引號→`%22`):`https://search.maven.org/solrsearch/select?q=` + `quote('g:"<group>" AND a:"<artifact>"')` + `&core=gav&rows=20&wt=json` → `response.docs[].v` 清單、我方過濾 prerelease 後取最大。**未編碼的字面 `"` 會被 Solr 回 HTTP 400**(r1 辯方實測坐實)。
  - `github:<owner>/<repo>` → `GET https://api.github.com/repos/<owner>/<repo>/releases/latest` → `tag_name`(GitHub `/latest` 已排除 prerelease/draft;剝前綴 `v`)。
- `current`:專案目前鎖定版。**必須與該 registry 的版本格式同方案、同精度**(段數一致——見〈semver 比較〉的等段數守衛);人放行升級後手動 bump 此欄。

### 候選 manifest(`lumos lint-watch --json` stdout)

```json
{
  "candidates": [
    {"name":"detekt","registry":"github:detekt/detekt","current":"1.23.7","latest":"1.24.0"}
  ],
  "checked": 3,
  "failed": [{"name":"sonar","reason":"registry query failed: timeout"}]
}
```

- `candidates`:僅列落後條(latest 可解析、與 current 等段數、且嚴格大於 current)。**不含 `behind` 欄**(candidates 恆為落後條,布林恆真無資訊)。
- `checked`:**成功查到 latest 並完成比較的條數**(不含 failed)。上例 4 條宣告、1 條 failed → checked=3。
- `failed`:查詢/解析失敗、或等段數守衛擋下(current/latest 段數不一致、prerelease、非數字段)的條目 `{name, reason}`。fail-open,不列入候選、不升 rc。

### 暫存 + 去重(治理層)

- 候選暫存:`governance/lint-upgrades/pending-<YYYY-MM-DD>.json`(當日新候選快照)。
- 去重 ledger:`governance/lint-upgrades/seen.jsonl`,一行一個已通知過的升級 `{"name":..,"latest":..,"seen":"YYYY-MM-DD"}`。**通知只對 `(name, latest)` 未在 seen 的候選發**(每個新版只通知一次,不每天洗版)。
- **seen 寫入時機**:候選一旦暫存即寫 seen(**不論 LINE 是否成功**)——通知是 best-effort,seen 記的是「已處置過此升級」,避免缺 token 時每天重打。缺點是缺 token 那次人收不到 LINE,但 `pending-<DATE>.json` 仍留檔可查(接受:token 缺是設定問題,pending 檔是兜底)。
- 人放行 = ① 把 `.lumos/lint-watch.json` 的 `current` bump 到 latest(並實際更新 lint.json 對應指令的版本)② 候選自然不再落後。seen 保留(冪等)。

## 機械核心細節(`scripts/lumos lint-watch`)

### CLI 接線(沿既有 subcommand 慣例,同 refcheck)

- `sub.add_parser("lint-watch")`;`--repo`(dest=`lint_watch_repo`,預設 `.`);`--json`(store_true)。無位置參數——清單固定讀 `<repo>/.lumos/lint-watch.json`。
- dispatch:`if args.cmd == "lint-watch": ...`。非 `--json` 時印人可讀摘要(每候選一行 `<name> <current> → <latest>`),`--json` 時印上述 manifest。

### semver 解析與比較

- `_semver_parse(v) -> tuple|None`:剝前綴 `v`;取 release 段(見下 prerelease 切法);split `.`;各段 int;任一段非純數字 → None(不猜)。回 `(n, ...)`。
- `_is_prerelease(v) -> bool`:涵蓋兩種慣例——① 含 `-`(SemVer prerelease,如 `1.24.0-RC1`);② PEP 440 dashless 後綴,release 段後接 `a`/`b`/`c`/`rc`/`alpha`/`beta`/`dev`/`pre` + 數字(如 `0.5.0b1`、`2.22.0.dev20260702`)。正則:`re.search(r'(?:[-.]|\d)(a|b|c|rc|alpha|beta|dev|pre)\d', v_lower)` 或含 `-`。**r1 辯方坐實 `'-' in '0.5.0b1'` 為 False**,故單靠 `-` 會漏 PEP 440 prerelease。
- `_semver_behind(current, latest) -> bool`:
  - 任一 `_is_prerelease` 為真 → False(prerelease 不建議、不比較)。
  - 兩者 `_semver_parse` 有一失敗(None)→ False(不猜)。
  - **等段數守衛**:兩 tuple 長度不同 → False(段數/精度不一致=方案不明,不猜)。此一守衛同時擋掉:calendar `2024.1`(2 段)vs semver `1.23.7`(3 段)的假陽性(r1 辯方坐實 `(2024,1)>(1,23,7)` 為 True 的假陽性),與 Maven 3 段 current vs 4 段 registry(`5.0.1` vs `5.0.1.3006`)的假陽性。
  - 皆通過且 `latest_tuple > current_tuple` → True。
- 被守衛擋下(prerelease / parse 失敗 / 段數不一)的條目 → 進 `failed[]` 記 reason(非 candidate、非靜默丟)。

### prerelease 處理(依 registry)

- pypi:`info.version` 若 `_is_prerelease` → 該條 failed(reason `latest is prerelease`);不改抓其他版(pypi json 的 `releases` 全量過濾成本高、YAGNI,dev/nightly 通道非本工具目標)。
- npm/github:`/latest` 端點本就排除 prerelease;若仍拿到 prerelease(異常)→ 同 pypi 進 failed。
- maven:`docs[].v` 我方過濾掉 `_is_prerelease` 者後取最大;過濾後空 → failed(reason `no stable version`)。

### HTTP 抓取層(可注入,測試不打網路)

- `_http_get_json(url) -> dict|None`:`urllib.request`(timeout 10s、`User-Agent: lumos-lint-watch`);非 2xx / 例外 / 非 JSON → None(fail-open)。
- `_registry_latest(registry, fetch=_http_get_json) -> str|None`:依 type 組 URL、呼 `fetch`、抽對應欄位、過濾 prerelease、回版本字串或 None。
- **測試 seam(端到端可測的具體機制)**:環境變數 `LUMOS_LINT_WATCH_FIXTURE=<json 檔路徑>` 存在時,`_http_get_json` **不打網路**,改讀該 fixture 檔(內容 = `{url: response_dict}` 映射,依 url 回對應假 response;無對應 key → None)。production 無此環境變數即走真 `urllib`。此 seam 讓 `test_lumos.py` 以 subprocess 跑真 CLI + fixture 驗完整 `--json` 管線(subprocess 無法注入 python 函式,故用環境變數 + 檔案)。

### rc 語意

- 全部查完(含部分 failed)= 0;`.lumos/lint-watch.json` 缺 = 0(無 watch、輸出空 candidates,非錯)。
- 清單存在但**格式壞**(非 JSON list / 條目非 dict / 缺 `name`/`registry`/`current` 必填欄)= 2。
- **網路失敗永不升 rc**(fail-open)。

## 治理排程層(`governance/lint-watch-check.sh` + `lint_watch_dedup.py`)

- 掛進 `governance/daily-governance.sh` 第 3 步(在報告、autonomous-loop 之後;wrapper `set -uo pipefail` 無 `-e`,本步失敗不影響前兩步)。
- 對 repo 根跑 `lumos lint-watch --repo <root> --json`。
- **去重 helper** `lint_watch_dedup.py`:`new_candidates(candidates, seen_path) -> list`——讀 `seen.jsonl`、回 `(name, latest)` 不在 seen 的候選。純函式、可單元測(給定候選 + seen → 新候選集)。
- 有新候選 → ① 寫 `governance/lint-upgrades/pending-<TODAY>.json`(僅新候選)② 對新候選寫入 `seen.jsonl`(不論通知結果)③ LINE 通知:訊息文字由 shell/dedup helper 組(**不重用 `line_notify.build_message`——那是 spec-放行 專用文案、領域不符**;重用的是 `line_notify.send(message, token)` 這個泛用 curl broadcast),格式:`🔧 lint 升級候選(<N>):\n<name> <current>→<latest>(<type>)\n...`(批次一則、列全部新候選);token 讀 `~/.config/ai-daily/line_token`,缺 → log 跳過。
- 無新候選 → 靜默(不通知、不寫檔)。
- 本步任何失敗只 log、rc 不外傳(wrapper 不 `-e`)。

## 實務隱患

- **併發**:daily wrapper 單一喚醒窗序列跑,無並發;seen.jsonl 單寫者(本步),無競爭。
- **冪等**:seen-ledger 保證每個 `(name,latest)` 只通知一次;重跑同日不重複通知(pending-<TODAY> 覆寫、seen 去重)。
- **資源**:HTTP timeout 10s、每 registry 一次呼叫、watch 清單通常個位數條 → 無熱路徑、無大資料。urllib response 讀完即釋放。
- **外部依賴**:registry API 可用性 = 外部;fail-open 確保單一 registry 掛不影響其他條與 wrapper。
- **rate limit**:GitHub 未認證 API 有速率限(60/hr/IP);watch 清單個位數 + 每日一次 → 遠低於限。

## 錯誤處理

- registry 單條失敗 → `failed[]`、跳過、續查其他(fail-open)。
- watch 清單缺 → rc 0 空候選(常態:沒宣告就沒事)。
- watch 清單格式壞 → rc 2(宣告錯要人修)。
- LINE token 缺 / broadcast 失敗 → log 跳過,不阻斷;pending 檔仍留。
- 網路整體不通 → 全部 failed、0 候選、rc 0、wrapper 續跑。

## 測試策略

機械核心(`scripts/test_lumos.py`,注入 fixture、不打網路):
1. `_semver_parse`/`_semver_behind`:`1.23.7` vs `1.24.0`→behind;反向→not;相等→not;`v1.2.3` 前綴剝除;非 semver 段(亂字串)→ parse None → behind False;**等段數守衛**:`2024.1`(2 段)vs `1.23.7`(3 段)→ not behind(進 failed);`5.0.1`(3 段)vs `5.0.1.3006`(4 段)→ not behind(進 failed)。
2. `_is_prerelease`:`1.24.0-RC1`→True;`0.5.0b1`→True(PEP 440 dashless);`2.22.0.dev20260702`→True;`1.24.0`→False。latest prerelease → 不進候選(failed)。
3. `_registry_latest` 四型:fixture 餵各 registry JSON 形狀(pypi info.version / npm version / maven docs[].v 過濾取最大 / github tag_name 剝 v)→ 正確抽出;maven prerelease 過濾;抓取回 None(例外/欄位缺)→ 該條 failed。
4. `lint-watch --json` 端到端(subprocess 跑真 CLI + `LUMOS_LINT_WATCH_FIXTURE` + git fixture + `.lumos/lint-watch.json`):落後條進 candidates、失敗/守衛擋條進 failed、checked 計數 = 成功比較條數。
5. rc:缺清單→0 空候選;壞清單(非 list / 缺必填欄)→2;全條 fixture-fail→rc 0(fail-open)。

治理層:`lint_watch_dedup.new_candidates` 單元測(候選 + seen → 新候選集,含空 seen/全已見/部分新三例);LINE `send` 重用既有、不重測;shell 接線以 `lumos lint-watch --json` 契約為準。

## 知識同步影響

| 受影響文件 | 需同步什麼 |
|---|---|
| `skills/lumos-project-notes/SKILL.md` | 指令表補 `lint-watch`(vault-free 版本偵測、rc 語意、`.lumos/lint-watch.json` 宣告) |
| `docs/methodology/圖譜即合約.md` | pitfalls 列補「版本偵測(lint-watch)——機械盯 registry 新穩定版」 |
| `Projects/pitfalls-lint-integration_計劃` | 第②塊 status → done + verified_by 回指落地 Verification |
| `governance/daily-governance.sh` 頭註 | 補第 3 步 lint-watch-check |

## 天花板 / 誠實邊界

1. **只驗「有沒有新版」,不驗「新版好不好 / 該不該升」**——升級決策(相容性、破壞性變更)是人的事,候選只搬信號到人眼前。
2. **不做 per-tool 新規則 diff**——新版是信號,changelog 由人審。
3. **registry 端點語意依賴上游**(pypi info.version / github /latest 排除 prerelease 的行為);上游改語意本偵測會失準——記進 valid_under。
4. **watch 清單靠人維護**(bump current);清單漂移(實際升了沒 bump)會漏報,同 lint.json「宣告是專案責任」的既有限制。
5. **版本比較是純數字 tuple + 等段數守衛**:current 必須與 registry 同版本方案、同段數宣告;段數不一致 / prerelease / 非數字段 → 進 failed 不猜(不會假陽性,但也不會跨方案比較)。calendar/hash 等非 semver 方案不支援。

## 審計修正紀錄(design-loop)

### R1(2026-07-04,canary type a=壞章節交叉引用(指向不存在的錯誤碼對照表節),sonnet,**CAUGHT**,辯方裁決後 severity=blocker,存活 findings=11)

canary 被正確識別(dangling pointer,全文無此節)。此輪 sonnet 紮實挖出真缺口,辯方(opus)對 3 條經驗性 ≥major 全實測**維持**(refute 不能):
- **B-2 blocker(折)**:Maven Solr URL 字面 `"` urllib 送出回 HTTP 400(辯方實測 `%22` 編碼才 200)→〈registry 端點〉改 `urllib.parse.quote` 編碼 q 值。
- **M-2 major(折)**:PyPI `info.version` 可為 PEP 440 prerelease(dev/nightly),`-` filter 漏抓(辯方實測 `'-' in '0.5.0b1'`=False)→ 新增 `_is_prerelease` 涵蓋 dashless PEP 440 後綴。
- **M-4 major(折)**:calendar `2024.1` 解析成全 int tuple、`(2024,1)>(1,23,7)`=True 假陽性,與天花板5 矛盾(辯方實測)→ 加**等段數守衛**(段數不一 → failed),一併解 m-2 的 4 段 Maven 假陽性;天花板5 改為誠實描述。
- **M-1 major(折)**:`checked` 定義(成功條數)與範例值(4,含 1 failed)矛盾 → 範例改 3、定義明確化。
- **M-3 major(折)**:LINE 通知訊息格式未定義、`build_message` 領域不符 → 明定批次訊息格式 + 只重用 `send()`。
- **M-5 major(折)**:端到端 fake-fetch 注入機制「環境或測試 hook」未定義(subprocess 無法注入 python)→ 明定 `LUMOS_LINT_WATCH_FIXTURE` 環境變數 + fixture 檔 seam。
- **m-1(折)**:seen 寫入 vs 通知失敗時序未定 → 明定「暫存即寫 seen,不論 LINE 結果」。
- **m-3(折)**:`lint-watch` argparse 接線未定 → 補 CLI 接線節。
- **m-4(折)**:去重 python 位置未定 → 明定 `lint_watch_dedup.py` helper + 進產出物清單。
- **m-5(折)**:`behind:true` 恆真冗餘 → 從 candidate schema 移除。
- **m-2(折,併入 M-4)**:4 段 Maven vs 3 段 current 假陽性 → 等段數守衛涵蓋。
存活 11 條全折入。
