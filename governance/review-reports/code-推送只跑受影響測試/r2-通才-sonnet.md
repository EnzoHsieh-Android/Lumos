severity: major

查了八個角度,只有一條真的會出事:掛鉤判「推的是不是主線」讀哪個 ref,測試完全沒守住。

**finding 1:把掛鉤傳給 `--pushed-ref` 的 `$_rref` 換成 `$_lref`,新增的六支掛鉤測試與全部相關測試照綠**
severity: major
blocking: 是
標題:推到遠端 main 的功能分支本機名(`git push origin feat:main`)的守衛沒有測試
引句:「[[ "$_PF_PR" -eq 1 ]] && _pf_extra=(--pushed-ref "$_rref")」
`scripts/hooks/pre-push:547`(快照 `r2-snapshot.patch` 內同行)

失敗場景:
- 這行必須傳遠端 ref(被推去的目的地),不能傳本機 ref。「推 main 照全套、不降級」靠這個。
- 假如有人改成 `$_lref`,`git push origin feat:main` 會被當成功能分支,降成文件加關鍵字子集。
- 推 main 的本機全套是唯一把關。CI 的 push 事件雖然也會對 main 跑全套,但那是推完才跑,不是推前的閘。
- 新測試的 `push(lines)` 在每個案例都讓本機 ref 與遠端 ref 同名:`feat/feat`、`main/main`、混推也是同名。換成 `$_lref` 完全看不出來。

最小重現(我在臨時目錄複製 repo 的 scripts 與 skills,只改複本的掛鉤):
1. 把第 547 行的 `"$_rref"` 改成 `"$_lref"`。
2. 跑 `python3.14 scripts/test_lumos.py -k prepush_feature_branch`。
3. 輸出 `20 passed, 0 failed`。守著這條路的 `t_prepush_feature_branch_failclosed`、`..._mixed_with_main`、`..._skips_full` 都沒紅。

缺口與補法:缺一個 `("refs/heads/feat", head, "refs/heads/main", base)`(本機 feat 推遠端 main)的案例,預期全套;對照 `("refs/heads/main", head, "refs/heads/feat", base)`,預期降級。

歸因:未判定。這是上一輪就存在、這輪沒人看的角落,不是修補造成的。我沒有跑修前版本。依據是快照裡 `_ppfb_harness` 的 `push` 與各測試的 `lines` 全部同名,這是靜態事實。
同一案例的修前、修後:修前版沒有這個旗標,不可比;修後本機 `$_rref` 版是綠的,`$_lref` 變異版也是綠的。

---

沒有其他會擋的問題。逐項結果:

**角度 2(被刪掉的行為)與角度 3(跨檔追蹤)**
- `_test_suite_for_range` 只有 `_pitfall_diff_collect` 兩處呼叫(`scripts/lumos:62269`、`:62336`)。兩條回傳路徑都有 `computed`,讀端直接索引,`t_pitfalls_suite_computed` 有測漏帶會 KeyError。
- `_pitfall_diff_collect` 另一個呼叫端是 `scripts/lumos:19522` 的 capture-counts,只讀 `claims`,不受影響。
- `.github/workflows/ci.yml` 與其他指令沒有讀 `suite_computed` 或 `pushed_mainline`;CI 的 suite 步驟只讀 `suite`、`suite_reason`、`suite_graph`,沒壞。
- 被拿掉的「`--no-verify` 兜底」與「CI 會跑全套當後盾」句子:
  - ci.yml 的 `pull_request` 事件確實跑全套(shards 工作靠 `prep.suite == 'full'`,PR 一律 full)。
  - `ci-wait --sha` 存在(`scripts/lumos:73989`),`_ci_list_runs` 用 `--commit` 查,PR 頭提交查得到。
  - 新文案對得上程式。

**角度 1(逐行)**
- `_pf_extra` 空陣列展開沿用既有的 `${x+"${x[@]}"}` 寫法,bash 3.2 與 `set -u` 下可用。
- `dest="pf_pushed_ref"` 探測字樣確實存在於 `scripts/lumos`。
- JSON 裡的引號有跳脫,檔名無法偽造 `"suite_computed": true` 去騙 grep。
- `_down="light"` 優先、`"branch"` 次之的順序正確;原本就判 light 的不設 `_SUITE_BRANCH_DOWN`,與 [S6] 一致。

**角度 5、6、7、8**
- 兩條降級路徑共用同一段取關鍵字的程式,沒有重複。
- `_pitfalls_pushed_mainline` 每個 ref 多跑幾次 git 查詢,有 10 秒上限,算不出來只剩 main、master 兩個固定名,屬可接受的推送熱路徑成本。
- 沒有逐字違反 CLAUDE.md 的行。

**兩個我認為不構成 finding 的設計取捨**(計劃明講「刻意不受 light_ok 約束」)
- 功能分支只改測試檔時,`_sr["code"]` 為空,關鍵字也空,本機只跑文件子集,改到的測試要等 PR 的 CI 才第一次跑。
- 遠端預設分支不是 main、master,且本機沒有 `refs/remotes/origin/HEAD`(例如 `git init` 後 `remote add`)時,直接推該分支會被當功能分支降級。對本 repo(主線是 main)不成立。

**圖譜鏡頭 8 篇**:沒有逐篇讀,判定如下,只憑 diff 與跨檔追蹤,未實讀節點。
1. main-direct 盲區:未讀節點。推 main 路徑有三個掛鉤測試仍全套。
2. pitfalls-code-loop、3. bound-tests-gate、4. lumos-cli-read、7. lumos-cli-lifecycle:未讀節點。只新增 JSON 欄位與一個選用旗標,沒動既有輸出鍵。
5. design-loop、6. guard-kill、8. 測試假綠形態:未讀節點。第 8 篇的假綠形態正是 finding 1 那種「測試與實作同名巧合」。

**三問**:①修補的行為證據:`..._failclosed` 與 `..._old_lumos` 能紅(算不出範圍、舊版 lumos 都回全套),正向路徑成立。②相鄰路徑:推 main、混推、標籤、舊版 lumos 都有案例;唯一缺的是本機與遠端 ref 不同名。③新發現同一案例:修前版未取出,不可比,未判定。

未驗範圍:沒跑全套;沒對真實遠端做推送。

臨時目錄 `/tmp/lumos-seat-work/code-推送只跑受影響測試/通才-sonnet` 已刪。
