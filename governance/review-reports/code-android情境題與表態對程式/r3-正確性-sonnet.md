severity: major

第 2 輪的修補大致守住了:`@Inject constructor`、逾時照 `over_budget` 兩條都修好了。但新加的快取清理有一個會刪到快取目錄以外檔案的洞,擋 1 條。

先講已驗過、沒問題的部分。
- **`@Inject constructor`**:`class X @Inject constructor(...)`、`private constructor`、`constructor`、200 個參數的長建構子,都判成類別本體,次建構子判成程式本體。20 萬行參數的 `_kt_sit_levels` 只花 0.24 秒,沒有二次方問題。
- **證據對不上**:我造了小 repo,跑 `code-loop dispositions` 再跑 `code-loop check`。證據行寫錯時 rc 0、印提醒,治理帳多一筆 `code-loop`/`warned`,帶 `scope: kt-situation`、`pending: blind-judge`。
- **缺段、缺列**:rc 1,擋。
- **段放行**:只關掉那段的證據提醒。放行過的段缺列、缺段、選 alt、evidence 超出段範圍,四種都照擋,沒有哪條路徑把缺答降成提醒,也沒有把提醒升成擋。
- **舊資料**:舊表態帳的欄位沒變,照樣讀得懂。快取 schema 升 3 後鍵不同,舊快取檔不會被讀到,下次寫入時照 24 小時期限清掉。

### F1 快取清理沒先驗目錄可不可信,可經捷徑刪到目錄外的檔
severity: major
blocking: 是

`_kt_situation_segments` 在寫快取之前先呼叫 `_home_cache_evict`,傳進去的是沒驗過的原始路徑。`_home_cache_write` 本來有 `_trusted_private_dir` 擋「目錄被換成指向別處的捷徑」(2026-09-06 全 repo 審視 #6)。原本唯一的清理呼叫端 `_drift_m1_cache_dir` 也先驗過目錄,不可信就傳 `None`、一支都不碰。新的呼叫端繞過了這層驗證。

引句:「+        _home_cache_evict(_kt_sit_cache_path(key).parent, _KT_SIT_CACHE_TTL)   # 寫之前清掉過期的(代碼審 r2 通才 F2、資源 F1)」

最小重現(已實跑):
1. 用暫時的 HOME,把 `~/.cache/lumos/kt-situation` 設成指向另一個資料夾的捷徑。
2. 那個資料夾放一個 mtime 3 天前的 `precious.txt`。
3. 跑 `lumos code-loop check --diff HEAD~1..HEAD --at-sha <sha> --branch feat/sit --repo <臨時repo>`。
4. 結果:`precious.txt` 被刪掉,清理前後資料夾內容是 `[precious.txt]` 變 `[]`。

file: `scripts/lumos:66955`(`_home_cache_write` 的驗證)、`scripts/lumos:59420`(`_drift_m1_cache_dir` 的驗證)

建議:傳給 `_home_cache_evict` 之前先過 `_trusted_private_dir`,不可信就不清。測試也要補一個目錄是捷徑的案子。現有 `r2 ①` 只測了一般目錄。

### F2 逾時發生在核對迴圈中途時,這一題已查出的缺段、缺列會被丟掉
severity: minor
blocking: 否

`_kt_sit_check` 在迴圈裡丟出 `_KtSitOverBudget`,區域變數 `probs` 跟著消失。`_kt_sit_verdict_one` 接到後直接回 `None`。同一份表態裡前面已經發現的缺段會變成放行,只記 `over_budget` 的 fail-open 帳。「已查出問題照擋」只在「別的題」的層級成立,同一題內不成立。

重現(行程內、模擬第 2 次期限檢查逾時):3 段、第 1 段沒答。`_kt_sit_check` 直接丟出 `_KtSitOverBudget`;走 `_kt_sit_verdict_one` 則回 `None`,且 `cache["over_budget"]` 為 True。

引句:「+    except _KtSitOverBudget:」
引句:「+        cache["over_budget"] = True」

預算 20 秒,實務上很少碰到,所以只列 minor。修法是 `_kt_sit_check` 逾時時帶著已收集的 `probs` 一起丟出,或改成逾時時回傳部分結果加旗標。

### F3 提醒帳沒去重、不封頂,會把之後「升擋」要看的數字灌水
severity: minor
blocking: 否

每次 `code-loop check` 都把全部提醒各寫一筆 `code-loop`/`warned` 進版控的治理帳,只有印在畫面的才限 6 條。同一份答案連跑 3 次,帳上 `warned` 變 2、4、6 筆(實測)。計劃寫的是「每列升 Block 要有提醒的真陽性數當依據」,而這本帳的筆數會隨推送次數增加。

引句:「+        _gate_event_or_warn(repo_root, "code-loop", "warned", r["text"][:120], hard=False,」

測試缺口:`t_kt_situation_waive` 的帳檢查只用 `any(...)`。把寫帳搬進 `if i < 6` 裡,測試照綠。也沒有「重跑不重複記」的案子。

建議:帳事件加 `(head_sha, seg, row)` 去重,或只記第一次。

### F4 快取鍵拿掉 lumos 檔時間後,切法改了忘記升 schema 就沒有任何守衛
severity: minor
blocking: 否

這輪改了切法並手動升 `_KT_SIT_CACHE_SCHEMA` 到 3,但沒有測試釘住這個約定。例如把 `_KT_SIT_GAP` 從 4 改成 5 而不升 schema,所有測試仍綠,因為測試用的 sha 每次都是新的。實際使用時會吃最多 24 小時的舊切段。

引句:「+_KT_SIT_CACHE_SCHEMA = 3   # 切段結果的形狀或切法改了就加一(r2:宣告頭判法改了)」

建議:把切段常數(`_KT_SIT_GAP`、`_KT_SIT_SEG_MAX`、`_KT_SIT_CTX`)和宣告頭正規式併進快取鍵。

### 後端卡(be-api-compat、be-authz)
沒有發現。
- **相容**:表態帳的 `kt-situation` 紀錄形狀沒變,舊紀錄照樣讀得懂。`_kt_sit_template` 的 `where` 只在檔名含控制字元時才有差別。
- **授權**:這批沒有新增端點或權限判斷。

### 測試獨立判準
`_sit_decl_header_ctor` 用手數的行號當預期值,把 300 字上限加回去會翻紅,是有效的守衛。

引句:「+        check(f"r2 宣告頭 {label}:bad() 的段材料只到 bad() 本身(第 {bad_at} 到 {bad_at + 3} 行)", mat == (bad_at, bad_at + 3), f"{mat}")」

`kws` 過濾掉 `init`、`get`、`set` 這三個,拿掉後行為不變(它們排在最後時結論本來就是「不是類別」),所以這部分是死過濾,但無害。

### 清理
我的臨時目錄 `/tmp/lumos-seat-work/code-android情境題與表態對程式/正確性-sonnet` 已刪。沒有改 repo,也沒有動 git。不帶 HOME 覆寫的幾次實跑,在真的 `~/.cache/lumos/kt-situation/` 留下幾個以 sha 命名的小快取檔。那些檔和別的會談的混在一起,我不用萬用字元刪,留給 24 小時期限自動清。

總結:最嚴重是 F1(快取清理繞過目錄可信驗證,可經捷徑刪到目錄外的檔,已實跑重現),會擋 1 條。
