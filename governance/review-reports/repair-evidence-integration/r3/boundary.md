severity: major

## design3-boundary-F1

severity: major  
blocking: 是

引句:「共用範本的留來源指引要求在squash/rebase前保存仍可取回的兩端完整來源」

設計要求改寫歷史前保存「兩端完整來源」，但實際交付的增量 bundle 並不自足：空物件庫驗證明確失敗，必須先取得 `c4f2b0cf…` 的完整物件閉包。計劃指定的前置來源只是可變動的遠端 `refs/heads/main`；既有收據也明載不保證遠端歷史永久存在。因此一旦 squash/rebase、force-push 或遠端清理使該提交不可取回，已保存的 bundle 就無法還原，正好破壞本案要防的情境。

需折回設計：在歷史改寫前，把前置提交的完整閉包存入真正受保護且已驗證不可改寫的 ref，或另存可獨立還原的完整 bundle；驗收必須從空物件庫、無 alternates、且不向活動 main 取前置物件完成還原。只在改寫前再測一次遠端可取回，不能構成留存。

佐證 file: `/tmp/lumos-seat-materials/repair-evidence-integration-r3/plans.md:35`  
佐證 file: `/tmp/lumos-seat-materials/repair-evidence-integration-r3/plans.md:80`  
佐證 file: `governance/review-reports/code-convergence-input-guards/r3-validation/reviewed-957-incremental-cold.json:15`  
佐證 file: `governance/review-reports/code-convergence-input-guards/r3-validation/reviewed-957-incremental-cold.json:63`  
佐證 file: `governance/review-reports/code-convergence-input-guards/r3-validation/remote-prerequisite-cold.json:127`

## 三類風險

- 金流：已讀五篇計劃，範圍沒有交易或金流操作，無 finding。
- 對外送出：主計劃只把提交 main 與 CI 列為已授權的後續交付；本席未執行推送、發布或外部通知，無新增 finding。
- 不可逆：有上述 blocking finding。歷史改寫本身可使增量 bundle 的前置物件永久失去取回入口，目前不能視為「來源先留存」已成立。

守衛面補充：實際登記的固定合約中，五個相關 Systems 節點只有 `Systems/測試假綠形態` 有一條「還原翻紅釘須配現場成立前置斷言」合約；本設計的 ABA、捕獲失敗與注入確認方向未違反它。其餘四個節點沒有登記固定合約，未把一般摘要敘述當合約。

## 指令、引用與版本核對

- `lumos home check --staged|--diff A..B --repo`、`lumos loop retro-stats --json --repo` 均由實際 `--help` 確認存在。
- `cmd_home_check` 確實呼叫 `write-tree` 捕獲索引，結尾再次比較並在不同或讀不到時撤回額外證據。
- S1、S2 所列測試函式均存在；`spec-trace` 顯示十條條款皆有 test 或 manual 綁定。
- 收據中的 `clone --bare --single-branch --branch`、`cat-file -e`、`merge-base --is-ancestor`、`bundle verify/list-heads`、`fetch` 均有退出碼 0 的實際紀錄；bundle 檔案雜湊也與收據相符。
- `refcheck` 對五篇計劃沒有辨識出可檢查 claim；因此另以檔案存在性、原始碼與收據人工核對，不能把該次零筆輸出當成引用全數通過。
- 當前 `scripts/lumos` 雜湊已不同於 957 收據；計劃有明寫最終版本必須重新綁定，因此此刻不判為缺陷，但交付前仍未完成。

## 閱讀量與未驗範圍

實際可見閱讀／搜尋輸出約 2,000 行；因一次廣搜意外產生約 397 行截斷結果，加上截斷後重讀審材，超過原訂 1800 行上限。我在確認 blocking 證據後停止擴讀。

未判定範圍：

- 指定允許執行 git 的 `/tmp/lumos-seat-work/修補驗證與來源留存整合/boundary/` 不存在；依派工限制，未改到 repo 根執行任何 git 指令，因此提交物件可達性與 bundle 即時重放未重新實跑。
- 未讀任何前輪或其他席報告。
- 未全面展開三份技能來源及所有 helper 的逐段語意；只定點核對主設計涉及的 home-check 路徑、測試入口、CLI help、合約與來源收據。
- 遠端 `main` 現在是否仍含前置閉包未做即時網路重驗；現有收據只能證明 2026-10-07 當時可取得，且其自身已聲明不保證永久存在。