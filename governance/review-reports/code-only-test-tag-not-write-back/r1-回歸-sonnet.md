severity: clean

# 回歸鏡頭報告(slot_parse 抽成 _slot_scan)

對照做了什麼:
- 比對基準:舊版 `git show 2aafdcb2:scripts/lumos`;新版為 repo HEAD 718d32bd 的 scripts/lumos,兩份用 SourceFileLoader 載入。
- 人工逐行對照:舊迴圈的 core.append 三處(反引號成對、反引號不成對 rest[i:]、一般字元)對上新版的 text 片段(t0..i、尾段 t0..n);欄位收尾與沒收尾(值沒收尾 → field 吐到行尾、之後 return,前面正文先吐)結果相同。
- fuzz:300000 筆隨機字串(詞庫含 `[`、`]`、反引號、`[test:`、全形冒號、大小寫鍵、`[foo:` 非白名單鍵、巢狀方括號、換行、空字串、只有反引號、欄位緊接欄位、欄位在行首行尾),對 slot_parse 整份回傳(fields 與 core)比較:0 筆不同。
- 真實資料:docs/lumos-toolchain-knowledge 全部 md 共 67854 行,新舊 slot_parse 回傳 0 行不同。
- 效能:同 67854 行各跑三次平均,舊 0.328 秒、新 0.266 秒,新版沒有變慢(略快)。
- 呼叫端:`grep 'slot_parse('` 共 13 處(`scripts/lumos:3757,3830,3907,4223,4280,29200,29207,29343,29694,29704,29796,32946`),全部只讀回傳的 fields/core;產生器不拋例外、也沒有呼叫端依賴舊版的內部行為或例外,回傳型別(dict,fields 為 tuple 清單)未變。
- sig:`_nodehome_parse_note` 只在 `scripts/lumos:26955`、`27298`、`27300`、`43055` 呼叫,sig 只在記憶體比較(`scripts/lumos:27301`、`27397`),沒有寫進檔案或帳本,也沒有跨版本比較;新版讀舊版存下的 sig 的情境不存在。兩邊快照都由同一版程式當場重建。
- 固定席筆記:派工詞說明這次沒附,無條目可判。

diff 引句:
引句:「掃描規則只有這一份,slot_parse 與 _slot_strip_keys 共用」——確認 slot_parse 與新增的 _slot_strip_keys 確實共用同一掃描器,且 slot_parse 行為與舊版逐位元相同。

無 finding。

總結:全份最高等級 clean
