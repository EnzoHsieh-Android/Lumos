severity: minor

# 設計審第 2 輪 邊界-sonnet 席報告

立場:極端輸入(空、單一、超大、卡界線、格式怪)。已實測:argparse 行為、`git show --diff-filter=A` 遇改名、`fmt_scalar` 對 42 種怪字串的寫出再讀回、本 repo 186 篇 valid_under 的長度與關鍵詞分布。

## F1 第③道讓「合法提到關鍵詞的項目」無法在 drift fix 保留,本 repo 就有實例
severity: minor
blocking: 否
引句:「每一項不能含 `_DRIFT_UNCOMMITTED_WORDS`,訊息點名是第幾項、哪個詞」
file: `docs/lumos-toolchain-knowledge/Verification/2026-07-15_主網M3_cascade帳本.md:10`
file: `scripts/lumos:26248`
1. 這篇 valid_under 第 3 項寫「torn 行跳過(=未提交)」,這裡的未提交是交易沒寫完,跟 git 無關;偵測(`scripts/lumos:26376`)照樣把整篇判成 c4。
2. 照 spec:證據頁把這一項標「← 要改的這項」並填 `<整項新內容>`;人若照原文保留這項,第③道回 2。要過就得把一句真話改寫成別的說法,或改走 `lumos set`(不記修復帳),再對這一行 `drift ack`。spec 沒有告訴人「這項是誤報,該走 ack」。
3. 同篇若另有一項真的過期,兩項都被③擋,無法只修過期那項而保留合法那項。
4. 另一實例 `Verification/2026-08-24_節點還原SOP落地.md:5`:單一長項裡混了真過期的「改動未提交」與不相干內容,③逼人整項重寫。
5. 建議:證據頁對每個關鍵詞項說明「若這個詞不是指 git 的還沒提交,用 drift ack」;或③只擋「詞出現的項目跟原文完全相同」而不是「含詞」。

## F2 多項 `--values` 遇到以 `-` 開頭的項目,沒有任何寫法能表達,預填指令還會直接印出壞指令
severity: minor
blocking: 否
引句:「單一項以 `-` 開頭時 argparse 會當成選項:寫成 `--values=-x` 的形式」
file: `scripts/lumos:27630`
1. 實測(python3 argparse,`nargs="+"`):`--values a -b` → unrecognized arguments;`--values=-b a` → unrecognized arguments;只有 `--values=-b` 單獨一項才過;`--` 分隔也不行。
2. spec 的補丁只涵蓋「單一項」。valid_under 有兩項以上且任一項以 `-` 開頭(無空白,例如 `-1 版`寫成 `-1版`、`-x`),整欄 `--values` 無法表達。
3. `_drift_sh` 的安全字元正規式含 `-`,所以 `-x` 會原樣不加引號印進預填指令,人照貼就被 argparse 擋。項目含空白時(`- 前提 x`)argparse 當位置引數,可以過,兩種行為並存。
4. 建議:預填指令遇到以 `-` 開頭的項改印「請自己組指令」分支,或加 `--values-file`。

## F3 「控制字元」沒定義;U+2028/U+2029 的項目會被印成可照貼、貼了卻被第②道拒
severity: minor
blocking: 否
引句:「整條超過 2000 字或任一項含控制字元時,不印可照貼的指令」
file: `scripts/lumos:9765`
file: `scripts/lumos:27683`
1. `_esc_clean` 只換 `< " "` 與 0x7f–0x9f;U+2028、U+2029、U+202E(雙向覆寫)、U+200B、U+FEFF 都原樣過。若「控制字元」照 `_esc_clean` 的口徑實作,含 U+2028 的既有項目會被印進可照貼的指令。
2. 人照貼 → 該項進入 `--values` → 第②道 `_drift_one_line` 用 `splitlines()` 判分行字元,U+2028 算兩行,回 2。第④道也因為少了原文那一項而擋。只剩 `lumos set`,而證據頁逐項列出時 `_esc_clean` 不會替人標出那是什麼字元。
3. 雙向覆寫字元印進「可照貼的指令」還會讓終端顯示的順序與實際參數不同(spec 資安節只提 `_esc_clean` 與 `_drift_sh`)。
4. 建議:「控制字元」明寫成 Unicode 類別 Cc、Cf、Zl、Zp,並與第②道用同一支判斷函式。

