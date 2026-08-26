# r3 收貨紀錄(regime-backtest)

- ext 席 ext-f5 引句原文抄錄時吃掉角括號(codex 慣性,r1 亦發生過同型):
  席原句=「舊 verdict 改名 verdict-日期-時分秒.json 存檔不回改」
  機械重現:`grep -n "verdict-<日期>" r3-snapshot.md` 命中第 30 行,原文=「舊 verdict 改名 `verdict-<日期>-<時分秒>.json` 存檔不回改」,語意逐字等同僅括號差。
  處置:引句修正為逐字版後重過 quote-check;判定內容(clean/已解)不受影響。
