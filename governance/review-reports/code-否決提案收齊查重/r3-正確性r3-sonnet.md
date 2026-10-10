severity: minor

## F1 子句切點把「翻案:原本不做 X」切成兩句,推翻的字眼和不做被分開,誤收
severity: minor
blocking: 否
引句:「逐子句看,有一句講不做、而且同一句沒有先講推翻/翻案,就算(推翻舊否決的那句不算,別句的停案照算)。」
佐證:file: `scripts/lumos:18181`(`_rejections_is_nogo`;切點是 `scripts/lumos:31271` 的 `_NS_NEG_SEG_CUT_RE`,含 `:：()（）`)
歸因:有證據的修復回歸
失敗場景:
1. 有效決策寫成 `content: 翻案:原本不做X,現在改做`,結論是「做」。
2. 修補後 `_NS_NEG_SEG_CUT_RE.split` 在「:」和「,」處切開,得到「翻案」、「原本不做X」、「現在改做」三子句。
3. 第二子句有不做、沒有推翻,`_rejections_is_nogo` 回真,這條被當成舊否決列出。
4. 修補前整串一起看,翻案排在不做之前,所以排除。
5. 同型寫法會一起誤收:「推翻 2026-08-17 的決定(原先:不做 X),改做」,括號和冒號都是切點。
6. 規格文字寫明「會有誤收,讀的人自己判」,所以只標 minor。
7. 真圖譜前後輸出逐字相同(diff 為空),目前沒有實害。
- 修前(09ffec28):`python3.14 scripts/lumos --vault $V rejections | grep p.md`,沒有 d3。
- 修後(25ee639c):同一命令印出 `Projects/p.md#d3: 翻案:原本不做X,現在改做`。
- 順帶:`實測推翻方案A所以不採A`(推翻在不採之前、同一子句、沒逗號)修前修後都不收。這是「同一子句推翻在前」規則本身的漏收,不是修補造成的。

## F2 內文是多行區塊(`|`)時,不做字樣在第二行,清單只印第一行
severity: minor
blocking: 否
引句:「"kind": "no-go-decision", "content": first_line(str(d.get("content", "")), 160),」
佐證:file: `scripts/lumos:18128`(`parse_decisions` 把區塊純量存成含 `\n` 的字串),判定在 `scripts/lumos:18185`
歸因:有證據的原有漏查
失敗場景:
1. 決策 `content: |` 兩行,第一行「第一行普通說明」,第二行「第二行不做Z方案」。
2. 判定用整串的前 120 字,所以第二行的「不做」命中。
3. 輸出的 `first_line` 只取第一行,清單印 `Projects/p.md#d1: 第一行普通說明`,看不到命中的字,讀的人無從判斷為什麼被收。
4. 修前、修後輸出都是這一行,所以不是修補造成。
5. 真圖譜目前沒有這種決策:我掃過,「第一行沒有關鍵字、第二行之後才有」的有效決策為 0 條。

## 三問與同一案例證據

**① 原問題的修復效果(各組 repair,都有修前修後命令)**
- 組 1 去重鍵型別
  - 命令:用測試佈景 `_rej_vault()` 的 vault 跑 `python3.14 scripts/lumos --vault $V rejections --json`。
  - 修前 09ffec28:rc=1,`TypeError: cannot use 'tuple' as a set element (unhashable type: 'list')`。
  - 修後 25ee639c:rc=0,`total` 21,context 依序為 `d2`、`d2`、`None`、`None`、`d2,d3`。
- 組 2 不做的判法
  - `推翻了丙的舊方案;戌方案停案`:修前不收,修後收。
  - 引號開在 120 字內、收在 120 字外的 `亥…「不做亥方案…」`:修前誤收,修後不收。
- 組 3
  - 正文 WHY 走 `SYMBOL_RE`,真圖譜 98 條正文 WHY、4 條帶不選,收集結果與修前相同。
  - 我另掃過這 98 條:沒有「帶不選卻解析失敗被丟掉」的。
