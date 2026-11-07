severity: major

上一輪正確性席 F1(git status 仍會執行 core.fsmonitor)已修好。我另外測了過濾器名字的各種寫法,都沒漏。新發現兩個 major,另有一個 minor。

## 核對上一輪 F1:已修好

- 輸入:臨時 repo 設 `core.fsmonitor`、`filter.Evil.clean`(大寫)、`filter.my.dot.clean`(名字含點)、只有 `smudge` 的 `filter.sm`、`filter.pr.process`(搭配 `required=true`)。四支檔大小不變、內容改過,再用 `.gitattributes` 指到各過濾器。
- 對照組:直接跑 `git status`,記號檔被造出(fs、Evil、dot、pr 都有)。
- 實際:`_lint_wt_git(R,"status","--porcelain=v1","-z","--untracked-files=all")` 回傳 rc=0,四支檔都顯示 ` M`,**沒有記號檔**。
- 預期:不執行任何設定指令。結果符合。
- 另外驗過:`lumos spec-freeze` 相關 126 個測試全過。`_lens_git` 加 `data` 之後,既有呼叫端不傳 `data`,走原路,行為沒變。

## F1 `_lint_wt_unready` 把 git 本身壞掉(rc 128)當成「刻意不查」,鉤子記成綠
這是上一輪通才席 F1 的同類洞,補丁只補了 git 跑不起來(回傳 None)這一半。

- 輸入:HEAD 檔內容被寫成 `garbage`(`git rev-parse --verify -q HEAD` 回 rc=128)。同理適用「不是 git repo」「dubious ownership」這類 git 直接拒絕工作的情況。
- 實際:`_lint_wt_unready` 回 `('deliberate','這個 repo 還沒有任何提交(沒有 HEAD),工作樹模式沒有基準可比')`。我實跑確認過,原因文字也是錯的。
- 預期:`--verify -q` 在「HEAD 真的不存在」時回 rc=1,rc=128 是 git 出錯。實測空 repo 回 1、非 repo 回 128。128 該回 `failed`。
- 影響:`_unchecked_kind` 對 deliberate 回 None,鉤子不記事件。收工檢查在這種 repo 每回合都沒作用,卻看不出來,正是補丁要消滅的「寧可記失敗,不記成綠」。
- 修法:只在 rc==1 時才算 deliberate,其餘 rc 都回 `F`。

引句:「return D, "這個 repo 還沒有任何提交(沒有 HEAD),工作樹模式沒有基準可比"」
severity: major
blocking: 是

## F2 SARIF 64MB 上限對所有模式生效,大型舊專案的推送閘會被靜默放行
- 輸入:`_lint_run_and_parse("python3.14 gen.py {LINT_SARIF_OUT} 150000", repo)`,產出約 70MB 的合法 SARIF(15 萬條告警)。
- 實際:回 `([], False)`。100 條時回 `(100 條, True)`。
- 預期:非工作樹路徑(推送前閘)照舊解析。
- 影響:`False` 在 `_lint_new_classify` 歸為 env,於是 `autopass=True`、狀態變 `env-unavailable`,推送閘自動放行。記帳理由寫「工具沒裝/逾時/拉不到規則」,實際是檔太大,理由是錯的。dotnet/Roslyn 這類會輸出整個方案告警的工具,舊專案超過 10 萬條不稀奇。
- 補丁動機是工作樹模式的記憶體,但 `if os.path.getsize(temp_path) > _LINT_SARIF_MAX_BYTES:` 沒有限定 `_LINT_WT_REG is not None`,也沒有獨立的狀態種類。
- 修法:上限只在工作樹模式生效(或超過時走獨立的「輸出太大」種類並擋,不歸 env 自動放行)。

引句:「if os.path.getsize(temp_path) > _LINT_SARIF_MAX_BYTES:」
severity: major
blocking: 是

## F3 HEAD 版超過大小上限但工作樹版已縮小的檔,舊告警全被當新增
- 輸入:HEAD 的 `Big.kt` 超過 `max_file_bytes`,工作樹改成小檔。
- 實際:`_lint_wt_pairs` 回 `('Big.kt', None)`,`skipped` 寫「整支當新檔」。這檔裡原本就有的告警全算新增,收工會擋。
- 預期:至少讀基準比對,或像超大檔一樣給可放行的指紋。
- 影響:只在「把超大檔縮到上限以下」時發生,場景窄。
- 這個行為是補丁刻意取捨,已寫在 skipped 說明裡。

引句:「skipped.append({"file": p, "why": f"HEAD 那一版超過 {cfg['max_file_bytes']} 位元組,沒讀基準,整支當新檔"})」
severity: minor
blocking: 否

總結:最嚴重是 F1(git 回 rc 128 被記成刻意不查)與 F2(64MB 上限讓非工作樹模式的大專案靜默放行),會擋 2 條;shell=False 的參數轉換、過濾器各種寫法、`_lens_git` 加 stdin 都實測沒問題。

臨時目錄 `/tmp/lumos-seat-work/code-android寫法回合結束檢查/正確性-sonnet` 已刪。
