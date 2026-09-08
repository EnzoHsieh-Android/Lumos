severity: blocker

# 條款綁測試算進度 code-clause-bindings r2 末輪驗收(單 reviewer)

被審:`governance/review-reports/code-clause-bindings/r2-snapshot.patch`(全量,1221 行,凍結)+ `r2-delta.patch`(本輪折入,960 行)。
方法:13 條逐一讀 diff 對照 r1 三份席報告的重現法,再用 `_load_lumos_inproc()` 直接呼叫 `clause_bindings`/`_disposal_clause_step` 重現或反例;`python3 scripts/test_lumos.py -k clause` 46 案例全綠(基線,非驗收依據)。

## 13 條逐一驗

### f1 只在範例/引用出現的 id 不算條款(undefined 態)
修了但引入新洞(見新 finding 1)。核心邏輯本身(獨立一行的範例/引用)修對:
引句:「只在範例/引用/行內出現過、從沒在行首定義 → 不是條款(r1 單reviewer blocker:純示範文字曾讓閘 FAIL)」
但修法把「lead 行上所有 [SN] 都算定義」寫成整行一視同仁,製造了同一行裡「真定義＋反引號範例」共存時的新反例——見新 finding 1,原 blocker 的症狀（合規計劃被閘擋）原樣重現。

### f2 表格列算定義行
修好。`_CLAUSE_LEAD_RE` 字元類加了 `|`,測試 S13(表格列)判 `bound`,`t_clause_bindings_states` 綠。
引句:「條款「定義行」:行首(去列表/標題/粗體/表格 | 符號)就是 [SN]」

### f3 顯式 root 贏過 env 反推
修好。`_clause_bindings_for` 改成 `root` 真值優先,呼叫端 `_dsp_root` 恆非 None(`Path(repo).resolve() if repo else _vault_repo_root(env)`),沒有走到「root 給了卻被蓋掉」的分支。
引句:「顯式 root(呼叫端已照 --repo 覆蓋規則算好)贏,env 反推只是預設——跟 _loop_status_disposal 其餘四步同一條優先序」

### f4 cutoff 改隔日 2026-09-09T00:00+08:00 且用 `_loop_ts_key` 換算 UTC、壞 ts fail-closed
修好。實測 `docs/.canary-log.jsonl` 全部 1200 筆 `ts` 都帶時區(python 逐筆解析核對),`_loop_ts_key` 對缺時區回 None 不會誤傷既有帳;壞值(`0000-00-00...`)`fromisoformat` 拋 `ValueError` 正確 fail-closed。
引句:「處置閘的條款綁定步只看首筆帳在這之後的迴圈——不回溯舊迴圈(週跑回放會重跑閘,回溯=舊判定全翻)」

### f5 跳過看 `_roster_kind`(code- 才跳),設計審拿 .patch 當審材 FAIL
修好。`kind == "code"` 才 skip,`kind is None`(如 `"code"` 無連字號的舊帳形態)也 skip 但訊息不同,其餘(design)才進 `.md` 副檔名檢查且不過就 `fail`(非 skip)。測試 `cg-d`/`code-cg` 兩案分流正確。
引句:「kind = _roster_kind(loop_id or "")」

### f6 `[manual:]` <4 字視同未標
修好。`_MANUAL_MIN_CHARS = 4`,用 `len(x.strip()) >= _MANUAL_MIN_CHARS` 過濾,S14(空)/S15(1 字)判 `untagged`,S16(4 字)判 `manual`,測試綠。
引句:「manual = [x.strip() for x in MANUAL_REF_RE.findall(seg) if len(x.strip()) >= _MANUAL_MIN_CHARS]」

### f7 `MANUAL_REF_RE` 搬進標記叢、收進 `INV_TAG_RE`
修了但引入 X(minor)。搬位置與收編都做了,`strip_test_refs`/`Check T`/`guard` 的呼叫端(3563/4022/7807/7833/7935/7943/8622 等處)邏輯本身不受影響,因為 `invariant_test_refs` 仍只讀 `TEST_REF_RE`(內容要求 `+`,未變)。但這次改動把 `INV_TAG_RE` 整體的內容量詞從 `[^\]]+` 放寬成 `[^\]]*`——不只 manual,连 test/audit/kill/src/git 都變成允許空內容。實測:`strip_test_refs("★INVARIANT★ 一句宣稱 [test:]")` 現在把畸形的空 `[test:]` 靜默剝乾淨(舊碼會留在乾淨文字裡),`裸 ★INVARIANT★` 錯誤訊息仍會觸發(`refs` 仍算空)但顯示片段少了這個線索,診斷降級,非功能性擋不住的洞。
引句:「INV_TAG_RE = re.compile(r"\[(?:test|audit|kill|src|git|manual):\s*[^\]]*\]")」

