severity: major

## F1 無副檔名 Python 檔失去 shebang 時整批消失於檢查與量測

severity: major
blocking: 是
引句:「+        k = _drift_m1_code_kind(p, run.head(run.spec(run.tip, tl, p) if st != "D" else run.spec(run.base, bl, p)))」
file: `scripts/lumos:28970`
file: `governance/eval/drift-exam/old-sentence/old_sentence_exp.py:502`

1. 對狀態 `M` 的無副檔名檔，分類只檢查終點首行。若起點是 Python 腳本，終點移除 shebang 或改成一般文字，結果是 `None`；若改成 shell shebang，則結果是 `other`。兩者都不會比較起點 Python 定義，因此被移除的函式與旗標完全不會成為候選。

2. 最小重現：

```python
# 載入 scripts/lumos 後
class R: pass
r = R()
r.base, r.tip = "base", "tip"
r.listing = lambda w: ({}, [], {"scripts/tool": w})
r.spec = lambda w, o, p: o[p]
r.cached = lambda s: False
r.read = lambda ss: None
r.head = lambda s: "#!/usr/bin/env python3" if s == "base" else "plain text"

print(m._drift_m1_classify(r, [("M", "scripts/tool")]))
```

輸出：

```text
[]
```

3. `coded=[]` 會讓正式檢查直接當成純文件推送：不印結論、不記治理帳，也看不到起點版消失的定義，違反「有改到程式檔就必記帳」及起終點兩版抽定義的條款。參考實作的 revisit 同樣用 `tt.get(b) or bt.get(a)` 優先挑終點，因此兩週重跑也看不到這一類漏報，無法由準度量測揭露。

4. 分類必須分別判斷起點與終點；任一邊是程式檔就應納入，而起點是 Python 時仍須抽取其定義，即使終點已不是 Python。

## F2 候選名稱與表態採用不同正規化，block 模式可永久卡住

severity: major
blocking: 是
引句:「+    return 1 <= len(s) <= _DRIFT_M1_NAME_MAX and _esc_clean(name, 10 ** 6) == name」
file: `scripts/lumos:28676`
file: `scripts/lumos:27635`
file: `scripts/lumos:27671`
file: `scripts/lumos:27566`

1. 候選檢查用原字串 `_esc_clean(name) == name`，但 `drift ack` 寫帳時會對名稱執行 `.strip()`，而之後又拿儲存值和未正規化的 finding 名稱做精確集合比較。

2. 刪除名稱以空白開頭的真實路徑，例如 ` tools/run.py`，提示產生的表態會成功寫入，但永遠無法涵蓋原 finding：

```text
name_ok= True ack_validation= None
stored_name= tools/run.py
left_after_ack= 1
```

也有相反情況：U+2028 行分隔字元未被 `_esc_clean` 視為控制字元，因此候選會被列出，但表態入口用 `_drift_one_line` 拒絕：

```text
name_ok= True
ack_err= --name 每個都要去頭尾空白後 1 到 200 字、一行(這個不行:'tools/line\u2028break.py')
splitlines= ['tools/line', 'break.py']
```

3. 在 `old_sentence=block` 時，合法表態成功後下一次推送仍重複擋下；U+2028 案甚至沒有表態出口，只能改寫筆記或略過整道漂移檢查。這也違反計劃明訂「含控制字元不列，因為沒有表態出路」。

4. 候選生成、提示、表態寫入與涵蓋比對必須共用同一個 canonical name；至少應用 `_drift_one_line` 判候選，並避免只在寫表態時單方面 `.strip()`。

## 圖譜鏡頭判定

- `lumos-cli-read`：改動未碰 search 的 superseded/stale 過濾與三路分岔，未發現破壞。
- `bound-tests-gate`：未改 code-loop 的合約測試收集、執行或 rc 判定。
- `guard-kill`：未改 rc 優先序或 JSON stdout 純度。
- `授權與歸屬`：未改 vendored 白名單、deinit 刪除流程或檔頭授權文字。
- `測試假綠形態`：本報兩項均以直接執行的最小重現確認，不依賴新增測試宣稱。
- `lumos-cli-lifecycle`：未碰 re-inject sentinel 或 CLAUDE.md 區外內容保留。
- `design-loop`：未改設計審處置閘、計劃審材限制或條款測試進度判定。
- `pitfalls-code-loop`：未見既有 code-loop 行為回歸；否決理由集中在 m1 分類與表態邊界。

最高等級:major