severity: major

我找到兩個推送前能躲過高風險代碼審的洞,一個 major、一個 minor。其餘手法擋住了。新增殘留這一關(`added`)對「分兩次推送先加索引列再加合約標記」和「刪帳」守得住,細節在最後。

實驗用 `scripts/test_lumos.py` 的 `_rc_repo` 當夾具,在暫存 git repo 跑 `lumos pitfalls --diff main..HEAD --json` 和 `lumos doctor --ci`,對的是 `/Users/enzo/orca/workspaces/lumos-toolchain/review-converge`(唯讀)。暫存目錄已刪。

**Finding 1:同句合約加第二條,新殘留躲過升級,doctor 也不報**

severity: major
blocking: 是 — 新殘留以 light 進主線沒過高風險代碼審,而且 doctor 也放過,等於外層看門和索引一致性檢查同時失效。
引句:「標記增減(加殘留、重審換戳記)、句尾多一個句號、多幾個空白都不改指紋」
攻擊步驟(輸入→結果):
1. 主線已有合法殘留:合約「下單不得超賣」帶 `[residual:Projects/a_計劃#d12]`,索引有 1 筆。
2. 在決策檔 `Projects/a_計劃` 加一筆新決策 d16,內容含 `checker:sonnet/2026-10-14`。
3. 在 `Systems/S` 的原合約行**之前**插一條同句合約:`KEY:★INVARIANT★ 下單不得超賣 [manual: 含 VIP 超賣例外] [audit:…] [residual:Projects/a_計劃#d16]`。
4. 指紋(`fp`)會剝掉 `[manual:]` 這類標籤,所以這條和原合約指紋相同(都是 `42853bf6c4856dcd`),也共用同一批問答。
5. 手寫索引,只留舊的那一筆,提交。
結果:
- `lumos pitfalls --diff main..HEAD` 回 `('light', '改動裡沒有程式檔(只有文件/資料/圖譜)')`,沒有升 high。
- `lumos doctor --ci` 的殘留與索引段完全沒報。
- 對照:真的跑 `lumos guard residual --reindex`,索引會長出 `[d16, d12]` 兩筆,而且 d16 那筆正是 `added`。

成因:
- 索引裡的條目有 `(node, fp)` 一樣的兩筆,doctor 把它們收進同一個 dict(`want`/`got` 以 `(node, fp)` 為鍵),後者蓋掉前者。
- 手寫索引只留 d12 那筆,比對時兩邊都只剩 d12,對得上。
- pitfalls 的分級只信這份被手改的索引,所以看不出新增。

建議:
- doctor 改成比整份清單(多重集合),不要用 `(node, fp)` 當字典鍵。
- 或讓索引條目的鍵帶殘留指標。

佐證:
- `scripts/lumos:19336`(doctor 的 `want`/`got` 字典)
- `scripts/lumos:18885`(`_residual_claim_fp` 剝標籤)
- `scripts/lumos:44596`(`_residual_tier_hits`)

**Finding 2:本機 `git replace` 讓起點讀到假索引,新增殘留被判 light**

severity: major
blocking: 是 — 推送前的守衛被本機的 replace refs 繞過,CI 的 `code-loop check` 是推送「後」才補查,擋不到已上主線。
引句:「用 git cat-file blob 讀原始位元組:不經 diff,所以 .gitattributes 標 -diff、textconv、帳裡的 NUL 位元組都影響不了」
攻擊步驟(輸入→結果):
1. 分支 feat 用 `guard residual --add` 正常新增殘留。此時 `pitfalls` 回 `high`,理由是「這次推送新增了殘留」。
2. 造一個假起點 commit:用 main 的樹,加上含該殘留的 `governance/residual-index.json`,父親取 `main^`。
3. 執行 `git replace <main 的 sha> <假 commit>`。
4. 再跑 `pitfalls --diff main..HEAD`:回 `('light', '改動裡沒有程式檔(只有文件/資料/圖譜)')`。
5. 實際推出去的物件沒有變,變的只是本機讀法。

成因:`git show`、`cat-file`、`ls-tree`、`diff` 都吃 replace refs,`scripts/lumos` 裡沒有 `GIT_NO_REPLACE_OBJECTS` 或 `--no-replace-objects`。
連帶影響:兩版治理帳比對(`_residual_ask_rows_at`)讀的也是 replace 過的版本,同樣被騙,可以藉此讓刪掉的 residual-ask 列不被算到。

建議:
- 這幾處 git 呼叫都設環境變數 `GIT_NO_REPLACE_OBJECTS=1`。
- 或在 `pitfalls` 入口發現 `refs/replace/` 非空就直接升 high。

佐證:
- `scripts/lumos:44495`(`_residual_index_read_at`)
- `scripts/lumos:44542`(`_residual_ask_rows_at`)

**Finding 3:把新反例塞進既有殘留決策,不改身分鍵就不升**

severity: minor
blocking: 否 — 只拓寬免測範圍,日後改到被守的程式仍會升 high 而且審查席看得到決策,風險有後續一關擋著。
引句:「殘留的身分是(節點、合約指紋、殘留指標)(r3 G3)」
攻擊步驟(輸入→結果):
1. 主線已有殘留 `d12`,決策原寫反例 c1、c3。
2. 分支用 `residual-ask` 新增 c2、c9 兩筆 untestable 問答,再把決策檔的「(反例 c1、c3)」改成「(反例 c1、c2、c3、c9)」。
3. 索引沒動,身分鍵 `(node, fp, 殘留指標)` 沒變。
結果:`pitfalls` 回 `light`,`doctor --ci` 的殘留與索引段沒報。新免測反例沒過高風險代碼審就拿到殘留。
建議:把決策內容或反例集合的雜湊放進身分鍵,或在索引記反例清單。

**檢查過、沒找到洞的路徑**
- 先加合約標記、不碰索引:`pitfalls` 回 light,但 `doctor --ci` 報「殘留索引跟圖譜對不上」。
- 先加索引列、再加標記:索引一動就是 `added` 或 `head_bad`,當次就升 high。
- 讀不出的頂端索引:有動過索引就升 high。
- `.gitattributes` 的 `-diff`、`filter`、`textconv`:`cat-file blob` 讀原始位元組,不受影響。
- 帳搬檔名:帳路徑寫死成 `docs/.governance-log.jsonl`,搬走會被算成刪列。
- 改寫帳列的格式(例如跳脫字元):整列位元組對不上,會被算成少了列。
- 一個提交內加了又拿掉的帳列:淨變化為零,而且本來就沒有舊版可比。

最高等級 major,blocking 2 條。
