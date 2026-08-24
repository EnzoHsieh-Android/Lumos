# selfaudit-loop r2 架構對齊審查

被審:`/tmp/selfaudit-loop-r2.md`(自足性審計閉環_計劃,131 行)。只判「跟本專案既有做法一不一致」,不找 bug、不評風格。★只審 v3 delta:設計節七步(40-77 行)、連動節(83-87 行)、測試十條(94-101 行)★。對照對象:`governance/autonomous_loop/*.py` 既有模組形狀(純函式/明確參數,`test_autonomous_loop.py` 的 import 測試模式)、`scenario_probe.py` 的 subprocess timeout+allowedTools 組裝、`covered.jsonl`/`gap_select` 的 skip 結構、`about_code_expired` 抽函式先例、`autonomous-loop.sh:6-14` dry-run 裁定註解的行文慣例、`cmd_self_audit` 的 `--model` 參數語意、`lumos canary record` 成本欄用法。

---

## 問一:分層與依賴方向——`_self_audit_lists` 的 import 路徑,跟 dry-run 白名單例外的裁定行文站不站得住

**`selfaudit.py` 要用 `SourceFileLoader` 拉一個吃 `env`(整個 `Env` 物件)的函式——跟 `SourceFileLoader` 真正的既有先例不同形狀,而且會是 `governance/autonomous_loop/` 這個套件第一次依賴 `scripts/lumos` 的內部物件模型——不對齊,major。**

spec 設計第 1 條:「把 Check S 判定從 `run_doctor` 閉包抽成頂層函式 `_self_audit_lists(env) -> (sa_missing, sa_stale)`(照 `about_code_expired` 先例…);selfaudit.py 用 `SourceFileLoader` 載入呼叫(canary_calibration/k1_stop_replay 既有先例)」(`/tmp/selfaudit-loop-r2.md:47-49`)。

引句:「selfaudit.py 用 `SourceFileLoader` 載入呼叫(canary_calibration/k1_stop_replay 既有先例)」(`/tmp/selfaudit-loop-r2.md:49`)

先看「抽成頂層函式」本身——`about_code_expired(vault, rel, stamp)`(`scripts/lumos:7736`)確實是被 `run_doctor` 內部(`:888`)與獨立的 `cmd_impact`(`:14128`)兩處共用的頂層函式,這半段引用站得住。但「用 `SourceFileLoader` 載入呼叫」這半段引用的兩個先例,實際拉的東西跟 `_self_audit_lists(env)` 形狀不一樣:`governance/eval/k1_stop_replay.py:11-15` 用 `SourceFileLoader` 載入 `scripts/lumos` 只為了抓 `_lm._estimate_remaining_defects`——這是 `_estimate_remaining_defects(capture_counts)`(`scripts/lumos:3699`)這個純函式,吃一個 list、吐一個數字,完全不碰 `Env`/vault/檔案系統;`governance/eval/canary_calibration.py:28` 拉的是同一個函式。也就是說,本庫僅有的兩個 `SourceFileLoader` 先例,選的都是「跟 `Env` 物件無關的純函式」,不是「吃整個 `env`、回傳全圖譜掃描結果的聚合函式」。`_self_audit_lists(env)` 要拿到的 `env` 是 `scripts/lumos` 自己的 `Env` 類型(vault 路徑+已載入的 notes),這是一個目前只在 `scripts/lumos` 內部流轉的框架物件。

更關鍵的是分層方向:把 `grep -rn "import\|SourceFileLoader" governance/autonomous_loop/*.py` 的結果核對過(8 個既有模組:`backlog.py`/`gap_select.py`/`confidence_report.py`/`cross_audit.py`/`difficulty.py`/`line_notify.py`/`lint_watch_dedup.py`/`orchestrator_result.py`),沒有一個 import 或依賴 `scripts/lumos`,清一色只用標準庫(json/pathlib/re/os/subprocess/urllib/ssl),明確參數傳遞、不吃框架物件。`selfaudit.py` 若照 spec 這樣寫,會是這個套件第一次反向依賴 CLI 層的 `Env` 型別,而且是透過一個原本只拿來取「無狀態純函式」的 loader 機制去拿一個「狀態耦合的聚合函式」——同一個機制被借用到形狀不同的用途上,判 major(跨層直呼:`governance/autonomous_loop` 這一層原則上不碰 `scripts/lumos` 的內部物件,這裡要直接穿透)。

**dry-run 白名單例外要加的裁定註解,沒交代這個新例外自己的回頭看條件——不對齊,non-major。**

spec 設計第 6 條:「autonomous-loop.sh 現鎖 dry-run(2026-07-29 confused-deputy 裁定)、PASS 要寫檔——★白名單例外,授權=d1 人裁…★:selfaudit.py 只准寫三類…範圍刀機械驗;loop 頭部裁定註解加一行引用 d1 與白名單。不解除整體禁令」(`/tmp/selfaudit-loop-r2.md:73-75`)。

