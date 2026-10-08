severity: major

問 1 分層與依賴方向:寫表態那層呼叫 `_codeloop_record_valid` 對齊(共用版本判定,`scripts/lumos:37279`、`scripts/lumos:37133`,同屬 code-loop 組,不算跨層);讀 kill-log 用 Path(repo_root)/"docs" 同 `scripts/lumos:37058`;推送前只讀記錄對齊(閉包附 out 同 `scripts/lumos:37343`;warnings 在 `scripts/lumos:37874` 印成提醒)。不對齊見 AA1。
問 2 命名:needs_backing、head_sha(同 `scripts/lumos:37061` 的 commit+head_sha 寫法)、backing(條目已有 carried/auto/hint,carry 淺拷貝 `scripts/lumos:37405`)、covers 皆無衝突;不一致見 AA3–AA5。
問 3 第二種做法:版本有效性確實沿用 `_codeloop_record_valid`;kill-add 更新語意屬新增行為;配方身分鍵、方法名正規化見 AA2;補換行見 AA5。
問 4 落點:兩篇合理;缺口見 AA6。

**AA1**
severity: major
blocking: 是(引入第二種做法)
表態證據驗證時機從「推送前讀側驗」改成「寫表態時算、存結果」;既有做法寫表態只驗形狀(`scripts/lumos:36985`),證據由推送前 `_dispositions_check_test` 驗(`scripts/lumos:37198`、`scripts/lumos:37325`);鏡頭表頭(`scripts/lumos:34834`)與技能文件都寫「寫入時工具只驗了形狀」,設計沒寫明刻意偏離也沒同步改這半句,九處清單沒列。要嘛在 Systems/棧別提問表態閘記成 WHY,要嘛把這半句列進要改的位置。
引句:「`_dispositions_verdict` 在 satisfied 分支(不是共用的 `_ev`,所以 tension 不受影響),對標了 needs_backing 的題看表態記錄裡的 `backing`」

**AA2**
severity: major
blocking: 是(同一個身分鍵在兩處各寫一份)
kill-add 用三欄 == 比對(`scripts/lumos:12862`),沒有雜湊也沒有共用函式;照字面會變成 kill-add 一份比對、kill 一份雜湊;雜湊先例是 join 後 sha256(`scripts/lumos:5830`、`scripts/lumos:5846`);方法名正規化也是內嵌(`scripts/lumos:13119`)。應抽成單一函式讓 kill-add、kill、寫表態三處共用。
引句:「**配方身分**=invariant、file、old 三者合起來的雜湊,跟 `cmd_guard_kill_add` 判「同一條配方」用的鍵相同」

**AA3**
severity: minor
blocking: 否
身分雜湊沒納入 node;kill-add 比對範圍是單一筆記內;兩篇筆記同 invariant 子字串、同檔、同 old 會被併組。雜湊要加 node 或分組鍵用 (node, 雜湊)。
引句:「把留下的紀錄按配方身分分組,每組看**最後一筆**的 `covers` 有沒有這一題」

**AA4**
severity: minor
blocking: 否
recipe 在專案指整條配方 dict;雜湊欄慣例是 _sha256 後綴(`scripts/lumos:7307`、`scripts/lumos:8102`),建議 recipe_sha256 或 recipe_id;backing.recipes 也可改名;weak 與 flaky_risk(`scripts/lumos:13218`)部分重複,整套一起跑目前只在 detail 文字(`scripts/lumos:13176`),升成布林合理。
引句:「`recipe`:配方身分雜湊。」

**AA5**
severity: minor
blocking: 否(錯誤處理不一致)
既有慣例失敗要在 stderr 講一句(`scripts/lumos:1234`、`scripts/lumos:13207`),設計例外記 none 沒有 stderr;第 4 步丟掉 `_codeloop_record_valid` 回的 why,git 逾時(`scripts/lumos:37165`)會被講成沒跑過;補換行只在破壞測試這一支做,其他追加帳檔不補(`scripts/lumos:1233`、`scripts/lumos:37078`、`scripts/lumos:8552`),先例只有 `scripts/lumos:18003`,應在 Systems/guard-kill 註明。
引句:「任何例外都記 `backing={"status":"none","reason":"讀取失敗"}`,照常寫帳」

**AA6**
severity: minor
blocking: 否(落點)
要改 Systems/效能檢核目錄 但沒列進 lands_in;--covers 讓 guard 層依賴題目表 `_stack_spec_by_id`,表態閘又依賴 kill-log,兩篇 Systems 雙向資料依賴;recall-miss 用 `_stack_spec_by_id` 是在表態閘那側(`scripts/lumos:37698`);Systems/guard-kill 要寫明新依賴方向。
引句:「`Systems/效能檢核目錄` 的消費專案設定段:補一句被標八題會看背書。」

不對齊共 6 條,其中 major 2 條
