severity: major

我把 spec 逐節讀完,再對照程式碼查證。寫入、凍結、重算判定的入口有 7 個:

| 入口 | 退回後還在嗎 | 舊版讀到會怎樣 | 要人收拾嗎 | 救得回嗎 |
|---|---|---|---|---|
| 盲判 `rule_hits` 事件 | 在,帳只追加 | 只有 `rule_hits`、沒有 `blind_judge` 欄的事件被 `_kt_bj_event_ok` 跳過;同檔含 `segments` 的事件照讀 | 不用 | 不救,見 F4 |
| `token` 欄 | 在 | `_gov_row` 對 blind-judge 事件用 `written_at` 當 token,新 `token` 欄被忽略 | 不用 | 見 F3 |
| `rule-review` 事件 | 在 | 舊版不認 | 不用 | spec 沒定義事件格式,見 F2 |
| fail-open 事件(scope `rule-review`) | 在 | 照常被 `gov --stats` 數 | 不用 | 不適用 |
| `.lumos/lint-review.json` | 在 | 我沒在 `scripts/lumos` 找到會讀它的程式,應是無害 | 不用 | 不適用 |
| 放行檔 `.lumos/lint-waivers.json` | 在,而且會被寫入 | 舊版讀得到 | 要,見 F1 | 要人處理 |
| 範本 | 手冊與範本退回,消費專案已複製的不會跟著退 | 消費專案的覆核宣告檔舊版不讀 | 不用 | 不適用 |

severity: major
blocking: 是
判準:回退節宣稱「不用收拾」,但設計本身會寫放行檔。
- spec 段落:〈回退〉與〈範圍 6〉。
- 問題:判 `real` 被擋時,放行出口是 `lumos lint-waive`,會寫放行檔。`_lint_waive_origin` 與 `_lint_waivers_add` 會記 `origin`(人或 AI),`lint-waive` 還會記治理帳 `waived` 事件。退回本計劃後,覆核規則的放行紀錄留在放行檔裡,AI 放行(`origin` 為 ai)會一直被 doctor 與推送前小結列為「沒人看過」。唯一的清法是 `lint-waive --ack --all`,連不相干的 AI 放行一起確認掉。
- 另外,「放行」在指紋上是永久的,放行一處等於放行同檔同片段的每一處。回退後那些指紋沒有任何覆核了。
引句:「放行檔沒被本案寫過,不用收拾。」
- 佐證:`scripts/lumos:41245`(`--ack --all`)、`scripts/lumos:41271`(`origin == "ai"` 的提示)。
- 與〈實務隱患〉「AI 自己放行真問題」以及〈天花板〉第 6 條自相矛盾。

severity: major
blocking: 是
判準:`rule-review` 的事件格式與讀取順序沒有定義,推翻無法機械地跟判定配對。
- spec 段落:〈用詞〉人複查、〈範圍 5〉「同一格只認第一筆」、〈範圍 6〉人複查。
- 問題:spec 只寫「寫一筆治理帳事件」,沒寫事件的 kind、欄位、綁哪個判定(seg 還是 token),也沒寫判定、推翻、重判、`agree` 交錯時以誰為準。
  - 「同一格只認第一筆」(情境題既有規則,`_kt_bj_cells_add` 已實作)與「`overturn` 後可再判」互相衝突。折疊規則必須按事件順序重寫,spec 沒講。
  - 重判之後,舊 token 的 `--batch overturn` 事件會不會回頭作廢新判定?沒定義。
  - `agree` 之後又 `overturn`,或 `overturn` 之後又 `agree`,誰贏?沒定義。
  - `overturn` 一筆本來判 `real` 的命中,語意不明。整批 token 同時含 `real` 與 `false` 時,`real` 也會被作廢,雖然方向偏安全,仍是浪費。
- 要補:折疊規則(以 `written_at` 為序,後者蓋前者,或作廢事件只覆蓋它之前的判定),加上對應的條款與測試。
引句:「`overturn` 讓那一筆作廢後,同一格可以再判(見範圍 6)。」
- 佐證:`scripts/lumos:73867`(`_kt_bj_read`)與 `_kt_bj_cells_add` 的「每格只認第一筆」。

severity: major
blocking: 是
判準:推翻要靠使用者輸入的 token,但 token 的定義、顯示與驗證都缺,打錯推翻別批的情況沒擋。
- spec 段落:〈範圍 5〉治理帳欄、〈範圍 6〉`--batch <token>`。
- 問題:
  - 現有程式裡 blind-judge 事件的 token 是 `written_at` 微秒時間戳(`scripts/lumos:17584`),不是獨立欄位。spec 說「另帶 token」,卻沒說它是什麼、`_gov_row` 要不要改。現況下新欄會被忽略。
  - 「待人看清單」只印筆數,沒說會印每筆的指紋與 token。使用者沒有東西可抄。
  - 沒有列出某個 token 底下有哪些命中的指令(像 `--list`)。盲判判錯一批時,spec 沒說怎麼找出是哪一批。
  - 沒寫「指紋或 token 不存在就拒收」。打錯 token、對到別次記帳,就推翻了別批的判定。
  - 沒有撤回推翻的指令。推翻錯了只能重派盲判,而且重判算不算「同一格第一筆」又回到上一條。
  - 條款 S4 只測了 3 筆正確 token 的推翻,沒有未知 token、跨分支 token、推翻後撤回的情境。
