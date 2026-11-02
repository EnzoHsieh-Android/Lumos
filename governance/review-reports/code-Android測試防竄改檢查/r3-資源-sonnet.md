severity: major

三輪下來，這次抓到四條會讓推送卡住或把記憶體吃光的資源問題，另有兩條次要的。F1 是這輪修補自己引入的回歸，F2 到 F4 是上限之內仍殘留的平方級（原有漏查）。

臨時目錄在 `/tmp/lumos-seat-work/code-Android測試防竄改檢查/資源-sonnet/`。重現腳本是 `gen/scen.py`，執行 `cd` 到 `gen/` 後跑 `python3.14 scen.py <情境> <逾時秒> [before,after]`，會印出修前、修後的秒數與記憶體峰值。「修後」用 `scripts/lumos`，它與 22cc667 的內容一致；「修前」用 ea1e0b8 抽出的 `lumos_before`。機器當時負載偏高（load 約 4 到 8），所以秒數偏大，看倍率比看絕對值準。

### F1 `_tg_class_has_body` 的泛型深度迴圈：上限之內平方級，比修前慢 15 到 20 倍
severity: major
blocking: 是 — 一個 200KB 到 2MB、每行都在 2 萬字以下的測試檔，能讓比對跑到遠超預算，而截止時間不會中途打斷。
引句:「depth += 1 if stripped[k] == "<" else -1 if stripped[k] == ">" else 0」
file: `scripts/lumos:48448`（迴圈在 48449 到 48455，呼叫處在 48436 的 `_tg_class_at`）

失敗場景：
- 這輪把 `find(">")` 換成逐字的 Python 迴圈。
- 一行 `class A<class A<class A<…`（共 2499 個 token、19,992 字）裡，每個 `class A` 之後的 `<` 都不會配對。
- 於是每個 token 都要掃到行尾，一行約 1.5 秒，行數一多就線性累加。
- 這比作者自己宣稱的「只看到那一行結尾、不往檔尾找」慢得多，S11 的 30 秒內也守不住。

重現（檔案形狀）：`app/src/test/kotlin/com/x/T.kt` 的內容為 `"package x\n" + ("class A<"*2499 + "\n")*N + " @Test fun a() { assertEquals(2, f()) }\n"`，base 是一支小測試檔。

| 情境 | 檔案大小 | 修前 | 修後 |
|---|---|---|---|
| `python3.14 scen.py gen10 100` | 200KB | 1.1 秒 | 16.2 秒 |
| `python3.14 scen.py gen30 280` | 600KB | 2.0 秒 | 49.4 秒 |
| `python3.14 scen.py gen100 320` | 2MB | 7.4 秒 | 153.9 秒 |

- 5MB 上限下是 250 行，用每行約 1.5 秒推算約 385 秒（推算，沒有實跑），超過預設 300 秒預算。
- 記憶體都在 340MB，不是記憶體問題，是時間問題。

歸因：有證據的修復回歸。兩版都是平方級，但修前是 C 層的 `find`，修後變成 Python 迴圈。

### F2 建置檔「每行重掃區塊開頭」：平方級仍在，修補還多加了一次
severity: major
blocking: 是 — 2 萬行、約 500KB 的建置檔就要約 21 秒，9 萬行約 98 秒，超過 S11 的 30 秒，峰值 2.25GB。
引句:「or _tg_names_test_task(head) or _tg_names_test_task(line))」
file: `scripts/lumos:48864`（同一段 `_tg_build_hits` 的迴圈到 48877；候選的 `ident` 在 `_tg_build_cands` 的 `f"{blk}\x00{line}"`，49220）

失敗場景：
- `heads[i]` 是同一個字串（最長 1.9 萬字），但迴圈每一行都對它跑 `_TG_TEST_BLOCK.search(head)`，這輪又加了一次 `_tg_names_test_task(head)`。
- 區塊開頭那行是 1.9 萬字、底下有 N 行時，工作量是 N 乘 1.9 萬。
- 每個候選的 `ident` 又複製了一份 1.9 萬字的開頭，90,000 條候選就是約 1.7GB。
- 計劃第 135 行寫的「區塊開頭用堆疊一趟算」只涵蓋算的那一步，用的那一步沒有。

重現：
- `python3.14 scen.py buildhead 150`。
- 檔案形狀是 `app/build.gradle.kts`，內容為 `"x"*19000 + " {\n"`，底下接 90000 行 `  excludeTestsMatching("c{i}")`。

| 版本 | 結果 |
|---|---|
| 修前 | 逾時，超過 150 秒 |
| 修後 | 97.8 秒、峰值 2251MB、90,001 條候選 |

函式層級的拆解（`gen/prof1.py 20000` 與 `gen/prof3.py`，N=20000 行）：
- 修前 `_tg_build_cands` 要 201.7 秒，修後 21.1 秒。
- 修後 21 秒裡，`_TG_TEST_BLOCK.search(head)` 約佔 15.7 秒（原有），新加的 `_tg_names_test_task(head)` 約佔 5.2 秒（這輪修補多的）。

