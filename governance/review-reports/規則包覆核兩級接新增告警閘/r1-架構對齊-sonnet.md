severity: minor

## 問一、分層與依賴方向:結構對得上,沒有跨層直呼
計劃只動兩處:`check.py` 的 `CONFIGS` 與 `_DIR_SEVERITY`,和 `linter精選目錄` 的宣告範本。擋不擋、放行、指紋仍交給既有新增告警閘,計劃也寫了「不改新增告警閘本身」。這跟現況一致:規則包只產 SARIF,閘讀 SARIF,放行檔由 `lint-waive` 管。沒找到跨層呼叫。下面 F1 是同一個分層的小偏差:三處檢查沒有一起列入改動。

## F1 「依據不足不擋」的判法換軸,連動的三處沒列全
severity: minor
blocking: 否
引句:「「引用出處不全的列只准 hint 級」那條檢查改成「只准放在 `rules-hints-unsourced/`」」
佐證 file: `configs/ast-grep/kotlin-android/check.py:393`(`r["severity"] != "hint"` 就報「只准 hint 級」)
- 現況的「依據不足不擋」靠兩件事:嚴重度只准 hint,加上範本不宣告 `sgconfig-hints.yml`。新做法把 `rules-hints/` 也接上閘,這時 hint 不再代表「不接閘」。真正不擋的只剩目錄,所以換軸是對的,而且是替換、不是並存。
- 但這個改動牽連 `check.py` 的另外三處,計劃的「做 2」只點名了 `CONFIGS`、`_DIR_SEVERITY` 和 `catalog_problems` 那一條:
  - `check.py:665` 的訊息寫死「hint 放 rules-hints/、info 放 rules-review/」。加了第四個目錄後,這句會誤導。
  - `check.py:749` 的「rules/、rules-review/、rules-hints/ 都是空的?」沒列第四個目錄。
  - `check.py:24` 的三級說明註解,計劃的「做 5」有點名,但 665 和 749 兩句沒有。
- `_DIR_SEVERITY` 反方向也沒規則:一條有出處的 hint 規則放進 `rules-hints-unsourced/` 不會報,等於悄悄少擋一條。這是對稱性缺口,不是第二種做法。

## 問二、命名與錯誤處理:命名跟既有一致,自檢錯誤句沒寫
## F2 新自檢錯誤句與 `_DIR_SEVERITY` 的值沒寫明
severity: minor
blocking: 否
引句:「`_DIR_SEVERITY` 讓 `rules-hints-unsourced` 只收 hint」
佐證 file: `configs/ast-grep/kotlin-android/check.py:27`(現值 `{"rules-hints": ("hint",), "rules-review": ("info",), "rules": ("error", "warning")}`)
- 新目錄名 `rules-hints-unsourced` 和設定檔名 `sgconfig-hints-unsourced.yml` 沿用既有的 `<目錄>` 配 `sgconfig-<尾綴>.yml` 對應。尾綴 `-unsourced` 是英文,跟 `-review`、`-hints` 同風格,命名一致。
- 錯誤句只有預期值表寫「報問題」,沒寫新句子的格式。既有格式是 `(規則 id, 一句中文原因)`,例如 `check.py:394` 的「引用出處不全的 {id},只准 hint 級」。實作時要沿用這個二元組,並把原因換成「只准放 rules-hints-unsourced/」,否則報出來的原因會跟現行句子不一致。
- ⚠ 計劃「做 3」的備案是實驗發現提示級在 SARIF 不出現時,把 `rules-hints/` 的嚴重度提到 info。那樣 `rules-hints` 與 `rules-review` 會變成同值,`_DIR_SEVERITY` 靠嚴重度區分目錄的邏輯會失效。計劃沒說這時怎麼辦,實作時才會碰到。

## 問三、第二種做法:沒有第二個放行出口,只有一個判法換軸
- 放行出口只有 `lint-waive`,計劃明寫沿用,沒有另造宣告檔或表態題。這跟既有放行流程對齊(`scripts/lumos:41735` 的放行指令組裝、`scripts/lumos:4226` 起的 AI 放行待看)。
- 「依據不足就不擋」只有一種做法(目錄不接閘),原本的嚴重度規則被替換。見 F1,不算第二種。

## 問四、落點:`lands_in` 對,但新檔沒登記到家,前案作廢標法不明
## F3 新增設定檔沒列入 `about_code`,舊描述也沒一併改
severity: minor
blocking: 否
引句:「新增 `sgconfig-hints-unsourced.yml` 只載這個目錄」
佐證 file: `docs/lumos-toolchain-knowledge/Systems/kotlin規則包.md:8`(`about_code` 現列 5 支檔,沒有第四份設定檔)
- 專案規矩是每支程式檔都要有家,而 `sgconfig-hints-unsourced.yml` 是新檔。計劃只說「`Systems/kotlin規則包` 補 WHY」,沒說要把它加進 `about_code`。
- 同一篇的「檔案」節還有兩處會過時,計劃只提到補 WHY:
  - `kotlin規則包.md:62` 說 `sgconfig-review.yml` 「接上前範本不接」,並指向要作廢的前案。
  - `kotlin規則包.md:63` 說 `sgconfig-hints.yml` 「範本預設不接」。
  - 這兩句要改寫,否則同一個節點裡新舊說法互相打架。
- `Systems/linter精選目錄` 的第 198 行「提示級規則預設不接」,計劃的「做 4」有寫要改,這點對齊。

## F4 前案作廢的標法只寫「標作廢」,沒說欄位
severity: minor
blocking: 否
引句:「前案計劃標作廢、指向本計劃」
佐證 file: `scripts/lumos:2531`(作廢判定看 frontmatter `status` 是 `superseded`);例 `docs/lumos-toolchain-knowledge/Projects/detekt協程規則真的在跑_計劃.md:3`(`status: superseded`)
- 既有做法是把 frontmatter 的 `status` 改成 `superseded`,連同 `tags` 裡的 `status/` 標籤,再用 `lumos set` 改。
- 計劃沒寫要改哪個欄位,也沒說前案已寫進圖譜的 `decisions`(d5、d6)是否同標 `superseded_by`。
- 這個標法同時會影響前案的驗證紀錄與 `kotlin規則包.md:62` 的連結(見 F3)。

四問各答完。不對齊共 4 條。
