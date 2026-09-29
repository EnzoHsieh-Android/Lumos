severity: major

# r2 回滾鏡頭報告(預設它要退回去)

先答派工問的四樣留下來的東西:
- `git config lumos.python`:舊版 lumos 與舊掛鉤全程式碼都沒讀過 `lumos.python` 這個鍵(grep 只有 `merge.*.driver` 一處 git config 讀取),留著無害,〈回退〉那句成立。唯一連帶:`lumos deinit/teardown` 的舊版不會清它(不是回退問題,是殘留)。
- `{python}`:只寫在工具鏈自己 repo 的 `.lumos/config.json`(第 6 點),不是消費專案。`lumos update` 只複製名單上的檔,不動消費專案的 config;`lumos init` 骨架用 `_SKELETON_RUN_CMD`(`python3 -m pytest -k {method}`),spec 沒說要改。舊版讀到 `{python}` 會怎樣:三處代入點(`cmd_guard_kill`、`_bound_tests_filter_probe`、合約測試閘)只換 `{method}`,字面 `{python}` 交給 shell,實測 `sh: {python}: command not found`、rc 127;guard kill 有 baseline 非綠就 abort(不會誤判成「殺到了」),合約測試閘整批紅。所以是「壞得很響」而非假綠;只要 `.lumos/config.json` 跟程式碼同一次還原就不會發生(見 F3 對「只回退擋下」的例外)。
- CI 範例補的「裝 3.14」一步:舊版 CI 上多裝 3.14 無害,不必清。
- doctor 新提醒:隨程式碼還原就消失,舊版不讀 Claude/Codex 設定裡的直譯器路徑,不必清。

## F1 〈回退〉漏了錨點:消費專案回退後推送會被「永遠不可跳」的 anchor verify 擋下
severity: major
blocking: 是 — 照〈回退〉三條做完的消費專案(有 anchor 基準線的)下一次 push 就被擋,而且照舊版提示的處理順序做錯還會擋第二次
引句:「更新完手動刪掉消費專案 `scripts/hooks/` 底下留下的共用檔(工具只複製名單上的檔、不刪舊檔,殘檔會被當成專案自己的程式掃)。」
file: `scripts/lumos:19960-20012`
file: `scripts/hooks/pre-push:130`
file: `scripts/lumos:18573-18590`
1. 現況:消費專案的 `pre-push` 在 doctor 之前先跑 `lumos anchor verify`(pre-push 第 130 行),有 `governance/anchor-baseline.json` 就逐檔比 sha256,並且用檔案系統對 `scripts/hooks/**` 做集合檢查(`_present - _listed` 報「多了 N 支沒登記的檔」、`_listed - _present` 報「登記過但檔案不在了」);程式註解與 `_anchor_blocked` 都寫「這道永遠不可跳」。
2. 前進路徑要人跑 `lumos anchor approve`(spec 第 1 點只對工具鏈自己的 baseline 寫了),消費專案已核可過新版三支掛鉤與共用檔(S9 把共用檔放進 `ANCHOR_FILES`)。
3. 回退時 `lumos update` 把 `pre-commit`、`pre-push`、`post-commit` 換回舊版內容 → 三支的 sha256 對不上基準線 → 擋 push。〈回退〉三條完全沒提 `lumos anchor approve`。
4. 順序陷阱:〈回退〉叫人「更新完手動刪掉共用檔」。舊版 `lumos anchor approve` 用舊 `ANCHOR_FILES`(不含共用檔)寫基準線;若共用檔還在就 approve,下一次 verify 會報「多了 1 支沒登記的檔」;若已 approve 過新版、刪檔後沒重簽,報「登記過但檔案不在了」。所以正確順序是:update → 刪共用檔 → 舊版 `anchor approve --note`,而且每個消費專案各做一次。spec 沒寫,也沒寫回退本身要提交(消費專案的 vendored 檔是已提交檔,刪檔與換檔要進一個提交,然後才推得上去)。
5. 工具鏈自己 repo 不受影響(還原提交連 baseline 一起還原);受影響的是每一個有基準線的消費專案。CI(`ci.yml` 也跑 `anchor verify`)同樣紅。
6. 對「只回退擋下」同理:掛鉤內容變了,經 `lumos update` 到消費專案後一樣要重簽。

## F2 「主線已有後續提交」那條的 3.9 檢查驗不到會炸的東西
severity: major
blocking: 是 — 照做通過檢查後回退,3.9 上仍會在執行期崩,而且是〈回退〉自己宣稱要防的情況
引句:「還原前先用真的 3.9 編譯一次 `scripts/lumos` 與 `scripts/hooks/**`,確認回退窗口裡沒人寫進 3.10 以上的語法」
file: `scripts/test_lumos.py:35832-35851`
1. 我在本機 3.9.6 實測:`compile()` 一段含 `def f(x: int | None)`、`import tomllib`、`zip(..., strict=True)` 的程式,編譯通過(這三樣都是執行期才炸)。spec 第 2 點自己就說 `def f(x: int | None)` 在 3.9「定義當下就會丟 TypeError」,所以編譯這一步對這類寫法無效。
2. 第 10 點就是把 `_toml_loads` 的代解分支改回直接 `import tomllib`(3.11+ 才有);回退窗口裡只要多一處同類新寫法,編譯照過、實跑才紅。
3. `scripts/hooks/**` 底下 `pre-commit`、`pre-push`、`post-commit` 是 shell,不能用 Python 編譯;只有 `claude/*.py` 那幾支可以,「編譯全部」對 shell 掛鉤是空檢查(該用 `bash -n`,並且用 3.9 實跑一次 `python3 scripts/lumos --version` 或掛鉤 smoke)。
4. 要驗的其實是「用 3.9 實際載入 `scripts/lumos`、跑一組子集測試」,不是編譯。

