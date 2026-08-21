# C — CLI 表層審計（`scripts/lumos`，61 個頂層子命令）

方法論：`docs/.usage-log.jsonl`（166 行，全機）只記 `context`/`show` 兩種讀取命令，其餘一律沒有機器級「這條命令被叫過幾次」的帳。改用四種代理證據交叉：① `lumos gov --stats` 讀 `.governance-log.jsonl`（20566 行,唯一真被 hook 動過的帳）② `.canary-log.jsonl`（487 行）③ `git log` 訊息命中數 ④ `grep -rc "lumos <cmd>"` over `skills/ CLAUDE.md`（是否被教過）。四者沒有一個是「使用次數」的正確代理，只能疊出「有沒有留下任何痕跡」的下界。

## 0. 全域數字先攤

- `lumos --help` 本文 **9147 字元**（純子命令清單+一段兩行說明；每個子命令一行中文簡述,無範例、無「先讀哪個」的順序提示）。
- `docs/.usage-log.jsonl` 166 行,只有 `show`(91) `context`(75) 兩種——**其餘 59 個子命令,這條帳完全看不到**（不是零使用,是零記帳:這條 log 本身只在 `cmd_context`/`cmd_show` 埋了 `_log_usage`,其它子命令沒接線）。
- `gov --stats` 揭示的閘帳只有 9 種 gate 名:`L2`(61) `anchor-approve`(145) `canary`(487) `check-e1`(703/1752) `check-s`(7407/18583) `ci`(25) `code-loop`(79) `doctor-run`(2) `signoff`(8)；`未出現的 gate(7): L3, check-e2, check-e3, check-j, check-k, check-r, kill`——這 7 個連「有沒有被動過」的帳都進不了(gov 工具自己註明「未出現 ≠ 無用,也可能是沒接線」)。

## 1. Git hook 實際「硬闖」的只有 4 個子命令

讀 `scripts/hooks/pre-commit` `scripts/hooks/pre-push` `.github/workflows/ci.yml` 逐行:

| 子命令 | hook | 阻擋方式 | 證據 |
|---|---|---|---|
| `doctor --ci` | pre-push, CI | **硬擋**(exit≠0 擋 push) | `scripts/hooks/pre-push:148` `if "$PY" "$GRAPHCTL" doctor --ci; then exit 0; fi` |
| `anchor verify` | pre-push, CI | **硬擋**(exit≠0 擋 push) | `scripts/hooks/pre-push:38` `if ! "$PY" "$GRAPHCTL" anchor verify; then` |
| `code-loop check` | pre-push | **條件硬擋**(僅當 `pitfalls --diff` 判 tier=high 且推向 `refs/heads/*` 才觸發;非分支 ref 全 advisory) | `scripts/hooks/pre-push:107-119` |
| `pitfalls --diff` | pre-push | 純 advisory(印出來,`\|\| true`;只是 code-loop 的觸發器) | `scripts/hooks/pre-push:98-134` |

pre-commit 掛的兩個子命令**全部 `\|\| true`,永不擋 commit**——`cochange check --staged`(`scripts/hooks/pre-commit:48`)、`delguard --staged`(`scripts/hooks/pre-commit:57`)。真正擋 commit 的 Gate 1/2/3 是**純 bash 字串比對**,不呼叫任何 `lumos` 子命令。

即:**61 個子命令裡,真正機械阻擋人類/Claude 動作的只有 `doctor`(--ci) 和 `anchor`(verify)兩個,外加一個條件式的 `code-loop`(check)**。其餘全部是「印出來,靠 Claude 自己記得看、記得聽話」——CLAUDE.md 自己也承認這點(design-loop 節點原句:「硬閘是紀律非技術鎖,lumos 擋不住『不跑就實作』」)。

Claude Code 側的 PreToolUse hook 是例外的真自動注入:`scripts/hooks/claude/impact-hook.py` 在 Edit/Write 前 subprocess 呼叫 `lumos impact --file <path> --json`,輸出真的會被注入 Claude 的 context(這條路徑可信,不靠人看 stdout)。`ci-status-hook.py` 同理但只在主路徑漏跑時補位提醒。

