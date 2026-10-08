severity: minor

# 邊界-sonnet 報告(邊界與輸入鏡頭)

實驗方式:`git clone --shared` 到臨時目錄,用 test_lumos 的 helper 建假 repo,對 `lumos set`、`drift fix --kind c3/c4`、`_drift_c4_same_commit`、`_delguard_parse_diff` 逐個餵怪輸入看實際輸出。沒有 blocker/major。

已跑過、行為正常的怪輸入(不成 finding):
- 同提交清單:根提交(無父)、改名進來(`--diff-filter=AR`)、合併提交(回空清單,不當機)、合併提交裡才出現的目錄、不存在的 sha(回 None,證據頁寫「查不到」)、淺複製(第一次提交寫「shallow,查不到最早提交」、範本寫 `<sha>`、同提交寫查不到,計劃名比對照列)。
- 目錄名含空白、雙引號、單引號、`$(touch pwn)`、前導 `-`、中文:都原樣列出,沒被執行、沒炸。
- `lumos set valid_under/revalidate_when`:`<sha>`、`<卷證>` 放在引號、反引號、多個值的其中之一、`List<sha>` 都擋;`related` 等別的欄位沒被牽連。
- c3 `--reason`:換行、`\r`、U+2028、空字串、少於 4 字擋;含全形「；」、反引號、雙引號、`<sha>`/`<卷證>` 完整字樣(擋);去頭尾空白正確。
- 刪除守衛跳過工具檔:`_VENDORED_ALL` 全是精確檔名(沒有目錄項),所以不會有「目錄項比不到」的問題;同目錄自己的檔(`scripts/hooks/claude/mine.py`)、`scripts/lumos.py`、`sub/scripts/lumos` 都照抽;刪除整檔的工具檔正確跳過;同一支檔出現兩次 `vendored_skipped` 只記一次。`_delguard_parse_diff` 拆成小函式後,對合成 diff 的輸出與拆前語意一致。
- 圖譜內既有筆記的 valid_under/revalidate_when 沒有含 `<sha>`、`<卷證>`、`<整項新內容>` 的,新擋法不會讓現存筆記改不動。

## F1 佔位字只認完整半形小寫字面,少半邊、全形、大小寫、括號內加空白都放行
severity: minor
blocking: 否
引句:「_SET_COND_SLOTS = ("<整項新內容>", "<卷證>", "<sha>")」
佐證行:file: `scripts/lumos:15146`(`_set_conditions_locked` 的 `left = [x for x in _SET_COND_SLOTS if any(x in v for v in vals)]`)
1. 重現:`lumos set Verification/A valid_under "提交 <sha"`(少右括號)、`"提交 <卷證"`、`"提交 ＜sha＞"`、`"提交 <SHA>"`、`"提交 <Sha>"`、`"提交 <卷證 >"`、`"提交 < sha >"`、`"提交 <整項新內容"` 各跑一次。
2. 實際輸出:八個全部 rc 0、`✓ set … valid_under 整欄換成 1 條`,佔位字殘片直接寫進驗證紀錄前提。對照組 `"提交 <sha>"` 與 `` `<卷證>` ``、`"<sha>"` 都 rc 2 擋下。
3. 走到哪:c4 證據頁範本印的是完整字面,人若只改一半(刪掉 `>` 或手打成大寫)就漏過;這正是計劃「照貼提示就寫進去」要擋的那類失誤的近親。同一份正規式做法也在 `--reason` 的 `_DRIFT_PLACEHOLDER_RE`(c3 理由驗證重用它),同樣不認這些變體。
4. 範圍很窄(要人手改壞才會發生),故只標低嚴重度。

## F2 同提交清單把卷證目錄名轉成 NFC 後印出,磁碟上是 NFD 的目錄印出來的路徑在區分正規化的檔案系統上不存在
severity: minor
blocking: 否
引句:「d = nfc(parts[2]) if len(parts) >= 4 and parts[:2] == ["governance", "review-reports"] else ""」
佐證行:file: `scripts/lumos:27969`(`_drift_c4_same_commit` 回傳 NFC 名;`_drift_c4_existing` 已存了 `{NFC: 原名}` 但同提交來源沒用原名)
1. 重現:在 review-reports 底下建目錄 `code-Done-濁ぱ`(ぱ 用 NFD,は+U+309A),與計劃名對得上,同提交加進來;跑 `drift fix … --kind c4`。
2. 實際輸出:`governance/review-reports/code-Done-濁ぱ(兩者)`,該字串 `is_normalized("NFC")` 為真;磁碟目錄名位元組是 `code-Done-濁ぱ`(NFD)。兩者位元組不同。
3. 影響:APFS/HFS+ 不分正規化所以看不出;Linux CI 或 Linux 開發機上人照清單挑路徑填進範本,填進 valid_under 的路徑指不到真目錄。補強前輸出用 `d.name`(原名),這是新增的差異。
4. 修法方向不在這裡寫;`existing` 已有原名可用。

## F3 卷證目錄清單沒有上限,整批匯入的提交會印出幾百行
severity: minor
blocking: 否
引句:「for d, src in ev["reports"]:」
佐證行:file: `scripts/lumos:28011`(`_drift_c4_print_dirs`)
1. 重現:計劃檔與 40 個 `bulk-NN` 卷證目錄同一個提交進來(模擬整批匯入或壓成一個的提交),跑 c4:輸出 45 行目錄,全部標「同提交」;`len(same) > 3` 只多印一行提醒,沒有截斷。
2. 目錄數到幾百時證據頁被清單淹沒,④⑤(要改的前提與預填指令)被推到最下面。同一支檔內別的清單(`_drift_print_hints`)都有 20 條上限與「還有 N 條」,這裡沒有,不一致。
3. 「同一提交加了大量卷證目錄」是使用者指定的怪輸入,實測不會出錯,只是輸出量;所以標低嚴重度。

## 圖譜鏡頭固定席逐條判定
(依 graph-lens.md 的節點;以下只答本鏡頭能實測到的)
- delguard(刪除守衛):不影響既有合約。實測消費專案路徑判斷只用精確檔名、恆 rc0 的 fail-open 結構沒動(timeout/例外分支用 `locals().get("vend")`,`vend` 未定義時是 None,`_delguard_vendored_note(None)` 回空字串)。
- guard-kill / 守衛預告句:c1 與 settle 共用 `_guard_settle_missing_say`,`say=False` 不印、回句子清單,`missing` 為空時 c1 訊息尾巴為空字串,無破壞。
- lumos-cli-write(set 整欄改前提/回頭條件):佔位字擋新增,不影響原有的空值、換行、多值檢查順序(先擋佔位字再擋空);`related` 等非 COND 欄位不受影響。
- 存量漂移守衛:c3 多收 `--reason`,不帶時輸出與舊版一致(實測補的行結尾無「理由」);c4 仍不寫檔、不寫帳(實測 rc 0、檔案位元組不變)。
- 順帶觀察(不成 finding,為既有行為):c3 理由裡的 `[[不存在的連結]]` 會寫進筆記,`lumos doctor` 會列成「連到不存在筆記」提醒但不擋;測試與計劃已明寫「不驗存在」。

最高等級:minor
