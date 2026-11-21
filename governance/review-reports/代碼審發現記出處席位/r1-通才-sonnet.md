severity: minor

整份 spec 已逐節讀完。引用的交叉參照都找得到:`[[Projects/代碼審minor解綁_計劃]]`、`[[Projects/審查帳節點映射_計劃]]`、`[[Systems/canary-audit]]` d4、`[[Systems/loop-convergence-recording]]`。主要的現況宣稱我也核對過,結果如下:
- 帳本統計「866 筆代碼審載體、52 筆帶 `finding_sources`」與實帳一致。
- `_CHOICE_SINCE` 的寫法、`_GOV_FIELD_TYPES`、canary 列 mapper、`_disposal_tpl` 都與 spec 描述相符。
- 載體裡 `findings_set` 與 `refuted_set` 不重疊,寫側確實擋(`scripts/lumos:19695`)。
- 讀同迴圈帳的 `_lrows` 已排除結局帳與規格閘留痕,所以「首筆不算結局帳」現成成立。

**固定席逐條判**
- canary-audit INVARIANT 1(記帳成功 ⟺ 已落盤且可讀回):不影響。新檢查全在 `_jsonl_append_verified` 之前,擋下時不寫帳;新欄位只是同一行 JSON 多一個鍵,讀回自驗照舊。
- canary-audit INVARIANT 2(second 紀錄純 telemetry):不影響。新旗標只掛 `--findings-set` 載體,`cmd_canary_second` 與 gate 輸出都沒碰。
- loop-convergence-recording:沒有合約被碰到。載體最後記、一輪只准一筆載體的規矩,spec 都沿用。

**逐節**
- 白話、用詞、舊否決比對:已讀,無 finding 之外的問題(除下列第 4 點)。
- 範圍、做法:見第 1、2、3、5 點。
- 驗收條款、預期值表、回退、依據來源:已讀,內部一致。
- 實務隱患:見下方逐類。

---

## g1
severity: minor
blocking: 否 — 實作者跑測試會當場看到紅燈,修法一目了然,不會做出壞系統。
spec 段落:〈做法〉生效日、〈範圍〉⑤範本。
問題:spec 以為把生效日預設成 9999-12-31 就能讓既有造帳測試不受影響,但範本的字串改動跟生效日無關,而且既有測試會把範本照填後真跑。
引句:「測試總檔預設設成 9999-12-31,讓既有造帳測試不受影響,新測試自己改」
引句:「迴圈編號 `code-` 開頭時多一段」
佐證:file: `scripts/test_lumos.py:103225`(t_fix_check 的 ⑫⑬,到 103246)取 `code-fx` 第 2 輪的 `disposal_cmd`,用一串 `.replace` 填完佔位符,再 `shlex.split` 真跑,斷言 rc 0。範本多出 `--finding-seat <id=席名>` 後,這串 replace 不認得它,字面 `<id=席名>` 會被當成 id 為 `<id`、席名為 `席名>` 的旗標值。這個 id 不在發現清單,寫側 rc 2,⑬ 翻紅。spec 沒把改這支既有測試列進工作項,也沒說範本在生效日前要不要印。

---

## g2
severity: minor
blocking: 否 — 字面讀法有歧義,但單看一輪載體的合理實作會算對。
spec 段落:〈做法〉統計、S8 與預期值表。
問題:「每個 (id, 席) 算一次」沒說在哪個範圍內去重。真帳的 id 會跨輪、跨迴圈重複使用(預期值表自己就用 `c1`、`a1`、`c9` 這種短 id)。若實作者在全窗口內對 (id, 席) 去重,會把不同輪的同名 id 併成一條,沒用率會被低估。S8 的測資 `c1/a1/a2/c2/c9` 剛好全不重複,抓不到這種錯。
引句:「每個 (id, 席) 算一次,id 在折入清單算有用,在放行清單或重現不到清單算沒用」
佐證:file: `scripts/lumos:18113`(到 18122)既有的 `finding_kinds` 統計是逐載體列累加,沒有全域去重。建議 spec 寫明「以載體列為單位」,S8 加一個跨輪重用 id 的案例。

---

