severity: major

整份 diff 逐 hunk 讀完。我另外造了兩個臨時專案實跑,也用改壞的 `scripts/lumos` 副本跑過測試(臨時目錄已刪)。

## 1 門檻值為 NaN 或 Infinity 時,永遠判達標
severity: major
blocking: 是
引句:「failed = value > t["max"] if bound == "max" else value < t["min"]」
- **場景**:門檻檔寫 `"max": NaN`(Python 的 `json.loads` 收 NaN,`_secev_num` 也放行),`value > nan` 恆為 False,所以不管現值多大都歸 `threshold_passed`。`"min": NaN` 同樣恆達標。`Infinity` 同樣是無限寬鬆。門檻檔的驗證在 `_macrobench_threshold_item_err`,檢查 `max`/`min` 時只看型別、沒擋非有限數。
- **重現**:現值 P90=3.6,門檻檔 `max` 寫 NaN,跑 `lumos macrobench --json`。輸出 `threshold_failures: []`,`threshold_passed` 內有 `'max': nan, 'current': 3.6`。該條門檻被判達標,而且 `--json` 輸出裡出現非法 JSON 字面值 `NaN`。
- **後果**:人裁的驗收門檻被靜默繞過,且沒有報錯。
- **修法**:`_macrobench_threshold_item_err` 加 `math.isfinite`。測試要有 `max: NaN` 與 `Infinity` 回 2 的案例。
- file: `scripts/lumos`(diff 內 `_macrobench_threshold_item_err` 與 `_macrobench_check_thresholds`)

## 2 rerun.sh 範本在沒解析到任何查詢時回 0,收據可以空轉通過
severity: major
blocking: 是
引句:「for qid, head, sql in re.findall(r'^-- \[(Q\d+)\] (.+?)\n(.*?;)\s*$', text, re.S | re.M):」
- **場景**:`queries.sql` 的最後一條查詢沒寫結尾 `;`,或標頭格式差一點(例如 `--[Q1]` 少空格)。`findall` 回空,`qs` 為空,迴圈不跑,`fail=0`,`sys.exit(0)`。
- **重現**:`queries.sql` 內容是 `-- [Q1] session=a trace=t requires=- expect=a:n=1` 加一行 `select 1 as n`(沒分號)。我用同一支正規式驗,結果是 `[]`。
- **後果**:SKILL 收尾第 2 步「自己跑一次確認回 0」和第 4 步盲測,都把「回 0」當作驗證成立,這時卻什麼都沒驗。
- **關聯缺口**:`manifest.layers[*].queries` 列的 Q 編號,範本不核對是否真的跑過;全部 `expect=-` 也回 0。
- **修法**:範本要在 `qs` 為空、或 manifest 列的 Q 沒在 `queries.sql` 裡時回非 0。
- file: `skills/lumos-android-evidence/reference.md`(rerun.sh 範本)

## 3 L0 的「另一次執行當基準」流程,會讓人裁門檻整個不被判
severity: major
blocking: 是
引句:「另建一個暫存目錄,放 `.lumos/macrobench.json`(`results_dirs` 寫基準那次的絕對路徑),`lumos macrobench --repo <暫存目錄> --update-baseline`,再把 `results_dirs` 改成候選那次的路徑跑 `--json`」
- **場景**:程式從 `Path(repo)/.lumos/macrobench-thresholds.json` 讀門檻。暫存目錄只放了 `macrobench.json`,所以 `--repo <暫存目錄>` 這次的 `threshold_failures`、`threshold_skipped` 恆為空。
- **後果**:SKILL 第 8 步的往下條件把 `threshold_failures` 當觸發之一。照這條流程做,若比基準沒變慢,收據會記「L0 通過」後停止,門檻沒達完全不會被看到。第 9 步抄 `contract` 也抄不到。
- **修法**:這段要寫明把專案的 `macrobench-thresholds.json` 複製進暫存目錄的 `.lumos/`,或另在專案根用候選結果單獨跑一次(只看門檻)。
- file: `skills/lumos-android-evidence/SKILL.md`(L0 第 5 步、第 8 步)

## 4 「第 N 條」編號與載入時的 stat 檢查,都有改壞測試照綠的例子
severity: major
blocking: 是
引句:「bads.append((why, json.dumps({"version": 1, "thresholds": [_mb_thr(), item]}, ensure_ascii=False)))」
- **場景**:`t_macrobench_threshold_bad_file` 每個壞案例都是 `[好的, 壞的]`,壞條永遠排最後(第 2 條),且 `scrollList` 情境有跑到。
- **改壞 A(編號)**:在 `_macrobench_thresholds` 的迴圈裡加 `i = len(raw["thresholds"])`,訊息一律報最後一條。
- **改壞 B(stat)**:把 `_macrobench_threshold_item_err` 載入時的 stat 檢查改成 `if False:`。
- **實測**:兩個改壞同時套用,`-k macrobench_threshold_bad_file` 是 `15 passed, 0 failed`。
- **為什麼測試抓不到**:
  - A:壞條永遠是最後一條,`i` 和 `len` 剛好相等。
  - B:「stat 不認得 P75」案例仍由執行期的 `_macrobench_check_thresholds` 補位(情境有跑到),輸出 rc2 與「第 2 條」。測試被另一道檢查代打,這違反〈實作測試品質〉第 4 點。
