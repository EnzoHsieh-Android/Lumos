severity: blocker

## F1 條件式回訪與轉正文字會被既有內容審判成不得存在
severity: blocker
blocking: 是 — 不改會讓新語法一面被要求保留、一面被推送閘要求刪除，形成無法正常提交的閉鎖。
引句:「**回頭條件的新寫法**:`REVISIT:[when:file src/x/runner.py] 補啟動環境不含金鑰的測試`」
file: `docs/lumos-toolchain-knowledge/Projects/筆記內容審_計劃.md:48`
file: `docs/lumos-toolchain-knowledge/Projects/筆記內容審_計劃.md:76`
file: `scripts/templates/note-audit-judge.md:11`

1. 筆記內容審保證每一行新增筆記都要判定，CODE 或 MIXED 行不消失就推不上去。
2. `[when:file ...]`、`[when:test ...]`、`[when:status ...]` 都直接陳述 repo 當前是否有檔案、測試或狀態；依現行判定詞，它們至少是 MIXED。
3. 本 spec 又要求這些條件留在原行供 drift 評估；刪掉就失去防線。`guard settle` 新寫的 `TEST:由 [test:...] 守` 同樣是可由程式與測試確認的 CODE 敘述。
4. spec 沒有讓 note-audit 排除探針結構，也沒改判定詞或改用不受內容審管轄的結構欄位，兩道硬閘組合後無合法通路。

## F2 第二道防線的考試缺少聲稱已存在的改寫輸入
severity: major
blocking: 是 — 不補齊就無法重現乙的分數，實作者只能自行發明考卷內容與重放方式。
引句:「考法是在考場複本的 067f005 上照稽核把 A7、B1、B2、B4 的回頭條件改寫成條件式」
file: `governance/eval/drift-exam/README.md:1`
file: `governance/eval/drift-exam/rtb-2026-09-28.json:176`

1. `governance/eval/drift-exam/` 實際只有 README 與原始 33 題 JSON；沒有 spec 所稱「存考卷旁」的條件式改寫檔，也沒有檔名、格式或套用座標。
2. `drift scan --at 067f005` 依設計讀提交樹；直接改考場複本工作目錄後再跑 `--at 067f005`，改寫不會被讀到。spec 沒定義暫存提交、暫存 ref 或內容注入方式。
3. B3 在考卷明列為 mechanism 2 的 drift，但乙的改寫清單漏掉 B3；它可明確改成 Phase 12 計劃狀態探針。
4. 因此 S14、S16 要求的逐防線分數沒有封閉、可重放的輸入。

## F3 新增的收尾值與豁免欄位都沒有接入既有 schema
severity: major
blocking: 是 — 照 spec 操作會寫出 lint 不接受的計劃狀態，且 c2 的正式豁免無法經合法指令建立。
引句:「當 lumos set 把計劃改成 done、superseded 或 abandoned」
file: `scripts/lumos:4949`
file: `scripts/lumos:4759`
file: `scripts/lumos:13840`
file: `scripts/lumos:14314`

1. 現行 project status 只允許 `todo/doing/done/superseded`；`abandoned` 只屬於 verification。
2. `lumos set` 會寫入任意 status 字串，之後 lint/doctor 才把 project 的 `abandoned` 判成錯誤；S5 因而會把正常收尾指令變成壞圖譜。
3. c2 所需的 `keep_open_reason` 不在已知 frontmatter 欄位、`SCALAR_KEYS`、`LIST_KEYS` 或條件欄位；`lumos set` 明確拒絕它。
4. c2/c3 的「已收尾」又只列 done/superseded，與 S5 宣稱的 abandoned 路徑內部不一致。

## F4 c2 把弱關聯誤當成計劃擁有 Issue
severity: major
blocking: 是 — 正常保留的跨題連結會擋計劃收尾，實作者無法從連結本身判定 Issue 是否應隨計劃結案。
引句:「Issue status 是 open/doing,跟一份 status 是 done/superseded 的計劃互相連結」
file: `scripts/lumos:15027`
file: `docs/lumos-toolchain-knowledge/Projects/skill寫法學借鑒與design-loop剪枝.md:3`
file: `docs/lumos-toolchain-knowledge/Projects/skill寫法學借鑒與design-loop剪枝.md:66`
file: `docs/lumos-toolchain-knowledge/Issues/散文紀律沒有退場機制.md:3`

