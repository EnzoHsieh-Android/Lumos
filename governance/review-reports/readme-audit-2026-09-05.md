# README 機制與強制力宣稱——外部稽核報告(2026-09-05)

稽核方法:讀原始碼(`scripts/lumos`、`scripts/hooks/*`)、跑真指令(`lumos doctor/guard list/enforcement`)、翻本機帳本(`~/.claude/projects/*/.jsonl`、`governance/logs/*.log`、`governance/pending/`、git log)、讀知識圖譜裡的自我體檢筆記。不採信文件對自己的描述,每條結論附可重現的證據來源。

判定代號:①名副其實 ②言過其實 ③空轉 ④邏輯不自洽

---

## 1. 「收工 Stop hook:Claude 只提醒」

**宣稱**(README §5 表格、§3b):「收工 Stop hook:這一輪改了 code、筆記沒動就點名——Claude 只提醒;Codex 同 session 擋一次」。

**證據**:
- `scripts/hooks/claude/check-graph-sync.py:699-700`:Claude 路徑執行 `print("\n".join(msg), file=sys.stderr); return 0`——固定印到 **stderr**、固定 `exit 0`。程式碼自己的註解(檔案開頭第 6 行)寫「Claude 側:軟提醒(**stderr surface 給 Claude**)」。
- 官方文件(`code.claude.com/docs/en/hooks`,WebFetch 查證):Stop hook 的行為表明確寫「stdout 寫進 debug log、不進 transcript」,且「**Stderr on exit 0 goes only to the debug log**,never visible to Claude or in the transcript」——即 exit 0 時 stderr **不會**餵給模型,也不進人看得到的 transcript,只進除錯日誌。
- 實測(`~/.claude/projects/-Users-enzo-harness-lumos-toolchain/*.jsonl` grep「通常要跟著改的是」):命中 5 份逐字稿、共 11+ 次觸發。每一次都以 `type:"attachment", attachment.type:"hook_success"` 形式寫入逐字稿檔(供人日後翻閱用),**但緊接在後的下一筆記錄無一例外是使用者訊息或 task-notification,從未出現助手主動回應/引用這條提醒的文字**——抽樣 11 次觸發全部如此。

**判定**:②言過其實。程式碼自己的註解就寫錯了(「stderr surface 給 Claude」與官方文件矛盾),而 11 次實測全部印證官方文件——模型從未看到、也從未對這條提醒做出反應。README 用「提醒」一詞暗示 AI 至少收到訊號、有機會自己補筆記,但實際上這條 stderr 只落進除錯日誌,連人不特別去查 transcript JSONL 都看不到,更別說模型。真正在守的只剩「人事後自己想到去翻」這一層,跟「Codex 會擋一次逼它續做」完全不是同一個強度,而 README 把兩者並排寫在同一張表格裡,讀者容易誤會兩邊都至少「有東西被看到」。

---

## 2. 「pre-commit 擋『改 code 沒帶圖譜』」

**宣稱**:README §5「提交 ── pre-commit 擋『改 code 沒帶圖譜』」。

**證據**(`scripts/hooks/pre-commit:148-155`):
```
[[ ${#src_files[@]} -eq 0 ]] && exit 0                                    # Gate 2:沒 code → 放行
if echo "$STAGED" | grep -qE "^${GRAPH_ROOT}/.*\.md$"; then               # Gate 3
  sync_nudge staged
  exit 0
fi
```
Gate 3 的判準就是字面上「有沒有任何一篇圖譜 `.md` 檔一起 staged」——不檢查改的是不是相關的那一篇。`sync_nudge`(呼叫 `lumos impact --diff staged --sync-only`)會把「跟你動的 code 直接相關卻沒動」的筆記點名,但那只印到 stderr、緊接著 `exit 0`,**不影響是否放行**。

**判定**:①名副其實(就字面「有沒有帶圖譜」而言),但有重要但書。這是設計者自己清楚意識到的取捨——程式碼註解直接寫「動過圖譜不等於動對篇」,並用 `sync_nudge` 這道軟提醒去補這個洞,不是無意的漏洞。如果讀者從 README 這行字推論「pre-commit 會驗我動對了正確的筆記」,那就是誤讀;它只驗「有沒有動任何一篇」。

