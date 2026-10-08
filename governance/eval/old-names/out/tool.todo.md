# tool 存量舊名清單(量測點 70d0843d)

每筆 = 筆記裡還在講、但程式裡已經刪掉的名稱。判準:讀的人照這句去找會找不到東西或做錯事 = 該改;句子本身在講歷史 = 不用改(或補歷史字眼)。

## 第 1 層:已逐筆判過:真或灰(先修這層)(2 筆)

- `Issues/2026-08-03_剝除與邊界解析的既有缺陷群.md:17` 名稱 `FENCE_RE`(消失於 4d33ec3b,原在 scripts/lumos) — 判真:Issue(status doing)摘要寫 FENCE_RE「還活著三處」,4d33ec3 當天就刪了,摘要沒改
  > KEY:★共同根因=同一件事有多份實作、且正則假設輸入格式良好★。r2 已收編兩處(load_vault/guard trace),但 `FENCE_RE` ★還活著三處★,而活下來的比已修的嚴重——餵的是 impact hook 與 design-loop 的 G1 硬閘
- `Systems/lumos-cli-read.md:36` 名稱 `FENCE_RE`(消失於 4d33ec3b,原在 scripts/lumos) — 判真:完成狀態的 Systems 摘要寫「FENCE_RE 仍活在 refcheck 家族三處未收編」,已刪
  > KEY:★預檢迴圈與主迴圈共用 `_search_visible_lines` 單一實作★(2026-08-03 code-loop r2)——原本預檢自己一份「整段 regex 剝 fence」,遇未閉合圍欄與主迴圈分岔,導致逐詞覆蓋虛報非零;同源修法也收編了 `load_vault`／`cmd_guard_trace`(見 [[Issues/2026-08-03_剝除與邊界解析的既有缺陷群]],★`FENCE_RE` 仍活在 refcheck 家族三處未收編★)

## 第 2 層:過濾最嚴那版列出、還沒判過(照同一標準自己判)(8 筆)

- `Issues/code-loop-pass自失效追尾.md:54` 名稱 `_BOOKKEEPING_DIR`(消失於 b4060e37,原在 scripts/lumos)
  > 判準是 `f in _BOOKKEEPING_FILES or f.startswith(_BOOKKEEPING_DIR)`,
- `Projects/Codex行為精修_計劃.md:111` 名稱 `codex_stop_decision`(消失於 72b38157,原在 scripts/hooks/claude/check-graph-sync.py)
  > - **改動 (A) 落在 `scripts/hooks/claude/check-graph-sync.py`**:新增 `STOP_BLOCK_HEAD`(固定首行)、`codex_stop_decision`(四道不擋條件:非 codex / `LUMOS_STOP_BLOCK_OFF=1` / `stop_hook_active` / 本 session 已擋過)、`_stop_block_dir`(0700,每次進到寫標記路徑順手清 7 天前)、`_stop_mar
- `Projects/公開精簡版_計劃.md:148` 名稱 `verification-rot-check.py`(消失於 38b11292,原在 scripts/hooks/claude/verification-rot-check.py)
  > | `install.sh` | 碰專案層 | ❌ **錯誤**——它只有一行 `exec ... lumos install --force`，`cmd_install` 全部動作都在 `$HOME`，**不碰專案任何檔案**。<br>★真正的地雷是別的★：它尾端呼叫 `_sync_global_claude`（`scripts/lumos:6620-6623`），會把 `check-graph-sync.py`／`verification-rot-check.py`／`i