## F4 c4 證據頁「同提交」清單用 `--diff-filter=A`,提交內被偵測成改名的卷證目錄會整個消失
severity: minor
blocking: 否
引句:`_nodehome_git(root, "show", "-z", "--name-only", "--diff-filter=A", "--format=", <提交>)`
file: `scripts/lumos:23621`
1. 實測(暫存 repo):同一個提交把 `review-reports/舊計劃/` 改名成 `新計劃/`、另加 `其他/x.md`。預設 `git show --diff-filter=A` 只列 `其他/x.md`;加 `--no-renames` 才列出 `新計劃/r1-a.md`。
2. 驗證紀錄第一次被提交的那個提交,若同時把卷證目錄從草稿名改成正式名(卷證目錄常跟著計劃改名),「同提交」清單少掉最相關的那個目錄,「兩者」就不成立,範本退回 `<卷證>`。
3. spec 說這寫法「同每支檔有家那一段既有的寫法」,那一段查的是新增檔;這裡要的是「這個提交出現的路徑」,語意不同。建議加 `--no-renames`。
4. 同一節另有一個未寫明的銜接:同提交路徑來自 git(位元組解碼),計劃名比對來自 `rr.iterdir()`(磁碟拼法)。求「兩者」交集若用原字串比,NFC/NFD 拼法不同的中文目錄會各算一次而永遠不成兩者。既有慣例 `_git_paths_nfc`(`scripts/lumos:12190` 一帶)就是為這個做的。⚠ 我沒能在本機造出 NFD 目錄實測,列為未確認。

## F5 證據頁的「全部列出」與現有 300 字截斷沒有交代
severity: minor
blocking: 否
引句:「證據頁全部列出、每個標來源(兩者、同提交、計劃名)」
file: `scripts/lumos:27957`
1. 現有②行用 `_esc_clean('、'.join(...), 300)` 印目錄,超過 300 字尾端變「…」。加上每個目錄的來源標記後,約 8 個中文目錄就超過。
2. 整批匯入提交(spec 自己舉的例子)可帶出數十個目錄;若沿用截斷,人要「從清單挑」的清單看不到後面的;若不截斷,一行輸出可能上千字。spec 沒寫該改成一行一項還是保留截斷。
3. 排序把「兩者」排最前,範本不受影響;影響的是「兩者」為空時人手挑選的可見範圍。建議寫明一行一項並設上限,超過印總數。

## F6 c1/settle 新辨認式:日期不進「已寫的轉正日期」比對,會留下兩個不同的轉正日期
severity: minor
blocking: 否
引句:「TEST:摘要區有 `TEST:[YYYY-MM-DD] 預告已轉正` 開頭的行」
file: `scripts/lumos:12178`
file: `scripts/lumos:12243`
1. `_guard_written_settled_dates` 只收正文手補段與 WHY 行尾日期。新增的 TEST 形式(以及 whynot、settle 括號形式)認得為「已是轉正後說法」,日期卻不進這支。
2. 場景:守衛紀錄的 TEST 行是手寫的 `TEST:[2026-09-01] 預告已轉正`,WHY 預告句還沒改。跑 `drift fix --kind c1` 沒帶 `--date`:`got` 為空,日期改取 git 的 pass 提交日(例如 2026-09-03),WHY 寫成 09-03。同一篇出現兩個轉正日期,「已寫的轉正日期不一致」那道守衛不會響。
3. 辨認式只寫 `YYYY-MM-DD`,沒說是不是真日期:`\d` 在 Python 會匹配全形與其他 Unicode 數字,`2026-99-99` 也算。既有的 `--date` 走 `_guard_date_arg` 會驗真日期與不晚於今天,寫入端與辨認端口徑不一致。
4. 「正文任一行符合 `_GUARD_MANUAL_SETTLED_RE`」是整篇搜,不限在 settle 句原本的位置附近;正文任何一行以「日期 已轉正」開頭(含「已轉正式…」這種開頭)都會讓 settle 被判為已處理。
5. 建議:辨認與 `_guard_written_settled_dates` 共用同一組收集,日期用 `datetime.date.fromisoformat` 驗。

