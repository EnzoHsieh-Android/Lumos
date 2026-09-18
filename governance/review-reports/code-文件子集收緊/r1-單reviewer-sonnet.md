severity: major

## F1 排除的真圖譜測試裡,t_slim_gate/其反事實測試驗的是「搜尋/goldset 等價性」,doctor --ci 完全沒驗這塊——「圖譜筆記由 doctor --ci 負責」這句設計理由對它不成立

severity: major
blocking: yes

觀察到什麼:`_docs_suite_select` 把「讀真圖譜(docs/\*-knowledge)」的測試整批排除在文件子集之外,排除的理由寫在程式碼註解裡,主張這類測試被 `lumos doctor --ci`(嚴格)這道推送前+CI 都會跑的閘接住。但 `t_slim_gate`(和它的反事實測試 `t_slim_gate_search_equivalence_counterfactual`)明確在名單裡被點名排除,而它們驗的不是「圖譜筆記格式健不健康」,是「在真 vault `docs/lumos-toolchain-knowledge` 上跑 goldset 30 條查詢是否全部非空」與「slim 版/完整版 `lumos search` 結果是否等價」——這是檢索/搜尋品質,不是圖譜結構健康度。我讀了 `scripts/lumos` 裡 `run_doctor`(974–2753 行,doctor 唯一定義處,整段自成一體,沒有再呼叫別支函式做這件事)整段原始碼,裡面沒有任何一處呼叫 `search`、提到 `goldset`、`retrieval` 或非空檢查——`doctor --ci` 檢查的是連結完整性、決策格式、stale、about_code 這類結構性項目,不會因為搜尋結果全部變空或 slim/完整版行為不等價而變紅。

怎麼重現:`docs/lumos-toolchain-knowledge/**/*.md` 屬於 `_DOCS_ONLY_PATHS` 白名單(`docs/` 前綴 + `.md` 副檔名),所以只改圖譜筆記內容的一次推送,會被 pitfalls 判成 `suite: docs`。這批改動生效後,這種推送在 pre-push 與 CI 都只會跑 `--suite docs` 子集——而 `t_slim_gate`/`t_slim_gate_search_equivalence_counterfactual` 不在子集裡(patch 裡的接線守衛測試明講排除它)。也就是說:如果一次「純文件」推送不小心把某篇被 goldset 大量依賴的圖譜節點刪掉、改名或抽掉關鍵詞,讓 goldset 30 條查詢裡有幾條變空、或讓 slim 版與完整版 `search` 結果不再等價,pre-push 與 CI 這兩道閘都不會跑到能抓到它的測試,`doctor --ci` 也驗不出來——要等到有人手動跑全套(`python3 scripts/test_lumos.py`,約 8 分鐘)才會發現。

為什麼是 bug 不是風格:這批改動的核心正當性建立在「排除掉的真圖譜測試,doctor --ci 會接住」這個宣稱上(程式碼註解與訊息裡明寫)。這個宣稱對 `t_slim_gate` 這兩支不成立,是可反駁、也確實被反駁掉的宣稱——不是主觀寫法偏好,是這批改動自己講的安全網對這兩支測試漏接,而它們驗的正是這次改動最可能波及到的「真的讀這次可能改到的真文件」(圖譜筆記內容)。

引句:「# `lumos doctor --ci`(嚴格)驗,那些測試多半是拿真圖譜當語料的重測試(t_slim_gate 34 秒);帳本(docs/.xxx.jsonl)也不算」

引句:「check("docs 子集不含只在假環境寫文件的重測試(t_ci_wait 136 秒、t_slim_gate 34 秒)", "t_ci_wait" not in names and "t_slim_gate" not in names, "")」

file: `scripts/lumos:974` (`run_doctor` 定義起點)
file: `scripts/lumos:2753` (`run_doctor` 結束,下一個頂層 def 是不相關的 `_search_region`)
file: `scripts/lumos:22282` (`_DOCS_ONLY_PATHS` 白名單含 `docs/`)
file: `scripts/test_lumos.py:24762` (`_slim_copy_install_files` 裡 `repo = _P(GRAPHCTL).parent.parent`,供對照:t_slim_gate 系列讀的是真 repo 的 `docs/lumos-toolchain-knowledge`,不是 fixture)

---

## 驗過的路徑(沒發現額外 blocker/major)

