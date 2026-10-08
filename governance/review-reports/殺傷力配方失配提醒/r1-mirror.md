# 設計審 r1 折入核對:殺傷力配方失配提醒

核對對象:現稿 `negguard/docs/.../Projects/殺傷力配方失配提醒_計劃.md`;報告 6 份共 30 條 finding(正確性 9、併發 3、回滾 5、接手 5、架構 3、邊界 5;編號 c/k/r/h/a/b 照 r1-intake)。程式取 `negguard/scripts/lumos`。唯讀,沒改任何檔。

## 一、30 條逐條

結果:已處理 20、部分處理 10、沒處理 0。

| 編號 | 判定 | 現稿哪一句 / 缺什麼 |
|---|---|---|
| c1 (正確性F1) | 已處理 | 做法1「基準」:`git -C <平台根> rev-parse --show-toplevel` 得 repo 頂,`file` 從 repo 頂算;S5 加「平台根是子資料夾」。(PRIOR-ART 殘留舊說法見鏡像 M1) |
| c2 (F2) | 已處理 | 做法3 首條「在判重之後、真正寫入之前…只更新 --covers 就是既有那一條(用它自己的 platform)」;S2 |
| c3 (F3) | 已處理 | 做法2「先自己把 config.json 當 JSON 解析一次…load_platforms 只呼叫一次」;S4「壞 JSON 印這一段算不出來」。小補:`json.loads` 解出非物件(例如陣列)時 `load_platforms` 的 `cfg.get` 會丟 AttributeError,預解析應一併要求是 dict,現稿沒寫 |
| c4 (F4) 絕對路徑符號連結 | 部分 | 做法1 寫「絕對路徑的符號連結…都在 outside」,但函式是在工作目錄做 realpath;連結若指回同 repo 內的絕對路徑,解析後在 repo 內,函式判 ok,guard kill 在隔離樹裡判 error。現稿宣稱的機制產生不出這個結果,S5 預期 `outside ↔ error` 這格會紅;〈誠實界線〉也沒記這個差異。要嘛判斷函式另外偵測「路徑上有絕對目標的連結」,要嘛誠實界線寫明 |
| c5 (F5) | 已處理 | 做法3 提醒字面依 hits/missing/undecodable/outside/malformed 分寫;非 UTF-8 與讀不到合併寫「判 drifted 或讀檔出錯」(沒明說會讓整支 guard kill 當掉,可接受) |
| c6 (F6) | 部分 | 做法1 把 platform/invariant 型別不對列 malformed。缺:(a) 沒寫「先判是不是物件、再取平台」的順序(呼叫端取平台根發生在函式之前);(b) `invariant` 為 null 屬「無值」不算 malformed,印「invariant 前 30 字」時 `None[:30]` 仍會炸(guard kill 自己也這樣寫);(c) S3 沒有「字串配方 + null invariant + 真失配三條同批都列出」的測試格。做法5「逐條包例外保護」只兜底成「這條判不了」 |
| c7 (F7) | 已處理 | 做法2「★一次判定裡只呼叫一次★,給每條配方共用」 |
| c8 (F8) | 部分 | S7 改綁對照測試並釘 drifted、逃逸字面;但「kill-add 失配宣告前後 stdout 逐字相同、stderr 恰多一行」沒有條款或測試釘(S1 只講回傳碼與恰 1 次不印) |
| c9 (F9) | 已處理 | 實務隱患「rtb 現有 73 條配方、工具鏈 1 條」 |
| k1 (併發F1) | 已處理 | 同 c3 |
| k2 (F2) FIFO | 已處理 | 做法1「不是一般檔…→ missing(不開它,避免讀具名管線卡住)」 |
| k3 (F3) | 部分 | 半截檔:實務隱患「讀到寫到一半的檔」已寫。快取:只在實務隱患寫「同一支檔被多條指到時只讀一次」,做法1 沒有對應規格(也沒說以 realpath 為鍵);慢速網路碟無逾時沒處理(報告本身認為不構成錯誤) |
| r1 (回滾F1) | 已處理 | 做法5「用 `warn_soft` 印…全部對得上用 `ok()`」,設定讀不了列在同一組項目;S4 涵蓋 |
| r2 (F2) | 已處理 | 做法3 首條「被判重擋下的情況不跑、不印」;S1 |
| r3 (F3) | 已處理 | 回退末條「`[test:]` 會懸空…status 改 superseded 或在實作紀錄記一句」。(doctor-run 的 soft=N 歷史殘留報告自認無害,沒寫) |
| r4 (F4) | 部分 | 同 c8 |
| r5 (F5) | 已處理 | 同 c3;做法2 只呼叫一次也壓住「根不存在」警告重複 |
| h1 (接手F1) | 部分 | kill-rm 已加(做法4、S6),kill-add 提醒結尾附修法。缺:(a) P2 每條列項沒寫修法(做法5 沒指定 `advice=`),人從 doctor 看到失配不知下一步;(b) kill-rm 的身分是完整字串相等,見鏡像 M3,P2 只顯示前 30 字會讓使用者湊不出完整 invariant |
| h2 (F2) | 部分 | RETIRE-IF 改看 `check-p2` 事件、做法5 加 gov_events。缺:(a) `gov_events` 只在 `--ci` 才落帳(程式 3178–3186 行 `if ci:`),現稿沒寫誰的 doctor 會落帳;(b) 新閘名要登記進 `_KNOWN_GATES`(程式 6951 行,另有漂移釘測試比對全檔 gate 字面值),現稿沒提,漏登會紅 |
| h3 (F3) | 部分 | REVISIT 已寫回報方式、落點、0 / 1–3 / 4 條以上三段門檻。「1 到 3 條再等兩週」沒有次數上限,可能無限延後 |
| h4 (F4) | 已處理 | 誠實界線末條落點:Systems/guard-kill、skill guard 指令表補 kill-rm、路線圖 1a。(kill-add 的 `--file` 說明字串要改,見 M10) |
| h5 (F5) | 已處理 | 誠實界線第 2 條「先提交程式與筆記,再跑 guard kill」 |
| a1 (架構F1) | 已處理 | 同 c1 |
| a2 (F2) | 已處理 | 做法5「專案根用 doctor 既有、P 段同一個 `repo_root`;找不到就印沒有 docs/,跳過」;程式 1583–1586 行確為 vault 往上找 docs 的 parent |
| a3 (F3) | 已處理 | 做法1「對照測試」+ S5 |
| b1 (邊界F1) | 已處理 | 同 c1 |
| b2 (F2) | 已處理 | 同 c3 |
| b3 (F3) | 部分 | 同 c6 |
| b4 (F4) | 已處理 | 做法5「某平台根不存在或不在 git repo:只列一條…不逐條列」;做法3 對應只印一行;S4 |
| b5 (F5) | 部分 | 前綴要帶分隔字元、file 解析為 repo 頂本身判 outside:已處理(做法1 逐字「加路徑分隔字元開頭」)。絕對路徑符號連結:同 c4 未真正處理 |

