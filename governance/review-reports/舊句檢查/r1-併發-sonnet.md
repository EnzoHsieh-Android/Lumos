severity: major

# r1 併發與資源鏡頭(併發-sonnet)

量測環境:clone-ns(工具鏈,45 支 .py + scripts/lumos 2.2MB 的無副檔名 Python)與 `git clone --shared /Users/enzo/rtb-mainwt`(rtb,2756 檔、276 支 .py、8.1MB、666 提交),直譯器 /opt/homebrew/bin/python3,唯讀。量測腳本在 scratchpad/os-r1 同層 bx-conc/m.py。

## 量測摘要(供各 finding 引用)

- 現況基線:`lumos drift check --diff HEAD~3..HEAD`(工具鏈)1.98 秒、HEAD~30..HEAD(rtb)1.87 秒。所以 m1 冷快取 3–7 秒是現有整段的 2–4 倍,暖快取才是 +0.3 秒等級。
- 冷剖終點整個 repo 的定義(只做 def/class 名,ast.parse):rtb 265 支 2.7 秒;工具鏈 45 支 2.2 秒(其中 scripts/lumos 一支 1.0 秒、峰值記憶體約 257MB)。約 0.3 秒/MB 原始碼。
- 讀內容:一個 `git cat-file --batch` 讀完 rtb 276 支 .py 0.08 秒;逐支 `git show` 讀同 276 支 4.9 秒(約 60 倍)。
- 快取大小:rtb 265 支定義集合 JSON 254KB(約 1KB/筆),推算 20000 筆約 20MB;JSON 載入 0.1–0.2 秒、寫出 0.07–0.15 秒(用 2KB/筆合成資料實測 41MB:dump 0.15 秒、load 0.20 秒、行程峰值 ~480MB)。
- 單檔記憶體:11.5MB 的生成式 .py(15 萬個函式)ast.parse 3.8 秒、峰值 RSS 3.2GB(約 280 倍原始碼大小)。
- `git rev-parse --git-common-dir`:在根目錄印 `.git`,在子目錄印 `../.git`(相對於目前目錄);連結工作樹裡印主樹 `.git` 的絕對路徑。
- 無副檔名檔:工具鏈 14 個、rtb 7 個,首行判 shebang 要讀內容,量小。

## 六組核心(A–F)從併發資源鏡頭的判定

- A 判定另開函式不進 must:資源面做得出來。另開函式共用同一個 deadline 物件,c1–c5 不會被 m1 拖累(m1 排在後面、自己看預算);唯一實作陷阱見 F5(早退)。
- B 兩個開關控制流:與資源無關,本鏡頭無 finding。
- C 表態名稱集合:與資源無關,本鏡頭無 finding。
- D 時間到 warn/block:warn 做得出來;block 有 F3 的收斂問題(冷快取時間到 → 算要處理,快取卻沒被填,下一次仍時間到)。
- E 三類消失判準與終點剖不動:判準本身不在本鏡頭;但「終點整個 repo」的成本模型有 F1(讀取方式)、F4(單檔記憶體)兩個洞。
- F 字眼表:與資源無關,本鏡頭無 finding。

## F1 快取鍵怎麼拿到、內容怎麼讀都沒規定,順著既有 reader 做會把冷/暖成本各放大一個量級
severity: major
blocking: 是
引句:「每個 blob 的定義集合以 blob 雜湊為鍵」
file: `scripts/lumos:23638`
file: `scripts/lumos:23683`
file: `scripts/lumos:23985`
1. 「暖快取約 0.3 秒」成立的前提是:終點樹每個 .py 的 blob 編號從 `ls-tree` 直接拿(`_nodehome_list(root, tip, oids)` 有 oids 參數可填),命中就不讀內容。spec 只寫「以 blob 雜湊為鍵」,沒寫編號從哪來。若照 PRIOR-ART 的「沿用 `_drift_probe_is_py(p, txt)`」——這支簽名要內容 `txt`——與既有 `_nodehome_reader`(每支一次 `git show`,見 `scripts/lumos:23683`)實作,就得先讀內容再自己算雜湊,暖快取也每次讀全部 .py。實測 rtb 276 支逐支 `git show` 4.9 秒,批次 0.08 秒;等於暖快取 0.3 秒的承諾變成 5 秒以上。
2. 冷快取同理:逐支讀 4.9 秒 + 剖 2.7 秒 = 7.6 秒,剛好是 spec 引的「7.4 秒」上緣;spec 引的實驗值若是批次讀出來的(未查證 ⚠),實作照 reader 做就多出一個量級,且隨 .py 檔數線性長(5000 支 .py 的 repo 逐支讀約 90 秒,單這一步就吃光 60 秒預算)。
3. 既有的批次讀取 `_nodehome_cat_blobs`(`scripts/lumos:23985`,一個行程讀完,註解記載過 600 個行程 13.5 秒的教訓)就是解法,但 spec 沒點名。
4. 起點版(範圍裡改到的檔)同理,要一次批次讀;起點與終點的無副檔名 shebang 檔也要進批次,否則又多出逐檔讀。
建議:做法 1 明寫「終點與起點的 blob 編號從 ls-tree/diff 拿,命中快取不讀內容;沒命中的一次 `_nodehome_cat_blobs` 批次讀」,並把「一次推送 git 行程數不隨檔數成長」(預期 ls-tree ×1–2、name-status ×1、cat-file --batch ×2–3,約 5–6 次)寫進 S5 的可測條款。

