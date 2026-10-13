severity: minor

這輪修補的圖譜和程式一致,沒有找到 blocking 的問題。我在實驗目錄的複本(已刪)上對修補處做了 11 處變異,每處都跑 `-k quote`。

**一致性結果**
- `lumos lint` 對計劃、Systems/loop-convergence-recording、兩篇 Issue、Verification 共 5 篇都是 0 問題。`lumos doctor` 是 0 issues(864 篇)。
- `-k quote` 176 條全綠。
- Issue 和計劃寫的「307 份判定檔」,跟 `governance/replay` 實數 307 相符。
- 計劃第 40 行的量測數字(2627/359/21/43/235)比現在實跑(2635/363/23/43/237)少,原因是帳本新增了列。那一行有標日期,不算矛盾。
- 計劃 S1–S8 的字面和測試斷言對得上。這輪新增的行為(診斷指令、MemoryError、`--json` 被擋、`unclosed`、換行統一)沒有放進條款,但都在計劃〈做法〉有寫,測試也有斷言。
- 沒有新的 ★INVARIANT★ 被違反。

**變異結果**
- 翻紅 8 處:
  - `_esc_clean` 換回直接用原字串
  - `cats=unclosed` 改回 `miss`
  - 拿掉 `--json` 的擋下
  - 拿掉人讀輸出的「格式不合」標記
  - 拿掉 `S_ISREG` 檢查
  - 拿掉 `O_NONBLOCK`(翻紅形式是卡住逾時)
  - 拿掉 `or "-"` 佔位
  - 把 `O_NONBLOCK` 與 `O_NOFOLLOW` 一起拿掉(同樣是卡住逾時,所以 `O_NOFOLLOW` 單獨沒有驗到)
- 沒翻紅 4 處,對應下面四條 finding。
- 沒跑成:`\r` 換行統一那一處,我的取代字串在檔裡出現 7 次,沒有套上。

1. 診斷指令開頭是 `-` 時補 `./` 沒有測試守著
severity: minor
blocking: 否
引句:「開頭是 - 的補成 ./ 免得被當選項(r2 邊界席)」
file: `scripts/lumos:26516-26518`
- 變異:把 `("./" + str(x)) if str(x).startswith("-") else str(x)` 換成 `str(x)`,176 條全綠。
- 新增的測試只用了含空白的路徑,沒有開頭是 `-` 的報告路徑。
- 這條是修補為了擋「照抄指令時路徑被當成選項」才加的,現在拿掉它沒有任何測試會紅。

2. 比較模式的 128 MB 上限與讀取上限沒有測試
severity: minor
blocking: 否
引句:「if st.st_size > _QUOTE_COMPARE_MAX_BYTES:」
file: `scripts/lumos:26727-26731`
- 變異 A:拿掉 `st_size` 檢查,176 條全綠。
- 變異 B:拿掉 `fh.read(MAX+1)` 與讀後長度檢查,改成 `fh.read()`,176 條全綠。
- 測試沒有把常數縮小,也沒有超大檔的案例。r2 資源席要擋的「超大檔被整個讀進記憶體」這件事,現在沒有測試守著。

3. 寫側擋下事件求 `kind` 時的 `except MemoryError: raise` 沒有測試
severity: minor
blocking: 否
引句:「資源不足不是判準的錯,三處(處置閘、寫側、比較模式)一律照常往外丟」
file: `scripts/lumos:25832-25833`
- 變異:整段拿掉,176 條全綠。
- 新增的 MemoryError 測試只打處置閘那一處。拿掉之後,寫側遇到暫時性記憶體不足會被下面的 `except Exception` 吞掉,記成 `kind=unknown cats=err`。
- 計劃明寫「三處一致」,但只有一處有測試。

4. 擋下事件片段先截 400 字沒有測試
severity: minor
blocking: 否
引句:「snippet = (re.sub(r"\s+", " ", _esc_clean(first[:400], 400)).strip()[:60] or "-") if first else "-"」
file: `scripts/lumos:25837`
- 變異:`first[:400]` 改成 `first`,176 條全綠。
- 輸出因為最後還有 `[:60]`,功能上看不出差別;這個截斷只影響效能(巨長引句先被截再清)。
- 沒有測試用超長引句量效能,所以這條截斷沒有被釘住。

另有兩點不列 finding。S6 條款字面只寫「帶報告、`--spec`、`--rule` 時 rc2」,沒列 `--json`,但測試和〈做法〉都有。`O_NOFOLLOW` 因為路徑已經過 `resolve()`,實務上沒有效果,沒有單獨驗。

我建的複本與目錄已刪,我跑出來的 8 個 `gctl-run-*` 暫存也已刪。

總結:最高等級 minor,blocking 共 0 條
