severity: major

我沒有改動 qo-frontmatter 本體。實驗都在 `/tmp/lumos-seat-work/code-待決問題改存開頭欄位/r4-合約圖譜-sonnet/` 的副本裡做(`repo` 是 d6bb423f,`before` 是 d6bb423f 的測試搭 646dc3a8 的 `scripts/lumos`,`mut-*` 是拆掉一道修補的變體)。有一點要說明:我用 grep 全 repo 找過期句時,輸出帶出了 r3 卷證的幾行摘錄,但沒有拿它們當依據。

## 修補驗收

- **S1–S7 與程式不一致。** 程式現在放行 U+200D 等 emoji 組合用的格式字元,S2 和 S3 的字面卻仍寫「格式字元要拒」。
- **條款綁定對不齊。** `t_qfm_r3_folds` 綁在 S1 和 S2,但它的主要斷言(寫入鎖範圍、逾時擋下)屬於 S3,而 S3 沒綁它。
- **寫入鎖說法大致成立。** 用語法樹逐一查了 `atomic_write_verify(` 的呼叫者:除了 `_guard_settle_pass` 與 `_drift_fix_write` 在本函式內自己拿鎖,其餘都由外層拿鎖。`_vault_lock_held_for` 對路徑做了 realpath 前綴比對。amend 的 fetch 確實在鎖外。
- **有一處過度宣稱。** 「逾時一律擋下」不成立,下面第三條。
- **新斷言抓得到大部分真錯。** 把新測試拿去跑修前程式:15 條紅,9 條綠。副本拆道實驗中,拆掉完全相符優先、`_is_commit` 檢查、guard 的 RuntimeError 捕捉都會紅。有三道拆了不會紅,見第四條。
- **相關測試全過。** `-k qfm` 195 條全過。

## Findings

**1. 條款 S2、S3 字面與現行程式相反**

severity: major
blocking: 是

引句:「任何值含控制字元、格式字元或 U+2028/U+2029 應回 2 且不改檔」

- 佐證:`docs/lumos-toolchain-knowledge/Projects/待決問題改存開頭欄位_計劃.md` 的 S3 條款;S2 有同型字句「值含控制字元或格式字元或 U+2028/U+2029」。
- 現象:r3 修補讓 `_pq_bad_char` 放行 U+200C、U+200D、U+00AD 和旗幟標籤字(`scripts/lumos` 的 `_pq_cf_ok`)。這些都是格式字元,條款沒改。
- 重現:`python3.14 repo/scripts/lumos --vault v question-add Projects/p_計劃 $'家庭\u200d要' --class a --stage 需求`,rc=0 且寫入。同樣用 `$'甲\u200b乙'`(零寬空格)則 rc=2。
- 後果:S3 照字面驗 U+200D 應回 2,實際回 0。S2、S3 是規格閘的驗收依據,依它出的反例會與程式對打。
- 歸因:有證據的修復回歸。修前同一輸入被擋(`before` 跑 `t_qfm_r3_folds` 的 ③ 紅,訊息是「值裡有控制字元…(U+200D)」)。計劃正文第 21 行和 `_pq_bad_char` docstring 已改,只有兩條款沒跟上。

**2. `t_qfm_r3_folds` 的綁定與條款字面對不上**

severity: minor
blocking: 否

引句:「[test: t_qfm_gate_holds_blocking, t_qfm_push_remind_ranges, t_qfm_r2_folds, t_qfm_r3_folds]」

- 佐證:同一份計劃的 S1、S2、S3 條款。
- 該測試的 24 條斷言分布:
  - ①②③ 屬 S2。
  - ④ 屬 S4 的決策連結。
  - ⑤ 其他筆記庫的鎖不算數、⑥ 逾時回「擋下」屬 S3。S3 的條款字面沒有這兩個行為,也沒綁這支測試,只有「沒拿鎖就不寫」。
  - ⑦ 範圍 `-` 開頭或 git 認不得則跳過,綁在 S1,但 S1 字面也沒寫。
  - S2 同樣缺「清單被中間頂格鍵切斷」和「旗標大小寫不分」。
