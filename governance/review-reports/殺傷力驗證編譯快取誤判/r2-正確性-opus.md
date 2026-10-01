severity: major

# 設計審第 2 輪 正確性-opus

實驗環境:`pc-r2-work-正確性-opus/repo`(`git clone --shared` 審材 repo)。我照 spec〈做法〉逐字做了一份雛形 `lumos.proto`:每次寫檔前等到新的一秒,寫完讀回、同一秒就補碰,每次 baseline 跑完和每次突變測試跑完都記下結束的秒。另外做了三個變體:`proto_b1` 只記第一次 baseline,`proto_norw` 拿掉還原前的等待,`lumos.orig` 是改動前的原版。腳本是同目錄的 `h.py`、`e1.py` 到 `e10.py`,結果直接抄在各條裡。run_cmd 裡的 `python3` 是 macOS 內建 3.9;`/opt/homebrew/bin/python3` 是 3.14。

整體結論:新做法本身是對的,雛形在下列情境都判對:原重現、改 a 再改 b、make、測試很快或很慢、多平台、拿修改時間跟現在比。問題出在三處:照字面實作會掉的標記、兩個條款測不到的半邊、一句容易讀成單數的話。

## F1 重試失敗時把 weak 設成 true,會被迴圈後的背書蓋章整個蓋回 false
severity: major
blocking: 是
引句:「並把這條結果的 `weak` 設成 true(弱證據,不當背書)」
file: `scripts/lumos:13999`
1. `cmd_guard_kill` 跑完所有組以後有一段背書蓋章迴圈,逐筆執行 `res["weak"] = bool(mk["ws"] or mk["flaky"] or node_dirty)`。這是直接指定,不是「或」上去。所以在配方迴圈裡先設的 `res["weak"] = True`,一律會被蓋成這三個條件算出來的值。
2. spec 只說「把這條結果的 `weak` 設成 true」,沒說要改蓋章那一行。照字面在組結果時設 true,run_cmd 帶 `{method}`、不在 flaky 平台、筆記也乾淨時,最後輸出就是 false。
3. 實驗 e7.py:用 `lumos.proto` 在行程內呼叫,把讀回檢查換成永遠回「重試 3 次仍同一秒」。標準錯誤照常印出「⚠ 修改時間重試 3 次仍同一秒,這條結果是弱證據」,但 `--json` 是 `[('killed', False)]`,kill-log 那一筆也是 `weak: False`、`verdict: killed`。
4. 後果:寫表態算背書時(`scripts/lumos:39448`),`r["verdict"] == "killed" and r["weak"] is not True` 會成立,這筆被當成強證據背書。這正好跟 spec 要的「不當背書」相反。S1 到 S3 沒有一條碰到這條路,實作做錯也全綠。
5. 建議:〈做法〉寫明蓋章那一行要改成保留已設的 true,例如 `res["weak"] = bool(res.get("weak") or mk["ws"] or …)`。再加一條條款,用替身讓讀回永遠同一秒,驗 `--json` 和 kill-log 的 weak 都是 true。

## F2 還原前的等待那半邊,S1 和 S2 照字面都測不到;拿掉它全綠,實際會誤判
severity: major
blocking: 是
引句:「測試以 run_cmd 每次跑時把被改的檔的修改時間與開始、結束時間寫進紀錄檔來驗,不靠時序」
file: `scripts/lumos:13950`
1. 每條配方的順序是「寫壞法 → 跑測試 → 還原」。還原寫出的修改時間,要等下一次跑測試才會被 run_cmd 看到。S1 是同一支檔兩條配方,下一條會在下一次跑之前先把壞法寫回去,把還原蓋掉;最後一條的還原後面根本沒有下一次跑。S2 記的是「被改的檔」,也就是那一條配方自己改的檔,所以同樣看不到還原。第 1 輪接手席提的「把還原那一半拿掉照樣綠」,照現在的字面還是成立。
2. 實驗 e10.py 照 S2 字面寫:run_cmd 每次記被改那支檔的修改時間和開始、結束時間,再驗每次寫檔的秒是否晚於上一次寫檔與上一次測試結束。結果如下:
   - 同檔兩條:原版 3/3 紅;雛形 3/3 綠;`proto_norw`(拿掉還原前的等待)也是 3/3 綠,判定照樣是 killed、survived,S1 也綠。
   - 改 a 再改 b、測試兩支都 import:第一條把 `prod.py` 的 `LIMIT = 5` 改成 `LIMIT = 9`,會讓測試紅,而且大小跟原檔一樣;第二條把 b.py 的 `'hi'` 改成 `'ho'`,無害。`proto_norw` 在這裡 3/3 把第二條判成 killed,是假的殺得掉。原因是 a 還原落在壞法那一秒,大小又一樣,第二條跑時吃到壞法的編譯結果。雛形 3/3 判對:killed、survived。