## 2. 從未被任何 skill / CLAUDE.md 真教過的命令

`grep -rc "lumos <cmd>\b" skills/ CLAUDE.md` 得零的有 11 個:`ci-status decision-reindex deinit delguard drift-history export link-candidates map rel-cascade remove teardown`。

但這組要再切一刀——`skills/lumos-project-notes/reference.md:86` 有一整段「61 個頂層命令全覽」,把全部 61 個命令名字都提了一次(逗號隔開的清單),沒有語法、沒有範例、沒有「何時用」。扣掉這行純報數的提及後:

- **真的連名字都只出現這一次、沒有第二處任何教學/範例的 8 個**:`ci-status` `decision-reindex` `deinit` `drift-history` `link-candidates` `rel-cascade` `remove` `teardown`。
- **有一行真範例但沒被寫進「教學路徑」的 2 個**:`map`(`reference.md:59` 表格一行 `map <筆記名> --depth 2`)、`export`(同表格 `export --folders Systems Projects`)——比前一組好一點,但都不在 CLAUDE.md 的「入口三步」或任何 skill 的主敘事裡,一個沒讀過 reference.md 全文的 Claude 撞不到。
- **`delguard` 是特例**:CLI 語法上不教(它不是給人手動打的命令,是 pre-commit 內部 `--staged` 自動呼叫的 advisory 掃描器),但機制本身有文檔(`SKILL.md:252`)、有 Verification(`2026-08-11_delguard落地.md`)、有真實 pre-commit 掛載——**不是虛設,是「本來就不該教手動用法」的命令被我的教學計數法誤傷**。

這 8+2 個命令裡,拿實際留痕再篩一次:

| 命令 | 有無真實留痕 | 證據 |
|---|---|---|
| `rel-cascade` | **有**,但極稀有(2 次) | `governance/rel-cascade/c-20260804063546-*.jsonl`、`c-20260811044607-*.jsonl` 兩個真帳檔,對應 rel-mainnet 專案兩次真跑;`scripts/slim-scan.py` `scripts/slim-gen.py` 有程式碼呼叫點 |
| `deinit` | **有**(git 訊息 28 命中,含真實 teardown 場景) | `git log --oneline --all \| grep -ic deinit` = 28 |
| `teardown` | 有(7 次) | 同上 grep = 7 |
| `map` / `export` | 有(6/4 次) | 同上 |
| `link-candidates` | 有,對應 2026-07-10/2026-08-07 兩次真落地 | `docs/lumos-toolchain-knowledge/Verification/2026-08-07_連結缺失補全落地.md` |
| `drift-history` | 有,兩份 Verification 引用 | `2026-08-12_通用性修正...md`、`2026-08-21_L4交叉審計30節點清帳.md` |
| `ci-status` | 弱(1 次 git log),但有 hook 掛載(`ci-status-hook.py`) | 命令本身很少被人手動打,主要靠 hook 觸發 |
| `decision-reindex` | **零** git log 命中、零governance帳,只在計劃文件裡被提及當「未來要做」 | `grep -c "cmd_decision_reindex" <(git log --all -p -- scripts/lumos)` 只抓到函式本身的 diff(19 次程式碼改動),沒有任何「執行紀錄」證據 |
| `remove` | 有測試覆蓋(`scripts/test_lumos.py:555-622` 六個 `run(v,"remove",...)` 案例),但無生產留痕帳(它是純量欄位撤銷操作,本來就不記帳) | — |

**淨結論**:8 個「零教學」命令裡,7 個其實有真實使用痕跡,只是散落在 git log / Verification 文件,沒有被收進任何「你該用這個」的教學路徑——這是文檔缺口,不是死代碼。唯一接近「真虛設」的是 `decision-reindex`(見下方缺陷 4)和 `canary second`(見下方缺陷 3)。

## 3. 主表(mechanism = 頂層子命令;61 列全覆蓋)

