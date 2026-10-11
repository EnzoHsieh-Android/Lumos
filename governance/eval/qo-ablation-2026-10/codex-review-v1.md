
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
