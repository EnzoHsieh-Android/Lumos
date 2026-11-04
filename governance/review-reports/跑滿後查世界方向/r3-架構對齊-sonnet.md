severity: minor

上一輪點的五件事都已改成借既有做法,我沒看到新的 major(第二種做法或跨層直呼)。下面有六條 minor,結構都對,只有細處跟鄰居不一致。

## 問一:分層與依賴方向

對齊。
- 世界查證的欄位檢查放進 `_cap_retro_check`(`scripts/lumos:22399`),沒有新增狀態。`_cap_retro_status` 的五種狀態不動(`scripts/lumos:22509`),五個呼叫端仍共用同一支判定。
- 統計改讀 `_cap_retro_status` 回的已驗回顧內容。這跟 `cmd_loop_retro_stats` 數族別、行動項同一條路(`scripts/lumos:23005`,`data = st.get("data") if key == "recorded"`)。上一輪「統計來源」那條已解。
- `--json` 多一個 `world_verdicts` 鍵,接在既有輸出字典 `{totals,names,loops,families,actions,gov_error}` 旁(`scripts/lumos:23019`),沒有另開輸出路徑。
- 跑滿提示改在 `_cap_retro_next_lines`(`scripts/lumos:22763`),`loop-retro` 的 d2 也確實是「起草獨立」(`Systems/loop-retro.md:18`)。
- 跨層直呼沒有。

不對齊 1(要判三種情況的地方沒有指名單一處)

severity: minor
blocking: 否
引句:「`--record` 寫的治理帳事件多帶 `world_verdict`:只在「要求」或「選填而且有填」、而且整份檢查通過時寫」
file: `scripts/lumos:22961`

- 三種情況(要求、選填、不管)寫在 `_cap_retro_check` 內部。
- `--record` 目前把檢查回傳的資料丟掉(`probs, _data = _cap_retro_check(...)`)。
- `retro-stats` 要區分「不管」和「沒填」,也得知道這是哪一種。
- 計劃沒說這個判斷由誰提供給 record 和 stats。若兩處各自重算人裁 `ts` 對生效常數,就長出第二個判定點。
- 既有慣例是「五個呼叫端共用 `_cap_retro_status` 一支判定,任何一處另判就會口徑分岔」(`Systems/loop-retro.md:16`)。
- 建議:由 `_cap_retro_check` 或 `_cap_retro_status` 的回傳帶出情況。
- ⚠ 我只能指出計劃沒寫,看不到實作。

## 問二:命名與錯誤處理

不對齊 2(verdict 先去空白再比對,跟既有列舉欄位不同)

severity: minor
blocking: 否
引句:「`verdict` 去頭尾空白後要在 `_RETRO_WORLD_VERDICTS」
file: `scripts/lumos:22459`

- 既有的 `family`、`target` 是原值直接比對固定清單:`if fam not in _RETRO_FAMILIES`。
- 世界查證的 `verdict` 先去空白再比對,帳上寫常數而不寫原字串。
- 這是列舉欄位驗法的第二種寫法。
- 統計若直接讀回顧檔裡的原字串,會對不上常數。
- 常數命名 `_RETRO_WORLD_VERDICTS` 和 kebab-case 取值,跟 `_RETRO_FAMILIES`、`same-family-unswept` 一致,這部分對齊。

不對齊 3(網址檢查沒有跟 `_secev_target_host` 的保守規則對齊)

severity: minor
blocking: 否
引句:「scheme 不分大小寫是 http 或 https,`hostname` 不是空的」
file: `scripts/lumos:10350`

- 這次借了 `urlsplit` 加 `ValueError` 的做法,方向對。
- 但 `_secev_target_host` 還額外拒收:授權段帶反斜線、空白、百分比編碼(「各家 URL 解析對這幾種不一致,寧可擋」)。
- 計劃沒提這條,也沒說為什麼不需要。
- 世界查證的網址只用來比重複,風險不同,不收也說得通,但應該寫出理由。
- 計劃也沒有指名要不要直接呼叫 `_secev_target_host`,因為它只回主機名。
- 全 repo 只有這一處用 `urlsplit`,所以要拆出共用函式還是另寫,計劃應該表態。⚠

## 問三:有沒有第二種做法

不對齊 4(同一句提示散在三處,沒有共用的一句)

severity: minor
blocking: 否
引句:「那一支與 `cmd_loop_cap_decision` 記成 extra-round 成功後印的」
file: `scripts/lumos:22790`

- 既有程式裡,「繼續之前先寫跑滿回顧」已經在兩處各印一次:`_cap_retro_next_lines` 的 `scripts/lumos:22790`,和 `cmd_loop_cap_decision` 的 `scripts/lumos:22846`。
- `_cap_retro_next_lines` 的 docstring 自稱是「人裁該印什麼的唯一決定處」。
- 計劃要在這兩處和 `--template` 的 stderr 提示(`scripts/lumos:22944`)各補一句 world_check,等於把重複擴成三處。
- S7 只用一支測試同時釘這幾處。
- 屬於延續既有重複,不是新發明,所以只給 minor。

不對齊 5(帳上新欄位沒有讀者)

severity: minor
blocking: 否
引句:「`retro-stats` 的世界查證統計讀 `_cap_retro_status` 回的已驗回顧內容」
file: `scripts/lumos:22961`

- 統計明說不讀事件,但 `--record` 仍把 `world_verdict` 寫進治理帳事件。
- 結果是同一個結論有兩份:回顧檔一份,帳上一份,卻沒有任何讀端用帳上那份。
- 既有 `recorded` 事件只帶 `loop`、`path`、`retro_sha256`、`rounds` 這幾個定位用的欄位(`scripts/lumos:22968`),沒有帶回顧內容的衍生值。
- 如果帳上欄位是給事後追溯用的,計劃要寫明;沒寫就是沒讀者的寫入。⚠

## 問四:落點

- 世界查證欄的 WHY 進 `Systems/loop-retro`,跑滿提示順序進 `Systems/loop-convergence-recording`,差異派工那篇補〈先查世界〉擴充。這個分法符合 `loop-retro` 責任欄「不負責 cap-hint 提示(歸 loop-convergence-recording)」(`Systems/loop-retro.md:6`)。
- 測試改成直接往治理帳寫帶明確 `ts` 的人裁事件,已對齊既有寫法(`scripts/test_lumos.py:104180`)。
- 生效常數的命名、帶時區的零點時間戳、不給環境變數覆寫、`ts` 解不開時當作「要求」,都對齊 `_SPEC_GATE_SINCE` 那一族(`scripts/lumos:13714`、`scripts/lumos:14999`)。

不對齊 6(借用清單和做法段對不上)

severity: minor
blocking: 否
引句:「測試裡改生效時限的 `_cap_real_cutoff` 寫法」
file: `scripts/test_lumos.py:50804`

- `PRIOR-ART` 說借了 `_cap_real_cutoff` 的寫法,但做法第 7 點說生效常數不給環境變數覆寫,也不靠真實時鐘。
- `_cap_real_cutoff` 改的是 `LUMOS_PANEL_RETIRE_CUTOFF` 環境變數,新測試只是照舊套用這個裝飾器,沒有借它去改生效時限。
- 同一份借用清單還列了 `_cap_retro_fix_cmd` 的修法表,但做法段的 version 擋下訊息是直接寫在 `bad()` 的字串裡,沒有呼叫它。
- 兩處都是描述過度,實作不會因此分岔。建議把借用清單改成跟做法一致。⚠

不對齊共 6 條,其中 major 0 條
