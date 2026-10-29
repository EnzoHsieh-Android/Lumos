severity: minor

審查範圍:正式程式的 diff 與修補差異。測試檔只看了 manifest 點名的那一行。我沒跑真機。SQL 用 Python sqlite3 仿 perfetto 的表驗證。收集腳本從 heredoc 抽出來,用假時鐘與替身函式驅動。實驗檔都在 `/tmp/lumos-seat-work/code-原生配置排行/正確性-sonnet/`,留給編排者收貨後刪。

## Findings

### 1. 修補新增的測試多了一個沒用到的解包變數,本機閘的 ruff 會紅
severity: minor
blocking: 否。這只讓推送前閘紅,不改任何執行行為,改一個底線就好。
引句:「Unpacked variable `d` is never used」(manifest 第 1 條的 ruff 訊息;測試檔不在 prod patch 內)
file: `scripts/test_lumos.py:18990`(`r, d, fake, _ = _ms_native_collect(td, env={"LUMOS_STABILITY_STEP_BUDGET_S": v})`)
歸因:有證據的修復回歸。
- 修後 07642d8e:`ruff check --select RUF059 --target-version py39 --output-format concise scripts/test_lumos.py` 在 18990:16 報 RUF059。
- `git blame` 顯示這行是 23c0d065 新增的。修前 84b487f2 沒有 `t_android_native_budget_values`,所以沒有這行。
失敗場景:`t_android_native_budget_values` 新增的 `for v in ("nan", "inf", "0", "-5", "一小時")` 迴圈每圈都解包 `d` 卻不用。專案的 ruff 設定含 RUF,推送前掛鉤和 `prepush-lint.py` 會擋,必須先改成 `_d`。

### 2. 第二段的查詢上限排在停錄與拉檔之後,驅動跑近截止時間時查詢只剩 1 秒
severity: minor
blocking: 否。結果是這段誠實寫成 failed,不影響第一段判定,但原因寫「查詢逾時」會誤導。
引句:「return T_LONG if deadline is None else max(1.0, min(T_LONG, deadline - time.time()))」
file: `scripts/templates/android-stability-collect.sh`(`native_run` 內的 `left()`,最後一次呼叫是 `native_query(trace, pkg, left())`)
歸因:有證據的修復回歸。修前 84b487f2 沒有 `left()` 和 deadline。修後的查詢上限和驅動上限共用同一個 deadline,但查詢排在停錄(約 30 秒)與拉檔(最多 120 秒)之後。
重現:用假時鐘跑 `native_run`,步驟上限 3600、開始時間 1000,所以 deadline=4420。
- 暖機 10 秒,量測驅動在 deadline 前 20 秒結束(1790 秒),停錄 70 秒。
- 實際呼叫序列:`[('drv', 2, 1800.0), ('drv', 5, 1800.0), ('query', 1.0)]`。查詢上限是 1.0 秒,此時離 3600 的整步上限還剩約 130 秒。
- 對照:驅動只花 1900 秒、提早結束時,查詢拿到 140 秒。
- 修前 84b487f2 這個輸入的查詢上限是 T_LONG,不受 deadline 影響。但修前驅動可以一直跑到整步被 e2e 砍掉,第一段判定也一起丟。所以修補整體更好,只是這個尾端沒處理好。
失敗場景:trace_processor 光載入一份 heapprofd 錄檔就超過 1 秒,所以必定寫 failed「查詢逾時」,一份完整的錄檔白白浪費。規格 `原生記憶體增長提示_計劃.md` 第 151 行與 S23 寫的就是這個語意,所以實作和規格一致。缺陷在規格:「扣 180 秒留給停錄、拉檔」實際保護的是驅動,保護不到排在它們後面的查詢。

### 3. 「跑不跑第二段」用整步上限預估,deadline 卻扣了 180 秒,中間有一段預估會超過 deadline 的窗口
severity: minor
blocking: 否。第二段會被自己的 deadline 砍成 failed,第一段判定不受影響。
引句:「if budget and elapsed + (2 * elapsed + 120) > float(budget):」
file: `scripts/templates/android-stability-collect.sh`(`native_skip`,對照 `main` 的 `deadline = None if b is None else t_start + b - NATIVE_MARGIN`)
歸因:有證據的修復回歸。deadline 是修補新加的;預估式 84b487f2 就有,但當時沒有 deadline 可以打架。
重現:呼叫修後的 `native_skip`,步驟上限 3600、deadline 偏移 3420。
- 第一段 1150 秒:回 `None`(要跑),預估結束在 3570,比 deadline 晚 150 秒。
- 第一段 1180 秒:才回 failed「時間不夠」。
- 所以第一段在約 1101 到 1160 秒之間,會放行一個預估本身就越過 deadline 的第二段。預估的「兩倍」很保守,實際未必會被砍,但規則自己的數字互相矛盾。
失敗場景:預估放行後,暖機和量測驅動被 `left()` 截短。結果是 failed,原因寫「驅動失敗:逾時」,而不是「時間不夠」,使用者看不出是時間預算的問題。

