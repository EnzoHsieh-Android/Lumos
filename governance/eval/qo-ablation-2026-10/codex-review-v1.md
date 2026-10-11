
我依 `lumos-project-notes` 流程交叉核對了程式、預先登記與圖譜計劃；計劃原本要求的是「該被問到的人決定」，但預先登記已弱化成全文關鍵詞命中。全程唯讀，未修改檔案。

## Findings

### 1. blocker — 六題都會在判分時拋例外，整批第一場即中止

- 檔案：
  - [scenarios.jsonl](/Users/enzo/orca/workspaces/lumos-toolchain/Backend_improve/governance/eval/qo-ablation-2026-10/scenarios.jsonl:1)
  - [scenario_probe.py](/Users/enzo/orca/workspaces/lumos-toolchain/Backend_improve/scripts/scenario_probe.py:331)
- 問題：六題的 `expect` 都是空陣列；`judge()` 卻無條件執行 `min(exp_idx.values())`。`run_one()` 呼叫 `grade()` 後，例外會被外層記成 fatal 儀器例外，然後停止整批。拿不到預計的 36 場。
- 驗證：

```text
$ python3 -c 'import scripts.scenario_probe as p; print(p.grade(
  {"expect": [], "forbid_before": []}, [], "合理回答"))'

ValueError: min() iterable argument is empty
```

- 建議：新增明確的「只收集回答、不跑既有命令判分」模式；或讓 `judge()` 對空 `expect` 回傳成功。必須先加一個以本題庫跑到 JSON 輸出的回歸測試，再消耗模型額度。

### 2. blocker — 預登記的命令不保存回答，且 repo 內沒有 gold 計分器

- 檔案：
  - [preregistration.md](/Users/enzo/orca/workspaces/lumos-toolchain/Backend_improve/governance/eval/qo-ablation-2026-10/preregistration.md:46)
  - [scenario_probe.py](/Users/enzo/orca/workspaces/lumos-toolchain/Backend_improve/scripts/scenario_probe.py:1143)
  - [scenario_probe.py](/Users/enzo/orca/workspaces/lumos-toolchain/Backend_improve/scripts/scenario_probe.py:1419)
- 問題：登記的執行命令沒有 `--out`；其預設值是空字串，因此每場的 `answer`、`calls` 等資料不會落檔。探針也完全不讀 `gold.json`，覆蓋率、亂問數、先寫程式數與截斷率都沒有已凍結的實作。跑完後才另寫計分程式會留下大量研究者自由度。
- 驗證：

```text
$ rg -n 'gold\.json|must_surface|should_not_ask' scripts/scenario_probe.py
# 無輸出

$ python3 -c 'from pathlib import Path; p=Path("scripts/scenario_probe.py").read_text();
print("gold refs",p.count("gold.json"),
      "must_surface refs",p.count("must_surface"),
      "should_not_ask refs",p.count("should_not_ask"))'
gold refs 0 must_surface refs 0 should_not_ask refs 0
```

而程式只在：

```text
1143: ap.add_argument("--out", default="")
1419: if a.out:
1422:     _atomic_write_text(... {"results": results, ...})
```

才保存結果。

- 建議：開跑前加入並凍結一支 scorer；命令明列甲乙各自的 `--out` 路徑。scorer 應讀兩份結果與 gold、輸出逐場逐項判定、總指標及輸入 SHA-256。

### 3. blocker — 主指標不能回答「有沒有找出要人決定的事」

- 檔案：
  - [preregistration.md](/Users/enzo/orca/workspaces/lumos-toolchain/Backend_improve/governance/eval/qo-ablation-2026-10/preregistration.md:7)
  - [preregistration.md](/Users/enzo/orca/workspaces/lumos-toolchain/Backend_improve/governance/eval/qo-ablation-2026-10/preregistration.md:51)
  - [arm-b-guidance.md](/Users/enzo/orca/workspaces/lumos-toolchain/Backend_improve/governance/eval/qo-ablation-2026-10/arm-b-guidance.md:15)
  - [後端工程提問與證據擴充_計劃.md](/Users/enzo/orca/workspaces/lumos-toolchain/Backend_improve/docs/lumos-toolchain-knowledge/Projects/後端工程提問與證據擴充_計劃.md:151)
