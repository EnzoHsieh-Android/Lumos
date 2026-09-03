# r1 架構對齊審查——派工鏡頭注入

被審材料:`/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/26a6b57a-9efc-4073-b845-c27e42a2fbb1/scratchpad/派工鏡頭注入-r1.md`(= `governance/review-reports/派工鏡頭注入/r1-snapshot.md` 同內容凍結版)
對照鄰居:`scripts/hooks/claude/impact-hook.py`、`scripts/hooks/claude/lumos-entry-hook.py`、`scripts/hooks/claude/ci-status-hook.py`、`scripts/hooks/claude/check-graph-sync.py`、`scripts/merge-claude-settings.py`、`scripts/lumos`(`_GLOBAL_CLAUDE_HOOKS` ≈:11017、`_print_sync_nudge` ≈:16455)、`docs/lumos-toolchain-knowledge/Projects/主動影響幅度偵測_計劃.md`

判定範圍只問「跟既有做法一不一致」,不判 bug、不評風格好壞。

---

## 問一:分層與依賴方向

新 hook 放的層跟鄰居完全一樣:住 `scripts/hooks/claude/`,由 `PreToolUse` 事件觸發(file: `派工鏡頭注入-r1.md:63`「1. **觸發**:`PreToolUse`,matcher `Agent`」);鄰居 `impact-hook.py` 同事件、不同 matcher(`Edit|Write|MultiEdit`,file: `scripts/merge-claude-settings.py:68`)——這正是設計自己在 PRIOR-ART 段主張的對照(file: `派工鏡頭注入-r1.md:40`)。誰呼叫它:跟四支現役 hook 一樣,由 Claude Code 的 hook 派發機制呼叫,不是誰 import 它。它呼叫誰:設計寫「跑 `lumos impact --diff <範圍> --json`」(file: `派工鏡頭注入-r1.md:64`),與 `impact-hook.py` 用 `subprocess.run([sys.executable, lumos, "impact", ...])` 呼叫 lumos CLI 的模式一致(file: `scripts/hooks/claude/impact-hook.py:473-484`)——沒有直接 `import scripts/lumos` 之類的跨層直呼跡象。單就「hook 放哪層、找誰要資料、誰觸發它」三件事看,不對齊之處查無。

★但★ 這支 hook 跟宿主(Claude Code)之間的「輸出契約」用了一種鄰居從未用過的通道——這件事嚴重到本身該算「這支 hook 在整條呼叫鏈裡站的位置跟鄰居不一樣」,詳細判定放在問三(f1),此處不重複記分,只點出:問一「誰呼叫誰」層面本身乾淨,問題出在「hook 回給宿主什麼」這一環。

## 問二:命名與錯誤處理

**退出碼協定 / stderr 訊息方式**:鄰居的一致做法是——技術性失敗(lumos 找不到、subprocess 逾時、JSON 解析壞掉)一律**純靜默** fail-open,不印任何東西;只有「有意義的內容」(如 `impact-hook.py` 的 rc=3 vault 找不到)才印一行 debug。原文明講「其他非 0 → fail-open 純靜默」(file: `scripts/hooks/claude/impact-hook.py:498-500`),`lumos-entry-hook.py`/`ci-status-hook.py` 的失敗分支也都直接 `return 0`、不印字。本案設計卻寫「算不出、超時、不是 git repo、lumos 不在——原樣放行,**stderr 印一行**(白話三段式)」(file: `派工鏡頭注入-r1.md:66`),把原本鄰居刻意留白的技術性失敗也一律發聲——這是錯誤處理的「發聲門檻」跟鄰居不一樣(不是結構性差異,鄰居也有 stderr 這條路,只是觸發條件收得更窄)。見下方 f2,minor。

**訊息措辭格式**:本案的固定標頭走 Markdown 語法 `## [lumos 自動附加] 本次改動的固定席節點`(file: `派工鏡頭注入-r1.md:65`)。四支現役 hook 注入或印出的文字(`build_ranked_context`/`build_additional_context`/SessionStart 訊息/CI 紅燈訊息)全部是純文字條列,沒有一處用 `##` 開頭或方括號代號前綴(對照 file: `scripts/hooks/claude/impact-hook.py:342-343`「必看——這 {len(pins)} 篇帶著不能破壞的合約或出過事故的筆記:」、file: `scripts/hooks/claude/lumos-entry-hook.py:108-109`)。這個標頭格式在同一天的姊妹計劃(`派工時自動補清單_計劃.md`)裡有先例,不是本案憑空發明,但相對「四支已上線 hook 現在的寫法」仍是新格式。見下方 f3,minor。

**命名慣例(hook 檔名)**:判不準——全篇沒有提出這支 hook 的實際檔名(逐字搜過 `.py`,唯一命中是既有的 `impact-hook.py`、`merge-claude-settings.py`,見審材本身無新檔名字串)。四支現役 hook 的命名慣例是「動詞/名詞短句 + `-hook.py`」或描述性全名(`impact-hook.py`/`lumos-entry-hook.py`/`ci-status-hook.py`/`check-graph-sync.py`),沒有名字就沒法判「跟鄰居一不一樣」。見下方 f4,⚠。

