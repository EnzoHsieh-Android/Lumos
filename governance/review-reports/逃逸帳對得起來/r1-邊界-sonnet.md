severity: major

## F1 撤回不會擋住同一個 auto-escape 去重鍵重新命中,撤回可能在下一次同觸發下被悄悄復活
severity: major
blocking: 是,照 spec 字面實作,操作者撤回一筆自動記的逃逸後,只要同一個 (loop, stage, sha) 再被同一個自動來源打中一次,系統會不告知任何人地重新記一筆一模一樣的逃逸,撤回等於白做,而且操作者不會發現。
引句:「`_escape_rows_for` 過濾掉被撤回的列與撤回紀錄本身。**所有讀逃逸帳的地方都要走這支**。2026-09-26 查:治理帳統計、問閘尾的漏斗、自動記的去重已經走它」
file: `scripts/lumos:9342-9345` `_auto_escape` 的去重集合 `existing` 目前就是用 `_escape_rows_for(env)` 的回傳建的(`existing.add((nfc(str(r.get("loop", ""))), r.get("stage"), r.get("sha")))`)。
file: `scripts/lumos:9360-9361` 判斷「已經記過」只看 `(nfc(loop_id), stage, sha) in existing`,同一鍵已存在就跳過。
file: `scripts/lumos:25026,25063-25069` CI 紅記逃逸是 CI 收到 webhook/輪詢就觸發,同一個 sha 的 CI 工作流程完全可能重跑(GitHub Actions「re-run failed jobs」)、或 push-gate 對同一 sha 在不同時間點被觸發第二次(`scripts/lumos:6383` push-gate 呼叫同一支)——都是同一個 (loop, stage, sha)。
本案 §三第二點親口承認「自動記的去重已經走它」,意即 spec 作者已知道去重邏輯讀的是 `_escape_rows_for`;但 spec 接下來要求 `_escape_rows_for` 濾掉撤回的列後,沒有處理「濾掉之後,go dedup 集合裡少了這一鍵,同鍵事件重打會重新記」這個後果。這不是理論推演——CI 重跑同一個 sha、push-gate 對同一 sha 二次觸發都是本 repo 現有機制會發生的事,可重現。要嘛撤回要記錄一個獨立的「已撤回鍵」讓 dedup 繼續認得(不再算進統計,但仍擋自動重記),要嘛在 spec 裡明講這是可接受的行為並說明理由,現在兩者都沒有。

## F2 撤回紀錄的欄位形狀完全沒定義,導致無法可靠分辨「撤回紀錄本身」與被撤回的目標,也可能撞壞落盤自驗
severity: major
blocking: 是,少了欄位形狀規格,不同實作者可能各自發明欄位名,不僅 `_escape_rows_for` 過濾不到,還可能讓落盤自驗誤判成功、或讓「撤回一筆撤回紀錄」變成未定義行為。
引句:「`lumos loop escape --withdraw <token> --reason <理由>`:追加一列撤回紀錄,不改舊列。寫入包在既有的圖譜寫入鎖裡。」
file: `scripts/lumos:9511-9519` 正常逃逸列的 schema 是 `{"token": "ESC-...", "loop":, "stage":, "severity":, "desc":, ...}`,`token` 欄位是這一列「自己的」落盤自驗鍵。
file: `scripts/lumos:8017-8045` `_jsonl_append_verified(path, rec, key_field, key_value)` 的落盤自驗是「重開檔找第一筆 `d.get(key_field) == key_value`」——docstring 明講「不寫死欄名(record 用 token、second 用自身 token)」,即每一種帳列都要有自己專屬、不與別列共用的鍵值。
若撤回紀錄沿用同一個 `token` 欄位、值填「被撤回那筆的 token」(spec 唯一給出的識別方式就是 `<token>` 參數),就會跟被撤回的原列共用同一個 `token` 值——`_jsonl_append_verified` 讀回驗證時可能比對到「先出現的那一筆」(通常是原列,因為它先寫入),即使撤回列真的寫入失敗也會被誤判成功;而之後任何要「用 token 找一列」的程式碼(含未來要支援「撤回一筆撤回紀錄」)也無法分辨兩者。
spec 沒有講撤回列要不要自己配一個新 token(當作它自己的落盤自驗鍵)、要用哪個欄位名裝「被撤回目標的 token」(例如 `withdraws`)、要不要有 `kind`/`type` 這類欄位讓 `_escape_rows_for` 認得「這是撤回紀錄本身」——S3 條款要求 `_escape_rows_for` 同時濾掉「被撤回的列」與「撤回紀錄本身」,但濾掉撤回紀錄本身要靠什麼欄位判斷,spec 全文沒有一處回答。

