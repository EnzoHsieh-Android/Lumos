severity: minor

## S1 開跑時工作目錄是髒的,跑完前清掉改動,結果照樣寫成 HEAD 的「驗過」
severity: minor
blocking: 否
- 誰:使用者本人,或照常操作的 AI。
- 從哪:`android-e2e-run.sh --feature X`。按功能跑不要求工作目錄乾淨,所以開跑時帶著未提交的程式改動。
- 送什麼:建置與驗收進行期間(最長可達數小時),他們做了 `git stash` 或 `git checkout -- <檔>`,把改動收掉。HEAD 沒變。
- 拿到什麼:`_e2e_feature_record` 只在結束時檢查工作目錄乾淨且 HEAD 等於 `start_head`,就把 `feature_runs` 寫進綁 HEAD 指紋的查證紀錄。但被驗的 APK 其實是含未提交改動的版本。開跑時記下的 `steps["dirty"]` 只拿去寫總表,沒有用來擋寫入。結果是 HEAD 那一版被記成這些情境已通過,而實際驗的是另一份程式。
- file: `scripts/lumos:40951`(`_e2e_feature_record` 的 `why = _e2e_precheck(root) or ...`)
- 建議:`steps.get("dirty")` 為真時,一律只記總表、不寫查證紀錄。

引句:「        self.data["dirty"] = lumos("android-e2e", "judge", "--repo", root, "--precheck")[0] != 0」

## S2 只列效能方法的情境,零項目也判 pass 且 complete 為真
severity: minor
blocking: 否
- 誰:使用者本人,或照常操作的 AI。
- 從哪:`--case 功能.情境`,對到的情境只列了 `macrobench`(效能測試方法),沒有 flows、visual、stability。
- 送什麼:這個情境的 `items` 是空清單。
- 拿到什麼:`rs` 為空,`probs` 也為空,於是 `result` 判成 `pass`,`complete` 為 True。效能那一步就算回傳碼非 0,也只進 notices。結果是沒有驗到任何東西的情境,在綁指紋的查證紀錄裡 `feature_runs` 顯示為完整通過。後續若有「功能有 pass 就放行」的檢查(計劃寫「下一批」),這個守衛就被一步繞過。這個結果只在日後有人拿 `feature_runs` 當放行依據時才有影響,現在讀它的檢查還沒實作。
- file: `scripts/lumos:40927`(`_e2e_case_results`)
- 建議:`items` 為空時判 `unjudged`,或 `complete` 設為 False。

引句:「        rs = [r for _k, _n, r in items]」

## 已看的三類

**①提示注入:已看,無。**
- 情境名、功能名都用 `[A-Za-z0-9_-]+` 限定。
- 效能測試方法名在拼進 `sh -c` 前,用 `[A-Za-z0-9_.#]+` 做 `fullmatch`。沒有空白、引號、`$`、`;` 或換行,也不能以 `-` 開頭,所以沒有 shell 插值或選項注入。
- 這些自由文字沒有進到給 AI 的派工詞或 hook 附加段。

**②讀寫與執行越界:已看,無。**
- 記憶體情境名拼成 `sid=<run-id>.<情境>`,只含 `[A-Za-z0-9_-]` 和 `.`,產物路徑不會跳出 `.lumos/artifacts/android/`。情境名由設定檔的物件鍵校驗,`stability` 清單的項目必須在鍵裡。
- `features.paths` 拒絕絕對路徑和 `..`,而且只用來比對「改到的檔屬於哪個功能」,不讀不寫。
- `stability_scenarios.driver` 與既有的 `stability.driver`、`e2e.build`、`macrobench_cmd` 一樣,以 `sh -c` 執行設定檔裡的字串。這是既有信任面,沒有新增新的不可信來源。打開陌生專案時,這些指令本來就由使用者自己下指令觸發。
- 新增的 `history.jsonl` 用追加寫入,路徑固定。要借捷徑跳出去得先在 repo 內另外造一個捷徑,屬刻意的多步偽造,不報。
- 沒有新寫進程式、範本或文件的密鑰與信箱。

**③非刻意走過守衛:已看。** 除 S1、S2 外還查了這幾處:
- 環境變數 `LUMOS_STABILITY_SCENARIO` 殘留在 shell 時,整套跑的收集腳本會套用該情境的 driver 與 scenario。但判定端 `_macrobench_stab_skip_reason` 會因情境對不上而把門檻標成 `applies:False`,`_e2e_judge_stability` 則判成 `unjudged`,所以不會被誤記成過。這是安全失敗,不報。
- 沒帶 `--no-record` 卻讀到 `selection` 時會拒寫並回 2,按功能跑的結果不會混進整套紀錄。
- 殘留的 `PYTHONPATH` 仍由 `env -u` 與 `-P` 擋掉。

一句話總結:沒有可直接利用的洞,只有兩處按功能跑的結果可能被記成「已驗過」的縱深問題,即開跑時的髒樹狀態沒用來擋寫入,以及沒有任何檢查項目的情境會判通過。
