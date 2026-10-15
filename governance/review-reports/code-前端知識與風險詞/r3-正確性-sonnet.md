severity: minor

審查範圍:修後版本 20df2187 對修前版本 f14f6808。我讀了 r3-repair-code.patch 全文,並在 `/tmp/lumos-seat-work/code-前端知識與風險詞/正確性-sonnet/` 用修前、修後兩版 `scripts/lumos` 逐輸入對照。沒有 blocker 或 major;共 4 條 minor,都不擋。

## Findings

1. 全形句點、全形冒號後面緊接英數時,門與 `pitfalls --check` 兩條路結論不一致
severity: minor
   - blocking: 否
   - 問題:URL 例外 `[.:](?=[A-Za-z0-9/])` 只對 ASCII 的 `.` 和 `:` 成立。門先 NFKC,所以全形的 `．`、`：` 會變成 ASCII 後套用例外而不切子句。`--check` 不 NFKC,全形字仍當邊界,所以兩條路分歧。測試 `t_door_keyword_send_nfkc_stops_both_paths` 只驗邊界字表,而且三個行為例子後面接的都是中文,沒碰到這條。
   - 具體例:輸入 `表單送出請求：Partner API`
     - 修後:門 True,`--check` False
     - 修前:兩條路都 False
     - 輸入 `表單送出請求．external`:修後門 True、`--check` False;修前反過來,門 False、`--check` True。
   - 影響:方向是 `--check` 比門低,所以漏的是 `--check` 那邊,不是門。
   - 歸因:有證據的修復回歸。URL 例外是這輪新加的;修前門在這兩個輸入都是 False。
   - 兩版查證命令與結果:兩版載入同一個小腳本,分別呼叫 `_door_keyword_hits` 與 `_pitfall_scan_classes`,結果如上(`t6.py`)。
   - 引句:「r"]|[.:](?=[A-Za-z0-9/])){0,80}?"」

2. 去處詞表收窄後,常見的對外去處名詞整句判低
severity: minor
⚠ 這是 r2 編排者明裁的取捨,所以不升級
   - blocking: 否
   - 具體例(都沒有別的風險詞兜底):

   | 輸入 | 修前 | 修後 |
   |---|---|---|
   | `表單送出請求到合作夥伴系統` | True | False |
   | `表單送出請求到對方伺服器` | True | False |
   | `表單送出請求至平台` | True | False |
   | `請求送出到雲端服務商` | True | False |
   | `請求送出至 Salesforce` | True | False |
   | `表單送出請求至 CRM` | True | False |
   | `送出表單至 HubSpot` | True | False |
   | `表單送出 PII 到分析平台` | True | False |

   - 差別:「外部」、「第三方」、「給」、`partner` 這類詞仍照算,只有詞表外的名詞掉了。大小寫(`PARTNER`、`Partner`)和「客戶端與客戶」的邊界判得正確。
   - 歸因:有證據的修復回歸。修前靠「至 往 向 對 到」命中,修後移除。這是有意取捨,我只報告實際漏掉的範圍。
   - 引句:「r"(?:給|外部|第三方|客戶(?!端)|廠商|供應商|銀行|物流|平台方|partner|vendor|external)"」

3. e2e 資料夾底下非 sh/py/ts/js 家族的檔,現在會產生產品型樣 claims
severity: minor
   - blocking: 否
   - 問題:修前 claims 掃描只看 `_TEST_INFRA_PATH_RE`。修後多了副檔名門檻,副檔名不在 `_INFRA_CODE_EXTS` 的 e2e 檔都不再跳過。
   - 具體例:新增 `e2e/seed.sql`、`e2e/db/schema.sql`、`e2e/helper.go`、`app/x.e2e.sql`。用 `_pitfall_diff_collect('HEAD~1..HEAD')` 對照:
     - 修前 claims 檔案只有 `src/e2e/x.ts`
     - 修後多出 `e2e/app/Main.kt`、`e2e/db/schema.sql`、`e2e/helper.go`、`e2e/seed.sql`、`app/x.e2e.sql`
   - 說明:`.kt` 是作者有意(r2 通3),測試 `t_test_infra_path_e2e_inner_lib_src` 也守住。但 `.sql`、`.go` 這種 e2e 測試資料現在也出 DELETE/UPDATE claims,這只會讓提示變多,不會漏。
   - 歸因:有證據的修復回歸,但屬假陽性方向。
   - 引句:「return Path(file_rel).suffix.lstrip(".").lower() in _INFRA_CODE_EXTS and bool(_TEST_INFRA_PATH_RE.search(file_rel))」

