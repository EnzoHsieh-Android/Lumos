severity: major

背景測試跑完了:`-k choice_layer` 56 個通過、0 個失敗,`-k choice_plan` 8 個通過、0 個失敗。所以我上一份報告裡「測試沒等到結果」那句已經過時,測試全綠。

綠燈不影響我的發現。現有測試沒有一案造出「多份各自略低於 100KB 的計劃同進一份材料」,所以抓不到下面這條。

severity: major
blocking: 是
`scripts/lumos` 的 `_choice_layer_plan_sides` 和 `_choice_layer_split`:一份材料附上的所有計劃加總沒有任何地方比上限。

- **重現**:5 份計劃、每份約 84KB,`_choice_layer_plan_sides` 回傳 `{}`。逐份呼叫 `_choice_layer_plan_md(p, v, None)` 後,那一份材料的計劃部分共 420685 位元組,約為 `_CHOICE_LAYER_PART_BYTES`(204800)的 2 倍。
- **會發生在哪**:「未歸計劃」組的 `_choice_layer_plans` 回傳全部存活計劃。
- **缺的守衛**:沒有警告,`_choice_layer_read_part` 也沒有大小檢查。
- **影響**:判讀代理拿到超過 200KB 的材料,違反〈範圍〉8 的份上限。

引句:「份上限只拿存活自己的材料比:size(存活清單) 是那幾個存活的材料位元組數」

severity: minor
blocking: 否
`scripts/lumos` 的 `_choice_layer_plan_md`:走旁檔的計劃,材料只剩條款號清單,段名清單被拿掉了。第 2 層作答要填段名,材料開頭又寫「只看這份材料」,與「判讀時要讀」旁檔互相矛盾。

引句:「(這份計劃的條款、預期值表與正文太大,整份在 `{side}`,判讀時要讀)」

總結:最高等級是 major。
