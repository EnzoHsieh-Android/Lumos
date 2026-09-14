severity: major

## F1 編譯期錯誤不收的範圍遠大於文件講的「import 解析不到」,把真的自成一體的錯也吞了

severity: major
blocking: 是
引句:「代價:解析不到的型別會被當成動態型別,依賴它的部分警告可能報不出來(漏報,不是誤擋)。」
file: `scripts/lumos:20988`

`_DART_SKIP_TYPES = {"COMPILE_TIME_ERROR"}` 是整個 type 一律丟,不是只丟「因為快照缺 import/套件解析設定」造成的那種。實測用真 dart 3.13.3 分析單一支自成一體、不需要任何 import 的檔:少給參數(`not_enough_positional_arguments`)、同檔內打錯變數名(`undefined_identifier`)、型別不符(`invalid_assignment`)、對型別呼叫不存在的方法(`undefined_method`)——四種全部回報 `type: COMPILE_TIME_ERROR`,而且完全不涉及跨檔案解析。這些正是這道閘要抓的「AI 寫碼特有的錯」(參數個數錯、打錯名字、型別不符),卻被這個過濾器連同「import 解析不到」的假警報一起吞掉,而文件只講了後者、沒交代前者。

最小重現(真跑,非模擬):

```
$ dart analyze --format=json lib/b.dart   # 單檔、無 import
{"code":"not_enough_positional_arguments","type":"COMPILE_TIME_ERROR","problemMessage":"2 positional arguments expected by 'add', but 1 found."}
{"code":"undefined_identifier","type":"COMPILE_TIME_ERROR","problemMessage":"Undefined name 'totallyUndefinedLocalName'."}
{"code":"invalid_assignment","type":"COMPILE_TIME_ERROR","problemMessage":"A value of type 'String' can't be assigned to a variable of type 'int'."}
{"code":"undefined_method","type":"COMPILE_TIME_ERROR","problemMessage":"The method 'frobnicate' isn't defined for the type 'int'."}
```

接上實際的新增告警閘(`_lint_new_verdict`),base 版 `add(int a,int b)` 正常呼叫、head 版新增一行 `add(1)`(少一個參數,同檔內、無 import、真的是錯):

```
status: clean  blocked: False
new: []
ran: ['dart analyze --format=json {LINT_FILES} 2>/dev/null | python3 scripts/lumos dart-sarif --out {LINT_SARIF_OUT}']
```

閘判「乾淨」,這條新引入的真錯完全沒被擋下——不是「型別解析不到的漏報」,是一個單檔就能查出來的呼叫錯誤被整批過濾器吞掉,而且文件與程式碼註解都沒有交代這一半。

## F2 冒煙換檔認的是「git 追蹤到的檔」不是「專案裡有的檔」,剛寫好還沒 git add 的檔會讓修好的冒煙又變回失敗

severity: major
blocking: 否
引句:「這個棧在專案裡一支檔都沒有時原樣送出(冒煙只驗得到「命令本身」)。」
file: `scripts/lumos:17174`

`_lintcheck_smoke_cmd` 用 `git ls-files -z -- "*.<stack>"` 找可以塞進 `{LINT_FILES}` 的真檔,但 `git ls-files` 預設只列「索引裡有的檔」(已 `git add` 或已 commit),不是「工作目錄裡有的檔」。docstring 講的前提是「這個棧在專案裡一支檔都沒有」,但實際觸發原樣送出的條件是「這個棧沒有被 git 追蹤的檔」——兩者不一樣,而新專案剛裝 dart 棧、寫完第一支 `.dart` 檔、還沒 `git add` 就先跑 `lint-check --smoke` 驗收宣告,正是這個功能設計要服務的第一手場景。

最小重現(真跑 CLI):