---

## 3. 「code-loop:高風險改動沒過代碼審,push 時硬擋」/「anchor approve 同理」

**宣稱**:README §5「code-loop | 高風險改動沒過代碼審 | push 時硬擋」;§7「lumos code-loop check|pass|skip # 高風險改動的代碼審留痕(pre-push 會查)」。

**證據**(`scripts/lumos:17925-17958` `cmd_code_loop`):
```python
if subcmd in ("pass", "skip"):
    status = "passed" if subcmd == "pass" else "skipped"
    _codeloop_write(repo_root, branch, status, note or "", head_sha, ts)
    _codeloop_gov_log(repo_root, branch, status, note or "", head_sha, ts)
    ...
    return 0
```
`pass`/`skip` 子命令**只寫入一筆自報紀錄**(留痕檔 + 治理帳),不驗證是否真的跑過 design-loop/code-loop 的審查迴圈、不查 `loop status --disposal` 有沒有真的 PASS 過、不檢查有沒有任何審查席報告存在。`check` 子命令(`scripts/lumos:17855-17921` `_codeloop_guard_verdict`)的判定邏輯只有:tier=high 且「留痕 sha == 目前 HEAD sha 且狀態是 passed/skipped」→ 放行。也就是說任何人在正確的 commit 上執行 `lumos code-loop pass --note "看過了"` 就能拿到通過 push 的憑證,工具端沒有任何機制反查這句話是不是真的。

圖譜自己也承認同型限制:`Verification/2026-07-16_dloop提效M2_cluster帳.md`:「cluster 歸併與三態標定仍是編排者自報(GIGO);accepted-minor 理由內嵌是機械格式強制,**理由內容真實性不驗**」。

`anchor approve`(`scripts/lumos:12713` `cmd_anchor_approve`)是同一種模式:重算錨點檔 sha256、要求帶 `--note`,寫回 baseline——它是文件自稱的「改錨點檔唯一合法路徑」,同樣不驗證改動本身有沒有經過審查,只要求留一句話。

**判定**:②言過其實。「push 時硬擋」這句話技術上真——沒有任何 `passed/skipped` 紀錄確實會被 pre-push 擋下(`scripts/hooks/pre-push:126-140`)。但「代碼審」三個字暗示的是「真的有人/AI 審過」,工具實際強制的只是「有沒有人打過這行指令」,兩者之間沒有機械連結。憑證本質是自陳,不是審查結果的證明。

---

## 4. 「判定凍結每週回放」「每天自動跑一輪」「情境探針」是否真的排程在跑

