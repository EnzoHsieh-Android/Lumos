severity: major

# 代碼審 r3 合約與圖譜鏡頭(席:合約圖譜-sonnet)

做法:在 /tmp/lumos-seat-work/code-審查席唯讀隔離/合約圖譜-sonnet-tmp/c(git clone 自 seat-guard 工作樹,HEAD 90afb403)跑測試與改壞實驗;沒動 repo 本身。
基線:`claude plugin test mods/claude/lumos-guard` 63 全綠、lumos-ledger 25 全綠;`python3.14 scripts/test_lumos.py -k plugin` 135 全綠、`-k license` 11 全綠;`lumos lint` 對 Systems/lumos-guard、Projects/審查席唯讀隔離_計劃、Systems/lumos-cli-lifecycle 各 0 問題;`lumos spec-gate` 風險高、13 條只綁了 3(S9–S11)、靠人 10(S1–S8、S12、S13)、S9–S11 三支綠。

改壞實驗(臨時複本,逐點改一行再跑 `claude plugin test`):
- 註冊檔最後一段接線改掉(tool.call 永不回 deny / agent.spawn 直接放行 / session.end 不呼叫 onEnd / 把 agent.spawn 掛鉤換成直接 next):63 全綠、0 紅(四種各一次)。
- makeIo 的真實路徑查詢改成回原路徑:63 全綠。
- AGENT_TYPES_OK 多塞一個類型:63 全綠。
- 其餘 10 處(cwd 取值、state 鍵、glab、send-email、逾時提示、ended 檢查、FOLDERS_ROOT、aboveStaging、…):都翻紅,綁條款的測試守得住。
- Python 端:同樣把 tool.call 接線改成永遠放行後跑 `-k guard_plugin`:24 通過 0 失敗(t_guard_plugin_files_valid 沒紅)。
- scripts/lumos 的 `_LUMOS_PLUGINS` 拿掉 lumos-guard:t_guard_plugin_files_valid 與 t_install_registers_guard_plugin 翻紅,守得住。
- 事件帳:onSpawn 的 `spawnEvent(e, r)` 改成 `spawnEvent({}, r)`:ledger 25 全綠。

### F1 守衛外掛的接線(register)整段沒有測試,改成永遠放行仍全綠
severity: major
blocking: 是 — 條款 S1–S8 的測試只呼叫 createGuard、checkTool、onCallFailed,從沒走過 register;接線改壞則整個隔離關閉而所有測試仍綠,同一類缺口代碼審 r1 在事件帳已判為要修(spawnEvent)
引句:「return deny === null ? next(e) : { deny }」
引句:「return st.guard.spawn(session, cwd, e, next)」
最小重現:在臨時複本把 register.ts 該行改成 `return next(e)` 後跑 `claude plugin test mods/claude/lumos-guard` 得 63 pass 0 fail,`python3.14 scripts/test_lumos.py -k guard_plugin` 得 24 passed 0 failed。同樣的結果出現在 spawn 接線改成 `next(e)`、`session.end` 拿掉 `await onEnd(st, e)`。makeIo 的 `$.fs.stat(...).realPath` 也從沒被真引擎驗過(只有 S13 一次性真機)。
三個月後的人讀計劃以為「S1–S8 綁了測試、改壞會紅」,實際上綁的是純函式;唯一碰到接線的是手動 S13(一次性、計劃自己標 manual),而 S10 只驗掛鉤名稱與 `.catch` 存在。事件帳那邊同一條教訓(代碼審 r1「原本測試只測 spawnFields,把接線改回 e.agentId 照綠」)的做法是把整組參數抽成純函式再測;守衛這邊 `onCall` 的「deny 轉成 { deny }」「spawn 轉交」「end 轉交」沒有套同一做法。
修法方向(只指方向):把 tool.call 的 deny→回傳物件、spawn、end 的接線各抽成可注入純函式並測,或在 S10 加一條針對註冊檔「掛鉤內有回 deny 的分支」的靜態斷言。

