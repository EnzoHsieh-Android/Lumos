severity: minor

LUMOS-SPEC: docs/lumos-toolchain-knowledge/Projects/審查有沒有用記帳_計劃.md

立場:簡單的守護者、複雜的敵人。上限輪:只有 blocking 級才算。方法:通讀 r3-snapshot.md 全文對照 r2-intake.md b1–b13 折入紀錄;★依指示以 `git show HEAD:scripts/lumos` 為準★核對 `_report_severities`(4815 行)、`_severity_check_row`(4828 行)、`cmd_canary`(4924 行)現況——HEAD 版本裡 `--reported`/`--refuted-set`/`--self-found-set`/`_report_reported_count` 均 0 命中,確認純屬設計審;工作樹(`git status`)另有 381 行未提交改動,懷疑是同工作區並行在動這支腳本,刻意不採工作樹當證據以免審一個會動的目標。對照 r2-snapshot.md 舊版 S1/S2 文字,逐條回答 (a)–(d)。

## (a) 拒收偵測正則:算不算第二份 severity 解析;不寫會漏什麼

severity: minor / blocking: 否
判準:這支正則不產生 severity 值、只做「認得的殘留寫法→擋」的比對,功能上是黑名單而非第二套計數邏輯,沒有違反「`_report_severities` 是唯一解析」這句話的字面;但兩個正則都繫在同一個語意(severity 怎麼標)上、要一起維護,是真實的耦合成本,值得留一句註解互相指路(架構席那邊的關切成立但不到擋)。不寫這支正則,靠「檔首檔級行 + 每條 finding 一行 severity」的 SOP 硬性要求也守不住——為什麼段自己舉的證據是今天另一批 8 份報告全用 `## F1 — BLOCKER` 這種標題內嵌格式,`_report_severities` 機器數到 0,這正是 ③ 要擋的三種殘留寫法之一;沒有偵測正則,這些報告會被 `_report_severities` 悄悄漏數成 `reported` 偏低(不是 rc2),而 `--findings ≤ reported` 這條不等式只擋「填的數字比機器數的高」,填一個同樣偏低的 `--findings` 照樣過關——這就是把 r2 剛證明過的「下限守衛單向可鑽」原樣請回來,只是換了個入口。

引句:「它是專案唯一的 severity 解析,不另寫寬鬆版」
引句:「掃到就 rc2,訊息列出行號」
file: `scripts/lumos:4815`(HEAD,`_report_severities`)
file: `scripts/lumos:4850`(HEAD,noparse 訊息)

## (b) `reported` 機器數:跟既有 `--findings` 差別是不是只剩 minor/clean;值不值一個新鍵

severity: clean / blocking: 否
判準:差別不是過濾條件,是「誰在什麼時候填的」——`--findings` 沿用既有語意,是編排者事後(辯方裁決/折疊之後)手填的存活數,`reported` 是 `canary record --report` 當下從報告檔文字機器算出、無旗標可覆蓋的數字,兩者分屬管線的不同階段(原始申報 vs 事後人工結論)。這正是整個 r1→r2→r3 改版鏈唯一在追的東西:r2 版本的 `--reported` 本身也是人填的(只是多一道解析下限守衛),照樣被證明單向可鑽;r3 把它換成機器數、鎖死不可覆蓋,才第一次讓 `--findings ≤ reported` 這條不等式有一個人填不動的錨——拿掉 `reported` 這個新鍵,不等式就沒有另一端,等於直接退回 r2 已經被打穿的設計。

