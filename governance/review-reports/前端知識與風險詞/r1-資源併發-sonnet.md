severity: major

# 前端知識與風險詞 r1 資源併發-sonnet 審查報告

白話:這份計劃新加的檢查在速度和記憶體上沒有問題,我拿大輸入實測過。問題在 infra 題組的觸發寫法。照 spec 方向實作會漏掉最常見的寫法(寫在引號裡的 `/tmp/`),又會被太普通的詞(`wait`、`date`、`cd `)打亮。d2 又把這組題接進推送閘。

實驗用的暫存目錄 `/tmp/lumos-seat-work/前端知識與風險詞/資源併發-sonnet/` 已刪。我沒有改工作樹。

## 風險類

- **守衛面**:碰到,見 F1、F2、F3、F4。
- **舊資料與舊帳**:本鏡頭無。門規則版本升 13 讓舊留痕重數,屬回滾鏡頭的範圍。
- **已在途分支**:本鏡頭無,理由同上。
- **跟其他會談或計劃的交界**:本鏡頭無。`_stack_key_for_file` 的順序規則 spec 已經寫明。
- **併發與子程序**:無。spec 沒有新增任何子程序或執行緒。`_arch_alignment_hints` 只有一個呼叫端(`_pitfall_diff_collect`),`vend_skip` 在那裡已經算好,多傳一個參數不會多跑 git。

## 各節資源與效能核對(已讀,無 finding)

- 做法 9 兩個新詞表正規式,實測如下:

  | 測試 | 結果 |
  |---|---|
  | `_door_keyword_hits` 掃 20 萬行(約 90 字一行) | 基準 16.34s、新版 16.71s,多約 2%(基準本身慢,來自既有的 `_door_scan_text`,不是這次新加的) |
  | `_pitfall_scan_classes` 那條路,540 萬字整段文字 | 新「送出」式約 0.18s、新「payment」式約 0.03s |
  | 單行 400 萬字、單行 700 萬字的 `ORDER_PAYMENT_` | 都在 0.05s 內,沒有災難性回溯 |
  | 試算例 `ORDER_PAYMENT_TIMEOUT`、`order_PAYMENT`、`PAYMENT_TIMEOUT` | 不命中 |
  | 試算例 `payment_service`、`Payment_Gateway`、單獨 `PAYMENT` | 命中 |
  | 試算例「請求送出時刻記錄」「當送出表單」「再按也不會送出第二個請求」 | 不命中 |
  | 試算例「送出請求到外部物流 API」「系統會送出通知給客戶」「把表單送出給第三方」 | 命中 |

  結論:兩個正規式的效能影響可以忽略。
- 做法 7 的 `_TEST_INFRA_PATH_RE`:對 20 萬字路徑跑 0.009s,spec 列的例子全部判對(`e2easy.ts` 與 `fixture.ts` 不算,其餘都算)。
- 做法 7 的鄰居排除:`vend_skip` 傳進去即可,可行。

## 逐條 finding

### F1 引號裡的 `/tmp/`、localhost:埠號 觸發不到,infra-shared 對最常見寫法失明
spec 段落:做法 6 的題庫表(infra-shared、infra-pid 的「觸發寫法(方向)」欄)、S12。

問題:棧別觸發比對前會先用 `_stack_norm_line` 把字串字面剝成 `""`。只有另外宣告 `when_raw` 的題才看字串內容。spec 的 infra 表只說 `when`,沒提 `when_raw`。shell 與 e2e 腳本裡的 `/tmp/…`、`http://localhost:5173`、`.pid` 檔名,實務上多半寫在引號裡。

具體例(我把 spec 表的六題 `when` 原樣塞進 `_stack_applicability` 實測):
- `LOCK_FILE="/tmp/e2e.lock"` → 沒有任何題亮。這正是緣起段 r1 的「/tmp 鎖與狀態檔」。
- `curl -sf "http://localhost:5173/health"` → 只亮 infra-timeout,infra-shared 沒亮。
- S12 的 `/tmp/` 如果寫成未加引號的 `X=/tmp/a` 測試會綠,真實腳本卻抓不到。

引句:「`infra-shared` | 埠、容器名、compose 專案名、/tmp 底下的檔與鎖,會不會跟另一份工作樹或另一次執行撞?」

佐證:``file: `scripts/lumos:30503` `` 的 `_stack_norm_line` 在 `keep_strings=False` 時先剝字串;``file: `scripts/lumos:30529` `` 的 `pats_raw` 才是看字串的路。

severity: major
blocking: 是
判準:照字面實作會讓這個題組的核心案例(/tmp 鎖、埠)在引號寫法下不被問,實作者會做出抓不到動機事故的守衛。

### F2 觸發詞不帶詞界,太普通的詞讓幾乎每個 `.sh` 與 async TS 行都亮,d2 又把它們接進推送閘
spec 段落:做法 6 的觸發欄(`wait`、`date`、`ps `、`stat `、`cd `、`until`),加上〈實務隱患〉守衛面的「題目 when 只收具體寫法,不是改到 .sh 就整組亮」。

問題:觸發比對用 `re.I`,沒有詞界。
- `wait` 命中 `await`。
- `date` 命中 `updated`、`candidate`。
- `ps ` 命中 `https `、`steps `。
- `cd ` 命中任何以 `cd` 結尾的字。

