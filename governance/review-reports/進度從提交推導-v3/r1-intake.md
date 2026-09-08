preflight-4: ran

# v3 r1 前掃留痕(折入後快照指紋 92621f8fd5aba60582fc25bdd966d8d9c2df881db5523f810d89a64c70dc67f6,     227 行)

## ④ 不屬實已改(3)
1. **「重用 impact 的計劃→檔關聯」=空前提**(與 v2 死掉的「重用既有抽取」同型,作者自己點名懷疑)。`cmd_impact` 是檔→節點;真正做計劃→檔的是 `cmd_dispatch_lens_spec`(`_LENS_SPEC_CODE_RE`),且它本身就是正則抽取非語意對應。→ [S3] 改重用那支並標明其性質。
2. **fail-open 描述不準**:原稿「非 0 即靜默、一個 try/except 包住」;實際三態(rc3 印一行 stderr 再放行)+ 各風險點 targeted try/except。→ 改寫。
3. **「大概」**(prose-lint 第 137 行,引述 v2 錯誤推論的句子)→ 改「應該」。

## ④ 查不到→轉前置(1)
- **PostToolUse payload 形狀**:repo 無任何程式讀過;已刪舊 hook 只讀 tool_name/tool_input.command/cwd,從未讀 file_path/tool_response。→ [S1] 加「拋棄式 dump hook 做一次 Edit 抄真實欄位」為第一步,沒做不准寫 S1。

## ④ 屬實補進設計(1)
- 既有 append-only helper `_ledger_append()`(O_APPEND|O_NOFOLLOW,rel-cascade 現役)→ [S2] 明寫重用,不自寫第二份。

## ④ 屬實不改(6)
PostToolUse 槽空 / hook payload 有 session_id、tool_name、tool_input(PreToolUse/Stop 而言)/ 三本帳無 session 維度(grep 命中全是自由文字提到 session)/ Codex 只適配三個無第四個 / usage-log 被版控且 .gitignore 無條目、程式內註記屬實 / 兩個 wikilink 內容逐字相符。arXiv 查不到(無網路),不改。

## ①③ 前掃自陳只做輕量掃描,未逐句窮舉——席位仍要掃。
## ② 零壞引用(7 個 wikilink 全存在、內容相符)。

## 補(接手席 F-hnd-6 指出)
- arXiv 2605.21997:前掃無網路查不到屬實;★編排者同日已用 WebFetch 讀過原文摘要★(tool-results 留有 736KB PDF),但**未逐頁讀原文**,與另三篇同一等級。d8 引述來自該摘要。
