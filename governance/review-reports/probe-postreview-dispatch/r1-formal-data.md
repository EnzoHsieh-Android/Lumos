severity: major

finding D1：非例外的子程序失效沒有持久 tombstone，下一次純合併會洗掉事故。

severity: major  
blocking: 是  
引句:「先以單次原子取代釘住事故，再歸檔舊資料；歸檔中斷不能讓下次重跑吃回成功外觀。」  
file: `governance/eval/ablation_lumos_first.py:248`  
失敗場景：tombstone 只在 `subprocess.run` 拋例外時建立；子程序正常返回 rc3／rc1 但未產生結果檔時，只留下記憶內的 `stop`。  
最小重現：題目含不存在的 target `definitely/not-here.py`；首跑真 CLI 得 `rc=3`、`skills_health_poisoned=true`、但 `with-q-*.json=[]`。同目錄再加 `--merge-only`，實測變成 `rc=0`、`skills_health_poisoned=false`、`missing=1`。這違反逐次失敗留痕及人工處置前不可洗白的契約。

finding D2：持久 Markdown 摘要完全漏掉 poisoned 狀態，會把不可採信批次呈現成正常統計。

severity: major  
blocking: 是  
引句:「summary 仍產出，但失效檔不參與統計，並已標 skills_health_poisoned。」  
file: `governance/eval/ablation_lumos_first.py:395`  
失敗場景：標記只存在 `summary.json`；`render_md` 沒讀 `skills_health_poisoned`。保存或分享 `summary.md` 時，stdout 的警告已消失。  
最小重現：同目錄放一個 with 健康成功檔與一個 without fatal 檔後跑 `--merge-only`。實測 `rc=3`、JSON poison 為真，但 Markdown 無「失效／不可採信／skills_health_poisoned」，仍顯示 `M1 通過率 | 1/1 = 100.0%`。

finding D3：原子替換只保證單檔完整，meta、JSON、Markdown 三檔仍可永久停在不同世代。

severity: major  
blocking: 是  
引句:「_atomic_write_text(out_dir / "summary.json", json.dumps(s, ensure_ascii=False, indent=1))」  
file: `governance/eval/ablation_lumos_first.py:356`  
file: `governance/eval/ablation_lumos_first.py:394`  
失敗場景：`meta.json` 在派工前先換，之後 `summary.json` 與 `summary.md` 再各自替換；程序中斷沒有世代識別或提交點。  
最小重現：預置三份 `OLD_*`，以 `unittest.mock.patch` 讓 `_atomic_write_text` 只在寫 `summary.md` 時拋 `OSError`，再跑 merge-only。實測 `meta_is_new=true`、`json_is_new=true`、`md_still_old=true`。既有 18 項 postreview 測試全綠，但抓不到跨檔世代分裂。

finding D4：`--arms` 未封閉值域或去重，同一題同一臂可在單路派工中排兩次並雙重計分。

severity: major  
blocking: 是  
引句:「for arm in a.arms.split(","):」  
file: `governance/eval/ablation_lumos_first.py:364`  
失敗場景：jobs 在任何結果落地前一次算完，`--arms with,with` 會加入兩個完全相同工作；後續 merge 又不按 `runs` 截斷。  
最小重現：以寫出一列健康結果的 stub `run_job` 執行 `--runs 1 --arms with,with`。實測 jobs 為 `[("with","a",1), ("with","a",1)]`、退出 0，而摘要宣告 `runs=1` 卻得到 `with.n=2`、題明細 `2/2`。

finding D5：讀取器不核對頂層 arm 與逐列 arm，衝突結果會被歸到錯誤實驗臂。

severity: major  
blocking: 是  
引句:「s = merge(out_dir, ids, a.runs)」  
file: `governance/eval/ablation_lumos_first.py:135`  
失敗場景：`load_results` 完全依頂層 `arm` 分桶，沒有核對每列已有的 `arm`。舊版、搬移或損壞檔案可直接反轉因果方向。  
最小重現：結果檔頂層寫 `"arm":"with"`，唯一結果列寫 `"arm":"without","id":"a","passed":true`，再跑 `--merge-only --runs 1`。實測退出 0，`with.n=1`、`without.n=0`，衝突沒有 poisoned 或診斷。

finding D6：純合併會用「現在的」日期與 Claude 版本覆寫舊資料 provenance，報表因此冒稱樣本由目前模型產生。

severity: major  
blocking: 是  
引句:「"started": datetime.datetime.now().isoformat(timespec="seconds")」  
file: `governance/eval/ablation_lumos_first.py:353`  
失敗場景：`--merge-only` 不啟動模型，卻仍查目前 `claude --version`、覆寫 `meta.json`，並把該值放入 Markdown 標題；逐次結果檔又沒有足以還原模型版本的欄位。  
最小重現：預置 `meta.json={"date":"2000-01-01","claude_version":"OLD"}` 與一筆健康舊結果後跑 merge-only。實測舊 meta 未保留，改成 `2026-10-04 / 2.1.288 (Claude Code)`，Markdown 首行也宣稱該模型，雖然本次沒有模型呼叫。

`Systems/ablation-lumos-first`：已讀；D1、D2、D5、D6 顯示「缺檔不能只停派」「摘要標失效」「新舊資料相容」仍未完整成立。  
`Verification/2026-10-04_探針停派與失敗留痕`：已讀；所列定向測試實跑 18 passed、0 failed，但未覆蓋上述六個反例，不能支持跨檔原子世代與完整資料 provenance。  
`Systems/codex-harness`：已讀,無 finding。  
`Systems/測試假綠形態`：已讀,無額外 finding；D1–D3 是現有綠測試未涵蓋的資料狀態。  
`Systems/lumos-cli-read`：已讀,無 finding。  
`Systems/canary-audit`：已讀,無 finding。  
`Systems/design-loop`：已讀,無 finding。  
`Systems/bound-tests-gate`：已讀,無 finding。  
`Systems/guard-kill`：已讀,無 finding。  
`Systems/lumos-cli-lifecycle`：已讀,無 finding。  
顯式 launch-exception 的「先 fatal、後盡力歸檔原檔」順序：已讀,無 finding。  
目錄鎖與舊鎖相容：在圖譜聲明的本機合作進程、目錄不被任意改名範圍內，已讀,無 finding。  
顯式 tombstone 經人工歸檔後再重跑：除 D1 的無 tombstone 路徑外，已讀,無 finding。

總結：最嚴重 severity major；blocking 6 條。
