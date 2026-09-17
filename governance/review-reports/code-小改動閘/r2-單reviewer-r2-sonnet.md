severity: blocker

## F1 `--no-renames` 把純改名當成 100% 重寫,大檔改名必被「相對量」擋下

severity: major
blocking: yes

引句:「r = subprocess.run(["git", "-C", str(rr), "-c", "core.quotePath=false", "diff", "--numstat", "--no-renames", git_range, "--"], capture_output=True, text=True, errors="replace")」

觀察:上一輪抓到的洞①是「numstat 對改名印 {a => b}」,這輪的修法是全面加 `--no-renames`。但 `--no-renames` 不是「印出正確路徑」,而是把一次 rename 拆成「刪掉舊路徑全檔」+「新增新路徑全檔」兩行 numstat——churn 從「這次真的動了幾行」變成「整支檔的行數」。相對量檢查用這兩行分別去跟 base 版本比:舊路徑在 base 存在、行數等於它自己整份,新路徑在 base 不存在、lt=0——兩邊都會被判成「改了 100%」。

重現(在 /tmp/seat-sc-r2-reviewer 這個唯讀 worktree 跑,不影響正式 repo):用 `_sc_setup` 建好 fixture 後,把 tests/test_x.py 撐到 364 行、Home.md 同時列 test_x.py 與 test_y.py(比照 patch 裡 t_prepush_small_change_gate ⑦ 案例的寫法),接著只做 `git mv tests/test_x.py tests/test_y.py`(**零內容改動**,純改名),提交後跑 `spec-gate --push-check`:

```
rc= 1
Projects/甲_計劃.md:全靠人驗的雙向門計劃,這次改動不算小改動——相對量:tests/test_x.py 改了 364 行(原本 364 行),超過 20% 也超過 300 行;相對量:tests/test_y.py 改了 364 行(原本 0 行),超過 20% 也超過 300 行
```

為什麼是 bug:計劃陳述的判準是「每檔 新增+刪除 ≤ base 行數×20% 或 ≤300 行」,目的是量「這次真的動了多少」。純改名(git mv,沒動任何一行內容)理論上是風險最低的一種改動,卻被算成「改了 100%」而擋下。r1 的修法只解決了「路徑字串印錯」,沒解決「churn 算錯」——這正是派工詞裡明講要覆核的反向錯,而 patch 裡唯一的改名測試(⑦)用的是 16 行的小 fixture,churn 永遠壓在 300 行絕對值門檻下,測不到這個形狀。凡是本專案自己動輒上千行的檔案(例如 scripts/lumos 本身)只要改名,不管動不動內容,小改動閘一律擋。

## F2 `_PITFALL_DIFF_SKIP_EXT` 把 .json/.html/.svg 整支排除在小改動閘之外,大改動完全隱形

severity: blocker
blocking: yes