## F2 快取鍵只有 blob 雜湊:抽取邏輯升級、剖不動的結果、Python 版本都會讓舊項目永遠錯
severity: minor
blocking: 否
引句:「讀寫失敗或檔壞掉都當沒有快取、照常跑」
1. blob 雜湊對內容不變,但值是「`_drift_py_names` 加類別層指派、加 add_argument 旗標」這支抽取函式的輸出。只要日後任何一次修抽取(例如審查修掉旗標抽取的洞),快取檔在 `.git/lumos/` 不進版控、也不隨 lumos 更新清掉,舊項目永遠命中、永遠是舊格式或舊漏洞的結果。工具是 symlink 分發、各機器版本不一,同一個 common-dir 被不同版本 lumos 讀寫時互相污染。壞掉的表現是「名稱被當成消失」的假 `m1`,不是失敗,所以「壞檔當沒快取」的防線接不住。
2. 剖不動(None)要不要快取沒寫。`_drift_py_names` 把 MemoryError / RecursionError 也回 None(`scripts/lumos:26790`);這類是暫時的(記憶體壓力),若寫進快取就固定成「剖不動」,之後每次終點都走文字比對、輸出「N 支剖不動」。反過來不快取則每次重剖一支必失敗的大檔。
3. 剖不剖得動也隨 Python 版本(下限 3.14,但新語法在更高版本才剖得動)變。
建議:鍵或檔頭帶 schema 版本號 + Python 主次版本;None 只快取 SyntaxError/ValueError(確定性),MemoryError/RecursionError 不快取。

## F3 快取何時寫、怎麼淘汰、暫存檔名沒定:時間到永不收斂,且沒排除固定暫存名互搶
severity: minor
blocking: 否
引句:「最多留 20000 筆,超過時丟掉最久沒用到的」
file: `scripts/lumos:14930`
1. 「最久沒用到」需要每筆記一個使用戳,而暖快取推送的所有命中都是「用到」——要更新戳就得每次推送重寫整個檔(推算 20MB 上下、載入 0.1–0.2 秒 + 寫出 0.1 秒);不更新就退化成「最久沒寫入」,常駐的老 blob 會先被丟。spec 沒說戳是牆鐘還是計數,也沒說命中時要不要落檔。建議:戳用單調計數或日期,命中只在戳落後超過一天才落檔。
2. 淘汰沒排除「這次推送的活躍集合」:終點整個 repo 的 .py blob 全是這次要用的。若某 repo 的 .py blob 數 > 20000(大型 monorepo)每次都在淘汰自己剛用的,快取等於無效、每次冷跑。目前 rtb 265、工具鏈 45,離上限兩個數量級,所以是門檻條件不是現況;要在 spec 寫「活躍集合超過上限就不存(或上限取 max(20000, 活躍集合×2))」。
3. 時間到不落檔是最壞的一種:若實作只在完整跑完才寫(spec 沒說何時寫),則冷跑成本 > 剩餘預算的 repo(約 0.3 秒/MB 原始碼,60 秒約 200MB;CI 機器慢 2–3 倍時約 70MB,且 CI 每次是全新 checkout、沒有快取,永遠冷)永遠 incomplete;block 模式下 incomplete 算要處理,等於永遠擋,唯一出路 `LUMOS_SKIP_DRIFT_CHECK=1` 還會連 c1–c5 一起略過。建議:剖到哪存到哪(每 N 支或時間到前 flush),下次推送續。
4. 多工作樹/兩個推送同時寫:read-modify-replace 會 lost-update(A、B 各讀同一份、各加不同新項目,後 replace 的贏,先寫的項目消失),不損壞、只多剖一次,可接受;但 spec 只寫「寫入走暫存檔」,沒寫暫存檔名要每次唯一。同一個 repo 裡已有前例:`_write_lf` 的註解記載固定暫存名兩個行程互搶,實測六個同時跑六個都噴 FileNotFoundError(`scripts/lumos:14930`)。固定名時,兩個行程同時 open('w') 寫同一個暫存檔會互相截斷,A 自驗讀到的是 B 寫到一半的內容,可能驗過又替換出被截斷檔;下次讀到是壞 JSON 當沒快取,所以最終只是又一次冷跑(不會錯判),但會在兩工作樹同時推的 CI 之外的本機造成偶發 +5 秒。建議寫「暫存名帶 pid+隨機」照 `_write_lf`。
5. 共用目錄還要 mkdir(`.git/lumos/` 預設不存在),`--git-common-dir` 在子目錄印相對路徑(實測 `../.git`),必須 `git -C <root>` 取後再與 root 相接;唯讀 checkout/CI 的 `.git` 寫不進當沒快取(spec 已寫)。

