severity: major

本席從固定版本獨立查證,結論是 1 條 major、3 條 minor。修補驗收的核心行為(三設定認部分複製、布林規則、帳被忽略時直讀工作目錄、帳進版控的部分複製不讀分岔點)修前紅、修後綠,實測成立。我沒有讀 r1 到 r3 的席報告與 cap-retro.json;列檔案名時看到了它們的檔名,內容沒開。暫存的兩個 worktree 與實驗目錄已用字面路徑刪除。

## Findings

1. S10 條款括號裡的「(或判不了是不是)」那一半沒有任何測試證到。條款與程式寫的是:部分複製或判不了是不是時,不讀分岔點那一版。綁定測試 `t_redbase_branch_rows_fallback_keeps` 只造了確定是部分複製(回 True)的案例。
   引句:「elif _git_partial_clone(rr) is not False:   # 部分複製讀分岔點那一版會自動連遠端」
severity: major
   blocking: 是
   - 重現(改壞):在 ae9c4d82 的複本把該行改成 `is True`,再跑 `-k t_redbase_branch_rows_fallback_keeps`(22 passed)與 `-k t_spec_gate_redbase`(61 passed),全綠。
   - 最小翻紅案例:一個只有判綠紀錄、帳進版控的 repo,把 `m._git_partial_clone` 換成回 None,呼叫 `m._redbase_branch_rows(root, "甲", "not")`。原碼回 `[]` 並印「部分複製(或判不了是不是)不讀…」,改壞版回出那筆判綠紀錄,也就是真的去讀了分岔點那一版。
   - 實際影響偏窄:要 `git config` 失敗而後續 git 呼叫又成功。但依本席規則,條款被保護的是驗收條款,所以標 major。
   - 歸因:有證據的修復回歸。這是修補新增的判斷分支,修前 fe970227 沒有它(修前 S10 整支紅),修後行為未見錯但該半邊沒測試。
   - 兩版證據:修前 `t_redbase_branch_rows_fallback_keeps` 有 2 條紅(S10 與 SHA-256),修後 22 條綠,改壞 `is True` 仍 22 條綠。

2. 存量漂移守衛新 WHY 綁錯測試,新原因「git 跑不起來」沒寫進回頭條件那組筆記。這同時是鏡頭 4 的答案。
   引句:「回頭條件寫下時就成立那段判 partial clone 改用共用的 _git_partial_clone(三個設定任一個成立就算、照 git 布林規則、判不了也標判不了)」
severity: minor
   blocking: 否
   - 該 WHY 綁的是 `t_drift_born_unknown`,它只證到「promisor 加 filter 一起寫」。
   - 我在複本同時改壞兩處:`_git_bool` 改成不認裸鍵與整數,並拿掉 `_drift_born_env_err` 的 None 分支。`t_drift_born_unknown` 仍 10 passed;`t_git_partial_clone_keys` 才紅 3 條(裸鍵、`promisor = 2`、S8 判不了)。
   - `t_git_partial_clone_keys` 在 docs 下沒有任何筆記綁它。用 `git grep` 查,只出現在測試檔與卷證。
   - 計劃 S8 的條款文字沒有「回頭條件判不了」。`t_git_partial_clone_keys` 的 docstring 標 S8、S10,但計劃的 S8、S10 都綁另一支測試。
   - `_drift_born_env_err` 在 `_git_partial_clone` 回 None 時回字串「git 跑不起來」。這個字串在 `git grep` 的 docs 與 skills 下,只出現在不相關的舊筆記。回頭條件計劃做法 5 與存量漂移守衛只寫「判不了也當判不了」,沒點出這個原因;該函式的 docstring 列的原因也沒有它。
   - 計劃〈回退〉說「第 1 項拿掉 `_redbase_branch_rows` 的過濾與兩處多傳的 ref」,沒提 `_drift_born_env_err` 改用 `_git_partial_clone` 這一塊。
   - 歸因:有證據的修復回歸(新寫的 WHY 與綁定出自修補)。

