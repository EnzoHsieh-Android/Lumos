severity: major

### F1 pickMain 漂移守衛用「逐字比對」,既有守衛用「共用案例檔」
severity: major
blocking: 是 — 引入第二種做法(同一類跨語言/跨份漂移,已有 rules-fixture.ts 案例檔做法,本案另起逐字比對)
引句:「用 `scripts/test_lumos.py` 的漂移守衛比對它跟事件帳外掛那份逐字相同」
佐證:既有做法是 mods/claude/lumos-ledger/hooks/rules-fixture.ts 放案例(RULES.main),Python 端 t_ledger_rules_match_reader 與 ledger.test.ts 兩邊各跑同一批案例,比的是行為而非文字(file: `scripts/test_lumos.py:70210`,`mods/claude/lumos-ledger/hooks/rules-fixture.ts`)。逐字比對的問題是:註解或空白一改就假紅,實作改寫但行為相同也紅,反過來完全不驗行為。plan 還自己寫「事件帳那份又已經由 rules-fixture.ts 對齊」,等於承認有一條案例檔做法卻不沿用。建議 lumos-guard 的測試也跑 RULES.main 案例(外掛只能匯入自己資料夾,測試檔可以直接讀事件帳那份 fixture 或各留副本再比 fixture 本身)。另 S14 綁的 t_guard_pickmain_matches_ledger 沒說會不會把 guard 加進 rules-fixture 的對照。

### F2 擋下理由三段式的寫法跟既有慣例只近似,沒指明沿用哪一套
severity: minor
blocking: 否 — 命名/錯誤處理不一致但結構對
引句:「`{ deny: "<一句擋了什麼>;<為什麼>;<該怎麼做>" }`」
佐證:內容順序(擋了什麼、為什麼、怎麼做)與專案「發生什麼→為何在意→指令獨立一行」三段式同序,方向一致;但既有 hook 的擋下是 `{"decision":"block","reason":…}`(file: `scripts/hooks/claude/check-graph-sync.py:1099`),且「指令獨立一行」這點本案寫成同一句用分號串,沒有提到要不要換行。plan 的例句是單行。建議明寫沿用三段式、指令部分換行獨立。S1 綁「理由帶『審查席不准寫 repo』」只驗了第一段,S2、S3 沒有等效條款,三類擋下的理由格式不統一(⚠ 我沒找到機械釘住既有三段式的測試,判不準其強制程度)。

### F3 標記 LUMOS-SEAT 的格式與解析跟 LUMOS-IMPACT/SPEC 不是同一套
severity: minor
blocking: 否 — 命名一致(LUMOS-前綴、獨占一行、取第一行),但解析規則是另寫的一份
引句:「逐行找 `LUMOS-SEAT: ` 開頭的行,取第一行;值照 `<迴圈編號>/<輪次>/<席名>` 切三段」
佐證:既有解析是 `^LUMOS-IMPACT:\s*(\S+)\s*$` 與 `line.strip()` 後 match,逐行取第一個(file: `scripts/hooks/claude/dispatch-lens-hook.py:25`、`:26`、`:144`)。本案是「開頭」比對(沒說 strip、沒說行尾空白、沒說冒號後多空白),語言又是 TypeScript,等於第二份獨立實作,且沒有任何跨語言守衛(Python hook 不讀 LUMOS-SEAT,所以不是衝突,但 S10 要「用外掛同一條格式規則檢查」範本,規則怎麼從 TS 進到 Python 測試沒交代,很可能又是第三份重寫)。另既有標記值是單一 `\S+`,本案值內帶 `/` 且允許中文,屬合理擴充,但應寫成錨定的完整正則並放進共用案例檔。

