severity: major

## r1 按檔各開一個 ast-grep 程序後,推送閘的 30 秒預算在約 650 到 1100 支 .kt 時耗盡,掃完的檔也全被丟成「挑壞法超過時限」,整道閘變成只提醒
severity: major
blocking: 是(閘的必要行為在大改動下失效且是放行方向;我能當場重現)

輸入:推送範圍改到 N 支 .kt,走 `_choice_push_scan` → `_choice_compute` → `_choice_scan`。

引句:「deadline = time.monotonic() + timeout」

壞在哪:
- 修後每支檔各開一個 ast-grep 程序,量到每支約 23 到 25 ms。修前整批只開一次。
- 推送閘總預算只有 `_KT_SIT_BUDGET` 30 秒。這 30 秒還要先給判不判要求、讀檔,掃描之後的 `_choice_file_points` 也共用同一個 `deadline`。
- 掃描把預算用完後,`_choice_file_points` 在第一個有節點的行就 raise「挑壞法超過時限」。連已經掃成功的檔都被記成 unverified。
- 全部 unverified 時 `_choice_needs_disposition(res["lines"])` 為空,`_choice_push_round` 回 `[]`,推送放行,只印提醒。

實測(從臨時 clone 載入 scripts/lumos,呼叫 `_choice_compute(..., deadline=now+30, scan_timeout=remaining)`,等同推送閘):

| 輸入 | 修前 7826895c | 修後 4dd1ed80 |
|---|---|---|
| 1400 支各 4 行 .kt | 3.2 秒,1400 支全判到、`lines`=1400 | 32.8 秒,`lines`=0、`unverified`=1400,原因全是「挑壞法超過時限」 |
| 1000 支各 4 行 .kt | 約 2.7 秒 | 25.3 秒,仍判得到,離上限只剩 5 秒 |
| 300 支各 201 行 .kt | 輸出超過 64MB,rc -25,整批算不出來 | 13.4 秒,判到,RSS 214MB |
| 900 支各 201 行 .kt | rc -25,整批算不出來 | 34.1 秒,`lines`=0、`unverified`=900 |
| 單一 720KB .kt | 22.2 秒 | 5.7 秒 |

- 「300 支 .kt 的啟動成本與總時限」的答案:300 支小檔掃描約 7 到 9 秒(`_choice_scan`),300 支 200 行的檔含挑壞法共 13.4 秒。預算上限約為 650 支(200 行的檔)到約 1100 支(小檔)。
- 這是效能代價:修前對小檔大量改動一次就掃完,修後會逾時。大檔那條路徑修補確實有改善(上表最後一列),且兩支大檔不再互相拖累。
- `_choice_waive_target` 與 `choice-kill` 走預設 300 秒,不受此影響,但每次 `lint-waive choice:` 都重掃全部改動檔,檔數多時每次要幾十秒。

file: `scripts/lumos:78428`(`_choice_push_scan` 把 `scan_timeout` 設成 `max(1.0, deadline - time.monotonic())`,且 `deadline` 同時傳給 `_choice_compute`)

重現(臨時 clone 內)步驟:建一個 base 提交,再提交 1400 支 `app/src/main/java/x/T$i.kt`(內容 `package x\nfun f(a: Int, b: Int): Boolean {\n    return a > b\n}\n`),載入 scripts/lumos 後呼叫 `m._choice_compute(G, f"{B}..{head}", head, m._choice_tables()[0], deadline=t0+30, scan_timeout=max(1.0, t0+30-time.monotonic()), cache={})`。修後輸出 `lines 0 unverified 1400`,修前 `lines 1400`。

歸因:有證據的修復回歸。修前同一輸入判到 1400 支,修後全部 unverified。

建議修向(不是判定):掃描與挑壞法各自計時;或按檔批次掃描,只對整批失敗的那批退回逐檔;掃完的檔不該因掃描耗時被丟掉。

## r2 守的測試雜湊用「git grep 第一支含測試名的檔」,碰到排在測試目錄前面的計劃筆記就算錯:補強測試不重跑、改計劃筆記卻重跑
severity: major
blocking: 是(r1 g1 要修的「測試名不變、內容補強後重跑」在這個版面下沒有修好,且反向造成多餘重跑)

