A  
verdict=concern  
severity: minor  
blocking: 否  
引句:「lines += ["", f"不一致題 with: {', '.join(a['inconsistent_questions']) or '—'};without: {', '.join(b['inconsistent_questions']) or '—'}"]」  
file: `governance/eval/ablation_lumos_first.py:410`  
evidence=確實違反計劃對題號轉義尖括號的承諾，見 `docs/lumos-toolchain-knowledge/Projects/探針隔離與清理收斂_計劃.md:119`，所以不是 clean。但現有程式只把 Markdown 寫入本機、印到終端，見 `governance/eval/ablation_lumos_first.py:481-484`；計劃也把「其他程式消費 summary.md」列為未來才需增設邊界的入口，見同計劃 `:130`。原始輸出目錄不入版控，見 `.gitignore:16-17`。題號來自本 repo 題庫，meta 來自本機輸出，正常檔名又是題號雜湊，見 `governance/eval/ablation_lumos_first.py:61-74`、`:238-242`、`:416-443`。目前沒有可核查的瀏覽器渲染或外部不可信輸入鏈，三條均應降為 minor。  
concern=日後若 summary.md 上線到會保留原始 HTML 的自動渲染器，或題庫／meta 改由不可信來源提供，需重新升級評估；目前證據只證明 Markdown 內容注入，未證明腳本在既有消費面執行。

B  
verdict=agree  
severity: major  
blocking: 是  
引句:「for p in _result_json_files(out_dir):」  
file: `governance/eval/ablation_lumos_first.py:218`  
evidence=這是舊缺口，不是本輪新回歸：凍結 patch 同時顯示修補前後都只掃傳入的單一 `out_dir`，見 `governance/review-reports/code-probe-postreview-dispatch-ledger/r3-snapshot.patch:168-177`。但它仍是明確條款違反：CLI 對外聲稱「五小時內最多開幾場」，見 `governance/eval/ablation_lumos_first.py:495-496`；預設路徑卻每日切目錄，見 `:511-512`。S18 也要求五小時窗口達限後不再啟動模型，見 `docs/lumos-toolchain-knowledge/Projects/探針隔離與清理收斂_計劃.md:144`。跨午夜是正常預設路徑，最多可重新取得整個窗口額度，故維持 major。  
concern=處置時應標成「本輪未補上的既有缺口／新 S18 未完整落地」，不能記成修補所引入的 regression。

C  
verdict=concern  
severity: minor  
blocking: 否  
引句:「if p.name.startswith(("with-", "without-"))」  
file: `governance/eval/ablation_lumos_first.py:158`  
evidence=`with-notes.json` 確實違反 S17「無關 JSON 不當探針事故」，見 `docs/lumos-toolchain-knowledge/Projects/探針隔離與清理收斂_計劃.md:143`。實際影響是 fail-closed：健康掃描在派工前阻止模型啟動，見 `governance/eval/ablation_lumos_first.py:444-448`；最後標不可採信並回 3，見 `:470-485`。它不會混入統計或產生假綠，只造成專用輸出目錄暫停，移走誤命名檔即可恢復，因此降為 minor。  
concern=這仍是 S17 的不完整修補，應把檔名範圍收至真實 `with-q-*`／`without-q-*` 與合法舊 shard；不能因降級而宣稱條款已滿足。

總結：最嚴重 severity major；blocking 1 條。
