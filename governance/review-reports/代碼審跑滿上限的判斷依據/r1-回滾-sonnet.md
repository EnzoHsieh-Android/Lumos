severity: major

## F1 建議字串照 spec 字面實作,人類文字模式下八成看不到(印出來的建議被靜默吞掉)
severity: major
blocking: 是(不改就是白做:這個功能的唯一目的是「讓人裁的時候有依據」,而字面實作出來的結果是預設模式看不到那段依據,做出一個看起來上線、其實沒生效的系統)
引句:「輸出應在交給人的那句底下列出每輪折入數、修正引起的條數與同類重複狀態,並給出一個建議」
file: `scripts/lumos:10598-10600` — `cmd_loop_next` 的 `emit()` 在非 `--json` 模式下,是逐一白名單印出 `out` dict 的鍵:`for k in ("canary_type", "record_cmd", "scope_cap", "cluster_hint", "note"): if k in out: print(...)`。任何不在這五個鍵裡的新欄位,即使被塞進 `out`,在預設(文字)輸出裡完全不會出現,只有帶 `--json` 才印得出來(`scripts/lumos:10563-10564`)。
file: `scripts/lumos:10479-10489` — 這個坑這支檔已經踩過一次:`tier_hint` 這個鍵也是同樣手法塞進 `out`(`out["tier_hint"] = (...)`),但它從沒被列進上面那個白名單,全檔搜尋 `tier_hint` 只有這兩處賦值、沒有任何 `print` 讀它——現存的功能本身就已經是「只存在於 JSON 模式」的啞欄位。
敘述:spec 只說「印在『停下來交給人』底下」,沒有一句提到要同步改 `scripts/lumos:10598` 的白名單。按最自然的寫法(比照 `scope_cap`/`note` 那樣 `out["cap_report"] = "..."`),在日常編排者不帶 `--json` 呼叫 `lumos loop next <id>` 時,S1/S2/S3/S4/S8 這幾條要求的「建議」文字都印不出來——而 `loop status --disposal` 那條路徑(`_loop_status_disposal`)是逐行直接 `print`,沒有這個白名單,兩處印法不對稱,implementer 很容易照抄 `loop next` 現有寫法(`out[key]=...`)而漏掉這一步,且不會有任何測試以外的訊號提醒(功能「有跑」,JSON 模式看得到,rc 也不變,唯獨人類預設看不到)。
重現:`grep -n 'tier_hint' scripts/lumos` 只有賦值兩處、無 print;對照 `python3 scripts/lumos loop next <帶 tier_hint 的舊帳編號>`(不加 `--json`)不會印出任何 tier_hint 相關字樣,`--json` 才看得到——同一個坑會在新欄位上重演。

## F2 新旗標 `--finding-class` 跟既有 `--finding-kind` 同形狀、近名,spec 沒指定要不要併入既有的「跟 --findings-set 一起給」防呆,也沒說寫進帳的鍵名
severity: minor
blocking: 否(不影響閘的判定與 rc,壞的是提示訊息精準度與資料乾淨度,不會讓實作者做出「錯的行為」,只是資料品質/UX 缺口)
引句:「記帳新增選填旗標 `--finding-class <id>=<短名>`」
file: `scripts/lumos:7514` — `cmd_canary` 簽名已有一個語意鄰近、格式相同的既有欄位 `finding_kinds`(`--finding-kind id=code|spec|process`,封閉列舉、要求對「findings 全集」逐條標,見 `scripts/lumos:7744-7758`),被 `gov --stats` 拿去算「process 自產工作量」百分比(`scripts/lumos:6663-6672`,`if v in fk: fk[v] += 1`)。
file: `scripts/lumos:7659-7661` — 現有的「哪些選填旗標一定要跟 --findings-set 一起給」防呆清單,是寫死在錯誤訊息裡的旗標名稱字串(`"--folded-set/--accepted-set/--accept-reason/--refute-verdict/--finding-kind 要跟 --findings-set 一起給"`),spec 沒提到 `--finding-class` 要不要併進這個 tuple/訊息;沒併的話,單獨給 `--finding-class` 不給 `--findings-set` 這種輸入沒有防呆,行為未定義。
敘述:這不是不能做,是 spec 沒把「這個新欄位在帳裡叫什麼鍵、要不要比照 finding_kinds 的『全集覆蓋』要求、要不要進同一組防呆訊息」寫清楚——三個問題留給實作者自己決定,若隨手取名撞到 `finding_kinds` 這個既有鍵,`gov --stats` 的既有百分比統計(現有下游讀帳處)會因為自由文字值(如「靜默回空」)混進只認 code/spec/process 三個值的計數器而被靜默忽略、不會報錯,但也不會反映真正加進去的資料(不是崩潰,是悄悄失真)。

已看,無:
- 「只印不擋、不改任何閘的判定」這個核心誠實界線,在架構上站得住——`cmd_loop_next` 的 rc 只由 `phase` 決定(`scripts/lumos:10627`:`return 0 if phase == "converged" else 1`,不看 `out` 裡任何其他鍵);`_loop_status_disposal` 的 rc 只由 `fails` 清單長度決定(`scripts/lumos:18580` 附近 `if fails: ... return 1`),而現有的「觀測不進合取」段落(canary 觀測、roster_tail、severity_tail、審查有沒有用漏斗,見 `scripts/lumos:18466-18540`)都是同樣的「只印不 append 進 fails」寫法,是這支檔已經驗證過很多次的既有模式——只要新報告函式照抄同一個寫法(印完不碰 `fails`/不動 `phase` 判斷),S6/S9「不改判定與退出碼」的宣稱是可信的。
- 「附理由放行」建議不會被拿去繞過既有硬規則——code 迴圈(`loop_id` 以 `code-` 開頭)只要該輪任一席 severity 是 major/blocker,`accepted_set` 必須為空的鐵則已經寫死在 `_loop_status_disposal`(`scripts/lumos:18389`:「★code 迴圈輪內有 major 以上的席,accepted 必須為空…不得附理由放行★」),這是獨立於這份計劃的既有合取項;就算建議算錯、或有人誤把它當指令照做去 `--accepted-set` 一條 major,閘本身仍會擋下、rc 仍是 1,不會因為這份計劃新增的印字而被放行——「建議造成傷害」這條路徑在目前程式碼結構下被既有硬規則接住了。
- 選填新欄位寫進 `docs/.canary-log.jsonl` 對舊讀法無害這件事,不是空話——這支檔到處是同一個「不給不寫鍵,讀側 `.get()` 帶預設」的慣例(`outcome`/`usd`/`finding_kinds`/`clusters` 都是這樣加的),沒有任何我看到的讀帳處對未知鍵做嚴格 schema 擋(doctor 巡檢的是圖譜筆記,不驗 canary-log 的欄位形狀),所以「回退拔掉呼叫、舊欄位留著無害」這句誠實界線本身是站得住的——前提是新欄位鍵名不要撞到既有鍵(見 F2)。
- `loop replay --freeze` 對同一個 loop 會呼叫 `_loop_status_disposal` 兩次(`scripts/lumos:634` 與 `648`,一次讀活檔算 G3、一次用凍結 sha 覆算),plan 描述的報告函式「只讀帳、不寫帳」——純讀函式重複呼叫兩次不會有副作用或狀態污染,效能上也只在跑滿/熔斷條件成立時才算,一次 freeze 頂多多算兩次,不是熱路徑常態負擔,這件事 plan 沒提但也不構成問題。

最嚴重 severity: major;blocking 共 1 條。
