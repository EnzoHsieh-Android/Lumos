severity: major

我查證了 spec 對程式現況的每個假設,結論是一個 blocker 都沒有,但有 7 條 major。這份 spec 的核心設計站得住,問題集中在切換機制、文件同步和維運證據三塊。實驗只用唯讀的 grep 和 Python 讀帳本,沒有改 repo,`/tmp/lumos-seat-work/引句錨定整段比對/接手的人-sonnet/` 下也沒有建任何東西。

## 1. `_QUOTE_STRICT_SINCE` 的格式,spec 和先寫好的測試互相矛盾
severity: major
blocking: 是
引句:「新常數 `_QUOTE_STRICT_SINCE` 設成合入隔日 `T00:00:00+08:00`(實作時填實際日期,寫法同 `_SECURITY_SEAT_SINCE`)」
file: `scripts/test_lumos.py:26935` 測試寫 `f"{m._QUOTE_STRICT_SINCE}T00:00:00+08:00"`,是把常數當純日期再補時間。
file: `scripts/lumos:8216` `_SECURITY_SEAT_SINCE` 是完整的 `2026-09-12T00:00:00+08:00`。
1. spec 說常數是完整時戳,寫法同 `_SECURITY_SEAT_SINCE`。
2. 測試把常數當純日期,寫法同 `_SEV_WRITESIDE_CUTOFF = "2026-08-27"`。
3. 照 spec 實作,測試會組出 `...+08:00T00:00:00+08:00`,`_loop_ts_key` 解析失敗回 None,S5 的「切換日當天判不過」那一格直接紅。
4. 照測試實作,spec 的 PRIOR-ART 就要改寫。兩邊必須擇一。
5. 測試也寫死了 `strict=` 這個關鍵字參數名稱,spec 只說「多一個參數」,沒有訂名字。

## 2. 寫側立刻用新判準,處置閘要隔日才用,中間有一段窗口會卡死
severity: major
blocking: 是
引句:「記帳寫側、手動 `quote-check`、席位核對 `seat-check` 一律用新判準」
file: `scripts/lumos:10965` 寫側檢查載體引句,沒有時間分支。
file: `scripts/lumos:26373` 處置閘讀側。
1. 合入當天 D,寫側就用新判準。
2. 一份載體含巢狀引號,新判準判錨定、舊判準判截斷。spec 量到這類有 45 組(約 1.7%)。它在 D 日記帳,寫側放行。
3. 處置閘看到該筆帳的 ts 早於切換時間(D+1),改用舊判準,判錨不到,處置閘擋下。
4. 帳本只進不出,只能換編號整輪重記。這正是 `loop-convergence-recording` 〈載體席〉那節想避免的事。
5. spec 的理由(「合入當天白天仍有人用舊碼寫帳」)只管讀側,沒處理寫側新、讀側舊的窗口。
6. 修法二選一:寫側也依「現在是否 ≥ 切換時間」選判準;或切換時間設成合入當下。

## 3. 同步清單漏掉會翻紅的既有測試,以及另外四處文件
severity: major
blocking: 是
引句:「代碼審 `skills/lumos-code-loop/SKILL.md` 步驟 2 以它為唯一來源,同步改那句摘述」
file: `scripts/test_lumos.py:45462` 斷言 SKILL.md 含「巢狀」兩字。
file: `skills/lumos-code-loop/SKILL.md:34`
1. spec 改後的新句子是「引句內有同型引號要成對…」,沒有「巢狀」。照改後 `t_…` 該測試(`code-loop skill 明寫引句內不要再包同型括號`)會紅。spec 的驗收條款沒提到它。
2. spec 的同步清單只列 `templates.md` §1 和 SKILL.md 兩處。我另外查到:
   - `scripts/lumos:25004` 的 `_CODEX_AGENT_INSTRUCTIONS` 內嵌了引句格式。
   - `scripts/lumos:26531` 的 quote-check 錯誤訊息「常見原因」只寫四項,沒有「引號沒閉合」或「落單收尾引號」。
   - `skills/lumos-project-notes/commands/05-設計審查迴圈.md:14` 只寫「錨不到的引句不採信」,沒提格式不合與新舊判準。
   - `Systems/loop-convergence-recording` 的〈載體席的引句要全錨〉,以及 `Systems/design-loop` 的收貨三道 KEY,都沒有「判準依帳的 ts 切換」這件事。
   - `Projects/逾期回頭條件立案清單2026-10_計劃` 第 18 項要求「明文承認」,與本案「改成機械修法」是兩條路,需要結案或改寫。
   - `Projects/世界解重新註解2026-10_總覽_調研` 第 6 名寫「行區間+整段」,本案只做整段,需要註明。
