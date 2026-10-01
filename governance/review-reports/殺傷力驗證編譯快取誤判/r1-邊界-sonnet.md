severity: minor

## F1 檔案系統只有 2 秒精度時,「比上一次晚 1 秒」會塌成同一個時間,S2 的嚴格遞增做不到
severity: minor
blocking: 否
引句:「至少比現在晚 1 秒、也比同一組上一次設的晚 1 秒」
file: `docs/lumos-toolchain-knowledge/Projects/殺傷力驗證編譯快取誤判_計劃.md:42`(凍結審材 r1-snapshot.md 的〈範圍〉第一條)
1. 實驗:在 macOS 用 `hdiutil create -fs MS-DOS` 建 FAT32 映像、掛載後對同一檔連設 base、base+1、base+2、base+3。讀回來的偏移是 -1、+1、+1、+3:base+1 與 base+2 變成同一個值,base 本身還被往下取成 base-1。
2. 照 spec 做:第一條壞法設 T、還原設 T+1,在 FAT 上兩個值可能相同(甚至 T 比「現在+1」早)。後果:S2「比同一組上一次設的時間晚」在這種檔案系統上不成立;Python 的編譯快取只比對整數秒加大小,若壞法與還原(或兩條壞法)的時間塌成同一秒,原本要防的誤判就會回來。
3. 這個前提 spec 自己也承認有:PRIOR-ART 提到「只到秒的檔案系統」。最小改法二選一:步長取 2 秒;或設完用 `os.stat` 讀回、比上一次不大就再加碼重設一次。
4. 觸發條件窄(需要 `TMPDIR` 指到 FAT/exFAT 之類),所以只標 minor。

## F2 設時間失敗時只在標準錯誤印一行,判定仍以強證據進帳,失敗的效果等於沒修
severity: minor
blocking: 否
引句:「設時間失敗(`os.utime` 丟出 OSError)不擋:印一行提醒到標準錯誤,照常跑測試(結果可能吃到舊快取,提醒裡寫明)」
file: `scripts/lumos:13949`(`cmd_guard_kill` 裡「套配方」到 `_kill_run` 之間;現況沒有任何設時間的步驟,實作要插在這裡)
1. 照 spec 做:`os.utime` 失敗(Windows 唯讀檔、不支援改時間的掛載等)後,那條配方照跑,若吃到舊編譯快取,結果可能是假的 killed。這個 killed 仍會走 `res["weak"] = bool(mk["ws"] or mk["flaky"] or node_dirty)`(scripts/lumos 約 14040 行),weak 為 False,寫進 `.kill-log.jsonl` 當強證據,背書閘照樣採信。
2. 「判定與回傳碼不變」是 spec 明定的(S3),所以不算矛盾;但本計劃要解的就是「假的合約有守住」,在已知可能吃舊快取的情況下仍給強證據,等於把同一個洞留在失敗路徑。建議這種結果至少標 weak 或在 detail 加註。
3. 另:提醒是每次設定各印一行。Windows 這類必定失敗的環境,每條配方壞法與還原各印一次,N 條配方就是 2N 行,spec 沒寫要不要只印一次。

## 其他已核對、無 finding 的項目
- 時鐘倒退:「max(現在 + 1 秒, 上一次 + 1 秒)」取大者,同一組內仍嚴格遞增;Python 的快取是比對相等不是比大小,倒退不影響。已讀,無 finding。
- 連跑累積:實測測試極快時每條配方消耗 2 秒(壞法 + 還原),10 次設定後比現在晚 10 秒;測試超過 1 秒時由「現在+1」主導不累積。百條級配方也只是數百秒偏移,暫存工作樹跑完即刪,沒有具體失敗場景,不標。
- 連結與唯讀檔:實測 `os.utime` 對連結會跟隨到目標、對 0444 檔(擁有者)可成功。spec 的圍欄先 `realpath`,設時間對象用 target 即可;已讀,無 finding。Windows 唯讀檔會丟 PermissionError(OSError 子類),落入 S3 路徑,見 F2。
- 壞法被判 drifted、路徑逃逸:現況這兩條分支都在寫檔之前就 `continue`,沒有改檔,因此不設時間是對的;spec 未寫但行為正確。還原失敗分支現況 `break`,spec 寫「還原成功之後」才設,一致。已讀,無 finding。
- 同一組不同檔:「上一次」是每組一個計數,不分檔,仍嚴格遞增,比逐檔計數更保守;S2 的 a/b 場景成立。
- 同一秒的奈秒/秒精度:Python pyc 只看整數秒,+1 秒步長足夠;奈秒檔案系統無問題。

最高等級:minor;blocking 共 0 條
