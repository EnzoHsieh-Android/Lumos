severity: minor

# 代碼審 r3 正確性席(末輪)

做法:逐 hunk 挑具體輸入走執行路徑,再走資料狀態五問(新舊互讀、寫一半、衍生資料、時間、不可逆)。實驗都在 clone 出來的臨時目錄(`scratchpad/x/w`)做,沒碰 repo。基線先跑 `python3.14 scripts/test_lumos.py -k ns_append`:88 passed、0 failed。另外對 `_ns_append_subtract` 做了突變:把「只扣照片段比的規則」還原成 r1 的「只有沒寫來源不扣」,`t_ns_append_line_rules` 兩條斷言當場紅,所以新測試有咬合力,不是假綠。

沒有找到 major 以上的問題。上一輪七項修法逐項走過,結論見「沒問題的項目」。下面是新發現的 minor。

## 發現

**C1 回頭條件兩條規則也變成「從不扣」,但計劃和程式裡的鍵表還說它們照(規則, 改法)扣**
severity: minor
blocking: 否 — 行為是偏嚴的方向、不會放過違規;問題是計劃與程式內部說法對不上、也沒測試釘住這個行為變化
引句:「if v[2] not in _NS_FRAG_KEY_RULES:」
1. r1 的程式只有「現況描述沒寫來源」不扣,其餘(含 `_NS_REVISIT_RULES` 的「回頭條件格式不合」「條件寫錯」)都照(規則, 改法)計數扣掉。r3 這行改成「不在 `_NS_FRAG_KEY_RULES` 就不扣」,於是這兩條回頭條件規則也一起變成從不扣。
2. 重現(在 clone 上直接呼叫 `_ns_append_subtract`,配對表給一行舊 REVISIT):`回頭條件格式不合 → 留下 1 扣掉 {}`、`條件寫錯 → 留下 1 扣掉 {}`、對照 `程式行號引用 → 留下 0 扣掉 {('N.md', 5): [...]}`。
3. 實際影響:起點版本裡本來就寫壞的 `REVISIT:` 行(開頭不是日期也不是條件標記),只在句尾補一段更正括號,現在提交會因為「回頭條件格式不合」被擋;r1 會放行。這個方向跟 r2 「整行層級一律不扣」的裁決一致,可以接受,但:
   - 計劃〈做法〉2 第 61 行(本 diff 沒動到,是 diff 上下文)還寫「`_ns_revisit_violations` 對 N 與 O 各算……鍵(規則, 改法)……補一個寫錯的條件會照報」,讀起來是會扣的。
   - `_ns_viol_key` 的 `_NS_REVISIT_RULES` 分支現在是死碼(能走到它的違規都在 `if v[2] not in _NS_FRAG_KEY_RULES` 之前被擋掉),它的 docstring 還說「回頭條件照(規則, 改法)」。
   - 新增的 `t_ns_append_line_rules` 只測 SEE 與不評估的條件標記,沒測這兩條回頭條件規則,行為變化沒有任何測試釘住。
   - 佐證:file: `scripts/lumos:27694`(`_NS_REVISIT_RULES`)、`scripts/lumos:27697`(`_ns_viol_key`)、`docs/lumos-toolchain-knowledge/Projects/舊行尾追加不算新寫_計劃.md:61`。
4. 修法方向:要嘛把這兩條也寫進「整行層級不扣」的清單並補一個測試,同時刪掉 `_ns_viol_key` 的回頭條件分支與計劃第 61 行;要嘛維持扣減並把判斷改成「照片段比的 + 回頭條件」。

**C2 放寬帳去重只認(路徑, 行號),同一次推送的不同分支撞到同一個位置時,後一筆被吞掉,「只多記、不少記」不成立**
severity: minor
blocking: 否 — 只影響放寬帳的計數與抽樣剔除,不影響擋或放
引句:「fin = {k: r for k, r in (relaxed.get("by_line") or {}).items() if k not in seen}」
1. 輸入:同一個 `LUMOS_PUSH_ATTEMPT=att-1`,掛鉤逐分支呼叫兩次。分支甲的 `N.md` 第 3 行放寬了「程式行號引用」(head_sha=tipA),分支乙的 `N.md` 第 3 行是另一份內容、放寬了「釘版本不合法」(head_sha=tipB)。
2. 走到 `_ns_relaxed_recorded`:回 `{("docs/k/N.md", 3)}`;`fin` 用(路徑, 行號)當鍵過濾,乙的唯一一行被濾光,`if fin:` 為假,乙那筆不寫。
3. 重現(clone 上直接呼叫 `_ns_relaxed_record` 兩次,env 同一個 attempt):`1 [('tipA', 'done', {'程式行號引用': 1})]`,tipB 那筆沒有。
4. 壞在哪:計劃〈做法〉5 與函式 docstring 寫「帳裡 pairs 被裁掉的行會再記一次(只多記、不少記)」,但不同分支、不同內容撞同一個(路徑, 行號)時是少記。「否定現況句」計劃第 4 節的抽樣剔除靠這份帳,少記的那行不會被剔除,分母會多一行。去重鍵應該帶上 `head_sha` 或舊行內容雜湊。
5. 佐證:file: `scripts/lumos:29493`(`_ns_relaxed_recorded`)。

