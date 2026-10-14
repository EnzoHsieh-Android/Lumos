severity: minor

審查範圍:`_canary_ledger_scan` 的 `spec_gate`/`fields` 選項、`_nogo_ctx`、`_nogo_major_lookup`、`_nogo_snapshot_rows`/`_prov_read`。我用自己造的帳實測,實驗目錄已刪。

**作者的數字重現得出來嗎**
- 記憶體方向重現,幅度比作者小。我造的是 5 萬筆、276MB 的長備註帳,用 `python3.14` 載入 `scripts/lumos` 後在同一個程序裡量峰值 RSS。
  - `spec_gate=True` 加 `fields=` 約 664MB。
  - `spec_gate=True` 不加 `fields=` 約 872MB。
  - 既有讀法(`spec_gate=False`)約 957MB。
- 這個峰值不是作者說的 351MB。我的帳比他的 118MB 大,基準不同,所以只能確認方向,不能對數字。
- 3000 筆 major 各帶不同快照、全比不上時,`_nogo_major_lookup` 第一次耗 1.2 秒,峰值約 43MB。作者量到 3.1 秒,量級相符,我這台機器較快。

**一次推送碰到多份計劃時,索引每份重建嗎**
- 不重建。`_spec_gate_push_scan` 只建一次 `ctx`,`ctx["major_done"]` 是跨計劃共用的游標。
- 我連查三份都不命中的計劃:第 0 份 1.2 秒,第 1、2 份各 0.0 秒。已讀,無 finding。

**既有讀者(處置閘等)有沒有變慢或變肥**
- 預設路徑(`spec_gate=False`)只是把 `lines` 改成條件賦值,行為不變。實測 4000 個編號耗時 1.41 秒,記憶體沒有增加。
- `spec_gate=True` 逐行解碼並對每列做 NFC,耗時約為預設路徑的 2 倍(2.83–3.06 秒對 1.41 秒)。這是單人推送前一次性成本,可接受。
- 既有讀者已讀,無 finding。

severity: minor
blocking: 否 — 峰值仍是帳大小的 2 到 3 倍,但單人使用、帳到 276MB 才碰到,不影響正確性
引句:「逐行解碼:不把整本帳先解成一份字串再切成一份行清單」
問題:`raw = path.read_bytes()` 整本讀入後,`_ledger_lines(raw)` 用 `re.split` 一次切出完整的位元組行清單,生成器再逐行解碼。解碼那份副本確實省了,但 `raw` 和行清單這兩份副本在整個迴圈期間都還在。所以「逐行解碼」只拿掉了字串副本,沒拿到真正的串流效果。
具體失敗情境:帳到 1GB 以上時,推送前檢查的峰值約為帳的 2 倍再加解析物件,可能吃掉可用記憶體。改用 `finditer` 按位移切片,或逐行讀檔,可以讓峰值接近一份。
佐證:``file: `scripts/lumos:13740` ``(`raw = path.read_bytes()`)、``file: `scripts/lumos:13743` ``(`_ledger_lines(raw)`)

最高等級 minor,blocking 0 條。
