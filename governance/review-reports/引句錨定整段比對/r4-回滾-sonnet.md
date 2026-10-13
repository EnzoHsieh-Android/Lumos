severity: major

我只讀了 spec 和 repo,沒改任何檔。實驗目錄 `/tmp/lumos-seat-work/引句錨定整段比對/回滾-sonnet/` 我沒建,所以沒有東西要刪。

先講結論:拿掉讀側隔離閥之後,「寫側切回 `legacy`」這條路只擋得住新帳,擋不住兩件事。一是已經蓋了 `full-span-v1` 章、卻被誤放行的帳。二是凍結入口把非綠判定凍成標準答案。凍結入口我逐一掃過,共四個:手動 `--freeze`、週跑補凍、`--note` 重凍、回放。spec 對每一個「遇到非綠怎麼辦」都沒答。

## 凍結、重算入口掃描

| 入口 | 位置 | 遇到非綠判定時現況 |
|---|---|---|
| 手動 `loop replay --freeze` | `scripts/lumos` 的 `cmd_loop_replay` | 只在 `rc==2` 擋下,`rc==1` 照樣把 `{"rc":1,"fails":[...]}` 寫進 `verdict.json` |
| 週跑補凍 | `governance/autonomous_loop/replay_weekly.py` | 對「治理帳有 converged 但沒 verdict」的迴圈直接跑 `--freeze`,不先確認現在判定是綠 |
| `--freeze --note` 重凍 | 同 `cmd_loop_replay` | spec 自己承認會「把舊判準的紅燈凍成標準答案」 |
| 回放 `--golden` | 同 `cmd_loop_replay` | 唯讀。丟例外時週跑把它歸成 `errors`,不是 `red` |
| 處置閘 `loop status --disposal` | `_loop_status_disposal` | 非綠就 rc1,不放行 |

repo 已有先例:`governance/replay/*/verdict.json` 305 份裡有 5 份是 `rc=1`,分別是 `code-batch14`、`code-batch13b`、`code-待決問題改存開頭欄位`、`code-審查跑滿回顧`、`code-兩席相反時端出張力-v2`。

---

## F1 蓋過章的判準「不改判定」只靠約定,章一旦蓋錯放行就沒有撤銷路
severity: major
blocking: 是
引句:「之後要調整新判準的判定結果(放寬、收緊、修誤判),一律新增一個版本值」
1. 這條規則在 spec 裡只是文字約定。F1 的改法是補一支測試,把 `full-span-v1` 對一組固定輸入的判定釘住(逐條 `ok`、`malformed`、`kind`)。目前沒有這種測試。`t_quote_full_span_*` 都是「功能對不對」,不是「版本值不可變」。
2. 實作 `full-span-v1` 的人發現誤判,最自然的修法是直接改分支,同時改測試。改完測試全綠,沒有任何機械訊號。
3. 更糟的是「新判準誤放行」(false-green)。誤放行的載體列被蓋 `full-span-v1` 章,處置閘通過,迴圈 converged,凍結的 `verdict.json` 是 `rc=0`。之後回放會說「回放一致」,等於章把誤放行固定成標準答案。
4. 修法只能新增 `full-span-v2`,而舊列永遠蓋 v1。工具沒有任何「撤回某版本」的辦法,也不能事後列出哪些迴圈吃過那個窗口的誤放行。唯一線索是自己對帳本 grep `quote_rule`。
5. 這正是被拿掉的讀側隔離閥當初負責的事。減法之後 spec 沒補替代機制,例如「已撤回版本清單,命中時處置閘降級為不放行」。
6. 誤判紅(false-red)這邊止得住。寫側跟處置閘用同一個函式,被寫側擋下的報告不會進帳,切回 `legacy` 就好。只有誤放行這個方向漏。