### F2 事件帳 S12 的「孫代理那筆 agent 欄」只測純函式,接線改壞仍全綠
severity: major
blocking: 是 — S12 條款宣稱的可觀察行為是 spawn 事件的發起方,實際接線 onSpawn 沒測試,改壞全綠;與 F1 同根因、同一類
引句:「await recordEvent(st, $, spawnEvent(e, r))」
引句:「子代理派的孫代理那筆的 `agent` 欄應是那個子代理的編號」
最小重現:臨時複本把 lumos-ledger 的 register.ts 該行改成 `spawnEvent({}, r)`,`claude plugin test mods/claude/lumos-ledger` 得 25 pass 0 fail(agent 欄會恆為 null,正是這次要修的 bug)。
補充:代碼審 r2 的「拆成三個變數再傳」設計把傳參縮成一行,但那一行本身(傳 e 還是別的)沒有測試咬住;onSpawn 的 e 是引擎物件,測試無法造。

### F3 計劃 S5 與做法一寫「沒接冒號的一般派工不擋」,程式與測試卻判寫壞並擋下派工
severity: minor
blocking: 否 — 是文件對不上程式(程式較嚴、錯在安全方向),不會讓隔離失效
引句:「只是提到 lumos-seat、後面沒接冒號的一般派工不算」
引句:「expect(parseMarker('LUMOS-SEAT 外掛的 bug 查一下').kind).toBe('bad')」
說明:程式的 SEAT_LOOSE_RE 只要求「去掉修飾後以 lumos-seat 開頭、後面不是英數或連字號」,不要求冒號;所以任何 session(含主會談)派出第一行是 `LUMOS-SEAT 外掛……` 或 `lumos-seat 資料夾` 的一般派工都會被擋下並說「寫壞」。計劃 S5 條款、做法一第二條都還寫「接冒號」。測試註解承認「代碼審 r2 起改判寫壞」,但計劃沒回寫。三個月後有人在這個 repo 裡派「lumos-seat 外掛的測試怎麼跑」之類的子代理會被擋,翻計劃只會得到相反的說明。

### F4 S1 條款寫「大小寫不同的都應擋」,同條的測試與做法卻是大小寫不同也放行
severity: minor
blocking: 否 — 條款措辭自相矛盾,程式行為(折小寫放行自己的資料夾)與做法二·2 一致
引句:「大小寫不同或經過連結指到外面的都應擋」
引句:「expect(await chk({ tool: 'Edit', file_path: '/private/tmp/LUMOS-SEAT-WORK/L/S/new/dir/b.txt' })).toBe(null)」
說明:條款 S1 與它綁的測試方向相反。若條款意思是「大小寫別名指到工作資料夾以外的」,應改寫;現在字面上照條款實作會把 macOS 上合法的大小寫寫法擋掉。

### F5 計劃 S8/做法二·6 說「非審查席子代理的 Bash 出錯照常放行」,實際接線對任何子代理都擋
severity: minor
blocking: 否 — 是文件過期;行為較嚴且 Systems/lumos-guard 的 PITFALL 已寫對,但計劃主文沒回寫
引句:「主會談與非審查席子代理的 Bash 出錯照常放行(代碼審 r1)」
引句:「return typeof id === 'string'」
說明:seatish 對任何字串編號回 true;`seatishOf` 在 guard 為 null 也回 true;`lookup` 讀 `$.state` 出錯時 `call` 對該子代理的 Bash 一律回 BASH_ERROR。所以「非審查席子代理」的 Bash 在掛鉤出錯、`$.state` 讀不到時都被擋。測試 'S8 掛鉤出錯時:主會談與非審查席的 Bash 照常' 用 `seatish=false` 呼叫 onCallFailed,這個值在真實接線中對子代理永遠不會出現,等於測了一條走不到的分支(測試假綠形態的第④型)。另外 'S8 查路徑丟出意外錯誤:非 Bash 放行,Bash 判斷出錯擋' 的標題說非 Bash 放行,斷言卻是 Read 被擋(realOf 把所有查路徑錯誤當不存在、最後走到 null),標題與斷言相反。

