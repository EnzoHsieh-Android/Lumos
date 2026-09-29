severity: major

# r1 整合/知識同步鏡頭審查報告(代碼審前後端角色鏡頭_計劃)

範圍說明:對照 worktree /Users/enzo/harness/lumos-toolchain/.claude/worktrees/fe-be-lens 逐節讀完 spec。交叉引用核對:[[Projects/代碼審資料狀態鏡頭_計劃]]、[[Projects/派工鏡頭注入_計劃]]、[[Projects/前端框架從vue分出_計劃]]、[[Systems/棧別提問表態閘]]、[[Systems/效能檢核目錄]]、Systems/design-loop、Systems/pitfalls-code-loop、Systems/codex-harness 目標檔都存在,無壞引用。固定席節點:派工時未附,無可逐條判;自行查了 派工鏡頭注入_計劃 的消毒原則(見 F9)。

## F1 角色卡機械附到「每一席」,與同型前案的分席規矩和本案「不改席位編制」互相打架
severity: major
blocking: 是
判準:不改,實作者會把前端/後端卡塞進架構對齊席與辯方類席位,做出稀釋差異化的壞系統。
- spec 段落:要做什麼第 3 點、不做。
引句:「代碼審的兩條派工通道(Claude 派工詞有圖譜鏡頭那行、Codex 派子代理那一刻領取)都附;設計審那條不附。」
引句:「不做閘、不改風險分級規則、不改席位編制(全端改動也不拆成前端席和後端席)。」
- 問題:附掛條件只是「派工詞有 `LUMOS-IMPACT:` 那行」,不是「正確性席」。但該標記不只出現在 §3 審查員;架構對齊席範本 §7.6 也要求「原樣留一行 `LUMOS-IMPACT:`」,且風險 light 檔只派一席架構對齊(SKILL 第 12 行)。走一遍:只改 `web/App.vue` 的 light 推送 → 只派架構對齊席(範本明寫「不找 bug」)→ hook 依標記照附前端卡(狀態競態、無障礙、資安,全是找 bug 題)→ 席位被帶離本職。同型前案已明確立了相反規矩,spec 對此一字未提、也沒說本案是否比照。
- 佐證:
  - file: `skills/lumos-design-loop/templates.md:362` 寫「代碼審多席:§3 第 1 點的資料狀態五問…只留給正確性/邏輯席,其他席派工時從第 1 點刪掉…不然每席都做同一份題,差異化被稀釋」。
  - file: `skills/lumos-design-loop/templates.md:266` 架構對齊席範本含 `LUMOS-IMPACT:` 標記。
  - file: `scripts/hooks/claude/dispatch-lens-hook.py:191` `main()` 只以 `find_marker(prompt)` 判斷是否處理,完全不分席。
  - file: `skills/lumos-code-loop/SKILL.md:12` light 只派一席架構對齊。
  - Spec「實務隱患」自己寫「注意力稀釋…只附改動真的碰到的那張卡」,只擋了「卡的多寡」,沒擋「席位錯配」。

## F2 「角色卡另走一次快速計算、不共用預算」與 hook 現有預算機制、薄殼規則、介面全都對不上,且介面未定義
severity: major
blocking: 是
判準:不改,實作者會因無現成預算可切而讓 S5 在真正超時情境下永遠失敗,或把 hook 改成違反薄殼規則。
- spec 段落:要做什麼第 3 點(子項一)、驗收 S5、回退、實務隱患「派工附段有時間預算」。
引句:「角色卡另走一次快速計算,只看改動檔清單、檔案匯入與 package.json,不跟圖譜那段共用預算與快取;圖譜那段超時或算出空白時,角色卡照附。」
- 問題:
  1. 未定義:算卡的入口(新子命令?`dispatch-lens` 的新旗標?)、回傳形狀、hook 呼叫順序(先於或後於圖譜那次)、「快速」的具體秒數。要做什麼清單裡也沒有一條寫「改 hook 主流程」,只在回退節以括號帶過「掛鉤檔改回後要重核可指紋」。
  2. 預算對不上:hook 唯一的預算工具 `_inner_budget` 回傳的是「剩餘時間」而非「每段配額」(註解明寫),下限 1 秒。走一遍:圖譜那段超時(rc5)時外層 subprocess 已用到約 `min(_dl+5, 54)` 秒(天花板 60),此時再呼叫算卡,`_inner_budget` 只給 `max(1.0, 42-已耗)`=1 秒;起一個 python 行程就要約 0.4–0.5 秒(hook 內註解實測),對稍大的 monorepo 讀 package.json 與匯入就會超,即 S5 想保護的那個情境剛好被丟掉。要不共用只能另訂配額,但那會讓 hook 總耗時可能逼近外層 60 秒天花板,違反 hook 內「內層一律從外層天花板算」的守衛。
  3. 現有 hook 超時路徑:`r is None or r.returncode == 5` 分支只 `_emit_updated(TIMEOUT_NOTE)` 後 `return 0`;`text` 空時直接 `return 0` 不注入。S5「超時/空白仍含卡」需要重寫這兩條分支,spec 沒點到。