## 二、鏡像一致(現稿內互相矛盾或殘留舊字眼)

查過的舊字眼:「平台根」當基準、抽成共用、一律擋、十幾條、S4 綁 rc 測試、不提供略過旗標、kill-add 擋下。除 M1 外沒有殘留:「十幾」「rc 測試」「略過旗標」皆已消失;「抽共用」「kill-add 擋下」「一律」現只出現在被否決或〈不做〉的語境,正確。

共 10 處不一致(M1–M10):

- **M1 PRIOR-ART① 殘留舊基準**:寫「同一種圍欄(realpath 要在平台根內)」,做法1 已改成 repo 頂。同一份稿對基準說兩套話。
- **M2 做法1 vs S5 的符號連結**:做法1 說絕對路徑符號連結歸 outside,S5 預期 `outside ↔ error`,但 realpath 在工作目錄做不出來(詳見 c4);誠實界線也沒記差異。
- **M3 kill-rm 身分 vs 引數名 vs P2 顯示**:做法4 說「用 `_kill_recipe_key` 算身分」,引數叫「合約 KEY 子字串」。`_kill_recipe_key(node, invariant, file, old)` 吃的是配方存的完整 `invariant` 字串、完整相等(子字串不行;guard kill 篩選才用子字串)。P2 與 guard kill 只顯示 invariant 前 30 字。做法4 沒寫「引數要等於存的整串,或接受唯一前綴」。
- **M4 kill-rm 標記移除條件單位不對**:做法4 寫「那篇沒有配方了」才拿掉 `[kill:recipes]`,但標記掛在每條合約 KEY 行上、一篇可有多條合約(rtb 73 條配方分在 7 篇)。應是「該 KEY 行已無配方」。
- **M5 治理帳事件的前提沒寫**:RETIRE-IF 與做法5 都靠 `check-p2` 事件,實際只有 `--ci` 才寫帳、閘名要登記 `_KNOWN_GATES`;REVISIT 要求跑 `lumos doctor --verbose`(不是 `--ci`)回報,兩者量的是不同路徑,現稿沒交代。
- **M6 平台不在設定裡**:做法2 與 S2 對 kill-add 寫了「平台不在設定裡」,做法5 的列項與 S3/S4 沒有這一種(P2 遇到時該列什麼沒定)。
- **M7 快取只在隱患段**:實務隱患說「同一支檔只讀一次」,做法1 判斷函式沒有快取規格,「每條讀一次」與「只讀一次」並存。
- **M8 P2 缺修法而 kill-add 有**:做法3 提醒附修法,做法5 列項沒有。
- **M9 intake 內部殘留(非計劃本體)**:r1-intake 前置掃描表 ④5 仍寫「判重迴圈之前」,後面 c2 已改成判重之後;讀 intake 的人會看到兩種插入點。
- **M10 `--file` 的基準與說明字串**:做法1 把 `file` 定成「從 repo 頂算」,程式 40131 行 kill-add 的說明是「相對配方平台 root」;計劃落點只列 kill-rm 一列,沒說要改說明字串或 skill 對 kill-add `--file` 的說法。

