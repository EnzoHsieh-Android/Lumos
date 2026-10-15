severity: major

這份 diff 有 1 條 major 和 6 條 minor。我拿 `scripts/lumos` 的正規式和 `_stack_key_for_file` 逐一餵輸入驗證。另外在自己的 clone 對實作做了 11 個改壞實驗:10 個有測試翻紅,2 個沒翻(F1、F6)。F1 是 major,F6 是 minor。

## 圖譜固定席
- **lumos-cli-read(search 濾網合約)**:不影響,diff 沒碰 search。
- **測試假綠形態**:F1 就是「現場走不到被測分支」這一型。
- **design-loop / guard-kill / lifecycle / bound-tests-gate 的合約**:不影響,這份 diff 沒動到相關函式。
- **pitfalls-code-loop**:`.sh` 改歸 infra 鍵這條規則缺行為測試,見 F1。

## findings

1. `.sh` 一律歸 infra 的規則沒有任何測試守住
severity: major
   - blocking: 是
   - 位置:`_stack_key_for_file` 新增的 `if ext == "sh": return "infra"`。
   - 輸入:`scripts/deploy.sh`、`scripts/setup.sh` 這類檔名不含 e2e/seed/fixture 的 shell 腳本。
   - 預期:鍵是 infra,觸發 infra 檢核題。
   - 實際:我把這兩行刪掉再跑 `-k infra`、`-k e2e`、`-k disposition`、`-k stack`、`-k arch_alignment`、`-k pitfalls_diff`,共 25、43、112、188、6、60 個案例全綠。
   - 原因:會走到 `.sh` 規則的測試用的檔名都是 `scripts/e2e.sh`,這個檔名同時被 `_TEST_INFRA_PATH_RE` 的第二條規則撈到,所以拿掉第一條規則也照樣回 infra。S23 用 `scripts/deploy.sh`,但它只驗 claims,不驗棧別鍵。
   - 這條規則是本變更「本機基礎設施腳本」的核心行為,卻沒有任何測試守住。
   - 建議補一條:`_stack_key_for_file("scripts/setup.sh", d) == "infra"`。
   - 引句:「    if ext == "sh":」

2. `*_PORT=` 這類埠變數不會觸發 infra-shared
severity: minor
   - blocking: 否
   - 位置:`"when": [... _INFRA_B + r"PORT\s*=" ]`,`_INFRA_B` 的前一個字元不能是英數或底線。
   - 輸入:`E2E_PORT=5173`、`WEB_PORT=${WEB_PORT:-5173}`、`export BACKEND_PORT=8080`。
   - 預期:亮「埠會不會跟別份工作樹撞」那題。
   - 實際:`_stack_applicability` 對這三行都回空;單獨的 `PORT=5173` 才亮。
   - 腳本裡最常見的寫法反而不亮。
   - 引句:「_INFRA_B + r"PORT\s*="」

3. `xargs kill` 和 `process.kill` 不會觸發 infra-pid
severity: minor
   - blocking: 否
   - 位置:`_INFRA_CMD + r"(?:kill|pkill)"`,kill 必須在指令位置。
   - 輸入:`lsof -ti:3000 | xargs kill`、e2e 的 ts 裡的 `process.kill(pid)`。
   - 預期:亮「殺程序前有沒有確認 pid 是自己的」那題。
   - 實際:兩行都回空。
   - 這兩種寫法正是按埠殺程序和 teardown 殺子程序。
   - 引句:「"when": [_INFRA_CMD + r"(?:kill|pkill)" + _INFRA_E」

4. 前端字樣漏接版本號緊貼和英文 frontend
severity: minor
   - blocking: 否
   - 位置:`_REQ_FE_WHEN` 的 `(?![a-z0-9])` 詞界和字樣清單。
   - 輸入:「改用 Vue3」、「升級 React18」、「ReactJS 元件」、「Nuxt3」、「Vite5」、「frontend」、「front-end」。
   - 預期:命中前端字樣。
   - 實際:`_req_frontend_hit` 對這幾個都回 None。
   - 同一個函式對「react-query」、「The service will react to events」會命中,所以可以只指出漏接方向。
   - 這會讓三個入口(`--stage`、計劃模式、`--check`)一起漏掉前端面。
   - 引句:「r"|前端|瀏覽器")」

