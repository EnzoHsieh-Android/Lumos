severity: clean

# 邊界-sonnet 第 1 輪報告(邊界與輸入鏡頭)

核對範圍:凍結 patch 內 `_kill_wait_new_second`、`_kill_after_write`、`cmd_guard_kill` 的寫檔/還原/收尾重算 weak 路徑;全部在 `git clone --shared` 出的臨時 repo 內實跑(直接呼叫兩個 helper,加端到端 `lumos guard kill --json`)。沒有找到會崩潰、空等無界、或判錯的邊界。

引句:「deadline = time.time() + 3.0」(等待有 3 秒上限,實測 state["w"] 設成未來 100 秒時 `_kill_wait_new_second` 只等 3.05 秒就放行)

## 實跑結果(每個邊界)
- 讀回修改時間失敗(檔被刪):`_kill_after_write` 回 False、不崩、0.0 秒。引句:「except OSError:            return False」
- 修改時間 0、負值(utime 設 0、-5):各等 1 秒、碰成現在後回 True,不崩。
- 檔本來帶很遠未來時間(+10^8 秒):因為寫後讀回,真實流程中檔的時間是現在;直接餵未來檔時回 True、state["w"] 變未來值,之後每次 wait 最多多等 3 秒、after_write 回 False,有上限、結果記弱證據,不卡死。
- 上一次測試結束時間在未來(時鐘往回撥):等 3.02 秒後回 False,有上限。
- 唯讀檔(0444):`os.utime` 對擁有者仍可成功,回 True;若 utime 失敗被 `except OSError` 接住回 False。唯讀檔本身寫入會在既有的 `open(target, "w")` 拋例外,這是 diff 之前就有的行為,不是本次引入。
- 符號連結(prod.py 指向 real.py):端到端 killed、rc0、不崩。
- 還原後檔仍存在:old==new 的配方(內容不變)端到端 survived,git checkout 仍把時間更新,沒有誤標 `_mtime_unsure`。
- 同一組第一條配方就 drifted(old 命中 0 次):在 `_kill_wait_new_second` 之前就 continue,第二條照常判 killed;耗時 3.2 秒,沒有空等。
- 配方很多:8 條無害配方端到端 16.7 秒,約每條 2 秒(寫前等一秒邊界、還原前再等一秒)。是設計內的線性成本;`cmd_guard_kill` 只有 CLI 入口(`scripts/lumos:41797` 一處呼叫),沒有程序內呼叫者設總逾時,所以不會被外層逾時砍。
- Windows / FAT 時間精度:最壞每條 ≈ 3+3+3+3 秒內有界,每個迴圈都有上限(after_write 最多 4 次 stat、3 次 sleep(1)),時間粗的檔案系統只會多等並標弱證據,不會無限等或判錯。

佐證行:file: `scripts/lumos:13742`(`_kill_wait_new_second`)、file: `scripts/lumos:13751`(`_kill_after_write`)、file: `scripts/lumos:14046`(收尾重算 weak 含 `_mtime_unsure`)

## 無需處理的觀察(不標 finding)
- Linux 內核粗粒度時鐘可能讓檔案時間比 `time.time()` 落後幾毫秒、剛過整秒邊界時 after_write 偶發多走一次 utime 重試(多 1 秒),自癒、不判錯;無具體失敗場景,不標。

最高等級:clean
