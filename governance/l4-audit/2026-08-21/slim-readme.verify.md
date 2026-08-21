C1 [✅] 開頭三句聲明「精簡版目的只有一個:讓接手的人能讀懂既有專案留下的知識圖譜」,且全文（含〈不要跑哪些〉節）不假設讀者已裝/讀過完整版 | 證據: slim/README.md:1-3

C2 [❌] test_lumos.py 實際檢查的 8 個 key+1 個懸空引用檢查,與主張列的 7 項不符——尤其⑦「凍結聲明/凍結快照」已被 2026-08-19 移除、改成檢查「lumos update」/〈更新方式〉章（測試函式自己的 comment 就寫「取代凍結聲明」）；主張①「怎麼裝(install.sh)+lumos --help」則完全不在檢查 key 清單裡 | 證據: scripts/test_lumos.py:17979-17989（8 個 key: lumos search/lumos context/lumos contracts/鐵則/移除的是入口不是全部程式碼/lumos update/install-hooks.sh/doctor）；slim/README.md 全文已無「凍結快照」字樣（`grep 凍結` 僅命中 177 行的「血換來的鐵則」誤配,無實質「凍結聲明」內容）

C3 [✅] t_slim_readme_assertions 確實 9 checks 全過 | 證據: `python3 scripts/test_lumos.py -k slim_readme` 輸出「9 passed, 0 failed」（8 個迴圈 check + 1 個懸空引用 check，見 scripts/test_lumos.py:17989,18023-18024）

C4 [❌] 實測 `-k slim` 為 474 passed, 0 failed,不是 217 | 證據: `python3 scripts/test_lumos.py -k slim` 輸出「474 passed, 0 failed」

C5 [❌] 實際 `slim-scan.py slim/README.md --json` 回傳 6 個候選,含 4 個 token 沒錯（init×2/self-audit/signoff）,但另外 2 個是 `design-loop`(form=skill-name)、`code-loop`(form=prose)——**不是**「均為帶 lumos 前綴的形態」；且完全沒有 `update` 候選（update 已於 2026-08-19 併入 KEEP 白名單，不再是懸空引用類別）,與主張「僅含 4 類 token(init/update/self-audit/signoff)」不符 | 證據: `python3 scripts/slim-scan.py slim/README.md --json` 輸出 total=6，含 design-loop/code-loop 兩筆非 prefixed 形態；scripts/slim-scan.py:35 KEEP 集合已含 update

C6 [❌] README〈⚠ doctor 有些建議指向本包沒給的指令〉段落列的未交付指令是 `lumos init`／`lumos self-audit`／`lumos signoff`（三支），**不是**主張所寫的「init/update/self-audit」——原文明講「`lumos update` 曾在此清單——本版起它**存在**了」,即 update 已從未交付名單移除，與主張直接矛盾 | 證據: slim/README.md:207（「已知至少有 `lumos init`、`lumos self-audit <node>`、`lumos signoff <node>`…`lumos update` 曾在此清單——本版起它存在了」）

C7 [❌] 〈怎麼裝〉段落兩行版指令是 `~/.lumos-slim/install.sh`（帶固定路徑前綴直接執行），全文找不到字面 `./install.sh` 這個形式（〈更新方式〉節也只寫「重跑 `install.sh --force`」不帶 `./`），不算主張所稱的「慣用形式 `./install.sh`」；一行版(curl|bash)與兩行版並列本身是對的 | 證據: slim/README.md:62-68(一行/兩行安裝並列，兩行版第 68 行為 `~/.lumos-slim/install.sh`)；`grep -n "\./install"` 全文零命中

C8 [❌] 〈怎麼移除〉段落原文明講是「**五步**」（bin/skill目錄/~/.lumos-slim/CLAUDE.md/manifest 共 5 條），不是主張所稱的「四步驟」；rc 三段式語意(0/1/2)與 bin 比對基準分兩層(manifest優先、~/.lumos-slim/scripts/lumos 備援)這兩部分描述正確 | 證據: slim/README.md:135(「下面五步各自獨立判斷、各自執行、互不阻擋」)，ol 列表 1-5 項見 139-144 行

C9 [✅] 〈`~/.lumos-slim` 是什麼〉獨立節存在，明講兩行版安裝不會建立此路徑（正常用法非錯誤操作），比對基準已改優先讀 manifest、此目錄留不留不影響卸載 | 證據: slim/README.md:153-161

C10 [✅] 〈會不會動我專案的 CLAUDE.md〉整節存在，說明有完整版區塊則整段取代原位置（非搬檔尾）、沒有則插檔首標題後、取代前 base64 備份藏在精簡版區塊自己的 HTML 註解裡（不新增檔案） | 證據: slim/README.md:88-109（第 94 行「整段移除…先把完整版原文位元組級備份」；第 98 行插入位置說明；第 100 行 base64 備份機制）

C11 [✅] README 內確有「取代後 `LUMOS:GRAPH-DISCIPLINE` sentinel 不存在，Check D 自動略過」的原文句，非舊版「刻意不觸碰另一個 sentinel」說法（且全文搜尋不到後者字樣） | 證據: slim/README.md:215（「取代後 `LUMOS:GRAPH-DISCIPLINE` 這個 sentinel 就不存在了，Check D 因此自動略過」）

C12 [✅] 〈注入目標守衛（裝到哪裡才安全）〉節存在，緊接在〈會不會動我專案的 CLAUDE.md〉之後，列三層守衛（不像專案根拒絕/拒絕裝進來源repo/動手前印大聲目標路徑）並說明 `--here` 逃生閥 | 證據: slim/README.md:111-119（標題行111，緊接88行節之後）；`--here` 說明見120行

C13 [✅] 〈支援平台〉節存在，插在標題之後、〈怎麼裝〉之前（第5行 vs 第54行），聲明 macOS/Linux/Windows 三平台、單一 Python 邏輯來源+薄殼架構，列各平台一行安裝指令（Windows 為 `irm … | iex`），並講 `~/.local/bin` 不在預設 PATH 需自行加入（分平台講法） | 證據: slim/README.md:5-21

C14 [❌] 主張「Windows 路徑未經真機驗證」與 README 現況直接矛盾——現行內容標題即「★Windows 真機驗證狀態（2026-08-03 更新）★」，明講「三支 `.ps1` 的開頭曾長期掛著『沒有在真機 Windows 上跑過』。**已經兌現了**」，並附三輪真機實測結果表（含 `.cmd` shim 可執行、`$LASTEXITCODE` 型別正確等具體證據） | 證據: slim/README.md:23-39（真機驗證狀態標題與證據表）；主張所述「開發機為 macOS 沒有 Windows/PowerShell,Windows 路徑未經真機驗證」與此段內容過時不符

C15 [❌] 主張②「三支 `.ps1` 改成 `$global:LASTEXITCODE=$LASTEXITCODE`…修法本身完全沒有真機驗證」與 README 現況矛盾——README 證據表明列「`$LASTEXITCODE` 對呼叫端可見且型別正確 | 實測成功 `rc=[0]`、失敗 `rc=[2]`，皆 `Int32`」,即該行為已有真機驗證；主張①（.cmd shim 的 `shutil.which()`/PATHEXT 細節未驗）與現況「仍然沒有真機證據的」清單裡的「PATHEXT 的完整解析細節」大致對應，但整條主張因②與現況矛盾而不成立 | 證據: slim/README.md:23-45（真機證據表第5列 `$LASTEXITCODE`；「仍然沒有真機證據的」清單第一項 PATHEXT）

✅7 ❌8 ❓0 ⏭0