## Manifest 16 條判定

- 第 1 條(ruff RUF059,`test_lumos.py:18990`):真隱患,見 finding 1。
- 第 2、3 條(`collect.sh:261`、`:314` 的 `open(`):誤報。
  - 兩處都是 `open(...).read()` 鏈式呼叫,CPython 用完立刻釋放。
  - 同形狀在 84b487f2 的 259、312 行就存在。
  - 這兩支範本在打開時由 `preflight` 的 `gone` 檢查先確認存在。
- 第 4 條(`collect.sh:487` 的 `time.sleep`):誤報。這是 `fresh_launch` 裡一次固定的 `time.sleep(SETTLE)`,不在迴圈裡,不累積延遲。
- 第 5 到 16 條(`android-stability-native.sql` 的 N+1,行 18、21、23、52、61、75、78、81、84、88、90、92):誤報。這些都是單一查詢裡的 CTE 與子句,沒有應用層迴圈。我另外在 sqlite 模擬環境跑 2 萬個葉子乘上 32 層深的輸入,約 7.6 秒完成,可以接受。

## 圖譜鏡頭

hook 說這次沒附固定席節點,所以我只能用規格當依據,逐條對照。
- S23(預算、deadline、值檢查、e2e 傳參數):實作與規格逐字一致。規格自身的缺口見 finding 2、3。
- S10(形狀不對整段不採用、超大整數、長名字):`_macrobench_native_print` 的整數運算和三段各自截字都成立。JSON 本身限制超過 4300 位的整數,走不到 `int→str` 的溢位。
- 新增兩支範本已登進 `_VENDORED_TREE_FILES`,preflight 的 `NATIVE_TEMPLATES` 也同步檢查。repo 內沒有第三份範本清單。
- `device_dirty` 已在整個 repo 移除,沒有殘留引用。

## 角色卡
- be-api-compat:`stability.json` 與 `macrobench --json` 只新增 `native_retained` 一個鍵。
  - 新 lumos 讀舊檔:缺段時回 `_macrobench_native_off`。
  - 舊 lumos 讀新檔:多出的鍵會被忽略。
  - e2e 的判定改讀 `--json` 的檔案,深度 4、5 層遠小於上限 20,也沒有大小截斷。判定不會被 200 個 sites 弄壞。
  - 沒有欄位被改名或刪除。
- be-authz:本次沒有新增或改動任何端點或資料存取,不適用。

## 配對案例的獨立核對

**repair 側**
- G2 ERROR 偽框架:SQL 模擬同一輸入,修前 `caller='ERROR 4'`,修後 `'?'`。並列時修前 `ERROR 4`,修後選有名字的 `zed`。
- G6 意外例外:假裝置丟 `RuntimeError`。修後 `state` 被清空,`abort_record` 送出 `kill -TERM 42` 與 `rm -f c t`,結果寫 failed「第二段出了意外(RuntimeError:boom)」。丟 `Terminated` 時,`state["rec"]` 留著交給 `main` 的 cleanup。
- G3 deadline:驅動的上限確實被 `left()` 截短,但查詢尾端有 finding 2。
- G1、G4、G5、G7、G9:只讀了程式,沒另跑。因果判為未判定。

**preserve 側**
- G2 SQL:跳過 libart 的呼叫者、取加總最大、名字升冪決勝、1 MiB 卡線(M-1 排除、M 收進)、整條都是配置器記 `?`、含引號與逗號與換行的名稱,結果都對。
- G8:`fresh_launch` 的順序是 force-stop、讀結束紀錄、monkey、sleep、pidof,與抽出前的 `measure` 逐行相同。第一段行為沒變。
- G6 的 SIGTERM 路徑沒有重跑,按讀程式的結果判為成立。

## 三問
1. **原問題的修復效果**:ERROR 偽框架、並列排序、意外例外收錄製、`fresh_launch` 抽出,都有上述行為證據,修後對、修前錯或不同。預算只修了一半,因為尾端有 finding 2、3。
2. **修補處的正常、錯誤、相鄰路徑**:
   - 正常:`left()` 在 deadline 為 None 時回 T_LONG,與修前相同。
   - 錯誤:`native_phase` 的例外分支會收錄製,收不掉時照實寫進原因。
   - 相鄰:`tp_rows` 抽出後,`heap_counts`、`cycle_numbers` 的切法沒變。
   - 未成立的部分只有 finding 2、3。
3. **新發現同一案例的前後結果**:
   - finding 1:修前 84b487f2 沒有這行,修後 ruff 紅。
   - finding 2:修前沒有 deadline,查詢上限是 T_LONG(但整步可能被砍)。修後同一輸入的查詢上限是 1 秒。
   - finding 3:修前沒有 deadline,預估放行就照跑。修後預估放行但可能被 deadline 截斷。

**未驗範圍**:真機上的 heapprofd 行為、真的 trace_processor 對這份 SQL 的效能和欄位格式、整套 `test_lumos.py` 的執行。

最嚴重 severity 為 minor,blocking 0 條。
