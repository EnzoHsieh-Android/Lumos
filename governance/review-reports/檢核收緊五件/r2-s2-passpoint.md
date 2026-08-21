# r2 s2 — S3 放行點綁定審計(code-loop pass 外家 fail-closed)

審計範圍:S3(外家 fail-closed 綁在 `code-loop pass`)。逐條核對 `cmd_code_loop`(scripts/lumos:14138)、`_codeloop_guard_verdict`(scripts/lumos:14046)、argparse(scripts/lumos:14673-14692)、`scripts/hooks/pre-push`(73-124)、`_TIER_ROSTER[("code","high")]`(scripts/lumos:4630-4638)、`_roster_family`/`_roster_dispatch_entries`(4654/4698)、實際 `governance/review-reports/*/rN-dispatch*.json` 檔、`.canary-log.jsonl` 慣例(scripts/lumos:3007/3211/4324/7608)。

---

## F1(blocker)`skip` 未受本設計約束,是無條件、更便宜的逃生門——整套 S3 可被繞過

引句:「這與 skip 一樣是逃生門,差別是留痕語意(passed-with-waiver vs skipped)」

哪裡錯:v2 自己承認 `skip` 是「一樣的逃生門」,卻只把外家 fail-closed 判定式掛在 `pass`(範圍刀明講「S3 完全在 code-loop pass 內」,`skip` 子命令完全不動)。但真正擋 push 的判定式 `_codeloop_guard_verdict`(scripts/lumos:14113-14122)在讀留痕時是 `rec_status in ("passed", "skipped")`——兩者被判定式視為**同等有效**,沒有任何欄位要求 `skipped` 記錄帶外家證據。而且 `scripts/hooks/pre-push:112-116` 擋下 tier=high 未過時印出的三個選項裡,選項 2 明文教使用者「lumos code-loop skip --note "<理由>" → 重 push(留痕)」——這是既有 UI 就會主動建議的路徑,且 v2「不改 pre-push」,訊息原樣保留。任何人想繞過外家 fail-closed,不需要碰 `--no-loop`/`--waive-external` 走任何審核路徑,直接 `code-loop skip --note "隨便"` 即可一次性拿到與「合法 pass」完全等效的放行資格。S3 標榜「掛在真正的放行點」以修正 r1 s4-F3(判定曾掛在可繞過的 `loop status`),但换了個一樣可繞過的洞——`skip` 本身就是「放行點」的另一半,S3 只補了半邊。

file:line:
- scripts/lumos:14167-14172(`cmd_code_loop` 的 `pass`/`skip` 分支——兩者呼叫同一組 `_codeloop_write`/`_codeloop_gov_log`,無 tier/loop 差異判斷)
- scripts/lumos:14113-14122(`_codeloop_guard_verdict` 讀留痕:`rec_status in ("passed", "skipped")` 視為同等有效)
- scripts/hooks/pre-push:112-116(擋下訊息選項 2 直接教 `code-loop skip`)

正確規則:外家 fail-closed 的判定式要嘛也掛在 `skip`(tier=high 時 skip 同樣要能證明「路徑已知、確實無外家可派」或走同一組 `--no-loop`/`--waive-external` 語意,而非裸 `--note`),要嘛判定式本身不能把 `skipped` 與「通過外家 fail-closed 的 passed」視為同一等級——至少要能從留痕分辨「skip 過的 tier=high commit 是否曾經過外家判定」。否則這條硬規則對任何知道 `skip` 存在的人形同虛設。

---

## F2(blocker)`pass` 內建的 tier 判定 range 與實際擋 push 的 range 不同源,兩處可判出不同 tier,造成整條 fail-closed 靜默失效

引句:「range 取 merge-base..HEAD,同 pre-push」

