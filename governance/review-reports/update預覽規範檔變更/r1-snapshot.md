---
type: project
status: doing
created: 2026-10-04
updated: 2026-10-04
tags:
  - type/project
  - status/doing
  - scope/platform
lands_in:
  - Systems/lumos-cli-lifecycle
related:
  - "[[Projects/交接2026-10-03_計劃]]"
  - "[[Systems/lumos-deinit]]"
summary: |-
  WHY:`lumos update` 加 `--dry-run`:先印這次會改哪些規範檔(CLAUDE.md、AGENTS 指示檔的紀律區塊)與哪些工具檔,專案一個檔都不動 [出處:Projects/交接2026-10-03_計劃 第 5 項,rtb 建議] [因:rtb 規定規範檔改動要使用者同意,現在 update 一跑就套用,只能事後看] [不選:每次 update 都停下來問(非互動環境與 CI 會卡住);只把套用後印的差異加長(還是事後)]
---
# update預覽規範檔變更_計劃

白話:`lumos update` 會把工具的新版裝進專案,順手改寫 CLAUDE.md 和 AGENTS 指示檔裡的紀律區塊。rtb 的規矩是規範檔要改得先問使用者,可是現在 update 一跑就改完了,只能事後補問。這次加一個只看不改的 `--dry-run`:先把「這次會改規範檔哪幾行、會換掉哪些工具檔」印出來,使用者看過、同意了,再跑一次真的套用。

依據:[[Projects/交接2026-10-03_計劃]] 第 5 項(rtb 2026-10-04 建議)。

PRIOR-ART: 同專案的 `lumos deinit --dry-run`(只印會動到什麼、不實際改動);外部是 terraform 的 plan/apply、`apt-get -s`——先算出計畫印給人看,確認後再套用同一份。
RETIRE-IF: 紀律區塊不再由 update 寫進消費專案(例如改成使用者自己引用一份共用檔),規範檔的改動就不經過 update,這個旗標就沒有存在理由。

## 範圍

- 做:`lumos update --dry-run`,預覽三件事——每個紀律區塊目標檔(CLAUDE.md、AGENTS.md 或 AGENTS.override.md)會怎麼變、哪些工具檔會被換新、其餘會做但這裡不細算的動作。
- 不做:互動式「要套用嗎?」問答;只套用部分檔案的選擇;改變不帶 `--dry-run` 時的任何行為。

## 做法

1. **來源照樣更新,專案不動**:`--dry-run` 跟真的 update 一樣先 `git pull` 工具來源(帶 `--no-pull` 就不拉),這樣預覽的就是接下來要套用的那一版。拉的只是工具來源那份 clone,不是專案。結尾印「確認後跑 `lumos update --no-pull` 套用剛才預覽的版本」——加 `--no-pull` 是為了套用時不會又拉到更新的版本,跟預覽對不上。
2. **紀律區塊的新內容要從來源的範本算**:真的 update 是先把範本複製進專案、再從專案裡的範本組區塊;預覽時專案裡的範本還是舊的,所以改從來源的範本算。把 `_reinject_claude_block` 拆成「算出新內容」與「寫回去」兩段,預覽只呼叫前一段;真的 update 走同一段算法,兩邊不會算出不同的結果。
3. **差異整段印出、不截斷**:套用時現在只印 CLAUDE.md 的前 20 行差異;預覽要讓人判斷能不能同意,所以每個目標檔都印完整差異。目標檔不存在(會新建)、有檔但沒有區塊(會接上)、區塊標記壞掉(不會自動改)也各講一句。
4. **工具檔清單**:用真的 update 那段同一份清單(`_VENDORED_TOOLKIT` 加 `_VENDORED_TREE_FILES`)、同一種比法(逐位元組比),列出會被換新或新增的檔。
5. **其餘動作只列名**:補設定骨架與忽略規則、設定 hooks 路徑、同步全域 hooks——這些不改規範檔,列一行「套用時還會做」就好。
6. **來源 repo 自身**:真的 update 在來源 repo 只刷新紀律區塊;`--dry-run` 就只預覽紀律區塊。
7. **回傳碼**:預覽成功回 0;來源無效、拉不下來照真的 update 的規矩回 2。

## 實務隱患

- **預覽跟套用對不上**:兩次之間來源又被拉新,或專案裡的檔被改了。前者靠結尾教人帶 `--no-pull` 套用;後者不擋,套用時照常印差異。
- **預覽不小心寫檔**:新增的唯一寫入點在「寫回去」那段,預覽路徑不呼叫它;驗收條款 [S1] 用真檔位元組比對守。
- 已排除:金流:本案只讀寫工具檔與規範檔,不碰任何付款或帳務
- 已排除:對外送出:預覽只印在終端;會連網的只有拉工具來源,那是 update 既有的行為
- 已排除:不可逆:預覽路徑不寫專案任何檔;拆函式後真的 update 的寫入行為不變,由既有紀律區塊注入測試守
- 已排除:守衛面:不改任何閘的判定,只新增一個唯讀旗標

## 驗收條款

- [S1] 當在消費專案跑 `lumos update --dry-run --no-pull` 時,專案工作目錄裡的每一個檔 應 一個位元組都不變,`git config core.hooksPath` 應 不變 [test:t_update_dry_run_writes_nothing]
- [S2] 當來源的紀律範本跟專案現有的區塊不同時,預覽 應 對每個目標檔印出完整的區塊差異,而且 應 跟接著真跑 `lumos update --no-pull` 寫進該檔的內容一致 [test:t_update_dry_run_rule_diff_matches_apply]
- [S3] 當來源的工具檔跟專案裡的不同或專案裡沒有時,預覽 應 列出這些檔,清單 應 跟接著真跑時「結尾自癒」補的檔一致 [test:t_update_dry_run_lists_vendored_changes]
- [S4] 當沒有任何規範檔會變時,預覽 應 明講「這次 update 不會改規範檔」 [test:t_update_dry_run_no_rule_change]
- [S5] 當在工具來源 repo 自身跑 `lumos update --dry-run` 時,應 只預覽紀律區塊,CLAUDE.md 與 AGENTS 檔 應 一個位元組都不變 [test:t_update_dry_run_source_repo]

## 回退

還原本案的提交即可:只新增一個旗標與預覽路徑,不帶旗標時行為不變,沒有資料要搬。

## 天花板

1. 預覽只細算規範檔與工具檔;補忽略規則、設定 hooks 路徑、同步全域 hooks 只列名不細算。
2. 預覽與套用之間的變動(別人推了新版、專案檔被改)只靠帶 `--no-pull` 與套用時照常印差異兜住,沒有鎖定機制。
