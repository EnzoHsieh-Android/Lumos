severity: minor

### F1（Q1 分層與依賴方向）新增檢查全部走既有的「掛鉤只呼叫 lumos 子指令」層次，沒有跨層重寫判定
severity: clean
blocking: 否 — 結構與既有閘一致，非引入第二種做法或跨層直呼
引句:「提交前掛鉤呼叫它，擋下就不提交，逃生說明跟既有那幾道一樣」
file: `scripts/hooks/pre-commit:52` 既有 Gate CC 同款「hook 只呼叫、不碰內容」，呼叫 `lumos cochange check --staged`
file: `scripts/hooks/pre-commit:61` 同款呼叫 `lumos delguard --staged`
S24–S26 把「需要家的檔」「別人的檔」「寫回落點」三條判定全放進 `lumos home check`（scripts/lumos 內），pre-commit/pre-push 只負責呼叫與印訊息，跟 cochange/delguard/code-loop check 的分層一致；S28/S29 doctor 三段與 `home check` 共用同一套函式，也對齊既有 S5/S6/S7 doctor 段落「不自己另寫一套」的慣例（scripts/lumos:1981-1982 明文寫「同一件事兩套算法一定分岔」）。沒有看到 hook 端自己用 shell 重算「這是不是程式檔」之類 lumos 已有的判定。

### F2（Q2 命名/設定鍵/訊息/治理帳）新欄位命名與門檻退回邏輯沿用既有家族
severity: clean
blocking: 否 — 命名、設定鍵、治理帳寫法跟既有一致
引句:「這次提交讓某篇的 about_code 變多、提交後超過上限」
file: `scripts/lumos:2070-2079` 既有 `node_scope.max_contracts` 讀 `.lumos/config.json`、bool 誤判單獨擋、壞值退回預設並出聲
file: `scripts/lumos:4629-4632` `_KNOWN_GATES` 既有登記慣例（check-s5/s6/s7 即此案的直接先例）
`node_home.max_files` 跟 `node_scope.max_contracts` 同一個 dot-namespace 設定鍵家族、同一套「壞值退回預設並出聲」防呆（S18），S27「閘名登記進已知閘名單」也直接對齊 `_KNOWN_GATES` 現有登記方式。`responsibility` 欄位的「至少 10 個字、要有實字」驗證（S16）跟既有 `_MANUAL_MIN_CHARS`「≥4 字且至少一個實字」的驗證形狀（scripts/lumos:4453、5713）同款，只是換了門檻數字。

### F3（Q3 第二種做法，⚠）「需要家的檔」程式檔判定要併進第幾份清單，spec 沒講清楚
severity: minor
blocking: 否 — 既有做法本身就是「四份清單+漂移守衛」而非單一來源，spec 沒說第五處落在哪，判不準
引句:「測試檔判定沿用測試地圖那一支，工具自裝檔判定沿用內容指紋那一支」
file: `scripts/test_lumos.py:7591-7602` `t_code_exts_four_lists_agree` 釘的四份清單分別在 pre-commit、post-commit、check-graph-sync.py、impact-hook.py，`scripts/lumos` 本體目前沒有自己的一份
S1 說程式檔判定「跟『改程式要動圖譜』那道閘同一份清單」，但那道閘現況是四份各自定義、靠測試釘住一致，不是單一可 import 的來源；`lumos home check` 要放進 `scripts/lumos`（S24），勢必要嘛新增第五份字面清單（沿用既有「多份+漂移守衛」的做法，不算新機制）、要嘛重構出一個四處共用的常數（那才是這案該做但 spec 沒點名的事）。因為既有做法本身就不統一，這條判不準，交編排者裁是否要求 spec 講清楚落點。

### F4（Q4 落點合不合理）規則五（條款綁定新步驟／派審材料）沒有落進它的既有家 Systems/design-loop，「落點」段只點了三處
severity: minor
blocking: 否 — 是落點誤判／段落不完整，非第二種做法或跨層，不擋
引句:「管提交前檢查的主程式與兩支掛鉤（lumos 主程式、提交前、推送前三支）」
file: `docs/lumos-toolchain-knowledge/Systems/design-loop.md:35` 既有「處置閘第五步（條款綁定）」的 KEY 行，正是 S21 要模仿的同形狀機制（同款「首筆帳日期生效、不回溯」）
file: `docs/lumos-toolchain-knowledge/Systems/design-loop.md:123` 該篇 about_code 只有 `scripts/lumos`
S21（處置閘多一步）、S22（派審附落點現況）、S23（架構對齊席多一題）動的是設計審出口與派工邏輯，跟既有「條款綁定」第五步是同一種機制、同一個既有的家 `Systems/design-loop`——但計劃的「落點」段只列了新開 `Systems/每支檔有家`、更新 `Systems/節點範圍與索引守衛`、教寫節點說明三項，design-loop 這篇完全沒被提到。若規則五因此預設併入新開的「每支檔有家」，會讓那篇一出生就同時管「檔案歸屬檢查」與「設計審處置閘/派工」兩件事，而它自己寫的負責範圍「程式檔歸屬與寫回落點的檢查；不管節點內容好壞」（S17 責任句）並不涵蓋後者——這正是這案自己想防的「一篇管太多」。

总结：最高 severity minor，blocking 共 0 條
