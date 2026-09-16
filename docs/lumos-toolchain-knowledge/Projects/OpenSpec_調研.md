---
type: project
status: doing
created: 2026-09-10
updated: 2026-09-10
aliases:
  - OpenSpec
  - 外部對照-OpenSpec
  - spec-driven development 對照
  - opsx
related:
  - "[[Projects/先問世界_存量掃描裁定]]"
  - "[[Systems/外部對照-code衍生wiki]]"
  - "[[Projects/Codex外審吸收_計劃]]"
  - "[[Projects/條款綁測試算進度_計劃]]"
  - "[[Projects/條款認領追溯_計劃]]"
  - "[[Systems/節點還原]]"
  - "[[Systems/design-loop]]"
  - "[[Systems/pitfalls-code-loop]]"
  - "[[Projects/執行DAG_調研]]"
  - "[[Projects/工具分類_計劃]]"
tags:
  - type/project
  - status/doing
  - scope/node-content
  - scope/guards-gates
summary: |-
  FLAG:ORIGIN
  KEY:調研對象=Fission-AI/OpenSpec(2026-09-10 讀 docs+原始碼+社群證言;67.8k★、MIT、TypeScript、v1.13.0 於 2026-09-09 出、週更):給 30+ 家 AI 編程助手用的「先寫 spec 再寫 code」薄層——openspec/specs/ 是「系統現在行為」的真相源,每件工作是一個 changes/<名>/ 資料夾(proposal/design/tasks/delta specs),歸檔時 delta 合併進主 spec
  KEY:★兩者答的不是同一題★——OpenSpec 答「寫 code 之前,人跟 AI 先在紙上對齊要做什麼」(事前對齊層);lumos 答「為什麼這樣設計、邊界在哪、哪些不能改、驗證過沒」(決策當下的第一手脈絡+合約+驗證+閘)。重疊區只有「變更單位」那一塊:change 資料夾≈計劃節點,delta spec 的 Requirement+Scenario≈[SN] 條款,design.md 的 Decisions≈決策四欄,tasks.md 勾選框≈T1..Tn
  KEY:★最深的一刀=強制力模型★——OpenSpec 自陳「Everything below is convention, not enforcement」「OpenSpec only checks that artifacts exist, so enforce the gate with your own CI or hook」:validate 只讀 markdown(原始碼證實 import 零 src/ 路徑)、verify 是 174 行 prompt 叫 AI 用關鍵字搜 code 寫建議報告(輸出無程式讀、不擋 archive)、init 不裝任何 git hook、artifact「做完」=檔案存在;lumos 的 16 層防護(pre-commit 擋「改 code 沒動圖譜」、pre-push 擋錨點不符/doctor 紅/高風險未過代碼審、合約→[test:]→[audit:]→[kill:] 鏈、22 道 doctor 檢查)全部在打同一個敵人=漂移
  KEY:★社群最大宗抱怨正是漂移,而官方解法是收費的★——HN alasano(用五個月以上、在 OpenSpec 上蓋商業 orchestrator 的人,2026-05):"keeps drifting and drifting until you have duplication and contradictions across specs";作者 2025-10 自承 drift "has to be manual unfortunately";#880「拿 code 對主 spec 驗」2026-03 掛到現在 future-roadmap;2026-08-28 出 OpenSpec Cloud Agent(付費,PR 時雲端 LLM 對 spec、引出不一致的行)。lumos 的 impact --diff + --sync-check + Stop hook 做同一件事:本機、機械、免費、擋得住 commit
  KEY:GitHub issues 的失效型態跟 lumos 記過的同款——archive「validate 說 OK、回 0、東西沒改」一週四張(#1799/1801/1803/1805,2026-09-06)=假綠;verify「42 [x]·17 [~] 回報 ✓ Complete」(#1761)、「skip checks when evidence unavailable then report All checks passed」(PR #1732)=席位通知宣稱沒發生的事;--no-validate 一繞關掉全部守衛(#1697)=--no-verify 全跳;團隊用半年後換掉的理由「spec never saves the user's original intent … never keeps the conversation」=provenance
  KEY:社群自己長出了 lumos 那層——第三方 schema anvil:「test-plan maps every spec scenario to a named test」+「fresh-context, read-only reviewer (a second model) emits a VERDICT: line」;OpenSpec 核心回應「enforce the gate with your own CI or hook」;HN 上重度使用者都把 OpenSpec 當前段(產 context+任務清單)、後段自己接 ralph loop
  KEY:規模與背景(2026-09-10)——Fission AI=YC W26、創辦人 Tabish Bidiwale 單人全職;repo 2025-08-05 建、v1.0.0 2026-01-26;星數 27k(03-06)→56k(06-26)→67.8k(09-10)已走平(09-05 那週 +0);TS 45,075 行、3,194 測試案例、10 個 runtime 依賴;Thoughtworks Radar Vol.34 Assess
  KEY:真相語意相反——OpenSpec 的 specs 是「描述性紀錄」:code 跟 spec 不一致時,文件教你「往真的那一邊改」、歸檔時 spec 跟著 code 走;lumos 圖譜是「意圖權威」:行為事實跟圖譜衝突不自動判誰對、立事故筆記(Codex 外審 2026-07-29 修正過的認識論)
  KEY:OpenSpec 真優勢(誠實記)——①事前對齊的儀式便宜且有效(「改一段 proposal 免費,改 400 行 code 不是」)②delta 讓 brownfield 不用先文件化整個系統(跟 lumos 節點還原的惰性生長同宗)③schema 可自訂 artifact 圖(lumos 的 skill 是散文)④分發:npm、30+ 家工具、每週出版、36 篇自食 spec+83 個歸檔 change⑤explore 模式與 onboard 教學⑥stores「No sync, ever — by design」的跨 repo 指針哲學跟 core_refs 同宗
  KEY:lumos 領先處(機械數,2026-09-10)——決策時效(289 條決策/20 條翻案、181 篇驗證 174 篇帶前提與重驗條件、144 行 REVISIT)、合約鏈(登記簿 35 條合約+9 條技術債、綁測試 36 行)、動手前注入(PreToolUse hook 把合約/事故推到眼前;OpenSpec 要 agent 自己敲 CLI)、code diff 反推波及節點(impact --diff;OpenSpec 沒有)、對抗式多席審查迴圈、[SN] 條款不綁 [test:] 不得過處置閘(39/172 篇計劃已用)
  KEY:回看 2026-07-07 的兩條裁定——借的「AC-n 編號驗收+核銷」已演化成 [SN]+[test:]+處置閘第五步,比 OpenSpec 的「每條 requirement 至少一個 scenario」強一階(綁到真測試、閘會擋);跳的「delta-spec=第二真相源」被社群漂移證言印證,但真因不是兩份真相、是「沒有東西逼 spec 跟現實」(OpenSpec 自己 docs 原話:"nothing forces them to track reality")
  KEY:★本篇只到調研,可借候選列出不裁★;待 Enzo 裁完才開 _計劃
  PRIOR-ART:①最小解層級=本篇是 PRIOR-ART 留痕,不動任何機制;②世界解過=OpenSpec/Spec Kit/Kiro 三家 SDD 都在「事前對齊」層,沒有一家做「決策時效+合約閘」;③零依賴家規下不採用(npm/Node ≥20.19),只借形狀
  DEP:[[Projects/先問世界_存量掃描裁定]]｜[[Systems/外部對照-code衍生wiki]]｜[[Projects/條款綁測試算進度_計劃]]｜卷證 governance/review-reports/openspec-research-2026-09-10/(兩份乾淨 agent 回報全文)
---
# OpenSpec_調研

> 白話:OpenSpec 是現在最紅的「先寫規格、再讓 AI 寫 code」工具(六萬八千顆星)。Enzo 要我查它到底做什麼、跟 lumos 差在哪。查完的一句話:**它管的是「動手前先講好要做什麼」,lumos 管的是「做完之後為什麼這樣、哪裡不能動、驗過沒」——兩個工具站在一件工作的前後兩端,真正重疊的只有「一件工作怎麼打包」那一小塊。而最深的差別不在功能表,在它刻意不擋任何事、lumos 幾乎每一層都在擋。**

PRIOR-ART:①最小解在哪一層——本篇是 PRIOR-ART 留痕,不動任何機制,只給日後「要不要借 OpenSpec 的某個形狀」一個查得到的答案。②世界解過沒——spec-driven development 三家(OpenSpec / GitHub Spec Kit / AWS Kiro)都站在「事前對齊」層;圖譜 2026-07-07 的存量掃描已掃過一遍(那時 OpenSpec 只佔一行),本篇把它單獨攤開。③借用／自建／採用——零依賴家規下不採用(它要 Node ≥20.19 + npm);候選只借形狀,列在最後一節,不在本篇裁。

## 這篇在調研什麼、圖譜之前記過什麼

- **緣起**:Enzo 2026-09-10 點名「調研 OpenSpec、分析跟 lumos 的區別」,後追加「深度調研」。
- **圖譜之前碰過三次,都沒攤開**:
  - [[Projects/先問世界_存量掃描裁定]](2026-07-07):OpenSpec 佔一行——借了「計劃節點 AC-n 編號驗收+核銷檢查」,跳了「delta-spec 格式(第二真相源禁忌)」。
  - [[Systems/外部對照-code衍生wiki]](2026-07-16):一句「OpenSpec 生成一次都偏(使用者洞見)」——Enzo 親手用過,觀察到 AI 一次生成的 spec 就會偏離。
  - [[Projects/Codex外審吸收_計劃]](2026-07-29):外審拿 ADR / Spec Kit / OpenSpec 當對照,結論「整合與治理生命週期是真差異,基礎方法論非發明」。
- **本篇的做法**:讀官方 docs 25 頁、clone 原始碼逐機制讀(validate / archive / verify / 有沒有 hook)、收社群一手證言,再對 lumos 逐維度機械數。

## OpenSpec 是什麼(2026-09-10 讀 docs 與原始碼)

### 一句話定位與規模

- **自述**:「A lightweight layer that gets you and your AI coding assistant to agree on what to build, in writing, before any code is written.」
- **四原則**(README):fluid not rigid / iterative not waterfall / easy not complex / brownfield-first。
- **規模**(GitHub 頁面 2026-09-10 讀到):67.8k 星、4.7k fork、MIT、TypeScript、Node ≥20.19、npm 安裝;最新 v1.13.0 是 2026-09-09 出的,從 v1.5.0(06-28)到 v1.13.0 十週出了九個小版,幾乎週更。
- **自食**:它自己的 repo 用 OpenSpec 管自己,「openspec/specs/」 底下 36 個 capability(cli-validate、opsx-verify-skill、context-injection、rules-injection、schema-resolution…)、83 個歸檔 change。(網頁抓到的「47」是錯的,clone 下來 `ls | wc -l` 是 36。)
- **程式規模**(clone 於 commit 9d4e597,2026-09-09):TypeScript 45,075 行、測試案例 3,194 個、runtime 依賴 10 個(commander / zod / yaml / fast-glob / diff / chalk / ora / inquirer 兩個 / cross-spawn)。

### 資料模型:specs 是現況真相、changes 是進行中的工作包

- **「openspec/specs/<capability>/spec.md」**:「the single agreed-upon answer to what does this software do?」——按 capability(如 「auth/」、「payments/」)分資料夾,內容是 Requirement + Scenario。
- **「openspec/changes/<名>/」**:一件工作的完整包,含四種 artifact:
  - `proposal.md`:Why / What Changes(**BREAKING** 標記)/ Capabilities(哪些 spec 會新增或改)/ Impact。
  - 「specs/**/spec.md」:**delta spec**——只寫 `## ADDED / MODIFIED / REMOVED / RENAMED Requirements`,不重抄整份。
  - `design.md`:Context / Goals-Non-Goals / **Decisions(要寫 why X over Y、alternatives considered)** / Risks / Migration / Open Questions。
  - `tasks.md`:`- [ ] X.Y 任務(含怎麼驗證完成)` 勾選框,apply 階段解析勾選框追進度。
  - 選填 `.openspec.yaml`:schema、`skip_specs: true`(純重構不動行為時免 delta)、`retire_capabilities: true`。
- **歸檔(archive)**:delta 合併進主 spec,資料夾搬到 「changes/archive/YYYY-MM-DD-<名>/」,全部 artifact 留著當史料。「Each archive merges its deltas, building up a comprehensive specification over time.」
- **sync**:不歸檔、只把 delta 合進主 spec(長跑的 change 中途用)。

### delta spec 的寫法規則(這是它最硬的一塊)

- 每條 `### Requirement: <名>` 用 SHALL/MUST(RFC 2119),「One statement, one SHALL/MUST」。
- 每條 requirement **至少一個** `#### Scenario: <名>`,WHEN/THEN 格式;「Scenarios MUST use exactly 4 hashtags. Using 3 hashtags or bullets will fail silently.」
- MODIFIED 必須貼**整條** requirement(含所有還活著的 scenario),「Using MODIFIED with partial content loses detail at archive time」。
- REMOVED 必須附 **Reason** 與 **Migration**。
- 新 capability 要 `## Purpose`(≥50 字,`--strict` 才唸)。
- 零 delta 的 change 要明寫 `skip_specs: true`,否則 validate 擋;「Do not invent a requirement just to satisfy validation.」
- 「Quick test: if the implementation can change without changing externally visible behavior, it likely does not belong in the spec.」——spec 只寫可觀察行為,class 名、library、步驟都不准進 spec。

### 工作流:artifact 圖,依賴是「解鎖」不是「關卡」

- **schema.yaml** 定義 artifact 圖:proposal(根)→ specs、design(各需 proposal)→ tasks(需 specs+design);apply 需 tasks。使用者可 fork schema 自訂 artifact 與依賴、改每個 artifact 的指令模板。
- **設計理由**(docs/opsx.md):舊版「指令埋在 TypeScript 裡改不了、一次生成全部無法逐個測」;新版把結構外部化。「Dependencies are enablers — they show what's possible, not what's required next.」「Actions, not phases — create, implement, update, archive — do any of them anytime.」
- **指令**(在 AI 助手的對話裡打,不是終端機):
  - core 檔:`/opsx:explore`(不留痕的思考夥伴)、`/opsx:propose`(一次生四種 artifact)、`/opsx:apply`、`/opsx:update`、`/opsx:archive`。
  - expanded 檔另加:`/opsx:new`、`/opsx:continue`(照依賴圖一次生一個)、`/opsx:ff`、`/opsx:verify`、`/opsx:sync`、`/opsx:bulk-archive`、`/opsx:onboard`(掃 repo 挑一個小改動帶你走一輪)。
  - 終端機 CLI:`init / update / config / validate / list / show(--diff) / status(--all) / archive / schema / store / instructions / feedback`。
- **給 agent 的機器介面**(docs/agent-contract.md):`instructions <artifact> --json`、`status --json`、`show --json`;`context` 與 `operationGuidance` 兩個欄位「read from the selected root on every invocation」——**agent 要自己敲 CLI 拿脈絡,沒有任何在改檔前自動塞脈絡的 hook**。

### 三個「驗」到底驗什麼

- **`openspec validate`**:查 markdown 結構——requirement 有沒有 scenario、有沒有 SHALL/MUST、MODIFIED 有沒有漏 scenario、零 delta 有沒有 skip_specs、`--strict` 把 warning 升 error。**不讀 code。**(原始碼逐條規則見下節「原始碼複核」)
- **`/opsx:verify`**:叫 AI「reads your artifacts and your code and tells you where they diverge」,從完整性 / 正確性 / 一致性三面出 CRITICAL / WARNING / SUGGESTION;docs 說「Treat its output as a to-do list for reconciliation」。**是建議報告,不是閘**;選用。
- **人的兩分鐘審**(docs/reviewing-changes.md):propose 之後、apply 之前,人讀 proposal → specs → tasks,七條清單(「Every requirement has a scenario that actually exercises it」「I'd be comfortable if the AI built exactly this and nothing more」),紅旗是「what's missing. The AI faithfully writes down what you said. Your job is to notice what you forgot to say.」**全手動。**

### spec 跟 code 不一致時怎麼辦(它自己的答案)

- docs/editing-changes.md 原話:「**The code is now correct, the spec is stale.** Update the delta spec… to describe the behavior you actually shipped.」或「**The spec is correct, the code drifted.** Keep building or fixing until the code matches the spec.」
- 「at archive time, your specs become the truth of record. So before you archive, **make the specs honest about what the code does**.」
- 換句話說:**誰對由人當場判,spec 是可以被改成跟 code 一樣的描述性紀錄**。這跟 lumos 的「圖譜是意圖權威、衝突立事故筆記」是相反的真相語意(見下)。

### brownfield、團隊、跨 repo

- **brownfield**(docs/existing-projects.md):「You do not document your whole codebase to start. You write specs only for what you're about to change.」明說不要回填:回填的 spec「go stale, because nothing forces them to track reality」。
- **團隊**(docs/team-workflow.md):一個 change = 一條 branch = 一個 PR;審查者先讀 proposal、再讀 delta、最後才讀 code diff;兩個 change 動同一條 requirement,歸檔第二個時在主 spec 出 merge conflict,「resolve it like any merge conflict, keeping the requirement that reflects reality」。**沒有建議任何 CI 跑 validate、沒有 git hook。**
- **stores(beta)**:planning 獨立成一個 repo,code repo 用 `references:` 唯讀引用,指令裡附「每篇 spec 一行摘要+抓取指令」;「**No sync, ever — by design.** OpenSpec never clones, pulls, or pushes.」

### FAQ 刻意沒回答的問題

FAQ 33 題裡沒有:AI 不照 spec 做怎麼辦、spec 過期怎麼辦、有沒有任何強制、spec 能不能取代測試、跟 Spec Kit/Kiro 差在哪、token 成本。這不是我漏抓,是它的定位——它把這些留給人。

## 原始碼複核(乾淨 agent clone 逐機制讀,commit 9d4e597)

派了一個沒看過本篇結論的 agent,拿「原始問題」去讀原始碼,每條附檔案與行號(CLAUDE.md 第四條:「沒有 X」要決定事情之前先派乾淨 agent 對一次)。clone 在 job 暫存目錄,不進 repo。

### validate:只讀 markdown,從不讀 code

- 實作在 「src/core/validation/validator.ts」(939 行);import 只有 fs、parser、zod schema、task-progress、artifact-graph,**沒有任何讀 「src/」 的路徑**。
- `--strict` 唯一作用:warning 也算失敗(`valid = errors === 0 && warnings === 0`);沒有任何規則會因 strict 改等級。
- 等級對照(我在文件層猜錯了一條:SHALL/MUST 不是 error):

| 規則 | 等級 |
|---|---|
| ADDED/MODIFIED 的 requirement 零 scenario | **ERROR** |
| 主 spec 的 requirement 零 scenario | ERROR(zod)再加一條 WARNING |
| 正文沒有 SHALL/MUST | **WARNING**(spec 明寫理由:不要求英文;strict 才擋) |
| 正文整段缺 | ERROR |
| MODIFIED 丟掉主 spec 仍有的 scenario | ERROR(只在 `openspec validate <change>` 走的路;archive 內部故意不查,留給合併那步 throw) |
| 零 delta 且沒 `skip_specs` | ERROR |
| `skip_specs` 但 「specs/」 底下有檔 | ERROR |
| Purpose 少於 50 字 | WARNING |
| 「archive 合併乾跑會拒絕」 | **INFO**(不影響判定;理由是「目標可能是還沒歸檔的 sibling change 加的」) |
| tasks.md 編號跑錯群組 | WARNING(只對內建 schema) |

- proposal.md 層的檢查(Why ≥ 50 字)只有 archive 用,而且註解明寫「Proposal validation is informative only (do not block archive).」

### archive:以標題文字為 key 的機械合併,找不到就 throw,跨 change 零協調

- 合併在 「src/core/specs-apply.ts」 的 `buildUpdatedSpec`(141–600 行),順序 RENAMED → REMOVED → MODIFIED → ADDED。
- key 是 `### Requirement:` 標題 **trim 後、大小寫敏感、內部空白敏感**;大小寫/空白不同只用來報 near-miss 然後 throw。schema 給 AI 的指令卻寫「whitespace-insensitive」——**指令文字跟程式碼不一致**(agent 標為未實跑推論)。
- MODIFIED 找不到目標 → throw;ADDED 已存在且內容不同 → throw;REMOVED 找不到 → warning 當作已移除;RENAMED 來源不在但目標在 → 當作已同步。
- **兩個 change 動同一條**:沒有鎖、沒有合併策略;第二個歸檔時內容相同就 no-op、不同就 throw。docs 說的「resolve it like any merge conflict」是靠人在 git 層解。
- 安全流程:寫任何檔之前先算每份 spec 重建後的內容並驗證(「so a late validation failure really does leave all targets unchanged」)、前後 sha256 指紋防併發改動;但最後寫入是 `fs.writeFile` **原地覆寫**,不是暫存檔+rename(對照 lumos 的原子寫入紀律)。
- **tasks 沒勾完不是硬擋**:互動模式問一句(預設 No),`--yes` 直接過。另有 `--skip-specs` 與 `--no-validate`(要再確認一次,並印一行「Validation skipped」)。
- 1.13.0 三條 archive 修正都是「validate 說 OK、archive 回 0、但要改的東西根本沒改」這一型:`*`/`+` 開頭的 REMOVED 靜默沒生效(#1800)、重複 `## ADDED Requirements` 標頭只吃最後一份(#1802)、blank 行壓縮誤改 fenced code(#1798)。★這一型正是 lumos「有機制、沒接線」與「假綠」的同款失效★。

### verify:174 行 prompt,唯一機械動作是叫 agent 跑三個唯讀 CLI

- 來源 「skills/openspec-verify-change/SKILL.md」,由 「src/core/templates/workflows/verify-change.ts」 生成。
- 「比對 code」的做法原話:「Search codebase for keywords related to the requirement / Assess if implementation likely exists」;heuristic:「Use keyword search, file path analysis, reasonable inference - **don't require perfect certainty**」;「Check if tests exist covering the scenario」是叫 AI 看,不是跑。
- 假陽性策略:「When uncertain, prefer SUGGESTION over WARNING, WARNING over CRITICAL」。
- **輸出沒有任何程式讀**:`grep -rn CRITICAL src` 只命中模板本身;「docs/commands.md」 明寫「Does not block archive, but surfaces issues」;spec 層那句「do NOT suggest running archive」是給 AI 的口頭約束。

### apply 與強制力:一條 regex 讀勾選框,整個 repo 零 git hook

- 追蹤:`/^\s*[-*]\s*\[([\sxX])\]\s*(.*)/`,註解自承「Permissive on purpose ... a task this parser drops is a task openspec archive stops warning about.」勾選由 AI 動手。
- 搜 `pre-commit / husky / lefthook / pre-push / git hook` 全部 src/docs/skills:命中只有 commander 的 `preAction` 生命週期、一句註解、以及 `validate --archived` 的說明「handy in a pre-commit hook」——**要使用者自己裝**。init/update 不安裝任何 hook。
- CI:「.github/workflows/」 三支全是 OpenSpec 自己 repo 的測試/發版/安全掃描;唯一會寫進使用者 「.github/」 的是 Copilot cloud agent 的環境設定檔,不是閘。
- 它自己的話:docs/team-workflow.md「**Everything below is convention, not enforcement.** OpenSpec won't make you do it this way」;docs/customization.md「**OpenSpec only checks that artifacts exist**, so enforce the gate with your own CI or hook」;docs/cli.md「These are behavioral contracts for generated agents, not enforceable CLI checks」;apply/archive skill「These are prompt-level behavior contracts, not enforceable checks.」

### 注入給 agent 的內容:受管區塊已成 legacy,現在是 skill 檔+機器介面

- **不再往根目錄 AGENTS.md / CLAUDE.md 塞受管區塊**:`<!-- OPENSPEC:START -->` 標記只剩 legacy-cleanup 在用(偵測並**移除**);migration-guide 說「OpenSpec markers in CLAUDE.md, AGENTS.md, etc. | No longer needed」。OpenSpec 自己 repo 根目錄的 AGENTS.md 是 0 bytes。
- 寫進使用者 repo 的是:每個工具的 「skills/openspec-*/SKILL.md」(12 支共 132KB;core 六支 71.5KB)+ 「.claude/commands/opsx/<id>.md」 指令檔 + 「openspec/config.yaml」(`context:` 塞技術棧、`rules:` 按 artifact 加規則;各注入成 `<context>`/`<rules>`/`<template>` 三段,上限 50KB)。
- 給 agent 的機器介面:`openspec instructions <artifact|apply|archive> --json`,回 `contextFiles`(artifact → 絕對路徑)、`progress`、`state`(blocked/ready/all_done)、`dependencies`、`unlocks`。**全部要 agent 主動敲;沒有 PreToolUse 這種在改檔前自動推的東西。**
- 對照 lumos(同日 `wc -c`):常駐注入 = CLAUDE.md 範本 7.2KB + SessionStart hook 一段;按需 = 五支 skill 共 55.7KB、project-notes 的 reference 121.8KB;動手前 = PreToolUse hook 算 impact 推合約/事故。**兩邊塞給 AI 的文字量同量級;差別在 lumos 有「不用 AI 記得敲」的那一層(hook),OpenSpec 沒有。**

### artifact 圖:「做完了」= 檔案存在

- 「src/core/artifact-graph/state.ts」:「Detects which artifacts are completed by checking file existence in the change directory.」有一個符合 `generates` glob 的檔就算 done,**不看內容**。
- 下一步 = 未完成且 requires 全完成者,依宣告順序;`/opsx:continue` 「Pick the FIRST artifact with status: ready」「STOP after creating ONE artifact」。
- custom schema 能改:artifact 清單/依賴/模板/指令、apply 的 requires 與 tracks;**不能改**:delta 的 `## ADDED` / `### Requirement:` / `#### Scenario:` 格式與合併規則(硬編)。
- [[Projects/執行DAG_調研]] 裁過「不能從證據重算的狀態不要做」——OpenSpec 的 done 是「檔案在」,比勾選框還弱一階,但它也沒拿這個狀態去擋任何事,所以沒有假完成的代價。

### stores / initiatives / explorations / work

- store = 只放 「openspec/」 的獨立 planning git repo;registry 在本機 「~/.local/share/openspec/stores/registry.yaml」(不提交);`--store` 解析五層(旗標 → 最近的 openspec/ → config 指針 → 全域預設 → 報錯)。
- `references:` 只在 `instructions` 輸出多一份被引用 store 的 spec **索引**(id+一行摘要+抓取指令),內容不內嵌,上限 50KB。「OpenSpec currently does not route tasks to repos.」
- 自食目錄裡的 「work/」(goal → roadmap → slice → result 四層)、「initiatives/」(已從 CLI 拔掉:「--initiative is no longer supported」)、「explorations/」(explore 本身不寫檔)都是**它自己的實驗區,沒有 spec 定義、沒有 CLI 支援**。

### 「有沒有」清單(乾淨 agent 逐條搜原始碼;關鍵字列在括號)

| 問題 | 答案 | 最接近的東西 |
|---|---|---|
| a. 決策作廢/被取代 | **沒有**(supersede / revisit / invalidat / deprecated decision) | design.md 的 Decisions 是自由文字;自食 decisions.md 用日期標題,「supersedes」只在散文 |
| b. requirement/scenario 綁具體測試 | **沒有**(test name / linked test / traceab) | schema 指令「each scenario is a potential test case」、tasks「state how to verify」塞在勾選框文字;**第三方 schema anvil** 做了「test-plan maps every spec scenario to a named test」 |
| c. spec↔code 機械漂移偵測 | **沒有**(drift / createHash / sha256 / stale) | 所有 hash 都不碰 src/:archive 指紋防併發、skill 檔與設定的漂移、store checkout 的 ahead/behind |
| d. spec 全文搜尋/排序 | **沒有**(search / fuzzy / relevance / rank) | `list --sort recent\|name`、`show --json` 按 index 過濾、`view` TUI |
| e. code diff 反推受影響 spec | **沒有**(impact / affected spec / git diff / blame) | proposal 模板的 `## Impact` 段,AI 用散文寫 |
| f. 驗證紀錄/歷史/重驗條件 | **沒有**(verified at / verification record / re-verify) | 歸檔資料夾日期前綴;`validate --archived` 只驗 tasks 全勾;verify 報告是聊天輸出不落盤 |
| g. 多審查員/對抗式審查 | **沒有**(adversarial / multi-agent / red team / second opinion) | PR 人審散文;**anvil** 有「fresh-context, read-only reviewer (a second model when one is available) and emits a VERDICT: line」——但 OpenSpec 核心說「enforce the gate with your own CI or hook」 |
| h. BREAKING 標記守衛 | **沒有** | `schema.yaml` 一句「Mark breaking changes with **BREAKING**」,之後沒程式讀 |
| i. 跨 repo 共用規則的反向索引 | **沒有** | `references:` 單向宣告;capability 目錄容忍 monorepo symlink |
| j. brownfield 先把現況寫成 spec 的 SOP | **沒有,且明確反對** | 「Resist the urge to back-fill everything」「Forcing a one-time bulk conversion tends to produce a large, stale spec nobody trusts」;`/opsx:onboard` 是掃 TODO 挑小改動走一輪 |

★anvil 那條值得記★:社群自己長出了「scenario 綁測試名+獨立審查員+VERDICT」的 schema——就是 lumos 的 `[test:]` 綁定+design-loop 那層——而 OpenSpec 核心的回應是「我只查檔案存不存在,閘你自己用 CI 或 hook 做」。這是兩邊分工最清楚的一句話。

### 它自己的 spec 也落後於 code(agent 讀到的,未跑 git 歷史確認)

- 「openspec/specs/cli-validate/spec.md」 兩個 scenario 引用 「openspec/AGENTS.md」 當「authoritative template」——這個檔已被 legacy-cleanup 刪除。
- 「openspec/specs/docs-agent-instructions/spec.md」 整篇規範 「openspec/AGENTS.md」 的寫法——同上,code 會刪它。
- 「cli-validate/spec.md」 寫的「Bulleted WHEN/THEN → 獨立 warning」在 validator.ts 找不到獨立實作,只有零 scenario 時附一段格式指引。
- 這不是抓小辮子:它是「nothing forces them to track reality」在作者自己 repo 裡的實例。36 篇 spec、3,194 個測試,沒有一道機制把 spec 裡的檔名對回檔案系統——lumos 這邊對應的是 Check Y(符號存在性)與 refcheck。

## 世界怎麼用它:一手證言與批評(乾淨 agent 收集,全文含 URL 在卷證 02)

### 背景先講清楚

- **誰做的**:Fission AI,YC W26,創辦人 Tabish Bidiwale(雪梨,前 Q-CTRL 資深工程師),2025 年中起全職做;repo 建於 2025-08-05,v1.0.0 是 2026-01-26。「Single maintainer creates sustainability risk」是實測評比裡列的缺點之一。
- **星數曲線已經平了**:27k(03-06)→ 約 37k(05-01)→ 56k(06-26)→ 64.3k(08-09)→ 67.3k(09-05,那週 +0)→ 67,842(09-10)。
- **它從來沒有一條自己的大 HN 串**:三次提交合計 5 分、2 則留言。所有真正的抱怨散在別人的串(Specsmaxxing、GSD、Ask HN)跟 GitHub issues 裡。
- **商業版=漂移偵測**:2026-08-28 發布 OpenSpec Cloud Agent——「A pull request can change how your product behaves without updating the spec that describes it. The OpenSpec Cloud Agent compares pull requests with your requirements and cites the exact lines when they disagree.」早期存取、人工上線、沒公開定價。已在自家 PR 上跑(有 `openspec-cloud[bot]` 留言)。
- Thoughtworks Radar Vol.34(2026-04)列 Assess,附註「re-evaluate the need for SDD tooling」as models get stronger。

### 那句「drifting and drifting」的真實出處

- HN 留言 47999279,2026-05-03,留言者 alasano,在 Specsmaxxing 那條串裡(不是 OpenSpec 的串;二手文章連到的 47994433 是祖父留言,連錯):「I enjoy the OpenSpec format but I think maintaining the main specs is not worth it. I've stopped doing it entirely and just archive directly after implementation. When you do the sync process, it just keeps drifting and drifting until you have duplication and contradictions across specs.」
- **講的人的脈絡很重要**:他從 2026-03 到 2026-08 連續用、在 OpenSpec 上面蓋了一個商業 orchestrator(engine.build,自動跑「review/fix/verification rounds until the implementation matches the spec」)、08-30 還說「I use and love openspec」。所以這是重度使用者對「主 spec 同步」這一段的放棄,不是對整個工具的否定——而他自己補的正是 OpenSpec 沒有的那層迴圈。
- 他回的那條父留言(jochem9,用了幾個月)講另一個方向:「when a spec changes, AI needs to find the relevant code to change it. It's pretty easy to miss something in large codebase.」——spec→code 這個方向沒有工具幫忙。

### 作者自己怎麼說漂移

- Discussion #169(2025-10-13,有人問「我直接改 code,spec 不會知道」):作者 TabishB 回「my view is it's ok to update the source of truth directly to match the changed implementation. I'm looking at ways to see if this is possible to detect in a simpler automatic way, but **up till then this process has to be manual unfortunately**.」
- Issue #880(2026-03-26,提議「拿現在的 code 對主 spec 驗」):作者回「I'm not opposed to this, it can most likely end up as an optional skill. Just unsure how often people would use it. … would need some automation behind it to be useful. e.g running it in CI every 5 commits」——至今掛 future-roadmap。
- Issue #141(2025-10-10):「sometimes you tweak things during implementation that makes the initial proposed spec invalid. There's currently no good way or step in the process yet to handle this without explicitly or manually updating the proposal」。
- ★結構性事實★:作者 2025-10 承認漂移只能手動;社群 2026-03 起要 CI 偵測;官方 2026-08 的答案是**付費 Cloud Agent**,不是開源 CLI。**lumos 用 hook 免費做的那件事(改 code 前後對圖譜),在 OpenSpec 的世界是商業產品。**

### GitHub issues 裡的失效型態(每條附重現步驟,是最硬的證據)

- **archive 靜默丟內容**:2026-09-06 一週內連開四張(#1799 `*`/`+` 開頭的 REMOVED 靜默無效、#1801 重複區段標頭丟 requirement、#1803 區段外的 requirement 無聲消失、#1805 壞的 RENAMED 對錯條),共通句「exit code shows success despite no changes applied」;v1.13.0 修了兩張。更早 #954(2026-04)主 spec 混進一個 delta 標頭,後面所有 requirement 對 validate/archive 隱形。**這一型=「檢查說 OK、工具回 0、東西沒做」**,跟 lumos 圖譜裡的假綠形態同款。
- **validate 過、archive 炸**:#1112(validate --strict 過,幾週後 archive 說 MODIFIED not found)、#1477。#1697/#1793:MODIFIED 沒辦法表達「我故意改 scenario 名」,會被當成丟 scenario 擋下,繞法是 `--no-validate`——**一繞就關掉全部守衛**。
- **AI 沒照流程走**:#1264(agent 跳過 sync 直接 archive)、#863(archive skill 叫 AI 自己搬檔不呼叫 CLI)、#783(propose 一次生四種 artifact 互相矛盾;「Claude Sonnet 4.5 didn't propagate design.md updates to specs and tasks」)、#687(沒有東西驗 spec 有沒有涵蓋 proposal,使用者自建 `/opsx:audit`)。
- **verify 假通過**:#1761「42 [x] · 17 [~] · 0 [ ] 回報 ✓ Complete,其中一項是真的缺測試」;PR #1732「/opsx:verify could skip checks when evidence was unavailable, then report 'All checks passed. Ready for archive.'」——**這是 lumos 圖譜記過的「席位通知會宣稱沒發生的寫檔」同一型:LLM 報告沒有 oracle。**
- **並行 change 互相看不見**:#1669「Overlap between open changes is invisible until one archives … deltas record only new text, lacking the base specification they derived from」;#1387 要 pre-archive drift check。

### 一手實跑報告(有專案或時長可查的)

- **最扎實的比較**(Ran the Builder 團隊,Palo Alto Networks,2026-04-13):BMAD / Spec Kit / OpenSpec 同一個真功能加進既有 serverless Python 後端,13 類評分 OpenSpec 4.00 第一(Spec Kit 2.77);planning 3 小時 $25、實作 1 天 $70。缺點原句:「Sometimes assumes context and adds rationale to decisions you didn't make」「Single maintainer creates sustainability risk」。建議「If you want the lowest-friction start: OpenSpec」。
- **團隊用半年後換掉**(Peng Qian,2026-09-01,推自家方案要打折):「The spec files OpenSpec writes **never save the user's original intent or original requirements, and they never keep the conversation the user had with AI**」;「some even using it just for show at the start and switching to pure vibe coding afterward」;code 改了沒回寫 → 「the spec files completely lose their value as a reference」。★這條直指 provenance——lumos 決策四欄與 handoff 讀逐字稿正是為了保留「當時怎麼想的」★。
- **忘了歸檔就漂**(azanello,2026-03-19):「If you forget to archive, specs and reality diverge … half the 'pending' changes had shipped months ago」;「I've watched Claude Code forget what task 2 did by the time it reached task 7」。
- **成本**(Andreas Lay,2026-06-26):「~2 million tokens per day」(Opus 4.8);「Both OpenSpec and Open Code Review eat up a lot of tokens」;但「Given a good spec state-of-the-art models can one-shot even complex tasks」。
- **一次實驗失敗**(dev.to,2026-04-01):.NET 網站 UI 美化,兩小時後「looked almost identical」,結論「A simple Instructions.md approach was faster」——但選題是純視覺、模型用 Haiku,對 SDD 不公平,列著不當證據。
- **正面**:HN 上 gbrindisi「it lets you tune the workflow to your liking and doesn't get in the way」、xpn「after trying SpecKit and GSD, I finally settled on OpenSpec」;兩人都把 OpenSpec 當「產 context 跟任務清單」的前段,後段接自己的 ralph loop。

### 可信度總評(agent 的判斷,我照錄)

- 真正一手實跑:HN 5 人、部落格 7 篇、廠商實測 1、論壇 1、GitHub issues 一批(每條附重現)。
- 二手/行銷不算證言:codemyspec 三篇(競品,全靠引 alasano 與 Augment,還連錯 ID)、avasdream(自承「it occured to me in a dream」)、jgcarmona(沒跑過)、intent-driven(模板作者)、vinodh(LLM 模擬團隊)。
- 量化數字只有三處:Ran the Builder 的成本與評分、Andreas Lay 的每日 token、#1761 的 42/17/0。
- Kiro / Tessl 對 OpenSpec 的真跑比較:**沒找到**。

## 兩者站在什麼位置

- **答的不是同一題**:
  - OpenSpec 的問題是「AI 太會做、但要求只在對話裡,怎麼在寫 code 前先講好」——解法是把「要做什麼」寫成可審的紙本,便宜地在紙上吵完。
  - lumos 的問題是「code 只告訴你現在長怎樣,為什麼這樣、邊界在哪、哪些不能改、驗過沒,下一個 session 的 AI 從哪知道」——解法是決策當下第一手記錄+合約+驗證+機械閘。
  - 用一件工作的時間軸看:OpenSpec 站在 **動手前**(explore → propose → 兩分鐘人審),lumos 從 **動手前**(圖譜先行、impact、hook 注入)一路管到 **做完後**(驗證紀錄、合約綁測試、REVISIT、stale 重驗)。
- **重疊區只有「一件工作怎麼打包」**:

| OpenSpec 的 change 資料夾 | lumos 的計劃節點 | 差在哪 |
|---|---|---|
| proposal.md(Why / What / Capabilities / Impact) | `Projects/<主題>_計劃` 的白話開頭 + `PRIOR-ART:` + KEY 行 + DEP 行 | lumos 多一行「世界解過沒」(PRIOR-ART,120/172 篇計劃有);OpenSpec 多一格「哪些 spec 會動」的機器合約 |
| delta spec 的 Requirement + Scenario | `[SN]` 條款 + `[test:]`/`[manual:]` | OpenSpec 要求每條至少一個 scenario(validate 擋);lumos 要求每條綁到**真測試名**才過處置閘(39/172 篇計劃已用)——強一階,但只在設計審迴圈裡擋 |
| design.md 的 Decisions(why X over Y、alternatives) | decisions 四欄(context / alternatives≥2 / why_chosen / trade_offs)+ `decided` 日期 | 形狀幾乎一樣;lumos 多 `valid`/`superseded_by`/`ended`(289 條決策、20 條翻案),OpenSpec 的決策歸檔後就凍在史料裡 |
| tasks.md 勾選框 | T1..Tn 任務段 | 都是人手維護的清單;[[Projects/執行DAG_調研]] 已量到 lumos 這邊「維護與否毫無規律」,OpenSpec 的 apply 只讀勾選框,一樣不驗 |
| archive(delta 合進主 spec、搬進 archive/) | `status: done` + Verification 節點 `plan_refs` 回指 + 同一次工作改 Systems 節點 | OpenSpec 有**機械合併**;lumos 是人改 Systems 節點,由 pre-commit「改 code 沒動圖譜」與 impact --sync-check 點名 |

## 九維對照

| 維度 | OpenSpec | lumos |
|---|---|---|
| **真相源** | 「specs/」 = 系統現在的行為(描述性,歸檔時跟著 code 走) | 圖譜 = 為什麼/邊界/合約/驗證(意圖權威;跟行為事實衝突立事故筆記) |
| **裝什麼** | 可觀察行為(SHALL/MUST + WHEN/THEN);class 名、library、實作步驟明令不准進 | code 讀不出的那層:決策理由、被否方案、合約、驗證前提、事故 |
| **變更單位** | change 資料夾四 artifact,歸檔合併 | 計劃節點 + 驗證節點 + 決策;不合併、留全史 |
| **驗證** | validate=格式;verify=AI 建議報告;人兩分鐘審 | ★INVARIANT★→[test:]→[audit:]→[kill:] 鏈;doctor 22 道;design-loop / code-loop 多席對抗;`spec-trace` 條款綁測試 |
| **強制力** | 零 hook、零 CI 範本、「visibility not guardrails」 | 16 層(pre-commit 擋改 code 沒動圖譜、pre-push 擋錨點/doctor/高風險未審、Stop hook 對帳、CI) |
| **決策時效** | design.md 歸檔即凍結;無 supersede、無重驗條件 | `valid_under` / `revalidate_when`(181 篇驗證 174 篇有)、`stale --candidate`、`REVISIT:` 144 行、決策翻案 20 條 |
| **檢索與推送** | `list / show / status --json`,agent 自己敲 | `search` 排序+多詞回退、`context`、`impact --file/--diff`、PreToolUse hook 在改檔前把合約/事故推到眼前、子代理派工鏡頭 |
| **brownfield** | 惰性:只寫你要改的那片,明說別回填 | 惰性:[[Systems/節點還原]] 七步,每句 why 標 `[src:]/[git:]/推測/佚失`,Check J 擋編造 |
| **跨 repo** | stores:planning repo + 唯讀 references,「No sync, ever」 | core-knowledge:`core_refs` 指針 + core-invariant-baseline hash 守合約欄位 |
| **分發** | npm、Node ≥20.19、30+ 家工具、週更、67.8k★ | python3 零依賴單檔(2.47 萬行、744 支測試)、Claude Code + Codex、單作者 |

## 最深的一刀:強制力模型

- **OpenSpec 刻意不擋任何事。** docs/opsx.md 通篇沒有 enforcement;artifact 圖的依賴是「解鎖」;validate 只讀 markdown;verify 是選用的建議報告;團隊文件沒建議 CI;spec 跟 code 打架時「往真的那邊改」。這是它的賣點——「fluid not rigid」——也是它六萬八千顆星的原因:對寫 code 的內圈零摩擦。
- **代價已經在社群顯形:漂移。** 用過的人最大宗的抱怨是 spec「keeps drifting and drifting until you have duplication and contradictions across specs」(HN alasano,2026-05,用了五個月以上的人;出處見證言節);作者 2025-10 自承「this process has to be manual unfortunately」;它自己的 docs 也承認:回填的 spec 會爛,「because nothing forces them to track reality」。
- **官方對漂移的解法是收費的。** 2026-08-28 的 OpenSpec Cloud Agent「compares pull requests with your requirements and cites the exact lines when they disagree」——在 PR 時用雲端 LLM 對一次。開源 CLI 那邊,#880「拿 code 對主 spec 驗」從 2026-03 掛到現在。lumos 的 `impact --diff` + `--sync-check` + Stop hook 對帳做的是同一件事,差別是本機、機械、免費、且擋得住 commit。
- **lumos 幾乎所有機械都在打這一個敵人。** pre-commit 擋「改 code 沒動圖譜」、Stop hook 收工對帳、impact --sync-check 點名該動沒動的節點、Check N/U/Y 驗數字/概化/符號還在不在、stale 掃過期驗證、anchor 驗裁判沒被動過。這些是 lumos「圖譜是真相」承諾的內生成本——OpenSpec 不做這個承諾,所以不用付。
- **兩邊都誠實:一邊承認它不維護,一邊承認維護稅很重。** [[Systems/外部對照-code衍生wiki]] 對 openwiki 講過同一件事:零紀律零維護的工具贏在內圈摩擦,輸在裝不下「不可漂移的真相」。OpenSpec 比 openwiki 多了一步——它的 spec 是人跟 AI 事前寫的(第一手),不是事後從 code 逆向的——所以它的 provenance 比 openwiki 好,但保鮮機制跟 openwiki 一樣是零。

## 真相語意:描述性紀錄 vs 意圖權威

- **OpenSpec**:specs 是「the truth of record」,但歸檔前要「make the specs honest about what the code does」——真相跟著 code 走。這在它的世界是對的:spec 只寫可觀察行為,行為以 code 為準沒錯。
- **lumos**:圖譜記的是 code 讀不出的東西(為什麼、邊界、合約),所以不能跟著 code 走——code 改了不代表理由變了。衝突時的正確動作是「查清哪邊錯,立一篇事故筆記」(Codex 外審 2026-07-29 把「圖譜為準」限縮成「意圖權威」的那次認識論修正)。
- **一個好例子看差別**:OpenSpec 的 MODIFIED 寫「The system MUST expire sessions after 15 minutes of inactivity. (Previously: 30 minutes)」——它記了「以前是 30」,但沒記「為什麼從 30 改 15」「哪個方案被否」「什麼前提下這個 15 才成立」。這三樣在 lumos 是決策四欄+`valid_under`,是它存在的理由。

## OpenSpec 真正的優勢(誠實記,不是恭維 lumos)

1. **事前對齊的儀式便宜、且針對 AI 最常見的失敗**:「Fixing a misunderstanding in a one-paragraph proposal is free. Fixing it after the AI wrote 400 lines is not.」lumos 的設計審迴圈也在事前,但它審的是「spec 有沒有洞」,不是「人跟 AI 有沒有講好」;lumos 沒有 `/opsx:explore` 這種「還沒立案就先聊」的入口。
2. **delta 格式讓 brownfield 零門檻**:「specify a change to a 50,000-line app without first documenting the whole thing」。lumos 的節點還原也是惰性,但七步+雙 agent 交叉審計比 OpenSpec 的「就寫你要改的那片」重得多。
3. **schema 可自訂、指令模板可實驗**:「edit a template, see if the AI does better」——lumos 的 skill 是散文,改了要靠情境探針驗,沒有「artifact 圖」這種結構化的工作流定義。
4. **分發與生態**:npm、30+ 家工具(Claude Code、Cursor、Copilot、Zed、Codex…)、週更、Discord、36 篇自食 spec、3,194 個測試案例。lumos 是單作者手工精品,只接 Claude Code 與 Codex。
5. **explore / onboard 兩個入口**:一個是無壓力思考,一個是掃 repo 挑小改動帶新手走一輪;lumos 的進場是「先敲 lumos search」,對新手是紀律不是引導。
6. **stores 的「No sync, ever」**:跨 repo 只用唯讀指針,不同步——跟 lumos core_refs 同宗,證明這條路不是 lumos 獨有的怪癖。
7. **MODIFIED 必貼整條、REMOVED 必附 Reason+Migration**:兩條寫法規則直接由 validate 擋,比 lumos 的決策翻案(superseded_by 有、migration 沒有)多一格「怎麼遷移」。

## lumos 領先處(機械數,2026-09-10;重算指令在誠實邊界節)

- **決策時效**:289 條決策、20 條翻案;181 篇驗證紀錄 174 篇帶 `valid_under` 與 `revalidate_when`;144 行帶日期的 `REVISIT:`。OpenSpec 沒有任何「這條 accepted 之後還算不算數」的欄位——2026-07-07 掃描時對整個 ADR 生態下的結論,對 OpenSpec 也成立。
- **合約鏈**:登記簿 35 條 ★INVARIANT★、9 條 ★DEBT★,綁測試 36 行;`guard kill` 證明測試真咬得住。OpenSpec 的 scenario「could become an automated test」——停在散文。
- **動手前注入**:PreToolUse hook 在 Edit/Write 之前把「必看合約/事故+相關筆記」推到眼前;子代理派工有 dispatch-lens。OpenSpec 明寫 agent 要自己敲 `instructions --json`。
- **code diff 反推波及**:`impact --diff main..HEAD` 聚合成受影響功能面;OpenSpec 只有 `show --diff`(這個 change 對主 spec 的差異,方向是 spec→spec,不是 code→spec)。
- **對抗式審查**:design-loop 多席+辯方+處置閘、code-loop 風險分級+辯方+pass 留痕綁 sha;OpenSpec 的 verify 是單 AI 讀完寫報告。
- **條款綁真測試**:[SN] 沒綁 [test:]/[manual:] 不得過處置閘(39/172 篇計劃已用);OpenSpec 的 scenario 沒有機器讀得到的測試連結。

## 回看 2026-07-07 的裁定

- **借的那條已經長大**:「AC-n GIVEN/WHEN/THEN 編號+核銷檢查」→ 現在是 `[SN]` 條款 + `[test:]` 綁定 + `spec-trace` 七態 + 處置閘第五步。比 OpenSpec 的原型強一階(綁到真測試、閘會擋),但只在設計審迴圈裡擋,計劃整份不寫 [SN] 就繞過(那篇計劃自己的 REVISIT 有記)。
- **跳的那條被印證、但理由要修**:當時跳 delta-spec 的理由是「第二真相源」。深讀後發現 OpenSpec 自己也把 delta 當暫態(歸檔即合併),不算兩份真相;真正出事的是「propose 到 archive 之間那段時間,沒有東西逼 spec 跟著實作動」——社群漂移證言全發生在這個窗口。所以 lumos 不借 delta 格式的理由該改寫成:**lumos 沒有這個窗口**——同一次工作內寫回、pre-commit 擋、Stop hook 對帳,漂移窗口被壓到一次 commit 以內。
- **一條新看到、當時沒看到的**:OpenSpec 的 REMOVED 必附 Reason + Migration。lumos 決策翻案有 `superseded_by` 沒有「怎麼遷移」;合約退場(★INVARIANT★ 降格或拿掉)走的是 delguard 擋刪測試,沒有「退場理由+遷移」的固定格式。列為候選。

## 可借候選(不裁,留 Enzo;每條寫借什麼/為什麼/落點/風險)

1. **REMOVED 必附 Reason + Migration → 合約退場格式**。借什麼:★INVARIANT★ 降格為 ★DEBT★ 或整條拿掉時,要一行「退場理由+下游怎麼遷移」。為什麼:現在只有 delguard 擋「刪了被綁的測試」,沒擋「合約悄悄消失」。落點:`lumos guard` 加 retire 子動作或 lint 規則。風險:又多一格要填;先查合約退場實際發生過幾次(沒發生過就不值得)。
2. **`show --diff`:計劃對 Systems 節點的差異預覽**。借什麼:一份計劃「做完會讓哪幾篇 Systems 的哪幾行變」的預覽。為什麼:現在 impact 是 code→節點,沒有 計劃→節點 的預覽;歸檔時人改 Systems 靠記憶。落點:`lumos impact --node <計劃>` 已列「誰指向它」,差一步「它宣稱要改誰」。風險:計劃裡「要改誰」是散文,機器讀不到;要先有 DEP 行慣例才做得到。
3. **`skip_specs: true` 的「明寫免除+理由」慣例**。借什麼:純重構/工具/文件的 commit,用一個宣告式標記說「這次不動行為所以不動圖譜」,而不是靠 pre-commit 白名單。為什麼:現在 pre-commit「改 code 沒動圖譜」的逃生口是路徑白名單與 `--no-verify`,前者不帶理由、後者全跳。落點:pre-commit 認 commit trailer 或 `.lumos/` 標記。風險:2026-07-07 已借過 `LUMOS_SKIP` 細粒度跳閘(scripts/lumos 已有 13 處),先查它跟這條是不是同一件事再決定。
4. **explore 模式:未立案的思考入口**。借什麼:「還不確定要不要做」時,不建計劃節點、先讀圖譜+code 攤選項的一段流程。為什麼:lumos 進場紀律是「先查再做」,但沒有「先聊、不留痕」的正式出口,常見結果是計劃節點開了又擱著(執行DAG_調研量到 43 篇 doing、17 篇一個月沒動)。落點:skill 散文一段,不加指令。風險:「不留痕」跟「同一次工作內寫回」的鐵則要劃清:探索不留痕可以,決定了就要留。
5. **人的兩分鐘審查清單**。借什麼:七條「我忘了說什麼」的清單放進設計審迴圈的人簽核那一步。為什麼:design-loop 審的是 spec 有沒有洞,`signoff` 簽的是業務規則對不對;「AI 忠實寫下你說的,你的工作是發現你沒說的」這個角度兩邊都沒有明寫。落點:signoff 的提示文字。風險:純散文,沒機械守衛——要附 REVISIT 才准寫。

## 刻意不借(理由同等重要)

- **delta 合併進主 spec 的機械合併**:lumos 的 Systems 節點承載的是「為什麼」,不是可觀察行為;合併演算法對散文無意義,且會製造「歸檔即真相」的窗口(見上)。
- **artifact 圖 schema**:lumos 的工作流是 skill 散文+閘,不是 artifact 依賴圖;[[Projects/執行DAG_調研]] 已裁「不能從證據重算的狀態不要做」,artifact 圖的 READY/DONE 是看檔案存在,不是證據。
- **採用為依賴**:Node ≥20.19 + npm,零依賴家規直接出局。
- **30+ 家工具接線**:平台類題目,跟本篇無關;lumos 只認 Claude Code 與 Codex 是刻意的。

## 誠實邊界

- **本 session 沒有實跑 OpenSpec 建一個 change**;結論建立在 docs 25 頁、原始碼逐機制讀、社群證言、與 Enzo 之前親用的一句觀察(「生成一次都偏」)。日後要硬化,可對一個已知 repo 跑一輪 propose → apply → verify → archive,人工抽查 delta 對 code 的偏差。
- **星數與版本是 2026-09-10 當天 GitHub 頁面讀到的**,它週更,一個月後數字必變。
- **社群證言的一手/二手比例**見證言節的可信度總評;「keeps drifting」那句是一手 HN 留言,其餘多數是二手歸納。兩份 agent 回報全文(含每條 URL 與 file:line)存在卷證資料夾,本篇引用時有刪節:

```
governance/review-reports/openspec-research-2026-09-10/01-source-read.md
governance/review-reports/openspec-research-2026-09-10/02-community-evidence.md
```

- **原始碼 agent 標的八處不確定**(卷證 01 末節)裡跟本篇結論有關的兩處:①「schema 指令說 whitespace-insensitive、程式碼只 trim」是讀碼推論未造測資實跑;②「init 不再寫 AGENTS.md 受管區塊」是讀碼推論未在乾淨目錄實跑 init。兩者都不影響「零強制」「零漂移偵測」的主結論。
- **lumos 側數字全部機械數**,重算指令:

```
scripts/lumos contracts | tail -1
grep -rhE '^\s+- content:' --include='*.md' docs/lumos-toolchain-knowledge | wc -l
grep -rl '^revalidate_when:' docs/lumos-toolchain-knowledge/Verification | wc -l
grep -rlE '\[S[0-9]+\]' docs/lumos-toolchain-knowledge/Projects | wc -l
scripts/lumos enforcement | tail -3
```

- **「OpenSpec 沒有 X」的清單**(決策翻案、測試綁定、漂移偵測、搜尋排序、impact、驗證歷史、多席審查、hook)是派乾淨 agent 拿原始問題對過原始碼的,不是我的印象——見「原始碼複核」節逐條證據。

REVISIT:2026-10-10 看 OpenSpec 有沒有把 verify 從建議報告變成閘、#880(code 對 spec 驗)有沒有從 future-roadmap 落成開源 CLI、Cloud Agent 有沒有公開定價(它週更,一個月可能翻掉本篇「零強制」那一節);同時看候選 1–5 Enzo 裁了沒,裁了的開 _計劃、沒裁的留著。
