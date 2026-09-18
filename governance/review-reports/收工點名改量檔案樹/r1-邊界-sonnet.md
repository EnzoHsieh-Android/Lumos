severity: blocker

# 邊界與極端輸入審查:收工點名改量檔案樹_計劃

審查範圍:docs/lumos-toolchain-knowledge/Projects/收工點名改量檔案樹_計劃.md(=被審材料 r1-work.md,兩檔逐位元組相同,已用 diff 核對)。對照程式碼:scripts/hooks/claude/check-graph-sync.py(現況仍是工具名列舉,尚未動手實作,S1–S6 對應的 t_sync_nudge_* 測試在 scripts/test_lumos.py 裡不存在)、scripts/hooks/claude/impact-hook.py。

## 這是怎麼被發現的 / 實測證據 / 根因

已讀,無 finding。三節都是描述現況症狀與診斷過程,不是新機制的邊界,已用 baseline-before-fix.txt(9 情境 7 個 FAIL)核對,數字與說法一致。

## 方案 —— 併發讀寫

severity: major
blocking: 是 — 本檔自己的機制證明「同一 session 兩個 Stop 同時到」是這個環境的真實情境,快照的讀取-取差集-覆寫若不是原子操作,兩個併發呼叫可能各自算出片面差集或互相覆蓋對方剛寫入的基準,讓 S1 要修的少報以另一種形狀復發。
引句:「當基準存在,清單不應含上一輪已經算過的改動(每輪重取基準,不是整個會談取一次)」
file: `/Users/enzo/.claude/jobs/9d19b273/tmp/stopfix/scripts/hooks/claude/check-graph-sync.py:719-731` — `stop_block_decision`/`_stop_mark_write` 專門用 `O_EXCL` 佔名額處理「兩個 hook 同時來只有一個成功」,快照的讀寫沒有對應的併發保護,S1–S6 全文也沒提到這個情境。

## 方案 —— 快照寫入中斷

severity: blocker
blocking: 是 — S3 只保護「取不到基準」(檔案不存在)這一種退化,寫到一半被砍會留下一份存在但截斷/損毀的檔案,不會落入「取不到基準」的判斷,下一輪若原樣讀入可能拋例外或算出錯誤差集,而不是安全地印出降級警語。
file: `/Users/enzo/.claude/jobs/9d19b273/tmp/stopfix/scripts/lumos:12508` 、`:14351`、`:23107`、`:25519` — 本 repo 對「跨輪次讀取的共用狀態檔」慣例是 tmp 寫入後 `os.replace` 原子取代,「實作時已知的坑」五條完全沒提快照寫入中斷這件事,也沒有指定用同一套寫法。

## 方案 —— 快照過期但仍「讀得到」

severity: major
blocking: 是 — 續接舊會談重用同一個 session_id 時,一週前留下的舊快照檔案存在、內容完整,不會觸發 S3 定義的「取不到基準」降級路徑,會被當成合法的「上一輪」基準直接取差集,安靜印出一個把一整週漂移全算成這一輪的精確數字。
引句:「不要安靜地報一個看起來精確的數字,少報最毒的地方就是看起來像正常運作」
file: `/Users/enzo/.claude/jobs/9d19b273/tmp/stopfix/docs/lumos-toolchain-knowledge/Projects/收工點名改量檔案樹_計劃.md:123` — S3 的判準只寫「當取不到上一輪的基準」,沒有「基準存在但過舊」這個分支。

## 方案 —— 檔名含換行

severity: major
blocking: 是 — 若快照用文字檔「一行一筆路徑+雜湊」的格式(方案未指定格式,但這是最自然的零依賴寫法),檔名內嵌的換行會把一筆記錄拆成兩行,下一輪解析取差集時整批路徑-雜湊對應錯位,可能讓正常改動也被誤判成「沒變」或「多了一個不存在的檔」。
file: `/Users/enzo/.claude/jobs/9d19b273/tmp/stopfix/scripts/hooks/claude/check-graph-sync.py:758-761` — `_safe_path` 專門把 `\r\n` 濾掉,註解寫明「檔名來自工作樹,不信任」,顯示這支 hook 本來就知道檔名資料不乾淨,但快照格式的條款沒有對應防護(如 `git status --porcelain -z` 的 NUL 分隔模式)。

## 方案 —— 符號連結 / FIFO / 權限不足檔

severity: major
blocking: 是 — 內容雜湊需要開檔讀取,工作樹上的符號連結(含指向不存在目標的斷鏈)、FIFO、socket、或當下無讀取權限的檔都可能讓開檔動作拋例外或卡住;S1–S6 沒有任何一條講到這類特殊檔案形狀的處理方式。
file: `/Users/enzo/.claude/jobs/9d19b273/tmp/stopfix/scripts/hooks/claude/check-graph-sync.py:245-256` — 同一支 hook 的 `_shebang_script` 已經為了同一顆工作樹特地用 `p.is_file()` 排除「目錄 / FIFO / socket / 不存在」,註解寫「開 FIFO 會卡死」,證明這類檔案在這個環境是已知會出現的形狀,新的雜湊步驟卻沒有沿用同一套防護。

