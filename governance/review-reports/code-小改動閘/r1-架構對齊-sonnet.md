severity: blocker

## F1
severity: major
blocking: true
引句:「_BOOKKEEPING_RE = re.compile(r"^(docs/\.[^/]+\.jsonl|governance/|\.lumos/)")   # 帳本、卷證、設定:不算擴散也不算量」

這批在 scripts/lumos 新開了第二套「簿記檔判準」。既有那套是 `_BOOKKEEPING_FILES`(逐檔列舉的白名單元組,見 `file: scripts/lumos:18436`)加 `_BOOKKEEPING_DIR = "governance/code-loop/"`(`file: scripts/lumos:18449`),它們上面的註解已經明講「單一源,兩個消費者……兩處分開寫過會漂移」(`file: scripts/lumos:18432`)。這批完全沒碰那兩個既有常數,自己開了個正則涵蓋範圍不同(`_BOOKKEEPING_RE` 收整個 `governance/` 目錄與任何 `docs/.*.jsonl`,但既有白名單是逐檔列名,兩者範圍不等價——比方 `governance/code-loop/` 是靠 `_BOOKKEEPING_DIR` 這個字首而不是正則收的)。這正是專案自己記錄過的事故形狀重演一次:同一件「哪些檔算簿記檔」被寫成第三份定義,分岔時沒有東西會翻紅。

## F2
severity: major
blocking: true
引句:「ab = _j.loads((rr / "governance" / "anchor-baseline.json").read_text(encoding="utf-8"))」

既有讀 anchor-baseline.json 已有唯一入口慣例:常數 `_ANCHOR_BASELINE_REL = "governance/anchor-baseline.json"`(`file: scripts/lumos:16489`)加對應解析寫法 `data.get("anchors") or {}`(`file: scripts/lumos:17763-17765` 的 `cmd_enforcement`/`enforcement_status`)。這批自己手寫路徑字串 `"governance" / "anchor-baseline.json"`,不用那個常數,而且解析寫法也不同:`ab.get("anchors") or ab if isinstance(ab, dict) else {}`(patch 行:`anchors = {nfc(str(k)) for k in (ab.get("anchors") or ab if isinstance(ab, dict) else {})}`)——同一份檔案現在有兩套「怎麼讀」,路徑字串跟解析邏輯都各自一份,跟既有 anchor 讀取慣例不一致。

## F3
severity: blocker
blocking: true
引句:「if str(e.get("ts", "")) < cutoff or not e.get("plan"):」

這支 repo 已經有專門處理「時間戳字串比較」的共用函式 `_loop_ts_key`,而且旁邊的既有註解就寫著這條規矩是被架構對齊席抓出來的:「比對走 _loop_ts_key 換算 UTC(r1 單reviewer:字串比日期會依記帳機器時區判不同)」(`file: scripts/lumos:5121`)。這批的 `_small_change_check` 算「近 escape_days 天有沒有逃逸」時,直接對 `e.get("ts")`(isoformat 字串,可能帶不同時區位移)跟 `cutoff`(同樣是 isoformat 字串)做裸字串比較,沒有經過 `_loop_ts_key`。這正是同一支檔案裡已經被抓過、寫進註解提醒「別再犯」的那個錯誤形狀,在同一次改動裡重犯——不同記帳機器時區不同時,這條「近期逃逸」判斷會算錯而不出聲(可能漏放行也可能漏擋)。

## 對照過的既有寫法(供參考,不是 clean 結論)
- 既有 git subprocess 呼叫慣例(`git -C <root> -c core.quotePath=false ... errors="replace"`,`file: scripts/lumos:4977,5756,8543`)這批的 `_small_change_check` 在 `subprocess.run(["git", "-C", str(rr), "-c", "core.quotePath=false", "diff", "--numstat", git_range, "--"], ...)`(patch 行 172)寫法一致,沒有違例。
- `_plan_system_links` 的兩種呼叫方式(預設 `systems_only=True` 只看 lands_in/related、`text=` 才掃正文)這批分別在算落點允許清單與算 Issues 連結時各自正確對應到函式自己文件寫的兩種既有用途(`file: scripts/lumos:5258-5259` docstring),沒有另開平行函式。
- `_impact_home_map`/`_nodehome_key` 沿用既有函式,沒有繞過或重刻(`file: scripts/lumos:5629,5633` 與既有 `file: scripts/lumos:5579,5581` 寫法一致)。