**C3 放寬帳去重在沒有任何違規被放寬時也讀整份治理帳檔尾(最多 24 MB)**
severity: minor
blocking: 否 — 每條分支每次推送多約 0.2 到 0.3 秒與一百多 MB 暫時記憶體,不影響判定
引句:「seen = _ns_relaxed_recorded(root, os.environ.get("LUMOS_PUSH_ATTEMPT", "").strip())」
1. 輸入:任一次經推送前掛鉤的 `note-shape --diff`(`LUMOS_PUSH_ATTEMPT` 一定有值),這次沒有任何補括號的行被放寬(最常見的情況)。
2. 走到 `_ns_relaxed_record`:推送模式 `relaxed` 在 `_ns_relaxed_settle` 之後恆有鍵(`count`、`rules`、`pairs`……),所以 `if not relaxed: return` 不會早退;`capped` 為假;接著無條件呼叫 `_ns_relaxed_recorded`,把檔尾最多 24 MB 整段 decode、split、逐行 `json.loads`。
3. 重現:造 24 MB、約 8.7 萬行的 `docs/.governance-log.jsonl`,`by_line` 傳空字典呼叫 `_ns_relaxed_record`,讀帳次數 1,耗時 0.24 秒(`_ns_relaxed_recorded` 單獨 0.30 秒,峰值 RSS 約 176 MB)。這個 repo 自己的帳檔已經 16 MB。
4. 壞在哪:只有 `by_line` 非空才需要去重,先判 `if not relaxed.get("by_line"): return` 或把讀帳放到 `fin` 為空之後,就不會在絕大多數推送白讀。r1 併發席特別看過這類推送路徑成本。
5. 佐證:file: `scripts/lumos:29511`(`_ns_relaxed_record`)。

**C4 〈舊行尾追加不算新寫〉計劃自己的〈做法〉8 還寫「重產時跳過放寬帳 pairs 記的行」,跟本 diff 改寫後的另兩處說法相反**
severity: minor
blocking: 否 — 文件前後矛盾,沒有程式行為受影響
引句:「量測程式不分、會多算,抽樣時人工剔除,見 [[Projects/舊行尾追加不算新寫_計劃]]」
1. 本 diff 把〈否定現況句配回頭條件〉計劃第 4 節與〈做法〉7 第 3 步都改成「放寬帳幫不上,它只在推送時記、只記有違規被減掉的行,提醒卻在提交前算,所以抽樣時人工剔除」。
2. 但〈舊行尾追加不算新寫〉自己的〈做法〉8「同步要改的字句」第 100 行(本 diff 沒動)仍寫「重產時跳過放寬帳 `pairs` 記的行,帳有 `pairs_truncated` 就註明抽樣不完整」,而且那份計劃的〈審計修正紀錄〉也沒提到這個改動。讀這份計劃的人會以為量測程式會跳過放寬帳的行。
3. 另一份相關計劃 `舊行插字不算新寫_計劃.md:53` 有同樣的舊說法。
4. 佐證:file: `docs/lumos-toolchain-knowledge/Projects/舊行尾追加不算新寫_計劃.md:100`、`docs/lumos-toolchain-knowledge/Projects/舊行插字不算新寫_計劃.md:53`。

## 固定席節點

逐條判斷(改動範圍是筆記形狀擋第一層、筆記內容審第二層的配對與申訴、放寬帳、測試與三份計劃和筆記):

