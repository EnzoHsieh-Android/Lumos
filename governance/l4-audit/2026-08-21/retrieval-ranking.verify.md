C1. ✅ search 預設走 BM25F 排序，title 權重為 body 4 倍 | 證據: scripts/lumos:1361 `_RANK_FIELD_W = {"title": 4.0, ... "body": 1.0, ...}`；scripts/lumos:14824 `_use_ranked = not args.search_legacy and not args.regex`（無旗標即預設 ranked）

C2. ✅ --legacy 走舊字母序全量排列（逃生旗標） | 證據: scripts/lumos:14401-14402 `--legacy ... dest="search_legacy"`；14824 legacy 時 `_use_ranked=False`

C3. ✅ --regex 自動改走 legacy 舊路 | 證據: scripts/lumos:14824 `_use_ranked = not args.search_legacy and not args.regex`（regex=True 即關閉 ranked）

C4. ✅ --ranked 旗標保留但對行為無額外作用（功能等同新預設） | 證據: scripts/lumos:14396 help 文「已是預設,旗標保留相容」；14824-14826 `_use_ranked` 計算完全不採用 `args.ranked`（只在與 --regex 併用時印 stderr 提示）

C5. ✅ --any 多詞回退 2026-08-03 起預設開，整串片語全庫 0 候選才觸發 OR 回退，--no-any 為逃生旗標 | 證據: scripts/lumos:1600-1615 docstring「2026-08-03 起為預設...`--no-any` 逃生」；14399 `--no-any` dest=search_no_any；14831 `any_terms=not args.search_no_any`；1616-1618 `if any_terms and (not regex) and len(_fb_terms) > 1:` 搭配 1636 `if not _fb_seen:` 才觸發回退（片語真的搜不到才轉 OR）

C6. ✅ context --recommend 融合公式 R=0.6L+0.4G，G=0.60B+0.25C+0.15J | 證據: scripts/lumos:6029 `R = round(0.60 * L + 0.40 * g["G"], 4)`；6000 `"G": round(0.60 * B + 0.25 * C + 0.15 * J, 4)`

C7. ❌ 共引×2＋飽和、Jaccard 部分屬實，但 BFS 衰減公式並非「1/2^k」 | 證據: scripts/lumos:5992 實際為 `B = min(1.0, 2.0 / (2 ** k))`（即 2/2^k = 2^(1-k)，k=1 時 B=1.0，非 claim 所述 1/2^k 在 k=1 時應為 0.5）；共引飽和見 5994 `C = cr / (cr + 2.0)`（同行貢獻 2、同節點貢獻 1，見 5978-5989）符合「×2 有飽和上限」；Jaccard 見 5998 `J = inter / union`

C8. ✅ impact --ranked 動態閾值係數現行為 0.65 | 證據: scripts/lumos:13725 `_impact_knob("LUMOS_IMPACT_DYN_COEF", 0.65) * max_free`

C9. ❌ R1 rescued 恆 pinned:false 屬實，但旋鈕 LUMOS_IMPACT_RESCUE_N 現行預設值為 3，非 1 | 證據: scripts/lumos:13750 `_rescue_n = int(_impact_knob("LUMOS_IMPACT_RESCUE_N", 3))`；13743-13744 註解本身承認「2026-08-07 考卷轉正預設 1」為歷史值，其下 13748-13749 另有「水位案考卷轉正 N=3」覆寫；rescued pinned:false 見 13757-13761 `rr = dict(r)` 繼承自 `dropped` 篩選條件 `not r["pinned"]`（13756）

C10. ✅ R2 裸檔名容錯機制，git ls-files 反查，旋鈕預設 1 | 證據: scripts/lumos:13120 `if int(_impact_knob("LUMOS_IMPACT_BASENAME_MATCH", 1))`（實際 env 名為 `LUMOS_IMPACT_BASENAME_MATCH`，claim 簡寫「BASENAME_MATCH」但值與機制相符）

C11. ✅ S2 水位謂詞：free direct < N 時補 need=N−count，N=3 | 證據: scripts/lumos:13748-13752 `_rescue_n = int(_impact_knob("LUMOS_IMPACT_RESCUE_N", 3))`；`_need = max(0, _rescue_n - _free_direct)`