哪裡錯:這句聲稱 `pass` 內部算 tier 用「merge-base..HEAD」與 pre-push 一致,但 `scripts/hooks/pre-push:74` 的註解白紙黑字寫「改讀 stdin 推送範圍逐 ref 判,**取代 merge-base**」——2026-07-21 的 prepush範圍修法已經把 pre-push 的判斷依據從 merge-base 換成 `$_rsha..$_lsha`(一般情形)或 `$_EMPTY_TREE..$_lsha`(新 ref/shallow,見 pre-push:79-89)。也就是說「同 pre-push」這個等式本身是假的:pre-push 現在**不用** merge-base..HEAD。

後果不是文字瑕疵,是真的會讓 gate 失效:`pass` 目前沒有 `--diff`/`--repo` 之外可指定 range 的入口(argparse 只給 `check` 有 `--diff`/`--at-sha`/`--branch`,scripts/lumos:14684-14691),若依 v2 文字實作,`pass` 會用 `_codeloop_guard_verdict` 現有的 `diff_range=None` 分支(scripts/lumos:14065-14077)——這段自己找本機 `main`/`master` 本地分支算 merge-base,連本機沒有這兩個本地分支都會 fail-open 判 `tier: "unknown"`(scripts/lumos:14077)。而 push 時 pre-push 傳的是 `$_rsha..$_lsha`(遠端當時位置到本地新 sha 的實際差異,對新分支/遠端落後的情形範圍可能大得多)。同一個 HEAD sha,`pass` 時可能因為算出 tier=standard/unknown 而完全不觸發「必帶 --loop」的檢查,照舊寫下 `status: passed`;等到 push 時 pre-push 用真實 range 算出 tier=high,`code-loop check`(pre-push:107-109)只檢查「有沒有 sha 相符的 passed/skipped 留痕」(`_codeloop_guard_verdict` 完全不重新驗證 loop/waiver),於是直接放行——外家 fail-closed 從頭到尾沒被評估過一次。

file:line:
- scripts/hooks/pre-push:74(明文:「取代 merge-base」)
- scripts/hooks/pre-push:79-89(實際算 range 的邏輯:`$_rsha..$_lsha` / `$_EMPTY_TREE..$_lsha`)
- scripts/lumos:14065-14077(`_codeloop_guard_verdict` 的 `diff_range=None` 分支,用本機 `main`/`master` merge-base,找不到即 fail-open)
- scripts/lumos:14113-14122(check 端只認「sha 相符+狀態合法」,不重算/不驗證外家條件)

正確規則:`pass` 判 tier 必須拿與 pre-push **同一個 range**,不能各自重算——要嘛 `pass` 也吃 `--diff <range>`(由呼叫端如 CI/編排者傳入,與 pre-push 傳給 `check` 的同一個 range 一致),要嘛把「查外家 fail-closed」的判定挪到 push-time 的 `check` 本身(用 pre-push 已經算好、傳進來的 `--diff` range),而不是分別在 `pass`(本機、自算 range)與 `check`(push、拿 pre-push 給的 range)兩處各自獨立判 tier。

---

## F3(major)輪序改用 canary-log「首筆 ts」排序,直接牴觸既有明文慣例(ts 只到秒、同秒會並列),可能選錯 K 窗

引句:「輪序取 `canary-log` 同 loop 各 round 首筆 ts 排序」

哪裡錯:程式碼裡對 canary-log 排序方式已有清楚且反覆重申的慣例——「讀 append 序(不 ts-sort:ts 只到秒、同秒會並列)」,見 scripts/lumos:3007 的方法註解、scripts/lumos:4324(`cmd_loop_status`docstring)、scripts/lumos:7608(rel-cascade 帳本沿用同一慣例)。甚至 `canary record` 產生 token 時特意用隨機 hex 而非時間戳,理由就寫在程式碼裡:「隨機,非時間戳(同秒不撞)」(scripts/lumos:3211)。這些都是同一件事的重複佐證:這個 codebase 的 ts 欄位精度只到秒(`isoformat(timespec="seconds")`,scripts/lumos:3212),不足以可靠排序,既有機制全部刻意避開 ts-sort。v2 的 r1 s2-F5 修法卻反其道而行,選了「各 round 首筆 ts 排序」——如果同一輪 panel 的多個 auditor 幾乎同時(同一秒內)各自 `canary record`,或不同輪的首筆記錄剛好落在同一秒(自動化 loop 常見),ts-sort 排出來的輪序可能與實際輪次順序不一致,導致 `min(K=2, 輪數)` 取到錯的兩輪去驗外家席數——在剛好卡在邊界(例如最新一輪外家不足、次新一輪外家足夠)的情況下,錯誤排序會讓 fail-closed 誤判為「過」。

