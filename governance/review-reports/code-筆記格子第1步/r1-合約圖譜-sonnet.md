severity: major

固定席筆記(note_shape 相關子集 178 條測試全過)沒有被破壞。核對計劃〈擋〉的 [S1]–[S10]、[S15] 時,我找到兩處不符:一處 major,一處 minor。我另外實跑了 `-k t_slots` 子集,88 條通過,但它蓋不到這兩處。`--slots` 參數有永久保留。

**G1** 推送時,上線前寫的行事後補欄位,被當成新寫而擋下(違反 S6「範圍裡格子還沒上線的提交寫的行也算舊行」)
severity: major
blocking: 是 — 這是計劃明寫要豁免的情境,開擋後會誤擋;但目前掛鉤沒帶 `--slots`,上線當下不影響任何人
引句:「        for texts in (sink.get("old_by") or {}).values():」
- 原因:`_ns_slots_old_lines` 只把「終點版本裡、不在 `texts2` 的行」與 `old_by` 當舊行。
  - 提交 A(格子上線前)寫 `WHY:句子`。
  - 提交 B(上線後)只補 `[applies:x]`。
  - 終點只剩補欄位後的版本,它被 B 收進 `texts2`。A 寫的原文既不在終點、也沒進 `old_by`(`old_by` 只收筆記形狀上線前的提交),所以舊行鍵對不上,B 這行被當成新寫。
- 重現(clone 後在 `scripts/` 下 `import test_lumos as T`):
  - 建 repo,commit pre(`WHY:上線前寫的句子`),再 commit 一個帶 `note-shape --staged --slots` 的 pre-commit 掛鉤,再 commit 補 `[applies:x]`。
  - 執行 `T._ns(r,"--diff",f"{base}..{tip}")`,預期 rc=0,實際 rc=1,擋下「缺 [出處:]、[因:]」。
- 缺口:`t_slots_edited_old_line` 只測 `--staged`,沒有任何測試走推送路徑的這一支,所以不會翻紅。
- 修法方向:`_notelines_range_added` 對「沒帶 mark2 的提交」寫的行另收一份,併進舊行。

**G2** 搬移或改名時,多行(有續行)的舊條目被誤擋(違反 S6「同次刪掉的別篇行也算、跟著改名」)
severity: major
blocking: 是 — 同一個 S6 情境,條目有續行就誤擋;同樣只在開擋後才會發生
引句:「        if ln.startswith("-") and not ln.startswith("---"):」
- 原因:`_ns_deleted_summary_lines` 取的是 diff 裡的實體行,逐行比對。新行的鍵來自 `_ns_summary_logical` 接回續行後的整行,兩邊核心一句不同,對不上。
- 重現:
  - 筆記 A 的摘要有 `WHY:舊的一句話很長` 加一行縮排續行 `    接續的第二行說明`,先 commit。
  - 再把這兩行搬到新筆記 B,然後 `git add`。
  - 執行 `note-shape --staged --slots`,rc=1,擋下 `B.md:14  缺 [出處:]、[因:]`。
  - 單行版本搬移同樣操作,rc=0。
- 改名加改動時,舊路徑讀不到,只剩同一套實體行,結果一樣(未另外實跑)。
- 修法方向:被刪的行也要用跟新行同一套邏輯行(接回續行)來算鍵。

**G3** 單次跳過算格子欄位時,多圖譜專案可能選錯圖譜
severity: minor
blocking: 否 — 只影響治理帳裡跳過事件的格子欄位,不影響放行
引句:「        sv = _ns_slots_violations(root, True, base_where, "index", "docs/" + vaults[0], slots)」
- `_ns_skip_slot_extra` 固定取第一個圖譜(`vaults[0]`)。
- 正常路徑在 `cmd_note_shape` 的 `vault_rel` 先看工作目錄所在的圖譜(`_vault_in`,位置在 `scripts/lumos` 約 27067 行),再退回第一個。
- 多圖譜專案在第二個圖譜提交時,跳過事件的 `slots_lines` 是算第一個圖譜的。
- 沒有實跑,是讀碼得出。

**逐條對照〈擋〉與 [S1]–[S10]、[S15]**
- S1–S5、S7(提交時不帶 `--slots` 不跑)、S9、S10、S15 有實作,對應測試也咬得到。S10 的「工具樣板豁免」實際只有 guard 預告句與轉正句,屬於同一套清單。
- 兩個弱點:
  - S4 的 SEE 夾字被擋,其實是舊規則(「SEE 只放連結」)擋的。格子路徑在 `_ns_slot_line_problems` 開頭的 `m.group(1) not in _SLOT_REQUIRED` 就放過 SEE,所以 `t_slots_fact_required` ④ 沒測到格子規則本身。結果沒錯,只是測試不咬格子。
  - S7 測試 ⑤(掛鉤範本裡格子記號最多出現一次)寫的是 `<= 1`,目前範本一次都沒有也過。這是刻意的「這次不開擋」,但沒有任何測試釘住開擋後「恰好一次」。
- S6 的測試缺口:沒有推送路徑,也沒有改名或多行案例,G1、G2 因此都漏掉。
- 〈回退〉第 1 步:`--slots` 永久保留已做到,`ns_p.add_argument("--slots", …)` 的 help 註明永不移除。沒有專門釘它的測試,但所有 `t_slots_*` 都帶它,移除會連帶全紅。

**筆記與程式一致性**
- `Systems/筆記內容閘` 新增的那條 WHY 寫「推送對範圍起點,再加範圍裡刪掉的行與格子上線前的提交寫的行」,G1 的情境與這句不符;G2 則與該筆記沒寫到的跨篇搬移邏輯有關。
- 這條 WHY 沒提 `note_shape.slots` 子開關、治理帳欄位、doctor 提醒,這些只在計劃裡有。這不算矛盾。
- 計劃檔的進度行說「實作中」、掛鉤範本未帶 `--slots`,與程式一致。

**其他節點的固定席**
- 共用抽取:`_notelines_new` / `_notelines_range_added` / `_notelines_range_cand` 只多了預設為 None 的 `mark2` / `sink`。`note-audit` 和既有呼叫端不傳這兩個參數,行為不變。`_notelines_live_sets` 與原本內嵌的邏輯等價。
- 既有的筆記形狀規則、否定現況句、前綴提醒:`_note_shape_eval` 只在 `slots is not None` 時多放兩個鍵,否定現況句與前綴提醒的收集與輸出順序不變。
- 報告函式:`_note_shape_report` 多了 `slot` 參數。只有格子違規時,`count` 字串會變成「新違規 0 條、格子缺漏 N 行」,既有機器消費端沒有看到依賴它的。

最高嚴重度 major,blocking 2 條
