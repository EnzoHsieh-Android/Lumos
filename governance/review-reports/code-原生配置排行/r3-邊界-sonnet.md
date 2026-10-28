severity: minor

整份只有兩條小問題,都不擋推送。兩條歸因都是修復造成,證據是算式與實跑函式,沒有在實機重現逾時。

## 1. 收尾預留 120 秒小於停錄加拉檔的上限
severity: minor
blocking: 否,只在拉檔卡住的極端情況下發生,會讓整步被 e2e 砍掉,但不產生錯誤的判定。
引句:「NATIVE_TAIL = 120   # 秒:第二段驅動跑完之後停錄、拉檔、查詢的預估」
file: `scripts/templates/android-stability-collect.sh:35`(對照 `:28` STOP_WAIT 預設 30、`:25` T_SHORT 120、`:345` stop_record)
歸因:有證據的修復回歸(算式證據)。
- 修前 `NATIVE_MARGIN = 180`(`git show 07642d8e:scripts/templates/android-stability-collect.sh` 第 34 行),註解寫明留給停錄最多 STOP_WAIT、拉檔 T_SHORT 與寫結果檔。
- 修後 `NATIVE_TAIL = 120`、`NATIVE_FINISH = 15`。
- 最壞情況的算式:
  - 修前:驅動到 end-180 截止,加停錄約 35、拉檔 120、查詢 1,約在 end-24 結束。
  - 修後:驅動到 end-120 截止,加同樣的 156,約在 end+36 結束。
- 具體場景:預算 3600,第二段驅動跑到截止時間,wifi adb 拉檔卡到 T_SHORT 逾時。收集腳本會越過 e2e 的上限,整步被砍,第一段的 stability.json 沒寫出,e2e 判成裝置卡住。這正是這個機制要避免的連累。
- 順帶:`left(NATIVE_FINISH)` 在 `max(1.0, …)` 的下限下,這時查詢只拿到 1 秒,必然逾時。
- 規格〈打算怎麼做〉第 3 步明文寫 120 秒,程式照規格做,所以是規格數字的洞。⚠ 逾時時序未在實機重現。

## 2. 「時間不夠」的原因文字出現負數和四捨五入的矛盾
severity: minor
blocking: 否,只是原因字串精度,不影響跑不跑的判定。
引句:「return True, "failed", f"時間不夠,不跑第二段(第一段 {elapsed:.0f} 秒,這一步只剩 {remaining:.0f} 秒)"」
file: `scripts/templates/android-stability-collect.sh:584`
歸因:有證據的修復回歸(新文字)。修前的訊息是印絕對上限 `{float(budget):.0f}`,沒有這個問題。
修後我用 `native_skip` 實跑:
- elapsed=0、remaining=119.9 時 `(True, 'failed', '時間不夠,不跑第二段(第一段 0 秒,這一步只剩 120 秒)')`。讀的人會以為 120 秒剛好夠(0×2+120 不大於 120),其實因為 119.9 而被跳過。
- remaining=-5(上限已過)時印「只剩 -5 秒」。

## 已驗主張(零 finding 的項目也留證據)

**查詢範本**
- 差分模糊測試:3000 組隨機資料,涵蓋 ERROR 偽框架、NULL 或空 mapping、`!` 路徑、淨留量 0、負數、±1 位元組、未配對的 free、非 libc.malloc 的 heap_name。修前(07642d8e)與修後(eeae9e15)的 `.sql` 輸出逐列相同,差異 0。
- 淨留量 0 的過濾不改結果,原因:
  - `agg` 以 `>= 1048576` 篩,0 淨留量的呼叫點加不進任何總和。
  - 呼叫者排序裡正值必勝零值。
- 手造資料驗卡線:
  - 剛好 1048576 列出,1048575 不列。
  - 配了又還到 0 的不列。
  - 系統與非系統的同名 .so 分兩列。
  - 並列時有名字的排在「?」前面。
  - 整條只有配置器時記「?」。
  - ERROR 偽框架當呼叫位置時記「?」,當呼叫者時記「?」。
  - `…/base.apk!libn.so` 取 `!` 之後的部分。
- 超過 200 個並列時,Python 端 `sites[:200]` 正確截斷。
- 效能:合成 5k、10k、40k 個葉子的查詢耗時 1.6 秒、3.4 秒、15.3 秒,線性成長。
- 真的 trace_processor v58.2 對空 trace 跑修後 SQL,語法可跑,輸出格式為 `"rows","","","",0,0,0`。

**收集腳本**
- 時間上限:實跑 `sh android-stability-collect.sh`,下列值都回 2 並印「擋下:LUMOS_STABILITY_STEP_BUDGET_S 要是大於 0 的秒數」:nan、inf、1e309、0x10、0、-1、-0、abc、單一空格。
- " 30 "、0.5 與空字串通過上限檢查。`"1_0"`(Python 的 float 接受,等於 10)也通過,算作可接受。
- 從 `native_skip` 取出實跑:
  - 剩下秒數剛好等於預估(100 與 320)時會跑。
  - 少 0.001 時跳過。
  - 第一段 0 秒、剩 120 時會跑。
  - 剩下秒數是 None、也就是沒設上限時,不管多大都會跑。
  - android_sdk 為 None、29 時是 unsupported,30、31 時會跑。
- `native_query` 用假 `tp_rows` 驗:
  - hex 奇數長度、retained 不是數字,都回「輸出看不懂」。
  - 沒有 rows 行、rows 為 0,都回「沒錄到原生配置記帳」。
  - stat 列會被回報。
  - 逾時時原因是「算不了…:逾時(1.0 秒)」,符合規格。
  - 非法 UTF-8 用 replace 解碼,不拋例外。
  - 超過 200 列時截到 200。
