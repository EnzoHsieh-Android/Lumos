---
type: project
status: done
created: 2026-10-12
updated: 2026-10-12
aliases:
  - 後端 MCP 調研
  - MCP 能力矩陣
tags:
  - type/project
  - status/done
  - scope/stack-knowledge
related:
  - "[[Projects/後端工程提問與證據擴充_計劃]]"
summary: |-
  FACT:PostgreSQL 兩個熱門 MCP 的唯讀模式都已被公開繞過——已封存的官方參考實作可用分號夾 COMMIT 跳出唯讀交易(修正未發版),Postgres MCP Pro 的 restricted 模式可用 pg_read_file 讀伺服器檔案(CVE-2026-85620,≤0.3.0 未修) [來源:外部] [confirmed:2026-10-12] [recheck:30天] [查:Datadog Security Labs 2025-08-21、vulncheck 公告、crystaldba/postgres-mcp issue 178]
  RULE:任何資料庫類 MCP 一律連「資料庫層只有讀權限」的帳號,不靠 MCP 自己的唯讀開關 [依據:外部] [since:2026-10-12] [retire:人裁] [until:2027-04-12] [confirmed:2026-10-12]
  FACT:Redis 官方 mcp-redis 沒有唯讀旗標與工具白名單,唯讀只能靠 Redis ACL(-@write);Confluent mcp-confluent 能連一般 Apache Kafka,有 --allow-tools 白名單,預設回傳使用數據(DO_NOT_TRACK=true 關) [來源:外部] [confirmed:2026-10-12] [recheck:30天]
  FACT:Grafana 官方有 mcp-k6(本機可跑、不需 Grafana Cloud、自稱實驗階段、run_script 會真的壓測、6 個工具全部自標具破壞性、授權 AGPL-3.0)與 mcp-grafana(--disable-write 唯讀、可透過 Prometheus 資料源下 PromQL);Prometheus 沒有官方 MCP [來源:外部] [confirmed:2026-10-12] [recheck:30天]
---
# 後端MCP能力矩陣_調研

> 白話:[[Projects/後端工程提問與證據擴充_計劃]] 第 2 階段的產出。任務書列了一串候選 MCP(資料庫、快取、訊息、壓測、監控、GitHub、Docker),這篇逐一查證:誰在維護、還活不活、實際有哪些工具、怎麼限制只讀、能不能在本機示範用、有沒有更簡單的替代。
>
> **查證範圍**:2026-10-12 由三個代理分頭網搜,每項說法附實際打開過的網址;工具清單從 README 或原始碼抄,不從部落格抄;查不到的標「未驗」。同日稍晚在本機實裝了 PostgreSQL(Toolbox)、k6、Grafana 三個並核對工具清單與唯讀防線,見〈實裝核對〉;其餘候選只到文件層。

REVISIT:2026-10-26 第 4 階段在本機裝好 Docker 後,把下面「建議採用」的每個 MCP 實際裝起來、用 Claude Code 列出真實工具清單,跟本篇的清單逐一比對,不一致的改本篇並記差異 [closed:2026-10-12 已實裝 PostgreSQL(Toolbox)、k6、Grafana 三個並核對,見〈實裝核對〉;Redis、Kafka、MongoDB 沒裝,要用時另照〈實裝核對〉的做法補]

## 結論

- **第一個真實 MCP:PostgreSQL 用 Google 的 MCP Toolbox for Databases**,連一個只有讀權限的資料庫帳號。實裝後確認它的命令列沒有「只載入某一組工具」與唯讀旗標,29 個工具會全部載入(見〈實裝核對〉),唯讀完全靠帳號。
  - 理由:大廠官方、維護活躍(2026-10-08 剛發版)、直接連本機 Docker 的 Postgres、工具清單可從原始碼確認、沒有在唯讀上出包的紀錄。
  - 次選:Bytebase 的 DBHub(Claude Code 官方文件拿它當範例,但唯讀要寫設定檔,實作方式未驗)。