圖例:enforcement 硬=git hook/CI 阻擋、軟=hook 自動呼叫但 `\|\| true` 不擋、prose=純靠人/Claude 記得手動叫。fires 一欄的數字來源標於括號內(gov=governance-log 帳、canary=canary-log 帳、git=git log 訊息命中、skill=skill/CLAUDE.md 教學命中數)。

| 命令 | 一句話用途 | enforcement | fires?(證據) | 到得了 Claude? | 裁定 | 修法(一行) |
|---|---|---|---|---|---|---|
| doctor | 圖譜四檢查+~20 個 Check 字母子檢查 | **硬**(--ci, pre-push+CI) | gov: doctor-run 僅 2 筆,但 check-s/check-e1 等子檢查帳合計 26k+ 筆(doctor 是母體) | 是(pre-push stdout 同輪可見) | 保留 | 把 ~20 個 Check(M/C/T/R/S/E1/E2/E3/H/K/D/N/Y/J/U…)列進 `doctor --help`,現在完全查不到有哪些檢查,要讀 15K 行源碼才知道 |
| links | 連出節點 | prose | skill:1 | 手動讀才到 | 保留 | 無 |
| backlinks | 連入節點 | prose | skill:5 | 手動讀才到 | 保留 | 無 |
| context | 節點+鄰居壓縮索引 | prose(但是 CLAUDE.md 入口三步之一) | usage-log:75(唯一被記帳的兩命令之一);skill:12 | **是**,是圖譜先行的官方入口 | 保留 | 無 |
| show | 節點完整內容 | prose | usage-log:91(比 context 還高);skill:3 | 是,靠人/Claude 手動叫 | 保留 | skill 主敘事該補一句「比 context 更完整時用 show」——目前 CLAUDE.md 入口三步沒提它,但實際使用量比 context 高,文檔與行為脫節 |
| contracts | 合約登記簿 | prose(CLAUDE.md 入口三步之一) | skill:4 | 是 | 保留 | 無 |
| lint | 單檔快檢 | prose,寫節點後自驗 | skill:11 | 是 | 保留 | 無 |
| gov | 唯讀治理事件帳(本次審計主要證據來源) | prose | skill:4;工具本身剛加 `--stats`(本週新功能) | 是,人主動查才到 | 保留 | 無 |
| canary | 對抗審計植入留痕(record/second) | prose | canary-log:487(caught 337/none 83/missed 67);**`second` 子模式 0 筆** | 是 | **修** | `second`(第二判者覆核)自 2026-08-14 canary 協議停用後從未被叫過一次——要嘛真的接上 loop 流程要嘛砍掉這個子命令,現狀是宣告了沒人用的旗標 |
| loop | 收斂查詢(status/compress/verify-progress/next/canary-stats/capture-counts) | prose,design-loop/code-loop 骨幹 | canary-log 依 loop 分組:top loop 19-15 筆量級,長尾多為 3-9 筆(見下) | 是 | 保留但精簡子模式(見§4) | `loop status` 的 6 種模式(legacy/--gate/--panel/--light/--settle/--disposal)要在 --help 明講哪個現行、哪個 legacy |
| guard | 合約守衛 scaffold(list/scaffold/bind/audit/trace/kill/kill-add) | prose | skill:16 | 是 | 保留 | 無 |
| spec-trace | 條款級追溯 RTM | prose | skill:4 | 是 | 保留 | 無 |
| signoff | 業務簽核留痕 | prose | gov: signoff 8 筆(2026-07-18~2026-08-08) | 是 | 保留 | 無 |
| sync-verified-by | 補 Check 3 漏寫 verified_by | prose,dry-run 預設 | skill:3 | 是 | 保留 | 無 |
| search | 全文搜尋 | prose(入口三步第一步) | skill:11 | 是 | 保留 | 無 |
| map | 鄰域樹狀展開 | prose | git:6;skill 表格 1 行範例,無「lumos map」字面教學 | 弱(要讀到 reference.md:59 那行表格才知道) | 保留 | CLAUDE.md 入口三步該提一下 map 跟 context 的差(map=結構樹,不含內容) |
| decisions | 讀 ADR 決策 | prose | skill:5 | 是 | 保留 | 無 |
| stale | stale 驗證/風險排序掃描 | prose | skill:8 | 是 | 保留 | 無(功能上與 doctor 不重疊,doctor 沒有風險加權排序邏輯) |
| query | 結構化 WHERE 查詢 | prose | skill:5 | 是 | 保留 | 無(CLAUDE.md 已明文分工:「找『講到詞』用 search;篩『欄位條件』用 query」,不算重疊) |
| recent | 最近 N 天修改 | prose | skill:4 | 是 | 保留 | 無 |
| stats | 資料夾統計 | prose | skill:2 | 是 | 保留 | 無 |
| export | mermaid/dot/html 輸出 | prose | git:4;同 map,只有一行表格範例 | 弱 | 保留 | 無(低頻本來就合理,是視覺化工具不是每日命令) |
| set | 改純量欄位 | prose,寫入鐵則之一 | skill:11 | 是 | 保留 | 無 |
| append | list 欄位追加 | prose,寫入鐵則之一 | skill:8 | 是 | 保留 | 無 |
| drift-history | 沿 git 歷史重放符號存在性 | prose | 只在總覽行提過;git 無直接命令行命中,但 2 篇 Verification 引用其分析結果 | 弱(結果進了圖譜,但命令本身沒人教怎麼叫) | 精簡 | 併入 `doctor` 的一個診斷旗標,或至少在 reference.md 給一行範例,現狀=「有用過,但只有作者自己知道怎麼叫」 |
| remove | list 欄位移除 | prose,append 逆操作 | 只在總覽行提過;測試覆蓋 6 案例(`test_lumos.py:555-622`) | 是(功能小,靠文檔字面即可猜到用法) | 保留 | reference.md 補一行用法(目前完全沒有独立範例,append 有) |
| self-audit | L4 自足性審計留痕 | prose | skill:2 | 是 | 保留 | 無 |
| new | 依模板建檔 | prose | skill:6 | 是 | 保留 | 無 |
| decision-supersede | 翻盤決策 | prose | skill:2 | 是 | 保留 | 無 |
| decision-reindex | 決策編號回填遷移 | prose | **只在總覽行提過,git log 對命令本身 0 命中,governance 帳 0 命中** | 弱到近乎到不了 | **砍或修** | 這是「decision_refs 養成前置」的一次性遷移工具,遷移窗口(P2)大概率已過——查清是否還有 legacy 節點缺 id、沒有就砍;有就補一行「何時該再跑」 |
| rel-cascade | 連鎖判定帳本 | prose | governance/rel-cascade/ 兩份真帳(2026-08-04, 2026-08-11);`slim-scan.py`/`slim-gen.py` 程式碼呼叫點 | 是,但只在特定專案(rel-mainnet)脈絡下 | 保留但補教學 | 只在總覽行提過,實際是有真用途的機制,該補進 reference.md 主敘事而非清單尾巴 |
| decision-add | 新增 ADR 決策 | prose | skill:6 | 是 | 保留 | 無 |
| install | symlink 全域 | prose,一次性安裝 | skill:2 | 是(安裝時) | 保留 | 無 |
| uninstall | 移除 symlink | prose | skill:1 | 是 | 保留 | 無 |
| archive | 滾動歸檔老 Verification | prose | skill:2 | 是 | 保留 | 無 |
| update | 從源更新 vendored 工具組 | prose | skill:1 | 是 | 保留 | 無 |
| bootstrap | 一鍵裝好一切 | prose | skill:2 | 是 | 保留 | 無 |
| init | 專案層初始化 | prose | skill:2 | 是 | 保留 | 無 |
| deinit | 專案層反安裝 | prose | 只在總覽行提過;git:28(高,但多半是「deinit 相關程式碼改動」而非「跑了 deinit」) | 弱 | 精簡 | 補進 reference.md,現狀完全沒教怎麼叫(對稱的 init 有 2 處教學,deinit 0 處) |
| teardown | 一鍵拆機 | prose | 只在總覽行提過;git:7 | 弱 | 精簡 | 同上,對稱缺教學 |
| fold-check | 折入後一致性複查 | prose | skill:2 | 是 | 保留 | 無 |
| refcheck | spec 指涉確定性核對 | prose,design-loop 前置排乾用 | skill:4 | 是 | 保留 | 無 |
| impact | 動手前算波及節點 | **軟**(Claude PreToolUse hook 自動呼叫) | skill:8;hook 程式碼確認會在每次 Edit/Write 前跑(`impact-hook.py`) | **是,真自動注入 context**,是本清單裡少數「機制上保證到得了」的 | 保留 | 無,這是本表現存做得最對的一個(自動、快取、真注入) |
| pitfalls | 實務隱患提問/--diff 代碼風險 | **軟**(pre-push 自動呼叫,advisory;tier=high 才升級成硬擋 code-loop) | gov 帳沒有獨立 gate 名(併在 code-loop 的觸發鏈裡);skill:8 | 是(pre-push stdout) | 保留 | 無 |
| ci-wait | push 後同輪等 CI 結論 | prose,主路徑 | gov: ci 25 筆 | 是 | 保留 | 無 |
| ci-status | 唯讀查最後 CI 結果 | **軟**(Claude hook 補位) | 只在總覽行提過;`ci-status-hook.py` 有真呼叫點 | 是(hook 補位注入) | 保留 | reference.md 補一行(目前只被 hook 呼叫,人類/Claude 手動場景 0 教學) |
| testmap | 檔案↔測試依賴地圖 | prose,advisory | skill:1 | 是 | 保留 | 無 |
| test-layers | 測試層軟提醒 | **軟**(pre-push 自動呼叫,純印) | skill:3 | 是(pre-push stdout) | 保留 | 無 |
| lint-check | .lumos/lint.json 健康度檢查 | prose | skill:2 | 是 | 保留 | 無 |
| sqlfluff-sarif | SQL linter→SARIF 橋接 | prose | skill:1 | 是(僅裝了 sqlfluff 的專案) | 保留 | 無 |
| stylelint-sarif | CSS linter→SARIF 橋接 | prose | skill:1 | 是 | 保留 | 無 |
| anchor | 錨點 sha256 baseline(verify/approve) | **硬**(verify, pre-push+CI 阻擋) | gov: anchor-approve 145 筆 | 是 | 保留 | 無,這是少數真正機械阻擋的閘 |
| quote-check | 引句錨定對回凍結快照 | prose,design-loop 收貨三件之一 | skill:3 | 是 | 保留 | 無 |
| mutate | diff 變異測試驗測試網 | prose | skill:1 | 是 | 保留 | 無 |
| link-candidates | code→節點補鏈候選 | prose,唯讀 | 只在總覽行提過;2 篇 Verification 引用真落地結果 | 弱(結果進圖譜,命令本身無教學) | 精簡 | 補一行範例 |
| seat-check | 有講沒做對帳 | prose,驗證層自證三件之一 | skill:2 | 是 | 保留 | 無 |
| lint-watch | 依賴版本落差掃描 | prose | skill:1 | 是 | 保留 | 無 |
| compose-metrics | Compose 指標回歸掃描 | prose | skill:1 | 是 | 保留 | 無 |
| cochange | co-change 漏改守衛 | **軟**(pre-commit 自動呼叫,`\|\| true` 不擋) | skill:1 | 是(pre-commit stdout,但從不擋) | 保留 | 無 |
| delguard | code 側刪除傳播守衛 | **軟**(pre-commit 自動呼叫,`\|\| true` 不擋) | 0 個「lumos delguard」教學命中,但 SKILL.md:252/Verification/2026-08-11 有機制文檔 | 是(pre-commit stdout) | 保留 | 這條不是缺教學,是我用「lumos <cmd>」語法找教學的方法論本身對它不適用(它不是給人手動打的) |
| code-loop | pass/skip/check 收斂留痕 | **硬**(check, pre-push 條件阻擋)+prose(pass/skip 手動) | gov: code-loop 79 筆(2026-07-05~2026-08-21);skill:7 | 是 | 保留 | 無,這是本清單第二個真正機械阻擋的閘 |

