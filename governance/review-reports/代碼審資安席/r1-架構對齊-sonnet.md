severity: major

## 三問總答(架構對齊鏡頭)

**①分層與依賴方向**:`_disposal_security_step` 若照 `_disposal_clause_step` 的樣子寫(獨立函式、由 `_loop_status_disposal` 直接呼叫、回 fail/ok/skip、自己印一行),呼叫方向與既有第五步一致,沒有跨層直呼問題(file: `scripts/lumos:14829-14830`)。但這一步要判「某個具名席位有沒有出席」——這件事現有唯一負責的元件是 `_roster_observe`/`_TIER_ROSTER`,而它明文只做觀測、不進 disposal 的 rc(file: `scripts/lumos:7817`)。[S2] 讓它直接參與 rc 判定,等於在既有的「席位觀測層」與「處置閘阻擋層」之間新開一條路,細節見 D1。

**②命名與訊息**:函式名、`[disposal]` 前綴、生效日常數命名與比法(`_loop_ts_key`)都照抄 `_disposal_clause_step`/`_CLAUSE_GATE_SINCE`,風格一致,沒問題。但成立時的成功訊息格式跟鄰居五步不同,見 D3。

**③第二種做法**:核心是 D1(用阻擋取代觀測處理席位出席,本庫首例);次要是 D2(已寫入圖譜的 d6 決策用了計劃自己禁止的稱呼)。

## 逐節

- frontmatter/summary、緣起、人裁:已讀,無 finding(政策取捨/事實陳述不在本鏡頭)。
- PRIOR-ART:已讀,無 finding——「不新增指令、不動 code-loop pass 介面」查證屬實,`_codeloop_guard_verdict`(`scripts/lumos:22901` 起)全函式不引用 `_TIER_ROSTER`/`_roster_observe`/`_roster_family` 任一個。
- [S1]:已讀,無 finding——`_rseat("資安","claude",False,"required",...)` 的形狀跟同表 `_rseat("架構對齊","claude",False,"required",...)`(`scripts/lumos:7632`)逐欄一致,是既有 `_rseat` 慣例的正常延伸。
- [S2]:見 D1(major)、D3(minor)。
- [S3]:已讀,無 finding——`_SECURITY_SEAT_SINCE` 命名與比法照抄 `_CLAUSE_GATE_SINCE`(`scripts/lumos:4388-4389`),沒有第二種寫法。
- [S4]:已讀,無 finding——§7.8 與「§7.7 立場表加一列」的做法,跟 2026-08-22 架構對齊席掛進 §7.6/§7.7 的先例一致(`skills/lumos-design-loop/templates.md:253,285,300`:架構對齊本身也是「不佔 W 但在立場表佔一列、指回自己的專屬模板」)。
- [S5]:已讀,無 finding——列的交叉引用逐一存在且真的提到「架構對齊」:`skills/lumos-project-notes/commands/06-代碼審與推送.md:5`、`skills/lumos-code-loop/SKILL.md:20,29`、`skills/lumos-code-loop/reference.md:86,106,283`、`skills/lumos-design-loop/SKILL.md:20`。
- [S6]:見 D2(minor)。
- 邊界與不做、承認的限制、實務隱患、驗收:已讀,無 finding(併發/效能/資源三類排除理由、REVISIT 格式、測試命名等不在分層/命名/第二做法這把鏡頭內)。

## 固定席節點逐條判

