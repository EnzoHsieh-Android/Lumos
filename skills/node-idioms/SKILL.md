---
name: node-idioms
description: 寫或審 Node.js／TypeScript 後端（HTTP API、worker、排程）代碼前必讀——通用不變量層的慣例規則：並行等待與有界並行、不阻塞事件迴圈、floating promise、外呼逾時與取消、錯誤與程序生命週期、stream 與記憶體、邊界驗證。每條附壞例→好例與機檢對照（typescript-eslint／eslint-plugin-n／eslint-plugin-security）。框架選擇（Express vs Fastify vs Nest、Prisma vs Drizzle vs Knex、ESM vs CJS）不在此裁——查該專案圖譜。前端 TS（Vue）另有 vue-idioms。
---

# Node.js／TypeScript 後端慣例（通用不變量層）

**這份文件治的病**：AI 寫出「正確但笨」的 Node——串聯了本該 `Promise.all` 的查詢、`items.map(async …)` 無上限打爆連線池、`fs.readFileSync` 站在請求路徑上、promise 沒 await 讓例外無聲蒸發、外呼沒 timeout 把整個服務拖死、用請求 id 當 key 的快取永遠不清。這些不炸在單元測試上，炸在負載、在半夜、在事件迴圈 lag 飆到 500ms 的那一刻。

**分層原則**：只寫不隨框架選擇改變的原則。Express 還是 Fastify、哪個 ORM、ESM 還是 CJS——查該專案的知識圖譜與 CLAUDE.md（`lumos search <關鍵字>` 起手）。規則以「可注入」「可替換」等能力措辭，不點名框架。

**機檢欄說明**：`ts-eslint:規則名`＝typescript-eslint（⚠ 多數關鍵規則要 **type-aware** 設定：`recommendedTypeChecked` 加 `parserOptions.projectService`，沒接型別等於沒裝）；`n:規則名`＝eslint-plugin-n；`security:規則名`＝eslint-plugin-security；`自訂`＝可寫 ESLint 自訂規則或 ast-grep；`不可機檢`＝只有本文件與審查鏡頭能守——排最前面。

> **誠實邊界（2026-09-08）**：本文件是網搜＋官方文件整理，**尚未在任何真 Node 後端專案上實跑**；第一個接入的專案要把踩到的坑回填進來。

---

## 一、async 紀律（本文件存在的理由）

> **審查時機管道**：本文標「⚠ 不可機檢」的效能／適用性條目，其載重問已由 lumos 效能檢核機制在三時機自動推送（動手前 impact hook 注入／push 前 pitfalls advisory／終審 code-loop 鏡頭；內容源＝lumos-toolchain 圖譜 Systems/效能檢核目錄 Node 段，雙向同步義務；`pitfalls --diff` 靠 `package.json` 分前後端，不靠副檔名）——可機檢條目歸 ESLint，勿靠人記。

### R1. 互不依賴的等待必須並行 ⚠ 不可機檢，頭號條款
```ts
// ✗ 笨（延遲相加）
const user = await users.find(id);
const orders = await orders.byUser(id);

// ✓ 一起飛
const [user, orders] = await Promise.all([users.find(id), ordersRepo.byUser(id)]);
// 個別失敗不連坐、要每個結果 → Promise.allSettled
```
- 判斷順序：先確認無資料依賴，再確認無共享資源（同一個 transaction／同一條連線的查詢**不准**平行），才並行。
- 依據：[MDN Promise.all](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise/all)

