severity: major

以下逐節審 /tmp/cpe/r1.md 的本案設計。主要問題:背書只證明「某支測試咬得住某個壞法」,但設計沒有要求那個壞法和被問的併發或效能題有關,過期判定也看不到測試本身。

**1. 背書沒有綁題目,任何合約的 killed 都能替任何被標題目背書**
severity: major
blocking: 是——照字面實作會把該擋的放掉。
- 位置:〈satisfied 要什麼證據〉第 2 點。
- 問題:背書判定只比對測試名,沒有要求那條配方的壞法和被問的題目有關(例如「拿掉鎖」「逐筆改回批次」)。
- 重現:某測試綁的 ★INVARIANT★ 是「輸出格式」,配方把格式字串改掉後測試紅,判 `killed`。表態 `sql-nplus1` 或 `java-concurrency` 為 `satisfied` + `test:那支測試`,檢查會回「強證據」。
- 補充:被標題目往往是多面向的複合題。`sql-transaction` 同時問鎖時間、隔離等級、鎖順序、parameter sniffing;`java-data` 問 N+1、LAZY、分頁、`@Transactional` 自呼叫。一條 killed 就背書整題,沒有定義要背書哪個面向。
引句:「找同一個測試名、`verdict=killed` 的最新一筆」
file: `scripts/lumos:21017` `sql-transaction` 是複合題;`scripts/lumos:21070` `java-data` 同樣是複合題。

**2. 過期判定只看配方檔,測試檔和被保護的程式碼改動都看不到**
severity: major
blocking: 是——照字面實作會把該擋的放掉。
- 位置:〈satisfied 要什麼證據〉第 2 點。
- 重現 1:killed 之後,測試被改弱(斷言拿掉、被 skip、被改成空測試),或鎖被搬到另一支檔。配方檔沒動,背書仍是「強證據」。
- 重現 2:紀錄只存配方檔,沒有記測試檔路徑,無法檢查測試檔是否被改過。
引句:「從那筆的 `commit` 到被推送版本之間,`files` 裡任一支檔有改動」
file: `scripts/lumos:13198` kill 的事件只取配方的 `file`,沒有取綁定測試的檔。

**3. 取「最新一筆 killed」會忽略更新的 survived / drifted,也會把多配方拆成互相干擾**
severity: major
blocking: 是——同一測試多條配方時會判錯。
- 重現 A:同一測試先 killed,之後測試被改弱,重跑變 `survived` 或 `abort`。先過濾 `verdict=killed` 再取最新,更新的失敗紀錄被無視。
- 重現 B:同一測試綁兩條配方 R1(檔 a)、R2(檔 b),R2 的檔在事件後被改,取「最新」就判過期,其實 R1 背書完整;反過來只要有一條 killed 就夠,其餘 survived 被無視。
- 缺口:spec 沒定義一支測試多條配方要全部 killed 還是任一。
引句:「找同一個測試名、`verdict=killed` 的最新一筆」

**4. 比對只用測試名,多平台同名測試會互相背書,ledger 的測試名格式也沒正規化**
severity: major
blocking: 是——多平台同名測試會判錯。
- 重現:ios 平台有 `testRace` killed;android 也有同名 `testRace`。表態 `test:android:testRace` 會被 ios 的 killed 背書。
- 格式不一致:ledger 的 `test` 欄來自原樣配方,可能帶平台前綴、裸名或 Kotlin 反引號;spec 沒說正規化規則。
引句:「找同一個測試名、`verdict=killed` 的最新一筆」
file: `scripts/lumos:13116` kill 在有平台時才去掉平台前綴並 strip 反引號。
file: `scripts/lumos:36954` `_dispositions_split_test` 裸名歸 default 平台。
file: `scripts/lumos:13198` 事件的 `test` 來自原始配方。

**5. 事件的 `commit` 在多平台下不是每條配方跑的當下 HEAD**
severity: major
blocking: 是——多平台或跨 repo 時祖先判定會判錯。
- 現行 `commit` 是每個平台組在迴圈內重設的單一變數,迴圈外只剩最後一組的值;平台 A 的事件會帶 B 的 HEAD。
- `git rev-parse` 失敗時 `commit` 為空字串,spec 沒定義;`files` 相對平台 root,跨 repo 會對不上。
引句:「`commit`(跑的當下 HEAD)」
file: `scripts/lumos:13070` 與 `scripts/lumos:13076` `commit` 在每組重設。
file: `scripts/lumos:13192` 注釋自承多平台時記最後一組的 HEAD。

