# r2 收貨紀錄

## 席位收貨

四席報告從逐字稿存,全數錨定。架構對齊席首交的總結句帶了「要升成 major」的條件式字樣(高於檔級 minor),退回只改總結句,補交版才記帳。編號:正確性 1–8 記 c1–c8、邊界 1–9 記 b1–b9、整合 1–14 記 i1–i14、架構對齊依出現順序 1–5 記 a1–a5(a1 統計的資料來源、a2 retro-stats 沒有 JSON、a3 d2 編號懸空、a4 測試改生效時間的做法、a5 網址正規化沒借 urlsplit)。

先查世界:本輪修法都是對齊 repo 既有做法(`urllib.parse.urlsplit` 與 `_secev_target_host` 的主機名取法、`_cap_retro_status` 回的已驗內容、`_SPEC_GATE_SINCE` 那一族不給環境變數覆寫、既有 cap-decision 測試直接寫帶 ts 的事件);外部方向在立案時已查。

## 依根因分組與去向

| 組 | 根因 | 發現 | 去向 |
|---|---|---|---|
| G1 | 「不要求時」驗不驗互相矛盾、world_verdict 寫進沒驗過的值 | c1 b1 b2 i5 | 折:分成要求/選填/不管三種;不管時整段不讀不驗不寫帳;world_verdict 只在檢查通過時寫常數本身 |
| G2 | 統計的資料來源、重記灌水、只看加開、JSON、RETIRE-IF 被判不準抵消 | c2 c3 b8 i8 a1 a2 | 折:retro-stats 讀 `_cap_retro_status` 已驗內容、每迴圈一次、只數 extra-round、四種次數含沒填、--json 同步;RETIRE-IF 改數「要換方向」,判不準過半另交人裁 |
| G3 | d1 與正文、白話段觸發條件不一致 | c4 i1 | 折:三處都改成「同類根因連兩輪出現、這一輪那組有 major」 |
| G4 | 測試改生效時間的做法 | c5 b6 i7 a4 | 折:常數不給環境變數覆寫,測試直接寫帶 ts 的人裁事件,S2、S5、S6 負向案例都這樣做 |
| G5 | 網址檢查(無主機名、解析例外、正規化步驟、同頁異寫法) | c6 b3 b4 b5 i6 a5 | 折(i6 的「方向:對/要換/判不準」對照表在 G7 一併寫進手冊):用 `urlsplit`,解不開算該項錯、要有 hostname,比 (scheme, hostname, port, 去結尾斜線的 path, query);同頁異寫法列天花板一 |
| G6 | 提示面不完整(已有人裁分支、--template 提示) | c7 | 折:兩處都補 world_check |
| G7 | 手冊同步點漏列、守衛粒度、§9 派工詞、對照表、步驟 4 先後、原句後半 | c8 i2 i3 i9 i10 i11 | 折:同步點逐處列(含 05 第 22、23 列、06、README 兩份、指令參考兩份、CHANGELOG);S8 逐處比對;§9 不要填加 world_check;手冊寫明 方向:對/要換/判不準 對 direction-ok/change-direction/undetermined;代碼審第 4 步補「換形狀前先查方向」;原句整句保留 |
| G8 | 新增狀態會讓計數表崩、修法表 | i4 | 折:不新增狀態,改在 --check 逐欄列錯那行講修法 |
| G9 | 寫回與 REVISIT(〈先查世界〉的 [不選] 並存、12-15 回頭條件量錯、審查跑滿回顧兩處舊說法、提示的家) | i12 i13 a3 | 折:新 WHY 寫明跟 [不選] 不衝突的理由;12-15 那行 REVISIT 加「方向:」行;兩處指過來;lands_in 補 Systems/loop-convergence-recording;d2 寫成 [[Systems/loop-retro]] d2 |
| G10 | 全標點湊字、骨架空殼 source 在 undetermined 時、舊工具讀 v2 | b7 b9 i14 | 折:全標點列〈不做〉與天花板一;錯誤訊息講「沒有來源就改成 []」;相容二寫明符號連結安裝同步生效 |

36 條:全部折入,0 條放行,0 條重現不到。
