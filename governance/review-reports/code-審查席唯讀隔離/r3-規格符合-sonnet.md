severity: minor

# 代碼審 r3 規格符合審查(審查席唯讀隔離)

做法:讀完計劃(S1–S13、d1–d6、範圍、誠實界線)、程式 patch 與筆記 patch;在 /tmp 臨時複本(`git clone --shared`,HEAD 90afb403)跑 `claude plugin test mods/claude/lumos-guard`(63 支全綠)與 Python 綁定測試(`-k guard_plugin`、`-k seat_templates`、`-k lumos_plugin_install_edge`、`-k plugin_market` 全綠);`spec-trace` 13 條款 0 懸空。另在複本把外掛程式改壞 8 處看測試紅不紅(結果見 F3)。

## 條款對照

| 條款 | 程式位置 | 綁定測試 | 判定 |
|---|---|---|---|
| S1 寫檔 | register.ts checkTool 的 Write/Edit/NotebookEdit 分支、realOf、workDir | guard.test.ts 的 S1 五支 + 超長路徑、/var/tmp、NFD 席名 | 符合 |
| S2 暫存處擋讀 | checkTool 的 Read、Grep/Glob 分支、searchBase、inStaging、aboveStaging | S2 五支 + r1 組一 | 符合(改壞 Glob 固定段、aboveStaging 各有測試翻紅) |
| S3 Bash 粗擋 | bashBlock(切詞、最後一段、BASH_STRINGS、1MB) | S3 四支 + r1 組二 + r2 組乙 | 符合;擋下理由文字與計劃二·4 不一致,見 F4 |
| S4 白名單 | TOOLS_OK、Agent/Task 的 isolation 與 subagent_type | S4 三支 | 符合 |
| S5 認出審查席 | parseMarker、firstLine、looseHead | S5 五支 + r1 組四 + r2 組丙 | 部分:寫壞判準比條款寬,見 F1 |
| S6 繼承 | spawn 的 parent 分支(cwd 沿用) | S6 兩支 + r2 組庚 | 符合 |
| S7 登記前呼叫 | pending/waiters/release、call 的等待迴圈、$.state 讀回 | S7 五支 + r1 組五 + r2 組甲 | 符合 |
| S8 外掛出錯 | call 的 catch、BASH_ERROR、onCallFailed、seatishOf | S8 三支 + r1 組四 | 部分:出錯時擋的範圍比計劃二·6 寬(F2),接線沒測試守(F3) |
| S9 安裝多外掛 | `_LUMOS_PLUGINS` 三支、既有逐支邏輯 | t_lumos_plugin_install_edge_cases、t_install_registers_guard_plugin(找得到、綠) | 符合;條款寫「兩支」與實際三支不符,見 F4 |
| S10 檔案合法 | t_guard_plugin_files_valid | 同左(找得到、綠) | 符合;`.catch` 那段只在本機有 claude 時跑,見 F6 |
| S11 範本 | templates.md §0 與 §1/§3/§7.6/§7.8 | t_seat_templates_carry_marker(找得到、綠) | 符合;§7.5 等未涵蓋是規格本身的缺口,見 F5 |
| S12 事件帳 | spawnFields、spawnEvent、recordEvent | ledger.test.ts 的 S12 兩支 | 符合(獨立 fix 提交 ad9b8bee 存在) |
| S13 真機驗收 | 無程式(人工) | Verification/2026-10-06_審查席隔離實作 記有一場 | 符合(人工條款,未重跑);驗證紀錄寫於 d4 之前的版本,r3 後事後查部分已刪,三項斷言仍成立 |

範圍「做」五項:外掛、認席、套規則、事件帳修正、範本與編排者須知,都在 diff 裡;「不做」清單沒有偷做(沒有 `$.process`、沒有事後查、沒有逐詞解析 git)。決策 d4、d5、d6 與程式一致(白名單、粗擋、暫存處擋讀、`$.state` 先讀再合併、會談結束只刪那一場)。

### F1 S5 寫壞標記的判準比條款寬,測試反過來釘住與條款相反的行為
severity: minor
blocking: 否 — 偏向擋、擋下理由明確可改第一行;但計劃與測試對立,收斂前須擇一改
引句:「只是提到 lumos-seat、後面沒接冒號的一般派工」
引句:「expect(parseMarker('LUMOS-SEAT 外掛的 bug 查一下').kind).toBe('bad')」
file: `mods/claude/lumos-guard/hooks/register.ts:41`

計劃做法一與 S5 都說:第一行去掉修飾後以 `lumos-seat` **接冒號**開頭卻不合格才擋下派工;沒接冒號的一般派工照常。程式的 `SEAT_LOOSE_RE` 不要求冒號(只要 `lumos-seat` 後不接字母數字連字號就算想寫標記),所以第一行是「LUMOS-SEAT 外掛的 bug 查一下」的一般派工會被擋下。測試註解寫明是代碼審 r2 起的決定,但計劃沒回寫。臨時複本把正規式改成要求冒號(照條款字面),兩支測試翻紅,表示測試釘的是偏離條款的行為。實際影響:正好在改這支外掛的 session 派一般子代理、第一行以這個詞開頭,會被誤擋。擇一:計劃 S5 與做法一改成「忘了冒號也算寫壞」,或程式與兩支測試照條款改回。