- 後果:這些行為只有計劃正文寫了,條款沒覆蓋,`spec-trace` 看不出缺口。
- 歸因:有證據的修復回歸,綁定是這輪新加的。`lumos spec-trace` 對該計劃顯示 S1–S6 全部「綁了」,所以工具不會抓到。

**3. 「鎖逾時一律擋下 rc2」不成立**

severity: minor
blocking: 否

引句:「鎖殘留時這些指令會等 60 秒才回」

- 佐證:`scripts/lumos` 中 `cmd_guard_plan`(約 15513)、`cmd_guard_abandon`(約 16214)、`cmd_guard_kill_add`(約 17126)。`Projects/待決問題改存開頭欄位_計劃.md` 的審計紀錄與 `Systems/lumos-cli-write.md` 的 WHY 代價句都這樣宣稱。
- 重現:`python3.14 sweep/sweep.py repo/scripts/lumos`。它把 `_vault_write_lock` 換成拋 RuntimeError,在 git 初始化過的筆記庫裡逐指令跑。結果:
  - amend、guard bind、guard audit、set、append、remove、決策各指令、question-add/set、dref-add-ai/promote、self-audit 都是 rc=2 加「擋下」。
  - guard plan、guard abandon、guard kill-add 是 CRASH,RuntimeError 沒被捕捉。
- 這三個指令也在「讀改寫開頭欄位的入口」之列,並寫入開頭欄位。
- 歸因:有證據的原有漏查。在修前的 `before/scripts/lumos`(646dc3a8)跑同一腳本,這三個也是 CRASH,這輪沒碰它們。「一律」這句宣稱是這輪新寫的。

**4. 三個新斷言抓不到對應的真錯**

severity: minor
blocking: 否

引句:「out_file = d / "pwn.txt"」

- 佐證:`scripts/test_lumos.py` 的 `t_qfm_r3_folds`。
- ⑦ 的 CLI 兩條:`--push-check --output=…` 這種寫法在 argparse 就被拒(rc2),根本到不了 `_spec_gate_push_check` 的 `-` 開頭守衛。即使真放行,git 寫出的檔名是 `pwn.txt..HEAD`,不是斷言查的 `pwn.txt`。
  - 拆道實驗:刪掉 `_spec_gate_push_check` 的 `startswith("-")` 守衛,測試仍全綠(24 passed)。
  - 手動以 `--push-check="--output=/tmp/…/pwn.txt..HEAD"` 重現:拿掉守衛會真的寫出 `pwn.txt..HEAD`,現行碼不寫。守衛有效,只是測試沒釘住。
- ⑥ 的 decision-amend:測試用的筆記庫不在 git 裡,amend 在 git 檢查就回 rc2,根本沒走到拿鎖。
  - 拆道實驗:把 amend 分派的 `except` 改回只收 ValueError,測試仍全綠。
  - 在 git 初始化過的筆記庫手動驗證:拆掉會 CRASH,現行碼是 rc2。
- ⑤ 沒有兄弟筆記庫前綴的反例:把 `startswith(v.rstrip(os.sep)+os.sep)` 改成 `startswith(v)`,全綠。
- 歸因:有證據的修復回歸,這些斷言是新加的。

**5. 過期句**

severity: minor
blocking: 否

引句:「所有讀改寫開頭欄位的入口都經 `_vault_locked` 拿鎖」

