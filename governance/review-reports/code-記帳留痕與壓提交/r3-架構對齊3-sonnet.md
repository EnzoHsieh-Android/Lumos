severity: clean

## 鏡頭範圍說明

席名:架構對齊3-記帳-sonnet。只判一件事:`cmd_canary` 裡新加的「code 開頭卻不是 code- 時照最嚴的當代碼審」這條從嚴接法,跟同檔既有三處也對 `_roster_kind(...)` 回 `None` 做出裁決的呼叫點(`_gated_seats_for`/`_disposal_security_step`、`_disposal_clause_step`、`_disposal_landing_step`)寫法與訊息一不一樣。不查第 2 點(壓提交失效訊息)本身對不對,那不在我的鏡頭內。

## 驗過的路徑(結論:一致,沒發現)

1. **判法統一走同一支函式,沒有另開一套規則**:`scripts/lumos:7717` `_rk = _roster_kind(str(loop)) if loop else "design"`,跟三個既有呼叫點(`scripts/lumos:17688`、`17812`、`17869`)一樣都是呼叫全檔唯一那支 `_roster_kind`(定義於 `scripts/lumos:9646`),沒有自己重寫 `startswith("code")` 之類的平行判法(這正是 r1 兩席折過的舊 bug 形狀,這次沒有復發)。

2. **「None 一律照最嚴的那一邊處理」的方向跟既有三處一致**:
   - `_gated_seats_for`(`scripts/lumos:17688-17692`):`kind == "design"` 才 skip,`None` 落下去跟 `"code"` 一樣要驗資安席(這裡「code」是嚴的一邊,因為它要求額外的資安席)。
   - `_disposal_clause_step`(`scripts/lumos:17812-17815`)與 `_disposal_landing_step`(`scripts/lumos:17869`):`kind == "code"` 才 skip,`None` 落下去跟 `"design"` 一樣要驗條款綁定/落點(這裡「design」才是嚴的一邊,因為 code 迴圈本來就被這兩步豁免)。
   - 新增的這處(`scripts/lumos:7717-7718`):`_rk != "design"` 才擋(即 `"code"` 與 `None` 同待遇),「code」是嚴的一邊(要求第一筆就帶 report+snapshot),「design」是寬的一邊(定錨後才強制)。
   三處既有呼叫點的共同規律是「None 分到不會被豁免的那一邊」,不是機械地「None 一律當 code」;新處恰好也落在這條規律上(這裡的嚴邊剛好也是 code),接法方向沒有走樣。

3. **訊息文字逐字沿用既有那句,沒有另造新措辭**:既有的 `_disposal_security_step`(`scripts/lumos:17743`)在 `_odd_id` 成立時印出的子句是「編號 code 開頭卻不是 code-,看不出是哪一種審查,照最嚴的當代碼審」;新處(`scripts/lumos:7719-7720`)在 `_rk` 既非 `"code"` 又非 `"design"`(即 `None`)時,組出的 `_what` 是 `f"迴圈 {loop}(編號 code 開頭卻不是 code-,看不出是哪一種審查,照最嚴的當代碼審)"`——核心子句逐字相同,只是外層包了「迴圈 {loop}(...)」而不是資安席那邊接在「這個迴圈沒有『{slot}』席的帳」後面,包法配合各自的上下文,措辭本體沒有分裂成兩套說法。真代碼審(`_rk == "code"`)的訊息仍是原本就有的「代碼審({loop})」,沒有被這次改動誤傷。

4. **實跑驗證三種情況各印什麼**(在 `/tmp` 建臨時 vault,唯讀操作,沒有動到 `/Users/enzo/harness/lumos-toolchain` 的 git 狀態):
   - `--loop code-demo-1`(真代碼審)缺 `--snapshot`→ `擋下:代碼審(code-demo-1)的每一筆記帳都要帶 --snapshot——…`,rc=2。
   - `--loop codeXreview-demo`(code 開頭無連字號,看不出種類)缺 `--snapshot`→ `擋下:迴圈 codeXreview-demo(編號 code 開頭卻不是 code-,看不出是哪一種審查,照最嚴的當代碼審)的每一筆記帳都要帶 --snapshot——…`,rc=2。
   - `--loop design-demo`(設計審)缺 `--snapshot`→ 不擋,正常記入,rc=0(定錨前的舊規則不變,相容)。
   三段輸出跟派工單第 24 行要我核對的「訊息在三種情況下各印什麼」對得上,也跟筆記 `docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md`(patch 第 17 行)裡「訊息照既有那幾處的說法講,不硬說它是代碼審」的描述一致。

5. **從嚴有沒有誤擋正當的「code 開頭、結構上就不帶快照」的記帳路徑**:新增的排除條件是 `outcome is None`(`scripts/lumos:7718`)。往前查 `scripts/lumos:7600-7604`,`--outcome` 本來就跟 `--round/--severity/--report/--snapshot/--intake/--findings` 互斥(帶 `--outcome` 就不准帶審查欄位),所以「只記結局的帳」結構上必定 `report`/`snapshot` 皆空,排除它不會放過真正該擋的漏帶。實跑 `--loop code-結局-demo --auditor orchestrator --outcome skipped`(不帶 report/snapshot)→ 正常記入,rc=0,沒被誤擋。除了 `--outcome` 這條,沒找到另一條「loop 是 code 開頭、結構上本來就不帶 report/snapshot」卻會被這道新擋誤傷的路徑。

6. **迴歸測試**(唯讀執行 `python3 scripts/test_lumos.py -k <關鍵字>`,不動 repo 狀態):`-k roster_kind`、`-k code_loop_record_requires_provenance`、`-k squash`、`-k roster`(65 案例)、`-k canary`(136 案例)、`-k code_loop`(27 案例)、`-k codeloop`(167 案例)、`-k disposal`(172 案例,直接跑到 `t_disposal_security_seat_required`/`t_disposal_clause_gate` 這幾支測我拿來對照的三個既有呼叫點本身)全數通過,沒有現有測試因這次的判法改動翻紅。

沒有發現跟既有三處呼叫點不一致的寫法或訊息;沒有發現被誤擋的正當記帳路徑。
