---
type: project
status: doing
created: 2026-09-09
updated: 2026-09-09
tags:
  - type/project
  - status/doing
  - scope/agent-dag
  - prior-art
related:
  - "[[Issues/流程自產工作量未量測]]"
  - "[[Projects/工具鏈全環節體檢_調研]]"
  - "[[Projects/世界repo掃描2026-09-02_調研]]"
  - "[[Systems/graph-sync-coverage]]"
  - "[[Systems/lumos-cli-read]]"
  - "[[Systems/design-loop]]"
  - "[[Systems/效能檢核目錄]]"
  - "[[Projects/驗形式與驗內容_調研]]"
  - "[[Systems/測試假綠形態]]"
  - "[[Projects/Codex完全支援_計劃]]"
  - "[[Projects/派工鏡頭注入_計劃]]"
  - "[[Projects/工具分類_計劃]]"
summary: |-
  FLAG:TECHNICAL
  KEY:調研對象=Spotify 2026-09 公開的 Portal shunt 插件(Claude Code 插件:PreToolUse 擋 Read 與 Bash cat 類讀 >350 行的檔,改派 Gemini 2.5 Flash 便宜讀者只回結構化條列;另一便宜模型照範例寫樣板碼直接落盤;CLAUDE.md 寫規則被無視後搬進 hook 層)——「90%」是 162K 行 Java 三個單發讀檔情境的 chars/4 平均(82/94/94),不是 session 帳;code-writer 無強制;摘要無可靠行號、便宜模型漏 thread-safety bug,明寫排除 debugging/架構/安全碼
  KEY:★先量再裁(2026-09-09,儀器 scripts/usage_scan.py 掃本 repo 14 天 21 session 12,482 請求)★——每次請求 context p50 486K/p90 880K,≥400K 桶佔 token 量 81%;工具輸出直接進 context 只 ≈280 萬 token 對比快取重讀 62 億;Read 佔工具輸出 1.8%、≥350 行大檔讀取 0.87%(scripts/lumos 讀 19 次平均 4.6K 字元=已是定點讀);模型自身輸出駐留 1.32× 全部工具輸出
  KEY:★裁定(待 Enzo 覆核)★——d1 不立案擋大檔 hook(擊中面 <1%,形狀已抄在卷證含三個逃生口,超線再開);d2 儀器留下不升格;候選 C1 派工詞補「只出條列、每條帶名字/路徑:行號」(子代理回報 p99 15.8K、官方無內建上限)/C2 模型自身長輸出寫檔再跑(紀律無機械)/C3 autoCompactWindow 提早壓縮(官方可調 100K–1M,預設約 967K=我們現況撞天花板才壓;先單 session 試一週再裁)
  KEY:hard block 的可活性來自逃生口——shunt 的擋放行 offset/limit、管線、重導,擋訊息把路寫在裡面;與 graph-sync-coverage「硬擋養出 --no-verify」不矛盾:沒逃生口的擋才會
  KEY:不借 code-writer 進本 repo——測試是合約層非樣板(見 related 測試假綠形態);消費端樣板測試多的地方另議
  KEY:誠實界線=只量本 repo(消費端零量測);駐留成本 chars/4 估、55% 的「其他」沒拆;Spotify benchmark 未重跑;shunt 舊 hook 格式 decision:block 在現行版本認不認未實測(現行文件=permissionDecision:deny+exit 2)
  DEP:scripts/usage_scan.py(唯讀儀器)、governance/review-reports/spotify-shunt-2026-09-09/(卷證:儀器輸出+shunt 原始碼節錄)
