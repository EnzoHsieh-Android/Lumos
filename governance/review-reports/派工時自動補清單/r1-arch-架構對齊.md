# r1 席報告:架構對齊(sonnet,不佔人數)

## 問一 分層與依賴方向:概念對齊,落點與呼叫機制材料空白(⚠)
概念層對齊:spec 定位為既有 PreToolUse 位置的第二個消費者、把 lumos impact 當黑盒 subprocess,
與 impact-hook.py、check-graph-sync.py 的 `_impact_missing` 同一依賴方向。
引句:「只在既有的 Claude Code `PreToolUse` hook 位置,把既有的 `lumos impact --diff` 輸出接進既有的派工路徑。本 repo 已有一支同位置的 hook」
⚠ 但具體放哪個檔、怎麼呼叫 lumos,材料完全沒講。四支既有 hook 一致住 `scripts/hooks/claude/*.py`,
由 `_sync_global_claude()` 複製到 `~/.claude/hooks/`(`scripts/lumos:11052-11065`);
呼叫一律 `shutil.which("lumos")` 優先、repo-relative 兜底。
spec 全篇零命中 `scripts/hooks/claude`、`subprocess`、`~/.claude/hooks`。
判不準(材料空白非矛盾),交編排者要求補件。

## 問二 ★安裝分發不對齊:疑似自造第二套,且引入 jq 外部依賴★
severity: major
blocking: 是
錯誤處理對齊(fail-open 慣例一致),不計。
但 repo 已有現成合併器 `scripts/merge-claude-settings.py`,它已做到 spec 要求的每一條:
寫入前備份(`:198-202`)、逐 event 只 append(`:165-179`)、`_equivalent()` 判重(`:132-140`)、
懸空註冊自動偵測與清理 `_prune_dangling()`(`:99-124`)+ 兩階段撤除(`scripts/lumos:11020-11045`)。
新 hook 進場的既有慣例=加進 `_GLOBAL_CLAUDE_HOOKS`(`scripts/lumos:11017`)+ 在 `HOOK_ENTRIES` 補條目
(`scripts/merge-claude-settings.py:33-96`,四支現役各一條)。
★spec 對這整套隻字未提(全部零命中),卻自述一套流程並宣稱實測走過★;
且 `jq` 在全 repo 找不到任何實際呼叫(唯一命中是測試斷言名稱,驗證邏輯其實是 Python `json.loads`),
而房規明寫「零依賴」「採用新依賴幾乎不選」——★引入 jq 這個外部二進位依賴且繞過現成合併器,是造第二套★。
引句:「安裝時**先備份再合併**,合併後立刻 `jq -e` 驗證 JSON 合法且抓得到新增那條」
引句:「這三條在 2026-09-03 的實測裡已經實際走過一遍並驗證過,不是紙上規劃」

## 問三-1 ★updatedInput vs additionalContext:全案優先度最高的一條★
severity: major
blocking: 是
impact-hook.py 是同事件、同樣消費 lumos impact 的鄰居,它的選擇是寫進圖譜的 DECISION、
且經 design-loop 多輪收斂才定案;程式 docstring 也把那句話當合約。
引句(鄰居決策):「hook 永不 block、永不改 permissionDecision」
(`docs/lumos-toolchain-knowledge/Projects/主動影響幅度偵測_計劃.md:26`;
 `scripts/hooks/claude/impact-hook.py:394-401`)
本 spec 選相反的路,連 permissionDecision 都明寫回 "allow":
引句:「回 `hookSpecificOutput.updatedInput` **可以改寫派工詞**」
引句:「本案唯一允許的回傳是 `permissionDecision:"allow"` 加 `updatedInput`」
★材料全篇只比較「PreToolUse vs SubagentStart」(哪個攔截點拿得到派工詞),
沒有一處比較「additionalContext vs updatedInput」★——沒測過也沒論證為什麼既有、已過審的做法不夠用。
這是「引入第二種做法且未交代」的教科書案例。
(旁註不影響判定:additionalContext 若確實無法投遞進「新派出的子代理」自己的上下文,
 那會是站得住的技術理由——但★材料裡完全沒寫★,審查只能對材料判,不能替材料補理由。)

## 問三-2 ★錨點保護清單:與既有明文決策相反★
severity: major
blocking: 是
現行 `ANCHOR_FILES`(`scripts/lumos:11404-11410`)只有五項,清一色 git 側裁判檔;
`scripts/hooks/claude/*.py` 四支一支都不在(`governance/anchor-baseline.json` 印證)。
★這不是疏漏是明文決策★——最貼身的鄰居在自己的實作計畫裡討論過同一問題,結論是不加:
引句(前案原文):「本 impact hook **比照現有 claude/ hooks 現況:預設不 anchor**」
(`docs/lumos-toolchain-knowledge/Projects/主動影響幅度偵測_實作計畫.md:211`)
spec 沒引用、沒反駁、沒交代「為什麼這支例外」就直接對沖這條先例。
且 ANCHOR_FILES 是對 repo 內受 git 追蹤的檔做 hash 校驗,而真正在跑的副本在 `~/.claude/hooks/`
(全域、不受版控)——★spec 沒處理「錨進去的是 repo 那份,還是機器上實際執行的那份」這個覆蓋落差★,
就宣稱這是硬約束能解掉的問題。
引句:「★這支 hook 必須納入,否則本案是在自己身上開一個後門★。這是硬約束,不是提醒」

不對齊共 3 條,其中 major 3 條。
