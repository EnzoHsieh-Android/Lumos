preflight-4: ran

# 設計前掃與第 1 輪 intake

工作：使用者指定的第 2 案「分支留痕」。登記工作樹是本 repo；程式紅綠基準另用乾淨 `main@2db51cc4d93c94a445b7a2a79d85a42e68c8d4b5` 副本。設計審 loop：`design-codeloop-pass-branch`；代碼審 loop：`code-codeloop-pass-branch`。正式設計審第 1 輪已派工；代碼審尚未派工，沒有代碼審耗時起點。

機械掃描：`lumos refcheck <計劃> --repo . --json` 回 `missing=0,out_of_range=0`；`prose-lint` 無命中；`pitfalls <計劃> --check` rc0。獨立唯讀前掃逐句對 `scripts/lumos` 和 `scripts/hooks/pre-push` 查語意，發現下列四處，均在凍結正式審材前折回計劃：

| 前掃項 | 修改前 → 修改後 | 重現／來源 |
|---|---|---|
| 分支短名 | 只說「`check-ref-format --branch` 檢驗」→ 明定短目的分支名，輸出須等於輸入，拒絕 `refs/heads/` 與 `@{-N}` 展開 | `git check-ref-format --branch refs/heads/main` rc0；pre-push 讀 `main` |
| marker 碰撞 | 「查其他分支不得借用」卻只改 `pass` → 新 marker 存分支身分、讀側核對，舊歧義檔退讀精確分支治理帳 | `a/b` 與 `a__b` 都寫 `a__b.json`；獨立 Git 倉庫兩次 pass 只剩一個 marker |
| 治理帳失敗 | 未限定「marker 和治理帳都寫入」→ S1 限治理帳可寫環境，保留既有失敗語意為明示剩餘缺口 | 無 `docs/` 的 Git 倉庫，pass rc0、marker 有而治理帳無 |
| 審查完成證據 | 「使用者須完成審查後才能 pass」疑似機械宣稱 → 明說編排者人工前提，本案不新增完成度驗證 | `cmd_code_loop` 的 pass 路徑收到指令即寫，不查審查卷證 |

2026-10-04 計劃判門：`spec-gate` high，因本案碰 code-loop 守衛面；四條條款均有人工驗法。正式席位報告、命令及處置會在本檔下續記，不回填猜測的時間。

## 正式設計審第 1 輪處置

凍結審材 `r1-snapshot.md` SHA-256 `41c3f660ea703b68cca60f1ab3511189aad55252210aa5f8929caa13b246f8d2`。四個正式席的報告均通過 `report-normalize`、`quote-check`、`refcheck`；`seat-check` 顯示通才與架構席各有 3 個材料未在報告點名，此為觀測限制，不當作已讀的證明。外家 Claude 報告格式不符合正式席要求，僅列為 advisory，不計入正式席數或 canary 發現數。

| finding | 機械重現與判讀 | 處置 |
|---|---|---|
| G1 skip 無目標分支 | HIT：`scripts/lumos` 的 `pass`／`skip` 共用只取 checkout 的寫入路徑，pre-push 依 remote ref 查。 | 折 S1、S4 |
| G2 真推送入口未測 | HIT：`t_codeloop_guard_prepush` 原案例的 stdin 目的分支等於 checkout 分支；缺 `feature → main`。 | 折 S4、S5 |
| B1 dispositions 碰撞 | HIT：`_codeloop_read_dispositions` 對已存在 marker 直接回傳 JSON；檔名將 `/` 換 `__`，未核對內存 `branch`。 | 折 S3 |
| B2 pre-push 提示錯位 | HIT：`scripts/hooks/pre-push` 阻擋提示沒有目的 `--branch`，照貼會寫在 checkout。 | 折 S4 |
| B3 legacy marker 身分 | HIT：舊 `_codeloop_write` 沒 `branch`；僅靠檔名分不出碰撞或大小寫別名。 | 折 S3 |
| B4 壞 pass marker | HIT：`_codeloop_read` 解析失敗立即回 None，沒有像 dispositions 那樣退讀治理帳。 | 折 S3 |
| S1 治理帳失敗仍留 marker | HIT：`pass`／`skip` 先 `_codeloop_write`，`_codeloop_gov_log` 吞 `OSError`，命令無條件回 0。無 `docs/` 的獨立 Git 倉庫也曾重現 rc0 與僅 marker。 | 折 S1；推翻前掃的「限可寫環境」處置 |
| S2 大小寫別名 | HIT：`git check-ref-format --branch Main` 與 `main` 均回 0；舊 marker 無身分，大小寫不敏感檔案系統可能指向同檔。此機器的具體別名行為待測，但設計不能信任舊檔。 | 折 S3 |
| A1 兩種 marker 身分規則分裂 | HIT：`dispositions` marker 已存 `branch`，讀側卻沒核對；同庫存在兩套身分判準。 | 折 S3，共用輸入驗法 |
| A2 pre-push 高風險正反例 | HIT：現有 hook 測試只查同名分支，直接 `check --branch` 不能證明 hook 取對目的 ref。 | 折 S4、S5 |

去重後是 6 類修補：目標分支覆蓋 pass／skip；治理帳先成功才有 marker；兩種 marker 核對完整分支且舊／壞檔退帳；高風險 hook 正反例；提示修正；安全回退來源。10 條正式 finding 全數折入，沒有放行或重現不到者。外家 advisory 的 rollback 與碰撞跨型態提醒也折入回退節和 S3；其建議的高風險測試條件折入 S4。各席原文保留在同目錄，不修改審查員的 severity 或引句。

r1(2026-10-04,4 席):10 條／blocking 9／全部折入，待 gate 裁決。
席報告目錄：`governance/review-reports/design-codeloop-pass-branch/`。
