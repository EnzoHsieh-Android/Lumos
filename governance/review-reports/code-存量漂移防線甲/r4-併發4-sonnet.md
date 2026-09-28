severity: blocker

## F1 筆記內容審共用的逐提交讀狀態,還有一條「一支 git log 失敗就整道放行」的路沒被這輪的 strict 參數擋住

severity: blocker
blocking: 是 — 這輪的核心承諾是「筆記內容審批次讀失敗時退回原本行為(只少那份完成審、其他新寫的行照審)」,但 `_note_status_seq` 裡逐篇的 `git log --follow` 這支呼叫失敗時,不看 `strict` 一律回 `None`,並沿著 `_notes_status_flipped`→`_note_audit_closed_plans`→`_note_audit_items` 一路傳到 `cmd_note_audit_check`,後者把 `got is None` 當「git 算不出這次的筆記行,跳過(fail-open)」處理——結果是「一篇計劃的一次 git 呼叫失敗,連別的新寫的行都不審」,跟這輪要修的 r2 回歸一模一樣,只是換了一個沒被 strict 蓋到的呼叫點。

引句:「★只有存量漂移那條路嚴格★(代碼審 r3 併發席 blocker:r2 讓共用這支一律嚴格」

1. `scripts/lumos` 的 `_note_status_seq`(約 24544 行)裡:`lg = _ns_git(repo_root, "log", "--follow", "--format=%H", "--name-only", "-z", rng, "--", p)`,緊接 `if lg is None: return None`——這兩行是 diff 裡沒變動的既有行(context line),不受這輪新增的 `strict` 參數保護;docstring 也老實寫著「git log 失敗回 None」,即不分 strict。
2. `_notes_status_flipped` 對每個候選路徑呼叫 `_note_status_seq(...)`,拿到 `None` 就 `return None`(整支函式失敗),不是「只丟掉這一篇」。
3. `_note_audit_closed_plans`(不帶 strict)直接把這個 `None` 往上傳;`_note_audit_items` 收到 `closed is None` 也 `return None`;`cmd_note_audit_check` 把整支 `None` 當成「這次推送完全算不出筆記行」,直接 `return 0` 放行,不只是漏審那一篇計劃,而是連同一批一起新寫的、跟那篇計劃完全無關的行也不審。
4. 重現(monkeypatch `_ns_git`,模擬「範圍內動過兩篇筆記 P1、P2,P1 的 `git log --follow` 這支剛好失敗、P2 讀得到且真的有翻轉」,呼叫筆記內容審預設的 `strict=False`、不帶 `deadline`):
   ```
   $ python3 /tmp/.../repro_note_audit_failopen.py
   筆記內容審(strict=False)拿到的結果: None
   ```
   若這輪真的把筆記內容審「退回原本行為」,P1 那支呼叫失敗應該只讓 P1 的完成審判不出來,回傳值該是 `["docs/kg-knowledge/Projects/P2.md"]`(P2 照樣被判成收尾翻轉);但實際回傳整支 `None`,對應到 `cmd_note_audit_check` 就是整批新寫的行都不審。
5. 全套既有測試(含這輪新增的 `t_drift_code_review_r3_regressions`)都綠,因為所有測試只 mock `_nodehome_cat_blobs` 回 `None`(批次讀失敗),沒有任何一條測試讓 `_ns_git(..., "--follow", ...)` 本身回 `None`,所以這個缺口沒被目前的回歸釘蓋到。

## F2 `_drift_tree_env` 傳給批次讀的 timeout 是進場前算好的舊值,沒扣掉 `_nodehome_list` 已經花掉的時間,實際超支比文件講的「多一次呼叫的時間」更多

severity: major
blocking: 是 — PITFALL 明確宣稱「批次讀以剩下的時間為上限」、「最壞比預算多一次呼叫的時間」,但 `_drift_tree_env` 裡批次讀拿到的 `timeout` 是呼叫端在還沒進這支函式之前算好的 `_left()`,函式內先跑一次 `_nodehome_list`(經 `_lens_git`,固定最多 20 秒)之後,才把那個沒扣掉這 20 秒的舊 timeout 原封不動交給 `_nodehome_cat_blobs`。

引句:「預算在每一次 git 呼叫前都看,正在跑的那一次不打斷(一般呼叫最多 20 秒,批次讀以剩下的時間為上限)」

1. `_drift_check_core`(scripts/lumos)算一次 `_left()` 就直接傳給 `_drift_tree_env(root, tip, vault_rel, override, timeout=_left())`(未變動的既有呼叫,round 沒有改這裡)。
2. `_drift_tree_env` 內先呼叫 `_nodehome_list(root, where)`(內部走 `_lens_git`,單次最多可以跑到 20 秒),沒有在這一步前後重新看剩下多少預算,也沒有重新計算;拿到結果後直接用**呼叫端傳進來、沒扣掉 `_nodehome_list` 已花時間**的同一個 `timeout` 數字去跑 `_nodehome_cat_blobs(..., timeout=max(1, timeout))`。
3. 重現(monkeypatch `_nodehome_list` 讓它睡 0.5 秒模擬慢速單次呼叫、`_nodehome_cat_blobs` 記錄實際拿到的 `timeout` 參數,預算只給 0.6 秒):
   ```
   進 _drift_tree_env 前算出的 timeout(給 cat_blobs 用的原始值): 0.6
   _nodehome_list 花掉的時間: 0.501
   cat_blobs 真正開始時,離 deadline 實際還剩: 0.099
   但傳給 cat_blobs 的 timeout 參數是: 1 (沒有扣掉 _nodehome_list 已經花掉的時間)
   ```
   把數字放大到真實的 `_DRIFT_BUDGET_SEC=60`:worst case `_nodehome_list`吃掉它自己上限的 20 秒後,`_nodehome_cat_blobs` 仍可能拿到接近原始 60 秒的 timeout(而不是剩下的 ~40 秒),讓 `_drift_tree_env` 這一步單獨就能跑到 20+60=80 秒——比文件講的「預算 60 秒 + 多一次呼叫(最多 20 秒)」的 80 秒上限剛好貼著邊界,但已經不是文件描述的機制(「批次讀以剩下的時間為上限」),而是巧合對上。若之後 `_drift_range_events` 那幾次呼叫也各自吃一點,或 `_nodehome_list` 本身要列的樹更大導致更久,總時間會真的超出文件宣稱的上限。
4. 目前的回歸測試(`t_drift_code_review_r3_regressions` 的 ⑥)只測了 `_note_status_seq` 內部逐次呼叫前都看 `late()`,沒有涵蓋 `_drift_tree_env` 這條「單次呼叫接批次讀」的鏈,所以這個 stale timeout 沒被抓到。

## 其餘看過、沒有 finding 的部分

- **settle 擋下時家筆記與守衛紀錄都沒動**:逐一讀過 `_guard_settle_home` 的每一條「擋下」分支(打不開、綁的測試裡沒有這支、預告行重複好幾條、找不到預告行),全部在呼叫任何 `atomic_write_verify` 之前就 `return False`;唯一會寫檔的兩個分支(拿掉重複預告行、換成正式行)都不是「擋下」路徑。`atomic_write_verify` 本身「任一步敗:tmp 丟棄,原檔不動」(scripts/lumos:14431),排除了寫到一半失敗留殘檔的可能。`_guard_settle_locked` 在 `_guard_settle_home` 回 `False` 時直接 `return 2`,不會碰 `gpath`(守衛紀錄)。已看,無 finding。
- **guard plan/settle/abandon 整段寫入鎖**:三支 `cmd_guard_*` 都是 `with _vault_write_lock(env.vault): return _guard_*_locked(...)`,把讀家筆記到寫完整段包住;`t_guard_commands_hold_vault_lock` 也用 `_VAULT_LOCK_HELD` 在讀檔當下斷言鎖已經拿著,三支都測了。已看,無 finding。
- **doctor 開頭多出的讀設定檔與 git 呼叫**:`_drift_gate_doctor_lines` 這輪把簽名從 `(repo_root, vault=None, ci=False)` 砍成 `(repo_root)`,函式內只有一次 `cp.read_bytes()`(讀 `.lumos/config.json`)加一次 `_lens_git(root, "show", f"HEAD:{_NOTELINES_PREPUSH}")`,跟同層的 `_note_shape_doctor_lines`/`_note_audit_doctor_lines` 開銷同量級,不是新增的資源熱點;砍掉的兩個參數在函式體裡原本也沒被用到,是死參數清理。已看,無 finding。
- **scan 判不了但不寫治理帳**:`cmd_drift_scan` 這輪拿掉了 `_gate_event_or_warn(root, "drift-check", "degraded", ...)`,只留列印;`_KNOWN_GATES` 已登記 `drift-check`,`docs/lumos-toolchain-knowledge/Systems/reversibility-governance-ledger.md` 也已經寫「放行不寫帳(同筆記形狀擋),doctor Z 段也不寫」,跟程式行為一致。已看,無 finding。

## 圖譜鏡頭:LUMOS-IMPACT 固定席逐條判

`lumos impact --diff e4158902..85d5fada` 列出的固定席多數是 `scripts/lumos` 這支巨檔的既有「家」節點,合約內容跟這輪 r3→r4 修正(settle 改寫比對、drift 預算、筆記內容審 strict 參數、doctor 開關提醒)不相交,逐條列在下面:

- **Systems/lumos-cli-read.md**(讀指令的合約:search 排除 superseded、doctor 全圖巡檢等):這輪改動不涉及 search/doctor 巡檢邏輯本身,只是 `run_doctor` 多印/少印幾行;drift scan 的「讀指令不寫帳」決策(該篇的 d1)反而是這輪 `[S2]` 改法的依據,一致不衝突。不影響。
- **Systems/guard-kill.md**(`guard kill` rc 優先序、JSON 輸出純淨、「本機推送只擋這次改動碰到的」):這輪動的是 `guard plan/settle/abandon`,不是 `guard kill` 本身,rc 優先序與 JSON 輸出沒有被碰。不影響。
- **Systems/design-loop.md**(設計審迴圈的條款綁定判定):功能不相關,diff 沒碰 `_clause_check`/`_visible_lines` 等函式。不影響。
- **Systems/loop-convergence-recording.md**、**Systems/pitfalls-code-loop.md**:分數來自 `scripts/lumos` 同檔關聯,內容分別是迴圈收斂記錄與 pitfalls 詞表,跟這輪改的 guard/drift/note-audit 函式不重疊。不影響。
- **Systems/授權與歸屬.md**(vendored LICENSE 白名單不得刪使用者授權檔):跟 deinit/vendor 流程有關,這輪沒有碰 `_VENDORED_TOOLKIT`/deinit 相關程式碼。不影響。
- **Systems/測試假綠形態.md**(修 bug 要配「前置斷言證明現場成立」的翻紅釘方法論):這是方法論節點,不是被這輪程式碼直接管理的行為;這輪新增的 `t_drift_code_review_r3_regressions` 用 monkeypatch 直接迫使失敗路徑成立(現場明確可控),沒有違反這條方法論。不影響。
- **Systems/lumos-cli-lifecycle.md**(re-inject 只覆蓋 sentinel 之間內容):跟這輪 guard/drift/note-audit 無關,diff 沒碰任何 CLAUDE.md re-inject 邏輯。不影響。
- **Systems/reversibility-governance-ledger.md**(閘名單登記):已用 `_KNOWN_GATES` 與該篇 WHY 行核對過——`drift-check` 已登記、事件種類跟這輪 `[S2]` 改成不寫 degraded 一致。不影響(已核對一致)。
- **Systems/節點範圍與索引守衛.md**、**Systems/lumos-deinit.md**、**Systems/check-t-sentinel.md**、**Systems/check-r-guard.md**、**Systems/cochange-guard.md**、**Systems/doctor-irreversible-hint.md**、**Systems/lumos-refcheck.md**、**Systems/core-invariant-baseline.md**、**Systems/judge-severity-gate.md**、**Systems/bound-tests-gate.md**、**Systems/canary-audit.md**、**Systems/slim-get-一行安裝.md**、**Systems/slim-install-安裝器.md**、**Systems/slim-uninstall-一行卸載.md**、**Systems/規格閘.md**、**Systems/每支檔有家.md**:皆是靠「同一支巨檔 scripts/lumos」關聯進固定席的既有合約節點,各自的 ★INVARIANT★/RULE 管的是索引覆蓋範圍判準、deinit 生命週期、Check T/K/R 的測試綁定判定、cochange 配對、可逆性回退提示、refcheck、CI 攔截嚴重度、bound-tests 篩選、canary 審計、slim 安裝腳本、design-loop 規格閘句式、每支檔有家的擋新增違規——這輪 diff 改的 `_guard_formal_line`(改用既有 `INV_TAG_RE`/`invariant_test_refs`,不是重寫這兩支被 Check T/K 依賴的共用函式本身)、`_notes_status_flipped` 家族、`_drift_*` 家族、`_drift_gate_doctor_lines`,都不落在這些節點宣稱要管的範圍內,且新增/改動的程式都落在既有的家(`存量漂移守衛.md`、`筆記內容審.md`、`guard-kill.md`)裡,沒有新開沒家的檔。不影響。
- **Systems/存量漂移守衛.md**(★家★,本輪主體):見上面「已看,無 finding」段與 F1/F2,已逐條核對過這篇自己宣稱的機制(五種一致檢查共用、settle 改寫共用同一支、開關提醒位置、判不了算要處理)跟程式碼一致,除 F2(批次讀預算未扣掉已花時間)之外沒有落差。
- **Systems/lumos-cli-write.md**(★家★,寫入類指令的合約):這輪的 `atomic_write_verify` 呼叫模式(settle/plan/abandon)沒有新開寫入路徑,沿用既有的「寫 tmp 自驗再換名」機制,沒有繞過。不影響。
- **Projects/雙向門放行_計劃.md**、**Projects/規格落成可驗收條件_計劃.md**、**Projects/逃逸自動記_計劃.md**、**Projects/公開精簡版_實作計畫.md**、**Projects/存量漂移防線_計劃.md**、**Projects/code側刪除傳播守衛_實作計畫.md**、**Projects/派工鏡頭注入_計劃.md**:皆是計劃筆記,非程式合約;`存量漂移防線_計劃.md` 正是這輪要兌現的規格本身,已在正文逐條核對(`[S2]`、`_notes_status_flipped` 共用段落的說明已在這輪同步更新,但 F1 顯示程式本身仍有缺口)。其餘計劃跟本輪主題無直接交集,不影響。

最嚴重等級是 blocker,blocking 共 2 條(F1、F2)。