- 佐證:`docs/lumos-toolchain-knowledge/Systems/lumos-cli-write.md` 約第 150 行。`_vault_locked` 這輪已從 `scripts/lumos` 刪除,改成各指令自己拿鎖。
- 同類殘留:`docs/lumos-toolchain-knowledge/Systems/情境出題.md` 第 6 行「(改存開頭欄位另案)」。該功能已上線,同篇第 26、45 行已寫上線。
- 其他 grep 結果:
  - `_pq_git_read_many` 與 `\0paths` 全 repo 零命中。
  - `last-write-wins` 在 `scripts/lumos` 零命中。docs 的兩處命中是在描述別的流程,不算過期。
  - `Projects/後端工程提問與證據擴充_計劃.md` 的決策 d10 與關卡表「S2 移到另案」是已作廢決策的歷史,不算過期。
- 歸因:有證據的原有漏查。`情境出題.md` 本輪不在修補差異內。`lumos-cli-write.md` 第 150 行在修前就含 `_vault_locked`,只是這輪才讓它變過期。

## 圖譜鏡頭

七篇的 `lumos lint` 在 d6bb423f 副本都是 0 問題。`lumos doctor` 的 S8–S10 在副本出現的是既有帳目提醒,沒指向本輪新增的函式。

- **`Projects/待決問題改存開頭欄位_計劃.md`:** 正文與程式一致:範圍切斷、旗標大小寫、字元例外、完全相符優先、鎖都對得上。條款有 finding 1、2 的問題。審計紀錄的鎖逾時句有 finding 3 的問題。
- **`Projects/後端工程提問與證據擴充_計劃.md`:** 摘要第 38 行(d10 由 d13 取代)正確。表內的「另案」是歷史,可接受。
- **`Systems/lumos-cli-write.md`:**
  - T1 第 0 步成立。
  - 「cmd_* 拿鎖再叫 _*_locked」成立,question-add/set 是直接包鎖。
  - amend 的 fetch 在鎖外成立。
  - 逾時一律擋下不成立(finding 3)。
  - 第 150 行過期(finding 5)。
- **`Systems/規格閘.md`:**
  - `_pq_renames` 與 `_nodehome_cat_blobs` 存在。
  - `_nodehome_name_status(...)[1]` 的方向(新對舊)正確。
  - `_spec_gate_push_check` 的家在這篇與 `bound-tests-gate`,說法一致。
- **`Systems/lumos-cli-read.md`:** `_pq_scan`、同一次判定每篇只解析一次、`resolve_test_refs` 的說法和程式一致。內容沒寫 r3 新增的規則,但也沒說錯。
- **`Systems/情境出題.md`:** 第 6 行殘留「另案」(finding 5),其餘已改為上線。
- **`Systems/pitfalls-code-loop.md`:** `--stage` 一段與 `t_qfm_stage_lists_open_questions` 一致,REVISIT 已結案標記正確。

## 三問

① **修復效果的行為證據。**
- 修前(646dc3a8 搭新測試)15 條紅、9 條綠,修後 24 條全綠。
- 拿 A 庫的鎖寫 B 庫的檔:修前「寫了」,修後拒寫。
- amend、guard bind、guard audit 鎖逾時:修前 CRASH,修後 rc=2 加「擋下」。
- `--push-check="--output=/tmp/…/pwn.txt..HEAD"`:修前寫出 `pwn3.txt` 與 `pwn3.txt..HEAD`,修後兩個檔都沒有。

② **修補處的正常、錯誤與相鄰路徑。**
- 所有 `atomic_write_verify` 呼叫者仍在鎖內。
- `-k qfm` 195 條通過。
- 逾時路徑有一個相鄰缺口:guard plan、guard abandon、guard kill-add 仍 CRASH(finding 3)。

③ **新發現的同一案例,修前與修後。**
- U+200D 題目:修前 rc=2(被拒),修後 rc=0(寫入)。程式是有意放行,條款沒跟上(finding 1)。
- guard plan、abandon、kill-add 鎖逾時:修前和修後都是 CRASH,沒變。
- 三個沒抓到真錯的斷言(finding 4):修前和修後測試都綠。

總結:程式側的 r3 修補在行為上成立;阻擋合併的只有一個,就是 S2、S3 條款字面與放行格式字元的現行程式相反,另有四個不擋合併的小問題。