**證據**:
- `launchctl list | grep lumos` → `com.enzo.lumos.daily-governance` 確實在跑(plist:`~/Library/LaunchAgents/com.enzo.lumos.daily-governance.plist`,`StartCalendarInterval` 09:30)。
- `governance/logs/daily-wrapper.log` 有從 2026-08-21 到 2026-09-05(今天)**連續每天**的執行紀錄,`daily-governance.sh` 依序跑治理日報→自主迭代 loop(`--dry-run 6`)→lint-watch→`doctor --ci`,四段皆 rc=0。
- 週回放(`governance/autonomous_loop/replay_weekly.py`)、情境探針(`scripts/scenario_probe.py`)、機制空轉週報(`gov --nags`)都是掛在同一支每日 wrapper 內、用 `.weekly-stamp`/`history.jsonl` 的 ISO 週號自己節流成「每週一次」——不是獨立的 cron/launchd 項目,但真的有在跑:`governance/replay/.weekly-stamp` 內容為 `2026-W36`(今天日期 2026-09-05 算出的 ISO 週正是 `2026-W36`),`governance/logs/autonomous.log` 逐日顯示「情境探針:本週已抽過,跳過」「回放週跑:本週已跑」。
- **但「自主迴圈每天跑一輪、挑缺口→寫設計→停在等人放行」這條的產出率極低,且產出的東西從沒真的離開過本機**:
  - `governance/autonomous.log` 逐日印出的「過去 7 天」統計,從 08-26 到 09-04 **連續十天,收斂數全部是 0**(例:「過去 7 天:跑 8 次、燒 $274.08、收斂 0、備好待放行 0、管線死 1」)。
  - `governance/pending/`(存放「收斂、待人放行」spec 的目錄)目前是空的;`governance/pending/archive/` 史上只有 2 個檔案,都是 2026-07-14 的(`corrosion-gauge.md`、`corrosion-gauge-confidence.md`)。
  - 那份 corrosion-gauge 設計從未真的落地:`find . -iname "*corrosion*"` 找不到任何實作檔(`governance/autonomous_loop/corrosion.py` 不存在),`git log --all --grep=corros` **零筆**。
  - 讀 `governance/autonomous-loop.sh:555-576` 才發現關鍵:daily wrapper 呼叫的是 `autonomous-loop.sh --dry-run 6`,程式碼裡真正會 `git checkout -b`、`git commit -m "auto-spec: ..."`、`gh pr create` 的分支只在 **非** dry-run 模式才執行——而生產環境**只掛了 dry-run 這一條路**,dry-run 分支只把 spec 複製進 `governance/pending/`(此目錄整個被 `governance/.gitignore` 排除,不進版控)。
  - 佐證:`git log --all --oneline --grep="auto-spec"` **0 筆**;`git branch -a | grep auto` **0 筆**;`gh pr list --search "auto-spec"` **0 筆**。也就是說,README 圖裡畫的「AUTO」節點聲稱的「寫設計 → 走同一條路 → 停在等人放行」,那條「走同一條路」開 PR 給人審的生產路徑,在這個 repo 有史以來**從未執行過一次**——所有「放行」動作(如果有)都只發生在一個不進版控、單機可見的資料夾裡,而且現在是空的。

**判定**:①③混合。「每天自動跑一輪」①名副其實,有真實 launchd 排程、真實花錢的 API 呼叫,logs 逐日可查。但「停在等人放行」這句話背後隱含的「有一個持續產出、等人簽字的佇列」在近十天的觀測窗裡③空轉——收斂 0 次、pending 佇列是空的、歷史上僅有的 2 份產出沒人記錄「放行」動作也沒被實作,而且**生產級的開 PR 路徑本身從未跑過**,只是程式碼裡寫著、cron 卻只餵 dry-run 參數。花費不小($270~330/週,見下方成本節),近十天內對應到 0 個實際交付。

---

## 5. 「派工時自動附節點,審查員不用自己翻」

**宣稱**:README §5 心智圖「LENS:派工時自動附節點——相關的規則與事故附進派工單,Claude 改派工單 · Codex 開場自領」。

**證據**:
- `Verification/2026-09-04_主session鏡頭利用率第一份報表.md`(唯讀量測,`governance/eval/lens-utilization/recount.py`):主 session 三週共 44 次注入,扣掉空/對不到錨點/scratch 後分母 33。**只釘 1 篇筆記的那型(16 次),高信心判準下 0/16 有被讀過**(啟發式加寬後仍只 2/16);**code 檔的推送 11 次只被讀過 0~1 次**;「11+ 篇」型雖然 7/13~10/13 有碰,但報表自己說明「那 13 次全是改 test_lumos.py,session 本來就在跟那些筆記打交道」,並非鏡頭的功勞。報表自己下的結論是「推送發生率低——三週 44 次,全在 4 個走 Edit 工具的 session」。
- `Verification/2026-09-03_派工鏡頭注入驗收.md`(針對「派工單附節點給審查員」這支機制,即 README 這句話真正指的 `dispatch-lens-hook`):驗收只測「有沒有正確附上去、會不會被當成注入攻擊拒答」,誠實界線一欄寫明:「**『有沒有用』沒驗,依 Enzo 裁定不驗;採用率 REVISIT:2026-10-03**」。

