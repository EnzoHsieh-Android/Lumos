severity: major

## 第 1 問 分層與依賴方向

**大致對齊,但有兩處計劃沒寫清楚。**

- **分級(範圍 2):** 放在 `_pitfall_tier`,它仍是呼叫端取分級的單一入口,位置對。`pitfalls --diff` 與 `code-loop check`(子程序跑 `pitfalls --no-lint --json`)確實都走它。
  - file: `scripts/lumos:64523`、`scripts/lumos:65147`、`scripts/lumos:65214`
- **拆法:** 鄰居把「讀資料」和「組理由」拆開,寫成 `_residual_tier_hits`(回 dict)加 `_residual_tier_reasons`。註解還寫明這樣是為了讓「分級函式不再變複雜」。計劃寫「分級函式最先讀…每個提交的完整訊息」,沒說要不要抽成獨立函式。這是要求實作比照鄰居拆開的注意事項,不算不對齊。
  - file: `scripts/lumos:64454`、`scripts/lumos:64527`、`scripts/lumos:64768`
- **拆範圍:** 計劃指定用 `_diff_range_ends`,跟 `_residual_tier_hits` 同一支。
  - file: `scripts/lumos:64794`
- **git 包裝沒指定:** 計劃只寫 `git log 起點..終點`,沒說用哪個包裝。專案已把「讀 git 用 `_lens_git`」收斂過一次(代碼審 r4 架構對齊席),實作不要自寫 `subprocess.run`。
  - file: `scripts/lumos:64539`(`_residual_blob_at`)、`scripts/lumos:69104`(`_lens_git`)
- **忽略註解(範圍 3):** 掛在 `_lint_new_run_cmds` 的 `out["ran"].append(cmd)` 之後。這是 commit 範圍模式與工作樹模式共用的唯一入口,沒有繞過,位置對。「沒跑的、只報不擋的不數」在程式裡也成立,因為前面的 `continue` 已經擋掉。
  - file: `scripts/lumos:43275`、`scripts/lumos:43301`、`scripts/lumos:41525`(工作樹模式也呼叫 `_lint_new_run_cmds`)
- **放行流程:** 走既有的 `_lint_new_key` / `_lint_new_diff_claims` / `_lint_waivers_add` / `cmd_lint_waive`,沒有另開一套。
  - file: `scripts/lumos:42830`、`scripts/lumos:42855`、`scripts/lumos:42908`、`scripts/lumos:41843`

## 第 2 問 命名與錯誤處理

**不對齊,共兩條(下面 finding 2 和 3)。**

- **git 讀不出時的方向:** 鄰居一律往多升 high,理由句收尾都是「看不出,當成有」。
  - `base_bad`、`files_unknown`、`asks_unknown` 就是這個做法。
  - `touched()` 在清單讀不出時回 True。
  - 只有「內容壞掉但 git 讀得到」才維持不升,因為 doctor 已經報過。
  - `_residual_blob_at` 把「確定沒有(missing)」和「讀不出(unreadable)」分成不同狀態。
  - file: `scripts/lumos:64499`、`scripts/lumos:64811`、`scripts/lumos:64806`、`scripts/lumos:64819`、`scripts/lumos:64539`
  - 計劃把「起點是空樹」(相當於 missing)和「git 讀不出」(unreadable)併成同一句「不升」,方向跟鄰居相反,也丟掉了三態區分。
- **理由字串:** 鄰居的理由是「事實(清單最多 3 筆…等 N 筆;為什麼),要過高風險代碼審」,外來字串另外清洗。
  - `_plain_label(…, 80)` 用在 `notes_unknown_why`。
  - `_tg_cand` 的註解寫明「擋下訊息是給 AI 讀的,不讓外來文字偽造出『接下來』這類段落」。
  - 計劃的理由是「人工標記高風險」直接接提交訊息那一行後面的字,沒有長度上限、沒有清洗,也沒說明要過審。
  - file: `scripts/lumos:64454`、`scripts/lumos:64486`、`scripts/lumos:70006`、`scripts/lumos:53272`
