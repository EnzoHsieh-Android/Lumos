---
type: project
status: doing
created: 2026-08-17
updated: 2026-08-17
tags:
  - type/project
  - status/doing
summary: |-
  KEY:立案動機(2026-08-17)——治全系統唯一紅燈的實證阻塞:2026-08-08 補鏈後依協定重釘快照 ab910519,P@8 0.713→0.447/固定席噪音 77,量到的是「labels 凍結於 7/20 語料」的過期而非檢索品質,回退 285d429 並留言「語料前進須配套標註刷新(另立 labeling 計劃)」——本案即該計劃。核心問題:題庫標註是凍結金標,語料前進時新候選未標=噪音,語料被鎖死不能前進
  KEY:PRIOR-ART: borrow-design——IR 評測經典解 TREC pooling/incremental qrels:新系統/新語料浮出未判文件→只補判那批(delta),不推倒重來;「未判=不相關」是文獻已知偏差(bpref/condensed-list 即為此發明,但改指標語意=既有門檻數字全失效,拒)。自家姿勢 borrow:雙評審+仲裁+人放行協定原樣沿用(raters/rater-instructions.md 已存在),lint-watch「機器備好、人點頭」流水線形狀
  KEY:四件套——S1 delta 出卷(目標語料重算候選池,diff labels 吐未標清單,沿現有 sheet 格式)/S2 補標(A席=乾淨 Claude、B席=Gemini Flash CLI headless 同指示檔;一致=建議 final 免逐筆裁,不一致=人裁 deep-read;整批 merge 必經人放行=批次級人閘)/S3 重釘機械閘(unjudged=0 才准寫 snapshot_commit,否則 rc1 吐 delta 清單;過渡週新舊快照雙跑留重疊點)/S4 未標率常設訊號(每輪考卷印 top-K 未標佔比進 history,週閘超門檻自動產 delta 表+通知等人放行)
  KEY:第二席環境實測(2026-08-17)——Codex 到期;Gemini CLI v0.55.1+API key(~/.gemini/.env,GEMINI_CLI_TRUST_WORKSPACE=true)headless 通,Flash 級免費(日 250 req);★Pro 級 RESOURCE_EXHAUSTED=免費 key 零配額,訂閱不涵蓋(實測),要用須 AI Studio 開 billing★;仲裁席=人(delta 量小,獨立性最強),量大再議 Pro 付費
  KEY:刻意不做——指標語意不改(未標仍=噪音,靠 delta 補標消滅而非改尺)/變更節點重標(僅列 mtime>標註日清單提醒,不阻塞)/評審自動 final(人閘不可拆)/LLM 在計分迴圈(評審只產標註,計分恆決定論可重算)
  TEST:驗收=重放 ab910519 重釘:S1 應吐出當時 77 噪音中的未標集、S3 未補標前 rc1 擋、補標後綠、雙跑分數量到品質而非過期;S4 在該快照未標率應超門檻亮燈
related:
  - "[[Projects/連結缺失補全_計劃]]"
  - "[[Projects/hook必看召回修復_計劃]]"
  - "[[Systems/retrieval-ranking]]"
---
# 標註刷新_計劃

> 白話:我們有一份考自己搜尋功能的考卷,答案是人批過的金標。但筆記庫一直長大,新筆記沒批過答案,照「沒批=算錯」的規則,筆記庫一更新分數就崩——上次崩過一次只好把考卷凍在舊庫上。本案的解法:庫更新時**只補批新出現的題**(不整本重批)、補批走現成的雙評審流程(Claude+Gemini,吵架人裁)、沒補完機器擋住不准換庫、再加一顆「該補批了」的警示燈。

## 緣起(事故帳)

2026-08-08 補鏈四筆後依 r1 協定重釘快照至 ab910519:P@8 0.713→0.447、hook 固定席噪音 77 條——新快照拉進 7/20 後全部未標節點,依「未標=噪音」規則淹沒指標。裁定回退 285d429,corpus_revision_note 明言「語料前進須配套標註刷新(另立 labeling 計劃)」。本案補此前置;紅燈(hook P@8 0.6944 差 0.0056)的後續改善全被此鎖死。

## PRIOR-ART

`PRIOR-ART: borrow-design(TREC pooling/incremental qrels + 自家 rater 協定)`——檢索評測界標準解:語料/系統前進浮出未判文件→delta 補判;「未判=不相關」為已知偏差,bpref/condensed-list 等改尺方案因會使既有門檻數字全失效而拒。補標協定原樣沿用 `governance/eval/raters/rater-instructions.md`(0/1/2 判準+純 JSON 輸出+仲裁 by/why),僅換 B 席執行器。