3. 所以實作只要漏掉還原前的等待,S1、S2 全綠,而「改 a 再改 b」這種真實情境會誤判。這是條款漏掉合約的一半。
4. 建議:S2 的測試固定用兩支檔。第一條改 a(壞法跟原檔一樣大),第二條改 b,測試同時 import a 和 b。紀錄檔要記兩支檔的修改時間,驗「第二次跑看到的 a 的修改時間所在的秒 > 第一次跑結束的秒」。這一條加進 S2 條款文字,不要只寫「被改的檔」。

## F3 「baseline 那次跑完也記」讀成只有一次 baseline,make 專案 5/5 誤判;baseline 其實會穿插在配方之間
severity: major
blocking: 是
引句:「都從 0 開始;baseline 那次跑完也記」
file: `scripts/lumos:13922`
1. baseline 是每個不同的 cmd 跑一次(`if cmd not in baselines`)。run_cmd 帶 `{method}`、同一組裡有兩個測試時,第二個測試的 baseline 會在第一條配方還原之後、第二條配方寫壞法之前才跑,中間就穿插了一次跑測試。spec 的「baseline 那次」是單數,〈做法〉列的每條流程「等 → 寫 → 跑 → 記 → 等 → 還原」也沒提到這次穿插的跑測試。
2. 實驗 e6.py 用 make 專案:`out.txt: src.txt` 用 cp 產出,run_cmd 是 `sleep 0.95; make -s && python3 test_guard.py {method}`。兩條配方都改 src.txt、大小不變,第一條會讓 TestLimitFive 紅,第二條會讓 TestName 紅。
   - 原版:`['survived','survived']` 5/5,兩條都誤判。
   - 雛形,每次 baseline 都記:`['killed','killed']` 5/5,判對。
   - `proto_b1`,只記第一次 baseline:`['killed','survived']` 5/5。第二條明明會傷到合約,卻被判成沒殺掉。原因是 TestName 的 baseline 在第 N 秒才 make 出 out.txt,第二條壞法也寫在第 N 秒;macOS 內建 make 3.81 只看到秒,我另外實測過,同一秒內來源較新也不會重編,所以用的還是舊產物。
3. F2 建議的 S2 測試只有一個 cmd,碰不到這條路,所以照單數讀法實作也全綠。
4. 建議:〈做法〉改成「每一次 `_kill_run` 跑完都記,包括每個不同 cmd 的 baseline,它們會穿插在配方之間」。S2 測試加一組帶 `{method}` 的兩個測試,第二個測試的 baseline 要跑超過 1 秒,讓它跨秒。

## F4 讀回檢查只比「上一次寫檔」,跟 S2 寫的「也晚於上一次測試結束」對不上;2 秒精度和時間戳較粗的檔案系統會漏
severity: minor
blocking: 否
引句:「`int(修改時間) <= 上一次寫檔的秒` 就等 1 秒、`os.utime(path)`(設成現在)再讀回,最多 3 次」
file: `scripts/lumos:13948`
1. S2 要求讀回的秒同時晚於上一次寫檔和上一次測試結束;〈做法〉的讀回檢查只比上一次寫檔。這是內部不一致。
2. 失敗場景(FAT):壞法寫在 98 秒,測試跑到 100.x 結束,等到 101 才還原,FAT 讀回是 100。100 > 98 所以檢查通過,但 100 等於測試結束的秒。測試中途在 100 秒 make 出來的產物,修改時間也是 100,只看秒的 make 不會重編。
3. 同一種情形也會發生在檔案時間戳比 `time.time()` 粗的系統上。Linux 一般用粗粒度時鐘蓋修改時間,剛跨秒就寫的檔可能落回前一秒。我在本機 APFS 量 3000 次寫檔加 40 次跨秒寫,一次都沒落回前一秒,所以 macOS 沒事;CI 是 ubuntu-latest,我這台沒有 Linux 可以實測,這一點是推論。
4. 實際殺傷力窄:要同時碰上「只看秒的建置工具」和「測試跨秒」。Python 編譯快取只比原始檔自己的修改時間,不受影響。但條款跟做法要寫成一致:讀回比的是 `max(上一次寫檔, 上一次測試結束)`。

