severity: major

這份 diff 的實作沒有判錯的輸入:我走了清單與宣告各種組合、NFC/NFD、改名、沒有主線、修補輪增量範圍,畢業判定都對。找到一個測試漏洞(major)和兩個小問題(minor)。

## Findings

**1. 測試抓不住「清單改讀增量起點版」**

severity: major
blocking: 是

位置:`scripts/lumos:57439`(`_arch_legacy_apply` 的 `ref` 參數),呼叫點在推送前分級和代碼審派工鏡頭。測試在 `scripts/test_lumos.py` 的 `t_arch_target_graduate_same_branch`。

引句:「targets, _grad = _arch_legacy_apply(root, ref, h, targets, rules)」

失敗場景如下。

- 修補輪的範圍起點 `b` 是分支自己的提交,不在主線上。
- 規則是清單和宣告都讀分叉點版 `ref`,不讀 `b`。
- 這是「分支自己加的清單不能決定自己怎麼被審」的唯一保護。
- 把 `ref` 改成 `b`,推送前分級那處也同樣改成 `_at_base`,17 支 `arch_target_graduate` 測試仍然全綠(17 passed, 0 failed)。
- 原因是所有測試的範圍起點都是 `main`,`b` 和 `ref` 剛好相同,改壞也不會翻紅。

最小重現是在拋棄式的 clone 裡加一支探針測試:

1. `main` 沒有清單。
2. C1 新增清單,列出 OrderOld 和 OldHelper。
3. C2 改這兩支檔。
4. 審查範圍用 `C1..HEAD`。

結果如下。

- 未改壞的程式:探針 2 項斷言全過,兩支檔都照目標審。
- 改壞的程式(`ref` 換成 `b`):探針 2 項都紅。
  - 推送前分級的輸出裡,OrderOld 不在 targets。
  - 派工鏡頭的 arch_text 裡兩支檔都沒附。

所以改壞版會讓分支靠自己加的清單逃過目標審,測試完全沒抓到。條款 S5 的「起點版清單不存在時清單不起作用」也只在 `base == main` 時驗了。

我已刪除探針 clone 和暫存現場。

**2. 沒有宣告時,說明行仍印「已照目標審」**

severity: minor
blocking: 否

位置:`scripts/lumos:57726` 的 `_arch_legacy_check_lines`。

引句:「out.append(f"舊檔清單比起點少了 {len(gone)} 行,其中 {len(gone & changed)} 支這次有改動、已照目標審")」

失敗場景:

1. 起點和頂端都沒有 `arch_targets`,即 `at_base == at_head == ([], [])`,所以 `not at_base[1]` 成立。
2. 兩版都有 `.lumos/arch-legacy.json`,頂端少一行。
3. 這時不會有任何目標審,但說明行照印「其中 0 支這次有改動、已照目標審」。
4. 「多了行」那行同理,會印「架構測試會跳過」。

這只影響說明文字,不影響判定。

**3. 舊檔清單 git 失敗被說成「讀不懂」**

severity: minor
blocking: 否

位置:`scripts/lumos:57464` 的 `_arch_legacy_doctor_line`。

引句:「if state != "ok":」

失敗場景:

- `_arch_legacy_at` 可能回 `unreadable` 或 `git-failed`。
- doctor 把這兩種都印成「讀不懂(要是 {"files": …})」,git 逾時時會誤導人去改一份沒壞的檔。
- 只提醒不擋。

## 逐項檢查與固定席判定

- **本案特定鏡頭,頂端版改法**
  - 頂端版清單、宣告、目標節點筆記、合併主線,都只能讓檔從「鄰居」變成「目標」,不能反向。
  - 頂端多出的行不影響審查;宣告相同的比對用解析後的規則,結果是失敗時偏嚴。
  - 規則原文照讀起點版。
- **三處判定一致性:一致**
  - 推送前分級、派工鏡頭、說明行共用同一組改動檔函式,以及相同的畢業條件。
  - 說明行與判定的條件等價。
  - 沒有主線時,推送前分級讀起點,派工鏡頭整段不附,和計劃一致。
- **過期的清單項目**
  - 沒有主線、起點版清單缺失、清單讀不懂時,都是失敗偏嚴。
  - 例外:清單裡殘留已刪除檔的路徑,之後有人在同路徑新建檔,會被當舊檔照鄰居審,偏鬆。
  - 這是計劃本身的設計,doctor 已有「已不存在」計數提醒,所以我沒另列。
- **測試品質**
  - 把 `h_rules == rules` 拿掉,B 案會紅。
  - 把 `h_state in (...)` 拿掉,C 案會紅。
  - 把 `keep` 改成不減頂端清單,A 案會紅。
  - 設計審路徑不讀清單,S11 測試會紅。
  - 除了 Finding 1,沒有 NFC/NFD 的行為測試;但名稱正規化出錯只會往偏嚴的方向錯,所以不另列。

固定席節點(`impact --diff` 附的那批):

| 節點 | 判定 | 原因 |
|---|---|---|
| `Systems/arch-alignment-lens`(家) | 不破壞,但被放寬 | 該節點說「宣告只讀起點、分支改的下次才生效」,diff 已同步補上畢業例外與清單分工。程式只開「宣告相同時、清單被刪的檔」這一個口。 |
| `Systems/pitfalls-code-loop` | 不影響 | 風險分級的 tier 判定沒動,只改 `arch_alignment` 的 targets。 |
| `Systems/design-loop` | 不影響 | 設計審只多讀一份 HEAD 清單分流,處置閘的判定沒動。 |
| `Systems/lumos-cli-read` | 不影響 | 沒動 `search`。 |
| `Systems/guard-kill` | 不影響 | 沒動 guard。 |
| `Systems/測試假綠形態` | 不影響 | 沒動它綁的測試。 |
| `Systems/reversibility-governance-ledger` | 不影響 | 沒動帳本。 |
| `Issues/code-loop守衛main-direct盲區` | 不影響 | 沒動 main-direct 判定。 |

- 角色鏡頭:本次沒附卡,略過。
- pitfalls manifest:本次沒有要答的檢核題,略過。
- 計劃檔的 `lands_in` 列了 `Systems/android-arch-template`,這個節點目前不存在。這是產生器那半尚未做,屬已知範圍,未列為 finding。

最嚴重等級為 major
