severity: minor

## F1 計劃筆記說「完整檢查都另印一行」,但 `--json` 路徑刻意不印,文字沒交代、測試也沒釘
severity: minor
blocking: 否
引句:「`--catalog-only` 與完整檢查都另印一行「還沒逐列查證 N 列」與前 20 個編號」
佐證:``configs/ast-grep/kotlin-android/check.py:827-833``。`--json` 分支只印 `json.dumps({"rules":…,"problems":…})`,`_print_unverified()` 放在 else 分支。
失敗場景:
- 執行 `check.py --sg <路徑> --json` 時 stdout 仍是純 JSON,不會讓讀 JSON 的呼叫端壞掉。這個設計是對的。
- 我在 scripts、.github、skills、configs、docs 裡找不到任何 `--json` 的呼叫端,所以目前沒有實際受害者。
- 問題只在文字。計劃第 5 點的「都另印」與程式不符,沒說 JSON 模式不印,也沒說該數字不在 JSON 裡。以後有人想從 `--json` 取「還沒逐列查證」的數字,會找不到。
- 測試 ⑦ 只走文字模式。若有人把 `_print_unverified()` 挪到 if/else 外面,`--json` 輸出會混進一行中文,整個 JSON 解析失敗,而測試全綠。
- 這個不變量(`--json` 的 stdout 必須是純 JSON)是 `--json` 存在的理由,卻沒被釘住。
- 降級說明:只有未來才可能出錯,現在沒有實際受害者,所以停在 minor。
建議:計劃那句補「(`--json` 例外,維持純 JSON)」,測試加一個 ⑧,用同一個假 `check` 跑 `["--sg", sys.executable, "--json"]`,斷言 `json.loads(out)` 成功。

## 修補三問
- 第一問,修補有沒有做到宣稱的:有,我逐項驗過。
  - 標記比對已改成含括號的 `"(出處不全)"`,與 `catalog_problems` 的 `check.py:364`、`386`、`390` 一致。
  - 真型錄實測 `catalog_unverified()` 回 `['API-14','TEST-31']`。
  - 主表 473 列,其中 34 列有 `(出處不全)`,與只比對四個字的算法一致。
  - 459 列帶〔查證〕,且 `_VERIFIED_RE` 對每一列都比對得上,沒有格式不合的漏網列。
  - 計劃寫的「459 / 34」和規則包節點寫的「剩 API-14、TEST-31 兩列」都與實況相符。
  - 新增的 ④b 用「討論出處不全時怎麼寫」做反例,能抓到只比對四個字的舊寫法。
- 第二問,修補有沒有帶進新問題:沒有。
  - `_ktpack()` 每次都用 `spec_from_file_location` 重新載入一個全新的模組物件。
  - 測試 ⑦ 暫時換掉的是 `m.check`,只影響這個私有物件,不是共用模組屬性。
  - 又有 try/finally 還原,例外時也不會汙染後面的測試。
  - 假 `check` 的簽名 `lambda sg` 與 `main` 的呼叫 `check(sg)` 相符;`--sg sys.executable` 通過 `os.access` 檢查。
  - 我執行了 `python3.14 scripts/test_lumos.py -k kt_catalog_unverified`,9 項全綠。
- 第三問,同類的地方有沒有沒修的:函式搬到 `main_rows` 後面,位置沒問題。除 F1 外,同類的「出處不全」子字串比對我沒再找到。

## 固定席
- Systems/kotlin規則包:這次只加一行提醒、不改退出碼,與「引用出處不全的規則只准提示級」沒有衝突。節點裡的數字已與實況一致。
- Systems/測試假綠形態 ★INVARIANT★:本案不是修 bug 的「還原翻紅釘」。但 ⑦ 本身有前置:`rc_full == 0`,以及輸出行比對的是由真型錄算出的 `want`;而 `want` 用被測函式算,所以和第 1 輪的 ①–④ 獨立判準分工。判不影響。
- 其餘固定席:只因改到超大測試總檔被連帶推出,而且只新增一支測試函式,判不影響。

## 本案特定與角色鏡頭
- 第 4 點:不矛盾,也不會讓讀 JSON 的呼叫端壞掉。唯一問題是 F1 的文字不一致。
- be-api-compat:`--json` 輸出格式沒變,文字模式只在最後多一行,沒有改欄位名、刪欄位或改預設值。判不影響。
- be-authz:沒有新增端點,不適用。

總結:全篇最高等級為 minor