### R2. `Promise.all` 不是佇列、不是限流器、不是連線池 ⚠ 不可機檢，生產最常炸
```ts
// ✗ 一萬筆同時開一萬個查詢 / HTTP 連線
await Promise.all(ids.map(id => fetchOne(id)));

// ✓ 有界並行（p-limit 之類，或自寫 worker 迴圈）
const limit = pLimit(10);
await Promise.all(ids.map(id => limit(() => fetchOne(id))));
```
- 集合大小不是你控制的（來自 DB／外部輸入）就一律有界；上限依下游（連線池／對方 rate limit）算，寫成常數並註明依據。
- 依據：[Node.js — Don't Block the Event Loop (or the Worker Pool)](https://nodejs.org/learn/asynchronous-work/dont-block-the-event-loop)

### R3. 沒有 floating promise：每個 promise 要嘛 `await`、要嘛明確 `void` 並處理錯誤
```ts
// ✗ 例外無聲蒸發；下一版 Node 未處理 rejection 直接砸 process
sendEmail(user);

// ✓
await sendEmail(user);
// ✓ 真的要 fire-and-forget：走佇列/背景工作，或至少接住
void sendEmail(user).catch(err => log.error({ err }, "email failed"));
```
- 機檢：`ts-eslint:no-floating-promises`、`ts-eslint:no-misused-promises`（async 函式塞進不等 promise 的回呼，例如 `forEach`／event handler）、`ts-eslint:require-await`。

### R4. 請求路徑上禁同步 IO 與 CPU 重活；重活離開事件迴圈
- `fs.*Sync`／`child_process.execSync`／同步 `crypto.pbkdf2Sync`／大 `JSON.parse`／大迴圈／回溯型正則，任一個在 handler 裡＝所有請求一起等。CPU 重活丟 `worker_threads`；大 JSON 走 stream parser 或限制 body 大小。
- 機檢：`n:no-sync`、`security:detect-unsafe-regex`；lag 監控：`perf_hooks.monitorEventLoopDelay`（10ms 好／100ms 壞／500ms 著火）。
- 依據：[Node.js — Don't Block the Event Loop](https://nodejs.org/learn/asynchronous-work/dont-block-the-event-loop)

### R5. 每個外呼都有逾時與取消；長連線要重用 ⚠ 不可機檢
```ts
// ✗ 對方掛了你也掛
const res = await fetch(url);

// ✓ AbortSignal.timeout；DB/HTTP client 單例 + keep-alive
const res = await fetch(url, { signal: AbortSignal.timeout(5_000) });
```
- 請求被客戶端中斷（`req.on("close")`／框架的 abort signal）要往下游傳，別讓已無人等的查詢繼續跑。
- 機檢：`自訂`（`fetch(`／`axios(` 呼叫無 `signal`）。

---

## 二、錯誤與程序生命週期

### R6. `unhandledRejection`／`uncaughtException` 只准「記錄→優雅關閉→退出」，不准「記一下繼續跑」
- 程序狀態已不可信；接下來靠 supervisor（systemd／k8s／pm2）重啟。handler 裡做的事：flush log、`server.close()`、`pool.end()`、`process.exit(1)`。
- 機檢：`自訂`（grep 這兩個事件的 handler 沒有 exit 路徑）。
- 依據：[Node.js process events](https://nodejs.org/api/process.html#event-uncaughtexception)

### R7. 優雅關閉是必備路徑：`SIGTERM` → 停收新請求 → 等在途完成 → 關連線池 → 退出
- 沒這條，每次部署都是一批 502 與半途交易。library 碼不准 `process.exit`（只有入口檔可以）。
- 機檢：`n:no-process-exit`。

### R8. 錯誤是值不是字串：throw `Error` 子類、帶 `cause`、邊界才轉 HTTP 狀態
```ts
// ✗
throw "not found";                       // 沒 stack、instanceof 失效
// ✓
class NotFound extends Error { constructor(what: string, opts?: { cause?: unknown }) { super(`${what} not found`, opts); this.name = "NotFound"; } }
```
- 領域錯誤 → HTTP 狀態的對映只在一處（error middleware／handler），內層不知道 HTTP。
- 機檢：`ts-eslint:only-throw-error`（舊名 no-throw-literal）、`ts-eslint:prefer-promise-reject-errors`。

---

## 三、資源與記憶體

### R9. 大資料走 stream，不整包進記憶體 ⚠ 不可機檢
- 檔案上傳／下載、匯出 CSV、轉送上游回應：`stream.pipeline`（會處理背壓與錯誤傳播），不用 `.pipe()` 裸串（錯誤不傳播、洩漏 fd）。DB 大結果集用 cursor／分頁。
- 依據：[Node.js stream.pipeline](https://nodejs.org/api/stream.html#streampipelinesource-transforms-destination-callback)

### R10. 長活集合有上限；請求範圍的狀態不放 module 全域 ⚠ 不可機檢
- module-level `Map`／陣列當快取＝沒有上限的洩漏；要快取就用有 LRU／TTL 的實作。每請求的上下文用 `AsyncLocalStorage` 或框架的 request 物件，不用全域變數（並發請求互相污染）。
- 機檢：`自訂`（module-level `new Map()` 被 handler 寫入）。

### R11. 連線池／client 單例、大小有依據
- DB pool、HTTP agent、Redis client 在程序生命週期建一次；pool 大小依實例數×每實例算，寫進設定並註明對方上限（太大壓垮 DB、太小排隊）。
- 機檢：`自訂`（handler 內 `new Pool(`／`createClient(`）。

---

## 四、邊界與型別

### R12. 外部輸入在邊界驗證後才進領域層；`unknown` 不是 `any`
```ts
// ✗ 把 req.body 直接當領域型別
const order = req.body as Order;
// ✓ schema 驗證（zod/valibot/ajv 之類，能力措辭：runtime schema）→ 得到窄型別
const order = OrderSchema.parse(req.body);
```
- 機檢：`ts-eslint:no-explicit-any`、`ts-eslint:no-unsafe-*` 家族（type-aware）；`tsc --noEmit` 的 `strict`＋`noUncheckedIndexedAccess`。

### R13. 秘密不進 log、不進錯誤訊息、不進 repo
- log 物件序列化前遮罩（token／密碼／卡號）；錯誤回應對外只給錯誤碼，stack 留 log。
- 機檢：`security:detect-*` 家族部分覆蓋；`自訂`（log 呼叫帶 `password`／`token` 欄位）。

### R14. 不可逆的外部動作（付款、寄信、刪資料）要冪等或有守衛
- 重試機制（client／佇列／k8s liveness）保證同一動作會再來一次：冪等 key、去重表、或明確「已做過」檢查，擇一並寫進節點的 `[guard:]`。
- 機檢：`不可機檢`；對應圖譜 ★IRREVERSIBLE★ 合約的 rollback／guard 要求。

---

### R15. 入口要有速率限制與同客戶並發上限 ⚠ 不可機檢
- 沒有限流，一個失控客戶（或重試風暴）就能把事件迴圈和連線池吃光，其他人一起等；限流放在最外層（反向代理或框架 middleware），按客戶／token 計，並對昂貴端點另設更低的上限。body 大小上限見 R4。
- 機檢：`不可機檢`（無 ESLint 規則）；`自訂`（入口檔沒掛 rate-limit middleware）。
- 依據：[OWASP Node.js Security Cheat Sheet — rate limiting](https://cheatsheetseries.owasp.org/cheatsheets/Nodejs_Security_Cheat_Sheet.html)、[nodebestpractices 6.2 Limit concurrent requests](https://github.com/goldbergyoni/nodebestpractices)

---

## 接線表（裝了不等於開了）

| 規則 | ESLint 規則 | 前提 | 動作 |
|---|---|---|---|
| R3 floating promise | `@typescript-eslint/no-floating-promises`、`no-misused-promises` | **type-aware**（`recommendedTypeChecked`＋`projectService`） | 升 error；沒接型別這兩條不會跑 |
| R4 同步 IO | `n/no-sync` | eslint-plugin-n | 對 `src/**` 開，`scripts/**` 可關 |
| R4 回溯正則 | `security/detect-unsafe-regex` | eslint-plugin-security | warning 即可（誤報多） |
| R7 process.exit | `n/no-process-exit` | eslint-plugin-n | 入口檔 `eslint-disable-next-line` 加理由 |
| R8 throw 非 Error | `@typescript-eslint/only-throw-error` | type-aware | 升 error |
| R12 any | `@typescript-eslint/no-explicit-any`、`no-unsafe-*` | type-aware | 逐步升 |
| 全部 | SARIF 進審查 | `@microsoft/eslint-formatter-sarif` | `eslint -f @microsoft/sarif -o <檔>` 登進 `.lumos/lint.json`；Biome 2.4+ 走 `--reporter=sarif` |

**依據總表**：[Node.js — Don't Block the Event Loop](https://nodejs.org/learn/asynchronous-work/dont-block-the-event-loop)、[Node.js process events](https://nodejs.org/api/process.html)、[Node.js stream.pipeline](https://nodejs.org/api/stream.html)、[typescript-eslint — Typed Linting](https://typescript-eslint.io/getting-started/typed-linting/)、[eslint-plugin-n](https://github.com/eslint-community/eslint-plugin-n)、[@microsoft/eslint-formatter-sarif](https://www.npmjs.com/package/@microsoft/eslint-formatter-sarif)。
