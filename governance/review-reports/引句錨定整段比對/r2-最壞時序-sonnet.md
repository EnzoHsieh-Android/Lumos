severity: major

我沒建任何實驗目錄,也沒改 repo。所有結論來自讀 `scripts/lumos` 和 `scripts/test_lumos.py`,沒有實跑。

先講「照字面判出什麼」的總表。五種最壞時序裡,兩種(寫側出錯、同輪混版)設計是對的,三種(舊版讀新章、舊章靜默降級、停用後工具脫鉤)有洞。

1. 同一輪幾席用舊版記、載體用新版記:已讀,無 finding。
   - 處置閘只讀載體那一筆的章。`_loop_status_disposal` 裡 `_qsrc = carrier`,非載體席的報告引句閘從不判。
   - 所以載體蓋新章、其他席沒章,不影響判定,這是想要的。
   - 反方向(舊版載體加新版其他席)也一樣,載體沒章就判 legacy,跟它當年寫側放行的判準一致。
2. 寫側通過到寫入之間出錯:已讀,無 finding。
   - 章是 `rec` 裡的一欄,和帳同一行 `json.dumps` 一次 append,不存在章與帳分開寫。
   - 檢查通過後若材料 sha 變動就 `return 2`,帳和章都不落。
   - 唯一殘餘是 `_jsonl_append_verified` 讀回失敗時帳已寫、章也已在。這是既有行為,與本設計無關。
3. 回放凍結後帳本行被人手改:設計對。
   - 刪章、改章都會讓 `all_row_shas` 對不上,回報「帳被動」紅燈。
   - 凍結前手改沒有任何偵測,見 F2。

## 1. 舊版程式讀蓋章帳:同一個 `_REPLAY_ENGINE_REV` 下無從察覺,巢狀引句那類會判紅
severity: major
blocking: 是
引句:「別台機器仍跑舊版程式時:它記的帳沒有 `quote_rule`,處置閘照舊判準重算,跟它當時寫側的檢查一致,不卡」
file: `scripts/lumos:9969` `_REPLAY_ENGINE_REV = "d5-2026-08-25"`(spec 決定不推進它)
file: `scripts/lumos:1224` 回放以 `engine_rev` 相等才重算

1. 時序:
   - T0:機器 B(新版)記 r2 載體,引句是 `「規則「甲」其實存在,規則乙也在。」`,蓋 `full-span-v1`。
   - T1:機器 A(舊版)拉到這份帳,跑 `loop status L --disposal`。
   - 舊判準把引句截在內層。〈量測〉說這類有 45 組:前半 `規則「甲` 不足 10 字,判錨不到。
   - A 的處置閘判紅。
2. 同一時序換成回放:B 凍結 r2 並提交 golden。A 的週跑回放因為 `engine_rev` 相同,不會跳過重算,用舊判準重算後報「邏輯漂移」。
3. 〈實務隱患〉只寫了舊版「寫」帳的方向,沒寫舊版「讀」新章帳。〈回退〉的完整還原段承認了同一個後果,但只當成「還原提交」的代價。實際上只要有一台機器或一個舊分支還沒更新,就會發生。
4. 不推進 `_REPLAY_ENGINE_REV` 的理由是「推了會讓黃金抽查跳過」,這個理由成立。但代價是舊版完全沒有「我太舊」的訊號。
5. 預期的處理:
   - 兩階段上線。第一個提交只讓讀側認得 `quote_rule`,並對未知值明確報錯。確認各機器都更新後,第二個提交才讓寫側開始蓋章。
   - 或者在 spec 把「讀者先於寫者上線」寫成上線條件。

## 2. 沒有章的帳靜默照 legacy 判,上線後這條路永遠開著,而且判定輸出不寫用了哪一版
severity: major
blocking: 是
引句:「有值就照那一版判;沒有這一欄就照舊判準 `legacy`——沒有這一欄的帳是舊版程式寫的」
file: `scripts/lumos:26405` 通過時只印「N 條引句全數錨定」,不印判準版本
file: `scripts/lumos:10542` `rec` 有 `ts` 欄,但 canary 帳沒有逐列雜湊

1. 時序:
   - T0:上線,`_QUOTE_RULE_WRITE = "full-span-v1"`。
   - T1:一台停在舊版的機器,或舊分支上的席,記一筆載體,報告是 `「合法前綴文字至少十個字」編造後半根本不在審材裡」`。
   - 舊寫側放行,沒有章。處置閘照 legacy 判過,印 `DISPOSAL GATE PASS ... 引句全錨定`。這就是 Issue 要擋的造假,仍然過關。
2. 「沒章 = 舊版寫的」這個前提,在上線日之後不成立:
   - 沒章的帳也可能是舊版機器寫的,也可能是手改刪章。
   - 帳上有 `ts`,但設計刻意不用時間,結果上線後的沒章帳跟上線前的沒章帳在輸出上分不出來。
3. 手改刪章:
   - canary 帳沒有逐列雜湊,凍結前刪章無任何偵測。
   - 刪章只會讓判準變寬鬆或變紅,不會繞過 v1 的新擋法。但一個本來就沒走 v1 寫側的帳,不會被補查。
