severity: minor

整合鏡頭(合約與圖譜一致/知識同步)的結論是 0 條 major、4 條 minor。文件說的程式行為,我都在修後版本 f14f6808(即 HEAD 13c893f9)的 `scripts/lumos` 上逐項跑過。lint 對 11 個改到的節點都是 0 問題。`-k` 六組測試(doc_sync、door_rule_version_pin、templates_security_web、t_infra、test_infra_path、stack_key_)全綠。文件引用的所有 `t_…` 測試名在 `scripts/test_lumos.py` 都有定義。

**文件與程式對得上的部分(已驗)**
- **門規則版本**:`_DOOR_RULE_VERSION=13`、`_DOOR_SCAN_LOGIC_VERSION=8`,和規格閘節點、計劃、`雙向門放行_計劃` 的說法一致。
- **量法程式段**:計劃做法 9 的 `NEW` 兩條正規式與程式的 `_PITFALL_SEND_WHEN`、`_PITFALL_PAYMENT_WHEN` 逐字相等,所以 2027-01-15 的 REVISIT 照這段重跑沒有問題。
- **送出例外與 PAYMENT 尾碼**:我把計劃寫的 17 個「照算」例句、6 個「不算」例句,和 PAYMENT 的放過與照算各例全跑一遍,都和文件一致。例句包括 `PAYMENT_GATEWAY_TIMEOUT`、`PAYMENT_AMOUNT_LIMIT`、`PAYMENT_COUNT`、`PAYMENT_TIMEOUT_MS`、`PAYMENT_MAX_RETRIES`。放過的尾碼表(TIMEOUT/TTL/DELAY/INTERVAL 可接單位,加單位本身與 RETRIES/RETRY_COUNT/MAX_RETRIES)也和程式相同。「到」的排除字 收拿做直等遇得想看找達 也一致。
- **e2e 三種路徑**:我對 26 個路徑逐一跑了 `_stack_key_for_file`,和文件描述一致。
  - `e2e/` 資料夾:`e2e/*.ts/.py/.mjs`、`tests/e2e/a.ts`、`apps/web/e2e/x.ts` 都是 infra。
  - `.e2e.` 檔名:`order.e2e.ts` 是 infra。
  - `.sh` 檔名:`run_e2e.sh` 是 infra。
  - 不收:`src/e2e/cipher.py` 回 py,`src/crypto/e2e.ts` 回 vue,`db/seeds/x.sql` 回 sql,`e2e/a.kt` 回 kt,`e2e/fixtures/data.json` 回 None。
  - 另外,根目錄 `tests/e2e/…` 確實擋不到 `_PITFALL_DIFF_TEST_PAT`,文件這一點屬實。
- **題數與 id**:infra 6 題、`_REQUIREMENT_FACETS` 共 25 列(前端面 10 列加 `verify-infra-script`),都和文件相符。效能檢核目錄「…/dart=7/infra=6」的總數和程式相符。
- **舊說法清掃**:`seeds`、`fixtures`、`LIMIT`、`COUNT`、「給至往」這幾個舊說法,全 repo 只剩 `規格閘.md:62` 一處(下面第 1 條)。計劃內提到舊寫法的地方都明寫是被取代的歷史,例如做法 7 的「代碼審 r1 收窄」。

**Findings**

1. 規格閘節點的金流詞表說明還是舊規則
severity: minor
   - blocking: 否
   - 位置:`docs/lumos-toolchain-knowledge/Systems/規格閘.md:62`(金流詞表那列)。
   - 問題:文件寫 `_COUNT` 這類調整參數結尾的 PAYMENT 不算,但修補把 `_LIMIT`、`_COUNT`、`_WINDOW` 移出了例外。
   - 例:輸入 `PAYMENT_COUNT`,文件讀者預期不算金流,實際在修後版本回「金流」。同節點第 40 行和計劃已改成新說法,所以節點內部也不一致。
   - 佐證:`ORDER_PAYMENT_RETRY_COUNT` 仍不算,因為它走 `_RETRY_COUNT`。
   - 歸因:有證據的修復回歸。修前版本 d2297c94 的 `_door_keyword_hits("PAYMENT_COUNT")` 回空,修後回金流;修補只改了該節點第 38 行,漏了這一列。
   - 引句:「全大寫識別字以 _TIMEOUT、_COUNT 這類調整參數結尾時的 PAYMENT 不算」

