severity: major

**Q1 分層與依賴方向**

severity: major
blocking: 是
引句:「規格閘直接讀〈待決問題〉(不呼叫 pitfalls)」
〈待決問題〉有三個消費者:規格閘擋法、lint 規則、`pitfalls --stage` 列未結題。計劃稿只說規格閘「直接讀」,沒指定三處共用一支解析函式。repo 的既有做法是共用一支:
- 條款由 `clause_bindings` 解析一次,`_clause_check` 同時給規格閘和處置閘用。file: `scripts/lumos:7323`
- lint 側直接呼叫同一支解析,不另寫:`_ns_clause_rows`。file: `scripts/lumos:32688`
- 程式註解明講「別各寫一份」。file: `scripts/lumos:15965`、`scripts/lumos:7740`

多一層限制:`cmd_pitfalls` 沒有 env,是 vault-free。file: `scripts/lumos:42832`。所以共用解析必須是只吃文字的純函式。「已決指到存在且 valid:true 的決策」這項檢查要查 `env.notes`,只能放在規格閘和 lint,不能放進解析函式,也不能放進 pitfalls。

我判 major 是因為計劃稿沒禁止、也沒指定,實作時各寫一份解析器的風險很高。⚠ 如果計劃稿在別處已指定共用解析函式,可降為 minor。

**Q2 命名與錯誤處理**

severity: minor
blocking: 否
引句:「lint:每行照上面的文法與」
計劃稿寫 lint「報錯」,S2 也寫「逐條報錯」,但沒說這條規則掛在哪。repo 對新的 lint 規則有固定做法:新規則進 `_lint_new_rules` 的 `_nl_rule_*`,擋不擋看 `note_lint.gate` 開關,沒設就是 warn。`_lint_collect` 才是無條件擋的原有規則。
- file: `scripts/lumos:6840`、`scripts/lumos:6541`
- 開關慣例見 `docs/lumos-toolchain-knowledge/Systems/lumos-cli-read.md:22`

兩種掛法行為不同,S2 要在預設設定下驗的「報錯」就會不一樣。這條規則該走哪一條,計劃稿要寫明。

severity: minor
blocking: 否
引句:「新增 `--stage <階段>`,只列那一階段的風險面與那一階段還沒結的題」
`--stage` 給了未知值,或和 `--diff` 並用時,計劃稿沒寫處理方式。repo 的查詢指令慣例是 usage error 回 rc 2。file: `scripts/lumos:42853`(`--diff` 以 `-` 開頭的擋法註解)。S3 只測排序和不帶旗標時的輸出,沒測這個失敗路徑。⚠ 只是沒寫,不是做法不同。

**Q3 第二種做法**

`_REQUIREMENT_FACETS` 多一個 `stage` 鍵,不算第二種做法:`id`、`q`、`when` 的形狀和 `_STACK_QUESTION_SPECS` 相同。file: `scripts/lumos:26516`。分開放也合理:`_STACK_TRIGGERS` 是載入時編譯、比對 diff 行,facets 比對計劃筆記文字。file: `scripts/lumos:26679`。計劃稿沒提 facets 的 `when` 也要載入時編譯。這點很小,我不另列一條。

規格閘的擋法有一處描述與現況不符:

severity: minor
blocking: 否
引句:「規格閘(風險高低兩種門都適用,這是現行風險高」
風險高「只印不擋」只指紅綠測試結果。條款綁定和句式在風險高時本來就擋,`_spec_gate_clause_part` 失敗時回 rc 1,和門的高低無關。file: `scripts/lumos:7552`、`scripts/lumos:7800`(docstring)。所以「風險高也擋」不是新種類的擋法。結構上該做成 `_spec_gate_front` 裡的前置步驟,像 `_spec_gate_clause_part` 那樣印出原因再回 rc,不要加在 `cmd_spec_gate` 後段。計劃稿的敘述改一下,也避免實作者誤以為要開新分支。

**Q4 落點**

四個落點都對得上:
- `scripts/lumos` 同時是 `Systems/規格閘`、`Systems/pitfalls-code-loop`、`Systems/效能檢核目錄` 的 about_code。
- 新開的 `Systems/情境出題` 沒有自己的檔,新開時要用 `lumos new system --code scripts/lumos`。這是既有的共用家做法,有 48 個節點同樣把 `scripts/lumos` 列在 about_code。
- lint 規則沒有專屬的家,落在規格閘或 lint 相關節點都可以,不算偏離。

總結:不對齊共 3 條,其中 major 1 條

(以上共 4 條 finding:1 major、3 minor。Q3 的 minor 計入。)

修正總結行:總結:不對齊共 4 條,其中 major 1 條
