preflight-4: ran

# r1 前掃收貨(2026-10-31)

前掃席:sonnet,一般子代理,固定四項清單(未定義的詞、壞引用、範圍自相矛盾、機械宣稱驗語意)。結果:①命中 7、②命中 0、③命中 4、④驗 9 條(成立 4、部分成立 2、不成立 1、待實測 2)。①②③與存在類命中直接修真檔、不算 findings;語意類命中逐條列在下面。沒有動到「核心裁定」(決策 d1、d2 的裁定內容不變;d2 的關鍵字類別範圍在做法第 6 條收窄,見語意第 4 條)。

## 語意類命中(修改前 → 修改後)

1. commands.json 路徑(④-3,部分成立)
   - 前:「每支 flow 通過的那次嘗試,讀它 debug 目錄的 commands.json」
   - 後:「從 steps.json 那次的 evidence.dir 讀 <dir>/debug/<flow 的 name:>/commands.json」;實測段補上探針用的旗標與實際落點。
   - 編排者重現:2026-10-31 探針流程 `name: label_probe` 帶 `--test-output-dir <ev> --debug-output <ev>/debug --flatten-debug-output`,`find <ev> -type f` 列出 `ev/debug/label_probe/commands.json`,`<ev>` 底下沒有另一份 commands.json。HIT(前掃懷疑的「應在 <ev>/commands.json」不成立,本機 2.10.0 實際落在 debug 子目錄)。

2. judge 拿不到主線(④-4,部分成立;連帶 ③-4)
   - 前:做法第 4 條讓 judge 判「新」情境並判沒過;條款 S1、S3、S4、S12 由 judge 判。
   - 後:分兩段——judge 只把 checks 記進紀錄並印預覽;推送檢查(已有挑主線的結果)判新舊與擋不擋。條款改為 S1–S3 驗 judge 記事實、S4–S10 驗推送檢查。整套跑時 judge 不讀 features 的問題一併消失(覆蓋在推送檢查用設定裡的情境→flow 對照算)。

3. 「跟主線上同一支 flow 上一份通過紀錄比」(④-5,不成立)
   - 前:「跟主線上同一支 flow 上一份通過紀錄比,算數的檢查變少就……列出」
   - 後:紀錄新增 checks 欄;比對對象明訂為「用分岔點那棵樹的 e2e 段算指紋找到的那份紀錄」;找不到或舊紀錄沒有 checks 欄印一行不比(S10)。

4. 單向門關鍵字表的類別(③-3)
   - 前:「命中規格閘同一張關鍵字表」(表有四類,含 self-governance)
   - 後:只取 payment、external-send、prod-irreversible 三類;S8 加「只命中 self-governance 的字不算單向門」。理由:Enzo 裁的單向門指金流、對外送出、不可逆資料,第四類是工具鏈守衛面、跟 App 功能無關。決策 d2 原文已寫「金流、對外送出、不可逆資料三類」,這裡是讓做法跟 d2 原文一致,不是改裁定。

5. 「沒有 commands.json(Maestro 太舊、沒帶 debug 旗標)」(④-6,成立但漏情況)
   - 前:只列兩種原因,判「沒判到」。
   - 後:evidence.dir 空、檔不在、格式看不懂一律記 checks: null;新流程因此被推送檢查擋(S5),涵蓋「不是用範本腳本跑的」。

6. 設定檢查不擋未知鍵(④-8)
   - 前:「lumos macrobench --check-config 應回 2 並印出哪一項壞」(未說明現在不驗)
   - 後:做法第 1 條寫明「現在的情境檢查不擋未知鍵,所以要新增檢查;舊版 lumos 讀到新鍵會靜默忽略」,S11 補 at、one_way、id 字元的檢查與「三個鍵都不寫照舊回 0」。

## 非語意類(直接修真檔)

- ① one_way 位置與值域、state 用途、accept_review.at 格式補進做法第 1 條;accept_required、risk 是 Q1、Q2 題目文字裡的當時建議,正文加一句「以決策為準」;「驗收總表」改寫(RETIRE-IF 改成抽查治理帳的擋下紀錄);檢查數的存放處補成紀錄的 checks 欄。
- ③-1、③-2 同上;條款重新依序編號 S1–S13。
- ④-1、④-2、④-7、④-9 成立,不改。

## 重現表

| 項 | 命令 | 結果 |
|---|---|---|
| ④-3 路徑 | 探針 `maestro --udid R52X305YY7W test --format junit --output r.xml --test-output-dir ev --debug-output ev/debug --flatten-debug-output probe.yaml`;`find ev -type f` | HIT:`ev/debug/label_probe/commands.json`,ev 底下無第二份 |
| ④-3 label 與 WARNED | 同一份 commands.json 逐條印 command/label/optional/status | HIT:A1 COMPLETED 有 label;A2 optional WARNED;runFlow SKIPPED、A3 不出現 |
