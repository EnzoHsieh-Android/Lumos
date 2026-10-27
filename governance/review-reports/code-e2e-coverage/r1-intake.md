# r1 收貨與去向(2026-10-27)

材料:r1-snapshot.patch(3f898ce8..d36d194f,759 行)。分級 standard:單審(C,正確性)一席、架構對齊(A)一席,兩席全新代理。兩份報告從逐字稿存檔;單審報告最後一行總結句被格式檢查擋,退回該席只改那一行、重交後存檔。quote-check 兩席全數錨定;refcheck 全對得上;reflog 核對工作目錄沒被動過。

這輪有 major,照代碼審規則 accepted 必須為空:6 條全折(修正前 d36d194f → 修正後 0bed2210)。

## 重現(觀察與判準分開驗)

| id | 重現 | 結果 |
|---|---|---|
| C1 | 提交 Z.kt 後在工作目錄把它補進 login.paths、不提交,coverage 整棵樹與 --changed 都仍列 1 支沒歸屬;HEAD 沒有 features、工作目錄剛補上時擋下回 2;補 t_android_e2e_coverage_worktree_cfg,修前 3 條紅 | HIT |
| C2 | 把 visual 或 stability 從判「會判情境」的鍵拿掉,既有測試照綠;補 t_android_e2e_coverage_judged_keys,兩種改壞各自紅 | HIT(守衛缺口) |
| C3、A1 | 同時在功能 paths 與 shared_paths 底下的檔:推送判定要整套,報告不列;歸屬三步在報告裡另寫一份;補 t_android_e2e_coverage_same_as_gate(沒歸屬+共用=推送判定要整套的那批),修前紅 | HIT |
| A2 | 檔名帶 ESC 的檔 --files 原樣印出;補同一支測試的控制字元斷言,修前紅 | HIT |
| A3 | coverage 另寫一份讀 HEAD 設定加驗證的序列;改用既有的 _e2e_worktree_e2e 後這段整個拿掉 | HIT(讀碼) |

## 去向

- 全折:C1、C2、C3、A1、A2、A3。
- A2 本來屬於使用者 2026-10-27 裁定的範圍外(「自用框架，不用過度修正資安風險」),但這輪有 major、放行欄必須是空的,照折;修法是用既有的 _esc_clean,沒有新機制。
- 修補因果:第一輪,沒有上一輪修補,不適用。