- reversibility-governance-ledger(RISK):不破壞它宣稱的行為。新增的 `capped` 放寬帳只有在推送模式有違規被查到時才會記(`table()` 只在有違規時被呼叫),仍符合「沒違規的放行不寫帳」的例外範圍;讀帳去重是新增的讀者,對尾端被併發寫到一半的行靠 `_drift_jsonl_iter` 容錯。唯一的成本是 C3(多讀帳),和 C2(去重鍵過粗少記),兩者都不改變該節點說的 `_gate_event_fit` 共用裁法或 `relaxed` 例外。
- lumos-cli-read(INVARIANT:search 預設排除 superseded):不影響,diff 沒碰搜尋與濾網。
- bound-tests-gate(INVARIANT):不影響合約本身。新增的 S47 到 S50 計劃條款綁的五支測試都在 `scripts/test_lumos.py` 裡存在,既有綁定的測試名(`t_ns_append_caps`、`t_gate_event_fit_bisect`、`t_note_audit_append_scope_more`、`t_ns_append_r1_minor_folds`)都保留。
- guard-kill(INVARIANT):不影響,diff 沒碰 guard kill 的 rc 優先序或 JSON 輸出。
- 授權與歸屬(INVARIANT):不影響。`scripts/lumos` 的改動從第 27530 行之後才開始,檔頭 SPDX 與 MIT 全文沒動,沒有新增被複製的檔。
- 測試假綠形態(INVARIANT:還原翻紅釘要配前置斷言):遵守。七支配對測試改成「舊行就有的行號引用 + 帶來源的括號」,並各補「改一個字配不上時照報」或「正常補括號不擋」的前置斷言;`t_ns_append_line_rules` 我做了突變(還原成 r1 的扣法)確實翻紅。唯一小缺口:該測試 docstring 寫了「對照:只扣照片段比的行號引用」,函式體裡沒有這條對照,但突變證明它仍有鑑別力,所以不單獨列為發現。
- pitfalls-code-loop(RISK):不影響,diff 沒碰風險分級或實務隱患筆記的程式。
- design-loop(INVARIANT:處置閘第五步,計劃條款綁測試):不影響,新條款 S43 到 S50 都是「當…應…」句式並綁了存在的測試,S39 維持 manual。
- 其餘「超出上限只列名」的十八個節點(lumos-cli-lifecycle、loop-convergence-recording、節點範圍與索引守衛、lumos-deinit、check-t-sentinel、cochange-guard、check-r-guard、doctor-irreversible-hint、lumos-refcheck、canary-audit、slim 三篇、規格落成可驗收條件_計劃、雙向門放行_計劃、逃逸自動記_計劃、core-invariant-baseline、judge-severity-gate):逐篇 grep 過 `note-shape`、`note-audit`、`舊行尾`、`relaxed`、`_gate_event_fit`,全部 0 筆,這份 diff 不會讓它們的說法失真。另外 grep 過 `lumos-relaxed-seen`、`_ns_relaxed_seen`、`記號放 git 目錄`,repo 內已無殘留引用。

## 沒問題的項目

上一輪七項修法逐項挑輸入走過,沒有找到會出錯的輸入:

- 只扣照片段比的規則(`_NS_FRAG_KEY_RULES`):SEE 夾句子加補括號、表格列已有不評估的條件標記加補括號,都照報(突變證明測試咬合);「程式行號引用」括號裡重複舊行同一個引用仍被扣、括號裡新的引用照報。`_ns_check_line` 產生的規則名只有「釘版本不合法」「程式行號引用」「SEE 只放連結」「現況描述沒寫來源」四個,分組表涵蓋完整,沒有漏掉的片段型規則。
- 候選上限回 `"cap"`:篇數、對數、位元組總和三種都由 `t_ns_append_caps` 各自驗過;`_nodehome_cat_sizes` 對不存在的版本回 None,不會被加進總和;提示只在第一次查表印一次;`failed` 與 `capped` 互斥;`_ns_relaxed_record` 的 capped 帳只在 `table()` 被呼叫(有違規)時才會有。
- NFC 與 NFD 並存:`_nodehome_list` 的第二個回傳值確實逐筆 NFC 化且不去重(讀過原碼),`Counter` 數得到並存;只在有新行的篇上擋;第一層經 `errs` 進 `_note_shape_report`(warn 模式印出不擋、block 模式擋),第二層經 `check` 的 `errs` 擋;doctor 事後掃描忽略 errs,不會誤唸。
- 同一次推送的放寬帳去重改讀治理帳:`attempt_id` 在 `_gate_event_build` 寫成 `att[:64]`,讀端用 `att[:64]` 比,一致;帳檔不存在或沒有 `docs/` 時回空集合;壞行由 `_drift_jsonl_iter` 跳過。
- 只判句尾的申訴只換同一個句尾:`{None, row.get("tail")}` 對整行列只剩 `{None}`,對句尾列含兩者;整行申訴換每一種範圍、句尾申訴不蓋整行 CODE、兩種都有取最重,`t_note_audit_dispute_scope` 六條斷言覆蓋;`_note_audit_fold`、`_note_audit_class_for`、`_note_audit_show_class` 三處用同一份 fold,顯示用語三種分類正確。
- 讀被刪摘要行補上的兩個旗標:`--inter-hunk-context=0`、`--diff-algorithm=myers` 與 `_ns_diff` 一致,`-U0` 下順序無關。
- 測試改法:牆上時鐘門檻改成呼叫次數(`_gate_event_fit` 兩萬筆約 17 次組事件,上限 40)與相對倍數(取三次最快,十倍輸入不到 30 倍),在忙的機器上不會誤紅;整份 88 條通過。
- 時間與新舊互讀:舊的 git 目錄記號檔不再被讀,留著無害;`tail` 欄與舊判定檔相容性沒被動到。

最高 severity:minor
