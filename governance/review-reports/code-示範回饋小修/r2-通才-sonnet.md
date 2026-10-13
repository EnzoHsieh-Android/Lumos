severity: major

## Findings

**1. 提醒印的 `rm` 與重建指令沒有加引號,名稱帶空白時照貼會刪錯檔(修補引入)**

引句:「print(f"    rm {path}")」
file: `scripts/lumos`(`cmd_new` 末段新增的提醒,diff 內 `print(f"    rm {path}")` 與 `print(f"    lumos new project {name}_計劃")` 兩行)

最小重現(vault 為任一臨時圖譜):
1. 在目前目錄放一個 `docs.md`。
2. 執行 `lumos new project "y docs"`,輸出 `rm …/Projects/y docs.md`。
3. 照貼執行,結果是 `rm: …/Projects/y: No such file or directory`,而目前目錄的 `docs.md` 被刪掉了。要刪的 `y docs.md` 還在。

- 名稱含空白時,`rm` 會把它當兩個參數,可能刪到目前目錄裡同名的別的檔。
- `a$b` 會被 shell 展開,`O'Brien` 會讓引號不成對。
- 重建那行 `lumos new project my plan_計劃` 同樣會被切成兩個參數,重建的名稱是錯的。
- 中文名稱(`訂單下單`)、連字號(`order-flow`)、日期名稱(`2026-10-14`)、`Plan2` 都能直接複製執行。
- 修法是用 `shlex.quote(str(path))` 和 `shlex.quote(name + "_計劃")`。
- 提醒指令的用意就是讓人直接複製,而且指令帶刪除,所以列 major。
- 上輪的 `name.startswith(".")` 與斜線擋法不擋空白,所以這條路徑確實走得到。

severity: major
blocking: 是 — 提醒要人照貼執行的 `rm`,對合法名稱(帶空白)會刪到別的檔,已當場重現。

**2. 觸發詞拿掉「搶」「同時」後,真的搶量場景漏掉,regex 只剩「搶購|搶票」(修補引入)**

引句:「"when": [r"大量|高併發|搶購|搶票|秒殺|尖峰|流量"]」

我用單句需求實測了 req-scale 與 arch-sync:

| 需求句 | 觸發? |
|---|---|
| 大量使用者同時下單 | 是 |
| 秒殺活動 | 是 |
| 演唱會搶票 | 是 |
| 活動期間流量暴增 | 是 |
| 上萬人同時搶 | 否 |
| 雙十一檔期預期千人同時結帳 | 否 |
| 熱門商品開賣很多人一起下單 | 否 |

- 你點名的三個例句都還觸發。
- 沒觸發的三句在原 regex(含「搶」「同時」)裡,前兩句會中。
- 這是 r1 為壓一般詞誤觸所做的取捨,誤報確實少了。代價是「搶紅包」「搶課」「N 人同時」這類寫法漏掉。
- `impl-concurrency` 仍保留「搶|同時」,所以三句裡有兩句還是會在實作階段被問到,只是在需求與架構階段不問量級。
- 這是召回率下降,不是壞掉。

severity: minor
blocking: 否 — 屬 r1 認定的精準度與召回率取捨,漏掉的題目在實作階段仍會由 impl-concurrency 補問。

**3. 測試的鑑別力有兩處缺口(修補引入的測試 / 上輪沒人看的角落)**

引句:「rush.write_text("# 搶購\n\n需求:做一個搶購下單的 API,活動開始時大量使用者同時下單,不能賣超過庫存。\n", encoding="utf-8")」

- `rush` 文本含「大量」。把 regex 裡新加的「搶購|搶票|秒殺」整段拿掉,① ② 仍然綠(未實跑變異,依 regex 與文本比對判斷),所以這些新觸發詞沒有測試守著。
- `t_new_project_warns_missing_plan_suffix` 沒有任何含空白或特殊字元的名稱案例,所以 finding 1 沒被抓到。
- ③ 只驗 system。issue 與 verification 建檔不受影響,這點我看 diff 確認,但測試沒鎖。

severity: minor
blocking: 否 — 測試目前沒有假綠,只是少了守住新觸發詞與特殊名稱的格子。

**4.「完全沒有底線」判斷會漏掉不合慣例但含底線的名稱(上輪沒人看的角落)**

