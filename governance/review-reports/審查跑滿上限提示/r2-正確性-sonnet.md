severity: major

## F1 quote-check 失敗不在「處置以外」白名單裡,走勢分支會判錯
severity: major
blocking: 是——照 spec 字面實作,quote-check 失敗的狀態會被誤判成「處置」內問題而去看走勢,結果印出「可考慮附理由放行」或「由人裁」而不是「先修這些」,建議內容跟真實情況相反。

引句:「留痕、條款綁定、落點、資安席、材料被改過」

計劃第二節第 1 點把「處置以外」明列成留痕/條款綁定/落點/資安席/材料被改過(=G3 hash)五類,只要 fails 裡出現這五類之一就一律「先修這些,不看走勢」。但實際處置閘 `_loop_status_disposal` 的 `fails` 詞彙表裡還有一個第六類 `"quote"`(quote-check 引句錨定失敗),spec 的白名單完全沒提到它:

file: `scripts/lumos:18468-18471` quote-check 沒錨到時 `fails.append("quote")`(在 G3/處置集合/留痕/條款綁定/資安席/落點之外,獨立一個類別)。

具體壞狀態:第 3 輪(已到 standard/high 的 cap=3)disposal 只有 `fails=["quote"]`(某席報告有一句引不回凍結快照,其餘六步全過),且前兩輪折入數遞減、最後一輪最高嚴重度是 minor。若實作者照字面判斷「fails 裡有沒有處置以外的類別」,`quote` 不在列舉的五類任何一類裡,會被當成「fails 裡只有處置類」,於是往下走趨勢分支([S6])印「可考慮附理由放行」——但 quote-check 失敗代表審查證據本身錨不到審材,跟留痕缺席是同一等級的問題(processo 閘七步合取裡兩者相鄰,都是「證據有沒有效」而不是「有沒有處置好」),照樣不看走勢直接說先修才對。

## F2 計劃指名重用的「處置閘尾」既有算式,對 code- 開頭的多席迴圈整批算不出折入數
severity: major
blocking: 是——如果實作者依 spec 指示直接接到那個既有呼叫點,114 個目前在案的 code- 前綴多席迴圈(範圍內、未被 S10 排除)在跑滿時全部拿不到折入數與走勢,advice 會全部落到「判不了,自己看」,S5/S6/S12 的分流形同虛設。

引句:「處置閘尾與 `gov --stats` 已經在用」

PRIOR-ART 段落指名沿用「處置閘尾」這個既有呼叫點來算折入數(而不是另寫第二份)。但處置閘尾實際呼叫 `_review_yield_round` 的那段被一個條件包住:

file: `scripts/lumos:18541` `if not readonly and not str(loop_id).startswith("code"):`(intake 觀測與「審查有沒有用記帳」的 `_review_yield_round(latest)` 呼叫都在這個 `if` 區塊內,見 `scripts/lumos:18550`)——凡是 `loop_id` 以 `code` 開頭,這整段(含折入數計算)完全不執行、不印。

計劃的適用範圍只排除「代碼審循序單審」(`seq` 變數,單人循序),沒有排除多席、有 round 記錄的 code 迴圈——這種迴圈的 `loop_id` 慣例上也是 `code-` 開頭(如 r1-intake.md 重現用的 `code-記憶索引大小守衛`)。實測本庫:

```
lp.startswith('code-') and 'round' in d 且首筆 ts >= 2026-08-26 的迴圈有 114 個
```

(用 `docs/.canary-log.jsonl` 逐行 `json.loads` 分組統計得出,方法:同一 `loop` 欄首筆 `ts` ≥ cutoff 且至少一筆帶 `round` 鍵。)這些迴圈全部在計劃範圍內,若照 PRIOR-ART 指的「處置閘尾」原地擴充,折入數這個關鍵輸入對它們永遠是空/None,advice 只會落在「有任何一輪沒記處置 → 判不了,自己看」這一支,S5(換做法)/S6(可放行)/S12(由人裁)三條規則對這 114 個現有迴圈完全用不到。

(對照:`gov --stats` 那處呼叫 `_review_yield_round` 沒有這個 code 前綴排除——`scripts/lumos:6721-6725` 用 `(loop, round)` 分組、不看 loop_id 字首。spec 把兩個行為不同的既有呼叫點並列成「已經在用」的同一種東西,沒有指出這個落差,是真正的缺口所在。)

## F3 熔斷累計(S8)與「沒記處置」(F=None)的輪同時出現時,累加會炸或算錯,spec 沒定義
severity: major
blocking: 是——`sum()` 對 `None` 直接相加會丟 `TypeError`,若字面翻譯成「把每輪折入數加總」,遇到這個帳本狀態會讓 `loop status --disposal` 本身崩潰(而不是優雅印「判不了」),比顯示錯誤建議更糟。

引句:「當同一個審查編號各輪折入累計超過 20 條,處置閘輸出應印建議拆小改動,且不改變過關判定與退出碼」

