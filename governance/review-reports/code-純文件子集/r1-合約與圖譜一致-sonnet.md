severity: major

## F1 純文件推送的「文件子集」漏掉一支真正在驗文件內容的既有測試,CI 也接不住

severity: major
blocking: yes

觀察到什麼:`_docs_suite_select`(scripts/test_lumos.py)挑子集的辦法是對每支測試函式呼叫 `inspect.getsource(t)`,用 regex 找函式**自己的原始碼字面**有沒有提到 `_DOCS_SUITE_PATHS` 裡的名字(README、CLAUDE、docs/ 等)。但既有測試 `t_commands_table_shape`(scripts/test_lumos.py:6816,本來就存在、不在這批新增範圍)驗的正是「README.md 等文件裡的 markdown 表格格數要跟表頭一致」,它的檔案清單完全外包給一支輔助函式 `_doc_files_for_guards(root)`(scripts/test_lumos.py:6372,會真的去讀 README.md/README.en.md/ONBOARDING.md/ARCHITECTURE.md/CLAUDE.md/AGENTS.md/SDD-vs-Lumos.md/docs/methodology 等)——但 `t_commands_table_shape` 這支函式**自己的原始碼裡完全沒有出現任何一個 `_DOCS_SUITE_PATHS` 的字樣**(它只呼叫 `_doc_files_for_guards(root)`、`_md_table_rows(...)`),於是被 `_docs_suite_select` 的字面比對漏掉。

怎麼重現:
1. `python3 scripts/test_lumos.py --list --suite docs 2>/dev/null | grep t_commands_table_shape` → 沒有輸出,證實這支測試不在文件子集裡。
2. 在 worktree 裡把 README.md 一張表格的一格跟下一格黏在一起(製造真的斷欄):
   ```
   - | 為什麼這樣設計?哪些規則要保留? | 可查詢的決策、邊界與合約筆記 |
   + | 為什麼這樣設計?哪些規則要保留?可查詢的決策、邊界與合約筆記 |
   ```
3. `python3 scripts/test_lumos.py -k t_commands_table_shape` → 真的抓到:`✗ ★表格每一列的格數都跟表頭一樣★  共 1 筆:['README.md:36 這列 1 格,表頭(第 34 行)2 格']`,`1 passed, 1 failed`。
4. 但這次改動只碰了 README.md,`lumos pitfalls --diff` 會判 `suite: docs`——照這批的設計,推送前掛鉤只跑 `--suite docs`(不含 `t_commands_table_shape`),而 CI 那一步(.github/workflows/ci.yml 的「這次推送要跑哪個測試範圍」)一樣是 `suite=docs` 才給分片帶 `--suite docs`、不會落回全套。也就是說這批斷欄的 README 改動,推送前跟 CI 都不會被這支現成的守衛測試攔下——而它本來(全套永遠跑)是攔得住的。

為什麼是 bug 而不是風格:這不是「少省一點時間」的取捨,是**已經存在、專門為了防這一類回歸而寫的測試被新機制悄悄關掉**,而且恰好是「純文件推送」這個新機制第一個要服務的場景。字面比對這個挑選機制本身有結構性缺口:任何測試只要把「掃哪些文件」外包給輔助函式、自己不重複寫路徑字樣,就會被漏掉,而且沒有任何機械訊號會提醒——以後新增的文件驗證測試如果照同樣寫法(呼叫共用輔助函式而不是自己重複列路徑),還是會一樣被漏掉。

file: `scripts/test_lumos.py:6816`(t_commands_table_shape,委外給輔助函式)
file: `scripts/test_lumos.py:6372`(_doc_files_for_guards,真正讀 README/CLAUDE.md 等的地方)
file: `scripts/test_lumos.py:56`(_docs_suite_select,只看被測函式自己原始碼的字面)

引句:「挑出原始碼裡提到任何一個純文件路徑的測試(README.md 也認 README、README.en.md)。」

## F2 「light 推送、keys 子集有紅要擋」這條路完全沒有任何測試走到過,新增測試的假執行器結構性走不到那條路

severity: major
blocking: yes

觀察到什麼:pre-push 對 light 改動多跑一趟 `--suite keys`,真正擋下推送的判斷在:
```
elif [[ "$_krc" -ne 0 ]]; then
  _rc=1
fi
```
(scripts/hooks/pre-push:418,`_krc` 是 `--suite keys` 那趟執行器的離開碼)。這條分支唯一會生效的前提是「有測試對到關鍵字、而且真的跑紅」(離開碼是非 0 非 3,例如測試真的斷言失敗回 1)。但這批唯一驗這段的新測試 `t_prepush_docs_and_light_run_subset`,把 `scripts/test_lumos.py` 換成一支假執行器:
```
sys.exit(3 if 'keys' in sys.argv else 0)
```
(scripts/test_lumos.py:44188)也就是只要參數裡有 `keys` 字樣就固定回 3(「沒對到任何測試」那條路),其餘一律回 0(全過)。這支假執行器**結構上不可能回傳除了 0、3 以外的任何離開碼**,所以 `_krc` 永遠不是「非 0 非 3」,pre-push 裡 `_rc=1` 這一行在這批新增的測試裡完全沒有被執行到過一次。

