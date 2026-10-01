severity: major

席名:正確性-opus(代碼審第 2 輪,只審第 1 輪的修正本身)

## F1 還原沒錯開造成的舊編譯快取會一直留到整組結束,carry 只帶到下一條,再下一條被記成強證據 killed
severity: major
blocking: 是
引句:「mstate["carry"] = True   # 還原沒錯開:這一條與下一條都記弱證據」
file: `scripts/lumos:13985`
file: `scripts/lumos:13986`
file: `scripts/lumos:13998`
file: `docs/lumos-toolchain-knowledge/Projects/殺傷力驗證編譯快取誤判_計劃.md:45`

1. 白話:還原寫回的檔如果跟壞法落在同一秒、大小又一樣,Python 會一直認為「壞法那次編出來的快取還有效」。只要這支檔之後沒被重新寫過,這份舊快取就一直被用,不只下一條,後面每一條 import 它的測試都會吃到。快取驗過一次不會重編,所以下一條跑完以後舊快取還是在。
2. 程式現在的做法是下一條套壞法寫完就把 carry 清掉(`mstate["carry"] = False`),從再下一條開始不再記弱證據。所以只要同一組有三條以上、後面的配方改的是別支檔,第三條起的結果就是「強證據」,其實那個紅燈來自第一條留下的壞法快取。
3. 重現(仿照修正自己的測試 ④ 的注錯法,把第一條還原的修改時間設回壞法那一刻、回 False;三條配方:a.py 傷合約、b.py 兩條無害,同一個測試 import a 跟 b):
   ```
   /opt/homebrew/bin/python3 carry_repro.py <clone>    # 腳本在 scratchpad/pcc-r2-work-正確性-opus/carry_repro.py
   a.py 'A = 1' -> 'A = 2' verdict= killed weak= True
   b.py '# x' -> '# y' verdict= killed weak= True
   b.py 'B = 1' -> 'B = 3' verdict= killed weak= False     <- 無害壞法被判強證據 killed
   ```
   連跑 3 次,3/3 一樣。對照組(不注錯)是 `killed False / survived False / survived False`,可見第 2、3 條的紅燈全來自第一條的舊快取。第三條 `weak=False`、verdict `killed`:rc 跟 kill-log 都當作真的接住了。
4. 觸發條件要誠實講:真實環境下 `_kill_after_write` 回 False,而且最後讀回的秒剛好等於壞法那一秒,只會發生在時鐘往回撥、或檔案系統不吃 `os.utime` 這類罕見情況(FAT 的 2 秒精度重試就會錯開)。不過 carry 本來就是為這個罕見情況加的,現在只蓋住一半,而且漏掉的那一半正好是會被當成背書的強證據。
5. 筆記也照錯的範圍寫:計劃第 45 行說「受影響的是下一條的測試,下一條也一起記」,程式註解「還原寫回的檔可能被這次的測試 import」也一樣。
6. 修法建議(擇一):carry 設了以後整組都不清(最簡單、偏保守);或記下「還原沒錯開的檔」,等同一支檔之後有一次寫後確認成功才清掉。測試 ④ 加一條第三條配方,改的是別支檔,斷言它也是 weak。

## F2 重試測試的「記進 state」斷言是空的:拿掉 `state["w"] = mt` 照綠
severity: minor
blocking: 否
引句:「check("①讀回跟上一次同一秒 → 等、碰成現在、錯開後回 True、記進 state", ok is True and st["w"] > int(t0) - 1」
file: `scripts/test_lumos.py:60607`

1. `st["w"]` 一開始就是 `int(f.stat().st_mtime)`,本來就大於 `int(t0) - 1`。所以就算 `_kill_after_write` 沒把讀回的秒記進 state,這個斷言也會過。後面那條 `int(f.stat().st_mtime) > int(t0) - 1` 也一樣是空的。真正有判別力的只有 `ok is True`。
2. 翻紅實驗:把 `_kill_after_write` 裡的 `state["w"] = mt` 刪掉,`-k kill_after_write_retry` 照綠(2 passed),`-k stale_build`、`-k mtime` 也都綠(3 passed、5 passed)。目前沒有任何測試守住「寫後確認成功要記進 state」這件事。
3. 建議改成先記 `w0 = st["w"]`,再斷言 `st["w"] > w0`,同時斷言 `st["w"] == int(f.stat().st_mtime)`。

## 已核對、沒有問題的部分
- carry 的設定與清除時機:第一條寫檔前 carry 初值是 False(`mstate = {"w": 0, "r": 0, "carry": False}`),不會誤記。還原失敗 `break` 時整組結束,carry 用不到。下一條在等待前就因 test 名不合法、逃逸、漂移、baseline 非綠而 `continue` 時,carry 不會被清,會留給再下一條(偏保守,方向正確)。`mstate` 建在每個平台迴圈裡面,各組各自獨立;`mt_warned` 跨組共用,符合「整次只印一行」。`_kill_after_write(...) and not mstate["carry"]` 會先呼叫寫後確認,`state["w"]` 照常更新。
- 翻紅:刪掉 `and not mstate["carry"]` 以後,`t_guard_kill_mtime_unsure_is_weak` ④ 翻紅(第二條 weak=False)。刪掉套壞法後的 `mstate["r"] = int(time.time())` 以後,`t_guard_kill_no_stale_build_cache` ③ 3/3 翻紅。兩個修正都有測試咬住。
- 穩定性:S2 加了 1.1 秒睡眠,斷言比的是「寫檔讀回的秒」對「測試裡印出的結束時間」,有寫前等待和寫後確認兩層保證,不靠運氣。Linux 的檔案時間戳取自較粗的核心時鐘,可能落後一點,但頂多讓寫後確認多重試一次,不會假紅。重試測試本機實測 5.5 秒,①、② 都不依賴秒邊界,不會假紅。
- 筆記:「最壞約 12 秒」= 兩次等待各 3 秒 + 兩次寫後確認各 3 秒,跟程式一致。guard-kill 的 weak 第四項、rc 段的「`weak` 欄不影響 rc」跟收尾重算 weak、rc 優先序的程式一致。

最高等級:major
