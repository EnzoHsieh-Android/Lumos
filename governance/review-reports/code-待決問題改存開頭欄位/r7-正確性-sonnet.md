severity: major

以下是這輪鏡頭的發現。複查用的副本在 `/tmp/lumos-seat-work/code-待決問題改存開頭欄位/r7-正確性-sonnet/`,`before` 是 19bd4719,`after` 是 36d4ffed。`python3.14 scripts/test_lumos.py -k qfm_r` 在修後版跑出 145 passed、0 failed。

**1. signoff 帳檔不可讀但可寫時,舊帳被清成 0 位元組,訊息只說「筆記已還原」**
severity: major
blocking: 是
引句:「            log.write_bytes(log_before)」
- file: `scripts/lumos:9112`(`log_before = log.read_bytes() if log_existed else b""`)、`scripts/lumos:9093`(還原時 `log.write_bytes(log_before)`)。
- 成因:帳檔存在但讀不了時,`read_bytes` 丟 `OSError`,`log_before` 還停在初值 `b""`。
- 接著進 `_signoff_restore`,`log_existed` 為真,就把 `b""` 寫回帳檔,整份帳被清空。
- 最小重現:
  - 建兩行的 `.signoff-log.jsonl`,`chmod 200`。
  - 跑 `lumos --vault <kg> signoff Projects/p_計劃 --note x`。
  - 修前:rc0,帳變 133 位元組(追加成功)。
  - 修後:rc2,訊息是「擋下:簽核記錄寫不進去…筆記已還原」,帳檔剩 0 位元組。
- 附帶疑慮(未重現,標 ⚠):原文是鎖外讀的(`_signoff_read_original`)。別的會談在鎖外改了同一篇,帳寫失敗時的還原會用舊內容蓋掉對方的改動。
- 歸因:有證據的修復回歸。

**2. 標準 emoji 與 FE0E 被誤擋,舊筆記讀回會整份判無法判定**
severity: minor
blocking: 否
引句:「    if unicodedata.category(prev) in ("So", "Sk"):」
- file: `scripts/lumos:6957`(`_pq_vs_ok` 只認 So/Sk 後面的 FE0F)、`scripts/lumos:7009`(行尾的 FE0E 也被擋)。
- 被擋的字:‼️、⁉️、ℹ️、〰️、〽️(底字是 Po/Ll/Pd)、行尾的 `☺︎`。蒙古文自由變體選擇符 U+180B 和日文異體字序列 U+E0100 也被擋。
- 重現:`question-add Projects/p_計劃 "要不要支援‼️ 重要通知" --class 需求 --stage 需求`。
  - 修前:成功,rc0。
  - 修後:印「擋下:…控制字元(U+FE0F)」。這段訊息誤導,因為 FE0F 不是控制字元。
  - 檔案沒動,是明著失敗。
- 修前寫進去的含這類字的題,修後讀回會判無法判定。
- 歸因:有證據的修復回歸。

**3. 「可忽略字元不得相連」這條規則拆掉後,測試仍全綠**
severity: minor
blocking: 否
引句:「    if _pq_is_default_ignorable(v[i - 1]) and not _pq_adjacent_dicp_ok(v, i):」
- file: `scripts/lumos:7009`。
- 我在副本把這兩行換成 `pass`,`-k qfm_r` 仍是 145 passed、0 failed。
- 拆掉之後,`❤\ufe0f\u200c字` 與 `❤\ufe0f\u200d字`(FE0F 緊接 ZWNJ/ZWJ 再接字)從「擋」變成「放行」。
- `t_qfm_r6_unicode_table_and_positions` 的相連案例沒碰到這個組合。
- 其他拆法都有紅:
  - `WriteBlocked` 只繼承 ValueError → 3 支紅。
  - 不還原帳 → 1 支紅,但是以 EXCEPTION 紅,不是斷言紅。
  - 拿掉 decisions 檢查 → 3 支紅。
- 歸因:有證據的原有漏查(相連規則是這輪新加的,測試沒跟上)。

**4. 空白變體字元仍可當看不見的通道** ⚠
severity: minor
blocking: 否
引句:「# 三個不是 DICP、畫面仍像空白的字：Braille Pattern Blank、Object Replacement Character、」
- file: `scripts/lumos:6928`(`_PQ_BLANK_LOOKALIKES`)。
- U+00A0、U+2003、U+200A、U+202F、U+205F、U+3000、U+1680 都是 Zs 類,`_pq_bad_char` 全放行。
- 混用這些字,每格都能多藏一位元,畫面上只是寬度略不同。
- `lumos-cli-read.md:120` 已寫明「不宣稱零容量」,所以我只當 ⚠ 提出。
- 歸因:有證據的原有漏查(修前同樣放行)。

