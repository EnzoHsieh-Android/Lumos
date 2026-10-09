severity: major

先講我核對屬實的部分。這些我都實跑過,沒有 finding:
- 兩個提交的日期、先後關係都對。
- 三案的斷言數與失敗索引對得上:Java 8/12 與 [8..11],圍欄 5/8 與 [5,6],鎖 4/4 與 [3]。
- 強測試 alarm 8 縮 2 秒的規則與程式一致。
- 12 格 corpus 在 `python3.14` 下全 `qualified=True`。
- 匯入錯誤、零斷言、逾時三種,`replay()` 都真的列 `invalid`,不是當成功或失敗。

---

ID: BND-1
severity: major
blocking: 是
引句:「整體15秒程序逾時、語法超出支援範圍、匯入錯誤、零測試列 invalid」
審材外佐證 file: `governance/eval/historical_handbook_trial.py:207`(整支子程序 `timeout=15`)
審材外佐證 file: `governance/eval/historical_handbook_trial.py:112`(每次卡住的取鎖固定吃 `signal.alarm(2)`)

問題:spec 同時凍結「每次取鎖最多等 2 秒」和「整個子程序 15 秒」,兩者的乘法關係沒寫,也沒限制 test 方法數。語法白名單允許任意多個 `test_` 方法。錯版上每個巢狀取鎖的方法都要卡滿 2 秒才拋 `lock-enter-incomplete`。寫得越完整、每個方法都抓到目標的測試,越容易超過 15 秒,被判 `invalid`(不當 survived,也不計改善)。這會系統性懲罰「測試寫得多」的那一臂。手冊臂如果更愛寫多個情境,不會被當成檢出。

重現:
```
python3.14 - <<'EOF'   # 不叫模型,只呼叫 grade()
import sys; sys.path.insert(0,'/tmp/lumos-readme-oct-audit/governance/eval')
import historical_handbook_trial as t
head='import unittest\nfrom subject import fixture\nclass L(unittest.TestCase):\n'
m=lambda i:f'    def test_n{i}(self):\n        with fixture("cache-moved") as s:\n            self.assertTrue(s.fallback_ready())\n            with s.lock():\n                with s.lock():\n                    self.assertTrue(s.held())\n'
for n in (1,5,8):
    r=t.grade(head+''.join(m(i) for i in range(n)))
    print(n,r['status'],{k:v.get('status') or v.get('reason') for k,v in r['versions'].items()})
EOF
```
輸出:
```
1 methods -> detected   (3.9s)
5 methods -> detected   (12.1s)
8 methods -> invalid {'faulty': ('invalid','TimeoutExpired'), 'fixed': ('executed', tests_run=8, failures=0)}   (16.0s)
```
8 個全都會抓到目標的方法,結果是 `invalid`,不是 `detected`。

判準:spec 要補上其中之一:(a)方法數或累計卡住時間上限,並列進凍結的受限語法;(b)子程序總時限由「方法數 × 2 秒」推出,或改成整體卡住時間達上限就停手,再算檢出。同時要寫明「因超時 invalid」與「測試本身有問題」的區別。

---

ID: BND-2
severity: major
blocking: 是
引句:「已有證據原樣保存，若判定器出錯就標該批無效，修訂後換新輸出目錄重跑。」
審材外佐證 file: `governance/eval/historical_test_quality.py:67`(`result.stdout.splitlines()`)
審材外佐證 file: `governance/eval/historical_test_quality.py:71`(`json.loads(lines[0])`,父程序、無 try)
審材外佐證 file: `governance/eval/historical_case_corpus.py:33`(`patch.read_text()` 沒指定編碼)

問題:spec 承諾「判定器出錯就標該批無效」。實際上有一整類父程序端的環境錯誤根本進不了 `invalid` 分類,直接丟出 traceback,rc=1,沒有 `report.json`。
- 根因 A:`text=True` 和 `read_text()` 用 locale 編碼。非 UTF-8 locale 下,中文原始碼被誤解成 Latin-1,其中的 `\x85` 被 `splitlines()` 當行界切斷,`RESULT_JSON` 那行斷掉,父程序 `JSONDecodeError`。
- 根因 B:同一個機制也會被 check 的 `detail` 裡的 U+2028 或 U+0085 觸發,因為 `ensure_ascii=False` 不會跳脫它們。
- 根因 C:corpus 在同樣的 locale 下,補丁 SHA 比對先失敗,丟出 `historical-patch-sha-mismatch`。這句錯誤訊息會誤導人去懷疑歷史證據被動過。

