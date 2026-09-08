---
type: project
status: doing
created: 2026-09-08
updated: 2026-09-08
aliases:
  - 提問表態閘
  - stack question disposition gate
  - 檢核答案機械化
  - 已滿足或不需要
  - 觸發式適用性
  - 哪些問要答
related:
  - "[[Projects/pitfalls棧別效能追問_計劃]]"
  - "[[Systems/效能檢核目錄]]"
  - "[[Systems/pitfalls-code-loop]]"
  - "[[Systems/convergence-evidence-gate]]"
  - "[[Systems/lumos-refcheck]]"
  - "[[Systems/bound-tests-gate]]"
  - "[[Systems/test-profile-multiplatform]]"
  - "[[Systems/known-pitfall-refresh-token]]"
  - "[[Issues/寫下風險當成處理風險]]"
  - "[[Issues/只退場不痛的機制]]"
  - "[[Issues/code-loop-pass自失效追尾]]"
  - "[[Projects/iOS與Node後端補棧_計劃]]"
  - "[[Systems/finding-refute]]"
tags:
  - type/project
  - status/doing
  - scope/guards-gates
summary: |-
  FLAG:DECISION
  KEY:★立案(2026-09-08 Enzo:「這些提問,實務上 Agent 進入實作時有在證明已滿足或不需要?」)★——查證答案是沒有:三時機(改檔前 hook/推送前 advisory/終審)全是「推到眼前」;唯一義務在 code-loop reference 一句「留痕**建議**含答案」並自註「工具不驗 note 內容、人工紀律」;治理帳 177 筆 code-loop 事件只有 5 筆帶一句答案;spec 端 pitfalls --check 只驗「實務隱患」節存在。=[[Issues/寫下風險當成處理風險]]形狀
  KEY:★第二題併入(Enzo 同晚:「功能如何判斷該問哪些問題,而不是窮舉出來之後每條都要附答案?耗時也耗 token」)★——每題掛 `when` 觸發 regex 對 added 行比對,命中才適用;未觸發由工具自動記 na(零 token);某棧改超過 300 行則全問;改檔前 hook 也只注入命中的題。世界解=CodeRabbit path_instructions/Danger 條件式留言/已知坑 pitfall_when 同型,Checklist Manifesto 5–9 殺手項,Meta 預測式測試選擇「按改動特徵選、用歷史量 recall」——借觸發與量 recall,不借 ML
  KEY:★裁定=借設計審處置閘+已知坑內容觸發,零新機制類型★——diff 有適用題時,推送前每一問要有機器可讀表態:satisfied(附證據 path:line 或 test:名)/na(理由)/todo(連 Issue+理由);★r1 折入後閘條件改為「有適用題就擋,不看 tier」★(邊界席 B1:tier 由 Python 形狀的 regex 算,kt/swift/vue 改動幾乎永遠 standard,原設計的閘等於開不了門;適用性把每次成本壓到幾行,擋得起);supersede 2026-07-20「standard 不擋」那條(當時是整棧全問的提醒,前提已變)
  KEY:★r1 折入的核心改動★——表態是獨立原語 `code-loop dispositions <檔>`(派審查員之前就寫,marker 原子寫入+治理帳事件),pass/skip 簽章不變、skip 一樣要先表態(外家 F1/正確性 C4:否則 skip 是無痛退場);check 用跟 pass 留痕同一套座標解析表態(本機 marker/CI 從治理帳事件重建/簿記豁免祖先 sha),錨點一律對被推送 commit 的樹驗(外家 F3),test: 走 `_platform_test_index` 多平台索引(F4/C2/H6/B4),存入原文==當前原文才認(F5),派工鏡頭附表態且快取 key 含表態 sha(C3;H3/B6:表態在派席前就存在才反駁得到)
  KEY:機械錨點只抓最懶的謊:path:line 在 at_sha 樹存在且行號在範圍;test: 名在該平台索引且該 root 對 at_sha 乾淨;todo 的 Issue 在 at_sha 樹存在且 status open/doing 並附理由;na/todo 理由門檻=非 ASCII ≥10 字、純 ASCII ≥25 字;答錯留給審查席(對稱既有辯方機制)
  KEY:副產品=每一問歷來 satisfied/na/todo/auto-na 比例進 gov --stats(mapper 白名單要放行新欄,接手席 H2);死題候選(≥10 次人工表態且 100% na)與觸發太窄候選(recall-miss ≥3);今天沒有任何辦法知道哪些題在空轉
  KEY:天花板(向人複述):表態可以敷衍,錨點與審查席只降機率不是證明——同設計審處置閘承認的 GIGO(垃圾進垃圾出:表態寫什麼工具就記什麼);閘內部錯誤走既有 `_gate_failopen`(治理帳 kind=fail-open,架構對齊席 A1);不做 LLM 判答案對錯、不做 LLM 前置分類(花 token 與動機相反)
  PRIOR-ART:①最小解在既有機制層——處置閘(每條 finding 折掉或附理由接受,機械數)已是設計審與代碼審的收斂判準,本案只是把「發現」換成「提問」;觸發借已知坑節點的 `pitfall_when: content:<regex>` 與 `_PITFALL_DIFF_PATTERNS`(同一種「內容命中才問」);錨點借 refcheck 存在性與 `_platform_test_index`;留痕借 code-loop 留痕座標與治理帳事件 ②世界解:CodeRabbit path_instructions(docs.coderabbit.ai/guides/review-instructions)、Danger.js 條件式規則、reviewdog 只對改到的行出聲、Checklist Manifesto 5–9 殺手項、Meta Predictive Test Selection(arXiv 1810.05286:按改動特徵選、95% 失敗仍抓到)、Meta RADAR 2026(LLM 分類 diff 風險類,列未來層);PR template checkbox 普遍但不擋(GitHub docs),真的擋的是「all review threads resolved 才准 merge」政策(2026-08-26 的世界對照報告 `governance/review-reports/world-benchmark-2026-08-26.md` 已引)——本案=把同一政策套到「機器提的問」;Vercel 實證靠模型自覺 56% 跳過 ③裁定=借用既有設計(家規三選一裡的 borrow-design:借既有/真沒輪子才自建/新依賴幾乎不選),不加依賴
  DEP:scripts/lumos(_STACK_PERF_QUESTIONS 形狀、_pitfall_diff_collect、_stack_key_for_file、cmd_pitfalls --dispositions-template、cmd_code_loop dispositions/check、_codeloop_guard_verdict、_codeloop_read_from_ledger、_codeloop_gov_log、_codeloop_write、_validate_repo_ref、_platform_test_index、cmd_dispatch_lens 與 _lens_cache_path、cmd_gov load mapper 與 _render_gov_stats)｜scripts/hooks/claude/impact-hook.py 棧段過濾｜scripts/hooks/pre-push advisory 分支與逃生文字｜skills/lumos-code-loop SKILL.md 步驟 1 後+reference.md 棧別段｜commands/06-代碼審與推送.md｜Systems/效能檢核目錄 KEY 行③