### f8 docstring、`--help`、commands/03、INDEX.md、docs/指令參考.md、docs/command-reference.md 語意
修好。六處全部核對過:`cmd_spec_trace` docstring、argparse `--help`、`commands/03-寫回圖譜.md`、`commands/INDEX.md`、`docs/指令參考.md`、`docs/command-reference.md` 都换成「裁決=條款行綁定,舊制回指只當對照」的新語意;另外多改了 `commands/05` 與 `skills/lumos-project-notes/reference.md`(超出原六處要求,非壞事)。
引句:「條款級追溯:計劃 [SN] 條款那一行綁的 [test:]/[manual:](裁決,有未標 rc1)× 回指 Verification 認領(舊制對照欄)」

### f9 spec 讀不到的措辭對齊 G3
修好。`_disposal_clause_step` 的讀檔失敗訊息改成「--spec 指的文件讀不成文字(…),確認路徑對不對」,與 G3 的「--spec 指的文件讀不到(…),確認路徑對不對」用詞一致(嚴重度仍是 fail 併入 fails 清單、非 rc2 立即中斷,r1 架構席原文承認這是「描述不一致不是一定同時觸發」,措辭層面已對齊)。
引句:「[disposal] 條款綁定: ✗ — --spec 指的文件讀不成文字({e.__class__.__name__}),確認路徑對不對」

### f10 spec-trace 提醒改兩行
修好。`cmd_spec_trace` 與 `_disposal_clause_step` 的 FAIL 分支現在都印同一句「每條要嘛在那一行綁…」,兩處排版一致。
引句:「每條要嘛在那一行綁 [test:測試名],要嘛寫 [manual:一句怎麼驗];沒有測試可掛也得講清楚靠人怎麼驗」

### f11 閘測試補真索引「綁了→過」「懸空→只提醒」
修好。`t_disposal_clause_gate` 新增 `cg-j`/`cg-k` 兩案,用 `_clause_repo`(真 git repo + `.lumos/config.json` + `tests/test_t.py`)驗證「綁了真測試 → PASS」與「懸空(寫錯+只被提到)→ 只提醒照過」,不再只用 `[manual:]` 撐過。
引句:「clause-gate: 真索引懸空(寫錯+只被提到)→ 只提醒照過」

### f12 fixture 加「只被提到」
修好。`_clause_repo` 的 `tests/test_t.py` 加了一行只在註解出現、不是 `def` 的字串,`t_spec_trace_clause_table` 用 `[test:t_mentioned]` 走真索引驗到 `mentioned` 態。
引句:「(d / "tests").mkdir(); (d / "tests" / "test_t.py").write_text("def t_ok():\n    assert True\n# t_mentioned 只在這句註解出現,不是 def\n", encoding="utf-8")」

### f13 審材裡別人的碼已拆掉
修了但引入 X(見新 finding 2)。指名檢查的三個識別字(`_scope_policy`/`_lumos_config_near_vault`/`t_lint_scope_policy`)在 `r2-snapshot.patch` 與 `r2-delta.patch` 裡確實都搜不到,也不在提交 `802fdad`/`0e1faab` 的 `scripts/lumos`/`scripts/test_lumos.py` 變更裡——程式碼污染真的清乾淨了。但同一支修復提交(`0e1faab`,就是折入這 13 條的那一次)另外夾帶了一段跟條款綁定完全無關、屬於同一個「工具分類」污染源的**文件**改動(`skills/lumos-project-notes/reference.md` 的 `scope/` 標籤家族說明列),第五型並行事故換了個檔案重犯一次。
引句:「★審材混進另一個 session 未提交的碼(第五型第三次),拆 commit 重做★。決策 d4 訂正 d3。」

---

## 新 finding

### 新 finding 1
severity: blocker
blocking: 是——判準:與 r1 單reviewer 原 Finding 1(blocker)同一種症狀(全部條款皆已綁定的合規計劃,仍被閘判 FAIL),只是觸發位置從「跨行」改成「同一定義行內」,原修法沒堵住這個變體。
引句:「if lead is not None:          # 定義行:這一行所有 [SN] 都算定義,各認到下一個 [SN] 之前」
file: `scripts/lumos:4118`

當「真定義」與「反引號範例/表格參考」的 `[SN]` 出現在**同一行**(而不是像測試 fixture 那樣分成兩行)時,新邏輯把該行內找到的**所有** `[SN]`(不只 lead 那一個)一律計入 `defined`,於是範例 id 被誤判成待標記的真條款。實測(`_load_lumos_inproc()` 直接呼叫):
```
text = "### [S1] 真條款 [test:t_ok],例如 `[S9] 範例格式`\n"
```
`clause_bindings(...)` 回傳 `S9` 為 `{'defined': True, 'state': 'untagged'}`;接著對 `_disposal_clause_step([{'ts': '2026-09-10T10:00:00+08:00'}], spec, root, None, loop_id='cg-repro')` 真跑,輸出:
```
[disposal] 條款綁定: ✗ — 1/2 條驗收條款沒標:S9(第 1 行)
```
S1 明明已綁 `t_ok`,閘卻因為同一行裡的範例文字誤判 FAIL——這正是 r1 blocker 原本要堵的洞,只是換了個「同行」的殼。

