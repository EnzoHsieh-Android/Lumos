severity: major

總評:程式本身我沒找到會讓提交或推送壞掉的實作錯誤,`t_slots*` 88 條在我的複本上全綠。洞在三處:測試咬不住推送那一側的行為、掛鉤旗標的位置有一個靜默失效的坑、開擋前的提示有噪音。圖譜鏡頭的固定席筆記派工詞沒附,我也沒跑 `lumos impact`。新增到 `Systems/筆記內容閘` 的 WHY 帶 `[test:t_slots_own_golive]`,那條測試確實釘住「掛鉤沒帶就不跑、記號之後才查」,這點不影響。

**U1 推送時「只改欄位的舊行」的豁免沒有任何測試咬住**
severity: major
blocking: 否 — 目前程式是對的,但將來這段壞掉,全套測試仍然全綠,開擋後會擋掉所有舊行補欄位的推送。
引句:「deleted = _ns_deleted_summary_lines(repo_root, base_where or _EMPTY_TREE_SHA, tip_where, "--", vault_rel)」
- `t_slots_edited_old_line` 只跑 `--staged`。推送一側的舊行來源有三條:範圍起點版本、範圍刪掉的行、上線前提交寫的行,測試一條都沒碰。
- 重現(在我的複本,改完要把 `scripts/lumos` 還原):
  1. 把 `_ns_slots_old_lines` 推送分支的 `old_reader` 改成 `(lambda _p: None)`,`deleted` 改成 `[]`。
  2. 場景:掛鉤帶 `--slots`,提交一行沒填欄位的舊 WHY,再在下一個提交補 `[applies:scripts/lumos]`,最後 `note-shape --diff base..tip`。
  3. 結果:原版 rc 0,改壞後 rc 1(`Systems/A.md:15  缺 [出處:]、[因:]`)。
  4. 改壞後 `python3.14 scripts/test_lumos.py -k t_slots` 仍是 88 passed, 0 failed。
- 只拿掉其中一道(範圍起點版本)推送也不會變,因為範圍刪掉的行會補上同一批舊行。測試要兩道一起拿掉才會紅,而現有測試兩道都咬不到。
- 缺的測試:推送版的「補欄位舊行不擋」。

**U2 推送時改名後的格子上線記號沒有測試,拿掉就靜默放行**
severity: major
blocking: 否 — 目前程式正確,是測試缺口。
引句:「for d_ in (by_path, old_by, by_path2):」
- 重現:
  1. 掛鉤帶 `--slots` 之後,提交一個缺格子的新 WHY,再提交把那篇 `git mv` 改名,然後 `note-shape --diff base..tip`。
  2. 原版 rc 1,擋下。
  3. 把 `_carry` 裡的 `by_path2` 拿掉,同場景 rc 0,缺格子的行被當成「上線前寫的」。
  4. `t_slots*` 沒有任何改名案例,不會紅。
- 這是推送端、CI 與 doctor 事後掃描共用的路徑。整批靜默漏查,方向是 fail-open,沒人會發現。

**U3 掛鉤記號依賴旗標順序,順序一換推送、CI、doctor 全部靜默失效,護欄測試也抓不到**
severity: major
blocking: 否 — 這一步的範本還沒帶 `--slots`;陷阱落在下一步「開擋步」,但守住它的測試在這個 diff 裡且太弱。
引句:「_SLOTS_GOLIVE_MARK = "note-shape --staged --slots"」
- 現有掛鉤行是 `note-shape --staged --repo "$REPO_ROOT"`(`scripts/hooks/pre-commit:230`)。最自然的改法是在行尾接 `--slots`。
- 重現,兩種順序對照:
  1. 順序 `--staged --repo X --slots`:提交時 rc 1(argparse 認得,擋得住);推送 `--diff` rc 0,整段不跑;doctor 還說「掛鉤沒帶 --slots」,講錯。
  2. 順序 `--staged --slots --repo X`:提交與推送都 rc 1,doctor 無提醒。