## 三、計劃對程式的宣稱

| 宣稱 | 結果 | 依據 |
|---|---|---|
| guard kill 開工作樹,根是 repo 最上層,`file` 從工作樹根算 | 屬實 | `cmd_guard_kill` 用 `git -C <proot> worktree add --detach`,再 `os.path.join(wt, file)`、`startswith(wt_real + os.sep)` |
| `load_platforms` 遇壞 JSON 退回預設 | 屬實 | 4519–4522 行 except 印提醒後 `cfg = {}`,退回 legacy 單一條目,不丟錯。補充:合法但非物件的 JSON 會在 `cfg.get` 丟 AttributeError(未捕捉) |
| doctor 各段用 `gov_events` 清單記 `check-xx` 事件 | 部分屬實 | 慣例確在(check-s、s2…皆是),但 P 段自己不記;只在 `if ci:` 才落帳;新閘名須登記 `_KNOWN_GATES`(6951 行,另有漂移釘測試)。現稿沒寫這兩點 |
| `warn_soft` 不記帳 | 屬實 | 1354 行只累計 `_soft` 計數並印出,不碰 `gov_events` |
| `_kill_recipe_key` 判身分 | 屬實 | 12870 行,以 (node, invariant, file, old) 雜湊;kill-add 判重也用它(但是完整字串相等,見 M3) |
| 唯一數原文出現次數在 cmd_guard_kill 且在基準測試之後 | 屬實 | baseline 失敗就 `continue`,之後才 realpath / 讀檔 / `count` |
| 輸出同長度前 30 字 | 屬實 | guard kill 輸出 `invariant[:30]` |
| P 段跳過規則逐字、`repo_root` 來源 | 屬實 | 2877–2925、1583–1586 行 |

沒有宣稱被證明是假的;不完整的有 2 處(doctor 事件落帳條件與閘名登記、絕對路徑符號連結的判定機制)。