## F2 凍結入口不看判定綠不綠,舊樹、不認得的章、新判準誤判都會凍出紅色標準答案
severity: major
blocking: 是
引句:「舊版程式(別的工作樹還沒同步主線)讀到 `full-span-v1` 章時不認得,會照舊判準重算——巢狀那類可能誤判紅」
file: `scripts/lumos:1140` 凍結第二趟 `_loop_status_disposal` 的 `rc` 之後只擋 `rc==2`,`1177` 把 `rc` 原樣寫進 verdict
file: `governance/autonomous_loop/replay_weekly.py:96` 補凍只看「有沒有 verdict」,不看現在判定
1. spec 只分析舊樹對「處置閘轉紅」的影響,漏了凍結。任何一個還沒同步主線的工作樹(多會談並行是常態)只要跑手動 `--freeze`,或週跑從那棵樹執行,就會對蓋了 v1 章的巢狀引句迴圈算出 `rc=1 fails=['quote']`,並寫進 `verdict.json`。
2. 同樣會發生的情況還有:未來蓋 `full-span-v2` 章的帳,被 v1 時代的程式凍結,章值判成「不認得」而失敗。
3. 這個 `verdict.json` 合進主線後,`engine_rev` 沒推進,所以新程式回放會報「邏輯漂移」紅燈。補救只有 `--freeze --note` 重凍。重凍本身就是 spec 說不要做的「把紅燈凍成標準答案」那一類動作。
4. 回放的 `verdict.json` 版控比對讓這份紅色答案受保護,要靠人記得「不是漂移是舊樹凍的」才能判斷。
5. 修法:`--freeze` 在 `rc!=0` 時預設擋下(要凍紅色需另帶旗標),並寫一條條款加測試。這同時補上週跑補凍。現有 5 份 `rc=1` 的 verdict 要先確認是有意凍紅還是同一種意外。
6. 同入口另一個缺口:〈回退〉第三條的「完整還原」之後,漂移的迴圈沒有第三條路。只能重凍(凍紅)或讓週跑回放紅燈永遠響。spec 沒寫這個等待期怎麼處理。

## F3 文件與範本的「整段對得上」宣稱不分階段,第一階段與回退到 `legacy` 時都是假的
severity: major
blocking: 是
引句:「工具只保證引號裡面那段是真的,引號外的文字不算引句」
引句:「第一階段(本計劃第一個功能提交):合入全部程式,程式預設 `write_rule=legacy`」
file: `skills/lumos-design-loop/templates.md:63` 現行錨定紀律那行
1. 〈同步改的地方〉列了 7 處(templates §1、兩份 SKILL.md、兩份 reference.md、`_CODEX_AGENT_INSTRUCTIONS`、05-設計審查迴圈.md、`Systems/design-loop`、`Systems/loop-convergence-recording`)要加「引號裡面整段要對得上」。spec 沒說這批文件跟哪個階段。
2. 第一階段「行為上等於沒改」,寫側仍是舊判準。若文件隨第一階段合入,範本與圖譜宣稱「工具保證整段」時,工具實際只驗第一個閉引號之前。
3. 範本還告訴席位「巢狀可以,要成對」。席位照做後,舊判準仍會把後半當未驗。後續的 AI 讀到文件,會相信保證存在。
4. 〈回退〉第一條切回 `legacy` 之後同理,文件不會回頭改。
5. 修法:文件改動綁第二階段,或寫成「判準由 `write_rule` 決定,現在是 X」。〈回退〉要加「文件與範本是否也退」一句。

## F4 新判準丟例外時,寫側主檢查與處置閘的行為沒有條款也沒有測試
severity: minor
blocking: 否
引句:「蓋了 `full-span-v1` 章的帳若讓處置閘丟例外,處置閘判失敗(不放行),等修好再問」
file: `scripts/lumos:26373` 處置閘呼叫 `_quote_rows` 外面只有 `except (OSError, UnicodeDecodeError)`
file: `scripts/lumos:10965` 寫側呼叫同樣沒包保護
1. 現行碼不會「判失敗」,例外直接成 traceback(Python 結束碼 1)。這是碰巧不放行,不是設計。〈讀章〉只規定章值壞掉要判失敗,沒規定 `_quote_rows` 內部例外。
2. 寫側同理。spec 只替「求 `kind` 用的另一版判準」包了例外保護,主檢查沒有。新判準丟例外時使用者只會看到 traceback,沒有「請把 `quote_check.write_rule` 設成 `legacy`」的提示,也不寫 blocked 事件。
3. 回放裡這種例外歸成 `errors` 而不是紅燈,週跑訊息只列前 5 筆。
4. 測試缺口:只有 `_qfs_record_with_broken_other_rule`(另一版判準壞)。沒有「主判準壞」、「處置閘遇到 v1 例外」、「回放遇到 v1 例外」三支。
5. 這一條 fail-closed,沒有資料傷害,所以 minor。

