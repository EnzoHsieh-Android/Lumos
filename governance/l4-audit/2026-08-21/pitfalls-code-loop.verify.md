C1 [❌] spec 模式其餘描述屬實，但「印通用3問」與現況不符——現為4問(3固定+1風險類反問，2026-08-08追加) | 證據: scripts/lumos:10230-10236(_PITFALL_GENERAL 共4項)；scripts/lumos:11896(cmd_pitfalls docstring 自陳「印通用 4 問(含風險類反問)」)；scripts/lumos:11894(cmd_pitfalls)、11817(_pitfall_scan_classes 掃 PITFALL_CLASSES 四類屬實)

C2 [❌] manifest 欄位敘述只對「內建 regex 類」claims 成立；lint 來源的 claim 欄位是 file/line/source/rule/message，無 class/pattern/question——並非「每筆」都含 file/line/class/pattern/question | 證據: scripts/lumos:10579-10584(_lint_run_and_parse claim={file,line,source,rule,message})；對照 scripts/lumos:11693-11695(regex claims 才有 class/pattern/question)。stack_questions 附加條件(kt/cs/vue/sql 命中附加，源自「效能檢核目錄」節點)屬實 | 證據: scripts/lumos:10248(_STACK_PERF_QUESTIONS 鍵=kt/cs/vue/sql)，10251-10253(comment「內容源=圖譜 Systems/效能檢核目錄」)，11719-11726(附加邏輯)

C3 [❌] tier 只有 standard/high 兩值，pitfalls --diff 從未輸出過 trivial；trivial 是 lumos-code-loop skill 裡供人自行判斷「typo/純文檔/一行無邏輯 diff」跳過 loop 的概念，不是 pitfalls --diff 產出的 tier 值，pre-push 也只判斷 tier=="high" | 證據: scripts/lumos:11717、11749(`"tier": "high" if claims else "standard"`)；scripts/lumos 全檔 grep "trivial" 零命中；scripts/hooks/pre-push:94(`grep -q '"tier": *"high"'`，無 trivial 分支)；skills/lumos-code-loop/reference.md:21(「trivial 可跳」為人裁概念，非 pitfalls 輸出)

C4 [✅] --diff 行號由 git diff `@@ -x,y +N` hunk header 推導、逐行遞增 | 證據: scripts/lumos:11672(`m = re.match(r"@@ -\d+(?:,\d+)? \+(\d+)", line)`)，11663(_diff_added_lines 同款邏輯)

C5 [✅] 排除 governance/review-reports/ 路徑且不外溢到路徑外同內容檔案(照掃) | 證據: scripts/lumos:11688(`not cur_file.startswith("governance/review-reports/")`)；測試 scripts/test_lumos.py:12516-12549(t_pitfalls_diff_skips_review_report_artifacts，含「收緊釘:同內容放在 review-reports 外照掃」案例)

C6 [✅] _BOOKKEEPING_FILES/_BOOKKEEPING_DIR 為單一源常數，pitfalls --diff 排除掃描與 code-loop 留痕豁免共用同一組(非各自維護區域變數) | 證據: scripts/lumos:10294-10296(常數定義)；scripts/lumos:11691-11692(pitfalls --diff 排除引用)；scripts/lumos:14110(`_WL_FILES, _WL_DIR = _BOOKKEEPING_FILES, _BOOKKEEPING_DIR`，code-loop 端直接取用同常數非另建)；測試 scripts/test_lumos.py:12554+(t_pitfalls_diff_skips_bookkeeping_ledgers)

C7 [✅] pass/skip 有效性規則(留痕 sha 之後只動簿記檔且仍為祖先→有效；動任何非簿記檔→失效；改寫史/非祖先→拒認)與程式碼一致 | 證據: scripts/lumos:14093-14121(_codeloop_guard_verdict 的簿記白名單豁免段：`git merge-base --is-ancestor` 檢查 + 逐檔白名單比對；非白名單檔或非祖先→落入下方 blocked 分支)；測試 scripts/test_lumos.py:8206-8250(t_codeloop_pass_survives_bookkeeping_commits，含簿記豁免不外溢與 amend 拒認兩條收緊釘)

C8 [✅] cmd_loop_status --gate 的 --spec 已改可選，缺省時 G1 直接 skip | 證據: scripts/lumos:4483-4494(`if spec is None: print("[gate] G1 refcheck(引用座標): skipped(無 spec 對象,code-loop 情境)")`)；測試 scripts/test_lumos.py:193-195(t_loop_gate 案14「新契約」)、219+(t_loop_gate_no_spec)

