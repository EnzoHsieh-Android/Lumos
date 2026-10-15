severity: major

我的立場是替極端輸入發聲。判定的依據是在修前版 `d2297c94`(`lumos_before`)與修後版 `f14f6808` 上各跑同一批輸入。腳本與輸出在 `/tmp/lumos-seat-work/code-前端知識與風險詞/邊界-sonnet/`(e2~e8.py、before/after 輸出檔),變異實驗副本在同目錄的 `mut/`。

## 發現

### 1. 「前後 80 字」的上限沒有任何測試守著
severity: major
blocking: 是
- 位置:`_PITFALL_SEND_CLAUSE` 的 `{0,80}?`,以及 S45~S47 三支測試。
- 重現:把 `mut/scripts/lumos` 的 80 改成 10,跑 `python3.14 mut/scripts/test_lumos.py -k door_keyword_send`,結果 42 passed、0 failed。改成 3 才開始紅。
- 原因:照算例句裡送出和去處最遠隔約 9 字,沒有一條在 80 附近。
- 後果:上限被誤改成 10,「系統將彙整後的訂單資料與發票明細一併送出請求內容到第三方物流」這種稍長的真對外送出會悄悄漏判,測試照綠。
- 邊界本身我用實例驗過:送出後正好 80 字再接「給客戶」會命中,81 字不命中,行為符合設計。缺的是測試。
- 歸因:有證據的修復回歸。80 字上限是這輪新加的,修前版沒有上限,上限沒有測試是這輪新缺的。
- 引句:「_PITFALL_SEND_CLAUSE = r"[^,.;:!?。、，；：！？\n]{0,80}?"」

### 2. e2e 路徑規則的 src/lib 排除看整條路徑,把 `e2e/lib/`、`e2e/src/` 底下的 e2e 輔助檔也排掉了
severity: major
blocking: 是
- 位置:`_TEST_INFRA_PATH_RE` 的 `^(?!(?:[^/]+/)*?(?:src|lib)/)`。
- 計劃文字:「路徑裡有一段資料夾恰好是 e2e,而且不在 src/、lib/ 底下」。依這句,`e2e/lib/x.ts` 應算 infra。
- 實際行為:先行斷言從開頭掃整條路徑,連 e2e 後面的 `lib/`、`src/` 也算,文件與程式對不上。
- 輸入對照(修前 → 修後):

| 路徑 | 修前 | 修後 |
|---|---|---|
| `e2e/lib/x.ts` | infra | None |
| `e2e/src/x.ts` | infra | None |
| `tests/e2e/src/x.ts` | infra | None |
| `e2e/src/lib/x.ts` | infra | None |

- 後果:這些檔沒有 infra 題,而且 claims 迴圈的跳過也不再生效,產品型樣會掃進 e2e 輔助程式,分級可能被抬高。
- 測試缺口:S50 與 `t_test_infra_path_tightened` 只測 `src/e2e/…`(e2e 在 src 底下),沒有「src/lib 在 e2e 底下」的反例。
- 歸因:有證據的修復回歸。命令是 `python3.14 e3.py <兩版 lumos>`,上表即結果。
- 引句:「_TEST_INFRA_PATH_RE = re.compile(r"^(?!(?:[^/]+/)*?(?:src|lib)/)(?:[^/]+/)*?e2e/|\.e2e\.|」

### 3. 「到」的黑名單與新增的「向、對」把前端日常句子判成對外送出
severity: minor
blocking: 否
- 位置:`(?<![收拿做直等遇得想看找達])到` 與去處字 `[給至往向對予]`。
- 以下輸入修前版全部不命中,修後版全部判「對外送出」:
  - 「請求送出後收不到回應時顯示逾時」
  - 「表單送出後使用者看不到結果」
  - 「請求送出後等不到回應就重試」
  - 「表單送出後使用者會受到提示」
  - 「在表單送出前對欄位做驗證」
  - 「請求送出期間向使用者顯示載入中」
  - 「表單送出後畫面捲動到錯誤欄位」
  - 「表單送出後對話框關閉」
- 這些正是這份計劃要放行的前端語境(逾時、載入中、驗證)。黑名單只列單字(`看`、`收`),「看不到、收不到、受到、接到、考慮到」都漏。
- 方向是多判高,所以不算危險。但例外在這些句子上失效,S45 的對照組只有三句。
- 歸因:有證據的修復回歸。命令是 `python3.14 e6.py <兩版>`。
- 引句:「(?<![收拿做直等遇得想看找達])到))」

### 4. 「去處寫在前面也算」被網址、主機名、小數點的 `.` 切斷
severity: minor
blocking: 否
- 輸入:「向 api.vendor.com 送出請求」「對 https://api.vendor.com/orders 送出請求」。
- 兩版都不命中對外送出,`pitfalls --check` 也是空。
- 計劃寫「有去處就照算,不論去處寫在送出前面還是後面」,被 `.` 當子句邊界破功。天花板那節只列了「去處在下一個子句」,沒列這種寫法。
- 歸因:有證據的原有漏查,兩版結果相同,不是這輪造成。
- 引句:「有去處就照算,不論去處寫在送出前面還是後面」