## F3 `--withdraw <token>` 沒有規定要驗證 token 是否真的存在於逃逸帳
severity: major
blocking: 是,照字面實作,打錯 token 或撤回一個不存在的 token 會被靜默接受、寫入一筆指向空氣的撤回紀錄,操作者會誤以為撤回成功,原本要撤的錯誤逃逸列繼續原封不動地算進統計,而且沒有任何錯誤訊息提醒。
引句:「追加一列撤回紀錄,不改舊列。寫入包在既有的圖譜寫入鎖裡。」
file: `scripts/lumos:9503-9508` 對照:正常記帳(`cmd_loop_escape` 非 `--list`/`--auto` 路徑)在寫入前會先驗證 `loop_id` 真的在審查帳的 `known` 集合裡,驗不到就 `擋下` 並印出查法(`lumos gov --stats`)——這是本檔既有的「防編號打錯」慣例。
spec 對 `--withdraw <token>` 完全沒有寫類似的「先確認 token 存在於逃逸帳」的檢查,也沒有寫找不到時要擋下還是靜默通過。S3 條款只驗證「已撤回的列不再被讀到」,沒有一條驗證「撤回不存在的 token 該怎麼辦」。這正好是既有程式碼一貫做法(逃逸記帳驗 loop_id 實存)沒有被沿用到撤回這個新入口的缺口。

## F4 重寫(rewrite)接手前記在舊迴圈編號下的逃逸,會完全從統計中消失,且不落在 spec 定義的任何一種「已知有損失」桶裡
severity: major
blocking: 是,一段合法的設計審查活動(舊迴圈確實跑過、確實有審查帳列、確實有下游逃逸)會被整支統計吞掉不留痕跡,而「誠實界線」段落宣稱的幾種低估來源(歸因不明、站名不認得)都沒有涵蓋到這種情況,讀報表的人無從得知漏了這塊。
引句:「分母:放行了的迴圈數。放行 = 治理帳裡有這個迴圈的收斂紀錄(處置閘過關時寫的),而且審查帳裡有它的列(排除測試留下的假紀錄)。」
file: `scripts/lumos:813-845` `cmd_loop_rewrite` 對舊迴圈編號寫進治理帳的是 `kind="rewrite"`,note 是 `f"prev={loop_id};successor={successor};{note}"`——不是 `kind="converged"`,也不含「PASS」字樣,所以不算 spec 定義的「收斂紀錄(處置閘過關時寫的)」(對照 `scripts/lumos:8392,8495,9244,9684,9797,10673,18584` 六處寫 `kind="converged"` 的呼叫,note 都帶「PASS」)。這代表被重寫的舊迴圈編號**不會**落進分母,合乎 S9。
file: `scripts/lumos:9326-9336` 但 `_auto_escape` 判斷一個迴圈編號能不能記自動逃逸,`known` 集合是掃描 `.canary-log.jsonl` 每一列的 `loop` 欄位——不分 kind、append-only、永遠不刪,所以舊迴圈編號即使被重寫,只要它有過審查帳列,`known` 就永遠含它,自動逃逸(CI/push-gate/code-loop)之後仍可以繼續記到這個舊編號上。
file: `scripts/lumos:9503-9508` 手動記帳同樣只看 `known`(審查帳裡存不存在這個編號),不看有沒有收斂,所以人工記帳也一樣能記到已被重寫的舊編號。
於是:舊迴圈編號有審查帳列(不是「無佐證」)、有明確的 sha/defect_ref(不是「歸因不明」)、站名認得(不是「站名不認得」)——但因為它在分母判準裡被排除(沒有 converged 記錄),这些逃逸列會直接消失,不進任何一個 spec 承諾要另列筆數的桶。「誠實界線」段落只提到「歸因不明」與「站名不認得」兩種低估來源,沒提到這一種。

## F5 「分級 × 範圍類」若照字面做成兩維度的全交叉表,放行數為 0 的格子會讓率的計算除以零
severity: major
blocking: 是,若實作者依循 "×" 的常見數學記法把類別做成「所有觀察到的分級」×「所有觀察到的範圍類」的完整交叉表,某些分級/範圍類組合可能一個放行迴圈都沒有(分母 0),沒有任何一條 S 條款或輸出規則說要怎麼處理分母是 0 的格子,literal 實作會拋 ZeroDivisionError 或印出無意義的 NaN/inf。
引句:「類別**:分級 × 範圍類。」
file: `scripts/lumos:8925-8974` 對照既有同形狀指令 `cmd_loop_canary_stats`(spec §PRIOR-ART 指名沿用它的「一本帳一支統計子指令」形狀):它的分組是用 `OrderedDict` 邊讀邊 `setdefault`,只會產生「實際出現過的」(loop, auditor) 組合,不會做交叉表——這支既有程式碼本身沒有交叉表的先例,但 spec 文字用的是「×」而不是「觀察到的組合」,兩者字面不同,實作者若照 spec 字面而非照著去讀 `cmd_loop_canary_stats` 的程式碼寫法,就會落入交叉表陷阱。
S8 條款只講「放行數少於 20」要標「樣本太少」,語意上假設分母至少是某個正數,完全沒有涵蓋「分母為 0」這個更基礎的邊界(0 < 20 但 0 需要的是「這格不存在/無資料」而不是「樣本太少不下結論」——率算不出來,不是率不可信)。

