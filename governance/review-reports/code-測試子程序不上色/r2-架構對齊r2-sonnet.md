severity: minor

我看到的內容:這次改動只動 `scripts/test_lumos.py` 和 `Systems/測試假綠形態.md`。固定席是該筆記的 ★INVARIANT★(翻紅釘要配前置斷言)。附加的表態記錄只講探針腳本,跟本次無關。我對照的是修後 205ebbf 的正文。

**問 1 分層與依賴方向:對齊。**
- 色彩中和放在 `main()` 唯一進入點:`scripts/test_lumos.py:35501-35502`。
- 它緊接在清 `GIT_*` 的 `_os_env.environ.pop` 之後(約 `:35490`),用同一個 `_os_env`、同一種「進程環境一次清好」的寫法,沒有往下一層推。
- 守衛測試只讀 `os.environ`,再起 `_sp.run` 驗證,跟 `t_runner_isolates_real_home_and_tmp`(`:628-650`)的「進入點設好、測試只驗」同構。
- 沒有跨層直呼。

**問 2 命名與錯誤處理:大致對齊,有一處不一致。**
- 前置斷言放在最前面,位置跟同檔 `:635`、`:647` 的「★前置★ 現場成立」一致。
- 訊息裡的「現場成立——」破折號寫法,`:7189` 也有同樣寫法。
- 「不上色:」前綴跟 `scaffold:`、`skills:`、`install:` 這類每支測試自選前綴的做法一致。
- 不一致:前置斷言的現場是用「環境原樣、只補 FORCE_COLOR=3」造的(`:516-517`),它依賴使用者殼裡沒有 NO_COLOR(見 A1)。同檔其他前置斷言(`:635`、`:647`、`:590`)檢查的都是自己造的現場,不吃外部環境。

**問 3 第二種做法:沒有。**
- 我用 `git grep` 查 205ebbf 全 repo,加上對 `/tmp/code-color/t.py` 的 grep,程式裡的 `NO_COLOR`、`FORCE_COLOR`、`PYTHON_COLORS` 只出現在 `scripts/test_lumos.py`,其餘只在筆記和 governance 的文字裡。
- 該檔的出現處是:守衛測試 `:509-520`、`main()` 的 `:35497-35502`、`search -h` 那支測試的註解 `:50893`。
- 拿掉 `search -h` 測試自帶的 `NO_COLOR` 後,同檔已沒有另一套「每支測試各自帶色彩變數」的做法。
- 守衛測試內只有一份局部的 `bare` 環境字典,是為了造反例現場,不是第二種中和機制。

## A1 前置斷言的現場吃使用者殼裡的 NO_COLOR
severity: minor
blocking: 否
引句:「    bare = {k: v for k, v in os.environ.items() if k != "PYTHON_COLORS"}」
佐證:file: `scripts/test_lumos.py:516`
佐證:file: `scripts/test_lumos.py:635`
失敗場景:殼裡同時有 `NO_COLOR` 時,`bare` 會把它原樣帶進子程序。我實測 `NO_COLOR=1 FORCE_COLOR=3 python3.14 -c "raise RuntimeError('x')"` 的輸出不含 `\x1b[`。這時前置斷言(`:518`)紅,卻不是因為中和壞了,而是現場沒成立。`main()` 沒清 `NO_COLOR`,所以這是 `:35497-35502` 之外的缺口。同檔 `:635` 這類前置斷言的現場都是自己造的,不吃外部環境。修法是把 `NO_COLOR` 也從 `bare` 排除,讓前置斷言檢查的只剩 FORCE_COLOR 這一個變數,跟其他守衛一樣只吃自己造的現場。
歸因:有證據的修復回歸。查證命令:`git -C /Users/enzo/harness/lumos-color show 91b8f331:scripts/test_lumos.py | grep -n "bare"` 應無輸出,前置斷言是修補才加的,而修補前的測試只有 ①②③。我沒有實跑這個查證命令,結論來自修補差異 `/tmp/code-color/r2-repair.patch` 的 `bare =` 是新增行。

不對齊共 1 條,其中重大 0 條
總結: 這次修補沒有另起一套做法,色彩中和仍只放在進入點、也沒有別處自帶色彩變數,只是新加的前置斷言會被使用者殼裡的 NO_COLOR 弄成誤紅,屬小瑕疵。