**6. 祖先判定遇到 rebase、壓提交、amend 會把有效背書整批判成「沒有背書」**
severity: major
blocking: 是——block 模式下會誤擋。
- 重現:feature 分支跑出 killed(commit=X),之後壓提交或 rebase,X 不再是祖先;內容沒變仍判沒有背書。可改用內容(配方檔與測試檔 blob 相同)判,spec 沒提。
- 缺口:7 碼短 sha;物件不存在時 rc 128 與「不是祖先」rc 1 沒區分;帳未提交時讀哪份沒定(見第 9 點)。
引句:「那筆的 `commit` 不是被推送版本的祖先 → 「沒有背書」(在別的分支跑的不算)」
file: `scripts/lumos:24198` 既有程式用 --is-ancestor,spec 未說明 rc 128。

**7. 新事件的 gate 欄位沒指定,而 `_gate_event` 會拒寫不在名單上的 gate**
severity: major
blocking: 是——照字面實作,事件根本寫不進去。
- `_gate_event` 對不在 `_KNOWN_GATES` 的 gate 不寫並回 False;名單有 `kill`,沒有 `guard-kill`、`contract-evidence`。
- 欄位要放進 `extra`;`_gate_event_build` 預設寫 `commit=head_sha[:7]`,會被 extra 覆蓋,spec 沒提。
引句:「為每條配方各寫一筆 `kind=guard-kill`」
file: `scripts/lumos:6943` `_KNOWN_GATES` 名單。
file: `scripts/lumos:1179` 與 `scripts/lumos:1234` `_gate_event` 與 `_gate_event_or_warn` 的簽名。

**8. tension 選 suggested 的 evidence 豁免,是繞過背書的現成路**
severity: minor
blocking: 否——spec 明文承認,是設計取捨。
- 併發題選 tension 並附任何測試名就繞過背書;RETIRE-IF 第①項沒量 tension 繞法。
引句:「包括 tension 選 suggested 時附的 evidence,v1 也不要求背書」

**9. 「治理帳」讀取位置與 CI 可見性沒有定義**
severity: major
blocking: 是——pre-push 與 CI 的判定可能不一致。
- 本機工作樹帳有 killed 但未提交 → 本機有背書、CI 沒有;讀 at_sha 樹則本機看不到剛跑完的事件。spec 沒選。
引句:「檢查只讀治理帳與 git,不載圖譜」
file: `scripts/lumos:36139` 既有讀帳是讀工作樹檔。

**10. warn 模式下的單題失敗處置,與既有 `_one` 例外處置衝突**
severity: minor
blocking: 否——spec 已指出分層,只是實作位置要注意。
- `_one` 單題例外一律擋;背書檢查若放在 satisfied 分支內,例外會被吞成擋,違反 warn。
引句:「單題驗不了(例如讀帳或 git 指令失敗),warn 模式印提醒」
file: `scripts/lumos:37395` 起每題例外統一轉成 problem 並擋下。

**11. 派工鏡頭快取鍵的落地方式不完整**
severity: minor
blocking: 否——可在實作時補齊。
- 背書狀態怎麼序列化進 extra 沒定;TTL 1200 秒;S11 沒有快取失效案例。
引句:「派工鏡頭的快取鍵(`_lens_cache_path`)要把背書狀態算進去」
file: `scripts/lumos:35782` 現行 extra=_disp_key。

**12. 沒有圖譜的專案段落,與 `_gate_event` 的行為沒有一一對上**
severity: minor
blocking: 否——語意方向是放行,不會誤擋。
- 關掉判定的條件沒寫;有 docs/ 但沒有治理帳檔的專案會持續提醒。
引句:「本案在沒有 docs/ 的專案比照合約測試那一關、不做背書判定,不加重那個死結。」

逐節:緣起與現況、教人怎麼寫測試、不做、回退、合約候選:已讀,無 finding。驗收條款缺多平台同名、多配方、rebase、killed 後 survived、測試檔改弱、帳未提交等案例。
實務隱患:併發無新增;效能——帳應一次讀入;資源無新增;相容同 spec。

最嚴重 severity:major;blocking 共 8 條(第 1、2、3、4、5、6、7、9 點)。
