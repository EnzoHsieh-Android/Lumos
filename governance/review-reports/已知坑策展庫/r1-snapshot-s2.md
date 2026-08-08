---
type: project
status: doing
created: 2026-08-09
updated: 2026-08-09
tags:
  - type/project
  - status/doing
summary: |
  KEY:v2 深度層(v1 反問給廣度/本案給類別內世界已知具體坑,跨 session 記憶)——pitfalls 接 known-pitfall 節點(有 pitfall_ask+content-trigger),spec 文本命中→提問+來源彈出;refresh-token→single-flight 種子
  KEY:pre-flight 三硬點各解:①vault-aware-if-present(有才查無降級,不破 vault-free 合約)②新欄位 pitfall_ask/pitfall_source(區別事故節點:後者 glob+無 ask,前者 content+有 ask)③比對吃 corpus 非 raw text
  KEY:刻意不做——破 vault-free 強制/預收全世界/改 gapfill 碼自動建/進硬閘
  FLAG:DECISION
---
# 已知坑策展庫_計劃

> 緣起:[[Projects/已知坑機械前置_計劃]] v1(S0 反問風險類)已落地=給「風險**類別**」廣度;本案=v2 深度層,注入「類別內的**世界已知具體坑**」(refresh-token→single-flight 型)——這顆 LLM 不知道也會被機械提醒,跨 session 記憶。分工:v1 抓盲類、v2 抓盲坑。★pre-flight(v1 那輪)已標三個硬點,本案照解:①cmd_pitfalls 刻意 vault-free ②無「提問」結構化欄位 ③比對須吃 corpus 非 raw text。

PRIOR-ART: ① 最小解——複用既有 `pitfall_when` 觸發機制(content trigger)+ pitfalls spec 模式既有的 `_pitfall_strip_spec` corpus + gapfill 填庫管道;新增=一個「有 vault 才查」的分支+一個提問欄位慣例。② 世界解:已知坑走 gapfill(網搜→refuter→人放行),快取式按需填,非預收全世界(v1 已定調)。③ Growth test:事故=v1 只給廣度、具體坑仍靠在場 LLM 知識+事後帳(v1 誠實天花板明載);非風格;既有機制接線。④ 裁定=borrow-design。

## 核心設計(照 pre-flight 三硬點各給解)

### 硬點①解:vault-aware-if-present(不破 vault-free 合約)
- cmd_pitfalls spec 模式:`corpus` 算完後,**`_vault_in(repo_root)`**(r1 勘誤:明定用此、比照 cmd_impact 慣例;repo_root 已由 _anchor_repo_root 解出=已知情境,不用 find_vault 免 --repo 指無 .git 目錄時兩者分岔);回 None=**靜默降級**(消費端無 vault=行為與現在分毫不差,vault-free 合約保住)。
- 這是把「vault-free」精確化成「vault-aware when present, unchanged when absent」——非破例,是擴充且向下相容。

### 硬點②解:known-pitfall 節點慣例(新欄位,與事故節點區隔)
- known-pitfall = Systems 節點,frontmatter 三欄:
  - `pitfall_when: [content:<寬 regex>]`(既有觸發機制,本案只加 content 型)
  - `pitfall_ask: "<一句隱患提問>"`(★新欄位★——事故節點的教訓在 summary 自由文字,無法機械讀;known-pitfall 要被 pitfalls 印出來,需結構化欄位)
  - `pitfall_source: "<世界來源 URL>"`(★新欄位★——區別「世界已知」vs 本專案事故;無來源不算 known-pitfall)
- **與事故節點天然區隔**:事故節點用 `glob:` trigger(碼路徑,code-time/impact hook 消費)+無 pitfall_ask;known-pitfall 用 `content:` trigger(spec 文本,design-time/pitfalls 消費)+有 pitfall_ask。**design-time 掃描只認「有 pitfall_ask 的節點」**,不會拖進一般事故節點。

### 硬點③解:比對吃 corpus
- content trigger 對 `_pitfall_strip_spec(text)` 後的 corpus 比對(與既有 4 類一致),不吃 raw text——否則 spec 引用舊事故文字提到「refresh token」會假陽性(v1 pre-flight 已警,剝除機制專防此)。