**timeout 處理**:設計有明確承接鄰居的教訓——「內層 subprocess timeout 必須明顯小於外層宣告(本 repo 栽過同款:內層 20s > 外層 10s)」(file: `派工鏡頭注入-r1.md:66`),這跟 `lumos-entry-hook.py` 的 `_enforcement_line`(內層 3s vs 外層宣告 10s,file: `scripts/hooks/claude/lumos-entry-hook.py:74-79`)是同一條紀律、同一個心智模型,只是沒給出本案的具體秒數——原則對齊,不算不對齊。

## 問三:第二種做法

安裝路徑:沒有引入新的。設計明講「住 `scripts/hooks/claude/`,加進 `_GLOBAL_CLAUDE_HOOKS` 與 `HOOK_ENTRIES`,由既有合併器安裝」(file: `派工鏡頭注入-r1.md:67`),對照 `scripts/lumos:11017` 的 `_GLOBAL_CLAUDE_HOOKS` 元組與 `scripts/merge-claude-settings.py:33-96` 的 `HOOK_ENTRIES` 字典——走的是同一條路,沒有新流程、沒有新二進位。

截斷規則:沒有引入新的。設計明講 cap 值「沿 `_print_sync_nudge` 的預設 8」(file: `派工鏡頭注入-r1.md:40`,亦見 d9 段 `派工鏡頭注入-r1.md:58`),對照 `scripts/lumos:16455` `def _print_sync_nudge(sync, diff_range, cap=8):`——直接借用既有數字與規則,不是自創一套。

★但★ **注入通道本身是一套鄰居沒有的新機制**:四支現役 hook(尤其是同樣攔 `PreToolUse` 且同樣呼叫 `lumos impact` 的 `impact-hook.py`)全部只用 `hookSpecificOutput.additionalContext`,而且明文自我約束「永不 block、永不改 permissionDecision」(file: `scripts/hooks/claude/impact-hook.py:397`;同一句也逐字寫進 `docs/lumos-toolchain-knowledge/Projects/主動影響幅度偵測_計劃.md:26`「DECISION:hook 永不 block、永不改 permissionDecision」)。本案卻改走 `hookSpecificOutput.updatedInput` 直接改寫派給子代理的 `tool_input`——設計自己也承認這是差異點(file: `派工鏡頭注入-r1.md:59`)。這不是「調個參數」的差異,是專案裡目前**唯一**一種讓 hook 侵入工具呼叫內容本身的做法,而且四支鄰居沒有一支這樣做過。詳見 f1,major。

---

### f1

updatedInput 改寫 tool_input 是專案裡第一次出現的 hook 輸出通道,跟現役四支 hook 統一只用 additionalContext、且明文承諾「永不改 permissionDecision」(也隱含不碰 tool_input 本身)的既有做法不一致。是否有正當理由(additionalContext 到不了子代理)不在本審查範圍內判——那件事本身已經是「新增了一種鄰居沒有的做法」,構成第二種做法。

severity: major
blocking: 是
引句:「本案與它的差別=改寫輸入(`updatedInput`)而非只注入上下文(`additionalContext`)」
file: `派工鏡頭注入-r1.md:59`
file: `scripts/hooks/claude/impact-hook.py:394-397`
file: `docs/lumos-toolchain-knowledge/Projects/主動影響幅度偵測_計劃.md:26`

### f2

失敗一律印 stderr 一行,跟鄰居「技術性失敗純靜默、只有有意義內容才發聲」的既有慣例不一致(結構仍是 fail-open,只是發聲門檻變寬)。

severity: minor
blocking: 否
引句:「算不出、超時、不是 git repo、lumos 不在——原樣放行,stderr 印一行(白話三段式)」
file: `派工鏡頭注入-r1.md:66`
file: `scripts/hooks/claude/impact-hook.py:498-500`

### f3

固定標頭改用 Markdown `##` + 方括號代號(`## [lumos 自動附加] ...`),跟四支現役 hook 目前注入/列印的純文字條列格式不一致;同日姊妹計劃裡有先例,但相對「現在已上線的鄰居寫法」仍是新格式。

severity: minor
blocking: 否
引句:「固定標頭 `## [lumos 自動附加] 本次改動的固定席節點`」
file: `派工鏡頭注入-r1.md:65`
file: `scripts/hooks/claude/impact-hook.py:342-343`

### f4

全篇沒有給出這支 hook 的實際檔名,無法對照鄰居的命名慣例(`xxx-hook.py` / 描述性全名)判斷一不一致——判不準,交編排者裁決:若採用時沿用 `-hook.py` 慣例則無問題,若另創格式才需要重新過這一題。

severity: ⚠
blocking: 否(交編排者判)
引句:「加進 `_GLOBAL_CLAUDE_HOOKS` 與 `HOOK_ENTRIES`,由既有合併器安裝」
file: `派工鏡頭注入-r1.md:67`
file: `scripts/lumos:11017`

---

## 結論

不對齊共 4 條,其中 major 1 條。
