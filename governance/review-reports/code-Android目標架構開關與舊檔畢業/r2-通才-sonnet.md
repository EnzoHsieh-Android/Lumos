severity: minor

審查範圍:`r2-code.patch` 全部 hunk,加 `scripts/lumos` 固定提交 44b0044d 的整個函式脈絡。我查了呼叫者、跑了測試,也在隔離的克隆裡做了 5 種改壞實驗。克隆已刪。

## Finding

### 1. doctor 的「已不存在」計數把已追蹤檔名轉 NFC,這一步沒有測試守
severity: minor
blocking: 否

引句:「leg_list, leg_probs = _arch_legacy_doctor_lines(root, rules, {nfc(x) for x in files} if ok_ls else None)」

- **失敗情境:**git 索引裡的檔名是 NFD(例如沒開 precomposeunicode 的 macOS 倉庫),清單裡寫的是 NFC。拿掉 `nfc(x)` 之後,清單上的檔會被誤報成「已不存在」。
- **證據:**
  - 我把該處改成 `set(files) if ok_ls else None`,再跑 `python3.14 scripts/test_lumos.py -k t_arch_target_legacy_doctor`,結果 `7 passed, 0 failed`,沒有翻紅。
  - `t_arch_target_legacy_doctor_lines` 只用 ASCII 檔名。畢業測試的 J 組只守審查那條路的 NFC,沒守 doctor。
  - 這只影響 doctor 的一個提醒數字,不擋推送、不影響審查判定,所以只降到 minor。
- **歸因:**未判定。`006c398` 的 `scripts/lumos` 裡沒有 `_arch_legacy_doctor_lines`,可見這段是修補輪新加的。我沒有兩版行為對照可比。
- **兩版命令:**
  - 修前:`git show 006c398b82f24827804d3a37893d5c64dcc2026c:scripts/lumos | grep -n "_arch_legacy_doctor_lines"`,無輸出。
  - 修後:同一條命令對 `44b0044d` 有輸出,上述改壞實驗為綠。

## 沒有列成 finding 的觀察
- **`_arch_legacy_graduation` 裡的 `and not h_warns` 是死條件。**`h_rules == rules` 且 `rules` 非空時,`_arch_targets_config` 回傳的警告必為空。我拿掉它,24 個畢業測試仍全綠。只是多餘,講不出失敗情境,所以不列。
- **`head == ref` 的短路也是等價的。**拿掉後測試照綠,因為同一版的清單相減本來就是空集合。
- **`_arch_target_doctor_lines` 對沒有宣告的專案也會多叫一次 `git ls-files -z`。**這個倉庫實測約 20 毫秒,不構成失敗情境,所以不列。

## 固定席逐條判定
- **`Issues/code-loop守衛main-direct盲區`:**不影響。這次改動沒碰 main-direct 守衛。畢業只在宣告一字不改時才開口,讀的版本是分叉點版。
- **`Systems/lumos-cli-read`(★INVARIANT★:search 預設排除 superseded、不排除 stale):**不影響。search 與 `--include-superseded` 路徑沒被改。
- **`Systems/pitfalls-code-loop`(★RISK★):**不破壞。`pitfalls` 只多了 `_arch_legacy_apply` 一行,清單不存在或讀不懂時退回空集合,失敗方向是多審。
- **`Systems/arch-alignment-lens`:**宣告只讀起點版的合約沒被破壞。畢業只在宣告一字不改時成立,規則原文仍讀起點版。我用 m1、m2 兩個改壞實驗核對過,頂端清單讀不懂時不畢業有測試守。
- **`Systems/design-loop`(★INVARIANT★ 處置閘):**不影響。設計審鏡頭只在 `_dispatch_lens_spec_arch_text` 加了一行,沒碰處置閘邏輯。
- **`Systems/測試假綠形態`(★INVARIANT★:還原翻紅釘要配前置斷言):**符合。畢業測試有「I 前置」這類前置斷言。
- **`Systems/guard-kill`(★INVARIANT★):**不影響,guard kill 沒被改。
- **`Systems/reversibility-governance-ledger`(★RISK★):**不影響。
- **其餘只列名的節點:**不逐條答。

## 修補鏡頭三問
1. **原問題修復效果:**
   - **輸入:**`python3.14 scripts/test_lumos.py -k t_arch_target_graduate`。
   - **預期:**畢業、清單 NFC、清單讀可信版本、說明行只算有改動的檔,全部成立。
   - **修後:**`24 passed, 0 failed`。
   - **修前:**我沒有跑修前版,所以修前是否紅是未判定。`r2-intake.md` 也寫明沒另存。
   - **改壞實驗:**
     - 條件被改掉時:m2 讓 C 組翻紅。
     - 條件是死碼:m1(`not h_warns`)、m3(`head == ref`)都不翻紅。
     - 先前就有的缺口:doctor 的 NFC(見 finding 1)不翻紅。
2. **相鄰呼叫路徑:**
   - `_arch_target_doctor_lines` 的回傳從 2 個值改成 4 個值,全 repo 只有 `run_doctor` 一個呼叫者,已同步改成 4 個值,例外回退分支也補齊四個空值。
   - `_arch_legacy_apply` 的三個呼叫者在沒有清單、沒有宣告、`head` 為 None 時,都原樣回傳 `targets`。
   - 派工鏡頭的 2000 檔上限在 legacy 扣除之前套用。這不會讓舊檔把新檔擠出上限,因為截斷看的是改動檔數,不是扣除後的檔數。
3. **新發現的同一案例修前修後:**只有 finding 1。修前沒有該函式,所以修前結果是「無此檢查」,修後是上述 NFC 缺口。

## 未驗範圍
- 沒有跑全套測試,只跑了畢業與 doctor 子集。
- 沒有驗證 `scripts/templates/android-arch-target.md` 與產生器。這兩項屬計劃的第二部分,不在這份 diff 裡。
- 沒有對大型清單(上萬行)做效能實測,只讀程式碼確認是集合運算加 O(清單 × 宣告數) 的比對。

最嚴重等級為 minor