- 問題：主指標在整份回答中搜尋關鍵詞，不要求它是問題、標成「待人」、尚未由證據回答，甚至不要求語意為肯定。這與圖譜計劃的「該被問到的人決定」不同。

  乙組又被要求列「待查／自答／待人／延後／已決」、記錄所有題目並附建議。因此只要把某項列成「自答」「不適用」或「延後」，照樣拿 must-surface 分；較長的固定格式也增加碰到正規式的機會。反過來，「一次最多問三題」卻要對六個 gold 項目算 recall，也可能懲罰真正照規則優先排序的乙組。

- 驗證：乙組原文已直接命中五個 gold 項次：

```text
$ python3 ... # 將每條 must_surface regex 套到 arm-b-guidance.md
P1 p1_idempotency '重試、重複'
P2 p2_idempotency '重試、重複'
P3 p3_consistency '一致性'
P3 p3_ops '維運'
P4 p4_idempotency '重試、重複'
```

否定敘述也得分：

```text
'庫存功能不在本期。'                 -> p2_inventory True
'延遲不是目前的驗收條件。'           -> p2_latency True
'不採 Kafka，因此沒有一致性問題。'   -> p3_consistency True
'點數永不過期。'                     -> p4_expiry True
'不採 2PC。'                         -> p6_consistency_vs_split True
```

- 建議：改成結構化輸出，主指標只評 `狀態=待人` 的前三題；至少同時報：
  - recall：應問的人決定有多少進入待人前三題；
  - precision：待人前三題有多少真的需要人決定；
  - 已知事項重問率；
  - 優先順序是否正確。  
  自答、延後、否定或純背景提及不得算 must-surface 命中。

### 4. major — gold 正規式有大量合理漏判與明顯誤中

- 檔案：[gold.json](/Users/enzo/orca/workspaces/lumos-toolchain/Backend_improve/governance/eval/qo-ablation-2026-10/gold.json:1)
- 問題：正規式多半只辨識名詞，不辨識意圖與極性；另一方面又把合理同義說法限制得很窄。實驗差距門檻只有 15 個百分點，這種誤差足以改變結論。
- 驗證，合理語意卻漏判：

```text
P1 async_scope:
'訂單建成後究竟要觸發哪些後續工作？' False

P1 response_model:
'API 成功回傳時，代表已完成扣庫存，還是僅表示請求已收下？' False

P1 hot_item:
'300 RPS 會打在同一個 SKU，還是平均散開？' False

P3 ops:
'這兩個元件由現有平台團隊代管嗎？' False

P5 slot_boundary:
'A 訂到 10:00，B 能否從 10:00 起訂？' False

P6 consistency_scope:
'哪些跨服務狀態必須原子提交？' False
```

同時，上一 finding 所列多個否定句全部誤中。

- 建議：每個 gold 項目先建立至少 3 個應中同義句、2 個不應中的否定／不適用句，讓 scorer 自測；最好由兩名不知道組別的人工標註者判「這是否是待人決定」，正規式只作初篩。

### 5. major — 「亂問」規則正好漏掉乙組被要求產生的格式

- 檔案：
  - [preregistration.md](/Users/enzo/orca/workspaces/lumos-toolchain/Backend_improve/governance/eval/qo-ablation-2026-10/preregistration.md:55)
  - [arm-b-guidance.md](/Users/enzo/orca/workspaces/lumos-toolchain/Backend_improve/governance/eval/qo-ablation-2026-10/arm-b-guidance.md:17)
  - [gold.json](/Users/enzo/orca/workspaces/lumos-toolchain/Backend_improve/governance/eval/qo-ablation-2026-10/gold.json:1)
- 問題：只有整行以問號結尾才算亂問；但乙組被要求標狀態、附建議答案。自然輸出會在問號後接「建議」「待人」等文字，因此同一個亂問，甲組較容易被抓、乙組較容易漏掉。另 P6 同樣是訂單題，卻完全沒有 `should_not_ask`，可重問 README 的 300 RPS、無付款、單區域而不受罰。
- 驗證：

```text
'尖峰流量是多少？'                         True
'[待人] 尖峰流量是多少？（建議沿用 300 RPS）' False
'尖峰流量是多少？ 建議：300 RPS'             False
'尖峰流量是多少？ #待人'                     False
```