- **示範的最小組合**:PostgreSQL(Toolbox)+ k6(mcp-k6)+ Grafana(mcp-grafana,唯讀)。Redis、Kafka 要等示範流程判斷需要才加;加了就用官方版並收窄權限。
- **不接的**:Prometheus MCP(mcp-grafana 已能查)、Docker MCP Toolkit(示範用不到它的容器隔離,多一層設定)、GitHub MCP(示範只看 CI 的話 `gh` 指令更簡單)。
- **最重要的一條**:不信任 MCP 的唯讀開關,唯讀一律做在被連的系統那一層(資料庫帳號只給讀權限、Redis ACL 拿掉寫入、Grafana 服務帳號只給查詢)。

## 能力矩陣

判定欄:已確認=文件與原始碼層面查到且可用;要設定=可用但要先做權限或設定;不支援=不適合本機示範或已停止維護;未驗=查不到。四格都是「文件層」,實裝驗證見開頭的 REVISIT。

### 資料庫

| 候選 | 維護者與狀態 | 最新版本 | 唯讀怎麼做 | 本機示範 | 判定 |
|---|---|---|---|---|---|
| 舊官方參考實作 server-postgres | 官方,2025-05-29 已封存 | v0.6.2(不再更新) | 號稱唯讀交易,可被分號夾 COMMIT 繞過,修正沒發版 | 不適合 | 不支援 |
| Postgres MCP Pro(crystaldba) | 社群,仍活躍 | PyPI 0.3.0(2025-05-16) | `--access-mode=restricted`,但預設可寫,且 restricted 可讀伺服器檔案(CVE-2026-85620 未修) | 功能最強但有未修漏洞 | 要設定(有未修 CVE) |
| MCP Toolbox for Databases(Google) | 官方,活躍 | v1.14.0(2026-10-08) | 沒有唯讀旗標(未驗);可只載入 `postgres/data` 一組;唯讀靠資料庫帳號 | 適合 | 要設定 |
| DBHub(Bytebase) | 廠商,活躍 | v1.5.0(2026-10-09) | 設定檔 `[[tools]]` 裡寫 readonly;擋法是關鍵字還是資料庫層未驗 | 適合 | 要設定 |
| AWS Labs postgres | AWS Labs | 目錄最後提交 2026-09-22 | 預設唯讀 | 只寫支援 Aurora/RDS | 不支援(本機) |
| Supabase MCP | 官方 | 未驗 | URL 參數 read_only | 只接 Supabase 自家專案 | 不支援(本機) |
| Neon MCP | — | 未驗 | 未驗 | 未驗 | 未驗 |
| MongoDB 官方 mongodb-mcp-server | 官方,活躍 | v3.0.5(2026-10-01) | `--readOnly`、`--disabledTools`;查詢結果預設包提示注入警告 | 適合(關掉 Atlas 類工具) | 要設定 |

- Toolbox 的 postgres 預設設定有 29 個工具(例如 `execute_sql`、`list_tables`、`get_query_plan`、`list_locks`);文件寫五組,實裝時日誌印六組(多一個 default)。`execute_sql` 照常能寫,所以唯讀只能靠帳號。
- 舊參考實作只有一個 `query` 工具;Postgres MCP Pro 有 `execute_sql`、`explain_query`、`analyze_db_health` 等 9 個。
- 不裝 MCP 的替代:`docker exec … psql -c`、`mongosh --eval`;零依賴,但沒有工具層保護,唯讀一樣靠帳號。

### 快取與訊息

| 候選 | 維護者與狀態 | 最新版本 | 讀寫刪分級與限制 | 本機示範 | 判定 |
|---|---|---|---|---|---|
| Redis 官方 mcp-redis | 官方,活躍(最後提交 2026-10-09) | 0.5.1(2026-08-05) | 53 個工具,含 `delete`、`set`、`rename`、`expire` 等寫刪;沒有 FLUSH 類;沒有唯讀旗標或白名單,唯讀靠 ACL;只支援 stdio | 適合 | 要設定 |
| 舊官方參考實作 server-redis | 已封存,npm 標示不再支援 | 2025.4.25 | 4 個工具,沒有唯讀開關 | 不建議 | 不支援 |
| Confluent mcp-confluent | 官方 repo,社群支援,活躍 | v1.6.0(2026-09-23) | 本機可用 11 個(含 `delete-topics`、`produce-message`、`create-topics`);`--allow-tools` / `--block-tools` 白名單;能連一般 Apache Kafka;預設回傳使用數據 | 適合 | 要設定 |
| tuannvm/kafka-mcp-server | 社群,近一年沒新提交 | v2.0.2(2025-11-29) | 9 個工具,只有 `produce_message` 會寫,天生不能建刪 topic | 可當備案 | 已確認 |

