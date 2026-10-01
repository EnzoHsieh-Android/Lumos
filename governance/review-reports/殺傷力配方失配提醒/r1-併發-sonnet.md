severity: major

## F1 設定檔解析失敗不會讓 load_platforms 丟例外,「設定檔讀不了」的分支做不出來
severity: major
blocking: 是
引句:「設定檔讀不了、或平台不在設定裡,不呼叫判斷函式,由呼叫端各自處理(見下)。」
file: `scripts/lumos:4504-4530`
1. 實測:`.lumos/config.json` 內容是 `{bad` 時,`load_platforms` 不丟例外,只印兩行警告,回 legacy 單一條目(`multiplatform False`、平台名 `csharp-xunit`、root=專案根);只有「設定錯誤」(缺 default_platform 等)才 raise ValueError。
2. 照 spec 字面實作(try/except 包 `load_platforms`、例外才算「設定讀不了」):JSON 壞掉時 doctor P2 不會印「這一段算不出來」,S4 的第三句無法由「設定檔壞掉」這個輸入觸發;kill-add 的 S2「設定讀不了」同理永遠不觸發。
3. 更糟的是壞設定下 legacy 回退會讓每條帶 `platform` 的配方都落到「平台不在設定裡」,沒帶 platform 的配方則拿專案根當平台根去讀檔,整段 P2 在每次 doctor(推送前、CI)一次噴出全部配方的假失配,而且這是平台根在網路磁碟或慢速時之外最常見的整批假警報來源。
4. 另外 `load_platforms` 每呼叫一次就把警告印出一次(stdout/stderr 各一行);若 P2 每個節點或每條配方各呼叫一次,壞設定下警告會重複 N 次。spec 沒寫「整段只載一次」。
建議:spec 明寫 P2 整段只呼叫一次 `load_platforms`,並用 `multiplatform`/設定檔 JSON 能否解析(自己先 json.loads)來判「設定讀不了」,S2/S4 的觸發條件改成可實作的輸入,測試用壞 JSON 與缺 default_platform 兩種各驗一次。

## F2 目標檔是具名管線(FIFO)時讀檔會永久卡住,doctor 沒有逾時
severity: minor
blocking: 否
引句:「用文字模式、UTF-8 開檔讀全文(跟 guard kill 同樣的讀法,換行一樣會被正規化,所以兩邊數出的次數一致);」
file: `scripts/lumos:12850-12870`
1. 實測:平台根內 `mkfifo root/fifo`,以 `open(...,encoding="utf-8").read()` 讀,3 秒後仍卡住(沒有寫端就永遠不返回)。`os.path.realpath` 圍欄擋不住它(路徑在根內),spec 的 `OSError/ValueError` 例外保護也接不到「阻塞」。
2. doctor 在推送前掛鉤與 CI 都跑,一條指向 FIFO 的配方會讓整個 doctor 無限期卡住;spec 要求的「整段包在例外保護裡,不讓整個 doctor 停掉」在此失效。
3. 場景偏冷(git 不追蹤 FIFO,要本機手造或工具產生的暫存管線),所以只標 minor;修法是讀前 `os.stat` 確認 `S_ISREG`,非一般檔回 `missing`(細節「不是一般檔案」)。

## F3 讀檔量與耗時:已讀,無 finding(附實測)
severity: minor
blocking: 否
引句:「每條配方讀一次目標檔全文;工具鏈與 rtb 現況各十幾條配方,量級可忽略;實作時量一次 doctor 多花的時間記進〈實作紀錄〉。」
file: `scripts/lumos:2877-2921`
1. 實測基準:本 clone 的 `lumos doctor` 一次約 16.8 秒(user 10.6s、sys 5.3s);工具鏈只有 1 條配方指向 `scripts/lumos`(約 2.4MB)。同一支 200MB 純文字檔連讀 10 次約 2 秒,即每次約 0.2 秒、記憶體峰值約檔案大小的 1~2 倍;十幾條配方即使全指向同一支 2.4MB 檔,多花也在毫秒級。spec「量級可忽略」成立。
2. 同一支檔被多條配方指到時 spec 沒寫快取;因量級可忽略不構成錯誤,但如果之後 rtb 配方變上百條且目標檔大,建議以 realpath 為鍵在 P2 段內快取一次讀取結果(`count` 本身要對每條 old 各算一次)。這條只是建議,不阻擋。
3. 平台根在網路磁碟或很慢時:每條配方一次序列讀,沒有逾時;耗時與配方數成正比,推送前掛鉤才會被拖慢,沒有正確性問題(讀不到走 `missing`,只提醒不擋)。同 F2 的阻塞風險一起處理即可。
4. 讀檔時另一程序正在寫(編輯器非原子存檔):可能讀到半截內容而報 `hits 0` 的暫時假警報;只是軟提醒、下次 doctor 自癒,不需處理,誠實界線可補一句。

最高等級:major;blocking 共 1 條
