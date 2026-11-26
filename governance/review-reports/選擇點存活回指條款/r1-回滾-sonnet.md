severity: major

## 入口清單與回退後痕跡

下面每個入口都寫了它的回退後結論。

| 入口 | 寫的痕跡 | 回退後誰讀、讀成什麼 |
|---|---|---|
| 覆蓋階段、`--reach-only` | `kind: reach` 事件 | 回退 1:S8 照印分類。回退 2:輸出拿掉,事件變死資料。舊讀者不會把它當判定,因為 `_choice_ledger_index` 已先篩 kind(`scripts/lumos:78792`)。 |
| `choice-layer <結果.json>` | `kind: layer` 事件 | 回退 3 之後沒人讀。舊讀者同樣篩 kind。但第 4 層建議出來的放行紀錄還留著,事後無法回溯哪些放行是來自判讀。 |
| 換候選 | 多筆 choice-kill 事件,帶 `candidate` | 回退 4 之後 `_choice_pick` 又回到第一候選,見 finding 9。 |
| 推送閘提示、`choice-points`、`gov --stats` | 不寫帳 | 這三處都是讀端。 |

- 舊版讀新事件基本安全。`_choice_ledger_index` 篩了 kind,擋下事件的去重迴圈(`scripts/lumos:79612` 附近)與 `situation-rule` 的讀帳(`scripts/lumos:79832` 附近)也都篩 kind。
- gov 的映射(`scripts/lumos:18560`)對 reach 與 layer 事件只會帶出 `verdict=None`,`_gov_choice_count_one`(`scripts/lumos:17943`)會忽略它們。
- 真正退不掉的有兩類。一類是「撤回、重算」沒有指令可用。另一類是換候選造成的壞法身分漂移。

## 發現

1. `--reach-only` 對不明事件不會重跑,「重算蓋過」沒有入口
severity: major
blocking: 是
段落:範圍 7、不可逆那條
引句:「不產壞法,只對這個範圍裡帳上目前是存活、而且沒有對得上的 reach 事件的行跑覆蓋階段」
- `unknown` 也是一筆 reach 事件,而且 `tests_sha` 對得上。
- 第一次沒設 `coverage`(S3 記「沒設定覆蓋」),之後設好再跑 `--reach-only`,這些行會被跳過。「時間不夠」與「覆蓋指令失敗」這類暫時性原因也一樣。
- 覆蓋設定寫錯,例如漏了 `-x`,會讓每行都被誤記成 `clause`。這種事件同樣對得上,也不會被重算。
- 不可逆那條寫的是「分類錯了下次重算的新事件蓋過」,但沒有任何指令會對已對得上的行重算,這個說法不成立。
- 要補一個 `--reach-only` 的重算旗標,至少讓 `unknown` 不算對得上。

2. 層事件記錯了無法撤回,也無法重判
severity: major
blocking: 是
段落:範圍 9
引句:「對範圍裡帳上目前是存活、沒有對得上的層事件的行,照〈用詞〉判讀材料印出」
- 判讀代理把該問人的歸成第 2 或第 3 層,事件的 `tests_sha` 與 `spec_sha` 便會一直對得上。
- 這一行不會再出現在 `--template`,範圍 10 又要求 `file`+`fp` 必須在材料裡,所以第二次記錄大概也會被拒。
- `layer` 的合法值只有 1–4,沒有撤回值。
- 目前唯一能撤的辦法,是改動該計劃任何一個字,或改動守的測試。這會連帶讓同一份計劃下所有層事件一起失效。
- 發現渠道只有 2027-03-15 的 REVISIT 抽 20 條。抽到錯的以後,spec 沒有交代怎麼處理。
- 同時,第 2、3 層的推送提示寫「不用問人」,人看不到 `before` 與 `after`,錯判在日常根本看不出來。
- 需要補三樣東西:`--template` 帶 `--redo` 或指定鍵、層事件的撤回語意,以及記錄端對「已有層事件的鍵」的處理。

