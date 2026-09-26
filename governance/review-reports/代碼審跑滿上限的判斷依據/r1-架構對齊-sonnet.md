severity: major

## F1 折入走勢訊號另開一套算法,沒接到既有的每輪問題數趨勢欄位/G2 閘
severity: major
blocking: 是
引句:「每一輪折入幾條(帳本的折入清單,整輪各席加總)。判成「下降」(最後一輪少於前一輪,且少於第一輪的一半)/「持平或上升」」

專案裡「每輪問題數的走勢」這個訊號已經有機械算法在跑,不是空白地帶:
- `file: \`scripts/lumos:9111\`` —— `lumos loop verify-progress` 早就把 `findings_trend: [r.get("findings") for r in rounds]` 當成標準輸出欄位,逐輪列出問題數。
- `file: \`scripts/lumos:9758-9763\`` —— full-basis gate 的 G2 步驟已經在判「每輪找到的問題數有沒有遞減到零」(單調不增、末輪 ≤1 且末輪=0 或末步嚴格下降),這條閘正是 `loop next`(`scripts/lumos:10663-10668`,② full-basis gate 委派)在跑的。

計劃的「訊號 1:折入走勢」是另外重新設計一套逐輪計數與門檻(最後一輪 < 前一輪且 < 第一輪一半 / 持平或上升),資料來源改用 `folded_set` 而非 `findings`,門檻邏輯也跟 G2 不同,但沒有在計劃裡交代「為什麼不延伸/複用既有的 `findings_trend` 或 G2 判斷式」。計劃的 PRIOR-ART 段落明講「機制層面沿用既有的 `loop next`⋯既有帳本欄位與凍結審材、既有 quote-check 的引句定位,不加新依賴」,但實際上對「逐輪趨勢」這塊沒有沿用既有那兩處,而是另立第二種算法——即使 `findings` 和 `folded_set` 語意不完全相同(前者是回報總數、後者是處置後折入數),兩邊都是「逐輪問題數列表 + 遞減/持平判斷」同一形狀的東西,理當在計劃裡說明為什麼不能借用既有的 `findings_trend`/G2,而不是默默重建一套。

## F2 --finding-class 沒有比照既有 --finding-kind / --finding-severity 的全集驗證慣例
severity: minor
blocking: 否
引句:「記帳新增選填旗標 `--finding-class <id>=<短名>`(編排者填,例如「靜默回空」「守衛假綠」)」

`file: \`scripts/lumos:7744-7757\`` 的 `--finding-kind`(`id=code|spec|process`)與 `file: \`scripts/lumos:7761-7776\`` 的 `--finding-severity`(`id=clean|minor|major|blocker`)是這個專案裡同構的「逐條發現打標籤」旗標,兩者都在寫入側強制「給了就要覆蓋全部 `findings-set`,少標一條就 rc2 擋下」(`if set(kinds) != F: 擋下…`)。

計劃裡的 `--finding-class` 是同一個 `id=值` 形狀(甚至連命名前綴 `--finding-` 都一樣),但計劃全文沒有提到要不要比照這條「給了就要覆蓋全集,否則擋下」的規則——摘要只說「沒填就印「沒填類別,判不了」」,沒交代「填了但只填一部分」該怎麼處理。跟隔壁兩支已經定型的旗標比,這是命名撞到既有慣例、但錯誤處理沒講清楚要不要一致,算命名/錯誤處理層級的不對齊,不到引入第二種底層機制的程度。

## 已看,無

- **分層與依賴方向(問 1)**:計劃打算把報告函式從 `loop next` 的 cap-reached 分支(`scripts/lumos:10677-10678`)與 `loop status --disposal`(`scripts/lumos:18265` 起)兩處呼叫,只讀帳本與凍結審材、不回頭改判定——這跟既有的「觀測不進合取」尾段寫法(`_disposal_clause_step`/`_disposal_security_step`/`_disposal_landing_step`,`scripts/lumos:18067`/`18153`/`18214`,以及 disposal 尾端的「審查有沒有用」漏斗 `scripts/lumos:18549-18552`)同一種呼叫方向:由 next/disposal 呼叫獨立的唯讀報告函式,不是報告函式反過來呼叫 disposal/next。方向一致。唯一要註記的是:既有的「審查有沒有用」漏斗目前明文跳過 code 迴圈(`not str(loop_id).startswith("code")`,`scripts/lumos:18541`),而這份計劃的對象正是 code 迴圈——這不是不對齊,只是新報告要自己撐住 code 迴圈這個既有漏斗沒管的象限,提醒實作時注意別套錯了跳過條件。
- **讀帳失敗處理(問 2 的另一半)**:計劃講的「讀到寫一半的最後一行要當沒這行,不得整段報錯」跟 `cmd_loop_next` 已經在用的 `_loop_records`(`scripts/lumos:9908-9911`,`json.loads` 失敗就 `continue`)是同一種寬容讀法,對齊。（`_loop_status_disposal` 對「整份帳有壞行」是另一套 fail-closed 規則,`scripts/lumos:18279-18285`,但那是擋別的問題——帳面損壞不是並發寫一半——計劃的措辭沒有把這兩種情境混為一談,不算違規。）
- **落點(問 4)**:`Systems/loop-convergence-recording.md` 自己讀起來是 171 行、`about_code: scripts/lumos`、帶 4 條 `decisions`、正文已經記過好幾次「在既有 disposal 七步合取上加一步新的觀測段落」的先例(摘要裡 2026-09-08 加⑤條款綁定、2026-09-11 加⑥資安席),形狀跟這份計劃要做的事(在 disposal/`loop next` 再加一段唯讀觀測輸出)完全同類,落這篇是對的。**以程式碼/筆記本體為準**:機器附加參考資料寫這篇「掛 0 份計劃、14 行 KEY、0 條合約」,跟我直接讀到的內容(遠不止 14 行 KEY、有 4 條 decisions)對不上,判斷仍以我自己讀到的檔案內容為準,沒有採信附加參考的數字。

不對齊共 2 條,其中 major 1 條。
