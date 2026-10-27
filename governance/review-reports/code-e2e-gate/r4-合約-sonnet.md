severity: major

鎖檔 `…/68797ffe…json.warming` 不存在,沒有鎖要處理,照派工詞審查。我只動了 `/tmp/lumos-seat-work/code-e2e-gate/合約-sonnet/` 裡的複本,審完已刪。

**LUMOS-IMPACT**:這份只有範圍,沒附固定席節點。「這次新增的殘留」段沒有可回報的條目。圖譜方面,S41、S43–S50 和三條 PITFALL、一條 WHY 的 `[test:]` 我逐條對過程式與測試,結果在下面的 finding。

審到的測試,我另外單獨跑過:`android_e2e_record_scan` 14 項過、`android_e2e_waive_all_records` 5 項過、`android_e2e_record_unreadable` 8 項過、`android_e2e_ai_count_copies_agree` 8 項過。

**1.**
severity: major
blocking: 是
引句:「pre-push 帶 `--keep-going`(lumos 認得時):五道都判完再擋,一次看到全部原因」
file: `skills/lumos-code-loop/SKILL.md:13`
失敗場景:這輪把同一行前半改成「六個獨立判定」,後半的「五道都判完再擋」沒改,一行裡自相矛盾。「六道」現在全 repo 還有三處留著五:`skills/lumos-code-loop/reference.md:612` 的「五個獨立判定」、`skills/lumos-project-notes/commands/06-代碼審與推送.md:8` 的「五個獨立判定」、上面這行。接手的人讀 skill 會以為 e2e 驗收不在 `--keep-going` 一次列出的範圍裡。
重現:`git grep -nE "五道都判完|五個獨立判定" -- skills`。
歸因:有證據的修復回歸。`SKILL.md` 這行是這輪改的,只改了一半。reference.md 和 commands/06 是有證據的原有漏查,舊的接線清單沒掃到它們。
兩版查證:修前版 `SKILL.md` 整行都是五;修後版只剩後半句是五。

**2.**
severity: major
blocking: 是
引句:「單份超過 2MB→放行不寫、判定擋下叫人修好或刪掉」
file: `docs/lumos-toolchain-knowledge/Projects/Android端到端驗收_計劃.md:S46`、`scripts/lumos:41408`
失敗場景:S46 說單份紀錄超過 2MB 時判定會擋。判定讀提交樹走 `_e2e_tree_blob`,上限是 `_SECEV_FILE_MAX = 16MB`(`scripts/lumos:8524`),2MB 這個上限只在 `waive` 寫回和掃描路徑。所以 2 到 16MB 的紀錄判定會照常放行,只有 `waive` 拒寫,條款說的行為程式沒做。綁的 `t_android_e2e_record_unreadable` ⑤ 只驗 `waive` 回 2,沒驗判定那一半,所以測試照綠。
重現:讀 `scripts/lumos:41408` 與 `:8524`、`:41824`,三個常數對不上。我沒有跑出真的放行結果,依規則自降一級的話是 major,維持 major 是因為這是對條款的直接反證。
歸因:有證據的修復回歸。S46 與 `_e2e_record_update` 的大小檢查是這輪新加的。
兩版查證:修前版沒有 S46,也沒有 `_e2e_record_update` 的大小檢查;修後版條款宣稱判定也擋,程式只有 `waive` 擋。

**3.**
severity: major
blocking: 是
引句:「`bad_record="git" not in rerr`」
file: `scripts/lumos`(`_e2e_gate_load`)、條款 S46 的「git 暫時讀不出→不叫人刪」
失敗場景:這個行為沒有測試守。改壞重現:把 `bad_record="git" not in rerr` 改成 `bad_record=True`,跑 `python3.14 scripts/test_lumos.py -k android_e2e_record_unreadable`,結果 8 passed, 0 failed,照綠。改壞後 git 暫時失敗也會叫人刪紀錄,這是條款明寫要避免的操作。另外這條靠訊息字串裡有沒有「git」來分類,訊息措辭一改就悄悄翻轉。
歸因:有證據的修復回歸。這輪才加這個分流。
兩版查證:修前版一律 `bad_record=True`,沒有分流;修後版有分流但沒有對應測試。

**4.**
severity: major
blocking: 是
引句:「太大的不讀,但算進沒讀的份數(同 lumos 的 _e2e_ai_pending_all)」
file: `scripts/hooks/claude/lumos-entry-hook.py:316-323`,以及 codex-harness 新 WHY 的 `[test:t_android_e2e_ai_count_copies_agree]`
失敗場景:新 WHY 說「總時間取 3 秒跟剩下時間(`_inner_budget`)的小者,太大的紀錄算進沒讀的份數」。同時拿掉 `min(..., _inner_budget())` 與 `unread += 1`,跑 `-k android_e2e_ai_count_copies_agree`,結果 8 passed, 0 failed,照綠。測試只斷言「有 3 筆」和複本函式逐字相同,沒量掛鉤的預算,也沒量沒讀份數。
歸因:有證據的修復回歸。這兩行與 WHY 都是這輪加的。
兩版查證:修前版兩行都沒有;修後版有兩行,沒有任何斷言。

