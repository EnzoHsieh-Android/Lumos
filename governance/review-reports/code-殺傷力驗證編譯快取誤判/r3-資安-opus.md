severity: minor

# 代碼審第 3 輪 資安席(資安-opus)

結論:這次新加的東西(換秒等待、寫後確認、`mstate["unsure"]` 清單、旁路欄、標準錯誤提醒)我逐一站在攻擊者那邊試過,都沒有打開新的洞。只找到一個**改動之前就有**的洞:配方的 `file` 指向工作樹裡的符號連結時,「還原」只把連結本身還原,真正被改壞的檔一直留著,後面無害的配方就會被判成強證據的 killed。新加的還原後確認檢查的是連結指向的那支檔,所以看不出這件事。這個洞不是這次造成的,不擋這次推送,建議另立 Issue。實驗都在 `pcc-r3-work-資安-opus/` 的 clone 裡跑,腳本是 `probe.py` 和 `probe_b.py`。

## F1 配方 file 指向符號連結時,還原的是連結、被改壞的是連結指向的檔,還原後確認也就沒有用(改動之前就有)
severity: minor
blocking: 否
引句:「if _kill_after_write(target, mstate):」
file: `scripts/lumos:13965`(`target` 經過 realpath,解析到連結指向的檔)
file: `scripts/lumos:13983`(壞法寫進 `target`,也就是連結指向的檔)
file: `scripts/lumos:13995`(還原用的是原始的 `r.get("file")`,也就是連結本身)

1. 前提:被測的 repo 裡已經提交了一個連結,例如 `L.py -> prod.py`,而且兩支檔都在工作樹裡,所以圍欄會放行。攻擊者只要能改筆記就夠了,測試程式可以是可信的。
2. 經過:配方寫 `file: L.py`。壞法經過 realpath 寫進 `prod.py`,還原時卻跑 `git checkout -- L.py`。連結本身沒變,`prod.py` 就一直維持被改壞的狀態。這次新加的還原後確認 `_kill_after_write(target)` 讀的是 `prod.py`:它的修改時間沒晚於上一次,就等 1 秒、`os.utime` 碰一下,然後回 True。結果是「還原成功、時間也錯開了」,`unsure` 不會記下這支檔。
3. 後果:同一組後面的配方,都會在 `prod.py` 還壞著的工作樹裡跑。攻擊者只要再寫一條完全無害的配方,就會被判成強證據的 killed,等於偽造出「這條合約的測試咬得住」的證據。
4. 重現(新舊兩版結果相同,所以是改動前就有的洞,不是這次造成的):
   ```
   $ python3 probe_b.py <repo>      # 第二條把 other.py 的 X = 1 改成 X = 2,測試根本沒 import other.py
   --- 新版 97f57017
   0 [('L.py', 'killed', False), ('other.py', 'killed', False)]
   --- 舊版 d8b02331
   0 [('L.py', 'killed', False), ('other.py', 'killed', False)]
   ```
   預期是 `other.py` 判 survived,並且回傳碼 1。
5. 和這次改動的關係:這次的設計假設「還原寫回的檔就是 `target`」,但遇到連結時這個假設不成立,所以新加的確認和 `unsure` 清單擋不住這種污染。修法(另開):還原改成對 `os.path.relpath(target, wt_real)` 跑 checkout;或者 `file` 只要經過 realpath 後跟原路徑不一樣就直接擋掉;還原後也可以加一步比對內容和原檔是否相同。

## 核對過、不能被利用的部分(不構成 finding)

### 核對 1:`os.stat`、`os.utime` 會不會被連結導到工作樹外
引句:「os.utime(path)」
1. `path` 就是寫檔用的那個 `target`,已經先過了兩邊都做 realpath 的圍欄。修改時間只會碰到原本就會被寫入的檔,權限沒有比寫檔更大。
2. 測試在跑的那段時間,可以把 `target` 換成指向工作樹外的連結。但還原用的 `git checkout` 會先把它換回一般檔,而且能做這件事的一定是測試程式本身,它本來就能在本機跑任意程式。只能改筆記的攻擊者碰不到這段空檔。第 1 輪的連結逃逸實驗結果仍然成立。

### 核對 2:`mstate["unsure"]` 能不能被拿來把弱證據壓成強證據
引句:「mt_ok = mt_ok and not mstate["unsure"]」
1. 清單用 realpath 後的 `target` 當鍵,所以換一種寫法指名同一支檔,會正確對到同一筆。實測 `probe.py` A4:第一條還原的確認被我強制改成失敗,第二條用 `./prod.py` 改同一支檔。輸出 `[('killed', True), ('survived', False)]`,也就是第一條記成弱證據;第二條重寫成功、修改時間錯開,快取已經作廢,移出清單是對的。
2. 只有「同一支檔又寫入一次,而且修改時間讀回來確實錯開」才會把檔移出清單,筆記沒有其他欄位能碰到它。唯一的例外就是 F1 的連結情況,但那是還原的對象選錯了,不是清單的問題。

### 核對 3:等待能不能被拿來拖慢
引句:「deadline = time.time() + 3.0」
1. `unsure` 清單只影響要不要記成弱證據,不會增加等待。
2. 換秒等待排在「old 命中恰好 1 次」之後,漂移、名稱不合法、baseline 不綠的配方都不用等。所以每條要等的配方都一定會跑一次完整的測試,攻擊者沒辦法用便宜的配方去疊等待時間。
3. 每條配方最壞多等約 12 秒,前提是修改時間被測試程式改到未來,而能這樣做的測試程式本來就能自己 sleep,沒有被放大。

### 核對 4:旁路欄能不能用筆記裡手寫的同名欄位偽造
引句:「res["weak"] = bool(mk["ws"] or mk["flaky"] or node_dirty or res.get("_mtime_unsure"))」
1. A1:配方寫 `"_mtime_unsure": false`,同時把確認強制改成失敗,結果是 `killed weak=True`,手寫的 false 會被 `res["_mtime_unsure"] = True` 蓋掉。
2. A2:配方寫 true,結果是 `killed weak=True`,`--json` 裡看不到這個欄,也不會印提醒。這只能把自己的配方降成弱證據,沒有利用價值。
3. A3:配方手寫 `unsure`、`w`、`r`、`weak: false` 這些和 `mstate` 同名的欄,結果是 `killed weak=False`,總共 1.8 秒。`mstate` 和 `r` 是兩個不同的物件,`weak` 收尾時會整欄重算,所以這些手寫欄位都沒有作用。

### 核對 5:標準錯誤提醒有沒有印出人寫的字
引句:「print("⚠ 有配方寫檔後修改時間沒能跟上一次錯開(檔案系統時間精度太粗或時鐘異常),結果可能吃到舊的編譯快取,"」
1. 提醒是固定字串,沒有帶入配方的任何欄位。整次只印一次,由 `mt_warned` 控制,A1 實測印出 1 次。

最高等級:minor