---
# 棧別提問表態閘（2026-09-08；r2 修訂稿——折入 r1 五席 + 併入「哪些問要答」）

> 白話：工具會在改檔前、推送前、終審時把「這個技術棧該問自己的效能問題」推到 agent 眼前，但推到眼前之後沒有任何機制要求它回答。這篇做兩件事：**（一）命中的每一問，推送前要留下一個機器讀得懂的交代**——做到了（附證據）、不適用（附理由）、還沒做（連到待辦）——缺一問就不准推；**（二）「命中」不是整棧全問，而是靠改動內容觸發**——沒碰到的題由工具自動記「未觸發」，零 token。做法全借既有機制：設計審的處置閘、已知坑的內容觸發、refcheck 的存在性核對、code-loop 的留痕座標。

## 現況查證（2026-09-08，全部實查；r1 正確性席訂正數字）

- 三個時機的實際效果都是「保證被看見」：hook 注入純提醒；推送前的 advisory 分支只印問題；終審蓋章把 note 原樣寫入。
- 唯一寫了義務的地方是代碼審 skill 的參考文件：「終審留痕**建議**含對應檢核問題的答案」，同一句自註「工具不驗 note 內容、人工紀律」。
- 治理帳裡 code-loop 的 pass／skip 事件 177 筆，其中 5 筆的 note 帶了一句檢核答案，其餘沒有（r1 前我寫「0 筆」是 grep 格式沒對上，席位抓到）。
- 設計端同形：`pitfalls --check` 只驗「## 實務隱患」節存在，段落寫「無」也過。
- 風險分級的來源跟棧命中無關：tier 由一組 Python 形狀的 regex 算（HTTP 呼叫、open、SQL 寫入、threading、sleep），Compose／協程／SwiftUI／Vue 的典型改動幾乎不會命中，所以 kt／swift／vue 的 diff 幾乎永遠是 standard（r1 邊界席 B1）。