引句:「reported` = 檔級之後的獨立宣告行數(含 minor、排除 clean)」
引句:「既有語意與 `--light`/`--gate` 對它的 fail-closed 依賴一律不動」
file: `scripts/lumos:4924`(HEAD,`cmd_canary`)

## (c) 整字 + 重現表列驗:intake 是編排者自己寫的,驗它等於自己驗自己——價值是什麼、不做會怎樣

severity: clean / blocking: 否
判準:spec 自己在段首就承認這步不驗對錯(「不證明重現做對了」),它驗的是「這個駁回 id 有沒有一列可稽核的機械重現紀錄可指」,把「任意字串都能駁回」降級成「必須先在 intake 造出一列對得上的紀錄才能駁回」——這是我自己在 r2 (c) 拿本案的 `r1-intake.md` 實測出 `a1` 因為是 `a10`…`a16` 的字首而被子字串命中 10 次、判 blocker 折入的洞,r3 用「整字 + 對 HIT/MISS 那一列」把它補起來,是對照已證偽漏洞的最小修補,沒有多做。不做這一步,`--refuted-set` 的 id/理由會回到 CLI 打任意字串就過的狀態,直接重演 r1 被折掉的「駁回清單可灌大」——這一步不是自己驗自己的空轉,是把「編排者說了算」的範圍從「打字」收窄到「留痕」,真正的正確性驗證本來就外包給逃逸帳,spec 段首已經講明這個天花板,沒有超額宣稱。

引句:「★對 intake 驗,整字不是子字串★」
引句:「不證明重現做對了——跟逃逸帳同一個天花板,段首寫明」
file: `governance/review-reports/審查有沒有用記帳/r2-intake.md:23`

## (d) 讀側 S 推導、兩個 REVISIT 數、K 與 30 天門檻——拿掉哪個不影響「開始記」

severity: minor / blocking: 否
判準:三者都是純讀側/事後推導,不對 `canary record` 增加任何一絲填寫負擔,拿掉任何一個都不會讓「開始記」這件事變得更容易做到,只會少一項事後可觀測的訊號——S 推導是 r2 b4(Codex)砍掉 `--self-found-set` 選填欄位後唯一還能抓到「存活多於席位報」這件事的機關,不印它等於把那個訊號整個關掉;段首兩句免責語是掛在 S 推導同一行,拿掉的話「N 是機器、R 是人填」這個可信度分層會被讀者當一組數字混算,正是本案「兩本帳」教訓要防的事。兩個 REVISIT 數(refuted-set 非 none 比例、S>0 輪數)與 K/30 天門檻若真要更小,可以砍的候選是後者——它是 spec 自己標的「暫用值」,而且是印給人看的一句提醒文字、不是資料欄位,砍了也不損「開始記」;但兩個 REVISIT 數對應兩條寫死日期的回頭條件(2026-10-08、2026-11-08),砍了它們等於讓那兩條 REVISIT 變成「回頭看什麼都沒有算好、得現場現寫查詢」,不划算——三者都便宜到不值得為了「更小」而拆,判定維持原案。

引句:「編排者自找的發現在讀側由算式推出:S = max(0, M+R−N)」
引句:「另印兩個給回頭條件用的數字」
引句:「門檻是暫用值,REVISIT 時看」

## S4(design-loop skill 補逃逸段、範本加三旗標、SOP 補三條)

已讀,無 finding。範圍限定在 skill 散文與收貨 SOP,不動 `ci-wait`,理由(12 紅 0 逃逸)在 r1 已被本席自己重現過,沒有新內容值得挑。

引句:「design-loop skill 步驟 10 之後補一段獨立散文」

## S5(範圍刀:不新帳本、不回填、不做模型)

已讀,無 finding。全部加在既有 `canary`/`gov --stats` 上,跟 (b)(d) 的新鍵/新段落是同一批既有結構的延伸,沒有另開檔案或另起掃描回合。

引句:「不新開帳本(全部加在既有 canary 列與 gov --stats 上)」

## 總結

severity: minor(全份最高,(a)/(d) 各一條 minor,無 blocking),四題(a)–(d)全部不擋:(a) 拒收偵測正則是黑名單而非第二解析,砍了會讓今天已在用的殘留格式重新變成單向可鑽的漏洞;(b) `reported` 是 `--findings` 不等式唯一填得動的錨,不是同義重複;(c) 整字+重現表列驗是對本席自己 r2 揪出的真實漏洞做最小修補,沒有自我拉抬效力;(d) 讀側三項都零填寫成本,K/30 天門檻是唯一可以再砍的贅字但不值得為此擋。三輪下來 S1/S2/S3 已經被拆到「拒收+機器數」這個不可再退的底線,本輪沒有新的贅肉可摳,建議直接放行進實作。
