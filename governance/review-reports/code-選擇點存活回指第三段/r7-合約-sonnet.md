severity: minor

我對照了修補差異、程式、圖譜與兩支釘值測試。`t_docs_command_count`(4 個)、`t_nogo_skip_logic_version_pin`、`t_door_rule_version_pin`、`t_choice_plan_sections*`(13 個)都綠。`lumos drift scan` 的輸出沒點到選擇點計劃、規格閘節點或這次的 Issues。`spans` 的三處收尾(同名新節、`## `/`# ` 節尾、檔尾)行號與 `_visible_lines` 的 1 起算一致。未給 `spans` 的呼叫端行為不變。計劃〈範圍〉8 與 `_choice_reader_lines` 的字面一致。WHY 行引用的兩個 `[test:]` 名稱存在。版本註解寫「9=」「17=」,與程式的 9、17 相符。Issues 第 16、17 條的內容與現在的判法一致。

severity: minor
blocking: 否
`docs/lumos-toolchain-knowledge/Systems/規格閘.md:38`:KEY 行仍寫 `_DOOR_RULE_VERSION=16`,版本沿革也只列到 16,這次升到 17 沒有同步。該行自帶「現值以程式碼為準」,照做的人會去查程式,所以只是過時線索,不會做錯行為。這次新加的 WHY 行(同檔第 58 行)已經寫了 17,同檔因此兩處數字不一致。
引句:「門判定規則版本 _DOOR_RULE_VERSION=16(現值以程式碼為準;版本沿革照 scripts/lumos 那個常數的註解」

總結:最高等級是 minor。