## 4. Overlap / 重複命名分析

- **search vs query vs map**:不重疊。CLAUDE.md 已經把分工寫死(「找『講到詞』用 search;篩『欄位條件』用 query」),map 是結構樹狀展開,三者是三個正交軸(全文/欄位/拓撲)。**不需要合併**,唯一問題是 map 教學太薄(見上表)。
- **context vs show**:表面像「摘要版 vs 完整版」,但 usage-log 顯示 `show`(91)實際被叫得比 `context`(75)還多——與 CLAUDE.md「入口三步只提 context」的敘事不符。要嘛承認 show 也是常用入口該寫進三步,要嘛查清為何 show 用量偏高(可能是 Claude 覺得 context 摘太兇要補讀全文,若是,context 的壓縮率該檢討)。
- **stale vs doctor**:不重疊。doctor 是 ~20 個結構完整性 Check(M/C/T/R/S/E1-3/H/K/D/N/Y/J/U 等)的集合體,stale 是獨立的「風險加權陳舊排序器」(用 pagerank 百分位算 risk band),兩者程式碼路徑完全不共用。
- **loop status 的 6 種模式**(legacy `--need`/`--gate`/`--panel`/`--light`/`--settle`/`--disposal`):**這是真正的重複面**。讀 `Systems/design-loop.md` 的 decisions/summary 才拼得出時間線:
  - legacy(`--need` K-streak)= 2026-06-19 原始版,現存但已被取代
  - `--panel` = 2026-07-09 引入、2026-08-05 起加嚴 K=2,summary 明講「取代 K-streak∧G2 序列」——**現行推薦**
  - `--light` = 2026-07-21 給 trivial|standard 間的小 spec,M1 已機械化
  - `--settle` = 2026-07-28「結清式收斂」,只接 legacy 清單,與 --panel/--light/--need 互斥
  - `--disposal` = 2026-08-04 重設計後的**新主路徑**(T4,獨立於 K-streak/panel 之外),summary 原句:「收斂改走處置閘」,但同一節點 2026-08-21 又補注「三合一退場不準確——panel 的『輪有效∧存活≤minor』仍是必要合取,只有 capture-recapture 降 advisory」
  
  即:六種模式裡至少 legacy K-streak、--panel、--disposal 三種同時「都還在」且都聲稱自己是路徑,連圖譜自己 2026-08-21 都要回頭更正「三合一退場」的說法不準——**這就是本表要抓的「Claude 能不能從 --help 選對」失敗案例**:`loop status --help` 只列旗標與一行互斥說明,不講時間線/現行推薦,一個沒讀過 `Systems/design-loop.md` 全部 summary(該節點單一 summary 欄位本身就有 11 條 KEY block,長達數千字)的 Claude 沒有辦法只靠 --help 選對模式。