decisions:
  - content: 不立案「擋大檔 Read/Bash 改派便宜讀者」hook(Spotify shunt 形狀)——先量後裁,本 repo 14 天大檔讀取佔工具輸出 0.87%、讀法已是定點讀;形狀已抄在卷證(含 offset/limit、管線、重導三個逃生口),REVISIT 2026-10-09 重量本 repo 與消費端超線再開。待 Enzo 覆核
    id: d1
    context: Spotify 2026-09 公開 shunt:PreToolUse 擋 >350 行 Read 改派 Gemini Flash 讀者,單發讀檔省 82–94%。乾淨 agent 對過:本 repo hook 註冊表無 Read/Bash 尺寸閘。儀器 scripts/usage_scan.py 量出快取重讀 62 億 token 對比工具輸出直接進 context 280 萬、≥400K context 桶佔 81%——痛點在 session 長度不在單筆讀取
    why_chosen: 抄一個擊中面 <1% 的 hook 是虛設;既有家規(hard block > 散文)已含此教訓;真正的槓桿(壓縮門檻、模型自身輸出)另列候選待裁
    decided: 2026-09-09
    valid: true
  - content: 儀器 scripts/usage_scan.py 留下但不升格:不接進 lumos 子指令、不進 doctor、不排程;作為流程自產工作量未量測與席位成本欄回填(世界掃描 B3)的第一支能跑的零依賴量法。要不要升格等 Enzo 裁
    id: d2
    context: 席位成本欄填充率 08-22 起 37%/2%,世界掃描 B3 指出本地 session JSONL 可零依賴回填;本調研需要「先量」所以順手寫了儀器
    why_chosen: 調研的交付是判斷不是新指令;升格要走設計審,且量法(chars/4、isCompactSummary 當壓縮點)還粗,先用一個月看數字穩不穩
    decided: 2026-09-09
    valid: true
---
# Spotify-shunt吸收_調研

> 白話:Spotify 公開了他們工程師用 Claude Code 的省 token 設定(叫 Portal 的 shunt 插件):貴的模型不准直接打開超過 350 行的檔,hook 當場擋下、叫它改派一個便宜模型去讀、只拿回摘要;另一個便宜模型照範例寫樣板碼直接存檔,貴模型連看都不看。Enzo 要我調研、吸取經驗。本篇做三件事:①對照原文與原始碼,把推文講漏的部分補回來;②**先量我們自己的 token 到底花在哪**(寫了一支唯讀儀器,掃本機逐字稿);③逐條判哪些借、哪些已經有、哪些不借,附回頭條件。
>
> 結論一句話:**他們的教訓(寫規則沒用、要用 hook 擋)我們早就是家規;他們的機制(擋大檔)對我們打不到痛點——本 repo 近兩週大檔讀取只佔工具輸出的不到 1%,真正貴的是 session 拉到五十萬到一百萬 token 的 context、每一輪都要再讀一次。** 儀器留下,擋檔 hook 不立案,附一個月後重量的回頭條件。

PRIOR-ART:①最小解在「量」這一層,不在機制層——Spotify 自己的 90% 是三個單發讀檔情境的平均(chars/4 估的),不是整個 session 的帳;要不要抄得先看我們的帳長什麼樣。②世界解=shunt 本身(Claude Code 插件,PreToolUse 擋 Read 與 Bash cat 類,零伺服器)+ Claude Code 原生 Agent 工具的 model 參數(派 haiku/sonnet 子代理)+ 原生 Explore 唯讀子代理——要抄的話零新依賴。③裁定=**借用既有設計為預設,但這次先不抄機制**:量出來擊中面 <1%,抄了是虛設;借的是「量法」與「hard block 要留逃生口」這兩條設計知識。

## 一、Spotify 那套到底是什麼(對照推文 vs 原文與原始碼)

來源:部落格 `engineering.atspotify.com/2026/9/portal-by-spotify-cut-my-claude-code-token-usage-by-90`、原始碼 `github.com/spotify/portal-ai-plugins/plugins/shunt`;hook 與 skill 全文節錄在 `governance/review-reports/spotify-shunt-2026-09-09/shunt-source-extract.md`(2026-09-09 抓 main 分支)。

