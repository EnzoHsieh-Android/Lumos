severity: major

審材是 r1-snapshot-乙.patch。我在 `--shared` 複本裡對程式各改壞一處、清快取後跑對應測試,共約 29 處。五支測試原樣都是綠的。改壞後翻紅的包括:仲裁判斷反轉、缺第一盲判改不擋、先到者勝改後到者勝、驗證放行不認得的欄位、仲裁沒有第一盲判對象就放行、`--missing` 失效、同提交兩筆盲判被去重、kappa 數字、統計的真陽性與誤報計數對調。這些路徑測試抓得到。

預期值方面,kappa 0.590 我手算得出:相符 20/25=0.80,偶然一致 0.336+0.176=0.512,(0.80-0.512)/0.488=0.5902,和實作無關。測試的假輸入形狀和實際寫入的帳(盲判事件、表態事件、`warned` 事件)一致。

沒翻紅或筆記對不上的有下列幾條。

F1
severity: major
blocking: 是
引句:「某一列真陽性至少 20 個 (段,列)、誤報少於一成才把那一列從提醒升成擋(證據樣式與多數決分開判)」
問題:「多數決提醒」的真陽性與誤報,在統計裡算反了,也量不出真誤報,而升擋決策正是靠這組數字。
- 作者判不適用、第一盲判與仲裁都判適用且照做時,`_kt_bj_check` 會發出 `verdict: majority-against-author` 的提醒,文字寫「三方多數判作者沒照做:作者 不適用」。
- 我用行程內探針跑 `_render_gov_situation`,輸出是「提醒確認 D-1(多數決):真陽性 0、誤報 1」。這則提醒按設計是對的,卻被記成誤報。
- 作者判適用的一般情形下,多數決提醒因為判定當下仲裁已經站在盲判那邊,終局一定算真陽性。「誤報少於一成」這個條件對多數決永遠成立,量不出誤報率。
- `t_blind_judge_majority` 只造了作者判適用的案例,`t_gov_stats_situation_agreement` 完全沒有多數決種類的提醒事件。我把統計的標籤判斷(`kind == 'evidence'` 那段)對調後,統計測試仍是 7 passed。
- 還有一個相關缺口:仲裁票與作者、第一盲判都不同時(三方各異),程式照樣印「三方多數判作者沒照做」,但三方其實沒有多數。
- 程式位置:`scripts/lumos:17180`(終局判定)、`scripts/lumos:72296` 附近(`_kt_bj_check` 的仲裁分支)。

F2
severity: minor
blocking: 否
引句:「`pitfalls --diff` 有情境段時也印這四步(跟著 stack_questions.gate:設 high-only 而這次不是 high 就不印)」
問題:筆記寫的是 Systems/棧別提問表態閘 的 `gate` 模式行為,`t_pitfalls_situation_blind_judge_hint` 只測預設設定,沒測 high-only。
- 我把 `scripts/lumos:63271` 的條件改成「忽略 tier」(`high-only` 一律印),測試 8 passed。
- 改成只認 `"all"` 也是 8 passed。
- 後果:非高風險的推送會被多印一段盲判指令,或高風險的推送漏印。

F3
severity: minor
blocking: 否
引句:「AI 下的段放行 應 在 doctor 列出直到 `--ack`」
問題:S6 條款和測試的 docstring 都說 doctor 會列出 AI 放的段放行,但測試只呼叫 `_lint_waivers_ai_pending`,沒跑 doctor 的輸出。
- 把 `scripts/lumos:4204` 的 `if _n_ais:` 改成 `if False:`,測試仍 8 passed。
- 把 `lv["ai_pending_situation"]` 改成恆為 0,測試也仍 8 passed。
- 後果:這是筆記宣稱的「段放行被濫用」的防線。壞了之後,AI 自己放行的段在 doctor 與推送前小結裡會悄悄消失。

F4
severity: minor
blocking: 否
引句:「`--disagreements` 應 只列不一致的(段,列)」
問題:`_kt_bj_pick_rows` 排除「已有仲裁的格」這個分支沒有測試。
- 把 `isinstance(cell.get("arbiter"), dict) or ` 拿掉(`scripts/lumos:72386`),`t_blind_judge_template_excludes_dispositions` 仍 12 passed。
- 場景:仲裁已經寫入後,再跑 `--template --disagreements` 還是列出那一格,編排者可能重複派仲裁。因為「同一格只認第一筆」,多派的結果會被忽略,造成白工。

F5
severity: minor
blocking: 否
引句:「被證據提醒過的(段,列)應 依盲判終局分成真陽性、誤報與待確認」
問題:統計裡幾個分支改壞後測試不紅。
- `fin` 判定改成「有仲裁優先、否則取第一盲判」(`scripts/lumos:17180`),測試仍 7 passed。這會讓「作者與第一盲判不一致、還沒仲裁」的格被算成真陽性,應該算待確認;該場景下推送被擋、提醒帳已經寫了,所以真的會出現。
- 把盲判票的 `setdefault` 改成後到者勝(`scripts/lumos:17130`),測試仍綠。程式實際「同格第一筆為準」,統計卻會讀到後到的重判。
- 把 `list(dict.fromkeys(warns))` 換成 `list(warns)`(`scripts/lumos:17142`),測試仍綠。同一(段,列)換版本重記時會重複計數。
- 把 `keys` 展開迴圈(總數事件)拿掉,測試仍綠。
- 把 kappa 樣本門檻 `>= 20` 改成 `> 20`(`scripts/lumos:17158`),測試仍綠。恰 20 個樣本的邊界沒測。
- 驗證紀錄寫「統計 6 道」都翻紅,這幾道不在其中,「31 道全翻紅」的說法只對它們自己挑的那 31 處成立。
- 這些統計只影響升擋決策,不影響推送閘,所以只列 minor。
- A2:仲裁採作者時不記 `followed`。改壞後 `t_blind_judge_majority` 仍 13 passed。後果是證據提醒仍印「待盲判」,而不是「盲判已判照做」。

總結:最嚴重是多數決提醒在統計裡真陽性與誤報算反(作者判不適用時被記成誤報),且測試完全沒涵蓋這個種類,會擋 1 條,另 4 條 minor 不擋。

我的複本目錄 `/tmp/lumos-seat-work/code-android情境題盲判/測試-sonnet` 已用字面絕對路徑刪除,repo 沒被修改。