### F2 外掛出錯時擋 Bash 的範圍:程式擋所有子代理,計劃二·6 只擋審查席與判不出者
severity: minor
blocking: 否 — 偏向擋、只在外掛自己出錯時發生;但與計劃二·6 的明文不一致
引句:「主會談與非審查席子代理的 Bash 出錯照常放行(代碼審 r1)」
file: `mods/claude/lumos-guard/hooks/register.ts:307`
file: `mods/claude/lumos-guard/hooks/register.ts:381`

計劃二·6:例外只限「已登記,或有審查席派工在啟動中、判不出是不是」的 Bash;主會談與非審查席子代理出錯照常放行。程式:`call` 在 `$.state` 讀不到(`found === 'error'`)時,任何帶 agentId 的子代理的 Bash 都擋;`seatishOf` 對任何字串型 agentId、或 guard 尚未建立,都回 true。非審查席子代理的 Bash 因此在外掛出錯時被擋。測試 `$.state 讀不到(丟錯):子代理的 Bash 擋` 與 `seatish(出錯時用)` 也釘在寬版。Systems/lumos-guard.md 的 PITFALL 修法已寫成寬版(「判不出是不是審查席也算」),所以是計劃二·6 與 S8 沒回寫,不是筆記沒寫。

### F3 S8 的接線(seatishOf、onCall 的 catch 分支)沒有測試守住
severity: minor
blocking: 否 — 不影響已測的規則本體;影響的是 S8 條款在接線層的綁定強度
引句:「出錯時只擋審查席的 Bash」
file: `mods/claude/lumos-guard/hooks/register.ts:381`

在臨時複本把 `seatishOf` 改成恆回 false(出錯時任何 Bash 都不擋),63 支測試仍全綠。原因:`onCallFailed` 的測試是手動傳入 seatish 布林,`seatish` 的測試只測 guard 方法,從 `.catch` 掛鉤算出布林的 `seatishOf`、以及 `onCall` 外層 catch 的 Bash 分支,都沒有測試走到。對照:改壞「查不到 $.state 時 Bash 不擋」「onCallFailed 不看 called」「逾時 toast」「會談結束不刪 $.state」「搜尋範圍不含暫存處上層」「Glob 固定段」各至少一支翻紅。補一支以真 `seatishOf`/`onCall` 走 catch 的測試即可。

### F4 計劃與筆記裡的數字、描述跟現況不一致(文件漂移)
severity: minor
blocking: 否 — 純文字,不影響行為
引句:「外掛清單的兩支應各自裝上(裝完列表確認)與移除」
引句:「條款 S1–S8,49 支;第一版改壞 25 處」
引句:「不叫人改用 `Grep` 工具:有些建置沒有 Grep、Glob(代碼審 r1 通才席實查)」
file: `docs/lumos-toolchain-knowledge/Projects/審查席唯讀隔離_計劃.md:110`

三處對不上:(a) 計劃做法三、S9、S10、S13 多處寫「兩支」,實際 `_LUMOS_PLUGINS` 與市集是三支(測試已改成通用寫法,條款文字沒跟);(b) Systems/lumos-guard.md 的 TEST 行寫 49 支,現況 63 支;(c) 計劃二·4 寫不叫人改用 Grep,但程式擋下理由寫「搜字可用 Grep 工具(有的話)」,計劃 r3 折入紀錄又寫「擋下理由教改用 `Grep` 工具」,計劃內部也自相矛盾。

### F5 計劃 S11 只涵蓋四段範本,同樣會派出審查席的 §7.5 等段沒有標記(規格缺口 ⚠)
severity: minor
blocking: 否 — 屬規格範圍的取捨,不是實作偏離;⚠ 判不準是漏列還是刻意
引句:「§1 審計員、§3 code-loop reviewer、§7.6 架構對齊、§7.8 資安四段的派工詞第一行加」
file: `skills/lumos-design-loop/templates.md:255`

§7.5 規格符合席(本席就是這一種)、§2/§4 辯方、§7 平行 panel 的派工詞沒有 `LUMOS-SEAT` 行;編排者照這幾段抄,那一席就沒有隔離,而計劃誠實界線也說「標記靠派工詞第一行:編排者漏寫,那一席就沒有隔離」。實作完全照規格,沒偏離;只是計劃要不要把這幾段列入或明寫排除理由,未交代。

### F6 條款綁定的兩處弱點
severity: minor
blocking: 否 — 綁定語意不強,不影響實作
引句:「測試標題以條款編號開頭,用 `claude plugin test mods/claude/lumos-guard` 在本機跑」
file: `mods/claude/lumos-guard/hooks/guard.test.ts:514`

(a) 條款綁定靠「S<n> 測試全綠」(標題前綴)。S7 的熱重載後新登記一席、會談結束只刪那一場、`$.state` 形狀不對、`$.state` 讀不到等測試標題沒有條款編號(掛在「代碼審 r2 組甲」下),照標題前綴篩 S7/S8 會漏掉這些;條款是 manual 綁定,spec-trace 只能看到整句,不會抓。(b) S10 的「兩個能擋人的掛鉤都掛 `.catch`」只在本機有 `claude` 時由 `t_guard_plugin_files_valid` 檢查,CI 沒有 claude 時靜默略過;計劃的 `[test:]` 綁定因此在 CI 上只守住其餘 15 條斷言。

總結:最嚴重 minor,blocking 0 條
