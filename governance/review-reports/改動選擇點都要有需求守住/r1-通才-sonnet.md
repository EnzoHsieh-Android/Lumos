severity: major

## t1 組處置要一條條款一支測試殺掉整組,與「一組=一條需求」的分組前提互相矛盾
severity: major
blocking: 是——照字面實作,多點的組會處置不了,只能逐點拆組,降噪的設計目的落空。
- 位置:〈範圍〉3「規格沒寫」、〈用詞〉需求脈絡組、預期值表 S18、S19。
- 問題:`situation-rule --group` 只寫回一條條款,綁一支測試,而且整組每一點都要被這支測試殺掉才寫回。但分組的依據只是「同函式、同守的測試集合」。S18 的例子是 `search()` 裡 `flatMapLatest`、`> 2`、`.distinctUntilChanged()` 三點成一組。一支測試要同時對這三種壞法都紅,通常要三個不同斷言。實務上它們會是三支測試、三條條款。
- 後果:這一組幾乎一定「有一點沒殺掉 → rc 1、不寫」,然後 `--split` 拆成單點。用詞表說「分組是近似」,但處置路徑把這個近似當成硬約束。
- 佐證:`scripts/lumos:79352` 的 `--test` 是 `required=True` 的單值參數。spec 沒有寫 `--test` 可重複,也沒有寫一組可以對應多條條款。
- 引句:「給 `--group` 時對組裡每一點各跑一次殺傷力(新條款綁的測試),全部 killed 才寫回條款」

## t2 每點呼叫一次 `cmd_guard_kill`:每點重建隔離工作樹並重跑基準,耗時成本被低估
severity: major
blocking: 是——照字面實作,跑完一次的時間數倍於 spec 的估計,RETIRE-IF ② 會一上線就觸發。
- 位置:〈用詞〉殺掉判定、〈範圍〉2、〈實務隱患〉第一條。
- 問題:spec 說「同一支測試指令的基準只跑一次」,但這個快取只存在於單次 `cmd_guard_kill` 呼叫裡。每點一次呼叫,就是每點一棵新的隔離工作樹加一次基準重跑。Android 的 Gradle 在全新工作樹上是冷啟動。
- 估算:一個普通 ViewModel 改動有 10 到 15 個選擇點。每點 2 到 5 分鐘的基準,再加上每支守的測試各跑一次壞法,總耗時是數十分鐘。依據來源那列寫的「約 10 秒判 killed」只是單點、暖機後的量測。
- 佐證:`scripts/lumos:28025-28031` 的 `baselines = {}` 在每個平台的 `_isolated_worktree` 區塊內宣告。基準重跑發生在 `cmd_guard_kill` 內部,`recipes_override` 只在單次呼叫內共用工作樹與基準。
- 修法方向:把全部點當多條 recipes 一次丟進同一次呼叫,同一棵工作樹、基準只跑一次,再按 recipe 的 `old` 分回各點。
- 引句:「一個選擇點只呼叫一次 `cmd_guard_kill`,把它全部守的測試當 `recipes_override` 一次丟進去(同一支測試指令的基準只跑一次)」

## t3 RETIRE-IF ② 按 spec 字面量不到
severity: major
blocking: 是——撤除條件量不到,等於沒寫。
- 位置:RETIRE-IF ②、〈範圍〉2「記」欄位清單、〈範圍〉5 `--stats`、S15。
- 問題:② 要看「每次推送前要補跑的選擇點中位數」和「殺傷力總耗時」。但:
  - `choice-kill` 帳列的欄位清單裡沒有耗時欄,也沒有「同一次 choice-kill 呼叫」的識別(run id)。
  - `--stats` 寫「每次 choice-kill 的點數與耗時中位數」,但每點一筆帳、沒有 run id,分不出哪幾筆屬於同一次呼叫。
  - 「每次推送前補跑」也對不上:推送閘不跑殺傷力,choice-kill 是作者獨立呼叫的,跟推送沒有綁定。
  - S15 的驗收也沒要求印耗時。
- 修法方向:帳列加 `run_id`、`elapsed`,把「每次推送」改成「每次 choice-kill 呼叫」。
- 引句:「每次推送前要補跑的選擇點中位數讓殺傷力總耗時超過十分鐘」

