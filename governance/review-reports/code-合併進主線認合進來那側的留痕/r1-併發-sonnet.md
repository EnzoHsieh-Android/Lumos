severity: minor

實測(唯讀,載入 /Users/enzo/harness/lumos-mergepass/scripts/lumos,cwd=/Users/enzo/harness/lumos-toolchain,b0b48b7b):
- 第一次 `_codeloop_merge_side_lookup`(審查 kinds)約 2.2 秒,成功找到 afb7115 的 passed;其中 git show 讀 19 MB 帳本約 0.55 秒。共約 10 次 git,每次帶剩餘時間當逾時(19.8 → 17.5 秒遞減,子程序逾時由 subprocess.run 殺掉,無殘留)。
- 同一個 cache 再查表態 kinds:0.38 秒(帳本不重讀,但 18 MB 字串仍重新逐行掃一次)。
- 記憶體:maxrss 由約 32 MB 升到約 146 MB(bytes 19 MB + decode 後 str 18 MB + 逐行解析暫存);cache 只活在單次 `_codeloop_guard_verdict` 的區域變數,函式返回即釋放,沒有跨呼叫累積。
- 推送前掛鉤多個 ref:每個 ref 各自呼叫判定、各自重讀帳本,合併提交的 ref 約 2.5 秒/個,線性成長、可接受。
- 期限方向:耗盡時全部走「不認」,審查關是多擋、表態關在紀錄無效路徑也是多擋(見 F1 例外);不是多放。

## F1 淺 clone 檢查的逾時例外沒人接,表態關會被當例外整關放行
severity: minor
blocking: 否 — 需要 git 在剩餘預算附近卡住才會觸發,實測只能以注入 TimeoutExpired 重現;方向是放行表態關但只在「合併提交且目標分支表態無效」這條新路徑
引句:「if _git_is_shallow(repo_root, timeout=max(1.0, deadline - __import__("time").monotonic())):」
說明:`_git_is_shallow` 只接 OSError,逾時會丟 `subprocess.TimeoutExpired`(file: `scripts/lumos:6018`)。其餘 `_merge_side_git` 都把逾時吞成 None,唯獨這一行例外外漏,違反「判不了一律不認」的設計句。外漏後:表態關由 `_codeloop_guard_verdict` 外層 `except Exception` 接成 `_gate_failopen`,整個表態核對被放行(原行為是擋);審查關 `_codeloop_review_block` 沒有 try,例外直接冒到 `check` 子命令成為 traceback(掛鉤怎麼處理非零/例外依掛鉤實作,未驗)。另外 `max(1.0, …)` 的下限讓這一步在期限已盡時還能再吃 1 秒。
重現:python 載入模組後 monkeypatch `subprocess.run`,遇到 `--is-shallow-repository` 丟 TimeoutExpired,呼叫 `_codeloop_merge_side_lookup(".", "b0b48b7bda44769205eca2658644d539e73db107", "d0b2439191f4f16b1a35dcc04fbfd2cf9df83736..b0b48b7b", ("passed","skipped"), {})` → 實測丟出 TimeoutExpired(沒回 (None, 為什麼))。建議:這一步也包 try/except TimeoutExpired 回「判不了」,下限改成 0 即不跑。

## F2 期限在表態關首次查詢時才建立,審查關可能因表態關後面的工作吃掉預算而一律不認
severity: minor
blocking: 否 — 多擋方向、使用者可看到原因並重推;只在表態關已走合併路徑且中間關卡總共超過約 20 秒才發生
引句:「cache["deadline"] = _t.monotonic() + _DISP_BUDGET」
說明:deadline 在第一次 lookup(通常是表態關)那刻起算 20 秒,審查關共用同一個 cache。表態關之後還有受波及合約測試、新增告警閘(跑 linter)等,耗時不計入但都吃這 20 秒;之後審查關的 `_merge_side_record` 第一個 `_merge_side_git` 就回 None,輸出「列不出合進來那一側的提交(git 出錯或時間用完)」,而 side 已經判成功。訊息誤導成 git 出錯,且實際是結構性飢餓而非 git 慢。
重現(實測):同一個 cache 先跑表態 kinds,再把 `c["deadline"]` 設成過去,再跑 ("passed","skipped") → 回 (None, '列不出合進來那一側的提交(git 出錯或時間用完)');換新 cache 同一查詢則回放行事件 afb7115。建議:期限改成每一關各自建(或 side 判定與紀錄查找各自一份預算),或把「期限已盡」與「git 出錯」分開講。
補充:`_codeloop_record_valid_ex(..., timeout=max(0.1, …))` 的 0.1 下限在期限已盡時,merge-base 幾乎一定逾時 → 回 (False, …, unsure=True),被呼叫端當無效跳過(多擋),不會多放;但每個候選紀錄都會各吃最多 0.1 秒、且無法分辨「無效」與「判不了」,訊息只剩最後一句「沒有包含主線頂端…的紀錄」。

## F3 合併側查詢吃掉表態關原本專屬的 20 秒預算
severity: minor
blocking: 否 — 只在慢環境(合併側查詢占掉可觀比例預算)放大既有的「超時 fail-open」面,正常約 2 秒、預算 20 秒
引句:「deadline=_time.monotonic() + _DISP_BUDGET,」
說明:`_dispositions_verdict` 的 deadline 在呼叫處建立,`merge_side()` 在 `_disp_record_for` 裡於逐題迴圈之前執行,等於把約 2 到 3 秒(CI 冷快取可能數倍)從逐題核對的預算裡扣掉;逐題迴圈超時且尚未查出問題時是 over_budget 放行(file: `scripts/lumos:47174`)。表態關以前只花預算在逐題核對,現在新增一段不計入、不可跳過的前置成本,合併提交的表態核對更容易走到「沒查完就放行」。實測前置成本見上。建議:迴圈期限在 merge_side 返回後重新起算,或給合併側獨立預算。

結論:資源面沒有阻擋級問題(約 2.2 秒、約 115 MB 暫時峰值,git 子程序都帶遞減逾時且逾時會被殺、cache 隨單次判定釋放);三條都是期限與例外邊界的 minor,最值得修的是 F1(逾時例外外漏破壞「判不了一律不認」)與 F2(兩關共用且起算過早的期限)。

圖譜鏡頭逐條:pitfalls-code-loop 是這次改動的家,已新增 WHY 與段落,與本鏡頭結論無矛盾,F1/F2/F3 修了應補一句期限語意;lumos-cli-read、guard-kill、lumos-cli-lifecycle、測試假綠形態、design-loop、reversibility-governance-ledger、loop-convergence-recording 的 INVARIANT/RISK 行此 diff 沒有碰到它們的條款(未動搜尋過濾、guard kill rc、re-inject、翻紅釘規則、設計審處置閘),判不影響;其餘「只列名」節點未逐篇讀。
