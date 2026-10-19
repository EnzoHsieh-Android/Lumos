severity: major

審查對象:`記帳與迴圈工具小修_計劃` 的 r1 凍結審材。鏡頭:正確性/邏輯。我對照了工作樹 `web-ledger` 的 `scripts/lumos`、審查帳 `docs/.canary-log.jsonl`、`governance/review-reports/*/r*-dispatch.json` 和兩份 SKILL。

**已讀無 finding**:
- §2(集合旗標認 `none`)
- §4(證據型別訊息)
- §5(留痕提醒)
- §6(pitfalls 分級印席位)
- §9(設計審首輪順序提示)
- spec 引用的既有成員都存在,包括 `_panel_retired_for`、`_patch_file_changes`、`_loop_anchor_tier`、`_REQUIREMENT_LABEL`、`t_seq_code_std_anchor`、`_seq_rec`。
- `("code","standard")` 的 `mode` 標籤改名沒有任何程式讀它,安全。

## 1. light 帶 `--round` 一律擋,會誤擋手冊自己教的記帳寫法
- 位置:§1 `canary record` 寫側的「light 而帶了 `--round` → rc2」,對應 S8。
- 問題:`skills/lumos-code-loop/SKILL.md` 步驟 6 的記帳範例對所有分級都帶 `--round rN`。spec 只改了 standard 的描述、步驟 6 不動,也沒給 light 的例外。審查帳上 9 個 `tier=light` 的代碼審迴圈第一筆帶了 `--round`,其中 6 個是 2026-10-07 之後的:`code-測試子程序不上色`、`code-rtb第三輪提案現況`、`code-test-quality-handbook-flake`、`code-cc292筆記`、`code-會談編號實測筆記`、`code-readme-manual-push`。
- 具體例:`canary record none --loop code-X --tier light --round r1 …` 照手冊範例寫。
  - 現況:寫進帳。light 不查收斂閘,所以沒壞。
  - 照 spec:rc2、不寫帳,而且 spec 說不提供跳過旗標。
- 誤擋面的盲點:〈實務隱患〉只列結局帳與舊循序迴圈,沒列 light。RETIRE-IF 的「合法流程被誤擋 ≥2 次就撤回」幾乎一定會被觸發。
- 要做的決定:要嘛 light 也改成帶輪次,要嘛把手冊步驟 6 對 light 講成不帶輪次。不能只擋。
引句:「誤擋面最可能在結局帳與舊循序迴圈,兩者都有條款釘住」
- 佐證:file: `skills/lumos-code-loop/SKILL.md` 步驟 6 範例帶 `--round rN`。file: `scripts/lumos:16392` 的 `loop next` light 守衛只在帳上已有記錄時才擋,不是寫帳時擋。
severity: major
- blocking: 是(照字面實作會擋掉手冊教的合法記帳,並讓 RETIRE-IF 立刻達標)

## 2. 拆包核對用 `auditor` 欄找席位,真實派工單裡這欄不唯一
- 位置:§7「找 `auditor` 跟這筆 `--auditor` 完全相同的那席」,對應 S19。
- 問題:真實派工單的 `seats[].auditor` 常常是模型名,不是席名。
  - 我數了 826 份有 `seats` 的 `rN-dispatch.json`,其中 276 份(約 33%)有重複的 `auditor` 值。
  - 這份審材自己的 `r1-dispatch.json` 六席 `auditor` 全是 `sonnet`,席名在 `seat` 欄。
  - 另有 329 份 `seats[]` 完全沒有 `materials`,材料在頂層。
  - 帳上 `--auditor` 與派工單 `auditor` 能對上的只有 2098 對,對不上的有 1352 對。
- 具體例:一份六席派工單 `auditor` 全是 `sonnet`,各席 `materials` 不同(拆包審)。第三席記帳寫 `--auditor sonnet --snapshot <第三包>`。spec 沒定義多個同名席取誰:取第一席就拿第一包的材料比對,「`--snapshot` 不在其中」成立,rc2 誤擋。
- 為什麼誤擋沒有出口:spec 說不提供跳過旗標,唯一出路是改派工單,而派工單屬於已凍結的卷證。
- 要補的規則:多個同名席時用 `seat` 欄比對;或同名多席時取聯集;或同名多席時一律跳過不擋。
引句:「派工單裡同名席的 materials 不含這筆的」
- 佐證:file: `scripts/lumos:28802` 的 `cmd_seat_check` 只讀頂層 `materials`/`seat`/`lens`,不讀 `seats[]`,所以 spec 說的「seat-check 既有讀法」只涵蓋單席形狀。
severity: major
- blocking: 是(多席同名時規則沒定義,實作者必須自己猜取哪一席,猜錯就誤擋)