3. 層事件的鍵沒綁壞法身分
severity: major
blocking: 是
段落:範圍 10
引句:「讀側同一鍵取最新一筆,`tests_sha` 與 `spec_sha` 都等於現在的才算對得上」
- `before` 與 `after` 描述的是某一個壞法。
- 鍵只有 `(file, fp)`,與該壞法的 `new_sha` 無關。
- `_choice_disposition` 的說明(`scripts/lumos:78800` 附近)明寫「挑到的壞法換了,行指紋沒變就照算」。換候選與回退 4 都會讓同一行換壞法。
- 換壞法之後,舊層事件仍然「對得上」,推送提示印的是舊壞法的業務問題。
- 要在層事件記壞法身分(`new_sha`),讀端也要比對。

4. 層事件沒有 `token`,gov 去重會把同一提交的多筆折成一筆
severity: major
blocking: 是
段落:範圍 10
引句:「欄位照結果另加 `tests_sha`(同存活那筆)、`spec_sha`(碰到的計劃檔內容雜湊,依路徑排序後串起來算)與 `written_at`」
- gov 去重鍵含 `token`,對 choice-kill 閘只取 `d.get("token")`(`scripts/lumos:18543` 附近、`scripts/lumos:18636`)。
- `_gate_event_build` 不會自動補 `token`(只做 `ev.update(extra)`)。
- 一次 `choice-layer` 記 20 筆,在 `gov --stats` 的「四層各幾筆」會只算 1 筆。
- 範圍 4 只替 reach 明寫了 `token`,層事件漏了。

5. 層事件引句的機械驗證擋不住「引一個很短的字串」
severity: major
blocking: 是
段落:範圍 10
引句:「`basis` 至少一筆 `where` 是那份計劃裡存在的條款號,`quote` 是那條條款原文的子字串」
- 沒有引句最短長度,也沒有正規化規則(空白、Markdown 符號、NFC)。
- 一個字(例如「當」)就是任何條款原文的子字串,可以輕易通過第 3 層。
- 〈實務隱患〉說三道擋之一是「引句要對得到計劃原文」,這一道目前形同虛設。
- 第 2 層的反面條件(不得是任何條款的子字串)同樣可以用一個罕見字繞過。

6. 換候選的終局 `no_result` 會被無限重跑,與自己的 WHY 矛盾
severity: major
blocking: 是
段落:範圍 11
引句:「3 個都編不過記 `no_result`,原因」
- `_choice_kill_pick`(`scripts/lumos:79072` 附近)對 `no_result` 一律重跑。`_choice_pick` 又是同一種子、同一順序,每次都從第 1 個候選開始。
- 三個都編不過的行,每次都白跑同樣三個候選,沒有轉機,卻照樣擋推送。這正是 WHY 說要避免的「留成跑不出結果、讓人去查不存在的問題」。
- `--max-seconds` 用完停在候選 1 與候選 2 之間時,spec 沒說最後一筆記什麼。每次都從頭重試,可能永遠進不到候選 2。
- 要定義:候選用盡的結局(例如記成建議等價並要人放行)、中途時限停止的記法,以及從第幾個候選續跑。

7. gov 白名單漏了 `candidate`
severity: major
blocking: 是
段落:範圍 5
引句:「治理帳讀取的欄位白名單與型別表要補 reach 與 layer 事件的新欄位」
- 只列了 reach 與 layer 的欄位。
- `candidate` 是掛在既有 choice-kill 事件上的新欄位。白名單(`scripts/lumos:18560`、`scripts/lumos:18562`)不收它,gov 會把它丟掉。
- 同一段要求印「編譯不過換候選幾次」,REVISIT 也要用這個數,字面照做會算出 0。
- 白名單與型別表要一併列入 `candidate`。

