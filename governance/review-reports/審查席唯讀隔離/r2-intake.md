# 審查席唯讀隔離 r2 收貨紀錄

- 四席全新報告(r2-snapshot.md,計劃 sha fdf94984…;外家席依 Enzo 指示不派)。報告收到時先存 repo 外,四席全交回才搬進卷證。
- 資安席首派被安全分類器中斷,交回的「severity: clean」是佔位、不採用、沒存檔;改成「防禦面覆蓋檢查」的框架重派(只對型別檔與設計文字判斷,不實際嘗試繞過),這份才是本輪的資安席報告。重派那份的引句行起初沒包「」,退回該席只補格式,它重交的全文跟原檔只差引句外框,卷證存的是補了外框的版本。
- 引句全數錨定(四席);refcheck 只有資安席一處佐證路徑找不到(相對路徑寫法),不影響判讀。
- 編號:r2 加席位字母加條號(c 正確性、e 邊界、s 資安、a 架構對齊)。
- 三席 major,而且大半在同一類:逐詞解析 Bash 指令。r1 這一類也最多,連兩輪同一類 → 換形狀。Enzo 2026-10-06 裁「粗擋+事後查」(決策 d3 取代 d2):Bash 不再逐詞解析,只粗擋對外動作;repo 內的改動改成審查席答完時比對。很多條因此不再適用(那段規則整個拿掉),處置寫「整類拿掉」。

## 編排者重現表

| id | 宣稱 | 重現 | 結果 | 處置 |
|---|---|---|---|---|
| r2c1 / r2e8 | 唯讀 git 的 -c、-o 誤擋 | `git grep -c hi` 在臨時 repo 輸出 `a:1`,合法唯讀 | HIT | 折(整類拿掉:不再判 git 選項) |
| r2c2 | -C 帶 $ 就擋,mktemp 寫法全擋 | 讀規則:斷詞後值是字面 `$T`,照字面必擋 | HIT | 折(整類拿掉;S3 放行例含 mktemp 寫法) |
| r2c3 | git init 路徑、clone、cd 後 commit 被擋 | 讀規則:只認 -C,屬實 | HIT | 折(整類拿掉;S3 放行例含 clone) |
| r2c4 | heredoc 內文被當命令位置 | 讀規則:斷詞沒提 heredoc,屬實 | HIT | 折(粗擋明寫 heredoc 裡也判、寧可誤擋並教換寫法) |
| r2c5 | 剩餘段含 .. 接在真實路徑後被判成暫存區 | `realpath('/tmp')+'/nonexist/../../Users'` 得 `/private/tmp/nonexist/../../Users`,字面前綴是暫存區 | HIT | 折(.、..、空段擋;懸空連結擋;欄位名分清) |
| r2c6 / r2s3 / r2e9 | Grep/Glob 萬用字元取不到真實路徑、上層目錄搜尋撈到暫存處 | 讀規則屬實 | HIT | 折(搜尋範圍=path+固定段,祖孫關係即擋) |
| r2c7 / r2e2 / r2e3 | 卷證資料夾同輪檔名判不出、迴圈編號對不到資料夾 | 掃 canary 帳與卷證資料夾:席位報的命名不齊屬實 | HIT | 折(卷證資料夾不保護,只保護暫存處) |
| r2c8 / r2e6 | 包裝詞表不全、bash -lc、stdin 餵 sh 繞過 | 讀規則屬實 | HIT | 折(整類拿掉:粗擋對整串字串判,不管包在哪) |
| r2c9 / r2a3 | marketplace update 跑了無害沒證據 | 讀 `_claude_do`:非零丟 RuntimeError,屬實 | HIT | 折(非零只警告、裝完列表確認、實作前隔離實測) |
| r2c10 | 白名單漏 TodoWrite、TaskOutput、TaskStop、Skill、Task | 讀規則屬實 | HIT | 折 |
| r2c11 | 暫存根有多個、保護範圍不明 | 讀規則屬實 | HIT | 折(暫存根列齊、暫存處整個資料夾) |
| r2e1 | 輪次格式太窄、寫壞靜默放行 | 掃 canary 帳 round 欄:`r3-dref` 3 筆、`r4-dref-delta` 2 筆、`r5-recap` 2 筆不合 `^r[0-9]+[a-z]?$` | HIT | 折(輪次不限格式、寫壞擋下派工、BOM 與全形空白) |
| r2e4 / r2s4 | repo 在暫存區時寫入保護全關、共用材料可改 | 讀規則屬實;S13 原情境自相矛盾 | HIT | 折(寫檔只准席位工作資料夾;真機驗收的暫存 repo 改放家目錄下) |
| r2e5 | 斷詞失敗配 fail-open 等於放行 | 讀規則屬實 | HIT | 折(沒有斷詞器了;Bash 判斷出錯、超長即擋) |
| r2e7 / r2s1 | git -C 暫存區照樣 push、config --global、造 .git 檔導回真 repo | 臨時目錄造 `fake/.git` 內容 `gitdir: real/.git`,`git -C fake commit` 後 real 的提交數從 1 變 2 | HIT | 折(粗擋 git+push;repo 內改動交給事後查,事後查含提交、分支、worktree、設定檔) |
| r2e10 | 逾時放行沒留痕、等整批 | 讀規則屬實 | HIT | 折(逾時跳固定開頭提示;等整批寫進實務隱患) |
| r2e11 | 相對路徑只用會談 cwd | 讀型別檔 AgentSpawnInput 有 cwd | HIT | 折(寫檔要求絕對路徑;搜尋以派工時的工作目錄補全;Bash cd 寫進誠實界線) |
| r2s2 | Agent 的 isolation 能派出不受攔截的代理 | 型別檔 Agent 輸入有 `isolation?: "worktree" \| "remote"` | HIT | 折(帶 isolation 擋、subagent_type 限准用清單) |
| r2s5 | 漏 --config-env、黏寫與縮寫 | 讀規則屬實 | HIT | 折(整類拿掉:不再判 git 選項) |
| r2s6 | NotebookEdit 欄位叫 notebook_path | 讀型別檔屬實 | HIT | 折 |
| r2s7 | 網路外洩與 dangerouslyDisableSandbox 沒寫進誠實界線 | 讀規則屬實 | HIT | 折(寫進誠實界線) |
| r2a1 | 暫存處慣例跟使用者記憶寫的位置不同 | 讀記憶屬實 | HIT | 折(範圍第 6 點寫明改記憶) |
| r2a2 | TS 斷詞器要寫理由並對齊 Python | 斷詞器整個拿掉 | HIT | 折(整類拿掉) |

## 換形狀後的新規則要跟著驗的

- 事後查用的 `turn.complete` 附文字,編排者收不收得到沒實測:寫進誠實界線並綁 S14 真機驗收,帶 REVISIT。
- 事後查自己跑 git:帶 `-c core.fsmonitor=false`、逾時 10 秒,引擎跑 git 時本來就關掉 repo 掛鉤(型別檔 `$.process.run` 說明)。