## F5 共用層壞掉時,切 `write_rule` 救不了,〈回退〉沒涵蓋
severity: minor
blocking: 否
引句:「新判準實作本身有缺陷:先照上一條把寫側切回 `legacy`,止住新章;再走一般修正提交。」
1. 〈回退〉把「新判準壞」和「v1 分支壞」畫等號。`_quote_rows(rule=…)` 的分派、`_quote_check_config`、讀章函式、寫入 `quote_rule` 的那段是新增的共用層,`legacy` 也會走。
2. 這一層壞掉(例如特定列讓讀章丟例外),切 `legacy` 沒用,處置閘與回放對所有迴圈都壞。〈回退〉第三條「完整還原」又限定第二階段之前。第二階段之後只有往前修一條路,spec 沒寫。
3. 第一階段會先在 `legacy` 下驗這一層,風險已壓小,所以 minor。但風險類別要分清楚:保護的是 v1 分支,不是整條路。

## F6 回退的實際槓桿沒講清楚:設定檔要走推送閘,且只在合入的工作樹生效
severity: minor
blocking: 否
引句:「消費專案共用同一份程式,要個別回退就在各自的設定寫這個鍵」
引句:「設定檔不在簿記清單,改它要照常走推送閘」
1. 緊急切 `legacy` 要改設定檔、commit、過推送閘、合入主線,其他工作樹再同步。這段期間別的會談照舊用預設 `full-span-v1`,繼續蓋 v1 章。
2. 全面回退其實是「還原第二階段改預設值的那個提交」,一次對所有消費專案生效。spec 沒把這條列為第二階段回退的手段,和「完整還原提交(第二階段之前)」混在一起。
3. 建議:補一句「第二階段回退=還原預設值提交」,並說明推送閘紅時的備案,不需要推送閘的環境變數或旗標。

## F7 S7 條款字面寫「兩版結果不同時」才報帳被動,實際上改章就一定報
severity: minor
blocking: 否
引句:「把帳上的章刪掉、或把章換成另一版而兩版結果不同時,回放 應報帳被動」
file: `scripts/lumos:1255` 帳被動由 `all_row_shas` 比對決定,與判準結果無關
1. 章在整行 JSON 裡,任何增刪改都會讓該列的 sha 對不上。所以只要動章就會是帳被動,與「兩版結果相同」無關。
2. 條款字面和機制不符。測試的斷言(`rc != 0` 且 stdout 有「帳」)方向對,但條款字面應改成「改動章即報帳被動」。這不影響正確性。

---

## 實務隱患逐類

- **不可逆**:有。章與擋下事件只進不出。F1 說明章錯放行後沒辦法撤銷。
- **併發、多工作樹**:有。見 F2、F6,舊樹會凍結或蓋章。
- **自我治理**:有。這次改的是審查系統自己收貨的守衛,F1、F2 都是誤判被固定成證據的路徑。
- **效能與記憶體**:已讀,無新 finding。預先配對、尾段掃描是線性,5000 個未閉合標籤有測試。我沒另外實測。
- **金流、對外送出**:無。spec 已排除,我也沒在程式中看到相關路徑。

已讀,無 finding 的節:〈量測〉、〈範圍〉、〈抽取規則〉、〈量測與留痕〉、〈推送前驗證〉。spec 引的 repo 行號與檔名我抽驗過,都找得到,包括 `skills/lumos-code-loop/reference.md` 第 91 行、`skills/lumos-design-loop/SKILL.md` 第 27 行、`Systems/design-loop` 第 62 行。

總結:最高等級 major,blocking 共 3 條(F1、F2、F3)。
