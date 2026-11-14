severity: major

被審範圍是 p1 這一包(掃描與型錄),實驗在我自己的臨時副本做,已刪。

我在 `7826895c1` 的副本裡讀完整份 patch,並做了這幾件事。

- 跑 `-k choice`,204 全綠。
- 拿真實 Kotlin 檔(約 250 支、492 個壞法)當輸入,每個壞法都做 `old→new` 重現比對,零不符、零例外。
- 用 gradle 內建的 kotlin-compiler 2.2.21 編譯 713 個壞法,語法層級沒壞。
- 唯一的編不過是字串串接(下面 c13)和 `s != null || s.length` 這種智慧轉型(型別層,必然)。

固定席筆記沒附上(鏡頭計算超時),所以圖譜鏡頭沒有固定席可逐條判;下面「圖譜與角色鏡頭」一節只判我讀到的影響面。

## c11 洗牌與種子沒有任何測試守:種子改成常數,204 支測試全綠
severity: major
blocking: 是——「類別洗牌、行指紋當種子」是論文 4.1 與規格明寫的必要行為,能指出具體改壞而測試照綠。

引句:「    random.Random(seed).shuffle(cats)」

- **改壞方式。** 把 `_choice_pick` 的 `seed = int(fp, 16)` 改成 `seed = 0`,整套 `-k choice` 仍是 `204 passed, 0 failed`。拿掉 `shuffle(cats)` 那行,p1 的 stable、scan、operands 也全綠。
- **輸入與落差。** 40 行 `if (a{i} > b && c || d + 1 > e) go()`,只有變數名不同:
  - 原版挑到 `UOI 15、LCR 9、ROR 8、AOR 8`。
  - 種子常數版 40 行全是 `ROR`。
  - 洗牌拿掉的後果:類別永遠依表順序取,不再依行分散。
- **測試為什麼抓不住。**
  - `t_choice_points_stable` 的「洗牌後 AOR 排第一」,AOR 被型別前提排除就改挑 ROR。常數種子或不洗牌時,AOR 或 ROR 排第一,結果都是 ROR。
  - 「一行有 ROR、LCR、UOI 三類只挑一個」只斷言類別落在三者之一,不洗牌也成立。
  - 「同一行跑兩次」「rebase 後同指紋同壞法」,常數種子必然穩定,等於沒測。
  - 缺的判準:不同指紋的行要挑到不同類別(統計或幾組已知指紋的預期類別)。
- file: `scripts/lumos:77232`、`scripts/test_lumos.py:143578`

## c12 節點排序與「被排除就換下一個節點」同樣沒有測試守
severity: major
blocking: 是——規格〈一行一個壞法〉③⑤的行為,改壞後測試照綠。

引句:「key=lambda n: (n["anchor"], -(n["e"] - n["s"]), n["s"])」

- **排序改壞。** 改成 `(-anchor, 內層優先, -s)`(右到左、內層先),整套 `-k choice` 204 全綠。
  - 輸入:`if (a > b && c < d) go()`,只留 ROR。
  - 原版挑 C-1 `a > b`。
  - 改壞版挑 C-2 `c < d`,是同一行右邊的運算子。
- **換節點改壞。** 把 `_choice_excluded` 之後的 `continue` 改成 `break`,p1 的 scan、operands、stable、arid 全綠。
  - 輸入:`val s = "id=" + id + ", total=" + (a + b)`。
  - 原版會跳過前面被型別前提排除的節點,挑到 `(a + b)`。
  - 改成 `break` 後這一行會落成「沒有壞法」。
  - 這條只跑了 p1 的四支測試,沒跑全套。
- file: `scripts/lumos:77236`

## c13 字串串接的型別前提只看「運算元原文是否以 `"` 開頭」,變數開頭的串接照樣產出編不過的壞法
severity: minor
blocking: 否——規格天花板 2 已承認型別前提只是近似,編不過會落成 no_result 要人放行;但最常見的寫法被漏掉,有具體輸入。

引句:「return any(x.startswith('"') for x in ops)   # 字串字面值、字串樣板,或左邊開頭就是字串的串接」

- **輸入。** `val s = prefix + ": " + name`。
  - 外層 `+` 的運算元 A 是 `prefix + ": "`,開頭是識別字,所以不排除。
  - 挑到 `$A - $B` 或 `(prefix + ": ") % name` 這類壞法。
  - 我用 kotlin-compiler 2.2.21 實編,錯誤是 `unresolved reference 'minus' for operator '-'`。
  - 這類節點的 4 個候選(`- * / %`)全編不過。
- **程式註解與行為不符。** 註解說「左邊開頭就是字串的串接」,但 `title + ": " + name` 左邊開頭是變數。
- file: `scripts/lumos:77003`

## c14 `_choice_file_points` 對整檔所有命中做乾節點與 ERROR 掃描,大檔是平方時間,過大還讓整次掃描失敗
severity: minor
blocking: 否——只影響大檔或生成碼,結果仍是「沒檢查到」,不會誤擋。

引句:「n = dict(h, anchor=anchor, op=op, arid=any(a <= h["s"] and h["e"] <= z for a, z in scan["arid"]))」

- 這個 `any(...)` 與 ERROR 的 `any(_choice_err_lines(...))` 對檔裡**每一個**命中都跑,與改到幾行無關。
- 實測(兩個改到的行):

| 輸入 | 檔案大小 | `_choice_file_points` 耗時 |
|---|---|---|
| 8000 行、每行含 Log 乾節點與兩個運算子 | 0.46MB | 13 秒 |
| 4000 行,每行一個中文識別字(ERROR) | 0.2MB | 21 秒 |
| 同上 8000 行 | 0.4MB | 85 秒 |

- 掃描輸出量也有問題:16000 行、0.94MB 的檔,ast-grep 的 JSON 輸出超過 `_LINT_WT_FSIZE` 上限,被 SIGXFSZ 殺掉,回 `-25`。
  - `_choice_scan` 於是 raise `_ChoiceUnverifiable`,同一批所有檔都變成「沒檢查到」。
  - 檔案大小低於 `_KT_SIT_READ_MAX`(4MB)的過濾線,所以不會被先篩掉。
- 修法方向:只處理 `by_line` 裡有改到行的命中,或用排序加二分。
- file: `scripts/lumos:76983`(掃描回 -25)

## 沒有發現問題的部分
- **多位元組字元。** 位元組位移與行列換算在我測的輸入上都對。
- **工作樹與暫存檔。** `_choice_scan` 的暫存目錄與子程序在例外、逾時、SIGINT 路徑上都有收掉。
- **`dt_table` 一般化。** 與原行為一致。
- **`_lint_wt_cfg_inside` 抽出。** 判斷邏輯與原本相同。
- **規格對照。** 乾節點 14 列、選擇點 31 列、錨點、ERROR 整行略過、一行一個壞法都照規格實作;只有 c11、c12 是測試沒守。

## 圖譜與角色鏡頭
- **固定席。** 沒有附,無從逐條判。
- **my 判斷。** 這包的 `choice-points` 是唯讀指令,不寫帳、不改既有指令輸出。
- **be-api-compat(對外相容)。** 沒破壞。
  - 新增 `choice-points` 子指令、`scan_ranges(config_path=)`、`catalog_problems(sg=)`,都是選用參數。
  - `check.py --catalog-only` 在沒裝 ast-grep 時多印一行提醒,現存測試沒有解析它。
- **be-authz(授權)。** 不適用,本地 CLI 沒有端點。

最嚴重:major;blocking 共 2 條
