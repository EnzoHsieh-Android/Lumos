severity: major

1. 比較模式的 `_read` 自己重寫了一遍安全開檔讀檔，沒有重用既有的 `_regular_own_fd` 和 `_retro_read_bytes`
severity: major
blocking: 是
引句:「fd = os.open(fp, os.O_RDONLY | os.O_NONBLOCK | getattr(os, "O_NOFOLLOW", 0))」
file: `scripts/lumos:26724`
- 這一行加上後面的 `os.fstat` 和 `S_ISREG` 判斷，做的事跟 repo 既有的 `_regular_own_fd(path, os.O_RDONLY, require_owner=False)` 一樣（`scripts/lumos:1387`）。兩邊都是 `O_NOFOLLOW` 加 `O_NONBLOCK`，都是開檔後才判一般檔。
- `_regular_own_fd` 的說明（`scripts/lumos:1390`）寫明這是同一套寫法的單一來源，之前另抄一份的人被代碼審點名過（r2 架構對齊席）。
- 帶上限的讀檔也已經有現成的：`_retro_read_bytes(p, limit=...)`（`scripts/lumos:14565`）。它走 `_regular_own_fd`，用分塊讀並在超過 `limit` 時停下，是同類「一次開檔、判一般檔、限長度」的函式。`limit` 目前只有 256KB 的預設，要再讀 128 MB 可以直接傳進去。
- 這裡等於在同檔引入第二種開檔做法。改法是把 `_read` 換成呼叫既有函式（`_regular_own_fd` 或 `_retro_read_bytes`），超限和不是一般檔再轉成 `OSError`。
- 注意：`_read` 前面已先 `resolve()` 並檢查在 repo 內，所以 `O_NOFOLLOW` 擋的只是最後一段。這跟既有函式的行為一致，沒有差異。

2. 診斷指令的「開頭是 `-` 補 `./`」另寫了一個 lambda，同檔已有現成寫法
severity: major
blocking: 是
引句:「_qarg = lambda x: _sh_quote(("./" + str(x)) if str(x).startswith("-") else str(x))」
file: `scripts/lumos:26518`
- 共用說明點名要查診斷改用 `_sh_quote` 是否用對。`_sh_quote` 本身用對了，參數也有加引號。
- 但同檔 `_drift_sh(v, node=True)`（`scripts/lumos:40086`）已經在處理「印給人貼的參數、`-` 開頭補 `./`、其餘交給 `_sh_quote`」，說明裡也解釋了 `-` 開頭加引號沒用。
- 另外 `scripts/lumos:17433` 對 `-` 開頭的做法是直接不印（回 `None`）。現在 repo 裡對「`-` 開頭」有三種處理。
- 這個 lambda 加上 `_sh_quote`，等於在 `_drift_sh` 之外再寫一套。
- ⚠ `_drift_sh` 沒有給 `_drift_` 以外的地方用過。`node=True` 的名字偏 drift 領域。若不想跨域呼叫，至少應該把這個 lambda 抽成共用 helper，或在說明裡寫為什麼不重用。這條我判不準是「必須重用」還是「抽共用」，但現況有兩套是確定的。
- 這個 lambda 在 `if/else` 的區塊內被定義，只用一次，是風格問題，不另列。

3. 片段改用 `_esc_clean`：用對了
severity: minor
blocking: 否
引句:「snippet = (re.sub(r"\s+", " ", _esc_clean(first[:400], 400)).strip()[:60] or "-") if first else "-"」
file: `scripts/lumos:25836`（約）
- 簽名和語意都對得上：`_esc_clean(v, limit=200)` 是顯示消毒，先截 400 再清，limit 給 400 不會多出 `…`。
- 這跟同檔其他用法一致（`scripts/lumos:1897`、`scripts/lumos:2404`）。沒有第二種做法。
- 清洗後 `strip()[:60]` 加 `or "-"` 是這裡才有的需求，不算分岔。
- 這條是確認項，不是缺陷。

4. MemoryError 三處寫法一致，但「比較模式」那一處不是明寫的 `except MemoryError: raise`
severity: minor
blocking: 否
引句:「except MemoryError:   # 資源不足不是判準的錯,三處(處置閘、寫側、比較模式)一律照常往外丟(代碼審 r2 架構對齊席)」
file: `scripts/lumos:25832`
- 寫側（`scripts/lumos:25832`）和處置閘（`scripts/lumos:26533`）都是 `except MemoryError: raise`，接著才是 `except Exception`，寫法一致。
- 比較模式（約 `scripts/lumos:26740`）對 `_quote_rows` 沒有 `try`，所以 `MemoryError` 自然往外丟，效果同樣是照常往外丟。
- 註解說「三處一律」，但第三處靠的是「沒有 `except Exception`」。若日後有人在比較模式外層加 `except Exception`，這條保證就破了。
- 目前沒有第二種做法，只是三處保護方式不同形；不算 major。

總結:最高等級 major,blocking 共 2 條
