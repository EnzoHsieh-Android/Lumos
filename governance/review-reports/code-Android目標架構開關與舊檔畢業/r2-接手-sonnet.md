severity: clean

## 總評

這份 diff 我找不到 major 或 blocker。我逐 hunk 讀完整份 diff(`r2-code.patch` 與 `r2-repair-review.patch`),並在固定提交 44b0044da 上跑了測試與自寫的探針。下面沒有標 finding 的疑慮,都找不到能讓行為出錯的具體輸入。

## 固定席逐條判定

- `Issues/code-loop守衛main-direct盲區`:不影響。這份 diff 沒碰 main-direct 守衛的判斷;改動只在架構對齊的目標基準與舊檔清單。
- `Systems/lumos-cli-read` 的 INVARIANT(search 預設排除 superseded、不排除 stale):不影響。`search` 的程式沒動。
- `Systems/pitfalls-code-loop`(RISK):接線影響已驗。推送前分級多一行 `_arch_legacy_apply`,只改 `arch["targets"]` 的內容;tier 的判定沒改。
- `Systems/arch-alignment-lens`:行為與筆記一致。「宣告不動才畢業、規則原文照讀起點版、被 none 命中的檔不看清單、起點版清單不存在或讀不懂時一律照目標審」都與程式相符。
- `Systems/design-loop`(INVARIANT:設計審審材要是 .md 計劃):不影響。設計審路只多一行 `_arch_legacy_apply(root,"HEAD",None,…)`,沒碰審材型別的檢查。
- `Systems/測試假綠形態`(INVARIANT:還原翻紅釘要有前置斷言):新測試大致符合。否定斷言 C、J1 的同一案裡,都有同一套設施的肯定斷言當前置(A、J2)。K 另外已驗不是空轉:`code-loop check` 在 K 場景印出「✅ code-loop check: OK」,只是沒有清單行。
- `Systems/guard-kill`(INVARIANT:rc 優先序與 --json 純度):不影響,guard 程式沒動。
- `Systems/reversibility-governance-ledger`(RISK):不影響,沒碰帳本。

## 三問

**① 原問題的修復效果有何行為證據?**

- **G2(沒宣告時不印清單說明行)**
  - 輸入:`arch_targets` 為 `{}`、起點與頂端都有清單,頂端少 1 行再多 1 行。
  - 預期:「舊檔清單」說明行不印。
  - 修前:K 紅,`code-loop check` 印出了「舊檔清單」說明行。把修前版 `scripts/lumos` 放進 44b0044da 的樹,跑 `python3.14 scripts/test_lumos.py -k arch_target_graduate_check_note`,結果 6 passed、1 failed,失敗的是 K。
  - 修後:`-k arch_target_graduate` 24 passed、0 failed,K 綠。
  - 我另用 `code-loop check` 直接跑 K 與 A 兩個場景:K 輸出只有「OK」一行;A 輸出「少了 1 行,其中 1 支這次有改動、已照目標審」。
  - 歸因:有證據的修復有效。
- **G1(清單讀可信版本、NFD 轉 NFC)與 G4(「其中幾支」只算有改動的)**
  - 修前修後同樣綠。我在修前版 `scripts/lumos` 上用修後測試檔的夾具,跑 I、J1、J2 的 `pitfalls` 輸出:兩版完全相同(I 的 targets 含 OldHelper 與 OrderOld,J2 含 Café,J1 沒有 targets)。
  - 修前版跑 `-k arch_target_graduate_check_note`,A2 也是綠的。
  - 結論:程式在修前就是對的,這次補的是測試覆蓋。這幾組的「修前紅」我這邊沒有證據。
- **G3(doctor 兩個計數、none 命中、git 失敗與列檔失敗)**
  - 修前版沒有 `_arch_legacy_doctor_lines` 這個函式名,測試在修前版跑不起來(EXCEPTION)。
  - 修後測試 7 passed。
  - 修前的行為差異(git 失敗被說成讀不懂)只能從 diff 文字確認,我沒有可執行的修前證據。歸因:未判定。
- **G5(測試時長)**:修後 `t_arch_target_graduate_same_branch` 約 52 秒(整支 `-k arch_target_graduate` 約 88 秒,機器負載不同),與作者量到的 42 秒有出入。此項我沒有修前對照,未驗。

**② 修補處的正常、錯誤與相鄰呼叫路徑是否仍成立?**

- **三個呼叫點與讀清單**
  - `_arch_legacy_apply` 的三個呼叫點(分級、代碼審鏡頭、設計審鏡頭)都改成接單值回傳,沒有遺漏。`_arch_target_doctor_lines` 只有 `run_doctor` 一個呼叫者,已改成四值。
  - 畢業判定只剩 `_arch_legacy_graduation` 一份,被 apply 與 check lines 共用。
  - `_arch_legacy_at` 讀 `{"files":[…]}`,對下列怪輸入都回 `unreadable` 或正常處理,不丟例外:100000 層巢狀、空字串、控制字元、`..`、絕對路徑、5000 層深路徑、孤立代理字元。
  - `_arch_legacy_doctor_lines` 吃這批怪路徑回 `7 支(已不存在 7、沒被判給目標節點 5)`,沒有例外。
- **doctor 的錯誤邊界變大**:修補把舊檔清單的獨立 try/except 併進宣告共用的那個。清單計算若丟例外,整段宣告行都會被「目標架構宣告檢查出錯」蓋掉。我試了上面所有怪輸入,找不到會丟例外的輸入,所以不標 finding。
- **doctor 多跑 `git ls-files`**:`_arch_target_doctor_lines` 在沒有宣告的專案也會跑一次 `git ls-files`,以前是提早回傳。這是效能變動,講不出具體失敗場景,不標。
- **check lines 不再印多了 N 行的情況**:起點版沒有宣告時不再印「多了 N 行」。`Systems/arch-alignment-lens` 與計劃做法 7 沒寫這個收窄,屬措辭落差,講不出照做會出錯的場景,不標。

**③ 新發現的同一案例修前修後各是什麼結果?** 沒有新 finding。

## 已驗與未驗

- **已驗**
  - `-k arch_target_graduate`:24 passed、0 failed。
  - `-k arch_target_legacy`:7 passed、0 failed。
  - `-k spec_lens_reads`:2 passed、0 failed。
  - K 的修前紅 / 修後綠(見上)。
  - I、J 修前修後 `pitfalls` 輸出相同。
  - 怪輸入探針:讀清單與 doctor 行皆不丟例外。
- **未驗**
  - G3 的修前行為。
  - G5 的修前時長。
  - 跑在真實大型 repo 的 `git ls-files` 成本。
  - S10 的 Konsist 實機紅綠(屬第二部分)。
- **臨時目錄**:我建的 `/tmp/lumos-seat-work/code-Android目標架構開關與舊檔畢業/接手-sonnet/before` 與探針腳本已刪;該目錄現在是空的(目錄本身還在,沒刪)。

最嚴重等級為 clean