**5.**
severity: major
blocking: 是
引句:「注意:另有 {unread} 份沒讀(讀超過 60 秒),那幾份這次沒標;再跑一次這個指令」
file: `scripts/lumos:_e2e_waive_ack`、`_e2e_ai_pending_all`、`_e2e_waive_list`
失敗場景:這輪起,超過 2MB 的紀錄會被算進「沒讀」。我造了一份帶 AI 放行的 2MB 加 1 位元組的紀錄,呼叫 `_e2e_waive_ack(root, [], True)`,輸出是「注意:另有 1 份沒讀(讀超過 60 秒)…再跑一次這個指令」,接著「沒有還沒人看過的 AI 放行。」,rc 0。實際耗時是 0 秒,原因是檔案太大,重跑永遠一樣。`waive --list` 對這份只印「紀錄讀不懂」。doctor 與開場提示仍叫人用這兩個指令看與標,所以這份放行永遠看不到也標不掉,這正是 r3 要消除的死路,只是換成大檔。S41 說「`--ack` 用完時間講沒讀到幾份」,程式把大檔也混進同一句。
重現:`_e2e_ack_targets(root, [], True)` 回 `([], 1, None)`,見上述輸出。
歸因:有證據的修復回歸。`unread += 1` 與 `cap=None` 都是這輪加的。
兩版查證:修前版大檔不算沒讀,沒有這句誤導;修後版大檔進入 60 秒那句訊息。

**6.**
severity: minor
blocking: 否
引句:「確定是誤擋,照它印的放行指令(拿掉驗收設定、紀錄讀不懂這幾種擋下不印放行指令,照它說的處理) `lumos android-e2e waive」
file: `README.md:68`、`README.en.md:29`
失敗場景:不印放行指令的擋下不只這兩種。`_e2e_gate_block` 沒帶 `fp` 的情況都不印,包含找不到主線、逾時、`merge_main`(含這輪新加的 S50)。`_cl_say_e2e_block` 的條件是 `rep.get("fp") and not bad_record and not newer_schema`。另外括號插在「放行指令」與指令本體之間,中英兩版句意一致但讀起來斷開。中英兩版的意思相同,沒有分歧。
歸因:有證據的修復回歸,措辭精度。

**7.**
severity: minor
blocking: 否
引句:「`t_android_e2e_waive_all_records`」所在 docstring 寫「S41」
file: `scripts/test_lumos.py`(這輪新增的幾支測試 docstring)
失敗場景:新測試 docstring 的條款編號與計劃不一致。`t_android_e2e_waive_all_records` 寫 S41,計劃綁它的是 S44;`t_android_e2e_scope_perf` 寫 S42,計劃綁的是 S45;`t_android_e2e_record_unreadable` 寫「S10、S38」,計劃是 S46。三個月後的人會順著編號找錯條款。
歸因:有證據的修復回歸。

**8.**
severity: minor
blocking: 否
引句:「表態那一道在 `code-loop check` 裡跟合約測試、新增告警、代碼審留痕排在一起」
file: `docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md`(白話段)
失敗場景:不帶旗標的早退順序仍寫「安全證據 → 合約測試 → 表態 → 新增告警 → 審查留痕」,e2e 只在 keep-going 那句括號裡出現。程式 docstring 與計劃說 e2e 排在安全證據之後、所有放行早退之前,不帶旗標也會跑,順序描述不完整。
歸因:未判定,我沒有跑不帶旗標的實際順序。

**逐條回應審查鏡頭**

- S41:新寫「`waive --list` 與 `--ack` 讀全部」這半句,由 S44 的測試實際守住。S41 自己綁的 `t_android_e2e_record_scan` 通過,但 `--ack` 60 秒、大檔計入沒讀的行為會被 finding 5 打破。
- S43:`_e2e_gate_out` 統一清理與測試對得上,中間不會漏掉列表與成對清單。
- S45、S48、S49、S50:讀程式與測試後,行為與條款一致,測試斷言對得上條款。我沒有對這幾條逐一做改壞驗證,沒有發現問題,也沒有證明它們守得住。
- S46:findings 2、3 指出兩個子句與程式不符或沒有測試。
- 「六道」:現在全 repo 不一致,見 finding 1。
- 驗證筆記改 stale:我沒有找到明顯該一起改的地方。frontmatter 與 tag 兩處都改了,這點未發現問題。我沒有檢查 doctor 對 stale 的 `verified_by` 是否報警。
- 三條 PITFALL 的 `[出處:][根因:][test:]` 格式成立,綁的測試存在。實際守住的範圍見 finding 4。
- pre-push 逃生路新句與擋下訊息實際印的:`removed`、`bad_record`、`newer_schema` 這幾種確實不印放行行,句子成立。

**三問**

1. 這輪修補有沒有帶進新的不一致?有。文件對程式:S46 的 2MB(finding 2);文件對文件:「六道」沒改乾淨(finding 1);文件對測試:條款或 WHY 宣稱的行為沒有測試守(findings 3、4);程式對自己:大檔訊息誤導(finding 5)。
2. 這輪新加的測試能不能抓到實際錯誤?多數能,但 S46 的 git 分流、掛鉤預算取小者、大檔計入沒讀這三處我用改壞驗證證明測試照綠。
3. 能不能放行進實作?不能,四條 major 都屬於這輪修補帶進的新問題,需要先處理或附理由接受。

最高等級 major,擋實作的 5 條(findings 1–5)。
