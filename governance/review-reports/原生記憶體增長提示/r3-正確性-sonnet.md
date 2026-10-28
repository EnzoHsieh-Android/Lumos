severity: major

### F1 池子在量測中途填滿時,分成「停住」還是「線性增長」取決於暖機與傾印的時間對齊,S5 的情境③不保證分對
severity: major
blocking: 是
引句:「heapprofd 接上行程的那一兩秒算在第一份裡、不影響 L1 與 L2」
file: `/Users/enzo/orca/workspaces/lumos-toolchain/native-mem-growth/governance/review-reports/原生記憶體增長提示/r3-snapshot.md:154`

1. 切點是照錄製總時長切,不是照輪數切。錄製總時長包含 heapprofd 接上行程的空白(gap)和停錄前多等的一個傾印間隔。
   - 這兩段會把 t1 往後挪,所以「接上行程的空白不影響 L1、L2」不成立。它不影響的只有 Q1 本身的內容,不包括 t1 的位置。
   - 每個 Q 的第一個傾印只在整秒邊界才看得到,配置要等下一個傾印才進表。
2. 我用 python 模擬情境③:上限 4 塊的池,暖機已配 2 塊,量測期間在第 1、2 輪各配 2 MB。傾印每秒一次,N=8。
   - 時間參數取 gap=1.5 秒、每輪 1.5 秒、尾端 1 秒。
   - t4 約 14 秒,t1 約 3.5 秒。第 2 輪的配置落在 3.2 秒,要等 4 秒的傾印才進表,所以晚於 t1。
   - 結果 L1=2 MB、L2=4 MB,3×(4−2)=6 ≥ 4,判成**線性增長**。S5 預期「池不列」,實際會列出。
3. 我掃了 gap 0.5–2.0 秒、每輪 1.2–2.2 秒、傾印相位 4 種,共 64 組:33 組判線性、31 組判停住,約一半誤判。
   - ⚠ 實驗室真實的每輪時長、gap、傾印相位我沒有,上述參數是假設。結論是「判定隨對齊翻轉」,不是「必錯」。
4. 一般化:池子線性填到佔錄製時長的比例 f 才停,L1=0.25C/f,L2=C。要判成停住必須 f<0.375。
   - 判法等於要求池在錄製前 37.5% 內填滿。
   - 實務隱患只寫「量測輪數小於快取上限」,低估了這條邊界。真正的邊界是錄製時長的前 37.5%,而且還受 gap 和傾印對齊影響。
5. 「N 小於 4 就 failed」不保證每份涵蓋一輪。N=4 時 Q 約 2.1 秒,Q1 內只有半輪。S5 草稿判法分對的事實不能轉移到新判法,spec 自己也承認新判法沒重跑。

### F2 一次性的階梯在 t1 到 t3 之間發生,會被判成線性增長,與 S2 的意圖相反
severity: major
blocking: 是
引句:「heapprofd 只記開錄之後的配置,所以每個呼叫位置的起點固定是 0」
file: `/Users/enzo/orca/workspaces/lumos-toolchain/native-mem-growth/governance/review-reports/原生記憶體增長提示/r3-snapshot.md:128`

1. 「起點固定是 0」讓 L1 取到 0 的條件很寬。只要某個呼叫位置的第一筆配置落在 t1 之後,例如量測中途才首次走到的功能延遲初始化,L1 就是 0。
2. 具體例:延遲初始化在第 3 輪一次配 6 MB,之後不變。
   - 模擬得 L1=0、L2=6 MB,3×6 ≥ 6,判**線性增長**。
   - 應為停住(一次性、有界)。
3. 「量測中途清一次快取」落在 Q2 時同理:L1 取到谷底,L2 是回填後的高點,誤報。
4. 反向也成立:Q4 內的一次大釋放會把 L2 壓到 1 MiB 以下,真漏被判不增長。窗口最小值對「單次下凹」沒有免疫,只對「每輪來回」有免疫。S12 只涵蓋後者。
5. 負累計:在我讀到的原始碼範圍內,L1、L2 不會因開錄前配置、錄中釋放而變負。
   - `profile_packet_sequence_state.cc` 對「alloc_delta 為負或 free_delta 為正」的封包會丟棄並計入 `heapprofd_malformed_packet`。
   - 零差額不寫列。
   - 網址:https://raw.githubusercontent.com/google/perfetto/v57.2/src/trace_processor/importers/proto/profile_packet_sequence_state.cc
   - ⚠ 服務端對「不認識的位址的 free」是否一律忽略,我沒讀到 heapprofd 原始碼,不能斷言。