C12. ✅ query junk 閘：剝 shebang 後殘餘 < MINLEN(預設1) 視同空查詢，L 臂靜默，事故探針不受影響，MINLEN<=0/NaN/Inf 停用 | 證據: scripts/lumos:13386-13401 `_impact_query_junk`；13395 `minlen = _impact_knob("LUMOS_IMPACT_QGATE_MINLEN", 1)`；13396 `if not (minlen > 0) or minlen == float("inf"): return False`；13678-13682 呼叫處註解「事故探針 _delta_q 刻意不受閘」

C13. ✅ impact --diff 聚合各檔 ranked impact，advisory 性質，未接 hook | 證據: scripts/lumos:13835-13840 docstring「定位=審計員鏡頭(advisory,人判)...故不接 hook」；scripts/hooks/claude/impact-hook.py:462 hook 呼叫的是 `lumos impact --file`，全 hook 檔無 `--diff` 呼叫

C14. ✅ hook v1.1：窗外 ranked top-8，TTL 窗內 incidents-only，content trigger 比對 delta（非整檔） | 證據: scripts/hooks/claude/impact-hook.py:458-465 「窗外→ranked...固定席+top-8...窗內→--incidents-only」；14560 `--top` default=8（hook 未傳 --top，沿用預設 8）；scripts/lumos:13629-13632 「content trigger 的比對對象(v1.1 精度修):有 delta→比對『這次改動的內容』」

C15. ✅ context --recommend 為 dormant，需顯式旗標 | 證據: scripts/lumos:14216 `p.add_argument("--recommend", action="store_true", help="...dormant v1")`

C16. ✅ A3 已消融殺除，現行排序路徑無 authority/PPR 生效；A1.5 狀態降權預設關 | 證據: scripts/lumos:1479-1481 註解「A3 權威度(in-degree 飽和加分)已試已殺...勿憑直覺復活」，`_rank_score_candidates`(1446-1483) 全函式無 authority/PPR 計算；`_graph_pagerank`(6234) 僅在 doctor Check S(828) 與 `stale` 排序(6373) 呼叫，皆非 search/context/impact 排序路徑，且無任何呼叫傳入 personalization 參數；1422 `_RANK_STATUS_MULT = 1.0 # ...1.0=關`

C17. ✅ A1 型別先驗：moc 詞彙分×0.4 | 證據: scripts/lumos:1419 `_RANK_TYPE_MULT_MOC = 0.4`；1425-1439 `_rank_type_mult` 對 `type=="moc"` 套用該乘數

C18. ✅ retrieval_eval.py 支援 nDCG/MRR/P@k，LUMOS_EVAL_VAULT 可覆寫 vault 路徑 | 證據: governance/eval/retrieval_eval.py:35 `def ndcg_at_k`；44 `def mrr`；51 `def precision_at_k`；17 `_VENV = os.environ.get("LUMOS_EVAL_VAULT")`

C19. ✅ build_goldset.py 30 題 search（分層 zh_short/identifier/acronym/single_char）+ 20 題 edit，候選池 legacy∪ranked 聯集 sha256+salt 去識別洗牌，--force-full 拆分空金標情境 | 證據: governance/eval/build_goldset.py:14-18 `SEARCH_QUERIES` 四類 12+8+6+4=30 題；57 `def edit_cases(n=20)`；43 `"""池 = legacy 命中前 8 ∪ ranked 前 8(去識別:只留節點名,洗牌)"""`；52-53 `hashlib.sha256((q + SALT)...); rnd.shuffle(pool)`；109-114 `--force-full` 旗標，未帶則 ERROR 擋下全量重建

C20. ✅ hop≥2 需 L>0 才納入，hop1 僅受靜態底線 | 證據: scripts/lumos:6027 `if g["hop"] >= 2 and L <= 0: continue`（`_reco_fused`，緊接 6026 comment「hop1 只受靜態底線」）

✅17 ❌3 ❓0 ⏭0