## F3 「只回退擋下」沒說清楚另外兩條擋下路徑要不要一起退
severity: minor
blocking: 否 — 有殘留的擋下路徑,但不會壞系統,操作者看訊息能自己解;只是〈回退〉描述的「掛鉤放行」與實作可能不一致
引句:「git 掛鉤找不到 3.14 時改成印提醒並跳過檢查——★是整道檢查不跑,不是改用 3.9 跑★」
1. spec 的擋下有三條:找不到 3.14(第 3 點)、`LUMOS_PYTHON` 有設但不合格「停下報錯,不往下找」([S1])、共用檔不見「印另一段說明並擋下」([S3])。〈回退〉只說第一條改放行,後兩條沒提;字面實作後,`LUMOS_PYTHON` 設了舊路徑的機器與殘缺安裝仍然被擋,跟這一項的目的(退回放行)不一致。
2. 同一條的「要講明的後果」沒提:掛鉤內容變了,依 F1 每個消費專案要重簽錨點。
3. 若這個「只回退擋下」發生在 `{python}` 已進 `.lumos/config.json` 的版本上(程式碼仍是新版):`{python}` 由新版 lumos 代入,不受影響;只有舊 lumos 讀新 config 才會 rc 127(見開頭 `{python}` 段),這種混搭只在工具鏈 repo 的 config 與 lumos 版本被分開還原時出現,〈回退〉沒有講「config.json 的 run_cmd 要跟 lumos 本體一起退」。

## F4 「不重跑安裝也不會壞」與第一條的操作互相矛盾,而且沒講 update 會重寫全域設定
severity: minor
blocking: 否 — 結果無害(舊版 python3 註冊回來而已),只是描述不精確,讀的人會誤以為設定檔沒動
引句:「Claude/Codex 設定裡的 3.14 絕對路徑照樣跑得動舊版掛鉤,不重跑安裝也不會壞。」
file: `scripts/lumos:18262-18272`
file: `scripts/merge-claude-settings.py:322-330`
1. 同一條前面叫人跑 `lumos update`;`cmd_update` 走 `_vendor_toolchain` 尾端的 `_sync_global_from_project`,對 claude 與 codex 都跑一次 merge。舊版 merge 用 `_equivalent`(只比 matcher 與腳本檔名)認出同一支 hook,`existing != new_entry` 時直接取代並印 `[migrate]`,所以引號包住的 3.14 絕對路徑會被換回不加引號的 `shutil.which("python3")`(在 macOS 上就是 3.9)。
2. 結論(舊掛鉤能跑)成立,但實際是「update 會把註冊改回舊版寫法」,不是「設定留著不動」;且這是機器全域動作,一個消費專案回退會改掉整台機器的 `~/.claude`、`~/.codex`,其他還沒回退的消費專案共用同一份。〈回退〉沒講機器全域這點。

## F5 回退沒處理新增的圖譜節點與綁定測試
severity: minor
blocking: 否 — ⚠ 依 spec 現有文字判不準會不會擋:第 12 點新開 `Systems/python直譯器選擇` 並寫 about_code 指向共用檔、[S1]–[S10] 綁測試名;〈回退〉只說「圖譜的收尾不跟著還原」,沒說這些新節點與條款怎麼辦
引句:「圖譜的收尾(Issue 結案、兩條 REVISIT、F65)不跟著還原,另外補一篇說明「下限退回 3.9」並重開那篇 Issue。」
1. 程式碼還原後,`Systems/python直譯器選擇` 的 about_code 指向已刪的共用檔、[S1]–[S10] 的 `[test:t_...]` 指向已還原掉的測試;〈回退〉只列了 Issue、REVISIT、F65,沒列這個節點(該標 superseded 或刪)與四篇 lands_in 節點被改過的敘述。
2. 專案規則是程式碼還原這次提交也得把圖譜補回(pre-commit 擋「改 code 沒動圖譜」),所以這一步不寫,實作者到還原那刻才會被閘擋住。

## 已讀,無 finding
- 〈回退〉第 1 條「用全域或工具鏈來源那份 lumos」:全域 `lumos` 是 symlink 到來源 clone,還原後的來源 clone 用 `pull --ff-only` 就到位(還原是新提交,不是改寫歷史),舊版在 3.9 上正常;「專案自己帶的那份是新版、在 3.9 上回 2」成立。
- 「工具只複製名單上的檔、不刪舊檔」成立(`_vendor_toolchain` 結尾只 `copy2` 名單內的檔);「殘檔被當成專案自己的程式掃」成立(`_vendored_state` 只跳過名單內且指紋一致的檔)。`.lumos/vendored.json` 由舊版 update 整份重寫,不會殘留共用檔的指紋。
- 第 4 條「暫時出口」:三種方式在舊掛鉤上都無效無害,不是回退問題。

## 實務隱患(回滾視角)
- 守衛面:見 F1(回退後 push 被 anchor 擋)。
- 對外送出:README/ONBOARDING 的「3.14+」與已送出的升級注意無法收回;〈回退〉沒寫要不要在 README 補一句「下限已退回 3.9」。已裝 3.14、已改 CI 的人不受害,無需清;不列 finding。
- 不可逆:`git config lumos.python` 與 CI 範例殘留無害(見開頭);升級注意「印一次」的標記若寫進消費專案檔案,回退不會清,再前進時不會再印——spec 沒寫標記存哪,無法判定,不列 finding,實作時留意。
- 併發/效能:無。回退是逐專案手動流程,沒有新的併發面。

最高等級為 major,blocking 共 2 條(F1、F2)。
