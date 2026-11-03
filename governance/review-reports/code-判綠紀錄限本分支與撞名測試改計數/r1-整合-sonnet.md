severity: major

整合席的立場是三個月後接手的人。我逐 hunk 讀完 diff,在 `/tmp` 的獨立複本上對新程式逐道做破壞測試(每道拆掉一次,看綁定測試會不會紅),並跑了相關測試子集:`spec_gate` 405 支、`gov_` 233 支、`redbase` 181 支、`test_guard` 87 支、`gate_event` 5 支、`t_name_collision` 22 支、`t_tq_guard_cli_contract` 99 支,全綠。`lumos spec-trace` 顯示 8 條條款都綁到測試、沒有懸空;七篇改到的筆記 `lumos lint` 都是 0 問題。程式本身沒找到會做錯事的地方,有兩條是驗收條款綁的測試證不到條款原意,一條是筆記殘句。

1. 驗收條款 S3 的後半「每種串接最多一次」,`t_name_collision_scales` 證不到
severity: major
   blocking: 是
   引句:「應抓到的錯:每個名字重建索引、或串接不快取每次重做 → 次數紅。」
   - 測試的計數子類 `Counting._join` 是先看 `self._joined` 有沒有這個鍵才記一筆、再呼叫 super。基底 `_join` 的快取守衛被拿掉時,第一次呼叫之後 `_joined` 就有鍵了,子類永遠只記到第一次,看不到基底重做。
   - 最小重現(未動真 repo):在 `scripts/lumos` 的 `_TitleIndex._join` 把 `if key not in self._joined:` 改成 `if True:`,跑 `python3.14 scripts/test_lumos.py -k t_name_collision_scales`,結果 `4 passed, 0 failed`(該測試 8.3 秒,正常 0.3 秒,低於 60 秒安全網)。
   - 對照:拆掉 `_name_collision_reason` 的快取,或在 `_name_filter_collisions` 每次重建索引,都會讓「①標題索引只建 1 次」紅,所以前半成立。
   - 同一個 overclaim 還寫進四處:測試 docstring、計劃做法 2「同時數建構次數與 `_join` 真的串接(快取沒命中)的次數」、`測試名收自由字串_計劃` 的 S79,以及 `test-profile-multiplatform.md` 那句「測試數索引與串接各建了幾次,不量時間」。
   - 原本的 15 秒門檻對這個退步至少會紅,新測試反而放過它,測試比改動前弱了一塊。

2. 驗收條款 S8 的「淺複製留」只被測到一半,另一條分支(rc 1 加淺複製)沒有任何測試守
severity: major
   blocking: 是
   引句:「verdict[sha] = None if is_shallow() else False」
   - 最小重現:把這行改成 `verdict[sha] = False`,跑 `-k t_spec_gate_redbase_green` 與 `-k t_redbase_branch_rows`,結果 12 passed 與 7 passed,全綠。
   - `t_redbase_branch_rows_fallback_keeps` 的淺複製案例用的是不存在的提交,走的是 rc 128 再 `cat-file` 那一條。真正的祖先在淺複製裡被回傳 rc 1(歷史被截掉)的那條沒人守。
   - 這不是理論情境,我用純 git 重現:`git clone --depth 1 -b featA`,再 `git fetch --depth=1 origin main`,此時 `git merge-base --is-ancestor <main 頂端> HEAD` 回 rc=1、`--is-shallow-repository` 回 true,而那個提交其實是真祖先。程式碼這條判對了(留),但被拆掉時測試沒反應,S8 沒被保護。
   - 同一輪的其他破壞都被抓到:拿掉分支名比對、rc 1 一律留、rc 0 一律丟、`cat-file` 失敗改留、超過上限不印、帳進版控也過濾、判綠或留痕不寫 ref,各自都有測試翻紅。

