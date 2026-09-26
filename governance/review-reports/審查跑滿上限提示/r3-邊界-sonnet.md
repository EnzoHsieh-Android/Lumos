severity: blocker

## F1 分級沒定錨時,`_TIER_PARAMS[分級]` 字面實作會直接 KeyError 炸整支指令
severity: blocker
blocking: 是(不是漏印那麼輕——照字面實作會讓 `loop next` 或 `--disposal` 對這些迴圈直接丟未接例外,連原本的判定輸出都印不出來,不是「只印不擋」而是「整支指令壞掉」)
引句:「分級取 `_loop_anchor_tier`;loop next 與處置閘都查這一張表,不另寫」
file: `scripts/lumos:9801` — `_TIER_PARAMS = {"light": (1, 2), "standard": (3, 3), "high": (5, 3), "legacy": (1, 6)}`,沒有 `None` 這個鍵。
file: `scripts/lumos:7905-7908` — `_loop_anchor_tier` 定義:「帳上第一筆帶 tier 的值」,找不到就回 `None`。
file: `scripts/lumos:7514` `cmd_canary` 的 `--tier` 是選配(第 116-121 行 `if tier is not None:` 才寫入 `rec["tier"]`),不是每筆都要帶。
敘述:實際跑一次帳本統計,2026-08-26(含)之後開的、有輪次記錄(panel 格式)的迴圈裡,有 22 個從沒記過 tier,例如 `severity-scan`(ts=2026-08-26,round r1/r2/r3,8 筆記錄全部 `tier=None`)、`design-contract-gate-timing`、`entry-latch` 都是非 code 前綴的 panel 迴圈,不受 S9 的「代碼審循序單審」排除。對這些迴圈,`_loop_anchor_tier(rounds)` 回 `None`,若照計劃字面「分級取 `_loop_anchor_tier`」直接 `_TIER_PARAMS[None]`,Python 會拋 `KeyError: None`。更嚴重的是:處置閘(`--disposal`)本來就不吃 `--tier` 參數(`lumos loop status --help` 印出的選項沒有 `--tier`),不像 `cmd_loop_next`(`scripts/lumos:10336` 起)那樣在 `_loop_anchor_tier` 為 `None` 時還有 `eff_tier = anchor or tier` 再退到 `"standard" if panel_fmt else "legacy"` 的既有回退邏輯(`scripts/lumos:10372,10393-10397`)可以借。計劃全文沒有交代處置閘這一側在未定錨時要怎麼查表,是可執行性缺口,不是措辭問題。

## F2 「代碼審循序單審排除」講的判法達不到它自己宣告的排除範圍
severity: major
blocking: 是(照字面實作,round-less 的代碼審循序迴圈只要開在 2026-08-26 之後就會被印,直接違反 S9 的排除承諾)
引句:「代碼審循序單審(沒有輪次記帳)、2026-08-26 以前的舊迴圈」
引句:「判法直接呼叫 `_panel_retired_for`」
file: `scripts/lumos:8197-8208` — `_panel_retired_for` 只比對 `rounds[0]` 的 ts 日期,完全不看帳列是否帶 `round` 欄、是否為 panel 格式;它的職責是「這個編號歸不歸新制處置閘管」,不是「這是不是單人循序審」。
file: `scripts/lumos:10402` — 判斷是不是代碼審循序單審的既有邏輯是 `seq = (eff_tier == "standard" and _roster_kind(loop_id) == "code" and not panel_fmt)`,要同時看 tier、roster 種類與 panel_fmt 三個條件,`_panel_retired_for` 一個都沒覆蓋到。
敘述:目前帳本裡還沒有「2026-08-26 之後開、round-less、code 前綴」的活生生案例(查過,0 筆),但機制仍在使用中——程式碼裡明寫「code 的 standard 走單 reviewer 循序」是設計行為(`scripts/lumos:10400-10402` 的註解),而且 `install.sh/get.sh` 那類移植型 code 循序審(`code-slim-python`/`code-slim-handoff`,雖然是 2026-07-31~08-01 的舊例)證明這個格式真的會被開出來。如果照計劃寫的「判法直接呼叫 `_panel_retired_for`」去實作排除條件,下一個開在 0826 之後的 code 循序迴圈就會被誤印這段,跟 S9 直接衝突。計劃這一句判法本身就是錯的依據,不是漏寫,得換成 `panel_fmt`(或等價的「有沒有 round 欄」)判斷。