## F6(minor) 「代碼審自動記的歸 design」這條讀側推斷規則沒有指定要檢查哪個欄位,舊列與新列可能推出不同答案
severity: minor
blocking: 否,不會做出錯的系統行為,只是同一支推斷函式要怎麼寫還缺一句話,實作時測試一寫就會暴露,不會留到上線後才發現。
引句:「代碼審自動記的歸 `design`(對不到設計審帳就是 `plan`);編號以 `code-` 開頭的是 `code`;其他在審查帳裡的是 `design`,不在的是 `plan`。」
file: `scripts/lumos:9363-9366` 自動記的逃逸列有 `auto: True`、`source: "code-loop"`(代碼審自動記時)兩個欄位可用,`stage` 也剛好等於 `"code-loop"`。
file: `scripts/lumos:9511-9519` 但手動記帳(`cmd_loop_escape` 一般路徑)完全可以讓人類自己打 `--stage code-loop`,寫出來的列沒有 `auto`/`source` 欄位。
spec 「代碼審自動記的歸 design」這句話沒有講清楚推斷函式要憑哪個欄位判斷「這是代碼審自動記的」——是 `source == "code-loop"`、`auto is True`,還是只看 `stage == "code-loop"`(那手動打的列也會撞進同一規則,雖然這裡巧合地兩種判法對這一類列的結果一樣都是 design,但下次改欄位語意時没有明文依據)。§一第二點「舊列沒有這欄:讀的一側用同一條規則推,推法寫成一支函式」也只重申要寫成函式,沒有多講判準用哪個欄位。

已看,無:
- 撤回同一個 token 兩次:兩筆撤回紀錄理由上都留在帳上、可查,`_escape_rows_for` 按 spec 的過濾邏輯是「有任一筆撤回紀錄指向它就濾掉」,不會因為撤兩次而產生額外的計算錯誤(對統計數字沒有影響,只是稽核時會看到兩筆撤回紀錄),沒有找到具體會壞掉的行為,不標。
- 「計劃檔被搬到 Archive」:查過 `scripts/lumos`,目前只有 `cmd_archive`(`scripts/lumos:15454`)會自動歸檔,且只動 `Verification/Archive/`,沒有任何機制會自動搬動 `Projects/` 底下的計劃筆記;`_plan_for_loop`(`scripts/lumos:9293-9298`)找不到計劃檔時的後果已經是 spec §四第二點「範圍類…沒有就『未分類』」的既定退化路徑,行為一致,不是新洞。
- 「同一 sha 在同一迴圈記兩站」:分子是「迴圈」為單位的二元判斷(§四第一點「分母裡,至少有一列有效逃逸…的迴圈數」),同一迴圈不論記幾站幾列都只算一次,不會因為多站而重複計數或漏算,查過去重鍵是 `(loop, stage, sha)`(`scripts/lumos:9344-9345`),不同站天生就是不同鍵,各自照該站的「下一站接住/漏網」規則判,邏輯上不衝突。
- 「同一個迴圈同時有設計審與代碼審帳」:查過 `scripts/lumos:8005-8011`,代碼審自動記逃逸時特地把 `loop` 欄寫成去掉 `code-` 前綴後的計劃名(歸給設計審迴圈),這是 spec 明講的既有行為(§WHY 段落),`loop_kind` 推斷規則第一條「代碼審自動記的歸 design」正是為了承接這個既有行為,兩個迴圈(裸名/`code-`前綴名)在分母裡本來就是各自獨立的兩個「迴圈」,不會互相污染對方的分母或分子。
- 「消費專案(沒有這些歷史帳)第一次跑」:escape-stats 的類別是由「放行迴圈」的實際分級/範圍類組合出來的(§四第三點),三本帳(逃逸帳、審查帳、治理帳)全空時,denominator 集合是空集合,類別枚舉自然是空的,輸出只會印末尾「全體的無佐證、歸因不明、站名不認得各幾列」(全部為 0),沒有發現字面實作會拋錯或印出誤導數字的路徑。

最嚴重 severity:major;blocking 共 5 條(F1、F2、F3、F4、F5)。
