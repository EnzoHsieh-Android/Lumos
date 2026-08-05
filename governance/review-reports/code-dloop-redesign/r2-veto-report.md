1. **major — `scripts/lumos:8213`**  
   全席留痕重驗會直接跳過缺少 `report_path` 或 `snapshot_path` 的席，最後仍宣稱全席驗證成功。具體重現：同一輪先在尚未定錨時記一席、不帶留痕；之後再記帶 `findings_set` 與完整留痕的 carrier。disposal gate 對前一席兩個缺欄都 `continue`，只驗 carrier，最終可 rc0。新增測試只覆蓋「有欄位但遭竄改」，沒有覆蓋全席缺欄。  
   引句：「`for i, r in enumerate(latest, 1):`」

2. **major — `scripts/lumos:2826`**  
   所謂 repo root 實際使用 `env.vault.parent`；正式布局中 vault 是 `docs/lumos-toolchain-knowledge`，因此它的 parent 是 `docs/`，不是 repo root。位於 `governance/review-reports/...` 的正常留痕會被記成絕對路徑；搬動或重新 clone repo 後，即使相對於新 repo 的檔案完整存在，舊帳仍指向舊機器絕對路徑而永久 FAIL。讀側 `scripts/lumos:3617` 同樣忽略已傳入的 `--repo`。測試的假 vault 恰好直接放在假 root 下，因此掩蓋了正式兩層目录布局。  
   引句：「`_stored = str(_pr.relative_to(env.vault.parent.resolve()))`」

3. **minor — `governance/eval/canary_calibration.py:85`**  
   新自驗以「末行 timestamp 相同」代替尋找並核對本次完整 entry，而且 timestamp 只有秒精度。兩個同秒執行的程序交錯 append 時，A 可能讀到 B 的末行；因 timestamp 相同仍判定 A 自驗成功，即使其他欄位不同。若 B 落在下一秒，A 又會在自己的 entry 已成功落盤時誤報 rc2。這沒有真正解決註解聲稱的併發問題，且本批未增加校準帳自驗測試。  
   引句：「`if json.loads(tail).get("ts") != entry["ts"]:`」

max severity: **major**