引句:「找不到記空字串;deadline 給了就共用那個時限」

壞在哪:`_choice_test_blobs` 用 `git grep -l -F -e <name> <sha> --`(不限路徑)取第一個命中檔的 blob。計劃筆記 `docs/.../Projects/*.md` 本身就寫著 `[test:<名>]`,而 `docs/` 在字母序上排在 `feature/`、`lib/`、`src/` 等模組之前。命中的就是計劃筆記,不是測試檔。
- 補強測試本體:blob 不變,`tests_sha` 不變,survived 不重跑(G3 repair 失效)。
- 改計劃筆記(`situation-rule --point` 就會寫計劃):blob 變,`tests_sha` 變,survived 與推送閘的 stale 提醒都被誤觸發,多跑整批 choice-kill。

實測(臨時 repo:`docs/k/Projects/p.md` 含 `[test:t_foo]`,`feature/src/test/java/x/FooTest.kt` 含 `fun t_foo`):

| 動作 | 修前 `tests_sha` | 修後 `tests_sha` |
|---|---|---|
| 只改 `p.md` | 2b8641ecef59d155(不變) | 9bfe0e8929065142,與前一版不同(變了) |
| 只在 FooTest.kt 加 `assertTrue(x)` | 不變 | 不變(9bfe0e8929065142) |

`git grep -l -F -e t_foo HEAD --` 回 `docs/k/Projects/p.md` 與 `feature/src/test/java/x/FooTest.kt` 兩筆,取第一筆。

測試為何沒抓到:`t_choice_kill_rerun_rules` 的測試檔放在 `app/src/test/java/x/VmTest.kt`,字母序排在 `docs/` 前面,剛好繞開。我跑了該測試,11 passed。

file: `scripts/lumos:77863`(`_choice_test_blobs` 的 `_lens_git_dl(rr, "grep", "-l", "-F", "-e", n, at_sha, "--", ...)`)

歸因:
- 「補強測試不重跑」:有證據的原有漏查。修前 `tests_sha` 本來就不看內容,修補宣稱解掉但只在 `app/` 排前面的版面成立。
- 「改計劃筆記就重跑」:有證據的修復回歸。修前不會,修後會。

## 已驗的正向主張與證據
- 按檔掃描後,單支大輸出檔不再拖累別支:修前 300 支 200 行輸出 82MB,rc -25(`RLIMIT_FSIZE` 64MB 的 SIGXFSZ),整批算不出來;修後同輸入判到 36000 行,0 unverified。
- 單一大檔的區間判法與不複製整檔:720KB 單檔修前 22.2 秒,修後 5.7 秒,RSS 約 240MB 不變。
- 逾時、Ctrl-C、例外下的程序與暫存:`_choice_sg_run` 在 TimeoutExpired 與 BaseException 都 `_kill_proc_group`。暫存目錄走 `TemporaryDirectory`,每支檔的 `finally` 都 unlink。這條只讀碼,沒實際送 SIGINT 驗,算未驗。
- 治理帳整本讀入:`_gov_vc_gate_events` 讀 22MB、12.5 萬行,0.19 秒、RSS 130MB,可接受。這是目前大小,未驗更大的帳。
- `-k choice_scan_per_file` 7 passed,`-k choice_kill_rerun_rules` 11 passed。
- 一支檔真的逾時時,剩餘時間全給它,後面的檔都記「沒掃到」。這個失敗路徑我造不出來(ast-grep 3.6MB 檔只要 2.6 秒),判未驗。

## 三問
1. 原問題的修復效果:大輸出與單一大檔的修復有行為證據,見上表。小檔大量改動的修復帶來 r1 的回歸,測試守的雜湊那條有 r2 的缺口。
2. 修補處的正常、錯誤、相鄰路徑:300 支以內正常路徑成立。超過預算是 r1,測試檔排在計劃筆記後面是 r2。
3. 新發現的同一案例修前與修後:見 r1、r2 兩張表。

## 圖譜鏡頭
這次沒附固定席節點(hook 說鏡頭計算超時),所以沒有節點可逐條判。

最嚴重:major;blocking 共 2 條

臨時目錄 `/private/tmp/lumos-seat-work/code-改動選擇點/資源-sonnet` 已用字面絕對路徑刪除。