## t4 `no_result` 沒有處置出口,而推送閘擋它;逼人用 `--judge --as equivalent`,弄髒 RETIRE-IF ① 的分母
severity: major
blocking: 是——照字面實作,壞法編不過的點只能用不實的標籤放行。
- 位置:〈用詞〉有效處置、〈範圍〉3、〈實務隱患〉「壞法編不過」、RETIRE-IF ①。
- 問題:有效處置只有 killed、judged、推定三種,`no_result` 不算。表壞法編不過是常態。例:`"a" + b` 套 `+`→`-` 在字串上編不過;`all`→`any` 之類的型別換寫法也可能編不過。spec 的說法是「多半要改表」,但表是工具鏈來源那份,作者推送時改不到。
- 後果:作者要放行,只剩 `--judge --as equivalent|not-requirement`。`as` 只有這兩個值,沒有「壞法編不過」,所以標籤是假的。這些假判會被 RETIRE-IF ① 算成「存活裡被判等價或不是需求」,把「表誤報多」誤讀成「人亂判」或反過來。
- 修法方向:加 `--as uncompilable`,或在跑之前先做一次編譯可行性預檢,把壞法編不過的點直接從表上剔除。
- 引句:「判跑不出結果、印失敗摘錄;多半要改表(把那個成員拿掉)而不是要人處置」

## t5 選擇點表裡有一批「單元測試下必然存活」的列,每次改動都會產生保證存活的噪音
severity: major
blocking: 是——表的第一版內容照字面實作,一個普通 ViewModel 改動會大量被擋。
- 位置:〈用詞〉選擇點表的協程與拿掉呼叫兩行。
- 問題:`Dispatchers.IO`↔`Default`、`SharingStarted.Eagerly`↔`Lazily`、`.flowOn(…)`、`.buffer(…)`、`.conflate()`、`.distinctUntilChanged()`。在 `runTest` 加注入 `TestDispatcher` 的單元測試裡,這些壞法幾乎不可能變紅。
- 噪音估算:一個改 30 行的 ViewModel,約 10 到 15 個選擇點;其中 4 到 6 個是這類。它們每次都存活,每次都要作者處置。
- 另外三個放大噪音的來源:
  - 守的測試只取進行中計劃條款綁的測試。舊程式碼已有的測試沒綁條款,算不進去,所以舊檔案改動時幾乎全部存活。
  - 純重構、搬函式、改縮排會讓整段的選擇點重新出現,身分是 `old` 加 `new`,縮排變了就是新點。
  - Compose UI 的條件(`&&`、`filter`)多半只靠 androidTest 或截圖測試守,而 androidTest 不在守的測試範圍內,必然存活。
- 後果:處置出口只有補測試、寫條款或判不是需求。實務上這會推動作者大量使用 `--judge`(見 t6)。
- 佐證:`scripts/lumos:28105-28120` 的 killed 判定要求失敗輸出歸因到那支測試名(`_kill_attribute`);dispatcher 互換在這類測試裡不會產生斷言失敗。
- 修法方向:這一版表先收「單元測試能分辨」的列,Dispatchers、SharingStarted、flowOn、buffer、conflate 等列移到 REVISIT 之後再加。
- 引句:「`Dispatchers.IO`↔`Dispatchers.Default`、`SharingStarted.Eagerly`↔`SharingStarted.Lazily`」

## t6 照常操作就能讓閘形同虛設,spec 沒有任何偵測
severity: minor
blocking: 否——spec 在天花板 4、6 已承認這幾條,屬已知範圍;但幾條可以便宜地加偵測。
- 位置:〈範圍〉3「換了一樣或不是需求」、〈用詞〉樣式、天花板 4 和 6。
- 作者可以這樣操作:
  - 判斷:`--judge` 的理由只要求「至少 10 實字」,`--group` 一次判整組,只用一句話。判 `not-requirement` 後,同函式同成員同組的未來新點永久自動推定、不擋、沒有到期日。`--consent` 的原話 AI 可自己填(`origin: ai`),屬已接受的信賴原則,不另提。
  - 殺掉:寫一支對任何原始碼變動都紅的測試(例如比對原始檔雜湊),綁一條條款,所有點都被記為 killed。`_kill_attribute` 只要失敗輸出含測試名就歸因。
  - 記錄過期:`test_blobs` 變了只提醒,測試被掏空後 killed 記錄仍然有效。
- 修法方向:對「殺掉點數異常多的單一測試」(例如殺掉不相關函式超過 N 點)出提醒;`not-requirement` 的樣式推定加到期或要求複查;`test_blobs` 變了至少在 `--stats` 列出。
- 引句:「`killing_test` 還在現在守的測試裡;測試本體改過只提醒」

