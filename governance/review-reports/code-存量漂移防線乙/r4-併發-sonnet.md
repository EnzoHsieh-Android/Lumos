severity: major

## F1 3.12 以前的斷詞預檢對每支大檔多花一倍以上時間,而且完全不看預算
severity: major
blocking: 是 — 預算 5 秒的條件實測跑 43 秒,預檢本身佔 25 秒,預算失效且成本是這份差異新增的
引句:「for t in _tok.generate_tokens(_io.StringIO(txt).readline):」
1. 輸入:語料裡有多支 15 萬字元以上的 .py(產生碼、遷移檔常見)、名稱出現在每支的文字裡。系統 python3.9 上跑。
2. 路徑:_DriftProbeTree.one 不帶路徑 → `any(self._defines(p, name, test) for p in items)` 逐支走 → _drift_py_names → _drift_py_too_deep;不到 15 萬字元才跳過,大檔整支斷詞一遍(純 Python 逐詞)才輪到 ast.parse。迴圈與斷詞內都沒有看預算。
3. 實測(3.9.6,40 支各約 1MB、每支含 target_sym、deadline=5 秒,腳本 cy4/t6.py,repo cy4/gp):
   - 有預檢:單一條件 43.4 秒,解析呼叫 40 次。
   - 把 _drift_py_too_deep 換成恆回 False:18.6 秒。預檢多出 24.8 秒,比 ast.parse 本身還貴。
   - 單支量測(cy4/t1.py):1MB 0.64 秒、5MB 3.2 秒、20MB 13.1 秒,約每 MB 0.6 秒,線性。「整支大檔量一次約 0.5 秒」只對 0.8MB 以內成立。
4. 後果:預算(預設 60 秒,起點與終點各一棵樹)在這條路徑上不能守;超時後 `one` 還回確定的 False(不是判不了),推送檢查與 scan 都沒有「超過預算」的說明。迴圈本身不看預算是上一版就有的,但這份差異把每支大檔的成本抬高 2.3 倍,並且是唯一新增的不看預算的長段。
5. ⚠ 沒有量到「一般專案」是否常有這麼多大檔;上面是造出來的最壞輸入,已如實標最壞。

## F2 _DriftNames 對全部改到的程式檔全文一次 re.findall,記憶體約為文字的 10 倍
severity: minor
blocking: 否 — 只在一次推送改到數十 MB 以上程式文字時出現,是暫時尖峰
引句:「self._names[key] = _DriftNames("\n".join(self._text[p] for p in key))」
1. 輸入:一次推送改到的程式檔合計約 50MB(例如整包 vendor 進來)。
2. 路徑:names_in 把所有改到的檔 join 成一個字串,_DriftNames.__init__ 的 `set(re.findall(r"\w+", text))` 先建出完整 token 串列才去重。
3. 實測(3.9,cy4/t2.py):52.9MB 全是不重複詞,耗時 1.45 秒,常駐記憶體從 18MB 升到 1059MB(join 後 510MB,findall 後再 +550MB)。同樣大小的重複詞文字 1.5 秒。時間可接受,尖峰記憶體是文字的 20 倍。
4. names_in 建完後不看預算(只在讀之前看一次)。

## 已看,無 finding
- 內容編號讀取:單一物件 missing 在 _nodehome_cat_blobs 回該位置 None,不影響其他檔;整批失敗(git 不可用、路徑含換行只會出現在退回「版本:路徑」的檔)回 None,names_in / _read 都當判不了。names_in 失敗不快取,每條候選行會重試一次 _read,但逾時會耗掉 deadline、下一行 _out() 直接短路;非逾時失敗只多開行程,實務無界問題。
- _DRIFT_OID_CACHE:跟 _DRIFT_LS_CACHE 同鍵、滿 8 個一起清、清完只放目前這個,兩者一致;一次 check 只用起點與終點兩個鍵。
- _drift_with_layout:每次有起點且非形狀改變的推送多列起點樹並算版面。用 200k 檔的 repo 量(cy4/t4.py):每棵樹列 0.27 秒 + 版面 0.21 秒,合計約 1 秒,結果有快取、後面判定會重用,不列 finding。
- _NotelinesNet 失敗當場停:失敗時 _m 設成 {},同一篇後面的行只是回空、不會 AttributeError,迴圈結束後 `net.failed` 回 None;git diff 只跑一次(failed 旗標擋住重試)。
- 候選篩選每行看預算、prefetch 每版一個行程:已看,無 finding。

最嚴重等級 major,blocking 共 1 條
