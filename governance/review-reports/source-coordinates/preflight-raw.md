severity: major

1. severity: major — 中間空白行缺少機械驗收

引句:「中間與末尾的實際空白行不得消失」

計劃明訂保留中間空白行，但 S4 測試只有空檔、單一空行與末尾空白行，沒有 `a\n\nb\n` 這類中間空白行案例。錯誤實作仍可能刪除中間空項而四組測試全綠。

建議：在既有 `t_refcheck_physical_legacy` 增加一個中間空白行案例，同時驗工作樹與釘版；不新增機制。

佐證 file: `docs/lumos-toolchain-knowledge/Projects/引用座標依實際換行_計劃.md:39`  
佐證 file: `scripts/test_lumos.py:69770`

2. severity: minor — 歷史歸因沒有可核對座標

引句:「共用函式在該功能前後相同，不記成該功能的修補回歸」

「該功能」未定義；`attribution.json` 也只有結論，沒有前後提交或可重跑的比對方式。現有卷證能證明目前四條路徑重現，不能單獨證明函式在某功能前後相同。

建議：若歸因不是修復理由，刪除這句；否則明定功能及前後提交，附宣告式比對。不要把未釘定的歷史判斷用作新功能理由。

佐證 file: `docs/lumos-toolchain-knowledge/Projects/引用座標依實際換行_計劃.md:31`  
佐證 file: `governance/review-reports/source-coordinates/attribution.json:2`

其餘無命中：共用入口、工作樹與釘版文字層、表態消費端、目錄短路及釘版 999 行超界均與實碼一致；以文字層正規化後的 LF 分割並只移除末尾哨兵空項，是現況下的最小修復。