4. 預期的處理(不需要時間切換,只要可見):
   - 處置閘輸出一行「引句判準:full-span-v1(帳上章)」或「legacy(帳上無章)」。
   - 沒章且 `ts` 晚於上線日時加一行警告。比對走既有的 `_loop_ts_key`,只警告不擋。
   - 這樣 RETIRE-IF 的 8 週觀察窗也數得到有多少沒章的漏網帳。

## 3. 測試只造「一輪一列」,實作讀錯列(例如 `latest[-1]`)不會翻紅;回放不變與停用兩個核心宣稱沒有任何測試
severity: major
blocking: 是
引句:「回放:凍結閉包裡的帳是整行原樣(含 `quote_rule`),重算照章判,判定不變」
file: `scripts/test_lumos.py:26922` `t_quote_full_span_rule_stamped_on_ledger`,每個 loop 只記一列載體
file: `scripts/lumos:26319` 同一段程式裡 `_qsrc = carrier if carrier is not None else latest[-1]` 已有一個取列分支

1. 取列錯誤沒有測試守:
   - 處置閘取章的列要是 `carrier`,不是 `latest[-1]`。
   - 現行程式碼的零發現分支就用 `latest[-1]`,實作者很可能照抄。
   - 測試只有單列輪,載體就是最後一列,實作取錯也全綠。
   - 要加的案例:同輪先記蓋章載體(後半編造),再記一個沒章的非載體席,預期判紅。
2. 回放宣稱沒有測試:
   - S1 到 S6 沒有一條跑 `loop replay --freeze` 再回放。
   - 「不推進 engine_rev 仍零漂移」只靠上線前人工抽 20 個。
   - 應補一條:凍結一個蓋章輪,回放判定不變;手刪章後回放紅燈。
3. 停用沒有測試:
   - 沒有案例把 `_QUOTE_RULE_WRITE` 改成 `"legacy"` 後驗證三件事:新帳蓋 `legacy`、寫側放行前綴照抄的後半編造、既有 v1 帳仍判紅。
   - 〈回退〉整段只靠文字。
4. S5 的 `rw.returncode == 2` 沒斷言帳本沒有新增一列。若實作先 append 再擋,測試照綠。

## 4. 章的值域沒定義:null、空字串、非字串、大小寫
severity: minor
blocking: 否
引句:「未知的 `quote_rule` 值(例如將來新版程式寫的、本版不認得):處置閘判失敗並寫明」
file: `scripts/lumos:9661` `_GOV_FIELD_TYPES` 沒有 `quote_rule`,各種型別都被容忍

1. 輸入 `"quote_rule": null` 或 `""`,用 `.get()` 讀會和「沒這欄」無法區分,靜默降成 legacy,繞過「未知值判失敗」。
2. 輸入 `"quote_rule": ["x"]`(手改或別的工具寫入),如果拿它去查字典會 `TypeError`,處置閘出 traceback。回放走同一條路。
3. 訊息「請用新版程式問閘」只適用將來版本寫的章。手改或打錯字的章會被誤導去升級程式。
4. 預期:沒這欄才是 legacy;有這欄但不是字串,或不在集合內,一律判失敗,訊息分「可能是新版寫的」與「章格式不合」兩種。

## 5. 停用後,手動 `quote-check` 與 `seat-check` 跟帳上的章脫鉤,〈回退〉「三者始終一致」不成立
severity: minor
blocking: 否
引句:「寫側、處置閘、回放三者始終一致。這個改動碰 `scripts/lumos`,照常走代碼審。」
file: `scripts/lumos:10960` 寫側擋下時印的診斷指令是 `lumos quote-check {report} --spec {snapshot}`,沒帶 `--rule`

1. 時序:
   - T0:r2 載體蓋 `full-span-v1`。
   - T1:`_QUOTE_RULE_WRITE` 改成 `"legacy"`。
   - T2:處置閘看到 r2 的章是 v1,判紅。
   - T3:人照慣例跑 `lumos quote-check <報告> --spec <快照>`,預設用 `_QUOTE_RULE_WRITE`,也就是 legacy,印「全數錨定」。
2. 閘說紅、診斷指令說綠,而且 spec 沒要求閘在失敗訊息裡指出用了哪一版。這和 F2 的輸出缺口是同一個。
3. `seat-check` 同理,對舊輪的報告用的是現在的寫側常數,不是該輪的章。
4. 預期:閘的失敗行印 `lumos quote-check ... --rule <帳上的章>`;〈回退〉的「一致」改寫成只涵蓋閘與回放。

## 6. 擋下事件 note 沒有唯一碼,同一秒連撞會被 gov 去重折成一次
severity: minor
blocking: 否
引句:「note 帶 `quote-rule=full-span-v1` 與不合的類別,REVISIT 到期有資料可數」
file: `scripts/lumos:10938` 同檔既有的擋下事件在 note 裡帶 `id={uuid.uuid4().hex[:8]}`,註解說明是為了避免 gov 去重折成一次

1. 時序:同一席在同一秒內連撞兩次(例如腳本迴圈重試),兩筆 note 相同。
2. 既有的作法是 note 末尾帶 `id=<uuid 短碼>`,並用 `hard=True`。spec 只寫「帶判準與類別」。
3. REVISIT 要「數 quote-rule 擋下事件」,折疊會讓分母偏小,誤傷率偏高估。
4. 預期:S6 的 note 規格補上 `id=` 短碼,並補一個連撞兩次的案例。

總結:最高等級 major,blocking 共 3 條
