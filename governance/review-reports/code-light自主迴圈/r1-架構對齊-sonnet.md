severity: major

## F1 掛鉤新增的「改到的東西有沒有被 test_autonomous_loop.py 測到」判斷,繞過專案既有的整字比對入口、自己用未跳脫的 grep -qw 重刻一份,語意跟既有實作不一致且可重現

（回答審材給的第②③問:探 runner 旗標的既有慣例 vs 新的關鍵字比對、以及「light 時該跑哪些測試」現在三處各自決定、整字比對語意不一致)

專案裡已經有一個專門處理「改到的識別字(affected_keys)有沒有整字出現在某支測試原始碼裡」的正式入口:`scripts/test_lumos.py:58-79` 的 `_keys_suite_select`,它用 `re.escape(k)` 把關鍵字裡的正規表示式特殊字元先跳脫掉再包邊界 `(?<![A-Za-z0-9_])…(?![A-Za-z0-9_])`,理由寫在同檔 docstring:「挑出原始碼裡整字提到任何一個關鍵字…的測試」。這支掛鉤(`scripts/hooks/pre-push:431`,舊碼,這次沒動)已經在用這個入口——`_keys_args=(--suite keys --keys "$_SUITE_KEYS")`,把同一批 `_SUITE_KEYS` 丟給執行器去做整字比對。

但這次 diff 為了決定 `test_autonomous_loop.py` 要不要整支跑,沒有沿用這個入口(例如再呼叫一次執行器、或把 `_keys_suite_select` 的比對邏輯抽成共用),而是在 hook 裡自己另開一段,用 bash 的 `grep -qw` 直接讀原始碼比對,且沒有跳脫關鍵字裡的正規表示式特殊字元:

引句:「      [[ -n "$_k" ]] && grep -qw -- "$_k" "$REPO_ROOT/scripts/test_autonomous_loop.py" 2>/dev/null && { echo "$_k"; break; }」

作者自己在註解裡講的設計意圖是「整字」比對:

引句:「light 也一樣(2026-09-18 實測 light 推送前 108 秒、其中 67 秒是這支):除非改到的檔名或函式名(affected_keys)」

問題是 `grep -qw` 不是逐字面(literal)比對——它仍然把整個 pattern 當 basic regex 解讀,只是外面包一層 word-boundary;`.` 在裡面照樣是「比對任意一個字元」的萬用字元,不是字面的句點。凡是 `_SUITE_KEYS` 裡帶了句點的關鍵字,就會出現「執行器判不算整字、hook 判算」的分歧。我用臨時檔實測重現:

```
$ printf 'this line mentions mainXpy nothing else\n' > t3.txt
$ grep -qw -- "main.py" t3.txt && echo "grep MATCHED (false positive)"
grep MATCHED (false positive)
$ python3 -c "
import re
rx = re.compile(r'(?<![A-Za-z0-9_])' + re.escape('main.py') + r'(?![A-Za-z0-9_])')
print(rx.search(open('t3.txt').read()))"
None
```
同一個關鍵字「main.py」,執行器那套(`scripts/test_lumos.py:72` 的 `re.escape`)正確判定「mainXpy」不算整字命中;hook 這段新程式碼會誤判命中。

這不是純理論案例。`_SUITE_KEYS` 裡帶檔名時,檔名鍵是 `_affected_test_keys` 去掉「最後一個」副檔名產生的(`scripts/lumos:22393-22395`:`b.rsplit(".", 1)[0] if "." in b.lstrip(".") else b`)——多層副檔名的檔名去一層還是留著句點。這種檔名在本 repo 真實存在,例如 `scripts/vendor/3d-force-graph.min.js`:去掉 `.js` 後剩下的鍵是 `3d-force-graph.min`,句點還在,長度與字元集都通過 `_KEY_OK_RE`(`scripts/lumos:22367`)。哪天有人動到這類檔案又被判成 light,`_SUITE_KEYS` 就會帶著句點鍵進到這段 `grep -qw`,只要 `test_autonomous_loop.py` 原始碼裡剛好有一段「句點前後字元對得上、中間隨便一個字元」的文字,就會被判成命中而整支跑——跟執行器那套(以及這次 diff 自己聲稱的「整字比對」設計意圖)不一致。方向上是「多跑」不是「漏跑」,不會讓推送誤放行,但它直接打破這次改動本身的目的(把 108 秒的 light 推送壓到 40 秒),而且是專案裡「同一個判準、三處各自實作、語意各異」的具體案例——`pitfalls` 算 `affected_keys`(`scripts/lumos:22370`)、執行器 `--suite keys` 整字比對(`scripts/test_lumos.py:58`)、這支 hook 新加的 `grep -qw`(`scripts/hooks/pre-push:358`),三套各自决定「算不算命中」,其中第三套沒有沿用第二套已經在同一支 hook 裡被呼叫過的入口。

