severity: clean

本輪沒有 blocking 發現,上一輪的兩項修補都做到了。

## 修補三問

**1. 做到宣稱的嗎?**
- 宣稱①(`--json` 維持純 JSON)做到了。`check.py` 的 `main()` 裡,`_print_unverified()` 放在 `else:` 分支內,`--json` 分支只印 `json.dumps(...)`。計劃筆記補了「`--json` 例外」那句。
- 測試 ⑧ 用假 `check` 跑 `main(["--sg", sys.executable, "--json"])`,斷言輸出能 `json.loads` 成 dict,且不含「還沒逐列查證」。
- 如果把 `_print_unverified()` 移到 `if/else` 外面,JSON 後面會多一行中文,`json.loads` 會丟 `ValueError`(Extra data),⑧ 會翻紅。我是讀程式推出來的,沒有實際改壞跑一次。
- 宣稱②(先取具名變數再判)做到了。`name, src = c[1], c[11]` 的下標對得上 `_MAIN_COLS = 12` 和欄位註解(名稱是第 2 欄,來源是第 12 欄)。`main_rows` 會把欄位數不是 12 的列 `continue` 掉,所以不會有下標越界。
- 我跑了 `python3.14 scripts/test_lumos.py -k kt_catalog_unverified`,10 項全過。真型錄上 `catalog_unverified()` 回 `['API-14', 'TEST-31']`,和計劃、WHY 行寫的數字一致。`--catalog-only` 印出「還沒逐列查證 2 列:API-14、TEST-31(只提醒,不影響退出碼)」,退出碼 0。

**2. 帶進新問題嗎?**
沒有。我 grep 了 `scripts/lumos` 和 `.github` 裡有沒有程式去解析 `check.py` 文字輸出的最後一行或「規則 N 條,問題」,沒有找到。文字輸出多一行不會破壞呼叫端。`--json` 的合約沒變。

**3. 同類地方還有沒修的嗎?**
`main()` 有三條輸出路徑:`--catalog-only`、完整檢查的文字輸出、完整檢查的 `--json`。前兩條有印提醒並有測試(⑤、⑦),`--json` 刻意不印並有測試(⑧)。找不到 ast-grep 的提早返回(回 2)走 stderr,不碰這個提醒,也不算漏。

## 固定席判定

- **Systems/kotlin規則包**:該節點沒有合約。WHY「查不到的列標(出處不全),引用它的規則只准提示級」沒被這份 diff 違反。新增的 WHY 行寫明 API-14、TEST-31 兩列找不到官方原文,保留在「還沒逐列查證」裡,沒有標(出處不全)。降不降級仍待人裁,所以沒有違反「只准提示級」。
- **Systems/測試假綠形態 ★INVARIANT★**(修 bug 的還原翻紅釘必須配前置斷言證明現場成立):這份 diff 不是修 bug,是新功能加提醒。測試仍保留 `★前置★ 五列都被主表讀到` 這條前置斷言,證明五列真的被主表讀到。
- 分組摘要:`check.py` 一支、測試總檔一個測試函式、計劃和 Systems 筆記各一份,其餘因為改到超大測試總檔連帶推出,和這份 diff 的語意無關。

## 角色卡

- **be-api-compat**:沒有欄位改名或預設值改變。`--json` 的輸出形狀完全不變(`{"rules","problems"}`)。文字輸出只在尾端多一行,不屬於結構化合約。
- **be-authz**:這份 diff 沒有新增或改動端點,不適用。

## minor(不阻擋,不窮舉)

- 測試 ⑧ 只斷言輸出是 dict,沒有斷言 `rules` 和 `problems` 的值。這不影響本輪結論。

總結:全篇最高等級為 clean
