severity: minor

## F1 報告的「沒歸屬+共用」不含推送前判定也會要求整套跑的驗收素材
severity: minor
blocking: 否
引句:「所以「沒歸屬」加「共用程式」正好是推送前會要求整套跑的那批」
file: `scripts/lumos:41584`
歸因：有證據的原有漏查(修前後行為相同;驗收素材的略過規則在 r1 就有)

- 輸入:提交只改 `.maestro/baseline/home_visual.png` 與 `.lumos/macrobench-thresholds.json`。
- 走到的行:`_e2e_coverage_report` 的 `if app is None or not inside: continue` 把驗收素材整個略過。
- 推送前判定的 `_e2e_gate_owners` 對同一批檔,`_e2e_scope_hit` 判在範圍內,`_e2e_file_owner` 回 "none"。
- 實測:
  - `coverage --changed` 修前、修後都印「沒歸屬的程式檔:0 支」。
  - 同一份提交跑 `android-e2e check`,回 `need: full`,原因是「`.lumos/macrobench-thresholds.json(對不到任何功能)、.maestro/baseline/home_visual.png(對不到任何功能)`」。
- 計劃 S3 段說「開發中就知道推送時會不會因為『對不到任何功能』被要求整套跑」,也跟實測對不上。
- 重新錄基準圖是常見動作,照這份說明做會以為不用整套跑,推送時才被擋。
- 最小重現:在 `app_dirs=["app"]`、`flows` 有 `.maestro/login.yaml` 的專案,改動只有基準圖和門檻檔,先跑 `coverage --changed`,再跑 `check`。
- 測試 `t_android_e2e_coverage_same_as_gate` 只用 app 底下的檔,抓不到這個差異。
- 該修的是說明:把「正好」改成「程式檔部分」,並註明驗收素材不在報告內。

## F2 `--json` 遇到非 UTF-8 檔名會丟 UnicodeEncodeError
severity: minor
blocking: 否
引句:「print(json.dumps(dict(rep, changed=changed, note=note), ensure_ascii=False))」
file: `scripts/lumos:42196`
歸因：有證據的原有漏查(修前後都崩)

- 輸入:用 `git update-index --cacheinfo` 登記一支檔名含 `\xff` 的已追蹤檔 `app/src/main/bad\xff.kt`。
- 走到的行:`os.fsdecode` 產生 `\udcff` 替身字元,`json.dumps(..., ensure_ascii=False)` 之後 `print` 丟 `UnicodeEncodeError`。
- 實測:修前(`d36d194f`)與修後(`0bed2210`)的 `coverage --json` 都以 traceback 結束。
- 文字版 `--files` 兩版都正常印出,檔名帶替代字元。
- 同檔已有處理這種字元的 `_nodehome_show`,JSON 這條路沒用。
- 只有 JSON 模式受影響,不是判定錯放行或資料消失。

## F3 文字版控制字元清理的測試抓不到拿掉清理
severity: minor
blocking: 否
引句:「print(f"    {_esc_clean(u['dir'], 200)}/  沒歸屬 {u['unowned']} 支 / 共 {u['total']} 支")」
歸因：有證據的修復回歸以外的新增測試缺口(本輪新補的清理,測試只涵蓋逐檔那一處)

- 改壞一:把 `_e2e_cov_names` 裡的 `_esc_clean(x, 200)` 拿掉。
- 改壞二:把資料夾那一行的 `_esc_clean` 拿掉。
- 在 `0bed2210` 的 `--shared` 複本上同時套這兩處,跑 `python3.14 scripts/test_lumos.py -k e2e_coverage`,結果 26 passed, 0 failed。
- 原因:`t_android_e2e_coverage_same_as_gate` 只在 `--files` 逐檔路徑放 ESC 檔名,資料夾名、沒人用的流程檔名與畫面名都沒有帶控制字元的案例。
- 功能名不構成漏洞:設定驗證已限制功能名只收英數字、底線與連字號(實測帶 ESC 的功能名被擋下)。
- 計劃明寫「資料夾、檔名、功能名都經 `_esc_clean`」,資料夾與清單那兩處沒被守住。
- 被保護的只是外來文字回顯,所以只算 minor。

## 配對案例(分開報)