### F6 筆記與驗證紀錄的測試數目過期
severity: minor
blocking: 否 — 數字漂移
引句:「TEST:claude plugin test mods/claude/lumos-guard(條款 S1–S8,49 支」
引句:「`claude plugin test mods/claude/lumos-guard`,49 支全綠」
file: `mods/claude/lumos-guard/hooks/guard.test.ts`(實跑 63 支全綠)
說明:代碼審 r2 又加了 14 支,Systems/lumos-guard 的 TEST 行與 Verification/2026-10-06_審查席隔離實作 的第一節仍寫 49,「改壞 25 處、11 處」的覆蓋說明也沒涵蓋 r2 新增的組別。三個月後的人用 49 當基準會以為少了測試。

### F7 計劃寫「不叫人改用 Grep 工具」,程式與 r3 折入紀錄叫人用;對應測試是空轉
severity: minor
blocking: 否 — 文件對不上程式;測試守不住它的宣稱
引句:「不叫人改用 `Grep` 工具:有些建置沒有 Grep、Glob」
引句:「expect(r.includes('Grep 工具') ? r.includes('Grep 工具(有的話)') : true).toBe(true)」
說明:做法二·4 與 d4 之前的描述不叫人改用 Grep,r3 折入紀錄寫「擋下理由教改用 `Grep` 工具」,程式實際字串是「搜字可用 Grep 工具(有的話)」。測試標題「不再叫人改用 Grep 工具」與程式相反,而斷言在訊息裡沒有「Grep 工具」時恆為真(條件式回 true),把整段提示拿掉也綠,所以它沒守住任何一邊。

### F8 只有四段範本帶標記,辯方席、規格符合席、SDD 派工沒有,誠實界線沒列
severity: minor
blocking: 否 — 範圍界定問題,沒寫進誠實界線
引句:「§7.6 架構對齊、§7.8 資安四段的派工詞第一行加」
說明:計劃白話段說「設計審、代碼審派出去的審查員」都被隔離,但 templates.md 只改 §1、§3、§7.6、§7.8;§2/§4 辯方席(吃的是席位 finding 文字,等於被審材料的二手轉述)、§7.5 規格符合席、§5/§6 SDD 實作與 reviewer、設計審首輪的便宜前掃 agent 都沒有標記,等於沒有隔離,且誠實界線只寫「標記靠派工詞第一行:編排者漏寫」。S11 只盯四段,新增一種派工範本時不會紅。三個月後的人讀「審查席隔離」會高估覆蓋面。

### F9 守衛擋掉的指令包含計劃與驗證紀錄自己指定的驗證指令,誤擋清單沒列
severity: minor
blocking: 否 — 屬已接受的誤擋類別,但最常用的一條沒記
引句:「外掛自己的測試要在本機跑:`claude plugin test mods/claude/lumos-ledger`(CI 沒有 Claude)」
引句:「路徑最後一段剛好是這些字的(例 `git diff -- mods/claude`)也會被擋,是接受的誤擋」
說明:`claude plugin test mods/claude/lumos-guard` 的詞 `claude` 命中 BASH_WORDS,審查席(例如審這支外掛的席)被派工詞叫去跑它就會被擋;`git log -- mods/claude` 同樣。實作計劃的「誤擋」段只舉 `grep -rn "git push" docs`、`command -v gh`。這與 REVISIT 2026-11-06 的誤擋統計相關,建議把它列進誤擋清單,否則審這支外掛的席會一再撞牆。⚠ 判不準:這是依規則推論(`bashBlock` 本身有測試斷言 `claude -p x` 被擋),我在無守衛環境沒能用真席位實測。

### F10 安裝維運手冊只列兩支外掛,漏了已合併的 lumos-context
severity: minor
blocking: 否 — 說明文件不完整
引句:「裝 Claude 外掛 `lumos-ledger`(事件帳)與 `lumos-guard`(審查席隔離)」
說明:同一次 diff 的 lumos-cli-lifecycle 寫「事件帳、交棒脈絡、審查席隔離三支」,`_LUMOS_PLUGINS` 與 teardown 提示也是三支,唯獨 skills/lumos-project-notes/commands/07-安裝維運.md 這列只寫兩支。

## 圖譜鏡頭:LUMOS-IMPACT d0b24391..HEAD 固定席逐條判
(尾端固定席節點;`lumos impact --diff` 於複本實跑,節點與合約行以下列為準)
- Systems/lumos-cli-lifecycle ★INVARIANT★ re-inject 只覆蓋 sentinel 之間:不影響。本次只動「Claude 外掛」節與 `_LUMOS_PLUGINS`,沒碰 CLAUDE.md 注入路徑;綁定測試 t_reinject_preserves_outside 屬 -k 範圍外,我跑的 plugin 子集與 license 子集全綠。節點本身已同步更新(多支外掛、測試名),`lumos lint` 0 問題。
- Systems/lumos事件帳:受影響且已同步。S12 修正與市集列三支;見 F2(接線測試缺口)。節點沒登記合約行。
- Systems/lumos-cli-read ★INVARIANT★ search 預設排除 superseded:不影響。diff 沒碰 search/濾網;`lumos search` 實跑隱藏 8 筆作廢結果,行為如合約。
- Systems/bound-tests-gate ★INVARIANT★、Systems/guard-kill、Systems/測試假綠形態、Systems/canary-audit:diff 只命中 scripts/lumos 與 test_lumos.py 的外掛清單段,不碰 code-loop check 的綁定測試真跑或殺傷力配方。測試假綠形態的「現場成立前置斷言」精神與 F1、F5(走不到的分支)相關,視為提醒不是破壞。
- Systems/授權與歸屬 ★INVARIANT★ 授權與 SPDX:不影響。新增的 mods/claude/lumos-guard 不在 _VENDORED_TOOLKIT,t_license_headers_travel_with_vendored_files 與 t_deinit_never_deletes_user_license 在 `-k license` 11 全綠。
- Systems/slim-install-安裝器、slim-uninstall-一行卸載、slim-get-一行安裝(★INVARIANT★ 一組):不影響。它們管 CLAUDE.md 的 LUMOS-SLIM 注入、manifest 與 .ps1,diff 沒碰 install.sh、uninstall.sh 或精簡版;`lumos teardown` 只改了確認訊息文字。
- Systems/design-loop ★INVARIANT★ 處置閘第五步(計劃有 [SN] 時條款要綁測試):影響到計劃本身。`lumos spec-gate Projects/審查席唯讀隔離_計劃` 結果條款 13 條全標、句式與回退節通過;S1–S8、S12、S13 走 manual 而非 test,規則允許,但這正是 F1、F2 的缺口所在。
- Systems/lumos-deinit ★RISK·不可逆★:不影響。只改了 uninstall 說明文字與 teardown 確認提示;不碰 vault 的 rmtree 四重閘。
- Systems/lumos-guard:新節點,about_code 列了六支檔,lint 0 問題;計劃的 RULE 行 [依據:審計][since][retire:人裁][until][confirmed][test] 俱全。內文有 F5、F6 的過期處。
- 其餘 ★RISK·守衛面★ 節點(loop-convergence-recording、pitfalls-code-loop、reversibility-governance-ledger、check-r-guard、cochange-guard、check-t-sentinel、lumos-refcheck、doctor-irreversible-hint、judge-severity-gate、core-invariant-baseline 與數篇舊計劃):只因 scripts/lumos 或 test_lumos.py 檔案命中,diff 內容為外掛清單常數與訊息字串,不碰它們管的邏輯,判不影響。
- 圖譜沒有釘到節點的機械反查三格皆空:本次實際有節點命中(上列),代表那段備援與本席查到的不同,不矛盾。

總結:最嚴重 major,blocking 2 條
