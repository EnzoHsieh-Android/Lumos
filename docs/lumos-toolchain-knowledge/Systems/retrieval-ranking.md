---
type: system
status: done
created: 2026-07-10
updated: 2026-07-11
tags:
  - type/system
  - status/done
summary: |-
  FLOW:tokenize(CJK bigram+ASCII拆分)→BM25F(欄位tf加權於飽和前,平滑IDF)→search --ranked只重排既有候選｜_reco(BFS-decay 1/2^k+共引同行×2飽和+Jaccard;G=0.6/0.25/0.15)×BM25F融合(R=0.6L+0.4G)→context --recommend｜impact --ranked(固定席=事故+合約,不占top_k;動態閾;stdin單包JSON prospective)→hook降噪(v1.1待接)
  KEY:search面已轉正預設(2026-07-11,goldset §6全過:修正尺 nDCG@5 +58.1%/held +106.8%;--legacy逃生,--regex走舊路,預設全量+逐檔命中明細——資訊零損失);recommend/impact面dormant(hook面gate未過:P@8=.52、過閾中位16、固定席噪音9/44);hop≥2需L>0、hop1只受靜態底線;結構前綴停用集(KEY:/FLOW:模板詞不算詞彙訊號);A1型別先驗:moc×0.4乘於詞彙分(train網格凍結,held零倒退,見[[Projects/節點靜態先驗_調研]])
  KEY:★DEBT★ 多詞片語候選=legacy片語語意(0候選不回退)｜cochange proxy對圖譜related面太稀(兩vault實證,僅sanity check)｜hook接線v1.1待評測
  DEP:[[Systems/lumos-cli-read]][[Systems/cochange-guard]]
  TEST:51/51(t_tokenizer_unit 7+t_search_ranked 17+t_context_recommend 10+t_impact_ranked 8+t_impact_diff 9)+全套994綠 | VERIFY:[[Verification/2026-07-10_檢索排序v1]][[Verification/2026-07-11_檢索goldset評測]]
related:
  - "[[Projects/檢索優化_計劃]]"
  - "[[Systems/lumos-cli-read]]"
  - "[[Projects/節點靜態先驗_調研]]"
verified_by:
  - "[[Verification/2026-07-10_檢索排序v1]]"
  - "[[Verification/2026-07-11_檢索goldset評測]]"
---
# retrieval-ranking（檢索排序與關聯推薦 v1）

設計三輪 panel（Codex 跨家族否決席全勤、5/5 canary 零漏——史上首例）收斂於 [[Projects/檢索優化_計劃]]，golden 凍結 governance/golden/retrieval/。雙盲合併（Claude×GPT-5.6）八處分歧裁定見計劃節點。

## CLI（search 面已轉正；recommend/impact 面 dormant）

- `lumos search <詞> [--top N] [--json]` — **BM25F 排序已是預設**（2026-07-11 轉正；標題權重 4×body；輸出保留逐檔命中明細，只換排檔順序）；`--legacy` 走舊字母序全量、`--regex` 自動走舊路、`--ranked` 保留相容。
- `lumos context <節點> --recommend [--top 8] [--min-score 0.20] [--json]` — 圖分×詞彙融合推薦+姐妹折疊。
- `lumos impact --file F --ranked [--stdin-payload] [--incidents-only]` — 固定席降噪；prospective incident（套 delta 後內容比對）。
- `lumos impact --diff <base>..HEAD [--json]` — **code-loop 橋接（2026-07-11）**：聚合整段 diff 各檔 ranked impact（query=該檔 hunk）成受影響功能面 manifest（固定席全保+top-8+來源檔）；advisory 審計鏡頭、不接 hook。見 [[Projects/impact-diff橋接_計劃]]。
- 評測器 `governance/eval/retrieval_eval.py`（nDCG/MRR/P@k；LUMOS_EVAL_VAULT 覆寫）。
- goldset 生成器 `governance/eval/build_goldset.py`：30 search（分層:繁中短詞/identifier/縮寫/單漢字）+20 edit（真 git 案例）；候選池=legacy∪ranked 去識別洗牌（sha256+salt 可重現）；標註表 retrieval-labeling-sheet.md（留白=0 省力制）。人標完解析回 goldset → retrieval_eval 跑 gate。