引句:「loop 頭部裁定註解加一行引用 d1 與白名單」(`/tmp/selfaudit-loop-r2.md:75`)

本庫唯一一段格式化的「裁定」註解就在同一支腳本開頭(`governance/autonomous-loop.sh:8-10`):「非 dry-run 停用(2026-07-29 使用者裁定,Codex 外審採納):子 agent 權限隔離…confused-deputy 已知漏洞…不留可執行入口——--pr 直接拒跑。解禁條件:read-only child isolation 落地+過 code-loop。」這段行文有固定四件事:裁定者+日期、風險理由、機制(不是口頭)、**解禁條件**。spec 這裡「機制」那塊接得上(白名單+範圍刀機械驗,呼應「不留可執行入口」的精神),但只講「引用 d1 與白名單」,沒有講這個新白名單本身什麼時候該被重新檢視(例如範圍刀誤放行 N 次、或 `nested-agent-permission-scope` 落地後這個白名單要不要收斂進正式解禁)。CLAUDE.md 自己的鐵則 4「承認風險要附回頭看的條件」也是同一個要求。這不是「第二種做法」,是行文格式的一塊沒補上,判 non-major。

**⚠ `selfaudit-skip.jsonl` 照 `covered.jsonl` 「同款結構」,但兩處對它的語意描述互相打架——判不準,不計入下方條數。**

spec 第 1 條:「照 `covered.jsonl` 同款結構開 `selfaudit-skip.jsonl`——已有未結案 pending 檔的篇跳過,人清 pending 後自動恢復」(`/tmp/selfaudit-loop-r2.md:51`);但第 4 條處置分支寫:「複審仍 FAIL=落 pending、記 skip 檔、本篇不再自動重試」(`/tmp/selfaudit-loop-r2.md:66`)。

引句:「照 `covered.jsonl` 同款結構開 `selfaudit-skip.jsonl`」(`/tmp/selfaudit-loop-r2.md:51`)

`covered.jsonl` 的既有結構(`gap_select.load_covered`/`mark_covered`,`governance/autonomous_loop/gap_select.py:25-38`)是「只加不減」的永久排除集——一旦寫入就沒有對應的「移除」函式,`load_covered` 的 docstring 直接寫「已被…覆蓋…永久排除,不再選/不重加」。spec 第 1 條說的「人清 pending 後自動恢復」是一個**可逆**行為(pending 檔還在就跳過、清掉就復活),這種語意用「檢查 pending 目錄現在存不存在該篇的檔」就能表達,不需要另開一個永久 append 的 jsonl;但第 4 條又說寫進 skip 檔就「不再自動重試」,這聽起來才是真的照抄 `covered.jsonl` 的永久排除語意。同一份 spec 對「skip 檔」到底是可逆狀態還是永久狀態,兩處說法不一致,判不準,標 ⚠。

---

## 問二:命名與值域——`--model auto/<model>` 跟 `self_audit` 既有值域,commit 署名慣例,連動節的 covered 對照

**`--model auto/<model>` 會讓 `self_audit` 欄第一次出現雙斜線,跟 `cmd_self_audit` 自己宣告的 `<model>/<date>` 格式、以及全庫現存值不符——不對齊,non-major。**

spec 第 4 條 PASS 分支:「PASS → `lumos self-audit <篇> --model auto/<model>`(★前綴 auto/,repo 既有 auto- 前綴慣例;arch:-auto 後綴無先例★)」(`/tmp/selfaudit-loop-r2.md:63`)。

引句:「PASS → `lumos self-audit <篇> --model auto/<model>`」(`/tmp/selfaudit-loop-r2.md:63`)

這是為了回應 r1 arch 審查的既有結論而改的(r1 指出 `-auto` 後綴無先例,本庫「自動流程」標記一律是前綴)。但這裡把 `auto/` 塞進 `--model` 這個參數的**值**裡,而不是塞進整個 `self_audit` 欄位的值。`cmd_self_audit(env, rel, model="sonnet", date=None)`(`scripts/lumos:7578`)的 docstring 明寫「寫 `self_audit: <model>/<date>` 到節點 frontmatter」,實作是 `f"{model}/{date}"`(`:7593`)——`--model` 這個參數的既有語意就是「審計 model(預設 sonnet)」(argparse help,`:15610`),是一個不含斜線的裸模型名。把 `auto/<model>` 整串餵給 `--model`,寫出來的欄位值會變成 `auto/<model>/<日期>`——兩個斜線、三段。核對全庫目前所有真實 `self_audit` 值(`grep -rhn "^self_audit:" docs/lumos-toolchain-knowledge/`,17 筆全部命中),清一色 `<裸模型名>/<日期>` 恰一個斜線,零例外(如 `self_audit: claude-fable/2026-08-24`、`self_audit: sonnet/2026-08-21`)。Check S 讀值時只用正則抓日期子字串(`scripts/lumos:834-835`)不會炸,所以機器不擋,但這是把「auto 前綴」接在了錯的欄位上——要嘛把 `auto/` 接在整個 `self_audit` 值前面(維持 `<model>/<date>` 兩段不變、外面再包一層),要嘛就得承認這是在改 `--model` 參數自己的既有語意。判 non-major(不影響機器判讀,是欄位語法被悄悄改了一格)。