### 新 finding 2
severity: major
blocking: 是——判準:折入 13 條的修復提交本身重演了 f13 剛裁定的同一種契約違反(凍結審材混進另一個 session、另一個計劃的未完成內容),破壞審查邊界的完整性,且該文件描述的 lint 行為在這條分支上完全沒有對應程式碼實作(讀者會被導向一個不存在的功能)。
引句:「值域由專案自己宣告在 `.lumos/config.json` 的 `scope` 區塊(`{"values":[…],"required":true}`)——宣告了 lint 才唸」
file: `skills/lumos-project-notes/reference.md:373`

用 `git show 0e1faab -- skills/lumos-project-notes/reference.md` 核對:折入 13 條的那次提交(即本輪要驗收的修復本身)夾帶了 `scope/` 標籤家族說明列的整段改寫,提到 `.lumos/config.json` 的 `scope` 區塊、`Projects/工具分類_計劃`——這是另一個計劃的功能敘述,跟條款綁定無關。用 `git show 802fdad --stat` 核對,產生條款綁定功能的原始提交完全沒碰 `reference.md`;`grep -rn "_scope_policy" r2-snapshot.patch r2-delta.patch` 兩份審材都是 0 命中,但目前 `scripts/lumos:3834` 確實有 `def _scope_policy`——只是還在工作樹裡未提交。也就是說:折入修復時,程式碼污染被正確地留在工作樹沒進 commit,**但描述同一功能的文件卻進了 commit**,兩者現在互相矛盾(文件說有,程式碼說沒有)。

### 新 finding 3
severity: minor
blocking: 否——判準:只影響「裸 ★INVARIANT★」錯誤訊息裡片段文字的可讀性(仍會正確擋,`refs` 判斷邏輯不受影響),不改變任何 rc 或放行結果,未能找到會翻紅的路徑。
引句:「INV_TAG_RE = re.compile(r"\[(?:test|audit|kill|src|git|manual):\s*[^\]]*\]")」
file: `scripts/lumos:3041`

新增 `manual` 時,連帶把整個聯集的內容量詞從 `[^\]]+`(至少一字元)放寬成 `[^\]]*`(可零字元),不是只加 `manual` 一項。實測:`strip_test_refs("★INVARIANT★ 一句宣稱 [test:]")` 在新碼下把畸形的空 `[test:]` 標記靜默剝除(舊碼下 `[^\]]+` 不會匹配空內容,標記會原樣留在「乾淨宣稱文字」裡當作可見的資料錯誤線索)。`invariant_test_refs`/`TEST_REF_RE` 仍要求 `+`,所以「裸 ★INVARIANT★」錯誤本身照樣觸發,只是顯示的片段少了這個視覺線索,診斷精度降級。

---

## LUMOS-IMPACT: Lumos/main..HEAD

固定席合約節點逐條答會不會破壞:

- `lumos-cli-read.md`(search 排除 superseded/stale):不影響,本輪改動沒碰 `cmd_search`/濾網。
- `bound-tests-gate.md`(code-loop 固定席合約測試逐支真跑):不影響,沒碰 code-loop bound-tests 檢查函式。
- `canary-audit.md`(record/second readback + second 純 telemetry):不影響,`_disposal_clause_step` 只讀既有 `rows` 的 `ts` 欄位,沒碰 `cmd_canary` 寫入/second 邏輯。
- `guard-kill.md`(rc 優先序/json 純淨):不影響,沒碰 `guard kill` 路徑。
- `slim-get-一行安裝.md`/`slim-install-安裝器.md`/`slim-uninstall-一行卸載.md`:不影響,沒碰任何 `.ps1`/slim install/uninstall 函式。
- `授權與歸屬.md`(LICENSE 白名單/SPDX):不影響,沒新增檔案、沒碰 `_VENDORED_TOOLKIT`/deinit 白名單。

新 finding 3(`INV_TAG_RE` 量詞放寬)雖然改到 `strip_test_refs` 這個 Check T/guard/contracts 共用的函式,但實測「裸 ★INVARIANT★」判定邏輯只看 `invariant_test_refs`(`TEST_REF_RE` 未變),放行/擋下結果不變,只是錯誤訊息片段的可讀性降級——不構成對上述任一 ★INVARIANT★ 節點的破壞。

## 總結

最高 severity:**blocker**(新 finding 1;13 條裡 f1 因此判「修了但引入新洞」)。
blocking 條數:**2**(新 finding 1 blocker、新 finding 2 major);另有 f7/f13 各附一條 minor/major 引入項(f7 之 X 已併入新 finding 3,f13 之 X 即新 finding 2,不重複計數)。