### F4 安裝流程改多外掛:沿用既有骨架,但改動範圍列太少,多處寫死單外掛
severity: minor
blocking: 否 — 結構沿用(清單化、各裝各移、各步獨立),但細節不一致
引句:「`_LEDGER_PLUGIN` 單一常數改成外掛清單,`_sync_claude_plugin` 與 `_teardown_claude_plugin` 對清單裡每一支各裝各移」
佐證:既有流程寫死單一外掛的點不只這兩個函式:`_LEDGER_MANUAL` 手動指令二元組(第二條是移市集,只該做一次不該每支各移)、`_plugin_sync_msg` 與 teardown 訊息硬寫「事件帳外掛」、`_ledger_user_plugin` 以 `_LEDGER_PLUGIN` 比對、`_ledger_market` 與市集移除(file: `scripts/lumos:21886`、`:21915`、`:21951`、`:22027`)。plan 沒說:①市集移除要等清單全部移完才做一次;②回傳狀態字串(ok/absent/no-source/failed)在多支時如何合併(S8 說「任一支失敗只影響自己」,但函式回單一狀態);③`_LEDGER_*` 名稱要不要改成通用名(沿用 `_LEDGER_` 前綴裝 guard 會誤導)。這些不補,實作時容易長出第二套平行函式。S8 與 t_ledger_plugin_files_valid「市集只列一個外掛」改成「恰好是清單那幾支」方向對。

### F5 行為測試的綁法跟事件帳外掛不同(⚠)
severity: minor
blocking: 否 — ⚠ 判不準:只能看出綁定名稱風格不同
引句:「[test:t_guard_seat_write_repo_denied]」
佐證:事件帳外掛的行為測試是 `ledger.test.ts` 裡以 `claude plugin test` 跑的 TS 測試(`test('S13 …')`),Python 側的 t_ledger_* 只做檔案/安裝/跨語言對齊(file: `mods/claude/lumos-ledger/hooks/ledger.test.ts:97`、`scripts/test_lumos.py:69604`–`:70210`)。本案 S1–S7、S12、S13 都綁 Python 風格名稱 t_guard_*、t_ledger_spawn_records_parent,卻是 TS 外掛核心邏輯的行為;是要在 test_lumos.py 包一支去呼叫 TS 測試,還是沿用既有「TS 測試標題以條款編號開頭」的綁法,plan 沒講。plan 的 PRIOR-ART 又說「測試做法全部沿用事件帳」,與此不一致。

### F6 落點新開 Systems/lumos-guard:合理
severity: clean
blocking: 否 — 符合鐵則 5(每支程式檔有家;外掛檔另有一個管它的 Systems 節點),且市集檔、安裝流程的家仍在既有兩篇
引句:「落點:新開 `Systems/lumos-guard`(管外掛檔);市集檔的家仍是 [[Systems/lumos事件帳]]、安裝流程的家仍是 [[Systems/lumos-cli-lifecycle]],只在那兩篇補一句」
佐證:既有外掛檔 mods/claude/lumos-ledger 的家是 Systems/lumos事件帳(file: `docs/lumos-toolchain-knowledge/Systems/lumos事件帳.md`),本案新開一篇管新外掛,再於舊兩篇補一句,做法一致。唯一小提醒:`lands_in` 只列了 lumos-guard,但實際會改 scripts/lumos、scripts/test_lumos.py、skills/lumos-design-loop/templates.md、事件帳外掛 register.ts(S13 順手修),各檔的家也得在 lands_in/改動說明中出現,否則 pre-commit 的家檢查會擋(⚠ 未逐檔確認其 about_code)。

四問摘要:
1 分層與依賴方向:外掛只匯入自己資料夾、核心可注入、事件帳外掛不加拒絕只由 guard 擋,分層與既有一致,未見跨層直呼(F4 的實作細節除外)。
2 命名與錯誤處理:外掛名 lumos-guard、目錄 mods/claude/lumos-guard、LUMOS-SEAT 前綴與逐行取第一行都一致;fail-open 與事件帳「只觀察」精神相容;擋下理由見 F2、解析規則見 F3。
3 第二種做法:pickMain 守衛是第二種做法(F1);安裝清單化沿用骨架但細節未盡(F4);標記解析另寫一份(F3)。
4 落點:合理(F6)。

不對齊共 5 條,其中 major 1 條
總結:最嚴重 major,blocking 1 條