- 測試 `t_slots_own_golive` ⑤ 寫的是 `len(hits) <= 1`。範本裡完全沒有記號(0 次)也算過,所以順序寫錯照過。
- 建議把 ⑤ 改成:開擋提交之後必須正好 1 次,並釘「`--slots` 緊接 `--staged`」。

**U4 doctor 在每個專案、每次推送都永久唸一條「格子規則沒在跑」**
severity: minor
blocking: 否 — 只提醒,不影響 rc。
引句:「out.append("筆記格子規則沒在跑:提交前掛鉤沒帶 --slots(開擋前是正常狀態;開擋後 lumos update 會換上帶它的掛鉤)")」
- `_note_shape_doctor_lines` 放在 ci 返回之前,所以 `doctor --ci`(pre-push 每次都跑)也會印。
- 我在複本跑 `doctor --ci`,第 2 行就是這條 ⚠,還多算進「另有 26 段提醒」。
- 計劃要求開擋前至少 14 天,這段時間所有人天天被唸一條自己說「正常狀態」的提醒。
- 要嘛只在 `slots` 不是 block 或掛鉤帶了旗標卻缺記號時唸,要嘛附 `REVISIT` 到期。

**U5 只因格子被擋時,收尾句講錯原因**
severity: minor
blocking: 否 — 擋下清單與範本本身清楚。
引句:「print("內容還在工作目錄,改完再提交(這道檢查不動筆記、不動暫存區)。為什麼擋:筆記只留程式碼推不出來的東西,"」
- 沒有任何形狀違規、只有格子缺漏時,仍印「為什麼擋:筆記只留程式碼推不出來的東西」。這跟格子無關,第一次被擋的人會被誤導。
- 推送模式(`--diff`)也印「改完再提交」,但那一側要的是改歷史。實測 E4 場景(見 U8)的輸出就是這樣。

**U6 治理帳 `slots_missing` 只算得到「缺 [鍵:]」那類問題**
severity: minor
blocking: 否 — `slots_lines` 仍準。
引句:「for k in re.findall(r"\[([^\[\]:]+):\]", x):」
- 實測 `slot_check` 的輸出:
  - 「缺 test、repro、防回歸 三選一」→ 解出 `[]`。
  - 「[retire:改用新閘] 不是機器式…」→ `[]`。
  - 「when-symbol 要帶路徑」→ `[]`。
  - 「缺 [until:]」→ `['until']`。
- 所以最常見的 PITFALL 缺防回歸,會讓帳上 `slots_lines=1` 配 `slots_missing={}`。
- 這個欄位的用途是配 RETIRE-IF,看哪個鍵最常缺。測試 ① 只釘「出處」一種,抓不到這個漏洞。

**U7 doctor 事後掃描與 20 條上限沒有測試**
severity: minor
blocking: 否
引句:「sv = _ns_slots_collected(root, False, gl, tip, vault_rel, sbox) if res else []」
- 對 `scripts/test_lumos.py` 搜尋「筆記格子缺漏的新增行」、`_ns_slots_doctor_box`、「另 N 行(共」都是 0 筆。
- 把這行改成 `sv = []`,現有測試沒有任何一條會去看它。
- `_NS_SLOT_SHOW` 的截斷也沒有超過 20 條的案例。

**U8 提交通過、推送被擋的落差,訊息跟使用者做的事對不上**
severity: minor
blocking: 否 — 行為合理(那行本來就缺格子),只是訊息容易讓人困惑。
引句:「if not staged and ln.strip() not in (live2 or {}).get(nfc(p), ()):」
- 重現(E4):
  1. 提交 1 用跳過或 `--no-verify` 帶進缺格子的 WHY。
  2. 提交 2 只補了 `[applies:x]`,提交時對 HEAD 是「舊行」,rc 0。
  3. 推送時對範圍起點它是新行,rc 1。
  4. 輸出卻寫「只改了欄位的舊行不算新寫」,跟使用者剛才的操作矛盾。
- 訊息應講明:這行是在這段推送範圍內才出現的。

最高嚴重度 major,blocking 0 條
