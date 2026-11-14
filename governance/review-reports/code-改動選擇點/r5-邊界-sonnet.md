severity: clean

本輪沒有 finding。修補的程式只有一處(`scripts/lumos` 的 `_choice_kill_report`,給不唯一的行印的照貼 `lint-waive` 指令)。

## 修補範圍與歸因
- 修補差異裡只有一行程式改動。K2(推送前計劃快取)與 K3(點號測試名)是只補測試、程式沒變,兩版行為相同。
- 圖譜固定席:這次沒附固定席節點(鏡頭計算超時),不逐條判。

## 已驗主張與證據
所有命令都在 `/tmp/lumos-seat-work/code-改動選擇點/邊界-sonnet/` 下的兩份 `git clone` 跑。修前是 `04b21d1ff`,修後是 `83ac95c8e`。為了在修前版跑新測試,我把修後的 `scripts/test_lumos.py` 複製進修前副本。

1. **K1 修復(照貼放行指令的檔名要加 shell 引號):已修復。**
   - 修前跑 `python3.14 scripts/test_lumos.py -k choice_kill_waive_hint`:2 條斷言紅,1 條綠。紅的是檔名 `Foo$(touch PWNED) x.kt` 與 `It's.kt`,印出的指令是未加引號的 `lumos lint-waive choice:app/src/main/Foo$(touch PWNED) x.kt:12 ...`。
   - 修後同一條命令:3 passed,0 failed。
   - 歸因:有證據的修復,修前紅、修後綠。
2. **K1 相鄰輸入(自己補的探針):**
   - 中文加空白、含單雙引號、含冒號、組合字元(NFD)的檔名,用 `shlex.split` 解回來都等於 `choice:<原檔名>:12`。
   - 一般 ASCII 檔名(`Vm.kt`)不加引號,與修前一致,修前修後都綠。
   - 檔名含換行或 U+202E 這類控制字元時,`_kill_esc` 會把它換成字面 `\u000a`,解回來不等於原檔名。這是修前就有的行為,沒有倒退。照貼後 `lint-waive` 找不到那一行,只會被拒,不會執行檔名裡的指令。
   - 這是印給人看的提示,沒有可行的合法寫法。我給不出會做出錯行為的具體場景,所以不列 finding。
3. **K2(推送前碰到的計劃只算一次):**
   - 程式沒變。修前與修後跑 `-k choice_guard_cache` 都是 2 passed。
   - 我把 `_choice_guard(rr, rng, at_sha, cache=cache)` 的 `cache=cache` 拿掉再跑修後版,「只算 1 次」那條斷言變紅(`_kt_sit_spec_names_calc` 被呼叫 2 次)。所以新測試抓得到這個改壞。
   - 歸因:新增測試守住既有行為,不是回歸修復。
4. **K3(點號測試名取最後一段):**
   - 程式沒變。修前與修後跑 `-k choice_test_blobs_name_shape` 都是 8 passed,包括新補的 `QuxTest.zap` 對 `Other.kt`。
   - 歸因:新增測試守住既有行為。
   - 我沒做「改取第一段」的翻紅實驗,所以那條翻紅釘我沒自己驗過。
5. **文件引用的測試:** 修後版跑 `-k scan_batch_share` 與 `-k partial_unverified_rc` 都通過,各 1 與 2 passed。

## 三問
- ①原問題的修復效果:K1 有修前紅、修後綠的證據,見上面第 1 點。
- ②修補處的正常、錯誤與相鄰呼叫路徑:一般檔名、含引號、中文和冒號的檔名都成立。控制字元檔名是修前就有的限制,見第 2 點。同檔其他印出的放行提示用的是 `<檔>:<行>` 佔位字樣,不帶真檔名,所以沒有同族漏點。
- ③新發現同一案例的修前修後:沒有新發現。

## 未驗範圍
- 這份差異沒碰到的邊界:上千個選擇點、3000 項串接、1500 行呼叫清單、生效日與回報上限的剛好值,我沒重走。
- 其餘兩項:ast-grep 不在或回非零,以及真 Android 專案的端到端耗時。後者派工單已列在「未覆蓋」。
- 我沒跑不帶 `-k` 的全套,也沒做整體無回歸的保證。

臨時目錄與探針檔都已用字面絕對路徑刪除。

最嚴重:clean;blocking 共 0 條
