severity: minor

本輪的併發與資源鏡頭沒找到會擋合併的問題,只有一條 minor。

1. `atomic_write_verify` 的符號連結檢查,在 `islink` 與 `readlink` 之間有一個極窄的時序縫。
   - 檢查通過後、組錯誤訊息前,若連結剛好被換成一般檔,`os.readlink` 會丟 `OSError`(EINVAL)。
   - 呼叫端多半只接 ValueError 與 RuntimeError,所以這種情況會變成堆疊追蹤。我用把 `islink` 強制回 True 的方式模擬過,確實丟出 `OSError: [Errno 22]`;真實的換名時序我沒能造出來。
   - 修前沒有這道檢查,所以這個縫是修補新帶進來的,但實際影響只是少印一個好看的訊息。
   - 筆記不會被寫壞:`os.replace` 本來就不跟隨連結。
   - ⚠ 窗口只有微秒,屬理論上的縫。
   - 歸因:有證據的修復回歸
   - 引句:「raise RuntimeError(f"這篇筆記是符號連結(指到 {_esc_clean(os.readlink(path), 160)}),寫進去會把連結換成一般檔、它指到的那篇不會改;"」
   - file: `scripts/lumos:19983`
   - 兩版查證:修前 `python3.14 p3.py old/scripts/lumos` 沒有這個例外,因為根本沒有 readlink。修後同一支腳本丟 `OSError [Errno 22]`,命令與輸出如上。
severity: minor
   - blocking: 否

本輪沒有成立為 finding 的觀察:

- **平方級:沒有。** 切斷檢查對頂格鍵最多掃一次(找到後就 break),整體是線性的。
  - 8 萬個頂格鍵加 8 萬行像題號的行:0.05 秒。
  - 單行 100 萬字的空白與 tab 混合,含刻意讓回溯最壞的結尾:0.05 秒內。
  - 160 萬個連續異體選擇符:`vs` 路徑 0.92 秒、`vs-same` 路徑約 0 秒,線性。
  - 16 萬面合法旗幟與很長的不合法標籤串:0.2 秒內。
  - 160 萬個空白類字元的 `_pq_blank`:0.28 秒。
- **符號連結時序沒有變差。** 在 `islink` 之後被換成連結,最後的 `os.replace` 只會換掉連結本身、不會寫穿到目標,修前也是這樣。我拿庫內符號連結跑了六個寫入指令(set、append、summary-line、decision-add、question-add、remove),修前全部成功,並把連結換成一般檔、讓目標與連結分家。修後只有 remove 沒走到寫入、照舊擋下,其餘五個都 rc2 擋下,連結原樣留著,沒有堆疊追蹤。
- **summary-line 的 try 範圍沒有半寫。**
  - 鎖內所有可能丟 ValueError/RuntimeError 的地方,都在 `atomic_write_verify` 的換名之前,或在 `_summary_line_locked` 的前置判斷。
  - 換名之後只有 `OSError` 可能,那個沒被吃,照舊傳出。
  - 外層 try 實際只多接了拿鎖逾時,以及鎖內程式漏接的內部錯誤。
  - 代價是內部 bug 的 ValueError 會被吃成 rc2 的「擋下」,不再有堆疊,可觀察性略降,但不是缺陷。
  - 順帶一點:被符號連結擋下時,「改前/改後」兩行已經先印出,畫面上像是改了、其實沒寫。這點在修前的其他擋下路徑也一樣。
- **16 個程序同時寫穩定。**
  - 我在 20 條滿載 CPU 迴圈下跑 `python3.14 scripts/test_lumos.py -k qfm_`,結果 253 通過 0 失敗,包含 16 個程序同時寫的 `t_qfm_decision_add_shares_lock`。
  - 同樣條件下 `-k concurrent_append` 連跑三次,都是 10 通過 0 失敗。
  - 最慢的 `t_qfm_commands_write_and_verify` 用了 44 秒,餘裕 4 倍,在負載下沒到逾時邊緣。
- **圖譜鏡頭:** 派工詞寫明這次沒附固定席節點,我沒有補讀 `lumos-cli-write.md`、`lumos-cli-read.md`、`規格閘.md`。

三問:

1. **原問題的修復效果。**
   - 切斷檢查改看「長什麼樣」,對應測試 `t_qfm_r5_folds` 在負載下通過。
   - 旗幟只收真旗幟形狀、異體選擇符與填充字被擋、符號連結被擋,這些我都用 `pq_parse`、`_pq_bad_char` 與命令列實際跑過,行為成立。
2. **相鄰路徑。**
   - 其他 26 個 `atomic_write_verify` 呼叫端多半已接 RuntimeError。
   - 我抽看了 `_drift_fix_write` 與 guard 補改,都接得住。
   - 其餘約二十處我沒逐一檢查是否接得住新的符號連結 RuntimeError;這是我沒覆蓋到的範圍。
   - 正常路徑與鎖未持有的錯誤路徑都沒變。
3. **新發現的同一案例的修前與修後。** 第 1 條的修前沒有該例外,修後有,查證命令與輸出見上。

總結:本輪沒有擋合併的問題,資源面線性、鎖與併發穩定,只有一個時序縫,可擇機把 `os.readlink` 包進 try 處理。
