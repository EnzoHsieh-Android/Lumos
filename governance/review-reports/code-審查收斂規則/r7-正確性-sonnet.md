severity: minor

審查範圍:修補差異全文,加上 `scripts/lumos` 裡相關函式的現況(`_pq_decision_target`、`_residual_ref_key`、`_vault_in`、`_lens_residual_section`、`_lens_git`)。這輪只靠讀程式,沒跑實驗,所以沒有臨時目錄要清。

## Finding 1

severity: minor
blocking: 否 — 只影響鏡頭列哪幾條,推送升不升 high 不受影響
引句:「1 = 改到存著殘留決策的筆記、索引記的筆記換了、問答指到殘留索引裡有的合約;」

問題:鏡頭排序把「改到決策筆記」從 0 降到 1,跟「判 untestable 的新問答指到索引裡有的合約」同級。同級的排序鍵是 (級, 節點名),所以節點名排前面的先列。上限只有 5 條(`_LENS_RESIDUAL_MAX`)。

具體失敗情境:一次推送改了決策筆記 Z,在那條決策裡追加反例,這是 r5 G1 要抓的動作。同時它在帳裡塞了 5 筆以上指到真實合約(節點名字母序比 Z 前面)的 untestable 問答。輸入是這樣的推送,輸出是這 5 條問答合約佔滿 5 個名額,Z 落進「另有 N 條合約未列」。審查席要自己翻 diff 才找得到被改的決策。

這個寫法比 r5 的順序弱:r5 把改筆記排在 0,偽造問答擠不掉它。它只影響鏡頭怎麼列,高風險判定不受影響,且最後有「另有 N 條未列」的提示。

佐證:``file: `scripts/lumos:44686`(`_lens_residual_wanted` 的 `want[ck] = 1` 與排序 `sorted(want, key=lambda ck: (want[ck], ck))`)``

## Finding 2

severity: minor
blocking: 否 — 只影響非 `docs/` 佈局專案的邊角,而且要同時有舊索引或解不出的指標
引句:「「圖譜的檔」= 圖譜資料夾底下的 .md,資料夾照 _vault_slug_of(bare=True」

問題:`_residual_note_hits` 現在判「改到圖譜的檔」,只認 `docs/<名>-knowledge/` 與 `docs/knowledge/` 底下的 `.md`。舊寫法會看殘留指標的頂層資料夾(例如 `Projects/`),舊註解還說「圖譜放在別處的專案靠它」。

`_vault_in` 認得的第三種佈局是獨立 vault,也就是 repo 根有 `MOC/` 加 `Systems/`,圖譜檔路徑是 `Projects/x.md`、不在 `docs/` 底下。這種 repo 裡,索引是舊格式或有解不出的殘留,卻改了圖譜筆記,`gfiles` 是空的。`notes_unknown` 不會出現,分級是 light,該升沒升。

此外,`_vault_slug_of` 本來就不認根目錄式 vault,所以改用它是刻意縮窄。但修補沒有交代這個退步,也沒有測試覆蓋。

佐證:``file: `scripts/lumos:44693`(`gfiles = sorted(...)`)、`scripts/lumos:26351`(`_vault_in` 第三種佈局)``

## 已讀,無 finding

- **誠實改動被誤升**:只改程式碼、沒碰 `.md` 圖譜檔的推送,在 `gfiles` 為空時不會因 `notes_unknown` 升高。有解析出路徑的殘留,會先確認路徑在起點樹裡,才比對有沒有被改到;沒在樹裡的會升 high,不算誤升。
- **舊格式索引升級後第一次推送**:舊格式加改圖譜筆記會升 high,這是原本就有的行為,理由句叫人 `--reindex`。這個升級無法避免:`--reindex` 的提交本身還是以舊索引為起點。
- **doctor 舊格式遮罩**:`legacy` 以 `k[:3]` 為鍵,只遮掉沒有 `notes` 欄的那幾筆,不影響其他條目的比對。新格式條目的 `unresolved` 值用 JSON 正規形比對,新舊雙方對得上。
- **`unresolved` 新欄位新舊互讀**:r5 讀者遇到 dict 值會落到 `None`,保守地判位置未知。新讀者遇到 r5 索引的 `notes` 缺鍵,會走「notes 沒記這筆」分支,理由句也對得上。
- **重複鍵衝突處理**:衝突或形狀不對時理由句有蓋掉,不會錯講成舊格式。
- **`_vault_slug_of(bare=True)`**:預設參數不變,6 處既有讀者都沒傳第二參數,行為不變。
- **`_res_unknown`**:判斷是在注入框整段文字裡找「算不出來」字樣,不是只看第一行,能抓到。
- **`_lens_residual_absent`**:3 秒上限、任一 git 呼叫失敗回 False。目前沒有找到會讓真有殘留的 repo 被當成「沒有」的路徑。
- **`ls-tree --full-tree` 的路徑基準**:跟索引相對路徑的基準若在 monorepo 子目錄下有落差,這是 r5 就有的問題,不是這輪新增。

最高等級 minor,blocking 0 條。
