severity: major

## i1 有效紀錄沒比對「現在綁的測試」,殺完再換成弱測試仍放行
severity: major
blocking: 是——照字面實作,條款先用強測試殺過,之後改綁弱測試,紀錄仍有效,推送前那一道放行,等於沒守住。
- 位置:〈用詞〉有效紀錄、〈範圍〉3。
- 引句:「計劃、條款編號、條款雜湊、第幾個、那句原文都對得上現在那一行」
- 問題:對得上的五項裡沒有「帳上 `test_name` 仍是這條條款綁的測試」。`_clause_sha` 的說明寫明不含綁的測試(`scripts/lumos:13913`)。`INV_TAG_RE` 加 `near` 後,`[near:]` 也不進雜湊。
- 人裁那邊為此另外比對:`_spec_gate_ruled_events` 要求「那一行綁的測試恰好是帳上的 test_name」(`scripts/lumos:14570-14576`),註解說「多綁、換綁都不算」。
- 例:S3 綁 `[test:t_strong]`,`clause-kill --test t_strong` 殺得掉並入帳;之後 S3 改成 `[test:t_weak]`。雜湊不變、`near_text` 不變、`old` 仍恰好一次,於是放行。
- 補法:有效紀錄加條件「帳上 `test_name` 在現在這條綁的測試集合裡」。同條款綁多支時,每支要跑的測試都要各有紀錄,或限定恰好等於那一支。
- 同一缺口:「同一個條款同一個第幾個取最新一筆」的鍵不含測試名。先殺 `t_a` 再對 `t_b` 跑,只有最後那支被證明。

## i2 新閘名 `clause-kill` 沒登記進 `_KNOWN_GATES`,治理帳事件會被靜默吞掉
severity: major
blocking: 是——照字面實作,`_gate_event` 對沒登記的閘名不寫帳。S4 的事件寫不進去,推送前那一道讀不到紀錄而永遠擋。
- 位置:〈用詞〉有效紀錄、〈範圍〉2「記」。
- 引句:「裡 gate 與 kind 都是 `clause-kill` 的一筆(寫法照人裁的 `_situation_rule_event_parts`)」
- 佐證:`scripts/lumos:1840` 的 `if gate not in _KNOWN_GATES:` 印警告後 `return False`,沒寫。名單在 `scripts/lumos:17706`,人裁自己的 `situation-rule` 就在 `:17760` 登記。
- 漂移守衛 `t_gov_stats_gate_drift`(`test_lumos.py:9644`)也會要求登記。
- 不是人裁複製得到的免費行為,spec 的〈範圍〉2、〈範圍〉4 都沒列這一步。
- 同批漏列(minor):
  - `cmd_gov` 的去重鍵是(提交、節點、閘、種類、token、check)(`scripts/lumos:18359`)。人裁為此在 `_gov_row` 加了 `ts+clause_id` 的 token(`:18293`)。
  - `clause-kill` 同一個 HEAD、同一份計劃、不同條款或不同 `near_index` 的多筆事件,在 `lumos gov` 顯示會折成一筆。
  - 要補 token 和 `--stats` 的種類。
  - `_GOV_FIELD_TYPES` 對新欄位 `near_index`、`near_text`、`file`、`old` 不設型別,不會被誤丟。`verdict` 已是 `(str,)`,沒問題。
- `_gov_vc_gate_events` 的呼叫端只靠閘名位元組先篩再比 `gate`,新閘名不會誤吞別的事件,這點沒問題。

## i3 人裁寫回的條款、`[keeps]` 條款要不要 `[near:]`,spec 沒講
severity: major
blocking: 是——照字面實作,人裁剛寫回的條款馬上被「沒有 `[near:]`」擋下,而它已經被人裁殺傷力證過。
- 位置:〈範圍〉1。
- 引句:「每條綁了 `[test:]` 的條款至少一個 `[near:]`(或 `[near:無 …]`)」
- 問題:唯一的豁免是 `[manual:]`。
  - 人裁寫回的行是 `- [Sn] 條款 [test:x]`,沒有 `[near:]`(`_situation_rule_event_parts` 的 `wline`)。
  - 預期值表那道明確扣掉人裁條款(`_spec_gate_ruled_ids`,`scripts/lumos:14618` 起),`[keeps]` 另算。
  - 這份 spec 的判定單位是「綁了測試的條款」,沒對齊「新行為條款」。
- 例:高風險計劃有一條人裁寫回的 S4,規格閘一跑就報「S4 沒有 `[near:]`」。作者只能手改成 `[near:無 …]` 或補跑 `clause-kill`。後者是第二次殺傷力,而人裁那次其實就是同一種證明。
- 補法:寫明「人裁寫回且沒改過字的條款(`_spec_gate_ruled_ids`)與 `[keeps]` 條款不要求」,或寫明要求並說明理由。
- 附帶:`[near:]` 不進雜湊,所以人裁事後補 `[near:無 …]` 不會讓人裁條款失效。這點可以放心。