- 佐證:
  - file: `scripts/hooks/claude/dispatch-lens-hook.py:117` `_inner_budget`(`max(_BUDGET_FLOOR, ...)`,docstring「這是還剩多少不是每段配額」)。
  - file: `scripts/hooks/claude/dispatch-lens-hook.py:300` `_cap/_dl/_run_tmo` 計算與 `:308` 超時分支只附 note;`:337` 空 text 直接 return。
  - file: `scripts/test_lumos.py:36068` 既有 hook 超時測試用單一 `patch subprocess.run` 對所有呼叫回 rc5、另一處 fake_run 對所有呼叫回同一份 JSON;hook 多一次 subprocess 呼叫後這兩個既有測試的假設(只有一次呼叫)會失真,spec 的測試清單沒列要改它們。

## F3 圖譜那段「失敗」(非超時、非空白)時角色卡全丟;Codex 武裝路徑更是在算卡之前就整個放棄
severity: major
blocking: 是
判準:不改,實作者做出的系統在無圖譜的消費專案、base 不在主線等情境永遠附不到卡,與「消費專案拿得到」的定位矛盾。
- spec 段落:要做什麼第 2、3 點;驗收 S5、S6。
引句:「當圖譜那段超時或算出空白,派工附段應仍含角色卡」
- 問題:S5 只涵蓋「超時」與「空白」。實際還有 rc≠0 的失敗:走一遍——消費專案沒有 `docs/*-knowledge`(尚未建圖譜)→ `cmd_dispatch_lens` 印「擋下:base 樹裡沒有 docs/*-knowledge」回 rc=3 → hook 走 `r.returncode != 0` 分支「放行」什麼都不附;base 不在主線得 rc=4、範圍不合法得 rc=2,同理。角色卡完全不需要圖譜,卻因為搭在圖譜呼叫的成敗上而消失。Codex 路徑更嚴重:`cmd_dispatch_lens_arm` 呼叫 `cmd_dispatch_lens` 後 `if rc != 0: return rc`,根本不武裝,SubagentStart 領不到任何東西,卡也就沒有載體;spec 也沒說卡是在 arm 時算好存進 meta,還是在 claim 時算(claim 只有 cwd,沒有範圍以外資訊),S6 只寫「領取的附加內容應含」。
- 佐證:
  - file: `scripts/lumos:31336` 與附近 `擋下:base 樹裡沒有 docs/*-knowledge`(return 3)。
  - file: `scripts/lumos:30988` `if rc != 0: return rc`(arm 在算圖譜失敗時不寫 armed 檔)。
  - file: `scripts/hooks/claude/dispatch-lens-hook.py:331` `if r.returncode != 0: ... return 0`。
  - file: `scripts/lumos:31065` claim 只回 `meta.get("text")`,無獨立卡欄位。

## F4 專案宣告的路徑對照只改角色卡,棧別題組與慣例 skill 仍走舊判定,同一支檔會同時拿到互相矛盾的指引;「出路」宣稱不成立
severity: minor
blocking: 否
判準:不改,實作者會做出「宣告了 web/** 是前端、卻仍印 node-idioms 與後端效能題」的分叉判定,但不致壞掉。
- spec 段落:現況、已知限制、要做什麼第 1 點。
引句:「空殼 package.json 會讓底下的前端 .ts 判成後端;出路是在 `.lumos/config.json` 宣告路徑對照。」
- 問題:本案新增第二套前後端判定(a)–(d),但 `_node_flavor`、`_stack_key_for_file`、`_idiom_skill_for` 三個既有消費者完全不讀宣告。走一遍:monorepo 空殼 package.json、`apps/web/x.ts` 宣告前端 → 角色卡附前端卡;同一份 `pitfalls --diff` 輸出裡「慣例 skill」印 node-idioms、棧別檢核題印 node 題(範本 §7.6 還寫「.ts/.js 看 package.json 分前後端」)。「出路是宣告」只修了角色卡那一條,spec 沒說要不要讓三個既有消費者也吃宣告,也沒說兩套判定不一致時的取捨;驗收 S1–S3 只測新函式。
- 佐證:
  - file: `scripts/lumos:20448` `_node_flavor`(只看最近 package.json,無設定入口)。
  - file: `scripts/lumos:20488` `_stack_key_for_file`、`scripts/lumos:26921` `_idiom_skill_for` 各自呼叫 `_node_flavor`。
  - file: `skills/lumos-design-loop/templates.md:262` 架構對齊席範本「.ts/.js 看 package.json 分前後端」。

## F5 判定所讀的「哪棵樹」未定義:刪除檔、整包被刪的 package.json、設定檔、匯入內容各有不同讀法,既有程式只讀工作樹
severity: minor
blocking: 否
判準:不改,實作者會沿用只讀工作樹的 `_node_flavor`,讓刪除檔與整包移除的前端判成「判不出」。
- spec 段落:要做什麼第 1 點(b)(d)。
引句:「不看改動行、不受改動行數門檻影響;刪掉的檔看改動前的版本。」
- 問題:spec 只為手機匯入補了「刪掉的檔看改動前版本」,(d) 的 package.json 與 (a) 的設定檔沒有對應規定。走一遍:分支刪掉整個 `web/`(含其 package.json)→ 被刪的 `web/src/a.ts` 在工作樹已不存在,`_node_flavor` 讀工作樹找不到 package.json → 回 None → 判不出,不附前端卡,而這正是最該附卡的「拆前端」改動。另 `dispatch-lens` 本身的原則是只信 base 樹(「圖譜根從 base 樹解析…分支加一個空目錄就能熄燈」),角色判定若讀被審分支的工作樹 `.lumos/config.json`,被審分支可自行改宣告把卡關掉或換卡;讀 base 則新增宣告的那一次分支不生效。spec 沒選。另:pre-push 熱路徑(註解實測 0.18 秒、逐 ref 跑)若對每個刪除的 .kt/.java/.swift/.dart 各做一次 `git show <base>:<path>`,沒有上限,S8 那行的成本未評。
- 佐證:
  - file: `scripts/lumos:20455` `_node_flavor` 以 `Path(repo_root)/file_rel` 讀工作樹。
  - file: `scripts/lumos:31313` 至 `:31330` 派工鏡頭以 base 樹為信任來源的實作。
  - file: `scripts/lumos:27417` 附近註解「本函式在 pre-push 熱路徑上逐 ref 跑」。

## F6 「前端 N 支、後端 M 支、判不出 K 支」與「只附碰到的卡」沒定義計數母體(測試檔、文件、鎖檔、產生檔算不算)
severity: minor
blocking: 否
判準:不改,實作者會各自決定母體,導致 K 被 .md/.json 灌水、或純測試/文件改動誤附卡。
- spec 段落:要做什麼第 3 點(全端兩張都附、全部判不出不附)、第 4 點、S2、S8。
引句:「只印在給人看的輸出、不進 JSON、不是檢核題,不改變分級。」
- 問題:S2 明定 `.md` 判「判不出」,所以文件一併計入時,一份純文件推送(pre-push 文件子集)也會印「前端 0、後端 0、判不出 N」;反之若 .test.ts、`*.spec.tsx` 也判前端,純測試改動會附整張前端卡。`pitfalls --diff` 現有母體已排除測試檔與非代碼檔(`_stack_applicability` 註解「呼叫端已排除測試檔與非代碼檔」),spec 沒說沿用。無副檔名的主程式(例如本 repo 的 `scripts/lumos`)、`.sh`、`.json`、`.yml` 全落到判不出,計數行對這類專案幾乎不含資訊。
- 佐證:
  - file: `scripts/lumos:20548` `_stack_applicability` docstring(母體排除測試與非代碼檔)。
  - file: `scripts/hooks/pre-push:259` 與 `:271` `:343` 該文字輸出被 `sed` 縮排後直接印給人,無下游解析(不擋,但會在每次推送都多一行)。

## F7 要同步的鏡像處清單不全:只列範本第 3 節,漏了 skill、reference、指令速查、§7 panel、hook 安裝副本與既有測試
severity: minor
blocking: 否
判準:不改,實作者做完後這些說明處會與新行為脫節(前案剛立過同型 doc-sync 守衛,可見這類漂移是慣常敗因)。
- spec 段落:要做什麼第 2 點、回退、lands_in。
引句:「派工範本第 3 節審查鏡頭加第 5 點」
- 問題與佐證(每一處三個月後接手者會撞到的):
  - file: `skills/lumos-code-loop/SKILL.md:29` 步驟 2 的「圖譜鏡頭」段是描述 hook 附加內容的地方,新增的自動附加卡沒地方指路;前案已用 `t_data_state_lens_doc_sync`④ 釘「步驟 2 指到資料狀態」,本案 spec 的 S7 只釘卡片單源,沒釘這一處。
  - file: `skills/lumos-code-loop/reference.md:74` refute framing 寫「完整鏡頭以範本第 3 節為準」,歷史區另有一份複本,本案沒說哪份要動(前案已有「歷史區不得補新子題」守衛,需確認新第 5 點不會被誤判)。
  - file: `skills/lumos-design-loop/templates.md:96` §3 ④ 與 `:362` §7 panel:前案在 §7 立分流句,本案沒表態(見 F1)。
  - file: `skills/lumos-project-notes/reference.md:83` 與 `skills/lumos-project-notes/commands/06-代碼審與推送.md:25` 描述 dispatch-lens 行為(Claude hook 自動叫、Codex arm),新增附加內容無處記載。
  - file: `install.sh`/`scripts/lumos:18064` hook 是 `shutil.copy2` 複製進 `~/.claude/hooks`,不是 symlink;卡片單源在 lumos 本體(消費端隨 lumos 更新),但 hook 副本要重跑 install 才更新。版本錯位有兩向:新 lumos + 舊 hook = 卡永遠不附(靜默);新 hook + 舊 lumos = 呼叫未知旗標得非 0,若 hook 沒有 fail-open 分支會被當失敗。spec「消費專案拿得到」只講了單源位置,沒講這條。
  - file: `docs/lumos-toolchain-knowledge/Systems/hook逾時預算.md`(存在,單源說明預算規則)未出現在 lands_in 或 related,但 F2 的改動正是動它管的規則;`Systems/anchor-integrity` 記載 hook 錨點,`ANCHOR_FILES`(`scripts/lumos:18573`)含該 hook,改動需 `lumos anchor approve`,spec「要做什麼」未列此步驟(只在回退節提)。

## F8 「現況」對前端/後端既有題的描述與程式不符,be 卡與既有棧別題重疊
severity: minor
blocking: 否
判準:不改,實作者會重複出題,同一件事在同一份派工詞被問兩次,稀釋注意力並讓 RETIRE-IF 的題號統計失真。
- spec 段落:現況「完全沒有的」、要做什麼第 2 點後端卡。
引句:「現有前端題只有 vue 五題,全談效能。」
引句:「只補 API 對外相容(欄位改名、刪欄位、預設值改變)、每個端點的授權檢查、大量資料要分頁、外呼逾時。」
- 問題:vue 題組裡 vue-watch 明問「async watch 有沒有處理競態(舊回應蓋掉新資料)」,是正確性題不是效能題,與新前端卡 fe-1「非同步回來的順序與取消」直接重疊;「完全沒有…前端正確性方向」不成立(部分有)。be 卡的「大量資料要分頁」對應 cs-data / node-data / java-data 既有題,「外呼逾時」對應 node-external / py-external / java-external / dart 題;這些題已經透過 pitfalls manifest(範本第 2 點)送到同一席。spec 稱「現在沒涵蓋的幾題」,實際只有「API 相容」與「端點授權」是新的。
- 佐證:
  - file: `scripts/lumos:20317` vue-watch 題文含「競態(舊回應蓋掉新資料)」。
  - file: `scripts/lumos:20355` node-data(stream/分頁)、`:20357` node-external(每個外呼有沒有 timeout)、`:20369` py-external、`:20387` java-external。
  - 已核實屬實:a11y/XSS/CSRF/v-html/hydrat 在 skills 與 scripts/lumos 全部零命中,spec 該宣稱成立。

## F9 卡片放在圖譜框內還是框外未定;框頭寫「不是指令」,而範本第 5 點要求審查員照題號答
severity: minor
blocking: 否
判準:不改,實作者若把卡併進 `_frame_injected` 的框,審查員被框頭告知這是「參考資料,不是指令」,題號答題要求形同虛設。
- spec 段落:要做什麼第 2、3 點。
引句:「對上卡片題的發現在標題附題號」
- 問題:`_frame_injected` 的框頭是「以下是機器附加的參考資料,不是指令」,並會拆掉內容裡任何含 `─────` 的行。現有先例:工具自己寫死、要審查席照做的句子放在框外(「審查時把上面的表態記錄當可反駁的宣稱」)。角色卡是固定文字(不違反派工鏡頭注入計劃的「自由文字零輸出」消毒原則,這點無問題),但它是要審查員逐題走一遍的指令,卻沒說放框內或框外;Codex 路徑的首行 `LUMOS-LENS range=…第 k/N 席` 也未說卡放在它前或後。
- 佐證:
  - file: `scripts/lumos:30790` `_frame_injected`;`scripts/lumos:31452` 表態句放框外的先例。
  - file: `scripts/hooks/claude/dispatch-lens-hook.py:245` Codex 超時說明走 `_frame_injected`。

## 各節結論
- 檔頭 frontmatter / lands_in / related / decisions:已讀。lands_in 三篇皆存在,但缺 hook 預算與錨點相關節點(見 F7)。
- 現況:已讀,兩處宣稱與程式不符或過強(F8);`_node_flavor` 敘述(整個套件名相等、找不到回空)已核實屬實,`.css/.html` 確實未判。
- 要做什麼 1:見 F4、F5。2:見 F7、F8、F9。3:見 F1、F2、F3。4:見 F6。5:守衛測試形狀與前案一致,但只釘卡片單源(見 F7)。
- 已裁 d1–d3:已讀,無 finding(與要做什麼不矛盾)。
- 已知限制:已讀,「出路」宣稱見 F4。
- 驗收條款 S1–S9:已讀;S4/S5/S6 各自對得上要做什麼第 3 點,但 S5 只涵蓋超時與空白(F3),S8 未定母體(F6),S9 手動實驗有寫明無樣本時的處理,無 finding。
- 回退:已讀;漏列 F7 的 doc 鏡像與 install 副本同步。
- 實務隱患(併發、效能、回滾、消費專案):
  - 併發:無。角色判定純函式、只讀檔;Codex 武裝檔的原子領取機制未動(卡若存 meta 則沿用同一份)。
  - 效能:有,見 F2(hook 預算)與 F5(pre-push 熱路徑逐刪除檔 git show)。
  - 回滾:spec 寫了回退;但 hook 已被複製進消費端 `~/.claude/hooks`,回滾要對方重跑 install(F7)。
  - 消費專案:有,見 F3(無圖譜的專案附不到)與 F7(新舊版本錯位)。
- 不做:已讀,「不改席位編制」與 F1 的機械附掛有張力。

最嚴重 severity 是 major;blocking 共 3 條(F1、F2、F3)。