怎麼重現(靜態確認,不需要真跑):全 repo 搜尋只有這一處呼叫 `--suite keys`(scripts/test_lumos.py:44165、44174 一帶),而唯一模擬「這一趟測試真的有紅」情境的地方是上面那支假執行器,它的離開碼硬編碼成 `3 if 'keys' in sys.argv else 0`——沒有任何分支能產生「keys 有對到、但其中有測試斷言失敗」的離開碼(例如 1)。同一批新增的 `t_runner_suite_flags` 也只驗證真執行器在「keys 0 支」時回 3(`check("keys 0 支:rc3...", r.returncode == 3 ...)`),同樣沒有一處驗證「keys 選中了測試、其中有測試斷言失敗」時執行器回什麼、pre-push 收到後會不會真的擋下推送。

為什麼是 bug 而不是風格:這正是「light 分支唯一的安全網」——light 是新開的口子,允許改到程式檔卻跳過全套,唯一補償是「至少把對到關鍵字的測試跑過、紅了要擋」。如果 `_krc` 的判斷式寫錯(例如離開碼判斷顛倒、或忘了把 `s0-keys.log` 併進 `_TESTS_LOG` 導致訊息印不出紅的是哪支、或執行器某個中間版本改了離開碼慣例卻沒人發現),擋不住的推送不會有任何測試翻紅去抓——這正是「該擋卻沒有任何測試證明擋得住」的形態,不是覆蓋率高低的取捨。

file: `scripts/hooks/pre-push:414-419`(_krc 判斷與 _rc=1)
file: `scripts/test_lumos.py:44174-44214`(t_prepush_docs_and_light_run_subset,唯一涵蓋 light+keys 的測試)

引句:「"$PY" "$REPO_ROOT/scripts/test_lumos.py" --suite keys --keys "$_SUITE_KEYS" > "$_sdir/s0-keys.log" 2>&1 || _krc=$?」
引句:「sys.exit(3 if 'keys' in sys.argv else 0)」

## F3(minor,不擋)docs 子集「明顯小於全套」的上限是拍出來的,跟實測值差距很大

severity: minor
blocking: no

觀察到什麼:`t_runner_suite_flags` 用 `0 < len(names) < total * 0.3` 驗「docs 子集明顯小於全套(不然省不到時間)」。實測(worktree 內跑 `--list --suite docs` 對 `--list`)是 191/1021 ≈ 18.7%,離 30% 這個上限還有不小距離,30% 這個數字在 patch 裡沒有任何量測依據或註解說明怎麼訂出來的,只是憑感覺留的餘裕。這條目前不會紅,也不影響行為正確性,純粹是「這個門檻是不是有量測依據」這個問題本身答案是「沒有,是拍的」,但因為留了餘裕、目前無害,不升等。

引句:「docs 子集明顯小於全套(不然省不到時間)」

## 已驗過但沒發現問題的路徑

- CLAUDE.md「CI 對純文件推送也只跑文件子集」這句話跟 `.github/workflows/ci.yml` 新增的「這次推送要跑哪個測試範圍」步驟一致:CI 完全沒有 light 的概念,只認 pitfalls 回的 `suite`,非 `docs` 一律退回全套——跟《雙向門放行_計劃》裡「CI 仍跑全套當後盾」對 light 這句吻合(CI 本來就不知道 push-check 判的 light,任何程式檔改動都會讓 `_test_suite_for_range` 回 full)。
- `_docs_only_file`(scripts/lumos)跟「每支檔有家」既有的 `_is_code_file` 共用同一顆底層判斷 `_nodehome_code_kind`/`_head_is_shebang`,但 `_is_code_file` 多了 `_NODEHOME_EXCLUDE_GLOBS`(含 `docs/*`)、`_nodehome_is_test`、ignore 設定三層排除,`_docs_only_file` 沒有套用——會不會因此把本該視為程式碼的檔誤判成「純文件」?查證後方向是安全的:`docs/*` 這種豁免只會讓 `_is_code_file` 更寬鬆(不需要有家),但 `_docs_only_file` 只要副檔名落在 `_NODEHOME_CODE_EXTS` 就直接判 `full`,不管豁免不豁免——兩邊分歧只會往「多跑全套」那個方向倒,不會漏判成 docs。這是第二套定義沒錯,但沒有製造危險方向的分歧,列為觀察不升等發現。
- `t_docs_suite_whitelist_matches_lumos` 用的 `_load_lumos_inproc()` 是真的用 `SourceFileLoader` 把 `scripts/lumos`當模組載進來執行(不是讀字串比對、不是抄一份常數),`_DOCS_ONLY_PATHS` 跟 `_DOCS_SUITE_PATHS` 相等這件事有真的被驗到。
- 分片與子集的順序(先挑子集再切片)、`--suite docs`/`--suite keys` 互斥旗標檢查、rc2/rc3 的區分,都對照 patch 逐行讀過,邏輯跟訊息文字一致,沒找到分歧。