- **「最先」跟既有說法衝突:** `_pitfall_tier` 的 docstring 和圖譜 KEY 都寫「殘留索引升 high 最先判」。計劃的「最先讀」若指排在殘留之前,要同步改這兩處,也沒說兩種理由並存時怎麼串。
  - file: `scripts/lumos:64523`、`docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md:63`
- **合成告警的欄位:** 計劃沒寫 `source` 與 `message` 該怎麼填。目前 `base_claims` / `head_claims` 的 `source` 都是 `lint:<driver>`。
  - file: `scripts/lumos:42377`

## 第 3 問 第二種做法

**有一條 major,另有兩條不好判、交給編排者。**

- **認工具的方法是第二套(major,finding 1)。**
  - 專案已有兩處用 shlex 切段、看命令頭的辨認:
    - `_detekt_command_codes` 經 `_detekt_walk_segments` 剝環境變數和包裝詞、展開 `sh -c`,再用 `_cmd_basename(seg[0])` 比對。
    - `_lint_wt_allow` 用 `words[0] != "ast-grep"`。
  - `_cmd_basename` 的註解明說,「原本 posixpath.basename 與自寫切法並存」就是 r4 架構對齊席抓過的缺陷。
  - 計劃改用「整條字串 + 字邊界正規式」認七個工具,其中 detekt 和 ast-grep 兩個鄰居已經各有一套辨認。
  - 我拿同一批命令字串實跑了既有的 `_detekt_command_codes` 和 `\b` 正規式:
    - `ruff check --config configs/detekt.yml {LINT_FILES}`:既有函式判 detekt 為 False,正規式認到 detekt 和 ruff 兩個。
    - `python3 scripts/lumos stylelint-sarif`:正規式認成 stylelint,實際是橋接腳本。
  - ruff、eslint、stylelint、semgrep、swiftlint 在 `scripts/lumos` 裡確實沒有現成的辨認表,所以這五個需要新表。但表應該建在既有切段函式之上,不是整串正規式。
  - file: `scripts/lumos:40588`、`scripts/lumos:40596`、`scripts/lumos:40660`、`scripts/lumos:41200`
- **放行流程沒有第二套。** 計劃重用 `lint-waive`,對齊。
- **規則包排除寫法:** 計劃只寫行為,沒寫 YAML,見 ⚠B。
- **人工標記入口:** 提交訊息裡沒有既有的訊息讀取器可對照。`_pitfall_tier` 被圖譜 KEY 鎖成 vault-free,所以不走計劃風險欄位而改讀提交訊息有理由。不拿 trailer 格式也有 `Projects/進度從提交推導_計劃` 的 d7 翻案紀錄撐著。這兩點對齊。

### ⚠ 交編排者(不計入下面的條數)

**⚠A 閘自己產生「繞過檢查」類候選,專案有三種寫法,計劃沒提任何一種。**

1. 工具告警走 SARIF 流。
2. `_lint_new_sep_split` 把清單項塞進 `out["oversize"]`。
3. 作弊比對 `test-guard`:
   - 候選走 `_lint_new_guard` 和 `_lint_new_guard_new`,併進 `out["new"]`。
   - 規則名用 `tq/` 命名空間。
   - 由 `_TG_WHY` 附「為什麼」和「該確認」,外來字串經 `_out_clean`。
   - 擋下訊息有專門的 `_cl_say_lint_tq` 段。
   - `_tg_main_cands` 加 `_tg_diff_locs` 做的是同一件事:數正式碼裡的字樣在改動前後各幾處,取新增。

計劃把合成告警塞進 `_lint_new_run_cmds` 的 SARIF 流,規則名用不帶命名空間的 `lumos-inline-suppression`,沒有 `verify` 欄,也沒說明為何不走 test-guard 那條。

計劃選擇有真實理由:它要「只數有跑的命令認得的工具」,test-guard 不知道哪些命令跑了。但鄰居本身不一致,我不硬判。建議計劃補一句為何不併進 test-guard,以及規則名與「該確認」欄怎麼寫。
- file: `scripts/lumos:43172`、`scripts/lumos:43134`、`scripts/lumos:43335`、`scripts/lumos:53272`、`scripts/lumos:53445`、`scripts/lumos:76205`
- 引句:「把新加的忽略註解當成一條新增告警送進同一條路,不另做一套」

