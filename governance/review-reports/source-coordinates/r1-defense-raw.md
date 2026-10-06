結論：八種來源都是有效 Python，不會停在 `compile`；不需要改成三引號。

- [scripts/test_lumos.py:69726](/tmp/lumos-review-source-coordinates/scripts/test_lumos.py:69726) 的八個 AST 字元為：`\x0b`、`\x0c`、`\x1c`、`\x1d`、`\x1e`、`\x85`、`\u2028`、`\u2029`。
- [scripts/test_lumos.py:69729](/tmp/lumos-review-source-coordinates/scripts/test_lumos.py:69729) 把字元放在單引號內：`first = f"text = '{sep}'"`。
- [scripts/test_lumos.py:69731](/tmp/lumos-review-source-coordinates/scripts/test_lumos.py:69731) 明確執行 `compile(text, "sample.py", "exec")`；其後 [69736–69739](/tmp/lumos-review-source-coordinates/scripts/test_lumos.py:69736) 才呼叫共用 `_validate_repo_ref`。
- [scripts/test_lumos.py:69705](/tmp/lumos-review-source-coordinates/scripts/test_lumos.py:69705) 的 fixture 會把相同 UTF-8 位元組寫入 `src/sample.py`，再建立 Git 提交。

Python 3.14.6 實測：從測試 AST 取出八個字元，逐一建立相同兩行來源後，八組皆得到：

```text
compile=ok
exec=ok
執行後 text 值等於原特殊字元
實體 LF 數量=2
```

再直接執行抽出的測試函式、於共用 validator 呼叫邊界計數，得到：

```text
validator_calls=64
8 字元 × 2 種來源（worktree/HEAD）× 4 種座標
各座標 2、3、1-2、1-3 均被呼叫 16 次
```

因此它們確實能越過 `compile`，走到共用引用驗證。改三引號不能修正行號判定，也不是有效性所需；反而會改變被測來源的詞法形狀。

需嚴格區分：以上證實「來源可 compile/exec」及「控制流程可達 validator」，不等於證實目前行號驗證已修正。唯讀沙箱拒絕建立 `TemporaryDirectory`，所以這一席沒有取得真實 worktree/HEAD validator 的通過結果，也不推論整體測試為綠。