- **canary(caught/missed) vs canary(none)**:2026-08-14 canary「植入」協議整體停用(decisions d5 的下游落地),所有輪次自此改記 `kind=none`。近期 canary-log 尾端 10 筆清一色 `none`(見下方缺陷 3),`caught`(337)/`missed`(67)是歷史帳,`none`(83)是現行帳——但**`canary --help` 完全沒有這個時間分野**,只寫「none=無植入輪的純處置帳載體,2026-08-14 協議停用後的常態」一行小字,容易被當成第三種平行選項而非「協議已停,以後都填這個」。

## 5. --help 可導航性

- 頂層 `--help` 9147 字元,61 個子命令一行一句中文簡述,無分類、無「先讀這三個」的提示——比對 CLAUDE.md 自己教的「入口三步」(search→context→contracts),這三步在 `--help` 輸出裡跟其他 58 個命令排序權重完全相同,**新鮮 Claude 只看 --help 選不出入口路徑**,必須先讀 CLAUDE.md 才知道優先序。
- `loop status --help` 單條約 1400 字元,6 個模式旗標裡有 4 對互斥組合(`--disposal` 與 `--panel/--light/--settle/--need/--min-seats` 互斥;`--settle` 又與 `--panel/--light/--need/--min-seats` 互斥),純文字沒有決策樹圖示,**選錯模式不會在 --help 層被攔,要跑了才知道噴 argparse 衝突或行為不對**。
- `guard`/`code-loop`/`canary` 的子命令 --help 相對精簡(2-7 個子動作,一行講清楚),導航性良好,是本表現存做得對的另一組。

