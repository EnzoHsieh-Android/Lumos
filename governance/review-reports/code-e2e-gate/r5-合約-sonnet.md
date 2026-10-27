severity: major

審查範圍:r5-repair.patch(de8a99bc 到 490dac6a),以 r5-snapshot.patch 為上下文。我在臨時複本做了十個改壞實驗。「六道」的說法全 repo 一致,早退順序與程式相符,這兩項沒有問題。問題在 S41、S51–S53 綁的測試釘不住條款,外加一個修補自己造成的缺口。

**1. 太大的紀錄不算沒讀之後,裡面還沒人看過的 AI 放行完全看不到**

severity: major
blocking: 是

- file: `scripts/lumos:41923`、`scripts/hooks/claude/lumos-entry-hook.py:322`
- 失敗場景:一份已經放行過推送的 AI 放行,後來紀錄長到 2MB 以上(寫入端只擋寫之前已超過的,最後一次寫入可以越線)。r4 把「太大」改成不讀也不算沒讀,理由是「推送前判定一律擋超過上限的紀錄,裡面的放行不生效」。這句只對「現在要推的這個指紋」成立。這份放行早先已經生效過,它的稽核價值(讓人看過)就此被默默吃掉:doctor、開場掛鉤的計數和 `--ack` 都不再提它。
- 重現:我造一份 2MB 加 10 位元組、帶一筆 `acked:false` 的 AI 放行的紀錄,呼叫 `m._e2e_ai_pending_all(root)`,回 `([], 0)`;呼叫 `m._e2e_waive_ack(root, [], True)`,印「沒有還沒人看過的 AI 放行。」。修前會算進「另有 N 份沒讀」。
- 引句:「+            if p is None:   # 太大的不讀、不算沒讀(同 lumos 的 _e2e_ai_pending_all:推送前判定一律擋超過上限的紀錄)」
- 歸因:有證據的修復回歸。上一版算進 unread,r4 修補拿掉,r3 資安席指出的洞被文字上「改由判定端守」帶過。兩版查證:修前 `de8a99bc` 的 `_e2e_ai_pending_all` 對 `path is None` 做 `unread += 1`,修後 `490dac6a` 直接 `continue`。

**2. S41「太大的不算沒讀」沒有任何斷言釘住**

severity: major
blocking: 是

