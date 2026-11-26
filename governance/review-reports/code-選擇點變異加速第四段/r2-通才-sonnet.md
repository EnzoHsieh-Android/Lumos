severity: minor

整體判斷:修補本身站得住,沒有會做出錯行為的洞。以下三條 finding 都是 minor、不擋推送。

**finding 1**
severity: minor
blocking: 否
引句:「mg.cool[plat] = mg.streak[plat] = mg.hang_streak[plat] = 0」
問題:`_kill_merge_trip` 裡把兩個連續計數歸零是多餘的,屬於 ⑦ 重複歸零。
- 跳開之後,`_kill_merge_breaker` 的停用分支只有恢復那條會碰到計數,其餘都直接 return。
- 恢復那條已經寫了「mg.streak[plat] = mg.hang_streak[plat] = 0」,所以跳開時的歸零沒有讀者。
- 兩處寫一樣的歸零,以後只改一處就會讓兩者不同步。
- 我分別把兩處拿掉推演,新增的 S3 案例(15 次跳開、`pass` 恢復、再 1 次;與 3 次掛住加 5 次逾時、恢復後 14 次)都只靠恢復那處就會翻紅;單拿掉跳開那處仍全綠。
- 所以測試鎖不住這一處,它是死碼。
- 歸因:未判定,純清理,不是修復造成的回歸。
- 查證:file: `scripts/lumos:29231`、`scripts/lumos:29263`。

**finding 2**
severity: minor
blocking: 否
引句:「body, sep, ev = line.rstrip().rpartition(" ")」
問題:事件行判定從正規式改成字串切之後,行尾空白的範圍變寬了。
- 舊正規式只吃行尾的空格、tab、CR,新的 `rstrip()` 連 `\xa0`、`\x0b` 都吃掉。
- 我用 30 萬筆隨機短行對照舊正規式與新函式,145 筆有差,我看到的 7 筆全部是行尾帶 `\xa0` 或 `\x0b`,其餘字元的結果完全一致。
- 影響:Gradle 不會輸出這種行尾,實務上無害。
- 計劃〈用詞〉寫的是「去掉行尾空白」,沒有逐字界定範圍,所以行為算對得上。
- 歸因:有證據的修復回歸,但後果可忽略。
- 查證:修前用舊正規式判 `"a > a > FAILED\x0b"` 得 None,修後得 `("a", "a >", "FAILED")`。

**finding 3**
severity: minor
blocking: 否
引句:「_kill_merge_base_run(mg, c, sh, lane, nf, min(cap, max(mg.remaining(), 1.0)), None)」
問題:重試上限新增的 S6 案例測得出「重試上限 ≤ 30」,但測不到「第二次逾時之後的分類」。
- 我走了一遍:剩餘時間不足時,重試上限會降到約 1 秒。
- 若 Gradle 拒收腳本、而第一次已吃掉大半時限,重試幾乎必然逾時,結果記成「合併基準:逾時」,不會有 `merge_init_off`,也不會記錯。
- 這是設計取捨,不是 bug;只是原因字樣不會是「拒收」。
- 不需要改,純記錄。
- 歸因:有證據的修復回歸,行為合理。
- 查證:file: `scripts/lumos:29120`。

**三問**

1. **原問題的修復效果**
   - 斷路器恢復後計數歸零:修後走 `_kill_merge_breaker` 的案例是 `[hw]*15 + pass + [hw]`。
     - 修前,跳開不清 `hang_streak`,恢復只清 `streak`,結果 15 變 16,再次跳開。
     - 修後恢復處清掉兩個計數,不再跳開。
   - 重試上限:修前重試沿用第一次的 `cap`。
     - 修後用 `min(cap, max(剩下, 1.0))`。
     - S6 案例斷言 `caps[0]==(100.0, True)`,重試上限 ≤ 30 且不帶腳本;還原成舊的 `cap` 會變成 100 而翻紅。
   - 長行事件解析:修前舊正規式(沒有走完整測試,只見到測試碼)在長行會回溯,修後 `rpartition` 加 `partition` 是線性。
     - 新測試放了六萬個 ` > ` 的長行,要求 1 秒內解完。
     - 我沒有實跑這條,只確認過 `rstrip`、`rpartition`、`partition` 都是線性操作。

2. **相鄰路徑是否仍成立**
   - `_cmd_arg_quote` 的邏輯與原來內聯的三行逐字相同(Windows 用 `list2cmdline`,其餘用 `shlex.quote`,`_IS_WIN` 仍在呼叫時才讀)。
     - 呼叫者只有 `_run_cmd_expand` 的 `{python}`、`{method}` 與 `_choice_merge_cmd` 的 `--init-script` 三處,沒有別處用到。
   - `_CHOICE_MERGE_EVENT_RE` 全檔已無引用,刪除沒有留下懸空。
   - `_kill_merge_trip` 只被兩個分支呼叫。
     - 輸出文字仍是「合併連續 {n} 次沒跑乾淨(最後一次:{why})」。
     - 原本掛住分支印的是常數 15,現在印 `mg.hang_breaker`;預設值相同,訊息不變。
   - `_KillMerge.__init__` 新增 `hang_breaker` 放在最後面的關鍵字參數。
     - 全檔的建構呼叫都沒用位置參數塞第 5 個,沒有破壞呼叫端。
   - 已知限制(原本就有):`breaker` 與 `hang_breaker` 預設值在定義當下綁定,以後測試若改常數不會生效。
     - 修前常數是呼叫時才讀的。
     - 目前沒有測試這樣改,只算 minor 風險。

3. **新發現案例在修前、修後的結果**
   - 3 個 finding 都是「清理或可忽略」性質,沒有修前修後行為翻轉的案例。

**未驗範圍**
- 沒有實跑 `scripts/test_lumos.py` 的相關子集;結論來自推演與隨機對照。
- 沒有驗圖譜固定席節點的合約文字,也沒有逐條對照計劃筆記的措辭;guard-kill 的 diff 只看到一條 WHY 補字,和程式行為一致。
- 沒有殘留段需要逐條答。

最高 minor,blocking 0 條
