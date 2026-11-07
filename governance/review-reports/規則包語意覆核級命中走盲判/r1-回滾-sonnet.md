severity: major

我把審查當成「這功能上線後要退回」來做。先列所有會寫入、凍結或重算判定的入口,再逐項問退回後還在不在、要不要人收拾、救不救得回。

**入口盤點(退回這個提交後)**

| 入口 | 退回後還在嗎 | 舊版讀到會怎樣 | 要不要人收拾、救不救得回 |
|---|---|---|---|
| 治理帳 `rule_hits` 欄(和 `blind_judge` 欄同一筆事件) | 在,帳只追加 | 舊讀法要求 `blind_judge` 非空,只有 `rule_hits` 的事件整筆不折。有 `blind_judge` 的事件照讀、忽略新欄 | 不用收拾,但撤不掉(見 F1) |
| 放行檔裡 origin ai 的「盲判判誤報」放行 | 在 | 舊版當一般 AI 放行,算進「還沒人看過」 | 要人收拾:沒有撤銷指令,也沒有批次標記可以挑出一批 |
| 放行檔新增的 `--verdict` 欄 | 在 | 舊 ack 流程照讀、不認 | 無害 |
| `lint.json` 的 `review` 段 | 在消費專案裡 | 舊 `_lintcheck_validate` 迭代所有鍵、value 非 list 就報錯。其他讀 lint.json 的地方是依副檔名取值,看不到這個鍵,所以不受影響 | 要人收拾:靠一個額外提交保留驗證器那行(見 F4) |
| 範本、doctor 提醒、統計 | 範本留在消費專案裡,統計和 doctor 提醒隨提交退掉 | — | 可救 |

---

**F1**
severity: major
blocking: 是(判錯一大批沒有任何撤回或重判的路,救不回來)
- 段落:範圍 4(結果檔、治理帳)、範圍 5(`false`)、回退
- 問題:設想壞掉的盲判把 50 筆真問題判成 `false`。
  - 帳:既有記帳在整份格子都已有紀錄時直接拒收,訊息寫「帳只追加、撤不掉;要重判只能等段材料變了」。覆核命中的 `seg` 是 (規則, 檔, 片段) 的指紋,片段不改就永遠是同一格,所以重判不可能發生。
  - 放行檔:`_lint_waivers_add` 遇到同一個指紋會直接報「已經放行過了」。全 repo 也找不到撤銷放行的指令或旗標。
  - 找出來:放行檔裡沒有批次欄位,只能靠理由開頭「盲判判誤報:」加時間去猜。
  - 計劃唯一的補救線(RETIRE-IF 八週、REVISIT 一個月)都是事後統計,不是撤回機制。
  - 回退節把這些放行說成「它們本來就是合法放行」,正好把這個問題當成沒事。
- 建議:放行紀錄要帶批次或判定來源欄位;要有 `lint-waive --revoke`,或在帳裡能作廢某筆判定;要規定重判怎麼進帳。
- 引句:「放行檔裡 origin ai 的覆核誤報放行留著(它們本來就是合法放行)」
- 引句:「同一格已有判定不再收」
- 佐證:file: `/Users/enzo/orca/workspaces/lumos-toolchain/rulepack-review-bj/scripts/lumos:74209`(整份都是已有格就 rc2、訊息寫「撤不掉」)
- 佐證:file: `/Users/enzo/orca/workspaces/lumos-toolchain/rulepack-review-bj/scripts/lumos:42306`(`key in cur` 就拒絕)

**F2**
severity: major
blocking: 是(人推翻了盲判,放行卻仍然生效,這是準確率統計的核心用途)
- 段落:用詞〈人複查〉、範圍 7
- 問題:`--verdict overturn` 只被計數,計劃沒寫它對已存在的放行有什麼作用。
  - 人明確寫下「這其實是真問題」之後,那筆放行仍是有效的,推送照樣放行,命中永遠不再擋。
  - 現有 `_lint_waive_ack` 只做 `acked=True`,不碰放行本身。
  - 這是「人發現判錯」的唯一機制,結果只改了統計。
