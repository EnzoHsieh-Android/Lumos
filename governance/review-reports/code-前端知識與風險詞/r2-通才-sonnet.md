severity: major

審的是修後版本 f14f6808,以 `scripts/lumos` 與 `scripts/test_lumos.py` 的實跑為準。實驗檔放在 `/tmp/lumos-seat-work/code-前端知識與風險詞/通才-sonnet/`。

**1. e2e 路徑的 src/lib 排除會一路掃到路徑尾端,把 e2e 底下自己的 lib、src 子資料夾也踢出 infra**

severity: major
blocking: 是

- **問題**:`_TEST_INFRA_PATH_RE` 開頭的 `^(?!(?:[^/]+/)*?(?:src|lib)/)` 會在整條路徑上找 `src/`、`lib/`。它找的是路徑中任何位置,不是「e2e 之前」。所以 `e2e/lib/…`、`e2e/src/…` 這類 e2e 自己的輔助碼資料夾也被當成產品程式。
- **輸入與結果**:
  - `e2e/lib/utils.ts` 與 `apps/web/e2e/src/helpers.ts`:`_stack_key_for_file` 回 None。這兩個路徑修前的正則都比得到(實測 True),現在比不到。
  - `e2e/lib/x.py`:回 `py`,不是 `infra`。
  - 在暫存 repo 的 `pitfalls --diff --json` 裡,`e2e/lib/h.ts` 內有 `await db.query('DELETE FROM users…')` 和迴圈,產生了 `('e2e/lib/h.ts','併發')` 的 claim。
- **預期與實際**:註解寫「只排除 e2e 在 src/lib 底下」。預期是 e2e 底下的 lib 還是 infra,不產生產品型樣 claim;實際相反。
- **歸因**:有證據的修復回歸。修前正則 `(?:^|/)(?:e2e|fixtures?|seeds?)/` 對這兩條路徑為 True,修後 `_stack_key_for_file` 回 None 或 `py`。
- **測試缺口**:`t_test_infra_path_tightened` 只測 `src/e2e/…`、`lib/e2e/…`,沒測 `e2e/lib/…`、`e2e/src/…`。把前置排除改成只看 e2e 之前的段落也能全綠。
- **改法**:把排除限定在 e2e 之前,例如 `^(?!(?:[^/]+/)*?(?:src|lib)/(?:[^/]+/)*?e2e/)`。

引句:「_TEST_INFRA_PATH_RE = re.compile(r"^(?!(?:[^/]+/)*?(?:src|lib)/)(?:[^/]+/)*?e2e/|\.e2e\.|(?:^|/)(?:[^/]*[._-])?e2e(?:[._-][^/]*)?\.sh$", re.I)」

**2. 「送出」的去處字太寬,前端常見句仍被判成對外送出,例外收窄過頭**

severity: major
blocking: 是

- **問題**:`_PITFALL_SEND_DEST` 把單字「對」「向」「至」與「到」(只排除收拿做直等遇得想看找達前綴)都當去處。「對應」「對欄位」「導向」「至少」都含這些字。
- **輸入與結果**:`_door_keyword_hits` 實測都回「對外送出」:

  | 輸入 | 命中原因 |
  |---|---|
  | `表單送出後顯示對應的結果` | 對 |
  | `請求送出後對使用者顯示錯誤` | 對 |
  | `送出前先對輸入做驗證` | 對 |
  | `表單送出後導向首頁,對使用者顯示成功` | 導向的「向」 |
  | `form 送出後向後端確認` | 向 |
  | `表單送出後跳到成功頁` | 跳到 |
  | `按鈕送出後回到列表` | 回到 |
  | `請求送出後滾到頂端` | 滾到 |

- **後果**:舊版「到」只認緊貼 `送出到`。新版放寬成同子句任意位置,再用不完整的黑名單排除,導航類動詞(跳、回、導、滾、轉、切)漏掉。這條修補本來要讓前端送出不誤升級,實際只擋到沒寫「對/向/到」的句子。
- **測試缺口**:`t_door_keyword_send_destination_variants_still_hit` 的「不算」對照只有三句,都避開了這些字。把「對」「向」從去處字拿掉,漏判照樣會被抓到,但「對應」誤中完全沒有守衛。
- **歸因**:有證據的修復回歸(「到」的部分),「對」「向」是新增放寬帶進來的。修前 `送出(?=[^,.;!?。、\n]*[給至往])` 沒有向、對,到也只認緊貼,所以 `跳到成功頁` 修前不算。這是從舊正則讀出來的推論,沒有另外跑修前版本。
- **改法**:去處字改成要求貼近送出的名詞結構,或把單字「對」「向」換成「對外」「向外」「向第三方」。「到」改回緊貼 `送出到`。

引句:「_PITFALL_SEND_DEST = r"(?:[給至往向對予]|外部|第三方|客戶(?!端)|廠商|銀行|物流|partner|external)"」

**3. 路徑判法在兩處不一致,e2e 底下非 infra 副檔名的檔會被棧別題拿到、claims 卻被跳過**

severity: minor
blocking: 否

