1. severity: blocker｜blocking: 是｜判準：d1 把 repo 現碼的關鍵證據降成未定義、未留痕、未驗內容真偽的敘述通道，實作者照做會讓 quote-check 只證明「讀過 spec」，不能證明 finding 的外部事實成立，直接弱化處置閘證據力。

引句:「存在性由 refcheck 守、真偽由編排者機械重現守,一條不漏」

佐證：現行 skill 只規定 quote-check 核對凍結快照、refcheck 核對 file:line「存在」，沒有定義「機械重現」的命令、輸出格式、失敗處置或治理帳欄位：skills/lumos-design-loop/SKILL.md:22-23。templates 反而明定「編不出引句的疑慮不要交」及錨不到不採信：skills/lumos-design-loop/templates.md:89-90。新規若只換成 file:line+敘述，內容真偽沒有等價機械閘。

2. severity: major｜blocking: 是｜判準：carrier「選全錨席」會按格式合規挑代表帳，而非按 finding 完整性挑證據，且 spec 未規定非 carrier 席的佐證如何逐條綁到彙總 finding，實作者可能記出全綠但證據缺席的處置帳。

引句:「記帳前對候選席報告跑 quote-check,選全錨席當 carrier」

佐證：現行記帳是一筆 carrier 承載全輪 findings/folded/accepted sets，但各席報告只留無 set 的紀錄：skills/lumos-design-loop/SKILL.md:27。若「全錨席」本身只發現部分問題，spec 沒要求 carrier 報告覆蓋彙總集合，也沒建立 finding→佐證通道的映射。

3. severity: major｜blocking: 是｜判準：spec 把兩次正常的「修真缺陷後審 delta」說成因 quote FAIL 才加開 r2，會讓實作者錯把 r2 的抓漏能力當成 d1 卷證規則的實測證據。

引句:「兩迴圈的 r1 carrier 皆因引句錨在審材外現碼觸發 disposal 閘 quote 關 FAIL,各加開一輪 delta 才過」

佐證：canary-log 顯示 code-prose r1 有 12 個 findings、10 折入、2 接受，r2 是修復後仍報 1 minor：docs/.canary-log.jsonl:639-641；code-cascade r1 有 10 個缺陷全折，含 blocker，r2 才是修復回歸零 finding：docs/.canary-log.jsonl:648-650。兩份 r2 報告也逐項驗證前輪修復，而非只補引句：governance/review-reports/code-prose-conv-impl/r2-s1.md:3-17、governance/review-reports/code-cascade-reminder/r2-s1.md:7-46。帳面不能支持「因 quote FAIL 各加開一輪」。

4. severity: major｜blocking: 是｜判準：d3 沒定義比例分母、何謂既有行、rename/move/整段替換如何計算，也沒定義核心裁定命中是 distinct 條目還是 finding 數，因此同一 diff 可被不同實作者算出相反裁定。

引句:「本輪折入的 diff 動了 spec 既有行的比例(git diff 可算)」

佐證：現行 skill 的重寫出口只有可直接數的 blocking/字數門檻：skills/lumos-design-loop/SKILL.md:43；spec 未提供計算命令、算法或例子。尤其純新增大量新裁定可能分母為零或波及率極低，整段刪除重寫又會受 diff 演算法影響。

5. severity: major｜blocking: 是｜判準：把兩訊號硬性合取會漏掉「單一核心裁定被推翻但牽動大半全文」或「多個核心裁定皆錯但修改集中於少數行」兩類應攤人的結構性重寫，卻沒有逃生條款。

引句:「兩訊號都到才建議攤人重寫;仍是人裁選項非自動」

佐證：這是建議訊號而非自動閘，仍使用必要條件「都到才」；一個訊號未達時，skill 便不會攤人，所謂「人裁」無從啟動。應明定 OR 型極端例外，或把雙訊號改成加權判讀而非合取資格。

6. severity: major｜blocking: 是｜判準：30% 明認無本地依據，卻只靠「下一個真案」校準且沒有樣本累積、人工標籤或調整規則，實作者無法判定何時、依何證據改值。

引句:「暫用門檻 >30% 為攤人建議訊號」

佐證：spec 自己承認 30% 是拍值及 [S4] 下案量測：/tmp/loop-friction-r1.md:49；但 [S4] 只說下一個真實迴圈驗證、數字同輪校準：/tmp/loop-friction-r1.md:37，單案不足以辨別 false positive/false negative，也沒有保存 numerator、denominator、人工重寫裁定的帳面 schema。

7. severity: major｜blocking: 是｜判準：d2 讓單一便宜 agent 對語意宣稱「命中直接修真檔」且不算 finding，等於讓高判斷性修改繞過多席、辯方與處置帳，誤修核心裁定也不留可審記錄。

引句:「命中直接修真檔,不算 findings」

佐證：現行首輪前掃只處理未定義詞、壞引用、範圍自相矛盾等較機械事項：skills/lumos-design-loop/SKILL.md:19；語意真假則需要讀碼和判斷。升級後沒有要求第二來源、diff 留痕或正式席重驗，與 repo 對會決定是否動手的否定／缺失宣稱要求乾淨 agent 對證的規矩不對稱：CLAUDE.md:21。

已讀無 finding：d4 落點與「零碼、處置閘語意不動」本身；落地件 [S1]-[S3] 的檔案範圍；金流／不可逆聲明。

總結：最嚴重 severity = blocker；blocking 共 7 條。