- 不算 finding 的觀察:site 或 stat 列欄數不是 7 時會被靜默丟掉,可能把壞輸出變成「沒有 1 MiB 以上」的 ok。真的 trace_processor 的 hex 欄不含逗號,我給不出實際會發生的場景,所以沒標。
- 錄製收尾順序(G2):`state.get("rec")`、`abort_record`、再 `state.pop`,收的那幾秒被中斷時 cleanup 仍收得到,邏輯成立。
- 設定驗證:實跑 `lumos macrobench --check-config`,以下被擋下:
  - 重複的清單項、null、字串、數字、巢狀清單。
  - 不存在的情境(含 `__proto__`、大小寫不同的 `X`)。
  - 含 ESC 的名稱,錯誤訊息裡已被清掉。
  - 空清單與合法情境通過。

**lumos 讀結果檔**
- 15 種怪形狀都不噴例外、回傳碼 0,包括:
  - reason 是整數或含控制字元。
  - retained 是布林、浮點、負數。
  - status 是清單、`sites: null`。
  - 最外層是清單、`symbol` 是字串。
  - `enabled: false` 但帶 ok 的 sites。
- retained 為 10**30 時用整數算 MiB,不溢位。
- 函式名 200、201、500 字的截長和 `--json` 清理成立。
- 只有控制字元的函式名會印成空白欄,不崩。
- `--json` 在 250 個 site 時剛好留 200 個。
- 對修後版本實跑 `scripts/test_lumos.py -k android_native`,208 通過、0 失敗(在 snapshot 副本跑,沒動 repo)。

未驗:實機 adb 與 heapprofd、真實大型 pftrace、e2e 整體跑。

## pitfalls manifest 15 條
- android-stability-collect.sh 第 263 行、第 316 行的 `open(` 資源題:誤報。兩處都是 `open(...).read()` 立刻讀完,臨時檔案物件隨即釋放,是既有慣例。
- 第 489 行的 `time.sleep(SETTLE)` 效能題:誤報。它在 `fresh_launch`,不在迴圈裡,只睡一次。
- android-stability-native.sql 的 12 條「N+1」(第 18、22、24、53、62、76、79、82、85、89、91、93 行):全部誤報。整支是單一語句裡的 CTE,不在應用程式迴圈裡被反覆呼叫。
- `arch_alignment` 附的 rtrim 的 sargable 疑慮:誤報,對記憶體中的小表做字串運算,沒有索引可言。我實跑確認 rtrim 的邏輯對 `/` 與 `!` 兩種路徑都正確。

## 圖譜鏡頭
- 固定席節點:lumos-cli-read(search 不排除 stale)、guard-kill(rc 優先序與 JSON 純度)、lumos-cli-lifecycle(re-inject)、design-loop(處置閘第五步)、bound-tests-gate(綁定測試真跑),都與這份 diff 無關。diff 只動 macrobench 的 native_retained、android-e2e-run.sh、收集腳本與兩支範本。
- 測試假綠形態的 INVARIANT 對測試檔有效,測試由另一席看,本席不判。
- loop-convergence-recording 與 pitfalls-code-loop 沒有 INVARIANT 行,只列為家。
- 沒有附「這次新增的殘留」段,也沒有備援段。

## 修復與保持對照(兩種結果分開報)
- **G1 時間上限**
  - 修復效果:預估與驅動截止共用 NATIVE_TAIL 這點成立(算式證據,上面的邊界實跑),測試也通過。
  - 殘留是 finding 1 與 2。
  - 保持:查詢逾時仍寫 failed 且原因帶「逾時(N 秒)」(`native_query` 假 `tp_rows` 驗過)。
  - 修前證據:只做了讀碼(07642d8e 版的 `deadline` 與 `NATIVE_MARGIN`),沒有在修前版本跑同一案例,所以修前行為是未判定。
- **G2 收錄製順序**:修復成立(讀碼)。保持:Terminated 與 KeyboardInterrupt 仍往上丟,由 cleanup 收錄製。
- **G3 命名**:只是改名,preflight 的 native 參數保持。這個行為由測試覆蓋,通過。
- **G4 查詢省工**:修前修後輸出相同(差分 3000 組,差異 0)。至於省多少工,同一個 20000 葉子合成資料實測約 10.4 秒對 7.7 秒,是單次量測,不穩定,標未判定。
- **G6 `--json` 清理**:實跑 ESC、雙向覆寫字元被換空格,保持。
- **G5 測試覆蓋、G7 文件**:G5 是測試案例,由另一席看。G7 是文件,本席拿到的差異只含正式程式,未判定。

## 三問
1. **原問題的修復效果**:G4 的輸出等價和 G6 的清理有行為證據。G1、G2 有讀碼和算式證據,沒有實機證據。
2. **修補處的正常、錯誤與相鄰路徑**:正常路徑與錯誤路徑(預算非法值、查詢逾時、意外例外)都成立。相鄰的「拉檔卡住時的尾端」是 finding 1,最壞情況比修前差。
3. **新發現同一案例的修前修後**:
   - 案例 1(拉檔卡住):修前 end-24,修後 end+36(算式,未實測)。
   - 案例 2(119.9 與 -5):修前文字印絕對上限,沒有這個問題。修後如 finding 2。

最嚴重 severity:minor;blocking 條數:0。
