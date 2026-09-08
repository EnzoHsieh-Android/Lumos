<!-- 外家否決席 r2(Codex, --sandbox read-only;原始逐字稿 r2-codex-raw.txt;正規化:去重複印出的第二份、去行尾雙空白) -->
severity: blocker

前輪①舊帳五格印 ?: 修好；已明定任一欄缺失時五格各自印 `?`，不再把未知偽裝為數字。
引句:「KEY:S3 讀側只印★問閘的這一輪★一行 + gov --stats 一段;缺欄位五格各印 ?」

前輪②駁回清單灌大: 修了但引入 X；必填、理由與 intake 驗證已補上，但驗證仍是子字串，不能證明是同一個 id。
引句:「有 --findings-set 就★必帶 --refuted-set★(跟 folded/accepted 同一種硬擋慣例),值 none 表示這輪 0 條駁回;id=理由 逗號串,理由 ≥4 字且含實字」

前輪③resolved 值域: 修好；改成驗收輪舊項不留 severity 行，與 `_SEV_ORDER` 的封閉值域一致。
引句:「KEY:S4 只改 skill(design-loop 步驟 10 後補逃逸段、範本加三旗標、驗收輪舊項不留 severity 行)」

1. 下限守衛可被列表格式完全繞過
severity: blocker
blocking: 是；它是 reported 誠實性的唯一機械下限，任何數量的列表 finding 都可填 reported=1 通過。
引句:「_report_severities 只認獨立行,標題內嵌/列表格式的報告數到 0 → 守衛形同虛設(不擋)」
file: `governance/review-reports/審查有沒有用記帳/r2-snapshot.md:71` 最小重現：報告有十行 `- severity: major`、`--reported 1`；`scripts/lumos:4822` 的 fullmatch 取得 0，故不會 rc2。

2. 把第一個 severity 宣告一律扣成檔級，會吞掉無檔級報告的第一條 finding
severity: blocker
blocking: 是；既有真實報告可直接從 finding 開始，提案沒有要求專用檔級行或可判定的檔級標記。
引句:「檔序第一個宣告=檔級」
file: `governance/review-reports/審查有沒有用記帳/r2-snapshot.md:41` 最小重現：首行 `severity: major` 就是唯一 finding、無檔級行、`--reported 0`；解析結果 1 被扣為 0，低報不擋。

3. intake 的子字串驗證可把不存在的 refuted id 當成存在
severity: blocker
blocking: 是；這會重新打穿「駁回不是任意 CLI 輸入」的核心保證。
引句:「每個駁回 id 要在 intake 檔文字裡出現(子字串),沒有就 rc2」
file: `governance/review-reports/審查有沒有用記帳/r2-snapshot.md:47` 最小重現：intake 僅含 `f10`，輸入 `--refuted-set f1=無法重現` 仍命中 `f10` 的子字串並計作 R。

4. self-found-set 無法證明「沒有任何一席報過」，可重標已報 finding
severity: major
blocking: 是；僅驗證它是 findings-set 子集，沒有逐席 finding-id 載體可排除席位已報的項目。
引句:「編排者自己踩到、沒有任何一席報過的發現」
file: `governance/review-reports/審查有沒有用記帳/r2-snapshot.md:49` 最小重現：某席已報 `f1`，carrier 仍可將 `f1` 寫入 self-found-set；讀側會把席位產出改算為 S，無從追究重標。

5. 多席輪的 N 與 M/R 不是同一粒度，單向不等式抓不到漏併
severity: major
blocking: 是；N 是每席 reported 加總，M/R 卻只能由唯一 carrier 的全輪集合得出，少併一席 finding 時不會印算術不通。
引句:「席位報 N(+編排者自找 S)→ 存活 M / 重現不到 R → 折 F / 放行 A」
file: `scripts/lumos:13600` 最小重現：兩席各 `reported=1`，carrier 僅列並折 `f1`、另一席的 `f2` 不進 carrier 集合；N=2、M=1、R=0，`N+S < M+R` 為假，遺漏仍靜默。

總結最嚴重 severity: blocker；blocking 4 條。