### 5. 門先 NFKC、`pitfalls --check` 不 NFKC,「兩種標點都列才一致」的宣稱不成立
severity: minor
blocking: 否
- NFKC 後會折成邊界、但不在類別裡的字有 27 個碼位,包括 `…`、`‥`、`｡`、`､`、`﹐`、`︔`、`﹕`、`︓`。
- 「表單送出……給客戶」:門回空,`pitfalls --check` 回 external-send,兩條路結論不同。
- S46 只測了全形逗號。
- 歸因:有證據的原有漏查。修前版同樣不一致,這輪宣稱「一致」但沒做到。
- 引句:「門先 NFKC、pitfalls --check 不 NFKC,兩種標點都列才一致)」

### 6. `xargs` 帶「有參數的選項」、以及 `child.kill()`、`os.kill(`、`process.kill (` 都沒亮
severity: minor
blocking: 否
- 修補只認 `(?:-\S+\s+)*`,選項後面再接一個值就斷了。這些輸入 infra-pid 與 infra-signal 都不亮:
  - `xargs -n 1 kill`
  - `xargs -I {} kill {}`
  - `xargs -P 4 kill`
  - `xargs -L 1 kill`
  - `xargs -r -- kill`
- `process.kill (pid)`(有空格)、`child.kill()`、`os.kill(pid, 9)` 也不亮。`.py` 是 `_INFRA_CODE_EXTS` 的成員,`os.kill` 是它的對應寫法。
- 有亮的:`xargs -r kill`、`-n1`、`-I{}`、`-0`、`xargs pkill`、`this.process.kill(`。
- 測試 S51 只用 `xargs kill` 與 `xargs kill -9`,沒有帶值選項的例子。
- 歸因:兩版都不亮,是原有漏查。修補只收了緊貼寫法,未判定它是否算修補漏洞。
- 引句:「(?<![A-Za-z0-9_])xargs\s+(?:-\S+\s+)*)\s*"」

### 7. `SvelteKit`、`sveltekit` 不算前端字樣
severity: minor
blocking: 否
- `(?![a-z])` 讓 `SvelteKit` 被後面的 `K` 擋掉(`re.I` 下 `K` 算 `[a-z]`)。
- `_NODE_FRONTEND_MARKERS` 有 `svelte`,但 S53 只測 marker 本身,沒測由它衍生的常見散文寫法。
- 歸因:有證據的原有漏查,兩版都是 None。
- 引句:「|front-?end|前端|瀏覽器")」

## 已驗且未發現問題
- 版本號緊貼(Vue3、React18、Nuxt3、Vite5、Next.js14、Preact10、Angular2):全部命中。`reactive`、`Reactor`、`Preactor`、`VueUse` 仍不命中。
- PAYMENT 尾碼:
  - 不算金流的有 `PAYMENT_TIMEOUT`、`_MS`、`_SECONDS`、`PAYMENT_MAX_RETRIES`、`ORDER_PAYMENT_RETRY_COUNT`。
  - 照算金流的有 `PAYMENT_TIMEOUT_KEY`、`_MS_X`、`PAYMENT_LIMIT`、`PAYMENT_GATEWAY_TIMEOUT`、`STRIPE_PAYMENT_TIMEOUT`、`payment_timeout`、`Payment_TIMEOUT`、`PAYMENT_RETRY_LIMIT`、`PAYMENT_TTL_HOURS`。
- 邊界輸入:
  - 全形空白、中間夾空格、大小寫混用(Partner、EXTERNAL)全部正確。
  - `MY_E2E_PORT=`、`E2E_PORT=`、`export BACKEND_PORT=` 命中。
  - `REPORT=`、`EXPORT=`、`SUPPORT=`、`PASSPORT=` 不命中。
- 效能:二十萬字單行(重複「給」、重複「請求送出」、重複「客戶」、重複 `PAYMENT_`)都在 1 秒內,線性。
- 路徑:`.e2e.` 檔名、`my_e2e.sh`、`run-e2e.sh`、`src/crypto/e2e.ts`(非 infra)、`db/seeds/x.sql`(sql)、`e2e/fixtures/data.json`(None)都符合設計。

## 三問
1. 原問題的修復效果:
   - 向、對、予、前置去處、外部、第三方、partner 等 r1 提的漏判都已補上,修前不命中、修後命中(`e2.py` 與 `e8.py` 的 diff)。
   - `E2E_PORT=`、`xargs kill`、`process.kill(` 與版本號緊貼確實生效。
   - 效果的上限見第 1、4、6、7 條。
2. 修補處的正常、錯誤與相鄰路徑:
   - 並非全部成立。第 2 條(`e2e/lib`、`e2e/src`)與第 3 條(前端日常句被判對外送出)是修補造成的新退步。
   - `e2e/main.kt`、`e2e/A.java` 現在拿到 kt、java 棧題,但 claims 迴圈仍整支跳過(它只看路徑),兩邊不對稱。沒有找到具體的壞輸入,所以只列為觀察,不算 finding。
3. 新發現同一案例在修前與修後:第 2、3 條是修前 infra 或不命中、修後 None 或命中,有證據的回歸。第 4~7 條兩版相同,是原有漏查。第 1 條屬於修補新增的上限沒有測試。

最嚴重 severity:major。blocking 共 2 條(第 1、2 條)。

臨時目錄 `/tmp/lumos-seat-work/code-前端知識與風險詞/邊界-sonnet/` 我沒有刪,請編排者收貨後照規定刪。
