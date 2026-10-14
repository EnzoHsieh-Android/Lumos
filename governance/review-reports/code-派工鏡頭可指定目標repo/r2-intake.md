# code-派工鏡頭可指定目標repo r2 收貨紀錄

七席全回(正確性、併發、邊界、合約、通才、架構對齊、資安),report-normalize 都不用改。共 26 條:正1–3、併1–2、邊1–4、合1–7、通1–4、架1–3、資1–3。

## 機械重現(quote-check 錨不到的)

| id | 錨不到的引句 | 重現 | 判定 |
|---|---|---|---|
| 合3 | 「"at": "skills/lumos-design-loop/SKILL.md:spec_commit」 | 引的是 r1-fix.json(卷證目錄不在差異快照):`grep -n` 該句 → r1-fix.json 第 334 行;同檔 `t_docs_enumeration_drift` 出現 4 次 | HIT,採信 |

## 根因分組與處置

同輪有 major(併1、邊1、通1、架1、合1–3、資1–2),accepted 必空,26 條全部折入。

- G1 拿掉截止時間的「沒給」判斷(併1、邊1、通1、架1,四席獨立一致):`_dispositions_verdict` 簽名仍是 `deadline=None`,修補把 `deadline is not None and` 刪掉,不帶 deadline 的呼叫(既有測試 t_contract_evidence_warn_only、t_contract_backing_marked_questions)丟 TypeError 變紅;跟本功能無關的順手修改。→ 還原判斷;掃一遍這輪修補動過的所有 deadline 比較,選填的一律保留 None 判斷;本分支 `-k contract`、`-k backing`、`-k disposition` 全綠才算。
- G2 圖譜資料夾本身是符號連結、節點名夾換行(資1、資2、邊4、通4):`_vault_node_path` 拿解析後的路徑比解析後的圖譜,圖譜資料夾換成指向外面的符號連結時整個檢查失效;節點名收得進換行,派工詞框內多出作者自寫的一行;另一方向,計劃路徑套節點名的 80 字上限與字元集,15 篇合法長計劃與全形標點被誤判「路徑含不收的字元」。→ 圖譜資料夾本身與它的上層每一段都不准是符號連結、且在 repo 根內;節點名一律要全符合節點名字元集(不含換行與控制字元),不合算「指到圖譜外/不收」;計劃路徑改用自己的規則(不含控制字元與換行、長度上限放寬到合理值、全形標點可收)。
- G3 spec-freeze 的快照放哪(合2、正3、通2、資3、架3):`--out` 只收計劃所在工作樹,但卷證、收貨、記帳都在會談目錄,手冊沒講怎麼對上;在計劃工作樹留未追蹤檔會碰到別的會談;repo 內任何不存在的位置都能建檔(含 `.lumos/`、`.claude/`)。→ 讓 spec-freeze 從會談目錄用 `<提交>:<路徑>` 凍計劃(同一個物件庫讀得到,不必進計劃工作樹);`--out` 只收執行所在 repo 的 `governance/review-reports/` 底下;手冊照這個寫;`--out` 的逐段檢查跟計劃路徑的逐段檢查共用一支。
- G4 手冊與綁定(合1、合3、合4、合5、合7):SKILL.md 第 1 步叫席位指 rN-snapshot、第 3 步仍說指工作副本,reference.md 詳版沒改;四個文件條目只綁一支跟它們無關的測試;計劃做法 9 與條款沒寫 `out_outside_repo`;筆記裡寫了輪次流水帳與指向別的分支的話;入口清 git 環境只寫在派工鏡頭節點。→ 三處手冊統一成一種說法(席位材料、rN-snapshot、--reviewed 都用 spec-freeze 那份);補一支文件守衛測試(拿掉 SKILL.md、templates.md 那幾句會紅);計劃補條款並綁測試;刪掉流水帳;入口那段寫進管 main() 的節點(lumos-cli-lifecycle)。
- G5 入口改環境變數漏進行程內呼叫(通3):測試十幾處在同一個行程裡呼叫 `m.main()`,入口設的值留在整個測試行程。→ 測試端:行程內呼叫 main 的共用寫法前後存回環境(不改四個分支逐字同一段的入口);寫一支測試釘住「行程內呼叫 main 之後環境照原樣」。
- G6 預算順序與整棵樹(正1、併2):便宜的落點排在最貴的 impact 之後,預算用完只剩空標題;`ls-tree -r` 列整棵樹,成本隨 repo 檔數而非候選數。→ 落點與連結先算、impact 最後用剩的預算;標題只在有項目時印;「提交裡有沒有」改 `cat-file --batch-check`(只查候選)。
- G7 小缺口(正2、邊2、邊3、合6、架2):NFD 名在提交寫法比不到;`.GIT` 大小寫沒測試;掛鉤拿非字串的失敗代碼查 frozenset 會崩;記事件測試沒計數器;掛鉤手抄一份只屬範圍的代碼。→ 查之前先 NFC;補 `.GIT`、`a/.Git/x` 測試;查表前判 `isinstance(code, str)`;測試加計數器與前置斷言;只屬範圍的代碼由 lumos 端推導。

## 修補因果核對(regression)

上一輪修補範圍 500b89cb..5b54619d(r2-repair.patch)。26 條的缺陷都落在 r1 修補新加或改寫的程式、測試或文件(G1 的順手修改、G2 的 `_vault_node_path` 與字元集、G3 的 `--out` 限制、G4 的手冊與 r1-fix.json 綁定、G5 的入口、G6 的批次查與預算、G7 的新代碼與測試),判為回歸。

regression-set:正1,正2,正3,併1,併2,邊1,邊2,邊3,邊4,合1,合2,合3,合4,合5,合6,合7,通1,通2,通3,通4,架1,架2,架3,資1,資2,資3

refuted-set:none。

## 記帳的審查行數

正確性、併發、通才、架構對齊、資安記 repair-code 加 snapshot(4394 行),邊界記 repair-code 加 repair-tests(1708 行),合約記 repair-docs 加 repair-tests(917 行)。
