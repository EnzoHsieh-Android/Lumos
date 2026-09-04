---
type: project
status: done
created: 2026-09-02
tags:
  - type/project
  - status/done
  - scope/governance
related:
  - "[[Projects/世界repo掃描2026-09-02_調研]]"
  - "[[Systems/lumos-cli-lifecycle]]"
  - "[[Systems/reversibility-governance-ledger]]"
summary: |-
  FLAG:DECISION
  KEY:立案(2026-09-02,GPT 外審建議 P1 過決策帳後採納)——新增唯讀指令 lumos enforcement:把各層防護「現在到底有沒有生效」匯總印一行,治「大量 fail-open→畫面看似裝好、其實某層沒生效、使用者不知道」的盲區。與痛點「機制有在跑但沒人知道它在」同源
  KEY:為什麼採這條(六條 GPT 建議對完決策帳後)——①真新(圖譜零筆、指令不存在)②低成本(純唯讀匯總,偵測邏輯多半現成:_version_nudge/cmd_anchor_verify/settings.json parse/hooksPath 偵測)③對症(fail-open 是刻意設計,代價正是「看不出哪層沒生效」)。其餘五條:拆檔=2026-07-29 已裁緩辦(單人期回報<風險);manifest=體檢#7 已知病但併拆檔大工程風險;presence→relevance=既有刪除守衛已在做;/tmp log=minor 同探針那條;裁判定位=講法建議已採
  KEY:偵測九層(各自 try 包住,一層壞不拖垮整份;fail-open 本身要能被觀測)——①SessionStart 入口 hook ②PreToolUse impact hook ③Stop 圖譜同步 hook(三者查 ~/.claude/settings.json 註冊)④pre-commit ⑤pre-push(查 core.hooksPath→scripts/hooks + 檔存在可執行)⑥python ⑦vendored 版本(_version_nudge:None=最新/不可達、str=落後)⑧CI workflow(.github/workflows/ci.yml)⑨anchor baseline(cmd_anchor_verify)
  KEY:三態誠實——active/inactive/unknown;GitHub required status check、branch protection 本機測不到=unknown(不假裝 green 也不算 red);"Effective protection: N/M active(K unknown)" 分母排除 unknown
  KEY:design-loop 跳過(小改動,此處註明)——純唯讀狀態匯總、不動任何判定/寫入/合約;核心 enforcement_status(root,home) 抽純函式走測試先行(9 層各構造 active/inactive/unknown 案例);零合約邊界
  KEY:2026-09-04 Codex完全支援 S0 加 9 列:codex-hook:×5(值域 registered-trust-unknown|degraded|inactive|unknown,★永不 active——信任狀態本機讀不到★,summary 分母排除)、codex-cli(印版本,地基實測在 0.144.1)、claude-skills/codex-skills、agents-md(區塊在且版本戳=CLAUDE.md);★沒 ~/.codex 的機器全列 unknown(不適用)★,入口 hook 才不會每 session 唸;偵測只看 ~/.codex 目錄不看 PATH(跟 HOME 隔離測試一致)
decisions:
  - content: 六條 GPT 外審建議對決策帳後,只採 lumos enforcement 這條現在做;其餘緩辦/已有/minor
    id: d1
    context: GPT 讀 code+hook 生的實作層建議六條,品質好但沒對決策帳,把 2026-07-29 已裁緩辦的「拆檔」當 P0 端上
    why_chosen: enforcement 真新+低成本+對症(fail-open 盲區);拆檔維持緩辦(單人期);manifest 併拆檔風險;relevance 既有守衛在做;/tmp minor;裁判定位純講法已採
    decided: 2026-09-02
    valid: true
---
# enforcement儀表板_計劃

> 白話:這套大量用 fail-open——找不到 python、CLI、環境不全就靜默放行,先讓人能工作、CI 當後盾。好處是治理工具一壞不會全公司不能 commit;副作用是**使用者看不出現在到底有幾層防護真的在生效**。畫面看似裝好,其實可能 hook 沒註冊、pre-push 不在 hooksPath、CI 不存在、anchor 失效。`lumos enforcement` 就是把這些各自查一遍、印一行「現在幾層在守」。

PRIOR-ART: ①最小解層級——新唯讀子命令,偵測邏輯多半複用既有(`_version_nudge`/`cmd_anchor_verify`/`~/.claude/settings.json` 解析/`core.hooksPath` 偵測),不新建機制、不動判定。②世界解過沒——GPT 外審建議(讀 code 生),形狀近 `doctor` 但聚焦「防護生效程度」而非「圖譜一致性」;業界同類=健康檢查/self-test 指令。③裁定=borrow-design,零依賴原生實作。

## 偵測九層(各自 try 包住,fail-open 本身要能被觀測)

| # | 層 | 偵測法 | 三態 |
|---|---|---|---|
| 1 | SessionStart 入口 hook | ~/.claude/settings.json 有 lumos-entry-hook.py 註冊 | active/inactive |
| 2 | PreToolUse impact hook | 同上 impact-hook.py | active/inactive |
| 3 | Stop 圖譜同步 hook | 同上 check-graph-sync.py | active/inactive |
| 4 | pre-commit | core.hooksPath→scripts/hooks 且 scripts/hooks/pre-commit 存在可執行 | active/inactive |
| 5 | pre-push | 同上 pre-push | active/inactive |
| 6 | python | shutil.which/sys.executable | active/inactive |
| 7 | vendored 版本 | `_version_nudge`:None=最新或不可達、str=落後 | active/degraded/unknown |
| 8 | CI workflow | .github/workflows/ci.yml 存在 | active/inactive |
| 9 | anchor baseline | `cmd_anchor_verify`==0 有效、baseline 缺=inactive | active/inactive/degraded |