## F3 處置閘有多條「判定之前」就 return 2 的早退路徑,S2「判定之後印,不論過關與否」沒交代這些路徑
severity: major
blocking: 是(這些早退路徑之一——同輪兩筆彙總帳——正是 LENS 指定要驗的邊界案例,字面實作要嘛在這些路徑漏印跑滿提示,要嘛得在 4、5 個不同 return 點各自補插,任何一種都跟 S2 的「不論過關與否」對不上)
引句:「處置閘應在判定之後印同一段,不論過關與否,且過關判定與退出碼不變」
file: `scripts/lumos:18341-18350` — 一輪內若有 2 筆以上帶 `findings_set` 的彙總帳(同輪兩筆彙總),`_loop_status_disposal` 直接印「擋下:第 … 輪有 … 筆記錄都帶了處置結果」並 `return 2`,這個 return 點在函式最前段(全部四合取判定之前),不會走到函式尾端 PASS/FAIL 的橫幅那兩行(18574-18582)。
file: `scripts/lumos:18320-18325` — round-less 帳列卻帶 `findings_set`,同樣在判定核心之前 `return 2`。
file: `scripts/lumos:18326-18330` — `--spec` 指的檔讀不到,一樣提前 `return 2`。
file: `scripts/lumos:18556-18557`、`scripts/lumos:18567-18568` — 條款綁定 `_cl == "abort"`、落點 `_ld == "abort"` 也各自提前 `return 2`。
敘述:計劃「一、什麼時候印」只講「處置閘:判定印完之後加這一段,不論過或沒過」,把「過/沒過」當成唯一的二元狀態(對應 `return 0`/`return 1`),但現有函式其實有五個不同的 `return 2` 提前出口,發生在計算「判定」之前。若這一輪剛好輪數已到上限、又剛好撞上「同輪兩筆彙總」這種輸入(LENS 指定的邊界案例),字面上跟著計劃走的實作找不到該在哪裡印——插在函式最尾端(現有 PASS/FAIL 之後)就漏掉這五種 rc=2 路徑;要涵蓋就得在五個 return 點各自加一段判斷,計劃完全沒提這件事,也沒說這五種算不算「不論過關與否」裡的一種。

