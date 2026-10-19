severity: minor

整體判斷:手冊、SKILL、reference 現行段與 Systems 筆記跟實際行為大致對得上,沒有 major。我開了 `scripts/lumos loop next`、`canary record --help`、`pitfalls --diff` 實跑對照,也跑了 `lumos lint` 檢查六篇改到的節點,結果如下。

**已核對、判無問題的項目**
- **循序舊說法**:`grep 循序 skills/ scripts/templates/` 後,現行段(SKILL 第 12、29、67 行、06 第 5 與 41 行、05 與 design-loop 護欄)都已改。剩下的 `reference.md:438/611/619/628` 在「歷史與停用」「入口頁舊版全文」段,計劃明說不動,可接受。
- **範本與提醒**:
  - 全新 code standard 的 `record_cmd` 與 `disposal_cmd` 都帶 `--round r1`。
  - `canary_type` 是 `{slot1: …}`,文字輸出有印 `disposal_cmd`。
  - 範本的 `--snapshot` 與 `--scope-lines` 佔位字有寫拆包審。
  - high 代碼審印兩條資安與記帳順序提醒,設計審首輪印兩條先排乾再凍結的提醒。
  - `pitfalls` 的 tier 行下面多印「這級仍要代碼審」。
  - 以上都跟手冊和筆記的說法一致。
- **名冊與測試**:`("code","standard")` 的 mode 已是 `single`,對上筆記。計劃 31 條驗收條款綁的測試全部存在,筆記提到的函式名也都在程式裡。
- **d3 翻案**:d3 推翻的是計劃自己原寫的「`none` 全面當空集合」,不是載體零引句那案。載體零引句的裁定(`none` 可以是真實 ID)被保住,計劃第 2 節與筆記都指回該案,沒有漏。
- **形狀**:摘要行前綴和必有鍵齊全,六篇 `lumos lint` 都是 0 問題,沒有新增程式檔,每支檔有家沒變。
- **回頭條件**:帶 `- ` 的 `REVISIT:2026-12-15` 符合 `_REVISIT_MARK_RE`,doctor 認得。

**圖譜固定席**
- **loop-convergence-recording、pitfalls-code-loop**:新增的是輪次規則、集合 none、提示與 `pitfalls` 輸出,「載體最後記」判斷式沒改,只多一句提示文字,不破壞 ★RISK★ 所述行為。
- **canary-record 未落盤事件**:這份 diff 沒碰落盤路徑,不影響。
- **design-loop(★INVARIANT★ 處置閘第五步)**:只加了 `loop next` 提醒和 `spec-freeze` 訊息半句,審材必須是 .md 計劃那條判斷不動,不影響。
- **lumos-cli-read、guard-kill、bound-tests-gate、lumos-cli-lifecycle**:這份 docs 包沒動到 search、guard kill、bound-tests 或 re-inject 的行為,不影響。

**Finding**

1. 跑滿回顧那邊的舊說法沒有指向新行為
severity: minor
   - blocking: 否
   - **哪裡:**
     - `Projects/審查跑滿回顧_計劃.md:163` 的 S17 和 `:208` 仍寫「沒有人裁紀錄的迴圈不受影響」「行為跟現狀相同」。
     - `Systems/loop-convergence-recording.md` 的 d7 WHY 仍寫「沒有人裁紀錄的迴圈行為不變」。
   - **具體例:**
     - 輸入:沒有人裁紀錄、這個編號有一列輪次不是字串的迴圈,再記一筆。
     - 舊說法:不受影響。
     - 實際:`canary record` 被輪次規則擋(rc2,見 `scripts/test_lumos.py:94623` 改過的斷言)。
   - **漏掉的部分:** 翻案只寫在新計劃第 215 行,舊計劃和舊筆記都沒標,三個月後從 S17 進來的人會被舊句子誤導。
   - 引句:「本案帳壞就擋之後,那種迴圈改由輪次規則擋(不落 cap-ledger-bad,跟跑滿回顧無關)」

2. 被推翻的「standard 代碼審走循序」只有新計劃單向回應
severity: minor
   - blocking: 否
   - **哪裡:**
     - `Projects/循序codeloop-tier錨定_計劃.md` 是 status done,summary 仍寫「code∧standard∧無 --round 循序=設計行為」,也沒有翻案指標。
     - `Systems/design-loop.md:60` 的 KEY 仍寫「單席循序一輪一筆處置帳→--disposal」。
   - **漏掉的部分:** 新計劃第 1 節〈回應既有決策〉有交代,但舊節點沒指過來,從舊計劃進來的人看不到 d1 把新迴圈改成每筆帶輪次。
   - 引句:「只讓新迴圈不再進這個形狀」

3. `canary record --help` 沒跟手冊同步
severity: minor
   - blocking: 否
   - **哪裡:**
     - 手冊叫人在 `--folded-set`/`--accepted-set` 沒有時寫 none,實跑的 help 只寫「折入計劃節點的 id 子集」「附理由放行的 id 子集」。
     - `--regression-set` 的 help 沒說只收 code-,也沒說 none 規則。
     - `r1-code.patch` 沒改這幾段 help。
   - **漏掉的部分:** 只看 help 的人不知道有 none 這個寫法,設計審帶 `--regression-set` 會被擋也沒預告。
   - 引句:「沒有就寫 none(等於空集合;none 不能跟其他 id 寫在一起)」

4. 計劃白話段的條數對不上
severity: minor
   - blocking: 否
   - **哪裡:** `Projects/記帳與迴圈工具小修_計劃.md` 白話段說「再順手修九個…小地方」,實際列出 8 項(none、regression-set、證據型別、留痕提醒、pitfalls、拆包審、資安包與順序、首輪先排乾)。範圍節 ②–⑨ 也是 8 項。
   - 引句:「當成 id、設計審收了用不到的欄位、表態證據型別錯看不懂、留痕入帳後沒提醒不能改、pitfalls 判 standard 沒講還要審、拆包審填錯整份、資安包與載體最後記的順序、首輪先排乾再凍結」

另外,`Issues/代碼審next把新處置帳誤判舊panel` 還是 status open。計劃只寫「可以順手關」,所以我沒另列為 finding。

最嚴重 severity:minor;blocking 共 0 條。