## 設計

### 一、哪些問要答：觸發式適用性（Enzo 2026-09-08 睡前指定；PRIOR-ART 見 summary）

- `_STACK_PERF_QUESTIONS` 每題從字串改成 `{"q": 原文, "when": [regex, …]}`。`when` 對「該棧檔案的 added 行」（測試檔排除，同既有規則）做不分大小寫比對，任一命中＝適用。每題都必須有觸發；寫不出觸發的題本身就是設計問題。
- 適用集合＝命中的題。`pitfalls --diff --json` 的 `stack_questions` 改為**只列適用題**（向後相容：仍是 list of str），另加 `stack_questions_meta`：每題 `{id, question, applicable, triggered_by}`（全表，含未觸發）。
- 大改動全問：某棧 added 行 > 300（`.lumos/config.json` 的 `stack_questions.ask_all_over_lines` 可調）→ 該棧全表適用。改得多＝觸發漏得多，寧多問。
- 改檔前 hook：對「目前檔案內容」跑同一組 `when`，只注入命中的題；沒命中任何題就不注入棧段。
- 未觸發的題由樣板自動填 `{"status":"na","reason":"未觸發:<regex 清單>","auto":true}`——帳本仍完整、零 token；check 重算適用性，適用題若表態是 `auto:true` → BLOCKED（工具判適用但沒人答）。
- 統計除三值外另計 auto-na 比例；審查席若在某次審查抓到「對得上某未觸發題」的問題，人工登記一筆 `recall-miss`（`lumos code-loop recall-miss <棧-序號> --note`），同一題累積 3 次就修它的 `when`（這是 Meta 預測式測試選擇「量 recall」那一半，用人工帳代替 ML）。
- 觸發表與問題表同處（單源），效能檢核目錄同步義務不變（多一欄「觸發」）。

### 二、表態的形狀

- 一份 JSON **檔案**（旗標吃路徑，同 `--from-json` 慣例；r1 接手席 H9），鍵＝`<棧>-<序號>`，值＝`{status, question, evidence|reason|issue, auto?}`。`question` 存原文；check 要求「存入原文 == 當前原文」，不等就當缺（r1 外家 F5：表換順序後舊答案不得套錯題）。
- `status` 三值只認小寫 `satisfied`／`na`／`todo`，大小寫不對的錯誤訊息明講「只認小寫」（r1 邊界席 B9）。`satisfied` 必附 `evidence`：`path:line` 或 `test:<名>`／`test:<平台>:<名>`；`na` 必附 `reason`；`todo` 必附 `issue`（`Issues/<名>`）與 `reason`（r1 接手席 H7：todo 是三態裡最好敷衍的，門檻拉齊 na）。
- 理由門檻（r1 邊界席 B8）：去掉空白後，含非 ASCII 字元的 ≥10 字、純 ASCII 的 ≥25 字。
- `path:line` 切分規則（r1 邊界席 B7）：最後一個冒號之後是行號（純數字或 `a-b`），之前是 repo 相對 POSIX 路徑；反斜線先正規化成 `/`；絕對路徑與含 `..` 一律拒收並明講原因，不當成 missing。
- 樣板由工具產：`lumos pitfalls --diff <範圍> --dispositions-template` 印出 JSON（適用題 status 留空、未觸發題自動 na）；零命中棧時印 `{}` 並在 stderr 說明「這次沒有要答的題」（r1 邊界席 B11），agent 填完存檔。