3. spec 只在 `lands_in` 列了 `Systems/loop-convergence-recording`。

## 4. 推翻 Issue 白紙黑字寫的前提,卻沒有記成決策
severity: major
blocking: 是
引句:「不推進回放引擎版本 `_REPLAY_ENGINE_REV`:回放重算餵回的是凍結閉包裡的整行帳(含 `ts`)」
file: `docs/lumos-toolchain-knowledge/Issues/引句錨定只驗前綴_後半可編造.md:55` 寫「改判準必須同時推進回放引擎版本」。
1. 那個 Issue 把「必須推版本」列為代碼審 r1 兩席各自抓到的結構性前提。spec 反過來決定不推,理由(判準跟帳的 ts 走)是新的,而且很可能是對的。
2. 但 spec 只寫「Issue 結案」,沒有要求用 `lumos decision-add` 記下「前提被推翻、為什麼」,也沒有要求在 Issue 上註明原前提已失效。
3. 三個月後的人讀 Issue 會看到相反的指示。
4. 這個決定的成敗又全押在 ★推送前驗證★ 那一步,見第 7 條。

## 5. 回退段彼此矛盾,且標記為制度演進的做法不存在
severity: major
blocking: 是
引句:「只想暫時關掉不還原:把切換日改到未來,所有輪次都回到舊判準(要走代碼審)」
1. 寫側和手動 `quote-check` 不看時間,「一律新判準」。把常數改到未來,只會讓處置閘回到舊判準,寫側仍是新判準。「所有輪次都回到舊判準」不成立,寫側與處置閘反而重新不一致。
2. 已凍結的黃金判定裡,若載體 ts 在原切換日之後,把常數挪到未來後會改用舊判準重算。第一段回退說的「巢狀、反引號示範」兩類會翻轉,引擎版本沒變,回放判成邏輯漂移 rc1,不是「golden 過期」。
3. spec 說的「照回放流程標記為制度演進」,在程式裡只有推進 `_REPLAY_ENGINE_REV` 才會觸發,而本案明確不推。實際能走的只有逐迴圈 `--freeze` 重凍,spec 沒寫這條路。

## 6. 量測數字沒有交代怎麼重算,口徑對不上
severity: major
blocking: 是
引句:「帳上 2631 組(報告, 快照)可讀。現行判準與新判準都判「全數錨定」的 2587 組」
這句話整行不能抄(內含「」),我把它縮成可抄的片段,供對照。
引句:「真正翻轉的是:引號沒閉合 8 條、引句後同一行有落單收尾引號 9 條、整段比對後錨不到 4 條」
file: `docs/.canary-log.jsonl` 我實際數,同時有 `report_path` 和 `snapshot_path` 的帳列是 3543 筆,spec 寫 2631 組,篩選口徑沒說。
1. spec 沒給量測腳本、指令或存放位置,下一個人無法重現。
2. 「44 組」扣掉「量測腳本自己多加的規則」後只剩 21 條(8+9+4),被扣掉的約 23 組沒有逐項交代。「多半是巢狀」(45 組)也沒給實數。
3. 「約 5%」報告會翻,後面列的卻是 160、178、90「條」,單位是報告還是引句條數,混在一起。以 1718 組算 5% 約 86,對不上 428。
4. 量測母體是全部席的報告,但處置閘和寫側只驗載體席(`scripts/lumos:26320`,`carrier`)。0.3% 對上線後實際會擋掉的比例沒有直接代表性。
5. 補救:spec 內附量測指令,或把腳本放進 `scripts/`,並註明篩選口徑(只取兩路徑皆在、是否包含非載體席、日期下限)。

## 7. 推送前回放驗證和 RETIRE-IF 都沒有機械入口
severity: major
blocking: 是
引句:「★推送前驗證★:對 `governance/replay/` 底下全部已凍結的迴圈實跑一次回放黃金抽查,零漂移才推」
file: `governance/replay/` 下有 305 個迴圈目錄。
file: `scripts/lumos:1060` `cmd_loop_replay` 一次只收一個 `loop_id`。
1. 沒有批次指令。spec 沒說怎麼一次跑 305 個、哪個 rc 算過、需要多久,也沒綁成測試或腳本。「零漂移才推」只存在於這篇計劃的散文裡。
2. 「上線後 8 週內人工抽查」沒有樣本大小、沒有抽樣方法、沒有誤傷與真抓的判準。
3. REVISIT 要求「數上線後被判格式不合的條目」,但新判準判出的格式不合不會被記下。處置閘只印不寫帳。寫側擋下時(`scripts/lumos:10965` 之後)只印訊息並回 2,沒有呼叫 `_gate_event_or_warn`,所以也沒有事件紀錄。到 12-15 那天沒有資料可數,得自己重跑全部報告。
4. 補救:至少讓寫側擋下時記一筆 gate 事件,或在 spec 附上重算腳本。

