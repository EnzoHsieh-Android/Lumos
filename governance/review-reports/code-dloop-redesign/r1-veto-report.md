1. **major — scripts/lumos:8090**  
   `quote-check` 只驗證「抽到的引句」是否存在，沒有落實 ≥10 字，也沒有核對每條 finding 都各有引句。具體失敗場景：報告列出多條 major finding，卻只放一條一字引句（例如「的」）；只要該字存在快照中，`rows` 全為 `ok`，disposal gate 就會宣稱「引句全數錨定」，未錨定的 findings 仍可放行。  
   引句：「每條 finding 必附一段**從文件逐字複製的原文引句（≥10 字）**——編不出引句的疑慮不要交。」

2. **major — scripts/lumos:8154**  
   disposal gate 只重驗 `carrier` 那一席的 report/snapshot；同輪其他席雖被 T6 強制記錄留痕，gate 完全不讀它們。具體失敗場景：r1 的 s1 帶 `findings_set`、s2 是 missed/major 並記入另一份報告；record 後刪除或竄改 s2 報告，s1 留痕仍完整時 gate 仍 rc0。這使「每席強制留痕」及 missed 席 findings 可追溯性變成寫側形式要求，而非讀側可重算合取。  
   引句：「if carrier is not None:  
        rp, sp = carrier.get("report_path"), carrier.get("snapshot_path")」

3. **major — scripts/lumos:3599**  
   JSONL 壞行對 disposal 沒有 fail-closed：讀取時雖累計 `n_badlines`，卻在把它交給任何檢查前直接進 `_loop_status_disposal`。具體失敗場景：最新一筆 blocker 或新處置帳因中斷寫入而成為半行 JSON；該行被略過，gate 以先前完整輪作為 `latest`，可能 rc0 放行。這與新閘宣稱的「全讀側可重算」及帳本 fail-closed 要求衝突。  
   引句：「if disposal:  
        return _loop_status_disposal(rounds, loop_id, spec)」

Manifest 判定：

- **governance/eval/canary_calibration.py:81 — 誤報。** handle 明確由 `with log.open(...) as f:` 管理，正常完成或 `f.write` 拋例外時都會離開 context manager 並關閉。  
  引句：「with log.open("a", encoding="utf-8") as f:  
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")」

max severity: **major**
