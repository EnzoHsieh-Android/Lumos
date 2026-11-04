severity: minor

本席沒找到會做出錯行為的 blocker 或 major。我跑過 `t_spec_gate_redbase_green*`、`t_redbase_branch_rows_fallback_keeps`、`t_tq_guard_cli_contract`、`t_tq_guard_string_comma_args`、`t_name_collision_scales`、`t_drift_born_unknown`、`t_spec_gate_redbase_written_on_red`,在 fe9702278 工作樹上全綠。下面 4 條都是 minor,其中第 1、2 條是新共用判斷 `_git_partial_clone` 的小缺口與測試盲區。

**finding 1:`_git_partial_clone` 把「沒寫等號的 promisor」當成不是部分複製,但 git 認它為 true**

`git config --get-regexp` 對沒寫值的布林鍵只印鍵名,沒有空白與值。`val` 因此是空字串,走到 `.promisor` 的值判斷時 `"" not in (...)` 成立,被 `continue`,最後回 False。git 對 `remote.<名>.promisor` 用布林解析,沒寫值等於 true。

我實測了兩個版本:
- 手寫 `[remote "origin"]\n\tpromisor` 的複製,`git config --type=bool --get remote.origin.promisor` 回 true。
- 把 `uploadpack` 換成留記號的腳本後,`git cat-file -e <不存在的提交>^{commit}` 觸發連線,記號檔出現。
- 該複製上 `_git_partial_clone` 回 False,`_drift_born_env_err` 回 None。
- 具體代價:這種複製上 `_redbase_on_branch` 會逐筆問 git,git 自動連遠端抓,逾時殺不到抓取程序。這正是 r1 資源席要擋的情形。實務上要手改設定檔才會出現,所以只列 minor。

引句:「if key.endswith(".promisor") and val not in ("true", "yes", "on", "1"):」

severity: minor
blocking: 否
歸因:有證據的原有漏查。修前 6e10ae5 只看 `extensions.partialClone`,同一個複製的 `_drift_born_env_err` 也回 None;修後 `_git_partial_clone` 仍回 False,不是新回歸。
兩版查證:用 `git show 6e10ae5:scripts/lumos` 載入的 `_drift_born_env_err(pcB)` 回 None;修後 `_git_partial_clone(pcB)` 回 False、`_drift_born_env_err(pcB)` 回 None。

**finding 2:`_git_partial_clone` 的測試只釘「promisor 與 partialclonefilter 同時存在」,拿掉任一個判斷都不會紅**

我在 scripts 的副本上改壞,再跑 `-k t_redbase_branch_rows`,每種都照樣 19 通過:
- 把 `_GIT_PARTIAL_KEYS` 拿掉 `remote\..*\.promisor` 那一支:通過。
- 把 `_GIT_PARTIAL_KEYS` 拿掉 `remote\..*\.partialclonefilter` 那一支:通過。
- 把 `.promisor` 的值判斷改成一律 `continue`:`t_redbase_branch_rows` 與 `t_drift_born` 都照樣通過。

原因是測試用的 `pc2` 兩個鍵都寫了,而真實 `clone --filter` 本來就兩個都寫。

另外我實測:只寫 `promisor=false` 加 `partialclonefilter=blob:none` 的複製,git 仍會連遠端。`_git_partial_clone` 在這種情況回 True(正確、保守),但沒有任何測試或註解記下這個行為,`remote.<名>.promisor=true` 的字面說法也不完整。

引句:「_sp.run(["git", "-C", str(pc2), "config", "remote.origin.partialclonefilter", "blob:none"])」

severity: minor
blocking: 否
歸因:未判定。`_git_partial_clone` 與這支測試都是這次修補才加的,修前沒有對應行為可比。
兩版查證:修前沒有 promisor 相關測試(`grep promisor` 只見舊式 `extensions.partialClone` 的設定);修後上述三種改壞都不紅。

**finding 3:驗收條款 [S8] 寫「過濾應把那幾筆紀錄照舊算進來並印一句說明」,但 HEAD 解不出與判不了帳有沒有被忽略兩種情形不印**

我直接呼叫修後的 `_redbase_branch_rows`:
- `ignored="unknown"`,帳裡有別條分支(ref=otherbranch)的判綠紀錄:回 1 筆,stderr 為空字串。這等於原本的跨分支漏洞靜默重現。
- `--orphan` 還沒有提交、帳裡有沒有 ref 的舊判綠:回 1 筆,stderr 為空字串。因為 `ok = bool(head) and ...` 成立不了,`unsure` 沒增加。

計劃做法 1 e 寫「b 以外」所以不印,與程式一致。但 [S8] 的條款字面把這兩種也列進去,綁定測試 `t_redbase_branch_rows_fallback_keeps` 對這兩種只斷言 `shas`,沒有斷言輸出。

按判準字面「測試抓不住錯而被保護的是驗收條款」可以升 major。實際傷害只是少一行提示,而且 git 連 check-ignore 都失敗時本來就不會有別的提示,所以我標 minor。要不要升級請編排者按條款字面裁。

引句:「過濾應把那幾筆紀錄照舊算進來並印一句說明」

severity: minor
blocking: 否
歸因:有證據的原有漏查。修前 6e10ae5 的 `_redbase_branch_rows(root,"x",None,"unknown")` 與 `--orphan` 加舊判綠,都是回 1 筆、stderr 為空;修後相同。
兩版查證:兩版輸出都是 `rows kept: 1 | stderr: ''`。

