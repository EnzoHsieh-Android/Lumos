# code-android寫法回合結束檢查 r1 收貨(2026-11-06)

範圍:`d241a3212..41f1b9abc`(乙線實作兩個提交,底是合入第三批的整合分支),tier high。材料 4521 行拆四包:甲(scripts/lumos、check.py、merge-claude-settings.py,1277)、乙(四支鉤子,1203)、丙(測試,1611)、丁(筆記與型錄,430)。七席:正確性(甲,角色卡)、邊界(乙)、資源(甲)、合約(丙)、通才(乙丁)、資安(整份 4521,照規矩不拆,範圍過大)、架構對齊(甲乙 2480,範圍過大:要同時看主程式與鉤子才判得出第二種做法)。圖譜鏡頭起點是合併提交、不在主線,派工詞直接點名計劃與四篇家。

## 收貨三道

- 正規化:六份已正規化;資安席等級寫在列表項,`report-normalize --write` 純格式搬移 3 處。
- quote-check:七份對整份 r1-snapshot.patch 全數錨定。
- refcheck:全對得上。

## 重現表

| 席-條 | 怎麼試 | 結果 |
|---|---|---|
| 正確性-F1 | 席位臨時 repo:lint.json 用 `--filter {LINT_FILES}`,檔名 `app/x$(touch${IFS}PWN2).kt`,跑 `lint-new --worktree --json` 後 repo 根出現 PWN2 | HIT |
| 資安-F1 | 席位臨時目錄:檔名含反引號與分號,`_lint_waive_cmd` 先 shlex.quote、`_safe_path` 再把反引號換成單引號,印出的放行指令引號被提前閉合 | HIT |
| 通才-F1、邊界-F1 | 讀 `_reason`:waive_cmd 過 `_safe_path` 截 160 字、整段截 1490 字;邊界席實跑 6 條告警只剩前 3 條、結尾提示消失 | HIT |
| 正確性-F2、資源-F2 | 兩席各自實跑新增 `app/sp ace.kt`:`ValueError: invalid literal for int() ... b'missing'`、rc1 沒 JSON、鉤子靜默放行 | HIT(兩席獨立) |
| 資源-F1 | 席位實測刪 200 個 5MB 已追蹤檔:約 9 秒、最大常駐約 4GB、回 no-files | HIT |
| 邊界-F2 | 讀 `_hookevent.py` guard 文件:內部吞掉逾時要自己 mark;新鉤子全無 mark 呼叫;席位實跑逾時記成 ok | HIT |
| 架構對齊-F1、合約-F1 | 圖譜 `Systems/hook信任邊界` 2026-09-08 訂正段:會讓安全檢查失效的共用邏輯照逐字複本加守衛,只是功能退化的才可走共用模組;`_trusted_lumos` 決定執行哪一份 lumos,屬安全邊界。合約席實跑把 `sh._trusted_lumos()` 換成 `which("lumos")` 加註解,守衛 21 passed | HIT |
| 架構對齊-F2 | 對照 `check-graph-sync.py` `_stop_mark_path`/`_stop_mark_write` 與新鉤子 `_name`/`_claim` | HIT |
| 其餘 minor | 讀材料與席位附的 file:line,合約席改壞實驗附指令與結果 | HIT |

## 設計審漏網

`Systems/hook信任邊界` 的既有規則(安全邊界的共用邏輯照逐字複本)在設計審時沒被讀到:計劃〈PRIOR-ART〉⑧寫「既有鉤子之間共用只有一種做法——底線開頭的共用模組」。照設計審手冊記逃逸(`loop escape android寫法回合結束檢查與改檔前推列 --stage code-loop`)。

## 先查世界

PRIOR-ART:命令注入——Python 官方 subprocess〈Security Considerations〉:不開 shell 時所有字元(含 shell 特殊字元)都能安全傳給子程序;開 `shell=True` 時引號由應用程式自己負責(https://docs.python.org/3/library/subprocess.html#security-considerations )。採用:工作樹模式不再把命令字串交給 shell,白名單通過後由程式組參數清單、`shell=False` 執行,SARIF 輸出由程式自己接到檔案;同一類「消毒發生在加引號之後」的放行指令,改成先消毒各組成再 shlex.quote,印出後不再改字元也不截斷。排除:繼續補白名單字表(同一類第二次被打穿,依手冊換形狀)。
PRIOR-ART:git `cat-file --batch` 對不存在物件輸出 `<object> missing`(https://git-scm.com/docs/git-cat-file#_batch_output ),object 名可含空白;採用:以行尾 ` missing` 判,不靠切詞數。
PRIOR-ART:鉤子共用邏輯——本 repo 既有規則 `Systems/hook信任邊界`(上表),照它分流,不翻案。

## 分組與去向(全數折入,除註明者)

- 甲 shell 執行與放行指令:正確性-F1、資安-F1、通才-F1、邊界-F1(major);通才-F2(minor)→ 工作樹模式改參數清單不開 shell;放行指令先消毒後 quote、不截斷;擋停訊息按條數累加到上限、結尾提示行保證留得下。
- 乙 靜默失效:正確性-F2、資源-F2、邊界-F2(major);邊界-F3、F4,資安-F3,正確性-F3,資源-F4,通才-F4(minor)→ cat-file 以行尾判 missing;逾時與失敗照 `_hookevent` 合約 mark;起點檔與 payload 型別錯放行不丟例外;Windows 沒有 killpg 時跳過;`LUMOS_SKIP_LINT_NEW` 生效時印一行;SIGTERM 處理器一併刪暫存 SARIF;SIGINT 與例外路徑也收工具群組;Popen 到登記之間擋 SIGTERM。
- 丙 資源:資源-F1(major);資源-F3、合約-F2(minor)→ 只在需要配對時才讀刪除檔內容,50 支上限在讀內容之前判;補「剛好 50 支」與上限值的測試。
- 丁 鉤子共用分流:架構對齊-F1、F2、合約-F1(major);合約-F7、架構對齊-F7(minor)→ 依 `Systems/hook信任邊界`:`_trusted_lumos` 與預算函式回到逐字複本、守衛恢復逐字比對;標記檔名消毒與 O_EXCL 佔名額搬進 `_hookshared`(功能類,兩道安裝守衛照加);匯入純度守衛只對匯入共用模組的那支放行列目錄,docstring 跟著改;收程序群組照複本規則處理。
- 戊 其餘 minor:通才-F3、F5、F6,架構對齊-F3、F4、F5、F6、F8,合約-F3、F4、F5、F6 → 各自照席位建議修;合約-F6(.kts)裁定:決策表只管 Kotlin 原始碼,`.kts` 不推、鉤子不送 `delta_new`,補案例。
- 資安-F2(git clean filter 藉 `git status` 執行):既有 `check-graph-sync.py` 同一個洞早已存在,這次只多一個呼叫點 → 這輪在新呼叫點加 `-c filter` 防護能做就做,做不到就開 Issue 記同族所有呼叫點(minor,折入:新呼叫點)。
