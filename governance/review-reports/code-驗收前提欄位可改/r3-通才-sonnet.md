severity: clean

已看,無:這輪新加的三塊東西都做了破壞性驗證,沒找到真問題。

1. `_YAML_TYPED_RE` 擴充(十六/八/二進位、六十進位、無限大、日期)——我把它臨時退回舊版「只認十進位整數與小數」的窄正則重跑測試,`t_set_condition_fields_standard_yaml_safe` 立刻紅 4 條(`0x1A`/`1:20:30`/`.inf` 三案例),證明測試真的會對這條回歸翻紅,不是空氣防線。引句:「+  WHY:[2026-09-26 驗收前提欄位可改,另一個對話回報、Enzo 裁「好」]`set` 收 valid_under」這段 commit 說明與程式碼行為一致。

2. 逐項核對題目點名的中文/英文誤判疑慮,實測(`fmt_scalar`)加上真的 js-yaml(Obsidian 用的引擎,repo 本身零依賴不含 PyYAML,所以拿 js-yaml 當「標準 YAML」比對才對題)回讀比對,全部一致、沒有誤判也沒有漏判:
   - 「3 個條件成立」「版本 1.2.3 之後」「2026-09 以後才重驗」「10:30 開會前」「commit d62ac66b 之後」都沒被 `_YAML_TYPED_RE` fullmatch 命中(有非數字/非日期的尾巴,不是整串匹配),照舊不加引號,js-yaml 讀回來字串一模一樣。
   - 「hash 163933e9」「1e3」單獨出現時才會被判定要加引號——用 js-yaml 實測確認 `1e3`、`163933e9` 這兩個「數字+e+數字」的寫法 js-yaml 真的會解成數字(1000 / 1.63933e14),所以加引號是對的,不是誤報。
   - 純日期「2026-09-26」、「0x1A」、「1:20:30」、「.inf」四個典型型別劫持案例,加引號後 js-yaml 讀回來跟寫入前一致;不加引號會被解成 timestamp/int/float,證實這條白名單守住了洞。
   - 額外測了「-5 個」「+5 個」「0755 權限」「a: b」「單引號'test」「雙引號"test」「~」「NULL」「含 # 井號但前面沒空白#test」等十幾組邊界值(用 js-yaml 全部核對),沒有一組寫入後讀回來跟原字不同。唯一觀察到的是 `-` 開頭一律加引號、`+` 開頭不加(白名單對 `-` 比 `+` 保守),這屬於「拿不準就加引號」設計本身允許的不對稱過度保守,不影響正確性,不是缺陷。

3. 決策文字欄位改走 `_fmt_decision_value` → 共用 `_yaml_plain_ok`/`_yaml_quote` 後,decision-add/supersede/reindex 全套測試(`-k decision`、`-k reindex`)60+10 條全綠,沒有既有輸出被改壞。也把 `_fmt_decision_value` 臨時還原成舊版手刻正則重跑 `t_decision_add_standard_yaml_safe`,兩條斷言都紅(結尾裸冒號寫不出合法 YAML、含「: 」又有雙引號寫不進去),證實這條測試真的鎖住了 r2 提到的第三套判準漏洞。

4. `set` 值參數改 `nargs="+"` 之後,檢查了 codebase 內所有 `cmd_set(...)` 呼叫點(signoff/settle/self_audit/about_code_stamp/responsibility 等內部呼叫都直接傳字串,只有 CLI 入口傳 list),`_cmd_set_locked` 用 `isinstance(value, list)` 分流,兩種呼叫方式都測過、都綠,沒有破壞既有內部呼叫。`t_set` 全量(91 條)、`append` 全量(76 條)、`signoff`(14 條)都重跑過,無回歸。

5. `signed_off` 日期加引號的副作用(commit 說明自己也點名了):查過 `signed_off` 不在 `DATE_KEYS` 裡(它在 `SCALAR_KEYS`),所以真的會走 `_yaml_plain_ok` 被判定為型別劫持而加引號;搜了全 repo 找不到任何地方用原始字串比對這個欄位(唯一寫入點是 `cmd_set(env, rel, "signed_off", today)`,唯一相關測試只斷言子字串 `"signed_off:"` 存在),兩邊解出來的字串值相同,沒有功能性影響,是文件裡已承認的已知代價,不算新問題。
