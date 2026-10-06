severity: minor

## 1. 分層與依賴方向(跨層直呼?)

沒有跨層直呼。guard 的分層跟鄰居一樣:核心邏輯在 createGuard,查路徑、時間、提示、存檔由 Io 注入,register 只接線。
- file: `mods/claude/lumos-guard/hooks/register.ts:352`(makeIo,對照 `mods/claude/lumos-ledger/hooks/register.ts:262` 的 makeIo)
- ledger 改成用 parentAgentId 當發起方,也是純函式 spawnFields、spawnEvent 加接線,沒有跨層。file: `mods/claude/lumos-ledger/hooks/register.ts:319`
- Python 端 `_LUMOS_PLUGINS` 只加一項,逐支安裝與移除的邏輯沿用,沒另寫一份。file: `scripts/lumos`(外掛段)
- 外掛安裝端與 TS 端之間沒有新的相依。

## 2. 命名與錯誤處理(跟鄰居一樣嗎?)

大致一樣:
- 檔名(register.ts、guard.test.ts、hooks.json 內容一字不差)、匯出 `register: Register`、注入式 Io 都對齊。file: `mods/claude/lumos-context/hooks/hooks.json`
- 能擋人的掛鉤掛 `.catch`,跟 lumos-context 一樣。file: `mods/claude/lumos-guard/hooks/register.ts:414`、`mods/claude/lumos-context/hooks/register.ts:42`
- 測試端 `claude plugin validate` 檢查 hasCatch,是複用 context 既有的做法。file: `scripts/test_lumos.py:72394`
- 錯誤訊息用「擋下/為什麼在意/怎麼辦」三段式,符合專案輸出慣例。

有兩處小不齊,見 F1、F2。

### F1 型別宣告走法跟鄰居不同(plugin.json 的 types 欄位與 types/ 目錄)
severity: minor
blocking: 否 — 結構沒變,只是外掛描述檔與目錄佈局多了一種鄰居沒有的寫法
引句:「"types": "./types/index.d.ts"」
說明:lumos-ledger、lumos-context 的 plugin.json 沒有 types 欄位,也沒有 types/ 目錄,一律用 `$: any`。guard 是第一支這樣做的,用 `declare module 'claude-code'` 擴充 PluginState 來型別化 $.state。我沒查到這個欄位與擴充是引擎公開支援的寫法(只在 guard 出現),⚠ 交編排者確認:若引擎沒文件化,就退回 `$: any` 的鄰居寫法。file: `mods/claude/lumos-guard/.claude-plugin/plugin.json:5`、`mods/claude/lumos-ledger/.claude-plugin/plugin.json`

### F2 席標記格式在 Python 測試裡複製了一份,沒有讀 TS 原始碼
severity: minor
blocking: 否 — 結構沒變,只是「同一條」靠註解保證,沒有機械綁定
引句:「# 跟 mods/claude/lumos-guard 的 SEAT_RE 同一條」
說明:既有外掛測試都是讀 register.ts 原始碼去檢查(例如 banned 清單),這支 S11 卻把 SEAT_RE 另寫一份,TS 端改了不會紅。做法上是範本檢查的獨立第二份真相。可改成從 register.ts 用正則抽出 SEAT_RE 的字面再比對。file: `scripts/test_lumos.py:72245`、`mods/claude/lumos-guard/hooks/register.ts:37`

## 3. 第二種做法(專案原本沒有的做法、或鄰居已有同功能卻自寫一份)

沒有 major。
- 持久化:鄰居用 $.fs 寫檔,guard 用 $.state 存對照表。兩者用途不同(一個寫 repo 事件、一個存會談內暫態,熱重載後讀回),且 guard 不寫檔,符合它「不寫檔」的自我約束與測試的 banned 規則,不算同功能重寫。file: `mods/claude/lumos-guard/hooks/register.ts:360`
- 子代理發起方判定:ledger 與 guard 都改用 parentAgentId,各自就地使用,沒有互相複製函式。
- Python 測試的 banned 清單在 ledger、context、guard 三支各有一份、內容略有出入:這是既有慣例(每支外掛各自一份),照做不算第二種做法。
- 既有測試 `t_install_registers_context_plugin` 改成「每支」「含」而非寫死清單,新增 `t_install_registers_guard_plugin` 只驗新增項,沒有重寫逐支邏輯。

總結:不對齊共 2 條,其中 major 0 條
