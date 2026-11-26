severity: major

我只動了 `/tmp/lumos-seat-work/code-選擇點變異加速第四段/合約與圖譜-sonnet/` 底下的副本,repo 本身沒碰。對應 diff 行號是 `r3-snapshot.patch` 的行號。

Finding 1 照我自己的判準重判:「測試沒斷言到驗收條款寫的必要行為 → major」,所以兩欄改成 major、blocking 是。檔級第一行與最後一行同步改為最高 major。

**Finding 1**
severity: major
blocking: 是
引句:「快篩有失敗時 應 照第二段的結果檔名單;含六萬個 ` > ` 的長行 應 一秒內解完」
- 第四段 S2 的這一句綁在 `t_choice_kill_merge_events_order`,但這支測試的真跑四案是「單支都不殺」「單支 b 殺」「零案例帶 b FAILED」「逾時沒有事件行」,沒有任何「有失敗」案。
- 最小重現:在副本的 `_kill_merge_screen` 把 `if kind == "unclean":` 改成不分結果類型都照事件覆寫 `merge_failed`、`merge_back`。`t_choice_kill_merge_events_order` 仍然綠。同一輪紅的只有 `t_choice_kill_merge_failed_first`、`t_choice_kill_merge_event_fields`、`t_choice_kill_merge_failure_goes_single`。
- 行為其實被第二段的測試守住了,所以不算實際漏洞,但 S2 這一句的綁定測試沒有斷言它。
- 歸因:有證據的原有漏查(兩版 scripts 相同,修前就沒有)。

**Finding 2**
severity: minor
blocking: 否
引句:「`_choice_merge_classify` 判逾時時看輸出:「跑到測試」→ 回 `("unclean", "逾時(跑到測試後掛住)", False)`;否則照舊」
- 合併基準現在也帶事件腳本,所以基準逾時而且有 STARTED 時,原因會變成「逾時(跑到測試後掛住)」。
- 這個字樣不在 `_CHOICE_MERGE_BASE_WHY`(那張表只有 `"逾時": "合併基準逾時"`),因此印出來的那行不再有「合併基準」字樣。
- 帳上 `merge_off` 也變成「合併基準:逾時(跑到測試後掛住)」,但第二段 S10 寫的是「值是 `合併基準:逾時`」,而 diff 沒有替 S10 加「部分被取代」註記。
- 第四段計劃只用一句「照原字串帶出」帶過。全部測試只斷言純「逾時」那條,這條沒有任何測試。
- 歸因:有證據的原有漏查。

**Finding 3**
severity: minor
blocking: 否
引句:「名單空(結果不是有失敗、或一支都對不到)→ 原順序。只改順序、不判任何事」
- `_kill_merge_failed_first` 的 docstring 沒跟上程式:程式現在還處理 `merge_back`(掛住層與通過層排最後),沒跑乾淨時 `merge_failed` 也會有內容。
- 同類:`_kill_merge_screen` 的 docstring 寫「有失敗時由 classify 填」;`_choice_merge_classify` 與 `_kill_merge_breaker` 的 docstring 仍寫「斷路器只數逾時」,沒提「跑到測試後逾時」另外數。`_KillMerge` 的 docstring 也沒列 `hang_streak`。
- 三個月後的人照註解推行為會推錯。
- 歸因:有證據的原有漏查(修前就沒有)。

**Finding 4**
severity: minor
blocking: 否
引句:「其餘三案直接呼叫 _kill_merge_breaker(真跑要十幾個壞法,單支測試時限放不下)」
- 程式實際直接呼叫的案有六案加一個 `hang_breaker=3`,註解還寫三案。
- 測試的 docstring 也只列到第五案,新增的「15 次跳開後恢復再 1 次」「3 次後原計數跳開、恢復後 14 次」「門檻帶 3」都沒寫進去。
- 另外那兩個恢復案其實分不出「恢復時歸零」這道:`_kill_merge_trip` 已先把 `hang_streak` 歸零,恢復必然發生在跳開之後。計劃〈做法〉3 寫「跳開與恢復兩個連續計數都歸零」,恢復那一道是冗餘的,不可觀測。
- 歸因:有證據的修復回歸(這兩處是修後新增案,註解與 docstring 沒跟上)。

