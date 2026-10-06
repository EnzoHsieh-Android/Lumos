severity: minor

PF1 — severity: minor  
凍結引句：「有效零發現兩席應仍通過處置閘。」  
file: `docs/lumos-toolchain-knowledge/Projects/負數發現計數在追加前拒收_計劃.md:29`

觀察：S2 所列兩個測試中，`t_canary_findings` 只驗 3、省略、非整數；`t_canary_carrier_quote_positive_controls` 只驗合法載體記帳，均未執行兩席零發現的 disposal gate。真正覆蓋此行為的是 `t_canary_negative_findings_rejected` 的兩席 record 與 gate 斷言（`scripts/test_lumos.py:332`），但 S2 沒引用它。

具體輸入→錯誤→查證：依 S2 僅跑其兩個 `[test:]` →「兩席 `--findings 0` 後 gate rc0」可壞而 S2 仍顯示已驗 → 開碼逐項核對上述三個函式確認。

判準：這是驗收條款的語意引用不完整，不是核心判準有錯；應讓 S2 指到現有實際覆蓋它的測試。

其餘已驗：未定義詞無阻斷歧義；其他檔案／測試引用存在；範圍與「舊帳讀側不改、無 Windows、不加集合大小等式、PR20 未稱已上主線」一致。CLI hash 確為 `84d013c…`；14/16、14/20 紅燈及合法對照吻合。`argparse` 的型別轉換與非法參數 rc2 說法符合[官方文件](https://docs.python.org/3/library/argparse.html)。未另跑實驗。