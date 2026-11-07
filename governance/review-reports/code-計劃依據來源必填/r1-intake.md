# code-計劃依據來源必填 r1 收貨(2026-11-06)

範圍:`5755ec772..cbce23a0b`(實作三個提交,範圍 1–5;範圍 6 刻意延後),tier high。材料 1284 行一包,七席都看整份:正確性(角色卡)、邊界、資源、合約、通才(八角度)、資安(工具鏈三類)、架構對齊。

## 收貨三道

- 正規化:七份已正規化。
- quote-check:七份全數錨定。
- refcheck:正確性 4 筆 missing(`docs/a-knowledge`、`docs/b-knowledge`、`scripts/link.txt`、`scripts/a.py:999`)、通才 1 筆 missing(`scripts/a.py:99999`)、邊界 1 筆 line_out_of_range(`scripts/lumos:99999`)——全是席位拿來示範怪輸入的例子,不是佐證;其餘對得上。
- seat-check:派工單頂層列了 materials;六席標 unreported(報告沒寫出快照路徑),引句全錨進快照,判定有讀。

## 重現表

| 席-條 | 怎麼試 | 結果 |
|---|---|---|
| 架構對齊-F1、邊界-F3、正確性-F1、合約-F2 | 三席各自造「從 Projects 外 git mv 進來」的計劃:`_plan_first_days_batch` 回搬入日、`_plan_first_day` 回原始加入日;批次 pathspec 限在 Projects,來源在外 git 印成 A | HIT(三席獨立) |
| 邊界-F1、正確性-F3 | `_validate_repo_ref` 不帶 at_sha 只看 `exists()`;席位在 macOS 實跑大小寫錯的路徑、`.git/HEAD`、指向 repo 外的符號連結都放行 | HIT |
| 合約-F1 | 席位改壞:`bad is None` 那圈改成 `return 0`、讀不成文字不 append,`-k spec_gate_push_sources` 仍全綠 | HIT |
| 正確性-F2 | 擋下訊息的範例列原封貼回計劃放行;`使用者 2099-12-31` 放行 | HIT |
| 通才-F1、合約-F5 | 掛鉤文案換回舊句,`-k spec_gate_push_sources` 仍綠;`Systems/bound-tests-gate` WHY 卻綁這支測試 | HIT |
| 通才-F4 | 讀碼:vault 在 repo 根時 `vrel` 是 `"."`、前綴 `./` 永不匹配 | HIT(讀碼推論) |
| 其餘 minor | 讀材料與席位附的 file:line、改壞實驗 | HIT |

## 先查世界

PRIOR-ART:同一件事一套算法——首次加入日改成只有一支實作:整個 repo 跑一次 `git log --reverse -M --diff-filter=AR --name-status`(不限 pathspec,才看得到從外面搬進來的改名;git 官方 log 文件 https://git-scm.com/docs/git-log `--diff-filter`、`-M`),結果在同一個程序內快取;單篇查詢改成查這份快取。這樣健檢與推送前(正確性-F4 寬範圍推送逐篇 git 34 秒)都只跑一次 git。排除:保留兩套加一致性測試(架構席要的是一套)。
PRIOR-ART:出處讀者查得到——判存在改用版控樹(`_validate_repo_ref` 既有 at_sha 參數,對 HEAD 驗,同時驗行號範圍),工作目錄有但沒進版控、`.git` 底下、大小寫不符都不算。示範用網域:RFC 2606 第 3 節保留 example.com、example.net、example.org「可當範例使用」(https://www.rfc-editor.org/rfc/rfc2606 ),這三個網域不算出處;使用者原話與實測的日期不得晚於今天。
PRIOR-ART:擋下留帳去重——本 repo 既有 `_kt_sit_reminder_log` 以(版本, 段, 列)去重的做法;採用:以(計劃, 出處格內容指紋, 階段)去重。

## 分組與去向(全數折入)

- 甲 首次加入日一套算法:架構對齊-F1(major);邊界-F3、正確性-F1、F4,合約-F2、F3,通才-F4、F5(minor)→ 一支實作、整 repo 一次、程序內快取;vault 在根時前綴正規化;逾時退路印一行;補「created 早於生效日、首次進 git 晚於生效日、又改名」的測試。
- 乙 出處判定:邊界-F1(major);正確性-F2、F3,通才-F6,邊界-F2、F4(minor)→ 版控樹判存在含行號;符號連結指向 repo 外不算;example.com 三個保留網域不算;未來日期不算;HTML 註解裡的表不算;型別讀不到時印一行。
- 丙 推送前測試與訊息:合約-F1(major);合約-F4、F5、F6,通才-F1(minor)→ 兩個照擋分支、只有依據來源時的最後兩行、分隔列與重複節各補先紅測試;掛鉤文案補一支直接讀 pre-push 的測試,筆記綁定改成真守它的測試。
- 丁 健檢:通才-F2、F3,架構對齊-F2、F3(minor)→ 例外不印綠勾、改 warn_soft 印例外;「是不是新計劃」只留 `_plan_sources_is_new` 一份,健檢傳預取資料;健檢這段改回慣例 3 條、`--verbose` 看全部(cap 參數拿掉,避免第二套截斷)。
- 戊 留帳與環境:資源-F3、資安-F1、資源-F1、F2(minor)→ 擋下事件去重;生效日被環境變數覆寫時印一行;資源-F1、F2 為可預期的小成本,不改程式。
