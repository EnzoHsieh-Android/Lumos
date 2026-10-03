severity: clean

C1／C2／C3 均已修復，原正常行為保留：

- C1 現在只接受實際讀取 `scripts/lumos`；README、Glob、相似檔名均翻紅。
- C2 Claude 非零退出會列為儀器例外；正常成功、正常題目失敗、截斷與用量上限優先序正確。
- C3 逐題統計只計有效場次，並另列排除數；全排除時顯示 `0/0 (不算分 2)`。

隔離舊版紅測為 19 passed／12 failed；目前 `python3 scripts/test_lumos.py -k probe_repair` 為 31 passed／0 failed。原三項 finding 可結案。
