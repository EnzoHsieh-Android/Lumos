1. **major — `scripts/lumos:8215`**  
   具體失敗場景：同一判定輪的第一席在 disposal 定錨前寫入，因此可合法缺少 `report_path`／`snapshot_path`；第二席再帶 `findings_set` 與完整留痕成為 carrier。讀側遇到第一席缺欄直接 `continue`，其餘 G3、處置集合及 carrier quote-check 都可通過，最終 disposal gate 仍回 rc0。這違反本輪宣稱的「判定輪全席留痕重驗」。新增測試只覆蓋「非 carrier 席檔案存在但遭竄改」，沒有覆蓋「非 carrier 席留痕欄缺失」。應將任一席缺 report、snapshot 或對應 sha 視為 gate failure。  
   引句：「`pth = r.get(key)`  
   `                    if not pth:`  
   `                        continue`」

2. **minor — `governance/eval/canary_calibration.py:85`**  
   具體失敗場景：既有 calibration log 因上次中斷留下無換行的半筆 JSON，例如 `{"ts":`；本次 append 會直接接在半筆後面，隨後 `json.loads(tail)` 拋出未捕捉的 `JSONDecodeError`，產生 traceback。也就是這次新增的「寫後讀回自驗」在它聲稱要偵測的半行帳情境下，沒有受控回傳 rc2。新增 diff 中亦沒有相應回歸測試。  
   引句：「`tail = log.read_text(encoding="utf-8").splitlines()[-1]`  
   `        if json.loads(tail).get("ts") != entry["ts"]:`」

max severity: **major**
