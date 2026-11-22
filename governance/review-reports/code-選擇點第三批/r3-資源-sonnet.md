severity: minor

## r1 C-40~C-47 改回正面寫後,長鏈與深巢狀的輸出變成平方成長,超過 64MB 讀取上限的門檻比修前低
severity: minor
blocking: 否

歸因:有證據的修復回歸(輸出量,相對修前 926c720);相對第一批 C-19 持平。時間沒有退步。

量測用真規則 `configs/ast-grep/kotlin-choice/sgconfig.yml` 跑 `ast-grep scan --json=stream`。修前版 api.yml 取自 926c72056。

單一運算式裡鏈 N 個 `.firstOrNull{ it }`:

| N | 修後輸出 / 時間 | 修前輸出 / 時間 | 同形狀 `.filter{}`(C-19,修前修後相同) |
|---|---|---|---|
| 200 | 2.4MB / 0.08s | 0.83MB / 0.07s | 1.78MB |
| 400 | 9.1MB / 0.16s | 3.1MB / 0.15s | 6.7MB |
| 800 | 35.5MB / 0.50s | 12.0MB / 0.47s | 25.8MB |
| 1600 | 140MB / 1.8s | 47MB / 1.7s | 101MB |

- 修後輸出約是修前的 2.9~3 倍,跟 C-19 同量級(約 1.37 倍),時間幾乎沒差。
- 鏈長約 1100 以上,修後輸出超過 `_LINT_SARIF_MAX_BYTES`(64MB)。
- 走到 `scripts/lumos` 的 `_choice_scan_batch` 與 `_choice_scan_one`,`out_path.stat().st_size > _LINT_SARIF_MAX_BYTES` 那行會回 None 或 raise `_ChoiceUnverifiable`,記成「算不出來」。
- 鏈長在約 1100 到 2300 之間的輸入,修前能掃完,修後算不出來。
- 巢狀 `x.firstOrNull { ….toIntOrNull() }` 深度 320 層:修後 17.1MB,修前 6.9MB,時間都是 0.5s。約 620 層才碰 64MB。
- 平鋪的 40000 行(2.7MB)密集 `firstOrNull{}?.toString()?.toIntOrNull()`:修後 195MB / 4.7s,修前 132MB / 4.6s。這個輸入修前修後都超過上限。13000 行同密度約碰上限。
- 單筆命中約 1.2KB(含 `lines` 與兩個 secondary label),所以平鋪情況的量主要來自命中數。

真實大小的檔(幾千行、鏈長個位數)都遠低於上限,這條只是量測後的邊界。這個代價 `Systems/kotlin規則包` 那條 WHY 已點名,測試 `t_choice_rule_shape_batch3` 也守住了形狀。

引句:「其餘(C-40~C-47 只往上兩層)照第一版 C-19~C-31 一字不差正面寫,不包雙重否定。」

## 已驗主張與證據(無 finding)
- **C-38、C-39 拿掉排除後,時間回到正常。**
  - 輸入:`supervisorScope { val r = async{1}` 後接 N 個 `.await().let{it}`,再接 `launch{}`。
  - 修前:N=100 為 0.68s,N=200 為 4.83s,N=400 為 37.7s,約三次方。
  - 修後:N=100 為 0.08s,N=200 為 0.15s,N=400 為 0.46s,輸出位元組相同(只差 C-38 的 1 筆)。
  - 用 `--filter` 單跑 C-38 掃 2000 個兄弟作用域,只要 0.11s。
- **同時跑的兄弟不被排除。** 樣本新增三條 HIT,`t_choice_samples_batch3` 43 條全綠,0.1s。
- **深巢狀作用域沒有時間退步。** 80 層 supervisorScope 與 coroutineScope 交錯:修前修後都是 0.17s,輸出位元組相同。
- **形狀測試成本很低。**
  - `t_choice_rule_shape_batch3` 20 條全綠,測試本身 0.0s。
  - 只讀 api.yml 並跑正規式,不開子程序、不建暫存。
  - `t_choice_scope_rule_output` 14 條全綠,1.5s,是這輪順手量到的。
- **子程序收尾沒有變動。**
  - 修補差異沒有動 `_choice_sg_run`:逾時走 `_kill_proc_group`,`BaseException` 也收,暫存目錄用 `TemporaryDirectory`。
  - 逾時退回逐檔那段(`_choice_scan_each`)也沒動。
  - 跑完 `/private/tmp` 下沒有 `lumos-choice-` 殘留。

## 未驗範圍與已知非回歸
- 20000 個平鋪的 `supervisorScope{...}` 語句超過 100s,2000 個為 2.57s,4000 個普通 `foo{ launch{}; run{} }` 為 10.3s,明顯是平方以上。
  - 修前與修後數字一致(2000 個 2.63s 對 2.57s)。
  - 單跑 C-38、C-39 只要 0.1s,元兇不在本批規則,屬原有。
  - 30 秒的 `_KT_SIT_BUDGET` 會擋下這種輸入,算不出來時走原有的提醒路徑,本次沒有追到是哪條規則。
- 工作樹模式的上限是 64MB,但 ast-grep 在逾時前會把輸出寫滿暫存碟(1600 鏈 140MB / 1.8s)。這段程式修補沒有動,沒有另量。
- 沒有跑全套測試,也沒有量慢機器上的時間餘裕。

總結:最高嚴重度 minor,blocking 共 0 條
