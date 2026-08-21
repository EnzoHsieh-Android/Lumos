C1. slim/README.md 是「公開精簡版交付內容之一」,是新人 clone 到精簡版後唯一的自足說明文件,不假設讀過完整版任何文件 | 預期驗證點: slim/README.md 開頭/簡介段落

C2. t_slim_readme_assertions 鎖住 README 七項必要內容:①怎麼裝(install.sh)+怎麼確認(lumos --help) ②進場三步 search→context→contracts ③frontmatter 四鐵則(逐字轉錄自 reference.md) ④合約鏈是什麼+doctor 為什麼擋+怎麼解 ⑤範圍聲明(功能子集,不含對抗審計;含「移除的是入口不是全部程式碼」逐字句) ⑥明講不要跑 install-hooks.sh、不要照 CLAUDE.md clone 完整版跑 install.sh,且誠實承認「本 README 壓不住專案自己的 CLAUDE.md」 ⑦凍結聲明(逐字句「凍結快照」) | 預期驗證點: scripts/test_lumos.py t_slim_readme_assertions 函式內容斷言

C3. t_slim_readme_assertions 共 9 checks,全部通過 | 預期驗證點: `python3 scripts/test_lumos.py -k slim_readme`

C4. slim 相關測試共 217 checks 全綠 | 預期驗證點: `python3 scripts/test_lumos.py -k slim`

C5. scripts/slim-scan.py 對 slim/README.md 掃描(`--json`)的候選集合等於已審查白名單,僅含 4 類 token(init/update/self-audit/signoff),且均為帶 `lumos ` 前綴的形態,無非預期懸空引用殘留 | 預期驗證點: scripts/slim-scan.py 輸出行為 / slim/README.md 內容

C6. README 內有一段揭露:「doctor 有些檢查會建議跑 lumos init/lumos update/lumos self-audit,這三支未交付,看到請忽略」,並說明 CLAUDE.md 相關檢查(Check D)在本版無修復路徑,是刻意的 | 預期驗證點: slim/README.md doctor 相關段落

C7. README〈怎麼裝〉段落的安裝指令用慣用形式 `./install.sh`(而非早期為遷就掃描器改寫的「用 bash 執行 install.sh」措辭),同時並列一行安裝(curl | bash)與兩行版(先 git clone 再跑 install.sh) | 預期驗證點: slim/README.md〈怎麼裝〉段落

C8. README 有獨立的〈怎麼移除〉段落,說明四步驟彼此互不阻擋,並用三段式 rc 語意描述結果(0=全成功,1=安全性跳過非硬錯誤,2=真正錯誤),bin 比對基準分兩層(manifest 優先、`~/.lumos-slim/scripts/lumos` 備援) | 預期驗證點: slim/README.md〈怎麼移除〉段落

C9. README 有獨立的〈`~/.lumos-slim` 是什麼〉段落,說明兩行版安裝本來就不會建立此路徑(屬正常用法非錯誤操作),且比對基準已改成優先讀 manifest,此目錄留不留都不影響卸載 | 預期驗證點: slim/README.md〈~/.lumos-slim 是什麼〉段落

C10. README 有〈會不會動我專案的 CLAUDE.md〉整節,說明:若專案已有完整版紀律區塊,安裝器會整段策展取代(原地替換);若沒有,則插入檔案首個標題之後(非純檔尾附加);取代前會把原內容以 base64 備份藏在精簡版區塊自己的 HTML 註解裡(不新增檔案) | 預期驗證點: slim/README.md〈會不會動我專案的CLAUDE.md〉段落

C11. README〈會不會動我專案的 CLAUDE.md〉段落內,doctor Check D 的說明是「取代後 `LUMOS:GRAPH-DISCIPLINE` sentinel 不存在,Check D 自動略過」,而非舊版「刻意不觸碰另一個 sentinel」的說法 | 預期驗證點: slim/README.md 對應段落文字

C12. README 有〈注入目標守衛(裝到哪裡才安全)〉一節,插在〈會不會動我專案的 CLAUDE.md〉之後,列出三層守衛(不像專案根即拒絕/拒絕裝進 lumos 工具鏈來源 repo/動手前印大聲目標路徑),並說明 `--here` 逃生閥用法 | 預期驗證點: slim/README.md〈注入目標守衛〉段落

C13. README 有〈支援平台〉節,插在標題之後、〈怎麼裝〉之前,聲明支援 macOS/Linux/Windows 三平台,採單一 Python 邏輯來源+薄殼分工架構,並列出各平台一行安裝指令(Windows 為 `irm ... | iex` 形式),提及 `~/.local/bin` 不在預設 PATH 需自行加入(分平台講法) | 預期驗證點: slim/README.md〈支援平台〉段落

C14. README〈支援平台〉段落內含誠實標記,聲明:開發機為 macOS 沒有 Windows/PowerShell,Windows 路徑未經真機驗證;`install.py`/`uninstall.py` 的 Windows 分支僅靠 `LUMOS_SLIM_SIMULATE_WINDOWS=1` 環境變數注入驗過分支邏輯本身;`.cmd` shim 真機行為、PATH 真實生效方式、三支 `.ps1` 薄殼本身皆未驗證 | 預期驗證點: slim/README.md〈支援平台〉誠實標記段

C15. README〈支援平台〉誠實標記段追加兩項未驗清單:①`.cmd` shim 直譯器 fallback——`install.py` 的 `_pick_windows_interpreter()` 用 `shutil.which()` 於安裝當下偵測,但 `shutil.which()` 在真實 Windows PATH/PATHEXT 下的實際解析行為未驗 ②三支 `.ps1` 收尾改成 `$global:LASTEXITCODE = $LASTEXITCODE`(不再呼叫裸 `exit`),修法本身完全沒有真機驗證 | 預期驗證點: slim/README.md〈支援平台〉段落 / slim 安裝相關 .ps1 腳本內容
