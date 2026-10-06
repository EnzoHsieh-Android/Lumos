# code-殺傷力配方綁的測試要在合約清單 r1 收貨

席報告 2 份(正確性 3 條、架構對齊 4 條)。quote-check 兩份全錨;refcheck ok;seat-check 派工單材料為凍結 patch。

彙整 id:正確性 c1–c3、架構對齊 a1–a4。

## 機械重現

| id | 重現 | 輸出 | 判 |
|---|---|---|---|
| c1 | 載入 scripts/lumos,平台表含鍵 `x;touch PWNED;#`,呼叫 _kill_binding_msg(不在清單、平台不同各一) | 兩句都印出 `--platform x;touch PWNED;#` 未加引號 | HIT |
| c2 | 翻紅:改成 bind 不帶平台、顯示不帶前綴、跳脫函式不加引號、不擋控制字元、平台前綴不跳脫 | 補格前無格會紅(席位實測);補 ⑬⑭⑮ 後 5 處各自紅 | HIT |
| a1 | 讀碼:cmd_guard_audit 的定位迴圈與 kill-add 同條件 | 同 INVARIANT_RE + INV_TAG_RE 含片段、多行擋 | HIT |

## 處置

- 折:c1(貼進指令的字一律走 _kill_cmd_arg)、c2(補三組測試格)、a1(guard audit 改用 _kill_find_contract)、a4(_kill_cmd_arg 內改用既有 _sh_quote)。
- 放行:c3(席位確認既有測試那格改得對,不是缺陷)、a2(_kill_norm_method 在拆殼外再去空白是必要的:合約側 resolve_test_refs 不去反引號、配方側前綴後可能帶空白;同檔其他各自 strip 是既有寫法,不是這次引入)、a3(把 warn_soft 傳入是為了不讓 run_doctor 複雜度上升,新增告警閘會擋;席位也判為刻意取捨)。
