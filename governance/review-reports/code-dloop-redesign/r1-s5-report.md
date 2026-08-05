1. **major — `scripts/lumos:3571`**  
   具體失敗場景：讀取 `.canary-log.jsonl` 時，不可解析的行只增加 `n_badlines` 並被略過；新增的 disposal 路徑沒有像 settle 路徑一樣檢查 `n_badlines`，便直接用剩餘的 `rounds` 重算。若最新處置紀錄遭截斷或被寫成壞 JSON，讀側可能忽略該行，退回先前完整輪並錯誤 PASS，違反帳本讀側 fail-closed。  
   引句：「`if disposal: return _loop_status_disposal(rounds, loop_id, spec)`」

2. **major — `scripts/lumos:2813`**  
   具體失敗場景：`--report`／`--snapshot` 以呼叫者提供的原始相對路徑落帳。使用者若在 repo root 執行 `canary record --report governance/...`，之後從子目錄執行 `loop status --disposal`，同一路徑會相對於新 cwd 解析，留痕明明存在卻被判「讀不到」，使合法 loop 永久無法通過。寫入時應保存已解析的絕對路徑，或保存相對於固定 repo/vault root 的路徑並在讀側依相同根解析。  
   引句：「`rec[_k + "_path"], rec[_k + "_sha256"] = str(_p), _h`」

3. **minor — `governance/eval/canary_calibration.py:81`**  
   具體失敗場景：新增的 `calibration-log.jsonl` 直接以 append 寫入，沒有讀回自驗或原子替換。磁碟空間耗盡、程序在 flush/close 前中止，或兩個校準程序同時執行時，可能留下截斷／交錯 JSON；程式仍缺少一致性驗證，累積校準帳之後便不再是有效 JSONL。這不影響 gate，但會破壞跨輪校準歷史。  
   引句：「`with log.open("a", encoding="utf-8") as f: f.write(json.dumps(entry, ensure_ascii=False) + "\n")`」

Manifest 判定：

- **`governance/eval/canary_calibration.py:81`「檔案 handle 有沒有 with/確定 close?」— 誤報。** 該寫入明確使用 `with log.open(...) as f`，正常返回與例外離開區塊時都會關閉 handle。真正問題不是 handle 洩漏，而是上述 JSONL 缺少寫後自驗／原子性。  
  引句：「`with log.open("a", encoding="utf-8") as f:`」

max severity: **major**
