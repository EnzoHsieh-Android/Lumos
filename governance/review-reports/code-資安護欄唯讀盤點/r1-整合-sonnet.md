severity: major

實測結果:
- `python3.14 scripts/lumos doctor --ci` 的 rc 是 0(907 篇、0 issues)。
- `note-shape --diff ec4c6307..20293afe` 的 rc 是 0,只有「測試索引對不上,交給 CI」的提醒。
- 四篇被改的筆記 `lumos lint` 都是 0 問題。
- `spec-gate` 顯示條款 13 條全綁、全綠,相依回歸 `t_search_forget_superseded` 綠。
- `test_lumos.py -k seclist` 是 203 passed。
- 在本 repo 跑 `security list --json`:rc 0、待分類合約 35 條、未登記 flag 節點 2 篇、coverage unknown、registration_complete=false。這跟 Verification 紀錄寫的一致。
- 我跑 spec-gate 時,它在 `docs/.canary-log.jsonl` 多追加了一行(SPEC-e3fe6b0f)。我已經把那一行手動刪回,`git status` 現在是乾淨的。

## 逐項核對結論

**七處保守做法(d1)和程式一致:**
- 零登記時 rc 0,`registration_complete` 是 false。
- 只有候選的入口同時列 `unmapped` 和 `candidate_only`。
- 任何捷徑(不分檔名)都記 `symlink_rejected` 並退出 2。
- 讀取中被改的檔內容不採用,檔案屬性一不符就 return。
- 例外過期只進 `issues`,rc 0;例外的決策作廢進 `errors`,rc 2。

**其他核對結果:**
- JSON 頂層欄位齊全,逐入口的欄位也齊全。
- 母計劃 d8、d9 的內容和 Q3/Q4 的 decision 指向互相對得上。
- `_visible_lines` 抽成 `_fence_regions` 的行為跟舊版等價。
- `Systems/lumos-cli-read` 的 search 不排除 stale 合約沒被碰,search 的程式碼這次沒改。

## Findings

### 1. 登記塊裡的 inventory 或 source 放了陣列值,指令會整個崩掉:rc 1、traceback、stdout 空

severity: major
blocking: 是

- 位置:`scripts/lumos` 的 `_secinv_inventory_problems`、`_secinv_inv_items`、`_sc_source`(r1-lumos.patch 的 `_secinv_inv_items` 與 `_sc_source`)。
- 問題:
  - `_secinv_inv_items` 在 id 不是字串時,先記了 `ip.append(...)`,卻仍然 `ids.append(it.get("id"))`。接著 `set(...)` 或 `x not in aset` 碰到 list 就丟 `TypeError`。
  - `_sc_source` 的 `{...}.get(kind)` 在 `kind` 是 list 時也丟 `TypeError`。
- 違反的契約:計劃〈CLI契約〉寫「2 表示輸入、schema、引用或讀取不完整」、「JSON stdout 始終僅一個可解析物件」,S2 寫「不靜默漏項」。
- 重現(臨時 vault,`Systems/A.md` 內一塊 `lumos-security-v1`):

| 輸入 | 指令 | 預期 | 實際 |
|---|---|---|---|
| inventory 的 `assets: [{"id":["x"],"description":"d"}]` | `lumos --vault v1 security list --json` | rc 2,單一 JSON 物件,errors 有 `inventory_error` | rc 1,traceback `TypeError: cannot use 'list' as a set element`,stdout 空 |
| surfaces 的 `asset_ids: [["a"]]` | 同上 | 同上 | rc 1,`TypeError ... x not in aset` |
| control 的 `"source":{"kind":["x"]}` | 同上 | rc 2,`invalid_record` | rc 1,`TypeError: cannot use 'list' as a dict key` |

- 測試缺口:203 條斷言全綠,沒有一條打到非字串的 id 或 kind。
- 因為整份盤點在這裡崩掉,一篇寫壞的筆記會讓其他所有正常護欄都列不出來。這是 schema 錯誤退出 2 與其他項保留的反例。

引句:「aset = set(_secinv_inv_items(cand["assets"], ("id", "description"), "assets", ip))」
引句:「"requirement": ("kind", "claim", "decision_ref")}.get(kind)」

### 2. 母計劃的「接手先讀」和多處正文還說 Q3、Q4 沒決,跟同檔 d8、d9 相反

severity: major
blocking: 是