**⚠B 規則例外「只看那一層類別」跟鄰居的寫法可能不同。** 同規則包的 `kt-register-without-unregister` 用一個放在最外層的 `not: inside: class_declaration has delegation_specifier regex: Application\( stopBy: end` 排除「跟程序同壽命」的擁有者,這是「任一層祖先類別」的寫法。計劃要的是「最近一層類別」,規則包裡沒有現成寫法。如果實作照鄰居寫,Service 裡的內部 Fragment 會被一併豁免,跟計劃語意矛盾,而 S1 沒有內部類別的樣本。另外,把 `not` 放到 `any` 外層是鄰居讓兩個分支共用排除的做法,可以照抄。
- file: `configs/ast-grep/kotlin-android/rules/architecture.yml:287`、`configs/ast-grep/kotlin-android/rules/state.yml:176`
- 引句:「只看那一層類別,不看裡面的內部類別」

規則包的樣本要求(壞例至少 2 處命中、好例 0 誤報且至少 2 段)沒有衝突。S1 說「同一支檔裡 Fragment 照報」,所以那支檔必須放在 `samples/bad/`,不能放 `samples/good/`。
- file: `configs/ast-grep/kotlin-android/check.py:1066`

## 第 4 問 落點

**範圍 1 和 2 的落點合理,範圍 3 漏了一篇。**

- **`Systems/kotlin規則包`:** 範圍 1(規則、樣本、型錄 STATE-5 那列)正是它的負責範圍,而且寫明「不負責新增告警閘本身的判定」。前例 `規則包覆核兩級接新增告警閘_計劃` 的 `lands_in` 也是這篇加 `linter精選目錄`。對齊。
  - file: `docs/lumos-toolchain-knowledge/Systems/kotlin規則包.md:5`
- **`Systems/pitfalls-code-loop`:** 範圍 2 的分級在它的 KEY 第 63 行,該寫進這篇。但這篇沒寫負責範圍,已有 343 行、96KB,又管著整個 `scripts/lumos`,範圍 3 的內容不該再往裡塞。
  - file: `docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md:63`
- **範圍 3 的家是 `Systems/pitfalls-lint-adapter`:** 它的負責範圍明寫「改動前後兩份快照各跑一次、SARIF 解析合併、指紋與差集、放行檔與 lint-waive」,並把「閘在代碼審檢查裡的順序與擋下訊息的組法」劃給 pitfalls-code-loop。前例 `新增告警閘_計劃` 的 `lands_in` 就是 pitfalls-lint-adapter 加 pitfalls-code-loop。計劃漏列了它(finding 4)。
  - file: `docs/lumos-toolchain-knowledge/Systems/pitfalls-lint-adapter.md:7`、`docs/lumos-toolchain-knowledge/Projects/新增告警閘_計劃.md:26`
- 如果採納 ⚠A 的折衷併進 test-guard,則 `Systems/test-guard.md:6` 也要列進去。
- 範圍 4(README)不需要節點。

## 不對齊的 finding

### finding 1:認工具另寫一套整串正規式
severity: major
blocking: 是
引句:「認工具的方法:整條命令字串用正規式找工具名」

### finding 2:git 讀不出提交時的方向跟鄰居相反
計劃是「讀不到就不升」,鄰居是「看不出就當成有、往 high 升」。計劃還把空樹和 git 讀不出併成同一句,丟掉三態區分。
severity: minor
blocking: 否
引句:「起點不是一個提交(例如新分支首推、範圍起點是空樹)、git 讀不出訊息時,分級照原本算」

### finding 3:理由字串的寫法、清洗與排序跟鄰居不同
severity: minor
blocking: 否
引句:「加那一行字樣後面的字;值寫什麼都一樣」

### finding 4:`lands_in` 漏了範圍 3 的家
severity: minor
blocking: 否
引句:「Systems/pitfalls-code-loop」

不對齊共 4 條,其中 major 1 條(另有 ⚠ 2 條交編排者,未計入)。

我在唯讀 repo 上只做了不寫檔的實跑(在行程內載入 `scripts/lumos` 比較辨認函式),沒有建立任何暫存目錄,也沒有留下 `.pyc`。
