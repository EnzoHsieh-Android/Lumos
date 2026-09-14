severity: blocker

（來源：設計審 r1 外家否決席，codex-cli 0.153.2，2026-09-14；本檔為逐字稿切出的報告本體）


1. 唯一 helper 沒有涵蓋搜尋的原文召回路徑
severity: blocker
blocking: 是；搜尋候選仍受字面標籤控制，直接推翻移除守衛的前提。
`cmd_search` 的回退預檢與主搜尋直接讀檔，以原文決定命中後才排序；`status: done` 搭配殘留 `status/doing`，仍會被搜尋 `status/doing` 找到，清理後則消失。S1 必須明訂這兩條原文路徑的合成、命中行與正則查詢語意，單靠兩個 `query` 測試不能證明所有判斷都已隔離漂移。
引句:「S1 之後漂移在定義上影響不了任何判斷」
file: `scripts/lumos:3097`
file: `scripts/lumos:3211`
file: `scripts/lumos:3223`

2. 清理前後相等，不等於改版前後排序不變
severity: major
blocking: 是；目前的等價測試不足以支持免做排序回歸驗證。
`_rank_fields` 保留清單重複值，`_rank_tokenize` 保留詞頻，評分也計入全部 token 長度；唯讀實跑確認，重新排列相等，但去重、補入原本缺少的鏡像，以及 S6 刪除 priority 都不相等。新版 helper 下清理前後相等，只證明新版忽略字面鏡像，不能證明舊版到新版的候選、詞頻及分數不變；必須區分這兩種承諾並補跨版本驗證。
引句:「排序的標籤欄改吃合成後的集合,所以遷不遷移排序位元相同、不必重跑金標」
file: `scripts/lumos:2712`
file: `scripts/lumos:2679`
file: `scripts/lumos:2763`

3. 「零消費家族」忽略通用查詢與排序消費者
severity: major
blocking: 是；退場理由漏算已存在的功能與檢索變化。
`query --tag` 對任意家族比對，排序也讀取全部 tags，因此 flag/、priority/ 都有程式消費者，無須出現家族專用分支。S6 清理會刪掉既有篩選結果及排序訊號，把警示補進正文只能保存可讀資訊，不能保存這些行為，必須明列並驗收退場造成的功能差異。
引句:「語意警示(`flag/` 家族)與優先級(`priority/` 家族)兩個零消費家族」
file: `scripts/lumos:10130`
file: `scripts/lumos:2712`

4. 新舊 CLI 並存時，免遷移承諾失效
severity: major
blocking: 是；合成版寫入與舊版讀取能對同一份圖譜產生相反判斷。
工具支援全域來源 CLI 與專案內的 vendored 副本，專案更新另走 `update`，並不隨全域入口同步更新。以新版 `set status done` 留下舊 `status/doing`，再用舊專案副本 `query --tag status/doing`，仍會命中；承諾必須限定所有讀者均已更新，並處理版本混用或要求清理，不能無條件稱為純美觀。
引句:「不要求消費專案遷移。** S1 讓殘留鏡像標籤變成無害，遷移純屬美觀。」
file: `scripts/lumos:14839`
file: `scripts/lumos:14865`
file: `scripts/lumos:13919`
file: `scripts/lumos:10130`

5. 工作目錄乾淨不是並行寫入鎖
severity: major
blocking: 是；清理器會覆蓋檢查通過後才發生的合法修改。
乾淨檢查通過後，另一個會談仍能在清理器讀檔與換名之間修改同一檔案，原子換名會完整覆蓋那次修改。現有寫入流程已用 `_vault_write_lock` 處理這種遺失更新，清理器必須承接互斥與外部修改偵測，不能把啟動前檢查當成全程保護。
引句:「唯一的並行風險是同一個工作目錄有別的會談在改檔，這由「工作目錄必須乾淨」那道檢查擋掉。」
file: `scripts/lumos:11042`
file: `scripts/lumos:11057`
file: `scripts/lumos:11089`

6. 清理中斷後，重跑與回滾條款互相卡住
severity: major
blocking: 是；批次部分完成時，設計指定的兩條恢復路徑均不能直接使用。
逐檔原子寫入只保證單檔完整，第若干檔失敗時，前面已改的檔案會讓工作目錄變髒，下一次啟動便遭乾淨檢查拒絕。此時清理提交尚未產生，也無法還原「那個提交」；S5 必須定義部分完成的辨識、續跑或撤銷流程，轉換函式冪等不能替代批次恢復。
引句:「清理前工作目錄必須乾淨（清理器自己先檢查，不乾淨就拒跑），清理獨立成一個提交，退回就是還原那個提交。」
file: `scripts/lumos:11066`
file: `scripts/lumos:11082`

7. 退場沒有同步承接規範單源
severity: major
blocking: 是；完成全部條款後，交付文件仍會要求使用者新增退場標籤。
S4 只改四種程式範本，S6 只規定警告與存量清理，但 reference 仍示範鏡像標籤、列出 priority/ 與 flag/，並說警示不用重複進摘要。必須把現行家族表、寫入範例與 skill 指引的更新納入驗收，否則分發後會持續製造新版工具自己警告的內容。
引句:「四種節點範本不再產鏡像標籤。」
file: `skills/lumos-project-notes/reference.md:286`
file: `skills/lumos-project-notes/reference.md:372`
file: `skills/lumos-project-notes/reference.md:375`
file: `skills/lumos-project-notes/reference.md:377`

8. 到期條款越過 S10 保留的人裁
severity: major
blocking: 是；未收到裁定被直接當成修改排序預設的授權。
S10 明訂由 Enzo 看數字裁，但末行把「仍未裁」推論成「訊號沒人在乎」，並要求直接排除 scope。doctor 的到期掃描只判斷日期，不提供採用價值或授權證據；到期動作必須維持催辦裁定，或另取得自動修改預設的明確授權。
引句:「若仍未裁，代表這個訊號沒人在乎，直接把研究方向排除在排序之外收案。」
file: `scripts/lumos:1896`
file: `scripts/lumos:1908`

最嚴重 severity 是 blocker，blocking 共 8 條。
