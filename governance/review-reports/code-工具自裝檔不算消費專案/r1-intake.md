# r1 收貨紀錄(編排者)

七席全數收齊後才動工作目錄。引句全數錨定(quote-check 七份皆 ✅);refcheck 的 missing 全是審查員在暫存 repo 自造的重現檔路徑,不是錯誤引用。

## 去重後的發現

| id | 等級 | 一句話 | 哪幾席抓到 |
|---|---|---|---|
| F1 | blocker | 照目錄前綴跳過,消費專案自己放在 scripts/hooks、scripts/templates 的程式被當成工具的檔,推送閘分級被降、逃過代碼審 | 外家否決 F1、邊界 F1、併發資源 F2、外家找洞 F1 |
| F2 | blocker | lint 那一層沒套跳過,宣告 lint 的專案照樣被工具自己的檔撐成 high | 整合 F1、外家找洞 F2 |
| F3 | major | 刪除行那條路少傳 skip_vendored,工具檔的刪行照樣進棧別觸發 | 整合 F2、正確性 F3 |
| F4 | blocker | about_code 的 set 會把既有多筆清單靜默壓成一筆 | 併發資源 F1、整合 F3、邊界 F3、外家否決 F3 |
| F5 | major | about_code 存在性檢查可被絕對路徑、../ 繞出 repo,也不擋目錄 | 正確性 F1、邊界 F2、整合 F4、外家否決 F2、外家找洞 F5 |
| F6 | major | 同一欄位兩套規則(set 當純量、append/remove 當清單);set 之後 remove 清不掉;「唯一寫入口」宣稱不實 | 架構 F1、外家找洞 F3/F7、正確性 F2 |
| F7 | major | set 覆寫既有欄位跳過引號處理,含「: 」的路徑寫出壞的欄位區 | 外家找洞 F4 |
| F8 | minor | 事故筆記把 about_code 講成波及連結入口(實際只做排序) | 外家找洞 F6 |
| F9 | minor | 安裝端另寫一份目錄清單,「不另記一份」不成立 | 整合 F5 |
| F10 | minor | _set_about_code 命名與擋下訊息順序跟鄰居不一致 | 架構 F2、F3 |
| F11 | minor | 技術棧計數對同一層重算相對路徑 | 併發資源 F4 |
| F12 | minor | 判別鍵檔若出現在消費專案,方向是恢復掃描(fail-closed),需要釘住 | 併發資源 F3 |

## 編排者機械重現(修改前的程式,a3f85fd7)

| id | 怎麼重現 | 結果 |
|---|---|---|
| F1 | 暫存 repo 提交 scripts/hooks/my_own.py(內含 open()),跑 pitfalls --diff --json | HIT:tier standard、claims 0 |
| F2 | 寫成測試:假 lint 對工具檔與專案檔各報一條,對齊/不對齊各跑一次 | HIT:兩種情況工具檔的 lint 命中都留著(測試 ⑦ 修前翻紅) |
| F3 | 暫存 repo 讓一支前綴下的 .vue 只刪行,跑 --dispositions-template | HIT:「要答的題 1 題」 |
| F4 | 兩筆清單的節點跑 set about_code src/c.ts | HIT:只剩 about_code: src/c.ts |
| F5 | set about_code /etc/hosts | HIT:rc0 寫入 /etc/hosts |
| F6 | 對照 LIST_KEYS 仍含 about_code、cmd_set 另開分流 | HIT(讀碼即可確認,另見 F4) |
| F7 | set about_code "src/a: b.ts" | HIT:寫出未加引號的 about_code: src/a: b.ts |
| F8 | 讀 doctor [S4] 的建議文字:「about_code 欄位只做排序不建連結」 | HIT |
| F9 | grep 安裝端 for sub in ("scripts/hooks", "scripts/templates") | HIT |
| F10 | 讀碼 | HIT |
| F11 | 讀碼 | HIT |
| F12 | 既有測試 ④ 已在工具鏈本體驗「不跳過」 | HIT(方向確認為安全,改成釘住) |

## 判讀

- F1 的判準:審查員提的「比對內容雜湊」可以更嚴,但需要安裝時記一份清單;這一輪改成「精確檔名清單 + 逐檔比對工具鏈 repo 的漂移測試」,
  剩下的邊界(專案改了工具自己的同名檔)寫進事故筆記並附回頭條件。
- F4–F7、F10 是同一個錯的前提:以為 about_code 實務上都是單一路徑。★拿掉 set 那條★,改成 append/remove 認得單一值寫法、append 加路徑檢查。
- code 迴圈:輪內有 blocker,accepted 必須是空的——十二條全折。
