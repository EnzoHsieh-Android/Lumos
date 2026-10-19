severity: minor

我先走過八個角度:`_node_flavor_of` 原本判 vue 的情況、`_PITFALL_DIFF_TEST_PAT` 的各個消費者、`_kt_flavor` 這組的快取與上限、doctor [F] 範本、`_dispositions_verdict` 的新提示,都找不到 major。`react-idioms` skill 在 `skills/react-idioms` 確實存在。下面三條是查到的缺口。

**固定席(LUMOS-IMPACT 節點)**
- `lumos-cli-read`、`guard-kill`、`lumos-cli-lifecycle` 三份 INVARIANT:這份 diff 沒碰 search 的 superseded 濾網、guard kill 的 rc 與 `--json`、re-inject 的 sentinel,判不影響。
- `design-loop`、`reversibility-governance-ledger`、`loop-convergence-recording`:沒碰處置閘第五步、帳本寫入與收斂紀錄,判不影響。
- `測試假綠形態`:新測試多數有前置斷言,例如 S14 的對照組、S34 的 300 與 301 支對照、S39 的同棧對照。這一條不影響。
- `pitfalls-code-loop`(RISK):它管的棧題、角色卡、`_PITFALL_DIFF_TEST_PAT` 這次都被改,是主要牽連面。上面我追過的幾條呼叫路徑都一致,下面三條 minor 是例外。

**表態記錄**
- 那五題表態(py-eventloop、py-parallel、py-external、py-memory、py-hotpath)講的是 Python 同步程式,和這份 diff 實際改的內容不對應。我對它們不下判斷。
- 這份 diff 的實質風險落在 Node/React/Kotlin 的題組,不在 py-* 題組。

1. `_RAN_EVIDENCE["node-jest"]` 新樣式在 `_kill_cap` 這條讀取路徑上,對帶色碼的 jest 摘要不再命中(退步)
severity: minor
   - blocking: 否
   - diff 段:`_RAN_EVIDENCE` 的 `"re": r"Tests:?\s+[^\n]{0,200}?\b[1-9]\d*\s+passed"`。
   - 問題:新樣式在數字前加了 `\b`,舊樣式沒有。diff 自己的註解承認 `_kill_cap` 逐行 `re.search` 不去色。
   - 具體例(我跑過):輸入是 `Tests:       \x1b[1m\x1b[32m1 passed\x1b[39m\x1b[22m, 1 total`。舊樣式 `Tests:.*?[1-9]\d*\s+passed` 命中,新樣式不命中。原因是 `m` 和 `1` 都是 word 字元,中間沒有 word boundary。
   - 影響:輸出超過 256KB 被截斷、摘要行落在被砍的中段時,`keep_re=_ran_evidence_re(...)` 保不住這行,真的跑過的測試會被判成「證不出跑過」。`file: scripts/lumos:19404`、`file: scripts/lumos:54669`。
   - 為什麼測試沒抓到:S4 的帶色碼案例走 `_ran_evidence_check`,它先去色,所以測不到這條路徑。
   - 修法:把 `\b` 換成 `(?<![0-9A-Za-z])`,或改成 `(?<!\d)`。
   - 引句:「①不錨行首、不加旗標——兩個讀者共用這條字串(_ran_evidence_check 去色後對整段 re.search、_kill_cap 逐行 re.search 不去色)」

2. `_uses_vitest` 只要根目錄有 `vite.config.*` 就判 vitest,不看專案實際的測試依賴
severity: minor
   - blocking: 否
   - diff 段:`_uses_vitest` 的 `for g in _VITEST_CONFIG_GLOBS: if any(p.is_file() for p in root.glob(g)): return True`。
   - 具體例:根目錄有 `vite.config.ts`,`package.json` 的 devDependencies 只有 `jest`(Vite 打包、測試用 jest)。猜到 `node-jest` 後被換成 `node-vitest`,骨架寫出 `npx vitest run -t {method}`。專案沒有 vitest,這條指令跑不起來,測試綁定靜默失效。
   - 骨架的 `_推測` 欄有講「看到 vite/vitest 設定」,使用者看得到,所以不到 major。
   - 修法:有 `vite.config.*` 但 `package.json` 依賴有 jest、沒有 vitest 時,不換。
   - 引句:「根目錄有 vite.config.* / vitest.config.*,或根 package.json 的依賴鍵(三類,_pkg_dep_keys)有 vitest。」

3. 說明註解被移到不屬於它的那一行
severity: minor
   - blocking: 否
   - diff 段:`_tension_candidates_into(arch, added_lines, repo_root)` 原本帶的註解「可能撞:改動檔新增了對照檔都沒有的做法(只端候選,不判)」,現在掛在 `_tension_drop_excluded(arch, _stack_excl)` 後面。
   - 影響:讀碼的人會以為那一行是在「端候選」。純註解錯位,行為沒問題。
   - 引句:「_tension_drop_excluded(arch, _stack_excl)   # 可能撞:改動檔新增了對照檔都沒有的做法(只端候選,不判)」

最嚴重 severity:minor。blocking 共 0 條。