引句:「只准單筆或單一 token,沒有 `--all`(解 r1 回滾 F6)。」
- 佐證:`scripts/lumos:17584`、`scripts/lumos:41192`(`_lint_waive_ack` 只記 acked,沒有撤銷)。

severity: major
blocking: 是
判準:判 `false` 的命中一旦推上主線,推翻就沒有可擋的對象。盲判判錯放過真問題,spec 沒有收拾辦法。
- spec 段落:〈範圍 6〉`false` 與人複查、〈天花板〉、〈實務隱患〉「待人看清單沒人看」。
- 問題:閘只看「這次新增的命中」。`false` 判定那次推送放行後,命中已在主線,下一次推送它不是新增,`overturn` 之後沒有任何閘會把它重新擋下。「恢復成要擋」只對還沒推的分支有效。
- 因此 d4 借用 Semgrep「人不同意就重新打開」,但 spec 沒有對應「重新打開」的機制。spec 只有統計,沒有補救路徑:已推送的誤判不會被找回,也沒有人被通知。
- 建議二選一:
  - `overturn` 已推送的命中時,另開一筆待處理項(例如印出該行、要求人修或放行)。
  - 明寫「已推送後的推翻只進統計、不救」,並把它列為〈天花板〉。
引句:「`false`:不擋,列進待人看清單(推送前小結印筆數、doctor 唸)(d4)。」
- 佐證:〈範圍 2〉「抽兩份快照、跑命令、比對新增」,只比對新增。

severity: major
blocking: 是
判準:推翻事件沒有分支與合併側的讀法,S12 只管判定那一側。
- spec 段落:〈範圍 3〉、S12。
- 問題:判定是依 `ev.get("branch") == branch` 讀的(`scripts/lumos:73867`),合併提交時用 `_disp_bj_source` 讀被合進來那一側的帳(`scripts/lumos:74237`)。spec 只說判定照這個讀法。`rule-review` 事件寫在哪個分支、合併後在 main 上被讀不讀,沒有交代。
- 情境:判定記在 feat,合併後在 main 上 `rule-review overturn`,事件在 main 的帳,而判定要從 feat 那側讀,兩邊對不起來,推翻無效。
- 這一條與 r1 那批「推翻無效」(d4 的起因)同形,是該條的平行路徑。
引句:「分支、版本、合併提交那一側照表態那一道 `_disp_bj_source` 的讀法」
- 佐證:`scripts/lumos:74237`、`scripts/lumos:73867`。

severity: minor
blocking: 否
判準:事件名稱重疊,讀者容易混淆。
- spec 段落:〈範圍 7〉。
- 問題:fail-open 事件用 scope `rule-review`,子指令與人複查事件也叫 `rule-review`,統計篩選時要靠 kind 區分,spec 沒指定 kind。建議事件 kind 明寫,避免 `gov --stats` 把兩種算在一起。
引句:「寫一筆 `code-loop` 閘 fail-open 事件(scope `rule-review`)」

severity: minor
blocking: 否
判準:rule_hits-only 事件的欄位形狀沒定。
- spec 段落:〈範圍 5〉。
- 問題:舊讀端用 `_kt_bj_event_ok` 驗 `blind_judge` 與 `role`(`scripts/lumos:73892`),缺欄就整筆跳過,所以舊版讀帳確實會略過 rule_hits-only 事件。但 spec 沒寫這種事件的 `role` 與 `blind_judge` 要不要寫成空值。新寫端若寫 `blind_judge: {}` 或不寫,行為不同。這點應寫進退回節與測試。
- 另外,`--unsure` 仲裁的角色判斷怎麼落在 `rule_hits` 上也沒寫。

抑噪:我沒在這輪重提 r1 已折的項目。r1 的改法大致改對了:放行檔不再被寫入判誤報、覆核宣告另開檔、例外隔離、`seg` 對照當次命中。r1 引入的新洞集中在「推翻」這條線,即 F2 到 F5。

總結:最高 severity 為 major,共 5 條 blocking(放行檔回退矛盾、推翻事件無格式與順序、token 無定義且無驗證、已推送的誤判無法找回、推翻事件的分支與合併側缺口)和 2 條 minor。F4 是設計層面的洞,不只是文字問題。