```
$ git init -q && mkdir -p .lumos lib
$ echo '{"dart": ["dart analyze --format=json {LINT_FILES} 2>/dev/null | python3 <lumos路徑> dart-sarif --out {LINT_SARIF_OUT}"]}' > .lumos/lint.json
$ echo 'int add(int a, int b) => a + b;' > lib/a.dart
$ git status --short        # 全部 ?? ,尚未 git add
?? .lumos/
?? lib/
?? pubspec.yaml
$ python3 <lumos路徑> lint-check --smoke
✗ lint-check: .lumos/lint.json 有 1 個問題:
  [dart] 冒煙失敗:命令跑不出可解析 SARIF(task 不存在/工具沒裝?)｜dart analyze --format=json {LINT_FILES} 2>/dev/null | python
```

`git add lib/a.dart` 之後同一條命令立刻通過(已用 `t_lintcheck_smoke_fills_lint_files` 的 harness 交叉驗證,只差在有沒有先 `git add`)。這正是代碼審 r1 整合席原本要修的那個假紅(c1),只是換了個沒被測到的時序又冒出來;而且訊息「工具沒裝?」會把人導向錯的除錯方向。這個裂縫只影響 `lint-check --smoke` 這道預檢,不影響真正推送時的 `_lint_new_verdict`(它走 `git diff` 兩個 commit,不受未追蹤檔影響),所以不算擋推送,但會讓「先驗收宣告健不健康」這件事在最常見的初次導入時序上失靈。

## 已確認

- 診斷清單/欄位形狀任一處不對就 `ValueError`→rc2 不寫檔(a1/a2/x2 的折法):`t_dart_sarif_bridge` 各種壞形狀案例本輪重跑全過,行為與 r1 記錄一致,沒有退化。
- 路徑正規化「字面算不進專案時,兩邊都換成真實路徑再算一次」(b1 的落地):把 `scripts/lumos` 複製到臨時檔案、拿掉 `_lint_run_and_parse` 裡新加的 realpath 回退區塊後,重跑 `t_dart_sarif_bridge` 的「專案根是符號連結」案例確實翻紅(`file` 變成一長串 `../../../../private/var/...`),換回原檔即綠——測試不是假守衛。另外針對「共用正規化會不會讓 ruff/detekt/eslint/SwiftLint 的路徑算錯」這個特別要查的點:讀過邏輯後,回退分支只在「字面判外、真實路徑判內」兩者矛盾時才會覆寫,對本來就在專案外的絕對路徑(字面與真實路徑都判外)不會被誤收——沒能找到會把「原本正確判成專案外」的檔案錯拉進專案內的具體輸入,這點沒有列成 finding。
- 編譯期錯誤過濾機制本身有測試釘住:把 `_DART_SKIP_TYPES` 改成空集合,`t_dart_gate_with_fake_analyzer` 的「新碼上的編譯期錯誤不擋」與「只擋新函式裡的沒用到的變數」兩個斷言確實翻紅(2 條斷言失敗),機制接線沒問題——問題在範圍(見 F1),不在有沒有守。
- 冒煙換檔機制本身有測試釘住(針對「已追蹤檔」的情境):拿掉 `cmd_lint_check` 裡呼叫 `_lintcheck_smoke_cmd` 那行,`t_lintcheck_smoke_fills_lint_files` 確實翻紅——機制接線沒問題,缺口在「未追蹤檔」這個時序(見 F2)。
- `--out` 給到不存在的目錄時 rc2 講清楚、不丟 Python 追蹤訊息(d3 的折法):本輪重跑 `t_dart_sarif_bridge` 該案例仍通過,行為與 r1 記錄一致。
- `_dart_rel` 已整支移除,`_dart_sarif_results` 確認只放原始路徑、不再自己算相對路徑(b1 的架構對齊):讀碼確認橋接層與共用正規化職責已分離,沒有殘留的第三套路徑邏輯。
- `scripts/test_lumos.py -k dart` 與 `-k smoke` 在真機(有 dart 3.13.3)上全跑,37+11 案例全過,`lumos lint-check --smoke` 在本 repo(py 棧,真檔已追蹤)本身也正常通過,沒有引入既有案例的退化。
