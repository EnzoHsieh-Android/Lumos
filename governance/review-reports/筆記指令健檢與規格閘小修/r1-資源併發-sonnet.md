severity: major

資源併發鏡頭。以 r1-snapshot 為準,前掃已修的項目不重報。

## 第 1 節(summary-add、summary-line 寫前檢查)
已讀,無 finding。
- `_drift_fix_shape_err` 每次呼叫只做一次 `ls-files -s`,規模是單篇、單行。
- 寫入走既有的鎖與 `atomic_write_verify`。

## 第 2、3、4 節
已讀,無 finding。這三節是文字與純字串判定,沒有 I/O 或大輸入問題。

## 第 5 節(lint 先唸寫下就成立的回頭條件)

### 1. 每篇 lint 多 2 次 git 呼叫,但 `lumos doctor` 會對每篇筆記都跑 `_lint_collect`
severity: major
blocking: 是(照字面實作會讓 doctor 變慢約一分鐘,實作者會做出壞系統)

- **spec 段落**:第 5 節做法第 2 點,加上〈實務隱患〉的效能條。
- **問題**:效能條只算「單篇,毫秒到百毫秒」。但 `lumos doctor` 的 L 段會逐篇呼叫 `_lint_collect`。
  - 這份計劃要新增的 F29 提醒就掛在 `_lint_collect` 裡。
  - 所以 F29 的 `git show HEAD:<這篇>` 與 `_nodehome_list(root, "index")` 會被 doctor 對每一篇各跑一次。
- **具體例**:本 repo 圖譜約 894 篇 .md,git 追蹤 14705 個檔。
  - 輸入:跑 `lumos doctor`。
  - 預期:幾乎不增加時間,因為大多數筆記根本沒有條件式回頭條件,不需要比對上一版。
  - 照 spec 字面實作:實測單次 `git ls-files -s -z` 約 25ms,`git show HEAD:<筆記>` 約 28ms。894 篇約多 45 到 50 秒。
  - 另外 `ls-files` 的結果每篇重複算,內容完全相同。
- **spec 沒寫的兩個關鍵**:
  - 沒寫「這篇抽不出任何條件式回頭條件或 RULE 撤除條件就整段跳過、不呼叫 git」。
  - 沒寫「索引清單在一次 doctor 或一次 `_lint_collect` 迴圈裡只讀一次並共用」。
- **佐證**:file: `scripts/lumos:2009` 是 doctor 的逐篇迴圈 `for rel, n in sorted(notes.items())` 內的 `_lint_collect(env, rel)`。
- 引句:「與一次讀索引清單(單篇,毫秒到百毫秒)」
- **該怎麼寫進 spec**:
  - 抽出的條件組是空的就先 return。
  - 索引清單由呼叫端快取一次,doctor 與 `cmd_lint` 都吃快取。
  - 驗收條款補一條:無條件的筆記不呼叫 git。

## 第 8 節(`git check-ignore --stdin -z`)

### 2. 整批送進 check-ignore,一個倉庫外或越界的路徑會讓整批 rc128、結果截斷
severity: minor
blocking: 否(邊界情形,只影響誤報與漏報,不會做出壞系統)

- **spec 段落**:第 8 節做法第 2 點。
- **問題**:spec 只說「整批問一次」,沒定義非 0 或 1 的回傳碼怎麼處理。
- **具體例**:我在臨時 git repo 實測 `printf 'a/b\0/etc/x\0c\0' | git check-ignore --stdin -z`。
  - 輸出:`fatal: ... '/etc/x' is outside repository`,rc=128,只吐出已處理到那點之前的 `a/b`,`c` 之後不處理。
  - 觸發路徑:筆記寫 `foo/../../x` 這類越界相對路徑。它第一段是真目錄,能通過 doctor P 段的 top_dirs 過濾,也能被 refcheck 抽出。
  - 照 spec 的結果:實作者若只拿 stdout 當「被忽略集合」,rc128 時漏掉排在後面的被忽略路徑,doctor 反而多列「已不存在」假陽性。
- **該補的規則**:rc 不是 0 或 1 時視同「不是 git,跳過這一步」。或先剔除含 `..` 段、絕對路徑的 token,再送進去。
- 引句:「不存在的路徑先整批問一次」

## 第 9 節(W6,doctor S8 看工作目錄版本)

### 3. 未追蹤檔列舉沒限定 pathspec,大型未忽略目錄會拖慢 doctor
severity: minor
blocking: 否(spec 能被實作者在實作時補上範圍,不致做錯決定)

- **spec 段落**:第 9 節 W6 做法。
- **問題**:文字說「圖譜 Systems 底下」,但指令 `git ls-files --others --exclude-standard` 與 `git diff --name-only` 沒寫 pathspec。
- **具體例**:消費專案(例如 order-web)的工作目錄若有未被 gitignore 的大目錄(建置產物、暫存匯出),無 pathspec 的 `--others` 會掃整個工作目錄。
  - 預期:只掃 `<vault>/Systems`,毫秒級。
  - 照字面:可能掃數萬檔。每次 doctor 都付一次代價。
  - 後半「只讀有變的節點」也沒寫限定是 Systems 底下的 .md。
- **該怎麼寫進 spec**:明寫 `-- <vault_rel>/Systems`,兩個指令都加上。
- 引句:「另列圖譜 Systems 底下未追蹤」

## 第 6、7、10(B1、B2、W10)、11 節
已讀,無 finding。

- **第 6、7 節**:都是單篇判定。第 7 節的 `_refcheck_scan` 只多一次 `exists`,不涉及迴圈或子程序。
- **第 10 節 B3(治理帳讀取)**:spec 已先用字串篩行再解 JSON。
  - 本 repo 治理帳約 20MB,篩行成本是毫秒到百毫秒級,可接受。
  - 只在審查帳找不到留痕時才讀一次,不是每份計劃各讀一次。
- **第 10 節 B2(推送閘多查 done 計劃)**:只多查這次範圍內被改到的 done 計劃,不會因歷史累積變慢。
- **第 10 節 W10(警告去重的模組層集合)**:key 是 (平台, root),每次警告只多存一筆,不會無限成長。
  - 測試以同一個 process 載入模組,相同 (平台, root) 的跨測試洩漏我只想得到推測情形,給不出具體失敗場景,不標。
- **第 11 節**:不做項目,無資源面。

## 風險類
- **守衛面**:本鏡頭不涉及。只看效能與記憶體,不判斷擋或放行的對錯。
- **舊資料與舊帳相容**:不涉及資源面。
- **在途分支**:不涉及資源面。
- **其他會談交界**:威脅模型限單人、AI 依序操作,不報多程序併發。
- **子程序收掉**:新增的 git 子程序都是 run-and-wait 的短命呼叫。
  - 這一點我只是依 spec 描述判斷,尚未驗證實作。
  - spec 沒有長駐程序或暫存工作樹,因為 `--red-at` 已被 d2 排除。

最嚴重 severity: major,blocking 共 1 條。
