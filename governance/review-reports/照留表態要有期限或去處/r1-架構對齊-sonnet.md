severity: major

# 架構對齊審查:照留表態要有期限或去處_計劃(r1)

## 問 1 分層與依賴方向
計劃把「算失效」放進 `_drift_load_acks`(讀完表態順手替每筆算 dead),比對函式 `_drift_split_acked` 只看 dead 字串。鄰居的分法不同:`_drift_load_acks` 只讀表態檔、過濾 path 與 kind,不碰任何筆記(`scripts/lumos:34353-34365`);「表態算不算數」全在 `_drift_split_acked` 比對時算(related/seq 走 `_drift_bound_latest`,`scripts/lumos:34372-34412`、`34437-34443`)。把讀節點(where=None 讀磁碟、有 where 走 `_drift_cat`)塞進載入函式,是讓「讀表態檔」的函式多出讀筆記狀態的依賴,該函式有 5 個以上呼叫點(`scripts/lumos:35668`、`35742`、`36672`、`36739`、`36801`),不論該處用不用得到都要付讀節點的成本。算在載入時的理由計劃有寫(只讀一次),但跟鄰居的分層不同,見 F2。另外 dead_ack 帶回發現的做法跟 `prev_ack` 同形(`scripts/lumos:34403`、`34451`),這一點對齊。

## 問 2 命名與錯誤處理
- 常數:鄰居叫 `_DRIFT_BOUND_KINDS`(`scripts/lumos:32259`),計劃叫 `_DRIFT_ACK_ROUTED`,同一件事(哪幾種表態要綁東西)兩個名字;minor,見 F3。
- 擋下訊息「擋下:…」+ rc2、`env.find` 解析、`_drift_ack_args_err` 擴參數,跟 `cmd_drift_ack` 現況一致(`scripts/lumos:34531-34545`、`34474`),對齊。
- 今天的日期:鄰居慣例有兩種,多數直接 `date.today()`,可測的函式用 `today = today or _dt.date.today()` 參數注入(`scripts/lumos:4104`)。計劃寫「今天(本機日期)」,沒說測試怎麼固定日期;S2/S3 的期限測試需要。未寫就是沒對到注入慣例,歸入 F3。
- 時區隱患計劃自己寫了(接受);與鄰居 REVISIT 到期(`scripts/lumos:2618`)同為本機日期,一致。

## 問 3 第二種做法
有,兩處:
1. 「筆記收尾了沒」的狀態集合:專案已有 `_DRIFT_OPEN_ISSUE = ("open","doing")`(`scripts/lumos:32231`)、`_DRIFT_CLOSED = ("done","superseded")`(`32230`)、`_DRIFT_SETTLED`(`32234`,註解明寫「不另寫一份」)、`_ISSUE_CLOSED_STATUSES`(`16860`)。計劃另造 `_DRIFT_ACK_ROUTE_OPEN = {"issue": ("open","doing"), "project": ("todo","doing")}`,Issue 那格是 `_DRIFT_OPEN_ISSUE` 的複本,而且改用「開著值」白名單、既有慣例是判「結案值」(`scripts/lumos:2631`、`32890`)。計劃的 PRIOR-ART 說沿用不另造第三種失效機制,但狀態集合實際另造了一份。見 F1。
2. 讀筆記狀態的方法:專案讀筆記 type/status 走 `_drift_tree_env(root, where, vault_rel)` 取得該提交的筆記表,再用 `_drift_str(n, "type"/"status")` 取值(`scripts/lumos:32632`、`32269`、`32583`)。計劃自己用 `_drift_cat` 批次讀 blob 再手動 `split_frontmatter`+`parse_frontmatter` 取兩個欄位,另一套讀法。見 F2。

## 問 4 落點
lands_in 寫 `Systems/存量漂移守衛` 是對的:表態檔格式、`_drift_split_acked`、REVISIT 與 c2/c3/c6 照留都記在那篇(`docs/lumos-toolchain-knowledge/Systems/存量漂移守衛.md`),不必另開。但計劃第 7 點只說寫回「表態失效規則、兩個新欄位」,未提 `_DRIFT_BOUND_KINDS` 與新規則的並列關係;若 F1、F2 改成共用既有集合與讀法,該篇要寫成「舊表態怎麼分、新表態怎麼分」同一處對照,否則會變兩套並列說明。`lumos-cli-lifecycle` 先查再補的處理合理。

## F1 狀態集合另造一份
severity: major
blocking: 是
引句:「`_DRIFT_ACK_ROUTE_OPEN = {"issue": ("open", "doing"), "project": ("todo", "doing")}`(取自 `_STATUS_ENUM` 的開著值)」
對照:`_DRIFT_OPEN_ISSUE` 已是 ("open","doing")(`scripts/lumos:32231`),結案側有 `_DRIFT_CLOSED`/`_DRIFT_SETTLED`/`_ISSUE_CLOSED_STATUSES`(`32230-32234`、`16860`)。改法:Issue 格直接引用 `_DRIFT_OPEN_ISSUE`;計劃的開著值若要新增 todo,另一格才新寫,或改成「type 是 issue/project 且 status 不在 `_DRIFT_SETTLED`」沿用既有結案集合,不另列開著白名單。

## F2 另一套讀筆記狀態的方法,且放進載入函式
severity: major
blocking: 是
引句:「`split_frontmatter`+`parse_frontmatter` 取 type 與 status,不在 `_DRIFT_ACK_ROUTE_OPEN` → 「綁的 X 已收尾或不是 Issue/計劃(狀態)」」
對照:專案讀某提交的筆記狀態走 `_drift_tree_env` + `_drift_str`(`scripts/lumos:32632`、`32269`、`32583`);`_drift_load_acks` 只讀表態檔(`34353`)。計劃在載入函式裡自己 `_drift_cat` 加手動解 frontmatter,是第二套讀法,也是載入函式跨層直呼讀節點。改法:失效判斷放 `_drift_split_acked` 或它的呼叫端,用呼叫端已有的 tenv/env.notes 查 type/status(check 路徑有 `tenv`,scan 路徑有 `env`),載入函式維持只讀檔。

## F3 命名與日期注入未對齊
severity: minor
blocking: 否
引句:「`_DRIFT_ACK_ROUTED = ("probe", "retire")`」
對照:同一概念「哪些種類的表態要綁額外東西」,鄰居用 `_DRIFT_BOUND_KINDS`(`scripts/lumos:32259`),建議叫 `_DRIFT_ROUTED_KINDS` 並緊鄰它宣告、註解互相指。另外「今天(本機日期)晚於期限」沒說明日期怎麼讓測試固定;可注入慣例見 `scripts/lumos:4104`(`today = today or _dt.date.today()`),S2/S3 的測試需要它。

不對齊共 3 條,其中 major 2 條
