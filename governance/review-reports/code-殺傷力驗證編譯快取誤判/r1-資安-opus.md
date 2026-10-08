severity: clean

# 代碼審第 1 輪 資安席(資安-opus)

結論:派工詞列的四個疑點我都逐一實測過,都打不出比原本更大的能力,所以沒有可報的洞。核對內容如下。

## 核對 1:os.utime / os.stat 會不會被連結導到工作樹外

引句:「mt_ok = _kill_after_write(target, mstate)」
file: `scripts/lumos:13960`(圍欄 `target = os.path.realpath(...)` 加 `startswith(wt_real + os.sep)`,這次沒改)

1. 碰修改時間用的 `target`,跟原本 `open(target, "w")` 寫檔用的是同一個值,而且已經先過了「兩邊都 realpath」的圍欄。寫檔本來就比改時間權限大,所以這次沒有開出新的攻擊面。
2. 實測:在工作樹裡提交一個 `link.py`,指向工作樹外的 `victim.txt`(修改時間先設成 1000000000)。guard kill 判成 `error`「file 路徑逃逸 worktree(圍欄擋下)」,跑完後 victim 的修改時間還是 `1000000000.0`,內容也沒變。重現腳本在 `pcc-r1-work-資安-opus/probe.py` 第 1 段。
3. 還原那一半的 `_kill_after_write` 排在綁定測試跑完之後,理論上測試程式可以在這段空檔把路徑換成連結。但 `run_cmd` 讀的是 repo 裡已提交的 `.lumos/config.json`,測試碼也來自同一份提交,不可信的提交本來就能在本機或 CI 上跑任意程式,直接 `os.utime` 任何檔都行。這條路徑沒有讓權限往上升。

## 核對 2:新加的等待能不能拖垮 CI

引句:「deadline = time.time() + 3.0」
file: `scripts/lumos:41797`(guard kill 只有命令列一個入口);`.github/workflows/ci.yml` 裡沒有出現 kill

1. CI 不跑 guard kill,所以談不上拖垮 CI。
2. 在本機,每條真的套上去的配方最多多等約 12 秒(兩次換秒等待各 3 秒、兩次寫後確認各 3 秒),一般情況下大約多 1 到 2 秒。實測 1 條配方加 baseline,總共 2.76 秒。
3. 攻擊者本來就控制測試碼和 baseline 要跑多久,逾時上限是 `max(b_elapsed*5, floor)`,每條配方都能撐到逾時,遠比這幾秒多。新的等待沒有放大攻擊者能造成的拖延。

## 核對 3:旁路欄 `_mtime_unsure` 能不能被筆記偽造

引句:「res["weak"] = bool(mk["ws"] or mk["flaky"] or node_dirty or res.get("_mtime_unsure"))」
file: `scripts/lumos:39495`(背書只有「至少一筆 killed 而且 weak 不是 True」才算強證據;只要有 survived 就一律不算)

1. 偽造 `false`:結果是 `{**r, …}` 疊出來的,寫後確認失敗時會蓋成 `True`,weak 又是用 `or` 合起來的,所以 false 壓不掉。實測配方裡寫 `"_mtime_unsure": false` 時,weak 照原本的判法算。
2. 偽造 `true`:實測配方寫 `"_mtime_unsure": true`,結果是 `killed weak=True`,`--json` 裡也看不到這個欄位。這只會把自己的配方降成弱證據。會寫這篇筆記的人,本來就能直接刪掉這條配方,而且 survived 不管 weak 是什麼都算失敗,所以不能拿來讓背書變強,也不能掩蓋 survived。
3. 旁註(不構成 finding):偽造 true 時,標準錯誤不會印那行提醒,看到的人只看得到 weak,看不到原因。不過這只會讓證據變弱,不算可利用的洞。

## 核對 4:標準錯誤的提醒有沒有印出人寫的字

引句:「print("⚠ 有配方寫檔後修改時間沒能跟上一次錯開(檔案系統時間精度太粗或時鐘異常),結果可能吃到舊的編譯快取,"」

1. 提醒是固定字串,沒有帶入配方的 file、test、old、new 這些人寫的欄位,沒有控制字元注入的空間。整次只印一次,由 `mt_warned` 控制。

最高等級:clean