引句:「if ntype == "project" and "_" not in name:」

- `order_flow`、`訂單_下單` 含底線,所以不提醒,但它們同樣不是 `_計劃` 或 `_調研` 結尾。
- 這是刻意放寬,為了不干擾 `_草案` 等既有寫法,屬設計取捨。
- 英文名(`Plan2`)、連字號名、日期名都會提醒,合理。
- 日期名稱提醒的是「建議加 `_計劃`」,不算誤報。

severity: minor
blocking: 否 — 沒有失敗場景,只是提醒範圍比慣例窄。

## 三問作答

**1. 有沒有改壞原本對的行為**
- 沒有改壞。我實跑 `-k t_new`(67 條)、`-k t_stage`(7 條)、`-k t_scenario`(3 條)、`-k t_backend_qo`(9 條),全綠。
- 建檔名稱:一律用原名,不再改名。
- 回傳碼:仍是 0。
- 順序:提醒印在「骨架建好了」之後、`NEW_HINT` 之前,system 的 about_code 提醒順序不變。
- system、issue、verification:只有 `ntype == "project"` 會進新分支,不受影響。

**2. 修補自己有沒有新洞**
- 有一個:提醒的 `rm` 與重建指令沒加引號,見 finding 1。
- 觸發詞變窄的取捨見 finding 2。
- 「完全沒有底線」對英文、連字號、日期名都合理,見 finding 4。
- 測試的缺口見 finding 3。

**3. 上輪問題有沒有修好**
- **改壞既有命名**:修好。`某題_調研`、`規劃_草案` 原樣建檔、不提醒,我實跑確認。
- **自動改名是第二種做法**:修好。`name` 不再被改,檔案存在檢查也用原名。
- **一般詞誤觸**:修好。「使用者修改密碼時同時更新暱稱」不再觸發 req-scale 與 arch-sync,代價見 finding 2。
- **測試沒鑑別力**:大部分修好。新增的 busy_words 格子在舊 regex 下會翻紅。
- **提示印太早**:修好。提醒在「骨架建好了」之後,測試用 `index` 比較順序。

## 固定席(impact `f01aa7ce..77138668`,固定席 30 加 top 7 逐條判,依據各節點的 ★INVARIANT★ 行與我實跑的測試)

- **`Systems/lumos-cli-write.md`**(家,未標 INVARIANT):它的 WHY 行已同步成「提醒、不改名」,與 `cmd_new` 一致,不影響。
- **`Systems/情境出題.md`**:觸發詞欄與 `_REQUIREMENT_FACETS` 一致,不影響。
- **`Systems/lumos-cli-lifecycle.md`**:INVARIANT 是 re-inject 不動 CLAUDE.md sentinel 之外的內容。`cmd_new` 不碰 CLAUDE.md,不影響。
- **`Systems/節點範圍與索引守衛.md`**:INVARIANT 在 `doctor` 的 S5/S6/S7 抽取與段落順序,與 `cmd_new` 和 facets 無關。唯一相關的是「純新增也動邊界」(插入位置)。新提醒在 `cmd_new` 內,沒有測試切這段輸出,`t_new` 全綠,不影響。
- **`Systems/測試假綠形態.md`**:INVARIANT 要求還原翻紅釘配前置斷言。新測試有「檔案存在加提醒文字」的前置條件,但沒覆蓋特殊名稱,見 finding 3,不算違反。
- **`Systems/bound-tests-gate.md`、`Systems/guard-kill.md`、`Systems/canary-audit.md`、`Systems/design-loop.md`、`Systems/lumos-cli-read.md`**:合約綁的是閘、殺傷力、審計、讀取路徑的測試。本修補只動 `cmd_new` 末段與兩個 regex,不在這些路徑。
- **`slim-*` 三個節點**:已凍結,與本修補無關,不影響。
- **`Systems/pitfalls-code-loop.md` 與其餘 ★RISK 守衛面節點**:`pitfalls --stage` 的輸出格式沒變,只有兩個 when 的觸發集合變窄,不影響。
- 其餘 Projects 與 Systems 固定席,我只看了與 `cmd_new` 和 `_REQUIREMENT_FACETS` 相關的部分,沒有逐篇讀完。

總結:最嚴重為 major,blocking 1 條(finding 1)。
