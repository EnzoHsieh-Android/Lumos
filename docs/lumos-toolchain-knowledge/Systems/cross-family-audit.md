---
type: system
status: done
created: 2026-06-26
updated: 2026-07-10
self_audit: sonnet/2026-06-26
tags:
  - type/system
  - status/done
verified_by:
  - "[[Verification/2026-06-22_cross-family-audit]]"
summary: |-
  FLOW:design-loop §2 步驟8 達標(連2輪caught+sev∈{clean,minor})→§2.5 放行前複核一次：opus 取材(grep spec 引用檔/符號當 ground-truth)→調 run_cross_audit() 打 qwen3-max(refute framing)→先判 status：degraded→放行標 degraded｜ok+≤minor→endorsed 放行｜ok+≥major→qwen findings 當新一輪 audit、opus grep 驗證後折入/標反證、cross_reject_count+1 回步驟1 續審，達2→停 disputed 不放行(必伴 converged:false)
  KEY:autonomous loop design-loop 收斂判定後、放行前多一道 qwen3-max 跨家族複核，補 opus 同門盲點；不取代每輪 judge-severity-gate
  KEY:run_cross_audit 只回 status+worst_severity；cross_verdict 判定在 orchestrator(prompt 層)，scripts/lumos good() 一行不動
  KEY:fail-open——API 掛/無key/429/超時→degraded、退回 opus 單審放行並 log/LINE 標註，不卡死 loop(誠實天花板 #4：degraded 是旁路非通過)
  KEY:結果回流走 orchestrator §3 三個扁平欄位 cross_verdict/cross_worst/cross_summary→autonomous-loop.sh get() 取；不碰 build_report、不寫跨程序檔
  KEY:調用禁 python3 -m governance.autonomous_loop.cross_audit(頂層 governance 無 __init__.py)；用 sys.path.insert(0,'<REPO>/governance')+from autonomous_loop import 絕對路徑版
  DEP:governance/autonomous_loop/cross_audit.py｜orchestrator-prompt.md §2.5｜autonomous-loop.sh(L60-61/80/107)｜~/.config/ai-daily/qwen_api_key(本機,不入 repo)
  TEST:scripts/test_autonomous_loop.py 27 passed(cross_audit 單元 mock urllib)
  VERIFY:[[Verification/2026-06-22_cross-family-audit]]
decisions:
  - content: 結果回流砍掉「寫 .cross-audit.json 跨程序檔 + 改 build_report 簽名 + 加報告節」整條數據流，改 orchestrator §3 輸出三個扁平欄位 cross_verdict/cross_worst/cross_summary，autonomous-loop.sh get() 取後走既有 log+LINE
    id: d1
    context: design-loop R4 排掉 canary 後 3 個 major(報告標題層級錯亂 / $SCRATCH 跨程序歸因 / build_report 第4參 dict-vs-檔路徑型別死結)全集中在「cross_audit 回流 build_report」這條數據流，與前輪 F2 同源、反覆牽動
    why_chosen: 判定該組件為根因，簡化(非打補丁)一舉消 F-A/F-B/F-C + 前輪 F2/F4/F6；扁平欄位由 json.load 後以 shell 變數傳遞，避開字面量注入與跨程序歸因
    decided: 2026-06-22
    valid: true
  - content: 收斂條件疊加跨家族三態——endorsed=通過 / degraded=旁路放行(fail-open) / disputed=否決不放行；degraded 計入放行屬刻意 fail-open，不偽裝成「滿足要求」
    id: d2
    context: design-loop R5 F6：API 不可用時不可卡死 loop，但也不能把「複核被旁路」謊報成「通過」
    why_chosen: 三態分明讓放行的人知道這次少了一道(degraded 時 log/LINE 明標)；對齊誠實天花板 #4「degrade 時無跨家族背書」
    decided: 2026-06-22
    valid: true
  - content: disputed 出口釘死——orchestrator §3 須明文輸出 converged:false，且未收斂分支 notify 依 cross_verdict 區分「跨家族否決」vs 真撞 cap，不沿用硬編碼「撞 cap」
    id: d3
    context: design-loop R5 F2：disputed 不伴 converged:false 就走不進 wrapper 未收斂分支(L80-85)；硬編碼「撞 cap」會把 qwen 否決誤導成撞輪數上限
    why_chosen: disputed 必須真能進未收斂出口才有意義；文案區分讓人看得出是被駁回還是耗盡輪數
    decided: 2026-06-22
    valid: true
---
# cross-family-audit

autonomous loop 的 design-loop 在判定收斂、**真正放行前**多一道 **qwen3-max 跨家族複核**，補 opus 同門盲點。qwen 提出 major+ 異議則退回讓 opus 驗證；API 不可用則 degrade 回 opus 放行並標註。

源起:日報 2026-06-20 inspiration「design-loop 每輪只靠單一 judge、外部證據顯示沒有單一評審穩定可靠 → 借 RAND JRH『換模型家族＋多數決＋換句話說穩定度測試』，opus 審/judge 可能同門、自我偏好偏心風險完全沒處理」+ backlog gap[4](6/20 放棄 judge 抗自偏，結論建在『換模型家族做不到』，漏了解法)+ 2026-06-22 PoC 實證(同草稿 opus 6 輪把 `python3 -m` import 失敗只標 minor，qwen3-max 一次判 blocker)。

## 定位
- **放行前的額外關卡,不取代既有 judge**:每輪 severity 仍歸 judge-severity-gate 的獨立 opus judge;qwen 只在 design-loop 判定收斂那一刻觸發**一次**。
- **只接 qwen**(YAGNI):$0 OAuth 只路由 Claude,qwen 是唯一已驗的跨家族補充;不支援 GPT/其他家族、不本地跑、不當每輪 judge。
- **插在 orchestrator 內部**(orchestrator-prompt §2.5),不在 wrapper 層:autonomous-loop.sh 收到結果時 design-loop 已結束,退不回繼續審、也拿不到逐輪狀態。orchestrator 有 Bash/Grep/Agent 工具可取材 + 調模組。

## 關鍵機制
### run_cross_audit(模組,只回 status)
`governance/autonomous_loop/cross_audit.py`,無第三方依賴(僅 urllib)。回傳三態 dict:
- `{"status":"ok","worst_severity":<clean|minor|major|blocker>,"findings":...,"usage":...}`
- `{"status":"degraded","worst_severity":None,"reason":"no_key"}`(key 檔不存在)
- `{"status":"degraded","worst_severity":None,"reason":"http_<code>"|"timeout"|"error:..."}`(API 失敗,含 429 額度耗盡)

`worst_severity` 在 degraded 態**統一回 None**(R5 F4:免 orchestrator 無條件讀鍵 KeyError——先判 status 再讀 severity)。`_parse_worst` 先正則抓「最嚴重 severity = X」,抓不到掃內文最高者(防 qwen 沒照格式)。

### cross_verdict 判定(orchestrator,prompt 層)
模組只回 status + worst_severity;`cross_verdict` 由 orchestrator 據此決定:degraded→`degraded`(放行)、ok+≤minor→`endorsed`(放行)、ok+≥major→把 qwen findings 當新一輪 audit(opus grep 驗證每條:真的折進 spec、誤報標反證),`cross_reject_count += 1` 回步驟 1 續審,達 2 → 停 `disputed` 不放行。`cross_reject_count` 為**每次 design-loop 獨立計數**(orchestrator 上下文內變數,不跨 loop 累積;每次 autonomous-loop.sh 啟動一輪新 design-loop 時歸零)。

### 結果回流(扁平欄位)
orchestrator §3 result JSON 輸出三欄 `cross_verdict`(endorsed|degraded|disputed)/`cross_worst`(severity)/`cross_summary`(單行摘要);autonomous-loop.sh 用既有 `get()` 取(L60),`cross_summary` 換行 replace 成空格防破版(L61);收斂分支 log 一行 + LINE(L107)、未收斂分支依 verdict 區分文案(L80-85)。**不碰 build_report、不寫跨程序檔**。

### key 與調用
- key 存 `~/.config/ai-daily/qwen_api_key`(單行,**不入 repo/git**;讀不到 → degraded/no_key);走國際 endpoint `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`(國內 endpoint 回 401),OpenAI 兼容模式,`qwen3-max`、`temperature=0.2`。
- 調用**絕對路徑版** `python3 -c "import sys;sys.path.insert(0,'<REPO>/governance');from autonomous_loop import cross_audit;..."`(orchestrator cwd 未必是 REPO)。**禁 `python3 -m governance.autonomous_loop.cross_audit`**:頂層 `governance/` 無 `__init__.py`(已核實 ABSENT),雖 `autonomous_loop/__init__.py` 存在,`-m` 仍因頂層非 package 失敗。

## 落地後的真機修正(設計稿外)
端到端真打 qwen API 暴露兩處,已修(見 commit `4fd7ce2`/`7d978b9`):
- `_ssl_context()`:orchestrator PATH 優先的 homebrew python 常無 cert(`ssl cafile=None`)→ `CERTIFICATE_VERIFY_FAILED`;探測系統/certifi cert bundle 修之。
- `_parse_worst`:容忍 markdown 粗體 severity(`**major**`),正則加 `\*{0,2}`。

## 已知限制(誠實天花板)
- **qwen 也是 AI**:跨家族**降低**共同盲點 ≠ 消滅「AI 評 AI」回歸,只把回歸推遠(兩家族都漏才漏),非 oracle。
- **opus 取材 = opus 框定 qwen 視野**:opus 漏 grep 的檔/符號 qwen 照樣盲;視野上限由取材者決定。
- **degrade 無跨家族背書**:API 掛/額度盡退回 opus 單審,log/LINE 標 degraded,讓放行的人知道少了一道。
- **計費未閉環**:免費額度靜默耗盡(429)會讓跨家族長期失效而 loop 照跑,須靠 console 監看餘額(本機制不自動查)。
- **prompt 層自律張力**:cross_summary 單行、先判 status、verdict 判定都靠 orchestrator LLM 自律,與本專案『別信 LLM 自填』(judge-severity-gate 斷開自填)精神有張力;已加防呆(degraded 統一 None、summary strip 換行)降低,但 verdict 判定**未完全斷開**。
- **放行=人 merge,絕不自動**:本機制只是「多一個不同家族的眼睛」,放行的人仍是最後也唯一真兜底。

## 相關
- 設計稿:`docs/design/2026-06-22-cross-family-audit.md`(2026-06-22 design-loop 6 輪、canary 6/6 全 caught、達 cap 6 未自動收斂,剩 F2/F4 文檔級無 blocker、人工定稿放行)。
- 實作計畫:`docs/superpowers/plans/2026-06-22-cross-family-audit.md`。
- 實作落點:`governance/autonomous_loop/cross_audit.py`、`orchestrator-prompt.md §2.5`、`autonomous-loop.sh`(L60-61/80-85/107)。