引句:「if (path in _BOOKKEEPING_FILES or path.startswith(_BOOKKEEPING_DIR) or Path(path).suffix.lower() in _PITFALL_DIFF_SKIP_EXT」

觀察:上一輪抓到的洞④是「自開 _BOOKKEEPING_RE,要改用既有的單一源」,這輪改成疊了三個既有常數(`_BOOKKEEPING_FILES`/`_BOOKKEEPING_DIR`/`_PITFALL_DIFF_SKIP_EXT`)+ 圖譜路徑一起當「不算程式改動」的判準。但 `_PITFALL_DIFF_SKIP_EXT` 是為了另一個目的存在的(見 scripts/lumos:18426 附近註解:「資料/紀錄檔不是代碼……探針結果 JSON、治理帳、log 裡記的指令字串被當代碼掃」),它的語意是「pitfalls 正則掃描別誤傷資料檔」,不是「這支檔不算風險」。這個常數收了 `.json`、`.html`、`.svg` 三個副檔名——對前端專案(i18n/config JSON、HTML 模板、SVG 圖示)來說,這些檔常常就是真正在改的內容。

小改動閘的存在意義是「幫全靠人驗、沒有任何測試的計劃畫一條安全的爆炸半徑」;把 .json/.html/.svg 整支從 `files` 清單剔除,代表這幾種副檔名的改動不只不算進擴散/相對量,連「落點外」與「碰到裁判檔」都不會檢查——因為它們根本沒進迴圈。

重現:用 `_sc_setup` 建 fixture,把 Home.md 的 about_code 從 tests/test_x.py 換成 web/config.json(在計劃落點內),先提交一支 500 個元素的 JSON,再提交一次把它整個重寫成 1000+ 個元素(等同整支檔案重寫):

```
rc= 0
✓ 甲_計劃:全靠人驗,改動通過小改動閘(擴散/相對量/歷史/目的四維度)
```

一次上千行等級的 JSON 重寫,四個維度全部顯示「過」,因為 `files` 清單裡根本沒有這一支檔——不是「相對量算出來很小」,是完全沒被量到。這正是派工詞要覆核的方向(「_PITFALL_DIFF_SKIP_EXT 把 .json/.html 排除後前端專案的小改動會不會漏算」),而且後果比 F1 嚴重:F1 是誤擋(fail-closed,安全方向錯),這裡是誤放(fail-open)——一個設計目的是「全靠人驗的計劃至少要小」的閘,對這三種副檔名完全不設防。

## 複核

上一輪五件逐一驗過,除②有偏差外其餘四件確實關上(細節與 F1/F2 的反向錯分開列在上面,不重複):

①(numstat 改名印 {a => b})——路徑字串本身確實不再印成合併形式,`--no-renames` 有生效;但如 F1 所述,修法本身在 churn/檔數計算上引進新洞,不算完全關上。

②(逃逸帳時間戳裸字串比→走 _loop_ts_key)——呼叫端確實換成 `_loop_ts_key`,不再是裸字串比較,cutoff 也用同一支函式換算,方向對。但 `_loop_ts_key` 自己的文件明講「沒帶時區的一律不猜(回 None):呼叫端退回字串比對」(scripts/lumos:7967 附近),而這裡的呼叫端:

引句:「k = _loop_ts_key(str(e.get("ts", "")))   # 時間戳一律換算 UTC 再比(代碼審 r1 兩席:字串比對在時區位移不同時會靜默反過來)」

沒有退回字串比對,是直接 `if k is None or ... : continue`——回 None 時整筆逃逸紀錄被當「不算近期」直接跳過,不是退回字串比對。跟同檔案裡另一個呼叫端 `_loop_ts_newer`(kb/ka 任一邊 None 時才退回字串比)寫法不一致。目前 escape-log 裡的紀錄全部帶時區(專案自己量過 1101/26443 筆都是 +08:00),所以現狀不會觸發;但這是「近 90 天逃逸帳」這道歷史檢查唯一的输入來源,一旦出現舊格式或裸时间戳的紀錄,會被小改動閘的歷史維度靜默漏掉,而不是像文件說的退回字串比對去嘗試判斷。這條沒有到需要單獨列 F 的地步(目前資料不會觸發、且是保守方向的疏漏,不是危險方向),但既然派工詞點名要查,記在這裡。

③(二進位檔 numstat 印 - 記成 0)——已用 `chmod +x` 做純 mode 改動實測:git 對 mode-only 改動印 `0\t0\tpath`(不是 `-\t-`),程式碼判定為非二進位、churn=0,正確放行;對真二進位內容改動印 `-\t-`,`la.isdigit()` 為假,正確標成二進位並擋下。這件關上,沒有反向錯。

④(自開 _BOOKKEEPING_RE)——已改走 `_BOOKKEEPING_FILES`/`_BOOKKEEPING_DIR`/`_PITFALL_DIFF_SKIP_EXT`/圖譜路徑,不再自己刻正則,做到「單一源」。但如 F2 所述,`_PITFALL_DIFF_SKIP_EXT` 是借用別的語意場合的常數,套進小改動閘後放大了誤放的範圍,這件形式上關上、實際上開了新洞。

⑤(手寫 anchor-baseline 路徑/解析)——已改用 `_ANCHOR_BASELINE_REL`(scripts/lumos:16495 定義)與 `(data.get("anchors") or {})` 這個既有寫法,跟其它三處使用 `_ANCHOR_BASELINE_REL` 的地方一致。這件關上,沒有反向錯。