- 建議:overturn 要讓放行失效,或把該命中改回要人當下確認。
- 引句:「不帶 `--verdict` 的 ack 照舊只記看過、不進準確率。」
- 佐證:file: `/Users/enzo/orca/workspaces/lumos-toolchain/rulepack-review-bj/scripts/lumos:41204`(ack 只 update `acked`、`acked_by`、`acked_at`)

**F3**
severity: major
blocking: 是(兩份記錄分開寫,中途失敗後重試被擋,留下無法修復的半寫狀態)
- 段落:範圍 4(治理帳)、範圍 5(`false`)
- 問題:記帳那一步要同時寫兩個地方,沒有規定順序,也沒有回滾。
  - 兩個地方是治理帳 `rule_hits`(追加)與放行檔(`_lint_waivers_add`)。
  - 若帳先寫成功、放行檔失敗(放行檔讀不了、鎖、該指紋已被人放行過回「已放行過」),重跑會被「整份都是已有格」拒收。
  - 於是放行永遠補不寫。命中沒進 AI 複查清單,「判誤報不直接消失」這條 PRIOR-ART 就落空。
  - 計劃也沒說 `false` 的「不擋」是看帳還是看放行檔,兩種讀法在半寫狀態下結果不同。
- 建議:先寫放行再寫帳,或讓重跑只補寫放行;S4 補一條半寫失敗的案例。
- 引句:「記帳那一步(`lumos code-loop blind-judge <結果檔>`)替它寫一筆放行」
- 佐證:file: `/Users/enzo/orca/workspaces/lumos-toolchain/rulepack-review-bj/scripts/lumos:74214`(`_codeloop_gov_append` 之後沒有其他寫入)

**F4**
severity: major
blocking: 是(回退節的前提在 git 退提交時不成立,而且沒有條款綁它)
- 段落:回退、範圍 8、驗收條款
- 問題:
  - 退回提交會連驗證器對 `review` 鍵的認得一起退掉。「留著那一行」要人另外手工補一個提交,九條 S 條款沒有一條釘它。
  - 範圍 8 又會讓範本把 `review` 段散播到消費專案,舊版 `lint-check` 對這類專案一律報錯。
  - 退回後,覆核誤報放行會被舊 doctor 當一般 AI 放行計數。`_lint_waivers_ai_pending` 只分情境段與非情境段,看不出哪些是盲判放的。
  - 人要用 `--ack --all` 整批清掉,且沒有 verdict。
- 建議:加一條 S 條款釘「舊驗證器對 `review` 鍵的相容」;或先出只認得 `review` 鍵、不跑它的前置提交,再出功能提交,退回就只退第二個。
- 引句:「否則已照範本加了 `review` 段的消費專案,`lint-check` 會因為不認得的鍵報錯」
- 佐證:file: `/Users/enzo/orca/workspaces/lumos-toolchain/rulepack-review-bj/scripts/lumos:39612`(迭代所有鍵,value 非 list 即報錯)
- 佐證:file: `/Users/enzo/orca/workspaces/lumos-toolchain/rulepack-review-bj/scripts/lumos:41191`(`_lint_waivers_ai_pending`)

**F5**
severity: major
blocking: 是(AI 自動寫的放行範圍比 AI 看到的材料大,真問題可被後續同片段複製洞穿)
- 段落:範圍 3、天花板 1
- 問題:判定只看「檔內最後一處」前後 8 行。但放行綁 (規則, 檔, 片段) 指紋,同檔同片段的所有處、以及之後新增的同片段都一併放行。
  - 例:`.value.add(x)` 第一處是 Map.Entry(誤報),AI 判 `false` 並自動放行。之後同檔又加一處 StateFlow 的 `.value.add(x)`,指紋相同,直接放行、再也不擋,盲判根本沒看過它。
  - 天花板 1 只講了人放行的語意。這裡 AI 寫的放行是自動、批次的,影響更大。
  - 範圍 3 也只寫「同片段另有 N 處」,代理看不到其他處的上下文。
