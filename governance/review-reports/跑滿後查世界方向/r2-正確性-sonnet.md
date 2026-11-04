severity: major

外部審稿人第 2 輪:對 `r2-snapshot.md` 逐節讀過,並開檔驗了 `_cap_retro_check`(`scripts/lumos:22399`)、`_cap_retro_status`(22509)、`_cap_retro_fix_cmd`(22577)、`_cap_retro_next_lines`(22763)、`cmd_loop_cap_decision`(22797)、`cmd_loop_retro`(22851)、`cmd_loop_retro_stats`(22981)、`_loop_ts_key`(19357)、`_retro_text_ok`(22395)、`_cap_real_cutoff`(`scripts/test_lumos.py:50804`)、`_cr_decide`/`_cr_retro_doc`(103441/103445)。r1 的 34 條我也逐條對過去向表,數目對得上(9+8+10+7)。

## r1 去向核對

- G2(提示順序)、G3(七處加逐處行號)、G4 的 queries 每條、undetermined、網址正規化、型別先驗:都在做法第 3 點寫定了。
- G5(舊格式分支、修法死路):修法已交給 `_cap_retro_fix_cmd` 那張表,但「不要求時整段不驗」與第 60 行互相打架,見第 1 條。
- G1(主觸發與決策說法一致):沒有修乾淨,見第 4 條。
- G8(回頭條件量得出來):量法只寫到一半,見第 2 條與第 3 條。

## 逐條 finding

1. 「不要求時」到底驗不驗 world_check,第 56 行與第 60 行互相矛盾;`--record` 取 `world_verdict` 時會讀到沒驗過的值。
引句:「不要求時(人裁早於生效日的 version 1)整段 world_check 不驗」
   - 第 56 行說不要求時整段不驗,S5 末句也這樣寫。第 60 行說「accept-risk、或不要求時:…有填就照上面驗」,而且「不是物件算型別錯」。
   - 輸入 A:人裁 extra-round,`ts` 早於生效日,回顧 `version: 1`,帶 `"world_check": "oops"`。照第 56 行,`--check` 通過。照第 60 行,型別錯。
   - 輸入 B:同上,但 `"world_check": {"verdict": 5}`,或 `verdict` 是 256KB 內的任意長字串。照第 56 行,`--check` 通過。
   - 兩種讀法都有測試可綁:S5 綁第 56 行,S4 的「填了一半算錯」綁第 60 行,所以實作者怎麼選,測試都能綠。
   - 後果在第 4 點:`--record` 要把 `world_verdict` 寫進治理帳。若實作者照第 56 行放行 A、B,`--record` 取值有兩種結果。A 的 `.get` 對字串丟 AttributeError,`--record` 在 `--check` 已過之後才吐堆疊。B 則把沒驗過的任意值寫進治理帳,retro-stats 的「方向對/要換/判不準」三種分法也接不住它。
   - spec 沒寫「`world_verdict` 只在 world_check 通過驗證時才取」,所以取值與驗證用的不是同一條判準。
   - file: `scripts/lumos:22961`(`--record` 取得 `_data` 的地方),`scripts/lumos:22972`(寫 recorded 事件的 `extra`)。
severity: major
blocking: 是——同一份 spec 對同一個輸入給出兩個相反判定,而且第 4 點的記帳取值會踩到沒驗過的資料。

