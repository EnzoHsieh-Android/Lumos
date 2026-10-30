severity: clean

# 第 3 輪邊界席審查報告(固定提交 1bb9609b)

我讀了完整的 r3-repair-review.patch,r3-code.patch 的相關 hunk 也讀了,正文以固定提交為準。實跑在臨時 clone 與臨時 git repo 裡做。`python3.14 scripts/test_lumos.py -k arch_target_` 跑出 182 passed、0 failed。

## Finding

沒有 finding。極端輸入逐一走過,沒有找到會做出錯誤行為的情形。

下面兩點只是觀察,不算 finding,也沒有失敗場景:

- `_arch_legacy_check_lines` 的 `pf_targets is None` 回退分支在真實流程裡永遠走不到。`_arch_alignment_hints` 只在 targets 非空時才寫 `targets` 鍵,而畢業的檔一定在 targets 裡。把這條回退拿掉,輸出也不會變。這只是效能最佳化,測試守不到也不影響必要行為。
- `{"files": []}` 搭配 doctor 會印「舊檔清單 0 支…」這一行。這是提醒行,不是錯誤。

## 修補鏡頭三問

**① 原問題的修復效果**
- G1(doctor 的 NFD 比對):在函式內轉 NFC 之後,`_arch_legacy_doctor_lines(d, rules, [_ARCH_CAFE_NFD])` 對 NFC 清單算出「已不存在 0」,這是新增的測試案例。
- 順帶注意:修前唯一的正式呼叫端 `_arch_target_doctor_lines` 本來就先轉 NFC,所以正式流程的行為沒有變。這是讓函式自己守住,不是修了一個正式流程裡真的會出現的 bug。
- G3(清單混入非字串元素)的命令:`m._arch_legacy_at(d, '{"files":[…,1]}')`。
  - 預期:`(set(), "unreadable")`。
  - 測試 H2 在固定提交通過。
  - 我另外跑了 `{"files":[null]}`、`{"files":[["a"]]}`、`{"files":null}`、頂層是清單、非 UTF-8 的 `\xff` 位元組,全部回 `(set(), "unreadable")`,不丟例外。

**② 修補處的正常、錯誤與相鄰呼叫路徑**
- 拿掉 `h_warns` 條件前後,我在同一個臨時 repo 上各跑一遍 `_arch_legacy_graduation`,修前(44b0044d)與修後(1bb9609b)結果逐項一致:
  - 宣告形狀壞:修前、修後都回空集合。
  - 宣告改成非 UTF-8:修前、修後都回空集合。
  - 宣告被刪掉:修前、修後都回空集合。
  - 宣告只多一個無關鍵:修前、修後都畢業 `{a.py}`。
- 原因在 `_arch_targets_config` 的寫法:只要有警告就一律回 `([], warns)`。所以「有警告」蘊含「規則為空」,比較 `h_rules == rules` 已經涵蓋警告。
- `_arch_legacy_check_lines` 的 `pf_data` 各種形狀我都實跑了,都不丟例外,結果也合理:
  - `None`、`{}`、`{"arch_alignment": None}`、`targets` 為 None、只有 `files` 鍵的結果都一致,走回退分支,數字與預期相符。
  - `targets` 有值時用 `keep & judged`。

**③ 新發現的同一案例修前與修後**
- 沒有新發現的案例。
- 上述 `h_warns` 的四個情境,兩版的結果相同。
- 修前證據:沒另存,記未判定。這次修前版是我現場拿 44b0044d 實跑的。

## 極端輸入已驗清單

以下輸入我走了 `_arch_legacy_at` 與 `_arch_legacy_doctor_lines`,都沒有例外,結果也合理:

- **空與重複**:空清單、清單內重複項。
- **BOM**:合法。
- **特殊字元**:空白、方括號、空字串項目。
- **NFD**:清單內是 NFD 寫法,讀入時轉成 NFC。
- **非 UTF-8**:歸為 `unreadable`。
- **doctor 的 tracked 參數**:
  - 兩萬支檔案加一個孤立 surrogate,0.02 秒完成。
  - 同樣的輸入分別用 list 與 set 傳入,都沒有例外。
  - `tracked=None` 與空 list 的行為相符,前者寫「算不出」,後者算全部不存在。

## 固定席逐條判定

- **lumos-cli-read(search 預設排除 superseded 的合約)**:不影響。這份 diff 只動 `_arch_*` 系列函式,不碰 search 的濾網。
- **pitfalls-code-loop、design-loop、guard-kill、測試假綠形態、reversibility-governance-ledger、arch-alignment-lens**:不影響。理由如下。
  - 各節點宣稱的行為,這份 diff 都沒有碰到。
  - pitfalls 的輸出形狀沒變,只多一個讀 `arch_alignment.targets` 的下游。
  - 設計審讀 HEAD 版清單的路徑照舊,畢業行為沒有改動。
  - 測試假綠形態的合約我也核對過:H2 與 NFC 兩個新測試,修法一還原就紅。
- **Issues/code-loop守衛main-direct盲區**:不影響。這份 diff 沒有動 main-direct 的守衛邏輯。
- **其餘「超出上限,只列名」的節點**:無法逐條判定,記為未驗。

## 未驗範圍

- 我沒有跑全套測試,只跑了 `arch_target_` 子集。
- 我沒有跑 Windows 路徑或大小寫不敏感檔案系統的情境。
- 我沒有用 git 逾時實跑 `_arch_legacy_at` 的 `git-failed` 狀態,只由既有測試守。
- 臨時目錄已用字面絕對路徑刪除。

最嚴重等級為 clean