計劃把「二、跑滿時的走勢判斷」與「三、提早熔斷」明寫成兩段獨立規則(「熔斷提示跟上面第二節獨立」)。二.4 用「有任何一輪『沒記處置』」這句話涵蓋了 `_review_yield_round` 回傳 `F=None` 的情形(有人報了條數卻沒彙總帳),並在 advice 分支裡先短路成「判不了」。但三的熔斷判準——「各輪『折』欄累計超過 20」——是獨立的另一套邏輯,沒有重複二.4 那條「遇到 None 就短路」的處理:

file: `scripts/lumos:7381` `F = len(carrier.get("folded_set") or []) if carrier else None`(carrier 缺席時 F 直接是 Python `None`,不是 `0`)

具體壞狀態:三輪帳,第 1 輪 F=18(有彙總帳)、第 2 輪 F=None(某席報了 5 條但沒人記彙總帳)、第 3 輪 F=3。熔斷要判「累計超過 20」,若照字面對 `[18, None, 3]` 做 `sum()`,Python 會直接拋 `TypeError: unsupported operand type(s) for +: 'int' and 'NoneType'`——這會讓整條 `loop status --disposal` 指令在跑滿判斷這一步當場中斷,而不是照 S9「不改變過關判定與退出碼」的承諾優雅印出訊息。spec 沒有講「累加時 None 當 0 算,還是整段回『判不了』,還是排除該輪」,三種選擇的結果都不一樣,是可執行性缺口。

## 實務隱患逐類作答

- **併發**:計劃自陳「報告函式只讀帳本;處置閘讀帳的方式與壞行擋法照舊」——查證屬實,`_loop_status_disposal` 全程只做 `Path.read_text`,沒有寫入(除 roster/severity 尾端既有的 `roster-alerts.log` 追加,那是既有行為不是本案新增)。無新增風險。
- **效能**:`loop next` 改問處置閘後會多跑 `_loop_status_disposal` 全部七步(含 quote-check、資安席、落點檢查),比舊路徑委派 `_loop_status_panel`(現在直接被 `_panel_retired_for` 擋下 rc2、幾乎零工作量)重得多——但這本來就是「修出口」這件事的必然代價,不是本案新增,計劃已在誠實界線外的段落承認過(舊編號 r1 併發席量過單次百毫秒級)。查證:沒有新的複雜度來源。
- **不可逆**:計劃自己承認 cap-reached 記號寫得出來、撤不掉,回退段落也講了處置辦法(換編號/`loop rewrite`/治理帳另記更正)。查證屬實,`_loop_gov_mark` 一律是 append-only 寫入(`scripts/lumos` 治理帳寫側同一支函式),沒有找到反例。
- **資安**:計劃只印文字、不觸碰任何外部輸入以外的資料源,loop_id 已有既有的 `shlex.quote` 防注入(見 `scripts/lumos:10456` 附近),本案新增的印出內容(fail_steps/rounds/advice)全部來自帳本既有欄位,沒有新的使用者可控字串被直接拼進指令或檔案路徑。無新增風險。
- **資料完整性**(額外一類,計劃「已排除」清單沒提但跟這次改動直接相關):F1/F2/F3 三條指出的都是這一類——折入數與失敗原因的計算,在特定帳本形狀下(quote-check 失敗、code 前綴多席迴圈、None 折入數混入累加)會給出跟真實情況相反或直接崩潰的結果。這類風險計劃完全沒有預先排除或討論,是本次審查的主要收穫。

已看,無:適用範圍段落(只改 2026-08-26 後多席迴圈、排除 light/代碼審循序單審/舊迴圈)用 `_panel_retired_for`/`seq` 變數對照程式碼查證過,邊界劃分本身沒有問題(F2 指出的是計劃「引用的既有呼叫點」本身在這個邊界內部又切出了一個計劃沒發現的子邊界,不是範圍劃錯);「少了 --spec 排在跑滿之前」與 `_loop_status_disposal` 用 `result_out` 回傳結構化 `fails`/`rid` 的機制已存在(`scripts/lumos:18571-18573`),計劃打算重用它是可行的,沒有發現字面不可行之處;lands_in 指到的 `Systems/loop-convergence-recording` 節點內容(14 行 KEY、12 條 decisions)沒有任何一條跟本案的「只印不改判定」方向衝突,d4(2026-09-07,loop next 印審查材料的裁定)反而是同方向的先例,寫進這篇不會破壞既有宣稱;回退段落裡「收斂記號只由處置閘寫」這句話跟現在的程式碼一致(`_loop_status_panel`/`cmd_loop_next` 各自呼叫 `_loop_gov_mark` 寫 converged 的邏輯只有一處會重複——本案要拿掉的正是 `cmd_loop_next` 自己 emit converged 前那次 `_loop_gov_mark(env, loop_id, "converged", ...)`,查證 `scripts/lumos:10672-10674` 確實存在這個重複點,計劃要拔掉它是對的);S9 提到「回放與凍結時不得印」,查證 `_loop_status_disposal` 已有 `readonly` 參數可用來擋掉新增的尾端印出,機制存在。

最嚴重 severity: major;blocking 共 3 條。
