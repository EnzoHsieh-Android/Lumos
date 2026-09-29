severity: major

## F1 c4 會把 YAML 巢狀結構或註解改成純字串

severity: major  
blocking: 是  
引句:「        return None, "那一項是行內清單、區塊文字或 YAML 標記開頭,工具不改,要手改"」  
file: `scripts/lumos:27991`  
file: `scripts/lumos:28044`  
file: `scripts/lumos:26363`

1. 具體輸入是合法 YAML：

```yaml
valid_under:
  - - 本工作樹(未提交)
```

2. 唯讀記憶體重現顯示，掃描會列出 c4；`_drift_fix_c4` 不報錯，輸出：

```text
c4 err = None
c4 output = '  - "已提交 abc"'
```

3. 標準 YAML 解析前後分別為：

```text
{"valid_under"=>[["本工作樹(未提交)"]]}
{"valid_under"=>["已提交 abc"]}
```

`raw[0]` 白名單漏擋 `-`、`#`、`?` 等 YAML 標記。註解輸入 `- # 本工作樹(未提交)` 也被掃成 c4，修後會把原本的 `null`／註解改成真實字串。工具自己的簡化 parser 會驗證成功，因此寫入、驗磁碟與消除發現全數通過，卻已改掉標準 YAML 的資料結構。

## F2 Env.find 把根目錄明確路徑退化成同名猜測

severity: major  
blocking: 是  
引句:「        a = a[2:] if a.startswith("./") else a」  
file: `scripts/lumos:697`  
file: `scripts/lumos:38195`

1. 唯讀記憶體重現使用正常的 `Env.from_texts` 排序，放入 `z.md` 與 `A/z.md`：

```text
notes order = ['A/z.md', 'z.md']
by_stem = ['A/z.md', 'z.md']
Env.find(./z) = A/z.md
expected explicit path = z.md
```

2. `./` 被剝掉後只剩 `z`，因為沒有 `/`，程式不走精確路徑分支，而改用 stem 並取第一篇。

3. `set`、`append`、`remove` 都直接使用這個結果。執行 `lumos set ./z status done` 會修改 `A/z.md`，不是使用者明確指定的根目錄 `z.md`，屬於寫錯檔。

## F3 乾淨檢查仍把檔名當 Git pathspec

severity: major  
blocking: 是  
引句:「    r = _lens_git(root, "diff", "--quiet", "HEAD", "--", gp)」  
file: `scripts/lumos:27769`  
file: `scripts/lumos:28161`

1. 唯讀 Git 重現：

```text
$ git diff --name-only HEAD^ HEAD -- 'scripts/[l]umos'
scripts/lumos

$ git --literal-pathspecs diff --name-only HEAD^ HEAD -- 'scripts/[l]umos'
<沒有輸出>
```

2. 這證明未加 `--literal-pathspecs` 時，`[l]` 被當成字元集合，不是檔名原文。

3. 若被修筆記的真實檔名含 `[`，`_drift_git_paths` 會回傳該原始路徑，但乾淨檢查不會匹配那支字面檔案；沒有其他符合模式的髒檔時，`git diff --quiet` 回 0。工具因此把已有未提交修改的筆記判成乾淨，接著原子寫入並覆蓋使用者修改。新增的 literal 保護只接在印給人的指令，沒有接到真正決定能否寫檔的檢查。

## 圖譜鏡頭逐條判定

- `Systems/lumos-cli-read`：search 的 superseded/stale 合約未受影響；F2 破壞的是共用節點解析與其他讀寫指令。
- `Systems/guard-kill`：未改 rc 優先序或 JSON 輸出路徑。
- `Systems/lumos-cli-lifecycle`：未改 reinject sentinel 外內容。
- `Systems/bound-tests-gate`：未改綁定測試執行或阻擋判定。
- `Systems/授權與歸屬`：未改授權檔白名單或檔頭；`_sh_quote` 搬家不影響這兩條合約。
- `Systems/測試假綠形態`：新增測試有前置斷言，但漏掉 F1 的 YAML 標記、F2 的根節點同名，以及 F3 的實際乾淨檢查。
- `Systems/design-loop`：未改處置閘、計劃審材或條款綁定判定。
- `Systems/pitfalls-code-loop`：未見該節點既有合約被直接改動；F3 仍讓寫入前安全閘失真。

最高等級:major