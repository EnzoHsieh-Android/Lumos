# r1 收貨紀錄

兩席收齊後一次寫進卷證(從逐字稿取最後一則回答);`quote-check` 兩份全數錨定,`report-normalize` 兩份不用改;收貨時 `git status` 只看到工具自動寫的治理帳與卷證目錄,reflog 停在 rebase 完成,沒有席位動過 repo。

## 重現表

| id | 重現命令 | 輸出摘錄 | 結論 |
|---|---|---|---|
| C1 | 把 `_e2e_note_gaps` 的 `not any(seen(f) for f in fl)` 改成 `not all(...)`,`python3.14 scripts/test_lumos.py -k android_e2e_coverage` | `41 passed, 0 failed` | HIT:改壞照綠,席位宣稱成立 |
| C2 | 把 `case_flows` 的 `[_e2e_norm(x) for x in ...]` 改成 `[x for x in ...]`,同一組測試 | `41 passed, 0 failed` | HIT:改壞照綠,席位宣稱成立 |

## 判讀

- C1、C2(major):觀察與判準都成立(規格明寫的兩點沒有測試守)。折:補「一個情境兩支流程檔、只有一支被綁到」與「對照表寫 `./` 開頭」兩組測試。
- C3(minor):讀碼確認子字串比對會把 `relogin.yaml` 算成提到 `login.yaml`。這輪有 major,不放行,折:路徑前後要是邊界,補六種正文寫法的測試。
- A1(major):`_e2e_flow_names` 自己讀流程檔、套 `MAESTRO_FLOW_RE` 與 `MAESTRO_NAME_RE`,沒走 `_walk_test_files`;`_residual_test_files` 已有同功能的「測試名 → 檔」索引。觀察成立。席位標 ⚠ 問「對照表給檔路徑、要檔 → 名」能不能豁免:不豁免,反查同一份索引就能得到檔 → 名。折:把殘留索引那段抽成共用的 `_platform_name_files`,兩邊都呼叫它,拿掉 `_e2e_flow_names`。
- A2(minor):觀察成立(載入器選擇的理由沒寫進圖譜);不改成用 env,因為 `load_vault` 的筆記物件不留正文,全文比對還是要重讀。這輪有 major,不放行,折:理由寫進 Systems/android-e2e-acceptance 一行 WHY。

## 修補的驗證

- 修補後 `python3.14 scripts/test_lumos.py -k android_e2e_coverage`:修前(7be6aac1 那版程式配新測試)紅,`46 passed, 3 failed`;修後綠,`49 passed, 0 failed`。
- 修補後逐道改壞各跑一次,四道都紅:`not all` 1 支紅、拿掉 `_e2e_norm` 1 支紅、正文比對退回子字串 3 支紅、綁定比對清空 5 支紅。
- 抽共用函式後 `-k residual` 全綠(`466 passed, 0 failed`)。
