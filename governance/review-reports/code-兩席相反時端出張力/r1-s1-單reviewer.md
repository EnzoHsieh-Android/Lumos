severity: minor

# 審查報告——兩席相反時端出張力(r1-s1 單 reviewer)

逐 hunk 讀完 `r1-snapshot.patch`(1295 行,九個檔:5 篇圖譜筆記/1 篇新 Verification/scripts/lumos/scripts/test_lumos.py/5 篇 skills 文件),並對照現在的 `scripts/lumos` 原始碼把每個可疑處的執行路徑走一遍。另外實跑了 `python3 scripts/test_lumos.py -k tension`(59 通過)與 `-k disposition`(100 通過),兩者皆 0 紅,證實六支新測試在當前實作下確實全綠。

## 逐條發現

### R1 既有 satisfied 的 test: 證據在設定檔壞掉/平台索引壞掉時,錯誤訊息被多包一層,語意變得自相矛盾
severity: minor
blocking: 否——不改變任何 rc/擋不擋的判定,純粹是訊息文字变得難讀,不影響任何既有測試斷言(逐字串包含判斷仍過)。

`_dispositions_verdict` 把 `satisfied` 分支原本「直接回傳一句完整訊息」的寫法,重構成先呼叫共用的 `_ev(ev)` 回 `(ok, why)`,再由呼叫端統一包一層 `f"{qid} 證據對不上:{why2}"`。這個重構本身是對的、也是 tension 的 `chosen=suggested` 需要共用驗法的合理做法——問題是 `_ev` 內部兩個「設定檔本身就壞掉,根本沒辦法驗證」的分支,原本回的字串就已經是「無法驗證」語意,重構後被硬套進「證據對不上」的外層模板,變成雙重否定式的怪句子。

引句:「return None if ok2 else f"{qid} 證據對不上:{why2}"」

diff 對照(從 patch 逐字複製,舊/新各一行):
- 舊(patch 裡的 `-` 行):`return f"{qid} 無法驗證 test: 證據:.lumos/config.json 解析失敗(先修設定檔)"`
- 新(patch 裡的 `+` 行):`return False, "無法驗證 test: 證據:.lumos/config.json 解析失敗(先修設定檔)"`

實際輸入/執行路徑:任一支消費專案的 `.lumos/config.json` 若壞掉解析失敗(`cfg_broken=True`),而某題 `satisfied` 的證據寫成 `test:<名>`——這是既有三值裡最常見的證據形式之一,不需要碰任何 tension 欄位就會踩到——`code-loop check` 現在印出的整句會是「kt-coroutines 證據對不上:無法驗證 test: 證據:.lumos/config.json 解析失敗(先修設定檔)」,而重構前是「kt-coroutines 無法驗證 test: 證據:.lumos/config.json 解析失敗(先修設定檔)」。前者讀起來像是先斷言「證據對不上」又補一句「其實是不能驗證」,對人類讀者是一個新的、更混淆的措辭,且跟本 repo 一貫的「工具輸出白話三段式:發生什麼→為何在意」風格(讀出的訊息不該互相矛盾)有落差。

file: `scripts/lumos:21616`(`_ev` 定義起點)、`scripts/lumos:21621`、`scripts/lumos:21626`(兩個「無法驗證」分支被改成回 tuple)、`scripts/lumos:21630-21632`(satisfied 分支呼叫 `_ev` 並外包「證據對不上」)

驗證:`python3 scripts/test_lumos.py -k disposition` 100 條全過,代表現有測試套件沒有任何一條斷言這個具體字串,這個回歸目前沒有機械守衛接住(fake-green 的反面——不是測試裝飾,是測試本來就沒管到這句話)。因為不影響 rc/擋不擋,只是文字,判 minor、不擋這次推送;若要修,最小改法是讓 `_ev` 對「設定檔本身壞掉」這兩個分支直接回一個已經完整、不會被二次包裝的 why 文案(例如把「無法驗證 test: 證據:」開頭去掉,讓外層「證據對不上:」接得順),或是讓呼叫端偵測 why 是否已經以「無法驗證」開頭就不再加前綴。

## manifest 命中逐條判定

`r1-manifest.json` 的 `claims` 為空陣列、`tier: standard`——沒有命中任何 pitfalls 規則形態。已依派工詞指示不因此略過散文外的 hunk,`scripts/lumos`/`scripts/test_lumos.py` 兩個非散文檔的每個 hunk 都逐段讀過(見上與下面各節),沒有在 manifest 之外另外抓到會被 pitfalls 規則覆蓋卻漏標的資源/併發/效能形態問題。

## 圖譜鏡頭(hook 附的固定席逐條判)

