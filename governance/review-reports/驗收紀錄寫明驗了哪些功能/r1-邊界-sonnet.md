severity: major

實驗方式:`git clone --shared` 到臨時目錄,載入 `scripts/lumos` 的 `Env`,對 16 種 `system_refs` 寫法各建一篇 `Verification/sub/V.md`(正文另連 `[[Systems/B]]`),印出 `fields`、`link_target`+`resolve` 結果與 `n.targets`。

## F1 「有鍵就只看它」遇到解析成空的寫法,會把整道檢查靜默關掉
severity: major
blocking: 是
引句:「開頭欄位有 `system_refs` 這個鍵(寫成空清單也算)→ 只看它,解析每項連結,落在 `Systems/` 的收進集合」
file: `scripts/lumos:477`(`parse_frontmatter`:`val==""` 分支遇到第 0 欄的 `- ` 就 break,`fields[key]=[]`)
file: `scripts/lumos:455`(`link_target` 只剝 ASCII `[[ ]]`)
1. 「鍵存在」與「寫對了」被當成同一件事。以下寫法都讓鍵存在、卻解析出空集合,而且 lint 不唸、doctor 2/4 也不報(實測 resolved=[]):
   - 清單項沒縮排(YAML 合法的 `system_refs:` 換行 `- "[[Systems/A]]"`)→ `fields=[]`
   - 全形括號 `［［Systems/A］］` → 解不到
   - `system_refs: ""` → `fields=''`
   - `system_refs:` 後面沒值
2. 後果:這份紀錄的正文連結本來會被推成義務(正文 `[[Systems/B]]`),現在整個被丟掉,verified_by 漏寫不再被擋。作者想要的「空清單=我宣告它沒驗任何功能」跟「寫壞了」無法區分。
3. 設計的 RETIRE-IF 第二條只量「漏列」,量不到「寫壞變空」。
4. 建議:空值(無項目、或項目全解析不到)不得當成「已宣告」,應退回正文推,或報 issue;只有字面 `[]` 才算明確的空宣告。(S3 只涵蓋 `[]`)

## F2 區塊寫法與一行多連結:被靜默截成最後一項,設計只擋了「回退」那條路
severity: major
blocking: 是
引句:「沒有這個鍵 → 照舊用現行 `n.targets`(正文去掉程式碼區塊後的連結,加上開頭欄位裡「整個值恰為單一連結」且不是區塊寫法的項)落在 `Systems/` 的。」
file: `scripts/lumos:643`(`as_list` 對 str 回 `[str(v)]`)、`scripts/lumos:626`(`resolve`:含 `/` 但找不到 → `rsplit("/",1)[1]` 取最後一段當 stem)
1. 設計對沒鍵的路徑特別排除區塊寫法,卻沒說有鍵時區塊寫法怎麼辦。實測 `system_refs: |-` 加兩行 `[[Systems/A]]`、`[[Systems/B]]`:`fields` 是整段字串,`link_target` 剝括號得 `Systems/A\nSystems/B`,`resolve` 取最後一段,結果只剩 `Systems/B`,A 被靜默丟掉(實測 resolved=['Systems/B.md'])。
2. 一行多連結 `system_refs: "[[Systems/A]], [[Systems/B]]"` 同樣只剩 B(實測)。此時 lint 會唸(讀側既有),但 doctor 3/4 仍是靜默少掛 A、不擋推送。
3. 設計的「解析每項連結」沒定義「項」怎麼切;若抄 `link_target`+`resolve`,就繼承這個「取最後一段」的行為。建議:區塊寫法的 `system_refs` 與含兩個以上 `[[` 的項,明確列為「寫法錯誤」issue,不要靜默收一半。