3. 規格閘這個家,以及舊計劃裡「相減分岔點」的句子,沒寫部分複製的新行為,也沒有家講 `_git_bool`。
   引句:「判不了的照舊算進來並印幾筆;治理帳進版控時不過濾」
severity: minor
   blocking: 否
   - 計劃天花板六與 S10 才有的行為:部分複製加帳進版控時,判綠觀測與去重整個不做。規格閘 WHY 沒寫;規格閘紅燈測試快照計劃仍寫「工作目錄的治理帳減掉分岔點那一版」。
   - `git grep` 查 `_git_bool` 在 docs 下只在計劃裡出現,沒有任何 Systems 筆記講它。
   - `scripts/lumos:15370` 印給使用者的句子「判綠過的 Kotlin/Java 測試,之後再跑出紅也不存」,在帳被忽略且壓過提交、或部分複製時不再全真。此句不在 diff 內,是佐證。
   - 歸因:有證據的修復回歸(S10 與部分複製的跳過來自 c8ce2022)。

4. 帳進版控(或判不了是否被忽略)時,SHA-256 repo 在算不出分岔點的分支上,判綠觀測與去重仍整個失效。r3 只補了帳被忽略的那條路。
   引句:「_d, added, bad = _gov_rows_delta(rr, fork or _EMPTY_TREE_SHA, None, b'"spec-gate-', _redbase_branch_keep)」
severity: minor
   blocking: 否
   - 空樹常數只對 SHA-1 的 repo 有效,所以這條路在 SHA-256 repo 上讀不出起點。
   - 實跑:建 `--object-format=sha256` 的 repo 加一份帳,`m._redbase_branch_rows(r, "甲", "not")` 在 ae9c4d82 與 fe970227 都印「讀不出起點那一版的治理帳…」並回 `[]`。
   - 計劃沒把它寫成天花板。SHA-256 的 repo 本來就極少見。
   - 歸因:有證據的原有漏查。

## 逐項核對結果

**鏡頭 1,計劃對程式。**
- `spec-trace` 顯示 S1 到 S10(S5 已移出範圍)共 9 條,全綁定、0 懸空。
- 逐條對到程式與測試:
  - 做法 1:`_redbase_branch_name`、`_redbase_branch_rows`、`_redbase_on_branch`、`_git_partial_clone`、`_git_bool` 都在。
  - 寫入端兩處多傳 ref,`_redbase_attach` 只叫一次 `_gov_ledger_ignored`。
  - 做法 2:`t_name_collision_scales` 數建構與串接次數。
  - 做法 3:`_TG_CONST_PAT` 補三引號,`_tg_ident` 與 `_TG_LIT_PAT` 說明已改。
- 順帶核對:`_TG_LIT_PAT` 用在 5 處、`_TG_CONST_PAT` 用在 3 處,跟計劃所寫相符。
- 做法 1 的 e 說「所有 git 呼叫走 `_lens_git_dl`」,但淺複製判斷走 `_git_is_shallow(timeout=t)`。它仍受截止時間約束,只是措辭不精確。

**鏡頭 2,筆記對程式。**
- 寫回的句子逐句開程式驗過,一致。
- 錯過的有 finding 2 與 3。
- 搜尋 `判綠`、`分岔點`、`整本`、`partial`、`promisor`、`15 秒`、`串接`,未見其他因這次變假的句子。
- 規格閘紅燈測試快照計劃做法 5 的舊句在 `docs` 內仍寫「淺層 clone」,屬原句,沒有變假。
- `_TG_LIMITS` 與測試品質標準兩份「抓不到」清單加的句子相同,`t_tq_guard_cli_contract` 99 passed。
- 7 篇改到的筆記 `lint` 皆 0 問題(存量漂移守衛的 2 條 warning 是舊 RULE 行,不是這次的);`lumos doctor` 為 0 issues。

