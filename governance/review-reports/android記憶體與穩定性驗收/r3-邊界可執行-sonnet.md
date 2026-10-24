severity: major

**Finding 1:量測輪中崩潰時,driver 失敗會把 exits 一起壓成跳過,崩潰變成灰色而不是紅色**
severity: major
blocking: 是(照字面實作,最該紅的崩潰情境判成跳過,S19 無法達成)
引句:「driver 來源不是 ok 時每一條都列成跳過」
佐證 file: `r3-snapshot.md:116`、`r3-snapshot.md:124`、`r3-snapshot.md:32`
- 失敗場景:量測第 3 輪 App 崩潰。UI Automator 找不到元件,測試失敗,輸出出現 `FAILURES!!!`,S16 把 driver 記成 failed。
- 依 S11 與判定段(第 76 行),七條檢查全部跳過,包括 exits、pids 變了這個最直接的證據。
- 結果是 S19 要求的「exits 應列成沒過」在實機上不會發生,崩潰只顯示「跳過:driver failed」。
- 這跟 WHY 第 32 行的意圖(防止其他數字照樣全綠)只對了一半。exits 與 pids 是獨立來源,driver 失敗反而是它們最該報的時候。
- 建議:exits 與 pids 不受 driver 狀態影響,獨立判定;driver 失敗只跳過需要完整 N 輪的檢查(native_unreachable、java_growth、instances、peak_vitals、frozen)。

**Finding 2:logcat 串流沒指定起點,暖機輪的 StrictMode 違規會被算進量測輪**
severity: major
blocking: 是(假紅:違規發生在暖機,卻被判為量測期間的違規)
引句:「收集腳本在 N 輪期間把這個 pid 的日誌持續串流到主機(`adb logcat --pid`)」
佐證 file: `r3-snapshot.md:37`、`r3-snapshot.md:71`
- 我在 SM-X710 上查了 `adb shell logcat --help`:`--pid=PID` 存在,`-T N` 與 `-T TIME` 也有。
- 沒帶 `-T` 時,logcat 會先倒出該 pid 在緩衝區裡的全部歷史,再接著串流。
- 失敗場景:冷啟動或暖機時印了一筆 StrictMode 行,步驟 4 才開始的串流照樣讀到它。
- 結果是「N 輪期間」這個條件不成立。S7 與表格的判不過條件(第 59 行)都沒寫起點。
- 建議:串流起點寫成「步驟 4 開始當下的時間」(`-T <時間>`),並加進 S7 的條款。

**Finding 3:S8 的「幀數」指稱不清,正常情況可能永遠是跳過**
severity: minor
blocking: 否(措辭歧義,可由測試綁定抓到)
引句:「設了 max_block_ms 而最長阻塞超過時也列成沒過;幀數是 0 時列成跳過」
佐證 file: `r3-snapshot.md:113`
- 結果檔裡有 `frozen_frames` 與 `frames` 兩個欄位。
- 若實作者把「幀數是 0」讀成 `frozen_frames == 0`,健康的 App 永遠是跳過、永遠不會通過。
- 建議條款改寫成 `frames`。

**Finding 4:⚠ 第二次原生掃描前先錄了一份 Java 快照,可能讓預設門檻 0 位元組誤報**
severity: minor
blocking: 否(無法證實,屬於 S17 與 2027-04-30 回頭條件要實測的項目)
⚠
引句:「掃一次沒人指著的原生記憶體;讀 Native Heap」
佐證 file: `r3-snapshot.md:72`
- 步驟 5 的順序是先錄第二份快照,再做第二次掃描。java_hprof 會在目標行程裡載入並分配少量原生記憶體。
- 預設門檻是差值大於 0 位元組。若有任何一塊留在行程裡且沒人指著,正常版也會紅。
- 實驗室的 0 位元組基線是否在兩次掃描之間錄過快照,spec 沒寫,我也無法從文件證實。
- 我看不出必須修改文字,但建議 S17 的實機驗收明寫「含快照順序」。

**固定席節點**
- `Systems/macrobenchmark-adapter`:已讀 spec 對它的描述。判不影響。「不接裝置」照留,新增的只是讀結果檔判定,而且 `_macrobench_thresholds` 與 `_macrobench_mode` 沿用門檻檔(`.lumos/macrobench-thresholds.json`)的讀法(`scripts/lumos:39656`、`scripts/lumos:39726`)。S14 也成立:門檻檔與 `.lumos/macrobench.json` 是分開的。
- 這個節點在會談目錄裡沒有,我只能對照凍結審材,沒有看到該節點本文。
- `scripts/lumos`:沒有牽到合約的節點。判不影響。

**其他已讀**
- S4 的記憶體分級表我沒能核對。vitals 官方網址回 404,我也沒找到替代頁面。上一輪邊界席已核對一致,這輪不另標。
- 順帶一提:SM-X710 的 MemTotal 是 7386728 kB,約 7213 MB,落在 6800–9216 這一級。
- 第 31–33 行(自己測自己、追蹤檔錄製與停止)已讀,無 finding。

總結:最高嚴重度 major,blocking 共 2 條
