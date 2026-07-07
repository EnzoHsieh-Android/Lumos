# Lumos 架構圖

> 「圖譜即合約」工具組的**唯一源 → 分發 → 消費端**模型。一張圖看懂:什麼東西住在哪、用哪個指令裝到哪、為什麼非這樣分不可。

## 1. 全景:唯一源 → 兩種 scope → 消費端

```mermaid
flowchart TB
    subgraph SRC["🟢 Lumos repo (唯一源 · 公開 EnzoHsieh-Android/Lumos · ~/harness/lumos-toolchain)"]
        direction TB
        CLI["scripts/lumos<br/>(python3 標準庫單檔 CLI)"]
        TEST["scripts/test_lumos.py"]
        GHOOKS["scripts/hooks/<br/>git: pre-commit / post-commit / pre-push"]
        CHOOKS["scripts/hooks/claude/<br/>PreToolUse (impact 注入) · PostToolUse (自足性/rot 後驗)"]
        INST["安裝器<br/>get.sh · get.ps1 · install.sh<br/>install-hooks.sh · install-graph-toolchain.sh · merge-claude-settings.py"]
        TPL["scripts/templates/graph-discipline.md<br/>(圖譜先行紀律範本)"]
        RENAME["scripts/graph-rename.sh · fetch-notesmd.sh<br/>(notesmd move 封印)"]
        SKILLS["skills/<br/>lumos-project-notes · core-knowledge<br/>design-loop · code-loop · pitfalls-gapfill"]
    end

    subgraph USER["① user-scope (每台機器一份)"]
        direction TB
        USKILL["~/.claude/skills/lumos-*<br/>(symlink → Lumos repo)"]
        UCHOOK["~/.claude/hooks/ + settings.json<br/>(L1/L3 + 註冊)"]
        UBIN["~/.local/bin/lumos<br/>(全域指令 symlink)"]
    end

    subgraph PROJ["② project-scope (每個專案 vendor 一份)"]
        direction TB
        PCLI["scripts/lumos (vendored copy)"]
        PHOOK["scripts/hooks/ + core.hooksPath"]
        PCLAUDE["CLAUDE.md<br/>(sentinel 注入紀律段)"]
        PGRAPH["docs/&lt;slug&gt;-knowledge/<br/>(圖譜資料 · 各專案自己的)"]
    end

    CONSUMER["消費端專案<br/>(你的專案 / MyApp 等)<br/>= vendored consumer"]

    SKILLS -. "install.sh (symlink)" .-> USKILL
    CHOOKS -. "install-hooks.sh --force" .-> UCHOOK
    CLI -. "lumos install" .-> UBIN

    CLI ==> |"install-graph-toolchain<br/>/ lumos update (vendor)"| PCLI
    GHOOKS ==> |vendor| PHOOK
    TPL ==> |"sentinel 注入"| PCLAUDE
    INST ==> |"scaffold (skip-if-exists)"| PGRAPH

    PCLI --- CONSUMER
    PHOOK --- CONSUMER
    PCLAUDE --- CONSUMER
    PGRAPH --- CONSUMER

    classDef src fill:#1b3a2a,stroke:#3ddc84,color:#e8fff0
    classDef user fill:#2a2440,stroke:#9a7bd6,color:#f0ecff
    classDef proj fill:#3a2a1b,stroke:#dcab3d,color:#fff5e0
    class SRC,CLI,TEST,GHOOKS,CHOOKS,INST,TPL,RENAME,SKILLS src
    class USER,USKILL,UCHOOK,UBIN user
    class PROJ,PCLI,PHOOK,PCLAUDE,PGRAPH,CONSUMER proj
```

**為什麼分兩種 scope**:CI 只 checkout 專案 repo(要能跑 `scripts/lumos doctor`)、git hook 是 per-repo —— 所以 CLI/hooks **必須 vendor 進各專案**。skills 是純方法論文件,user-scope symlink 共用一份就好,不必 vendor(否則各專案副本會漂移)。

## 2. 安裝 / 生命週期指令做了什麼

```mermaid
flowchart LR
    subgraph BOOT["bootstrap (一鍵上手)"]
        direction TB
        B1["clone Lumos<br/>(--pull: 既有也拉最新)"] --> B2["install.sh<br/>→ skills symlink"]
        B2 --> B3["lumos install<br/>→ 全域 lumos"]
        B3 --> B4["install-hooks.sh<br/>→ repo git hooks"]
        B4 --> B5["⟳ 重啟 session<br/>(L1/L3 載入)"]
    end

    subgraph UPD["lumos update (升級既有專案)"]
        direction TB
        U1["git pull Lumos 來源"] --> U2["re-vendor<br/>CLI/hooks/範本"]
        U2 --> U3["CLAUDE.md 紀律同步"]
        U3 --> U4["結尾 diff 自癒<br/>(逐檔比對補漏)"]
        U4 --> U5["⚠ git commit<br/>vendored copy"]
    end

    subgraph NEW["lumos init (導入新專案 · 底層 install-graph-toolchain)"]
        direction TB
        N1["vendor 工具組"] --> N2["scaffold 圖譜<br/>(skip-if-exists)"]
        N2 --> N3["注入 CLAUDE.md"]
        N3 --> N4["裝 git + Claude hooks"]
    end

    classDef boot fill:#1b3a2a,stroke:#3ddc84,color:#e8fff0
    classDef upd fill:#2a2440,stroke:#9a7bd6,color:#f0ecff
    classDef new fill:#3a2a1b,stroke:#dcab3d,color:#fff5e0
    class BOOT,B1,B2,B3,B4,B5 boot
    class UPD,U1,U2,U3,U4,U5 upd
    class NEW,N1,N2,N3,N4 new
```

