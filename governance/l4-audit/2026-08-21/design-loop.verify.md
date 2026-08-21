C1 [✅] canary 植入/判定協議在操作層已標示停用、`loop next` 殘留的 caught/missed 樣板明文要求跳過(封存未拆,非刪除) | 證據: skills/lumos-design-loop/SKILL.md:11(「工具封存未拆」)、scripts/lumos:4877-4888(record_cmd 仍印 caught|missed 樣板,但同一 emit() 於非 legacy/light 時另吐 disposal_cmd 作為現行路徑,4882-4888)

C2 [✅] 現行輪記帳改用 `lumos canary record none`,kind 仍接受 caught/missed 供歷史回放但 skill 層指示一律用 none | 證據: scripts/lumos:14246(`choices=("caught","missed","none")`)、skills/lumos-design-loop/SKILL.md:11

C3 [✅] panel「none 制」輪有效之數字門檻確為 ≥2(但非僅此一條,另合取零 missed) | 證據: scripts/lumos:3524-3532(`_round_valid_m2`:`(kinds.count("caught")+kinds.count("none"))>=2 and kinds.count("missed")==0`)、3578-3583(`_panel_round_conjuncts` 印「記帳席 N」「≥2」)

C4 [✅] 收斂機制自 2026-08-04 起改走處置閘(`--disposal`),為 design-loop 現行推薦路徑 | 證據: scripts/lumos:4332-4336([T4 處置閘] 獨立路徑,design-loop重設計 d2/B5)、skills/lumos-design-loop/SKILL.md:16-17(「★收斂改走處置閘★」)

C5 [❌] 「K-streak∧capture-recapture∧存活≤minor 三合一硬閘已退場」不準確——panel 舊三合取中只有 capture-recapture 一項降為 advisory,另兩條(輪有效∧存活≤minor)仍是必要合取且 2026-08-05 起對新 loop 還加嚴為 K=2(兩輪各自過);「K-streak」一詞在程式碼裡實際專指 legacy 模式(K=2∧G1∧G2),與 panel 三合取是兩套機制,claim 把兩者混為一談;「1/38 從未放行」全庫搜不到出處 | 證據: scripts/lumos:3604-3620(capture-recapture 降 advisory,另兩條合取原樣印✓/✗)、3706-3708(`_panel_k2_active`/K=2 於 2026-08-05 起對新 loop 生效,非退場而是加嚴)、4483-4492(K-streak 一詞只出現在 legacy `--gate` 分支)

C6 [✅] capture-recapture 殘餘估計自 2026-08-14 起降為 advisory,不進收斂合取,鑑別力≈0 的量化陳述與程式碼註解逐字一致 | 證據: scripts/lumos:3604-3609(「★2026-08-14 降 advisory,不進合取★」)、3796-3805(cluster 帳同款降級)、skills/lumos-design-loop/reference.md D1 段(「殘餘<門檻 ⛔ 2026-08-14 降 advisory 不進合取(鑑別力≈0:67% vs 對照 79%,p≈0.25)」)

C7 [✅] code-loop 已於 2026-08-08 改走處置閘、經具名裁定推翻原防浮動條款,A 案舊機制碼(含 `t_panel_k2_and_probe`)保留供歷史帳重放而非刪除 | 證據: skills/lumos-code-loop/SKILL.md:16-17(「2026-08-08 閘切換...原刻意分流/不得改本檔警語與 A 案防浮動條款經 Enzo 具名推翻」)、SKILL.md:20(「A 案(K=2+抽查)機制碼與 t_panel_k2_and_probe 保留不刪(舊帳重放消費)」)、scripts/test_lumos.py:12457(`t_panel_k2_and_probe` 仍存在且測試綠燈,已執行驗證)

C8 [✅] dispatch manifest(rN-dispatch.json)宣告 materials,分類 unreported/out_of_scope,越界記入 out-of-scope.jsonl 不進收斂帳,materials 空時 vacuous 豁免恆 rc0 | 證據: scripts/lumos:4663(讀 `rN-dispatch*.json`)、9995-10064(`cmd_seat_check`:10017-10023 vacuous 豁免、10036-10064 out_of_scope 與 ledger 寫入、10004「恆 rc0」)、14634-14637(CLI `seat-check --dispatch/--ledger`)

C9 [✅] seat-check 有機械測試 `t_s1_seat_check`,已實跑驗證通過(6 passed 0 failed) | 證據: scripts/test_lumos.py:20079;實跑 `python3 scripts/test_lumos.py -k t_s1_seat_check` → 6 passed, 0 failed

C10 [✅] quote-check 對「凍結快照」做逐句機械比對,作為審計員讀過材料的把關手段 | 證據: scripts/lumos:9552-9566(`cmd_quote_check` docstring 明列「比對對象必須是派工當下的凍結快照,不是現檔」)、9552(函式簽章 `report, spec`)

C11 [✅] `lumos loop status --gate` 支援 legacy(預設)/panel/light/settle 四模式並互斥處理(另有獨立的 --disposal 第五路徑,不與 claim 衝突) | 證據: scripts/lumos:4324-4326(light∧panel 互斥報錯)、4341-4353(settle 與 panel/light 互斥、與 --need/--min-seats 互斥)、4332-4336(--disposal 與其餘旗標互斥,獨立路徑)

C12 [✅] legacy 模式 K=2(預設 need)、max cap=6 筆 record,達 cap 停手記「達 cap 未收斂」攤人 | 證據: scripts/lumos:4320-4322(`need is None` → `need=2`)、4573(`_TIER_PARAMS = {..., "legacy": (1, 6)}`)、4976(cmd_loop_next:「cap={cap} 到頂未收斂——停,攤給人裁」)、skills/lumos-design-loop/SKILL.md:150(「max cap ＝ 6 筆 record」);註:cap=6 的機械執行點實際在 `cmd_loop_next`(_TIER_PARAMS)而非 claim 預期的 `cmd_loop_status` legacy 分支本體,但數值一致

C13 [❌] 「panel 收斂 = 輪有效∧存活≤minor 兩條合取」只描述了舊版單輪判準,漏掉 2026-08-05 起(cutoff 2026-08-06,可用 env 覆寫)對新 loop 已加嚴為 K=2——需連續兩輪(判定輪+前一輪)各自都過該兩條合取,今日(2026-08-21)所有新開 panel loop 皆落在 cutoff 之後、K=2 為現行預設路徑,並非 claim 所述的單輪二合取 | 證據: scripts/lumos:3705-3708(`_panel_round_conjuncts` 兩條合取後,3706「[A案 2026-08-05] K=2:cutoff 起的新 loop,收斂需最後★兩★輪各自過三條合取」)、3557-3563(`_panel_k2_active` cutoff=2026-08-06);實跑 `t_panel_k2_and_probe` 綠燈(單一乾淨輪 FAIL、連續兩乾淨輪 PASS)

C14 [✅] light 模式 M1 為單席機械謂詞,FAIL 區分 retryable/ratchet 兩因 | 證據: scripts/lumos:4424-4426(ratchet:「已有 caught 輪 severity≥major,永久升 standard」)、4434-4435(retryable:「末輪 missed(判決不採信;light cap=2 內可重試)」)

C15 [✅] Component A 原語有測試覆蓋:`canary record --loop/--severity` 見 `t_canary_loop_fields`,`loop status --need` 見 `t_loop_gate_need3`,兩者實跑皆綠燈 | 證據: scripts/test_lumos.py:3205(`t_canary_loop_fields`)、208(`t_loop_gate_need3`);實跑分別 3 passed/1 passed, 0 failed

✅11 ❌3 ❓0 ⏭0