1. 現行關係層刻意把 `related` 視為弱邊，不納入連鎖展開。
2. repo 已有完成計劃在正文連到仍應保持 open 的 Issue：完成的是一次 skill 剪枝，Issue 管的是全 repo 尚未裁定的退場機制。
3. c2 的「任一方向 wikilink 或 related」會把這類脈絡、來源、後續研究連結全部當成必須同步結案的所有權。
4. `keep_open_reason` 又沒有合法寫入口，誤擋時沒有 spec 所宣稱的正常出口。

## F5 c4 會把釘在乾淨工作樹上的可重現驗證判成漂移
severity: major
blocking: 是 — 新增同形驗證紀錄時會被硬擋，且這正是 repo 已採用的可重現基線寫法。
引句:「而這篇筆記本身已在被檢查的提交樹裡。」
file: `docs/lumos-toolchain-knowledge/Verification/2026-09-15_多詞題庫重標與新基線.md:5`
file: `docs/lumos-toolchain-knowledge/Verification/2026-09-16_多詞題庫補到二十題與新基線.md:5`

1. c4 只要 `valid_under` 含「工作樹」且筆記已進提交樹就成立，沒有判斷句子是在說「未提交工作」還是「釘在某提交的乾淨工作樹」。
2. 現有兩份 pass 驗證都使用「提交 X 的乾淨工作樹」描述可重現條件；它們提交後仍完全有效。
3. 同形新驗證會在此次推送被 c4 擋下，迫使作者刪掉必要前提或表態放行假陽性。

## F6 撤除節的 substring 判法重做了既有決策已否決的漏洞
severity: major
blocking: 是 — 否定句或仍有效的快照說明會讓整節真漂移被靜默排除。
引句:「小標題底下第一個非空行是引用區塊」
file: `docs/lumos-toolchain-knowledge/Projects/code側刪除傳播守衛_計劃.md:25`
file: `docs/lumos-toolchain-knowledge/Projects/code側刪除傳播守衛_計劃.md:132`

1. 既有 delguard 設計明文否決用字樣判歷史節，原因是 substring 會把「尚未作廢」誤當「已作廢」。
2. 本 spec 又以「已撤／撤除／快照」等任一子字串判整節退休。
3. `> 本節尚未撤除，以下仍是現況` 或 `> 這份快照格式仍是現行合約` 都符合退休條件。
4. 一旦誤判，該節所有 c1–c4、when、符號與測試漂移都不擋，屬整節 fail-open。

## F7 上線門檻只量數量，不量正確率或最低抓取率
severity: major
blocking: 是 — 考試即使抓不到真漂移或擋到非漂移，仍能依現行門檻啟用 block。
引句:「接線:drift check 接進工具鏈自己的推送前掛鉤與 CI(排在 code-loop check 之前),照考試結果決定預設 block 還是先 warn」
file: `governance/eval/drift-exam/README.md:7`

1. spec 記錄 13 題非漂移的誤報數，也記錄真題的擋到／點到數，卻沒有任何可接受的誤報上限或最低 recall。
2. 唯一模式門檻是考題提交平均「要處理」筆數是否超過 20。
3. 每個提交擋 1 個非漂移、真漂移抓 0 個時，平均仍低於 20，結果會選 block。
4. 第 0 節又先宣稱 block 為預設，與第 6 節聲稱考後決定預設互相衝突。

## F8 非 Python 路徑在未量誤報前硬擋，實質翻掉 delguard d0
severity: major
blocking: 是 — 消費專案會被一套已承認更粗、未經考試的字面判法硬擋。
引句:「其他語言:從 delguard 只讀改動行的抽法延伸——刪除行裡的識別字,再讀終點那支檔全文確認整檔都不再出現」
file: `docs/lumos-toolchain-knowledge/Projects/code側刪除傳播守衛_計劃.md:29`
file: `docs/lumos-toolchain-knowledge/Projects/code側刪除傳播守衛_計劃.md:33`
file: `docs/lumos-toolchain-knowledge/Projects/code側刪除傳播守衛_計劃.md:35`

1. d0 裁定字面識別字比對先 advisory，等有誤報數再談硬擋。
2. 本 spec 對非 Python 仍借 delguard 的識別字抽法，只多了長度、大小寫和終點全文存在性；它自己承認誤報高於 Python且考卷只考 Python。
3. 把同一未校準信號搬到另一個 gate 名稱，不會消除 d0 所禁止的硬擋風險。
4. 預設 block 上線會直接改變 pos-ios、taroko_app 等消費專案行為，與「不翻 d0」的宣稱相反。