file:line:
- scripts/lumos:3007(`.canary-log.jsonl` 讀取:「append 序」註解)
- scripts/lumos:4324(`cmd_loop_status` docstring:「讀 append 序(不 ts-sort:ts 只到秒、同秒會並列)」)
- scripts/lumos:7608(rel-cascade 帳本沿用同一慣例的說明)
- scripts/lumos:3211-3212(`canary record` token 刻意不用 ts 排序/去重的理由,及 ts 精度只到秒的實證)

正確規則:輪序應沿用既有慣例——用 append 序(canary-log 檔案內的實體行序,或直接用 round-id 本身的數字排序,`rN` 已是嚴格遞增字串,`_roster_dispatch_entries` 的 glob 已按檔名排序,scripts/lumos:4664),不要引入 ts-sort。

---

## F4(major)「輪數」的認定來源未定義:當某輪已有 dispatch 快照但還沒寫 canary 記錄(進行中的一輪,常常正是最新一輪)時,`min(K, 輪數)` 該怎麼數沒有規則

引句:「取最後 **min(K=2, 輪數)** 輪(r1 s6-1 冷啟動)」

哪裡錯:v2 的排序依據(F3)是「canary-log 同 loop 各 round 首筆 ts」,但一輪的生命週期通常是「先產生 `rN-dispatch*.json`(派工)→ 審計進行 → 事後才 `canary record`(收尾留痕)」。也就是說,呼叫 `code-loop pass --loop <id>` 當下,最新一輪如果還在跑(尚未 `canary record`),在 canary-log 裡完全沒有這一輪的 ts——F3 的排序方法對這一輪根本算不出順序。既有的 `_roster_observe`(scripts/lumos:4732-4736)在做類似對帳時,`rids` 的來源是「canary-log 出現過的輪」**聯集**「dispatch 檔案 glob 出來的輪」(scripts/lumos:4713-4720),不是只看 canary-log。v2 沒有講清楚它打算沿用哪一種:如果只用 canary-log 決定「輪數」與順序(照 F3 引句字面讀就是如此),那麼最新、尚未寫 canary 記錄的一輪會被整個排除在 K 窗之外——`code-loop pass` 驗到的會是「上一輪已結案」的外家席位組成,而不是「這次要放行的這一輪」的組成,等於驗了一輪跟本次改動無關的舊資料就判過。

file:line:
- scripts/lumos:4713-4720(`_roster_observe` 現行做法:`rids` 取 canary-log 輪與 dispatch 檔案輪的聯集)
- scripts/lumos:4664-4666(`_roster_dispatch_entries` 只讀 dispatch 檔案,不依賴 canary-log 是否存在)
- 前引 governance/review-reports/檢核收緊五件/r2-dispatch-*.json 六份檔案均無 `ts` 欄,佐證 dispatch 快照本身無法排序,只能靠外部來源(canary-log 或檔名/mtime)

正確規則:「輪數」與排序都要以 dispatch 快照(或至少是 dispatch∪canary-log 聯集)為準,不能只看 canary-log 是否有記錄——否則最新、進行中的一輪會被系統性忽略,K 窗永遠驗的是「已結案」的舊輪,不是「本次要放行」的那一輪。

---

## F5(major)`--no-loop` 與 `--waive-external` 的關係未定義,測試清單只驗證了兩者中的一個

引句:「`--no-loop "<理由>"`/`--waive-external "<理由>"`:明確旗標」

