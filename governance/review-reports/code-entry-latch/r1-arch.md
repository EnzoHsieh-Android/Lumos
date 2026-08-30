# code r1 架構對齊席

**A-1**|major|blocking:是
引句:「_EL_DATE_PREFIX_RE = re.compile(r"^\d{4}-\d{2}-\d{2}_")」
scripts/lumos:11515 已有逐字相同的 _NODE_DATEPFX_RE(cmd_impact D2 近名判定同用途)——patch 自己宣告「不另寫第二份」卻在日期前綴子步驟開了第 N 份同型實作。

**A-2**|minor:_el_is_cjk 範圍 tuple 與 _cjk_nospace_hint 內聯判斷逐字相同;檔內已並存 ≥3 種 CJK 判定,係既有重複慣例延續非新樣式。
**A-5**|minor:兩處裸 except Exception 完全靜默不留痕,比同檔其他 advisory 失敗至少走 stderr 更沉默;仍在既有 fail-open 光譜內。
引句:「out["related_nodes"] = _el_related_nodes(env, Path(spec).stem if spec else loop_id)」

抑噪(一致面):_el_near_ratio 復用 difflib 手法同 _arch_alignment_hints;_el_query_tokens 正確重用 _rank_tokenize;不走 cmd_search 頂層=helper 呼 helper 方向正確;放置位置同慣例;related_nodes 專屬列印分支 vs 純量白名單=同 roster 二分慣例。

severity: major