**FAIL 鏈修復通過後的 commit「訊息三 model 署名」,本庫自動化 commit 目前只有一種慣例,且沒有署名區塊——不對齊,non-major。**

spec 第 4 條:「→ 第三個乾淨複審 agent(不給報告與修法)→ PASS=蓋章+commit(訊息三 model 署名)」(`/tmp/selfaudit-loop-r2.md:65`)。

引句:「PASS=蓋章+commit(訊息三 model 署名)」(`/tmp/selfaudit-loop-r2.md:65`)

`grep -rn "git commit" governance/*.sh governance/*.py governance/autonomous_loop/*.py` 在整個治理自動化層裡只有一處真的會 commit:`autonomous-loop.sh:380` 的 `git commit -m "auto-spec: $TOPIC（自主迭代 loop 收斂產出，待人放行）"`——單行訊息,沒有任何署名/trailer 區塊。selfaudit 鏈要在一則 commit 訊息裡列三個 model(審計/修復/複審)的署名,是本庫自動化 commit 目前唯一先例裡沒有的格式。這不是「第二種做法」在做同一件事(既有那筆 commit 的是 spec 產出,這裡 commit 的是筆記修正,任務本身不同),所以不判 major,但既然要新開一種 commit 訊息格式,spec 目前沒有交代它照的是哪個既有格式、還是純自訂,判 non-major。

**連動節「backlog『腐化偵測延遲』條標 covered」沒有點名要寫入的逐字 weakness 字串,而 `covered.jsonl` 的比對是逐字集合相等——不對齊,non-major。**

連動節:「backlog「腐化偵測延遲」條標 covered」(`/tmp/selfaudit-loop-r2.md:86`)。

引句:「backlog「腐化偵測延遲」條標 covered」(`/tmp/selfaudit-loop-r2.md:86`)

`governance/backlog.jsonl` 裡這條真實記錄的 `weakness` 是一整句長字串:「L3 腐化偵測延遲很大(commit 後、每週才人工看),自主 loop 想閉合這缺口卻沒守住『延遲×力道』的上限。」`gap_select.mark_covered(covered_path, weakness)`(`governance/autonomous_loop/gap_select.py:35-38`)寫入 `covered.jsonl` 的是這個字串本身,而 `load_covered`/`select` 用的是純字串集合相等(`g.get("weakness") not in covered`,`gap_select.py:61/69`),沒有任何模糊比對或正規化。連動節只寫「標 covered」,沒指向 `mark_covered` 這個既有函式、也沒把要寫入的字串釘死——照抄一個近似但不逐字的 weakness 字串,`covered.jsonl` 就攔不住這條 backlog 項再被選中,跟該功能的既有比對機制不符。判 non-major(連動節本來就是清單而非實作,但既有機制對「逐字」這麼硬性,值得點名)。

---

## 問三:測試段落有沒有引入本庫查無先例的做法

**測試段落收尾那句「shell 段落照 t_install_global_hook_sync 模式(bash -n+函式抽測)」,是 r1 s2 已經判過 major(f9)、指出本庫查無此先例的原句,v3 一字未改地留下來,還跟同段落開頭剛下的結論自相矛盾——不對齊,major。**

測試段落開頭先說:「(全部走 `test_autonomous_loop.py` 直接 import selfaudit.py 的既有模式——s2f9:bash 層無可測先例,故邏輯全在 python)」(`/tmp/selfaudit-loop-r2.md:96`),結尾卻又寫:「shell 段落照 t_install_global_hook_sync 模式(bash -n+函式抽測)。」(`/tmp/selfaudit-loop-r2.md:101`)

引句:「shell 段落照 t_install_global_hook_sync 模式(bash -n+函式抽測)」(`/tmp/selfaudit-loop-r2.md:101`)