- **後果**:若情境沒跑到,壞 stat 的門檻檔會變成 rc0 + 沒判,與 S5 條款矛盾。本案特定鏡頭「第 N 條編號對得上檔案順序」也沒被守住。
- **補法**:加「壞條在第 1 條、好條在第 2 條」的案例,以及「壞 stat 但該情境沒跑到」仍回 2 的案例。
- file: `scripts/test_lumos.py`(`t_macrobench_threshold_bad_file`)

## 5 decided_at 只驗格式,與計劃條款 S5 不符
severity: minor
blocking: 否
引句:「if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", t["decided_at"]):」
- **場景**:`2026-13-45` 通過驗證。實測該門檻檔可正常載入並判定。
- **不一致**:S5 條款寫「`decided_at` 不是日期」要回 2,但實作只驗寫法。
- **修法**:用 `datetime.date.fromisoformat`,測試補 `2026-13-45`。

## 6 text 輸出的斷言是恆真式
severity: minor
blocking: 否
引句:「check("文字輸出不說達標", "達標" not in rt.stdout or "沒判" in rt.stdout, rt.stdout)」
- **場景**:`_macrobench_print_thresholds` 的摘要行一定印「N 條達標、…、N 條沒判」,所以 `"沒判" in rt.stdout` 恆真,這條斷言抓不到任何錯誤。
- **補充**:上一條 JSON 斷言已守住行為本身,所以只是多餘的假保護,不是缺口。
- **修法**:改成斷言文字輸出有 `[沒判]` 且沒有 `[達標]` 之類的行。

## 7 來源 sha256 不是用解析的那份 bytes 算的
severity: minor
blocking: 否
引句:「src = {"file": Path(rel).as_posix(), "sha256": hashlib.sha256(f.read_bytes()).hexdigest()}」
- **場景**:`_macrobench_read_file` 已用 `read_text` 讀過並解析,這裡又獨立讀一次 bytes。兩次之間檔案被改,sha256 對不上實際入基準的統計值,「找雜湊對得上的那次執行」(SKILL L0 第 6 步)會指錯 Trace。
- **例外風險**:這行不在 try 內,若檔案剛好在中途消失或權限改變,`--update-baseline` 會噴 traceback,不是記進 `failed`。
- **修法**:讀一次 bytes,同時拿去解析與算雜湊。

## 8 reference.md 引用的步驟編號錯誤
severity: minor
blocking: 否
引句:「L0 本身的重跑指令寫在 report.md(見 SKILL.md L0 第 4 步)」
- **錯誤**:SKILL 的 L0 第 4 步是拉結果檔與算 sha256;`lumos macrobench --json` 與「寫進 report.md」是第 5 步。

## 9 rerun.sh 的 expect 解析有冷門限制,文件沒講
severity: minor
blocking: 否
引句:「key, _, pairs = kv['expect'].partition(':')」
- **場景**:`expect` 的 key(第一欄值)含冒號,例如 slice 名 `HWC:validate`,會被截斷成假失敗(BAD)。
- **場景**:第一欄值含逗號,或第一欄是數值(`rows` 只收 `"` 開頭的行),也會誤判。
- **文件缺口**:「值不能有空白」那句沒提這些限制。
- **修法**:加註限制,或改 CSV 解析。

## 10 已檢查、不成立的項目
- **舊基準(沒有 `source`)**:`_macrobench_entry_ok` 不看多餘的 key,新舊互讀都能比,測試也驗過。
- **重複情境被剔除**:`entries.pop` 之後,`source` 不會殘留(`v` 隨 `pop` 一起丟)。
- **`--update-baseline` 冪等**:同一批輸入重跑結果相同。
- **門檻與基準比對互不干擾**:`res.update(judged)` 只動 `threshold_*` 三個 key。同一指標同時進 `regressions` 與 `threshold_failures`,兩邊值各自正確。
- **JSON 布林當數字**:`_secev_num` 擋住了 `true`/`false`。
- **門檻檔的「第 N 條」編號(實作)**:`enumerate(…, 1)` 的編號與檔案順序一致,問題只在測試守不住(第 4 點)。
- **`PROJECT_ROOT`**:rerun.sh 的 `$HERE/../../..` 對 `<專案>/.lumos/receipts/<run-id>/` 是對的。
- **requires 鏈**:會去重,也有防迴圈。

## 圖譜鏡頭(固定席)
派工詞說明 `LUMOS-IMPACT` 範圍算不出來,hook 沒附固定席節點,這次是「沒有固定席」的備援情況,不逐條答。我只就 diff 內碰到的節點判定。
- **`Systems/macrobenchmark-adapter`**:新增的 WHY/PITFALL 行格式齊全。唯一的內容問題是上面第 1 點,「門檻判定可靠」這個隱含承諾被 NaN 破壞。
- **`Projects/Macrobenchmark驗收門檻_計劃`(S1~S9)**:
  - S5 的「decided_at 不是日期」與實作不符(第 5 點)。
  - S5 與「第幾條」的測試守不住(第 4 點)。
  - S8 的 L0 描述與 SKILL 的暫存目錄流程牴觸(第 3 點)。
- **其餘節點**:`Android逐層診斷_計劃`、`Android診斷證據接入_調研`、`Macrobenchmark退步提醒_計劃`、驗證紀錄、`04-自檢與健康.md`、`lumos-project-notes/reference.md`。我讀不出它們破壞既有合約,判不影響。理由是它們只加新增段落或指令手冊文字,沒有改既有行為。

severity 總結:max severity = major(第 1、2、3、4 條)
