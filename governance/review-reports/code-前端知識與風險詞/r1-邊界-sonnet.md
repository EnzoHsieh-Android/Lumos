severity: minor

邊界與輸入鏡頭,逐條照實跑過。重現方式是用 `importlib` 載入工作樹的 `scripts/lumos`,呼叫 `_door_keyword_hits`、`_pitfall_scan_classes`、`_stack_key_for_file`、`_stack_applicability`,以及 CLI `pitfalls --stage 需求`。沒有找到 major。

1. 「送出」的去處「到」只認緊貼,中間隔一個名詞就漏判,把原本會判高的計劃放成風險低
severity: minor
   - blocking: 否
   - 輸入:`送出表單資料到外部客服系統`、`系統送出請求內容到第三方物流`
   - 預期:有明確外部去處,和 S35 的「送出表單資料給客服」同形,應該判對外送出。
   - 實際:`_pitfall_scan_classes` 回 `[]`,`_door_keyword_hits` 也回 `[]`。
   - 走到哪一行:第 1 條分支的 `[給至往]` 沒有「到」。第 2、3 條的 `到` 只接在「請求/表單」緊貼之後。第 4 條 `送出(?!請求|表單|…)` 在「送出」後面接請求或表單時直接放行。
   - 影響:S35 的標題寫「去處不緊貼、在同一句裡照算」,但測試只涵蓋給/至,沒有「到」。「到」是最常用的去處字,這條規則放行的就是它。
   - 相對照:`請求送出到` 會命中,`送出表單資料給客服` 也會命中。
   - 引句:「送出(?=[^,.;!?。、\n]*[給至往])|(?<=請求|表單)送出(?=到)|送出(?=(?:請求|表單)到)」

2. 前端字樣詞界把 `Vue3`、`React18`、`Nuxt3`、`nextjs` 排除
severity: minor
   - blocking: 否
   - 輸入:計劃寫「畫面改用 Vue3 與 Pinia。」
   - 預期:列出前端面。
   - 實際:`pitfalls --stage 需求` 數到 0 條 `req-fe-*`。把同一句改寫成「Vue 3」,就數到 2 條。
   - 原因:框架名後面接 `(?![a-z0-9])`,框架名緊貼版本號就不算。`vue3`、`react18`、`nuxt3`、`nextjs` 全部 `False`。
   - 測試缺口:S6 只測了大小寫與 `reactive`,沒有測緊貼版本號的寫法。
   - 引句:「|(?<![a-z0-9])(?:react|vue|svelte|angular|next\.js|nuxt|vite|solid-js|preact)(?![a-z0-9])」

3. PAYMENT 例外的尾碼太寬,把有金流語意的設定名一起放行
severity: minor
   - blocking: 否
   - 輸入:`PAYMENT_CHARGE_LIMIT`、`PAYMENT_GATEWAY_TIMEOUT`(都不命中金流)。S36 還明文把 `ORDER_PAYMENT_RETRY_COUNT` 列為不算。
   - 原因:中間的 `(?:_[A-Z0-9]+)*` 允許任意字,結尾的 `LIMIT|COUNT|RETRIES` 也算參數。
   - 實際:金流扣款的重試次數與額度上限,正是冪等與重複扣款要被追問的設定。
   - 反例:`PAYMENT_API_KEY`、`ENABLE_PAYMENT`、`PAYMENT_TIMEOUTX`、`payment_TIMEOUT` 仍照算,這部分正確。
   - 引句:「|LIMIT|COUNT|RETRIES|WINDOW))(?![A-Za-z0-9_]))」

4. 測試基礎設施路徑樣式把整個資料夾的非 shell 程式檔都改歸 infra 或 None,範圍比說明寬
severity: minor
   - blocking: 否
   - 輸入與實測:
     - `src/e2e/cipher.py` 回 `infra`(端對端加密模組放在 `e2e/` 資料夾)。
     - `lib/e2e/keys.kt`、`e2e/app/Main.kt`、`a/b.e2e.kt` 回 `None`,這些檔失去 kt 棧別題。
     - `scripts/prod-seed.sh` 命中路徑樣式,所以 `DELETE FROM` 這類產品型樣不掃。
   - 原因:說明只舉了 `src/crypto/e2e.ts` 這種檔名為例,S24 也只測檔名。資料夾恰好叫 `e2e/`、`fixtures/`、`seeds/` 時,不在 `_INFRA_CODE_EXTS` 裡的副檔名(kt、java、cs、swift、dart、vue)直接回 None。
   - 這會重現表態閘 r2 邊界席 B4 修過的「零覆蓋零稽核」。
   - 引句:「return "infra" if ext in _INFRA_CODE_EXTS else None」

5. infra-pid 的指令位置漏掉 `xargs kill`
severity: minor
   - blocking: 否
   - 輸入:`cat pidfile | xargs kill -9`
   - 預期:亮 infra-pid。
   - 實際:回 `[]`。`_INFRA_CMD` 的前導字不含 `xargs`,所以 `kill` 不在指令位置。這種寫法正是「從 pid 檔批次殺」,pid 被重用的風險最大。
   - 附帶:`TRAP=1`、`DATE=1` 這種變數名會誤亮 infra-signal 與 infra-portable。這個誤報方向安全,只是雜訊。
   - 引句:「_INFRA_CMD = r"(?:^|[;&|(`!{]|\$\(|(?<![A-Za-z0-9_])(?:if|then|do|else|elif|while|until|sudo|exec)\s)\s*"」

6. 已知的不完整,不另算 finding
   - 「點擊送出按鈕」仍判對外送出,只會多判高,方向安全。
   - 「網頁」、`Tailwind`、`Webpack` 不算前端字樣。

另外確認過幾項沒有問題:
- Windows 反斜線路徑不會出現,因為 diff 路徑是 POSIX。
- `e2easy/`、`fixtures.ts` 不誤中。
- 全形 PAYMENT、夾零寬字元、尾端句點、右括號的處理都保守或正確。
- 詞界 `(?-i:...)` 在 re.I 下行為正確。

圖譜固定席:這份 diff 沒碰 `search` 預設排除、guard kill 的 rc 優先序或 JSON 純度、re-inject 的 sentinel 範圍,所以這幾條合約不影響。`bound-tests-gate` 的新測試名要靠測試索引,檢查沒有懸空。`t_door_rule_version_pin` 與 `_DOOR_RULE_VERSION` 13 已一起 bump,pin 邏輯沒被繞過。`design-loop` 的處置閘不受影響,因為本次風險詞只會少判高,不改審材型別。

我在 `/tmp/lumos-seat-work/code-前端知識與風險詞/邊界-sonnet/` 的實驗檔已用字面絕對路徑刪除。

最嚴重 severity:minor,blocking 共 0 條。
