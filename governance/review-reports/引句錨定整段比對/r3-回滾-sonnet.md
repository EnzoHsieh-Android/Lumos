severity: major

我照第 3 版〈回退〉三條路逐條走,拿 `/tmp` 的沙盒 clone 實測,實驗已刪。實作還沒寫,所以寫側、處置閘、回放對隔離閥的反應,我是讀現行程式加改寫模擬,沒有跑新程式。

**已讀,無 finding 的項目**
- 完整還原後舊程式讀到多一欄:我在沙盒帳本的載體列手加 `"quote_rule":"full-span-v1"`,跑 `loop status … --disposal` 照常 `GATE PASS`,沒有 traceback。〈回退〉第四點「逐欄 `.get`、多一欄不受影響」成立。
- 305 個已凍結迴圈:`governance/replay/*/verdict.json` 共 305 個,帳列都沒有 `quote_rule`;`docs/.canary-log.jsonl` 4219 行也沒有。「照 legacy 重算、與凍結當時相同」成立。
- 設定檔改動要不要走代碼審:沙盒裡只改 `.lumos/config.json` 一個提交,`lumos pitfalls --diff` 判 `tier: light`。`.json` 在 `_PITFALL_DIFF_SKIP_EXT`,不在 `_BOOKKEEPING_FILES`,所以「不在簿記清單、照常走推送閘」屬實,而且不需要代碼審。

**1. 隔離閥開著時,週跑自動凍結會把舊判準的結果凍成標準答案**
severity: major
blocking: 是
引句:「隔離閥開著期間,已凍結且章是 `full-span-v1` 的迴圈若新舊判準結果不同,週跑回放會報漂移——那是預期的,關掉隔離閥後回到一致。」
file: `governance/autonomous_loop/replay_weekly.py:92-104` 週跑第一步,對已收斂但還沒凍結的迴圈自動 `--freeze`。
file: `scripts/lumos:1114-1128` `cmd_loop_replay` 凍結只擋 `rc == 2`,`rc == 1` 照樣把 `verdict.rc` 與 `fails` 寫進 golden。
1. 隔離閥開著期間,有迴圈在新判準下收斂(載體列蓋 `full-span-v1`,例如巢狀引句)。
2. 週跑把它補凍。凍結呼叫處置閘,依稿被強制走 legacy,巢狀引句被截斷,判 rc=1 `fails=['quote']`。
3. 這個紅燈被存成 golden。現有 305 個 golden 裡已有 5 個 `rc=1`(`code-batch14` 等),證明紅色結果會被凍成標準答案。
4. 拿掉隔離閥後,這個 golden 的帳列帶 `full-span-v1` 章,新判準算出 rc=0,與 golden 的 rc=1 不同,報邏輯漂移。這不是「關掉閥就回到一致」,必須人工 `--freeze --note` 重凍。
5. 稿只在完整還原那條說重凍有害,隔離閥這條沒寫「閥開著不准凍結」,測試也沒有。

**2. 隔離閥期間的收斂事件看不出是在閥開著時過的**
severity: major
blocking: 是
引句:「設了之後處置閘與回放對所有帳一律用 `legacy` 重算並印一行警告」
file: `scripts/lumos:11463` `_loop_gov_mark(env, loop_id, "converged", "gate PASS")`,note 固定是 "gate PASS"。
1. 閥開著時,載體引句後半編造的迴圈被 legacy 放行,治理帳記一筆 `converged`。
2. 警告只印在 stdout,沒進治理帳也沒進 canary 帳。稿裡沒有任何一句要求把「這次是閥放行」留痕。
3. 閥拿掉後,這個迴圈用新判準會判紅,但治理帳早已記收斂,事後查不出哪些收斂是閥開著時過的。
4. 這正是稿想保護的那道守衛關著的期間,需要可事後篩出的標記(例如 note 帶 `override=legacy`)。

**3. 設定檔壞掉時,隔離閥與回退都靜默失效,且退回的預設是新判準**
severity: major
blocking: 是
引句:「讀法照 `_bound_tests_parallel`:區塊不是物件、值不在認得的集合,印一句提醒並當沒寫。」
file: `scripts/lumos:49799-49802` `_bound_tests_parallel` 讀設定的整段 `try` 遇到任何例外就 `return 1`,而且不出聲。
file: `scripts/lumos:49796-49797` 函式說明寫「設定檔讀不了不在這裡出聲,同一次呼叫裡 `load_platforms` 會先講」。
1. 我在沙盒寫一份尾逗號的壞 JSON(`{"bound_tests": {"parallel": 4},}`)呼叫 `_bound_tests_parallel`:回 1,stdout 與 stderr 都是空字串。
2. 處置閘與回放不會先呼叫 `load_platforms`,沒有人替它出聲。
3. 人在緊急時手改 `.lumos/config.json` 設 `read_override` 或 `write_rule: "legacy"`,只要 JSON 有一個語法錯,整份被當不存在,退回第二階段預設 `full-span-v1`。回退失效,卻沒有任何訊息。
4. 稿同時說「寫錯出聲」又說「照 `_bound_tests_parallel`」,兩句互相矛盾。稿也沒說最外層不是物件、檔案是捷徑(symlink)時怎麼辦(`scripts/lumos:30480` 的 node_home 讀法會拒絕跟捷徑)。
5. 要補:`quote_check` 專用讀函式,解析失敗必須出聲,而且不能默默退回新判準。

