severity: minor

這一輪我沒找到會讓閘做出錯誤行為的缺陷,只有四條清理或文件類的 minor。

**第一輪 F1 到 F6 的核對**

我實跑了 `_plan_first_days`、`_plan_src_path_ok`(`scripts/lumos`、`./scripts/lumos`、行號與範圍、`scripts//lumos`)、`_doctor_plan_sources_lines`,其餘以讀碼核對,全部修好:
- **F1(掛鉤文案沒綁測試)已修**:新增 `t_psrc_hook_generic_message`,直接讀 `scripts/hooks/pre-push` 的原文來比對。
- **F2(健檢例外印綠勾)已修**:例外改走 `warn_soft`,並有測試。
- **F3(新舊判斷兩份)已修**:只剩 `_plan_sources_is_new` 一份,健檢傳預取的 `firsts`。
- **F4(圖譜在 repo 根時前綴失效)已不存在**:首次加入日改成整個 repo 一次掃,不再用 `vrel` 前綴。
- **F5(逾時悄悄退回)已修**:逾時會往 stderr 印一行,並有測試。
- **F6(行號不驗)已修**:行號交給 `_validate_repo_ref`,`:999` 與 `5-2` 都會被擋。

我在本 repo 實跑,整個 repo 掃一次耗時 0.25 秒;健檢那段(`_doctor_plan_sources_lines`)1.0 秒、36 次 git。效能沒有問題。

F1 規格閘筆記還留著已刪機制的 PITFALL 修法
引句:「WHY:計劃第一次進 git 的日期只有 _plan_first_days 一套」
severity: minor
blocking: 否
- 失敗情境:這次新增的 WHY 行說首次加入日「只有一套算法」。但 `Systems/規格閘.md` 第 56 行的 PITFALL 沒動,`[修法:_plan_first_day 只用 diff-tree -M 逐跳追改名]` 仍在。`_plan_first_day` 已改成查快取、不再逐跳呼叫 `diff-tree`。
- 代價:下一個 session 讀到修法,會以為單篇路徑還有逐跳那套。這句話對不上程式碼,違反專案「筆記跟程式對不上」的處理規矩。
- 同樣的舊敘述還在 `Projects/高風險測試證據加嚴_計劃.md` 第 99 行與第 161 行(「只追改名…diff-tree -M 看它是不是…」,這兩處是歷史計劃,可標明已被取代)。
- 更簡單的做法:把第 56 行的修法改成「只開 -M 不開 -C,整 repo 一次 git log 依序接改名」,並指到 `_plan_first_days`。

F2 單篇規格閘對舊計劃也要掃整個 repo 歷史,結果存全部路徑
引句:「"--name-status", "--format=%x01%cs"],」
severity: minor
blocking: 否
- 失敗情境:以前單篇只追那一支檔的改名,最多幾次 git。現在 `lumos spec-gate <單篇>` 遇到 `created` 早於生效日的計劃,就要跑整個 repo 的 `git log -M --name-status`。
- 代價:歷史長的消費專案,每次對舊計劃跑規格閘都付一次全歷史掃描,最長到 60 秒逾時。結果字典存進 repo 內所有曾經被新增或改名的路徑,快取最多留 8 份,記憶體隨歷史線性長。
- 實際需要的只有 Projects 下的 `_計劃.md`,以及它們改名鏈上的舊路徑。
- 更便宜的做法:存字典時只留與計劃相關的路徑。單篇查詢可以先用 `git log --diff-filter=A -- <路徑>` 判斷「是否在生效日之前進 repo」,只在需要接改名時才升級成全掃。

F3 符號連結只驗目標沒有跑出 repo,不驗它還在不在
引句:「if not target or target.startswith("/"):」
severity: minor
blocking: 否
- 失敗情境:HEAD 裡有 `scripts/x -> nonexistent`(指向 repo 內但不存在的檔,或指向目錄),或 `scripts/a -> b`、`b -> /etc/hosts` 這種連鎖。`_plan_src_path_ok` 只看第一層目標的字面路徑沒跑出 repo,就回 True。
- 代價:出處標準是「讀者 clone 下來查得到」,懸空連結或連鎖指到 repo 外的連結照樣算出處。這是本輪新補的符號連結守衛的缺口。
- 威脅模型是單人、AI 依序操作,所以只列 minor。
- 更簡單的做法:對符號連結的目標遞迴呼叫 `_plan_src_path_ok`(設跳數上限),讓它必須是 HEAD 樹裡的 blob。

F4 擋下留帳去重的指紋在有出處格時忽略問題清單
引句:「fp = _hl.sha256(_j.dumps([rel, cells or probs], ensure_ascii=False).encode("utf-8")).hexdigest()」
severity: minor
blocking: 否
- 失敗情境:`cells` 一旦有內容,指紋只算被擋的出處格。同一份出處格不變、但別的問題變了(例如表頭被改壞、又多出重複節),指紋相同。
- 代價:`sources-missing` 事件被當成重複而不寫,治理帳少了一筆「問題清單已變」的擋下紀錄。
- 更簡單的做法:指紋改算 `[rel, cells, probs]` 三者。

總結:最嚴重是 minor,會擋 0 條。