2. `world_verdict` 與 retro-stats 的資料來源沒定,RETIRE-IF 要的數字照字面算不出來。
引句:「`--record` 寫的治理帳事件多帶 `world_verdict`(沒填就不帶),`retro-stats` 多印一段」
   - 事件欄位與檔內 `verdict` 是兩個來源。`_cap_retro_scan` 只把 `_cap_retro_status` 的結果交給 stats,stats 看不到事件(`scripts/lumos:22648`、22994 起)。
   - 若 stats 數事件:同一迴圈的回顧改完重新 `--record`(spec 與既有提示都鼓勵這樣做),會有兩筆 recorded 事件,同一個迴圈被數兩次。回顧在 `--record` 之後被改而變 stale 時,事件裡的舊 verdict 還在,仍被數進去。
   - 若 stats 讀 `st["data"]`:事件欄位沒有人讀,第 4 點等於只是多寫一欄。
   - `verdict` 檢查時去頭尾空白,但事件欄位沒寫要不要 strip。` direction-ok ` 在檔裡合格,事件裡若原樣存,三分法就對不上。
   - stats 的段落沒分人裁種類。RETIRE-IF 只看人裁加開的迴圈,但 accept-risk 且填了完整 world_check 的迴圈也會被數進同一段,數字被灌水。
   - RETIRE-IF 還要比「加開後那一輪的折入數」,retro-stats 不輸出這個數。
   - file: `scripts/lumos:23002`(stats 只取 `st.get("data")`)。
severity: minor
blocking: 否——只影響回頭看的量測,不影響放行與擋下,補一句「取每個迴圈最新人裁之後最新一筆 recorded、且只數 extra-round」即可。

3. `undetermined` 可以零來源,等於整道保底有一條成本最低的過關路;RETIRE-IF 的條件也被它抵消。
引句:「是 undetermined 時可以沒有來源(查不到就照實寫,note 裡講查了什麼、為什麼沒有)」
   - 最小過關輸入:`queries: ["abcd"]`、`verdict: "undetermined"`、`sources: []`、一段 20 個字的 note。字數口徑是 `_retro_text_ok`,只數 `strip` 後的長度,所以標點湊字也過。
   - 這跟「AI 可以編網址」是兩回事。編網址至少要寫出兩個像網址的字串,undetermined 是 spec 明文放行的零動作路徑。
   - RETIRE-IF 寫的是「要換方向」或「判不準」次數為 0 才撤。AI 一律填 undetermined 時,次數永遠大於 0,這道機制沒改變任何決定,撤除條件卻永遠不成立。
   - 手冊與提示寫「至少兩個來源」(第 50、51 行),檢查卻允許 0 個,手冊的 `方向:對|要換|判不準` 與檢查的三個英文值之間也沒有對照表。
   - 這屬於「不防偽造」的天花板範圍,所以我只標 minor。但撤除條件被它抵消,是 spec 自己漏掉的接縫。
   - file: `scripts/lumos:22395`(`_retro_text_ok` 只比 `len(v.strip())`)。
severity: minor
blocking: 否——格式檢查本來就不保證真查過;建議的缺口只在 RETIRE-IF 的算法,把 undetermined 單獨列一項不併入「判不準」即可。

4. d1 與白話段仍帶「準備換形狀時」,做法第 0 點沒有這個條件;r1 的 G1 只改了一半。
引句:「同一類根因連兩輪出現而這一輪那組有 major、準備換形狀時,既有〈先查世界〉擴成也查方向」
   - r1-intake G1 寫「d1 改成『連兩輪出現而這一輪有 major』」,但 d1 現文(第 16 行)與白話段(第 25 行)都還留著「準備換形狀時」。
   - 做法第 0 點與「最小解」(第 43 行)的觸發只有「連兩輪、這一輪有 major」,沒有這個條件。
   - 分歧輸入:某組根因連兩輪、本輪有 major,但編排者打算沿用同一形狀只補洞。依 d1 與白話段不必查方向,依第 0 點必做。手冊同步測試 `t_manuals_world_direction_sync` 只比對字樣,抓不到這個分歧。
   - 這是 r1 整合席第 3 點(d1 與正文說法不同)的同一個根因,所以不能算已修好。
severity: minor
blocking: 否——r1 當時就判措辭層、改一邊即可;只是 intake 已經記成「折入」,現文卻不符。

