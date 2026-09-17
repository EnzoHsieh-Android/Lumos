severity: clean

**四問逐項核對**

**① 上一輪「手寫 while 找應該改 lookbehind 正則」折了沒——對齊。** 本輪把 `_shall_index` 從手寫 `while` 迴圈改成 `_SHALL_RE.search()` 後取 `m.start() if m else -1`,跟本檔既有的排除上下文正則同一招(`file: scripts/lumos:6404` `re.compile(r"(?<!\w)" + ... )`、`scripts/lumos:25705` `_LENS_SPEC_CODE_RE = re.compile(r"(?<![\w/])...)`)。`m.start() if m else -1` 這個薄包裝寫法也不是孤例,本檔到處是 `X if m else Y`(`file: scripts/lumos:3929,3934,12749,16758` 等),沒有引入新做法。

**② 字元集常數該跟鄰居同形——對齊。** 舊的 `_SHALL_COMPOUND_PREV = "反效因適回對相供答感響呼"` 是給手寫迴圈用的普通字串;新版直接把中文字元類寫進 `re.compile()` 的字元集 `[反效因適回對相供感響呼順理照接自]`,跟緊鄰上一行的 `_CLAUSE_SEP_RE = re.compile(r"[,，]")`(同一批常數群組裡,file: `scripts/lumos:4652`)是同一種「正則字元類裡直接放中文/全形字」的先例,擺位也緊接在同一群組常數之後、函式之上,跟 `_CLAUSE_HANG_STATES` 那組「常數群 + 兩行註解 + 下方函式」的排法(`scripts/lumos:4648-4655`)一致。

**③ 命名與擺位——對齊。** `_SHALL_RE` 命名跟本檔其他 `_XXX_RE` 一致(如 `_CLAUSE_SEP_RE`、`_ROLLBACK_H2_RE`、`_LENS_SPEC_CODE_RE`),擺在使用它的函式 `_shall_index` 正上方,跟 `_LENS_SPEC_CODE_RE`(擺在 `_nodehome_landing_sizes` 等使用它的函式群之上,`scripts/lumos:25704-25711`)是同一種「常數緊貼使用處上方」的排法。註解也是兩行、上面一行解釋語意、下面一行補代碼審溯源與例外理由,跟 `_CLAUSE_HANG_STATES` 上方那兩行註解(`scripts/lumos:4653-4654`)同款。

**④ `_clause_grammar` 內兩處「缺應」判斷從 `"應" not in rest` / `"應" not in b` 改成 `_shall_index(...) < 0`——對齊,而且是修掉上一輪遺留的內部不一致。** 之前「找位置」走 `_shall_index`(跳複合詞)、但「判斷有沒有應」卻是裸字串 `in` 檢查(不跳複合詞),等於同一份語意用兩套邏輯,這正是上一輪 review 抓到的漏洞成因之一;本輪統一收斂成只有 `_shall_index` 一個入口,沒有引入第二套做法,反而是消掉既有的雙軌問題。

引句:「_SHALL_RE = re.compile(r"(?<![反效因適回對相供感響呼順理照接自])應")」
引句:「    return m.start() if m else -1」

不對齊共 0 條,其中 major 0 條。
