severity: major

推論來自逐行閱讀程式,未端到端執行 cmd_guard_kill。

**1. 背書沒有檢查破壞測試是在哪一版程式上跑的**
severity: major
blocking: 是,照字面實作會在測試被改弱後仍判 strong。
第 4、5 步只比對 platform、方法名、covers,不看 kill-log 的 commit 也不看測試檔內容。情境:提交 A 測試夠強 killed;提交 B 把斷言掏空保留同名;在 B 上重表態,`_codeloop_record_valid` 只比 head_sha,記錄有效,背書重算仍讀到 A 的 killed 判 strong。重表態這一步本身就會撞上,重算反而替舊結果重新背書;kill 在別的分支、clone 或 main 上跑也算 strong。
引句:「所以背書最舊只到「最後一次重表態時本機破壞測試紀錄的狀態」。」
file: `scripts/lumos:13089` 只記 short HEAD,沒有讀者比對。
file: `scripts/lumos:37133` `_codeloop_record_valid` 只比對 head_sha 與 marker_sha。

**2. 配方分組鍵(node、invariant、file)太粗**
severity: major
blocking: 是,沒被咬住的配方會被另一條的 killed 蓋掉。
kill-add 重複檢查鍵是 (invariant, file, old);同檔不同 old 是兩條合法配方,併成一組只取最後一筆,結果取決於跑的先後;分組鍵沒含 test;invariant 欄存的是當時敲的片段字串。
引句:「按配方分組(配方=同一 node、同一 invariant、同一 file),每組取檔案順序最後一筆。」
file: `scripts/lumos:12849` 重複檢查鍵。
file: `scripts/lumos:12847` recipe 存 invariant_substr。

**3. 先篩 covers 與方法名再分組,改掉 covers 或改綁測試後舊 killed 永遠留著**
severity: major
blocking: 是,covers 被改掉後仍判 strong。
情境 1:covers 改成別題後重跑 survived,新紀錄被先篩掉,最後一筆仍是舊 killed。情境 2:配方改綁測試 Y 後 survived,對 test:X 表態只剩舊 X killed。應先按配方分組取最後一筆,再判 covers 與方法名。
引句:「取「platform 與方法名都對得上、而且 `covers` 含這一題」的紀錄,按配方分組」

**4. 配方被刪、改名、節點搬移後,kill-log 只增不刪,spec 沒規定如何對帳**
severity: major
blocking: 是,兩個方向都會判錯。
已刪配方的舊 survived 讓該題永遠 none,已刪配方的舊 killed 仍被算 strong;節點改名後舊組仍在;流程從不讀目前節點的 kill_recipes 驗配方還存在且 covers 含這題。
引句:「至少有一組,而且**每一組**的最後一筆都是 `killed` → 背書=`strong`」

**5. 既有配方無法補 --covers,spec 給的補救指令會被擋**
severity: major
blocking: 是,補救指令照做會失敗。
kill-add 對同 invariant、同檔、同 old 回「已經有了,先把舊的那條手動拿掉」並 return 2;沒有更新既有配方的路徑;--covers 不驗 id,打錯永遠不涵蓋。
引句:「`lumos guard kill-add` 多一個選填參數 `--covers <題目id>[,<題目id>…]`,存進配方」
file: `scripts/lumos:12849`

**6. 「改了程式表態就失效」精度不足**
severity: minor
blocking: 否,失效規則確實涵蓋測試與受測程式,只是有例外沒列。
簿記檔含 docs/.kill-log.jsonl;簿記目錄含 governance/replay/、governance/review-reports/;同 sha 時工作樹未提交改動也判有效。
引句:「表態記錄本來就綁提交:改了程式,表態依 `_codeloop_record_valid` 的既有規則失效,要重表態」
file: `scripts/lumos:21527` 簿記檔清單。
file: `scripts/lumos:21544` 簿記目錄清單。

**7. off 模式與 --carry 帶來的舊 backing**
severity: minor
blocking: 否,問題在模式邊界。
--carry 淺拷貝會帶 backing;off 時沒說要丟掉,backing:"strong" 會原樣寫進記錄、派工鏡頭照印;題目由 satisfied 改成 na/todo 時舊 backing 要不要剔除沒寫。
引句:「樣板裡若已帶 `backing`,一律丟掉重算,不信任手填或 `--carry` 帶過來的值。」
file: `scripts/lumos:37393`

**8. 平台欄的來源**
severity: minor
blocking: 否,只影響多平台專案的少數配方。
kill 的平台是 r.get("platform") or platform_override or default_plat,不從 test 前綴推;沒帶 --platform 的 test:"android:X" 在預設平台跑,kill-log platform 為 default,對不上或誤算。
引句:「`method`:實際跑的測試方法名,照 `cmd_guard_kill` 現行的正規化(有平台時去掉平台前綴、去掉 Kotlin 反引號)。」
file: `scripts/lumos:13048`

**9. 「檔案順序最後一筆」**
severity: minor
blocking: 否,只在多人合併 kill-log 時才錯。
追蹤的 kill-log 兩分支各自追加再 merge,行序不是時間序;消費專案 kill-log 是本機檔,換機器讀不到,沒記成已知限制。
引句:「每組取檔案順序最後一筆」

**10. 切分規則與 kill 的正規化不完全一致**
severity: minor
blocking: 否,邊角情形。
引句:「用 `_dispositions_split_test` 把 evidence 拆成(平台, 方法名),方法名照 kill 同一套正規化。」
file: `scripts/lumos:36954`
file: `scripts/lumos:13070`

**11. guard kill --invariant 只跑子集**
severity: minor
blocking: 否,解讀說明不足。
各組可能來自不同 commit,spec 只說印「那次」的提交與日期,多組怎麼印沒說。
引句:「v1 只在提醒與派工單印出那次破壞測試的提交與日期,讓人判斷要不要重跑。」

逐節:緣起、題目、推送前檢查、開關、派工鏡頭、不做、回退、合約候選:已讀,無獨立 finding。實務隱患:併發——第 3、4 條是多算背書,「只會多提醒」不成立;時差見第 1 條;效能、資源、相容無。

最嚴重 severity:major;blocking 共 5 條(第 1 至 5 條)。
