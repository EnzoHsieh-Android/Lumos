severity: major

**固定席筆記逐條判定**

- Systems/codex-harness:影響。這次改了其中「回答保存上限」那條的綁定測試描述,新增 `_run_scenario`,筆記已同步,與程式一致。
- Systems/lumos-cli-read:不影響。search 排除 superseded 的行為沒被碰到。
- Systems/design-loop:不影響。處置閘的審材與計劃判定沒有改動。
- Systems/bound-tests-gate:不影響。新增的 `t_backend_qo_unreadable_questions_fail_closed` 不是綁定合約測試。
- Systems/guard-kill:不影響。
- Systems/lumos-cli-lifecycle:不影響。
- Systems/授權與歸屬:不影響。`scripts/lumos` 檔頭與授權白名單沒動。
- Systems/測試假綠形態:影響。新測試的翻紅釘要有前置斷言,但本次新測試沒涵蓋下面的縮排收尾圍欄形狀(見 finding)。

**Finding 1**
severity: major
blocking: 是

分層與依賴方向、命名與錯誤處理跟鄰居一致。新做法只有一處:`_pq_unreachable` 自己用一條正規式判斷「圍欄有沒有沒關」,等於寫了第二套圍欄判定。專案規定圍欄判定只有 `_visible_lines` 一套,那支函式的說明就寫著「全檔唯一的 fenced-code 判定實作」。

兩邊的判法不同:

- `_visible_lines` 只認縮排 3 格以內的 ``` 或 ~~~ 當標記,4 格以上算縮排程式碼區塊內容。
- `_pq_unreachable` 用 `re.match(r"^\s*(```|~~~)", last)`,縮排不限。
- 所以檔尾是 4 格縮排的 ``` 時,`_visible_lines` 認為圍欄沒關,看門卻判成「已關」,把藏在裡面的阻塞題放掉。這就是第 2 輪想補的洞(圍欄沒關、題目被藏起來),只補了一半。

引句:「unclosed = tail < len(lines) and not re.match(r"^\s*(```|~~~)", last)」

佐證:
- file: `scripts/lumos:4898`,這是 `_visible_lines` 的標記判定(縮排 3 格以內才算)。
- file: `scripts/lumos:6938`,這是新寫的第二套判斷。

最小重現(對 46bc93c3 的 `scripts/lumos` 跑 `parse_pending_questions`):

```
t = "# p\n\n## 待決問題\n\n```\n範例\n- [Q1] 訂單成功的定義 [類:需求][階段:需求][狀態:待人][阻塞]\n    ```"
```

- 標準未關(沒有最後那行縮排 ```):`qs=[(None, bad)]`,`gate=True`,被擋。
- 末行是 4 格縮排的 ```:`_visible_lines` 只看得到第 1 到 4 行,`qs=[]`,`gate=False`,規格閘放行。標了阻塞、尚未決定的需求題整題消失。
- 修法方向:讓 `_visible_lines` 或它旁邊的共用函式直接回報「收尾時圍欄是否還開著」(它內部 `_scan` 已有這個值,目前被丟掉),`_pq_unreachable` 改用那個值,不要自己再判一次。

歸因:有證據的原有漏查,但判斷這件事的程式是這輪新寫的。
- 修前 112ad15f:標準未關與縮排收尾兩種都是 `qs=[]`、`gate=False`,都放行。
- 修後 46bc93c3:標準未關改成被擋,縮排收尾仍放行。
- 結論:行為上不是退步,是補到一半;新增的是第二套判定。

**其他三問,未發現問題**

- `_h2_section_lines(..., nested=False)` 是給既有找節函式加參數。預設行為不變,回退節與實務隱患節兩個既有呼叫(`scripts/lumos:7203`、`scripts/lumos:7307`)不受影響,沒有長出第三套找節邏輯。
- `_run_scenario` 抽成模組層函式,選配參數一律經 `_run_kwargs`。`main` 的 `run_at` 只剩一行轉呼叫,沒有重複的執行器分派。
- qo_ablation 新增的 `_result_row` 讓 `_valid` 與 `_load_runs` 共用,收掉了重複的讀檔邏輯。`packets` 重產時只清 `packet-*.json`,沒有牽涉別的流程。
- 新增 `_PQ_DEF_RE`、`_PQ_FLAG_LOOSE_RE`,與既有 `_PQ_LOOKS_RE` 並存,職責不同。我給不出具體失敗場景,不列。

總結:最嚴重 major;blocking 共 1 條。