### 三、表態何時寫、閘放哪裡（r1 折入的核心改動）

- **新寫側原語 `lumos code-loop dispositions <檔.json>`**：驗形狀（三值、必附欄、question 非空、理由門檻），寫 `governance/code-loop/<branch>.dispositions.json`（原子寫入：暫存＋`os.replace`；r1 外家 F6）並追加治理帳事件 `{"gate":"code-loop","kind":"dispositions","commit":<head_sha>,"dispositions":{…}}`。**在派審查員之前做**（code-loop 步驟 1 算完 pitfalls 就填），所以派工鏡頭附得到、審查席反駁得到（r1 接手席 H3／邊界席 B6：原設計把表態綁在 pass，派工當下根本不存在，最後一次 pass 之後也沒人能反駁）。
- **`pass`／`skip` 不帶表態旗標、簽章不變**。表態是實作者對改動的陳述，跟「審不審」是兩件事：`skip` 一樣要先表態（r1 外家 F1／正確性 C4：否則 skip 是無痛退場，或者照 pre-push 印的指示做卻被擋）。pre-push 印的逃生路徑文字加一句「先 `lumos code-loop dispositions <檔>`」。
- **閘條件：diff 有適用題就擋，不看 tier**（r1 邊界席 B1）。理由：tier 是 Python 形狀 regex 算的，跟棧命中無關；原設計「tier high 才擋」對 kt／swift／vue 幾乎永遠開不了門；適用性讓每次表態成本壓到幾行，擋得起。這一條 supersede 2026-07-20「standard 只提醒不擋」的裁定（當時前提是整棧全問，現在前提變了），記進 pitfalls棧別效能追問_計劃 的決策。`.lumos/config.json` 的 `stack_questions.gate` 可設 `all`（預設）／`high-only`／`off`，給消費專案過渡。
- **`code-loop check`**（pre-push 與 CI 都跑它）：用跟 pass 留痕**同一套座標邏輯**解析表態記錄——本機讀 marker、CI 從治理帳事件重建（`_codeloop_read_from_ledger` 與 `_codeloop_gov_log` 的 schema 一起改，把 `dispositions` 帶出來；r1 四席一致：F2／C1／H1／B2）、留痕 sha 是目標 sha 的祖先且中間只動簿記檔時照樣認（同既有豁免，r1 接手席 H8）。有適用題 → 逐問核對，任一缺／原文不符／錨點壞 → BLOCKED，訊息三段式，最多列 10 問、其餘一句「另有 N 問」（r1 邊界席 B12）；沒有適用題 → 不多印一個字。tier standard 的既有 advisory 分支改成同一道閘。
- **沒有 `docs/` 目錄的專案**（r1 邊界席 B3）：治理帳寫不進去（既有行為），CI 端重建不了，跟 pass 留痕今天的限制相同；check 在這種情況印明確訊息「這個專案沒有 docs/，CI 端讀不到表態，只能靠本機 pre-push」而不是判「全缺」。
- **`.lumos/config.json` 壞掉時**（r1 邊界席 B5）：`test:` 證據一律判「無法驗證：設定檔解析失敗」→ BLOCKED 並印修法，不拿 csharp 預設 profile 去比。
- 閘內部錯誤 → 走既有 `_gate_failopen`，治理帳 kind 為 `fail-open`（r1 架構對齊席 A1：不是 `warned`）。
- 誤擋時怎麼退：修表態重跑 check；真的要硬推走既有 `--no-verify`（本機不留痕、CI 標紅），同其他閘。

### 四、錨點怎麼驗（只抓最懶的謊；一律對「被推送的 commit」驗，不是工作樹——r1 外家 F3）

