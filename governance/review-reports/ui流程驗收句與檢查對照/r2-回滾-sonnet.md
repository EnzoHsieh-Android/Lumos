severity: major

審查範圍:回滾鏡頭,對照 r2-snapshot.md 與 r2-delta.patch,並開 `scripts/lumos` 與範本腳本核對。

入口盤點(會寫紀錄、判定、擋下或放行的入口):
- (a) 範本腳本寫 steps.json 的 `evidence.debug`。
- (b) judge 寫 `runs.blocks.ui[].checks`。
- (c) `_e2e_record_err` 驗型別。
- (d) 推送檢查的新擋下條。
- (e) `--check-config` 與推送檢查共用的格式檢查。
- (f) 第 7 條對分岔點舊紀錄的比對。
- (g) 第 8 條只列不擋。
- (h) 放行子指令 waive。

## 前置與緣起、實測、做法第 1~3 條
已讀,無 finding。三個新鍵被舊版 lumos 靜默忽略,而 e2e 段整段算進指紋,所以退版後算出的指紋不變(`_e2e_fingerprint` 的 `canon` 整段 hash)。

## 做法第 4 條(judge 記事實)

1. 工具鏈組合錯配時,新流程被擋、使用者無法靠重跑或 AI 放行解開。
   - 範本腳本只有在 `EVIDENCE` 為真時才帶 `--debug-output`,否則 `evidence.dir` 是 `None`(`scripts/templates/android-e2e-run.sh:495-501`)。這發生在 Maestro 沒有 `--debug-output` 的版本,也發生在專案裡留著舊版 vendored 範本腳本。
   - 這時 `evidence.debug` 沒有值,judge 對每支流程記 `checks: null`。
   - 第 5 條再把每支新流程擋下(`checks` 是 null → 讀不到執行紀錄)。
   - 擋下訊息的下一步只印「改設定或流程再跑整套」,不附放行指令(第 5 條「不附 AI 放行的指令」)。
   - 實際上重跑同樣讀不到,AI 放行蓋不過,人放行又沒有指令可抄。
   - 使用者只剩 `LUMOS_SKIP_ANDROID_E2E=1` 整道關掉。
   - spec 沒有為「Maestro 或範本腳本不支援 `--debug-output`」這個前提寫退路,也沒寫 `evidence.debug` 在 `EVIDENCE` 為假時該記 null 還是不記。
   - 引句:「子目錄零個或超過一個、檔不在、讀不懂,都記 `checks: null` 加原因。」
   - file: `scripts/templates/android-e2e-run.sh:330` 與 `:495-501`。

severity: major
blocking: 是,照字面實作會讓合法環境(舊 Maestro 或舊範本腳本)的新流程永遠擋下且無處理指令。

## 做法第 5 條(推送檢查)

2. 人放行寫成「蓋得過」,但擋下訊息不給人放行的路,而且舊的人放行會悄悄蓋過新規則。
   - 現行 `_cl_say_e2e_block` 只印 `_e2e_waive_hint`,而放行記成人還是 AI 取決於有沒有互動終端。
   - 第 5 條與 S12 要求新規則的擋下訊息不印放行指令,所以人放行在使用者面前沒有入口。
   - 另一面:放行綁指紋,新規則上線前人因別的原因(裝置誤擋)寫的放行,指紋沒變就同樣蓋過零檢查、單向門這幾條。
   - 退版或混用時,舊版 lumos 寫的人放行會讓新規則靜默失效,而 spec 沒有區分放行的原因。
   - 引句:「放行只有人放的(`by` 是 human)蓋得過這幾條;AI 放行蓋不過」
   - file: `scripts/lumos:41713` `_e2e_waiver_ok` 只驗 `by`(human 或 ai)與 `note`,沒有放行原因欄。

severity: major
blocking: 是,字面實作會有兩種結果:要嘛人無路可放行,要嘛舊放行誤蓋新規則。

3. 「更新 lumos 後重跑」的訊息對「沒有 `checks` 欄」這個情境指錯原因。
   - 沒有 `checks` 欄的紀錄,可能是舊版 lumos 寫的,也可能是退版後的舊 lumos 重新覆寫的。
   - 舊版 lumos 對同一份紀錄做 `_e2e_record_update`,`_put` 會整個換掉 `rec["runs"]`,`checks` 隨之丟失。
   - 使用者重新升級後,分支上已提交的紀錄全被判成「舊版寫的」,要重跑實機。
   - spec 的回退一節沒有講這個代價(見 finding 4)。
   - 引句:「紀錄是舊版 lumos 寫的,更新 lumos 後重跑」
   - file: `scripts/lumos:41100-41135`

severity: minor
blocking: 否,影響是訊息精度與重跑成本,資料救得回(重跑即可)。

## 回退一節

4. 回退一節的宣稱不完整,漏了指紋連動。
   - 專案層「情境拿掉三個新鍵」會改變 e2e 段 canonical hash,所有既有通過紀錄的指紋失效,每個分支都要重新整套實機驗收。
   - spec 第 1 條格式檢查其實講了「三個鍵改了,舊的通過紀錄自然失效」,但回退一節沒有引用,也沒有把「要退就得全部重跑實機」寫成代價。
   - 同節把「要撤」寫成「只能還原工具鏈」,卻沒說還原工具鏈後專案裡的新鍵可以保留(舊 lumos 忽略),兩層回退的先後順序也沒講。
   - 引句:「專案層:情境拿掉三個新鍵,就不做逐句對照;但新情境的 `one_way` 必填,拿掉會被擋(要撤也只能還原工具鏈)。」
   - 引句:「既有查證紀錄多出的 `checks` 欄被忽略即可」
   - file: `scripts/lumos:40829-40841` 指紋含 e2e 段整段雜湊。

severity: major
blocking: 是,回退一節是 spec 自己宣稱的退路,漏掉全數失效的代價且與「拿掉新規則的程式就回到現在的行為」那句有出入。

5. `E2E_SCHEMA` 不升版,新型別嚴驗讓未來混用走到「刪掉紀錄」。
   - S4 讓 `_e2e_record_err` 對 `checks` 型別不對判「讀不懂」,擋下走 `bad_record`,訊息叫人「修好或刪掉」。
   - spec 沒提 `E2E_SCHEMA` 要不要升。若下一版調整 `checks` 形狀(例如這份 spec 自己預告的 S14 實測可能改欄位),舊的新版 lumos 會把新紀錄當壞紀錄,而不是走 `newer_schema` 的「更新 lumos、紀錄不要動」。
   - 同一份紀錄被兩種版本的 lumos 輪流讀寫時,使用者會被叫去刪掉真正有效的紀錄。
   - file: `scripts/lumos:40854-40855`、`:42005-42006`、`:68482`。
   - ⚠ 這個情境依賴 S14 實測後改欄位,屬未來版本,先判小。

severity: minor
blocking: 否,目前這一版沒有改欄位形狀,屬升版紀律。

## 做法第 6、7、8 條
已讀,無 finding。
- 第 7 條對分岔點舊紀錄缺 `checks` 時只印一行,不擋,混用安全。
- 第 8 條只列不擋,不寫紀錄。

## 驗收條款與實務隱患
已讀,無 finding。
- 逐類(金流、對外送出、不可逆、守衛面):不可逆那條「拿掉新規則的程式就回到現在的行為」大體成立,補充見 finding 4。
- 守衛面已標命中,走設計審。
- 資源類(大檔、深層巢狀)有專用上限,與本鏡頭無衝突。

## 落點、審計修正紀錄
已讀,無 finding。

最嚴重 severity: major;blocking 共 3 條(finding 1、2、4)。