- 替代:`docker exec … redis-cli`;Kafka 自帶的 topics、console-consumer、consumer-groups 指令或 `kcat`。

### 壓測、監控、開發與基礎設施

| 候選 | 維護者與狀態 | 最新版本 | 唯讀與限制 | 本機示範 | 判定 |
|---|---|---|---|---|---|
| grafana/mcp-k6 | Grafana 官方,自稱實驗階段 | v0.7.0(2026-10-05) | 工具 `validate_script`、`run_script`(真的壓測,單次上限 5 分鐘)、`list_sections`、`get_documentation`;無唯讀旗標;v0.7.0 修了一個任意讀檔的 CVE;v0.7.0 容器映像沒推上去 | 適合,本機可跑、不需 Grafana Cloud | 已確認(Docker 版要設定) |
| grafana/mcp-grafana | Grafana 官方,活躍 | v2.0.2(2026-10-07) | `--disable-write` 唯讀、`--enabled-tools` 白名單;有 `query_prometheus`、`query_loki_logs`、`search_dashboards` 等;需要 Grafana 服務帳號 token | 適合 | 要設定 |
| Prometheus MCP | 沒有官方版;社群 pab1it0 版 v1.6.2(2026-08-03) | — | 工具全是查詢類,README 沒明寫唯讀 | 不必另接 | 不支援(官方不存在) |
| github/github-mcp-server | GitHub 官方 | v2.0.2(2026-10-08) | `--read-only`、`--toolsets`;遠端版網址加 `/readonly` | 可用但非必要 | 已確認 |
| Docker MCP Toolkit / mcp-gateway | Docker 官方 | v0.44.1(2026-09-23) | 沒有統一唯讀開關,看各伺服器;Docker Desktop 版本需求兩份官方文件說法不同(4.59 或 4.62 以上) | 示範可跳過 | 要設定(選用) |

- 替代:`k6 run` 加 `curl` 打 Prometheus 的查詢介面;`gh run view`。

## 權限設定說明

這節回答計劃 B 塊要的「權限說明」。

- **資料庫**:建一個示範專用的唯讀角色,只授予查詢權限,不能是 superuser,也不能有讀伺服器檔案的角色(`pg_read_server_files`)。MCP 的連線字串只用這個帳號。
- **Redis**:用 ACL 建唯讀使用者(拿掉寫入類指令),連線網址帶這個使用者。
- **Kafka**:mcp-confluent 用 `--allow-tools` 只開列出、消費、看消費群組與延遲的工具;要示範發訊息時才另外加 `produce-message`;設定 `DO_NOT_TRACK=true`。
- **Grafana**:mcp-grafana 加 `--disable-write`;服務帳號只給 Viewer 或查詢資料源的權限;設定 `DO_NOT_TRACK=1` 關掉匿名統計。
- **k6**:`run_script` 會真的壓測——只讓它打本機,壓測腳本開頭檢查目標不是 localhost 就中止。
- **Claude Code 這一側**:寫入、刪除、執行類的 MCP 工具(例如 `execute_sql`、`delete-topics`、`run_script`、Redis 的 `delete`)在 Claude Code 的權限設定裡設成每次詢問;唯讀工具才放進允許清單。
- **Codex 這一側**:Codex 的 MCP 工具核准設定本次沒查(未驗)。

REVISIT:2026-11-12 查 Codex 對 MCP 工具的核准設定怎麼寫(設定檔位置、能不能逐工具設詢問),補進上面「Codex 這一側」

## 實裝核對(2026-10-12)

