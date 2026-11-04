severity: minor

## 上一輪項目驗證

| 項目 | 結果 | 對照 |
|---|---|---|
| 字數口徑第二套 | 已改回 `_retro_text_ok` | `scripts/lumos:22395`,與 `why_cap`、`avoid` 在 `scripts/lumos:22483-22485` 同一用法。`_real_chars` 在 `scripts/lumos:13923`,屬另一支閘,不用是對的。 |
| verdict 沒放常數 | 已放常數 | `_RETRO_WORLD_VERDICTS` 的命名、tuple 形狀與英文 kebab 值,跟 `_RETRO_FAMILIES`、`_RETRO_TARGETS`、`_RETRO_DECISIONS` 同一排(`scripts/lumos:22119-22122`)。 |
| 提醒輸出串流 | 已對齊 | 改成 stderr 加 `[retro]` 前綴、只印不擋,跟 `--template` 分支的 `[retro]` 提示一致(`scripts/lumos:22942-22946`)。 |
| intake 小節名 | 已對齊 | 沿用〈先查世界〉,不另開標題。設計審第 6 步和代碼審第 5 步的「修前先查世界」段確實在 `skills/lumos-design-loop/SKILL.md:41` 與 `skills/lumos-code-loop/SKILL.md:50`。 |
| 落點 | 已對齊 | `lands_in` 是 `Systems/loop-retro` 與 `Systems/每輪修補差異派工`。後者已掛 code-loop 的 SKILL 與 reference,以及 design-loop 的 templates,也已有〈先查世界〉的 WHY(`Systems/每輪修補差異派工.md:20`)。 |

## 一、分層與依賴方向

沒有跨層直呼。驗法放在 `_cap_retro_check`,它本來就拿 `decision` 參數,所以讀人裁 `ts` 不用改簽名。`--record` 目前丟掉的 `_data` 可以拿來印提醒,不必重讀檔。跑滿提示改在 `_cap_retro_next_lines` 一處,`[cap-hint]` 與 `loop next --json` 共用,也沒有長出第二個決定處。

## 二、命名與錯誤處理

**1. 彙整的資料來源沒講清楚**

現行 `cmd_loop_retro_stats` 的族別和行動項,都是從 `_cap_retro_status` 回傳的 `st["data"]`(驗過的回顧檔)取。這個函式註明是「唯一判定」(`scripts/lumos:22509-22511`)。

設計把 `world_verdict` 寫進 `--record` 的事件,又說 retro-stats 從這裡數,但沒講數的來源。`_cap_retro_status` 內部的事件 E 沒有回傳,retro-stats 要讀事件就得自己再掃一次治理帳。這樣同一個事實會有兩個來源:檔案被改過、狀態變過期時,事件欄位還在、`st["data"]` 卻是 None,兩邊的數字會對不上。

如果 retro-stats 是從事件欄位數,我會升成 major。目前文字看不出來,所以標 ⚠ 交編排者。
severity: minor
blocking: 否
引句:「`--record` 寫的治理帳事件多帶 `world_verdict`(沒填就不帶)」
file: `scripts/lumos:22981`

**2. retro-stats 只講印文字,沒提 JSON**

`cmd_loop_retro_stats` 有 `as_json` 模式,`out` 字典裡有 `families`、`actions` 等欄位(`scripts/lumos:22981`、`scripts/lumos:23010`)。`skills/lumos-project-notes/commands/06-代碼審與推送.md:134` 也指示用 `retro-stats --json`。

設計和 S6 都只提文字輸出。新統計若只在文字版有,會和既有的文字加 JSON 雙輸出不一致。
severity: minor
blocking: 否
引句:「`retro-stats` 多印一段」
file: `scripts/lumos:23009`

**3. 引用了不存在的決策編號**

「破壞起草獨立」那句括號裡寫 d2,但計劃 frontmatter 的 `decisions:` 只有 d1。專案慣例是決策紀錄有編號、有四欄理由,懸空的編號查不到。要嘛補一筆 d2,要嘛去掉這個引用。
severity: minor
blocking: 否
引句:「破壞起草獨立(d2)」
file: `docs/lumos-toolchain-knowledge/Systems/loop-retro.md:20`(`WHY:[2026-10-05 d2]` 是同類的編號寫法)

## 三、第二種做法

**1. 測試改生效時間的寫法**

「生效常數」這個名詞指向模組常數 `_CAP_WORLD_CHECK_SINCE`,它跟 `_SPEC_GATE_SINCE`、`_CLAUSE_GATE_SINCE`、`_SECURITY_SEAT_SINCE`、`_LANDING_GATE_SINCE` 同一族(`scripts/lumos:13713`、`14809`、`35295`)。這一族沒有一個帶環境變數覆寫,測試是靠資料本身的 ts 控制。cap-decision 的測試也有這個先例:直接寫一行帶明確 ts 的治理帳(`scripts/test_lumos.py:104180`)。

設計說「照 `_cap_real_cutoff` 的寫法」,但那是個測試裝飾器,它設的是正式碼早就會讀的 `LUMOS_PANEL_RETIRE_CUTOFF`(`scripts/test_lumos.py:50804`、`scripts/lumos:18839`)。它沒讓任何模組常數可改。新設計等於混用兩種做法:常數形狀跟 `_SINCE` 族一樣,卻又要加一個只給測試用的環境變數。

建議二選一:S5 測試改成寫帶明確 ts 的人裁事件,對齊 `_SINCE` 族和 `scripts/test_lumos.py:104180`;或明講新增環境變數,並寫它的名稱和讀取位置。

另外,第 7 點說「S4 兩支測試」設常數,但驗收條款裡的前後生效測試是 S5(S4 是 accept-risk),編號對不上。
severity: minor
blocking: 否
引句:「生效常數照 `_cap_real_cutoff` 的寫法讓測試能改(環境變數覆寫,只給測試用)」
file: `scripts/test_lumos.py:50804`

**2. 網址正規化**

repo 裡沒有網址去重的既有函式,所以不算重複造輪子。但最近的做法是 `_secev_target_host`:用標準庫 `urllib.parse.urlsplit` 解析,取 `hostname.lower()`,授權段含反斜線、空白、百分號就判不出來(`scripts/lumos:10351-10366`)。

設計寫的「scheme 不分大小寫、`://` 後面不是空、去 `#`、去結尾斜線」像手寫字串切片,PRIOR-ART 的借用清單也沒提 `urlsplit`。手寫會長出第二套 URL 解析口徑,例如 `HTTP://A.com:80/`、`user@host`、`\` 這幾種寫法兩邊會判不同。建議在設計裡明寫用 `urlsplit`,並沿用 `_secev_target_host` 那條授權段限制。
severity: minor
blocking: 否
引句:「兩項以上的網址在正規化(scheme 與主機名轉小寫、去掉 `#` 之後、去掉結尾斜線)後要互不相同(用集合比)」
file: `scripts/lumos:10351`

## 四、落點

落點沒有問題,見上面的驗證表。手冊七處加 `docs/command-reference.md:137` 的同步清單,跟我實查的位置一致:
- design-loop 的 `SKILL.md:67`、`reference.md:332`、`reference.md:542`
- code-loop 的 `SKILL.md:66`、`reference.md:245`、`reference.md:620`
- `commands/05-設計審查迴圈.md:33`

寫回的 WHY 放 `Systems/loop-retro` 與 `Systems/每輪修補差異派工`,符合各自的 responsibility。只有上面第二節第 3 條的 d2 懸空要補。

不對齊共 5 條,都是 minor。第二節第 1 條判不準,標 ⚠ 交編排者。