**finding 4:修補把 `_redbase_branch_rows` 的第 3、4 個參數從絕對截止時間改成相對秒數 `budget`,測試裡兩處舊呼叫沒改**

`rows(sh, _t.monotonic() + 30)` 與 `rows(pc, _t.monotonic() + 30)` 仍照舊傳「現在時間加 30」。現在的語意是相對秒數,所以實際預算是開機秒數加 30,過濾那一段 10 秒預算完全沒被驗到。

同一支測試裡其他呼叫已改成 `rows(pc2, 30)`,同檔內寫法不一致,看起來像漏改。目前不會讓測試失敗,因為每次 git 另有 20 秒上限。但如果有人之後讓 `budget` 被忽略,淺複製與部分複製這兩段不會紅。

引句:「shas, out = rows(pc, _t.monotonic() + 30)」

severity: minor
blocking: 否
歸因:有證據的修復回歸,僅限測試。r3 修補同一個提交改了簽名,只更新了部分呼叫端。
兩版查證:修前 `def rows(root, deadline)` 內部用 `m._redbase_branch_rows(root, "甲", deadline, "ignored")`,傳絕對時間是對的;修後簽名是 `(root, loop, ignored, budget)` 的相對秒數,這兩處呼叫沒跟著改。

---

**三問回答**

**① 原問題的修復效果有何行為證據?**
- 只寫 promisor 加 partialclonefilter 的部分複製:我建了一個複製並設定這兩個鍵。修前 `_drift_born_env_err` 回 None(判成不是部分複製);修後 `_git_partial_clone` 回 True,`_drift_born_env_err` 回「partial clone 讀舊版本會去網路抓,不讀」。
- 帳被忽略時不再算分岔點:`t_redbase_branch_rows_fallback_keeps` 的 `forks == []` 與 `unknown` 時 `forks != []` 對照,兩個都綠。
- 取分支名改借 `_note_reread_branch`:同名 tag 的 S2 測試綠。
- 還沒有提交的 HEAD:我自己跑 `--orphan`,不崩,ref 不同的丟、沒 ref 的留。

**② 修補處的正常、錯誤與相鄰呼叫路徑是否仍成立?**
- 呼叫端:`_redbase_branch_rows` 只有 `_redbase_attach` 一個呼叫端(grep 全 repo),簽名改了沒有外部呼叫端會壞。
- 回頭條件那支:`_drift_born_env_err` 的 `_git_partial_clone` 回 None(git 失敗)時,`if` 判斷仍是假值,與舊的「git 失敗就當不是」一致,沒有新增放行或擋下。
- `ref` 欄位:`ref` 加進事件後,我查了全檔對 `ref` 的讀者(`_codeloop_read_from_ledger` 等),都用 `gate` 篩過,沒有誤讀;`rec` 本來沒有 `ref`,`extra` 排除它也無害。
- 淺層、完整、逾時與 CAP 路徑:我模擬 300 個不存在的 head_sha,耗時 6.93 秒,100 筆因超過 CAP 照留,印一句。每個不存在的 sha 要問 2 次 git,10 秒預算夠用,只是在極端情況下 spec-gate 會卡約 7 秒。這是 r2 設計下的既有取捨,我沒另列 finding。

**③ 新發現的案例,修前、修後各是什麼結果?**
- finding 1(只寫 promisor、沒寫值):修前和修後都判成非部分複製。非回歸。
- finding 3(unknown 與 unborn 不印):修前和修後都不印。非回歸。
- finding 4:修前呼叫與簽名一致,修後不一致,是回歸,但只在測試裡。

**已驗**
- 三個修補檔 `d4bbaaea` 與前一版差異我讀完。
- 我在副本上做了三種改壞並實跑。
- 我實測了 git 2.39.2 的 promisor、partialclonefilter 與連遠端行為。
- `_TG_CONST_PAT` 三引號的 `_lazy_re` 是 possessive,沒有 ReDoS;三處 fullmatch 都一起認得三引號。
- `t_name_collision_scales` 的 `id()` 計數:若 `_join` 不快取,每次新 tuple 會讓集合至少有 2 個 id,所以快取被拿掉會紅,沒有 id 重用造成的假綠。

**未驗**
- 真實 blobless/treeless 遠端複製,我只用設定加留記號腳本代替。
- Windows。
- 時鐘倒退。
- 大 repo 沒有 commit-graph 時的速度。
- 並行會談(範圍外)。
- 「壓提交後判綠紀錄不再算數」這個計劃已承認的天花板一。它與專案本身「推送前壓成一個」的慣例相撞,所以在帳被忽略的專案上是常態,但這是已記在計劃的取捨,我沒列成 finding。
- 計劃/筆記與圖譜 `lumos lint` 是否通過,我沒跑。

涉及檔案(皆在 `/Users/enzo/harness/lumos-green-scope`):
- `scripts/lumos`:`_git_partial_clone` 約第 12035 行,`_redbase_branch_rows` 第 14401 行,`_redbase_on_branch` 之後。
- `scripts/test_lumos.py`:`t_redbase_branch_rows_fallback_keeps` 約第 123980 行。
- `docs/lumos-toolchain-knowledge/Projects/判綠紀錄限本分支與撞名測試改計數_計劃.md`。

我已刪除自己的暫存目錄 `/private/tmp/lumos-seat-work/code-判綠紀錄限本分支與撞名測試改計數/通才-sonnet`。

最嚴重等級是 minor,blocking 共 0 條。