**判定**:②言過其實。附加機制本身確實存在且技術上正確運作(有消毒、有單元測試),但「審查員不用自己翻」暗示的效果——附上去的東西真的被讀、真的省了審查員翻圖譜的力氣——目前**沒有任何量測支持**,唯一做過的量測(主 session 版本的類似機制)顯示利用率很低,而審查席版本的利用率**被明確裁定不驗**、且截至今天(2026-09-05)REVISIT 日期(2026-10-03)尚未到。

---

## 6. 「每條意見都有交代才過關」

**宣稱**:README §5 心智圖「每條審查意見都要有交代(採納就改稿、不採納要寫理由),一輪全部有交代才過關」。

**證據**(`Projects/收斂閘漏項敏感度_計劃.md`,狀態 superseded,但問題陳述被 v2 承接):
> 「收斂閘只驗『你列的都處理完了』(自洽),不驗『該列的都列了』(覆蓋);`findings_set` 是編排者自己打進 CLI 的字串,寫入端(`cmd_canary`)有機械檢查,但檢查的全是三個集合彼此自洽(折∪放行==全部、折∩放行==空、放行理由齊)——**沒有任何一項把 `findings_set` 的內容拿去跟一個外部來源比對**。」

該筆記引用兩篇外部論文(arXiv 2608.31016、2608.01000)獨立量到:AI 判官抓「多出來的東西」判別力 0.79–0.94,抓「漏掉的東西」只有 0.50–0.63(近擲硬幣),且「換措辭/多席投票/提示詞優化全部無效」。

**接手案** `Projects/收斂閘漏項敏感度v2_計劃.md`(`status: doing`,今天 2026-09-05 仍在進行中,尚未有結論)正在設計一套實測(M1 復原率)來量化這個洞到底有多深,目前**還沒有答案**。

**判定**:②言過其實。README 這句話講的是「有交代」的那一半(折入或給理由),這一半機械上確實會查(`cmd_canary` 的三個集合自洽檢查是真的、違反會 rc2 擋);但沒講清楚「有交代」跟「該提的都提了」是兩件事,後者完全沒有機械把關,連圖譜自己都承認、正在立案量測、且尚未有結論。讀者容易把「每條意見都有交代」腦補成「審查不會漏掉東西」,那個推論目前沒有證據支撐。

---

## 7. 「doctor 22 道、`--ci` 會擋」

**證據**:
- README.md 本文其實**沒有**寫「22 道」這個數字(全文搜尋「22」在 README.md 裡 0 命中);「22 道」出現在內部方法論文件 `docs/methodology/圖譜即合約.md`、`圖譜即合約-全景圖.md`,且全景圖第 41/104 行的小標題本身就寫「檢查員定期巡查(22 道;**大多只提醒,少數硬擋**)」——這句話本身就沒有宣稱「22 道都擋」。README.md 自己只在 §5 表格寫「`lumos doctor` | 全圖健檢 | `--ci` 模式會擋」,沒有給數字,字面沒錯但沒說清楚「擋」只是一部分檢查的行為。
- 直接讀 `run_doctor()`(`scripts/lumos:747-1875`),數 `section(...)` 呼叫,共有 **29** 個獨立區塊(1/4、1.5/4、2/4、3/4、4/4、G、L、M、C、T、R、S、S2、I、E1、E2、E4、E5、E3、H、K、D、V、P、Y、N、J、W、F);其中 J、W 是條件式區塊(規重生節點存在 / 非源 repo 時才顯示),常態下可能看不到。
- 用 `warn()`(計入 `issues`,`--ci`/`--strict` 時 `issues>0` → `return 1`,真的會讓 rc 非 0)的區塊:1/4、1.5/4、2/4、3/4、4/4、G、L、M、C、T(5 條子檢查)、R(僅 `rev_err` 那半)、I(僅「缺席」那半)、D(僅 sentinel 損壞/不同步/超長那半)、J(僅 `j_err_lines`)、F(含「沒接 linter」一句,但該呼叫傳空清單,對 `issues` 貢獻恆為 0)——粗估約 13~14 組**可能**觸發硬擋。
- 用 `warn_soft()`(明確「提醒,不擋」,不計入 `issues`)的區塊:R 的另一半、S、S2、E1、E2、E4、E5、E3、H、V、P、Y、N、J 的另一半、W——約 15 組。
- 本 repo 實跑 `lumos doctor --verbose`(2026-09-05):列出 ⚠ 的有 S、S2、E4、E5、E3、P、N、F 共 8 段,但**最終「✓ 圖譜健康 — 0 issues」**——即這 8 段全部是軟性 `warn_soft`(或 F 那個空清單的邊角案例),當下沒有任何硬擋條件被觸發。

