severity: major

（來源：設計審 r1 架構對齊席，sonnet，2026-09-14）

## 問一：分層與依賴方向

對齊 ✓。S1 要求把型別與狀態標籤一律從純量欄位當場合成、所有消費點走同一個 helper，這正是本專案既有模式：小型純函式放檔案前段、被讀路徑多處呼叫。

file: `scripts/lumos:441`（status_of，直接讀 fields 而非讀標籤，15 處呼叫涵蓋 query/context/lint/sync-verified-by）
file: `scripts/lumos:390`（as_list，59 處呼叫）
file: `scripts/lumos:2696`（_rank_fields，被 2757 與 9670 呼叫）

目前型別/狀態標籤的字面讀取散落至少五處：
file: `scripts/lumos:1202`（doctor Check M）
file: `scripts/lumos:4451`（lint 漂移守衛）
file: `scripts/lumos:9774`（context 頭部過濾）
file: `scripts/lumos:10143`（query 顯示過濾）
file: `scripts/lumos:11163`（cmd_set 自驗）

S1 把它們收斂成一個共用 helper，方向正確、不是新發明的分層。本專案是單檔 CLI，「層」是文件節點的治理邊界而非 Python 模組邊界，讀寫兩側共用工具函式本來就是常態，沒有跨層直呼問題。唯一沒講清楚的是 helper 放在檔案哪個區段，屬實作細節，不影響對齊判斷。

## 問二：命名與錯誤處理

對齊 ✓（在有具體命名可查的範圍內）。S10 的消融旋鈕雖未給出精確變數名，但 PRIOR-ART 明講要照 A1/A3 前例走 env 旋鈕切換。
file: `scripts/lumos:2737`（LUMOS_RANK_MOC_MULT）
file: `scripts/lumos:2743`（LUMOS_RANK_STATUS_MULT）
S6 的凍結退場訊息也對齊既有 feature/area 的 lint warning。
file: `scripts/lumos:4394`

白話三段式錯誤訊息慣例無從查——這份 spec 沒有給出任何一句實際會印出的訊息文字，判不準，標 ⚠ 交編排者，不硬判。

## 問三：第二種做法

### 不對齊 ①：清理器的形狀完全沒講，可能繞過既有唯一寫入路徑

severity: major
blocking: 是

S5/S6/S7 都需要一個能批次改寫 frontmatter 的「清理器」，spec 六次提到這個詞，但從未說它是不是 lumos 子命令。

引句:「清理器要是冪等的，跑兩次結果一樣」
引句:「清理前工作目錄必須乾淨（清理器自己先檢查，不乾淨就拒跑）」

本專案對「一次性回填遷移／批次維護」有明確既有形狀，都是註冊在 argparse 子指令表、走 atomic_write_verify 的正牌 lumos 指令：
file: `scripts/lumos:27588`（decision-reindex，一次性回填 + --all 批次）
file: `scripts/lumos:9523`（sync-verified-by，dry-run 預設 + --apply）
file: `scripts/lumos:27626`（archive）

而圖譜明文寫著八個寫入原語是專案層圖譜寫入的唯一安全路徑、取代手改 frontmatter：
file: `docs/lumos-toolchain-knowledge/Systems/lumos-cli-write.md:26`

若清理器被實作成 scripts/lumos 之外的獨立腳本（spec 完全沒排除這個可能），就是繞過這條唯一安全路徑、自己重造一套 frontmatter 寫入邏輯——典型的「之後每個接手的人要在兩套之間猜」。

### ② 消融旋鈕

對齊 ✓，非新做法。PRIOR-ART 已明確承諾走既有 env-knob 消融慣例。

### ③ 凍結退場

對齊 ✓，非新做法。PRIOR-ART 明講照 2026-08-05 的 feature/ 與 area/ 前例（讀側仍認、寫側警告），與既有 lint 處理一致。
file: `scripts/lumos:4394`

補充（不算 finding）：S1 把「反正規化欄位＋同步器＋漂移守衛」整組換成「讀時合成」，本身確實是新模式，PRIOR-ART 自己也承認是同一題的另一個標準答案。但舊做法在 S3 被整組拔除、不是並存，未來不會有兩套邏輯同時活著讓人猜，所以不落入本席 major 錨定範圍。
file: `scripts/lumos:10841`（edit_fm_sync_status_tag，將被拔除）

## 問四：落點合不合理

對齊 ✓。lands_in 選 lumos-cli-read／lumos-cli-write／retrieval-ranking 三篇有強前例：同類型的既往標籤治理計劃都是 related 恰好指向前兩篇，而且落地成果真的寫進了那兩篇的 summary。
file: `docs/lumos-toolchain-knowledge/Projects/標籤結構收編_計劃.md:11`
file: `docs/lumos-toolchain-knowledge/Projects/狀態標籤同步守衛_計劃.md:11`
file: `docs/lumos-toolchain-knowledge/Systems/lumos-cli-write.md:34`
file: `docs/lumos-toolchain-knowledge/Systems/lumos-cli-read.md:19`

第三篇 retrieval-ranking 對應 S2 與 S10，屬於它的本業，也合理。三篇目前份量都不大（22/16/11 行 KEY），未觸及「每支檔有家」或節點過肥的機械門檻，不構成另開新篇的理由。

⚠ 一個與本設計無關、但落點會踩到的既有缺口：lumos-cli-write.md 的 frontmatter 完全沒有 about_code 欄位（不是空清單，是整個鍵缺席），跟它正文聲稱的角色對不上。這是圖譜既有的資料缺口、不是這份設計造成的，但編排者可能想一併讓實作者補上。

不對齊共 1 條，其中 major 1 條
