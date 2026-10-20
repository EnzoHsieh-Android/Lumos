severity: minor

我只審了 `r3-repair-lumos.patch` 裡 scripts/lumos 的修補。三個問題都不會讓不合格的推送被放行,最糟是整道誤擋或訊息誤導。

## 1. 審查紀錄的觀察時間設成 9999-12-31 時,仍然整道 evaluation_error
severity: minor
blocking: 否

引句:「d.astimezone(_dt.timezone.utc)      # 換到 UTC 會溢位的極端值(0001-01-01T00:00+05:00)在讀進來這一層就判看不懂」

這次修補(邊界席 E2)想讓極端時間在讀進來那一層就判成看不懂。它只擋了「換到 UTC 會溢位」的那一邊。

`9999-12-31T23:59:59Z` 能通過 `_secev_iso`,後面在 `_secev_judge_review` 做 `obs + timedelta(days=90)` 時會丟 OverflowError。這個例外不是 ValueError,也不是 `_SecevDataError`,`_secev_judge_item` 接不住。所以只要一筆 review_record 帶這個值,所有護欄的判定都跟著丟掉。

重現:用 python3.14 -B 載入單函式,傳入 `observed_at="9999-12-31T23:59:59Z"`、`expires_on="2026-11-01"` 的審查項。
- 修後 474346765:`EXC OverflowError date value out of range`。
- 修前 7655a12d:同樣的 OverflowError。
- 對照 `observed_at="2026-10-21T00:00:00Z"` 時,兩版都回 `([], 'ai')`。

歸因:有證據的原有漏查。修前修後結果相同,不是修補造成的回歸。但 E2 想關掉的「極端日期造成整道出錯」這一類,實際還開著。

我沒有跑完整的 `security evidence` 管線,所以沒有看到 `evaluation_error` 實際印出來。整道出錯是照 `_secev_judge_item` 沒接這個例外、以及 lumos:10803 的整道錯誤處理推得。

## 2. `_SecevDataError` 從頭到尾沒有任何地方丟出它
severity: minor
blocking: 否

引句:「except _SecevDataError as e:」

`grep -n _SecevDataError` 在修後版只有兩處,一處定義、一處 except。修前版沒有這個名字。

因此「單項壞只讓那一項 invalid」這條路現在是死碼。把寬的 except 收窄之後,凡是讀證據那一層沒先檢查型別、冒出的 TypeError、KeyError、IndexError、ValueError、AttributeError,都變成整道 evaluation_error。

我另外試了這幾條讀取路徑,沒找到會漏出例外的輸入:
- JUnit:空檔、BOM、UTF-16、重複身份、`name`/`classname` 為空、巢狀 testsuite。
- SARIF 與 k6 的型別閘:程式碼走讀,未實跑。
- test-quality 收據的型別:程式碼走讀,未實跑。

所以目前是死碼加一道沒有真實觸發者的防線,不是已經炸開。「有宣告卻沒有實作的收口」是內部不一致,要報。

歸因:未判定。修前版沒有這個類別,修後版沒有使用者,沒辦法比較。

## 3. 新的收據原始碼比對假設 cwd 就是 repo 根
severity: minor
blocking: 否

引句:「pre = cwd.rstrip("/") + "/"」

`_secev_tq_rel` 把快照路徑去掉收據 cwd 前綴後,直接當成 repo 相對路徑。

我跑了幾個輸入:
- cwd 是 `/r/backend`、路徑是 `/r/backend/src/a.py`:得到 `src/a.py`。提交樹裡實際的路徑是 `backend/src/a.py`。這種收據會判 `receipt_source_changed`,訊息卻說「收證之後這幾支檔改了」,實際沒改。
- cwd 是 `/r/backend`、路徑是 `/r/shared/lock.json`(在 cwd 外):得到 `None`,判 `receipt_source_unmapped`。
- 檔名帶空白或中文(`/r/空 白/中文.py`):得到 `空 白/中文.py`,沒問題。
- cwd 是 `/`:得到 `x.py`,沒問題。

只要在子目錄收證(monorepo 常見),`fault_sensitivity` 就一定被誤擋,而且訊息會誤導。這不會放行錯的東西,補救是改從 repo 根重收。

我沒有造完整收據端到端跑,只驗了 `_secev_tq_rel` 這個函式。它取代的是另一支函式,不是 `_secev_tq_rel` 本身(`_secev_tq_rel` 是新增),新舊對照不成立。

歸因:未判定。這是修補新增的檢查,修前版沒有可比的行為。

## 回答三問

1. **原問題的修復效果,有行為證據的部分:**
   - `_secev_iso` 擋掉 `0001-01-01T00:00:00+05:00` 與 `9999-12-31T23:59:59-05:00`,都回 None。這兩個值換到 UTC 會溢位,不是修補的新增問題。
   - `_secev_mainline_override` 的行為我造臨時 repo 跑了兩個對照,結果都對:
     - 主線 tip 版沒有 config 時,回 None(視為沒設)。
     - config 寫了不存在的遠端 ref 時,回 `mainline_unknown`。
   - `_cl_sec_block_lines`:
     - 缺威脅類別時,「在意的原因」講護欄層,不再講故障證據。
     - gate_detail 帶換行或 ESC 時,進輸出前會被 `_secinv_show` 跳脫。
   - `_secev_exception_shape`:
     - 非 dict、缺 `covers_kinds` 或 `compensating`、型別怪的情形,都走回碼,沒有看到 traceback。

   沒驗到的有三項:「超過上限」只讀了程式碼,沒有真造 16MB 的檔;逾時路徑沒實跑;核可鏈符號連結守衛沒實跑。

2. **修補處的正常、錯誤與相鄰路徑:**
   - 超過 12 筆時印「…另有 1 處」,剛好 12 筆不印,邊界正確。
   - `_secev_main_side_trace` 的上限 50:剛好 50 個 tip 會逐個查,51 個回 None 走完整判定。
   - 到期日恰在今天:`exp < ctx.today` 才算過期,當天仍有效,與註解一致。
   - `_secev_target_host` 沒被這輪動到;我順便跑了大小寫、IPv6、帳密、反斜線、百分比編碼、空主機和超大埠號,結果都偏保守或正確。
   - `_secinv_lines_text` 對 `_SECEV_CONST` 常數沒有造成輸出變形;`_SECEV_CI_STEP` 含換行,但不經這條路。

3. **新發現的同一案例在修前、修後各是什麼結果:**
   - 發現 1:兩版都是 OverflowError。
   - 發現 2 與 3:無可比的修前行為。

零回歸保證不成立:我沒有跑 test_lumos 全套,也沒有端到端跑 `security evidence`。

最嚴重 minor,blocking 共 0 條。
