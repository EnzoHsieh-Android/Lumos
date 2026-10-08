severity: major

審查範圍:只比對這份設計和專案既有做法是否一致,不找 bug、不評風格。事實層面的依據是我對 `scripts/lumos` 與 Systems 節點的實際查證。

**1. 分層與依賴方向**
- 第一項(外部事實行)放在 `_lens_render_listed` 之內,做法對,不算不對齊。依據:`scripts/lumos:40007`。
  - 它是 diff 與 spec 兩種鏡頭共用的一支渲染函式,呼叫處在 `scripts/lumos:40361` 和 `scripts/lumos:40564`。
  - 外部事實行也該在這裡印。
- 掃描位置有問題,見 finding 1:設計沒說摘要行掃描由誰做。
- 第二項(補選碼表筆記)有風險,見 finding 2。
  - 它把挑筆記的邏輯塞進鏡頭層,而鏡頭現在只消費 impact 的結果。

**2. 命名與錯誤處理**
- `<棧>-extcode` 的 id 跟鄰居 `node-external`、`py-external`、`java-external` 撞語意,見 finding 4。依據:`scripts/lumos:23467`、`scripts/lumos:23479`、`scripts/lumos:23497`。
- 時間不夠時多印一行「外部碼表補選因時間上限中止」,風格上跟鏡頭其他降級行(例如 `_LENS_FOOT_SKIP` 的「略」行)一致,不列。依據:`scripts/lumos:39283` 一帶的 `_LENS_FOOT_SKIP`。

**3. 第二種做法**
- 見 finding 1、3、5。

**4. 落點**
- 見 finding 6。

**Finding 1**
severity: major
blocking: 是
引句:「在合約行之後,另印該篇裡以 `FACT:`、`FLOW:`、`DEP:` 開頭(允許前置空白與列表符號)且帶 `[來源:外部]` 標記的行」
- 這會另寫一套「摘要行掃描」。專案已有兩套現成的可借用:
  - `_CTX_SOURCE_RE`(`scripts/lumos:3373`)已認 `[來源:…外部…]` 標記。
  - `_NOTE_SHAPE_PREFIX_RULES`(`scripts/lumos:3367` 一帶)已把 FACT/FLOW/DEP 三個前綴綁在一起。
- 合約行有「全檔唯一」的掃描 `_contract_key_matches`(`scripts/lumos:39369`),它的註解明寫「別再各寫一份」。
- 設計寫了「現行正規式只認 `[來源:外部]`」,卻沒說要重用 `_CTX_SOURCE_RE`,也沒說要抽一支「唯一的來源行掃描」。
- 最容易走偏的是另寫一個前綴加來源的正規式。這樣會跟 `_CTX_SOURCE_RE` 各管一半,標記格式一改就漂移。
- 設計要明寫:新增一支與 `_contract_key_matches` 對稱的單一掃描,或直接重用 `_CTX_SOURCE_RE` 加 `_NOTE_SHAPE_PREFIX_RULES` 的前綴集合。
- 另外「`[來源:外部]` 只認這一種寫法」是縮窄,`_CTX_SOURCE_RE` 本來就允許標記內的空白,設計應說明為何不同。

**Finding 2**
severity: major
blocking: 是
引句:「補選要在鏡頭內層 45 秒總帳的剩餘時間內做:每讀一篇前先看剩餘時間,不夠就停止補選」
- 鏡頭預算已有一套:`_LENS_INNER_BUDGET = 45.0`(`scripts/lumos:39401`),搭配 `_t0` 與 `deadline = _t0 + _LENS_INNER_BUDGET - _LENS_FALLBACK_RESERVE`(`scripts/lumos:40349` 一帶),備援段也是照這個模式接。
- 設計沒說補選用這同一組變數,也沒說要不要像備援那樣保留 `_LENS_FALLBACK_RESERVE`。這點判不準 ⚠。
- 風險是補選另算一個時鐘,或不預留尾端時間,結果擠掉合約行與備援段。
- 另外「多讀自由席 8 篇」用的是 `_lens_git show`(`scripts/lumos:40355` 一帶),已有 20 秒逾時;補選每篇都走同一支,這部分一致。
- 設計要明寫:共用 `_t0` / `_LENS_INNER_BUDGET`,並說明補選的預留量。