## g3
severity: minor
blocking: 否 — 現有 `_loop_ts_key` 的退回字串比對對日期前綴剛好能用,但寫法不統一會讓測試與時區行為各說各話。
spec 段落:〈做法〉必填條件、生效日。
問題:spec 要比「迴圈首筆帳時間」跟「生效日」,卻只說常數是 `YYYY-MM-DD` 日期、仿 `_CHOICE_SINCE`,沒說比較方式。`_CHOICE_SINCE` 是推送閘用的日期,不是拿來比帳上時間戳的。repo 裡比帳上時間戳的先例 `_SECURITY_SEAT_SINCE` 用帶 `+08:00` 的完整 ISO 字串,並走 `_loop_ts_key` 換算 UTC。
- 裸日期過 `_loop_ts_key` 會因沒帶時區回 None,等於退回字串比對,又回到先例註解說過會「依記帳機器時區判不同」的做法。
- 「首筆」是檔案順序第一筆還是時間最小一筆,spec 也沒講。
引句:「這條迴圈帳上首筆(不算結局帳)的時間不早於生效日」
佐證:file: `scripts/lumos:15769`(註解,到 15770)、`scripts/lumos:20847`(`_loop_ts_key` 對 naive 回 None,到 20862)、`scripts/lumos:77744`(`_CHOICE_SINCE` 純日期)。

---

## g4
severity: minor
blocking: 否 — 只是圖譜決策沒翻案,不影響程式行為。
spec 段落:〈舊否決比對〉、〈範圍〉⑦。
問題:spec 只在自己的 WHY 與〈舊否決比對〉裡說 canary-audit d4 不適用,範圍 ⑦ 的「筆記同步」只列 lands_in 的 `loop-convergence-recording`,沒要求在 `canary-audit` 登記決策。那邊的 d4 仍是 `valid: true`,內容明寫「否決跨期統計/席位信譽」。下一個 session 查 `lumos decisions canary-audit` 會看到一條沒被翻案的否決,而它對應的機制已經上線。依本 repo 的規則,結構化決策紀錄有挑戰程式碼的效力,這會造成筆記打架。
引句:「數字只給人看,不進任何閘、不自動調席位;統計只看最近 8 週」
佐證:file: `docs/lumos-toolchain-knowledge/Systems/canary-audit.md:76`(d4 `valid: true`,到 81 行)。建議 spec 補一條:用 `lumos decision-add` 在 canary-audit 記「d4 在代碼審逐席沒用率這項不適用」,並寫出作用範圍。

---

## g5
severity: minor
blocking: 否 — 只影響事後可觀測性,不影響擋不擋。
spec 段落:〈實務隱患〉守衛面、REVISIT。
問題:spec 把「擋錯了會讓載體記不進帳、整輪卡住」列為主要風險,防線只有「擋下時不寫帳、訊息點名」,沒說新擋下要不要像同類必填欄位那樣在治理帳留 `canary/blocked` 事件。既有的 `refuted-set-missing`、`report-not-normalized` 都會留。不留的話,RETIRE-IF 與 12-11 的回頭檢查就量不到「這道新擋被撞了幾次」。
引句:「擋下時不寫帳、訊息點名缺哪些 id 或哪個席名;生效前開的迴圈不受影響」
佐證:file: `scripts/lumos:19647`(refuted-set 缺漏時 `_gate_event_or_warn(... "blocked" ...)`,到 19654)、`scripts/lumos:19910` 附近的同類寫法。

---

**實務隱患鏡頭逐類**
- 金流、對外送出:無。純記帳,不連網。
- 不可逆:無。檢查全在寫帳前,擋下時不寫帳。
- 併發與交易:無(單人、沿用既有附加寫法)。
- 守衛面:有,見第 5 點。另外 light、legacy、循序的 `code-` 迴圈沒有載體範本(`disposal_cmd` 只在 `not light and eff_tier != "legacy"` 時印,`scripts/lumos:24866`),但它們在生效日後一樣必填。這屬可接受:擋下訊息直接給寫法,這類迴圈也沒有 `--round`,值只能是本筆 `--auditor`,spec 已覆蓋。
- 天花板(席位自填):spec 已誠實標明工具不驗那條發現真的出自那一席。
- 讀側型別:spec 已要求補 `_GOV_FIELD_TYPES` 與 canary mapper。這支讀法的同族教訓是手改帳值為清單時會 TypeError(見 loop-convergence-recording 的 `PITFALL`)。實作時,統計段讀 `finding_seats` 的值也要先判型別,不能只靠 `gov` 的整列略過。
- 消費專案:spec 已列。擋下訊息要自帶寫法,否則外部專案會被卡。

最嚴重 severity:minor。blocking 共 0 條。