5. 「送出第二個請求」後面接「到」會漏掉,跟「送出請求到」不一致
severity: minor
   - blocking: 否
   - 位置:`_PITFALL_SEND_RE` 最後一支的 `送出(?!請求|表單|第[二兩2][個次]請求)`。
   - 輸入:「送出第二個請求到物流商」。
   - 預期:跟「送出請求到」一樣算對外送出。
   - 實際:門判定回 `[]`,「送出請求到」則回對外送出。
   - 同類漏接還有:「送出請求 POST 到外部」、「使用者請求送出補發通知」(沒有給/至/往,也沒有緊貼的到)。
   - 這是規則刻意往「少命中」走的代價;第二個請求的「到」是補不補的差別,可以順手補。
   - 引句:「送出(?=(?:請求|表單)到)」

6. PAYMENT 的參數尾碼只有一部分被測到
severity: minor
   - blocking: 否
   - 位置:`_PITFALL_PAYMENT_RE` 的尾碼清單 `TIMEOUT|TTL|SECONDS|SECS|SEC|MS|MINUTES|MINS|DELAY|INTERVAL|LIMIT|COUNT|RETRIES|WINDOW`。
   - 實驗:把 `TTL|SECONDS|SECS|SEC|MS|MINUTES|MINS|DELAY|INTERVAL` 刪掉,`-k caps_identifier_payment` 仍 4 個全綠(測試只用了 TIMEOUT 和 RETRY_COUNT)。
   - 另外,尾碼前面的中段 `(?:_[A-Z0-9]+)*` 沒有限制。`PAYMENT_AMOUNT_LIMIT`、`MAX_PAYMENT_AMOUNT_LIMIT`、`PAYMENT_ID_COUNT` 都被當成調整參數而不算金流。
   - 「金額上限」這類實際影響扣款的設定名會被判風險低。
   - 引句:「|LIMIT|COUNT|RETRIES|WINDOW))(?![A-Za-z0-9_]))")」

7. `pitfalls --check` 和門判定對全形標點的處理不一致
severity: minor
   - blocking: 否
   - 位置:`_PITFALL_SEND_RE` 的子句邊界 `[^,.;!?。、\n]` 依賴先做 NFKC,但 `_pitfall_scan_classes` 不做 NFKC。
   - 輸入:「表單送出後，畫面顯示給使用者」(全形逗號)。
   - 預期:兩條路徑結果一致,都不算對外送出。
   - 實際:門判定回 `[]`,`_pitfall_scan_classes` 回 `['external-send']`;半形逗號則兩邊都回空。
   - 方向是多命中,所以不會漏風險。
   - 但 S40 只測了 ASCII,沒有抓到這個差異,和註解「兩條路一起變」的說法不符。
   - 引句:「# 送出——同一子句(到下一個 , . ; ! ? 。 、 或行尾;掃描前已 NFKC,全形標點折成半形)後面寫了去處」

## 驗過沒問題的部分
- `_vendored_skip` 的集合只含原封不動的檔,`_arch_alignment_hints(skip=vend_skip)` 的 `relative_to(repo_root)` 路徑格式一致,拿掉 skip 會讓 S27 翻紅。
- 其餘改壞實驗都翻紅:
  - 拿掉 claims 的 infra 路徑跳過
  - 縮窄「第二個請求」
  - 拿掉 `到` 的分支
  - `[^…]` 改成 `.*`
  - 拿掉資料檔回 None 的分支
  - 拿掉前端面輸出
  - 拿掉 `--check` ✗ 路徑的前端提醒
- `_TEST_INFRA_PATH_RE` 對 `src/crypto/e2e.ts`、`reseed.sh`、`deploy.sh` 不誤判。對 `e2e/x.kt` 這類非程式副檔名回 None,是設計取捨。

最嚴重 severity: major,blocking 共 1 條(F1)。
