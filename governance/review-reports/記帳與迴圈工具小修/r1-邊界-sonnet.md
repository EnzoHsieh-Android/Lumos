severity: major

我對照 `scripts/lumos`(web-ledger 工作樹)、真帳 `docs/.canary-log.jsonl`(536 個迴圈)和 `governance/review-reports/*/r*-dispatch.json` 逐項查證。沒有寫任何檔案,也沒有開臨時目錄。

**F1 light 規則會讓 light 代碼審記不了處置帳**
severity: major
blocking: 是(照字面做,有發現的 light 代碼審沒有任何寫法能入帳)
- spec 段落:〈做法 1〉規則與寫側第 68 行 light 守衛、[S8]。
- 引句:「light 每筆都不帶。迴圈已經有的格式定死,寫進去會變成」
- 問題:處置帳(`--findings-set`)必須帶 `--round`,這道擋在 `cmd_canary`。新規則又規定 light 第一筆帶 `--round` 就 rc2。兩邊相撞,light 迴圈有發現時記不了載體。
- 具體例:真帳 14 個 light 代碼審迴圈裡有 9 個帶輪次,其中 10 筆帶 `findings_set`,最近的是 2026-10-07 的 `code-測試子程序不上色`、`code-rtb第三輪提案現況`。新規則上線後,同樣的流程第一筆帶 `--round` 被擋,不帶的話後面的處置帳又被擋(混用或必須綁輪次),整條路走不通。
- spec 的「真帳數字」只數了 standard,沒數 light。`loop next` 現在確實對 light 帶輪次 rc2,但寫側目前收,實際用法也存在。設計審 light 也有 3 個帶輪次的迴圈。
- 佐證:`scripts/lumos` 的 `cmd_canary` 有「處置帳(--findings-set)必須綁 --round 和 --auditor」,`cmd_loop_next` 有 light 帶輪次 rc2 的守衛。
- 要補的:spec 得先決定 light 有發現時走哪條路,再決定要不要擋 light 帶輪次。

**F2 拆包核對只用 `auditor` 比對席位,真帳大量用 `seat`,核對常常不會觸發**
severity: major
blocking: 是(F28 的修法在常見派工單形狀下形同虛設,[S19] 的測試能過、實務不生效)
- spec 段落:〈做法 7〉。
- 引句:「派工單有兩種既有形狀:多席形狀是」
- 問題:spec 只用 `auditor` 找席位,沒提 `seat`。真實派工單的 `seats[].auditor` 常是模型名(例如六席全是 `sonnet`),席名放在 `seat`,而帳上 `--auditor` 填的是席名(`邊界-sonnet`)。
- 具體例:本計劃自己的 `r1-dispatch.json` 是「頂層 `materials` + 六個 `seats`」,各席只有 `seat`、`lens`、`auditor:"sonnet"`,沒有各自的 `materials`。`--auditor 邊界-sonnet` 找不到任何席,照 spec 靜默不擋。
- 數字:465 筆 `scope_oversize` 裡,能讀到派工單的 445 筆中,有約 93 筆只能靠 `seat` 對上,對不上 `auditor`。
- 另一個缺口:spec 沒說「席有、但沒自帶 `materials`、頂層有 `materials`」怎麼辦。這種形狀有 376 個檔。
- 另一個缺口:單席形狀在固定檔名 `<輪次>-dispatch.json` 下,一輪只能容一席,裝不下多席。真帳只有 1 個檔是這種形狀。
- 要補的:席位比對的鍵(`seat` 與 `auditor` 兩者,以及兩者都命中時怎麼辦)和三種形狀的處理。

**F3 `--snapshot` 與 `materials` 路徑形式不同會誤擋,而且沒有逃生口**
severity: major
blocking: 是(合法記帳被 rc2,訊息還講錯)
- spec 段落:〈做法 7〉比對。
- 引句:「比正規化後的路徑或 sha256」
- 問題:spec 沒說正規化對象是哪一邊,也沒說 `materials` 讀不到時怎麼辦。
- 具體例:真帳有 205 筆(再加 26 筆混合形式)的 `materials` 是絕對路徑,例如 `/tmp/cpe/code-r2-snapshot.patch`,而 `--snapshot` 入帳是 repo 相對路徑。這些暫存檔已不在(全域暫存清理規則本來就會刪)。
- 照 spec 字面做:字串比對對不上,sha256 又讀不到材料,結果 rc2,訊息卻說「你填的是另一份」。
- 另有 3 筆材料只寫檔名(例如 `r1-snapshot.patch`),基本名相同但路徑不同,同樣誤擋。
- 〈不做〉又寫「不提供跳過新規則的旗標」,使用者無法繞過。
- 要補的:路徑比對的規則,以及材料不存在或形式不同時的退路(建議改成只提醒)。

