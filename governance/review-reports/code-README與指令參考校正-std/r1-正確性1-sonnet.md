severity: major

我只讀未改檔。實驗都在 `/tmp/lumos-seat-work/code-README與指令參考校正-std/正確性1-sonnet/repo`(`git clone --shared`,對應 HEAD 0221bd2e)。

## F1 spec-gate 寫成「不擋」,但低風險計劃與相依回歸紅燈都會擋(rc=1)
severity: major
blocking: 是

位置:`docs/command-reference.md` 與 `docs/指令參考.md` 新增的 `lumos spec-gate` 行。
引句:「runs the bound tests once and prints red/green (does not block)」

- 程式證據:
  - `scripts/lumos:7807-7810`:相依回歸有紅就 `return 1`。
  - `scripts/lumos:7809`:風險低(`door == "low"`)且 `_spec_gate_print_twoway` 回 False 就 `return 1`。
  - 只有風險高才是「紅綠只印不擋」(`scripts/lumos:7816`)。
- 我實際跑過:`python3.14 scripts/lumos spec-gate "Projects/探針判準對齊程式碼為主_計劃"`。
  - 5 條綁定測試都綠,輸出 `[spec-gate] 風險低: ✗ — 5 條沒過放行條件(沒標 keeps 的每一條各自紅…)`。
  - 結束碼 `rc=1`,沒有寫 PASS 留痕。
- 讀者照做會怎樣:
  - 低風險計劃的條款測試若已經是綠的、又沒標 `[keeps]`,spec-gate 不給過。這時不能直接實作、不派審。
  - 推送閘讀的是這份 PASS 留痕,所以也會卡在推送。
  - 文件卻說紅綠不擋,讀者會以為這步不會失敗。
- 建議改法:寫成「風險低的計劃,紅綠是放行條件,不符就擋;風險高只印不擋;相依功能的合約測試紅燈一律擋」。
- 附帶:`spec-gate --help` 本身也寫「(不擋)」,與程式不符;文件是照 help 抄的。

## F2 查詢考卷的通知門檻單位寫錯:是「候選筆記沒標答案」,不是「題目沒標答案」
severity: minor
blocking: 否

引句:「the exam alerts a person only when unlabelled questions reach one tenth or more, so someone can label them.」

- 中文版與 `generate.py` 的 desc 也有同樣問題(「沒標答案的題目達到一成以上」「only alerts when too many questions are unlabelled」)。
- 程式證據:
  - `governance/eval/refresh_labels.py:402-427`:`signal` 取 `unjudged_rate`,`>= 0.10` 才 `over=yes`。
  - `governance/eval/retrieval_eval.py:238-262`:`collect_unjudged` 的分母是「計分觸及集裡的 (題目, 候選筆記) 組數」,有 `labels` 的才算已標。
  - `governance/autonomous-loop.sh:331-348`:只在 `over=yes` 時才產 delta 表並通知。
- 具體情境:題庫每題都有標準答案,但檢索多撈出一批沒人批過的候選筆記,佔觸及集一成以上就會通知。讀者看「題目都標了」會以為不會通知。
- `docs/updates/2026-10-10-readme-audit.md` 的「另修的說法」同樣寫「未標題目達一成以上」。

## F3 專案開關表前言的例外名單漏了 `lint_new`,它也讀工作目錄那份
severity: minor
blocking: 否

引句:「most pre-push checks read the version in the commit being pushed」

- 前言接著只說 `stack_questions` 與 `note_lint` 讀工作目錄。
- 程式證據:新增告警閘判定入口 `scripts/lumos:28210` 的 `cfg = _lint_new_config(repo_root)`,走 `p.read_text` 讀工作目錄的 `.lumos/config.json`;`scripts/lumos:49331` 同樣。
- 具體情境:有人只在本機把 `lint_new.gate` 改成 warn、沒提交就推。本機照 warn,CI 讀被推的提交仍擋,文件沒警告這個落差。
- 同時,`note_lint` 是提交時的檢查,不是推送前檢查,措辭鬆了一點。

## F4 開關表自稱「沒寫就用下表預設」,卻漏了新「只列出」那段背後的 `note_shape.wording` 等四個開關
severity: minor
blocking: 否

引句:「Unset switches use the defaults below」