C9 [✅] PITFALL_CLASSES 類名集合與 difficulty.RISK_CLASSES 鍵集合相等、_PITFALL_BLACKLIST 與 difficulty._BLACKLIST 集合相等，兩條測試即 TestPitfallsDrift；該守衛與 difficulty.py 皆非 vendored 到消費專案(toolchain-only) | 證據: scripts/test_autonomous_loop.py:373-398(TestPitfallsDrift 兩條 test_pitfall_classes_match_risk_classes/test_pitfall_blacklist_match)；scripts/lumos:8783-8785(_VENDORED_TOOLKIT 僅含 scripts/lumos、test_lumos.py、merge-claude-settings.py、graph-rename.sh、fetch-notesmd.sh，不含 test_autonomous_loop.py 或 governance/autonomous_loop/difficulty.py)；scripts/lumos:9133(cmd_bootstrap 全域 lumos 為 symlink 指向來源，非 vendored copy)

C10 [✅] --diff 分類軸為形態類(併發/效能/資源)非四業務類；SELECT→效能(N+1)，INSERT/UPDATE/DELETE→併發(交易) | 證據: scripts/lumos:10280-10287(_PITFALL_DIFF_PATTERNS：`r"\bSELECT\b"`→"效能"；`r"\bINSERT\b|\bUPDATE\b|\bDELETE\b"`→"併發")

C11 [✅] --diff 過濾規則(跳 .md/.txt/.rst、跳測試檔、跳註解行)與 doctor Check H 的 _scan_diff_for_irreversible_hints 過濾規則完全同值 | 證據: doctor Check H 位置 scripts/lumos:1003(`section("H", ...)`)；filter 函式 scripts/lumos:2231-2266(_scan_diff_for_irreversible_hints：_SKIP_EXT={.md,.txt,.rst} L2236、_TEST_PAT L2237、註解 startswith 判斷 L2266)對照 --diff 端常數 scripts/lumos:10288(_PITFALL_DIFF_SKIP_EXT)、10297(_PITFALL_DIFF_TEST_PAT)、11696(註解 skip)——四組值逐一相同

C12 [✅] --check 只驗證「## 實務隱患」節字串是否存在，不驗內容 | 證據: scripts/lumos:11920(`has_section = re.search(r"(?m)^##\s+.*" + re.escape(section_title), text) is not None`)，11921-11924(僅據 has_section 布林值判定 rc)

C13 [✅] tier=high 且有收斂中 spec 時追加 spec-conformance 審查席，四類(已實作/縮水/多做/未實作)，記於 templates §7.5 | 證據: skills/lumos-code-loop/SKILL.md:169、reference.md:173(spec-conformance slot 觸發條件與四類判斷)；skills/lumos-design-loop/templates.md:181-197(§7.5 明列「已實作 / 縮水(做了但比 spec 少) / 多做(diff 有 spec 沒有的行為變更) / 未實作」)

C14 [✅] 真跑優先規則(2026-07-18 S1)：綁 [test:] 星標合約節點時 pass 前必跑該綁定測試且須綠；三順位①合約節點/圖譜記載完整指令②依棧慣例組指令③歧義/查無→退跑測試檔/模組級再不行跑全套並留痕記「解析歧義」，不得因解析不了而靜默不跑 | 證據: skills/lumos-code-loop/SKILL.md:218

C15 [❌] t_pitfalls_spec 確為9條、TestPitfallsDrift 確為2條、t_loop_gate 案14與t_loop_gate_no_spec 均存在，但 t_pitfalls_diff 實際為12條(非11條)；整體374 passed 因測試套件跑很久(6分50秒仍未跑完、CPU time僅11s多為IO等待)未能在限時內完整驗證，已終止該次執行 | 證據: scripts/test_lumos.py:5638-5667(t_pitfalls_spec 內 `grep -c 'check("pitfalls'` = 9)；scripts/test_lumos.py:5529-5587(t_pitfalls_diff 內同法計數 = 12，非11：含 rc0/資源/效能/tier-high/class形態軸/每條有line/requests.post第3行/SELECT第5行/.md-skip/測試檔skip/INSERT併發/CJK檔名 共12個 check() 呼叫)；scripts/test_autonomous_loop.py:373-398(TestPitfallsDrift 2條)；scripts/test_lumos.py:193-195,219(t_loop_gate 案14、t_loop_gate_no_spec 均存在)

✅10 ❌5 ❓0 ⏭0