### F3 判法用呼叫位置自己的累計當分母,穩定的大基底會遮住真正在漏的量
severity: minor
blocking: 否
引句:「用整數比 3 ×(L2 − L1)≥ L2,不用浮點除法」
file: `/Users/enzo/orca/workspaces/lumos-toolchain/native-mem-growth/governance/review-reports/原生記憶體增長提示/r3-snapshot.md:131`

1. 同一函式在第 1 輪配 100 MB 之後每輪再漏 1 MB:模擬 L1=100、L2=105,3×5=15 < 105,判停住。
2. 同一個函式帶一份穩定大緩衝時,真漏就被遮住。這是漏報,不會多列。
3. 計劃的 REVISIT 只提到重定 1/3 和 1 MiB,沒有寫這個失效形狀。只提醒的產品行為下可接受,但應寫進邊界。

### F4 「在 callsite 層先取前 200 再歸併」與〈判法〉的呼叫位置層定義不等價
severity: major
blocking: 是
引句:「先篩出最後累計至少 1 MiB 的 callsite、照 L2 取前 200 個」
file: `/Users/enzo/orca/workspaces/lumos-toolchain/native-mem-growth/governance/review-reports/原生記憶體增長提示/r3-snapshot.md:139`

1. 第 4 步的「最後累計 ≥ 1 MiB」「L2 前 200」都在 callsite(完整堆疊)層做。〈判法〉第 1、2 條的 L1、L2 與 S1 的 1 MiB 下限是在歸併後的呼叫位置層。
2. 漏列例:同一個包裝函式 S 從 5 個呼叫者進來,各自線性漏到 0.9 MiB。
   - 每個 callsite 的最後累計 0.9 MiB < 1 MiB,全被預篩丟掉。
   - 歸併後 S 的 L2 約 3.4 MiB、L1 約 1.1 MiB,依 S1 應被列出,實際永遠看不到。
3. 擠出例:某個呼叫位置的 callsite 數量超過 200 時,前 200 全是同一個位置的不同堆疊,其他位置被擠掉。這個條件我沒量,先標 ⚠。
4. 歸併後 L2 不是各 callsite L2 的加總。兩個互補相位的 callsite 各自 L2=0,合併後恆為 2 MB;預篩用的是前者,數字會差。
5. 第 5 步和 S11 說「照 L2 排、最多 200 項」,沒說是 callsite 層還是歸併後。兩處對不上時,實作者無從選。
6. 「呼叫者記累計最大的那個」沒說累計量是哪個量(最後累計還是 L2),也沒說是對 callsite 層加總還是單一 callsite 比較。
7. 應該的做法:先歸併到呼叫位置,再套 1 MiB 與前 200。這與「不做傾印數乘列數的連接」不衝突。

### F5 呼叫者的「累計最大」未定義
severity: minor
blocking: 否
引句:「呼叫者記累計最大的那個」
file: `/Users/enzo/orca/workspaces/lumos-toolchain/native-mem-growth/governance/review-reports/原生記憶體增長提示/r3-snapshot.md:127`

1. 「累計」可能指最後累計、L2、或整段 size 加總,三者在不同呼叫者間排序可能不同。
2. 平手時沒有規則,輸出會不確定。
3. 這是 F4 第 6 點的獨立條款問題:S1 要印呼叫者,但沒有對應的確定規則。

### 計劃自己的情境與新形狀走算結果
- 以下用 python 模擬,N=8、gap 1.5 秒、每輪 1.5 秒、傾印每秒一次:
  - 每輪漏 2 MB:L1=2、L2=12、結尾 16 MB,線性,正確。
  - 池 2 塊(第 1、2 輪各配 2 MB):L1=2、L2=4,**線性**(見 F1,隨對齊翻轉)。
  - 池填 3、4、6 輪:都判線性。
  - 漏得越來越慢(√x 型):判線性,合理。
  - 每兩輪才配一次 2 MB:L1=2、L2=6,判線性,合理。
  - 一次性延遲初始化 6 MB:判線性(F2)。
  - 前段 100 MB 加每輪 1 MB:判停住(F3)。
- 每輪配了又還的緩衝:S12 在模擬裡沒有誤報。保護來自最後停錄前多等的一個傾印間隔。
  - 我沒有推翻 S12。
  - 這條保護依賴「驅動結束時已釋放」。若最後一輪結束時緩衝仍活著,最後一列不是谷底,S12 的保證失去依據。⚠ 我沒有造出這個輸入實測。
- 條款文字與〈判法〉第 3 條在數字、比較方向、邊界上逐字一致:S1 的 L2 至少 1 MiB 與 3×(L2−L1) 不小於 L2,S2 的 L2 不到 1 MiB 與 3×(L2−L1) 小於 L2,方向與包含端點都對得上。

總結:整份最高嚴重度為 major,blocking 共 3 條
