severity: minor

我跑了比較模式、處置閘診斷行和擋下事件片段三條路徑,沒找到 blocking 問題。`python3.14 scripts/test_lumos.py -k quote_full_span` 是 90 通過、0 失敗。實驗目錄已刪。

比較模式我造了一個小 repo,13 種報告路徑加 2 種快照路徑:
- **上限邊界:** 剛好 4 MB 的報告會讀進來,多 1 位元組算讀不到。
- **路徑類:** 管線、repo 外路徑(`../x`、`/etc/passwd`)、含 NUL 的路徑、孤立代理字元路徑、不存在的檔,都算讀不到,不丟 traceback。
- **內容類:** 非 UTF-8 單獨計 1 組,CRLF 和單獨 `\r` 會統一成 `\n`。符號連結先解析再讀。
- **例外傳遞:** `UnicodeDecodeError` 照樣傳到呼叫端的 `except`,`MemoryError` 往外丟。

新舊判準本體我也讀過,沒找到錯。

**1. 診斷指令過 `_esc_clean` 後,含控制字元的路徑印出來不是原路徑,過長路徑被截成壞指令**
severity: minor
blocking: 否
引句:「_qdiag = _esc_clean(f"    診斷:lumos quote-check {_drift_sh(_prov_path(rp), node=True)}」
file: `scripts/lumos:26525`
- 我用 `_drift_sh` 加 `_esc_clean` 實際跑了一次。路徑是 `a\nb` 時,先被 `_drift_sh` 加了引號,再被 `_esc_clean` 把換行換成空格,印出 `'a b'`。照貼會指向另一個路徑,或找不到檔。路徑含 ESC 時也是同樣情形,印出 `'a [31mb'`。
- 路徑超過約 1900 字元時,整行被截成 2000 字加 `…`,印出的指令是壞的。
- 同檔的 `_drift_fix_hint` 遇到特殊字元路徑是不印可照貼的指令,這裡沒有照做。
- 影響只限診斷行,不影響閘的判定。要修的話,路徑含控制字元或過長時改印說明、不印指令。

總結:最高等級 minor,blocking 共 0 條
