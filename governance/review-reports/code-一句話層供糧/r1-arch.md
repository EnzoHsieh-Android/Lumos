**A-1**|clean|blocking(否)
引句:「_GIST_LABEL_RE = re.compile(r"^(FLOW|KEY|FLAG|DEP|TEST|DECISION):\s*")」
scripts/lumos:5979-5981 vs :5917/:6632/:7404/:4934。就近宣告+子系統前綴被 EL 層組裝=既有慣例。一致。

**A-2**|minor|blocking(否)
引句:「恆回 str;任何例外回空(fail-open)。」
scripts/lumos:5997-6034(自包式 try/except)vs :6238-6247(EL-5 呼叫端式)。第二種 fail-open 款式,但自包式已有 6 個先例(_usage_log/_ymd/_ver_tuple/_impact_knob/_bound_tests_log/_delguard_log_degraded),非新開第三條路。

**A-3**|clean|blocking(否)
引句:「先 _esc_clean 消毒(控制碼換空格,同逃逸帳載重合約),大 limit=只消毒不在這層截。」
scripts/lumos:5988 呼叫 _esc_clean(:5300)。復用不另寫。一致。

**A-4**|minor|blocking(否)
引句:「回輸出合約 dict(EL-16):{"query","queried","nodes":[{"name","status","decisions","near_name"}]}」
scripts/lumos:6042 docstring 契約行未同步補 gist 第五鍵(:6079 已加、測試 :23814 已改五鍵)——docstring 是 EL-16 引用處當真相源在讀的,漏補誤導下一個讀者。建議同 commit 補。

**A-5**|clean|blocking(否)
引句:「m = _load_lumos_inproc()」
test_lumos.py:24135+:24183 混用手法沿用同家族唯一前例 t_entry_latch_advisories(:23789-23883);★紅釘★ 註解格式一致。

**A-6**|clean|blocking(否)
引句:「超出上限的前 10 篇列名+一句話層(L0)、之後純列名,仍不必答」
SKILL.md:19 vs 計劃.md:39 d9 原句逐字對上;必答/不必答分界未動,d9 正確落地。

severity: minor