## F4 「最後一輪對前一輪」沒定義成什麼順序,帳上真的有跳號輪次會讓字面實作找錯「前一輪」
severity: major
blocking: 是(帳上round-id 不保證連號,若實作依round數字字面取「N-1輪」去查,會查到不存在或查到錯的一輪,印出跟真實走勢不符的提示)
引句:「若最後一輪折入數大於或等於前一輪,則提示應是換做法」
file: `scripts/lumos:18293-18310` — 處置閘認定「最後一輪」的既有作法是 `groups`(`OrderedDict`)最後一個插入的鍵(`rid, latest = next(reversed(groups.items()))`,18314),鍵是任意字串 round-id,不是照數字排序;「前一輪」若要沿用同一套語意應該是 `groups` 裡倒數第二個插入的鍵,不是把目前輪的數字減一。
file: `docs/.canary-log.jsonl` — `lint-new-gate` 這個編號(2026-09-13 開、tier=standard、在 2026-08-26 之後、屬於 panel 格式,不在 S9 排除範圍內)的 round-id 序列是 `r1, r3`,中間沒有 r2(`grep '"loop": "lint-new-gate"' docs/.canary-log.jsonl` 可查到 6 筆,round 只出現 r1 與 r3 兩種值)。standard 分級上限是 3(`_TIER_PARAMS["standard"] = (3, 3)`),若照「帳上已記的輪數」取 round 最大數字視為輪數,這個編號在只有 2 個相異輪次時就會被誤判成「已到上限第 3 輪」;若實作反過來想找「前一輪」用 `int(當前round去掉r前綴) - 1` 組字串去查 `groups`,對 `r3` 會去找 `r2`,查無此鍵,程式要嘛拿不到「前一輪」資料要嘛用錯的鍵撞到 `KeyError`。
敘述:計劃全文沒有一句話講「最後一輪」「前一輪」是按 round-id 的插入順序取,還是按 round 數字大小取;既有函式(`_loop_status_disposal`)採用前者,但計劃自己描述「帳上已記的輪數」時([[做法一之首段]])講的是跟分級上限比較的「輪數」,容易被讀成「round 數字」。兩種讀法在帳有跳號時會給出不同結果,而跳號在真實帳本裡已經發生過,不是純假設。

已看,無:
- `loop next` 的插入點驗過沒問題——全部正常階段(`escalate`/`plant-canary`/`gate-pending`/`converged`/`cap-reached`)最終都收斂到同一個 `emit()` 函式(`scripts/lumos:10419` 起),文字與 JSON 輸出各自只有一個出口(`scripts/lumos:10563-10624`),所有提前 `return 2` 的擋下路徑(`--orchestrator` 不合法、tier 中途換掉、格式不一致等)都不經過 `emit()`——計劃「只要正常印出結果就加在末尾、被擋下的不印」這句話對 `loop next` 這一側是可以照字面在 `emit()` 尾端(10624 行的 `return` 之前)插一處搞定,沒有可執行性缛口。
- 處置閘的唯讀呼叫點驗過:三個呼叫 `_loop_status_disposal` 的地方(`--freeze` 兩次,`scripts/lumos:634,648`;golden replay 一次,`scripts/lumos:796`)全部帶 `readonly=True`,和既有 `if not readonly:` 慣例(18534、18541 行)一致,S3「新段落自己包一層唯讀判斷」照現有模式接得上,沒發現漏掉的唯讀呼叫點。
- 「帳首剛好在退役日」這個邊界驗過沒問題:`_panel_retired_for`(`scripts/lumos:8203,8208`)用 `ts[:10] >= cutoff`,`cutoff` 預設 `"2026-08-26"`,跟計劃「2026-08-26(含)之後」用的閉區間一致,沒有差一天的問題。
- 「只有彙總沒有各席」這個形狀查過:`_review_yield_round`(`scripts/lumos:7364`)對只有一筆 carrier 列的輪,N/M/R/F/A 都能正常算,沒有除以零或空集合取值的錯誤路徑。

實務隱患逐類:
- 併發:計劃自己講只讀帳本、不另開讀寫路徑;上面四條 finding 都是「讀了但算錯/炸掉」的正確性/可執行性問題,不涉及併發競態,故此類「無」。
- 效能:新增呼叫都是對單一編號的既有輪次資料跑,量級跟現有 `_review_yield_round` 呼叫一致,無新增大量迴圈或 I/O,判「無」。
- 金流/對外送出/不可逆:計劃自己已排除且合理(純讀本機帳本、不寫帳、不呼叫外部服務),上面查證沒有推翻這幾點,判「無」。
- 守衛面:這正是本次審查主軸——F1/F3 兩條如果照字面實作,不是「多印一段沒用的話」,而是可能讓處置閘/loop next 對特定既有迴圈直接丟例外或漏印,等於在「只印不擋」的承諾之外意外改變了工具的可用性,已在上面兩條列出。

最嚴重 severity: blocker;blocking 共 4 條。
