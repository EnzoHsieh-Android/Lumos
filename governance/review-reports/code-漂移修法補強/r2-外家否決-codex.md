severity: major

## F1 暫存區差異卻用工作目錄指紋分類，會漏報使用者刪除並誤報工具更新

severity: major
blocking: 是
引句:「+        parsed = _delguard_parse_diff(r.stdout, gr_rel, frozenset() if _is_toolchain_repo(root) else _vendored_state(root)[0])」
file: `scripts/lumos:17799`
file: `scripts/lumos:29581`
file: `scripts/lumos:29598`

1. `git diff --cached` 與後續 `_delguard_confidence(... --cached)` 都檢查暫存區，但 `_vendored_state(root)` 的 `ref=None` 明確讀工作目錄。兩份快照不一致時，跳過集合便不是被提交內容的分類結果。
2. 消費專案先修改工具同名檔並 staged，再只把工作目錄還原成安裝版時，工作目錄指紋吻合，暫存區內使用者刪掉的名稱卻整支被跳過。唯讀純解析重現：

```console
$ PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3 -c 'ns={"__file__":"scripts/lumos","__name__":"lumos_review"}; exec(compile(open("scripts/lumos",encoding="utf-8").read(),"scripts/lumos","exec"),ns); diff="diff --git a/scripts/lumos b/scripts/lumos\n--- a/scripts/lumos\n+++ b/scripts/lumos\n@@ -1 +1 @@\n-def UserOwnedGuard():\n+x = 1\n"; print(ns["_delguard_parse_diff"](diff,"docs/x-knowledge",frozenset({"scripts/lumos"})))'
{'tokens': [], 'vault_diffs': {}, 'vendored_skipped': ['scripts/lumos']}
```

3. 反向也會錯：先 staged 一次原封不動的工具更新，再於工作目錄追加尚未 staged 的自訂內容；工作目錄指紋不符，守衛便掃描本應跳過的純工具更新，對工具鏈刪掉或改名的舊符號產生誤報。
4. 這不是第一輪「只看檔名」的舊問題；本輪改成看指紋後新增了快照錯位。現成 `_vendored_state(root, "")` 才讀暫存區及其中的 manifest。

## F2 近似佔位字正則會擋下正常的數量比較條件

severity: minor
blocking: 否
引句:「+    return re.compile("[<\uff1c]" + r"\s*" + word + r"\s*(?![\w-])|" + before + word + "[>\uff1e]")」
file: `scripts/lumos:14636`
file: `scripts/lumos:14641`
file: `scripts/lumos:15165`

1. 中文佔位字的「只剩右角括號」分支沒有左側邊界，因此正常條件 `若卷證>20個就重驗` 會把 `卷證>` 認成殘缺的 `<卷證>`。
2. 唯讀函式重現：

```text
輸入: 若卷證>20個就重驗
匹配: <卷證> → 卷證>
```

3. `_set_conditions_locked` 見到這個匹配後立即回傳 2，原本可寫入的正常 `revalidate_when` 因本輪修正被誤擋。相同問題也出現在文字 `輸出 git-sha> 時重驗`；程式註解聲稱這種形狀不算佔位字，實際仍匹配 `sha>`。
4. 新測試只驗 `a < b`、`sha 值 > 3` 與 `commitsha>`，沒有覆蓋保留字本身作為比較運算元或前面接連字號的正常內容。

## F3 NFC 等價檢查會把已改名的 Git 舊名當成現存目錄印出

severity: major
blocking: 是
引句:「+        if d and d not in out and nfc(d) in keys:」
file: `scripts/lumos:27980`
file: `scripts/lumos:27988`
file: `scripts/lumos:27993`
file: `scripts/lumos:28008`

1. `_drift_c4_same_commit` 以目前磁碟目錄的 NFC 集合判斷舊 Git 原名是否「還存在」，匹配後卻輸出 Git 原名。若目錄後來只做了 NFC／NFD 拼法改名，舊名在區分正規化的檔案系統上已不存在，仍會被列為同提交證據。
2. 唯讀函式重現：

```text
current= ["'code-Caf\\xe9'"]
reported= ["'code-Cafe\\u0301'"]
reported_exists_exactly= [False]
nfc_equal= True
```

3. 證據頁會印 `governance/review-reports/code-Café`，但目前真目錄只有 `governance/review-reports/code-Café`。使用者依清單填進 `valid_under` 後會得到指不到真目錄的路徑。
4. 新測試甚至用目前集合只有一種原名、Git 回兩種 NFC 等價原名的資料，要求兩種都列；它把這個失敗行為固定成綠燈，沒有驗證每一條印出的路徑都能精確命中目前目錄。

## 圖譜鏡頭逐條判定

- `Systems/存量漂移守衛`：F3 破壞 c4 證據頁只列現存真目錄的行為；c1 與 c3 的本輪修正未見另洞。
- `Systems/bound-tests-gate`：未改固定席合約測試的發現、執行或阻擋判定，不影響該合約。
- `Systems/guard-kill`：只改 settle 缺句組字；kill 的回傳碼優先序與 JSON 純度未受影響。
- `Systems/授權與歸屬`：沒有增減 `_VENDORED_ALL` 成員，也未改授權檔或 deinit 刪除流程，不影響兩條授權合約。
- `Systems/測試假綠形態`：受影響。delguard 測試把 index 與工作目錄維持一致，漏掉 F1；c4 測試直接接受 F3 的不存在原名；set 測試漏掉 F2 的正常比較式。
- `Systems/lumos-cli-read`：未改 search 的 stale／superseded 過濾，不影響。
- `Systems/lumos-cli-lifecycle`：未改 re-inject 或 sentinel 外內容保留，不影響。
- `Systems/design-loop`：未改處置閘、計劃審材或條款綁定判定，不影響。
- 超出鏡頭上限的節點中，`Systems/delguard` 直接受到 F1 影響；`lumos-deinit` 與 slim 安裝系列雖共用工具檔集合，但本輪未改其安裝、更新或移除流程。其餘所列治理閘、索引、審查與回放節點未碰到對應路徑，判不影響。

最高等級:major