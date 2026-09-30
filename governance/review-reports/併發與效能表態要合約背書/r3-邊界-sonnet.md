severity: major

S1~S14 測試名只有 t_guard_kill_json_purity 已存在(`scripts/test_lumos.py:20214`),其餘 12 個還沒寫。

**D1 殘行補換行只處理行沒處理位元組,半個中文字讓背書永久讀取失敗**
severity: major
blocking: 是 — 中斷寫入後背書一律 none,補換行修不好。
kill-log 用 ensure_ascii=False 寫中文,殘行可能停在多位元組中間;補完換行壞位元組還在;第 3 步沒規定位元組讀或 errors="replace",read_text 會拋 UnicodeDecodeError,被 try 接成讀取失敗且每次都發生;gov 的 load 也在 try 外會崩(`scripts/lumos:7252`);補換行的判斷要用位元組;空檔、只有換行、單行無換行三個邊界沒寫。修法:讀寫都用位元組或 errors="replace",逐行 decode 失敗略過;S5 加截斷多位元組案例。
引句:「寫 kill-log 前,檔案若不是以換行結尾(上次寫到一半被中斷),先補一個換行,免得新的一批接在殘行後面整行壞掉。」
file: `scripts/lumos:13199`
file: `scripts/lumos:7252`

**D2 covers 與配方雜湊取自工作樹筆記,沙盒跑的是 HEAD,版本綁定只綁一半**
severity: major
blocking: 是 — 合約候選第 2 條做不到。
配方來自 `_kill_read_recipes` 讀工作樹筆記(`scripts/lumos:13037`),沙盒是 detach HEAD;筆記沒提交就 guard kill,kill-log 記下工作樹才有的 covers 與 head_sha=不含配方的 HEAD,表態判同版本可得 strong,被推送的筆記卻沒有這個 covers;kill 偵測到 dirty 只印警告(`scripts/lumos:13085`)沒寫進 kill-log;漏洞在筆記髒、受測檔與測試乾淨那一格。修法:節點檔髒時 weak 設 true,或 kill 從 git show HEAD:<節點> 讀配方。
引句:「背書只認在有效版本上跑的破壞測試,且涵蓋該題的每條配方在有效版本上的每一筆都是非弱的 killed。」

**D3 其他欄位完全相同沒列舉欄位**
severity: minor
blocking: 否 — 有手動繞法。
其他欄位有 new/test/platform/note 四個沒說比哪幾個;--note 預設空字串(`scripts/lumos:38889`),沒重打 note 就被擋並給錯方向訊息;platform 缺鍵視為 None 沒寫;取代還是聯集沒定;沒有指令能移除 covers;自驗 check() 只看 invariant 與 old(`scripts/lumos:12888`);同時帶 --test 沒說;S3 沒鎖這些分界。
引句:「就只更新那條的 `covers`,印出更新前後,其餘情況照舊擋。」

**D4 第 3 步沒說欄位型別不對的行**
severity: minor
blocking: 否 — 不會誤判 strong,只是誤報 none。
head_sha/test/platform/verdict 非字串時,例如 head_sha: 5 讓 subprocess 拋 TypeError,被外層 try 接走全題讀取失敗;淺 clone 的專屬原因(`scripts/lumos:37146`)被第 4 步吞掉。修法:每行先驗 isinstance(str)。
引句:「逐行解析,不是合法 JSON 或不是物件的行略過;`covers` 不是清單就當空清單。」

**D5 有背書的分母定義自相矛盾**
severity: major
blocking: 是 — S13 與 RETIRE-IF ① 照字面量不出繞開比例。
只有 satisfied 且被標的事件寫 backing,na/todo/tension 上線後也沒有 backing;紀錄沒有上線後標記,gov 表態段只按題目彙整 status(`scripts/lumos:7063`);缺 backing 的可能是上線前 satisfied、上線後 na/todo/tension、不需背書的題,三者無法區分;同 sha 重表態重複計入。修法:分母改用事件時間晚於固定啟用日,或 na/todo/tension 也寫 backing 佔位鍵。
引句:「缺 backing 欄位的(上線前寫的)不算進分母。」

**D6 派工鏡頭讀 backing.recipes[0] 沒有 try,S12 沒測壞形狀**
severity: minor
blocking: 否 — 只有記錄被手改或形狀壞時觸發,但一出錯派工整個失敗。
`_lens_dispositions_lines` 呼叫處不在 try 內(`scripts/lumos:35878`);recipes 缺、空清單、note 非字串會 IndexError/TypeError。
引句:「背書註記接在截斷**之後**另起一段,不佔那 200 字」

**D7 S7 一條綁九種情況,少承重案例**
severity: minor
blocking: 否 — 邏輯風險主要由 D1、D4 承擔。
沒列:killed_unattributed/timed_out_weak/drifted/abort/error、最後一筆 covers 取法、空 head_sha 與淺 clone、壞行與欄位非字串;S11 沒測 high-only 非高風險;S4 沒點名空 head_sha 與 weak 兩種來源。
引句:「各判 none 並寫對原因;全數強證據判 strong [test:t_contract_backing_cases]」

已查證無 finding:八題 id 與 `_stack_spec_by_id` 存在(`scripts/lumos:21493`);kill-log 在簿記清單(`scripts/lumos:21530`);`_codeloop_record_valid` 對空 sha、淺 clone、不在 repo 都回 False;warnings 不影響 blocked;carry 的 backing 會被拿掉;gov 去重不受影響;無新寫入點;輸出純度成立。

最嚴重 severity: major,blocking 共 3 條(D1、D2、D5)。
