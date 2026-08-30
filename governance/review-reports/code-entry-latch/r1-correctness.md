# code r1 正確性席(這段 code 會出錯的假設者)

**C-1**|major|blocking:否(fail-open 下退化為無此功能,但整條 advisory 存在理由被繞過)
引句:「濾純數字(「2026」命中 381/385=全庫召回)與長度 1 的 ASCII token」
佐證:scripts/lumos _el_query_tokens 濾網+「token ≤1 且無 CJK」閘。dref-v4/gate-v2 型「單字+版號」編號清洗後只剩 1 token,落無訊號分支——自建 vault 實測 `search dref` 命中 0.592 但 loop next 回 queried:false。可查的單字被閘掉。

**C-2**|minor|blocking:否
引句:「src_stem = Path(str(source)).stem」
呼叫端已 .stem 過一次,函式內再 .stem 對含句點 stem 非幂等:`2026-07-11_hook面v1.1轉正` 被截成 `…v1`,difflib 0.9091→0.7778,near_name 系統性壓低。

**C-3**|minor|blocking:否
引句:「"\u4e00" <= ch <= "\u9fff" or "\u3040" <= ch <= "\u30ff"」
_el_is_cjk 與 _RANK_CJK_RE(1867)不同源:漏擴充A、多認切詞器不產出的假名/諺文(死碼)。

**C-4**|minor|blocking:否
引句:「_rank_score_candidates(env, query, cands)[:top]」
混合 token(batch3)在 ranker 內再切詞,被濾掉的數字子詞回到記分集——只影響進榜候選間排序,不影響進不進榜。

抑噪:CJK bigram 二次切詞不變形(bigram 的 bigram=自己,實跑多組一致);首輪必達 plant-canary(rounds 空判在 spec None 判之前);except Exception 不吞 KeyboardInterrupt/SystemExit;B 的 folder 單層假設對 TEMPLATES 全型成立;rc_side 提早 return 路徑對 B 不可達;EL-4 修復有效(不經 cmd_search 頂層,紅釘過)。

severity: major