哪裡錯:S3 條文第一次出現「必帶 `--loop` 或 `--no-loop "<理由>"`」(只講 `--no-loop`),第二次條列行為時卻寫成「`--no-loop`/`--waive-external`」二選一並列、當同一件事描述其寫入行為(`status: passed, waiver: {...}` + `gate: external-waived`)。全文從未講清楚這是「同一個旗標的兩個別名」還是「兩個獨立旗標、語意不同(例如 `--no-loop` = 這次改動根本不屬於任何 loop,`--waive-external` = 有 loop 但外家席位不足、明確豁免)」。若是後者,兩者該不該寫入相同的 `waiver`/`external-waived` 事件、`detail` 欄要不要區分理由類別,文件沒答案。測試策略(122 行文件第 99 行)裡,第 16 條 `t_codeloop_pass_high_requires_loop` 只驗證「兩者都不給 → rc2」,第 19 條 `t_codeloop_pass_waiver` 只驗證 `--waive-external` 這一支的完整行為(寫 passed+waiver+`external-waived` 事件);全部 23 條測試中沒有一條驗證「單獨給 `--no-loop "<理由>"`」時應該寫出什麼——實作者拿到這份 TDD 清單,寫得出「兩者都不給要 rc2」但寫不出「`--no-loop` 該做什麼」,只能猜。

file:line:(設計文件內部矛盾,無對應既有 code;引 122 行文件本身第 71/73/99 行)

正確規則:先在文件裡把 `--no-loop` 與 `--waive-external` 明確定義成「同一旗標的兩個名字(pick one)」或「兩個獨立旗標、各自語意與寫入格式」,並各補一條 `--no-loop` 專屬的成功路徑測試(比照第 19 條),不要讓兩個旗標名稱互相替代出現卻只有一個有完整規格。

---

## F6(major)「三個逃生口全部落治理帳、可數」的自我治理主張,自相矛盾地漏掉 skip

引句:「三個全部落治理帳、`gov --stats` 可數、退場條件直接拿這些數當分子」

哪裡錯:這句話出現的上下文是列舉三件的逃生口:「S1 標 A、S2 ack、S3 `--no-loop/--waive-external`」——把 S3 的逃生口窄化列成只有 `--no-loop/--waive-external` 兩種旗標,只字未提 `skip`。但同一份文件第 73 行才剛親口承認「這與 skip 一樣是逃生門」。這是文件內部的自我矛盾:如果 skip 也是逃生門(F1 已證實它甚至是更便宜、無條件的那個),那麼「S3 的逃生口=--no-loop/--waive-external」這個列舉本身就是不完整的,連帶「三個全部落治理帳、可數」與退場條件表(87-91 行,S3 那列只拿 `external-waived` vs `code-loop`(passed)算比例)也系統性地看不到 skip 造成的逃逸量——skip 事件確實會寫進 `docs/.governance-log.jsonl`(`gate: code-loop, kind: skipped`,scripts/lumos:14020-14045),但退場條件公式沒有把它算進分子/分母,於是即使團隊在 tier=high 時大量改用 `skip` 繞過外家 fail-closed,S3 的退場量測(「waived/passed ≥50% → 管道不穩」「連續 90 天零 waived 且有 passed → 維持」)仍會顯示「健康」,因為它壓根沒在看 skip 那條channel。

file:line:
- scripts/lumos:14020-14045(`_codeloop_gov_log`:skip 事件確實落帳,`kind: "skipped"`,`hard: False`)
- 文件本身第 73 行 vs 第 104 行的列舉矛盾(同一份文件内部不一致,非 code 問題)

正確規則:S3 的退場量測公式要嘛把 `code-loop`(skipped, tier=high)也算進分母/另立一條「skip 佔比」量測,要嘛先把 F1 補上(skip 也受同一組判定約束),否則這條「逃生口濫用是對策就是被數」的自我治理主張對 S3 不成立。

---

blocker: 2 / major: 4 / minor: 0