## 6. 三到五個最重要缺陷(file:line 證據)

1. **使用量帳本本身有 98% 盲區**:`docs/.usage-log.jsonl` 只在 `cmd_context`/`cmd_show` 埋了記帳呼叫,其餘 59 個子命令完全沒接線——本審計被迫用 git log 訊息關鍵字命中數(充滿假陽性,commit 訊息提到某詞不代表真的跑了那個命令)當代理。修法:比照 `_log_usage` 的模式(應在 `scripts/lumos` 內約 context/show 呼叫處附近)把記帳呼叫下放到 argparse dispatch 的統一出口,一行改動換全命令可觀測。

2. **loop status 六模式並存且互相修正對方的「誰是主路徑」宣告**——`Systems/design-loop.md` frontmatter 的 summary 欄自己在 2026-08-21 寫「★更正:三合一退場不準確★」推翻 2026-08-04 版本自己講的「收斂改走處置閘」。連權威節點自己都要回頭修正時間線,`scripts/lumos` 第 14310-14343 行的 argparse 定義純靠互斥旗標表達關係,沒有任何機制防止一個 Claude 讀了舊版 skill 說明就用 legacy `--need` 模式跑新 spec。修法:`loop status --help` 開頭加一行「現行推薦:--panel(K=2)或 --disposal;legacy 僅供舊帳重放」。

