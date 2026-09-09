severity: clean

# 架構對齊審查——棧別提問表態閘反面詞擴充

## 問一:反面詞放的位置與形狀

直接塞進同一個 `when` 清單,沒有分「範式詞/反面詞」兩欄,這跟既有做法一致、不是新形狀。`_STACK_QUESTION_SPECS` 本來就只有 `{id, q, when}` 三鍵,`when` 從第一版起就是一串未分類的觸發 regex(例:`scripts/lumos:15150` `vue-lcp` 原本就混著 `<img`、`<picture`、`IntersectionObserver` 等不同性質的詞),沒有「詞的來源類型」這個維度,所以把反面詞併進同一串不是打破結構,是延續結構。

下游唯一會逐一展開 `when` 內容的消費者是 `_dispositions_template`(`scripts/lumos:21536`):`"reason": "未觸發:" + ", ".join(spec_w for spec_w in (s["when"] for s in _STACK_QUESTION_SPECS[_stk] if s["id"] == qid) for spec_w in spec_w)`——它本來就把整串 `when`(不分類型)攤平接成一句話印給人看,並非改動引入的新行為。`gov --stats` 端(`scripts/lumos:4518` 起的表態閘統計段)只以題目 `id` 為鍵彙總 satisfied/na/todo 四值,從未按觸發詞類型分桶;若真要「分別統計哪類觸發」,現有 `triggered_by`(`_stack_applicability` 回傳,`scripts/lumos:15328`)已經記錄命中的**確切 regex 原文**,要事後分類範式詞/反面詞可以直接用文字比對已記錄的內容做,不需要在 `when` 這層先分欄。沒有找到需要拆開的具體理由,也沒有找到既有慣例被打破的證據。

## 問二:raw 旗標與 in_strings 判斷邏輯是否一致

一致。既有慣例在 `_PITFALL_DIFF_PATTERNS`(`scripts/lumos:15344`)講得很白:「SQL 本來就寫在字串裡,要看字串;其餘只看真代碼」——`in_strings` 只給「內容本來就活在字串字面裡」的形狀開。`_STACK_TRIGGERS` 的 `raw` 旗標(`scripts/lumos:15198`)在此之前就寫著同一條規則:「這題的 when 要看字串內容(.on("error"、LIKE '%、import from "./x"),剝了字串反而誤判;同 _PITFALL_DIFF_PATTERNS 的 in_strings」——這段說明本身是既有代碼(不在本次 diff 增修範圍內,是 diff 的 context 行),本次診斷只是把既有規則套用到符合這個形狀的四題。

實測驗證(用 `_load_lumos_inproc` 同款方式原地載入 `scripts/lumos`、直呼 `_strip_string_literals`):
- `cs-data` 新增反面詞落在字串字面內:`'using var cmd = new SqlCommand("SELECT * FROM t", conn);'` 剝字串後變成 `'using var cmd = new SqlCommand("");'`——SQL 內容消失,若不開 raw 就永遠比對不到,和 SQL 該看字串的既有規則同形。
- `node-eventloop` 新增的 `child_process`:`"const cp = require('child_process')"` 剝字串後變 `"const cp = require(\"\")"`——同樣消失,需要 raw。
- `vue-lcp` 新增的 `createElement\(['\"]img`:`"const el = document.createElement('img')"` 剝字串後變 `'const el = document.createElement("")'`——同樣消失,需要 raw。
- `node-data` 新增的 `'[\'\"](SELECT|INSERT|UPDATE|DELETE)\\s'` 與 cs-data 同理,是刻意比對字串裡的 SQL 字面。

四題改 raw 全部對應「這題至少有一個詞本來就活在字串字面裡」,跟 `in_strings`/既有 `raw` 說明的判斷邊界相符,不是另創一套語意。`raw` 本身是「整題一個開關」而非逐詞開關,這個顆粒度在 `vue-bundle`(既有,`raw: True`)與 `sql-sargable`(既有,`raw: True`)已經是先例,本次只是把既有顆粒度套用到多四題,沒有引入新的顆粒度。

## 問三:有沒有引入第二種做法

沒有。本次 diff 對 `scripts/lumos` 的改動範圍只有:①在既有 spec 的 `when` 清單裡追加字串元素;②替四個既有 spec 補上既有的 `raw: True` 鍵;③加一行說明用途的註解。`_stack_norm_line`(`scripts/lumos:15293`)、`_stack_applicability`(`scripts/lumos:15306`)、`_strip_string_literals`(`scripts/lumos:15362`)、`_STACK_TRIGGERS` 的組裝邏輯(`scripts/lumos:15199`)這些真正決定行為的函式一個字都沒有被改動——比對用的仍是同一套正規化、同一個 `raw` 布林旗標語意、同一種 `{id, q, when}` 表的產生方式。測試端新增的 `_legacy` 樣本字典沿用同函式所在測試裡既有的 `_samples` 字典寫法(`stack: (qid, hit, miss)` 或此處的 `stack: [(qid, line), …]`,一樣是「呼叫 `_stack_applicability` 直接斷言 applicable 集合」的既有驗證手法),沒有另立驗證管道。

（`scripts/test_lumos.py` 同一段 diff 裡另外新增的 `t_usage_scan_smoke` 測的是 `scripts/usage_scan.py`,與本次「反面詞」主題無關——查 `git log` 確認它來自另一個既有提交 `004154f`(Spotify shunt 調研),只是恰好落在同一個 `LUMOS-IMPACT` 範圍內,不是本次變更引入的第二種做法,不列為本題發現。）

不對齊共 0 條,其中重大 0 條。
