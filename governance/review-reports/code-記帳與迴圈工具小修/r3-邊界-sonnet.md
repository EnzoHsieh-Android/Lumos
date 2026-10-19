severity: major

這輪我只驗修補的 hunk,上一輪點名的輸入多半守住了,但有一個回歸:`_jsonl_append_verified` 的讀回自驗在備註含 U+2028/U+2029/U+0085 時會誤報沒記成功。實驗都在 `/tmp/lumos-seat-work/code-記帳與迴圈工具小修/邊界-sonnet/`。修後是 5248791e 匯出的 `after/`,修前是 69ee6d76 匯出的 `before/`,用 python3.14 實跑。

## 發現

### 1. 讀回自驗改用 `splitlines()`,備註含 U+2028 時已寫進帳卻報「落盤自驗失敗」
severity: major
blocking: 是
歸因:有證據的修復回歸

- **位置**:`_jsonl_append_verified` 新增的「只讀回新寫的那段」。
- **問題**:`json.dumps(ensure_ascii=False)` 不跳脫 U+2028、U+2029、U+0085。新寫法 `tail.splitlines()` 會把同一列從這些字元處劈開,兩半都不是合法 JSON,全被 `continue` 跳過,最後走到「找不到這一筆」並回傳 rc=2。
- **為什麼算已知坑**:repo 自己的 `_ledger_lines` docstring 已寫明「不用 splitlines(它還認 U+2028/U+2029/U+0085…一列會被劈開丟掉)」。修前的 `for line in f`(文字模式)不會在這三個字元斷行。
- **重現**:
  ```
  cd .../邊界-sonnet/p   # git init 的空 repo,附 docs/t-knowledge
  python3.14 after/scripts/lumos  canary record none --loop L1 --note $'a\u2028b'
  python3.14 before/scripts/lumos canary record none --loop L1 --note $'a\u2028b'
  ```
  - 修後:印「canary record: 落盤自驗失敗——系統說寫成功了,但讀回來找不到這一筆」,rc=2,但 `docs/.canary-log.jsonl` 已有 1 列(`wc -l` 為 1)。
  - 修前:印「✓ 這筆審查結果(none)記下來了」,rc=0。
- **後果**:呼叫端看到 rc=2 會重記。帳本只能追加,同一席會多一列。
- **同族**:`cmd_canary_second` 等其他走 `_jsonl_append_verified` 的寫入器是同一條路徑。

  引句:「        for line in tail.splitlines():」

- **測試缺口**:這輪新增的 11 個測試沒有一個含 U+2028(`r3-repair-tests.patch` 內 grep "2028" 為 0)。把 `splitlines()` 換回 `_ledger_lines` 之前,沒有測試會紅。
- **建議修法**:改用 `_ledger_lines(tail)`,並補一支備註含 U+2028 的測試。

### 2. `loop verify-progress` 沒走四個入口的結局帳過濾
severity: minor
blocking: 否
歸因:有證據的原有漏查(修前修後行為相同,不是這輪造成)

- **位置**:`_is_outcome_row` 的 docstring 說「讀審查列的入口一處濾掉」,但 `cmd_loop_verify_progress` 自己逐行讀帳,只濾 `kind != "spec-gate"`。
- **重現**:帳上只有一筆 `--outcome converged` 的列時,`lumos loop verify-progress L5` 輸出 `rounds=1 clean_streak=0 kinds=['none']`,結局帳被算成一輪審查。
- **影響**:`loop canary-stats` 與 `loop list` 也直接讀帳,未逐一驗是否也算進結局帳。

  引句:「                if d.get("loop") == loop_id and d.get("kind") != "spec-gate":   # 規格閘留痕不是審查輪(雙向門放行_計劃 S16):不計席、不判無效」

### 3. 擋下訊息裡的示意指令不是原樣的編號
severity: minor
blocking: 否
歸因:未判定(修前修後的清控制字元方式不同,我沒逐一比對兩版輸出)

- **輸入**:`--loop $'code-a b\x1b[31m中$(x)\'q'`(第一筆、沒帶 `--tier`)。
- **輸出**:`'code-a b [31m中$(x)'"'"'q'`,ESC 被換成空格。
- **影響**:照抄貼上會開出另一個迴圈。編號帶 ESC 或換行本身很病態,所以我只列 minor。
- **已守住的部分**:空白、中文、`$()`、單引號、`;` 都有 quote;200 字長編號沒有截斷。

  引句:「    return _esc_clean(s, len(s))」

## 已驗且守住的主張(附證據)

- **帳尾沒換行**:先寫 `{"loop":"L1","tok`(不帶換行),再 `canary record`,新列獨立成一行,rc=0。檔內容為 `'{"loop":"L1","tok\n{"ts"…"token": "T1"…}\n'`。
- **非 UTF-8 只在別的編號的列**:
  - 帶 `--orchestrator codex` 時,修前丟 traceback,修後改為「整本判不了」的擋下訊息(rc=2),是改善。
  - 不帶旗標時兩版訊息相同。
  - `loop next` 與 `loop status` 在這種帳上仍然丟 `UnicodeDecodeError` 堆疊,修前也一樣,不屬於這輪。
- **`none` 保留字**:實跑輸出的訊息都是「none 是保留字」。
  - `--findings-set` 為 `none`、`a,none`、`NONE ` 都被擋。
  - `--regression-set none,none` 被擋。
  - `--refuted-set None=abcdefg` 被擋。
  - 整串只寫 `--regression-set None`(搭配 `--findings-set n1`)能通過,只剩「還沒處置」的後續檢查。
  - 全形 `ｎｏｎｅ` 不會被 casefold 當成 none,屬非中英文範疇,不報。
- **`--findings-set none` 改為擋下**:repo 內(除審查卷證外)沒有任何文件或腳本用到,沒有破壞既有用法。
- **結局帳**:帳上有 `--outcome` 的列,再用 `--tier light` 記一筆審查列成功(rc=0),`loop next` 正常列出第 2 輪。
- **空帳、純結局帳、`--round` 純空白**:`rec` 端對 `--round` 純空白有「當沒帶」的程式碼(`round_id = None`),我讀過但沒另外實跑。

## 未驗範圍

- 沒跑 `scripts/test_lumos.py` 的測試,也沒做拿掉實作看測試會不會紅的變異檢查。
- 沒驗 `loop replay` 的凍結雜湊在帳上有結局帳時,凍結與回放兩側是否一致。
- `_cap_retro_record_block` 的 rows 傳入路徑只讀了程式碼,沒實跑人裁紀錄的情境。

## 三問回答

1. **原問題的修復效果**:帳尾補換行、`--orchestrator` 帳壞訊息、`none` 保留字、示意指令 quote 這四項有行為證據,實跑修前修後各一次(`--orchestrator` 帳壞修前是 traceback,修後是擋下訊息)。結局帳過濾我只驗了 `canary record` 加 `loop next` 這一條,另外三個入口未實跑。
2. **相鄰呼叫路徑**:`_jsonl_append_verified` 這條在備註含 U+2028/U+2029/U+0085 時不成立(發現 1)。其餘 `canary record` 的寫入、擋下、結局帳路徑我跑過的都成立。
3. **新發現在修前修後的結果**:
   - 發現 1:修前 rc=0,修後 rc=2,是修復造成。
   - 發現 2:修前修後同為 `rounds=1`,不是修復造成。
   - 發現 3:未判定。

最嚴重 severity:major,blocking 共 1 條。