## i4 推送前那一道沒限定計劃狀態,todo 計劃的設計階段推送會被擋
severity: major
blocking: 是——todo 計劃本來就還沒實作,不可能有 `clause-kill` 紀錄。照字面「接在現有計劃清單上」會擋設計階段的推送。
- 位置:〈範圍〉3。
- 引句:「接在 `_spec_gate_push_check` 現有的計劃清單上,只看風險高、計劃日期不早於生效日的計劃」
- 佐證:
  - `plans = _spec_gate_push_candidates(...)`(`scripts/lumos:17535`)包含範圍內任何狀態被碰到的計劃檔。
  - 預期值表那圈自己用 `_live`(doing,或 done 且被碰到)濾掉 todo(`:17243` 起、`:17290`)。
  - 這份計劃本身 `status: todo`。
- 補法:寫明和預期值表那道同樣只看 `_live`。
- 同圈的順序與重複:
  - 風險低全套那圈和風險高 near 那圈以門互斥,不重複。
  - 但 `_expected_gov` 現在讀 `("signoff","situation-rule")`,再多讀 `clause-kill` 會是整本治理帳的第三次全讀。建議併進同一個 tuple,共用 `ctx["exp_gov"]`。
  - 預期值表缺和 near 缺各自 `return 1`,規格閘會讓人分兩輪才改完。建議兩者併列印出。

## i5 `[near:]` 的取法:反引號裡的範例會被剝掉,含 `]` 的截斷偵測不到
severity: major
blocking: 是——照字面加 `near` 進 `INV_TAG_RE`,spec 自己的 S2、S10 就會被誤處理,「含 `]` 要擋」也寫不出來。
- 位置:〈用詞〉近似錯誤寫法、〈範圍〉1。
- 引句:「一行可以有多個;一句話至少 6 個實字、不得含 `]`(含了會讓標記截斷)」
- 引句:「讓 `_clause_body_of` 剝掉 `[near:…]`、條款雜湊與文法檢查不受它影響」
- 實測(把 `near` 加進 `INV_TAG_RE` 後呼叫 `_clause_body_of`,腳本在 `/tmp/lumos-seat-work/條款近似錯誤寫法要殺得掉/整合-sonnet/t1.py`):
  - S2 行 `當 \`[near:]\` 少於 6 個…或 \`[near:無 …]\` 的理由…` 變成 `當 \`[near:]\` 少於 6 個實字或 \`\` 的理由…`。反引號裡的範例被剝掉。
  - 取 `[near:]` 的程式若不遮反引號,S2 會被當成宣告了一個理由只有 1 個字的 `[near:無 …]`,自己判形狀不合。S10 同理,不過它是 `[manual:]` 豁免。
  - `[near:用 list[0] 取代 getOrNull,空清單會崩潰]` 變成正文剩 `取代 getOrNull,空清單會崩潰]`。標記被截斷,殘渣留在條款正文,雜湊與文法都悄悄變了,沒有任何錯誤。
  - 沒有哪一步能報「含 `]`」。〈預期值表〉S2 也沒有這一列,所以那條沒有可寫的測試。
- 補法:
  - 取 `[near:]` 用遮反引號的版本(`_clause_visible` 或 `_inline_visible_mask`,`scripts/lumos:403`),不能在原始行上直接用 `INV_TAG_RE`。
  - 另加殘渣偵測:遮完剝掉合法標記後,行內還有 `[near:` 或落單的 `]` 就判形狀不合。
  - 補 S2 一列:含 `]` → 形狀不合。
  - 範例裡的 `list[0]` 這類碼很常見,要在〈用詞〉講怎麼寫(例如改用全形括號)。
- 副作用:`INV_TAG_RE` 有 20 處用,包含 ★INVARIANT★ 合約行的指紋(`scripts/lumos:28238`)。`scripts/lumos:6038` 的註解還特別說「合約行不認它」。更安全的是只在 `_clause_body_of` 加一個條款專用的正規式。
- 自我適用:這份計劃的日期是 2026-11-13。若 `_NEAR_SINCE` 設成上線當天且 ≤ 這天,這份計劃自己就要有 `[near:]`,而 S2 的範例會讓它自己擋自己。要明寫生效日晚於這份計劃的日期,或讓這份計劃走 `[near:無 …]`。

