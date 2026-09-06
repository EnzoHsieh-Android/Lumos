severity: major  
blocking: 是  
file: `scripts/test_lumos.py:5329`

`t_commands_table_shape` 只接受以 `|` 開頭的表格列，因此省略外側豎線的標準 Markdown 表格完全不受檢查。

引句:「表格每一列的格數都跟表頭一樣」

實跑原守衛並餵入：

```markdown
A | B
--- | ---
only-one-cell
```

表頭有兩欄、資料列只有一欄，但守衛全綠（`RESULT 2 0`）。這正是它宣稱要攔的 MD056 類錯誤。

3. severity: minor  
blocking: 否  
file: `scripts/test_lumos.py:5334`

表格守衛以豎線字元數代替實際欄數，會誤抓合法的「有前導、無尾隨豎線」寫法。

引句:「比對時要先把跳脫過的 `\\|`」

實跑：

```markdown
| A | B |
| --- | --- |
| x | y
```

這是合法兩欄表格，但守衛回報資料列只有一格並翻紅（`RESULT 1 1`）。

4. severity: minor  
blocking: 否  
file: `scripts/test_lumos.py:5295`

旗標守衛要求文件中的長旗標逐字存在，與 argparse 預設允許的無歧義長旗標縮寫不一致。

引句:「文件裡教的每個 lumos 指令與旗標都真的存在」

`python3 scripts/lumos search code --cod` 實跑 rc=0，`--cod` 被解析成 `--code`；但將 `` `lumos search foo --cod` `` 餵給原守衛會假紅（`RESULT 1 1`）。若專案刻意禁止文件使用縮寫，需把此限制明文定為文件規則；目前守衛宣稱驗的是「真的存在／能否執行」。

5. severity: minor  
blocking: 否  
file: `ONBOARDING.md:41`

新增的配額說明與現行席數不符。

引句:「設計審 / 代碼審一輪會同時派三到四個子代理讀全份材料」

現況 `_TIER_PARAMS` 是 standard=3、high=5（`scripts/lumos:5863`），設計審另有一席不佔人數的架構對齊席；代碼審 standard 則是一席加架構席。因此實際可能是 2、4 或 6 席，不是固定三到四席。佐證見 `skills/lumos-code-loop/SKILL.md:19` 與 `skills/lumos-design-loop/reference.md:236`。

`_lumos_parser_tree()` 本輪未找到可重現的現況副作用：目前 `main()` 在 `parse_args()` 前只建 parser，且 monkeypatch 有 `finally` 還原。主要脆弱點仍是依賴 `main()` 永遠使用 `parse_args()`，但尚不足以列為已查證 finding。
