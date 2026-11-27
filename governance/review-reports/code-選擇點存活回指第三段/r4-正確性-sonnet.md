severity: minor

**修補三問**
1. 修到沒:修到了。判段只有一個來源。`_choice_plan_sections` 只由 `_choice_plan_view` 呼叫(`scripts/lumos:81151`),材料、第 2 層引句驗證和 `deps_sha` 都走 `ctx.view`,三個讀者拿到的是同一份段落。旁檔也修到了:每組(`_choice_layer_split_groups`)各算自己的旁檔,同組各份用同一個 `g`,一份材料只指到自己這組的旁檔,旁檔檔名依「清單編號加計劃路徑雜湊」固定,跨組同一份計劃指到同一支檔。
2. 有沒有引入新問題:沒有阻擋級的新問題,只有下面一條覆蓋缺口。
3. 同類位置還有沒有:有。「從正文排除」(`_choice_layer_not_body`)和「另外收進預期值表」(`_EXPECTED_H2_RE`)是兩套判斷,寬度不一致,見下面那條。

我跑了 `-k choice_plan_sections`、`-k choice_layer_plan_sides`、`-k choice_layer_side`、`-k choice_layer_split`,各自全綠(9、4、2、3 條)。

severity: minor
blocking: 否
`scripts/lumos:81086` 一帶。`_CHOICE_LAYER_NOT_BODY_RE` 會排除「預期值表(說明)」、「預期值表:說明」、「§2 預期值表」這類標題,但預期值表的讀取用 `_EXPECTED_H2_RE = ^##\s+預期值表\s*$`(`scripts/lumos:14412`),只認標題恰好是「預期值表」。標題帶括號、冒號或前綴時,這一節既不進 `expected`,也不進 `sections`,材料和第 2 層引句驗證都看不到它的內容,第 2 層無從引它。repo 裡現有的預期值表標題全是裸「預期值表」,所以目前不會發生,只是新排除形狀比讀取形狀寬。「驗收條款」標題帶說明時也一樣:節內非條款行的說明文字,排除後不會出現在任何地方。這是覆蓋面問題,不會做出錯的行為。未能重現(未實跑)。
引句:「_CHOICE_LAYER_NOT_BODY_RE = re.compile(r"(?:\S+\s+)?(?:驗收條款|預期值表)\s*(?:[(（][^\n]*[)）]\s*|[:：][^\n]*)?")」

總結:最高等級是 minor