## F7 `_guard_settle_rewrite` 多回傳一個值,接線點只列 c1 與 settle,漏了 c5 與兩支包裝
severity: minor
blocking: 否
引句:「在 guard 區段 `_guard_settle_rewrite` 既有的」
file: `scripts/lumos:12290`
file: `scripts/lumos:12537`
file: `scripts/lumos:28010`
1. `_guard_settle_rewrite` 目前回二元組,兩個直接呼叫者是 `_guard_pass_rewrite`(`:12290`,回四元組給 settle 與 c1)與 `_guard_settle_record_lines`(`:12537`,回三元組給 settle 第二步與 c5 `:28010`)。
2. 讓回傳多一個值,這兩支包裝與 c5 的 `new, _missing, synced =` 解包、測試 `t_drift_fix_c5*`(`scripts/test_lumos.py:54201` 包了 `_guard_settle_record_lines`)都要跟著改。spec 第 3 節只寫「`_drift_fix_c1` 與 `guard settle` 印訊息時」。
3. c5 走的是同一支改寫,「已是轉正後說法」對它沒有訊息可說,要明寫 c5 丟掉那個集合,否則實作者容易漏改而在 c5 路徑解包失敗。

## F8 刪除守衛:升級時被刪或改名的工具檔不在跳過集合,而這是最常見的更新形狀
severity: minor
blocking: 否
引句:「拆除工具鏈(把工具檔刪掉)的那個提交,索引裡已經沒有那些檔,不會跳過」
file: `scripts/lumos:17765`
file: `scripts/lumos:17833`
1. `_vendored_intact(root, "")` 只看索引(提交後的樣子)。凡是這個提交把某支工具檔刪掉,它不在索引,不進「跟安裝清單一致」集合,`-` 行全數抽名稱。
2. 不只是「拆除」:`lumos update` 到新版時,新版的 `_VENDORED_ALL` 若已不含某支舊 hook(這個 repo 的 hooks 清單一直在增減),那支的整檔 `-` 行照抽,正是這次要降噪的那種誤報。誠實界線與 REVISIT 只寫了拆除與只暫存工具檔兩種。
3. 既有 `_vendored_skip`(`:17833`)已經處理「起點原封不動、終點刪掉」(`_intact_start - _present_end`),推送前分級用得到;刪除守衛是否也要這一段,spec 沒交代原因。
4. 另一個相反方向:索引是原封不動版,但被覆蓋掉的舊版是專案自己改過的(專案在 `scripts/hooks/pre-commit` 加了自己的函式,`lumos update` 蓋回原版)。跳過只看後影像,專案自己被刪掉的函式名稱靜默不查。同樣沒在界線裡。

## F9 刪除守衛工具檔判定:「受剩餘時間限制」只擋得住呼叫前,擋不住呼叫中
severity: minor
blocking: 否
引句:「在既有的剩餘時間判定(`_over()`)內取 `_vendored_intact(root, "")`」
file: `scripts/lumos:33068`
file: `scripts/lumos:17765`
1. `_vendored_state` 對 `_VENDORED_ALL`(17 支)逐支呼叫 `_lens_git`,再加一次讀 `.lumos/vendored.json`,共約 18 次子程序;`_lens_git` 的逾時是固定 20 秒,不接收剩餘時間。
2. `_over()` 只在呼叫前檢查。git 卡住(索引鎖、網路磁碟、防毒掃描)時,每次 20 秒,最壞 6 分鐘,遠超 `LUMOS_DELGUARD_DEADLINE` 預設 15 秒,而這道守衛的契約是恆 rc0、超時降級,跑在 pre-commit 內。
3. 「diff 至少碰到一支工具檔」的觸發條件沒寫怎麼判:若用 diff 檔頭,只有權限變更(`old mode/new mode`,沒有任何 hunk)的工具檔也會觸發這 18 次呼叫,卻沒有任何 `-` 行可跳。改名(`-M`)時檔頭 ` b/` 是新名字,被改名走的工具檔不算碰到。建議改成「碰到且有 `-` 行」才判,並把剩餘時間傳成 `_vendored_state` 的逾時。

