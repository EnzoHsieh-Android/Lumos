severity: major

## c1 有效紀錄沒比對「現在綁的測試」,換綁或亂指 `--test` 都能沿用舊紀錄
severity: major
blocking: 是——照字面實作,條款改綁別支(更弱的)測試後,舊的「殺得掉」紀錄仍判有效。
- 位置:〈用詞〉有效紀錄、〈範圍〉2 驗證。
引句:「那句原文都對得上現在那一行」
- 問題:對得上的欄位只有計劃、條款編號、`clause_sha`、第幾個、`near_text`。`test_name` 在欄位表裡,但沒有任何一句要求它等於條款現在綁的測試。
- 為什麼會漏:`_clause_sha` 不含 `[test:]`,綁的測試是另外比的。人裁那邊就是靠另一道比對補上這點,程式註解寫明是代碼審 r1 通才 t1 抓到的:`scripts/lumos:14575` 的 `got[1] == {e["test_name"]}`。
- 例 1:S1 綁 `[test:t_strong]`,跑了一筆 killed。作者改成 `[test:t_weak]`(雜湊不變)。推送閘看到舊紀錄對得上,放行。
- 例 2:條款綁 t_a、t_b,`--near 1 --test t_a` 殺掉了。t_b 沒被驗,推送閘照樣放行。
- 例 3:〈範圍〉2 只寫「條款綁多支時要 `--test` 指定其中一支(綁一支時可省)」。條款綁一支 t_a 時給 `--test t_other`,沒有規則拒絕。於是可以拿一支與條款無關、本來就會紅的測試跑出 killed,記成這條條款的有效紀錄。
- 該補的規則:`--test` 必須屬於條款現在綁的清單,推送閘比對 `test_name` 是否仍在現在的綁定裡。

## c2 「沒有弱證據」不在紀錄裡,推送閘看不到;呼叫方式也沒說怎麼取
severity: major
blocking: 是——弱證據的 killed 會被記成「殺得掉」並通過推送閘。
- 位置:〈用詞〉殺得掉、有效紀錄的欄位表、〈範圍〉2 跑。
引句:「呼叫 `cmd_guard_kill(..., recipes_override=[壞法], source="clause-kill")`」
- 問題:`weak` 是獨立的布林欄位,不是 verdict 的一個值(`scripts/lumos:28009`)。成因是整套一起跑(run_cmd 沒有 `{method}`)、平台標 flaky、筆記有未提交改動、mtime 不確定。這時 verdict 仍是 `killed`。
- 兩個缺口:
  1. 〈範圍〉2 的呼叫沒有 `result_out`,也沒說用回傳碼還是結果列判定。`cmd_guard_kill` 的 rc 對 `killed`+weak 回 0(`scripts/lumos:28071` 之後的收尾;說明文字「全 killed(含 timed_out)=0」在 `scripts/lumos:27772`)。只看 rc 會把弱證據當成功。
  2. 有效紀錄欄位沒有 `weak`。就算 clause-kill 當下判對了,推送閘只讀帳,只能看到 `verdict: killed`,沒辦法區分強弱。
- 例:run_cmd 沒有 `{method}`,整套跑時某支不相干的測試紅了。結果是 `killed`+`weak:true`,rc 0,記成殺得掉,推送閘放行。這與「沒有弱證據」的定義矛盾。

## c3 `clause-kill` 這個閘名沒登記,照〈用詞〉的寫法事件會被丟掉
severity: major
blocking: 是——按字面實作,治理帳寫不進去,推送閘永遠找不到紀錄。
- 位置:〈用詞〉有效紀錄、〈範圍〉2 記。
引句:「寫法照人裁的 `_situation_rule_event_parts`」
- 問題:`_gate_event` 對不在 `_KNOWN_GATES` 的閘名直接不寫(`scripts/lumos:1840`)。人裁的閘名是靠登記才寫得進去。spec 的〈範圍〉4 與〈回退〉都沒列這個登記。
- 同族會連帶紅或失準,spec 也沒列:
  - `LOOP_NOT_CLOSE_EVENTS`(`scripts/lumos:20643`,守衛 `t_loop_close_kinds_classified`)要分類新的 (gate, kind)。
  - gov 統計的去重 token 對 `situation-rule` 有特例。`clause-kill` 沒有 token,同一提交同一計劃多筆會被折成一筆。這只影響統計,不影響推送閘。
