severity: minor

(對照的是 negguard 快照裡的 scripts/lumos,行號以該份為準。)

## 問 1 分層與依賴方向

大致一致。現況是 doctor 3/4(`scripts/lumos:1476-1507`)與 `cmd_sync_verified_by`(`scripts/lumos:15843-15860`)各寫一份一模一樣的「跳過 stale/fail/superseded、從 `n.targets` 取落在 Systems/ 的連結」,註解還要求兩邊對齊(`:1484-1490`、`:15851-15853`)。計劃把它抽成一支共用函式,兩邊呼叫,方向符合專案慣例:同檔內頂層 `_xxx(env, ...)` 純函式、doctor 與別的指令共用同一支(例:`_home_map_from_notes`/`_impact_home_map` `:38674`,`status_of` `:732`)。沒有跨層直呼:函式只讀 `env.notes`/`env.resolve`,寫入仍走 `cmd_append`(`:19200-19210` 的既有寫法)。小提醒(不列 finding):`status_of(env, rel)` 只收 rel,新函式簽名收 `(env, rel, n)`,rel 與 n 重複;回傳「None 或 (集合, 問題清單)」的混合型,鄰居 `_about_code_path` 用 `(值, err)` 二元組。結構對,不阻擋。

## 問 2 命名與錯誤處理

- 欄位名 `system_refs`:專案的 `XXX_refs` 欄位(`plan_refs`、`core_refs`、`decision_refs`)都是「指到某類節點的清單」,`plan_refs` 是 `[[連結]]` 清單,同型;`core_refs` 是純路徑(例外,有明文理由)。`system_refs` 對 `plan_refs` 同型,命名一致。建檔旗標 `--systems` 對 `--plan`(`:44612`)也一致。
- 函式名 `_verification_system_targets`:跟鄰居 `_nl_rule_*`、`_doctor_stale_rules` 的「底線 + 做什麼」同風格。
- 錯誤處理:建檔寫失敗的提醒句、rc2、走 `cmd_append`、`except (OSError, ValueError, RuntimeError)`,都照 `:19197-19211` 既有寫法。唯一不同:鄰居 doctor 4/4 對 `plan_refs` 指到不存在的節點會自己報「斷鏈」(`:1523`),即使 2/4 也會報;計劃對 `system_refs` 刻意不重複報(見 F1)。

## 問 3 第二種做法

- 「宣告優先、沒宣告才從正文推」:專案內有近似先例但不完全同形。①`aliases` 宣告制(`aliases: []` 明示無同義詞算合法,缺鍵才硬擋),跟計劃「空清單也算宣告」同構;②`.lumos/lint.json`「有宣告才驗,沒宣告一行跳過」(`:3262-3269`);③`_review_role_wanted`「宣告命中的檔不讀(宣告優先)」(`:23857`)。但「欄位在就蓋掉正文推導、欄位不在就退回推導」套在同一個判斷上,是這個判斷首見。它不算「第二種做法」:取代的是 doctor 3/4 自己那段推導,不是跟某個既有機制並行;兩處呼叫點(doctor、sync)已收斂成同一支,不會分岔。不阻擋,但 PRIOR-ART 只引外部世界例子,漏引本 repo 的內部先例(見 F2)。
- 「只進 `LIST_KEYS`、不進 `TYPED_EDGE_FIELDS`/`LINK_KEYS`」跟 `plan_refs` 待遇不同:算不一致嗎?不算。`lands_in`、`about_code`、`aliases`、`tags` 都只在 `LIST_KEYS`(`:17105`),`LINK_KEYS` 只有 `verified_by/plan_refs/related/core_refs`(`:17125`),且 `lint` 的已知欄位清單會併入 `LIST_KEYS`(`:5891`),所以不必動 `_KNOWN_FRONTMATTER_KEYS`,計劃這句屬實。計劃明講範圍收窄是 Enzo 裁的,且同名 `lands_in` 就是同待遇的先例,可補一句引它。

## 問 4 落點

寫進既有兩篇,不另開。`Systems/lumos-cli-read` 管 doctor(`about_code: scripts/lumos`),`Systems/lumos-cli-write` 管 new verification/sync-verified-by/append(同樣 `about_code: scripts/lumos`),計劃要改的三塊正好各落一邊,都已有家,符合「每支檔有家」。共用函式只在一邊詳寫、另一邊用 `[[連結]]` 指過去即可(照 CLAUDE.md 鐵則 5 與 `lumos-cli-write.md:21` 慣例)。`lumos-cli-write` 內有 `LIST_KEYS` 列舉但已標「以常數為準」(`lumos-cli-write.md:36,93`),新增一鍵不會踩計數標記(`lumos:count` 只綁 `SCALAR_KEYS`)。

## F1 doctor 3/4 對 system_refs 指到不存在節點不報,跟 4/4 對 plan_refs 的報法不同
severity: minor
blocking: 否
引句:「解析不到的不收(doctor 2/4 會報)」
file: `scripts/lumos:1523`(4/4 對 plan_refs 解析不到仍自己印「plan_refs 斷鏈」,即使 2/4 的 `:1470-1474` 也會報同一個連結)

1. 鄰居慣例是各段各報自己欄位的斷鏈;計劃選擇不重複報,屬刻意差異,理由(避免雙報)寫在計劃裡,但沒說明為何跟 4/4 不同。
2. 建議:在計劃加一句理由,或讓 3/4 照 4/4 報(同一個連結雙報在既有輸出本來就存在)。

## F2 PRIOR-ART 只引外部例子,漏引本 repo 的宣告制先例
severity: minor
blocking: 否
引句:「宣告的優先、沒宣告才退回推」
file: `scripts/lumos:23857`(「宣告命中的檔不讀(宣告優先)」)、`scripts/lumos:5927`(aliases 宣告制:`aliases: []` 明示無同義詞)

1. 家規「借用既有設計」要求先看本專案;`aliases: []` 就是「空清單=明示宣告過」的既有寫法,值得在 PRIOR-ART 引用,也讓審查者確認「空清單算宣告」不是新發明。
2. 純文件補強,不影響設計結構。

不對齊共 2 條,其中 major 0 條