**F4 輪次規則放的位置和「共用同一次讀帳」互相矛盾**
severity: major
blocking: 是(照字面放,[S5][S7][S9] 最核心的幾個情境不會觸發)
- spec 段落:〈做法 1〉`canary record` 寫側第 65 行。
- 引句:「那段讀帳之後、寫帳之前,跟它共用同一次」
- 問題:既有「載體最後記」那段由 `if loop and round_id and outcome is None:` 包著,必須有 `--round` 才進得去。
- 具體例:輪次規則要擋的正是「這筆沒帶 `--round`」,在 [S5]、[S7]、[S9] 這些情境,實作者照字面放進那段就根本不會執行。要改成自己讀一次帳,或把守衛條件拆開。
- 缺口:`_loop_records_checked` 在帳壞時回 `([], 原因)`,整本非 UTF-8 時看起來像零筆。spec 沒說這時是放行、擋下還是當作第一筆。放行會被利用,當作第一筆又會誤報。

**F5 零筆改走帶輪次的非 `seq` 路徑,連帶改了未提的輸出**
severity: minor
blocking: 否(不影響入帳和判定)
- spec 段落:〈做法 1〉`loop next`。
- 問題:`seq` 變成假之後,第一輪 plant-canary 的 `canary_type` 會從單一值變成 `slot1` 字典,而且會印 `cluster_hint`。spec 只講了範本和名冊。
- 具體例:`scripts/lumos` 的 `cmd_loop_next` 裡 `if light or ... or seq` 和 `not seq and n_next == 1` 兩處。[S1] 沒涵蓋,但行為變了。

**F6 既有的結局帳列也會讓「既有加這一筆」判成混用**
severity: minor
blocking: 否(真帳 12 個結局迴圈全是只有結局帳,目前沒有實例)
- spec 段落:〈做法 1〉寫側第 66、67 行。
- 問題:spec 只豁免「這筆是結局帳」,沒豁免「既有列裡有結局帳」。
- 具體例:帶輪次的迴圈先記了一筆 `--outcome`,之後再記一般席,既有列算上結局帳(無輪次)就變 mixed,擋下訊息「既有都帶輪次」是錯的。

**F7 〈做法 4〉只講一半**
severity: minor
blocking: 否
- spec 段落:〈做法 4〉。
- 問題一:`evidence` 是 `[]`、`{}`、`0` 時,現況 `or ""` 會當成「沒附」,「有給但不是字串」沒定義這類值怎麼處理。
- 問題二:讀側 `scripts/lumos` 約 55613–55650 行,satisfied 與 tension 的 `_ev(str(ent.get("evidence") or ""))` 是獨立的 `str()`。`_dispositions_tension_shape(check_evidence=False)` 在讀側不切 evidence。spec 說訊息「自然帶到」只對 tension 的 `existing` 成立,satisfied 的清單 evidence 在讀側照舊是「切不開」。寫側先擋,所以只在治理帳重建的紀錄上才會出現。

**F8 其他小處**
severity: minor
blocking: 否
- 〈做法 8〉第 121 行的「下一輪 r<N+1>」:輪次編號是自由字串(`r1b`、`R2`),沒說不是 `r<數字>` 時怎麼印。
- 〈做法 8〉[S21]:寫「定錨 high」,但第一輪帳上零筆沒有定錨,只有 `--tier high`。
- 〈做法 8〉的 `hints` 沒說在 plant-canary 以外的 phase(converged、cap-reached 等)印不印。
- [S7]:「印補了 `--round r1` 的同一條指令」,`cmd_canary` 拿不到原始 argv,只能是示意字串。測試只能斷言含 `--round r1`。
- 〈做法 5〉提醒印的是使用者給的檔名,建議走 `_esc_clean`。

**已讀、沒有 finding 的部分**
- 〈做法 2〉:`_ids` 現況與 spec 描述相符,`none` 改空集合的行為變化 spec 已明講。
- 〈做法 3〉:`_roster_kind` 三值判法與 spec 一致。
- 〈做法 6〉:名冊 `("code", tier)` 三個鍵都存在,`_REQUIREMENT_LABEL` 也存在。
- 〈做法 9〉:`out_conflict` 的訊息位置存在。
- 〈做法 10〉:SKILL 第 12、29 行的措辭與 spec 描述相符。

風險類:
- 守衛面:有,見 F1、F3 的誤擋。
- 舊帳相容:不溯及這點成立,F1 的 light 迴圈是例外。
- 在途分支:無,規則只作用於新記帳。
- 跨會談:無,單人依序操作。

最嚴重:major,blocking 共 4 條(F1、F2、F3、F4)。