**Finding 5**
severity: minor
blocking: 否
引句:「席報告與收貨紀錄:governance/review-reports/選擇點變異加速第四段/(r1-*-sonnet.md、r1-intake.md)」
- 計劃〈審計修正紀錄〉只有設計審 r1 一筆。
- 計劃〈用詞〉〈做法〉卻多處引「代碼審 r1」,S2、S3、S6 也有代碼審後才加的案,但沒寫這些改動來自 `code-選擇點變異加速第四段/` 的哪一輪,也沒有 r2、r3 的條目。
- 接手的人查不到後來加了六萬個 ` > `、`\r`、恢復後從頭數、重試上限重算是為什麼。
- 歸因:未判定。

**已驗主張**
- **PITFALL 的 repro 成立。** `_choice_merge_events("x.V > foo (bar) FAILED", ["foo (bar)"])` 在 HEAD 回 `failed: []`,`["foo"]` 也一樣是空,與 PITFALL 行相符。
- **`t_choice_kill_merge_hang_breaker` 全綠。** 兩個真跑案、七個直接呼叫案都過,在補齊 `skills/`、`scripts/` 的完整副本上跑。
- **S3、S6 逐項對得上。** 連續 5 次跑到測試後逾時不跳開、連續 15 次才跳開、4 無 1 有 1 無在第 6 個跳開、試探逾時不恢復、`hang_breaker` 可帶入;S6 重試上限 100、30,與預期值表一致。
- **數字自洽。** 142 = 117 + 25、25 = 15 + 10、沒跑乾淨 15 = 11 + 4、被殺 13 = 10 + 3;14197/142 約 100 秒;15 次 × 150 秒約 37 分鐘;10 次 × 90 秒 = 15 分鐘。
- **做法對程式。** `scratch`、`merge_init_off`、`hang_streak`、`_kill_merge_trip` 兩種計數共用,都與〈做法〉1–3 一致。
- **事件解析效能。** 1000 支測試、2000 行事件的 `_choice_merge_events` 約 0.3 秒。
- **重複定義。** `_cmd_arg_quote` 與三支新測試函式在 `scripts/` 各只出現一次。

**固定席逐條**
- `bound-tests-gate`:
  - 不影響。`_run_cmd_expand` 改成 `_cmd_arg_quote` 後,Windows 與 POSIX 兩條分支行為不變。
  - 新增三支測試都有 `[test:]` 綁定。
- `guard-kill`:
  - 不影響。rc 優先序沒動。
  - 新增的提示都走 stderr,`--json` 純度保持。
- `測試假綠形態`:新測試的真跑案都靠精確順序斷言證明現場成立(假 Gradle 只在帶 `--init-script` 的合併呼叫才印事件)。
- `lumos-cli-read`、`lumos-cli-lifecycle`、`design-loop`、`pitfalls-code-loop`、`loop-convergence-recording`:不影響,diff 沒有碰搜尋過濾、re-inject、處置閘或收斂記錄。
- 其餘「超出上限、只列名」的節點:我沒有逐篇讀,未驗。

這次沒有「這筆殘留」段,所以沒有殘留要答。

**三問**
1. **文件跟程式有對不上嗎?** 有。Finding 2 是 S10 沒註記而且測試沒涵蓋;Finding 3 是 docstring 過期;Finding 5 是紀錄不全。
2. **上一輪沒人看的角落有嗎?** 有。合併基準逾時在帶事件腳本後的新字樣、`_kill_merge_failed_first` 的 docstring、測試 docstring 的案數。
3. **新發現在修前、修後各是什麼結果?** 兩版 `scripts/` 完全相同,Finding 1、2、3 在兩版都存在。Finding 4 只在修後(新增案但沒更新註解);Finding 5 未判定。

**未驗**
- 完整測試檔的全套跑法、真實 Gradle 對初始化腳本的拒收訊息是否會被 `_KILL_COMPILE_RE` 吃成「編不過」而不走重試(我只能看計劃的敘述,沒有實測)。
- Windows 路徑那條只看了測試用的 monkeypatch。

清理:四個我自己跑出的 `gctl-run-*` 暫存現場已用字面路徑刪掉。另一個現場來自我那輪 `-k t_choice_kill_merge` 的變異實驗,但輸出沒印出它的路徑,無法確認是哪一個,所以沒刪,其餘 `gctl-run-*` 不是我建的。`/tmp/lumos-seat-work/code-選擇點變異加速第四段/合約與圖譜-sonnet/` 還在,留給編排者收。

最高 major,blocking 1 條