| 推文說的 | 原文/原始碼實際是 |
|---|---|
| 「兩個便宜助手」 | 兩個 AiKA(Spotify 內部平台)mode,模型 **Gemini 2.5 Flash**(可換),temperature 0.2,每次呼叫獨立、無狀態;經 Portal CLI 的 actions 呼叫,單次上限 180 秒、請求走命令列參數所以吃 ARG_MAX(macOS 1 MB,自設 400 KB 上限) |
| 「超過 350 行就擋」 | 兩支 PreToolUse hook:`Read` 工具看 `file_path` 行數;`Bash` 工具抓 `cat/head/tail/less/more` 開頭的指令。**逃生口三個**:Read 帶 offset 或 limit 直接放行(「Claude 已經知道它要哪一段」);Bash 有管線 `\|` 或重導 `>` 放行;檔不存在放行。門檻 350 的理由是**延遲**不是錢——委派一次來回 10–30 秒,小檔委派的開銷比省的 token 還貴 |
| 「擋下之後送給便宜的」 | 擋的訊息原文:「File is N lines (threshold: 350). Use the /bulk-reader skill to delegate this read to AiKA instead of reading it directly. If you need exact content for editing, re-read with an offset/limit for just the section you need.」——擋訊息本身就把兩條路都寫出來 |
| 「寫規則沒用、擋才有用」 | 原文:「A block of routing rules in CLAUDE.md. It sort of worked… The rules were advisory, not enforced. Claude could ignore them.」→ 搬進 hook 層;skill 只剩「讓路走得順」的角色。★但只有 bulk-reader 有 hook 強制,code-writer **沒有任何強制**,靠 skill description 讓 Claude 自己想起來★ |
| 「省 90%」 | 162K 行 Java monorepo 三個**單發讀檔**情境:4,014 行單檔 33,684→5,737 token(82%);源碼+測試對 7,408 行 75,990→4,148(94%);跨服務三檔 1,281 行 16,221→821(94%);平均 90%。token=chars/4 估的。**不是整個 session 的帳**,code-write 那格他們自己說沒法公平比 |
| 「兩件事還是貴」 | ①摘要**沒有可靠行號**,要改檔仍得定點讀原檔;②便宜模型漏了一個 thread-safety bug,Claude 幾秒抓到 → 明寫排除 debugging、架構決策、安全關鍵碼 |
| (沒說的) | 便宜讀者的系統提示:「Output structured bullets only. No greetings, no prose… Lead every bullet with the exact name, type, or line number.」——**回傳格式硬性化**是省下游 token 的另一半。只做 Claude Code,Codex/Cursor 側沒有 shunt |

## 二、先量:我們自己的 token 流向(2026-09-09,本 repo 近 14 天)

儀器:`scripts/usage_scan.py`(唯讀、零依賴,掃 `~/.claude/projects/<slug>/*.jsonl`,按 message.id 去重——逐字稿一個 content block 一行、usage 會重複,不去重會多算一倍;壓縮點以 `isCompactSummary` 判);輸出全文在 `governance/review-reports/spotify-shunt-2026-09-09/usage-scan-14d.txt`。重跑:

    python3 scripts/usage_scan.py --days 14

| 量什麼 | 數字 | 白話 |
|---|---|---|
| 樣本 | 21 個 session、12,482 次請求、23 個壓縮點 | 全是本人與自主迴圈在本 repo 的用法 |
| 每次請求的 context | p50 486K、p90 880K、最大 100 萬 token | session 常態就是拉到五十萬以上 |
| token 量按 context 大小分桶 | ≥400K 那桶佔 **81%** | 錢主要燒在「很長的 session 每輪重讀整個 context」 |
| session 開頭底盤 | p50 44K(系統提示+CLAUDE.md+skill+記憶) | 壓縮後只剩 75K → 早壓縮能省的空間很大 |
| 工具輸出直接進 context | 11.2M 字元 ≈ 280 萬 token / 14 天 | 這才是 shunt 省的那種;對比快取重讀 62 億 token |
| 工具輸出誰最多 | Bash 78%(10,628 次、單筆 p50 371 字元、最大 16.9K)、Agent 14.6%(865 次、p99 15.8K)、**Read 1.8%**(73 次) | 沒有任何一筆超過 2 萬字元;是「幾千次小輸出」不是「幾次大讀取」 |
| ≥350 行大檔讀取 | Read 50 次、97K 字元;cat/sed 類 659 次、平均 1,219 字元 | **佔工具輸出 0.87%**;最常讀的 `scripts/lumos`(23,708 行)19 次共 88K 字元=平均 4.6K,早就是定點讀 |
| 駐留成本(字元 × 之後同段內請求數) | 模型自身輸出 : 全部工具輸出 = **1.32 : 1** | 模型自己寫的長腳本、長回覆比工具吐回來的更佔 context |

