severity: minor

## r1 點號測試名改取最後一段後，git grep 輸出隨詞出現次數線性膨脹，記憶體約為輸出的 11 倍
severity: minor
blocking: 否 這個膨脹是修補新加的，但只對詞很常見的測試名發生，也沒有造成資料或判定錯誤。
- 輸入：守的測試綁成 `FooTest.value` 這種寫法，最後一段 `value` 是常見字。
- 路徑：`_choice_test_blobs` 把查找詞改成最後一段，再用 `git grep -z -o -w -F` 對整棵樹的 `.kt` 檔查詢，不限於測試路徑。
- 為什麼會膨脹：`-o` 讓每個命中各輸出一行。`_lens_git` 用 `capture_output=True, text=True` 且沒有輸出上限。測試路徑的過濾要等 `r.stdout.splitlines()` 全部載入記憶體之後才做。
- 預期與實際：修前 `FooTest.value` 整串查不到，輸出幾乎是 0；修後輸出隨詞的出現次數線性增加。
- 量測：2000 個檔、每檔 150 行、`value` 出現 60 萬次。
  - 修前：RSS 47MB，0.14 秒，結果是不明標記 `?`。
  - 修後：git grep 輸出 37MB，RSS 413MB，約 0.6 秒，雜湊吃進 2000 個檔的物件編號（`sig_len` 81999）。
  - 估算（未實測）：記憶體隨出現次數線性長，約 1000 萬次出現會到 7GB 等級。
- 呼叫點有兩處：choice-kill 在 `scripts/lumos:78245`，推送前在 `scripts/lumos:78616`，後者時限 30 秒，但記憶體沒有上限。
- 副作用：同一個詞出現在無關的測試檔，雜湊也會跟著變，只會多重跑，不會漏。
- 實務強度：⚠ 只有常見字當方法名時才會碰到。修前的整串寫法同樣有這個形狀（例如綁成 `value` 單名），修補只是讓點號寫法也進來。
引句:「term = {n: (n.rsplit(".", 1)[-1] if _dotted_ident(n) else n) for _p, n in keys}」
file: `scripts/lumos:77933`
歸因：有證據的修復回歸（修前同一輸入的輸出是 0，修後是 37MB。兩版都以 `_choice_test_blobs(rr, HEAD, [{"plat":"android","name":"T5.value"}], plats)` 在 `/private/tmp/lumos-seat-work/code-改動選擇點/資源-sonnet/e1` 實跑，這個暫存目錄跑完已刪）。

## 已驗的正向主張與三問回答

**① 原問題的修復效果**
- 點號名。
  - 命令：同一個 `_choice_test_blobs` 呼叫，輸入 `T5.value`、`T5.f3`、`T5`。
  - 修前：`T5.value` 和 `T5.f3` 都回不明標記 `?`；`T5` 回 40 位的物件編號。
  - 修後：`T5.value` 和 `T5.f3` 都找得到所在檔（簽名長度分別是 81999 和 40）。
  - 一般名 `T5`：兩版結果相同，一個物件編號（preserve 成立）。
  - 修後的簽名長度是 `T5.f3` 40 位、`T5.value` 81999 位。f3 只在 T5 所在檔出現一個物件編號、value 在全部 2000 檔出現，所以才差這麼多。
- 暫存目錄落在忽略 `*.kt` 的 repo 底下。
  - 命令：`TMPDIR` 設在 .gitignore 寫 `*.kt` 的 repo 內，對 `_choice_scan` 丟兩支檔、各一個 `x > y`。
  - 修前：0 個命中，沒有 bad，靜默。
  - 修後：2 個命中。
  - `TMPDIR` 設在 repo 外時，兩版都是 2 個命中，沒有退步。

**② 修補處的正常、錯誤與相鄰路徑**
- 1400 支小檔整批掃描：兩版都是 0.36 秒、1400 個命中、bad 為 0，加 `--no-ignore` 的時間和記憶體都沒有可見差別。

**③ 拿掉推送前碰到計劃的時限底線**
- 結論：推送前那一步的 `_choice_guard` 一定命中快取，所以這步的建圖沒有時限底線也沒有影響。
- 為什麼一定命中：`_choice_push_scan` 回 "ok" 之前，必先經過 `_choice_requirement`，它用同一個快取鍵 `("spec", rng, at_sha)` 呼叫 `_choice_spec_calc`。提早回傳的情形是沒有 kotlin 平台和沒有改到的 .kt，這兩種都會 skip，不會走到 guard。
- 例外路徑：`_choice_requirement` 裡 `_kt_sit_spec_names_calc` 若丟例外，結果不會被快取，但例外會被 `_choice_push_scan` 接成 unverified，不會走到 guard。
- 實測：在 `24ec789` 的副本裡，於 `_choice_guard` 入口加探針，跑 `python3.14 scripts/test_lumos.py -k spec_gate_push_choice`，結果 42 項全過。
  - 推送前呼叫端 `_choice_push_round`：17 次，全部 `has_spec=True`。
  - `_choice_ledger_status`（choice-points）：1 次，無快取、無時限。這條本來就沒有快取，修補沒動它，也不是推送前路徑。
- 未驗範圍（修補前後同樣存在，所以不算這次修補的問題）：快取命中之後 `_choice_guard` 還會做 `_platform_test_index`、`clause_bindings`、`_choice_bound_names`。`_platform_test_index` 的惰性函式會走整個平台根讀完所有程式檔成 haystack。這幾步在推送路徑上從來沒有時限，我沒有量大型 Android 樹下的耗時。

**子程序與暫存**
- 這次修補沒有新增子程序或暫存路徑：`--no-ignore` 只是 `ast-grep` 引數，`_choice_test_blobs` 仍是單次 `git grep`，逾時由 `_lens_git_dl` 的 `deadline` 控制。逾時、Ctrl-C 這幾條路徑我沒有重新實驗，不判定。

**圖譜鏡頭**：這次沒附固定席節點，沒有節點可逐條判。

最嚴重:minor;blocking 共 0 條