**4. 隔離閥期間,週跑的漂移紅燈分不出是預期還是真漂移**
severity: minor
blocking: 否(能靠人工比對撐過去)
引句:「隔離閥開著期間,已凍結且章是 `full-span-v1` 的迴圈若新舊判準結果不同,週跑回放會報漂移」
file: `governance/autonomous_loop/replay_weekly.py:134-141` `build_msg` 只列 `red` 的迴圈編號,沒有帶閥是否開著。
1. 週跑只看輸出字串有沒有「邏輯漂移」。稿印的警告行不在 `RED_MARKERS` 裡,LINE 訊息也不帶。
2. 閥開著的每個週一,訊息都叫人去看,看到的 `--golden` 輸出同樣紅。真的回放漂移(讀側程式被改壞)會混在預期漂移裡。
3. 實測 `code-batch14` 回放約 0.87 秒,305 個約 265 秒,超過 `FULL_SWEEP_SECONDS=180`,所以週跑只抽 5 個加新凍結,不是全掃。稿的「全部約 5 分鐘」是手動推送前驗證的口徑,週跑看到的漂移是抽樣,不能當「所有受影響迴圈」的清單。
4. 要補:閥開著時週跑訊息前綴一行「隔離閥開著,漂移可能是預期」,或回放在紅燈行附上閥狀態。

**5. 還原步驟缺作廢必填鍵,也沒更新到期提醒**
severity: minor
blocking: 否(工具會當場提醒,不會誤放)
引句:「本計劃、`Systems/design-loop`、`Systems/loop-convergence-recording` 講判準蓋章的句子標 `[status:superseded]`,Issue 重開。」
file: `scripts/lumos:4670-4671` 標了 `[status:superseded]` 就必須寫 `[被取代:…]`(沒有接手的寫 `無 <理由>`),否則 lint 唸。
1. 稿的還原步驟只說標 `superseded`,沒說要補 `[被取代:無 <理由>]`。
2. 回退成 `write_rule=legacy` 後,`REVISIT:2026-12-15` 要看的 `new-only` 筆數必然是 0(寫側已不再用新判準擋)。這會被讀成「零誤傷」,與 RETIRE-IF 的前提衝突。稿沒要求回退時同步改 REVISIT 或 RETIRE-IF。

**6. 隔離閥與無效章的優先序沒定**
severity: minor
blocking: 否(實作時選一邊即可)
引句:「有這個鍵但值不是字串、是空字串、或不在集合內 → 判失敗,不 traceback。」
1. 「隔離閥:所有帳一律 legacy」與「章值不合判失敗」在同一列上衝突,稿沒說誰優先。
2. 實測測試只涵蓋「章合法的 v1 列 + 閥」(`t_quote_full_span_rule_stamped_on_ledger` 最後一組)。
3. 閥開著時,手改壞的章會被默默放過,而不是判失敗。要選一邊並寫進條款。

**7. 回退路徑的測試缺口**
severity: minor
blocking: 否
引句:「`read_override` 為 `legacy` 時處置閘 應 一律用舊判準並印警告」
file: `scripts/test_lumos.py:26959-27010` `t_quote_full_span_rule_stamped_on_ledger` 的 `read_override` 只測處置閘。
file: `scripts/test_lumos.py:27040-27056` `t_quote_full_span_replay_follows_stamp` 沒設隔離閥。
1. 沒有任何測試涵蓋「閥開著時回放與凍結」。如果實作只讓處置閘認閥、回放與凍結不認,全部測試仍綠,但回放會漂。
2. `write_rule` 回退後 `seat-check` 與手動 `quote-check` 的預設沒有測。`_QUOTE_RULE_STAMP_SINCE` 的警告也沒有測。
3. 要補:閥開著時凍結或回放一個蓋 `full-span-v1` 且新舊判準結果不同的迴圈,斷言依序出現「凍結被拒」或「回放與凍結一致」。再補壞 JSON 設定出聲的測試,對應 finding 3。

**8. ⚠ 回退只說了本 repo**
severity: minor
blocking: 否
引句:「第二階段:另一個提交把程式預設改成 `full-span-v1`(本 repo 不必寫設定)。」
1. `lumos` 是每台機器裝一次(project CLAUDE.md 與記憶「lumos 更新分發」),消費專案共用同一份程式。
2. 第二階段合入後,各消費專案的預設一起翻成 `full-span-v1`。要回退得逐專案各自提交 `.lumos/config.json`。
3. 稿的回退只描述了本 repo 的設定檔,沒有說明消費專案怎麼辦。這點我只讀了文件,沒有實測,所以標 ⚠。

總結:最高等級 major,blocking 共 3 條