**鏡頭 3,圖譜。**
- 逐條判,固定席多數與本案無關。
- 測試假綠形態的 INVARIANT(還原翻紅釘要配前置斷言)有遵守。新測試有 ★前置★ 檢查,`t_git_partial_clone_keys` 只有 ★對照★。
- `design-loop` 的處置閘第五步:計劃的 S1 到 S10 都帶 `[test:]`。
- `lumos-cli-read`、`lumos-cli-lifecycle`、`guard-kill` 的合約與本案無牽連。
- 治理帳新增 `ref` 欄位:`git grep` 查讀取端 `.get("ref")`,只有 `_redbase_on_branch` 本身、回頭重讀的 branch 欄位處理與簽核帳三處會讀,都不會把 spec-gate 事件誤讀。

**鏡頭 4。** 見 finding 2 與 3。`_git_partial_clone` 在存量漂移守衛有一條 WHY 提到;規格閘那個家沒寫;`_git_bool` 沒有任何家提到。

## 修補三問

1. **原問題的修復效果。** 我在 fe970227 的 worktree 放進修後測試檔後逐支跑:
   - `t_git_partial_clone_keys` 有 4 條紅:裸鍵、`promisor = 2`、含空白遠端名且 `promisor = false`、S8 判不了。
   - `t_redbase_branch_rows_fallback_keeps` 有 2 條紅:S10 與 SHA-256。
   - 修後在 ae9c4d82 全綠。
   - 另外用 `git cat-file -e` 加留記號的 uploadpack 腳本,驗到只寫 `partialclonefilter` 也會讓 git 去連遠端。三設定各自算部分複製的說法成立。

2. **修補處的正常、錯誤與相鄰路徑。**
   - 帳被忽略:同分支留、他分支丟、祖先留、非祖先且完整 repo 丟、淺複製、部分複製、逾時、超限都留,都有測試。
   - 帳進版控:`t_spec_gate_redbase_green_tracked_unfiltered` 證到改寫提交後仍算判綠。
   - 相鄰的回頭條件:修前後的 `t_drift_born_unknown` 都綠,修後多了新式部分複製案例。
   - 判不了是不是部分複製這一支,只有 `t_git_partial_clone_keys` 的 mock 證到(見 finding 2)。
   - 缺口只有 finding 1 與 4。

3. **新發現案例的修前與修後。**
   - finding 1:修前沒有這個分支;修後原碼回 `[]`,改成 `is True` 則回出判綠紀錄。
   - finding 4:修前修後相同,都印「讀不出起點那一版」並回 `[]`。
   - finding 2 與 3 是筆記與綁定的問題,沒有行為差別。

## 已驗主張與未驗範圍

**已驗主張。**
- 7 支相關測試在 ae9c4d82 全綠:`t_git_partial_clone_keys`、`t_redbase_branch_rows_fallback_keeps`、`t_spec_gate_redbase_green_other_branch`、`t_spec_gate_redbase_green_tracked_unfiltered`、`t_name_collision_scales`、`t_tq_guard_string_comma_args`、`t_drift_born_unknown`;另有 `t_spec_gate_redbase*`(61 passed)與 `t_name_collision*`(22 passed)。
- 三個改壞實驗:
  - `_TitleIndex._join` 不快取 → ② 紅(513 個不同 id)。
  - 拿掉 `_TG_CONST_PAT` 的三引號段 → S4 紅。
  - 改成 `is True`、改壞 `_git_bool` 與拿掉 None 分支 → 見 finding 1 與 2。

**未驗範圍。**
- 真實 blobless 或 treeless 遠端複製、Windows。
- git 2.39 以外的版本。實測環境是 Apple Git 2.39.2。
- 時鐘倒退。
- 全套測試(留給推送前閘)。

最嚴重等級是 major,blocking 共 1 條。