具體例(同樣的實測):
- `await fetch('http://localhost:3000/health')` → infra-signal 亮(因為 `await`)。
- `echo updated` → infra-portable 亮。
- 最普通的 `cd "$ROOT"` 加上 `VERSION=$(date +%s)` → infra-path 與 infra-portable 亮。
- 工具鏈本 repo 有 20 支 `.sh`(`get.sh`、`governance/*.sh`),改任何一支幾乎必亮至少兩題。d2 讓這等於每次都要表態才推得出去,跟 spec 自己說的「不是改到 .sh 就整組亮」相反。

引句:「題目 when 只收具體寫法,不是改到 `.sh` 就整組亮(超過行數門檻時照既有規則整組亮)。」

severity: major
blocking: 是
判準:照 spec 列的詞原樣寫成正規式,會做出幾乎每支 `.sh` 都亮的閘,而 spec 明講要避免這件事,所以實作者會在不知道的情況下違反設計意圖。

### F3 S11 的預期結果有兩種讀法,而且 `fetch(` 沒有任何 infra 逾時觸發
spec 段落:S11、做法 6 的 infra-timeout。

問題:S11 要求「適用題應不含 vue-reactive、應改列 infra 題組」。「列」可以是 `stack_questions`(命中棧整組)或 `stack_questions_applicable`(只列適用)。infra-timeout 的觸發只有 `curl`、`wget`、`docker`、`psql`、`mysql`、`gradlew`、`until`、`sleep`,`fetch(` 沒有。

具體例:
- `e2e/global-setup.ts` 新增 `await fetch(…)` 輪詢、沒有 `AbortSignal.timeout`。
- 實測 applicable 只亮 infra-signal(而且是被 `await` 誤中),沒有任何逾時題。
- 緣起段 r3「健康檢查沒逾時」在 TS 側仍然沒人問。
- S11 用整組判斷會綠,用 applicable 判斷會看到問錯題。

引句:「[S11] 當 diff 只改到前端 package.json 底下的 `e2e/global-setup.ts`、新增行有 `fetch(` 時,適用題應不含 vue-reactive、應改列 infra 題組。」

severity: minor
blocking: 否
判準:實作者會在 S11 的測法上猜錯,但不會做出壞系統;缺的 `fetch(` 觸發在實作時補一個詞就能收掉。

### F4 infra 桶吃進所有副檔名的資料檔,行數門檻混算,輸出也被文件檔污染
spec 段落:做法 6 的 `_stack_key_for_file` 第一條規則、做法 7 的路徑樣式。

問題:`fixtures/`、`seeds/`、名字帶 `e2e` 的檔不論副檔名一律回 `infra`。三個後果:
1. `pitfalls --diff` 的 `stack_questions` 迴圈在跑 `_stack_changed_ok` 之前,對 `added` 裡的每個檔都會呼叫 `_stack_key_for_file`,連 `.md`、圖片也算。實測 `docs/spec-e2e.md` 判成 infra,輸出多印「[infra 效能檢核]」六題,即使它不會進表態閘。
2. 表態閘的行數門檻(預設 300,``file: `scripts/lumos:30470` ``)是同一棧所有檔的增刪行加總。400 行的 `seeds/*.sql`、`e2e/fixtures/*.ts` 資料檔,單獨或加上小腳本,就讓六題 infra 全亮。這些題問的是 pid、trap、路徑實體化,對資料檔沒有意義。
3. 可能撞的候選會讀 infra 檔的鄰居,每個鄰居上限 2MB。實測 2MB 的 yaml 讀加正規化約 0.19s,最壞 20 個檔乘 3 個鄰居約 11s。以前這類 `.yaml`、`.xml`、`.tsv` 的 fixtures 沒有題組鍵,根本不進這條路。有上限所以不會爆,只是推送前閘多出一段可預期的時間。

引句:「符合這個樣式的檔:①棧別鍵一律 `infra`(做法 6),不再拿 vue-reactive、sql-transaction 這類產品題;」

severity: minor
blocking: 否
判準:行為是雜訊與耗時,不會讓守衛放行該擋的,實作者照字面做也不會崩。

### F5 S28 與 2027-01-15 的 REVISIT 依賴的比對腳本沒有存在任何地方
spec 段落:S28、REVISIT 的第三行、做法 9 的量法。

問題:S28 寫「重跑 2026-10-15 那支唯讀比對腳本」,REVISIT 寫「對所有消費專案重跑一次詞表新舊比對(做法 9 的量法)」。但 repo 裡找不到這支腳本:`scripts/`、`governance/` 都沒有,spec 也沒說放哪、怎麼取三個消費專案的路徑。做法 9 的量法只有一句描述。

具體例:2027-01-15 到期時接手的人沒有可以跑的東西,得照一句話重寫。重寫時口徑(取第一個命中、逐行比(行, 類)、「整份再無其他命中」)很容易跟這次不同,數字就不可比。這是「純散文的回頭條件」。

引句:「[manual: 重跑 2026-10-15 那支唯讀比對腳本(對本 repo 與三個消費專案的 Projects),輸出「該類在整份再無其他命中」的行數應為 0]」

severity: minor
blocking: 否
判準:不影響本次實作做出什麼,影響的是未來回頭檢查能不能執行。

最嚴重 severity:major;blocking 共 2 條(F1、F2)。
