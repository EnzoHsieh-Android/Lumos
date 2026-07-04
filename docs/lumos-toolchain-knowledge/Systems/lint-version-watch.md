---
type: system
status: doing
created: 2026-07-04
updated: 2026-07-04
tags:
  - type/system
  - status/doing
related:
  - "[[pitfalls-lint-adapter]]"
  - "[[pitfalls-code-loop]]"
  - "[[pitfalls-lint-integration_計劃]]"
verified_by:
  - "[[Verification/2026-07-04_lint-version-watch]]"
summary: |-
  FLOW:讀 .lumos/lint-watch.json → 查各 registry 最新穩定版(pypi/npm/maven/github)→ _compare_versions 三態 → 落後進 candidates manifest → 治理層 dedup(seen-ledger)→ 新候選暫存 governance/lint-upgrades/ + LINE 通知 → 人放行 bump current
  KEY:核心定位——只做版本偵測、不自建規則 diff;新版本本身=信號、changelog 由人審(同第①塊「規則庫讓給社群」)
  KEY:機械核心在 scripts/lumos `lint-watch` 子命令(vault-free、dispatch 置於 find_vault 前);純數字 tuple 比較 + 等段數守衛(段數不一→skip,擋 calendar 2024.1 / 4段 Maven 假陽性)
  KEY:prerelease 一律不建議——_is_prerelease 涵蓋 SemVer `-` 與 PEP 440 dashless(a/b/rc/dev);過濾在 _registry_latest 內、回 (None, reason)
  KEY:Maven latest 取數值 tuple max(嚴禁字串 max——'3.9'>'3.20.0' 字串誤判)+ q 值 urllib.parse.quote(%22,字面雙引號 Solr 回 400)+ sort=timestamp+desc + docs 在 data["response"]["docs"]
  KEY:_registry_latest 回 (latest, reason) 二元組(單一 None 承載不了 網路失敗/prerelease/無穩定版 三因);_compare_versions 回 (state, reason) 三態(bool 承載不了 failed 分流)
  KEY:HTTP 抓取層 fixture seam——LUMOS_LINT_WATCH_FIXTURE 環境變數指 {url:response} 檔則不打網路(subprocess 測試可注入);fail-open(網路失敗 → failed[],永不升 rc)
  KEY:治理層所有 JSON 讀寫在 python(lint_watch_dedup.py __main__:pending 寫入 + seen append + LINE dict stdout);shell(lint-watch-check.sh)零 JSON 解析/組裝、只把 $MSG 當不透明字串傳;lumos 用 python3 $REPO/scripts/lumos(cron-safe)
  KEY:rc——成功(含缺/空清單)=0;清單格式壞=2;網路失敗永不升 rc
  DEP:[[pitfalls-lint-adapter]]
  DEP:[[pitfalls-code-loop]]
  TEST:test_lumos.py 443 passed(t_lint_watch_semver/registry/cli)+ test_autonomous_loop.py 53 passed(TestLintWatchDedup 6)
  VERIFY:[[Verification/2026-07-04_lint-version-watch]]
  DECISION:[2026-07-04]只做版本偵測不做 per-tool 規則 diff(valid);[2026-07-04]新宣告檔 .lumos/lint-watch.json(lint.json 指令不透明抽不出工具身分)(valid);[2026-07-04]操作型候選不走 design-spec orchestrator、獨立輕量放行路徑(valid)
---
# lint-version-watch

pitfalls-lint-integration 計劃第②塊。每日排程機械偵測「宣告的社群 linter 有沒有新穩定版」(查 registry vs `.lumos/lint-watch.json` 鎖定版)→ 落後產「該升級 X」候選 → 輕量放行紀律(暫存 + LINE 通知 + 人放行)。**只做版本偵測、不自建規則差異比對**。

## 組件(spec 逐行權威 `docs/design/2026-07-04-lint-version-watch.md`)
- **機械核心**(`scripts/lumos` `lint-watch`):`_semver_parse`(純數字點分、剝 v)/`_is_prerelease`(SemVer `-` + PEP 440 dashless,前綴分隔符必需免 `cobra` 假陽性)/`_compare_versions -> (state, reason)` 三態/`_http_get_json`(fixture seam)/`_registry_latest -> (latest, reason)` 四型抽取。
- **治理層**:`governance/autonomous_loop/lint_watch_dedup.py`(`new_candidates` 純函式 + `__main__` 收 pending/seen/LINE dict 側效)+ `governance/lint-watch-check.sh`(掛 `daily-governance.sh` 第3步、fail-open、shell 零 JSON)。

## 天花板 / 誠實邊界
- 只驗「有沒有新版」,不驗「該不該升」(相容性/破壞性由人審 changelog);不做 per-tool 規則 diff。
- 版本比較純數字 tuple + 等段數守衛:current 須與 registry 同版本方案、同精度宣告(靠人維護,清單漂移會漏報)。
- registry 端點語意依賴上游(pypi info.version / github /latest 排除 prerelease 行為);上游改語意會失準(記 valid_under)。

## design-loop 判定(誠實)
6 輪 canary 6/6 全 caught,抓修真缺陷(Maven `%22`+字串 max 病灶、PEP440 prerelease、三態、等段數守衛、fixture seam、shell↔python JSON 側效)。**未拿 GATE PASS**:核心機械設計 r4-r6 連 3 輪判乾淨=收斂,churn 全在治理 shell wrapper 散文;判定核心 design-approved、shell 於實作階段真 shell 測試定稿(Task 5 真檔端到端 smoke 通過)。

## 相關
- 計劃:[[pitfalls-lint-integration_計劃]](第②塊落地;③④ 塊待做)。
- 地基:[[pitfalls-lint-adapter]](第①塊,吃 SARIF;本塊補「linter 該升級了」的維護面)。
