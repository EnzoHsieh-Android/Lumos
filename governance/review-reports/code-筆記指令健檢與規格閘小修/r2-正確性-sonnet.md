severity: major

範圍:只讀了 `r2-repair-lumos.patch` 的 807 行,整份改動只當上下文查。修前版本是 `55da596f`,修後是 `b76b570e`,兩版 `scripts/lumos` 都存在 `/tmp/lumos-seat-work/code-筆記指令健檢與規格閘小修/正確性-sonnet/`(`lumos_before`、`lumos_after`)。我沒有跑全套測試,也沒有實際跑 `_spec_gate_status_at` 的推送端對端。

## Findings

1. **`_ref_cmdline_token` 收窄成「要有 `-` 旗標才截」,沒旗標的子命令指令現在被報成路徑不存在(refcheck 與 doctor P 段共用同一支)**
severity: major
   blocking: 是
   歸因:有證據的修復回歸
   - **輸入**:筆記反引號裡寫 `scripts/lumos doctor`、`scripts/lumos search 詞`、`src/a.py 的某函式` 這類第一個詞是真檔、後面沒有 `-` 開頭詞的寫法。
   - **執行路徑**:`words[1:]` 沒有 `-` 開頭的詞,條件不成立,回傳整串原文。接著 `"/" in token` 成立,`scripts` 在 top_dirs,整串 `exists()` 為假,於是報 missing。
   - **修前**:只要有空白就截成第一個詞,第一個詞存在就是 ok。
   - **證據一(臨時 repo,`scripts/lumos` 與 `src/a.py` 存在)**:
     - `lumos_before refcheck plan.md --json`:claims 只有 `scripts/lumos` 與 `src/a.py`,`missing 0`。
     - `lumos_after`:`scripts/lumos doctor`、`scripts/lumos search 詞`、`src/a.py 的某函式` 三筆 missing,`missing 3`。
   - **證據二(本 repo 真實筆記,對 `docs/lumos-toolchain-knowledge/**/*.md` 每篇逐一比對修前修後的 missing 集合)**:新增的 missing 只有兩篇。
     - `Projects/最低Python版本改3.14_計劃.md`:新增 `scripts/lumos python-path`、`scripts/lumos …`
     - `Projects/派工鏡頭可指定目標repo_計劃.md`:新增 `scripts/lumos dispatch-lens`,該篇的 missing 從 7 變 8。
   - **測試抓不到**:`t_ref_path_spaced_dir_not_cut` 只測 `scripts/e2e.sh --cleanup`(帶旗標),沒有一條「路徑加子命令、無旗標」的案例。把規則改回「有空白就截」,第 ①②④⑤ 會翻紅(帶空白缺檔不再報 missing),第 ③ 仍綠,所以改壞方向的守衛是有的;但這次的回歸沒有任何一條測試擋。
   - **⚠ 交編排者**:計劃〈做法〉8 第 160 行白紙黑字寫「第一個詞之後有 `-` 開頭的旗標」才當指令,所以這是設計取捨,不是寫歪。只是它放棄的是更常見的 `scripts/lumos <子命令>` 寫法。我不替你裁要不要收回。
   - 引句:「if len(words) > 1 and any(w.startswith("-") for w in words[1:]) and not exists(s):」

2. **`_spec_gate_pick` 改成「同時間取後列的」,本機帳的最新一筆會輸給治理帳裡同一秒的較舊一筆**
severity: minor
   blocking: 否
   歸因:有證據的修復回歸
   - **輸入**:同一計劃的規格閘在同一秒內跑兩次(留痕 `ts` 只到秒)。本機帳只留最新的 B;治理帳有 [A, B]。`_spec_gate_latest_merged` 呼叫 `_spec_gate_pick(can[lp], *gov_rows)`,實際傳入 (B, A, B)。
   - **執行路徑**:B 先進;輪到 A 時 `k >= bk` 成立(同秒),best 變成較舊的 A;最後一個 B 因 token 已見過被略過。
   - **證據**:`lumos_before._spec_gate_pick(B,A,B)` 回新的 B;`lumos_after` 回舊的 A。
   - **影響**:留痕指紋對不上,可能多擋一次,或讓舊 `tests` 清單被拿去跑。要同一秒內跑兩次規格閘才會發生,實務上少見,所以只給 minor。
   - **測試抓不到**:`t_spec_gate_pick_bad_ts` 只涵蓋壞 `ts`,沒有同秒重跑案例。
   - 引句:「if best is None or k >= bk:      # 同時間(秒級 ts 常撞)取後列的」