## 8. 反引號和圍欄排除,開了一個「引句不被驗」的後門
severity: major
blocking: 是
引句:「包在反引號行內程式碼或 ``` 圍欄程式碼區塊裡的不算(說明文字示範格式時常這樣寫,舊抽取器會誤抓,見 Issue 第四點)」
file: `scripts/lumos:25786` 現有 `n_markers` 補差額的 fail-loud 機制。
file: `scripts/lumos:10055` 與 `scripts/lumos:10130` 專案已有圍欄追蹤(`_visible_lines`)。
1. 席位把一條編造的 `引句:「…」` 包進反引號,既不進抽取,也不進標記數。這條引句既不算錨定也不算錨不到,直接消失。只要報告還有別的未包反引號的引句,整份就判過。
2. 圍欄沒閉合(例如席位漏寫收尾的 ```),後面所有引句都會被當成程式碼區塊內容吞掉。
3. spec 沒定義:`~~~` 圍欄、縮排圍欄、雙反引號行內碼算不算;整份只剩被排除的引句時,是回零引句 rc2,還是報告視為沒有引句。
4. spec 也沒說要重用 `_visible_lines`,還是另寫一份。`_quote_norm` 有「單一實作鐵則」,同一類規則再寫第二份,就是 `_quote_norm` 註解禁止的事。

## 9. 抽取規則 3、4 在多條引句時語意沒訂
severity: minor
blocking: 否
引句:「掃到報告結尾還沒回到零:這條判格式不合(引號沒閉合)。」
1. 一個漏掉的 `」` 讓深度永遠回不到零,後面所有真引句的 `引句:「` 都被當作巢狀吞進去,只產生一條 malformed,其他引句消失。舊判準是「標記數 − 抽取數」補差額列,行為不同。
2. 引句結束後是從該位置續掃,還是從下一個標籤續掃,spec 沒說。引句內容本身含 `引句:「` 字樣時結果不同。
3. 規則 4 的「落單同型收尾引號」,對「引句結束後同一行剩下的文字」的邊界(行尾、下一條引句同行)只靠測試的兩個例子推論。

## 10. 邊界細節:ts 無時區、PRIOR-ART 的陳述不準
severity: minor
blocking: 否
引句:「比較走 `_loop_ts_key` 換算 UTC(那兩處註解記載的坑:合入當天白天仍有人用舊碼寫帳;字串比日期會依記帳機器時區判不同)」
file: `scripts/lumos:10493` `_SEV_WRITESIDE_CUTOFF` 其實是字串比較(`str(ts) >= _SEV_WRITESIDE_CUTOFF`),沒有走 `_loop_ts_key`。只有 `_SECURITY_SEAT_SINCE`(`scripts/lumos:8217` 註解)走。
1. spec 說「兩個先例」都走 `_loop_ts_key`,不準。
2. ts 沒時區時 `_loop_ts_key` 回 None,spec 只說「缺 `ts` 用舊判準」,沒處理「有 ts 但解析不動」。資安席一步的做法是 fail,不是退回舊判準。這兩種寫法選哪個沒訂。
3. 帳上 4205 列裡有 95 筆是 `+00:00`,不是 `+08:00`,所以換算是必要的,不是理論問題。

## 11. 手動 `quote-check` 和處置閘對同一份舊報告會給出不同結論
severity: minor
blocking: 否
引句:「記帳寫側、手動 `quote-check`、席位核對 `seat-check` 一律用新判準」
1. 重審舊迴圈(切換日之前記帳的載體)時,手動 `quote-check` 用新判準,處置閘用舊判準,兩邊可能一個紅一個綠。
2. 輸出沒標示用的是哪一版判準,也沒有 `--legacy` 之類的旗標可以選。
3. 編排者依 `templates.md` 的 carrier 選席 SOP,記帳前先跑 `quote-check`。新舊判準不同時,這一步的結論可能和閘的結論相反。

已讀、無 finding:「範圍」節、「實務隱患」節的三個「已排除」項(金流、對外送出、不可逆)。`seat-check` 一律用新判準與測試對得上,它本來就跳過 `malformed` 列,spec 這點交代屬實。

總結:最高等級 major,blocking 共 7 條