- README 寫「a few less common switches are listed in the command reference」。
- 程式證據:`scripts/lumos:31399`(`negation`)、`31446`(`tag_hints`)、`31542`(`close_summary`)、`31583`(`wording`),都是 warn/off 的提醒開關。
- 提交 d85c913e 的訊息寫明「共用 note_shape.wording 開關」。
- 具體情境:讀者想關掉文件新寫的「一行綁好幾支測試要拆開」「數量句要掛標記」這些提交時提醒,在表裡找不到對應開關。
- 修法:在表補列,或前言加「僅列主要開關」。

## F5 審查回放通知條件列得不完整
severity: minor
blocking: 否

引句:「A person is alerted when review replay finds a case whose verdict no longer matches or needs refreezing」

- 程式證據:`governance/autonomous_loop/replay_weekly.py:166-183` 的 `build_msg` 還會通知「舊帳無 spec_path 凍不了 N 個」(`unfreezable`)。
- 另一方面,括號寫的「回放執行出錯也會通知」只涵蓋逐包出錯(`errors`)。回放模組整支崩潰時,`governance/autonomous-loop.sh:430-433` 只記 log、不蓋章、不通知。
- 具體情境:有舊案凍不了,會收到通知,但文件沒列這一種。

## F6 派工鏡頭「算不出範圍會講一聲」寫得太廣
severity: minor
blocking: 否

引句:「if the impact range can't be computed, a line at the end of the dispatch text says so instead of silently attaching nothing」

- 這行說明是 Claude 側 hook 加的,不是 `lumos dispatch-lens` 指令本身印的。
  - 程式證據:`scripts/hooks/claude/dispatch-lens-hook.py:62` 的 `FAIL_NOTE`。
  - 只認 lumos 回報的固定原因碼,範圍格式寫錯就不講。
- 提交 5cfb4999 的訊息:「範圍格式寫錯、舊版 lumos 照舊放行」。該修正針對的是「會談開在 A 專案、審 B 專案分支」。
- 具體情境:用 `--range` 寫錯格式,派工詞尾端不會有那行。

## F7 圖產生器家筆記記「用 qlmanage 轉圖目視確認」,與同篇筆記自己的 PITFALL 矛盾
severity: minor
blocking: 否

引句:「用 qlmanage 轉圖目視確認字沒超出框」

- 同一篇 `Systems/README圖產生器.md` 的 PITFALL 寫 qlmanage 會截到動畫第一格並裁成正方形,目視要改用無頭 Chrome。
- 我用無頭 Chrome 重新渲染四張圖(`drift-guard-en/zh`、`evals-overview-en/zh`):新字都放得下,沒有擠出框。所以結論沒錯,只是紀錄寫的檢查方法不可靠。

## 核對過、屬實的句子

**關卡與開關**
1. 「改程式沒動筆記」一定擋、專案不能關:`scripts/hooks/pre-commit` 的 Gate 3(只有 `--no-verify` 或同批有筆記才過),沒有任何設定檔開關。
2. `--no-verify` 跳過後 post-commit 會記 `docs/.bypass-log.jsonl`:`scripts/hooks/post-commit` 檔頭與尾段。
3. 專案開關表的預設值與值域,逐列對過程式:
   - `drift_check.gate`:`scripts/lumos:39200`,預設 block。
   - `drift_check.old_sentence` 與 `drift_check.retire`:沒寫時照 gate,`39147` 與 `39181`。
   - `note_reread.gate`:`34746`,預設 block。
   - `note_shape.gate`:`30428`,預設 block。
   - `note_shape.test_refs`:`32520`,預設 warn。
   - `note_shape.slots`:`32015`,預設 block,且受 gate 管;須掛鉤帶 `--slots` 才跑(`31881`)。
   - `node_home.gate`:`28960`,on/warn/off,預設 on。
   - `lint_new.gate`:`27662`,預設 block。
   - `stack_questions.gate`:`26867`,all/high-only/off,預設 all。
   - `note_audit.gate`:`33363`,預設 block;本專案的 `scripts/hooks/pre-push` 與 `.github/workflows/ci.yml` 確實都沒呼叫 `note-audit check`。
   - `note_lint.gate`:`6807`,預設 warn。壞值改用 on 屬實,其餘壞值退回各自預設也屬實。
4. 沒有開關的清單:
   - 連結斷掉靠 `doctor --ci`(`pre-push` 約 316-330 行)。
   - 高風險沒審查紀錄靠 code-loop check(約 456 行)。
   - 測試/掛鉤檔被改靠 `anchor verify`(約 263 行)。
   - 全套測試只在 Lumos 自己的 repo 跑(約 625 行)。
   - 找不到 Python 3.14 就擋(約 105 行)。
