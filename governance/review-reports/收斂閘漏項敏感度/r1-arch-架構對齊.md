# r1 席報告:架構對齊(sonnet,不佔人數)

## 問1 分層與依賴方向 — 大致對齊,三處 ⚠ 交編排者
spec 沒明講檔案路徑,但從 PRIOR-ART 措辭可推斷跟 governance/eval/ablation_lumos_first.py 骨架走。
引句:「實驗骨架直接沿用 [[Projects/修法A_lumos先行ablation_計劃]] 的預註冊格式」
⚠ 讀治理帳的路徑:retrieval_eval.py 全程用 _lum()(subprocess 呼叫 CLI 拿 JSON),從不直讀 vault/ledger;
  ablation_lumos_first.py 只讀自己產出的 json。本案要「從帳上 folded_set 反推」,沒說走 CLI 還是直開 jsonl。
⚠ 重新派審查員的機制:design-loop 慣例靠 loop next 現場派席(非全自動 subprocess);
  ablation_lumos_first.py 走全自動 scenario_probe.py→claude -p headless。本案用哪條沒寫。
⚠ 兩點都屬「專案有不只一種既有做法、spec 沒表態」,不硬判。
file: `governance/eval/retrieval_eval.py:22`

## 問2 命名與錯誤處理 — 兩處 minor
對齊:預註冊寫死跑完不得改;撞窗口援引既有 --wait-on-limit / 逐題補缺。
file: `governance/eval/ablation_lumos_first.py:270`、`:113`
severity: minor
blocking: 否
minor 1:產物落點/命名完全沒定。鄰居有明確慣例 governance/eval/ablation-lumos-first/<date>/ +
  meta.json/summary.json/summary.md、每題每組一檔永不覆寫;本案只用抽象詞帶過。
  引句:「本案在隔離副本裡重跑歷史迴圈、記在獨立帳上,不碰任何真迴圈的計分」
file: `governance/eval/ablation_lumos_first.py:283`
severity: minor
blocking: 否
minor 2:重試哲學與鄰居不一致。鄰居是「隨時可重跑、逐題逐組算缺場、無限補到齊、自動等窗口重置」;
  本案是撞限流封頂只補一次。
  引句:「記部分結果與缺的場次,**只補跑一次**,結論降級為「初步」」

## 問3 第二種做法 — 兩處 major
severity: major
blocking: 是
major①:與 lumos loop replay 的關係全篇未交代。cmd_loop_replay 本身就是「重跑歷史迴圈的判定」的既有原語,
  --freeze 產 governance/replay/<id>/verdict.json,含 git blob 錨定與 engine_rev 漂移偵測,
  拿的正是「有快照的收斂迴圈」這套東西。本案概念空間幾乎同一個,卻連提都沒提為什麼不擴充它、邊界在哪。
  PRIOR-ART 查了外部論文與 guard-kill/canary-audit 兩個內部案例,漏了拓樸上最近的親兄弟。
  引句:「拿有快照的收斂迴圈,機械刪掉一條當初被折入的實質條款,隔離重跑同一輪,看有沒有人再抓到一次」
file: `scripts/lumos:451`、`:453`、`:559-561`

已排除(對齊):guard kill 原語的取捨有講清楚——明確「借方法、不借實作」,且點名沿用共用的 quote-check。
  guard-kill 那套是「改原始碼字串+重跑綁定單元測試」,結構上對不上「刪一段文字+重派 AI 面板」,不硬套合理。
  引句:「本案的「能執行的東西」=被刪的那條條款是否被逐字錨回(沿用既有 quote-check 機制,scripts/lumos:11670-11691)」

severity: major
blocking: 是
major②:隔離執行環境沒選邊,且正好是本專案出過事故的那類風險。專案現有兩種隔離做法:
  guard-kill/loop-replay 用 git worktree;scenario_probe.py 用 rsync 複本+拔遠端+擋 pre-push 的沙盒,
  原因是 2026-08-23 曾發生探針複本把東西真的推上遠端。本案要派活的 AI 面板去審被動過手腳的材料,
  風險屬性更接近後者,但 spec 只用「隔離副本」帶過,沒選定也沒提防重演。
  引句:「★這個區別要在實作時用目錄與帳檔隔離兌現,不是嘴上說說★」
file: `scripts/scenario_probe.py:150-176`;`scripts/lumos:6848`

不對齊共 4 條,其中 major 2 條。