3. **`canary second` 子命令:0 筆使用記錄,`kind=none` 已成事實上的預設**——`grep -c "second" docs/.canary-log.jsonl` = 0,而近 10 筆 canary-log 全是 `none`(`docs/.canary-log.jsonl` 尾端)。`second`(S2 第二判者覆核,`scripts/lumos` `cmd_canary` 的 kind choices 之一)是「oracle 品質包」設計出來但從沒被實際呼叫過的旗標。修法:查 `oracle品質包` 相關 Verification 是否已判定 second 不划算,是則砍;否則排進下一輪 design-loop 真的接上。

4. **`decision-reindex` 是唯一一個「連間接使用痕跡都找不到」的子命令**——不同於 map/export/deinit/teardown/link-candidates/drift-history/rel-cascade(這些都能在 git log 或 Verification 裡找到至少一次真實觸發),`decision-reindex` 只出現在 `skills/lumos-project-notes/reference.md:86` 的 61 命令總覽逗號清單裡,`git log --all` 對命令字面 0 命中(19 次命中全部是函式定義本身被改動的 diff,不是「被執行」的證據),governance/canary/bypass 三本帳 0 命中。它的設計用途(「decision_refs 養成前置」P2 一次性遷移)很可能窗口已過。修法:`lumos query --tag` 掃一次現存節點是否還有 decisions 缺 id,零則砍此命令,非零則補教學+保留。

5. **pre-commit 兩個自動掛載的守衛(`cochange check` `delguard`)設計上恆真放行,但輸出文案讀起來像是在「擋」**——`scripts/hooks/pre-commit:57` `"$CC_PY" "$REPO_ROOT/scripts/lumos" delguard --staged 2>/dev/null || true`,`\|\| true` 讓這條路徑永遠 exit 0,但 SKILL.md:252 描述它「S1 命中時會機械吐上面 1-3 這三問」,讀起來像有攔截力,實際只是印字。修法:pre-commit 輸出文案該明講「advisory,不會擋 commit」,避免 Claude 誤以為沒看到輸出=沒有 delguard 命中(它可能命中了,只是 `2>/dev/null` 把非 stderr 輸出以外的東西吃掉,實測需要另外驗證這條真的會印到 stdout 而非被吞)。