## F4 單檔剖析吃記憶體是檔大小的約 280 倍,「剖檔不可中斷」沒有上限就不只是多一支的時間
severity: minor
blocking: 否
引句:「剖檔在行程內不可中斷,最壞多出一支檔的時間」
file: `scripts/lumos:26790`
1. 舊行為只剖「被推送改到的檔」;新行為是終點整個 repo(冷快取)每個 .py 都剖,所以 repo 裡任何一支 vendored / 生成式(protobuf、grpc、大型字典資料 .py)的大檔在第一次冷跑就被剖。實測 11.5MB 生成式 .py 剖 3.8 秒、峰值 3.2GB(約 280 倍);工具鏈自己的 scripts/lumos 2.2MB 就是 257MB、1 秒。
2. 「最壞多出一支檔的時間」在時間軸上成立,但記憶體不受預算管:`_drift_py_names` 接的 MemoryError 在 macOS/Linux 常態是先被 OOM killer 或壓縮/swap 拖死,接不到;推送前掛鉤行程被殺,`git push` 得到的是掛鉤失敗而不是「剖不動」。spec 的「記憶體或遞迴過深」例外組管不到這個。
3. 已有現成的上限機制:`_nodehome_cat_blobs_capped`(先 `--batch-check` 問大小、超過的不讀進記憶體,`scripts/lumos:23967`)。建議對超過上限(例如 2MB 或 3MB)的 .py 直接歸「剖不動」走既有的文字比對回退,並在輸出印「N 支太大略過」;順帶保證 spec 寫的「終點版有剖不動的檔時候選名稱再用文字比一次」不會因為這個路徑讓大檔名稱被當成消失。⚠ 上限值需要專案實測後定,這裡只給量級。

## F5 呼叫點與既有早退的關係沒寫:c1–c5 乾淨時 m1 會被跳過;預算檢查點也沒到 flush
severity: minor
blocking: 否
引句:「在既有 c1–c5/probe 那段之後呼叫」
file: `scripts/lumos:28238`
1. 現有 `cmd_drift_check` 在 `must` 與 `unknown` 都空時 `return 0`(核對 cmd_drift_check 尾段:`if not must and not unknown: return 0`),而 m1 最典型的情境正是 c1–c5 乾淨。照字面「之後呼叫」放在早退後面會讓 m1 只在 c1–c5 已有東西時才跑;放在前面又要處理 listed 的印出順序。S3 的四種組合測試(gate × old_sentence)可能沒有覆蓋「c1–c5 乾淨 + m1 有東西」這一格,建議 S3 補一格,或 spec 寫明「m1 在 must/unknown 早退之前跑」。
2. 資源面的答覆(使用者鏡頭的問題):m1 不會讓既有 c1–c5 受影響——它排在後面、共用同一個 `deadline`(`scripts/lumos:28261` 起算),c1–c5 先用先得;受影響的是 m1 自己(預算剩多少就跑多少)。真正的邊界是「最壞總時間 = 60 秒 + 一次不可中斷的剖檔/git 呼叫」,而不是 60 秒。這點 spec 寫了,不另標。
3. 記帳是每次有範圍的 drift check 一筆(含零筆)寫進 `docs/.governance-log.jsonl`。實測該檔已 93587 行、被版控追蹤,每次推送多 1 筆、最長 note 2000 字;`_append_governance_log` 類寫入是 `open(..,"a")` 追加,同機兩個推送同時追加不互毀;CI 上寫的是暫時 checkout,不回寫。兩週後的量估計可接受(每推一次一行,遠小於現有 drift-check 的 37 筆之外的其他閘),不標。

## 實務隱患(併發與資源類逐類)

- 快取檔多行程讀寫:F3(lost-update 可接受,暫存檔名要唯一);損壞讀取 spec 已寫當沒快取,接得住。
- 共用預算:F5(不影響 c1–c5;block 時間到算要處理,加上 F3-3 才有收斂問題)。
- 記憶體:F4。
- git 呼叫次數:F1。
- 20000 筆與「最久沒用到」要記什麼:F3-1、F3-2。
- 檔多大、讀寫多久:實測見量測摘要——20000 筆推算 20MB,讀 0.1–0.2 秒、寫 0.1 秒;不構成獨立 finding。
- CI 與本機同時:兩邊各自的 `.git`,不共用快取;CI 永遠冷,見 F3-3。
- 不可逆/金流/對外送出/資安:無,原因同 spec 已排除段(只讀、只印、只記帳)。

最高等級:major;blocking 共 1 條
