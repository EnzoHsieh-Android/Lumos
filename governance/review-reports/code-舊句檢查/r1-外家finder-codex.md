severity: major

## F1 無副檔名 Python 腳本改成其他格式時，舊定義整批漏報

severity: major  
blocking: 是  
引句:「k = _drift_m1_code_kind(p, run.head(run.spec(run.tip, tl, p) if st != "D" else run.spec(run.base, bl, p)))」  
file: `scripts/lumos:28970`  
file: `docs/lumos-toolchain-knowledge/Projects/舊句檢查_計劃.md:175`

1. 對狀態 `M` 的無副檔名檔案，分類只看終點首行。若起點是 Python 腳本，終點移除 Python shebang 或改成 shell，起點仍是本次應比較的 Python 檔，卻分別被分類成「非程式」或 `other`。
2. 前者使 `_drift_m1_classify` 回空清單；若這是唯一改動，m1 不印結論也不記帳。後者雖算程式檔，但 `_drift_m1_rough` 只對 `k == "py"` 抽定義，因此仍把所有刪除的函式、類別、指派與旗標漏掉。
3. 例如 `scripts/tool` 起點含 `#!/usr/bin/env python3` 與 `def old_helper_x()`，終點改成 shell 並刪掉該函式；筆記仍寫著 `old_helper_x`，即使 `old_sentence=block` 也不會擋。

最小唯讀重現：

```text
python->plain []
python->shell [('M', 'scripts/tool', 'other')]
```

這是直接以假起終點首行呼叫 `_drift_m1_classify` 的輸出。修正需要同時分類起點與終點；起點為 Python、終點不再是 Python時，仍須以起點定義對空集合或終點 Python 定義集合判消失。

## F2 候選名稱與表態名稱正規化不同，合法路徑無法被表態

severity: minor  
blocking: 否  
引句:「rec["names"] = sorted({str(n).strip() for n in names})」  
file: `scripts/lumos:27671`  
file: `scripts/lumos:28673`

1. `_drift_m1_name_ok` 只用去頭尾空白後的長度驗證候選，卻保留原字串；`drift ack` 寫帳時則會 `.strip()`。刪除名稱含頭尾空白的合法 Git 路徑後，finding 帶原名稱，但照提示表態會存成不同名稱，永遠無法滿足子集比對。
2. 候選端以 `_esc_clean` 判單行，表態端則用更嚴格的 `_drift_one_line`。例如含 U+2028 的路徑在候選端通過，表態端卻拒絕。
3. 唯讀重現結果：

```text
candidate_ok True
ack_error --name 每個都要去頭尾空白後 1 到 200 字、一行(這個不行:'src/x\u2028y.py')
space_candidate_ok True stored_ack src/x.py
```

候選生成與表態應共用完全相同的正規化及單行判定；否則 block 模式只能改筆記或整道略過，不能對該筆精確表態。

## 圖譜鏡頭逐項判定

- `Systems/lumos-cli-read`：不影響；search 的 superseded/stale 濾網未被修改。
- `Systems/bound-tests-gate`：不影響；code-loop check 與合約測試執行路徑未變。
- `Systems/guard-kill`：不影響；回傳碼優先序及 JSON stdout 合約未變。
- `Systems/授權與歸屬`：不影響；授權白名單、移除流程及主程式檔頭未變。
- `Systems/測試假綠形態`：未直接破壞合約；但 F1 的「起點是 Python」轉態目前沒有覆蓋。
- `Systems/lumos-cli-lifecycle`：不影響；re-inject sentinel 外內容保留機制未變。
- `Systems/design-loop`：不影響；處置閘與條款綁測試判定未變。
- `Systems/pitfalls-code-loop`：不影響；風險分級及代碼審留痕路徑未變。

驗證限於唯讀原始碼檢查及不寫檔的函式級重現；未執行會建立暫存 repo 的測試子集。

最高等級:major