## F3 「解析不到的不收(doctor 2/4 會報)」對非 wikilink 項不成立
severity: major
blocking: 是
引句:「解析不到的不收(doctor 2/4 會報)」
file: `scripts/lumos:611`(`n.targets` 的開頭欄位部分只收 `_SINGLE_WIKILINK_RE.fullmatch` 的項)
file: `scripts/lumos:1470`(doctor 2/4 只看 `unresolved`,來源是 `n.targets`)
1. 計劃自己的前提(PRIOR-ART 與範圍)是每項是 `[[連結]]`,但解析走 `as_list`+`link_target`,連純文字都吃。
2. 純文字打錯 `system_refs: Systems/Typo`:`link_target`→`Systems/Typo` 解不到(實測 resolved=[]),但它不是 wikilink,不在 `n.targets`,2/4 看不到。結果:3/4 不收、2/4 不報、4 無人報。「誤擋:指錯會算 issue」的承諾落空,且整份紀錄因 F1 變成「驗了零個功能」。
3. 全形括號同理(2/4 也不報)。
4. 反向:純文字 `system_refs: Systems/A`(無括號)會被當成有效(實測 resolved=Systems/A.md),跟「每項 `[[Systems/X]]`」的文字不一致,而且它不在 `n.targets`,圖譜邊不會有它。建議:`system_refs` 的項只收 `_SINGLE_WIKILINK_RE.fullmatch` 的,其他一律另報「寫法不對」。

## F4 沿用 `resolve` 的 stem 回退,錯路徑會被悄悄救成 Systems,S4 的「存在但不是 Systems」抓不到這一類
severity: minor
blocking: 否
引句:「`system_refs` 指到存在但不是 Systems 的節點時 doctor 3/4 列出(指到不存在的節點,doctor 2/4 本來就會報,不重複報)」
file: `scripts/lumos:626`(`resolve`:`Projects/A` 不存在時改用 stem `A` 找)
1. 實測:`[[Projects/A]]`(Projects/A 不存在、Systems/A 存在)→ resolved=Systems/A.md,被當成合法的 Systems 項;2/4 也不報(因為能解到)。路徑寫錯卻過關,跟「指到計劃會算 issue」不一致(誤擋條款的場景是指到真正存在的計劃才成立)。
2. 同 stem 兩處都存在(`Projects/A` 與 `Systems/A`)時,寫 basename `[[A]]` 取 `hits[0]`(依 sorted 順序是 Projects),會被判成「存在但不是 Systems」誤擋。建議在 S4 補一條:`system_refs` 的項若不是完整路徑 `Systems/…` 要不要接受,寫明。

## F5 status 大小寫與空白:跳過集只有 `strip()`,沒有 `lower()`
severity: minor
blocking: 否
引句:「當驗收紀錄是 stale、fail 或 superseded 時,不論有沒有 `system_refs`,doctor 3/4 與 sync 都應照舊跳過」
file: `scripts/lumos:732`(`status_of` 只回字串)、`scripts/lumos:1467` 附近(`.strip() in ("stale","fail","superseded")`)
1. `status: Fail`、`FAIL`、`Superseded` 不會被跳過(既有行為),`status: [fail]` 這種清單值讀成 "" 也不跳過。共用函式抽出後這個漏洞被複製成唯一一份;S8 只測小寫。建議共用函式內 `.strip().lower()`,並在 S8 補大寫例。

## F6 Verification 子資料夾:設計沒講,現況可用
severity: minor
blocking: 否
引句:「(驗了哪些 Systems 的 rel 集合, `system_refs` 裡指到存在但不是 Systems 的項)」
file: `scripts/lumos:1457`(`rel.startswith("Verification/")` 已含子資料夾)
1. 實測 `Verification/sub/V.md` 能被讀到,`system_refs` 照常解析。沒有缺口,只是計劃的測試沒涵蓋子資料夾,建議 `t_doctor_check3_system_refs_authoritative` 其中一個案例放在子資料夾,避免共用函式日後改成 `split("/")[0]` 比對出錯。(判不準影響:⚠ 僅預防性)

## 對得上的項目(無 finding)
- 帶別名 `[[Systems/A|A]]`、帶段落 `[[Systems/A#x]]`、大小寫 `[[systems/a]]`、basename `[[A]]`:實測都解到 `Systems/A.md`。重複兩次因為用集合不影響。
- 純量字串 `system_refs: "[[Systems/A]]"` 與 S1 字面寫法 `system_refs: [[Systems/A]]`:都解到 `Systems/A.md`。

最高等級:major,blocking 共 3 條