## 規格
### S1 pitfalls 接 known-pitfall(唯一新碼)
- spec 模式(--check/print/json 三路徑):corpus 後加掃 `pitfall_ask` 非空且 `pitfall_when content:` 命中 corpus 的節點 → 收集 `(node, pitfall_ask, pitfall_source)`。
  - 複用 `_match_incident_triggers`(file_rel 傳 spec 檔名占位、file_content=corpus),回傳 `{node,matched_by}` 後**以 node 反查 `env.notes[node].fields.get('pitfall_ask')`**,非空才留、順帶取 `pitfall_source` 與 `pitfall_severity` 欄組四元組(r1 勘誤:函式不吐 ask 值,要反查)。
  - print:多一段「已知坑追問(來源 URL)」;json:多一鍵 `known_pitfalls`。
  - ★--check rc 語意不變(r1 勘誤:原「併入 section-required」自相矛盾——那擴大被擋集合=進硬閘,違反本頁「刻意不做」)★:known-pitfall **advisory-only,不進 --check 判定**;它的牙齒=design-loop panel 審實務隱患節時,對照有沒有答/排除(v1 裁定留痕紀律),非機械擋。
- vault 缺=known_pitfalls 空,三路徑行為 = 現況(向下相容)。

### S2 種子(證線通 + 首條真坑)
- 建 `Systems/known-pitfall-refresh-token.md`(★r1 勘誤:pitfall_when 必用 block-list 逐項一行,零依賴 parser 不認 flow-list `[...]`——會被當純量字串、`startswith("content:")` miss、種子永不命中且 lint 抓不到;走 `lumos append pitfall_when "content:..."` 非手改 frontmatter★):
  - `pitfall_when: ["content:refresh.?token|refreshToken|token.?rotat"]`(block-list 一行)
  - `pitfall_ask`/`pitfall_source` 走 `lumos set`(純量)。
  - ask=「多分頁並發 refresh:token 一次性輪換?前端 single-flight(僅一個 refresh 在飛其餘等待)?refresh 中的請求排隊或放行+失敗回滾?」;source=OWASP session management cheatsheet URL。

### S3 gapfill 填庫慣例(skill 文本,不改 gapfill 碼)
- pitfalls-gapfill skill 補一句:網搜坑放行後,除了進 linter-gap 表,**高危 pattern 型的坑另建 known-pitfall 節點**(三欄)——第一次碰某 pattern 才建(快取式)。★本案不改 gapfill 碼、不自動建★:定義慣例+種子證線,gapfill 產出 known-pitfall 節點是人放行時的動作。

## 審計修正紀錄
- **pre-flight(2026-08-09)**:①vault 尋找 `_vault_in(repo_root)`/find_vault 並列未裁→明定 _vault_in(比照 cmd_impact)②★自相矛盾★「刻意不做:不進硬閘」vs S1「--check 併入 section-required」——後者擴大被擋集合=進硬閘→改 advisory-only 不碰 --check rc(牙齒=panel 審裁定留痕)③_match_incident_triggers 不吐 pitfall_ask 值→明定以 node 反查 fields④★種子 flow-list `[content:...]` 零依賴 parser 不認(當純量字串→startswith miss→永不命中且 lint 抓不到)★→改 block-list+走 append⑤正向測試 fixture 須 --repo str(v) 非 v.parent(否則假測降級路徑)。

## 刻意不做
- 破 vault-free 讓消費端強制要 vault(有才查、無降級)。
- 預收全世界坑(快取按需,v1 已定調)。
- 改 gapfill 碼自動建節點(人閘不可拆;S3 只定慣例)。
- known-pitfall 進硬閘(--check 只加 section-required,仍是 rc 0/1 既有語意,不新增擋法)。
- 動 impact hook 的 glob-trigger 事故消費(code-time 面不碰)。

## 實務隱患
- **效能**:pitfalls spec 模式多掃一輪有 pitfall_ask 的節點(全圖但過濾後極少,~個位數),design 時一次性、非熱路徑;vault 缺直接跳。
- **[self-governance]**:--check 只多一個 section-required 觸發源(命中已知坑→要求寫實務隱患節),不新增擋法;寬 content regex 誤報=多讀一句;排除走 v1 的裁定留痕。
- **噪音防膨脹**:庫快取按需長(Growth test);某坑 regex 過寬到處彈=收緊 regex/降權(逃逸帳反向)。
- **向下相容**:vault 缺=行為不變(消費端零影響)——測試須含「無 vault 降級」案。
- **[prod-irreversible]**:不適用(唯讀+文本節點)。

## 驗收線
- S1 測試:`t_pitfalls_known_pitfall`(★正向命中案必用 `--repo str(v)`(vault 本身當 root),非 `v.parent`——後者踩 vault-not-found 分支=假測降級路徑,r1 勘誤★:content 命中 corpus→pitfall_ask 攤出+來源/無 pitfall_ask 的事故節點不誤觸/corpus 剝除:風險詞只在黑名單節不觸發/**無 vault 降級=行為同現況**/--check rc 語意不變(known-pitfall 命中不改 rc,advisory-only))。
- 種子驗:含「refresh token」的 spec 跑 pitfalls → single-flight 提問+OWASP 來源彈出。
- 不設「庫須達 N 條」門檻(快取按需長)。
