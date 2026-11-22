severity: minor

## g1 C-40~C-47 改回正面寫 inside 後,長鏈輸出量變大,輸出量守衛的覆蓋少了這八條
severity: minor
blocking: 否

引句:「規則跟 C-19~C-31 一字不差(只往上兩層、不往下找,」

- 重現輸入(300 次 `.singleOrNull()?` 串成一條鏈):上一版(修前)與這一版(修後)各掃一次。
  - 上一版 `926c720…` 的 api.yml:整套規則掃出 1.60MB。
  - 這一版 `9ebd62d…` 的 api.yml:掃出 4.67MB,仍是 300 筆 C-40 命中。
- 命中集合沒變。大小是次要標記造成的,每個命中都帶著外層鏈,隨鏈長平方成長。
- 另一個輸入(300 次 `.firstOrNull { it.toIntOrNull() != null }`):上一版 7.7MB,這一版 15.5MB。
- 這是作者刻意取捨。計劃第 111 行已記錄巢狀 200 層約 23.8MB,與第一版 C-19 同量級。
- 缺口在守衛。`t_choice_scope_rule_output` 這輪實跑 14 條全過,但它只覆蓋 C-38、C-39、C-48、C-53,C-40~C-47 沒有任何輸出量守衛。往後若有人把 C-40~C-47 再加一層 inside,`t_choice_rule_shape_batch3` 會要求外包雙重否定,但不會量輸出。
- 長鏈撞 64MB 上限的臨界點我沒有找。
- 歸因:未判定。上一版的雙重否定輸出明顯較小,所以量變大來自本次修補;但改回正面寫是為了統一形狀,不算漏洞。
- 兩版查證命令:`ast-grep scan --rule <舊版或新版 api.yml> --json=compact a.kt | wc -c`。

## 已驗主張(零 blocking)
severity: clean
blocking: 否

引句:「建立後立刻 .await()/.join() 的照算:不看先後的排除會把同時跑的兄弟一起排掉」

- 作用域兩列拿掉「建立後立刻 await/join 的不算」排除:
  - 樣本 `supervisorScope { launch { g() }; async { f() }.await() }` 等三條「先開一支不等、再開一支立刻等」的 HIT 標記,在 `t_choice_samples_batch3` 全過(43 條)。
  - 每支都立刻等的樣本改標 HIT。型錄 C-38、C-39、計劃第 107、148、190 行、api.yml 兩處註解、test_lumos.py 的 `_CB3_S5_MARKS` 與翻紅釘說明,都已一致改成「照算、落成等價放行」。
  - 我沒找到留下舊說法的地方。
  - `choice-batch3.kt:103` 與 api.yml 第 590 行那兩處「立刻等不收」指的是 C-50(LAZY),不是子協程,沒有錯。
- `t_choice_rule_shape_batch3`(S11)實跑 20 條全過,C-19 的判準自驗也過。
  - 我讀過 `_cb3_rule_shape` 的縮排與 `inside` 計數:C-40 的 `inside:` 加 `inside: {…}` 算 2 層,不超過 2,判成不用包,符合預期。
  - 判準用正規表示式掃文字,沒有做 ast-grep 解析;對現有規則沒有誤判。
- 未驗範圍:
  - 我沒有真的拿掉雙重否定或加回排除來翻紅 S11 與 S5。
  - 沒有跑不帶 `-k` 的全套測試。
  - 文件半邊(Systems/kotlin規則包 的 WHY 全文)只看了 grep 命中的行,沒有逐條核對。

總結:最高嚴重度 minor,blocking 共 0 條