- 例:跑 `lumos clause-kill`,殺傷力成功、rc 0,但 `_gate_event` 印「不在 `_KNOWN_GATES`」並回 False。推送時閘找不到有效紀錄而擋,重跑 Gradle 也無解。
- 該補的規則:寫明要登記 `_KNOWN_GATES`、`LOOP_NOT_CLOSE_EVENTS`、gov 去重 token。事件寫不進去時,clause-kill 不能回 0。

## c4 「`[near:]` 含 `]` 就擋」用 `INV_TAG_RE` 同一支正則做不到
severity: major
blocking: 是——含 `]` 的 near 不會被形狀檢查擋下,殘字還會留在條款正文裡。
- 位置:〈用詞〉近似錯誤寫法、〈範圍〉1。
引句:「形狀不合(太短、含 `]`、理由太短)也擋」
- 問題:剝除用的是 `[^\]]+`,遇到第一個 `]` 就結束。
- 例:`[near:用 list[0] 代替 list.first(),空清單會崩]`。
  - 正則只抓到 `用 list[0`,有 6 個以上實字,形狀檢查通過。
  - 剩下的 ` 代替 list.first(),空清單會崩]` 留在條款正文,進入 `_clause_sha`、文法判定和 `clause_bindings` 的視野。
  - 記下的 `near_text` 是被截斷的版本。
- 補強方向:要有獨立掃描器,找每個 `[near:` 之後到行尾,檢查括號配對;或明寫殘留的 `]` 視為形狀不合。
- 備註:Kotlin 的 `arr[i]`、`list[0]`、`[[連結]]` 都是常見寫法。

## c5 紀錄只綁被改檔的原文,測試被改弱後仍有效
severity: minor
blocking: 否——〈天花板〉2、3 已承認新鮮度只看原文,但範圍比寫的更貼近核心。
引句:「原文還在但周邊改了不會發現(天花板 2)」
- 說明:殺傷力證明的是「測試在殺傷力那一刻能抓到錯寫法」。紀錄沒有測試檔的雜湊或提交。殺掉之後把測試改成只送一次值,同名測試仍判有效。
- 例:t_x 在第一次跑時是兩值版本,killed。之後改成單值版本,紀錄仍通過推送閘。
- 這正是這份計劃要防的弱測試,建議把〈天花板〉2 的描述擴成「測試本身被改」,或讓紀錄帶測試檔 blob 雜湊。

## c6 「同一位置有多筆取最新一筆」的取法與排序依據沒定義
severity: minor
blocking: 否——兩種取法都可能被實作成可接受,但結果不同。
引句:「同一個條款同一個第幾個有多筆時取最新一筆」
- 疑義 1:先挑最新再比對雜湊,還是先過濾雜湊相符的再挑最新?
  - 例:跑一筆 killed(雜湊 X)→ 改條款後跑一筆 survived(雜湊 Y)→ 改回雜湊 X。先挑再比對會擋;先過濾再挑會放行(舊 killed 仍有效)。
- 疑義 2:「最新」是檔內順序還是 `ts`?`ts` 是 `isoformat(timespec="seconds")` 加本機時區(`scripts/lumos:1597`),跨時區或跨機器字串排序會錯。
- 該補的規則:說清楚「過濾後取檔內最後一筆」。

## c7 `[near:]` 放在行中時,S3 的「雜湊不變」不成立
severity: minor
blocking: 否——只有放在句中才會出錯。
引句:「條款雜湊與文法判定 應 跟沒有它時一樣」
- 說明:`INV_TAG_RE.sub("")` 之後只做 `.strip()`,沒有壓縮空白(`scripts/lumos:13902`、`scripts/lumos:13913`)。
- 例:`當 A [near:xxxxxx],應 B` 剝完是 `當 A ,應 B`,與原本 `當 A,應 B` 的雜湊不同。
- 影響:如果原本有人裁紀錄,雜湊對不上,會導致紀錄失效。
- 該補的規則:`[near:]` 只准放在標記尾端,或剝除時一併吃掉前導空白。