**判定**:①名副其實,但需要補一句才完整。README.md 本身沒有寫死「22 道」也沒有宣稱「22 道都會擋」,反而是內部文件自己標題就寫明「大多只提醒,少數硬擋」——比對到程式碼,這句自我描述比 README 簡表更準確。真正的落差在「22」這個數字本身跟目前程式碼的實際區塊數(29,含 2 個條件式)對不太上,可能是文件更新滯後於程式碼演進(該行文件自己標註「2026-09-05 更新」,即今天才剛改過,可能統計口徑跟我用 `grep section(` 數的不同,例如把 1/4~4/4 算成一組)。

---

## 8. ★INVARIANT★ 必須綁測試、doctor 會擋——實際覆蓋

**證據**:
- `lumos guard list` 與 `lumos doctor` 的 [T] 檢查一致回報:「合約 23 條 — 真綁 23 / 懸空 0 / 偽證據 0 / 裸 0 / 未審 0」。
- 直接 `grep -rE "KEY:★INVARIANT★" docs/lumos-toolchain-knowledge` 找到 35 筆,比 23 多——追查後確認落差是**假警訊**:多出的 12 筆全部是「正文裡討論/舉例這個標記語法」的散文(例如設計計劃裡貼一段測試碼字串 `assert _impact_contract(note_with("KEY:★INVARIANT★ x [test:t]"))`、或討論消毒規則時引用範例),不是活的合約宣告。doctor/`guard list` 的解析器**只認 frontmatter 的 `summary:` 欄位裡的 KEY 行**,正文一律不掃(圖譜自己在 `Projects/節點還原SOP_計劃.md` 也明寫這條:「Check J 只掃 frontmatter 的 summary 行,正文不掃」)——排除這 12 筆假警訊後,剩下 23 筆全部落在 9 篇 `Systems/*.md`,每筆都有 `[test:xxx]` + `[audit:model/日期]`,且測試方法名逐一比對過(`guard list` 的「已綁真方法」逐條列出)。

**判定**:①名副其實。這是稽核中發現機制最紮實的一條——23 條活合約全部綁了存在且可執行的測試方法、全部過了獨立審計,0 例外。「必須綁測試、doctor 會擋」在這個 repo 目前狀態下完全兌現。

---

## 9. 成本量測——README 有沒有講清楚燒多少

**證據**:
- README.md 唯一提到成本的地方是 mermaid 圖裡「觀測帳:附的節點有沒被用‧被舊決定擋幾次‧**每支迴圈燒多少**」這一句,沒有給任何數字或指向哪裡查。
- 但成本**真的有在量,而且量出來的數字不小**:
  - `governance/logs/autonomous.log` 每次 orchestrator 跑完都印一行「本輪成本:US$xx.xx | xx 分鐘 | xx 輪 | xx tokens」,且每天彙總「過去 7 天:跑 8 次、燒 $274.08…」——近十天穩定在每週 $270~330 之間,對應到收斂 0 次(見第 4 條)。
  - 今天(2026-09-05)剛落地一份專門的成本基線筆記 `Verification/2026-09-05_skill-doctor成本基線.md`:用 Claude Code 2.1.261 新指令 `/skill-doctor` 量到「7 天:`lumos-code-loop` 930 萬 token / 49 次(平均約 19 萬一次)、`lumos-design-loop` 300 萬 / 56 次(約 5 萬一次)、`lumos-project-notes` 130 萬 / 239 次(約 5 千一次)」,並誠實記下界線(「7d tokens 官方沒寫怎麼歸因」「只量一台機器一週」「數字是手機翻拍截圖人工抄的」)。