- 建議：先解析一題一行的結構，再對「問題欄」判斷，而非要求問號為行尾；以禁止主題去重計數。P6 也應套用所有適用的 README 已知事項。

### 6. major — 允許的截斷量本身就足以翻轉 15 點門檻

- 檔案：
  - [preregistration.md](/Users/enzo/orca/workspaces/lumos-toolchain/Backend_improve/governance/eval/qo-ablation-2026-10/preregistration.md:53)
  - [preregistration.md](/Users/enzo/orca/workspaces/lumos-toolchain/Backend_improve/governance/eval/qo-ablation-2026-10/preregistration.md:70)
  - [scenario_probe.py](/Users/enzo/orca/workspaces/lumos-toolchain/Backend_improve/scripts/scenario_probe.py:1066)
- 問題：每組 3/18 場被切到 1500 字時，截斷率只有 16.7%，仍可判定；但三場各有六個 gold 項目，最多可丟掉 18/108＝16.7 個百分點，已大於通過門檻。乙組被要求留下完整紀錄，尤其容易更長，形成差別性截尾。
- 驗證：

```text
17/108 = 0.1574074074074074
3 truncated runs x 6 / 108 = 0.16666666666666666
```

- 建議：保存完整回答；另存原始長度、是否裁切與 SHA-256。若仍限制大小，任何主要結果所用回答遭裁切都應判整組無效，而不是容許 20%。

### 7. major — 「先寫程式」會漏掉最常見的 shell 寫檔方式

- 檔案：
  - [preregistration.md](/Users/enzo/orca/workspaces/lumos-toolchain/Backend_improve/governance/eval/qo-ablation-2026-10/preregistration.md:57)
  - [scenario_probe.py](/Users/enzo/orca/workspaces/lumos-toolchain/Backend_improve/scripts/scenario_probe.py:184)
- 問題：Bash 只找 `gradle init`、`spring init`、`start.spring.io`。模型可用 `touch`、重新導向、`tee`、Python、`git apply`、`cp` 等直接建立程式而完全不計。這不是邊角案例，是 agent 常見寫檔路徑。
- 驗證：

```text
'mkdir -p src/main/kotlin && touch src/main/kotlin/App.kt' False
'python3 -c "open(\"build.gradle.kts\",\"w\").write(...)”' False

tool_calls_from_stream(...) =>
[('Bash', 'mkdir -p src/main/kotlin && touch src/main/kotlin/App.kt')]
```

探針確實保存該 Bash 指令，但預登記規則不會判成先寫程式。

- 建議：每場模型結束、清除沙盒前，以凍結基線比較 `git status --porcelain`／檔案樹差異；任何非文件程式檔新增或修改都算。工具呼叫只作輔助證據。

### 8. major — 18 場不足以支持「不增」；15 點只是效果門檻，不是可靠證據

- 檔案：[preregistration.md](/Users/enzo/orca/workspaces/lumos-toolchain/Backend_improve/governance/eval/qo-ablation-2026-10/preregistration.md:60)
- 問題：實際獨立設計單位更接近六個固定情境，不是 18 個；每題的三次是巢狀重跑。最壞情況下，18 個獨立有界場次之組差標準誤約 16.7 點，已大於 15 點門檻。對稀有副作用，即使乙組 0/18，單側 95% 上界仍約 15.3%，不能宣稱「不增」。
- 驗證：

```text
worst-case SE(diff of 18 independent run means) = 0.16666666666666666
0/18 one-sided 95% upper = 0.1533175539572782
```

- 建議：仍可保持簡單：
  1. 先算六個情境各自的三次平均差；
  2. 要求總平均差 ≥15 點；
  3. 對六個情境差做精確 paired sign-flip/permutation test，單側 `p≤.05`；
  4. guardrail 只表述為「本樣本未觀察到增加」。若要證明非劣，必須預先定可接受增幅並擴大樣本。

### 9. major — 固定批次順序、缺場與「會重試」的文字互相不一致

