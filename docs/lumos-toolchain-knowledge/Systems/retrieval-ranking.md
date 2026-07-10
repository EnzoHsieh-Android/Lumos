---
type: system
status: done
created: 2026-07-10
updated: 2026-07-10
tags:
  - type/system
  - status/done
summary: |-
  FLOW:tokenize(CJK bigram+ASCII拆分)→BM25F(欄位tf加權於飽和前,平滑IDF)→search --ranked只重排既有候選｜_reco(BFS-decay 1/2^k+共引同行×2飽和+Jaccard;G=0.6/0.25/0.15)×BM25F融合(R=0.6L+0.4G)→context --recommend｜impact --ranked(固定席=事故+合約,不占top_k;動態閾;stdin單包JSON prospective)→hook降噪(v1.1待接)
  KEY:全部dormant(旗標啟用,legacy預設不動);翻預設gate=人工goldset評測過§6門檻;hop≥2需L>0、hop1只受靜態底線;結構前綴停用集(KEY:/FLOW:模板詞不算詞彙訊號)
  KEY:★DEBT★ 多詞片語候選=legacy片語語意(0候選不回退)｜cochange proxy對圖譜related面太稀(兩vault實證,僅sanity check)｜hook接線v1.1待評測
  DEP:[[Systems/lumos-cli-read]][[Systems/cochange-guard]]
  TEST:35/35(t_tokenizer_unit 7+t_search_ranked 10+t_context_recommend 10+t_impact_ranked 8)+全套978綠 | VERIFY:[[Verification/2026-07-10_檢索排序v1]]
related:
  - "[[Projects/檢索優化_計劃]]"
  - "[[Systems/lumos-cli-read]]"
verified_by:
  - "[[Verification/2026-07-10_檢索排序v1]]"
---
# retrieval-ranking（檢索排序與關聯推薦 v1）

設計三輪 panel（Codex 跨家族否決席全勤、5/5 canary 零漏——史上首例）收斂於 [[Projects/檢索優化_計劃]]，golden 凍結 governance/golden/retrieval/。雙盲合併（Claude×GPT-5.6）八處分歧裁定見計劃節點。

## CLI（全 dormant）

- `lumos search <詞> --ranked [--top N] [--json]` — BM25F 排序（標題權重 4×body）。
- `lumos context <節點> --recommend [--top 8] [--min-score 0.20] [--json]` — 圖分×詞彙融合推薦+姐妹折疊。
- `lumos impact --file F --ranked [--stdin-payload] [--incidents-only]` — 固定席降噪；prospective incident（套 delta 後內容比對）。
- 評測器 `governance/eval/retrieval_eval.py`（nDCG/MRR/P@k；LUMOS_EVAL_VAULT 覆寫）。