3. 計劃做法 4 承諾要補的「判綠觀測」殘句沒補,仍寫「只看這條分支自己寫的」
severity: minor
   blocking: 否
   引句:「判綠觀測只讀工作目錄的治理帳、只看這條分支自己寫的那幾筆(跟分岔點那一版做行差)」
   - 見 `docs/lumos-toolchain-knowledge/Projects/規格閘紅燈測試快照_計劃.md:62`。diff 只在上一條「分岔點」補了一句指標,這條判綠觀測句子原封不動。
   - 治理帳被忽略時,現在是「分支名加祖先」過濾,不是跟分岔點做行差。計劃做法 4 第二小點明列這句與「判綠過的不存」兩處要補,實際只補了 `:61` 一處。
   - 同檔 `:57` 的「這支測試在這條分支上曾被規格閘判綠過」也沒標「被忽略時另有認法」。
   - 這是讀筆記的人會被誤導的殘句,不影響程式。

不影響的部分(對照你列的鏡頭):

- 計劃對程式:做法 1 到 3 與 S1、S2、S6、S7、S8(淺複製半支除外)、S9、S4、S3(前半)都對得到 diff 行與測試。程式與計劃有出入的只有:讀取端的 `ref` 與 `_redbase_branch_name` 本身走 `_lens_git`、不在整批 10 秒截止內,但計劃寫的「所有 git 呼叫走 `_lens_git_dl`」限定在祖先過濾那一段,所以對得上。
- 筆記對程式:
  - `_TG_LIMITS` 與 `test-quality-standard.md` 逐字相同,`t_tq_guard_cli_contract` 綠。
  - `_TG_LIT_PAT` 的註解與 `_tg_ident` 的說明對照 `_C_STRIP_PAT` 實際內容屬實。
  - 計劃寫的「還沒有提交的 repo 的 head_sha 會寫成字面 HEAD」我實測屬實。
  - `_note_reread_own_fps` 的 rc 處理描述屬實。
  - 三引號常值樣式讓 `assertEquals("a", """${f()}""")` 這類帶樣板的原始字串也被算成常值,單行的 `"${f()}"` 本來就是,屬既有近似判讀,不另列。
- 鏡頭 4(新增的 `ref` 欄位):全 repo 讀事件 `ref` 的只有新程式的 `_redbase_on_branch`。
  - 代碼審留痕讀取 `_codeloop_read_from_ledger` 只認 `gate=code-loop` 與 `branch` 欄位。
  - 推送前讀規格閘留痕認的是 kind、loop、ts;比對工具讀紅燈版認的是 `redbase` 欄位。
  - `gov --stats` 與 doctor 沒有讀 `ref`;spec-gate 留痕與判綠事件不在本機帳白名單(`_GOV_LOCAL_PAIRS` 只有 `spec-gate-run`),維持進版控帳。
  - 審查帳 `.canary-log.jsonl` 那筆沒有被加 `ref`,`extra` 的排除是無作用的保險。結論:不受影響。

固定席筆記逐條判定:

- `lumos-cli-read` 的 ★INVARIANT★(search 排除 superseded):diff 沒碰 search,不影響。
- `測試假綠形態` 的 ★INVARIANT★(還原翻紅釘要有前置斷言):新測試多數有前置斷言。S1 有「判綠紀錄記下分支名」,S7、S9、S8 淺複製與 scales 都有 ★前置★。S6 同名重開與提交不存在兩案沒有明寫前置,但分別被我的 rc 1 一律留、`cat-file` 失敗改留兩種破壞測出,實質成立,不破壞。
- `loop-convergence-recording`、`pitfalls-code-loop`、`reversibility-governance-ledger`(★RISK★):只在 spec-gate 事件多一個 `ref`,代碼審留痕與治理帳分流白名單都不讀它,不影響。
- `design-loop` 的 ★INVARIANT★(處置閘第五步):不碰設計審迴圈與處置閘,審查帳留痕形狀不變,不影響。
- `guard-kill`、`bound-tests-gate`:兩者共用的 `_name_collision_reason` 與 `_run_bound_tests` 程式沒改,只改測試,不影響。
- 只列名的節點(`規格閘`、`test-guard`、`test-profile-multiplatform`、`test-quality-handbook` 等):逐一對照新寫的句子,除上面第 1、3 條外沒有與程式矛盾。

最嚴重等級是 major,blocking 共 2 條(第 1、2 條)。

我建在 `/tmp` 的臨時複本已用字面絕對路徑刪除。