8. 回退 4 之後,已處置的行可能被打回「跑不出結果」
severity: major
blocking: 是
段落:〈回退〉第 4 條
引句:「帳上 `attempt` 大於 1 的舊事件照既有規則讀(同鍵取最新一筆)。」
- 一行原本靠候選 2 被殺掉,或被人用 `situation-rule --point` 寫回。
- 回退後 `_choice_pick` 回到不驗編譯的第一候選。
- 日後測試雜湊一變,這一行重跑會得到 `no_result`「壞法編不過」,最新一筆蓋過原來的 `killed`,於是退回「未處置」並擋推送。
- 再用 `situation-rule --point` 處置它,壞法身分也是那個編不過的候選,殺傷力過不了,只剩放行這一條路。
- 〈回退〉沒有處理這個情況。要寫明做法,例如回退時保留換候選的選擇,只關掉新的呈現。

9. 回退 2 與回退 3 漏了文件端
severity: minor
blocking: 否
段落:〈回退〉第 2 條
引句:「[[Systems/guard-kill]] 的 WHY 標作廢。」
- lumos-code-loop 手冊的判讀四步、規格閘的提示句、路線總圖的指向,回退時都沒有跟著撤。
- 之後 AI 會照手冊去跑已經不存在的 `choice-layer`。
- 〈實務隱患〉說「讀者逐一列出、各補一案」,但全文只列了 S10 的三處,沒有逐一列出。

10. `--reach-only` 的整次 run 事件沒定義
severity: minor
blocking: 否
段落:範圍 4
引句:「整次 run 那筆多 `reach_secs`(覆蓋階段秒數,無條件進位)與 `reach_groups`(跑了幾群)。」
- `--reach-only` 不產壞法。
- 它要不要寫 `kind: run` 沒說。寫的話,「choice-kill 呼叫次數」與「改動行中位數」會被零值拉偏(`scripts/lumos:17943` 附近、`scripts/lumos:17982` 附近)。
- 不寫的話,`reach_secs` 沒有地方放。

11. 層事件超過 4096 位元組時的處理沒寫
severity: minor
blocking: 否
段落:範圍 10
引句:「全過才寫:每筆一個治理帳事件,閘名照 choice-kill」
- `_gate_event_fit`(`scripts/lumos:1884`)只會縮 `list_key` 指定的清單。
- 層事件的 `basis`、`quote`、`question`、`before`、`after` 是自由文字,沒有指定要縮哪一個,也沒有字數上限。
- 超過 4096 照寫,帳長得更快。spec 沒說。

12. 「最新一筆」的順序依據沒定義
severity: minor
blocking: 否
段落:範圍 5
引句:「同一鍵取最新一筆 reach,而且它的 `tests_sha` 等於存活那筆的才用」
- 治理帳是版控的 jsonl,分支合併後檔內順序不等於時間順序。
- 既有讀者用檔內順序(`evs[-1]`),層事件卻有 `written_at`。spec 沒說用哪個。
- 兩個分支各判讀同一行,合併後會讀到哪一筆沒有定義。

13. `spec_sha` 用整份計劃檔雜湊,會被無關編輯洗掉
severity: minor
blocking: 否
段落:範圍 10
引句:「`spec_sha`(碰到的計劃檔內容雜湊,依路徑排序後串起來算)」
- `lumos set` 改 frontmatter 的 `status` 或 `updated` 就會讓雜湊變掉,所有層事件一起失效。
- 「碰到的計劃」這個集合本身也會隨其他計劃進行中或完成而變動。
- 失效是被動回到安全側(改印覆蓋分類、顯示「未判讀」),所以只算 minor。

## 逐節

- 白話、用詞、不做、天花板、依據來源:已讀,無 finding。
- 實務隱患「新舊帳互讀」:舊讀者行為已驗證安全,只剩 finding 9 提到的清單缺漏。
- 實務隱患「判讀把該問人的歸成第 2、3 層」:三道擋裡的兩道有洞,見 finding 2 與 5。

總結:最高等級是 major,blocking 共 8 條