## c8 不是殺得掉就一律 rc 1,漏了「執行錯誤」的處理與訊息
severity: minor
blocking: 否——只影響訊息準確度,不影響守衛結論。
引句:「判定不是殺得掉時 rc 1」
- 問題:`cmd_guard_kill` 對 drifted/abort/error 回 rc 2。clause-kill 把它與 survived 合併成 rc 1,並印「補測試讓它紅」。
- 例:`--old` 出現兩次,guard kill 判 drifted(`scripts/lumos:26700`);編譯失敗是 error。這兩種情況補測試沒有用。
- 建議:分開訊息(換 `--old`/`--new`、修編譯),rc 仍可用 1 或 2。

## c9 風險高的人裁寫回條款、`[keeps]` 條款也被要求宣告 `[near:]`
severity: minor
blocking: 否——是流程摩擦,不是錯誤判定。
引句:「`[manual:]` 條款不要求」
- 問題:預期值表那道扣掉人裁寫回(`_spec_gate_ruled_ids`)與 `[keeps]` 的條款(`scripts/lumos:14603`)。〈範圍〉1 只排除 `[manual:]`,而且說「同一個判法」只講了門。
- 例:情境題流程用 `lumos situation-rule` 寫回 `[S3] … [test:t]`,不帶 `[near:]`。計劃是高風險時,推送被 S1 擋下。作者得手動補 `[near:]` 再跑 Gradle。
- 要寫明:是要求、豁免,還是複用預期值表的集合。

## c10 `[near:無 …]` 無限制,`--old/--new` 與 `[near:]` 句子沒有任何綁定
severity: minor
blocking: 否——〈實務隱患〉第一條承認「靠設計審」,但這兩個洞比那句話寫的大。
引句:「用在想不出有意義錯寫法的條款」
- 免宣告:`[near:無 想不出來有什麼錯寫法]`(10 個以上實字)可以放過任何條款,包括面試題那個 flatMapLatest 案例。
- 沒綁定:紀錄的 `old`/`new` 與 `near_text` 之間沒有機械關聯。任意檔案、任意無關替換,只要測試紅就記成殺得掉。
- 設計審只看得到 `[near:]` 那句,看不到實際壞法。建議至少要求紀錄裡的 `old`/`new` 可被審查看到(例如計劃或帳的摘要)。

## c11 `--file` 沒定義路徑基準與驗證
severity: minor
blocking: 否——單人環境,影響面小。
引句:「被改檔、原文、錯寫法、要補的 import」
- 問題:人裁那邊的 `kfile` 是從平台根所在 repo 的最上層算的(`scripts/lumos:75898`,在 srl 分支)。clause-kill 沒說 `--file` 相對誰。
- 推送閘用 `git show <推送提交>:<file>`,基準是 repo 根。平台根是巢狀 repo 時兩者不同,會一直判 0 次而擋。
- 沒說的驗證:`../`、絕對路徑、符號連結。

## 已讀、無 finding 的部分
- 〈白話〉〈舊否決比對〉〈不做〉〈回退〉:交叉引用的目標存在、說法一致。
- 〈範圍〉3 只讀帳不重跑:與預期值表那道一致(`_spec_gate_push_scan`)。
- S9 的生效日邏輯:`_plan_effective_day` 讀不到時回 None,呼叫端當生效日之後,即偏嚴。
- 預期值表缺列:S8 只有「出現 0 次」,沒有「出現 2 次」。〈範圍〉3 的規則有涵蓋,屬補列。

## 固定席逐條判:Systems/guard-kill
- `★INVARIANT★ guard kill rc 優先序`:不影響。理由:`source` 只加進 kill-log 那一行(`scripts/lumos:28041`),rc 的計算(`scripts/lumos:28071` 起)沒動。clause-kill 另外把判定轉成自己的 rc,不改 guard kill 的 rc。
- `★INVARIANT★ --json 模式 stdout 恰一行`:不影響。理由:clause-kill 不傳 `as_json`,`source` 不影響輸出。
- 前提:`source` 只能是選用參數且預設行為不變。若實作改成預設也寫 `source`,「不傳維持原行為」的〈回退〉才會破。

## 實務隱患鏡頭
- 併發與交易:無。單人依序操作,沿用 guard kill 隔離工作樹。
- 資料量:無。紀錄單行有 4096 位元組的政策上限,但 `_gate_event` 本身不硬擋(`scripts/lumos:1850` 附近說明);`old` 很長時可能超過,影響只是帳變長。
- 跨平台:見 c11。
- 資安:無新增面。唯一要注意的是 `near_text`/`note` 進入帳與終端輸出,需照人裁走 `_kill_esc`。

最嚴重:major;blocking 共 4 條