## F5 時鐘往回撥時,等待迴圈沒有上限,會無聲卡住
severity: minor
blocking: 否
引句:「`while int(time.time()) <= max(上一次寫檔的秒, 上一次測試結束的秒): sleep(0.05)`」
file: `scripts/lumos:13947`
1. 迴圈拿牆上時鐘比已記下的秒。時鐘往回撥 X 秒,例如手動改時間、還原 VM 快照、NTP 直接跳,就會等 X 秒,中間不印任何東西,也不吃 `m_timeout`。
2. 實驗:用雛形的 `_kill_wait_new_second`,把記下的秒設成比現在晚 6 秒來模擬往回撥 6 秒,實測等了 6.5 秒。撥回一小時就卡一小時。
3. 建議:用 `time.monotonic()` 設上限,例如最多 3 秒;超過就印標準錯誤提醒、這條標 weak 後照常跑(F1 修好後 weak 才傳得出去)。程式裡別處已經這樣用 monotonic 算截止時間,例如 `scripts/lumos:148`。

## 白話/依據/PRIOR-ART/RETIRE-IF/REVISIT
已讀,無 finding。核對了「兩次寫檔落在同一秒、大小又一樣,後一次就拿到前一次留下的編譯結果」,也核對了「誤判是雙向的」。e1.py 同檔兩條(e2.py 的形狀改成「兩支檔」):原版 Python 3.9 5/5、3.14 4/5 把第二條判成 killed;雛形兩個版本都 5/5 判對。e2.py 也看到反方向:改 a 的壞法跟原檔一樣大時,原版 5/5 判 survived,吃到 baseline 留下的原檔快取;雛形 5/5 判 killed。〈實務隱患〉說「Python 3.14 沒量過」,這裡補上:3.14 用工作樹內的 `__pycache__`,在 macOS 照樣重現,雛形也修好。「`_kill_run` 還有其他 3 處呼叫」對得上:13922 是 baseline,另外兩處在 38139 和 38192;13950 是突變那一處本身。

## 範圍
已讀,無 finding,不一致的部分見 F4。核對了「不把任何檔的修改時間設到未來」:e9.py 的測試斷言 `getmtime(prod.py) <= time.time()`,雛形 3/3 判對,無害的判 survived、有害的判 killed。

## 做法
見 F1、F3、F4、F5。核對了「還原:等 → `git checkout -- <file>` → 讀回修改時間,同上補碰 → 記下」。cmd_guard_kill 只有兩條寫檔路徑:突變寫入在 13947,`git checkout` 在 13951。drifted、檔開不了、路徑逃逸、baseline 非綠都在寫檔前 `continue`;還原失敗走 `break`,後面不再寫。沒有漏等的寫檔路徑。多平台(e8.py:a、b 兩組各兩條同檔配方):原版 3/3 全判 killed,雛形 3/3 判 killed、survived、killed、survived,每組各自從 0 開始是對的。

## 條款
見 F2、F3。S3「應不晚於跑測試的當下」可以寫成不靠時序的測試;不過它只擋回到乙(設未來時間)那條路,原版程式也會綠,這跟它的用意一致。

## 回退
已讀,無 finding。核對了「revert 實作提交:guard kill 回到不設修改時間,舊的誤判會回來」;改動只在暫存工作樹裡等待和寫檔。

## 實務隱患
已讀,無 finding。核對了「每條配方最多多等約 2 秒」,實測:
- 測試很快時,雛形每條配方多約 1.85 到 1.9 秒。e1.py 兩條:原版 0.9 秒,雛形 4.6 秒;e8.py 四條:1.1 秒對 8.5 秒。
- 測試跑 1.3 秒時,每條多約 1.4 秒(e5.py 三條:7.8 秒對 12.1 秒)。
- 換上雛形跑 `test_lumos.py -k guard_kill`:246 個全過,耗時從 2 分 29 秒變 3 分 46 秒(多 77 秒,約 +52%)。
- 讀回補碰在 macOS 從沒觸發過;最壞情況是兩次寫檔各補碰 3 次,每條多約 8 秒。
都在計劃估計內。全套測試總共會多幾分鐘,計劃沒寫,建議補進〈實作紀錄〉。

## 實作紀錄/審計修正紀錄
已讀,無 finding。核對了「S2 改成用 run_cmd 寫紀錄檔驗秒數、不靠時序(接手席:原 S2 把還原那一半拿掉照樣綠)」,這次折法沒有真的補到,見 F2。

最高等級:major;blocking 共 3 條
