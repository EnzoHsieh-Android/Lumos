severity: minor

合約與圖譜鏡頭的結論:沒有破壞既有合約,也沒有漏掉的讀者或寫者,只有兩條措辭層級的殘留。我讀了 diff 的 `scripts/lumos` 與圖譜筆記各 hunk,並回到 repo 查證。

- **「覆蓋接不起來」**:這不是新斷路原因。它已在 `_CHOICE_REACH_TEMP` 的暫時性清單裡(`scripts/lumos:79716`),`reach_why`、`--reach-only` 重補、計劃的原因表都已涵蓋。新的 `settle` 斷路只是多一條路徑指向同一個字串,沒有漏讀者。
- **`.base.json` 寫者與清快取**:
  - 寫者只有 `store()` 一處,且只在 `keep` 且路徑以 `.exec` 結尾時寫;失敗走 OSError 回 None。
  - 讀者 `_choice_cov_base_read` 對壞檔、過大、非綠都回 None,`cached()` 會連 `.exec` 與 `.base.json` 一起刪掉重量。
  - `_choice_cov_prune` 用 `shutil.rmtree` 整個 at_sha 資料夾清,會連帶清掉 `.base.json`,不需要改。
- **`_choice_merge_facts`**:只有 `_choice_merge_classify` 一個呼叫者(`scripts/lumos:29015`)。回傳形狀沒變,空殼檔略過後每支目標測試仍由 classify 要求恰好對到一筆。全是空殼時照舊回「結果檔讀不出來(zero_cases)」。
- **基準快取形狀**:`cached()` 放回 `c.baselines` 的五元組與 `scripts/lumos:28537` 的寫法一致。
- **guard-kill 的 rc 優先序與 `--json`**:新增的 `trip`、`settle` 只印 stderr,沒動 rc 與 JSON 輸出。
- **筆記指到的測試**:`t_choice_cov_proj_pkgs`、`t_choice_merge_stray_empty_suite`、`t_choice_cov_resume`、`t_choice_cov_red_breaker`、`t_choice_cov_rerun_edges`、`t_choice_kill_merge_interrupt` 都存在。`_ChoiceKillRun._on_first` 也存在。

severity: minor
blocking: 否
`scripts/lumos:29239`:`take` 的說明字串還寫著判 Robolectric 的舊規則,與補修後的 `_choice_cov_exec_robo` 不符。補修把判定改成看 `AndroidTestEnvironment`、`AndroidSandbox`、`SdkEnvironment` 這三個類別有執行紀錄,同一個 diff 改了 `_choice_cov_exec_robo` 的說明,卻漏了這處。三個月後的人照這句會以為「有任一 `org/robolectric/` 類別就算」,這正是補修要修掉的誤判(334 份中只有 284 份真的建了環境)。只影響閱讀,行為不受影響。
引句:「記 got、數專案類別、看是不是 Robolectric(覆蓋資料有 org/robolectric/ 類別);」

severity: minor
blocking: 否
`docs/lumos-toolchain-knowledge/Issues/選擇點存活回指第一段末輪小問題第二段先修.md:3`:這篇 Issue 的 summary 仍把第 1 條寫成未修。`status: open`、`updated: 2026-11-26` 沒動,也沒標第 1、2、3、4、6 條已修。
- summary 的 PITFALL 還帶著 `[repro:t_choice_cov_rerun_edges 加一案:掛覆蓋與不掛都逾時 → 現在 tripped 為真]` 與 `[修法:不掛重跑綠才斷路]`。這個重現在補修後已經變綠。
- 新增的「進度」節與 `什麼條件算修好` 節矛盾。後者仍寫「第二段開工的第一個提交把 1–7 條修掉」。
- 下一個接手的人用 `lumos search` 只會讀到 summary,會誤以為第 1 條還沒修。
- 同樣的小遺漏:計劃與 `Systems/guard-kill.md` 正文已改,但兩篇的 `updated` 日期沒跟著改(計劃 2026-11-24,guard-kill 2026-11-26)。
引句:「- 還剩第 5 條(沒有 Gradle 快取的機器只做靜態檢查)、第 7 條(測試唯讀真的 Gradle 快取),留給第二段開工。」

總結:最高等級是 minor
