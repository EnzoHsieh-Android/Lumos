severity: minor

整體上,畢業判定、讀清單函式和四處接線的執行路徑都走得通,沒有找到 major 以上的問題。我跑了四支新測試,全綠:`graduate` 17 支、`arch_target_legacy` 5 支、`arch_target_spec_lens` 2 支。

**1. 沒有任何 `arch_targets` 宣告時,`code-loop check` 仍會印清單說明行**
severity: minor
blocking: 否
- 位置:`scripts/lumos`(`_arch_legacy_check_lines`,diff 第 284–301 行)和呼叫它的 `_arch_target_check_lines`(diff 第 278 行)。
- 引句:「if extra:
        out.append(f"舊檔清單比起點多了 {len(extra)} 行:審查本次照起點版、架構測試會跳過它們")」
- 重現:臨時 repo 的 main 上沒有 `.lumos/config.json`,feat 分支只新增 `.lumos/arch-legacy.json` 一行,然後呼叫 `_arch_target_check_lines(root, {}, "main..feat")`。實際輸出 `['舊檔清單比起點多了 1 行:審查本次照起點版、架構測試會跳過它們']`。
- 原因:這支函式只檢查 `if not trusted`,沒有檢查是否有宣告(`at_base[0]` 為空)。
- 少行的情況同理:沒宣告、清單少了 N 行時,會印「少了 N 行,其中 0 支這次有改動、已照目標審」。但沒有任何目標宣告,那句「已照目標審」是假話。
- 對照:計劃做法 7 和 S6 說的是「接在既有每個目標節點一行之後」,也就是有目標宣告的前提。
- 後果:三個月後接手的人看到這行,會去找不存在的目標宣告。

**2. 測試抓不到「其中 M 支這次有改動」被改成全部少掉的行數**
severity: minor
blocking: 否
- 位置:`scripts/test_lumos.py` 的 `t_arch_target_graduate_check_note` A 案,以及 `scripts/lumos` 的 `_arch_legacy_check_lines`。
- 引句:「out.append(f"舊檔清單比起點少了 {len(gone)} 行,其中 {len(gone & changed)} 支這次有改動、已照目標審")」
- 重現:把 `{len(gone & changed)}` 改成 `{len(gone)}`,再跑 `python3.14 scripts/test_lumos.py -k arch_target_graduate_check`,輸出 `5 passed, 0 failed`,照綠。改回原樣後工作樹已還原。
- 原因:A 案的清單只少了 OrderOld 一行,而它剛好有被改動,所以 N 和 M 都是 1,分不出兩個數字。
- 缺的案例:從清單刪掉一支沒改動的檔,這時應該印「少了 1 行,其中 0 支」。
- 定級:S6 明寫「其中幾支有改動」,這是需求的一部分,但只是提示行的數字、不影響審查判定,所以判 minor。

**固定席逐條判定**
- `lumos-cli-read`(search 預設排除 superseded 的合約):不影響。diff 沒碰 `search` 或其濾網。
- `guard-kill`、`design-loop`(設計審首筆帳、`.md` 審材的合約):不影響。diff 沒碰 `guard kill` 的回傳碼或 JSON 輸出,也沒碰處置閘第五步。設計審鏡頭只在目標段多扣掉清單上的檔。
- `測試假綠形態`(還原翻紅釘要有前置斷言證明現場成立):大致符合。新測試在 A、D 兩案有「畢業/還原後確實出現」的正向斷言。例外是 finding 2 那個數字,沒有獨立斷言。
- `pitfalls-code-loop`、`reversibility-governance-ledger`(兩篇都標 RISK):不影響。分級只多扣一道清單,清單讀不到時多審、不漏審,沒有改動帳本或可逆性判定。
- `arch-alignment-lens`(家):新加的兩條說明和程式一致。逐項核對了 `_arch_legacy_apply` 的畢業條件(宣告一字不改、頂端清單 ok 或 missing)、起點版清單不存在或讀不懂時當空、改名走目標。
- 其他只列名的筆記(`bound-tests-gate`、`loop-convergence-recording`、`check-r-guard` 等):不影響。這次沒碰推送前閘的分片或測試綁定。

**其餘本案鏡頭**
- 其他讀 `arch_targets` 的呼叫端:
  - `_arch_target_doctor_lines` 的「命中 N 支檔」仍把清單上的檔算進去。這是預期的,宣告命中數本來就是宣告層級的數字。
  - 張力候選吃的是 `arch["files"]`,清單上的檔會走鄰居,所以行為正確。
- 派工範本 §7.6(`~/.claude/skills/lumos-design-loop/templates.md`)沒有提到舊檔清單,但「段外照鄰居」已涵蓋。
  - 該範本裡的「範圍內舊檔只判新增或改到的行」,字面和新詞「舊檔清單」相近,但意思不同。我不確定接手的 AI 會不會混淆,⚠ 交編排者判斷是否補一句區分。
- `scripts/lumos` 的 `_at_grad` 和 `_grad` 回傳了但沒被使用。只是多餘的變數,沒有行為問題。

最嚴重等級為 minor