## F9 刪除或改名後以終點樹找家，會把最該擋的命中降成只列
severity: major
blocking: 是 — 正確更新 about_code 的改名提交反而會讓舊路徑漂移逃過硬閘。
引句:「落在被改程式檔的家(`about_code` 列了它)的筆記裡」
file: `scripts/lumos:22675`
file: `scripts/lumos:22691`

1. spec 同時規定搜尋讀終點樹，家由終點筆記的 `about_code` 判定。
2. 正常改名提交會把程式 `old.py` 改成 `new.py`，並把家筆記的 `about_code` 同步改成 `new.py`。
3. 若同篇正文仍殘留 `old.py`，終點家對照表已沒有 `old.py`；該命中不再符合「被改程式檔的家」。
4. 它因此被降成只列而不擋。設計必須保留起點家對照或明定 rename 的舊、新家映射，目前兩者都沒有。

## F10 測試探針借用的索引不支援提交快照
severity: major
blocking: 是 — 歷史 scan、考試及推送未 checkout 的 ref 會用錯版本的測試集合。
引句:「測試索引裡有這支測試(借 `_platform_test_index`)」
file: `scripts/lumos:11194`
file: `scripts/lumos:11203`
file: `scripts/lumos:11208`
file: `scripts/lumos:4163`
file: `scripts/lumos:4248`

1. `_platform_test_index` 從目前檔案系統讀 `.lumos/config.json`、平台 root 與測試檔，不接受 git ref 或 blob reader。
2. `drift scan --at <提交>` 與 `drift check` 卻承諾依指定提交／推送頂端的樹判定。
3. 在目前 checkout 跑 `scan --at 067f005`，借用現行 helper 會索引 checkout 的測試，不是 067f005 的測試。
4. 現有測試引用還有多平台前綴與 default platform 規則；spec 的 `[when:test <測試名>]` 沒定義是否沿用，跨平台同名測試的判法也未落字。

## F11 Python 符號只寫名稱，無法同時正確處理同名與搬移
severity: major
blocking: 是 — 任一可行實作都會在常見 refactor 上漏擋或誤擋。
引句:「比對頂層與類別內的 def/class 名、模組層大寫常數」
file: `scripts/lumos:29399`
file: `scripts/lumos:29407`

1. 借用的 `_lens_py_defs` 回傳裸名稱、起訖行，不含檔案或類別限定名。
2. 若全 repo 以裸名稱做集合，刪除 `A.run` 而 `B.run` 仍在會被判成名稱未消失。
3. 若改成 `(路徑, 名稱)`，把未改名的函式搬到另一檔會被判成舊符號消失，家筆記或摘要命中後硬擋。
4. `[when:symbol <路徑>::<名稱>]` 也沒有類別限定語法；S10 未涵蓋同名方法、跨檔搬移或模組搬移。

## F12 doctor Z 把高成本歷史掃描與已知高雜訊範圍放進每次推送
severity: major
blocking: 是 — 接線後本機 pre-push 與 CI 都會支付未設上限的歷史掃描，並重報刻意保留的歷史記錄。
引句:「當執行 doctor,工具應開一段 Z 印 scan 的筆數與前幾筆」
file: `scripts/lumos:2647`
file: `scripts/lumos:2648`
file: `scripts/lumos:2650`
file: `scripts/hooks/pre-push:179`
file: `.github/workflows/ci.yml:96`

1. 現有 doctor Y 經實測只掃 Systems；註解明載 Projects 是未來名稱、Verification/Issues 是歷史，掃它們會產生假陽性。
2. 新 scan 改成任何筆記，且「曾在歷史定義過」不會排除 Verification：驗證紀錄提到已移除函式，正好同時滿足曾定義與現在不存在。
3. 每個候選再跑 `git log -G`，上限 500；spec 只替 check 設 60 秒，沒有替 scan 或 doctor Z 設 deadline。
4. pre-push 與 CI 都固定執行 doctor；這不是偶爾手動跑的掃描，而是每次推送的熱路徑。

## F13 截斷與超時沒有定義硬閘的回傳語意
severity: major
blocking: 是 — 實作者必須自行決定部分未檢查時放行還是擋下，兩種選擇都會改變安全契約。
引句:「超過就印截斷並記 `degraded` 帳,不靜默放行也不無限跑」
file: `scripts/lumos:25599`
file: `scripts/lumos:25616`
file: `scripts/lumos:25671`