## 規格

### S1 delta 出卷
- `build_goldset.py` 加 delta 模式:對「目標語料」(當前工作樹)重算每題候選池(`search_pool`/`edit_pool` 現成),與 `labels` diff → 未標候選清單 → 產 delta 標註表(沿 `retrieval-labeling-sheet.md` 格式,僅未標列)+ 機器可讀 JSON。
- 已標候選不重出(金標不重批);題目(queries)恆不變,動的只有語料側候選。

### S2 補標(雙評審+人閘)
- A 席=乾淨 Claude agent、B 席=Gemini(`gemini -m <flash 現行版> -p`,headless,同一份 rater-instructions);各產 `rater-{claude,gemini}-delta.json`。
- 兩席一致 → 列入「建議 final」(免逐筆人裁);不一致 → 逐筆人裁(deep-read,沿用 `by`/`why` 欄位)。★整批 merge 進 goldset `labels` 前必經人放行(批次級人閘)——一致案免的是逐筆裁決,不免整批放行★。
- 免費額度界線:Flash 日 250 req;單輪 delta(~80 筆)一天內完成。

### S3 重釘機械閘
- 重釘模式斷言:目標語料全題候選池 `unjudged == 0` 才寫入 `snapshot_commit`;否則 rc1 並吐 delta 清單(=「先跑 S1/S2」的機械提示)。
- 過渡:重釘當週新舊快照各跑一輪考卷,兩筆都進 history(重疊點,分數線可比);`corpus_revision_note` 記轉場與語料差異一句話。

### S4 未標率常設訊號
- `retrieval_eval.py` 每輪加印 unjudged rate(全題 top-K 候選中無標註佔比)並寫入 history jsonl 欄位。
- 週閘 wrapper=`governance/autonomous-loop.sh` 週期考卷段(現呼叫 `retrieval_eval.py --goldset … --split held` 處):unjudged rate 超門檻(暫定 10%,實跑校準)→ 自動產 delta 表 + 通知(LINE,同 lint-watch 慣例)→ 等人放行補標。崩分從「事後發現」變「事前亮燈」。

## 刻意不做(記帳防回鍋)
- 改指標語意(bpref/只算已判):既有門檻與歷史分數全失效,拒;未標靠 delta 補標消滅,不靠改尺。
- 變更節點重標:節點內容改動後舊標註可能過期——v1 僅列「mtime > 標註日」清單軟提醒,不阻塞重釘。
- 無人放行即入金標:人閘不可拆——兩席一致只買「免逐筆裁決」,整批 merge 仍必經人放行(pbt-oracle 教訓:自動生成+自動採納=maker bias 閉環)。
- Pro 付費仲裁:量小人裁更獨立;量大再開 billing($2/$12,一輪數元台幣)。

## 實務隱患
- **B 席可用性**:Gemini 免費層規則今年已變兩次;B 席斷供時退化為「A 席+人全批」(協定不變,量小可承受),不阻塞。
- **評審漂移**:rater 模型版本換代→標註口味漂——delta 只批新題、舊金標不動,漂移影響侷限於增量;仲裁人裁兜底。
- **[self-governance]**:S3 是擋人閘(rc1)——假紅風險=delta 清單誤報;斷言邏輯與 S1 同源(同一份 pool 計算),不另寫一套。
- **[prod-irreversible]**:不適用(goldset 是 repo 檔案,git 可回退)。

## 驗收線
- 重放 ab910519:S1 吐出當時 77 噪音中的未標集;S3 未補標前 rc1、補標後綠;雙跑留重疊點;S4 未標率在該快照超門檻。
- 回歸測試:delta diff 正確性(已標不重出/新候選全出)、S2 路由與併入(兩席一致→建議 final/不一致→標人裁;merge 正確性;仲裁 `by`/`why` 欄位寫入)、S3 閘 rc 合約、S4 欄位寫入。
- S2 流程驗收:一輪真 delta 走完雙評審→人放行→merge,goldset 解析無損(json 合法+既有標註零變動)。

## 審計修正紀錄

- **pre-flight(2026-08-17,機械排乾,不算 loop findings)**:①S2「兩席一致直接併 final」與刻意不做「人閘不可拆」自違→消歧為批次級人閘(一致免逐筆裁,整批 merge 必人放行)②S4 週閘 wrapper 未指名→指名 `governance/autonomous-loop.sh` 週期考卷段 ③S2 無驗收著落→回歸測試補路由/併入/仲裁欄位,驗收線補一輪真 delta 全流程。其餘六類檢查(檔名函式存在性/交叉引用/CLI touchpoint 現況/數字留痕比對)全過。