- file: `scripts/test_lumos.py:20411`(`t_android_e2e_record_scan`)、`docs/lumos-toolchain-knowledge/Systems/codex-harness.md:45`
- 失敗場景:S41 和 codex-harness 的 WHY 都說太大的「不算沒讀」,綁的 test 是 `t_android_e2e_record_scan` 和 `t_android_e2e_gate_r4_paths`。record_scan ② 只斷言兩邊(lumos 與掛鉤)數字彼此一樣,不問絕對值。
- 重現:把 `scripts/lumos` 和掛鉤兩處的 `path is None` 都改回 `unread += 1`。`-k t_android_e2e_record_scan` 是 14 passed、0 failed,`-k t_android_e2e_gate_r4_paths` 是 4 passed、0 failed,`-k t_android_e2e_ai_count_copies_agree` 是 8 passed、0 failed。條款被改壞,三支綁定的測試全綠。
- 引句:「+- [S41] 當 doctor 與開場提示讀工作目錄的紀錄時,兩處應用同一套規則:照修改時間由新到舊最多 500 份、單份 2MB(太大的佔名額不讀、不算沒讀:」
- 歸因:有證據的修復回歸。這個條款文字是 r4 修補改的,測試沒跟著更新。

**3. S51 的測試只釘住一小部分被保護的行為**

severity: major
blocking: 是

- file: `scripts/test_lumos.py:20906`(`t_android_e2e_text_gates`)、`scripts/lumos:40273`、`41134`、`41152`、`41982`、`42131`、`42141`、`40531`
- 失敗場景:S51 說「e2e 指令印的每一行『擋下:』都應清掉控制字元」,也說 app_dirs、exclude、shared_paths 超過 1000 項要不合格。實際釘住的只有 `waive_ack`(42011)和 `waive_cmd` 那三處的清理,以及 app_dirs 超過 1000。
- 重現一:把 `_e2e_say_block` 在 40273、40301、41134、41152、41982、42131、42141 這七處改回原樣印出,`-k t_android_e2e_text_gates` 與 `-k t_android_e2e_input_guards` 仍全綠(8 passed、9 passed)。
- 重現二:把 40531 的 `len(sp) > E2E_DIR_LIST_MAX` 改成 `> 10**9`,text_gates 仍是 8 passed、0 failed。shared_paths 超過 1000 項的上限沒有斷言。
- 另外,條款寫的是 `macrobench --check-config` 判不合格,測試只直接呼叫 `_e2e_relpath_err`、`_e2e_paths_err`、`_e2e_shared_paths_err` 三個函式,沒走指令。
- 引句:「+- [S51] 當設定的路徑含控制字元、換行或看不見的格式字元、超過 64 層,或 app_dirs、exclude、shared_paths 超過 1000 項時,`macrobench --check-config` 應判不合格;e2e 指令印的每一行「擋下:」都應清掉控制字元」
- 歸因:有證據的修復回歸。條款和測試都是 r4 修補新增的,「統一出口」的好處沒有逐出口測試守。

**4. S53「上一版查不出來時應擋」,測試把被審的函式整個換掉了**

severity: major
blocking: 是

- file: `scripts/test_lumos.py:20984`(`t_android_e2e_gate_r4_paths` ②)、`scripts/lumos`(`_e2e_parent`)
- 失敗場景:測試用 `m._e2e_parent = lambda ...: (None, "git 失敗(測試造的)")` 蓋掉真函式,只驗得到呼叫端「有 gerr 就擋」,驗不到 `_e2e_parent` 自己在 git 失敗時會回錯誤。
- 重現:把真的 `_e2e_parent` 的失敗分支改成 `return "", None`(退回 r4 要修的「git 失敗當成沒有上一版、放行」),`-k t_android_e2e_gate_r4_paths` 是 4 passed、0 failed,`-k t_android_e2e_gate` 是 120 passed、0 failed。
- 引句:「+        return None, f"查不出 {sha[:8]} 的上一版(git 失敗或逾時)"」
- 歸因:有證據的修復回歸。這個函式和測試都是 r4 修補新增的。

**5. S52 / WHY 的「git 暫時失敗不叫人刪」,真正產生錯誤型別的地方沒被測**

severity: major
blocking: 是

- file: `scripts/test_lumos.py:20950`(`t_android_e2e_record_size_gate`)、`scripts/lumos`(`_e2e_tree_blob` 三處 `_E2eGitErr(...)`)
- 失敗場景:測試把 `_e2e_tree_json` 整個換成直接回 `_E2eGitErr`,只驗得到 `isinstance` 分流。
- 重現:把 `_e2e_tree_blob` 三處 `_E2eGitErr(f"...")` 還原成純字串,`-k t_android_e2e_record_size_gate` 是 4 passed、0 failed,`-k t_android_e2e_gate` 是 120 passed、0 failed。這等於 git 暫時失敗時又會叫人把好紀錄刪掉,而 r4 要修的正是這個。
- 引句:「+        _e2e_gate_block(f"查證紀錄 {rerr}", bad_record=not isinstance(rerr, _E2eGitErr), **info)」
- 歸因:有證據的修復回歸。

**6. README 兩版列的「不印放行指令」擋下不全,「要先合主線」那條也講不準**

severity: minor
blocking: 否

- file: `README.md:391`(同一段在 `README.en.md:391`)、`scripts/lumos` 的 `_cl_say_e2e_block` 與 `_e2e_gate_body`
- 失敗場景:中英兩版意思一致,都列「找不到主線、逾時、要先合主線、拿掉驗收設定、紀錄讀不懂」。實際不印放行指令的擋下還有四類:提交裡的 e2e 段不合格、算不出分岔點(沒有共同祖先或淺層 clone)、讀不到要推的提交或列不出改了哪些檔、紀錄超過 2MB(`bad_record`)。
- 另一個不準的地方:`mainline_newer`(主線的驗收要求比這一版新)那種「要先合主線」的擋下,因為帶 `fp`,同時印合併指令和放行指令。只有 `merge_main` 那種(沒帶 fp)才不印。
- 重現:讀 `_cl_say_e2e_block` 末段條件 `rep.get("fp") and not bad_record and not newer_schema`,對照 `_e2e_gate_block` 各呼叫點有沒有帶 `**info`,即可看出。
- 引句:「+**推送前會擋。** 推送前的檢查從被推送的提交裡讀這一版的查證紀錄」
- 歸因:未判定。上一版只列「拿掉驗收設定、紀錄讀不懂」,這輪擴寫後仍不全,不是這輪才出現的類型。

**7. pre-push 掛鉤的註解還寫「三個獨立判定」**

severity: minor
blocking: 否

- file: `scripts/hooks/pre-push:542`
- 失敗場景:註解說「合約測試紅 / 有適用題表態不完整 / tier=high 無留痕,三個獨立判定」,與現在的六道不一致。
- 引句:「+- pre-push 和 CI 對每個分支 ref 都叫 `code-loop check`:有資安登記時安全證據不合格(排最前、不看 tier)、合約測試紅」(這是這輪補成六個獨立判定的那一句,與掛鉤註解不一致)
- 歸因:有證據的原有漏查。這行不在 r5-repair.patch 裡,是舊註解沒隨安全證據、新增告警、e2e 三道的加入更新。純註解,不影響行為。

**三問**

1. **S41、S51–S53 每條說的行為,程式真的那樣做嗎?** 程式行為都對。早退順序是安全證據、Android、合約測試、表態、新增告警、留痕,與 `pitfalls-code-loop.md` 的說法一致。`cfg_weakened` 與 `mainline_newer` 的分流也有測試守。但 S41 的「不算沒讀」有第 1 條的設計缺口。
2. **綁的 [test:] 驗了條款說的行為嗎?** 沒有,見第 2–5 條。改壞後仍全綠的有四個:太大的算不算沒讀、七個「擋下:」出口的清理、shared_paths 超過 1000 項的上限、`_e2e_parent` 與 `_E2eGitErr` 的真實產生處。被正確釘住的有:判定端 2MB 上限(改回 16MB 會紅)、錯誤型別分流的呼叫端、改弱設定的訊息、結束時間讀不懂不覆蓋(只驗了 waive,沒驗 judge 重跑)。
3. **「六道」在全 repo 一致嗎?** 一致。`git grep` 沒有殘留「五道」或「五個獨立判定」;SKILL.md、reference.md、06、08 與 `scripts/lumos` 的幾處說明都已是六。例外只有第 7 條那行舊註解。

最高等級:major,擋實作的 5 條(第 1–5 條)。