歸因：有證據的原有漏查（修前更慢）；其中約 25% 是這輪修補新增的呼叫。修法是依 `head` 字串做一次判斷後記住，並且 `ident` 不要重複複製開頭（改用摘要）。

### F3 CI 行尾續行：區塊開頭可以長到 MB 級，記憶體隨「命中數 × 開頭長度」暴增
severity: major
blocking: 是 — 檔案不到 1MB，記憶體就可以破 2GB。
引句:「head = lambda idx: _tg_norm(rows[parent[idx]][1]) if parent[idx] >= 0 else ""」
file: `scripts/lumos:48914`（命中處在 48919、48924；候選的 `ident` 在 `_tg_ci_cands`，49240）

失敗場景：
- 2 萬字單行上限只管實體行，但 `_tg_ci_lines` 會把行尾 `\` 的續行併成一條邏輯行，上限管不到。
- 這條邏輯行如果是父層（縮排較淺），底下每個命中都要先對整條做 `_tg_norm`，再把整條複製進 `ident`。
- 5MB 上限下理論上到父層 2.4MB 乘 7 萬多個命中、約 170GB（推算，沒有實跑）。

重現：
- 檔案形狀是 `.github/workflows/ci.yml`，內容為 `"jobs: \\\n" + ("x"*19990 + " \\\n")*25 + "end\n"`，也就是一條約 500KB 的續行父層，底下 N 行 `  - run: ./gradlew test -x test`。
- `python3.14 scen.py cicont1000 200` 與 `python3.14 scen.py cicont4000 250 after`。

| 情境 | 修前 | 修後 |
|---|---|---|
| cicont1000 | 13.6 秒 / 801MB | 6.9 秒 / 802MB |
| cicont4000 | 未跑 | 23.4 秒 / 2262MB |

歸因：有證據的原有漏查。修前記憶體完全相同，這輪把往回掃改成堆疊，只改善了時間，沒碰到「逐命中正規化整條父層」。

### F4 `_tg_class_at` 每行都 join 整串類別路徑：巢狀類別深度的平方級記憶體
severity: major
blocking: 是 — 約 140KB 的檔案就吃近 1GB，3 萬層巢狀吃 3 到 4.4GB，再大有被系統殺掉的風險。
引句:「path_at[line] = ".".join(nm for _d, nm in stack)」
file: `scripts/lumos:48425` 與 `48438`

失敗場景：
- 每一行都新建一份完整的類別路徑字串，記憶體約是「行數 × 深度 × 名稱長度」。
- 一行一個 `class C{i} {` 的巢狀檔，行數等於深度，所以是深度的平方。

重現：`python3.14 scen.py nestc10000 100`（也可用 `nestc20000`、`nestclass`，每行形狀是 `class C{i} {`，最後補相同數量的 `}`）。

| 情境 | 修前 | 修後 |
|---|---|---|
| 1 萬層 | 4.1 秒 / 960MB | 4.3 秒 / 964MB |
| 2 萬層 | 13.6 秒 / 2917MB | 13.7 秒 / 2922MB |
| 3 萬層 | 30.5 秒 / 3024MB | 32.1 秒 / 4436MB |

- 10 萬層、名稱一個字元（`class A{`）時約 10GB（推算，沒有實跑）。
- S11 只列了「3000 層巢狀」，沒涵蓋這個形狀。

歸因：有證據的原有漏查，不在修補差異內，是上輪沒人看的角落。修法是讓堆疊每一層帶著已接好的路徑，`path_at` 只存參照。

### F5 讀內容的 git 逾時或截止時間用完，被當成「讀不出來」變成可放行的候選，而不是「沒跑完」
severity: minor
blocking: 否 — 推送還是被擋，只是出口與訊息不對。
引句:「if sizes is None or blobs is None or sizes[i] is None:」
file: `scripts/lumos:49096`（對應的 `res[slot] = "UNREADABLE"` 在 49097，屬於 r3-code.patch 全量內容，不在修補差異內）

失敗場景：
- `git cat-file --batch` 逾時，或截止時間在讀內容前已用完，`_nodehome_cat_blobs` 回 None。
- 這時每支改到的檔都變成 `tq/unreadable`，訊息寫「這支檔從 git 讀不出來（含檔名不是 UTF-8、含換行）」。
- 這條路徑沒有丟 `TimeoutError`，與 S13 寫的「超過截止時間應記成沒跑完」不一致。
- 人若照訊息放行，這些檔的比對根本沒跑過。

重現：`python3.14 gen/probe_timeout.py after`，用假的 `subprocess.run` 讓 `cat-file --batch` 丟 `TimeoutExpired`，得到 `error=None`，`cands=[('tq/unreadable', 'app/src/test/kotlin/com/x/T.kt', '這支檔從 git 讀不出來…')]`。

歸因：有證據的原有漏查。修前修後在這條路徑上沒有差異，我只跑了修後。

### F6 單次出口 `LUMOS_SKIP_LINT_NEW=1` 照樣把整支比對跑完
severity: minor
blocking: 否 — 計劃已把「off 的專案仍付比對成本」寫成代價，但沒涵蓋比對本身就是病態慢的情境。
引句:「return _lint_new_off(repo_root, start, tip, skip_env, out, deadline)」
file: `scripts/lumos:38961`（`_lint_new_off` 裡的 `g = _lint_new_guard(repo_root, start, tip, deadline)` 在 38995）

失敗場景：
- 比對跑太久被擋時，擋下訊息叫人設環境變數再推。
- 但設了之後，同一個病態輸入又完整分析一次，而截止時間只在換檔時看一次，單檔跑到一半不會被打斷。
- 所以逃生門救不了「比對自己卡住」。

重現：`python3.14 gen/probe_skip.py`。對 `nestc20000` 設環境變數後，狀態是 `off`、沒擋，但花了 12.9 秒、峰值 2.78GB。

歸因：原有設計，這輪沒有新增這項成本。

## 圖譜鏡頭

LUMOS-IMPACT 沒附上，我自己在 repo 目錄用 `lumos impact --diff 047031883..22cc667` 和 `lumos show Systems/test-guard` 讀過。

- `Systems/test-guard` 的摘要行 `WHY:任一行超過 2 萬字的檔不解析…` 寫的 `[不選:繼續逐點補(第三輪仍會有漏網的那一處)]`，F1 到 F4 就是那個「漏網的那一處」。
- 計劃做法一第 135 行「判讀跟輸入大小成正比…區塊開頭用堆疊一趟算」，與 F1、F2、F3 的實測不符。這句屬於線索，不是有結構的決策紀錄。實作程式比筆記說的慢，所以按規則以程式為準，且該立 Issue。
- `[S11]` 的「5000 層巢狀 try、9 萬行建置檔改一行都 30 秒內」我獨立驗過仍成立；它沒涵蓋 F1 到 F4 的形狀。
- `WHY:比對花掉的時間不算進檢查命令的預算，最壞整道閘兩倍預算` 是已記載的取捨，我不另立 finding。

## 修補鏡頭：repair 與 preserve 分開報

**repair（確認修好的）：**

| 情境 | 修前 | 修後 |
|---|---|---|
| 3000 層巢狀 try | 16.8 秒 | 1.4 秒 |
| 6 萬層巢狀 try/catch（每行約 400 個） | 逾時，超過 200 秒 | 5.7 秒 |
| 9 萬行建置檔改一行（開頭很短） | 117.6 秒 | 2.6 秒 |

**preserve（維持住的）：**

| 情境 | 修前 | 修後 |
|---|---|---|
| 9.5 萬支單行測試，預期值全改 | 14.3 秒 | 14.6 秒 |
| 45 支函式各 2000 條斷言，預期值全改 | 8.8 秒 | 6.8 秒 |
| 約 114 萬對括號的單支函式 | 3.8 秒 / 531MB | 4.7 秒 / 539MB |
| 4 萬個 CI `continue-on-error`（`cikeys`） | 1.3 秒 | 1.5 秒 |

## 三問

**① 子程序與暫存目錄在逾時、Ctrl-C、例外時有沒有收乾淨？**
- 比對全程只用 `subprocess.run`（`_lens_git`、`_nodehome_cat_sizes`、`_nodehome_cat_blobs`），`TimeoutExpired` 和例外時都會殺掉子程序。
- `test-guard` 路徑不建暫存目錄，所以沒有洩漏。
- 這是我讀程式得出的結論，沒有實測 Ctrl-C。

**② 時間預算會不會在大輸入或慢機器上誤擋正常推送、超時後放行，或跑得比宣稱久？**
- 超過截止時間會丟 `TimeoutError`，被擋，不會放行。
- 但截止時間只在換檔、換函式時看，單檔內沒有中斷，所以 F1 到 F4 的病態單檔會遠超預算，而 F6 的出口也救不了。
- 超時發生在讀內容那一步時，會變成可放行的 `tq/unreadable`（F5）。
- 另有一個已記載的取捨：任一行超過 2 萬字的檔，連 main、build、ci 類的檔都整支列 `tq/too-large`，每次修改要人放行。

**③ 有沒有整份大檔、整個推送、整本治理帳或深層巢狀一次讀進記憶體，或做二次方以上的工作？**
- 有。F1 到 F4 就是。
- 補充量測：35 支測試檔各約 2.7MB（讀入總量 189MB，在 200MB 上限之內），預期值全改。
  - 結果是 201 秒、2.0GB，約 175 萬條候選。
  - 沒有候選數量上限，不構成 finding，只提供基準。
- 治理帳沒有被整本讀進來。

F1 到 F4 的上限內平方級仍在，其中 F1 是這輪修補自己引入的回歸；F5、F6 是不影響擋與放的次要問題。
