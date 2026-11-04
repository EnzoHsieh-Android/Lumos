severity: major

派工尾端沒有附上任何合約或事故節點(`r1-dispatch.json` 也沒列),所以固定席的逐條判讀只能自己查。我讀了 `Systems/規格閘.md` 裡跟判綠與紅燈版有關的 WHY 行,判讀寫在最後的「合約/事故節點」一段。

## 逐節結果
- 名詞、問題與最小解、做法 1 到 4、驗收條款、回退、實務隱患,全部讀完,各條 finding 都掛在對應的節。
- 前頭資料(frontmatter)與審計修正紀錄(空節):已讀,無 finding。
- 交叉引用:`Projects/紅燈版實跑三缺口_計劃`、`Projects/規格閘紅燈測試快照_計劃`、`Systems/規格閘`、`Systems/test-guard` 都存在,無壞引用。
- 做法 3 的註解差異(`_TG_LIT_PAT` 對 `_C_STRIP_PAT`):對照 `scripts/lumos:6786` 全部屬實。
- 做法 3 補三引號:我把 `_TG_CONST_PAT` 換成含 `_TG_LIT_PAT` 的版本,在暫存 repo 跑 `_tg_analyze`。
  - 改前:`assertEquals(1, f())` 換成 `assertEquals("""a""", """a""")` 一條都不列。
  - 改後:列 `tq/assert-weakened`。
  - S4 判紅判綠成立,這節無 finding。

## findings

1. 做法 4 說 `lumos update` 只動考場本機分支,這不是事實,回退也還原不了
severity: major
blocking: 是(實作者照字面在 mOrangePos 考場執行,會動到整台機器共用的東西,還以為能用 git 還原)
引句:「考場本機分支跑 `lumos update`,照 S5 的判準看 `lumos loop escape --list`;不推、不併,也不碰 mOrangePos 主目錄」
引句:「第 4 項考場分支 git 還原 lumos 那幾支檔」
- file: `scripts/lumos:32544` `_pull_source_or_abort` 對來源 repo(預設 `$LUMOS_HOME` 或 `~/harness/lumos-toolchain`)跑 `git pull --ff-only`。那是別的會談也在用的工作目錄。
- file: `scripts/lumos:32827` 緊接著呼叫 `_sync_global_from_project`。
- file: `scripts/lumos:33578` `_sync_global_hooks` 把 hooks 複製進 `~/.claude/hooks` 與 `~/.codex/hooks` 並合併 settings。所有專案和同時在跑的會談的 hook 都會換版,包括 `prepush-lint.py` 這類全域掛鉤。
- 這些都不在考場分支裡,回退節的「git 還原」還原不了。
- 另外 `update` 拿到的是來源 repo 當下的版本。spec 沒寫要在本計劃第 1 到 3 項併回主線之前還是之後做,所以考場拿到的可能沒有第 1 項。

2. 祖先過濾的 200 個上限放在「按迴圈篩選之前」,目標場景裡會自己關掉
severity: major
blocking: 是(照字面實作後,被忽略的治理帳累積到上限,第 1 項修復會無聲失效)
引句:「不同的 head_sha 超過 200 個就整批照舊留(不逐一問)。」
引句:「一條分支的判綠紀錄通常不到十筆」
- 計數對象錯了。治理帳被忽略時,`_redbase_branch_rows`(`scripts/lumos:14367`)回傳的是整本帳所有分支、所有迴圈的留痕與判綠紀錄,不是「一條分支的」。
- 迴圈篩選要等到 `_redbase_branch_state` 才做(`scripts/lumos:14455` 附近的 `d.get("loop") != loop`)。
- 被忽略的帳只增不減。本 repo 有追蹤的帳,在約六週內就有 74 筆 `spec-gate-record`、56 個不同 head_sha。mOrangePos 從 2026-06 起累積,再加上考場的本機分支,不同 head_sha 超過 200 個是會發生的。
- 超過後整批照舊留,等於退回修之前的行為,只印一句話。S1 在那種帳上會紅。
- ⚠ mOrangePos 實際帳量我沒量到。
- 規格寫的是在 `_redbase_branch_rows` 收齊後過濾,該函式不認識迴圈。缺口是設計層的:先篩迴圈或提高上限都沒寫。

3. 已併入主線的別條分支,它的判綠紀錄仍會漏進新分支,天花板沒寫到
severity: major
blocking: 是(「判綠紀錄限本分支」的承諾,在這個 repo 實際在用的合併流程下不成立,規格卻沒承認)
引句:「判綠時實作還沒提交、之後從同一個 HEAD 開新分支重來,那筆判綠紀錄的 head_sha 仍是新分支的祖先」
- 天花板二只講「同一個 HEAD 開新分支」。
- 我在暫存 repo 重現:分支 A 提交 Y,`merge --no-ff` 併進主線,再從主線開分支 B。`git merge-base --is-ancestor Y HEAD` 回傳 rc 0,判綠紀錄被留下。
- 這個 repo 的 PR 是 merge commit(`7d029f469 Merge pull request #154`)。
- 結果:治理帳被忽略、同一份計劃的同名測試在 B 上重新判紅時,「曾判綠」會再次擋掉紅燈版。這跟 spec 開頭那個事故是同類。
- 單純排除「分岔點以前的祖先」不能當解法。分岔點(HEAD 等於分岔點)當下寫的判綠,可能是這條分支自己的,也可能是同源兄弟分支的,需要決策。
- spec 至少要把這個天花板寫進去,並決定要不要處理。

