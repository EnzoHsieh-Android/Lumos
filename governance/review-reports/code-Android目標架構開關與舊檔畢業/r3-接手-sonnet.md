severity: minor

審查依據是固定提交 `1bb9609b` 的正文,我另在 `/tmp/lumos-seat-work/code-Android目標架構開關與舊檔畢業/接手-sonnet/pre` 驗了兩個版本。我讀完了 r3-code.patch 和 r3-repair-review.patch。這輪沒有 major 以上的問題,只有一條 minor。

## Finding

1. 說明行的測試 L 標著修補理由,但修前也是綠的,所以它不是這次修補的翻紅釘。
   引句:「L: 起點沒有清單、分支新增清單 → 印多了 1 行(代碼審 r2:說明行要讀頂端版清單)」
   - 修前的 `_arch_legacy_check_lines` 讀的就是頂端版清單,行為本來就對。
   - 這條只是補一個既有行為的情境,不是抓修補回歸。
   - 把測試名裡的「代碼審 r2:要讀頂端版清單」當成這條在守的修補,三個月後接手的人會被誤導。
   - 查證:在 `pre` 副本(修前 `44b0044d` 加修後測試檔)跑 `python3.14 scripts/test_lumos.py -k arch_target_graduate_check_note`,結果 8 passed, 0 failed。修後同一支測試也是全綠。
   歸因:有證據的原有漏查(測試措辭問題,不是修復回歸)。
severity: minor
blocking: 否

## 固定席逐條判定

- `Systems/arch-alignment-lens.md`(家):不影響。畢業說明寫的「宣告有任何不同就不畢業」仍符合程式。拿掉警告條件後,規則比對已涵蓋警告,因為 `_arch_targets_config` 的每條警告路徑都回空規則。
- `Systems/lumos-cli-read.md`(INVARIANT:search 不排除 stale):不影響,diff 沒碰 search。
- `Systems/design-loop.md`(INVARIANT:處置閘):不影響。設計審派工鏡頭讀清單的路徑沒改,畢業函式在 head 等於 ref 時回空。
- `Systems/測試假綠形態.md`(INVARIANT:還原翻紅釘要有前置斷言):不影響。NFC 的翻紅釘在修前確實翻紅(見第一問)。
- `Systems/guard-kill.md`(INVARIANT):不影響。
- `Systems/pitfalls-code-loop.md`(RISK)、`Issues/code-loop守衛main-direct盲區.md`、`Systems/reversibility-governance-ledger.md`(RISK):不影響。`code-loop check` 的輸出只改說明行的資料來源,不改擋或放的判定。

## 三問

1. 原問題的修復效果
   - NFD 檔名的修復有行為證據。修前跑 `pre` 的 `-k arch_target_legacy`,結果 8 passed, 1 failed,失敗的是「git 列出 NFD、清單寫 NFC → 認得是同一支」,實際輸出「已不存在 1」。修後同一組是 9 passed, 0 failed。
   - H2(清單混了非字串元素)修後綠。沒有「元素檢查」的對照版本可跑,我是讀碼判斷:沒有那道檢查,`nfc(1)` 會丟例外,所以這支測試能抓到。
   - 「沒宣告只有清單」的 doctor 摘要,修前修後都綠,因為修前的行為本來就對。
   - 「拿掉警告條件」是等價改動。警告只會跟空規則一起出現,所以 `h_rules == rules` 已涵蓋。

2. 修補處的相鄰路徑
   - `-k arch_target_graduate` 在 `1bb9609b` 跑,26 passed, 0 failed。
   - 其中宣告有改不畢業(B)、清單讀不懂(C)、頂端多出行(E)、NFD 清單(J)、修補輪範圍起點(I)都仍成立。
   - 說明行改用 `pf_data["arch_alignment"]["targets"]` 後,我確認該資料與 `disp_range` 同源(同一範圍的 pitfalls 輸出)。`targets` 缺鍵時退回自算,兩條路徑的結果等價。

3. 新發現的同一案例在修前、修後的結果
   - 只有 L 這條,修前修後都綠(見上)。
   - 沒有發現新的同類案例。

## 未驗範圍

- 全套測試和 `lumos doctor`、`code-loop check` 的整體輸出沒跑,只跑了三組相關子集。
- 第二部分的 S1–S4、S7、S8、S10 不在這次範圍。
- Konsist 那一半和多模組情境沒驗,計劃已有 REVISIT 回頭條件。
- `templates.md` §7.6 和 `06` 的改動我只做了關鍵字核對,沒發現與程式矛盾的措辭。

最嚴重等級為 minor
