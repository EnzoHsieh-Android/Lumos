severity: minor

## 問 1 分層與依賴方向
未見跨層直呼。guard 維持「純函式核心 createGuard + 注入 Io + register 接線」的分層,跟 ledger 一致;Python 測試端只讀 TS 原始碼文字,不反向相依。新增的 `loadVersioned` / `saveSeats(ifVersion)` 都放在注入的 Io 型別上,核心不直接碰 `$.state`。對照 file: `mods/claude/lumos-ledger/hooks/register.ts:7`(Io 注入)、`mods/claude/lumos-guard/hooks/register.ts:394`。

## 問 2 命名與錯誤處理
命名沿用 `onXxx` / `createXxx` / `Io`。錯誤處理方向一致(判不出來寧可擋),但 `found === 'error'` 在派工回 deny、在寫檔工具回 deny、在讀取放行、在 Bash 用 BASH_ERROR,四條各自一行寫在不同位置,ledger 沒有對應的「擋」語意可比,屬 guard 自己內部的分散,不是跟鄰居不一致。無不對齊。

## 問 3 第二種做法
### F1 tool.call 掛鉤接線抽成 onTool,鄰居是內聯 + 釘字串
severity: minor
blocking: 否 — 結構仍是「掛鉤只轉交給函式」,只是跟 ledger 的內聯寫法不同,沒有引入新的跨層路徑。
引句:「export async function onTool(st: State, $: any, e: any, next: (e: any) => any): Promise<any> {」
說明:ledger `register.ts:379-395` 的 tool.call / agent.spawn 接線內聯,靠 `t_ledger_plugin_files_valid` 以原始碼字串釘住(`scripts/test_lumos.py` 的 S12);guard 這輪改成抽 `onTool` 並 export 讓 TS 測試直測,Python 端另釘「掛鉤只轉交」字串。兩種做法並存,但 guard 的 onSpawn/onEnd 本來就是 export 函式(ledger 的 onPrompt 等也是),方向一致,故只列 minor。

### F2 存回帶版本重試與逾時競速是專案新模式
severity: minor
blocking: 否 — 專案內鄰居(ledger、context)都沒有跨實例共用 `$.state`,沒有既有做法可對照,不算「鄰居已有卻自寫」;但此為專案首例,宜在圖譜記一筆。⚠ 交編排者判:是否要把 `ifVersion` 重試抽成共用慣例。
引句:「for (let i = 0; i < SAVE_TRIES; i++) {」
說明:`SAVE_MS` + `Promise.race([save(), io.sleep(SAVE_MS)])` 也是新做法;ledger 的寫檔是佇列串行(`queue`)而非版本重試。對照 file: `mods/claude/lumos-ledger/hooks/register.ts:119`。

### F3 Python 端用正則從 TS 原始碼抽 SEAT_RE
severity: minor
blocking: 否 — 同樣是「Python 讀 register.ts 文字」的既有手法,只是從「in code 子字串」升級成「抽正則再編譯」,多了一種寫法。
引句:「mre = _re.search(r"^const SEAT_RE = /(.+)/$", guard_src, _re.M)」
說明:ledger 慣例是 `"..." in code` 釘字串(`scripts/test_lumos.py` 的 S9、S12),並以 rules-fixture.ts 兩端各寫一份、拿同一組案例測。guard 此處改成單一來源抽取,反而比 ledger 的「兩份」更好,但是第二種寫法;S11 以外的 S10 仍用 `in code` 釘字串,同一檔內混用兩種。

總結:不對齊共 3 條,其中 major 0 條