**Finding 3**
severity: major
blocking: 是
引句:「改動行剝掉註解:」
- 設計要自己另寫「diff 行解析」與「剝註解、保留字串」的步驟。專案已有:
  - `_stack_norm_line(code, keep_strings=True)`(`scripts/lumos:23871`),註解開頭整行不算、行尾註解也剝,正是「只剝註解、保留字串」。
  - 題目表第三欄 `when_raw` 就是用它。
  - `_PITFALL_DIFF_PATTERNS`(`scripts/lumos:23926`)與同一套正規化對稱。
- 設計該明寫:共用形狀正規式的輸入走 `_stack_norm_line`,diff 的增刪行取得方式沿用 `_stack_applicability` 一帶(`scripts/lumos:23884`)已有的做法,不另開一條解析。
- 「測試檔沿用既有的測試檔判斷」是對的,但沒指名函式。程式裡有 `_nodehome_is_test`(`scripts/lumos:26070`)和 `_testmap_is_test`,該指名是哪一個。判不準 ⚠。

**Finding 4**
severity: minor
blocking: 否
引句:「id 為 `<棧>-extcode`」
- 題目 id 的慣例是「棧-名詞」描述主題,例如 `node-external`、`py-external`、`java-external`(`scripts/lumos:23467`、`scripts/lumos:23479`、`scripts/lumos:23497`)。新 id 在 node、py、java 三棧會跟 `*-external` 並存,語意重疊。
- 設計應說明為何不併進既有 external 題,或換一個跟鄰居有區別的名字。
- 也要確認 `*-external` 的 `when` 是否已會在同樣改動亮起。

**Finding 5**
severity: minor
blocking: 否
引句:「題目文字與觸發形狀全部引用同一組常數(單一來源)」
- 專案慣例是每題的 `q` 與 `when` 都在題目表裡直接寫字面。表在載入時編譯成 `_STACK_TRIGGERS`(`scripts/lumos:23551`),「壞 regex 就啟動即錯」。
- 八題共用一個常數,結構上沒問題,而且是在鄰居沒有的地方去重複。
- 不一致之處在於:
  - 題目文字 `q` 常數化跟既有慣例不同。
  - 設計沒說 `when_raw` 與 `when` 的分組要怎麼接進 `_STACK_TRIGGERS`,尤其「欄位名那組放一般欄、引號數字那組放保留字串欄」,一般欄不能空的限制。
- 這點判不準 ⚠,先標 minor。

**Finding 6**
severity: minor
blocking: 否
引句:「lands_in:
  - Systems/pitfalls-code-loop
  - Systems/design-loop」
- 落點不合理。
  - 計劃的三項改的是派工鏡頭渲染、impact 結果補選、題目表。
  - 派工鏡頭不是設計審,design-loop 是設計審查迴圈。
  - pitfalls-code-loop 裡 `_lens_render_listed` 與「派工鏡頭」的出現次數是 0,design-loop 是 1 次;兩篇都不是現況主要記載處。
- 實際上,派工鏡頭的現況記在:
  - `Systems/hook逾時預算`
  - `Systems/anchor-integrity`
  - `Systems/bound-tests-gate`
  - `Systems/codex-harness`
  - `Systems/開發工作流總覽`
- 第三項(題目表加題)的家顯然是 `Systems/棧別提問表態閘`。它的 DEP 行已列 `_STACK_QUESTION_SPECS`、`_STACK_TRIGGERS`、`_lens_dispositions_lines`。依據:`docs/lumos-toolchain-knowledge/Systems/棧別提問表態閘.md:45`。
- 設計該把 lands_in 改成:
  - 題目表那項 → `棧別提問表態閘`。
  - 鏡頭那兩項 → 先確認管派工鏡頭的家是哪一篇(`lumos search` 查到的多是 Projects 計劃),再決定。
  - 另外要預期 `pitfalls-code-loop` 與 `design-loop` 都是「沒寫負責範圍」的節點,硬塞進去會養出巨型節點。

不對齊共 6 條,其中 major 3 條