- 位置:`Projects/消費專案產品安全Brief與證據驗收_計劃.md`。本 diff 把 Q3、Q4 改成「已決」並新增 d8、d9,但沒有同步改正文,這些行在目前簽出的檔案裡:
  - 第 118 行:「P0 的隔離資格與成本確認仍依 Q3 處理」。
  - 第 120 行:「有效方向依d1–d3、d5、d6、d7……Q3仍阻塞新的安全故障執行;Q4阻塞正式交付放行／強制閘接線……新方向不批准故障執行、採購或正式接線」。這句沒列 d8、d9,字面上等於說它們不是核可方向。
  - 第 192 行:「Q3仍限制新的故障執行,Q4仍限制正式接線」。
  - 第 211 行:「Q3核可後補P1故障……」。
  - 第 321 行:「先完成Q3的隔離副本及執行預算核可,才跑故障翻紅／還原」。
  - 第 364 行:「對母計劃跑規格閘仍會阻塞;不得……假稱Q3已決」。
  - 第 479 行:「Q3 才可從待查移為已決／已驗」。
- 問題:三個月後的接手者讀入口段,會得到跟 frontmatter 已記錄的使用者核可相反的狀態。例如他會以為 P1 故障執行與正式交付閘裁定都還沒核可,而它們已核可。
- 重現:`grep -n "Q3\|Q4" docs/lumos-toolchain-knowledge/Projects/消費專案產品安全Brief與證據驗收_計劃.md` 對照第 99、105 行的 d8、d9。
- 程式碼答不了這件事,依 CLAUDE.md 第 3 條,有決策紀錄的 d8、d9 才是依據,正文是線索。所以該改的是正文。
- 第 120 行是「接手先讀」的主入口,所以我標 major。其他幾行是同一個根因。

引句:「Q1–Q2已依d1決定；Q3仍阻塞新的安全故障執行；Q4阻塞正式交付放行／強制閘接線，不阻塞唯讀盤點設計。」

### 3. 子計劃「本次不改 S1–S13、不改母計劃 Q3/Q4」的句子已過期,凍結的設計審指紋也對不上

severity: minor
blocking: 否

- 位置:`Projects/資安護欄唯讀盤點_計劃.md` 的〈目的與授權〉與〈首案登記與實作順序〉第 5 點。
- 問題:
  - 這份 diff 同時改了 S1–S13 的綁定,新增 d1、Q1、Q2,但文中仍寫「本次僅補此指路與成熟度說明,不改本篇schema、輸出契約或S1–S13」,和「不改母計劃Q3／Q4」。
  - `governance/replay/資安護欄唯讀盤點/verdict.json` 的 `spec_sha` 是 f78f0678…,那是設計審通過時的舊文字。
  - 文中沒標明「凍結後新增了哪些段落」,接手者要自己比對。
- 為什麼只算 minor:S 條款文字本身沒變,只有綁定從 `[manual:]` 換成 `[test:]`,d1 也有記錄。這是措辭精度與可追溯性的問題。

引句:「本次僅補此指路與成熟度說明，不改本篇schema、輸出契約或S1–S13；既有凍結卷證保持原樣」

### 4. 筆記說「測試守住」的範圍比實際大

severity: minor
blocking: 否

- 位置:`Verification/2026-10-19_資安護欄唯讀盤點實作.md`。
- 問題:紀錄寫「十三條驗收條款都有測試守著,而且把關鍵守衛逐一弄壞時對應測試會紅」。但 inventory 與 source 的畸形形狀(finding 1)根本沒被測到。
- `valid_under` 只說證「S1–S13 隔離樣本與故障變體」,沒有寫明「欄位型別畸形」不在範圍。
- 修好 finding 1 之後,補一行「未驗:欄位值型別畸形」即可。

引句:「`lumos security list` 的十三條驗收條款都有測試守著,而且把關鍵守衛逐一弄壞時對應測試會紅。」

## 圖譜鏡頭(固定席)

- `lumos-cli-read` ★INVARIANT★(search 不排除 stale):不影響。diff 沒碰 search,`_visible_lines` 是保行為重構,`t_search_forget_superseded` 綠。
- `design-loop` ★INVARIANT★(處置閘第五步):不影響,diff 沒碰 `loop`、處置閘的程式。
- `lumos-cli-lifecycle`(re-inject)與 `guard-kill`(rc 優先序、`--json` 純度):不影響。`security` 子命令是獨立分派,排在一般 `Env(vault)` 之前,沒碰這兩處。
- `測試假綠形態` ★INVARIANT★(還原翻紅釘要配前置斷言):finding 1 是其反例,即測試沒走到畸形形狀。
- 其餘固定席(`loop-convergence-recording`、`pitfalls-code-loop`、`reversibility-governance-ledger` 等 ★RISK★ 節點):不影響,只共用 `scripts/lumos` 這支檔。
- 每支檔有家:`scripts/lumos` 的家 `Systems/lumos-cli-read` 的 `about_code` 有列。計劃 `lands_in` 是 `Systems/lumos-cli-read`,跟實作落點一致。

最嚴重 severity:major,blocking 共 2 條(finding 1、finding 2)。
