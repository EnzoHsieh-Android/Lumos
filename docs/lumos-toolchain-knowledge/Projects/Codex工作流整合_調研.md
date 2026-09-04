---
type: project
status: doing
created: 2026-09-04
updated: 2026-09-04
tags:
  - type/project
  - status/doing
  - scope/governance
related:
  - "[[Projects/派工鏡頭注入_計劃]]"
  - "[[Projects/主session鏡頭利用率_計劃]]"
  - "[[Projects/code階段強化_計劃]]"
  - "[[Systems/design-loop]]"
  - "[[Systems/heterogeneous-finder-ensemble]]"
summary: |-
  KEY:Lumos 目前只把 Codex 當外家審查員/辯方(codex exec 一問一答);帳上 codex 席名 9 種寫法共 62 筆,家族辨識因此失準
  KEY:★本機 Codex CLI 0.144.1 三個實驗證實★:hook 在 codex exec 下 fire(使用者層 -c 設定;PreToolUse additionalContext 哨兵被模型逐字抄回)、專案層 .codex/ hook 未信任不載入(--dangerously-bypass-hook-trust 不跳過專案層信任)、子代理在 exec 下可派(collab_tool_call/collaborationwait_agent;SubagentStart/Stop 帶 agent_id 與 agent_transcript_path)
  KEY:hook 事件表與 Claude Code 同構(10 事件;PreToolUse 可 deny/updatedInput/additionalContext;Stop block reason 變下一個 prompt);限制=只攔簡單 shell/MCP、prompt/agent 型 handler 不執行
  KEY:候選(未裁):①--output-schema 鎖外家席報告格式(今天收貨正規化踩三次) ②codex review 當第二種外家形態(輸出未測) ③Codex 側 dispatch-lens 薄殼(PreToolUse collaboration* 工具,tool_input 形狀待測) ④recount 多讀 Codex 逐字稿(格式未看) ⑤lumos install 多一個 ~/.codex 目標 ⑥席名統一;REVISIT:2026-09-18
---
# Codex工作流整合_調研

> 白話:Lumos 現在只把 Codex 當「另一家的審查員」用——每輪設計審一席外家否決、代碼審低共識條目派它當辯方,一律 `codex exec --sandbox read-only`,一問一答。2026-09-04 調研+三個本機實驗確認:本機 Codex CLI 0.144.1 ★有 hook(事件表與 Claude Code 幾乎同構、PreToolUse 能 additionalContext 也能 updatedInput)、有子代理(GA 2026-03,`~/.codex/agents/*.toml`)、兩者在 `codex exec` 非互動模式下都會動★。另有一個沒用過的 `codex review` 非互動代碼審子命令。

## Lumos 現在怎麼用 Codex(圖譜+腳本+帳面盤點)

- **設計審迴圈**:每輪一席「外家否決」(`lumos-design-loop/SKILL.md` 步驗 5、`templates.md` 辯方段;`codex exec --sandbox read-only "<prompt>" < /dev/null`,stdin 必重導否則掛住——session memory「檢索v1+外家席編制」08-23 裁外家一律 Codex,Gemini 只備援不算否決)。
- **代碼審迴圈**:低共識 ≥major 條目派 Codex 辯方(`lumos-code-loop/SKILL.md` 步驟 4、`reference.md:141/152`;2026-07-18 S5:雙 Codex 角色僅 code-loop)。
- **性質測試席**(code階段強化_計劃 S3/S5):性質合法性必過 Codex 辯方。
- **帳面**:canary-log 裡 codex 席名有 9 種寫法、共 62 筆(外家否決-codex 16、ext-codex 26、codex 8、codex-s5-finder 3、panel(...veto-codex) 3、其餘各 1–2)——席名沒統一,`loop status` 的家族辨識因此常印「看不出是哪一家」。
- **用法形態**:全部是「我出題、它一次答完」;沒有用它的 hook、子代理、MCP server、`review`、`--output-schema`。

## Codex CLI 0.144.1 能力(2026-09-04 本機驗證)