★unknown 誠實留白★:GitHub required status check、branch protection 本機測不到,列 unknown,不假裝 active 也不算 inactive。輸出末行 `Effective protection: N/M active(K unknown)`,分母排除 unknown。

## 誠實界線

- 這指令回答「這些層有沒有裝/接上」,不回答「它們判得對不對」——後者是各層自己的事(anchor 只證裁判沒被動、不證測試寫得對)。
- 本機測不到遠端 GitHub 設定(required check/branch protection),那兩項恆 unknown;要真查得接 gh API,本案不做(零依賴+離線可跑優先)。
- 純唯讀,不改任何狀態;跟 doctor 一樣 fail-open,自己壞也只印該層 unknown,不炸。

## 測試策略(先紅後綠)

`enforcement_status(root, home)` 抽純函式回 `[{layer,status,detail}]`;測試對 9 層各構造 active/inactive/(unknown) 的臨時 root+home 目錄,斷言狀態;CLI 包一層印表格+算 N/M。design-loop 跳過(唯讀匯總、零判定/寫入/合約邊界,見 summary)。

## 交付(2026-09-02)

- `lumos enforcement` [--repo --json] 已實作:`enforcement_status(root,home)` 純函式回九層+遠端 unknown 一列、`enforcement_summary` 算 N/M、`cmd_enforcement` 印表。複用 `_version_nudge`/anchor baseline sha 比對/settings.json 解析/core.hooksPath 偵測,零新機制。
- 偵測邏輯抽純函式、收 root/home 可注入;測試 `t_enforcement_all_active`/`_all_inactive`/`_summary_excludes_unknown`/`_never_raises_on_missing`(4 案 15 檢)全綠。
- README 與 README.en「強制力從軟到硬」表下各補一段(fail-open 副作用 + 這指令補的盲區)。
- ★實跑自驗:本 repo 跑 `lumos enforcement` = 8/9 active、1 unknown(遠端檢查)、anchor 那層當下 degraded 因 test_lumos.py 加了測試未重簽——正是它該抓的訊號,推送前 anchor approve 解除。★
- design-loop 跳過(唯讀匯總、零判定/寫入/合約);走測試先行。

## 代碼審(2026-09-02,standard 兩輪)

standard tier(pre-push 不擋,仍照紀律審)。loop=code-enforcement,卷證 governance/review-reports/code-enforcement/。
- **r1**(一席):抓 3 major——①hook 只查註冊沒查目標 .py 檔在不在(懸空註冊假綠)②漏檢第四支 hook ci-status ③`_version_nudge` 回 None 有四種情境全當 active(沒裝 lumos 的專案假綠)+ 4 minor。全折。
- **r2**(新席複核):#1#2 修好;#3 只修一半——「來源 clone 不可達」與「真的最新」都回 None、仍假綠(乾淨機器/CI 沒 clone 時顯示綠燈)。已補:偵測來源可達性,不可達→unknown;兩分支各加測試。
- 三態最終:active/inactive/degraded(懸空 hook、anchor sha 不符)/unknown(無 CLAUDE.md、無版本戳、來源不可達、遠端設定)。degraded 計入分母不計 active(懸空 hook 不會真執行防護=沒生效)。
- 測試:8 案(含懸空 hook→degraded、無 CLAUDE.md→unknown、來源不可達→unknown、版本相等→active、anchor 不符→degraded、缺目錄 11 列不炸)。
- ★上線後一致性守衛(2026-09-02)★:新指令觸發 8 條同步守衛翻紅——指令索引(commands/04)補 enforcement 行、五份文件命令數 64→65、slim 掃描白名單加「enforcement」散文假陽性(英文詞撞指令名,同 playwright install 先例)。全補齊。這正是「加一個頂層指令」的散落列舉稅(體檢 #7 那型),被守衛如實抓到。
## 自動觸發(2026-09-02,補「記得才有用」的洞)

> Enzo 一句「這個指令,也是記得才會有用」——唯讀指令本身犯了它想抓的病(不被機械觸發=裝飾)。

把 enforcement 搭進 SessionStart 入口 hook(`scripts/hooks/claude/lumos-entry-hook.py`):每個 session 開頭自動跑 vendored `lumos enforcement --json`,**只在有 inactive/degraded 時追一行、全綠或只剩 unknown 靜默**(unknown 本機修不動,如遠端 GitHub 設定,不 nag)。抽純函式 `_enforcement_alert(rows)` 走測試先行。

★繞不過的極限(誠實)★:若連 SessionStart hook 自己都沒裝,這條自動線也不會觸發——抓不到「自己完全不存在」(雞生蛋)。能抓的是**部分漂移**(hook 裝了但 pre-push 掉/anchor 過期/CI 被刪),那是實務最常見的。整台全沒裝靠人發現 hook 從不響或 bootstrap。★CI 不是觸發點★:CI 沒有本機 ~/.claude,看不到本機裝設,enforcement 本質是本機/每人一份的事。
- 自動觸發代碼審(code-enf-autohook,standard 一席)抓 2 major:①內部 subprocess timeout 20s 大於外層 hook 10s 天花板→卡住會被 SIGKILL 吃掉核心提醒(降 3s);②fail-open 分支零測試(補 exit1/非JSON/真逾時三分支)。均修訖,逾時測試真跑滿 3s 驗優雅降級。報告 governance/review-reports/code-enf-autohook/。
