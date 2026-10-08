severity: major

**Q1**
severity: major
blocking: 是,別棵樹、別的提交、祖先以外的歷史都能算出 strong,CI 讀這個 strong 當背書。
算背書時沒拿紀錄的 commit 跟表態 head_sha 或當下 HEAD 比;kill 在 detach worktree 的 HEAD 上跑,killed 只證明那個提交當時咬得住;kill-log 在簿記白名單,之後重跑 survived 再提交,舊表態照樣有效;--at-sha/--branch 讓表態綁被推的 sha,背書卻讀 cwd 那棵樹;追蹤的 kill-log 經合併帶進別人的紀錄會被當本機紀錄;天花板沒列這條,升擋前提漏了它。
引句:「讀本機 `docs/.kill-log.jsonl`(讀不到或沒有這個檔 → 背書=`none`,原因「本機沒有破壞測試紀錄」)」
file: `scripts/lumos:13101`
file: `scripts/lumos:13201`
file: `scripts/lumos:21530`
file: `scripts/lumos:37161`

**Q2**
severity: major
blocking: 是,安全性結論錯,錯在誤放行的方向。
破壞測試跑完整批才一次寫多行,正在跑的那批寫入前完全不可見;讀到的最後一筆是上一筆,上一筆 killed 而新一批其實 survived 就算 strong;寫到一半被砍留下殘行,下一次 append 接在後面整行壞掉,略過壞行會丟掉正常的新紀錄;檔案順序不等於時間順序,ts 只到秒。
引句:「讀到半行(另一個破壞測試正在寫)照第 3 步略過壞行,結果是少算背書、只會多提醒。」
file: `scripts/lumos:13199`

**Q3**
severity: major
blocking: 是,照字面實作會出現 traceback 而不是 none。
非 UTF-8 丟 UnicodeDecodeError、非 dict 行丟 AttributeError、covers 字串變子字串比對;背書計算在寫帳前、那段沒有 try,例外讓指令一筆都沒寫,warn-only 功能擋住寫表態。必須整個包 try,例外得 none 原因「讀取失敗」照常寫帳。治理帳與標記吃同一份 data 不會分岔;validate 不拒多餘欄位。
引句:「算出來的結果以 `backing` 欄位存進該題的表態(樣板裡若已帶 `backing`,一律丟掉重算,不信任手填或 `--carry` 帶過來的值)。」
file: `scripts/lumos:37664`
file: `scripts/lumos:37690`

**Q4**
severity: major
blocking: 是,同檔兩條配方互相遮蔽。
kill-log 沒存 old/new;同合約同檔兩條壞法併成一組;只有後一條宣告 covers 時前一條被先濾掉;兩條都宣告時前 survived 後 killed 看成 strong。要加配方識別(例如 old/new 雜湊)納入分組鍵。
引句:「按配方分組(配方=同一 node、同一 invariant、同一 file),每組取檔案順序最後一筆。」
file: `scripts/lumos:13215`

**Q5**
severity: major
blocking: 是,合約漏寫實際缺口。
測試檔就是程式碼,改它會讓表態失效並重算,所以天花板第 1 條描述的情境大致不會發生;真正的缺口是 kill-log 是簿記豁免檔,表態之後新增的 survived 不會讓舊表態失效;〈過期〉那句因此不準。
引句:「表態之後才改弱測試**:背書在重表態時才重算;表態之後、推送之前若把測試改弱但沒動到會讓表態失效的檔,背書仍是舊的。」
file: `scripts/lumos:21530`
file: `scripts/lumos:37161`

**Q6**
severity: minor
blocking: 否,文字精度問題。
「取最後一筆」讓多次 survived 後一次碰巧 killed 就變 strong,可被重跑洗成 strong;flaky_risk 不標併發類測試。
引句:「破壞測試只跑一次,機率性才紅的併發測試可能剛好紅而拿到 killed(誤放行),也可能剛好綠而 survived(誤提醒)。」
file: `scripts/lumos:13175`

**Q7**
severity: minor
blocking: 否,只影響 gov 顯示與統計筆數。
去重鍵含 commit,kill 源 token 是 invariant+ts;改成逐筆 HEAD 後多平台不再折成一筆;實作要把 commit 存進每個 results 元素,S3 要用兩平台 HEAD 不同的情境。
引句:「同時修一個既有小問題:`commit` 改成每筆記它那一組平台跑的當下 HEAD(現行多平台時整批只記最後一組)。」
file: `scripts/lumos:7293`
file: `scripts/lumos:7326`
file: `scripts/lumos:13089`

**Q8**
severity: major
blocking: 是,與 Q1 同根,spec 的宣稱本身不成立。
CI 讀到的是「某台機器算出的 strong」,不能重算、不能驗證、手動追加治理帳就能偽造;要列進天花板,升擋要改成 CI 端自己能驗。
引句:「之後照既有流程先寫治理帳的 `kind=dispositions` 事件、再原子寫標記——CI 讀得到,因為它本來就讀這筆事件。」
file: `scripts/lumos:37055`

已讀,無 finding:推送前檢查不讀帳不跑 git 成立(`scripts/lumos:36926`);寫入順序不分岔;標記寫失敗只提醒(`scripts/lumos:37697`);`_codeloop_write_dispositions` 暫存檔帶 pid 與隨機名。

最嚴重 major;blocking 為是的條目是 Q1、Q2、Q3、Q4、Q5、Q8,共 6 條。