4. SvelteKit 的套件名 `@sveltejs/kit` 仍不算前端字樣
severity: minor
   - blocking: 否
   - 具體例:`_req_frontend_hit("@sveltejs/kit 路由")` 回 None。
   - 對照:`SvelteKit`、`sveltekit`、`svelte-kit`、`Svelte Kit` 都是 True。
   - 原因:`svelte` 後面緊接 `j`,被 `(?![a-z])` 擋掉。
   - 歸因:有證據的原有漏查。修前 `@sveltejs/kit` 同樣不中,這輪只補了 `SvelteKit` 拼法。
   - 引句:「r"|(?<![a-z0-9])(?:react(?:js)?|vue(?:js)?|svelte(?:kit)?|angular(?:js)?|next\.?js|nuxt|vite|solid-?js|preact)(?![a-z])"」

## 已驗無問題

- **80 字邊界**:前面、後面各 80 字會算、81 字不算,測試能抓。我把 `{0,80}` 想成 `{0,81}`,`t_door_keyword_send_clause_window_80` 的 ② 會翻紅。
- **去處詞表**:每個詞各自必要,測試 ④ 是集合相等檢查。「客戶端送出請求」不算,「客戶端與客戶」照算。
- **網址例外**:`向 api.vendor.com 送出請求` 和 `https://…` 都照算,修前 `api.partner.io` 漏掉,現在補回。
- **子句邊界表**:`t_door_keyword_send_nfkc_stops_both_paths` 跑通,表等於 BMP 內 NFKC 後含基本邊界字的全部碼位。BMP 之外的 🄀(NFKC 後成 `0.`)讓 `--check` 比門多算,是保守方向。
- **`_is_test_infra_file` 呼叫者**:共 2 處,`_stack_key_for_file` 與 `_pitfall_diff_collect`。棧別鍵的語意與修前恆等;只有 claims 掃描的行為變了,見第 3 條。
- **e2e 排除樣式**:`e2e/lib/x.ts`、`e2e/src/x.ts`、`tests/e2e/lib/util.ts` 都是 infra;`src/e2e/cipher.py`、`packages/x/lib/e2e/a.ts` 不是 infra。
- **xargs 前綴與 `.kill(`**:`-0`、`-n1`、`-I{} -P4`、`-r`、`-d '\n'`、`--no-run-if-empty` 都命中。以 2 萬個選項、2 萬個空白、2 萬個分號壓測,最慢 0.01 秒。
- **測試**:跑了 `-k door_keyword_send`(85)、`test_infra`(19)、`infra_`(51)、`sveltekit`(2)、`req_fe_when`(8)、`door_rule_version`、`door_scan`(239),全過。

## 三問回答

1. **原問題的修復效果有行為證據嗎?** 有。
   - **網址主機名**:`向 api.partner.io 送出請求` 修前 False,修後 True。
   - **前端日常句**:`表單送出後顯示對應的結果`、`導向首頁` 等 14 句不再誤算,由 `t_door_keyword_send_frontend_everyday_not_hit` 守住,我手動跑過。
   - **e2e 內層 `lib/`、`src/`**:修後仍是 infra,見上方「已驗無問題」。
   - **xargs**:帶參數的選項現在能命中 `kill`,見上方。
2. **修補處的正常、錯誤與相鄰呼叫路徑仍成立嗎?** 大致成立。
   - 相鄰路徑出現 3 個偏差:第 1 條(門與 `--check` 分歧)、第 3 條(claims 範圍變寬)、第 2 條(收窄使部分真對外送出判低)。
   - 沒發現例外或 None 路徑問題,也沒有效能退化。
3. **新發現的同一案例修前、修後各是什麼結果?** 已逐條附在各 finding 內。

## 未驗範圍

- 沒有在 `pitfalls --diff` 的完整命令列端到端跑過。
- 沒跑全套測試,依規定留給推送前的閘。
- 沒查 `--check` 比門低的後續下游影響。

最嚴重 severity:minor;blocking 共 0 條。