- `path:line`：`git cat-file -e <at_sha>:<path>` 存在、`git show <at_sha>:<path>` 行數涵蓋該行（不驗內容）。沒有 at_sha（本機直接叫 check）就退回工作樹（借 `_validate_repo_ref`）。
- `test:<名>`／`test:<平台>:<名>`：用 `_platform_test_index`（多平台感知；r1 F4／C2／H6／B4）取該平台的方法集，裸名走 default_platform；為了對得上被推送版本，要求該平台 root 在 `git diff --quiet <at_sha> -- <root>` 下乾淨，否則 BLOCKED「工作樹跟推送版本不同，先提交」。
- `Issues/<名>`：`git cat-file -e <at_sha>:docs/*-knowledge/Issues/<名>.md` 存在，且開頭 `status:` 是 open／doing（純文字讀，不載入圖譜——check 跑在 pre-push，載入整個圖譜要好幾秒）。
- 答對答錯不驗：留給審查席。派工鏡頭 diff 模式讀表態記錄附進派工單；快取 key 加表態記錄的 sha256（r1 正確性席 C3：原本 20 分鐘 TTL 會吃到舊版）。

### 五、副產品：哪些題在空轉

- `gov --stats` 多一段：按 `question` 原文彙總歷來 satisfied／na／todo／auto-na 次數；某題 ≥10 次人工表態且 100% na → 印「死題候選」；`recall-miss` 累積 ≥3 → 印「觸發太窄候選」。治理帳讀側的 mapper 白名單要放行 `dispositions` 與 `recall_miss` 欄（r1 接手席 H2）。

## 驗收條款

- [S1] `lumos pitfalls --diff <範圍> --dispositions-template` 只對適用題留空 status、未觸發題自動填 na（含 `auto:true` 與觸發清單）、含 `question` 原文；零命中印 `{}`；某棧 added 行 > 門檻時該棧全表適用 [test:t_dispositions_template]
- [S2] `_STACK_PERF_QUESTIONS` 每題有 `when`；`pitfalls --diff --json` 的 `stack_questions` 只列適用題（仍 list of str）、`stack_questions_meta` 列全表；每棧至少一題有「命中樣本／不命中樣本」測試；既有 `t_pitfalls_stack_questions` 的樣本改成會觸發全表的內容 [test:t_stack_question_triggers]
- [S3] 改檔前 hook 對檔案內容跑 `when`，只注入命中的題；零命中不注入棧段 [test:t_impact_hook_stack_questions_filtered]
- [S4] `code-loop dispositions <檔>`：形狀壞（未知或大小寫錯的 status、缺必附欄、question 空、理由不到門檻、evidence 切分失敗）rc2 不寫並講原因；形狀好原子寫 marker＋治理帳事件 [test:t_codeloop_dispositions_write]
- [S5] `code-loop check`（有適用題，不看 tier）：缺鍵、存入原文≠當前原文、適用題卻 `auto:true`、`satisfied` 的 path:line 在 at_sha 樹不存在、`test:` 名在該平台索引掃不到或該 root 對 at_sha 不乾淨、`todo` 的 Issue 在 at_sha 樹不存在或非 open/doing → 各自 BLOCKED 並列出該問（最多 10）；全部合法 → 照舊放行；skip 留痕一樣要表態；`stack_questions.gate` 設 off 時不擋 [test:t_codeloop_check_dispositions_gate]
- [S6] CI 路徑：marker 不在時 `_codeloop_read_from_ledger` 從治理帳事件重建出 `dispositions`；簿記豁免（祖先 sha 之後只動簿記檔）下 check 仍認得表態；config 壞掉時 `test:` 證據 BLOCKED 並說明是設定檔問題 [test:t_codeloop_dispositions_ledger_fallback]
- [S7] pre-push：有適用題未表態 → 擋（同 check）；逃生路徑文字加「先表態」；沒有適用題時輸出與今天相同 [manual:對 kt 樣本 diff 跑 scripts/hooks/pre-push 看輸出與 rc]
- [S8] 派工鏡頭 diff 模式附表態記錄（有才附），快取 key 含表態記錄 sha256 [test:t_dispatch_lens_includes_dispositions]
- [S9] `gov --stats` 多一段按 `question` 原文彙總四值，死題候選與觸發太窄候選；mapper 放行新欄；`code-loop recall-miss` 寫事件 [test:t_gov_stats_dispositions]
- [S10] 文件：code-loop SKILL 步驟 1 之後加「表態」步驟；reference.md 棧別段改成「有適用題：check 會擋；tier 不再是條件」並拿掉「建議」；commands/06 加一列；效能檢核目錄 KEY 行③改成同義（H5）；pitfalls棧別效能追問_計劃 記 supersede 決策 [manual:讀改後的四份文字對照本節]

