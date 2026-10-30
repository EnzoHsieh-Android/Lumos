severity: minor

整體判斷:我逐 hunk 讀完,也追了所有呼叫端,找不到會做出錯誤審查結果的路徑。下面三條都是 minor。

我實跑的結果如下:
- `python3.14 scripts/test_lumos.py -k arch_target` 是 169 passed、0 failed。
- 新增四支測試單獨跑都綠。
- 我讀 `_arch_legacy_at`、`_arch_legacy_apply`、`_arch_legacy_check_lines` 時挑了這些輸入,沒有出錯:
  - 清單是 `{}`、頂層是 list、`files` 不是字串陣列:`_json_at_ref` 非 dict 回 None,走 unreadable,不會例外。
  - 起點版清單不存在、讀不懂,或讀成空集合:`_arch_legacy_apply` 的 `if not legacy` 提早回傳,等於全照目標審,與文件說的失敗方向一致。
  - 範圍終點是工作目錄時:`_at_rules` 被清成空,`_arch_legacy_apply` 的 `if not targets` 提早回傳。
  - 沒有主線時:推送前風險分級、派工鏡頭、`code-loop check` 三處各自的 ref 取法一致。
  - 起點與頂端的宣告比對:`h_rules == rules` 比的是解析後的規則,清單裡的路徑兩邊都轉 NFC。

severity: minor
blocking: 否
1. `scripts/test_lumos.py`(`t_arch_target_legacy_doctor_lines`):`回傳碼跟沒有清單時一樣` 這條斷言在一次輸出很大的 `-k legacy` 整批執行中紅過一次,訊息是 `0 vs 1`(有清單的 repo 回 0,沒清單的 repo 回 1)。之後單獨重跑兩次、整批重跑一次都綠(135 passed),未能重現。
   - 候選成因:`doctor` 的回傳碼在負載下不穩,或測試之間互相影響。
   - 我沒查到根因,所以交編排者判斷(⚠)。
   - 這條斷言只比兩邊相等,沒有檢查回傳碼的絕對值,所以「有清單造成 doctor 變紅」這種壞法它抓不到。
   - 引句:「check("回傳碼跟沒有清單時一樣", r.returncode == r0.returncode, f"{r.returncode} vs {r0.returncode}")」

severity: minor
blocking: 否
2. `scripts/lumos:57439` 的 `_arch_legacy_apply` 算出並回傳「畢業的檔」`grad`,三個呼叫端(`scripts/lumos:58550`、`63958`、`64966`)全部接成 `_at_grad` 或 `_grad` 後丟掉。畢業判定在 `_arch_legacy_apply`(`keep`/`grad`)和 `_arch_legacy_check_lines`(`b_leg - h_leg`)各算一次,兩處的條件靠人工保持一致。
   - 把回傳值縮成只回 `targets`,或讓 `_arch_legacy_check_lines` 直接用 `grad`,可以去掉重複。
   - 現在兩處條件等價,所以不會出錯;若有人只改一處,印出的「已照目標審」行會和實際判定不一致。
   - 引句:「targets, _grad = _arch_legacy_apply(root, ref, h, targets, rules)」

severity: minor
blocking: 否
3. 新計劃筆記的驗收條款 S1、S2、S3、S4、S7、S8 綁的六支測試在 `scripts/test_lumos.py` 都不存在(產生器、開關資料檔、`Systems/android-arch-template` 也不在這份 diff 裡)。
   - 我跑了 `lumos spec-trace`,六條都回「懸空(寫錯)」。
   - `lumos doctor` 的 S5 只提醒、不擋,`lumos lint` 回 0 問題。
   - 計劃狀態是 `doing`,分次實作可以接受。實作跟上之前,這份計劃會一直在 doctor 的 S5 提醒裡出現。
   - 引句:「[test: t_arch_template_android_all_combos]」

固定席逐條判定:
- `Issues/code-loop守衛main-direct盲區`:不影響。這次改動沒碰推送範圍判定(`_range_base`、`_push_range_start`),只在「讀哪一版宣告」之後加了清單讀取,可信版本仍取自主線的分叉點。
- `Systems/lumos-cli-read` 的 search 合約:不影響。這次沒碰 search 的過濾,也沒碰搜尋三路分岔。
- `Systems/pitfalls-code-loop` 的 RISK:不影響。推送前風險分級仍只標檔、不載圖譜;清單讀取只多幾次 `git show`,沒有載入圖譜。
- `Systems/arch-alignment-lens`:這份 diff 只改了 `scripts/test_lumos.py`(測試)。它的「宣告只讀起點版」合約被刻意開了一個畢業的口。這個口在實作上收得很窄:要宣告解析後完全相同、頂端清單讀得懂,而且只放行清單被刪的檔;規則原文仍讀起點版。文件那句話也同步改了,實作與文件一致。
- `Systems/design-loop` 的 INVARIANT:不影響。處置閘第五步只管審材格式和 `[綁定測試]`,這次設計審路只在 `_dispatch_lens_spec_arch_text` 多扣一次清單。
- `Systems/guard-kill`、`Systems/測試假綠形態`、`Systems/reversibility-governance-ledger`:不影響。這次沒碰 `guard kill`,也沒碰治理帳。四支新測試我沒逐支對照「還原翻紅釘需要前置斷言」那條 INVARIANT,不敢說符合。能確定的是 `same_branch` 每個情境都先斷言了現場。
- 超出上限、只列名的節點:未逐條判。

最高等級:minor