**判定**:①③混合看角度。就「有沒有在量」而言①名副其實(量測機制真實存在、今天才剛新增一份、logs 逐日可查);但就「README 有沒有把這件事講清楚」而言算資訊揭露不足——沒有給讀者任何量級概念,而實際量級(近十天 $270~330/週的自主 loop,對應 0 次收斂交付;代碼審一次均值 19 萬 token)是會影響一般人「要不要開這個自動迴圈」判斷的關鍵數字,卻完全沒有出現在 README 或任何面向外部讀者的文件裡,只藏在本機 log 和今天剛寫的一篇圖譜筆記中。

---

## 10. 其他發現的「文件內部/跨文件矛盾」

1. **程式碼註解與官方文件矛盾**(呼應第 1 條):`check-graph-sync.py` 檔頭註解自稱「Claude 側:軟提醒(stderr surface 給 Claude)」,但 Claude Code 官方 hooks 文件與本次逐字稿實測都證明 exit 0 的 stderr **不會**送給模型。這不是 README 的問題,是原始碼自己對自身行為的描述就是錯的,而 README 的表格照搬了這個錯誤前提。
2. **README 的「22 道」與程式碼實際區塊數對不上**(第 7 條):內部方法論文件今天(2026-09-05)才更新這個數字,但獨立用 `grep "section("` 數出來是 29 個區塊(含 2 個條件式)。不確定差距是統計口徑不同還是文件滯後,但數字本身經不起機械複驗這件事,恰好呼應圖譜自己 [N] 檢查那天(今天)抓到的另外兩個真實數字漂移案例(`Projects/graph-engineering掃描2026-08-19_調研.md` 宣稱 187 實測 206;`Projects/閘觸發帳統計_計劃.md` 宣稱 21 實測 22)——這反而是佐證:圖譜自己承認「數字會漂」是常態,不是特例。
3. **「自主迴圈」在 README 的心智圖裡跟「code-loop pass」共享同一種「自報即通過」模式,但強制力被畫成完全不同層級**:README 表格把「code-loop」畫成「push 時硬擋」(看起來很硬),把「自主迴圈」畫在最外圈的「觀測/跑它」(看起来只是背景設施)。實際上兩者都存在「機器只驗有沒有一筆自報紀錄,不驗紀錄內容真實性」的相同結構性洞,只是前者至少有 pre-push 真的擋、後者現在連「開 PR 給人看」這條路徑都沒被實跑過。README 的呈現方式讓讀者對兩者的信任度產生不對稱的錯覺。
4. **「良性循環」mermaid 圖畫的是理想閉環,但本次查核的 3 條資料鏈(鏡頭利用率、收斂閘覆蓋率、自主迴圈產出率)目前實測值都偏低或掛零**——不代表設計不對,但 README 把這張圖放在「日常怎麼用」這種偏「現況說明」的章節,而不是放在「願景/正在驗證中」的章節,容易讓第一次看的人誤以為這是已經跑順的常態,而不是一個仍在自我量測、多處承認「還沒驗過有沒有用」的實驗性子系統。

---

## 總結(給沒空看全文的人一句話版)

- 兩層機械把關做得紮實、經得起查:**INVARIANT↔測試綁定**(第 8 條,23/23 全綁)、**pre-push 三合一硬擋**(anchor+test+doctor,第 3 條佐證)。
- 三層「聽起來是強制,實際是自報」:**收工提醒對 Claude 根本不可見**(第 1 條,不是弱化是失效)、**code-loop/anchor 的通過憑證是自己打字就能拿到**(第 3 條)、**收斂閘只驗自洽不驗覆蓋**(第 6 條,官方自己在查,還沒有答案)。
- 兩個「派工自動附料」與「自主天天迭代」的機制**技術上真的在跑,但產出效益目前量到的數字很小甚至掛零**(第 5、4 條),且相關「有沒有用」的驗證被明確裁定延後或還在進行中——這是誠實揭露不足,不是憑空捏造。
- 成本是真金白銀在燒且圖譜今天才第一次量出量級(第 9 條),README 完全沒提數字。