- 組 4
  - 真圖譜 `rejections` 修前修後輸出逐字相同(46965 bytes)。
  - `t_rejections_retired_statuses_in_enum` 通過。
- 組 5:空圖譜與有資料都是 `{"total","results"}`,測試通過。
- 組 6:條款措辭與 `_spec_gate_print_rejections` 的行為一致(出錯不印筆數、印一行略過原因)。
- 測試:`-k rejections` 46 過 0 敗,`-k decisions_superseded` 2 過,`-k docs_enumeration` 12 過,`-k spec_gate` 104 過,`-k drift` 1053 過。

**preserve 與相鄰路徑**
- `lumos decisions --superseded`:真圖譜修前修後 `cmp` 一致(44 行)。測試佈景輸出為 `→ ?`、`→ []`、`→ ['d2', 'd3']`、純量 `→ d2`,與規格相符。
- 「推翻 X 的刻意不做」型:真圖譜的 `評測尺翻案_計劃#d1` 正確被排除,真圖譜只有這 1 條被排除,沒有被誤殺的。
- 開頭停案後文提推翻、引號裡的否決、120 字之後、四個關鍵字、`- WHY:`、圍欄、沒有不選的 WHY:這些保留案例都由測試佈景覆蓋並通過。
- 我另外確認:引號開在 120 字內、收在 120 字外的案例,修後不收。
- 規格閘的 `--push-check` 走 `_spec_gate_push_check`,不經過 `_spec_gate_front`,所以多印的那一行不會進 pre-push 認 light 的 grep(`scripts/hooks/pre-push:432`)。
- 效能:真圖譜 0.9 秒。我另造 5000 條決策加 2 萬個巢狀 `[不選:` 的 WHY 行,0.72 秒、rc 0。

**② 修補處的正常、錯誤、相鄰呼叫路徑**
- 正常:同上,保留案例都成立。
- 錯誤路徑:測試以 `side_effect` 讓收集丟 ValueError,規格閘印略過原因、rc 與正常時相同。
- 讀不到檔:`env_text` 回 None 時用 `or ""` 接住,不會例外。
- 相鄰路徑:新增的 F1 就是這裡的退步,F2 是原有的。
- 其餘見上。

**③ 新發現同一案例的前後**
- F1:修前不收、修後收(見 F1)。
- F2:修前修後都一樣,不能歸因於修補。

## 圖譜固定席判定
- `lumos-cli-read` 的 ★INVARIANT★(search 預設排除 superseded):不影響。diff 沒碰 `search`,只新增 `rejections` 和抽出 `_superseded_decisions`。
- `design-loop`、`bound-tests-gate`、`guard-kill`、`授權與歸屬`、`測試假綠形態`、`lumos-cli-lifecycle`:不影響。
  - 這些合約說的是處置閘第五步、固定席測試真跑、guard kill、授權檔、還原翻紅釘、re-inject。
  - 本 diff 沒動這些路徑。
  - 規格閘只多印一行,不改判定與 rc;push-check 路徑不經過它。
  - 主程式 SPDX 檔頭沒變。
- 未驗範圍:`-k note_shape` 我跑了但沒等到結果。diff 沒修改 `_NS_NEG_SEG_CUT_RE` 與 `_drift_mask_quotes`,drift 測試 1053 過,所以判存量漂移與筆記形狀檢查的原使用者沒被動到。

**本案特定鏡頭 4**
- 兩個共用件都只被唯讀呼叫,diff 沒有任何 hunk 改動它們。
- 遮蔽佔位字 `\x01` 不在切點集合內,不會製造新切點。引號內的標點被整段遮掉,有利於不被切碎。
- 語意落差只有兩處:一是 F1 的冒號、括號切點;二是半形 `"` 不被 `_drift_mask_quotes` 遮,而 `_NS_NEG_QUOTES` 認得。後者規格只寫全形引號,所以不標。

共 2 條 finding,最高一條是 F1
