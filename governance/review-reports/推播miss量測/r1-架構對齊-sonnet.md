severity: major

# 架構對齊審查——推播miss量測_計劃 r1

## 問一:分層與依賴方向

新東西的位置對:PRIOR-ART 明寫「擴充既有唯讀腳本 recount.py」,S1/S2/S3 都是在 `governance/eval/lens-utilization/recount.py` 既有的 `scan_file`/`classify_bash` 邏輯上加解析與分類,沒有另開一支平行腳本,這跟 `refresh_labels.py`、`retrieval_eval.py` 兩支同目錄腳本「各自一支、職責不疊」的擺法一致。

S2 判「規則內」miss 時明寫「直接問 impact,不在儀器裡另寫一套比對」,呼叫 `lumos impact --file F --json`——這跟 `refresh_labels.py`/`retrieval_eval.py` 一律 subprocess 呼叫 `scripts/lumos`(不 import lumos 模組、不重寫圖譜比對邏輯)的既有依賴方向一致(`governance/eval/retrieval_eval.py:23` 的 `subprocess.run([sys.executable, str(LUMOS), ...])`);`lumos impact --file --json` 真的回 `{"direct":[...], "indirect":[...]}`(`scripts/lumos:20626`),about_code「只做排序不建連結」的說法也跟 `scripts/lumos:1456` 的既有規則一致,沒有自造第二套判準。

誰呼叫它:S4 寫「在每日治理那支排程的週期觀測段加一步」,對照 `governance/daily-governance.sh:243-249` 第 2 步呼叫 `autonomous-loop.sh`,而「週期觀測」五段(檢索考卷/情境探針/空轉提醒/回放週跑/backlog)實際定義在 `governance/autonomous-loop.sh:305-467`——呼叫層級對得上既有慣例,沒有跨層直呼的問題。唯一沒交代的是:這一步的膠水邏輯要不要跟 `run_replay`/`run_nags` 一樣包成 `run_xxx` 函式、呼叫一支印 `LOG:`/`MSG:` 行的 python 模組(`governance/autonomous_loop/replay_weekly.py` 那個既有慣例),S4 沒提,留給實作猜——這點併入問三 D1 一起講。

## 問二:命名與錯誤處理

週字串格式 `<年>-W<週>` 跟既有 `date +%G-W%V`(`governance/autonomous-loop.sh:405,423`)算法一致,原子寫入(暫存→自驗讀回→整檔換名)也明寫對齊「本 repo 改共用檔的原子寫入慣例」,跟 `refresh_labels.py` 的 `_atomic_write_json`(`governance/eval/refresh_labels.py:42-49`)、`daily-governance.sh` 的 `write_health`(`governance/daily-governance.sh:208-222`)同一套,這兩點是對的、不算發現。

但輸出檔位置與失敗語意跟鄰居不一樣,列 D2、D3。

## 問三:第二種做法

主要問題是 S4 的「本週跑過沒」判斷機制:本 repo 在 `autonomous-loop.sh` 裡已經有三個現成的「每週跑一次」實作(情境探針、空轉提醒 `run_nags`、回放週跑 `run_replay`),三個都是同一套慣例——獨立的戳記檔(跟真正輸出檔分開存放)、在跑正事之前先比對戳記、而且戳記只在拿到有效輸出後才蓋章。S4 沒有提到沿用這套戳記檔慣例,驗收案例的寫法(「本週沒檔→寫一份」)暗示改用「輸出檔存不存在」當作跑不跑的判準,這是本 repo 目前沒有的第二種週跑閘門機制,列 D1。

S2 收尾把「判不出」miss 標完後「進 edit 卷……走它既有的流水線」,但 `refresh_labels.py` 的 `delta/apply` 既有流水線只處理「既有案例(`id`/`file`/`commit`/`delta`/`split`)缺的標籤」,不處理「新增一筆案例」——`retrieval-goldset.json` 的 `edit` 陣列每筆案例都釘著一個具體 commit 的 diff 片段,不是逐字稿衍生的(檔案,節點)配對;miss 候選要怎麼變成這種形狀的新案例,S2 沒交代,列 D4(判不準)。

---

D1
severity: major
blocking: 是
引句:「本週沒檔 → 寫一份;同週再跑 → 覆寫同一份、不多出檔」
file: `governance/autonomous-loop.sh:405;423-424`
本 repo 三個既有週跑(情境探針/`run_nags`/`run_replay`)一律用獨立戳記檔判「本週跑過沒」,戳記與輸出檔分開、且只在輸出驗證有效後才蓋章;S4 的驗收案例用「輸出檔存不存在」當閘門,是本 repo 目前沒有的第二種週跑機制,沒有引用或沿用既有戳記檔慣例。往後要加下一個週跑步驟的人會在兩套閘門邏輯間猜該抄哪一套。

D2
severity: minor
blocking: 否
引句:「governance/eval/lens-utilization/archive/<年>-W<週>.json」
file: `governance/eval/lens-utilization/2026-09-04-first-report.json:1`
既有的首份報表 `2026-09-04-first-report.json/.txt` 直接放在 `lens-utilization/` 目錄下,沒有子目錄;S4 新開一層 `archive/` 子目錄放週檔,跟鄰居檔的擺放方式不同,但不影響邏輯正確性。

D3
severity: minor
blocking: 否
引句:「本週沒跑過才跑,輸出寫到」
file: `governance/autonomous-loop.sh:429-431`
`run_replay` 明寫「模組炸掉時不蓋週戳……明天重試」並 fail-open,是踩過真事故(cb3 finder-f4)才補上的規則;S4 全文沒交代週跑腳本本身失敗(例外/壞逐字稿以外的整支崩潰)時,閘門與重試怎麼處理,跟鄰居檔比對不到對稱的錯誤處理段落。

D4
severity: minor
blocking: 否
引句:「由 `governance/eval/refresh_labels.py` 維護;走它既有的流水線」
file: `governance/eval/refresh_labels.py:112-149`
⚠ 判不準:`refresh_labels.py` 的 `delta`/`apply` 既有流水線(`cmd_delta`/`_apply_locked`)只補「既有案例缺的標籤」,不建立新案例;`retrieval-goldset.json` 的 `edit` 案例綁定具體 commit 的 diff 片段,跟逐字稿衍生的(檔案,節點)miss 配對形狀不同。S2 沒交代這一步怎麼把 miss 候選轉成合格的新 `edit` 案例,是漏寫還是另有機制,交編排者裁。

---

不對齊共 4 條,其中 major 1 條;最高 severity: major
