severity: major

r2 修法查證:版本綁定語意成立(`scripts/lumos:37133`,同 sha 或祖先且只剩簿記檔);kill-log 在簿記名單(`scripts/lumos:21530`),K 對 D 有效、D 對 M 有效則 K 對 M 有效,推送前只讀 backing 是對的;head_sha 兩側都是完整 sha;配方身分鍵與 kill-add 判重一致(`scripts/lumos:12852`);warnings 只提醒(`scripts/lumos:37871`);backing 隨 dispositions 進帳與標記(`scripts/lumos:37055`、`scripts/lumos:37076`),快取鍵跟著變;步驟 4→5→6 沒找到判錯組合。

**K1 步驟 6 任一筆不是 killed 就永遠拿不到背書,連基礎設施失敗也算**
severity: major
blocking: 是——同一版上重跑全綠仍判沒有背書,提醒沒有出路。
理由只講 survived,規則卻把 abort、error、drifted、timed_out_weak、killed_unattributed 一併算;重現:第一次機器慢得 timed_out_weak(`scripts/lumos:13167`)或 baseline 被環境弄紅得 abort(`scripts/lumos:13133`),修好後重跑全部 killed,程式沒變仍判 none,唯一出路是做無關提交換版本;建沙盒前的 error 因 head_sha 空被步驟 4 排除,abort 卻被算,不對稱。修法:只讓 survived 與 killed_unattributed 洗不掉。
引句:「涵蓋這一題的每一組,組內**每一筆**都要是 `killed` 且 `weak` 不是 true;任一筆不是 → none」

**K2 配方與 covers 讀工作樹筆記,沙盒跑 HEAD,版本綁定沒涵蓋配方宣告**
severity: minor
blocking: 否——只影響涵蓋宣告是否已提交,v1 只提醒。
`_kill_read_recipes` 讀工作樹(`scripts/lumos:13041`),沙盒是 detach HEAD(`scripts/lumos:13108`);kill-add --covers 沒提交就 guard kill,covers 來自未提交筆記而 head_sha=HEAD,判 strong,推出去的筆記沒有這條 covers;平台 repo 髒只印警告(`scripts/lumos:13096`)。建議警告點名筆記或 kill-log 加 dirty 欄當弱證據。
引句:「之後改了測試或受測程式,破壞測試紀錄就不再有效,要重跑破壞測試再重表態。」

**K3 合約候選第二條宣稱強度比機制強**
severity: minor
blocking: 否——措辭與機制落差。
背書只在寫表態那刻快照;寫完後同一版又跑出 survived,推送前仍讀到舊 strong;合約文字應改成「寫表態當下」或在天花板補一條並掛回頭條件。
引句:「背書只認在有效版本上跑的破壞測試,且涵蓋該題的每條配方在有效版本上的每一筆都是非弱的 killed。」

**K4 天花板第 5 條對已刪配方描述不準**
severity: minor
blocking: 否——文件精度。
配方住在筆記,筆記不是簿記檔,刪配方並提交後先前紀錄立即失效;仍被算進去的只有刪了沒提交,應併入 K2。
引句:「在同一版程式上跑過、之後才從筆記刪掉的配方,它的紀錄仍會被算進去,直到程式再改一版。」

**K5 步驟 3 壞行容錯太窄**
severity: minor
blocking: 否——只造成讀取失敗的 none。
head_sha 非字串讓 subprocess 丟 TypeError,`_codeloop_record_valid` 只接 TimeoutExpired(`scripts/lumos:37141`),整題讀取失敗;test/platform 非字串同樣;快取不跨題、寫表態沒有總預算。建議逐行 try、型別不對略過、以 sha 為鍵快取給八題共用。
引句:「逐行解析,不是合法 JSON 或不是物件的行略過;`covers` 不是清單就當空清單。」

**K6 配方身分雜湊沒寫分隔方式**
severity: minor
blocking: 否——實作細節。
直接串接會碰撞;應用 json.dumps([invariant, file, old]) 並讓 kill-add 去重與雜湊共用同一支函式。
引句:「**配方身分**=invariant、file、old 三者合起來的雜湊」

**K7 步驟 4 失敗原因的「都」字有歧義**
severity: minor
blocking: 否——措辭。
應寫成「平台或名字任一不符」並明列三種失敗各自原因。
引句:「若平台或名字都對不上,原因改成」

**K8 head_sha 取得與建沙盒是兩個獨立 git 呼叫**
severity: minor
blocking: 否——競態窗極小,但同工作目錄多會談是本 repo 常態。
現行 rev-parse(`scripts/lumos:13090`)後才 worktree add(`scripts/lumos:13108`);應一次取完整 sha 並當 worktree add --detach wt <sha> 的參數。
引句:「`head_sha`:那一組平台跑破壞測試時的完整 HEAD(存在每一筆自己身上,不是迴圈外的共用變數)」

實務隱患:併發見 K3、K8;效能見 K5;資源、相容、輸出純度無。用詞、題目、配方宣告、推送前檢查、開關、派工鏡頭、驗收條款、回退:已讀,無 finding。

最嚴重 severity:major;blocking 共 1 條(K1)。
