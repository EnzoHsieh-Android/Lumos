severity: minor

範圍:/tmp/lumos-seat-work/code-審查席唯讀隔離/r4cg(repo HEAD f317b6ce 的乾淨複本)內實測。外掛測試 `claude plugin test mods/claude/lumos-guard` 79 支全綠,與筆記寫的 79 支相符。我另在複本裡逐條改壞程式 22 處(外掛 19、Python 釘行 3 處),結果見各 finding。複本改完都還原。

## 條款對程式與測試(鏡頭 1)結論先講

- S1–S8 修改後的文字跟程式、測試對得上:資料卷別名、`/.vol/`、Glob 大括號、段數上限、會談結束記次數、存回帶版本與重試、存回卡住不拖住派工、`/clear` 保留席、讀回驗段落、讀不到對照表時寫檔與派工擋下、標記判準放寬,各自都有測試。
- 這些改壞後測試會翻紅(各至少一支紅):接線 onTool 一律放行、`/clear` 的 keep 拿掉、資料卷剝除拿掉、`/.vol/` 拿掉、讀不到對照表時派工放行、讀不到對照表時寫檔放行、讀回席位不驗段落、Glob 大括號檢查拿掉、結尾斜線先拿掉再數段數(挪回去紅 2 支)、會談結束世代比對改回只增不減的寫法、存回不重試、存回不設逾時、空 cwd 不退回會談 cwd、NFKC 與剝零寬拿掉、標記連字號變體拿掉、零寬行跳過拿掉。
- Python 端:S11 範本改壞(§7.5 拿掉標記)翻紅;S12 事件帳接線改成用 `e` 取代 `r` 翻紅;S10 派工、工具、會談結束三行釘行,整行換掉會紅。
- 誠實界線新增幾條與程式、型別檔核對屬實:`$.state.set` 的 `ifVersion` 選項與 `isSet` 回傳(型別檔 plugin-authoring/types/claude-code.d.ts:3309-3310)、`session.end` 的 `reason: 'clear'`(同檔 10511-10512)、`FsStat.realPath` 懸空連結不給(同檔 4843-4845)都對得上;計劃寫的 `$.state` 是會談範圍(同檔 3274-3278)與「/clear 後沒實測」那條一致。

### F1 工具呼叫掛鉤的 `.catch` 內容沒有任何東西釘住
severity: minor
blocking: 否 — `.catch` 只在 `onTool` 自己丟錯時才走(`onCall` 已把所有例外吃掉),實際可達性很低;但「接線改成一律放行會紅」這個宣稱在這一條上不成立。
引句:「掛上去的那幾行要原樣釘住(行為由 guard.test.ts 的「接線」那組測)」
最小重現:把 `register.ts` 的 `.catch(($, e, next) => onCallFailed(e, next, seatishOf(st, e)))` 換成 `.catch(($, e, next) => next(e))`,`python3.14 scripts/test_lumos.py -k t_guard_plugin_files_valid` 為 24 passed 0 failed(本機有 `claude`,validate 也只看 hasCatch),`claude plugin test mods/claude/lumos-guard` 為 79 pass 0 fail。S10 的 Python 釘行只釘 `on(...)` 那一行,不含 `.catch` 那行;TS 只測 `onCallFailed` 本身,沒有東西驗它被接上。
修法方向:把 `.catch` 那行也加進釘行清單,或用假的 `on` 收集器直接呼叫 `register` 驗掛鉤與 catch。

### F2 釘行是子字串比對,註解或死碼就能保持綠
severity: minor
blocking: 否 — 要刻意才做得到,但 CI 沒有 `claude`,S10 能擋的只剩這些子字串。
引句:「check(f"S10 {what}的掛鉤只轉交給受測的函式", want in code, want)」
最小重現:在複本把 `on('tool.call', async ($, e, next) => onTool(st, $, e, next))` 改成同一行加 `// ` 前綴、下一行另掛 `on('tool.call', async ($, e, next) => next(e))`,並用 `PATH=/usr/bin:/bin`(模擬 CI 沒有 `claude`)跑 `t_guard_plugin_files_valid`:23 passed 0 failed。S10 的 `sorted(set(...))` 對重複掛鉤也不敏感。
修法方向:釘行前先剝註解與字串,或要求該行恰好出現一次且為行首縮排兩格。