4. S3 的次數檢查看不到索引內部的預處理退化
severity: minor
blocking: 否(S3 條款字面成立,只是它所替換的原測試想抓的錯會漏掉)
引句:「同一個 cache 底下 1000 個名字,`_TitleIndex` 要恰好建 1 次;牆上時間 60 秒內只當安全網」
- 我把 `_TitleIndex._join`(`scripts/lumos:68804`)改成不快取,其他照 spec 做法:換 `_raw_test_titles`、用計數子類、走 `_name_collision_reason`。結果建構次數 1 次、耗時 5.31 秒。
- 這同時通過「恰好 1 次」和「60 秒內」。正常路徑是 0.28 秒。
- 原測試 docstring 的「應抓到的錯:每個名字對每個標題重做預處理」被換掉後沒有補上等效守衛。
- 這條只能靠 `_join` 的建置次數或把牆上門檻收緊來補。

5. S5 的觀察字樣 `★已撤回★` 在輸出裡不存在
severity: minor
blocking: 否(驗收者可能照字面找不到而誤判不通過)
引句:「那兩筆原列尾端有 ★已撤回★」
- file: `scripts/lumos:20114` 實際輸出是 `★已撤回(原因;簽名,日期)★`,中間帶括號內容。
- 標頭 `其中 2 筆已撤回(統計不算)` 與 `scripts/lumos:20100` 吻合,這部分沒問題。

6. 做法 3 對三處 fullmatch 的描述跟程式不符
severity: minor
blocking: 否(實作者會自己搜 `_TG_CONST_PAT`,但描述會誤導驗收對照)
引句:「判預期值是常值、判實際值是常值、判兩邊都常值」
- 實際三處是:
  - `scripts/lumos:49191` 單參數的 `assertThat(x)` 的 x 是常值。
  - `scripts/lumos:49195` `assertTrue`/`assertFalse` 的條件是常值。
  - `scripts/lumos:49197` 實際值參數全是常值。
- 沒有「預期值」或「兩邊」的那一處。

7. 採用「祖先」過濾,等於翻掉既有 WHY 的一條「不選」理由,spec 沒寫要改
severity: minor
blocking: 否(知識圖譜漂移,不影響程式)
引句:「天花板一:壓過或 rebase 過的分支,壓掉的提交上的判綠紀錄不再算數」
- file: `docs/lumos-toolchain-knowledge/Systems/規格閘.md:51` 的 WHY 寫「同一條分支之後再跑出紅,那支不存紅燈版」。
- 同一行的 `[不選:記寫入當下的版本編號…(壓提交後原提交不在…)]` 正是因為壓提交才否決版本編號。
- 本計劃改用 head_sha 祖先,同樣受壓提交影響。spec 的 lands_in 列了 `Systems/規格閘`,但沒寫要把這條 WHY 改成條件式。

## 實務隱患逐類
- 效能:祖先判斷只在 `_redbase_attach` 有紅燈版素材時呼叫一次(`scripts/lumos:14511`),不在熱路徑。風險在 finding 2 的上限語意,不在速度。
- 回滾:第 1 到 3 項回退成立。第 4 項見 finding 1,全域 hooks 與來源 repo 的拉取不可回。
- 併發:同一工作樹同時兩個規格閘,本設計只讀不寫,沒有新的判錯路徑。各工作樹的被忽略治理帳彼此獨立,無共用。無新增風險。
- 其他平行路徑:`spec-gate-green` 與 `spec-gate-record` 只有 `_redbase_branch_state` 讀工作目錄那本帳。推送時比對工具讀的是 git 範圍裡的帳,不需要祖先過濾,所以沒有漏過濾的第二條讀取路徑。
- 判綠失敗的方向:被誤丟的判綠紀錄會多存一份實作後的紅燈版,讓作弊起點失效。這是 spec 已承認的天花板一方向,spec 沒寫但屬實的是 amend 與 rebase 都會觸發。

## 合約/事故節點(固定席)
- `Systems/規格閘.md` 判綠 WHY(`[test:t_spec_gate_redbase_skips_after_green]`):行為在壓提交與 rebase 後變成條件式,不是被破壞。但需要寫回,見 finding 7。
- `Systems/規格閘.md` 紅燈版寫入 WHY(`[test:t_spec_gate_redbase_written_on_red]`):格式與寫入不動,不影響。
- `Systems/test-guard.md`:第 3 項只讓 `tq/assert-weakened` 對三引號常值多列,沒碰合約行。我實跑確認 `assertEquals("a", "a")` 本來就會列,新增行為與既有單行字串一致,不影響。
- 其餘節點沒附,我沒另外判。

最嚴重 severity 是 major,blocking 共 3 條。

我的暫存目錄是 `/tmp/lumos-seat-work/判綠紀錄限本分支與撞名測試改計數/正確性-sonnet/`,裡面只剩 `t1.py`、`t2.py`、`t3.py` 三支實驗腳本。已刪掉自己建的暫存 repo,整個目錄留給編排者收貨後刪。