## t7 運算子「兩側都有空白」對行尾運算子是歧義
severity: minor
blocking: 否——照字面實作,常見的多行條件寫法會被漏掉或誤判。
- 位置:〈用詞〉選擇點的運算子規則、天花板 2。
- 問題:ktlint 與 Kotlin 慣例把二元運算子放在行尾,下一行接續,例如 `a &&\n    b` 和 `"x" +\n    y`。右側是換行不是空白字元。spec 沒說換行算不算空白。這些恰好是最常見的 `&&`、`||` 條件,也是 `+`→`-` 的字串串接。
- 佐證:`scripts/lumos:6869` 的 `_strip_c_comments(keep_length=True)` 保留換行,所以換行字元會出現在等長文字裡;spec 沒定義它是否算「空白」。
- 修法方向:明寫「空白含換行」,並補一列 S2 的預期值。
- 引句:「運算子成員只認兩側都有空白的(`a < b`;`List<String>` 的角括號、`a!!`、`!=` 裡的 `!` 不算)」

## t8 生效日的環境變數是推送時一鍵關閉的後門
severity: minor
blocking: 否——只有一條旁路,沒留痕。
- 位置:〈用詞〉生效日。
- 問題:`LUMOS_CHOICE_SINCE` 在推送前設成遠期日期,閘整個不要求,不留任何帳。這跟 `LUMOS_HIGH_RISK_EVIDENCE_SINCE`(`scripts/lumos:14525`)同型,是既有慣例,但在 spec 裡沒有標明風險。
- 修法方向:被覆寫時至少記一筆 `blocked` 以外的 `bypassed` 事件,或在推送輸出印一行提醒。
- 引句:「環境變數 `LUMOS_CHOICE_SINCE` 供測試覆寫;測試總檔比照 `LUMOS_HIGH_RISK_EVIDENCE_SINCE` 預設 9999-12-31」

## t9 〈舊否決比對〉說「沒有翻 d1」,與同段的承認自相矛盾
severity: minor
blocking: 否——只影響決策紀錄的完整性,不影響實作行為。
- 位置:〈舊否決比對〉第一條。
- 問題:`guard殺傷力驗證_計劃` 的 d1 內容是「不做自動變異生成」,`valid: true`,理由是「人宣告的壞法保證語意有變(繞開等價變異)」和「零依賴跨語言工具不內建語言知識」。這份用型錄自動產生壞法,等價問題正面出現,spec 自己也寫「自動產生壞法這件事本身換了答案」。d1 管的是「不自動產生壞法」這個選擇本身,不只是合約配方。這其實就是翻案。
- 修法方向:用 `lumos decision-add` 把 d1 改成限定範圍(只管跨語言通用路徑),或標 superseded 並寫理由,不要靠一句「沒有翻」帶過。
- 佐證:`docs/lumos-toolchain-knowledge/Projects/guard殺傷力驗證_計劃.md:13` 的 d1 與 `valid: true`。
- 引句:「d1 管的是合約的殺傷力配方,這份管的是改動的選擇點,沒有翻 d1;但「自動產生壞法」這件事本身換了答案」

## 已讀,無 finding 的部分
- 範圍 1(`choice-points`)、範圍 5(登記與讀者)、範圍 6、〈回退〉:已讀,交叉引用的符號都存在。核對過的有 `_KNOWN_GATES`(`scripts/lumos:17706`)、`LOOP_NOT_CLOSE_EVENTS`(`:20645`)、`_gov_rows_at`(`:65061`)、`_kt_sit_read_many`(`:40114`)、`_spec_gate_push_bad_head`(`:17373`)、`_backing_kill_rows`(`:77491`)。
- 〈範圍〉4「從 B 版讀」的設計與 `_gov_rows_at` 的簽名(`rev` 參數)一致。
- 〈用詞〉的 `_strip_c_comments(blank_strings=True, kotlin=True, keep_length=True)` 組合在程式碼裡可用,`${…}` 裡的程式碼保留符合 spec。
- 〈舊否決比對〉的另外三筆(高風險測試證據加嚴、guard-kill 的共用函式、前一版 `[near:]`)與這份不衝突。
- 預期值表各列對應〈用詞〉與〈範圍〉的引用都找得到目標;S17 是 `[manual:]`,只是不被機械驗收。
- 天花板 1 到 7 完整:這份能保證的是「表列到的寫法有測試守著」,不是「每個語法選擇都有需求」。使用者大方向裡的「所有語法」目前只做到選擇點表,spec 已在天花板 1 明說。

## 圖譜鏡頭(固定席節點逐條判)
- `docs/lumos-toolchain-knowledge/Systems/guard-kill.md` 的 `t_guard_kill_rc_precedence`(rc 優先序:survived→rc1、drifted/abort/error→rc2):不影響。這份新增的 `source` 是選用參數,不傳維持原行為,rc 計算沒動。
- 同一節點的 `t_guard_kill_json_purity`(`--json` 成功跑完時 stdout 恰一行 JSON):不影響。choice-kill 走 `result_out` 而不是 `--json` 輸出,spec 沒有改 stdout 的格式;不過實作時 `source` 的新參數要確認不會多印診斷到 stdout。

最嚴重:major;blocking 共 5 條
