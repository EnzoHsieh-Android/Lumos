severity: major

## 第一輪修法驗收

F1:修到 — `_VENDORED_TREE_FILES`/`_VENDORED_ALL`+`_is_vendored_path` 改成整條路徑精確比對(非目錄前綴),實測消費專案自己放的 `scripts/hooks/my_own_deploy.py`、`scripts/templates/render.py` 仍被掃到、tier 仍判 high。
F2:修到 — `_pitfall_diff_collect` 在「對齊」判斷之前先用 `_is_vendored_path` 濾掉 lint_claims(scripts/lumos:17744),對齊/未對齊兩條路都套到。
F3:修到 — 全庫三個 `_stack_changed_ok(` 呼叫點(含刪除行那條)都已改傳 `_skip_vendored`,grep 無漏傳。
F4:修到 — `_set_about_code` 與 `cmd_set` 的 about_code 特例整段拿掉;實測 `set S about_code x` 現在 rc2 擋下,不會再把既有多筆清單壓成一筆。
F5:修到 — 實測 `/etc/hosts`(絕對路徑)、`../outside/o.ts`(逃逸)、`src`(目錄)三種輸入皆 rc2 擋下、檔案不動。
F6:修到 — 規則收斂成 append/remove 共用 `_list_key_scalar_to_list`,不再有 set 當純量的第二套規則。
F7:修到 — 實測含「: 」的路徑 `src/a: b.ts` 經 append 寫出時被 `fmt_list_item` 正確加引號,讀回一字不差。
F8:修到 — 新事故筆記與相關節點裡 about_code 的敘述已寫明「不建立波及連結,只做排序」,查無殘留誤導文字。
F9:修到 — `_vendor_toolchain`/`_deinit_remove_vendored`/`_stack_ext_counts` 全改讀同一個 `_VENDORED_TREE_DIRS`,不再各記一份。
F10:修到 — 專用函式 `_set_about_code` 已整支刪除,命名/訊息不一致的載體不存在了。
F11:修到 — `rd = _os.path.relpath(dirpath, _base)` 移到檔名迴圈外,每個目錄只算一次。
F12:修到 — `_is_toolchain_repo` 判別鍵沿用既有慣例、方向仍是「找到鍵才不跳過」(fail-closed 掃更多);測試④原地保留繼續斷言這個方向。

## Findings

### F13 同一行清單守衛比對未去引號的原始字串,兩種同行清單寫法繞過擋下、靜默寫壞
severity: major
blocking: 是 — 牴觸新增測試⑨自己宣稱的「同一行清單一律擋下、檔案不動」,兩種常見變體(加引號、雙空白)實測都繞過、把使用者資料寫壞。
引句:「if (val.startswith(("[", "{")) and not val.startswith("[[")) or "]], [[" in val or "]],[[" in val:」
1. 守衛只看未去引號的 `val` 開頭字元是 `[`/`{`;`about_code: "[a.ts, b.ts]"`(整串被引號包住)不符合這個字面判斷,直接被當成單一值送進轉換。
2. `related: [[Systems/A]],  [[Systems/B]]`(兩個空白,非一個)同樣繞過,因為第二、三個子句只認 `"]], [["`(單空白)與 `"]],[["`(零空白)兩種寫法。
3. 兩種輸入都被 `fmt_list_item` 包成一整條字串寫成單一個清單項,而不是像不加引號版本那樣 rc2 擋下、檔案不動——本應保留的兩筆內容被吃成一筆壞資料。
最小重現(已跑,非臆測):
- vault 裡 `Systems/S.md` 含 `about_code: "[a.ts, b.ts]"`,對 repo 有 `src/new.ts` 執行 `lumos append S about_code src/new.ts`。預期(比照不加引號的同行清單)應 rc2、檔案不動;實測 rc0,寫出 `about_code:\n  - "[a.ts, b.ts]"\n  - src/new.ts`。
- vault 裡 `Systems/R.md` 含 `related: [[Systems/A]],  [[Systems/B]]`,執行 `lumos append R related "[[Systems/C]]"`。預期應 rc2、檔案不動;實測 rc0,寫出 `related:\n  - "[[Systems/A]],  [[Systems/B]]"\n  - "[[Systems/C]]"`。

### F14 about_code 路徑正規化在大小寫不敏感檔案系統上不去重,跟函式自己的宣稱矛盾
severity: minor
blocking: 否 — about_code 只影響排序加分(不建波及連結),重複項是資料整潔問題,不會造成資料遺失或安全繞過。
引句:「存成正規化的樣子,排序加分用的鍵才對得上(src/../src/a.py 跟 src/a.py 要是同一個)」
1. `_about_code_path` 只用 `Path.resolve()` 處理 `../`/`./`,不做大小寫正規化;macOS/Windows 預設檔案系統大小寫不敏感,`is_file()` 對 `SRC/A.TS` 跟 `src/a.ts` 一樣回 True 而各自照原樣存回。
2. 兩個大小寫不同的字串因此都通過檢查、都被接受進同一個清單,產生指向同一支檔案的兩筆不同拼法——跟這句引句宣稱的正規化目標(讓同一個目標收斂成同一個鍵)矛盾。
最小重現(已跑):repo 有 `src/a.ts`;依序 `append S about_code src/a.ts`(rc0)、`append S about_code SRC/A.TS`(rc0),結果 `about_code:\n  - src/a.ts\n  - SRC/A.TS`,兩筆但是同一支檔案。

## 風險掃描清單驗收
manifest 那 1 條(scripts/lumos:17603 命中 `open(`):誤報——命中的是 `_stack_changed_ok` docstring 裡描述 2026-08-11 舊事故的散文「命中 open(...)」,不是真的 `open()` 呼叫,該函式本體不含任何檔案開啟。

總結:最高 severity major,blocking 共 1 條