- `Projects/公開精簡版_計劃.md:222` 名稱 `verification-rot-check.py`(消失於 38b11292,原在 scripts/hooks/claude/verification-rot-check.py)
  > 原稿寫「`check-graph-sync.py` 的作用正是催人維護＝**強制**維護，與『不設強制』的裁定衝突」。**這個理由現在站不住**：使用者裁定①已把「強制」收窄為**機械強制＝擋人的閘**，而四支 hook 逐一讀 docstring **全部是非阻斷的**——`check-graph-sync.py`「軟提醒，不 block turn 結束」／`verification-rot-check.py`「Never blocks commit (exit 0 alw
- `Projects/公開精簡版_計劃.md:231` 名稱 `verification-rot-check.py`(消失於 38b11292,原在 scripts/hooks/claude/verification-rot-check.py)
  > | `verification-rot-check.py` | ★範圍裁定★ 同上 |
- `Projects/工具鏈全環節體檢_調研.md:38` 名稱 `verification-rot-check.py`(消失於 38b11292,原在 scripts/hooks/claude/verification-rot-check.py)
  > 1. **Claude hooks 雙重註冊**:`~/.claude/settings.json` 裡 `verification-rot-check.py`(每次 Bash)與 `check-graph-sync.py`(每次 Stop)各註冊兩次——每次都跑兩遍,純燒錢。★已實查★。
- `Projects/檢索多詞回退_計劃.md:135` 名稱 `t_search_multiword_fallback_is_opt_in_and_only_on_zero`(消失於 fc509b8a,原在 scripts/test_lumos.py)
  > `t_search_multiword_fallback_is_opt_in_and_only_on_zero` 的第三條斷言
- `Systems/native-windows-support.md:62` 名稱 `verification-rot-check.py`(消失於 38b11292,原在 scripts/hooks/claude/verification-rot-check.py)
  > - `_install_hooks_py(root)`(取代 `install-hooks.sh` 4 件事):① `git config core.hooksPath scripts/hooks` ② **複製 Claude hooks(`check-graph-sync.py`/`verification-rot-check.py`)到 `~/.claude/hooks/`**(r1-F2:漏此步 L1/L3 不啟用)③ `merge-claude-settings.py

## 第 3 層:其餘(誤報多,有空再看)(14 筆)

- `Projects/code側刪除傳播守衛_實作計畫.md:550` 名稱 `_git_root`(消失於 a3995ebf,原在 scripts/lumos)
  > - Placeholder 掃：無 TBD/「適當處理」;唯二留白＝`_git_root`/`_find_graph_root` 指示「先找既有 helper 不新造」，屬指令非佔位 ✓
- `Projects/design-loop折入守衛_計劃.md:68` 名稱 `FENCE_RE`(消失於 4d33ec3b,原在 scripts/lumos)
  > 3. **reverse-omission flag**(全文域):抽全文**高訊號 token 三類**(實作 T5 降噪:原含 backtick-code/CamelCase 對長技術 spec 爆量假陽 237 條→收窄後 24 條全真):① `--flag`(`--\w[\w-]*`)② `★MARKER★`(★…★)③ **帶已知副檔名的檔名**(`\w[\w./-]*\.(json|py|md|sh|txt|kt|cs|vue|js|ts|yml|yaml)`,避
- `Projects/design-loop重設計_實作計畫.md:110` 名稱 `t_calibration_smoke`(消失於 7e25876a,原在 scripts/test_lumos.py)
  > **Create**: governance/eval/canary_calibration.py(2026-08-26 已退場,詳建了沒人跑批次裁定)（stdlib）；**Test**: 冒煙進 test_lumos（`t_calibration_smoke`，`_need_src` 守門）
- `Projects/主動影響幅度偵測_計劃.md:185` 名稱 `verification-rot-check.py`(消失於 38b11292,原在 scripts/hooks/claude/verification-rot-check.py)
  > - **過濾**:讀 hook payload 的 **`tool_input.file_path`**(r8-F9:`file_path` 在 `tool_input` 巢狀 dict 內、非頂層——`payload["tool_input"]["file_path"]`,MultiEdit 亦同;巢狀結構參 `verification-rot-check.py:270-273`,r9-F8 註:該處讀的是 `tool_input.command`,僅示範「tool_inp
- `Projects/檢核收緊五件_計劃.md:152` 名稱 `FENCE_RE`(消失於 4d33ec3b,原在 scripts/lumos)
  > - **r2 panel(2026-08-21,五席同門+外家 gemini-3-flash)**:blocker 9 / major 15 / minor 4(外家 6 條中 2 條引句含省略號不採信;其 #1「loop id 可重用」論點編排者自核成立,以自查名義折入)。★裁定=v3 重寫★:S3 閘從 pass 移到 push 檢查點 `code-loop check`(留痕綁 range+HEAD,不同源即擋)、skip 在 high 改破窗制、撤 `--no-loo
- `Projects/檢索優化_計劃.md:340` 名稱 `t_search_ranked`(消失於 5ea0aa83,原在 scripts/test_lumos.py)
  > - **階段一（2026-07-10）✅**：`_rank_tokenize`（CJK bigram+ASCII 拆分）/`_rank_idf`（平滑）/`_rank_bm25`/`_rank_score_candidates`（BM25F 欄位 tf 加權於飽和前）+ `search --ranked --top --json`（dormant，legacy 不動）。t_tokenizer_unit 7 斷言+t_search_ranked 10 斷言；全套 960 綠。真
- `Projects/派工鏡頭注入_計劃.md:181` 名稱 `INNER_TIMEOUT`(消失於 d89cfda2,原在 scripts/hooks/claude/dispatch-lens-hook.py)
  > - **hook 端**:`scripts/hooks/claude/dispatch-lens-hook.py` 薄殼(正規式→subprocess→updatedInput;INNER_TIMEOUT 45<外層 60)。
- `Projects/舊句檢查_計劃.md:25` 名稱 `--restore`(消失於 828a68be,原在 scripts/hooks/claude/memory-sweep.py)
  > - 撤除節②收窄(引用區塊行要同時含撤除字樣與範圍宣告字):現在的工具鏈圖譜「只因②才不看」的非空行 603 行/10 篇 → 163 行/2 篇;rtb 圖譜 0 → 0。剩下兩篇:`Systems/記憶過期清掃` 107 行(真宣告)、`Projects/主session鏡頭利用率_計劃` 56 行(「…撤掉兩次…本節以下是重寫版」,仍是誤觸發)。對照組誤報第 4 筆(`Systems/記憶過期清掃:171` 的 `--restore`,828a68be 那版第 30 行
- `Projects/舊句檢查_計劃.md:89` 名稱 `--restore`(消失於 828a68be,原在 scripts/hooks/claude/memory-sweep.py)
  > - **名稱先篩**(規則跟下面的「整字」同一個定義,只是先把一定不會命中的名稱拿掉,不改任何結果):把整份圖譜全文切成 ASCII 詞 `[A-Za-z0-9_]+` 的集合;一個候選名稱裡的每一段 ASCII 詞都在集合裡才留下,名稱裡沒有任何 ASCII 詞(純中文的函式名)一律留下;留下的一律交給下面的整字正則判,不再用 `\w` 邊界對全文跑第二次(既有 `_DriftNames` 就是那樣做、`\w` 含中文字,所以不能直接拿它來用)。為什麼不會篩掉該列的:整字正
- `Projects/舊句檢查_計劃.md:95` 名稱 `--restore`(消失於 828a68be,原在 scripts/hooks/claude/memory-sweep.py)
  > - ②節內宣告(r1 收窄):節內任何一行以 `>` 開頭的撤除行,**同一行還含範圍宣告字(下面、以下、本節、這一節、整篇、之後)**,才從那一行到節尾(下一個同層或更高層標題之前,含子節)不看;在一級標題底下就是到整篇尾。例:`> 下面凡是講 --restore 的段落都是寫檔版的歷史紀錄` → 從這行起不看;`> golden 已凍結,…`(沒有範圍宣告字)→ 不觸發,後面照掃;`> 撤除 hook 一刀刪炸掉…` → 不觸發。
- `Projects/舊句檢查_計劃.md:129` 名稱 `--restore`(消失於 828a68be,原在 scripts/hooks/claude/memory-sweep.py)
  > - 發現分兩段印:先要處理、再只列出,每筆用 `_drift_print_findings`:`[m1 程式改了、筆記還在講舊東西] 路徑:行  原文`,下一行 why =「消失的名稱:`foo_bar`(原本在 a.py)、`--restore`(原本在 scripts/x.py)」(why 照既有 `_drift_print_findings` 截在 1000 字,名稱很多時尾巴會截掉;完整名單在改法那行,上限 4000 字);`m1` 的發現不帶 prev_ack、不借
- `Projects/舊句檢查_計劃.md:133` 名稱 `--restore`(消失於 828a68be,原在 scripts/hooks/claude/memory-sweep.py)
  > - **提示**:`_drift_fix_hint(kind, path, line, names=None)`,`m1` 回「改成歷史說法(例:「原本叫 <名稱>,已移除」)或刪掉這句;確定照留就 `lumos drift ack <節點> <行號> --kind m1 --name=<名稱1> --name=<名稱2> --reason "<為什麼照留>"`」。`<為什麼照留>` 是刻意的佔位字:照貼前要換成真理由,原樣照貼會被既有的佔位字檢查(`_drift_place
- `Projects/舊句檢查_計劃.md:189` 名稱 `--restore`(消失於 828a68be,原在 scripts/hooks/claude/memory-sweep.py)
  > - [S10] 當筆記的一行提到候選名稱,工具應照參考實作 `_mk_rx` 以 ASCII 識別字邊界判整字(一次推送一條正則),中文緊貼算提到;候選名稱超過 `_DRIFT_M1_PREFILTER_MIN` 個時名稱先篩只拿掉「有某一段 ASCII 詞不在全文 ASCII 詞集合裡」的名稱,不改任何結果(同一批輸入把 `_DRIFT_M1_PREFILTER_MIN` 設成 0 與設成極大各跑一次,輸出逐字相同);例:「改了foo_bar函式」→ 列;「加了--rest
- `Projects/驗證層去模型化_計劃.md:104` 名稱 `t_mutate_diff`(消失於 7e25876a,原在 scripts/test_lumos.py)
  > - S4:`t_mutate_diff`(三算子生成/worktree 隔離/testmap 選測/殺與活判定/cap 抽樣/無測試檔如實列/rc 合約);對本週真實 diff(hook必看召回修復那批)實跑一輪,活口清單如實入 Verification——**不設「殺率須達 X」門檻**(觀測層,防預期寫成驗收)。