- 建議:有多處時每處各給前後 8 行,或讓 `false` 放行只在處數與判定時相同時有效。
- 引句:「材料取檔內最後一處(複製貼上時新加的通常在後面)」
- 引句:「放行一處等於放行同檔同片段的每一處」
- 佐證:file: `/Users/enzo/orca/workspaces/lumos-toolchain/rulepack-review-bj/scripts/lumos:42261`(同指紋計次,超出基準次數才算新增;被放行指紋全部略過)

**F6**
severity: minor
blocking: 否(統計與門檻失準,但不影響推送閘本身)
- 段落:範圍 7、用詞〈人複查〉
- 問題:`--ack --all` 與 `--verdict` 能否合用沒定義。
  - 若可以,人一次帶 `--verdict agree` 就把清單上全部 AI 放行(目前 62 筆)蓋成同意,「`--verdict agree` 至少九成」的建議門檻立刻成立。
  - 計劃沒規定 `--verdict` 必須逐筆、且要看過理由。
- 建議:`--verdict` 只准搭單一指紋。
- 引句:「不帶 `--verdict` 的 ack 照舊只記看過、不進準確率。」
- 佐證:file: `/Users/enzo/orca/workspaces/lumos-toolchain/rulepack-review-bj/scripts/lumos:41193`(`_lint_waive_ack` 目前支援 `ack_all`)

**F7**
severity: minor
blocking: 否(實作時會踩,但不影響設計方向)
- 段落:範圍 4(治理帳)
- 問題:新欄 `rule_hits` 沒登記進 `_GOV_FIELD_TYPES`,也沒進 `_gov_row` 的欄位白名單。
  - 該表的註解寫明,型別錯會讓整個 gov 當掉。
  - `_gov_row` 目前只轉出 `blind_judge` 與 `role`,統計拿不到 `rule_hits`。計劃把這兩處當成不用動,S8 的驗收會抓不到。
- 引句:「判定放在新欄 `rule_hits`(不放進舊的 `blind_judge` 欄)」
- 佐證:file: `/Users/enzo/orca/workspaces/lumos-toolchain/rulepack-review-bj/scripts/lumos:17511`
- 佐證:file: `/Users/enzo/orca/workspaces/lumos-toolchain/rulepack-review-bj/scripts/lumos:17602`

**F8**
severity: minor
blocking: 否(文字內部不一致,補數字即可)
- 段落:範圍 7
- 問題:說「七成、八成是本案自己的數字」,但同一段只出現九成(agree)與八成(false 佔比),全文找不到七成。
- 引句:「七成、八成是本案自己的數字,上線後照 REVISIT 回頭校準。」
- 佐證:file: `/Users/enzo/orca/workspaces/lumos-toolchain/rulepack-review-bj/governance/review-reports/規則包語意覆核級命中走盲判/r1-snapshot.md:100`

---

**逐節狀態**
- 前言、用詞:已讀。62 條、7 條出處不全、對應型錄列唯一這幾個數字我核對過,都對。規則數是 12 加 50,型錄有 473 列,3 列標「(人裁)」,而這 62 條規則沒有一條引用到它們。
- 範圍 1、2、6、8:已讀,除 F4 外無 finding。其他讀 lint.json 的地方都是依副檔名取值,不會迭代到 `review` 鍵,和計劃宣稱一致。
- 範圍 3:見 F5。
- 範圍 4:見 F1、F3、F7。
- 範圍 5:見 F1、F2、F3。
- 範圍 7:見 F2、F6、F8。
- 不做、實務隱患、依據來源、驗收條款、預期值表、天花板、審計修正紀錄:已讀,無 finding。內部交叉引用我都核對過。
- 回退:見 F1、F4。

**風險類**
- 金流、對外送出:無。只讀本機檔、跑本機 ast-grep、不連網。
- 不可逆:有。計劃寫「退提交即回原狀」,但實際上治理帳不可撤、放行檔沒有撤銷指令,見 F1。
- 守衛面:有,而且計劃自己承認。自動放行與誤判批次的隱患見 F1、F3、F5。

最嚴重 severity:major,blocking 5 條(F1–F5),minor 3 條(F6–F8)。
