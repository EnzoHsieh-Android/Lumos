severity: major

finding G1: 子程序輸出須先是候選檔，不能靠另一份標記維持失敗語意
severity: major
blocking: 是
引句:「unfinished = {p.stem for p in Path(out_dir).glob("*.pending")}」
file: `governance/eval/ablation_lumos_first.py:149`
處置：正式 JSON 只由父程序完整驗證後 `os.replace` 產生；事故歸檔標記後候選檔不能計分。

finding G2: 成功退出的結果列數須等於要求場數
severity: major
blocking: 是
引句:「or any(x.get("id") != qid for x in rows) or len(rows) > n」
file: `governance/eval/ablation_lumos_first.py:273`
處置：少列亦整批失效，保留未完成標記。

finding G3: 窗口額度須包含用量重試
severity: major
blocking: 是
引句:「n += len(json.loads(p.read_text(encoding="utf-8")).get("results", []))」
file: `governance/eval/ablation_lumos_first.py:207`
處置：讀取結果時加計 retry_attempts，探針本批以 max-attempts 限實際模型呼叫。

finding G4: 舊檔錯型欄位或非物件列不能計分
severity: major
blocking: 是
引句:「bad = d.get("skills_health_bad")」
file: `governance/eval/ablation_lumos_first.py:111`
處置：頂層與逐列健康、計分欄位採精確型別；非物件列整檔拒收。

finding G5: 題號邊界須在模型前封閉
severity: major
blocking: 是
引句:「if (not isinstance(qid, str) or not qid or "," in qid」
file: `governance/eval/ablation_lumos_first.py:68`
處置：空白、不可列印、重複題號先拒絕；合法短線題號用 argparse 等號形式。

finding G6: 歸檔故障注入須證明 fatal 正式結果先落地
severity: minor
blocking: 否
引句:「check("歸檔注入確實發生且留有致命嘗試", bool(interrupted) and bool(ablation.collect_skills_health(outdir))」
file: `scripts/test_lumos.py:37997`
處置：斷言實際注入及正式 JSON 的 fatal 值。

finding G7: 多跑一題不能遮掉另一題缺場
severity: minor
blocking: 否
引句:「| 缺場 / 撞上限 / 其他儀器例外 |」
file: `governance/eval/ablation_lumos_first.py:320`
處置：逐題 `max(0, runs-have)` 加總。

finding G8: 空 meta 要標來源未知
severity: minor
blocking: 否
引句:「if not isinstance(meta, dict):」
file: `governance/eval/ablation_lumos_first.py:396`
處置：只補缺欄或錯型來源欄，不查當前 CLI 冒充歷史版本。

finding G9: 無關 JSON 不應毒化探針輸出目錄
severity: minor
blocking: 否
引句:「return ["結果檔組別無效，健康狀態不可判"]」
file: `governance/eval/ablation_lumos_first.py:117`
處置：只掃 `with-`／`without-` 逐題與舊 shard 正式結果。