## i6 壞法和 `[near:]` 句子脫鉤:`new` 不入帳,`--file` 不限制
severity: major
blocking: 是——照字面實作,證據可以由一條與近似寫法無關、甚至不是改實作的替換產生,後續審查也無從核對。
- 位置:〈範圍〉2、〈用詞〉有效紀錄。
- 引句:「--file <檔> --old <原文> --new <錯寫法> [--test <測試名>]」
- 問題:
  - 事件欄位有 `old`、`near_text`,沒有 `new`。殺傷力帳本也不存 `new`(`scripts/lumos:28040` 的欄位表沒有)。
  - 壞法在隔離工作樹跑完就丟,事後沒有任何東西能看出當時換了什麼。
  - 機器不檢查 `--new` 和 `[near:]` 那句話的關係。
  - `--file` 沒限制成正式碼。人裁的檔來自情境題段,這裡是自由輸入。
- 例:`--file` 指測試檔本身,`--old` 取一個斷言,`--new` 換成 `fail()`。測試紅在自己名字上,歸因過,判定 killed,紀錄有效。
- 這正是「繞過才算守衛」要先試的洞。spec 的天花板 1 與實務隱患第 1 條只講作者挑太容易殺的句子,沒講這個機器可擋的更低成本繞法。
- 補法:
  - 事件加 `new`(或它的雜湊),設計審與代碼審才核對得了。
  - `--file` 拒絕測試檔,判法用現成的 `_nodehome_is_test`(`scripts/lumos:17759` 前後的 `_is_code_file` 在用)。
  - RETIRE-IF 第一條「第一次就殺掉的比例」要有 `new` 才量得準。
- 次要:`[near:無 …]` 理由只驗 10 個實字,不驗內容,也沒有統計入口看「無」的占比。想在退場條件裡量,要另開一個計數。

## i7 `LUMOS_NEAR_SINCE` 沒寫測試總開關預設
severity: major
blocking: 是——照字面實作,既有規格閘與推送閘的高風險測試(`test_lumos.py` 3700+ 案例)在 `_NEAR_SINCE` 上線後可能整批翻紅。
- 位置:〈用詞〉生效日。
- 引句:「環境變數 `LUMOS_NEAR_SINCE` 供測試覆寫(同 `_expected_since` 的寫法)」
- 佐證:`_expected_since` 的做法不只是函式。`test_lumos.py:159` 有 `setdefault("LUMOS_HIGH_RISK_EVIDENCE_SINCE","9999-12-31")`,讓既有測試停在生效前。
- spec 只抄函式的寫法,沒說在測試總檔也設同樣預設,也沒提 `t_near_since_and_low_exempt` 要在自己的案例裡改回。
- 補法:寫明 `test_lumos.py:159` 旁邊加 `LUMOS_NEAR_SINCE` 的預設。

## i8 不論判定都入帳,取最新一筆會被暫時性失敗洗掉有效紀錄
severity: minor
blocking: 否——照字面實作不會錯,但會製造不必要的重跑,訊息也會誤導。
- 位置:〈範圍〉2「記」、S5。
- 引句:「不論判定,治理帳寫一筆 `clause-kill` 事件」
- 問題:
  - `cmd_guard_kill` 有七種結果。abort(基準不綠)、drifted(`old` 命中不是 1 次)、error、weak 都算「不是殺得掉」,spec 的 rc 1 對應它們。但 `cmd_guard_kill` 自己的優先序是 survived→1、drifted/abort/error→2(guard-kill 的 ★INVARIANT★ `t_guard_kill_rc_precedence`)。這兩個 rc 對不上時沒說誰為準。
  - 人裁那邊是只認「沒有弱證據的 killed」,其他一律 rc 2 且帳和計劃都不寫(`scripts/lumos:75913-75922`)。
  - 若 abort 也入帳,一次網路或環境造成的基準紅,就會變成「最新一筆」,蓋掉前面一筆好的紀錄。推送前被擋,必須再跑十幾分鐘 Gradle。
  - 擋下訊息「補測試讓它紅,或改寫這條近似錯誤寫法」只對 survived 對。對弱證據(run_cmd 沒有 `{method}`)和 drifted,正確的補法是改設定、改 `old`。
- 補法:只記 killed 和 survived(也可連同弱證據,但不蓋掉好紀錄);abort/drifted/error 走 rc 2 不入帳;訊息分流。

## i9 `clause-kill` 直接呼叫 `cmd_guard_kill`,漏了人裁那層的收尾與 import 零件
severity: minor
blocking: 否——實作者會發現,但 spec 描述不準。
- 位置:〈範圍〉2「跑」。
- 引句:「補 import 走人裁同一條 `also` 路徑」
- 佐證:前置分支 `/Users/enzo/harness/lumos-srl-android` 的 `_situation_rule_also(rr, sg, head, old, new, imports)` 要吃情境題段 `sg` 和 `_kt_sit_read_many`(`scripts/lumos:76242-76256`),不是通用零件。
- 通用的只有 `_situation_rule_imports_problem(src, new, imports)`。
- Ctrl-C/SIGTERM 收尾的 `_situation_rule_signals`、基準耗時提示、失敗摘錄的顯示都在 `_situation_rule_kill` 裡。spec 寫的是直接呼叫 `cmd_guard_kill(..., source="clause-kill")`,Gradle 十幾分鐘的中斷會漏掉這層。
- 補法:寫明是把 `_situation_rule_kill` 參數化(`source`、`note`、訊息),還是新寫一份並接 signals。
- `--old`/`--new` 以 `-` 開頭時 argparse 會當選項,要說明用 `--old=` 或在說明文件裡講。