## 實務隱患

- **守衛面**：本案改 pre-push／CI 的擋法，而且擋的範圍比原設計寬（不看 tier）。已排除誤擋的來源：①適用性讓沒碰到的題不用答；②閘內部錯誤走既有 fail-open 進治理帳；③CI 讀治理帳重建，跟 pass 留痕同一條路（本來就要「pass 後提交帳本再推」，表態事件走同一流程）；④錨點對被推送 commit 驗，工作樹不乾淨時明講原因；⑤設定檔壞掉明講是設定檔；⑥消費專案可用 `stack_questions.gate` 過渡。
- **併發**：同 sha 兩次 `dispositions` 寫入＝原子覆寫、治理帳兩筆，check 取該 sha 最後一筆事件（明文規則）。pre-push 與 CI 同時跑 check 只讀不寫。
- **不可逆**：無——marker 與治理帳都是可 git 還原的簿記。
- **對外送出／金流**：無。
- **既有 pass 記錄**：沒有表態記錄的舊 sha，只在「當前 diff 有適用題」時才被要求；留痕本來就綁 sha。
- **本 repo 自己**：Python 不在棧問題表，這道閘對 scripts/lumos 的改動不會觸發（r1 邊界席 B10，接受：py 題組另案）。

## 刻意不做

- 不用 LLM 判答案對錯，也不用 LLM 前置分類決定適用性（RADAR 型；花 token，跟動機相反）——等 auto-na 比例與 recall-miss 帳告訴我們 regex 不夠再開。
- 不做設計端（spec）的逐問表態——`pitfalls --check` 的節存在性檢查另案。
- 不做路徑 glob 觸發（棧本來就靠副檔名／package.json 認；glob 留給消費專案 config 覆寫，未來）。
- 不加 Python 題組（B10，另案）。

## 審計修正紀錄

- r1（2026-09-08，5 席：正確性／邊界／接手／架構對齊／外家 Codex）：34 條（外家 6、正確性 5、接手 9、邊界 12、架構對齊 2；blocker 5 條全折）；同題合併後折入：表態改成獨立原語在派席前寫（解 skip 逃生／派工時不存在／最後一次 pass 無人反駁）、閘條件改「有適用題就擋」不看 tier、CI 從治理帳重建含表態並改讀側 schema、錨點對 at_sha 樹驗、多平台索引、原文對照、原子寫入、鏡頭快取 key、gov mapper 放行、fail-open kind、S7 保留 standard 語意改寫、todo 門檻拉齊、理由門檻分 ASCII、path:line 切分規則、status 小寫訊息、零命中印 `{}`、BLOCKED 截斷、docs/ 缺席訊息、config 壞掉判法、效能檢核目錄 KEY 行、旗標吃路徑；數字訂正 0→5/177；接受 2 件（架構對齊 A2 三值詞彙 vs 處置閘二值：語意本來就三元；邊界 B10 Python 不在表：另案）。卷證 `governance/review-reports/棧別提問表態閘/r1-*`。

REVISIT:2026-10-08 看留痕帳裡 satisfied/na/todo/auto-na 的分布：人工表態 na 佔比 >70% 代表被敷衍或題目不對，回頭裁「加嚴」還是「刪題」；auto-na >90% 且 recall-miss 有帳代表觸發太窄，修 when。