**5. 頂格「不是 `鍵: 值`」的行會讓整份判無法判定,另有工具寫出的 YAML 在多行情境下是壞的** ⚠
severity: minor
blocking: 否
引句:「_PQ_TOP_KEY_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_. -]*):(.*)$")」
- file: `scripts/lumos:7057`。
- 含 `pending_questions` 時整份開頭欄位逐行歸屬,以下頂格寫法都被當錯:
  - 頂格 `- a` 的清單(YAML 允許)。
  - 中文鍵、帶引號的鍵、數字開頭的鍵。
  - 巢狀 mapping。
- 修前只檢查 `pending_questions` 之後的行,這些寫法修前不會讓整份失效。
- repo 854 篇模擬加一題後都讀得懂,所以只影響手寫的筆記。
- 另一條無關這輪的舊問題:`decision-add --context $'背景\nid: Q9'` 會寫出頂格續行,等於壞掉的 YAML。這篇之後每次 `question-add` 都被擋。修前同樣如此。
- 歸因:有證據的原有漏查(中文鍵、頂格清單這類整份判無法判定是修後新增)。

**6. `load_raw_for_edit` 加了符號連結拒絕,唯讀呼叫端也受影響** ⚠
severity: minor
blocking: 否
引句:「        raise WriteBlocked(f"這篇筆記讀不到:{exc};檔案沒動") from exc」
- file: `scripts/lumos:20374`;`scripts/lumos:17311` 的 `_kill_p2_unbound` 是唯讀,外面包 `except Exception: continue`。
- 符號連結筆記現在會被它靜默略過。我沒實跑,所以標 ⚠。
- 歸因:未判定。

**圖譜鏡頭(固定席)**
- `Systems/lumos-cli-write.md:124` 寫「任一步丟 `RuntimeError`」。
  - 現在實際丟的是 `WriteBlocked`,它是 RuntimeError 的子類。
  - 同檔 118 行已改寫,但這句沒同步,屬過期線索,以程式碼為準。
- 同檔 118 行說簽核「筆記先、帳後」並還原。程式碼的還原路徑有發現 1 的缺口,筆記沒寫。
- `Systems/lumos-cli-read.md:120` 說 FE0E/FE0F 在合法位置放行,實際見發現 2。
- `Systems/規格閘.md` 與 `Projects/待決問題改存開頭欄位_計劃.md` 的描述與程式一致,沒發現矛盾。
- 計劃第 88 行寫「帳追加失敗要把筆記與帳都還原成原位元組」,發現 1 顯示帳還原會清空,與這句承諾不符。

**三問**
1. **原問題的修復效果有何行為證據?**
   - 甲:題目搬進 `decisions`、`aliases` 等清單外欄位時,修後都報錯(`id : Q2`、`ID: Q2` 都擋),修前這些寫法靜默放行或誤報成別的原因。拆掉 decisions 檢查後 3 支測試紅。
   - 丙:`WriteBlocked` 拆成單繼承後 3 支紅;不還原帳 1 支紅。
   - 乙:家族旗、ZWJ 家庭、🏳️‍🌈、🏴‍☠️、1️⃣、印度文字、Persian ZWNJ 都放行。
2. **修補處的正常、錯誤與相鄰呼叫路徑是否仍成立?**
   - 工具流程:`decision-add`、`append`、`signoff`、`summary-line` 在含題目的筆記上,連續呼叫後仍讀得懂。我用 28 種特殊開頭的值組合試過,沒有誤判。
   - 錯誤路徑:帳檔不可讀時不成立(發現 1)。
   - 相鄰路徑:emoji 與 FE0E 的相鄰路徑不成立(發現 2)。
   - 其餘各指令的 rc 沒看到變化:只接 ValueError 的呼叫端在 AST 掃描裡沒有同時包住寫入原語的。
3. **新發現的同一案例在修前、修後各是什麼結果?**
   - 發現 1:修前成功並追加(rc0),修後 rc2 且帳歸零。
   - 發現 2:修前成功,修後擋下。
   - 發現 3:兩版都放行相連組合,差別是修後有這條規則但測試測不到。
   - 發現 4:兩版都放行。
   - 發現 5:兩版的 `decision-add` 都寫出壞 YAML;中文鍵、頂格清單修前讀得懂、修後整份判無法判定。
   - 發現 6:未實跑。

總結句:帳檔不可讀但可寫時,signoff 的還原會把舊帳清空,這是這輪唯一會擋合併的問題;其餘是 emoji 誤擋、一條規則缺測試,以及幾個疑慮。
