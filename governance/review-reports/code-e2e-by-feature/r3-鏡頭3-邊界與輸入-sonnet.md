severity: minor

鎖檔 `/Users/enzo/.cache/lumos/dispatch-lens/93aaa64b…673f0.json.warming` 不存在(cat 回「No such file」),所以沒有鎖可檢查或刪除。

## F1 run-id 可以取成 history.jsonl,把本機總表的位置佔成目錄
severity: minor
blocking: 否
file: `scripts/templates/android-e2e-run.sh:` preflight 的 run-id 檢查只擋 `[A-Za-z0-9._-]+` 與純點。總表路徑是 `scripts/lumos` 的 `E2E_HISTORY_REL`,跟 run 目錄在同一層(`.lumos/artifacts/android/`)。
失敗場景:`sh android-e2e-run.sh --feature login history.jsonl` 會在 `.lumos/artifacts/android/` 底下建出名為 `history.jsonl` 的**目錄**。之後每一次跑(我接著跑了 run-id `r2`)都沒有產生 `history.jsonl` 檔,總表寫不進去。`lumos android-e2e history` 因 `p.is_file()` 為假,只會印「還沒有檢測紀錄」。反過來,總表檔已存在時用這個 run-id,`os.makedirs` 會失敗。
另有一個同類的小碰撞:記憶體情境收在 `<run-id>.<情境>`,run-id `a` 加情境 `b` 會佔用 `a.b`。之後用 run-id `a.b` 開跑,建置與安裝都跑完才會在收集腳本被擋(「已經有結果檔了」)。這個是 fail-closed,沒有資料損壞。
引句:「    if not re.fullmatch(r"[A-Za-z0-9._-]+", run_id) or set(run_id) <= {"."}:」
歸因:有證據的原有漏查,不是修復造成。修前 787dd51b 與修後 4b056532 跑同一指令,結果相同(都產生 `history.jsonl/` 目錄)。我用假的 adb 與 maestro 重現。
建議:run-id 檢查加上不准等於 `history.jsonl`,或把總表搬出 run 目錄那一層。

## manifest 判定
內建的 `open(` handle 題是誤報。diff 裡新增行沒有任何 `open(`。命中的三處(`gradle_modules` 的 `open(...).read()`、`Steps.save` 的 `with open`、收集腳本讀設定的 `json.load(open(...))`)都是既有 context 行,而且是短命的一次性腳本。

## 圖譜鏡頭
- 派工訊息的 LUMOS-LENS 寫「這次沒附固定席節點」,所以沒有固定席筆記可逐條判。
- 我自己跑了 `lumos impact --diff`,只讀跟本次最相關的:
  - `Projects/Android端到端驗收_計劃.md` 的 S22 到 S28 逐條對照:
    - S23:打錯的 `-` 開頭旗標回 2、`--no-perf` 沒配挑法回 2、讀 git 失敗回 2,都成立。
    - S26:方法名的 regex 比條文更嚴(白名單,條文只列「開頭 #、空白、$」),不矛盾。
    - S26:`stability_scenarios` 的 `warmup`、`cycles` 上限與 `stability` 段一致(1 到 10000)。
    - 我沒發現筆記與程式對不上的地方。
  - `Systems/android-stability-collector.md` 的條款我只做了 grep,沒有逐條核對。
  - 其餘約 40 個節點只因 `scripts/lumos` 被改而連到,沒有逐條檢查。

## 三問的答案
1. **原問題的修復效果(方法名的 `$` 與路徑 `.`)已修好。** 同一份設定、兩個版本各跑 `lumos macrobench --check-config`:
   - 方法名 `$HOME`、`a$HOME`、`x.$Y#z`:修前 rc=0(放行),修後 rc=2(擋下)。
   - 功能 paths 寫 `.`:修前 rc=0,修後 rc=2。
   - 載入的版本是各自 clone 的 `scripts/lumos`,分別 checkout 到 787dd51b 與 4b056532。
2. **相鄰路徑仍成立,修前修後結果相同。**
   - 方法名:`Cls#m1` 通過。`$(id)`、`a;b`、`-x`、含換行(含尾端換行)都被擋,regex 用 `fullmatch`,沒有 `$` 尾端換行的漏洞。
   - 功能名與情境名:帶點、中文、尾端換行都被擋。
   - 情境設定:`cycles` 為 0、字串、true 都被擋。
   - 路徑:`app/`、`./app` 通過,`app/src/../x` 被擋。
   - 對照表:`features: {}`、`cases: {}`、情境清單為空、`visual` 不在 `e2e.visual` 都被擋。
   - `lumos android-e2e select` 的參數:
     - `--case login`(沒有點)、`--case a.b.c` 回 2 並列出可用情境。
     - 重複的 `--case` 與 `--feature a --case` 去重。
     - `--feature ''` 與 `--feature=` 回 2。
     - `--feature login,` 的結尾逗號被忽略。
   - 範本腳本(用假的 adb):
     - `--no-perf` 沒配挑法回 2,`--chnaged` 回 2。
     - `--feature --changed` 被當成值,由 argparse 擋下回 2。
     - run-id 放在參數前後都認得。
   - `--changed`(臨時 repo):
     - 工作目錄乾淨,或只改 `.maestro/baseline/`、門檻檔,回 2 並列出改到的檔。
     - 中文加空白的檔名、刪除、改名(新舊路徑都算)都正確挑到功能。
     - 對照表外的檔只放在 `unmatched` 提醒。
     - detached HEAD 正常。
     - 沒有主線時有「找不到主線分岔點」的說明。
3. **新發現 F1 的修前修後**:兩版相同,所以不是修復造成。

## 未驗範圍
- 真機的 adb 與 Maestro、`#` 在真實 Gradle 指令裡的行為,都沒有實測。
- 記憶體情境的實際收集(沒有 `trace_processor`)沒跑。
- 淺 clone 與「專案根不是 git 根」的情境只做了簡單試跑,沒有結論。
- 兩個 `{{TEST}}` 的設定通過檢查,執行時是 `replace` 全換,我沒有跑到那一步。

整體只有一條與 run-id 命名空間相關的小問題,修復本身(`$` 與 `.` 的擋法)在修前修後對照下成立。

臨時目錄 `/tmp/lumos-seat-work/code-e2e-by-feature/鏡頭3-邊界與輸入-sonnet` 已用字面絕對路徑刪除,刪之前 lsof 無程序佔用。