粗估拆帳(chars/4,中文會偏低,只看量級):工具輸出駐留 ≈ 12 億 token ≈ 快取重讀的 19%;模型自身輸出 ≈ 16 億 ≈ 26%;**剩下約 55% 是底盤+使用者訊息+hook 注入+壓縮摘要,這一半沒再拆**。

## 三、五條經驗逐條對照

1. **「寫在 CLAUDE.md 的規則是建議,hook 才是擋」——已是家規,這是第三個獨立來源**。既有:[[Systems/效能檢核目錄]] 的 Vercel 實證(靠模型自己想起要查,56% 會跳過)、[[Projects/驗形式與驗內容_調研]] 的 arXiv 2605.14744(純文字治理 27.3% 化妝式合規)、[[Projects/工具鏈全環節體檢_調研]]「每條規則旁邊必須寫誰會擋我」。**新學到的一點是 hard block 的可活性來自逃生口**:shunt 的擋有 offset/limit 這條永遠走得通的路,擋訊息把路寫在裡面;對照我們 [[Systems/graph-sync-coverage]] 刻意不硬擋的理由(「硬擋會把人訓練成反射 `--no-verify`」)——兩邊不矛盾:沒逃生口的擋才會養出 `--no-verify`。
2. **「350 行以上擋 Read、改派便宜讀者」——不借(量出來擊中面 <1%)**。乾淨 agent 對過(原始問題丟過去,不帶結論):hook 註冊表(`scripts/merge-claude-settings.py` 的 HOOK_ENTRIES)沒有 Read/Bash 的尺寸閘;最接近的是 `lumos context` 輸出超 20KB 提醒用 `--brief`([[Systems/lumos-cli-read]] d5),`lumos show` 無上限。本 repo 的讀法已經是定點讀(sed -n 平均 1.2K 字元),一支擋檔 hook 兩週內會觸發幾十次、每次省幾千 token,對比 62 億的快取重讀是零頭。**消費端專案(Kotlin/C#/iOS)沒量**,那邊檔案結構不同,回頭條件見末段。
3. **「便宜模型照範例寫樣板碼直接落盤」——本 repo 不借,消費端另議**。理由:本 repo 的測試是合約層不是樣板([[Systems/測試假綠形態]]、合約綁測試鏈),便宜模型「照鄰居寫一份」正是假綠的溫床;Spotify 自己也承認 code-writer 沒有強制、只適合「>80% 可從參考檔預測」、產出還要 Claude 補 5–20% 判斷。既有的分級已經有一半:[[Systems/design-loop]] 範本第 157 行「計畫含完整代碼→haiku;多檔整合/寫測試→sonnet」,guard audit 刻意用較弱的 sonnet 不腦補補洞。
4. **「便宜讀者只准出結構化條列、每條帶名字/行號」——可借,零機制**。我們的子代理回報 p99 15.8K 字元、最大 19.3K,是工具輸出第二大宗。設計審範本已有「每條 finding ≤3 句」;**一般 Explore/查證派工與 code-loop 派工詞沒有回傳格式上限**。最小解=派工詞尾巴固定一句「只出條列、每條開頭是名字或路徑:行號、不要前言總結」;不需要 hook。
5. **「摘要沒有可靠行號,改檔前仍要定點讀」——我們的方向對了**。refcheck/quote-check 的錨點制(引句 ≥10 字+路徑:行號機驗)就是在防「拿摘要當事實」;shunt 的 skill 也只能寫一句「Verify specific line numbers… before using them in edits」靠自覺。

## 四、裁定與候選

- **d1 不立案「擋大檔 Read/Bash」hook**(本調研裁,待 Enzo 覆核)。要抄的話形狀已抄好在卷證(兩支 hook 共 60 行 bash,含三個逃生口),開案成本一個下午;不開的理由純粹是量出來打不到痛點。
- **d2 儀器留下**:`scripts/usage_scan.py` 是 [[Issues/流程自產工作量未量測]] 與 [[Projects/世界repo掃描2026-09-02_調研]] B3(席位成本欄填充率 37%/2%、「本地 session JSONL 可零依賴回填」)的第一個能跑的東西。**沒接進 lumos 子指令、沒進 doctor、沒排程**——要不要升格等 Enzo 裁。
- **候選 C1(便宜、建議做)**:派工範本補回傳格式硬性一句(第三節第 4 條)。改 `skills/lumos-design-loop/templates.md` 與 code-loop 派工詞;量法=改前改後 Agent 工具輸出 p99 對比(儀器 B 段)。
- **候選 C2(最大槓桿、但沒機械解)**:模型自身輸出是最大駐留源。本 session 自己就犯了三次「把三千字腳本用 heredoc 寫在對話裡」——寫進檔再跑,對話裡只剩一行指令。這是紀律,目前沒人擋;回頭條件併入末段 REVISIT。
- **候選 C3(潛在省最多、一行設定、但有代價,待 Enzo 裁)**:81% 的 token 量在 ≥400K 的 context;壓縮後底盤只有 75K。官方文件(claude-code-guide 席查 `code.claude.com/docs/en/model-config`)確認壓縮門檻可調:設定鍵 `autoCompactWindow`(100K–1M;預設依模型,Sonnet 5 約 967K——對得上我們 p90 880K、最大 100 萬的形狀,現在是撞天花板才壓)。改法三選一:

      /autocompact 500k
      {"autoCompactWindow": "500k"}   ← 寫在 settings.json
      CLAUDE_CODE_AUTO_COMPACT_WINDOW=500000

  **代價要先講**:壓縮=丟脈絡,設計審/代碼審那種一輪派八席、要對照前幾輪卷證的 session,壓早了就要重讀;所以不在本調研裡直接改(這是全機器所有 session 的設定),建議先在一個 session 用 `/autocompact 500k` 試一週,用儀器 A 段比壓縮次數與 ≥400K 桶佔比,再決定寫不寫進 settings。另兩個官方數字順手記下:Bash 輸出上限 `bashOutputMaxChars` 預設 30,000 字元(對得上我們最大 16.9K,沒撞到,不用動);子代理回報**沒有**內建長度上限,只能靠派工詞(所以 C1 的做法就是官方建議的做法)。

## 五、確認不用再看

- 「90%」不能拿來預期我們的帳降 90%:那是單發讀檔的 chars/4 估值,不含 session 駐留、不含委派本身的延遲與便宜模型的錢。
- shunt 只做 Claude Code;Codex 側我們的 PreToolUse 攔得到 Bash 與 apply_patch([[Projects/Codex完全支援_計劃]] 地基事實②),要抄也只能擋 cat 類,Codex 有沒有獨立的 Read 工具沒查。
- 便宜讀者回傳無可靠行號 → 不可能取代 Edit 前的定點讀;不用再想「全靠摘要就能改碼」。
- Explore 子代理 + Agent 的 model 參數已是 Claude Code 原生,不需要為「便宜讀者」建任何基礎設施;缺的從來不是工具,是「什麼時候該派」的判準——而那個判準要有量才立得起來。

## 六、誠實界線

- 只量了本 repo 21 個 session、14 天;消費端專案零量測。本 repo 的讀法(定點 sed)是這幾週紀律養出來的,別的專案未必。
- 駐留成本是估的(字元 × 之後請求數、chars/4),快取重讀 62 億是逐字稿裡的實際 usage 數字;兩者量級互證(工具輸出駐留 ≈ 快取重讀的 19%),但 55% 的「其他」沒拆。
- Spotify 的 benchmark 我沒重跑,數字抄自 README。shunt 的 hook 用 `{"decision":"block","reason":…}` + exit 0;現行官方 hooks 文件寫的擋法是 `hookSpecificOutput.permissionDecision:"deny"` + **exit 2**(文件明講 exit 2 才是權威、reason 會顯示給模型)——舊格式在目前版本還認不認沒實測,真要抄就照現行文件寫。
- 儀器只認 `isCompactSummary` 當壓縮點;若逐字稿格式改了,C 段駐留數字會偏。

REVISIT:2026-10-09 用 `python3 scripts/usage_scan.py --days 30` 重量本 repo 與一個消費端專案(Basic,用 --project-dir 指過去);大檔讀取佔工具輸出 ≥5%、或單筆 >20K 字元的讀取兩週內 >10 次 → 開擋檔 hook 案(照卷證形狀抄,含逃生口);≥400K 桶仍 >70% 且壓縮門檻可調 → 開壓縮時機案;C1 改了範本就對比 Agent 輸出 p99。
