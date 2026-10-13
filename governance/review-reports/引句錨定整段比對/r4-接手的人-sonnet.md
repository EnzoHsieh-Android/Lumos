severity: major

1. 同步改的文字在第一階段就宣稱工具有整段保證,現實要到第二階段才成立
severity: major
blocking: 是
引句:「這階段行為上等於沒改,只是所有讀帳的地方都認得章了。」
file: `scripts/test_lumos.py:27034`
- 〈兩階段上線〉說第一階段預設 `legacy`,行為等於沒改。〈同步改的地方〉沒分階段,寫的是一整批文字改動:範本、兩份 SKILL、四處收貨三道、`05` 指令表、Systems 節點。
- 這些文字都寫「工具只保證引號裡面那段是真的」或「引號裡面整段要對得上」。
- 第一階段合入後到第二階段之間,寫側仍用舊判準。只驗第一個閉引號之前,這句話是假的。
- 三個月後的接手者照第一階段清單改完文件,文件就比程式多宣稱一截。這正是 Issue 要補的「明文承認」被寫反。
- 〈回退〉的第一條把 `write_rule` 切回 `legacy`。那時已寫進文件的「整段保證」同樣沒有退回的步驟。
- 立案清單第 18 項「標結案」也沒寫在哪一階段做。
- 接手者缺的是三件事:同步清單哪些屬第一階段、哪些屬第二階段,回退時文件怎麼處理,第 18 項與 Issue 何時結案。

2. 第二階段的出發條件沒有放行與否決的門檻,接手者無法獨立決定要不要做
severity: major
blocking: 是
引句:「依〈量測〉口徑重算並寫回〈量測〉,然後開第二階段的提交」
- 第一條 REVISIT 只要求「重算、寫回、然後開提交」,沒寫數字長什麼樣就不開。
- 〈量測〉的數字是舊腳本得來的,而且說只是量級。重算後「舊判過新判不過」若遠大於 21 條,或誤傷比例高,接手者沒有判準可用。
- RETIRE-IF 只管第二階段合入之後的 8 週,管不到合入之前的放行判斷。
- 結果是第二階段會變成照 REVISIT 日期機械執行。
- 補一條「重算後舊判過新判不過超過 X,或人工抽看誤傷超過 Y 就不開」才算接手者能獨立做完。

3. 第二條 REVISIT 的判讀步驟,接手者實際做不出來
severity: major
blocking: 是
引句:「逐筆照事件 note 的報告路徑與指紋讀擋下的報告,判真抓或誤傷,對照 RETIRE-IF」
file: `scripts/lumos:9532`
- 步驟 1:REVISIT 要接手者用 `gov --stats` 看「new-only 筆數」。但輸出字面只有 `引句判準 d` 這一個總數,沒有 kind 分格。
  - 現行輸出只有 `記帳被寫側擋下 N 次(…)` 一行。
  - 接手者得自己去事件帳篩 `kind=new-only`,卻沒有任何指令寫在 spec 裡。
- 步驟 2:被擋的報告多半會被「退回該席重寫」。
  - 同一路徑的檔案被覆蓋。事件只留路徑加前 12 碼指紋,沒有留內容。
  - 8 週後那份報告若沒進 git,只剩指紋,無法讀它判真抓或誤傷。
  - 這點我無法從 spec 確認流程是否都會先留檔,標 ⚠。
- 缺口是 RETIRE-IF 的核心證據(人工逐條判誤傷)沒有保存機制。
- 要補其一:擋下時把報告落檔,或事件帶引句片段。

4. 立案清單第 18 項宣稱「完成條件符合」,但同步清單漏了講收貨三道的地方
severity: minor
blocking: 否
引句:「立案清單第 18 項標結案指向本篇」
file: `docs/methodology/圖譜即合約.md:152`
file: `skills/lumos-project-notes/reference.md:699`
- 立案清單第 18 項的完成條件是「所有講收貨三道的地方」都有那句明文。我 grep 全 repo 的 `收貨三道`,不算 governance 卷證與歷史計劃,清單外還有:
  - `docs/methodology/圖譜即合約.md` 第 152 行,另有第 347 行講「引句由 quote-check 機驗」。
  - `skills/lumos-design-loop/templates.md` 第 444 行判讀那段。
  - `skills/lumos-design-loop/reference.md` 第 241 行。
- 另外 `skills/lumos-code-loop/SKILL.md` 第 41 行是收貨三道摘述。spec 只指定改步驟 2 的格式那條。
- 所以「符合完成條件」的宣稱不成立,至少要列出判定「講收貨三道」的範圍。
- 〈同步改的地方〉也沒提到把 `quote_check.write_rule` 記進設定說明。
  - 同類設定 `bound_tests.parallel` 記在 `skills/lumos-project-notes/commands/07-安裝維運.md`。
  - 消費專案要回退得靠這個鍵,卻沒有地方查得到。

