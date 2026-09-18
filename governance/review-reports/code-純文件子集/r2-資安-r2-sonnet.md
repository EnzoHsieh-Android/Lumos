severity: major

## F1 `affected_keys` 允許以 `-` 開頭的 key,傳進 `--keys` 時被 argparse 當成旗標吃掉,整趟 keys 檢查會誤判成「有紅」而擋下合法推送

severity: major
blocking: yes

觀察到什麼:`_affected_test_keys`(scripts/lumos:22347)只用 `_KEY_OK_RE = re.compile(r"[A-Za-z0-9_.-]{3,}")` 過濾,這個字元類允許 `-` 出現在任何位置(含開頭)。函式名來源(`def xxx`)不可能以 `-` 開頭,但**檔名來源**可以:

引句:「_KEY_OK_RE = re.compile(r"[A-Za-z0-9_.-]{3,}")」

引句:「只留 [A-Za-z0-9_.-] 且 ≥3 字的(逗號、空白這種會在 shell 的逗號串裡被切錯——r1 邊界席);算不出回空清單。」

這些 key 之後在 pre-push 被 `,`.join 成一個字串,整串交給執行器:

引句:「_keys_args=(--suite keys --keys "$_SUITE_KEYS")」

怎麼重現(輸入→錯誤輸出):在乾淨臨時 repo 裡新增一支程式檔 `scripts/-xx.py`,內容不含任何頂層 `def`(例如只有 `y = 2`)。實際跑 lumos 這支函式:

```
$ python3 -c "...exec scripts/lumos..."
_test_suite_for_range(...) => {'suite': 'full', 'code': ['scripts/-xx.py'], 'light_ok': True}
_affected_test_keys(...) => ['-xx']
```

`light_ok` 是 `True`(該檔是程式檔、非文件),`affected_keys` 只有一個字 `-xx`,`,`.join 後就是字串 `-xx`,整串以 `-` 開頭。這正是 pre-push 判成 light 時真的會塞進 `--keys` 的值。實際餵給執行器驗證:

```
$ python3 scripts/test_lumos.py --suite keys --keys "-xx" --list
usage: test_lumos.py [-h] [-k KEYWORD] [--list] ... [--keys 名字,名字] [關鍵字]
test_lumos.py: error: argument --keys: expected one argument
rc=2
```

argparse 看到 `--keys` 後面的下一個 token 以 `-` 開頭、且不是負數,判定它「像旗標」,不當成 `--keys` 的值,直接印 usage 並 `SystemExit(2)`。

為什麼是 bug 而不是風格:`_run_group`(scripts/hooks/pre-push)把子行程離開碼分三類——0 綠、3「選中 0 支」、其餘一律當紅(`_bad=1` → `return 1`)。rc=2 不是 0 也不是 3,會落進「有紅」那條路:

```
_krc=1(來自 argparse SystemExit(2))
→ 不是 3,進 elif [[ "$_krc" -ne 0 ]]; then _rc=1
→ 印「擋下:test_lumos.py 有紅,有測試沒過。」並列出 grep 到的 ✗ 行(這裡其實一支都沒有,因為根本沒跑到任何測試,只是 argparse 報錯)
```

也就是說:只要這次小改動裡「唯一/最先算出的關鍵字」是一個以 `-` 開頭、去掉副檔名後 ≥3 字的檔名(例如 `-xx.py`、`--legacy.py`,而且該檔這次的變動沒有動到任何頂層 `def`,不然函式名關鍵字會排在檔名前面把它擋住),light 這條路整個失效:不但沒有真的跑 keys 子集去驗證改動,還會用一則跟「測試沒過」無關的誤導訊息擋下開發者本來合法、乾淨的推送。攻擊路徑四件:
- 誰:任何能把一支這樣命名的程式檔合進歷史的人(自己的分支,或別人先前合併進來、後來被自己的小改動範圍帶到的檔)
- 從哪裡:該檔案存在於這次推送的 diff 範圍內(不需要是這次才新增,只要落在 push-check 判定的計劃落點內、且被小改動閘接受為 light)
- 送什麼:對該檔案做一次「不動任何頂層 def」的小修改(例如改一行內部邏輯、加註解、改變數)並推送
- 拿到什麼:pre-push 對這次推送印出「有測試沒過」並以 rc1 擋下,實際上一支真正的測試都沒跑到、也沒有紅

