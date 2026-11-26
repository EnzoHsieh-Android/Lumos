severity: major

審查依據:`/Users/enzo/harness/lumos-choice-speed4` 的 `scripts/lumos` 與 `scripts/test_lumos.py`。逐節讀完,沒有跳段。跨段引用我都核對過:第一段計劃〈用詞〉、第三段〈用詞〉、第二段 S1/S2、第一段 S13 都存在。

**逐節結論**
- 白話、WHY、PRIOR-ART、RETIRE-IF、實測、用詞:除下列 finding 外已讀,無 finding。
- 做法 1(初始化腳本):已讀,無 finding。
  - `_isolated_worktree` 的路徑是 `<mkdtemp>/wt`,所以 `dirname(c.wt)` 是每個平台組各自的上層資料夾,收尾整個刪除,宣稱成立。
  - `_choice_merge_cmd` 只有 `_kill_merge_ready` 與 `_kill_merge_base` 兩處呼叫,其餘是測試直接呼叫,宣稱成立。
- 做法 2、3、落點、驗收、回退、實務隱患:見 finding 1 到 4。
- S4:`t_choice_kill_no_merge_unchanged` 已存在。`--no-merge` 與 `LUMOS_SKIP_CHOICE_MERGE=1` 不進 `_kill_merge_iter`,所以呼叫數與順序不變,宣稱成立。

1. **做法 3 / WHY 第二條 / 實務隱患(斷路器不計跑到測試的逾時)**
severity: major
   blocking: 是(判準:這條拿掉了第一段計劃明講「由斷路器擋」的最壞情形保護,且沒有替代的煞車)
   - 問題:「逾時而且已跑到測試」一律不計、不歸零,所以工具自己的逾時上限不夠時也不會被計到。
   - 現況:快篩上限是 `_choice_merge_screen_cap` = min(max(合併基準耗時 × 5, 下限), 剩餘時限)。合併基準耗時是樹已編好、不含增量編譯的一次。
   - 失敗場景:壞法每次都要先增量重編(kapt/ksp 或大模組),重編加測試超過上限,逾時時已經有測試開始。
     - 第三段會計數並在連續 5 次後停用合併。
     - 這份改完永遠不跳開,每個壞法白付一次快篩上限再退回逐支。
     - `merge_why` 還被記成「逾時(跑到測試後掛住)」,把工具上限太小記成壞法的錯。
   - 第一段計劃自己承認這個量沒量過:file: `docs/lumos-toolchain-knowledge/Projects/選擇點變異加速_計劃.md:153`,「每次增量編譯多久(專案有沒有 kapt/ksp)…都沒量過」。
   - spec 只列了「機器過載」這一種代價,引句:「代價:機器過載讓每個壞法都逾時、而且都跑到了測試時,斷路器不再跳開」。
   - 唯一回頭條件是 RETIRE-IF ② 的「連續 10 個以上、累計 3 次」,要等 2026-12-31 才有人讀帳。
   - 能分開工具太小與真掛住的訊號只有「那支掛住的測試單支跑會不會也逾時」,spec 沒有拿它回饋計數。
   - 破壞次數:每次呼叫最多多付「壞法數 × 快篩上限」,例如 142 × 90 秒約 3.5 小時,只被 `--max-seconds` 截斷。

2. **做法 2、四層(通過層排在掛住層前面,沒有理由)**
severity: minor
   blocking: 否(判準:判定不變,只多花逐支次數)
   - 場景:快篩逾時時,守 8 支,7 支 PASSED、1 支 STARTED 沒結束,沒有未跑到的。
   - 這份排成 7 支通過層、最後才是掛住那支。每支逐支都要套壞法、等新的一秒、跑 Gradle、還原,7 支都存活,最後那支逾時判「測試掛住」,結果是 `no_result`。
   - 掛住的排最前,1 次就得到同一個 `no_result`。
   - 通過層只有在「合併裡過、單支才紅」(測試間有順序相依)時才有價值。spec 的 WHY 與〈不做〉都沒講這個理由。
   - 預期效益只算被殺掉的 10 個,這種「最後仍是 `no_result`」的案例成本被少算。
   - 驗收 S2 把 b、d、a、c 寫死,實作者無從得知這個順序可以不要。

3. **實務隱患「輸出很大」**
severity: minor
   blocking: 否(判準:只影響逐支順序)
   - 引句:「中段的事件會丟,丟掉的名字進未知層」
   - 這句不對。`_kill_cap` 保留頭尾各約 128KB。
   - STARTED 在頭、PASSED/FAILED 落在被砍的中段時,依〈用詞〉四層定義那支會被判成「有 STARTED 而它之後沒有結束事件」,進掛住層(最後),不是未知層。
   - 例:原本該排最前的紅層測試,因 FAILED 行被砍,反而排到最後。
   - file: `scripts/lumos:29` 附近的 `_kill_cap`。
   - 要在這個函式裡處理截斷標記,或把這句話改正。

