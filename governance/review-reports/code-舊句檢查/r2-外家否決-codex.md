severity: minor

## F1 名稱索引碰到共同前綴時仍會越過 30 秒預算

severity: minor

blocking: 否

引句:「out = [n for w in words for n, segs in idx[0].get(w, ()) if n in ln and all(x in words for x in segs)]」

file: `scripts/lumos:28867`  
file: `scripts/lumos:29191`  
file: `scripts/test_lumos.py:56939`

1. 新索引只用名稱的第一段 ASCII 詞分桶。大量刪除 `src/...` 路徑時，所有候選都落進 `src` 桶；任何含 `src` 的筆記行仍會逐一執行 `n in ln`。
2. 現有壓力測試用 `gen_func_000000` 等名稱；底線屬於 ASCII 詞，因此每個名稱各自成桶，沒有覆蓋共同前綴。
3. 具體失敗輸入：刪除數萬支 `src/pkg_N/file.py`，另一篇筆記的隱藏區保留這些完整路徑使先篩不剔除，再讓排序較前的筆記含一行接近 2 萬字且帶 `src`。該行會做「桶內候選數 × 行長」的子字串掃描；截止時間只在進入該行前檢查，無法在桶內中止，推送可能遠超過宣稱的 30 秒才落成 timeout。
4. 這也會把本來可判的推送記成判不了，抬高兩週量測的 timeout 比例。應在桶內定期檢查截止時間，並補共同前綴與無 ASCII 段名稱的壓力案例。
5. 未能重現：唯讀沙盒無法建立共同規則要求的 shared clone，故依規則自降一級；以上為靜態可達路徑。

## 其餘鏡頭核對

- `lumos-cli-read`：search 的 stale／superseded 過濾路徑未被修改。
- `bound-tests-gate`：合約測試的阻擋語意未變。
- `guard-kill`：回傳碼優先序與 JSON 純度路徑未變。
- `授權與歸屬`：授權標頭及 vendored 清單未變。
- `測試假綠形態`：F1 的壓力測試只證明「第一段互異」的輸入，未證明共同前綴現場。
- `lumos-cli-lifecycle`：re-inject sentinel 外內容未受影響。
- `design-loop`：處置閘與計劃審材判定未受影響。
- `pitfalls-code-loop`：`gov` 去重把 `check` 納入鍵的方向正確，未看到 c1–c5／probe 事件被誤折。

另核對重定基底結果：`drift_check.gate` 仍預設 `block`，`drift_check.old_sentence` 仍獨立預設 `warn`；未發現兩者回傳碼接反或 warn 模式被 m1 誤擋。

最高等級:minor