①「真 repo 根」寫法逐一對 `--list --suite docs`:在 worktree 裡把 `_docs_suite_select` 的 `rx_real` 換成涵蓋 `repo = Path(...)`(排除已知走 tempdir 的用法)、`_repo_root(`、`\bROOT\s*=`、`os.path.dirname(os.path.dirname(__file__))`、`Path(__file__).parent.parent`(無 resolve)等寫法的加寬版本,對全部 1021 支測試重新用同一套 rx_doc 掃過一次,逐一核對跟現有選中的 63 支的差集。一輪找到的差集(`t_disposal_gate_r2_panel_hardening`、8 支 `t_slim_install_*`)逐支讀原始碼後確認都是誤判:前者是 docstring 裡提到函式名 `_vault_repo_root(`(不是程式碼真的用這個真 repo 根寫法讀文件);後者是測試本體字面寫了一份**假**的 `CLAUDE.md`(temp dir 裡的假來源 repo)、`CLAUDE` 字樣命中純屬巧合,真正的「真 repo 根」寫法(`_slim_copy_install_files`/`_need_src` 裡的 `Path(GRAPHCTL).../.parent.parent`)複製的是 `slim/install.sh`、`slim/install.py`、`slim/claude-block.md`——`slim/` 根本不在 `_DOCS_ONLY_PATHS` 白名單裡,改到它本來就不會被判成 `docs` 子集,不存在漏測風險。逐檔核對 `scripts/test_lumos.py` 裡所有 `repo = Path(GRAPHCTL)...`/`_P(GRAPHCTL)...`/`Path(__file__).resolve().parent.parent` 出現處(共 20+ 處),全部要嘛被現有 `rx_real` 正則涵蓋、要嘛指向 tempdir 而非真 repo 根。沒找到會漏判「真的讀真文件」測試的路徑寫法。

②見 F1。另外檢查了 `t_precommit_whitelist_drift_guard`(也被排除、`_need_src` 綁定 `docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md` 存在性)——它驗的是 hook 腳本裡的豁免清單字樣對齊,不是圖譜筆記內容本身,`doctor --ci` 涵蓋不涵蓋它不影響這次改動的安全性主張,沒有另開一條。

③ `docs/(?![\w.-]*-knowledge)(?!\.)` 在 worktree 裡實測:`docs/methodology/foo.md`、`docs/心智模型.md` 都命中(正確算「文件」);`docs/lumos-toolchain-knowledge/`、`docs/lumos-toolchain-knowledge/Systems/foo.md` 都不命中(正確排除真圖譜);`docs/.governance-log.jsonl`、`docs/.usage-log.jsonl` 都不命中(正確排除帳本)。跟 `t_runner_suite_flags`/patch 裡的斷言方向一致,沒發現誤判。

④ 讀了 `scripts/hooks/pre-push` 337–420 行整段:`_SUITE_SEEN` 在迴圈裡只要處理過至少一個非刪除 ref 就會被設成 1(不論 pitfalls 成功與否);pitfalls 失敗時 `pf_json` 可能是空字串,但 `_suite_this` 預設值就是 `"full"`,不命中 docs 才會覆寫成 `"docs"`——所以 pitfalls 失敗時會保守退全套(`_SUITE_FULL=1`),`_AUTOLOOP_ARGS` 維持空陣列、自主迴圈整支照跑,不是「判不出來卻只跑一條」。多 ref 情境下 `_SUITE_FULL`/`_SUITE_LIGHT` 是跨迴圈「只要有一個 ref 命中就設 1」不會被後面的 ref 重置,`_AUTOLOOP_ARGS` 只在**所有** ref 都判成 docs 時才收窄,跟 `test_lumos.py --suite docs` 那條路徑(`_SUITE_LIGHT` 也算 docs 子集)刻意不同,這個不同是 patch 註解裡明講的設計(「純文件推送(每個 ref 都判 docs,不含 light)」),不是疏漏。

⑤ CI `id: suite` 那步(`.github/workflows/ci.yml` 31–46 行):判斷式第一條就是 `github.event_name = push`,`pull_request` 事件必然不成立,`suite` 維持初始值 `full`,自主迴圈那步在 `SUITE=full` 分支跑完整 `test_autonomous_loop.py`。跟程式碼裡的註解「pull_request 事件沒有 before,也是全套」一致,沒發現落差。