5. 測試生效時間的做法只涵蓋一部分測試,其餘會在合併當天紅,且沒講常數解不開時怎麼辦。
引句:「S4 兩支測試直接把常數設到人裁時間的前一秒或後一秒,不靠真實時鐘」
   - 時間相關的是 S5,不是 S4(S4 是 accept-risk,與常數無關)。S4 在這裡應是 S5 的筆誤。
   - 更要緊的是 S2:`_cr_decide` 的 `ts` 是真實時鐘(`scripts/lumos:1601`),生效日是合併隔天零點,合併當天 `now` 早於常數。S2 的負向案例(version 1 要被擋、world_check 缺要被擋)在合併當天,人裁被當成「生效日前」而不要求,測試判成通過,於是翻紅,隔天零點又翻綠。第 7 點只說 S4 的兩支改常數,沒有說 S2、S5、S6 的負向案例也要釘常數。
   - 環境變數覆寫的值格式沒寫。`_cap_real_cutoff`(`scripts/test_lumos.py:50804`)示範的是 `"2026-08-26"` 這種日期,抄過來給 `_CAP_WORLD_CHECK_SINCE` 用時,`_loop_ts_key("2026-11-05")` 回 None(沒帶時區,實測)。spec 沒定義常數解不開時的行為,與「ts 解不開當成要求」並置時,比較式會 TypeError,`canary record`、`loop next`、doctor 都會吐堆疊(`_cap_retro_record_block` 沒有包 try)。
   - 這個覆寫是 production 路徑讀的環境變數,spec 寫「只給測試用」但沒有任何守衛。這是既有慣例(`LUMOS_PANEL_RETIRE_CUTOFF`,`scripts/lumos:18839`),所以不列獨立發現。
   - file: `scripts/test_lumos.py:103441`。
severity: minor
blocking: 否——本機推送前閘當天就會看到紅,不會漏進主線;但 spec 要把「全部負向案例都釘常數、值要帶時區」寫進第 7 點。

6. 網址檢查的下限還是太寬:無主機名的網址能湊成「兩個互異來源」,正規化的規則沒寫到可以實作。
引句:「每一項 source:`url` 去頭尾空白、scheme 不分大小寫是 http 或 https、而且 `://` 後面不是空的」
   - 輸入:`https:///a` 與 `https:///b`。scheme 對,`://` 後面是 `/a`、`/b` 非空,正規化後互異,`point` 各 10 字,verdict 填 direction-ok,整份通過。同理 `https://?x`、`https://:80`。
   - `https://#a` 與 `https://#b` 在去掉 `#` 之後變成相同的 `https://`,會被判重複,所以這兩個被擋是巧合。
   - 「主機名轉小寫」沒定義怎麼切主機名(含 userinfo、連接埠、IPv6 方括號)。偷懶的實作會整串轉小寫,於是大小寫不同的路徑(`/Foo` 與 `/foo`)被誤判重複,把合法的兩個來源擋掉。
   - 同頁異寫法仍可湊兩項:`https://a.com/x`、`https://a.com/x?`、`https://a.com/x?utm=1`、`https://www.a.com/x`、`http://a.com/x`。spec 的天花板只免了偽造防護,沒免這個。
   - 「兩個來源」是兩個網址還是兩個網域,沒說。
   - file: `scripts/lumos:22395`(沒有可借用的 URL 驗證器,全新自寫一套)。
severity: minor
blocking: 否——欄位本來只擋格式;但 spec 宣稱的 `://` 後面不是空,擋不住無主機名的網址。

7. 「查 → 攤人裁 → 記 cap-decision」只在兩個提示點生效,接手的會談與骨架提示漏掉 world_check。
引句:「`_cap_retro_next_lines`(跑滿提示與 `loop next --json` 共用)在」
   - 該函式只在「還沒有人裁」那一支(`scripts/lumos:22779`)加一句。「已有人裁」那支(22790)印「繼續之前先寫跑滿回顧:…」,沒提 world_check。
   - `--template` 的 stderr 提示(22944–22945)寫「編排者補 avoid 與 changes、填 completed_by」,同樣沒提。
   - 擋下路徑也只講 `--template`:`_cap_retro_record_block`(22694)、處置閘第八步(22733–22737)、`loop next` 的 cap_retro。
   - 實際情境:人裁記完後會談中斷,新會談讀到的只有「先寫跑滿回顧」。上網查的結果只存在原會談的對話裡,沒有任何檔案留存,新會談得到 `--check` 報 world_check 缺才知道要查,此時可能憑空補寫。
   - 第 1 點只改兩處,與第 5 點「每一處都改」的口徑不一致。
   - file: `scripts/lumos:22790`。
