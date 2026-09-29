severity: major

## F1 七題的觸發集合未定義，硬閘適用範圍無法一致實作
severity: major
blocking: 是——觸發字直接決定哪些提交必須表態並被推送閘阻擋，不能留給實作者自行發明。
引句:「**觸發字原則**:沿用範式詞加反面詞;要具體到不誤傷」

Spec 只列七題的自然語言與抽象原則，沒有逐題列出 `when`、`when_raw` 或完整的正反樣本。S5 又只要求「每題各給」樣本，沒有規定那些樣本的內容，因此測試作者仍在測自己選的觸發集合。

file: `scripts/lumos:20015` 現有題表的合約是每題必須明列 `when`；`_STACK_TRIGGERS` 直接由這些字串編譯。

file: `scripts/lumos:20294` `_stack_applicability` 逐題跑這組 regex，命中結果直接成為 `applicable`，後續表態閘據此阻擋。

具體失敗場景：非測試 Python 檔新增 `Path("state.json").write_text(json.dumps(value))`。實作者甲把 `write_text` 列入 `ds-partial-write.when`，結果 `ds-partial-write` 適用、缺表態時推送被擋；實作者乙只採 S1 明示的 `os.replace(` 與開檔模式，結果同一提交沒有任何 `ds-` 題適用。兩者都能自行挑選 S5 的命中樣本而通過現有條款，產品行為卻相反。

## F2 逃生口與留痕承諾不成立，無 docs 專案會被推向全域關閘或 no-verify
severity: major
blocking: 是——新增題組擴大已知死結的觸發面，且規格指定的觀測帳無法記錄受害案例，沒有可審計的逐次逃生路徑。
引句:「誤擋的逃生口沿用既有的 `na`(附理由)與設定檔 `stack_questions.gate`(all/high-only/off);擋與放都進治理帳。」

file: `scripts/lumos:31446` 表態寫側要求 repo 必須存在 `docs/`；沒有時直接拒寫，因此 `na` 不是這類專案可用的逃生口。

file: `scripts/lumos:31658` `gate=off` 與非 high 的 `high-only` 直接返回放行，不產生表態事件。

file: `scripts/lumos:32304` `code-loop check` 只在 `blocked` 時寫閘事件，設定造成的放行沒有對應事件，與「擋與放都進治理帳」不符。

file: `scripts/lumos:880` 沒有 `docs/` 時，連 blocked 事件也直接回傳 `None`；因此 spec 最後要求從治理帳觀察「沒有 docs/ 被表態閘擋」的 REVISIT 永遠看不到目標事件。

file: `docs/lumos-toolchain-knowledge/Issues/沒有圖譜的專案答不完表態題.md:24` 既有 Issue 已確認此類 repo 會陷入「閘要求表態、表態又寫不進去」的死結；第 26 行記載實務結果是改走 `--no-verify`。

具體失敗場景：沒有 `docs/` 的 repo 在程式檔新增 `os.replace(...)`。依 S1，`ds-partial-write` 適用；`code-loop check` 因缺表態擋下，但 `code-loop dispositions` 因沒有 `docs/` 回 rc2。作者只能提交 `stack_questions.gate=off`，永久關閉所有棧別與資料題且沒有放行事件，或使用 `git push --no-verify` 跳過整組本機閘。11 月的治理帳檢查仍會得到零筆，無法觸發計劃承諾的升級條件。

### 逐節覆核

- Frontmatter、summary、`lands_in`、`related`：已讀，所有交叉引用均可解析，無 finding。
- 現況：已讀，無 finding。
- 設計：已讀；觸發集合缺口見 F1，其餘無 finding。
- 驗收條款：已讀；S5 無法固定產品行為，見 F1，其餘無 finding。
- 回退：已讀，無 finding。
- 實務隱患：已讀；自我治理逃生與留痕失效見 F2。金流、對外送出、不可逆、資源與並發風險沒有另達 major 的直接行為缺陷。
- 最小實驗：已讀，交叉引用〈撤除條件〉有效，無 finding。
- 撤除條件：已讀，無 finding。
- 誠實界線：已讀；已知死結及不可觀測的 REVISIT 見 F2，其餘無 finding。
- 平行消費端已核對：`stack_questions`、`stack_questions_applicable`、`stack_questions_meta`、`_STACK_PERF_QUESTIONS`、表態樣板／判定、`gov --stats`、`recall-miss`、impact hook 與張力候選路徑；除上述兩項外，未找到另一條達 major 的破壞。

審查標的: `/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/09938cdc-5dfc-4dfa-9f18-9b255de108f6/scratchpad/ds-r1.md`（依指示未另寫檔）

總結: major，blocking 共 2 條。