3. **補跑紅前的「有未提交改動」警告會被治理帳這類每次都有的改動觸發**
severity: minor
   blocking: 否
   歸因:未判定,沒跑兩版對照。
   - `git status --porcelain --untracked-files=no` 只要有任何已追蹤檔被改就印 ⚠,不看是不是實作檔。
   - 本 session 開頭的 git status 就是 `M docs/.governance-log.jsonl`;規格閘自己寫留痕進治理帳,重跑時會自己觸發這句,是雜訊。
   - 引句:「if st is not None and st.returncode == 0 and st.stdout.strip():   # 前置條件:沒提交就換」

## 已驗主張(行為證據)

- **`_spec_gate_pick` 的壞 `ts`**:修前 `_spec_gate_pick({"ts":"garbage"}, 好的)` 拋 `TypeError: '>' not supported between instances of 'float' and 'tuple'`。修後回讀得懂的那筆;兩筆都壞時取後列的,不崩。修復成立。
- **`_lint_excluded_lines` 先數冒號**:`_EXCLUDED_RE` 要求「已排除」後有兩個冒號才可能匹配,而 lint 這段 `s` 與 `_excluded_line` 內部是同一個字串(只多一個 `lstrip("*_ ")`)。冒號少於 2 個時,先判 None 與原本結果等價,沒有誤放。
- **`_fm_touch_updated`**:與修前行內迴圈逐行等價,summary-line 刪行時的 `e-1` 邊界在範圍內。
- **`_probe_cond_keys`**:`extract=None` 時走 `_probe_lines`,與原寫法等價;lint 端等同原本「probe 加 retire」的聯集。
- **doctor S14**:`_spec_gate_latest_merged(env) or _spec_gate_latest_records(env)`。治理帳壞時 merged 回 None,治理帳空時 merged 回 `{}`,兩種都會退到只看本機帳,沒有 None 解參考。
- **改名 `_doctor_s14_plan_status`**:全 repo 沒有舊名殘留引用。

## 未驗範圍

- `_spec_gate_status_at` 的四種情境(起點是 doing 這次改 done、起點是 done 這次改回 doing、計劃改名、起點不存在),我只讀碼推演,沒實際跑。
  - 範圍字串沒有 `..` 或起點拿不到那一版,一律回 None 並當成不是 done,偏嚴;這個方向不會放行該擋的推送。
  - 單一 rev 或空樹起點(新分支兜底)會讓原本寬待的已完成計劃變嚴,屬保守方向,沒回歸成放行。
- `_summary_write_shape_check` 的 gate off/warn/block 與非 git 分支只讀碼。每次寫入多一次 `_nodehome_list(root, "index")` 全 repo `ls-files`,沒量效能。
- 否定句 `_NS_NEG_CLAUSE_PUNCT` 沒收 ASCII 的 `.`,「…尚未實作時.」不會被當子句記號。這是中文筆記的少見寫法,沒有可重現的失敗案例,不列 finding。
- 圖譜固定席:
  - `lumos-cli-read` 的 search 排除 superseded 合約不受影響,diff 沒碰 search。
  - `guard-kill` 的 rc 優先序與 JSON 純度合約不受影響,沒碰 `guard kill`。
  - `design-loop` 的處置閘第五步不受影響。
  - `測試假綠形態` 的還原翻紅釘:本輪新增測試多半有前置斷言(例如 `t_ref_path_ignored_dir_trailing_slash`),我沒逐條驗證。

## 三問的答案

1. **原問題的修復效果**:壞 `ts` 崩潰、已排除行回溯、冒號先數、`check-ignore` 結尾斜線、`--nth` 要配 `--after`,這幾項的程式路徑看起來成立。帶空白路徑的修復部分成立:`src/app v2/x.py` 這種缺檔不再被截成存在的前綴,但代價是 finding 1。
2. **修補處的正常、錯誤與相鄰呼叫路徑**:相鄰路徑出了兩個新洞,見 finding 1(`scripts/lumos <子命令>` 變 missing)和 finding 2(同秒取到舊留痕)。
3. **同一案例修前、修後**:
   - finding 1:`scripts/lumos doctor`,修前 ok,修後 missing。
   - finding 2:(本機 B,治理帳 [A,B]),修前取 B,修後取 A。
   - finding 3:沒有兩版對照,未判定。

最嚴重 severity:major;blocking 共 1 條。
