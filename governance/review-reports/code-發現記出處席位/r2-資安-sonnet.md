severity: minor

審查範圍:凍結 patch 全部 10 個檔(`scripts/lumos`、測試檔、計劃與知識筆記、skill 文件、`.lumos/lint-waivers.json`)。patch 內的密鑰或信箱掃過,無。

## ①提示注入
已看,無。
- 新增的自由文字入口是 `--finding-seat` 的席名,以及擋下事件裡的迴圈名與席名。
- 席名必須逐字等於同輪帳上某一筆的 `--auditor`,對不上就 rc2、不寫帳。
- 事件寫入前用 `_one()` 去掉空白與控制字元。
- 這些字串只印到 stderr 或 `gov --stats`,沒有進派工詞、hook 附加段或 AI 指令。

## ②讀寫與執行越界
已看,無。
- 新增程式不開子程序,沒有 shell 插值或 eval。
- 不寫 repo 外的路徑,不讀外來路徑,也沒有下載。
- 只寫既有的 `.canary-log.jsonl` 與治理帳。
- 測試檔的 `_sh.rmtree(root, ignore_errors=True)` 刪的是測試自建的暫存目錄(由 patch 片段看),不是外來路徑。
- 測試檔沒有新增真能用的憑證。

## ③非刻意、一步就能繞過的守衛

**發現 1:殘留的 `LUMOS_FINDING_SEAT_SINCE` 讓必填關卡整個失效**

severity: minor
blocking: 否

- 誰:使用者本人,或照常操作的 AI。
- 從哪:shell 裡殘留了 `LUMOS_FINDING_SEAT_SINCE=9999-12-31`。測試總檔預設就會 `setdefault` 這個值,若有人 export 或 source 過,就可能殘留。
- 送什麼:對新開的代碼審迴圈照常執行 `lumos canary record none --loop code-… --findings-set …`,不帶 `--finding-seat`。
- 拿到什麼:`_finding_seat_required_block` 走 `first < since` 分支回 None,必填關卡被意外走過,帳上不帶席名也寫得進去。
- 已有補償:`first >= const` 時印一行 stderr「提醒」,所以不是完全靜默。
- 為什麼只列 minor:提醒只印 stderr、不寫治理帳事件、也不擋。使用者按 Enter 就過了,事後帳上也查不到這筆是被推遲才放行的。
- 補強建議:推遲生效時記一筆治理帳事件(例如 `finding-seat-since-overridden`),讓事後查得到。
- 引句:「_os_mod.environ.setdefault("LUMOS_FINDING_SEAT_SINCE", "9999-12-31")」
- file: `scripts/lumos:19600` 附近(`_finding_seat_since_key` 與 `_finding_seat_required_block`,行號依 patch 位置估計)

**其餘已看,無:**
- 帳上有時間讀不動的列時,`finding-seat-badts` 會擋下(沒有走寬放行)。
- 沒帶 `--loop` 的 `--finding-seat` 會擋下。
- 席名先 NFC 正規化再比對,帳上存原字串。
- `_gov_event_types_ok` 對 `finding_seats` 做了型別驗證。
- 範圍外:自行造帳或回填更早的 `ts` 屬刻意偽造,不報。

最嚴重等級 minor