- **Systems/pitfalls-code-loop**:不影響其宣稱的整體行為(既有 `pitfalls --diff`/code-loop skill 流程不動),但節點裡已寫入的 d6 決策文字跟本計劃自己的用詞規定衝突,見 D2。
- **Systems/hook信任邊界**:不影響——本案不碰 hook 解析順序、複製清單或錨點清單,新增的是處置閘一步與編制表一項,程式路徑跟 hook 系列完全不相交。
- **Systems/arch-alignment-lens**:不影響其宣稱的行為(架構對齊席本身的 required/不佔 W/§7.6 內容都沒被動),但兩席共用同一張表、同一個 `requirement="required"` 值,今後卻一個仍是觀測、一個變成阻擋——即 D1 指出的不一致,值得跟這個節點的維護者對一下。
- **Projects/roster對帳併入問閘_計劃**(直接連結):有張力——該節點 [邊界] 明文「PASS/FAIL 布林零改動」,是本庫對「席位夠不夠格能不能阻擋收斂」唯一的先例;[S2] 是第一個讓具名席位出席與否直接決定 rc 的設計,詳見 D1。

## D1

severity: major
blocking: 是
判準:不改的話,實作者會把「架構對齊」「外家finder/外家否決」這些標了 required/required-fail-closed 卻從不阻擋的先例,誤讀成「有 required 標籤的席位都可以自由選擇要不要變成阻擋」,寫出一個跟既有編制表語意衝突、以後每加一席都要重新吵一次「這席要不要阻擋」的模式。
引句:「要求帳裡至少一筆資安席帳列且留痕對得上」
file: `scripts/lumos:7629-7630` `_rseat("外家finder","external",True,"required-fail-closed")` 與 `_rseat("外家否決","external",False,"required-fail-closed")`——標籤字面比單純的「required」更強(fail-closed),但從未讓 disposal gate 的 rc 因此改變。
file: `scripts/lumos:7817` 註解明講:「此席編制為 fail-closed(本行僅轉述編制對照,不裁決;處置見 code-loop skill)」——本庫對「席位夠不夠格」的既定立場是轉述、不裁決。
file: `docs/lumos-toolchain-knowledge/Projects/roster對帳併入問閘_計劃.md:29`「邊界:編制表/lens 值域/--panel/--light 不動;PASS/FAIL 布林零改動。」——2026-08-26 定案時明文劃的界。
file: `scripts/lumos:7632` `_rseat("架構對齊","claude",False,"required",...)`——同一張表裡,標籤跟本案 [S1] 要加的「資安」座位完全一樣(claude/不佔W/required),但架構對齊席至今從未讓 disposal 的 rc 因它缺席而變 1。
[S2] 讓「這個迴圈有沒有一輪派了資安席」直接決定退出碼 1/0,是本庫第一次把「席位出席」升級成阻擋型判準,取代了 `_roster_observe` 既有的觀測型做法——這正是引入第二種做法。

## D2

severity: minor
blocking: 否
判準:不算的話,下一個讀 pitfalls-code-loop 節點的人會把「處置閘第五條」對應到資安席而不是條款綁定,兩邊對不上時要多花一次查證才能對齊,但不影響任何機械判定。
引句:「不叫「第五條」——處置閘的「第五步」已經是條款綁定」
file: `docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md:35` summary KEY 行寫「處置閘第五條合取」。
file: `docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md:71` d6 決策 content 也寫「機械擋=處置閘第五條合取」。
兩處都是本計劃 S6 聲稱「2026-09-11 已做」的既有圖譜文字,不是假設情境,且跟計劃自己在 [S2] 明令的稱呼直接衝突。

## D3

severity: minor
blocking: 否
判準:不改的話,`_disposal_security_step` 印出的成功行會跟既有五步(G3/處置集合/留痕/quote-check/條款綁定)的格式不一致,讀 disposal 輸出的人要多認一種格式。
引句:「資安席:✓ 第幾輪、哪一席」
file: `scripts/lumos:14969,15028,15088,14894` 分別是 G3/處置集合/留痕/條款綁定四步的成功印出,格式固定為 `[disposal] <標籤>: ✓ — <說明>`(前綴+冒號+符號+破折號)。spec 給的成功訊息範例缺少 `[disposal]` 前綴與「— 」分隔,若照抄實作會跟鄰居長得不一樣。

## 總結

最嚴重 severity 是 major(D1);blocking 共 1 條(D1)。