## 方案 —— 大型工作樹與既有逾時預算的衝突

severity: major
blocking: 是 — 本檔已有明確的逾時分帳機制,外層天花板預設 10 秒;「量檔案樹」是這次新增、要掃描並雜湊整棵工作樹(含未追蹤檔)的步驟,在檔案數量大或有大型未追蹤檔的專案上可能單獨吃光整個天花板,而方案全文沒有把這個新步驟算進逾時預算,超時等同悄悄退回目前要修的少報行為。
file: `/Users/enzo/.claude/jobs/9d19b273/tmp/stopfix/scripts/hooks/claude/check-graph-sync.py:538-586` — `_outer_budget`/`_inner_budget` 與其註解「異常大的值會讓內層跟著失控放大,等於整個 fail-open 形同虛設」;PRIOR-ART 引用的「4074 檔 30ms」量的是 `git status --porcelain` 的路徑列舉,不是內容雜湊,兩者成本不是同一件事。

## 方案 —— 暫存目錄撞名

severity: major
blocking: 是 — 「已知的坑」第三條只規定基準檔不能放進 repo 工作樹,沒有規定要用 session_id 之類鍵值命名;若兩個會談共用的暫存目錄下快照檔名不是以 session 區分,後寫的會直接蓋掉先寫的基準,讓另一個會談的下一輪把不屬於自己的差集算成這一輪。
引句:「基準檔不能放在 repo 的工作樹裡。」
file: `/Users/enzo/.claude/jobs/9d19b273/tmp/stopfix/scripts/hooks/claude/check-graph-sync.py:732-737` — `_stop_mark_path` 用消毒過的 `session_id` 當檔名;`/Users/enzo/.claude/jobs/9d19b273/tmp/stopfix/scripts/hooks/claude/impact-hook.py:169-172` 的 `_ttl_marker_path` 用 `lumos-impact-<session_id>` 當目錄名——本 repo 同類「會談自己的暫存位置」都明寫用 session_id 隔離,這份計劃沒有把這點寫成條款或測試。

## PRIOR-ART / RETIRE-IF

已讀,無 finding。兩節都是既有做法佐證與撤除條件,沒有新的邊界輸入需要處理。

## 驗收條件

severity: minor
blocking: 否 — 驗收條件 2 的精神是「餵一個沒列舉過的手法」比補完列舉表更能證明修對,但列出的例子(`tee`、`patch`、一行 python)全部是「新工具寫入」這一種未知,沒有對稱地餵一個刪除、二進位、或超大檔的情境;這不影響機制本身能不能運作,只是驗收涵蓋面可以更廣。
引句:「這比補完列舉表更能證明修對了」

零改動 / 只改一支 / 一輪兩百支(例如跑格式化工具)三種量級:已讀,無 finding。既有的顯示上限邏輯(前 10 筆列名、其餘「另 N 個」、整段訊息 1500 字截斷)已經處理大清單,不是這次量檔案樹新增的風險。

## 實作時已知的坑

severity: minor
blocking: 否 — 五條坑都指名了來源,但被刪除的檔案怎麼進入「這一輪改了哪些檔」清單沒有被列為第六條坑:量檔案樹天生量得到刪除(git status 會列出 D 狀態),但對「刪除算不算改了程式碼檔、要不要雜湊」沒有明講,不影響機制能否運作,只是容易在實作時漏想。

## 條款 S1–S6

severity: minor
blocking: 否 — S1 條款文字列舉的是「重導向、原地取代、heredoc、管線寫入」等寫入手法,沒有明講刪除是否算「改了程式碼檔」;S2–S6 各自對應的邊界(混用工具、無基準、跨輪基準、快照位置、同大小同時間)在條款文字裡都有對應句子,判準清楚,不再重複列。
引句:「收工點名的清單應含每一支被改的檔,不得少報」

## 實務隱患 / 回退

已讀,無新增 finding。「實務隱患」已誠實把守衛面標成不能排除、照走設計審,符合這輪審查的前提;「回退」段的風險與「暫存目錄撞名」那條重複——若快照目錄不是以 session 區分,回退時「刪掉基準快照目錄」可能連帶清掉其他還在跑的會談的基準,見上方 F7,不另立一條。

---

總結:整份最高等級 blocker(1 條:快照寫入中斷沒有原子寫入防護,壞快照會被誤當成有效基準讀入);blocking:是 共 7 條(併發讀寫、寫入中斷、快照過期未降級、檔名含換行、符號連結/FIFO/權限、逾時預算衝突、暫存目錄撞名),blocking:否 共 3 條(刪除語意未明講、驗收條件涵蓋面、已知的坑漏第六條)。
