severity: minor

# spec對照-sonnet:漂移修法補強 代碼審 r1

方法:逐條對 [S1]–[S5]、〈做法〉、〈回退〉、〈誠實界線〉讀 patch;clone 到臨時目錄跑綁定測試(t_drift_c4_reports_from_first_commit、t_set_conditions_blocks_drift_placeholders、t_drift_fix_c1_missing_message、t_drift_fix_c3_reason、t_delguard_skips_vendored_toolkit、t_drift_fix_c4_evidence_then_replace)全綠;另跑 -k delguard(102)、-k settle(72)、-k drift_fix(142)全綠。另手跑一次「只動工具自裝檔的提交」,治理事件 note 為 `tokens=0 hits=0 secs=0.0 vendored-skip=1 files=scripts/lumos`,格式對上。

逐條結論:
- S1:排序、標來源(兩者/同提交/計劃名)、AR、NFC、只留還存在、逐行 _esc_clean(路徑經 _nodehome_show)、超過 3 個的提醒、範本 `<卷證>`/`<sha>` 取自同一份常數、最後一行提醒,皆與〈做法〉一致。差異見 F1。
- S2:三個佔位字取自 _SET_COND_SLOTS;單一佔位字時訊息與改前逐字相同(以 patch 的 hint 字串對照原訊息確認);其他檢查順序不動。與條款一致。
- S3:c1 與 settle 走同一支;判定與回傳值未動;名稱直接用 _GUARD_PROSE_NAMES。差異見 F2(已於實作紀錄自承 say 參數)。
- S4:_DRIFT_FIX_ALLOWED、argparse 說明、佔位字檢查、三種寫法都在最後接「;理由:」(ASCII 分號,與計劃檔位元組一致);長度檢查用 strip 後長度、純空白理由會被擋,與「先去頭尾空白」一致。與條款一致。
- S5:純路徑、`_is_toolchain_repo` 為假才傳 _VENDORED_ALL、預設空集合、回傳 vendored_skipped、note 格式與 20 支上限、degraded/timeout/例外三條路徑都傳 vend,與〈做法〉一致。〈回退〉各項(呼叫端不傳、note 拿掉)與程式結構一致,可行。

## F1 「同提交:查不到」只在沒有提交或 git 失敗時印,措辭卻寫「或沒有」
severity: minor
blocking: 否
引句:「+        print("    同提交:查不到(git 失敗或沒有)")」
佐證行:file: `scripts/lumos:_drift_c4_print_dirs`(patch 內同名函式)
1. 〈做法〉第 1 節寫「git 失敗或逾時當空,證據頁寫『同提交:查不到(git 失敗或沒有)』」;實作 `_drift_c4_same_commit` 只在 sha 為空或 git 回 None 時回 None,git 成功但那個提交沒加卷證目錄時回 `[]`,`ev["same"] is None` 為假,這句不印。
2. 實作紀錄已自承這點,但〈做法〉本文沒改,印出的字樣「或沒有」實際上只涵蓋「查不到第一次提交」,不涵蓋「提交裡沒有卷證」。
3. 綁定測試 ⑤ 只測「這篇未提交」一種;git 已成功但同提交清單為空、以及 shallow/git 逾時兩種沒有測。誠實界線說「驗證紀錄另外提交時同提交清單是空的,只剩計劃名比對」,此時證據頁完全不提同提交來源,讀的人看不出是「沒有」還是沒查。

## F2 c1 多句找不到時每句都重複接一遍說明尾巴
severity: minor
blocking: 否
引句:「+    miss = "".join(";" + x for x in _guard_settle_missing_say(cx["rel"], missing, say=False))」
佐證行:file: `scripts/lumos:_drift_fix_c1`(patch 內同名函式)
1. 改前 c1 把所有缺的名稱用「、」接成一段:「;找不到A、B,沒改」;現在每個缺的名稱各接一整句「;找不到X——可能已經是轉正後的說法(不用改),或被手改過(看一下)」。四種預告句都缺時,結果訊息重複同一尾巴四次。
2. 條款 S3 只規定「字樣相同、名稱不疊字」,沒定多筆時的形狀;行為上與 settle 逐句印提醒一致,所以不算違反,但 t_drift_fix_c1_missing_message 只測單一缺句(TEST),多缺句的 c1 訊息形狀沒有任何測試釘住。