方向是 fail-closed(擋下而非放行),所以不是「繞過檢查偷跑高風險程式碼」那種典型漏洞,但它確實是「不可信輸入(檔名)流進 argparse 造成程式做出錯的行為」,且會讓 keys 子集這條路徑名不符實地失效(該跑的關鍵字檢查沒跑,卻印出跟事實不符的「有紅」訊息),不是風格問題。修法：`_KEY_OK_RE` 應該禁止以 `-` 開頭(例如 `r"[A-Za-z0-9_][A-Za-z0-9_.-]{2,}"`),或呼叫端在 `--keys` 前加 `--` 分隔符 / 用 `--keys=$_SUITE_KEYS` 的等號形式避免 argparse 誤判。

## 其餘類別(逐項看過)

- 2 登入與權限:本次 diff 不涉及任何登入/權限程式碼。已看,無。
- 3 密鑰與個資:`_PP_TMP="$(mktemp -d "${TMPDIR:-/tmp}/lumos-prepush-XXXXXX")"`(scripts/hooks/pre-push)用 `mktemp -d`,macOS/Linux 預設建目錄權限 0700(僅本人可讀),`_sg_out="$_PP_TMP/sg-$RANDOM.log"` 只是在這個私有目錄底下取檔名,`$RANDOM` 可預測沒差,因為目錄本身不可預測且權限已收斂。`tee "$_sg_out" >&2` 寫進去的內容跟同時印到 stderr 的內容一模一樣,沒有額外外流的資訊。`trap 'impact_done; rm -rf "$_PP_TMP"' EXIT INT TERM` 涵蓋正常結束/訊號兩條路,跟 r1 已經抓到的「逐檔 rm 在 exit 1 漏清」問題已經改成整個目錄砍掉,沒有新的遺留視窗(`kill -9` 殺不掉任何 trap,是 bash 通用限制,不是這次改動引入的新洞)。已看,無。
- 4 加密傳輸:本次 diff 沒有網路/傳輸程式碼。已看,無。
- 5 執行邊界:
  - 已驗證 `governance/*.json`、`docs/*.jsonl`(含 `docs/.canary-log.jsonl` 這種審查帳)會被 `_docs_only_file`(scripts/lumos)判成「純文件」,因此單獨改動這些檔的推送/CI 只跑 `--suite docs` 子集、不跑全套。但查過 `_ledger_has_manual_only`、`anchor-baseline.json` 檢查(scripts/hooks/pre-push:109-118,不在本次 diff 範圍內)、`doctor --ci`、`spec-gate --push-check` 這些治理閘,全部是在 suite 判定**之外、無條件執行**的獨立指令,不受 `--suite docs` 影響;而 `test_lumos.py` 全套本身原本也不是「驗證留痕內容真偽」的機制(它驗的是程式邏輯,不是治理帳的內容真實性)。所以把這類檔案歸類成「文件」並不會讓一個原本存在、現在消失的檢查消失——這條路沒有新增可利用的洞,只是把本來就不做內容真偽驗證的檔案排除在全套測試之外(方向上與既有設計一致)。
  - 已驗證 `.lumos/config.json` 的 `ignore` 清單:即使攻擊者把某支真程式檔加進 ignore,該檔仍然不在 `_DOCS_ONLY_PATHS` 白名單路徑內(例如 `scripts/`、`.github/` 都不在),所以 `_test_suite_for_range` 的 docs/full 判定完全不讀這份 ignore 清單,不會被此清單影響而誤判成 docs。ignore 只影響 `_is_code_file` → `light_ok`,而且方向是「被 ignore 的檔案不算程式檔」→ 會拉低 `light_ok`(讓非文件檔不再「全部是程式檔」),逼向 full/standard,不是逼向 light——是保守方向,不是可利用的繞法。已看,無。
  - CI 對 `github.event.before` 的信任:這次改動的寫法(`git cat-file -e "$BEFORE^{commit}"`、判不出來就退回 full)跟同檔既有步驟一致,而且方向本來就保守(算不出來就全套)。GitHub 在強制推送等情境下 `before` 語意的邊界案例我沒有把握完整驗證,寫不出具體攻擊路徑,標「推論」,不升等。
  - 沒有找到 `eval`/`shell=True` 之類把不可信內容送進解譯/shell 的新增用法;所有新增的 `subprocess.run` 呼叫都是 list 參數形式。已看,無。
