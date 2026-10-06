severity: clean

## 1. 分層與依賴方向
對齊。r4 的差異全在 lumos-guard 自己的檔:`register.ts` 內的 `release`、`save`、`end`、`onEnd`、`searchBase`,加上型別註解與 Python 測試。沒有新增跨層直呼:外部操作仍只走 `io`(`io.sleep`、`io.toast`、`io.saveSeats`),`onEnd` 仍只轉交給 `guard.end`,外掛沒有新呼叫 `$.process`。
對照:file: `mods/claude/lumos-guard/hooks/register.ts:265-280`(`save` 用 `Promise.race([job(), io.sleep(SAVE_MS)])`)。lumos-ledger 同樣用 `Promise.race` 加時鐘 sleep 限時,file: `mods/claude/lumos-ledger/hooks/register.ts:353`。這是同一種做法,不是新的。

三處已寫明理由的新寫法,理由站得住:
- onTool 抽出並匯出:理由是事件帳外掛只用 Python 釘字串,守不住「改成一律放行」。這輪 Python 端改成先拿掉註解、取 `export const register` 之後的片段、逐條釘接線字串(含 `.catch`)、確認每個事件只掛一次,是在既有的字串釘法上加固,沒有另開機制。file: `scripts/test_lumos.py:72211-72236`
- 存回帶版本、撞版重試:另兩支外掛不跨實例共用 `$.state`,理由成立。r4 補上逐格限時與撞版放棄的 toast,沿用 ledger 的「限時加提示」做法。
- Python 從原始碼抽正則:理由是標記格式只留一份真相;這輪沒有擴大這種做法。

## 2. 命名與錯誤處理
對齊。新 toast 以 `lumos-guard 存回撞版 …` 開頭,與既有的 `lumos-guard 逾時放行:` 同前綴同格式。`.catch` 的處理沿用 lumos-context 的「工具已跑過就交回原結果」做法,file: `mods/claude/lumos-context/hooks/register.ts:40-42`。`release(session, p)` 改成帶參數,命名與同檔的 `wake(p)` 一致。`onEnd` 加 `resume` 與型別檔註解同步更新。

## 3. 第二種做法
沒有新增。細看兩處:
- 測試內 `banned` 用原始碼本文比對,接線釘住用拿掉註解後的 `live`。同一支測試裡有兩種比對底稿,但各有明講的理由(禁用字樣連註解也要禁;接線要排除註解與死碼),不算第二種做法。
- `REVISIT:2026-11-06 …` 是專案規定的格式,綁在型別檔那句「沒實測」的宣告上,是把一句會過期的話搬成獨立一行的標準做法。

總結:不對齊共 0 條,其中 major 0 條