## 3. CLI 子命令家族 (41 個頂層命令)

```mermaid
flowchart TB
    ROOT["lumos &lt;cmd&gt;<br/>(python3 標準庫 · 零依賴 · 41 個頂層命令)"]

    ROOT --> READ["讀取 / 導航 (11)"]
    ROOT --> HEALTH["巡檢 / 治理 (6)"]
    ROOT --> WRITE["寫入 (6)"]
    ROOT --> GUARD["合約守衛 (guard*)"]
    ROOT --> LOOP["對抗審計 loop (6)"]
    ROOT --> INTEG["完整性 / 影響 (2)"]
    ROOT --> SARIF["社群 linter 橋 (3)"]
    ROOT --> LIFE["安裝 / 生命週期 (6)"]

    READ --> R["context · contracts · search · links<br/>backlinks · map · export · decisions<br/>stale · recent · stats"]
    HEALTH --> H["doctor · lint · lint-watch<br/>self-audit · sync-verified-by · gov"]
    WRITE --> W["set · append · new · archive<br/>decision-add · decision-supersede"]
    GUARD --> G["guard {list · scaffold · bind · audit · trace}<br/>(★INVARIANT★→[test:]→[audit:] 綁定鏈)"]
    LOOP --> LP["pitfalls (--diff tier) · code-loop {pass/skip/check}<br/>canary {record} · loop {status}<br/>fold-check · refcheck"]
    INTEG --> I["anchor {verify · approve}<br/>impact (影響半徑 + 事故觸發)"]
    SARIF --> ST["sqlfluff-sarif · stylelint-sarif<br/>compose-metrics"]
    LIFE --> L["install · uninstall · update<br/>bootstrap · init · deinit"]

    classDef root fill:#1b3a2a,stroke:#3ddc84,color:#e8fff0
    classDef cat fill:#2a3142,stroke:#5a9bd6,color:#e0f0ff
    classDef leaf fill:#222,stroke:#666,color:#ddd
    class ROOT root
    class READ,HEALTH,WRITE,GUARD,LOOP,INTEG,SARIF,LIFE cat
    class R,H,W,G,LP,I,ST,L leaf
```

> `guard`/`anchor`/`canary`/`loop`/`code-loop` 各帶子命令(如 `anchor verify`);上面 41 是頂層命令數,權威清單以 `lumos --help` 為準。

## 4. 強制力管線 (圖譜不腐爛的機制)

由「動手前推播 → commit 把關 → push 硬閘 → CI」四段;訊號主動推到眼前(impact),硬閘擋在提交與推送點。

```mermaid
flowchart TB
    subgraph BEFORE["🟣 動手前 (Claude hooks · 推播,不擋)"]
        PRE["PreToolUse: impact-hook<br/>Edit/Write 前注入<br/>受影響關聯節點 + 命中事故 (pitfall_when)"]
        POSTT["PostToolUse<br/>自足性 / verification-rot 後驗"]
    end

    EDIT["改 code + 圖譜"] --> PC{"pre-commit (git)"}
    PC -->|"改 code 沒帶圖譜更新"| BLOCK["⛔ 擋下 (可 --no-verify · post-commit 留痕)"]
    PC -->|通過| COMMIT["commit"]

    COMMIT --> PUSH{"pre-push (git)"}
    PUSH -->|"① lumos doctor --ci"| PB1["⛔ 圖譜不健康"]
    PUSH -->|"② anchor verify"| PB2["⛔ 測試/閘檔動了沒核可"]
    PUSH -->|"③ code-loop check (tier=high)"| PB3["⛔ 未過 code-loop<br/>(pass/skip/--no-verify 三路)"]
    PUSH -->|全過| PASS["push"]
    PASS --> CI["CI: lumos doctor --ci<br/>+ ★INVARIANT★→[test:] 真跑"]

    classDef gate fill:#3a2020,stroke:#dc5b5b,color:#ffe8e8
    classDef ok fill:#1b3a2a,stroke:#3ddc84,color:#e8fff0
    classDef push fill:#2a2440,stroke:#9a7bd6,color:#f0ecff
    class PC,PUSH,BLOCK,PB1,PB2,PB3 gate
    class COMMIT,PASS,CI,EDIT ok
    class BEFORE,PRE,POSTT push
```

> **地板不是 oracle**:PreToolUse 是推播(可被無視)、git 閘可 `--no-verify` 繞(自負、留痕)。守得掉「忘了/隨手漏」,守不掉「刻意繞+不誠實」——那留給人。
