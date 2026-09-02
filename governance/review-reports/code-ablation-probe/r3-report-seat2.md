severity: minor

# code-ablation-probe r3 審查報告(審 r2 修正——邊界輸入+統計正確性)

單家族視角(本輪未派外家 Codex；聚焦 r2 report 列的五個查核點，逐點掃全檔+實際執行驗證，非僅讀碼)。

## 核過無誤

1. **ever_lumos 三態全檔掃描——沒有一處把 None 當 False 靜默算錯，也沒有 None 參與比較/算術炸掉。**
   讀 `ever_lumos` 的地方只有 `governance/eval/ablation_lumos_first.py:180-181`（`m2_known = [r for r in valid if r.get("ever_lumos") is not None]` / `m2 = sum(1 for r in m2_known if r.get("ever_lumos"))`）——兩處都先用 `is not None` 篩過，True/False/None 三態互不混淆。`classify_question`、`per_question`（m1）只讀 `passed`，跟 `ever_lumos` 無關；`run_one`（`scripts/scenario_probe.py`）產出的 `ever_lumos` 恆為 bool，None 只由 `backfill_limit` 對「截斷且看不到真呼叫」的舊資料回填，路徑上下游一致。

2. **M2 分母 m2_known=0 不會除零，pct 顯示對。**
   `ablation_lumos_first.py:194`：`"m2_rate": round(m2 / len(m2_known), 4) if m2_known else None` 已用 `if m2_known else None` 擋除零。實測構造「整組 valid 全 None」的情境（見下方驗證），`m2_ever=0 m2_n=0 m2_rate=None`，`render_md` 印出 `0/0 = —`，不炸、不誤導。

3. **collect_skills_health 對壞 json / 非 dict / 缺欄 / 欄位型別不對都不炸，跟 load_results 同款防禦。**
   `ablation_lumos_first.py:95-114`：`try/except Exception` 包 `json.loads`，`isinstance(d, dict)` 檢查後才 `.get`，跟 `load_results`（`ablation_lumos_first.py:75-93`）的防線一致。實測餵「非法 JSON」「合法 JSON 但頂層是 list」「合法 dict 缺 skills_health_bad」「skills_health_bad 是字串不是 list」四種壞檔，`collect_skills_health` 與 `load_results` 均不拋例外，正常回傳。

4. **backfill 對 calls 內非 list/tuple 元素、len!=2、c[1] 非字串的防禦還在，r2 沒弄丟。**
   `ablation_lumos_first.py:55-58`：`isinstance(c, (list, tuple)) and len(c) == 2 and c[0] == "Bash" and LUMOS_CALL_RE.search(str(c[1]))` 三道防禦（型別、長度、`str()` 轉型）原樣保留。實測餵 8 種畸形 calls（len 1、len 3、純字串元素、int 元素、None 元素、c[1] 是 int、c[1] 是 dict、tuple 形式的正常呼叫）全部不炸，行為符合預期（畸形跳過，tuple 正常呼叫判 True）。

5. **M4b content 篩選（`is not None`）對三態處理正確。**
   `ablation_lumos_first.py:186`：`content = [r for r in ans if r.get("answer_content_ok") is not None]` 正確排除 None、保留 True/False；分子 `m4_content_passed`（`ablation_lumos_first.py:197`）只計 True。實測構造 True/False/None 混合資料，`m4_content_n` 正確排除 None 那筆、`m4_content_passed` 正確不誤計 False 那筆。

## 附理由接受(minor，不影響本輪判定)

- **`backfill_limit` 頂部 docstring 與實作不同步**（`governance/eval/ablation_lumos_first.py:44-48`）——docstring 末句仍寫著 r1 的舊邏輯「所以只在『沒被截斷』時才重算 ever_lumos；截斷且原本標 True 的保留 True。」，但下方實作（`ablation_lumos_first.py:59-66`）已是 r2 修正後的三分支（不截斷重算／截斷可見有真呼叫=True／截斷可見無真呼叫=None），行內註解（`ablation_lumos_first.py:64-65`）有寫對新邏輯，只是**函式頂部摘要沒跟著改**，對照著讀會自相矛盾（CLAUDE.md 明白點過這種「單篇筆記內部新舊打架」的風險）。不影響執行結果（測試與實跑都驗證行為是新邏輯），純粹是文件準確性——下次有人只掃 docstring 不往下讀實作，會照著舊行為理解。建議：把第 48 行改成呼應 64-65 行的三分支敘述。

## 驗證方式

- 對五個查核點各自寫最小重現腳本直接呼叫 `ablation_lumos_first` 的真實函式（`backfill_limit`／`_arm_stats`／`collect_skills_health`／`load_results`），不是憑讀碼推論。
- 跑 `python3 -m unittest scripts.test_autonomous_loop.TestScenarioProbeAblation scripts.test_autonomous_loop.TestProbeSandboxGuard -v`：25 個測試全綠。
- 讀的是工作目錄現存檔案（已含 r2 修正、尚未 commit 的狀態），跟 r3-snapshot.patch 內容一致，非單看 patch 文字。

## 結論

r2 對五個查核點的修正在邊界輸入與統計正確性上站得住——三態語意一路貫穿到底、分母除零已擋、壞檔防禦到位、防禦性型別檢查沒被 r2 動改動弄丟。唯一發現是 docstring 與實作不同步的文件準確性小問題，不影響本輪資料/結論可信度。
