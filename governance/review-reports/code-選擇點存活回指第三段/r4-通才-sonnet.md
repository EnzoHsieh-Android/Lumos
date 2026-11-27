severity: clean

驗收結論:上一輪三處修補都修到了,我沒找到新的阻擋問題。

- **計劃正文判段**(`_choice_layer_not_body`、`_CHOICE_LAYER_XREF_RE`):我用 grep 掃了 `docs/` 裡全部 `##` 標題,含「審計修正紀錄」的真標題都歸對,「設計(…各條出處見〈審計修正紀錄〉)」這類交叉引用不被誤排。`## 驗收條款(…)` 這類帶括號說明的也歸對。`## S26 端到端(計劃〈驗收條款〉S26)` 不被整行比對誤吞。`_choice_plan_sections` 的呼叫端只有 `_choice_plan_view` 一處,簽名沒變。
- **旁檔外移改看加總**(`_choice_layer_plan_sides`):每份約 84KB、五份的案例,舊的單份判法比 100KB 上限小,會得到 0 份旁檔,所以新測試 `t_choice_layer_plan_sides_total` 確實會對改回單份判法翻紅。
- **每份帶自己這組的旁檔**(`_choice_layer_split_groups`、`_choice_layer_write_parts`):`_choice_layer_split` 本來就按組各自切,改成逐組呼叫行為不變。旁檔檔名由清單編號加計劃路徑雜湊決定,同一份計劃在不同組共用同一支檔。旁檔指路與段名清單寫在各份材料裡,`--part n --list` 讀回靠整份材料檔的雜湊,沒受影響。
- **跑過的測試**:`python3.14 scripts/test_lumos.py -k choice_plan_sections` 9 條全過,`-k choice_layer` 62 條全過(含 `t_choice_layer_side_content`、`t_choice_layer_template`)。

總結:最高等級是 clean。