## i10 「被推送版本」的來源與讀的倉庫沒講清楚
severity: minor
blocking: 否——是既有天花板的延伸,但這份把兩個來源混進同一個判定。
- 位置:〈用詞〉有效紀錄、〈範圍〉3。
- 引句:「`old` 在被推送版本(`git show <推送提交>:<file>`)的整份檔恰好出現一次」
- 問題:
  - `_spec_gate_push_check` 只拿到 `git_range` 字串,可能是 `a..b`、`a...b` 或單一版本,spec 沒說怎麼取右端。
  - 條款那一行(雜湊、`near_text`、`near_index`)讀的是工作目錄的計劃(預期值表那道的既有天花板),`old` 卻讀推送提交。同一個判定用兩個來源,工作目錄不等於被推的分支時就對不上。
  - `file` 是殺傷力工作樹裡的路徑(`_isolated_worktree(proot, ghead)`)。`git show` 要在哪個倉庫跑(`rr` 還是平台根 `proot`),spec 沒講。
- 補法:明寫右端怎麼取、`git -C` 哪個倉庫、與預期值表同樣的工作目錄天花板。

## i11 殺傷力帳本的讀者列舉不準
severity: minor
blocking: 否。
- 位置:〈範圍〉2。
- 引句:「讀殺傷力帳本、目前只跳過人裁那幾筆的讀者(`_backing_kill_rows`、doctor P2 等,實作時 grep `_SITUATION_RULE_SOURCE` 列全)一併跳過 `clause-kill`」
- 佐證:
  - grep 只有一個跳過點:`scripts/lumos:77028` 的 `_backing_kill_rows`。doctor P2 的 `_kill_log_latest` 在 `:26982` 也走它。
  - `cmd_gov` 的 `load(".kill-log.jsonl")`(`:18324`)完全不看 `source`。`clause-kill` 與人裁一樣會算進 `kill` 這一源的 verdict 史。人裁已是這樣,可以接受,但 spec 要明講「這個不跳」。
- 補法:跳過條件從 `== _SITUATION_RULE_SOURCE` 改成「`source` 非空」,下一種來源就不用再改一次。

## 實務隱患逐類
- 作者挑太容易殺的壞法或用「無」逃掉:見 i6,spec 只靠設計審,沒有計數入口。
- 暫時性失敗或環境:見 i8。
- 帳膨脹:`old`、`near_text` 沒有長度上限。`_gate_event` 的 4096 位元組是政策值(`_gate_event_fit`),人裁沒存 `old`。一條很長的 `old` 讓治理帳一行長很多。建議存雜湊加長度,或套 `_gate_event_fit`。
- 效能:每個 `[near:]` 各跑一次基準加壞法,Gradle 十幾分鐘。高風險計劃 8 條條款、每條 1–2 個,就是數小時的串行等待。spec 的「推送前不重跑」是對的,但沒提作者端的成本,也沒給批次入口。
- 跨平台、併發、外部輸入:併發已在 spec 排除。外部輸入只剩 i9 的 `-` 開頭參數。
- 回退:`_NEAR_SINCE` 設遠未來是有效回退,但 i7 的測試預設要一起補。

## 固定席逐條判
- `Systems/guard-kill` 的 ★INVARIANT★「guard kill rc 優先序」:不影響。`source` 只影響殺傷力帳本那筆的欄位,`rc` 的判定在 `:28060` 之後仍由 `verdicts` 決定。i8 講的是 `clause-kill` 自己的 rc 對照,不是 `cmd_guard_kill`。
- `Systems/guard-kill` 的 ★INVARIANT★「`--json` 成功時 stdout 恰一行 JSON」:不影響。`clause-kill` 不走 `as_json`,`source` 參數不改輸出。
- `Systems/規格閘`:沒有掛合約,所以沒有被破壞的合約行。但它的 KEY 行談風險高只印不擋(`cmd_spec_gate` 說明);預期值表那道已有擋下先例,near 這道照辦不衝突。

## 已讀無 finding
- 〈白話〉、〈舊否決比對〉(三條引用都存在,d1、「另抽共用」、「2026-12-15」都核對過)、〈不做〉、〈回退〉、〈天花板〉。
- 〈依據來源〉、〈驗收條款〉S1–S10 的編號與預期值表各列的條款欄對得上。

最嚴重:major;blocking 共 7 條