5. 處置閘「專案根」的描述與閘的實作對不上
severity: minor
blocking: 否
引句:「專案根從哪來:處置閘與回放用它們既有的 `root`(`root` 是 None 時用 `_vault_repo_root(env)`)」
file: `scripts/lumos:26195`
file: `scripts/lumos:26235`
- 處置閘依〈讀章〉只讀帳上的 `quote_rule`,根本不讀設定檔,不需要專案根。
- 這句卻要求閘在 `root` 是 None 時去找根。`_loop_status_disposal` 的 `env` 預設值是 None,`_vault_repo_root(None)` 會丟例外。
- 閘現行的 `_prov_path` 在 `root` 是 None 時把路徑當 cwd 相對路徑,語意跟「用 `_vault_repo_root`」不同。
- 實作者看到這句會把設定讀取加進閘,或是照字面實作而炸。
- 要嘛刪掉閘那一半,要嘛寫明閘為什麼需要根。

6. 第二階段「釘預設值的那支測試」不止一支,而且預設常數沒有名字
severity: minor
blocking: 否
引句:「把程式預設改成 `full-span-v1`、把釘預設值的那支測試改成新值。」
file: `scripts/test_lumos.py:27034`
file: `scripts/test_lumos.py:27164`
- 現成測試裡依賴「沒設定時是 legacy」的至少兩處:
  - `t_quote_full_span_rule_stamped_on_ledger` 的「沒有設定檔」那段,在 27034 行。
  - `t_quote_full_span_manual_commands_repo` 的 `bare` 根「切在內層、不越界」,在 27164 行。
- 第二階段預設翻成新值,這兩處都會紅。
- spec 說的是「那支測試」單數。
- 程式預設散在 `_quote_check_config` 裡,沒有命名常數,接手者只能 grep。
- 第二階段的推送前驗證也沒寫:是否重跑回放全跑?
  - 預設翻轉後,沒有設定檔的專案(包含本 repo)寫側立刻換判準。
  - 〈推送前驗證〉整節只對第一階段有意義。

7. 內部不一致:窗口描述前後兩處講法不同,PRIOR-ART 對設定讀法的比照也與正文偏離
severity: minor
blocking: 否
引句:「舊版程式(別的工作樹還沒同步主線)讀到 `full-span-v1` 章時不認得,會照舊判準重算」
- 〈兩階段上線〉說窗口是「第一階段到第二階段之間沒同步的工作樹」。〈實務隱患〉說的是「第二階段合入後還沒同步主線的工作樹」。兩個時間點不同。
  - 真正的風險是任何還沒同步到第一階段的工作樹,看到 `full-span-v1` 章時的行為。
  - 兩處該對齊成同一句。
- 〈回退〉的「完整還原只在第二階段之前做」也有漏洞。第一階段允許在設定裡明寫 `write_rule: full-span-v1`,測試就是這樣用的,所以第二階段之前帳上可能已有該章。
- PRIOR-ART 說設定沿用 `_bound_tests_parallel` 的讀法:「寫錯出聲、退回預設」。
  - 正文是壞值退回 `legacy`。第二階段預設變成 `full-span-v1`,兩者就不同。
  - 現行 `_bound_tests_parallel` 對讀不了設定檔是不出聲的。
- 其餘:
  - 「本檔約 30 處」的「本檔」指哪個檔,spec 沒寫清楚。
  - `gov --stats` 新的第四格說 note 開頭判斷,現行是子字串判斷。
  - 現行「其餘 → 缺 refuted-set」那一格,已經混進了 `cap-retro` 類的 blocked 事件(`scripts/lumos:10564`)。四格互斥的「相加等於總數」成立,但「缺 refuted-set」格的語意本來就不純。

已讀,無 finding:
- 〈量測〉的算術:3273 − 20 − 221 = 3032;2587+356+44+45 = 3032;44−23 = 21;21 = 8+9+4。全部吻合。
- 〈範圍〉四個呼叫點:`scripts/lumos` 的 10965、26373、26529、26787 逐一對上。
- 同步清單的行號:
  - `templates.md:63` 原句逐字吻合。
  - design-loop `SKILL.md:27`、design-loop `reference.md:94` 與 514、code-loop `reference.md:91` 都對得上。
  - `05-設計審查迴圈.md:14` 對得上,Systems/design-loop 第 62 行、Systems/loop-convergence-recording 的該節標題也對得上。
- 命令與資料:
  - `decision-add` 的參數(`--decided`、`--context`、`--why`)對得上。
  - `loop replay --golden` 存在。
  - `governance/replay` 底下有 305 個目錄。
  - `_REPLAY_ENGINE_REV` 與 `engine_rev` 過期跳過的行為,和 spec 描述相同。
  - 凍結閉包的 `rows` 確實是整行原樣。

實務隱患(逐類):
- 自我治理、不可逆、效能、金流與對外送出:spec 已列,我沒有新增意見。
- 文件與現實不同步:這是上面第 1 條。
- 交接:這是上面第 2、3、6 條。

實驗目錄 `/tmp/lumos-seat-work/引句錨定整段比對/接手的人-sonnet/` 已刪;沒有改動 repo 任何檔。

總結:最高等級 major,blocking 共 3 條