| 能力 | 狀態 | 證據 |
|---|---|---|
| hook | `codex features list`:`hooks stable true` | 事件:SessionStart/SubagentStart/PreToolUse/PermissionRequest/PostToolUse/PreCompact/PostCompact/UserPromptSubmit/SubagentStop/Stop;stdin 欄位含 session_id/transcript_path/cwd/tool_name/tool_input/tool_use_id/turn_id;PreToolUse 可回 `permissionDecision` allow/deny、`updatedInput`、`additionalContext`;Stop 的 block reason 變下一個 user prompt |
| hook 在 `codex exec` 下 fire | ★實驗 2 證實★ | 使用者層 `-c "hooks.PreToolUse=[...]"` + `--dangerously-bypass-hook-trust`:SessionStart 與 PreToolUse(Bash)各 1 筆,`additionalContext` 的哨兵字串被模型逐字抄回 |
| 專案層 hook | ★實驗 1:不 fire★ | `<repo>/.codex/config.toml` 的 hook 在專案層未被信任時不載入;`--dangerously-bypass-hook-trust` 只跳過 hook 定義信任,不跳過專案層信任(文件明寫;GitHub issue #17532 另記互動模式同症) |
| 子代理 | `multi_agent stable true`;內建 default/worker/explorer;自訂 `~/.codex/agents/*.toml`(name/description/developer_instructions,可帶 model/sandbox_mode/mcp_servers) | 只在明確要求時才派;`agents.max_concurrent_threads_per_session` 上限 |
| 子代理在 `codex exec` 下 | ★實驗 3 證實★ | 提示「派一個 explorer 子代理」→ `collab_tool_call`(工具名 collaborationwait_agent),SubagentStart(agent_type=default)/子代理自己的 PreToolUse(帶 agent_id)/SubagentStop(帶 agent_transcript_path)都 fire,結果回到父代理 |
| `codex review` | 非互動代碼審子命令,`--base <branch>`/`--commit <sha>`/`--uncommitted`,可帶自訂指示 | 未實測輸出格式 |
| `codex mcp-server` | 把 Codex 當 MCP 伺服器給別的 agent 呼叫 | 未實測 |
| `--output-schema <FILE>` | exec 回應可綁 JSON Schema | 未實測——對「席報告一定要有 severity/blocking 獨立行」這種收貨格式問題很對症 |
| hook 限制(文件) | 只攔簡單 shell 呼叫,不攔非 shell 非 MCP 工具;`async`/`prompt`/`agent` 型 handler 解析但不執行;多 hook 並行、順序不保證;timeout 預設 600 秒 | — |

## 對 Lumos 的意義(候選,未裁;都不是今天要做)

1. **席報告格式**:外家席報告的 severity/blocking 同行、引句改述,今天光是收貨正規化就踩了三次——`codex exec --output-schema` 可以在源頭鎖格式(schema=finding 陣列,每條 severity/blocking/quote/file 欄位)。這是成本最低、命中最準的一項。
2. **`codex review` 當第二種外家形態**:它自帶「對 base 的 diff 審」流程;可對照現行 exec+自訂 prompt 的席,看漏抓率——但輸出格式未知,先量。
3. **Codex 子代理側的鏡頭**:Claude 側的 `dispatch-lens-hook` 靪 PreToolUse(Agent)+updatedInput;Codex 側對應事件是 PreToolUse(collaboration* 工具)——★工具名與 tool_input 形狀要先實測(實驗 3 只看到工具名 collaborationwait_agent)★,可行的話同一支 lumos `dispatch-lens` 兩家共用,hook 各寫一支薄殼。
4. **利用率量測跨家**:Codex 的 transcript_path/agent_transcript_path 都有,recount 那支腳本理論上可以多讀一個來源——但 Codex 逐字稿格式(`~/.codex/sessions/`?)未看,先不承諾。
5. **專案層 hook 走不通**:要給 Codex 側裝 lumos hook,只能走使用者層(`~/.codex/hooks.json` 或 config.toml)——跟 Claude 側 `lumos install` 寫 `~/.claude/settings.json` 同形態,合併器要多一個目標。
6. **席名統一**:9 種寫法是自家帳的病,跟 Codex 無關;`loop status` 的家族辨識靠席名,順手修。

## CLAUDE.md / skills 在 Codex 的對應物(2026-09-04 補,官方文件+本機查)

| Claude Code 這邊 | Codex 那邊 | 差在哪 |
|---|---|---|
| `CLAUDE.md`(專案規矩,每 session 自動進 prompt) | `AGENTS.md`:全域 `~/.codex/AGENTS.md`(有 `AGENTS.override.md` 就只讀它),再從 git 根往 cwd 一層層找 `AGENTS.override.md` → `AGENTS.md` → `project_doc_fallback_filenames` 列的備名;全部**串接**(不是覆蓋),總量上限 `project_doc_max_bytes`(文件寫預設 32 KiB,超過就停止再加檔) | 本 repo 根目錄已有一份 `AGENTS.md`(8 行指路檔,叫 Codex 去讀 CLAUDE.md 與 MOC)。**Codex 不會自動讀 CLAUDE.md**——要它直讀得把 `CLAUDE.md` 加進 `project_doc_fallback_filenames`,但這只在「AGENTS.md 不存在」時才生效,所以現制(AGENTS.md 指路)是對的 |
| skills(`~/.claude/skills/<名>/SKILL.md`,描述觸發或 `/名` 顯式叫) | Codex skills:repo 層 `.agents/skills/` 或 `.codex/skills/`、使用者層 `~/.agents/skills/`、管理層 `/etc/codex/skills`;每個 `<名>/SKILL.md` 必填 `name`/`description`,選配 `scripts/`、`references/`、`assets/`、`agents/openai.yaml`(`policy.allow_implicit_invocation` 預設 true);顯式叫法 `$名`,隱式靠 description 比對;目錄清單佔 prompt 上限=context 的 2% 或 8k 字(`skills.max_context_tokens` 可調,硬上限 10000 tokens);`skills.config[].path/enabled` 可逐支開關 | **同一個開放標準(agentskills.io)**,SKILL.md 格式互通——理論上 `lumos-*` 四支 skill 直接 symlink 進 `~/.agents/skills/` 就能被 Codex 看到。★沒實測★:本機 `~/.codex/skills/` 只有 `cache` 子目錄、`~/.agents/skills/` 不存在、本 repo 沒有 `.agents/` `.codex/`,也就是**現在 Codex 席一支 lumos skill 都看不到**,它審設計時對 lumos 指令、合約標記、記帳規矩的認識全靠 prompt 裡塞的那段 |
| 子代理定義 `.claude/agents/*.md` | `~/.codex/agents/*.toml`(`developer_instructions`+model/sandbox/skills.config) | 見上節 |
| plugins(bundle skills+hooks) | `codex plugin add/list/marketplace/remove`;`features list` 顯示 `plugins` stable、`plugin_hooks` **已移除**(hooks 不能靠 plugin 帶,只能 config/hooks.json) | 沒細查 marketplace 內容 |
| 全局系統提示替換 | `model_instructions_file`(整份取代內建指令,不是加在 AGENTS.md 上)、`developer_instructions`(額外注入一段) | 沒測 |

候選 7(接上節,未裁):**把 `lumos-*` skills 安裝進 `~/.agents/skills/`**(install.sh 多一個 symlink 目標),讓 Codex 席審 lumos 相關設計時有同一本手冊;前提是先實測 Codex 真的載入、且 `$lumos-design-loop` 這種名字的隱式觸發不會亂咬。REVISIT 併入 2026-09-18 那條。

## 沒查/沒測的

- `codex review` 的輸出與 exit code;`--output-schema` 實際約束力;`mcp-server` 的工具面。
- Codex 子代理的 PreToolUse `tool_input` 形狀(要改寫派工詞就得知道)。
- Codex 逐字稿格式與存放位置。
- 互動模式下的 hook(GitHub issue #17532 說專案層 hook 有不 fire 的症狀;本案只測 exec)。

## 實驗留痕

暫存目錄 codexhook.*(hook.py 記 stdin 到 hook.log;三次 `codex exec --json` 的 out*.jsonl);未進版控,結論以上表為準。實驗 1 的失敗(0 筆)先被誤判成「hook 不會 fire」,換使用者層設定才對——★專案層信任這一刀是文件寫了、我沒先讀★。

**實驗 4/5(2026-09-04,scratchpad codexfull/;接本篇「沒查/沒測」第二條)**:未信任 repo 裡 `codex exec --sandbox workspace-write -c hooks.*` ——①AGENTS.md 哨兵字與 repo 層 `.agents/skills/` 哨兵字都回到最終回覆(兩者未信任也載入,skill 且被隱式選用)②PreToolUse 攔到 `apply_patch`,`tool_input={"command":"*** Begin Patch\n*** Add File: beta.txt…"}`,沒有 file_path ③攔到 `collaborationspawn_agent`,`tool_input={"task_name","fork_turns":"all","message":"gAAAA…"}`——message 是加密字串,回 updatedInput 改它子代理沒收到(哨兵沒出現)④`matcher="Agent"` 的 PreToolUse 沒攔到 spawn(0 筆)⑤SubagentStart 回 `additionalContext` 的哨兵字被子代理原文回報→這是 Codex 側餵子代理脈絡的可用通道。後續設計見 [[Projects/Codex完全支援_計劃]]。

REVISIT:2026-09-18 若要動候選 1–3 任一項,先補「沒查/沒測」四條裡對應那條,不憑本篇下手。
