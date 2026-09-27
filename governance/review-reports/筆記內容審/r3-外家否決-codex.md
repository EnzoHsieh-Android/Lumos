severity: major

## F1 新增派工範本不會隨 `lumos update` 發到消費專案
severity: major
blocking: 是 —— 照 spec 實作後，消費專案缺少判定者必要範本，`prepare` 無法產生規定的派工詞。

引句:「★派工詞放在新範本檔★ `scripts/templates/note-audit-judge.md`」

1. 位置：〈做法〉第 3 節第 2 點、〈規範文字與路由〉、S13，`governance/review-reports/筆記內容審/r3-work.md:83`、`:109`、`:125`。
2. 失敗場景：工具鏈新增並追蹤 `scripts/templates/note-audit-judge.md`，消費專案依第 5 節執行 `lumos update`；更新器只複製 `_VENDORED_TOOLKIT + _VENDORED_TREE_FILES`，現有範本白名單只有 `graph-discipline.md`，所以新檔不會到消費專案，隨後 `note-audit prepare` 找不到自己的範本。
3. 查證：範本精確白名單見 `scripts/lumos:16903`、`scripts/lumos:16911`；實際複製迴圈只走該白名單，見 `scripts/lumos:17169`、`scripts/lumos:17173`。既有測試還要求受版控的 `scripts/templates/` 檔與白名單完全相等，新增範本卻不更新清單會直接翻紅，見 `scripts/test_lumos.py:11554`、`scripts/test_lumos.py:11564`。
4. 必須補入設計：把新範本登記進 `_VENDORED_TREE_FILES`，並以消費專案執行 `lumos update` 後確實取得範本、`prepare` 可渲染為驗收條件。

## F2 doctor 給的 CI 接線跳過首推空樹正規化
severity: major
blocking: 是 —— 新分支首推時 CI 後盾拿到全零 SHA，不能依設計檢查該範圍。

引句:「在它後面加一行 `python3 scripts/lumos note-audit check --diff "${{ github.event.before }}..${{ github.sha }}"`」

1. 位置：〈做法〉第 3 節第 9 點及 S16，`governance/review-reports/筆記內容審/r3-work.md:98`、`:128`。
2. 失敗場景：GitHub 新分支首推的 `github.event.before` 是 40 個零。現行正式 workflow 先把它換成空樹，再用 shell 變數 `$BEFORE..$SHA`；spec 新增的命令重新展開原始 GitHub expression，直接繞過前面的正規化。
3. 查證：正確接線在 `.github/workflows/ci.yml:127` 至 `:136`；現行 doctor 範本仍直接使用原始 expression，見 `scripts/lumos:23885` 至 `:23889`。現行範圍入口遇到無法解析的起點會直接跳過，見 `scripts/lumos:23977` 至 `:23981`。因此照字面複製會在首推漏查；若新命令改成 fail-closed，則首推固定因無效範圍紅燈。
4. 必須補入設計：note-audit 必須置於同一個 `run` 區塊並使用正規化後的 `"$BEFORE..$SHA"`；S16 增加 `before=000…000` 的首推驗收。

## F3 `decision-amend` 把 reflog 誤當成 fetch 成功時間
severity: major
blocking: 是 —— 正常執行錯誤訊息指定的 `git fetch --all` 後，命令仍會永久拒絕合法的未推決策修改。

引句:「對每個遠端,看它底下追蹤參照 reflog 裡最新一筆(fetch、pull、push、clone 都算)距今不超過 10 分鐘」