- 檔案：
  - [preregistration.md](/Users/enzo/orca/workspaces/lumos-toolchain/Backend_improve/governance/eval/qo-ablation-2026-10/preregistration.md:46)
  - [preregistration.md](/Users/enzo/orca/workspaces/lumos-toolchain/Backend_improve/governance/eval/qo-ablation-2026-10/preregistration.md:70)
  - [scenario_probe.py](/Users/enzo/orca/workspaces/lumos-toolchain/Backend_improve/scripts/scenario_probe.py:1163)
- 問題：
  - 題序固定 P1→P6，每題三次連跑；
  - 甲乙是兩個獨立批次，未預登記隨機或交錯順序；
  - 文件稱用量上限會重試，但所列命令未帶 `--wait-on-limit`，預設是 0 秒、不重試；
  - 允許每組只剩 15 場，卻直接平均，可能甲缺 P6、乙缺 P1，組成不再相同。
- 驗證：

```text
1163: ap.add_argument("--wait-on-limit", type=int, default=0,
1164:   "預設 0=不等,照記成儀器例外")
```

- 建議：預先產生固定亂序表，以 `(題目, run)` 為單位交錯 A/B；只分析完整配對。每題至少保留同數有效重跑，否則整個 pair 排除；明列等待與最大嘗試次數。

### 10. major — 乙組 commit history 直接暴露「arm B guidance」

- 位置：兩份受測 repo 的 Git 歷史。
- 問題：乙組不只多一段文字，還多一個標題為 `arm B guidance` 的提交。受測 agent 若依既有規矩查看 git log，會立刻知道自己是實驗組，產生 demand characteristic；甲組則沒有對應提交。
- 驗證：

```text
order-svc-a HEAD: 91d0435 lumos init
order-svc-b HEAD: 3b6f6d2 arm B guidance
```

- 建議：兩組都從各自乾淨建置產生相同形狀的歷史，提交數及中性訊息一致，例如都 squash 成 `chore: initialize evaluation fixture`。不要讓分組名稱出現在 repo 可見內容。

### 11. minor — 兩組沙盒的目錄拓樸仍不同

- 位置：兩份受測 repo 的 `docs/order-svc-knowledge/`。
- 問題：B 由 Git clone 產生，Git 不保存空目錄；因此 A 有五個額外空資料夾，B 只有 `MOC`。`make_sandbox()` 使用 `rsync -a`，會保留這個差異。模型若列目錄或決定把「待決問題」放哪裡，可能看到不同環境。預登記的「只差 20 行」並不完全成立。
- 驗證：

```text
A dirs: Projects Verification Sessions Systems Issues MOC
B dirs: MOC
```

- 建議：用相同產生程序建兩個 fixture，或在 A 移除未追蹤空目錄；開跑前比較完整目錄樹、追蹤檔內容與經正規化後的 Git 設定。

### 12. major — 人工複核不足以攔住上述判準錯誤

- 檔案：[preregistration.md](/Users/enzo/orca/workspaces/lumos-toolchain/Backend_improve/governance/eval/qo-ablation-2026-10/preregistration.md:76)
- 問題：
  - 固定抽每題第 1 次，不是隨機抽樣；
  - 編排者知道組別，也知道門檻結果；
  - 「全部判定」分母不清楚是否包含 must-surface、should-not-ask、每條 regex 或每行；
  - 容許最高 25% 誤判仍接線，但主要效果門檻只有 15 點，誤判容許量反而更大。
- 驗證：文件逐字規定「每組每題抽第 1 次」與「超過 25%」；沒有盲化、抽樣種子、分母公式或分歧仲裁規則。
- 建議：至少隱去 arm 與 run，對 36 場全部做雙人獨立標註；先寫清判定單位與分歧處理。若只抽樣，固定亂數種子並將任何足以改變 15 點結論的誤判判為無定論，而不是等到 25%。

## 已核對、目前沒發現問題的部分

- 三份指紋前綴都與實際 SHA-256 相符。
- 乙組的 `CLAUDE.md` 與 `AGENTS.md` 都逐字附上完整 guidance；甲組兩檔都沒有：

```text
order-svc-a CLAUDE.md False
order-svc-a AGENTS.md False
order-svc-b CLAUDE.md True
order-svc-b AGENTS.md True
```

因此 Claude/Codex 各自的 repo 指示檔確實都帶到了乙組內容；但本次預登記只執行 Claude Sonnet，不能把結果外推成 Codex 效果。

總結：blocker 3 條，major 8 條。