## 3. 「共用同一次讀帳」做不到,讀帳壞掉時的行為也沒說
- 位置:§1「跟它共用同一次 `_loop_records_checked` 讀帳,不多讀一次」。
- 問題:既有「載體最後記」那段的讀帳被 `if loop and round_id and outcome is None:` 包住。要擋的毒害情境正是這筆沒帶 `--round`(S5、S7、S9),這時那段根本不會讀帳。實作者只能另讀一次。
- 具體例:照 spec 字面把新檢查掛進那段,S5 的測試(既有都帶輪次、這筆不帶)永遠走不到檢查,會是紅的。
- 另一個缺口:`_loop_records_checked` 帳壞時回 `([], 原因)`。spec 沒講這時怎麼辦。
  - 若照「零筆」處理,第二、三席會被誤當第一筆而被擋,訊息還講「第一筆」。
  - 若 fail-open,mixed 判斷就失效。
  - 現有載體段對 `finding_sources` 是 fail-closed,對其他情況放行。
引句:「寫側只多用既有那一次讀帳」
- 佐證:file: `scripts/lumos:11847-11870`。
severity: minor
- blocking: 否(實作者跑測試會發現,不會做出壞系統;但要先決定帳壞時 fail-closed 還是 fail-open)

## 4. 帳上沒定錨、這筆才宣告 `--tier` 時,毒害擋不住
- 位置:§1「有既有列時分級用帳上定錨(`_loop_anchor_tier`),沒定錨就只做 `mixed` 判斷」。
- 問題:分級只認帳上已有的定錨。沒定錨的舊迴圈(沒帶 tier 的舊帳)補進第一個 `--tier` 時,這筆自己就成為定錨,卻不檢查它的格式。
- 具體例:
  - 設計審 `foo`,既有 2 筆都沒帶 tier、也沒帶 round(帳上這類 `tier=None`、不帶輪次的設計審有 24 個)。新記一筆 `--tier standard` 不帶 `--round`。`mixed` 不成立,所以放行。
  - 結果:定錨成 standard 且全無輪次,`loop next` 對非 seq(設計審)直接擋「standard 規定每筆都要帶輪次」,和 spec 要防的毒害同形。
- 反向:既有全帶輪次且沒 tier,補一筆 `--tier light --round r2`,同樣放行,之後 `loop next` 擋 light 帶輪次。
- 要做的決定:有效分級要取「帳上定錨,否則取這筆的 `--tier`」。
- 佐證:file: `scripts/lumos:16386-16393`(`loop next` 的 tier 與格式一致性檢查)。
severity: minor
- blocking: 否(要先動手補 tier 到舊帳才會踩到,屬少見路徑)

## 5. 結局帳列被算進「既有列」,訊息會講錯
- 位置:§1「既有列加上這一筆,`_loop_round_format` 會變成 `mixed`」,加上 S10。
- 問題:結局帳(`--outcome`)沒有 `round`,也沒有 tier。它寫進後,同迴圈之後任何帶 `--round` 的一般記帳都會被判 `mixed`,擋下訊息「既有的 N 筆都帶輪次」就不對了。
- 具體例:
  - 一個全帶輪次的迴圈寫了結局帳 `converged`,再補記一筆 `--round r3`。
  - 擋下訊息說「既有的都帶輪次、這筆不帶」或反過來,其實是結局帳那一筆造成的。
  - 結局帳若是這個編號的第一筆(自主迴圈 `skipped`、`tier-blocked:*` 沒進過審查輪),之後同編號首次審查會被誤當「既有都不帶輪次」而擋。
- 要補的規則:`_loop_round_format` 的輸入要先濾掉帶 `outcome` 的列,與訊息的筆數一致。
- 佐證:file: `scripts/lumos:11719`(結局帳不得帶 `--round`),file: `scripts/lumos:16317`(`loop next` 的 `n_round` 數法不濾結局帳)。審查帳目前沒有任何 `outcome` 列,所以只是潛在風險。
severity: minor
- blocking: 否(目前沒有實例,自主迴圈寫結局帳是未來路徑)

## 6. §8 的提醒講得比實際擋的範圍大
- 位置:§8 hints 第二條「載體記了以後同輪不能再補」。
- 問題:PR #95 的「載體最後記」只在同輪已有帶 `--finding-source` 的載體時才擋。沒帶 `--finding-source` 的載體記完後,同輪補資安照樣能記。
- 具體例:提醒把「補資安只能記下一輪」說成無條件,實作者或編排者照字面會把可以補的席也推到下一輪,多花一輪額度;standard/high 已到上限時還要先 `cap-decision`。
- 要補的規則:文字限定成「帶 `--finding-source` 的載體」。
- 佐證:file: `scripts/lumos:11852`(判斷 `any(r.get("finding_sources") for r in _same)`)。
severity: minor
- blocking: 否(只是提醒措辭過寬,不影響判定)

## 7. 拆包超標的提醒順序自相矛盾
- 位置:§7 寫側拆包核對。
- 問題:`scope_oversize` 的提醒在 `cmd_canary` 較早處就印了(`scripts/lumos:11426-11431`),內容含「不擋你記錄」。§7 的 rc2 發生在更後面。
- 具體例:使用者先看到「不擋你記錄」,接著又被「擋下」。
- 要補的規則:被擋時不印前一段,或把提醒移到擋下判斷之後。
引句:「拆包核對只在超標時讀一份派工單」
- 佐證:file: `scripts/lumos:11426`。
severity: minor
- blocking: 否(訊息矛盾但結果清楚)

最嚴重 severity:major;blocking 共 2 條(#1、#2)。