重現:
```
cd /tmp/lumos-readme-oct-audit
LC_ALL=en_US.ISO8859-1 python3.14 governance/eval/historical_test_quality.py --out /tmp/x1
  -> json.decoder.JSONDecodeError: Unterminated string starting at: line 1 column 12   (rc=1,/tmp/x1 為空資料夾)
LC_ALL=en_US.ISO8859-1 python3.14 governance/eval/historical_case_corpus.py --out /tmp/x2
  -> ValueError: historical-patch-sha-mismatch                                         (rc=1)
LC_ALL=C python3.14 …            -> preflight_passed: true   (PEP 538 會強制 UTF-8,所以 C locale 正常)
LC_ALL=en_US.ISO8859-1 PYTHONUTF8=1 python3.14 …  -> preflight_passed: true
```
另外,`h.replay(src,'def t_x():\n    check("★前置★ x", True, "a\\u2028b")\n',method='t_x')` 直接 `JSONDecodeError`,父程序崩潰。

判準:spec 要寫明需要 UTF-8 環境,或程式端指定編碼、拿掉 `splitlines()`(改成 `split('\n')`),並把解析失敗列為 `invalid` 原因。

---

ID: BND-3
severity: minor
blocking: 否
引句:「執行固定入口並核對四組明細」
審材外佐證 file: `governance/eval/historical_test_quality.py:83`(`mkdir(exist_ok=False)` 排在 `git show` 之前)
審材外佐證 file: `governance/eval/historical_test_quality.py:27`(`git show` 的 stderr 被吞掉)
審材外佐證 file: `governance/eval/historical_case_corpus.py:101`(`results.json` 逐格覆寫,`summary.json` 只在最後寫)

問題:S1/S3 沒寫前置條件:要完整歷史、要 3.14 以上的直譯器,實作也沒預檢。
- 缺歷史提交(淺層 clone 或被 gc):`CalledProcessError`,rc=1。因為 `capture_output` 吃掉了 git 的 stderr,看不出是缺提交。輸出資料夾已被建成空的,同名重跑會 `FileExistsError`,換名字才行。
- 用系統 `/usr/bin/python3`(3.9.6):`test_function` 裡 `ast.parse` 解析歷史 `test_lumos.py` 就 `SyntaxError: f-string expression part cannot include a backslash`。rc=1,資料夾空。圖譜裡的 repro 寫的是 `python3`,在標準 macOS 上會踩到。
- corpus 中途崩潰:會留下只有部分資料的 `results.json`,沒有 `summary.json`。

重現:
```
# 假 repo(只有一個空提交)
git -C $F init; … --allow-empty commit
cd $F && python3.14 governance/eval/historical_test_quality.py --out $W/s1
  -> CalledProcessError … '2b4cb7ce…:scripts/lumos' returned non-zero exit status 128;rc=1;ls $W/s1 為空
python3.14 … --out $W/s1  -> FileExistsError
/usr/bin/python3 governance/eval/historical_test_quality.py --out $W/py39
  -> SyntaxError at historical_test_quality.py:32;rc=1
```

判準:spec 補一句前置條件(完整歷史、Python 3.14),入口在 mkdir 前先預檢並明說缺什麼。

---

ID: BND-4
severity: minor
blocking: 否
引句:「證據應保存完整歷史來源提交、檔案與測試片段 SHA、執行器 SHA、原始輸出和逾時調整。」
審材外佐證 file: `governance/eval/historical_test_quality.py:64`(逾時分支只回 `{'status','reason'}`)

問題:逾時那一格不保存 stdout 和 stderr(`TimeoutExpired.stdout` 其實拿得到),與 S2「原始輸出」不符。逾時正好是最需要看原始輸出的情境。

重現:
```
h.replay(src,'def t_x():\n    check("★前置★ x",True,"")\n    import time; print("partial-output",flush=True); time.sleep(30)\n',method='t_x')
  -> {'status':'invalid','reason':'child-timeout'}   # keys 只有 reason、status,partial-output 遺失(15.0s)
```

判準:逾時分支也要寫入 `exc.stdout` 和 `exc.stderr`;否則 S2 要註明「逾時格例外」。

---

ID: BND-5
severity: minor
blocking: 否
引句:「歷史弱測試不能在錯版重現通過，或強測試不能只因目標問題翻紅並在修復版回綠」
審材外佐證 file: `scripts/lumos@2b4cb7ce:24648`(`_t.time() - lock.stat().st_mtime < stale_sec`,牆鐘判斷「過期接手」)
審材外佐證 file: `governance/eval/historical_test_quality.py:62`(`timeout=15`)

問題:同一批輸入,結論會隨環境變化,而 spec 沒寫重跑規則,又把環境錯一次就退案。
- 時鐘:錯版的「卡住」依賴鎖檔 mtime 不超過 30 秒。只要巢狀取鎖那一刻牆鐘往前跳 30 秒以上,錯版會把自己的鎖當過期接手,巢狀成功,強測試在錯版變綠,該格 `qualified=False`。
- 負載:本機 120 個 `yes` 把 CPU 吃滿(10 核),四個子程序全部 `child-timeout`,`preflight_passed=false`,rc=2。4 倍核數負載下還能通過,但整體耗時從 8.6 秒拉到 46 秒。
- 重跑:兩次重跑的 `report.json` 位元組不同,因為 stdout 內含暫存路徑。結論欄位一致,但整檔雜湊不能當重現憑證。