4. **落點 / 第二段、第一段既有條款沒標被取代**
severity: minor
   blocking: 否(判準:文件與測試敘述會不實,但程式行為在測試環境不變)
   - 第二段 S2:file: `docs/lumos-toolchain-knowledge/Projects/選擇點變異加速第二段_計劃.md:123`,寫「沒跑乾淨…照原排序…跟 `--no-merge` 的壞法階段相同」。
   - 第一段〈用詞〉:file: `docs/lumos-toolchain-knowledge/Projects/選擇點變異加速_計劃.md:55`,寫「斷路器只數…逾時…」。
   - 這份改完,真實 Gradle 帶事件時兩句都不再成立。
   - 第三段對自己改掉的舊句子有標〔部分被取代〕(見第三段 75 行)。這份〈落點〉只提到「語意不變」的測試,沒有為這兩句標被取代。
   - `t_choice_kill_merge_failed_first` 的 S2 在 fake 下沒有事件行所以仍綠,docstring 卻說「合併逾時…跟 --no-merge 相同」,之後會誤導。

5. **落點 / 驗收 S2、S3(假 Gradle 輸出不會 flush)**
severity: minor
   blocking: 否(判準:實作者跑測試會當場紅,不會放進生產)
   - spec 要求假 Gradle「在逾時睡眠之前印」事件行。
   - `_CKM_GRADLE` 用普通 `print`,stdout 導到暫存檔,是區塊緩衝。
   - 被 `_kill_proc_group` 用 SIGKILL 收掉時緩衝內容會全丟,`tail` 沒有事件行。
   - S3 前半(有 STARTED 應不跳開)會變成跳開,S2 逾時案的順序全落原順序。
   - spec 沒寫要 `flush`。
   - file: `scripts/test_lumos.py:146259`(`_CKM_GRADLE`,`mode == "hang"` 睡 60 秒之前沒有 flush)。

**四層排序 vs `--no-merge` / 第三段(逐支流程停止規則)**
- 判定與 `--no-merge` 不同:這是第二段就有的設計,第二段 S1 案 4、5 已明文。這份新增的只是同一件事擴到逾時。
- 我找不到比第三段更差的判定。
  - 紅層、未知層、通過層、掛住層之間,任一個強 killed 都會在第一次決定性列時 `finish`。
  - 新增的場景要「合併裡通過、單支卻紅」或「合併裡掛住、單支卻殺掉」且另一支(未知層)單支會掛住,才會出現「第三段 killed、這份 no_result」,需要多重巧合,我不標。
  - 時間成本變差的場景見 finding 2。
- `killing_test` 是第一支強 killed,順序改了就可能不同,同第二段既有行為。

**事件行對到合併道**
- 測試名在這個系統裡是裸方法名,例如 fake 的 `aCase`。基準階段已要求每支恰好對到 1 個完整名,所以「同名跨套件撞兩支」在實務上到不了。
- 第三條「m 以 `. 加 f` 結尾」只在 m 帶類別時有意義,不會讓裸名誤對。
- 判斷:一支不會被對到兩層。同一事件對到兩支名字只在合併道有兩支同名類別時才發生,這在基準階段就被擋掉。我無法構造出對錯人的案例,承認對。

**實務隱患鏡頭逐類**
- 金流 / 對外送出:無。只在本機跑測試,不連網。
- 不可逆:無。初始化腳本寫在隔離工作樹的上層資料夾,收尾整個刪除。`--keep-worktree` 時跟現場一起留,是人要看的現場。
- 併發與交易:無。每個平台組各有一個 `mkdtemp` 上層資料夾,檔名固定但不會互撞。直接用 `SimpleNamespace(wt=<共用暫存>)` 的既有測試才可能寫到共用目錄,spec 已列為要改成 `<暫存>/wt`。
- 效能:見 finding 1 與 2。
- 資源:無新增。輸出上限沿用 `_kill_cap`。事件行每支兩行,數千支測試以內不會碰到 256KB,碰到時見 finding 3。
- 回滾:無問題。`LUMOS_SKIP_CHOICE_MERGE=1` 與 `--no-merge` 整個不開合併;事件沒有單獨開關,spec 已明講需還原提交。`merge_why` 新字樣是既有欄位的新值,讀端照字串讀,我 grep 沒有地方比對固定值。

**固定席(`Systems/guard-kill`)**
- 兩條 ★INVARIANT★ 不受影響:
  - rc 優先序只看 verdict 集合,不看列的順序。
  - `--json` 純度只看 stdout,事件行只進 `_kill_run` 的暫存檔與合併 `tail`,不印出。
- 這份也沒有新增任何標準輸出或標準錯誤的列印。
- 兩條合約都判不影響。

最高 major,blocking 1 條