## F10 跳過事件寫在哪個欄位:spec 說 detail,現有治理事件沒有這個欄位
severity: minor
blocking: 否
引句:「記在既有的 delguard 治理事件的 detail 裡(RETIRE-IF ② 要抽樣這些名稱)」
file: `scripts/lumos:29401`
1. `_delguard_log_result` 寫的事件形狀是 `gate、kind、hard、nodes、note`(`note` 是一個字串,形如 `tokens=N hits=N secs=X`),沒有 `detail`。
2. 這個記帳只在「掃描走完」的路徑呼叫。超時降級、內部錯誤、`--json` 之外的早退不寫跳過資訊;把 20 個名稱塞進 `note` 也會跟既有的 `secs=` 串接。RETIRE-IF ② 的「抽樣 5 次被跳過的名稱」要能讀出名稱,得指定欄位與格式。
3. 「少抽了哪些名稱」要對照沒有 skip 的解析結果才知道,等於解析一次 diff 兩遍;一次 `lumos update` 的 diff 可含兩份整支 `scripts/lumos`,這個成本 spec 沒估。

## 已讀,無 finding
- c3 理由 4/200 字界線:`_drift_fix_reason_ok` 用 `len(r.strip())`,恰好 4 與 200 都過、3 與 201 擋;全形空白(U+3000)`strip()` 會去掉;含 U+2028 被 `_drift_one_line` 擋;含尾端換行的理由在去空白前就被 `_drift_one_line` 拒(原樣行為,c2 同)。補的那一行仍走 `texts=[(txt, "body")]` 的形狀擋,`scripts/lumos:27906` 的 `txt` 加上理由後行號引用、前綴照樣被判。
- 第④道:重複項、只差空白、全形半形。`_conds` 與 `vals` 都用 `strip()`,只差首尾空白視為同一項;只差內部空白或全形半形的會被第④道當「少了」而擋,訊息列出缺項,是預期的保守。既有重複項在 `--values` 只給一份時會被靜默去重,語意不變,不算問題。
- 整欄算法對怪字串:我用 `fmt_scalar` 寫出再由 `parse_frontmatter` + `_conds` 讀回,42 種輸入(`yes`、`~`、`a: b`、`#x`、`[[link]]`、全形數字、`--dry-run`、U+202E、含 tab、單雙引號並存等)單項與清單兩種寫法全部一致,只有單雙引號並存拋 ValueError(spec 已處理)。
- 2000 字界線:本 repo 186 篇 valid_under 最長一篇 811 字、沒有超過 1700 的,對本 repo 無影響;「整條」是否含 `lumos drift fix <節點> <行號> --kind c4 --values` 前綴沒寫,但我給不出失敗場景,不標。
- `--values` 空值與零項:`--values ""` 走第①道空值擋;零項由 argparse `nargs="+"` 自己回錯。`--values` 放在節點與行號之前會吞掉位置引數,argparse 報缺參數,不是靜默。
- 卷證目錄四段路徑界線:`governance/review-reports/x.md`(三段)排除、`.../x/y`(四段)收、更深層取第三段,與 spec 一致;根提交(第一個提交)`git show` 會列全部檔,不影響。

## 實務隱患逐類
- 不可逆:寫入前五道擋在乾淨檢查之前,`--dry-run` 也擋;F1 的失敗方向是拒絕而非誤寫,無誤寫風險。
- 金流、對外送出:無,本機命令列工具。
- 守衛面:見 F8、F9、F10(刪除守衛是提醒不擋,失敗方向是誤報或逾時,不會誤放行工具檔以外的東西)。
- 資安:見 F3(雙向覆寫與 U+2028 沒被「控制字元」涵蓋)、F2(預填指令 `_drift_sh` 對以 `-` 開頭的項不加引號)。
- 效能:見 F9。
- 併發:第④道在鎖外用載入時的內容比,鎖內比指紋;我沒找到邊界輸入能繞過。

## 合約(★INVARIANT★)逐條判
- `Systems/guard-kill.md:20` guard kill rc 優先序:不影響。這份設計只改 settle 與 c1 的「找不到」訊息與判定,不碰 guard kill 的 rc。
- `Systems/guard-kill.md:21` guard kill --json 純度:不影響。settle 訊息字串走 stderr,不碰 guard kill 的 stdout JSON。
- `Systems/lumos-cli-write.md`、`Systems/delguard.md`、`Systems/存量漂移守衛.md`:這三篇在 repo 內沒有帶 ★INVARIANT★ 的行(grep 為零),無合約可判;但 lumos-cli-write 的「S3 黃金字串」與「WHY 綁 `t_drift_fix_c4_evidence_then_replace`」在 spec 第 6 節已保留,F7 提到的拆函式簽名要與它同步。

最高等級:minor;blocking 共 0 條
