# code r1 併發資源席

**R-1**|major|blocking:否(不影響 rc/正確性,但推翻 spec 唯一效能宣稱)
引句:「text = (env.vault / rel).read_text(encoding="utf-8-sig")」
Verification 筆記宣稱 0.6s,實測 pre/post 對照(真 vault 385 篇):密集查詢(impact-鏡頭機械化re)+1.4~1.9s、稀疏查詢 +0.17~0.19s,波動逾 10 倍;且三條 revalidate 無一涵蓋 A 效能退化。

**R-2**|minor:候選檔 21%(81/386)被讀兩次(OR 掃描一次+_rank_fields 一次),絕對值 ~14-29ms。
引句:「for rel, _score, _hits in _rank_score_candidates(env, query, cands)[:top]:」

**R-3**|clean:pitfalls 的 :5806 handle 提示=誤鳴(read_text 內建 with;與既有 _rank_fields 同款)。
**R-4**|minor:純讀無寫入無競態(逐行確認無 open('w')/_write_lf);但無快取無鎖,並發各自重付全掃成本。
引句:「out["related_nodes"] = _el_related_nodes(env, Path(spec).stem if spec else loop_id)」
**R-5**|clean:B 在合成 10,000 篇 vault 實測 9ms、5,000 篇全命中極端案 101ms——difflib 成本可忽略。

severity: major
