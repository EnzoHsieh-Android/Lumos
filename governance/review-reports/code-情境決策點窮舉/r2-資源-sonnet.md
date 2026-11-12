severity: minor

hook 沒附固定席節點(只有「沒附固定席節點」的參考段),我讀了 `/tmp/lumos-seat-work/code-情境決策點窮舉/lens-r2.txt` 當固定席,沒有逐條可答的節點筆記。警告鎖我只看、沒有刪。

## 1. `_bad_lines` 拿 `splitlines()` 與 `split("\n")` 兩套行數對同一份檔
severity: minor
blocking: 否
引句:「code = lumos._strip_c_comments(text, blank_strings=True, keep_newlines=True, kotlin=True).split("\n")」
file: `configs/ast-grep/kotlin-android/check.py`(修後 `_bad_lines` 內),同函式的 `raw = text.splitlines()` 與 `code[no - 1]` 取值。
具體失敗場景:壞例檔含換頁字元(`\x0c`)、U+2028 這類 `splitlines()` 會切、`split("\n")` 不切的字元時,`raw` 的行數比 `code` 多,`// BAD` 的行號對到錯的 `code` 行。
- 複現:`printf 'val a = 1\x0c\nval b = 2 // BAD\n'` 寫成 `bad/kt-x/A.kt`,呼叫 `_bad_lines(lumos, 目錄, 'kt-x')`。
- 結果:`raw` 三行、`code` 三行但位置錯開(`['val a = 1\x0c','val b = 2 ','']`)。`no=3` 取到空字串,找不到下一個語句,回傳 `([], [])`,沒有問題也沒有 BAD 行。
- 後果:該規則的片段會被誤報「片段不在 samples/bad/…標了 // BAD 的行上」。U+2028 版(`B.kt`)同樣回 `([], [])`。
- 影響面:壞例樣本是 repo 內自己寫的檔,要出現這類字元才會觸發,所以只算 minor。
- 修前對照:修前版本只用 `splitlines()`,不會錯位。
歸因:有證據的修復回歸。兩版查證:修後實跑上述複本得 `([], [])`;修前 `8cd6d3c5e` 的 `_bad_lines` 只有一套行數來源,沒跑同一案例,所以修前結果是讀碼推得、未實跑。

## 資源鏡頭

我是在 `/Users/enzo/harness/lumos-d4-triggers` 唯讀量 `--catalog-only`。這台沒有 ast-grep,`--sg` 完整模式沒跑。

- **子程序、逾時、Ctrl-C**:這份 diff 沒有新增子程序、執行緒或逾時設定。`SCAN_FAILED` 與 `scan_index` 的接線只是把鍵改成共用的 `_sample_abs`,掃描本身是舊程式碼。測試新增的暫存目錄(`gctl-badlines-*`、`gctl-ktpack-*`)都在 finally 裡 `rmtree`。`mc.HERE.parents[2]` 對到 mkdtemp 的根目錄,沒有指到真 repo。
- **時間預算**
  - 有 `__pycache__` 時,`--catalog-only` 兩次:1.09 秒 / 67MB、0.97 秒 / 66MB,0 個問題。
  - 沒編譯快取時(`PYTHONPYCACHEPREFIX` 指到全新目錄):5.04 秒 / 405MB,0 個問題。
  - 程序內分段計時:API 段 0.28 秒,反查段 0.18 秒,共 195 個反查單位。
  - 以上跟作者的表態一致,我這邊沒有反駁的證據。
- **記憶體與二次方**
  - 逐檔整份讀入,只在 `_bad_lines` 與 `_fence_body` 內。
  - `_strip_c_comments(kotlin=True)` 是明確堆疊加線性掃描,沒有遞迴。
  - `_fence_body` 每個單位重跑兩次 `_visible_lines`(全範本檔),量級是單位數乘範本行數,實測可忽略。
  - 連續單獨成行的 `// BAD` 會讓 `nxt` 搜尋變二次方,但要上萬行刻意構造的壞例檔才有感,沒有真實場景,所以不標 finding。

## 三問回答
1. **原問題的修復效果**:靜態與行為證據是真型錄 `--catalog-only` 回 0 個問題(兩種快取情況都跑了),`_parts_in_order` 對只有 `…` 的片段改回 `False`。G1 到 G6 各守衛的逐案翻紅,我沒有獨立跑 `t_kt_catalog_bad_snippets_reach_rows`,**未判定**。修前逐案原始輸出沒保存,修前都是「未保存」。
2. **修補處的正常、錯誤與相鄰路徑**:正常路徑(真型錄)成立。錯誤路徑中,非 UTF-8 檔改回問題不崩,我只讀碼確認、沒有實跑。相鄰路徑有一處不成立,就是 finding 1:`splitlines` 與 `split("\n")` 在非 `\n` 換行字元上錯位。
3. **新發現的同一案例修前修後**:修後 `A.kt` 與 `B.kt` 都回 `([], [])`,會誤報。修前版本未實跑,只能說讀碼上沒有這個錯位。

未驗範圍:`--sg` 完整模式(缺 ast-grep)、`flatMapConcat` 等 D-4 樣本檔判定、`-k` 子集測試。

總結:最高等級 minor,共 1 條