2. 計劃「天花板」列出的四個未命中例句,有兩個現在其實會命中
severity: minor
   - blocking: 否
   - 位置:計劃做法 9 的「天花板」行,這一行是修補自己改寫的。
   - 問題:文件說這些句子比不到,但修補新增的「後面的到」去處規則讓兩句命中。
   - 例:
     - 「送出請求後將資料同步到 ERP」:修前 `[]`,修後「對外送出」。原因是「同步到」的「步」不在排除字裡,所以「到」算去處。
     - 「表單送出後通知客戶」:修前 `[]`,修後命中,因為「客戶」是去處詞。
     - 另外兩句仍不中,和文件一致:「將重試請求送出」、「送出請求,包含客戶資料到外部」。
   - 影響:三個月後有人拿這兩句當「已知漏判」去補測試或詞表,會發現它們本來就中。
   - 歸因:有證據的修復回歸。修前和修後我都跑了。
   - 引句:「「送出請求後將資料同步到 ERP」(到隔太遠以外,同步不在詞表)、「表單送出後通知客戶」」

3. 效能數字還是舊正規式的量測
severity: minor
   - blocking: 否
   - 位置:計劃〈實務隱患〉的「效能」行。
   - 問題:「540 萬字與 700 萬字單行輸入下都在 0.2 秒內」是 r1 對舊的兩條正規式量的。新的 `送出` 正規式不是這個量級:540 萬字不含「送出」的文字確實約 0.23 秒,但滿是「請求送出」的 400 萬字要 5.0 秒。經 `_door_keyword_hits`,100 萬字約 2.7 秒。
   - 影響:仍是線性、沒有回溯爆炸,所以只是數字過期,不影響結論。
   - 歸因:有證據的修復回歸,因為正規式是修補改的。
   - 引句:「兩個新詞表正規式在 540 萬字與 700 萬字單行輸入下都在 0.2 秒內」

4. 角色與表態閘的描述漏了 `.e2e.` 檔名和 node 後端
severity: minor
   - blocking: 否
   - 位置:`代碼審前後端角色鏡頭_計劃.md` 做法 1(b)、`arch-alignment-lens.md`、`棧別提問表態閘.md` 的 infra 段。
   - 問題:這些處都寫成「`e2e/` 資料夾裡的 py/ts/js」,但程式還有 `.e2e.` 檔名這條路,且該路徑不排除 `src/`、`lib/`。
   - 例:`server/order.e2e.ts` 在 node 後端 package 底下,修前判後端並附後端卡,修後是 infra 並判不出。文件的「原本走 vue 判前端、走 py 判後端」也沒列 node 判後端。
   - 歸因:未判定。這個遺漏在 r2 前的文件就有,修補只是沒補到。
   - 引句:「infra(.sh 與 e2e 資料夾裡的 py、ts、js 家族,2026-10-15」

另有一些更小的文件偏差,各不到單獨一條:
- 計劃做法 6 的觸發表和效能檢核目錄的表沒列 `process.kill(`。前者另缺 infra-portable 的 `timeout`。r1 補的觸發字有寫在效能檢核目錄的 prose,所以不算缺漏。
- `情境出題` 的前端字樣清單沒寫英文 `frontend`、`reactjs`、`vuejs`;程式的 `_REQ_FE_WHEN` 認這些。
- `每輪修補差異派工.md` 結尾新增的 `SEE:` 行帶了一句話,和 CLAUDE.md「SEE 不寫句子」的規定不符。lint 沒抓到,而且它在正文不在摘要。

**對三問的回答**
1. 原問題的修復效果:送出與 PAYMENT 例外、e2e 路徑收窄的行為證據,上面已驗,文件和程式一致,量法程式段與常數逐字相等。文件層面的殘留是第 1 到 3 條。
2. 修補處相鄰路徑:`.sh` 一律 infra、樣式內的 kt/java/sql 照原棧、資料檔回 None、claims 迴圈只跳過樣式內檔案,這些在 `scripts/seed-prod.sh`、`scripts/setup.sh`、`e2e/a.kt` 等例子上都成立。路徑正規式對 20 萬字路徑約 0.01 秒,沒問題。
3. 新發現的修前修後結果:第 1、2 條的修前與修後結果都已實跑,見各條;第 3 條只有修後數字,修前數字沿用文件舊值,所以只標「過期」,不另外做修前比較。

**未驗範圍**:`templates.md` 的內文逐句內容、`lumos doctor` 的全量輸出(只看到與本案無關的既有警告)、消費專案的實際計劃。

**我做錯的一件事**:我一度在 web-fe-knowledge 跑了 `git checkout -q --detach`,把 HEAD 移到無分支狀態。我立刻用 `git symbolic-ref HEAD refs/heads/EnzoHsieh-Android/web-fe-knowledge` 改回,HEAD 仍是 13c893f9,工作樹檔案沒動,`git status` 已確認。留下的暫存都已用字面絕對路徑刪除。

最嚴重 severity:minor。blocking 共 0 條。
