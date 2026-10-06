severity: minor

驗證方式:在 /tmp 的 --shared 臨時複本(提交 01dd1f2f)實跑。外掛測試 90 支全綠;`t_guard_plugin_files_valid` 25 條全綠;`lumos lint` 對 Systems/lumos-guard 與 Projects/審查席唯讀隔離_計劃 各 0 問題。測試數「90 支」與 grep 到的 test( 數、`claude plugin test` 輸出一致,Verification 與 Systems 兩處都寫 90,對得上。條款 S1/S2/S5/S7 新補的每一句,都找得到對應測試(`/.vol/`、段數上限加結尾斜線、資料卷別名擋 Read/Grep、Glob `..` 與大括號巢狀、格式字元、空白與底線要接冒號、`/clear`/resume 保留席、舊派工不扣新計數、撞版提示、空字串 cwd)。

改壞驗證(13 處,每處用完還原):
- 12 處翻紅:`end` 的 keep 提早返回拿掉(3 支紅)、`reason === 'resume'` 拿掉、`release` 改成不比對自己那份計數、`version ?? 0` 拿掉、撞版 toast 拿掉、`Promise.race` 存回上限拿掉(2 支紅)、`\p{Cf}` 換回只剩零寬、底線與空白寫法不接冒號、Glob `..` 判斷拿掉、Glob 大括號巢狀拿掉、大括號內絕對路徑拿掉、U+2028 分行拿掉。
- 1 處沒翻紅:見 F1。

Python 端釘掛鉤(鏡頭 1 的重點)另做 5 種改壞,全翻紅:
- 接線改成一律放行、原行留在 `//` 註解裡:紅(「工具呼叫的掛鉤只轉交…」)。
- 原行包在 `/* */` 裡:紅,而且 `claude plugin validate` 也紅。
- 原行放進樣板字串、另掛一條放行:「每個事件只掛一次」紅。
- 影子掛鉤加死碼:紅。
- 拿掉派工的 `.catch`:紅。
所以「去註解再比」確實擋得住「接線改成一律放行」與「原行留在註解」。

### F1 擋下派工理由改字沒有測試守住
severity: minor
blocking: 否 — 只是提示文字,不影響擋不擋;但 r4 紀錄與條款附註宣稱的「理由不再叫人刪掉第一行」沒有東西守
引句:「是審查席就修好第一行再派;不是審查席,第一行別用 lumos-seat 這個詞開頭(改寫第一行,不用刪內文)。」
實驗:把 register.ts 的這句改回「不是審查席,拿掉這行」,外掛 90 支測試與 Python 測試照綠(0 fail)。Systems/lumos-guard 的 TEST 行寫「r2、r3、r4 的修正各自逐條撤回驗過會翻紅」,這一條是例外。建議補一支斷言理由含「改寫第一行」或不含「拿掉這行」的測試,或把紀錄改成「除理由文字外」。

### F2 做法一節的會談結束段沒跟上 `/clear`、resume 保留席的新語意
severity: minor
blocking: 否 — 誠實界線與回退節已寫明例外,但「做法」是接手者先讀的設計段,讀到的是舊說法
引句:「會談結束(`session.end`)清掉那個會談的對應與「啟動中」清單,叫醒還在等的工具呼叫,`$.state` 也一併拿掉這場的席。」
這一句(做法一的最後一條,本輪 diff 沒動)對 `reason` 為 clear 或 resume 的結束現在不成立:程式 `end(session, keep)` 在 keep 時直接返回,不清啟動中清單也不刪 `$.state`。「回寫進設計」的 r4 紀錄說已回寫,但 grep 計劃全文,做法一節沒有任何 clear 或 resume 的字。三個月後的人從做法讀會以為 /clear 也會清。建議在這句補「(`/clear` 與接續結束除外,見誠實界線)」。

### F3 新增的風險承認沒各自帶獨立的回頭條件行,且舊句沒刪
severity: minor
blocking: 否 — REVISIT 都在、日期合規、lint 0 問題;只是寫法違反 CLAUDE.md 鐵則 4「那一句本身搬成獨立一行、原行刪掉那一句」
引句:「- `/clear` 與接續結束的會談不刪席,行程活得越久、清越多次,舊會談的席越多,沒有回收(代碼審 r4 併發席)。」
- 這條「沒有回收」的承認本身沒有緊跟的 REVISIT;它的回頭條件被併進 162 行另一條 `REVISIT:2026-11-06 實測一次 /clear 與 --resume…;順便看 /clear 與接續留下的舊會談席有沒有長到要定上限`,一行兩件事(實測 + 定上限),且沒有給「長到多少算要定」的門檻,不像相鄰那條有「單場超過一百席」。
引句:「新實例不知道這一席,它的第一批工具呼叫會放行(代碼審 r3 併發席在單元層重現;真引擎熱重載時舊實例在飛的派工會不會先等完沒查)。」
- 「沒查」這句沒實測的承認還留在原行,同時又在下一行新增 REVISIT,等於同一件事講兩次;lumos-guard.md 的型別檔那段同理(括號裡的「引擎執行時會不會擋沒實測」已刪、改成獨立 REVISIT,這一處做對了,可當這兩條的對照)。

### F4 S10「只掛三個事件」那一檢查仍比對含註解的原始碼
severity: minor
blocking: 否 — 只會誤紅不會漏放(註解裡寫 `on('x.y'` 會讓它紅),實測不構成繞過
引句:「check("S10 只掛派工、工具呼叫、會談結束三個事件",」
同一個測試函式裡其他新檢查改用去註解後的 `live`/`reg`,只有這條仍用 `code`。不一致而已,建議一併改用 `reg` 或在註解說明刻意。

### 圖譜鏡頭:LUMOS-IMPACT 固定席筆記逐條判
- 機械反查三格皆空(受影響測試、共改、呼叫者皆 0),我自己查:改動檔 `mods/claude/lumos-guard/hooks/register.ts`、`guard.test.ts`、`types/index.d.ts` 的家是 Systems/lumos-guard(本 diff 已更新其 TEST 行、新增三處刻意不同的說明與 REVISIT),`scripts/test_lumos.py` 的測試綁在條款 S10。判:家節點有跟著改,不漏。
- Projects/審查席唯讀隔離_計劃 的 S1、S2、S5、S7 條款:與程式及測試一致(見上方驗證),S9–S13 本輪沒動,不受影響。
- Systems/lumos-guard 的 `RULE:外掛原始碼不呼叫 $.process…`(有 since、retire:人裁、until、confirmed):本輪沒引入 $.process、沒改寫輸入,測試 25 條全綠,規則仍成立,不影響。
- 該節點新增「三處跟另兩支外掛寫法不同」:①`onTool` 匯出、②存回帶版本、③Python 端從原始碼抽 `SEAT_RE`(test_lumos.py 72258 行確實有 `^const SEAT_RE = /(.+)/$` 的抽取),三句與程式一致。
- Systems/lumos事件帳、Systems/lumos-cli-lifecycle:本輪沒碰事件帳程式與安裝流程,不影響。
- Verification/2026-10-06_審查席隔離實作:90 支與實測一致;但它仍寫「S1–S8」而 90 支裡的條款標籤實際只分布在 S1 至 S8(S7 有 27 支),吻合,不影響。
- `lumos doctor` 對 guard 相關無新告警(輸出的 c2 是無關的舊 Issue)。

總結:最嚴重 minor,blocking 0 條
