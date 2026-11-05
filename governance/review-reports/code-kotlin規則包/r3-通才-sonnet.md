severity: clean

這輪沒有值得列的問題。八個角度走完,沒有一個候選能講出具體失敗情境。

- **驗證範圍:** 本機沒有 ast-grep,所以只驗到靜態那半。`python3.14 scripts/test_lumos.py -k kotlin_` 跑出 80 通過、0 失敗,不含需要 ast-grep 的樣本掃描與逾時案例,那兩段要靠 CI 的 0.51.1 驗。
- **逐行與跨檔:**
  - `_files_block_is_test_only` 的新正規式,我拿全部 207 條規則逐份比對新舊結果,0 份有差。
  - `good_cases` 現在略過 `review-fp-` 檔,207 條規則的好例段數仍全部至少 2 段。
  - `(無)` 的比對,第一個字面是半形括號,第二個是全形,型錄裡實際用半形,沒有搞反。
  - `_ktpack_sg()` 現在可能回傳 None,它在檔內只有兩個呼叫端,兩處都已先判斷 None 才往下用。
- **逾時旗標與命令組裝:** `_TIMED_OUT` 只在 `check()` 開頭重設。檔內沒有 `check()` 以外的 `scan` 或 `loaded_count` 呼叫端,不會殘留旗標。測試裡 `sleep 5` 的腳本在 POSIX 上只會等子程序被殺,不會卡滿 5 秒。`shlex.quote` 套用的位置正確。
- **設定檔:** `.lumos/config.json` 的 node_home 忽略規則收窄成 `*.kt` 與 `*.kts`。`configs/ast-grep` 底下實際只有 kt、yml、py 三種副檔名,沒有漏掉的樣本檔類型。

這輪改動的行為都有對應的測試,我沒有發現漏網的缺陷。