repair 案例

1. 工作目錄補歸屬、不提交
   - 輸入:提交 `B.kt` 後,在工作目錄把它補進 `login.paths`,不提交。
   - 預期:整棵樹與 `--changed` 都不再列它。
   - 修前:整棵樹仍列 `B.kt` 沒歸屬 1 支(`--changed` 為空)。
   - 修後:`unowned: []`,兩種模式都一樣。
   - 比較:已修復。
   - 另測:HEAD 沒有 features、工作目錄剛補上,修後 `test_lumos.py -k e2e_coverage` 的 26 條全過,其中含這個案例。
2. 只有 visual 或只有 stability 情境的功能
   - 只靠 `t_android_e2e_coverage_judged_keys` 驗,它給的鍵組跟推送前判定一致,結果是只有 bench 被列出。
   - 我自己造的 cases 為空與只列效能兩種設定被設定驗證擋下,沒跑到報告。
   - 因此這條未能獨立重現,依賴單元測試判斷為已修復。
3. 同時在功能 paths 與 shared_paths 底下的檔
   - 輸入:`Z.kt` 同時在 shared_paths 與 `vis` 功能的 paths 底下。
   - 預期:報告列在共用程式。
   - 修後:`"shared": ["app/src/main/Z.kt"]`。
   - 修前:輸出沒有 `shared` 鍵。
   - 驗證了 app 底下的檔;驗收素材見 F1,「沒歸屬+共用」不涵蓋它們。
4. 控制字元清理
   - 逐檔名這一處有效。
   - 資料夾名與清單兩處沒有測試守住,見 F3。

preserve 案例

1. `_e2e_gate_owners` 的擋下原因字樣與 owners 集合
   - 輸入:`shared` / `none` / `owned` 三種檔都有的一批檔。
   - 結果:原因字樣為「`(共用程式,列在 shared_paths)`」「`(對不到任何功能)`」,owners 為 `{'login'}`。
   - 比較:程式碼逐行比對,`shared` 原本 `continue`、現在回空集合 `update` 為空操作,兩版等價。
2. 設定壞掉、沒有 e2e 段、沒有 features
   - 這幾種情形 coverage 仍回 2 並說原因,由 `t_android_e2e_coverage_bad_config` 通過(26 條全過)。
   - 我自己造的 cases 為空、控制字元功能名、缺 results_dirs 也都被設定驗證擋下並說原因。
3. doctor 缺口行在沒有缺口時不印
   - 由 `t_android_e2e_coverage_doctor_line` 驗,通過。
   - 我自己沒另外驗 doctor 輸出。

## 三問

1. 原問題的修復效果:工作目錄設定與共用程式兩項有同一案例的修前、修後行為差異,證據如上。
2. 修補處的正常、錯誤與相鄰路徑:推送前判定行為等價;錯誤路徑 rc 2 仍成立;相鄰的 `--changed` 與整棵樹都走工作目錄設定。
3. 新發現的修前、修後:F1、F2 修前後都有,屬原有漏查;F3 是本輪新補清理的測試缺口。

## 其他鏡頭

- py 效能題:逐題採信表態記錄的 `na`;`py-external` 是 `scenario_probe.py` 的舊程式,不在新增行。新增行以 ruff 逐行檢查,在新增的涵蓋報告與逐檔歸屬範圍內沒有新告警。
- 圖譜固定席節點:`lumos-cli-read`、`guard-kill`、`lumos-cli-lifecycle`、`design-loop` 等的 INVARIANT 與本次新增的只讀子命令無交集,判不影響。
  - `_e2e_gate_owners` 行為等價(見 preserve 1)。
  - `pitfalls-code-loop`、`README圖產生器` 等 RISK 節點只牽連產圖腳本與 SVG,未讀到被破壞的宣稱。
- 角色卡:`be-api-compat` 與 `be-authz` 對這個本機 CLI 沒有對外 API,也沒有授權端點,不適用。
  - JSON 輸出新增 `shared`、`changed`、`note` 鍵,屬新增欄位,不影響舊讀者。

## 未驗範圍

- doctor 實際輸出。
- git 子程序逾時的實際行為。
- SVG 與產圖腳本的視覺結果。

總結:本報告最高等級為 minor