severity: minor
blocking: 否——`--check` 會逐欄列出 world_check 缺什麼,不會放行;只是提示面不完整。

8. 手冊同步點「共七處」仍可能漏列,而 S8 的守衛只比對字樣。
引句:「共七處,措辭各不同,逐處列」
   - 我對 `skills/` 與 `docs/command-reference.md` 搜 `cap-decision` 與 `跑滿回顧`,有講到頂後流程、但 spec 沒列行號的有:
     - `skills/lumos-project-notes/commands/05-設計審查迴圈.md:22`(「跑滿上限沒過,人裁決定…」那一列)。
     - 同檔第 23 列(「記了人裁,要寫跑滿回顧」)。
     - `README.md:92-93`(人的裁定與回顧流程;`README.en.md` 我沒開檔驗,⚠)。
     - `skills/lumos-project-notes/commands/06-代碼審與推送.md:130-134`(retro 與 retro-stats 的使用說明)。
   - spec 列的 05 只有第 33 行;`templates.md:574`(「人裁記了 cap-decision 之後,繼續之前」)只在 §9 的編排者須知補一句。
   - 這些列是否算「到頂的說法」要看實作者怎麼劃線。`t_manuals_world_direction_sync` 若只掃已列的七個檔,漏列的列不會被抓到。這跟 r1 的 G3(數錯處數)同一個根因。
   - file: `skills/lumos-project-notes/commands/05-設計審查迴圈.md:22`。
severity: minor
blocking: 否——AI 平常翻的是指令速查,漏列只讓一處手冊落後,工具保底照擋。

## 各節已讀

- 〈問題與最小解〉〈不做〉〈回退〉:已讀,無 finding。回退段「version 收 1 或 2 那段留著」只涵蓋部分回退;整支 `git revert` 時,已記 v2 回顧的迴圈會變 stale 而擋 `canary record`,spec 的相容二已記此風險。
- S1、S3、S4、S6、S7:已讀,無獨立 finding(S4 的「空骨架」邊界已由做法第 3 點定義清楚)。

## 實務隱患逐類

- 併發:無新風險。`--record` 驗證與算指紋用同一份位元組,`cap-decision` 夾在 `--check` 與 `--record` 之間時,`_cap_retro_status`(`scripts/lumos:22569`)會用新的最新人裁重驗,不合就判 stale,寧擋不放。
- 效能:無。新增的是對 ≤256KB 檔的常數次欄位檢查與一次集合比對。壞項多時問題清單不封頂,r1 已實測放行。
- 資源:無。工具不上網、不開新檔、不起程序。
- 回滾:見回退段註記。第 1 條是 production 判定面的問題,不是回滾問題。

## 圖譜節點(逐條判)

- `Systems/loop-retro`:0 條合約。其中兩條 PITFALL 不受影響:「`_cap_retro_fix_cmd` 唯一決定修法」,spec 照它新增一種狀態;「`_cap_retro_next_lines` 唯一決定提示」,spec 照它改。WHY d7(五處共用同一支判定)不受影響,因為「是否要求 world_check」放在 `_cap_retro_check` 內,五個呼叫端同口徑。
- `Systems/每輪修補差異派工`:0 條合約。既有 WHY 的 [不選] 是「只在跑滿或卡關時才查」,保底層正是「跑滿時查方向」。d1 已用不同查證對象(修法 vs 方向)解釋這點,但寫回那行 WHY 時要把這層區別寫明,否則讀者會看成翻案。

最嚴重 severity 是 major(第 1 條),blocking 共 1 條,其餘 7 條 minor 皆 blocking 否。