重現(時鐘):在強測試的外層與內層取鎖之間插 `time.time=lambda: _r()+3600`,對錯版:
```
normal         executed failed_idx=[3]  qualified=True
clock-step+1h  executed failed_idx=[]   qualified=False
```
RETIRE-IF 寫的是「環境錯」該案就不進分母,但同一份 spec 又說要「按根因處置」。兩者矛盾,沒說暫時性環境錯要重跑幾次。

判準:補一條規則,區分暫時性環境無效(負載、時鐘)與案例本身壞掉,規定重跑次數和記錄方式。

---

ID: BND-6
severity: minor
blocking: 否
引句:「任一組合無法重播、強錯版失敗理由超出固定目標、正常基準紅或環境錯，該案不進模型效果分母」
審材外佐證 file: `governance/eval/historical_case_corpus.py:96`(`failed` 只取索引)
審材外佐證 file: `governance/eval/historical_case_corpus.py:98`(`qualified` 只比檢查數與索引)
審材外佐證 file: `governance/eval/historical_case_corpus.py:93`(Java 不要求 `★前置★` 標籤)
審材外佐證 file: `governance/eval/historical_test_quality.py:102`(單案入口有驗 `detail`,corpus 沒有)

問題:RETIRE-IF 把「失敗理由」列為退案條件,但 corpus 的資格判定完全不看失敗理由(`detail`、`label`)。同一個鎖案例,單案入口驗了 `'巢狀拿同一把鎖卡住了' in detail`,corpus 沒驗。Java 案還不要求前置斷言,只要 `checks[0]` 為真就算,而 `checks[0]` 只是「①@Test void 認得」,不是前置。

重現:
```
把強測試的 _boom 訊息換成 'unrelated-load-timeout',跑錯版:
failed= [(3,'unrelated-load-timeout')]
corpus 規則(len==4 且 failed==[3]):True
preflight 規則(detail 含 '巢狀拿同一把鎖卡住了'):False
```
實務上這個缺口目前不會誤判,因為索引在確定性程式碼下對應唯一原因。但條件寫在 spec 卻沒有被機械實作,屬於未落實的承諾。

判準:corpus 要比對 label 或 detail,或 spec 改寫成「只比對索引」。

---

ID: BND-7
severity: minor
blocking: 否
引句:「固定案例集應保留提交或快照來源、各檔SHA、原／實跑測試SHA、12組原始結果及預定失敗索引」
審材外佐證 file: `governance/eval/historical_case_corpus.py:94`(每格只寫 `test_sha256=sha(code)`,即實跑版)
審材外佐證 file: `governance/eval/historical_case_corpus.py:74`(manifest 欄位清單)

問題:`manifest.json` 只有整檔 SHA(`scripts/lumos`、`scripts/test_lumos.py`),沒有「原測試片段」的 SHA;`results.json` 每格只有實跑片段的 SHA。鎖案例實跑與原版不同(alarm 8 改 2),原版片段 SHA 在產物裡沒有,只能事後從 `test-materials.json` 重算。corpus 也沒有 `report.json` 那樣的 `instrument` 欄,逾時調整只能靠比對兩份文字。所有產物都沒記錄直譯器版本、git 版本、locale,所以 BND-2、BND-3、BND-5 那幾類結果不一致無法事後診斷。

判準:`manifest` 補 `original_test_sha256` 和 `instrument`、`python_version`、`git_version`。

---

逐類答實務隱患:
- 併發:無。三個並行跑各用各的輸出目錄,都通過。每格用獨立暫存目錄,鎖的 key 是各自 `mkvault` 路徑的雜湊,沒有共用狀態。同名輸出目錄靠 `mkdir(exist_ok=False)` 原子互斥,後到的會 `FileExistsError`(行為見 BND-3)。
- 效能:無額外問題。單案約 8.6 秒,corpus 約 18.8 秒。stdout 沒有大小上限,但執行的是受信任的歷史碼。對模型產出的限制是 AST 節點數上限 2000 加子程序 15 秒。超時風險見 BND-1。
- 資源:無。實測後暫存目錄都清掉,沒有殘留子程序。環境裡殘留的 `lumos-history-probe-*` 是 10-07 的舊物,不是這次產生的。
- 回滾:無問題。`exist_ok=False` 確保舊證據不被覆寫,spec 寫「換新輸出目錄重跑」與程式一致。入口只讀 git 歷史並寫輸出目錄,撤回提交即可。

各節:
- 目的與最小試行:見 BND-3、BND-4。
- 效果比較下一階段:已讀,無 finding。
- 實務隱患:已讀,無 finding。
- 回退:見 BND-2。
- 模型對照預先凍結:見 BND-1。
- 第一個模型對照結果:已讀,無 finding。
- 減少題目提示的對照:已讀,無 finding。
- 減少提示試行處置:已讀,無 finding。
- 固定案例集資格預檢:見 BND-5、BND-6、BND-7。
- 案例資格結果:已讀,無 finding。

總結最嚴重 severity: major;blocking 共 2 條
