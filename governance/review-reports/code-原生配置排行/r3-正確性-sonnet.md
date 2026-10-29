severity: minor

**審查範圍**:`223de76d` 全部正式程式,加修補鏡頭 `07642d8e` 到 `eeae9e15`。重現實驗是把收集腳本的 Python 段載進命名空間、用模擬時鐘和假的 `shell` 跑。這份回答所有結果都出自那些實驗。臨時目錄已用字面路徑刪除。

## 1. 「預估放行時驅動至少還有第一段兩倍的秒數」在剛好放行時差 `fresh_launch` 那幾秒
severity: minor
blocking: 否:只是文件條款的措辭精度,行為上驅動仍有約兩倍秒數,不會被注定砍掉。
引句:「預估放行時驅動至少還有第一段兩倍的秒數」
file: `docs/lumos-toolchain-knowledge/Projects/原生記憶體增長提示_計劃.md:151`、`scripts/templates/android-stability-collect.sh:597`(`native_run` 在 `fresh_launch` 之後才呼叫 `driver(..., left(NATIVE_TAIL))`)
歸因:有證據的修復回歸不成立。修前矛盾更大,修補把缺口從約 62 秒縮到約 2 秒,殘留是原有設計的邊角。
具體失敗場景:第一段 100 秒、剩下剛好 320 秒(2×100+120),`native_skip` 回 None 放行。`native_run` 先花 `SETTLE`(預設 2 秒)再加幾次 adb 呼叫,才算第一次驅動的上限。
- 修後(`223de76d`,`SETTLE=2`、adb 呼叫不耗時):兩次驅動上限都是 197.99 秒,小於 200。
- 修前(`07642d8e`,同一輸入,上限時刻 = 開跑時刻 + 預算 - `NATIVE_MARGIN`):兩次驅動上限是 137.99 秒,放行了注定偏短的第二段。
- 真機上 `force-stop`、讀結束紀錄、`monkey` 都要時間,短得更多。
- 測試 `t_android_native_budget_rule` 用 `SETTLE=0` 且 `shell` 假成不耗時,斷言寬鬆成 `t >= 2*e-1`,所以抓不到。

## 2. 裝置在第二段後段無回應時,第二段會把整步推過上限,第一段的結果檔跟著丟
severity: minor
blocking: 否:觸發需要裝置在第二段後段掉線,而且是原有設計邊界,不是這次修補造成。
引句:「這樣第二段不會把整步推過 e2e 的上限、連累第一段的判定。」
file: `scripts/templates/android-stability-collect.sh:345`(`stop_record` 裡每個 `perfetto_alive` 最多三次、每次 `T_SHORT`=120 秒)、`scripts/templates/android-stability-collect.sh:663`(結果檔在 `main` 最後才寫)
歸因:有證據的原有漏查,修前修後都一樣。
具體失敗場景:預算 3600 秒,第二段驅動在上限扣 120 秒處結束,此刻 adb 對每個 `shell` 都逾時 120 秒。
- 用模擬時鐘重現:修後超過上限 1446 秒,修前 1566 秒。
- 超過上限後 e2e 單步被砍,`stability.json` 沒寫,第一段已量好的判定一起丟失。
- 「扣 120 秒」只在 adb 回應正常時成立,條款寫成無條件。
- 這是個性取捨:r4 已明文撤掉「先寫結果檔」,改走預算檢查。要保證不連累,得在第二段開始前先落盤第一段,或停錄之後的 adb 呼叫也吃剩餘時間。

## manifest 15 條判定
- `open(` 兩條(第 263、316 行):誤報。皆為 `open(...).read()`,CPython 引用計數立即關閉;同函式的 `open(local, "w").write(cfg)` 也是同一模式。
- `time.sleep(SETTLE)`(第 489 行):誤報。只在 `fresh_launch` 睡一次,不在迴圈裡累積。
- SQL「N+1」12 條:全部誤報。整支是一條 `with recursive` 語句,不在迴圈裡被呼叫。

