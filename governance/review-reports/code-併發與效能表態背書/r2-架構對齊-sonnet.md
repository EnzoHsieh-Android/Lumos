severity: minor

只讀了 diff、scripts/lumos 與凍結 patch,沒跑測試。

驗收上輪兩條 major:另寫一套讀 jsonl——已改用 errors="replace" 逐行讀,但同功能 helper 沒被換掉(見 R2A1);另寫補殘行換行——已拿掉,diff 無殘留。

**1. 分層與依賴方向**:對齊。依賴單向(`_contract_backing_apply` → `_backing_kill_rows` → `_jsonl_tolerant_rows`;`_backing_valid_rows` → `_codeloop_record_valid_ex`);`_kill_recipe_key`、`_kill_method_name` 共用;gov load 走 `_jsonl_tolerant_rows` 再套 `_gov_event_types_ok`(對照 `scripts/lumos:7346`)。

**2. 命名與錯誤處理**:提醒與擋下前綴同鄰居(`scripts/lumos:13361`);except Exception 加 stderr 比鄰居寬但有註解說明理由;`_ex` 三元組加原名包裝沒有先例,但保住兩個既有呼叫端二元組簽名(`scripts/lumos:38336`、`scripts/lumos:38673`),timeout 與判不了是新需求,不構成第二種做法(見 R2A2)。

**3. 第二種做法**:`_jsonl_tolerant_rows` 對齊 `cmd_canary_second`(`scripts/lumos:8658`)、`_ci_write`(`scripts/lumos:33516`)、`_jsonl_append_verified`(`scripts/lumos:8620`)的內聯寫法;但 repo 已有「路徑 → [dict]」共用 helper `_drift_jsonl_rows`(`scripts/lumos:28970`)加 `_drift_jsonl_parse`(`scripts/lumos:28737`),read_bytes、errors=replace、只在換行切、略過壞行與非物件;新 helper 沒提它也沒說明不用的理由。方向是把兩個讀者收斂,降為 minor ⚠。

**R2A1**
severity: minor
blocking: 否(結構對,但同功能已有 `_drift_jsonl_rows` 共用 helper 沒被採用或提及)⚠
引句:「def _jsonl_tolerant_rows(path):」
file: `scripts/lumos:28970`
file: `scripts/lumos:28737`

**R2A2**
severity: minor
blocking: 否(`_ex` 三元組加原名包裝沒有命名先例,結構合理)
引句:「def _codeloop_record_valid_ex(repo_root, rec_sha, marker_sha, timeout=None):」
file: `scripts/lumos:38119`

不對齊共 2 條,其中 major 0 條