### F3 `makeIo` 的真實存回(`ifVersion`、`isSet`)沒有測試守住
severity: minor
blocking: 否 — 型別檔核對過,寫法與規格相符;只是「撞版重試」這個條款(S7)只對假的 Io 驗過。
引句:「return r?.isSet !== false」
最小重現:把它改成 `return true`,或把 `{ ifVersion }` 改成 `{ ifversion: ifVersion }`,`claude plugin test mods/claude/lumos-guard` 都是 0 fail。`makeIo 接 $.state` 那支只驗 `isSet: true` 與 `saveSeats(..., 3)` 回 true,沒驗帶 `ifVersion` 傳進 `$.state.set`、也沒驗 `isSet:false` 回 false。
修法方向:`makeIo` 測試補一組假 `$.state.set` 回 `{ isSet: false }`,斷言回 false 且收到的第三參數是 `{ ifVersion: 3 }`。

### F4 ` `/` ` 分行與「只有零寬字元的行被跳過」沒有計劃文字、也有測試說法對不上
severity: minor
blocking: 否 — 行為偏安全方向,但文件與測試標題會誤導接手的人。
引句:「for (const raw of prompt.split(/\n| | /)) {」
查證:把它改回 `split('\n')`,測試 0 fail(沒有測試);計劃〈做法〉一只說「跳過『去掉空白後為空』的行」,沒寫零寬行也跳過、也沒寫以 U+2028/2029 分行。測試標題「標記的連字號換成別的橫線、底線、空白,或夾零寬字元:判成寫壞」下第二個斷言卻是 `parseMarker('​\nLUMOS-SEAT: L/r1/s').kind` 為 `seat`(零寬字元獨占一行時合格),計劃寫的是「零寬字元開頭都判寫壞」。兩者在「同一行開頭」才一致,獨占一行時計劃沒講。
引句:「合格與否用原文逐字比(全形冒號、零寬字元開頭都判寫壞)」
修法方向:計劃補一句「只剩零寬字元的行視為空行跳過」,補一支 ` ` 分行的測試,測試標題分開寫。

### F5 `/clear` 保留席之後,計劃與型別檔的「會談結束就刪」說法沒同步
severity: minor
blocking: 否 — 誠實界線與 S7 條款已寫對,只是另外三處舊句還在,三個月後會被讀成互相矛盾。
引句:「會談結束(`session.end`)清掉那個會談的對應與「啟動中」清單,叫醒還在等的工具呼叫,`$.state` 也一併拿掉這場的席。」
同樣舊句還在:計劃〈回退〉「會談結束時外掛自己刪掉那一場的,拿掉外掛後殘留的值沒有人讀」(`/clear` 結束的場不刪),以及 `types/index.d.ts` 註解「session 是所屬會談,會談結束時只刪那一場」。file: `mods/claude/lumos-guard/types/index.d.ts:2`
修法方向:三處都補「`/clear` 結束的場不刪」。

### F6 r3 新增的行為掛在不相干的條款編號下,條款文字也沒寫到它們
severity: minor
blocking: 否 — S1–S8 綁的是「標題以 S 編號開頭的測試」,掛錯號不會讓測試不跑,但回頭對條款時找不到。
引句:「test('S4 派工帶空字串 cwd:退回會談的 cwd,不帶 path 的搜尋照常', async () => {」
同類:`S1 派工接線登記審查席、工具接線把擋下理由轉成 deny`(派工登記是 S6/S7,不是寫檔的 S1)、`S2 資料卷別名…自己的工作資料夾照樣可寫`(放行寫檔是 S1 條款的文字)、`S1 段數上限`、`S7 從 $.state 讀回的席位段落不合規則`(S7 條款文字沒提驗形狀)。S4 條款只講白名單與 Agent isolation,沒有空 cwd 的內容;S2 條款沒提資料卷、`/.vol/`、Glob 大括號。
修法方向:把這幾項寫進對應條款句,或標題改成實際對得上的號;S1–S8 都是 `manual:`,不在 CI 跑,條款句是接手的人唯一的對照。

### F7 兩條「沒實測」的承認沒有拆成回頭條件
severity: minor
blocking: 否 — 照專案鐵則 4,承認風險要把回頭條件拆成獨立一行。
引句:「真引擎熱重載時舊實例在飛的派工會不會先等完沒查」
另一條在 Systems/lumos-guard.md 新增的型別檔段「引擎執行時會不會擋沒實測」。`/clear` 那條有 `REVISIT:2026-11-06`,這兩條沒有,doctor 不會唸。
修法方向:各補一行 `REVISIT:` 或併進現有 2026-11-06 那條。

## 圖譜鏡頭:`lumos impact --diff d0b2439..HEAD` 的固定席筆記逐條判

整條分支共改 87 檔;核心程式只有外掛三支(guard、ledger、少量 ledger 接線)、`scripts/lumos` 6 行(外掛清單加一支、`teardown` 提示字串)、`scripts/test_lumos.py`、範本與兩份 SKILL/reference 的收貨文字。其餘筆記判斷如下。

- Systems/lumos事件帳:受影響(事件帳 `register.ts` 抽出 `onSpawn`、改接線;S12 + Python 釘行)。筆記本身這輪沒改,未見相左,不需再改。
- Systems/lumos-cli-lifecycle ★INVARIANT★(`re-inject` 只覆蓋 sentinel 內):不受影響,diff 沒碰 CLAUDE.md 注入;`scripts/lumos` 只動外掛清單與 `teardown` 印出的字。該筆記已補三支外掛的說明,與程式一致。
- Systems/lumos-cli-read、lumos-cli-write:不受影響,沒改任何讀寫指令。
- Systems/bound-tests-gate、guard-kill、測試假綠形態:受測試檔變動牽連但不受影響;新增的 Python 檢查是釘行而非綁定機制。(建議注意 F2:假綠形態的一種,子字串釘行遇註解。)
- Systems/授權與歸屬、canary-audit、slim-*、節點範圍與索引守衛、check-r/t、cochange、refcheck、loop-convergence、pitfalls-code-loop、reversibility-governance-ledger、judge-severity-gate、core-invariant-baseline、doctor-irreversible-hint:不受影響——只因共改 `scripts/lumos` 而入列,該檔改的是外掛清單常數、一句 `teardown` 訊息與註解,沒碰它們的邏輯。
- Systems/lumos-deinit ★RISK·不可逆★:受牽連但不受影響——`teardown` 多印一個外掛名,實際移除走既有逐支移除流程;對應測試 `t_lumos_plugin_install_edge_cases` 這輪沒改。
- Systems/design-loop ★INVARIANT★:範本與兩份 SKILL 的收貨文字改了(席報告收齊前不落地)。檢查「所有席收齊」那一步沒被削弱,只加了先留在對話裡、到齊再寫進卷證;不影響機械收貨三道。
- Systems/lumos-guard:受影響且已更新(79 支、型別檔段);見 F5、F7。
- Projects/審查席唯讀隔離_計劃:受影響且已更新;見 F4–F7。
- Projects/Claude-mod第二批_計劃、Lumos事件帳_計劃:不受影響——交棒脈絡外掛(`lumos-context`)這輪沒動,事件帳條款文字沒改。
- Projects/規格落成可驗收條件、引用座標依實際換行、異常派工單回報輸入錯誤、逃逸自動記、雙向門放行、公開精簡版_實作計畫、code側刪除傳播守衛_實作計畫、test-layers軟提醒、舊句檢查:不受影響,只因共改 `scripts/lumos`、`test_lumos.py` 入列。
- 表態記錄:py-eventloop 寫「整支沒有 async def」——針對的是探針腳本,與本輪外掛無涉;我沒有要反駁。

總結:最嚴重 minor,blocking 0 條