5. 回頭重讀(reread):
   - 只有推送前掛鉤帶 `--gate`,CI 與手動只提醒(`pre-push` 約 526-543 行,`ci.yml` 約 247-264 行,`--help`)。
   - `lumos drift ack --kind reread` 存在(`drift ack --help`)。
   - 單次略過 `LUMOS_SKIP_REREAD_CHECK=1`(`scripts/lumos:35272`)。
6. 結 Issue:
   - `drift fix --kind c2 --close` 在寫入前擋待定決策與未處理回頭條件(`scripts/lumos:38596`)。
   - `lumos set` 結案只列出、不擋(`36299`、`36323`)。
7. 3 輪上限:`_TIER_PARAMS` 的 standard 與 high 都是 cap 3,light 是 2(`scripts/lumos:12128`);`cap-decision` 只收非 light 且有輪次的多席迴圈(`9204-9215`)。

**評測**
8. 情境探針:
   - 每場從批次基線重新複製(`scripts/scenario_probe.py:1250-1262`)。
   - 全域 skills 連結被動到或清理失敗會整批停下(`1366-1440`)。
   - 截斷與用量上限不算分,有效場次不到一半不下結論(`1078-1105`)。
   - 用量帳預設不開(`--max-per-window` 預設 0,`1168`)。
   - 週跑沒有帶該參數(`governance/autonomous-loop.sh:383-386`)。
   - 探針有題沒過才通知(`391-399`)。
9. 查詢考卷分數退步只記錄不通知(`autonomous-loop.sh:308-360`);也會順帶考 `$HOME/backend/LandmarkMember`(`466`)。推播漏網週跑不發通知(`449-463`)。

**指令、數字與連結**
10. 指令旗標逐一對過 `--help`:`loop fix-check/cap-decision/retro/escape`、`lint-waive`、`note-audit reread-prepare/record/check`、`test-quality scan/capture/check/capabilities`、`summary-line`、`updated-sync`、`events`、`drift scan/fix/ack`。
11. 頂層指令數 85,「八十多個」屬實。
12. 更新清點:
    - 170 個提交、分類(chore 54、docs 38、feat 10、fix 37、merge 21、test 10)與 `git log` 吻合。
    - 表中 170 列的短碼、完整碼、標題、台北時間,我用腳本逐列比對,零差異。
    - release 指向 4a42dede 用 `git ls-remote` 核對屬實。
    - 代表提交編號都對得上描述。
    - `20f41c8e` 確實是發布 10/7 清點的提交。
13. 連結錨點:
    - `docs/command-reference.md#project-switches` 與 `docs/指令參考.md#專案開關` 都有對應標題。
    - `test-quality-standard.md`、`03-寫回圖譜.md#實作測試品質`、`#事後掃描與執行收證已安裝-cli`、`07-安裝維運.md`、`docs/updates/2026-10-10-readme-audit.md` 都存在。

**圖產生器**
14. `python3 assets/readme-diagrams/generate.py --check` 為綠。重產後 `git status` 零差異,證明 SVG 是產生器產出、沒有手改。
15. `generate.py` 的差異只有 7 處字串,沒有邏輯變動。新字經無頭 Chrome 轉圖,在框內放得下。中英的圖內文字、`<desc>` 與 README alt 說法互相不衝突。

**其他**
16. 英文版「測試品質」一節與中文版逐段對應,連結一致。兩版 README 與兩版指令參考的新增段落事實對應一致(F2 的錯在兩版同樣出現)。
17. 圖產生器家筆記沒有登記任何合約(`lumos contracts` 回「沒有登記」)。這次 diff 沒破壞它宣稱的流程(不手改 SVG、跑 `--check`、轉圖目視),只有 F7 的紀錄問題。`lumos lint` 該筆記 0 問題。

**角色鏡頭**
- 後端卡 be-api-compat、be-authz:這份 diff 是文件與圖字串,沒有端點或對外欄位,只算「文件列出的指令旗標」是否相容,全部屬實。這兩題不適用,沒有對應發現。

## 沒核對的範圍
- 沒有真的送出 LINE 通知,只讀了觸發條件;沒有 token 時其實是靜默不發。
- `ONBOARDING.md`、`SDD-vs-Lumos*.md` 及其他未改的文件。
- 完整測試。我只跑了 `--suite docs`:733 過、0 紅、1 跳過。跳過的是 `t_codex_s1_r1_fixes`,判紅訊息是環境預期跳過數超標,與這份 diff 無關。
- 提交時提醒類(一行綁多測試、數量句、更正括號)的實際觸發細節,只對過提交訊息與開關名,沒逐一實測。

最高等級:major