`grep -rn "bash -n" scripts/ governance/*.py scripts/test_lumos.py scripts/test_autonomous_loop.py` 在本庫原始碼裡零命中(唯一出現的地方是 `governance/scenarios/*.json` 幾份情境探針的**題目文字**,不是測試方法論)。`t_install_global_hook_sync`(`scripts/test_lumos.py:323`)實際測的是 `_sync_global_claude` 這個 Python 函式,手法是用 `SourceFileLoader` 把 `scripts/lumos` 當模組載入、在假 `HOME` 下直接呼叫函式(`scripts/test_lumos.py:328-336`)——整套都是 Python 函式呼叫加子行程隔離,完全沒有 `bash -n`(bash 語法檢查),也沒有從任何 `.sh` 檔案抽出 bash 函式來測。這正是 r1 審查 s2 席位對 v1 同一句話下的判定(`governance/review-reports/selfaudit-loop/r1-s2.md:158-164`,判 f9 major:「這個方法論引用的先例本身就不成立,而且本倉庫沒有任何檔案示範過『bash -n + 函式抽測』」)。核對 `/tmp/selfaudit-loop-r2.md` 跟 `governance/review-reports/selfaudit-loop/r1-snapshot.md:63`,這句話逐字相同,一個字都沒動——r1 審計修正紀錄自稱「全折,零放行」(`/tmp/selfaudit-loop-r2.md:116`),但這條 major 沒有真的折進去,只是同段落開頭補了一句「全邏輯進 python」把它架空,沒把矛盾的殘句刪掉。既然架構裁定已經把 `autonomous-loop.sh` 要新加的部分限定在「只加 3 行呼叫」(`/tmp/selfaudit-loop-r2.md:45`),跟 `run_exam`/`probe`/`nags` 一樣「零測試」,這句話描述的「shell 段落」測試在這個架構下已經沒有對應的東西可測,留著只會誤導下一個實作者去找一個不存在的先例、寫一個本庫從沒示範過的測試手法。判 major(方法論引用不存在的先例,且跨到一個架構已裁定不需要測的層)。

---

## 結論

不對齊共 **6** 條,其中 major **2** 條:

1.(問一)`selfaudit.py` 用 `SourceFileLoader` 拉的是 `_self_audit_lists(env)`——一個吃整個 `Env` 物件的聚合函式;但本庫僅有的兩個 `SourceFileLoader` 先例(`governance/eval/canary_calibration.py:28`、`k1_stop_replay.py:11`)拉的都是無狀態純函式 `_estimate_remaining_defects(capture_counts)`(`scripts/lumos:3699`),`governance/autonomous_loop/*.py` 現有 8 個模組也全部不依賴 `scripts/lumos` 的內部物件——這會是該套件第一次跨層直依賴 CLI 層的 `Env` 型別。**major**。
2.(問三)測試段落結尾「shell 段落照 t_install_global_hook_sync 模式(bash -n+函式抽測)」(`/tmp/selfaudit-loop-r2.md:101`)是 r1 s2 已判 major(f9)、指出本庫查無此先例(`grep -rn "bash -n" scripts/` 零命中,`t_install_global_hook_sync` 實測是純 Python 函式呼叫)的原句,v3 逐字未改,且與同段落開頭「邏輯全在 python」的結論自相矛盾。**major**。
3.(問一)dry-run 白名單例外要加的裁定註解只講「引用 d1 與白名單」(`/tmp/selfaudit-loop-r2.md:75`),沒交代這個新例外自己的回頭看/解禁條件——跟 `governance/autonomous-loop.sh:8-10` 既有裁定註解「裁定者+日期/風險理由/機制/解禁條件」四件式行文不完整對齊。
4.(問二)`--model auto/<model>`(`/tmp/selfaudit-loop-r2.md:63`)把 `auto/` 前綴塞進 `--model` 參數值本身,寫出來的 `self_audit` 欄變成雙斜線三段,跟 `cmd_self_audit` docstring 宣告的 `<model>/<date>` 格式與全庫現存 17 筆真實值(清一色恰一個斜線)不符。
5.(問二)FAIL 鏈複審通過後「commit(訊息三 model 署名)」(`/tmp/selfaudit-loop-r2.md:65`)在本庫自動化 commit 唯一既有先例(`autonomous-loop.sh:380` 的 `auto-spec: $TOPIC`,單行、無署名區塊)裡找不到對應格式。
6.(問二)連動節「backlog『腐化偵測延遲』條標 covered」(`/tmp/selfaudit-loop-r2.md:86`)沒有點名要寫入 `covered.jsonl` 的逐字 `weakness` 字串,而 `gap_select` 的比對是純字串集合相等(`governance/autonomous_loop/gap_select.py:61/69`),沒有模糊比對。

另有 1 條判不準標 ⚠、不計入以上條數:`selfaudit-skip.jsonl`(`/tmp/selfaudit-loop-r2.md:51`)照 `covered.jsonl` 同款結構,但 spec 第 1 條說它「人清 pending 後自動恢復」(可逆)、第 4 條又說「不再自動重試」(`/tmp/selfaudit-loop-r2.md:66`,永久)——跟 `covered.jsonl` 本身「只加不減、永久排除」的既有語意,兩處說法互相打架,判不準是哪一種。