file: `scripts/test_lumos.py:58-79`(既有整字比對入口 `_keys_suite_select`,含 `re.escape`)
file: `scripts/hooks/pre-push:431`(同一支 hook 既有呼叫這個入口的地方,--suite keys --keys)
file: `scripts/hooks/pre-push:358`(這次新加、繞過上面入口自刻的 grep -qw)
file: `scripts/lumos:22393-22395`(檔名鍵可能保留內部句點的由來)
file: `scripts/vendor/3d-force-graph.min.js`(repo 裡真實存在、會踩到這個分歧的檔名範例)

severity: major
blocking: yes

## 驗過的路徑

**Q1(審材第①問,run_group 內部起子行程再 wait pid 陣列 vs 新的背景子殼)**:判定「對齊,不算不一致」。既有的平行寫法在 `run_group` 內部(`scripts/hooks/pre-push:437-456`,未改動):同一批同質工作(N 個分片)各自 `&` 起、pid 收進陣列、逐一 `wait` 收離開碼。這次 diff 改的是外層——兩個「已經是黑盒、各自平行」的 `run_group` 呼叫要同時起(`scripts/hooks/pre-push:464-471`,對應 patch 的 `( run_group s … ) & _gpid=$!` … `( run_group k … ) & _kpid=$!; wait "$_kpid" …; wait "$_gpid"`)。這裡沒有伸手進 `run_group` 內部改它的 pid 陣列或跨層直呼它的私有狀態,只是把 `run_group` 當函式呼叫、外面再包一層背景子殼——用的仍是同一個 bash 慣用語(`cmd & pid=$!` 之後 `wait "$pid" || rc=$?`),只是套用在「兩個異質工作」而不是「N 個同質分片」上,形狀自然不同(純量 pid 對陣列 pid),但不構成「第二種做法/再刻一份既有工具/繞過既有寫入口」。兩個 rc(`_grc`/`_krc`)後面各自被檢查,沒有被另一段邏輯蓋掉或吃掉。

**Q2 獨立於檔名比對之外的部分(探 runner 旗標的 `grep -q -- '"--x"'` 慣例本身)**:這次 diff 完全沒有動到 `--shard`/`--suite`/`--graph` 那三處旗標探測(`scripts/hooks/pre-push:404,410,420`,均在 patch 範圍外、原樣保留)。新加的 `grep -qw` 服務的是不同的任務(比對「識別字有沒有整字出現在原始碼」,不是「原始碼裡有沒有這個帶引號的旗標字面值」),兩者本來就該用不同的 grep 選項,單看旗標探測慣例本身沒被破壞。真正的問題不是「該用 -q 還是 -qw 探旗標」,而是這個新任務本身已經有專案唯一的正式入口(`_keys_suite_select`)可用卻沒用,見上面 F1。

**Q3**:併入 F1(整字比對三處各自實作、語意不一致且可重現,已附機械跑出的反例)。

其餘檢查過、沒有落在本席範圍內的異狀:patch 裡 `test_lumos.py` 的新增測試(`t_prepush_docs_and_light_run_subset` 那幾行 check)只是新增斷言配合上面兩處行為改動,沒有另開新的比對/平行寫法,不重複列。

不對齊共 1 條,其中 major 1 條。
