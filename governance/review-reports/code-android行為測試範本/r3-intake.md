# r3 收貨紀錄(code-android行為測試範本,最後一輪)

## 收貨

- 第 3 輪(standard 上限輪),修補差異 r3-repair.patch(cea727087..9ca57983a,1226 行),整份 r3-snapshot.patch。兩席 sonnet:驗收審、架構對齊。外家預設不派,結論寫成「單家族視角下」。
- 兩席都沒有 major。驗收審實跑 57 格矩陣 0 不符、API-31 另寫 8 種變形(4 合法全綠、4 壞寫法全紅)、圍欄比對測試改壞兩份各自翻紅、3 萬組隨機輸入兩份判定差異 0。
- 引句錨不到 3 句:驗收審 #3、#5 是跨行引句(原文在 r3-snapshot.patch 內,逐行皆在);架構對齊 #4 多抄一個冒號(原文是 `if j in visible and lines[j].startswith("## ")), end)`,`scripts/test_lumos.py` 的 `_kt_template_sections`)。不改席位引句,編排者機械重現見下表。臨時目錄已清。

## 重現表

| id | 來源 | 重現 | 結果 |
|---|---|---|---|
| 三驗3 | 驗收審 F3 | `grep -n 'delay(100)   // 真的儲存通常會掛起' skills/kotlin-idioms/test-templates.md` | HIT:原文存在 |
| 三驗5 | 驗收審 F5 | `grep -n 'not ln.startswith("\\t")' configs/ast-grep/kotlin-android/check.py` | HIT:原文存在 |
| 三架4 | 架構對齊 F3 | `grep -n 'j in visible and lines\[j\].startswith("## ")' scripts/test_lumos.py` | HIT:第 125892 行 |

refuted: none

## 逐條去向

- 最後一輪,兩席皆 minor,全部附理由放行(不觸發新一輪,照末輪驗收紀律):
  - 三驗1、三驗2(守衛只認 `.test {`、只剝 `//` 註解):守衛只掃本 repo 的範本檔,實際紅綠由 75 格矩陣擋;範本裡目前沒有這些寫法。
  - 三驗3(save 測試不驗 repo 收到幾次):不在型錄 TEST-18 那列的範圍。
  - 三驗4(Turbine 出處檔名措辭):清單本身經 javap 核對無漏。
  - 三驗5(tab 子句死碼):行為無影響。
  - 三驗6(`_kt_kotlin_blocks` 未閉合不退寬鬆):範本每節圍欄都閉合,型錄自檢的圍欄判定另有退寬鬆。
  - 三架1(main_rows 以參數回報問題):結構對、只是同模組慣例不一。
  - 三架2(比對測試只比 `_visible_lines`):另有 3 萬組隨機比對實跑差異 0(驗收審)。
  - 三架3(組終點與小節切分仍在測試端):目前行為相容。
  - 三架4(複本存在理由):check.py 在 CI 以獨立程式執行(`--catalog-only`),不能保證能載入沒有 .py 副檔名的 scripts/lumos;比對測試守住口徑。
- REVISIT:2026-12-06 範本內容守衛若被新寫法(`.test(timeout=…) {`、`testIn`)繞過一次,就把守衛改成解析 Kotlin 呼叫而不是找字串
- 載體:架構對齊席應編排者要求把 F3 那句引句改成原文、其餘一字不改重交,存為 r3-架構對齊-引句更正-sonnet.md(全錨),以它當載體;原檔 r3-架構對齊-sonnet.md 保留為原始證據。
