severity: clean

這一輪修補沒有資源類 finding。以下數字都是我在 `spec-gate-nondo` 的程式上用 Python 3.14 實測的,沒有跑任何會寫帳的指令。

**`_ledger_physical_lines`:已讀,無 finding**
- 100MB 單行:0.49 秒,峰值約 350MB。這包含測試資料本身 100MB 和丟出那一行時複製的 100MB,所以比作者量的更快,結論是線性。
- 96MB、1200 萬條短行(`{"a":1}\n`):5.99 秒,峰值 135MB。
- 100MB、每行 40KB(比區塊大):0.45 秒,峰值 134MB。
- 90MB 純 `\r` 行尾:13.99 秒;100MB 的 `\r\n` 行尾:11.54 秒。兩者峰值都在 140MB 以內。
- 很多短行時,`del buf[:pos]` 沒有變回平方級。每行約 0.5 微秒,耗時只跟行數成正比。慢的是一塊裡要切很多行,不是刪緩衝。
- 區塊結尾是 `\r` 時只把 `scan` 退回該位置,不會重掃整個緩衝。

**`_is_invisible`、`_pq_is_default_ignorable`、`_door_scan_text`:已讀,無 finding**
- 1MB 全中文:`_strip_zero_width` 0.10 秒,逐行 `_door_scan_text` 0.25 秒,`_door_keyword_hits` 0.28 秒;整份當一行時也是 0.29 秒。
- 其他全非 ASCII 的 1MB 輸入:é 0.11 秒、組合記號 0.16 秒、補充平面字元 0.07 秒。
- 每字元查表(`unicodedata.category` 加 `bisect`)大約每字元 0.1 微秒,不是瓶頸。
- 先刪再 NFKC 再刪(兩趟)的額外成本小。最壞的放大案例是 1MB 的 U+FDFA(NFKC 展開約 18 倍,約 630 萬字元):整行掃描 1.94 秒,`_door_keyword_hits` 2.66 秒。這是單次、有上限、一次性的耗時,對本機單人使用不算失控。
- 35 萬條單字短行 1.19 秒,50 萬條 ASCII 短行 1.20 秒,都是線性。
- ASCII 路徑改用 `translate`,不逐字查表。

**治理帳推送前只讀一次:已讀,無 finding**
- 100MB 的版控治理帳,`_retro_gov_events(root)` 耗時 0.80 秒,峰值約 409MB,約為檔案的 4 倍。這是既有的整本讀入加整本切行,不是這輪修補造成的。這一輪讓它從每份計劃讀一次變成每次推送讀一次,峰值沒有隨計劃份數成長。
- 單人本機下沒有足以擋下誠實操作的量級,所以不記 finding。
- 不帶編號取全部 `loop-retro` 事件後,`_cap_retro_status` 仍用 `e.get("loop") == loop_id` 篩選,沒有跨迴圈串味的問題。

**其他:已讀,無 finding**
- `_under_root` 兩處替換只是路徑拼法的收斂。

最高等級 clean,blocking 0 條。