1. 位置：〈做法〉第 3 節第 4 點及 S12，`governance/review-reports/筆記內容審/r3-work.md:85`、`:124`。
2. 失敗場景：repo 已 clone 超過十分鐘、遠端分支內容沒有變；作者執行工具印出的 `git fetch --all`，遠端追蹤 ref 沒有新值可更新，reflog 仍不能證明「剛 fetch 成功」。命令再次檢查仍判過期。另有 `remote.<name>.skipFetchAll=true` 的正常設定時，`git fetch --all` 明確跳過該遠端，但 spec 同時要求每個遠端都新鮮，形成無法解除的拒絕。
3. 查證：Git 將每次 fetch 的結果寫進 `FETCH_HEAD`，而 reflog 記的是 ref 更新，不是「成功連線查過但值沒變」的時間；`--all` 也明定跳過 `skipFetchAll` 遠端。[git-fetch 官方文件](https://git-scm.com/docs/git-fetch)、[Git data model 的 reflog 說明](https://git-scm.com/docs/gitdatamodel)。
4. 必須改用每個遠端實際成功 fetch 的可驗事件；錯誤訊息所列命令必須能建立該事件，並加入「遠端無更新」及 `skipFetchAll` 的測試。

## F4 `decisions_items` 不會解析 spec 宣稱的決策編號、欄名或 valid
severity: major
blocking: 是 —— S3、S4 所需的完成審排除與內容編號沒有可執行的既有資料來源。

引句:「決策編號與欄名用既有的 `decisions_items` 解析取得」

1. 位置：〈做法〉第 1 節「所屬小標題」「計劃被收尾」及 S3、S4，`governance/review-reports/筆記內容審/r3-work.md:58`、`:62`。
2. 問題：`decisions_items` 只回傳 decisions 區塊起訖、各 item 的行範圍及兩個縮排值；它不回傳 `id`、各行欄名或 `valid`。照 spec 呼叫它，無法生成 `decisions/<決策編號>/<欄名>`，也無法排除 `valid:false` 的整條決策。
3. 查證：函式契約及完整回傳值見 `scripts/lumos:14088` 至 `:14120`。另一支 `parse_decisions` 只回語意 dict、不保留各欄行號範圍，見 `scripts/lumos:12919` 至 `:12973`；現況沒有一支既有函式同時提供 spec 所需的兩組資料。
4. 必須明定新的「item 範圍＋逐欄範圍＋解析值」共用介面，或寫死兩支解析器的對齊及失敗規則；S3、S4 要覆蓋 block scalar、巢狀清單、缺 id 與 `valid:false`。

## F5 只比範圍兩端會漏掉同一批推送內的重新收尾
severity: major
blocking: 是 —— 一個正常的 reopened-plan 批次推送會放過 spec 明定要做的第二次完成審。

引句:「收尾後又改回 doing、再收尾,每次收尾都審一次」

1. 位置：〈做法〉第 1 節「計劃在範圍內被收尾」、完成審編號及 S3，`governance/review-reports/筆記內容審/r3-work.md:62`、`:68`、`:115`。
2. 失敗場景：遠端起點的計劃已是 `done`；本機提交 A 改回 `doing`，提交 B 再改成 `done`，兩個提交一次推送。spec 定義只比較「範圍起點不是 done/superseded」與終點，這裡起點、終點都是 done，完成審集合為空，舊正文不會重新判。
3. 查證：既有範圍函式已取得並逐一走訪範圍內提交，見 `scripts/lumos:23590` 至 `:23606`、`:23620`；修訂稿卻只把完成狀態定義在整段範圍兩端，沒有使用這條提交序列找狀態轉換。
4. 必須按提交序列偵測非收尾→收尾轉換，至少用範圍內最後一次轉換的提交作完成審編號；S3 增加「base=done、途中 doing、tip=done」的單次批次推送案例。

## 逐節覆核

1. 標頭、白話、依據、PRIOR-ART：已讀，無其他 finding。
2. 〈判定者能不能用：小實驗〉：已讀，無 finding。
3. 〈做法〉第 0 節：已讀，無 finding；未把刻意排除的存心刪改判定檔重報。
4. 〈做法〉第 1 節：F4、F5。
5. 〈做法〉第 2 節：已讀，無 finding。
6. 〈做法〉第 3 節：F1、F2、F3。
7. 〈做法〉第 4 節：已讀，無 finding。
8. 〈做法〉第 5 節：F1。
9. 〈條款〉：F1、F2、F4、F5；其餘已讀，無 finding。
10. 〈回退〉：已讀，無 finding。
11. 〈實務隱患〉：F1、F2、F3；其餘已讀，無 finding。
12. 〈誠實界線〉：已讀，無其他 finding。
13. 〈前身 r3 發現怎麼處理〉、〈審計修正紀錄〉：已讀，無其他 finding。
14. `r3-delta.patch`：完整核對；F1、F3、F4 是 r2 新修法銜接出的洞，F2 是新增 CI 指令與既有 workflow 的不一致。
15. 交叉引用：八個 wikilink 目標及所有內部章節目標均存在；`Systems/筆記內容審` 與新派工範本是本案明示的新建產物，不列為壞引用。

## 實務隱患鏡頭

- 守衛面：有，F2、F5 會漏掉應擋範圍。
- 分發／接手：有，F1 使消費專案拿不到必要範本。
- Git 邊界：有，F3 的 freshness oracle 與 Git 實際語意不符。
- 資料解析：有，F4 缺少決策語意與行範圍的共同解析介面。
- 對外送出：無 finding；送出的筆記、上下文與程式碼及供應商邊界已明寫，沒有新增第二家供應商。
- 資源併發：無 finding；亂數逐件檔與 `_write_lf` 原子換名涵蓋判定檔競爭，治理帳衝突只影響觀測且已揭露。
- 可用性：無其他 finding；模型中斷有帶理由的 skip 出口。
- 容量與速度：無 finding；批次讀取、150 行切分、五秒重驗條件均有接電。
- 不可逆：無 finding；擋點在推送前，修改仍在本機且有明確撤線順序。
- 金流：無；功能不接觸付款、計費或金額資料。

總結: major；blocking 5 條。