- **問題**:`_stack_key_for_file` 現在用 `ext in _INFRA_CODE_EXTS and _TEST_INFRA_PATH_RE.search(...)`。`pitfalls --diff` 的 claims 掃描卻只判 `not _TEST_INFRA_PATH_RE.search(cur_file)`,沒看副檔名。
- **例**:`e2e/app/Main.kt`、`e2e/reset.sql` 的棧別鍵是 kt、sql。暫存 repo 實測 `stack_questions` 有 kt、sql,但這些檔的新增行不進產品型樣掃描。
- **取捨**:注意這個 patch 的 `t_test_infra_path_tightened` 第②項寫「非 infra 副檔名照原棧」。claims 這邊沒同步,同一個正則在兩處語意不同。
- **歸因**:未判定。修前 `_stack_key_for_file` 對這類檔回 None,所以是不是回歸看你怎麼定義;我沒有拿修前版本跑 claims。
- **有沒有實害**:`e2e/reset.sql` 的 `DELETE FROM users` 在這個實驗裡沒有出 claim,所以我沒實證造成漏報,只指出不一致。

引句:「        if (cur_file and _stack_changed_ok(cur_file, vend_skip) and not _TEST_INFRA_PATH_RE.search(cur_file)」

**4. `_INFRA_CMD` 的 xargs 分支漏掉「選項與參數分開寫」的常見寫法**

severity: minor
blocking: 否

- **輸入**:`git ls | xargs -I {} kill {}`。
- **結果**:`_stack_question_specs["infra"]` 的 `when` 比對下沒有 infra-signal、infra-pid 命中(set())。
- **對照**:`xargs -0 kill`、`xargs -I{} kill {}`、`xargs -r -n1 kill -9` 都命中。
- **原因**:`xargs\s+(?:-\S+\s+)*` 只吃 `-X` 或 `-Xarg` 單塊,`-I {}` 中間隔了空白,`{}` 不以 `-` 開頭而斷鏈。
- **測試缺口**:S51 只測 `xargs kill` 與 `xargs kill -9`。
- **歸因**:修補新增的觸發,不是回歸。

引句:「_INFRA_CMD = r"(?:^|[;&|(`!{]|\$\(|(?<![A-Za-z0-9_])(?:if|then|do|else|elif|while|until|sudo|exec)\s|(?<![A-Za-z0-9_])xargs\s+(?:-\S+\s+)*)\s*"」

**5. 測試檔 E302 空行不足**

severity: minor
blocking: 否

- **位置**:`t_test_infra_data_files_no_stack_key` 修改後,檔尾與下一個 `def t_disposition_gate_covers_infra_questions` 之間只剩一個空行(`scripts/test_lumos.py:67788`)。
- **是否違規**:我跑 `ruff check --select E302` 沒有報這一行,不能引專案規則,所以只算 ⚠。專案 ruff 設定我沒查到,留給編排者用專案閘確認。

引句:「              and set(data.get("stack_questions") or {}) <= {"infra"}, f"{list(data.get('stack_questions') or {})} {data['claims']}")」

**三問回答**

1. **原問題的修復效果**:以下我實跑後都成立。
   - `PAYMENT_TIMEOUT_SECONDS`、`PAYMENT_TIMEOUT_MS` 這類參數名已不算金流。
   - `PAYMENT_API_URL`、`PAYMENT_RETRY_COUNT_MAX` 仍照算。
   - 子句邊界與 80 字線性限制有效。
   - 全形逗號、`src/e2e` 保護、`db/seeds` 不再特別處理,都有行為證據。
   - `-k test_infra_path` 8 個通過,`-k door_keyword` 85 個通過。
   - 但「送出」例外在 finding 2 的輸入下仍會誤判。
2. **修補處的相鄰呼叫路徑**:
   - `_stack_key_for_file` 的三處呼叫者(`scripts/lumos:46710`、`47374`、`47384`、`50215`)走新判法,語意一致。
   - 唯獨 claims 掃描(`scripts/lumos:47359`)直接用 `_TEST_INFRA_PATH_RE`,與上述不一致(finding 3),並且 finding 1 的收窄在此處放大。
   - `_PITFALL_SEND_RE`、`_PITFALL_PAYMENT_RE` 舊常數名在 `scripts/lumos`、`scripts/test_lumos.py` 已無殘留引用。我只 grep 了這兩支檔,沒 grep 文件。
   - `_INFRA_CODE_EXTS` 依賴 `_NODE_EXTS`,後者定義在前(約 30305 行),載入順序沒問題。
3. **新發現在修前、修後的結果**:
   - Finding 1 的路徑在修前為 infra,修後不是,回歸成立。
   - Finding 2 的「到」類是修前不算、修後算。
   - Finding 2 的「對」「向」部分,修前我沒有跑修前版本,這部分未判定。
   - Finding 3 與 4 是修補新增的行為。

**未驗範圍**:
- 沒有跑全套測試。
- 沒有逐項對照 `_NODE_FRONTEND_MARKERS` 守衛測試在新增框架時是否翻紅,只看到它對現有 8 個名稱通過。
- 沒有核對 `_DOOR_RULE_VERSION=13` 與計劃文件的敘述,只確認 origin/main 在此工作樹不存在、無法比對是否已有 13 上主線。
- 沒有做記憶體或 8 秒以上的線性壓測,只看到 S47 測試通過。

最嚴重 severity: major,blocking 共 2 條。