- **做法**:在本機 Docker 起一個測試用 PostgreSQL 17(另建只有查詢權限的帳號)與 Grafana;用一支照 MCP 協定握手的小程式(初始化、宣告已初始化、列工具,必要時呼叫工具)直接跟每個 MCP 伺服器對話,不經過、也不改 Claude Code 的設定。原始輸出存在 governance/eval/mcp-lab-2026-10-12/(工具清單 JSON、呼叫紀錄、測試環境設定;密碼已換成佔位字)。握手小程式是一次性的,沒有提交。
- **PostgreSQL / MCP Toolbox 1.14.0**(npx 執行 `@toolbox-sdk/server`):回報 29 個工具,與文件一致。
  - 命令列沒有「只載入某一組」也沒有唯讀旗標(`--help` 全列過);啟動時預設上網查新版,`--disable-version-check` 可關;HTTP 模式預設允許任何來源與主機(啟動日誌自己警告),走 stdio 不受影響。
  - 用唯讀帳號實際呼叫 `execute_sql`:查詢成功;改庫存被資料庫以「沒有權限」拒絕;「分號夾 COMMIT 再刪表」被擋(它一次只收一條指令);讀伺服器檔案被拒(帳號沒有那個權限)。事後用管理員帳號確認資料原封不動。
- **k6 / mcp-k6 0.7.0**(GitHub 發布的 Apple 晶片執行檔,雜湊與官方核對過;Homebrew 版要從原始碼編譯,本機命令列工具太舊而放棄):回報 6 個工具——文件列的 `validate_script`、`run_script`、`list_sections`、`get_documentation` 之外,還有 `info` 與 `search_terraform`。
  - 6 個工具全部自我標示為「具破壞性、非唯讀」,連查文件的也是,所以不能靠標示判斷哪些安全。
  - 授權檔是 AGPL-3.0(README 寫的 MIT 不對)。
- **Grafana / mcp-grafana 2.0.2**(uvx 執行;服務帳號只給 Viewer):預設 79 個工具,`--disable-write` 後 62 個。
  - 唯讀模式下仍留著通用的 `grafana_api_request`,它的參數只允許 GET;實際送 POST,伺服器端回「唯讀模式只允許 GET」,真的有擋。
  - 不開唯讀、但服務帳號只有 Viewer 時,呼叫 `create_folder` 被 Grafana 以 403 擋下。兩層各自擋得住。
- **註冊到 Claude Code**:這次沒做。核對清單不需要它;測試容器用完就拆了。第 4 階段在示範 repo 的專案設定裡註冊(不含密碼,密碼從環境變數讀)。

## 未驗與疑點

- Redis、Kafka、MongoDB 三類沒有實裝。
- DBHub 的唯讀是關鍵字檢查還是資料庫層唯讀交易。
- mcp-grafana 的告警與註記工具名稱沒逐一列;它沒有官方的 `claude mcp add` 範例。
- Redis 官方版的 `claude mcp add` 寫法 README 沒寫;它的 Python 版本需求 README 與 PyPI 說法不一致。
- mcp-confluent 的 `get-partition-offsets` 能不能用在本機連線。
- Docker MCP 型錄裡有沒有 Grafana 與 k6。

## 來源

- 資料庫:modelcontextprotocol/servers-archived 的 postgres 目錄;Datadog Security Labs〈MCP vulnerability case study: SQL injection in the PostgreSQL MCP server〉;crystaldba/postgres-mcp(README、server 原始碼、issue 178)、PyPI postgres-mcp、vulncheck 公告〈postgres-mcp-pro 0.3.0 restricted mode bypass via FROM clause function〉;googleapis/mcp-toolbox(releases、postgres 預設工具設定檔);bytebase/dbhub(releases、toml 設定文件);awslabs/mcp 的 postgres-mcp-server;supabase-community/supabase-mcp;mongodb-js/mongodb-mcp-server(README、releases、安全公告);Claude Code 官方 MCP 文件(code.claude.com/docs/en/mcp)。
- 快取與訊息:redis/mcp-redis(README、main 與各工具原始碼、releases)、PyPI redis-mcp-server;servers-archived 的 redis 目錄與 npm 頁;confluentinc/mcp-confluent(README、工具名稱原始碼、configuring-claude-code 文件、releases、npm);tuannvm/kafka-mcp-server(README、工具原始碼、releases);OSV 漏洞資料庫查詢(四個套件皆無紀錄)。
- 壓測監控:grafana/mcp-k6(README、releases、v0.7.0 版本說明);grafana/mcp-grafana(README、releases);github/github-mcp-server(README、Claude 安裝指南、遠端伺服器文件、releases);docker/mcp-gateway(README、releases)與 Docker 官方 MCP Toolkit 文件;pab1it0/prometheus-mcp-server(README、releases)。
- 各代理原始報告的完整網址清單留在本次會談紀錄,未另存卷證。
