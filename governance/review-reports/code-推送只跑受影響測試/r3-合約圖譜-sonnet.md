severity: minor

**固定席前 8 篇(逐篇對照,結論都是不影響)**
1. Issues/code-loop守衛main-direct盲區:沒有登記合約。這輪沒動 code-loop check 的範圍算法,只在 pitfalls 呼叫多帶 `--pushed-ref`。不影響。
2. Systems/pitfalls-code-loop:沒有登記合約。pitfalls 只多輸出兩個欄位(`pushed_mainline`、`suite_computed`),tier 判定沒動。不影響。
3. Systems/bound-tests-gate:合約是「code-loop check 逐支真跑綁定的測試」,綁 `t_bound_tests_gate`。這輪改的是全套降成 light 的判定,沒碰 code-loop check。不影響。
4. Systems/lumos-cli-read:合約講 search 排除 superseded,跟這輪無關。
5. Systems/design-loop:合約講處置閘第五步,跟這輪無關。
6. Systems/guard-kill:合約講 rc 優先序與 JSON 純度,跟這輪無關。
7. Systems/lumos-cli-lifecycle:合約講 re-inject 保留 sentinel 之外的內容,跟這輪無關。
8. Systems/測試假綠形態:合約要求「還原翻紅釘」配前置斷言。新測試有做到,見下面的變異驗證。

**finding 1**
severity: minor
blocking: 否
t_prepush_feature_branch_mixed_with_main 耗時只剩 2 倍餘裕,慢機器上可能撞 180 秒超時而假紅
引句:「    r3, calls3 = push([("refs/heads/main", head, "refs/heads/feat", base)])」
`scripts/test_lumos.py:125891` 起。這支測試現在一次跑四趟掛鉤:混推、feat:main、main:feat 再加原有的混推。我在本機實測 85.5 秒,測試執行器自己標出「餘裕 2x ⚠ 餘裕不足 3 倍」。超時上限是 `TEST_TIMEOUT_SEC` 的 180 秒(`scripts/test_lumos.py:48338`),超過就判紅。CI 的分片機器比這台慢時,這支可能無緣由地紅。這是推測:我沒有 CI 的耗時資料,但本機另一支同時在跑,所以 85 秒可能略偏高。
歸因:有證據的修復回歸。修補後多了 feat:main、main:feat 兩趟推送。修前版本的耗時我沒量,所以只能算「有證據」到趟數增加,耗時差未判定。

**finding 2**
severity: minor
blocking: 否
`.github/workflows/ci.yml` 檔頭說 CI 是「push 後必跑」,與這次的行為不合
引句:「    PASS --> CI["CI (GitHub Actions): 全套測試<br/>+ doctor --ci + anchor verify<br/>(推 main 或開了 PR 才跑;Lumos 本 repo 推功能分支時本機也不跑全套,要等 PR 的 CI)"]」
佐證:`.github/workflows/ci.yml:3` 寫「這裡是 push 後必跑的後盾——pre-push 提示裡的「CI 仍會抓」由本 workflow 兌現」。第 5–9 行的 `on:` 只有 main、tag、pull_request。推功能分支沒開 PR 就不跑 CI。ARCHITECTURE 這輪已經改對,ci.yml 的註解沒跟上。這是註解,不影響行為;「CI 仍會抓」在掛鉤和 scripts/lumos 裡已經找不到(grep 過)。
歸因:有證據的原有漏查。這個註解在修前就是這句,修補沒碰它。

**鏡頭 2:文件對程式**
- ARCHITECTURE 流程圖的 CI 節點:`ci.yml` 的 `on:` 確實是 push 限 main 與 tag、加 pull_request,PR 事件一律全套(`ci.yml:83`)。對得上。
- bound-tests-gate 2026-09-18 那行:「判主線看推去的目的地(掛鉤每行的遠端 ref)」對應 `scripts/hooks/pre-push:547`,用的是 `_rref`。「t_prepush_feature_branch_mixed_with_main 釘兩個不同名案例」存在,且確實是 feat:main 和 main:feat。
- 掛鉤註解 `_down`:`spec_light` 不設 `_SUITE_BRANCH_DOWN`、`feature_branch` 才設,與 `scripts/hooks/pre-push:580-591` 一致。

**鏡頭 3:其他文件**
- 我查了 README.md:481、skills/lumos-project-notes/commands/08-自動跑的.md:7、06-代碼審與推送.md:42,三處都已寫成「推功能分支由 PR 的 CI 跑」。
- 掛鉤 `scripts/hooks/pre-push:359`、`:734` 的「CI 會再跑」指的是別的閘,不在這次範圍。
- 除 finding 2 外沒有其他漏同步。

**鏡頭 4:[S1]–[S8] 綁定**
- 我跑了 `-k prepush_feature_branch`,22 條全綠,涵蓋 t_prepush_feature_branch_* 七支。
- t_pitfalls_pushed_mainline 和 t_pitfalls_suite_computed 在 `scripts/test_lumos.py` 都存在。這兩支我只讀沒跑:`-k pitfalls_pushed_mainline` 與 `-k pitfalls_suite_computed` 兩次執行輸出被截斷,沒看到結果。
- [S4] 的案例涵蓋 main、master、標籤、空字串、遠端 HEAD 指向的 trunk、feat/x、feature/main,讀起來是真測 pushed_mainline。[S5] 讀起來是真測 computed(computed 為 false、缺 key 時 KeyError)。
- 沒有發現實作偏離設計。

**三問(修補回答)**
- 原問題的修復效果:r2 抓到的是「各案例本機與遠端同名,改看本機 ref 測試照綠」。修前掛鉤已經是 `--pushed-ref "$_rref"`(修前版本 `9918ed76` 的 546–547 行),所以這輪是補測試,不是改行為。
  - 變異實驗:我把複本的 `scripts/hooks/pre-push` 第 547 行 `$_rref` 改成 `$_lref`,結果 t_prepush_feature_branch_mixed_with_main 失敗 2 條斷言。
  - 修前的測試全是同名案例,理應抓不到這個變異。這點我沒有實跑修前測試,未判定。
- 修補處的相鄰路徑:
  - spec_light 路徑不印降級那行,對應 t_prepush_feature_branch_already_light,綠。
  - 推 main 全套,對應 t_prepush_feature_branch_failclosed,綠。
  - 範圍算不出來時照全套,同一支測試裡有案例,綠。
  - 舊版 lumos 沒有 `dest="pf_pushed_ref"` 字樣時退回全套,對應 t_prepush_feature_branch_old_lumos,綠。
- 新發現的同一案例修前修後:feat:main 在修前掛鉤與修後掛鉤的行為相同(兩版都帶 `_rref`),所以沒有行為回歸;只有 finding 1 的測試耗時是新增。

**未驗範圍**
- 沒跑全套。
- 沒量修前測試的耗時,也沒實跑修前測試。
- 沒驗 CI 實際耗時。

臨時目錄和我那次變異留下的 `gctl-run-ksgyf6fn` 已用字面絕對路徑刪除,刪前 `lsof +D` 沒有輸出。
