severity: major

## F1 c4 可吃掉既有引號並寫出無效 YAML

severity: major  
blocking: 是  
引句:「那一項原本有引號 → --new 不能有同一種引號(雙引號另外不能有反斜線);原本沒引號 → 換完的整項要過 _yaml_plain_ok;」  
file: `scripts/lumos:27975`

1. 輸入：

   `valid_under: "本工作樹(未提交)"`

   執行時令 `--old='未提交)"' --new='已提交'`。`--old` 合法且只命中一次，但它同時吃掉了原本的收尾引號。

2. `_drift_c4_yaml_err` 只檢查 `--new` 是否含同種引號，沒有確認替換後的整項仍保留成對引號；後面的 `parse_frontmatter` 又是寬鬆解析器，因此會接受並寫出：

   `valid_under: "本工作樹(已提交`

3. 唯讀重現：

```text
PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3 -c 'import runpy; m=runpy.run_path("scripts/lumos"); before="valid_under: \"本工作樹(未提交)\""; after="valid_under: \"本工作樹(已提交"; old="未提交)\""; new="已提交"; print("text_err=", m["_drift_c4_text_err"](old,new)); print("yaml_err=", m["_drift_c4_yaml_err"](before,after,new)); print("tool_parse=", m["parse_frontmatter"]([after])[0]); print("written_line=", after)'

text_err= None
yaml_err= None
tool_parse= {'valid_under': '"本工作樹(已提交'}
written_line= valid_under: "本工作樹(已提交
```

4. 標準 YAML 解析器對同一結果翻紅：

```text
/usr/bin/ruby -e 'require "yaml"; YAML.safe_load(%q{---
valid_under: "本工作樹(已提交
})'

Psych::SyntaxError: found unexpected end of stream while scanning a quoted scalar
exit_code=1
```

這條路會讓 `drift fix` 成功寫入已損壞的 frontmatter，違反計劃 [S5] 的「不得改壞開頭欄位結構」。修正時需驗證替換後完整項目的引號邊界，並補一格 `--old` 吃掉開頭或收尾引號的測試。

## 圖譜鏡頭逐條判定

- `Systems/guard-kill`：未改動 kill 回傳碼優先序或 JSON 純度；c1/c5 的家節點比對不影響兩條合約。
- `Systems/lumos-cli-read`：未改動 search 的 superseded/stale 過濾。
- `Systems/lumos-cli-lifecycle`：未改動 reinject sentinel 外內容保留行為。
- `Systems/bound-tests-gate`：未改動綁定測試的執行與阻擋判定。
- `Systems/授權與歸屬`：未碰 vendored 白名單、授權檔或程式檔頭。
- `Systems/測試假綠形態`：新測試覆蓋了插入引號，卻未覆蓋 `--old` 吃掉既有引號的路徑；本 finding 即由此逃逸。
- `Systems/design-loop`：未改動處置閘、計劃審材或條款綁定判定。
- `Systems/pitfalls-code-loop`：五筆 lint waiver 各有獨立指紋與理由，未改動 code-loop 判閘；未見會放行錯誤程式行為的泛化規則。

最高等級:major