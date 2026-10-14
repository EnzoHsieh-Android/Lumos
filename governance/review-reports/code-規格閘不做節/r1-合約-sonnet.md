severity: minor

我讀了 patch,在工作樹 7c1cd3c7 跑了 `-k nogo`(63 支)與 `-k door_rule_version_pin`(1 支),全綠。另外用 `_nogo_skip_lines` 直接探了一批邊界輸入。圖譜與程式的一致性我沒找到破口:

- `lands_in`、規格閘與雙向門兩篇文件、版本 2 這三處,跟程式對得上。
- ★INVARIANT★ 合約行沒被動到。
- 表態記錄裡 py-eventloop、py-parallel 等「na」我也沒找到相反證據。

只有下面這一條。

severity: minor
blocking: 否 — 只能讓「做法」裡的一段縮排散文漏出風險判定,而且得是作者刻意這樣寫;最壞結果是風險高的計劃被判成風險低,所以記為 minor,不算 major。
引句:「縮排至少到上一個項目的內容起點(標記之後第一個非空白字元的欄位),而且上一個非空行是項目或續行」
問題:`_nogo_skip_lines` 的續行規則只看縮排欄位,不看前面有沒有空行,也不管那行是不是散文。清單項目後面隔一個空行、再接一段縮排 2 格以上的散文,會被當成項目的續行整段跳過。這跟計劃 S7 寫的「不做節裡用散文段落…寫扣款,也應判風險高」有出入。S7 的測試只用了從第 0 欄開始的散文,沒測縮排散文。
具體失敗情境:計劃寫 `## 不做\n- 不做匯出\n\n  這一版其實會扣款`。我實測 `_nogo_skip_lines` 回 `{2,3,4}`,第 4 行含「扣款」的縮排散文被跳過。`_door_judge` 因此不記訊號,只記進 `nogo_skipped`。實務隱患四行已排除齊全時,整份判風險低,審查席看不到。
這跟計劃自己承認的「一開始就在不做清單裡寫一條其實要做的事」同一型,只是進入點是縮排散文,不是清單項目。留痕後事後增減還是會被指紋抓到,所以只是初判時漏,不是推送前也漏。
佐證:
- `scripts/lumos`:`_nogo_skip_lines` 裡 `elif not (col is not None and len(ln2) - len(ln2.lstrip(" ")) >= col and s[0] not in "#<>|" ...)`
- `scripts/test_lumos.py`:`t_spec_gate_nogo_stops_at_any_heading` 的 `prose` 夾具全是頂格散文
修法建議:空行之後的縮排續行不算續行(遇空行就要求下一個非空行必須是清單項目),或在測試補一條縮排散文的案例並在計劃寫明接受。

最高等級 minor,blocking 0 條。