1. 第 0 節列出的 drift 事件種類沒有 `degraded`，實務隱患卻要求寫 `degraded`。
2. S1 只定義有發現時 block/warn/off 的 rc，沒有定義 300 名稱上限或 60 秒後尚有未檢查項目的 rc。
3. 既有 advisory delguard 對 degraded 明定 rc0 且標示掃描不完整；硬閘不能不加判準直接照搬。
4. fail-open 會漏過未掃部分，fail-closed 會讓大型正常推送必然被上限擋住；「印出來」不等於定義門禁結果。

## F14 回退只拔接線會讓條件式 REVISIT 永久失去讀者
severity: major
blocking: 是 — 照回退章執行後，既有條件式風險承諾會被所有健檢靜默跳過。
引句:「推送閘接線是掛鉤與 CI 各一行,拿掉那一行即退回。」
file: `scripts/lumos:1944`
file: `scripts/lumos:1965`
file: `scripts/lumos:1967`

1. 本 spec 不只新增 gate；它還修改 note-shape 接受 `[when:]`，並讓 doctor E5 遇到 `[when:]` 跳過日期解析。
2. 若依回退章只移除 hook/CI 的 `drift check`，已提交的條件式 REVISIT 仍被 E5 跳過。
3. drift scan/check 已撤、E5 不讀，該條回訪條件此後沒有任何消費者。
4. 回退章必須涵蓋條件資料遷移或保留評估器；現行「拿掉一行即退回」是不成立的行為宣稱。

## F15 guard settle 的跨檔改寫沒有失敗一致性
severity: major
blocking: 是 — 任一中途寫入失敗都會留下合約、狀態與歷史文字互相矛盾，且新增的 c1 抓不到 pending 半成品。
引句:「寫後自驗照既有 `atomic_write_verify`。」
file: `scripts/lumos:11792`
file: `scripts/lumos:11821`
file: `scripts/lumos:11827`

1. 現行 settle 先原子改功能節點的合約行，再另一次 `cmd_set` 改守衛節點 status；兩檔之間沒有交易或回滾。
2. 本 spec 還要在守衛節點改 TEST、WHY 與正文，至少形成三組邏輯更新。
3. 功能節點成功、守衛文字或 status 失敗時，正式合約已生效但守衛仍 pending；反向排序則會留下「已轉正」文字但正式合約未寫入。
4. c1 只檢查 status=pass，因此 pending 半成品不會被新一致性檢查抓到。單檔 `atomic_write_verify` 無法保證這個跨檔狀態。

## 逐節核對

1. frontmatter、`lands_in`、`related`：已讀。既有引用目標均存在；`Systems/存量漂移守衛` 是本計劃宣告的新落點，無額外 finding。
2. 前言、PRIOR-ART、RETIRE-IF：已讀；決策衝突見 F6、F8，其餘無 finding。
3. 範圍：已讀，無 finding。
4. 做法 0：已讀；撤除判法與降級契約見 F6、F13，其餘無 finding。
5. 甲：已讀；schema、c2、c4 與 settle 一致性見 F3、F4、F5、F15。
6. 乙：已讀；跨閘閉鎖、考試輸入與快照索引見 F1、F2、F10。
7. 丙：已讀；非 Python、家映射與符號身分見 F8、F9、F11。
8. 健檢：已讀；doctor Y 範圍與效能退化見 F12。S13 排除計劃條款，因此既有 doctor S5 不會被重複列，這部分無 finding。
9. 考卷與考法：已讀；可重放性與上線門檻見 F2、F7。
10. 掃全圖譜與修復：已讀；接線前後的效能與模式判準見 F7、F12、F13。
11. 條款 S1–S18：逐條已讀；測試名均為新條款目標，內部節號存在。未封閉的行為已分別列於 F1–F15。
12. 回退：已讀；條件式回訪失去讀者見 F14。
13. 實務隱患：已讀。守衛正確性、誤擋、效能、跨語言、消費專案、寫入一致性分別見 F1、F4–F13、F15；jsonl 併發衝突已有明文處置，無額外 finding；金流、對外送出與不可逆三類排除理由成立。
14. 誠實界線：已讀；已承認的語意盲區不構成新增 finding，但不能抵銷 F8、F11 的硬擋錯判。
15. 考試結果、修復結果：已讀；目前為待填占位，無額外 finding。
16. 既有機制影響：delguard d0 被 F8 實質翻案；筆記內容審與筆記形狀擋組合被 F1 破壞；doctor E5 回退被 F14 破壞；doctor Y 的既有降噪邊界被 F12 破壞；doctor S5 保持原行為。

最高 blocker，blocking 共 15 條。