- **Systems/bound-tests-gate**(★INVARIANT★ code-loop check 對固定席合約測試逐支真跑):不影響。這次 diff 完全沒有碰 `_codeloop_guard_verdict` 判定合約測試的路徑,只加了 `_dispositions_verdict`/`_dispositions_validate` 裡 tension 相關分支與 `_tension_candidates_into`;bound-tests 的硬合約(紅/懸空/偽證據→擋)程式碼一行未動。
- **Systems/canary-audit**(★INVARIANT★ record/second 落盤驗證、second 純 telemetry):不影響。diff 沒有任何一段落在 canary record/second 的程式碼區域,牽連檔只是因為 `scripts/lumos` 是同一支巨型檔案。
- **Systems/guard-kill**(★INVARIANT★ rc 優先序、--json 純淨度):不影響。guard kill 相關函式未被此 diff 觸碰。
- **Systems/slim-get-一行安裝**(★INVARIANT★ .ps1 ASCII-only/無保留名 $Args):不影響。此 diff 不含任何 `.ps1` 或安裝腳本改動。
- **Systems/slim-install-安裝器**(★INVARIANT★ CLAUDE.md 注入原地取代/冪等等七條):不影響。安裝器程式碼未被觸碰。
- **Systems/slim-uninstall-一行卸載**(★INVARIANT★ 卸載四步互不阻擋等六條):不影響。卸載程式碼未被觸碰。
- **Systems/授權與歸屬**(★INVARIANT★ LICENSE 白名單/SPDX 檔頭兩條):不影響。這次改動全部落在既有檔案(`scripts/lumos`/`scripts/test_lumos.py`)的中段,檔頭 SPDX/MIT 全文未動,也沒有新增未標示的檔案(新增的只有一篇圖譜 Verification 筆記,不在 `_vendor_toolchain` 白名單掃描範圍)。
- **Systems/測試假綠形態**(★INVARIANT★ 修 bug 的翻紅釘要配前置斷言證明現場成立):與本案直接相關,已在下面「本案特定鏡頭 (d)」逐條核對六支新測試的「翻紅釘」宣稱,沒有抓到假綠形態。
- 其餘超出顯示上限、只列名的節點(`lumos-cli-read`/`lumos-cli-lifecycle`/`pitfalls-code-loop`/`loop-convergence-recording`/`cochange-guard`/`check-r-guard`/`lumos-deinit`/`doctor-irreversible-hint`/`reversibility-governance-ledger`/`check-t-sentinel`/`core-invariant-baseline`/`judge-severity-gate`/`lumos-refcheck`):抽查了跟本案概念最近的 `Systems/design-loop`,其 ★INVARIANT★ 是「處置閘第五步對 [SN] 條款要綁 [test:]/[manual:]」,管的是設計審查流程本身(而本案計劃筆記的 [S1]–[S7] 每條都已附 `[test:...]`),跟這次 code diff 改的執行期程式碼(dispositions/candidates)無關,不影響。其餘節點(CLI 讀寫生命週期、deinit、reversibility 帳、check-r/check-t、core-invariant-baseline、judge-severity-gate、refcheck)按名稱與既知職責判斷,均與 dispositions/tension/candidates 這條路徑的函式無交集(diff 沒有觸碰 `_validate_repo_ref`、reversibility ledger、judge-severity 等相關程式碼,`_dispositions_check_path_line` 雖然共用 `_validate_repo_ref`,但該函式本身這次完全沒被改),判不影響。

## 本案特定鏡頭

**(a) 合法 tension 是否會被擋、rc 是否真的不變**:沒找到反例。`_one` 的 tension 分支對「合法輸入」(existing 1–20 項且每項在被推送樹存在、hazard/suggestion 過門檻且 ≤2000 字、chosen 合法、suggested 時 evidence 可驗)最終一定回 `None`(過),不進 `problems`,`out["blocked"]` 只由 `bool(out["problems"])` 決定;實測 `t_codeloop_check_tension_warns` 的③案例(existing 三項、兩個不同路徑)確認 rc0 且 stderr 印 ⚠ 張力段。唯一找到的落差是 R1(訊息文字,不影響 rc),已如上報告。

**(b) 候選的題是否必在 stack_questions_applicable**:分析成立,不是巧合。`_tension_candidates_into` 只在某 pattern 命中改動檔的**增行**(`added_lines`,已先過 `_stack_changed_ok`)時才可能產生候選;而 `_stack_applicability` 判定某題適用與否,是對同一支 `_stack_norm_line` 正規化後、聚合了該棧**所有** changed_lines(含這支改動檔的增行)去跑同一組 `pats`(when)——candidate 命中的那個 pattern 必然也會在聚合掃描裡命中,使該題 `hits` 非空、`applicable=True`(超過 `ask_all_over_lines` 門檻時全題適用,更不會反例)。`_tension_candidates_into` 刻意只用 `pats` 不用 `pats_raw`(when_raw),不會出現「候選只靠 when_raw 命中卻沒被聚合層算進 when 命中」的落差。測試⑦(簿記路徑同樣增行→無候選且題不適用)與整組 S3 測試組(59 條全綠)驗證了這條不變量在合成樣本上成立。

**(c) 既有 satisfied/na/todo 三值行為有沒有被動到(回歸)**:`na`/`todo` 分支完全沒被觸碰,`satisfied` 分支被重構成呼叫共用的 `_ev` helper——這正是 R1 的來源,一個訊息文字的回歸,rc/擋不擋語意不變。除此之外沒有發現其他行為差異。

**(d) 六支新測試有沒有假綠**:抽兩支逐行想像拔掉實作:
- `t_dispositions_validate` 若拔掉 `_dispositions_validate` 裡 `if st == "tension": errs.extend(...)` 那一段,`status="tension"` 仍會通過 `st not in _DISP_STATUSES` 檢查(tension 已在合法值裡),`errs` 保持空、寫入 rc0——test 裡「①…→ rc2 且講哪一欄」的 12 個壞形狀案例會全部變成 rc0,真的會翻紅,不是裝飾性斷言。
- `t_pitfalls_tension_candidates` 若拔掉 `_pitfall_diff_collect` 裡 `_tension_candidates_into(arch, added_lines, repo_root)` 這行呼叫,`arch.get("tension_candidates")` 永遠拿不到值,①的 `len(c) == 1` 會變成 `len(c) == 0`,翻紅。
兩支都已實跑確認(`-k tension` 59 條全過),docstring 宣稱的翻紅釘與程式碼實際控制流一致,沒有找到假綠。

## 總結

嚴重度最高 minor(R1),blocking 條數 0。合法 tension 不擋推送、rc 不變、候選必適用、三值既有行為除 R1 訊息文字外未被改到、六支新測試均非假綠。
