severity: major

第 3 版沒有 blocker;簡化立場下只有一條 major:RETIRE-IF 量法做不出來。頭部摘要、緣起、題目、過期、開關、不做、回退、合約候選:已讀,無 finding。

**H1 RETIRE-IF 的量法現在無法照字面執行**
severity: major
blocking: 是。撤除條件 ① ② 量不出來,這層機制就沒有可執行的退場路。
- ① 分母「上線後、被標題目、人工表態」:backing 只寫進 satisfied 且被標的題,na/todo/tension 事件上線前後長得一樣,切不出「上線後」;gov --stats 是聚合輸出看不到逐筆時間;S13 沒有上線日切點。
- ② 分子分母都沒有資料來源:提醒只印終端不進帳;「使用者回報」沒有登記入口;「因此補上合約的次數」沒有計數。
- ③ 與 ① 同分母,同樣缺切點。
- 最小修法:為被標八題每筆表態(含 na/todo/tension)記一個機制版本標記,S13 以它切分母;② 改成可數的量或刪掉。
引句:「分母=上線後、被標題目、人工表態(不含自動記的未觸發)的事件」
引句:「②使用者回報的誤提醒多過因此補上合約的次數」
file: `scripts/lumos:7277` gov 讀 dispositions 事件,沒有八題分流也沒有機制版本欄。

**H2 weak 欄位與既有 flaky_risk 幾乎重複**
severity: minor
blocking: 否。多一個冗餘欄位不影響正確性。
flaky_risk 已寫進 kill-log(`scripts/lumos:13218`),整套一起跑已有 note_ws 判斷(`scripts/lumos:13127`);只新增 whole_suite 事實欄,讀端用 flaky_risk or whole_suite 判弱,定義只留讀端一處。
引句:「`weak`:那次是整套測試一起跑(run_cmd 沒有 `{method}`)或平台有 `flaky_risk` 時為 true。」

**H3 kill-add 只更新 covers 這條路可以砍**
severity: minor
blocking: 否。拿掉它,人先手動拿掉舊配方再重新 add 即可。
現行擋下訊息已指示手動處理(`scripts/lumos:12855`);要比對「其他欄位完全相同」,note/test/new/platform 算不算 spec 沒寫;若保留要寫明欄位清單。
引句:「就只更新那條的 `covers`,印出更新前後,其餘情況照舊擋。」

**H4 背書記錄存的細節比讀者用得到的多**
severity: minor
blocking: 否。只是讓記錄變胖。
提醒與派工鏡頭只用是否 strong、條數與第一條 note 前 40 字。
引句:「每組記 node、invariant、head_sha 前 8 碼、ts、配方的壞法說明(note 截到 80 字、去掉換行)。」

**H5 九處同步其實是八處外加一條不用改**
severity: minor
blocking: 否。
第 9 處是「不用改」卻被算進九處、S14 要求逐一打開;第 2、8 處可併入第 1 處。
引句:「9. 全域紀律範本(`scripts/templates/graph-discipline.md`)不提表態與破壞測試,不用改;」

已查過不構成 finding:配方身分雜湊鍵與 kill-add 判重一致(`scripts/lumos:12855`);補換行可留;共用讀取函式有理由(`scripts/lumos:7291`);整體比例在 H1 補上前提下不算明顯不成比例。

最嚴重 severity: major;blocking 共 1 條。