## 三問與已驗主張

**① 原問題的修復效果有何行為證據?**
- **時間算法**:見 #1,修前驅動上限 138,修後 198(目標 200)。預估 `native_skip` 與驅動截止 `left(NATIVE_TAIL)` 現在用同一個保留量,`main` 的 `end` 只讀一次。查詢扣 `NATIVE_FINISH`,且不超過 `T_LONG`,是我讀碼確認的,也由 `t_android_native_budget_rule` 覆蓋。
- **錄製順序**:`native_phase` 意外例外分支現在是 `state.get("rec")`、`abort_record`、再 `state.pop`。收的那幾秒被 `Terminated` 打斷時,錄製還在 `state`,`cleanup` 找得到。我讀碼確認此路徑正確。測試 `t_android_native_phase_exception` 的最後一段也覆蓋。
- **查詢範本 `having sum(size) != 0`**:我在真 SQLite 用隨機合成表比對有無這一行,400 組(共 1220 個 site 列),結果完全一致。
  - 零淨留量的葉子不影響任何加總。
  - 零淨留量的呼叫者也不可能在 `pick` 裡勝出。
  - 因為門檻 ≥ 1 MiB,最大者必為正數。
- **`--json` 清理**:實測控制字元、方向覆寫、孤立代理字元都被換成空格。長度不會再被截斷,因為 SQL 已先 `substr(...,1,500)`。
- **跑測試**:`python3.14 scripts/test_lumos.py -k android_native`,修後 `223de76d` 208 passed、0 failed。

**② 修補處的正常、錯誤與相鄰路徑是否仍成立?**
- `native_query` 拿掉逾時特判後,`tp_rows` 回 `rc=None` 且 `err="逾時(N 秒)"`,落入 `rc != 0` 分支。原因文字變成「trace_processor 算不了原生配置記帳:逾時(N 秒)」,逾時優先於 stat、rows 的檢查順序不變。
- `preflight` 的參數改名沒有任何關鍵字呼叫者。
- `left` 的 `max(1.0, …)` 下限在已過截止時會給驅動 1 秒,屬於可接受。
- `native_skip` 的 `remaining` 可為負數,訊息會印「只剩 -30 秒」,只是外觀。
- `--json` 的 `sites` 未知額外鍵不會被清理,但 `json.dumps` 會跳脫,不構成問題。
- 新增的「清理後原因為空白」情況,文字輸出會印出空白原因而不是「沒寫原因」,只是外觀。

**③ 新發現的同一案例在修前、修後各是什麼結果?** #1 與 #2 都各附修前、修後數字,見各條。#2 是修前修後一樣。

**固定席與角色卡**
- 固定席節點(`lumos-cli-read`、`guard-kill`、`design-loop`、`lumos-cli-lifecycle`、`bound-tests-gate` 等):這份 diff 只動 macrobench 與收集腳本,沒有碰到它們宣稱的 search 濾網、guard kill rc、re-inject、處置閘、綁定測試閘。不破壞。
- `loop-convergence-recording` 與 `pitfalls-code-loop` 兩個 RISK 節點:diff 不碰它們的函式,未見影響。
- 「這次新增的殘留」段:沒附。
- `be-api-compat`:`stability.json` 新增 `native_retained` 段,舊版 lumos 會直接忽略它。新版 lumos 讀舊檔時回 `enabled:false`、`reason:"結果檔沒有 native_retained 段"`,不印任何東西。macrobench `--json` 新增固定鍵,屬純新增,e2e judge 取鍵讀值,未見嚴格比對鍵集合的程式碼。
- `be-authz`:無新增端點,不適用。

**未驗範圍**:真機 heapprofd 的 stats 在 DISCARD 緩衝下是否常有非零 error 或 data_loss,會讓整段 failed(規格明定取捨,沒有真機可驗);沒有真實 trace_processor 跑過大錄檔的效能。

最嚴重 severity: minor;blocking 條數:0
