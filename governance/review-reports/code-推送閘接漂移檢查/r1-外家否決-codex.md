severity: major

## F1 CI 把參數錯誤也當成漂移違規標紅

severity: major

blocking: 是

引句:「+    # CI:照 code-loop gate 那步的寫法,push 事件、before..sha 原樣交給 lumos;只有 rc1 讓 CI 紅」

file: `.github/workflows/ci.yml:168`  
file: `scripts/test_lumos.py:51112`

1. 規格與註解都限定只有回傳 1 才讓 CI 紅；實作卻對其他非零值執行 `exit "$rc"`。因此工具回 2（參數或執行環境錯誤）時，CI 仍失敗，會把沒有漂移判決的推送錯誤標紅。
2. 最小重現：

   ```text
   bash -c 'python(){ return 2; }; BEFORE=0000000000000000000000000000000000000000; SHA=abc123; python scripts/lumos drift check --diff "$BEFORE..$SHA" --repo . || { rc=$?; if [ "$rc" -eq 1 ]; then exit 1; fi; exit "$rc"; }'
   exit=2
   ```

3. 新測試反而把 `{"2": 2}` 當成正確結果，會固定這個錯擋。依凍結規格，CI 包裝應只對 1 失敗，並把測試的回傳 2 預期改為放行。

## 圖譜鏡頭逐項判定

- `code-loop守衛main-direct盲區`：使用推送提供的起訖值，且排在 code-loop 後，未重開舊盲區。
- `存量漂移守衛`、`bound-tests-gate`：範圍、模式、掛鉤順序符合紀錄；CI 回傳碼處理有 F1。
- `每支檔有家`：新增的掛鉤與 workflow 已被系統節點認領。
- `筆記內容閘`：沿用其 fetch 結果，未改動原閘判定。
- `測試假綠形態`：測試有執行真掛鉤與真 drift 路徑，但錯誤地把 F1 寫成通過條件。
- `anchor-integrity`：基準線已同步，`lumos anchor verify --repo .` 通過。
- `lumos-cli-lifecycle`：只更新既有 vendored 檔，舊版更新器已認得這些路徑；未發現消費專案升級漏檔。
- `lumos-cli-read`：沒有改動唯讀指令或其寫帳邊界。
- 其餘列名節點涉及既有審查、安裝、卸載、逃逸與可逆性流程；本 diff 沒改其 API 或控制流，未發現合約破壞。

最高等級:major