## F3 S1 綁定測試沒釘到「code- 開頭」對計劃名來源也適用、超過 3 個的邊界、git 逾時路徑
severity: minor
blocking: 否
引句:「+    rows = sorted(src.items(), key=lambda kv: (0 if kv[1] == "兩者" else 1 if kv[0].startswith("code-") else 2, kv[0]))」
佐證行:file: `scripts/test_lumos.py:t_drift_c4_reports_from_first_commit`(patch 內同名測試)
1. 測試裡唯一的計劃名來源是 `done-old-plan`(不是 code- 開頭),所以「code- 開頭不分來源都排在其他前面」這一子句(排序寫在同一個 lambda 裡)沒被驗;把 lambda 改成只有同提交來源才給 1,測試仍綠。
2. 「超過 3 個」只測了 7 個(印)這一側,沒測剛好 3 個(不印);`>3` 改成 `>=3` 測試仍綠。
3. 其餘子句(AR、只留還存在、中文目錄、<卷證>、最後一行、<sha>)測試都有釘,且測試自述的翻紅釘與實際相符。

## F4 vendored-skip 支數會算到只是「碰到」而沒有刪任何名稱的工具檔,且「兩遍都跳過」的第一遍無測試可證
severity: minor
blocking: 否
引句:「+                skipped += [] if cur in skipped else [cur]」
佐證行:file: `scripts/lumos:_delguard_parse_diff`(patch 內同名函式)
1. 計劃寫 vendored_skipped =「這次 diff 碰到並跳過的工具檔路徑」,實作一遇到 `diff --git` 那支路徑就記,不管該檔有沒有 `-` 行(重跑 `lumos update` 只新增或只改內容的提交也會記一筆,我手跑純內容改動的提交已見 `vendored-skip=1`)。與計劃字面一致,但 RETIRE-IF ② 要「累計 ≥20 次後抽 5 次、用 git show 看刪掉的名稱」,分母含大量沒有刪除的事件,樣本效率會比計劃預期低;計劃沒寫這點。
2. 條款與〈做法〉要求「抽 `-` 行名稱與收 `+` 行回收表兩遍都跳過」。回收表是逐檔的,而第二遍已整檔跳過,第一遍的跳過在行為上看不出來;測試 ⑤ 的翻紅釘只列「第二遍不跳」,沒有任何案例能讓「第一遍不跳」變紅。不是缺陷,是計劃寫了、程式做了、但測試證明不到的一條。

## 程式做了但計劃沒寫的
- `_SET_COND_SLOT_HINT` 對 `<卷證>`、`<sha>` 各有自己的提示語(「換成從證據頁清單挑的卷證目錄」「換成真的提交編號」),多個一起留著時用「逐個換成真的內容」;計劃只寫「訊息點名是哪一個」,未指定提示語。
- `_drift_c4_print_dirs` 在清單頂端多印一行圖例說明(兩者/同提交/計劃名的意思);計劃沒寫,無害。
- 為降告警把 `_delguard_parse_diff` 拆成三支小函式(`_delguard_path_flags`、`_delguard_added_tokens`、`_delguard_take_removed`)並把 `tok_re` 提到模組層 `_DELGUARD_TOK_RE`;計劃只在實作紀錄提到,〈回退〉「呼叫端不傳 skip 即回到原行為」仍成立,既有 102 條 delguard 測試綠,拆分行為等價(逐段對過兩遍的分支順序:diff 頭/Binary/非 +- 行/vault/排除)。

## 計劃寫了但程式沒做
- 無(除 F1 的「git 成功但空」不印句,及 `_guard_settle_missing_say` 由「組字」改為「回傳清單並選擇是否印」,兩者皆已列在計劃〈實作紀錄〉)。

最高等級:minor
