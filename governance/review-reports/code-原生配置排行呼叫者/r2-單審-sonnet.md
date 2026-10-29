severity: minor

我沒有找到會做出錯行為的缺陷。查詢本身(`scripts/templates/android-stability-native.sql`)對各種呼叫鏈都正確,問題只出在測試的鑑別力和一處文件措辭。

鎖檔 `.warming` 不存在,所以沒有鎖要處理。固定席筆記派工詞說沒附,我也沒看到。

在副本(`scripts/` 整份複製到臨時目錄)裡,我把跳過條件逐一改壞,跑了 `-k android_native_query`。基線 61 條全過。

| 改壞方式 | 結果 |
|---|---|
| 拿掉條件 | 紅 1 條 |
| 按 `boot.oat`、`boot-framework.oat` 整個跳過 | 紅 2 條 |
| `glob 'art*'` | 紅 1 條 |
| 拿掉 `coalesce` | 紅 1 條(NULL 呼叫者被誤跳) |
| `glob 'art_*'` | 全綠 |
| `glob 'art_jni_trampoline*'` | 全綠 |
| `like 'art_jni_trampoline'`(底線當萬用字元、不分大小寫) | 全綠 |
| `lower(fname) != …` | 全綠 |
| `instr(fname,'trampoline')=0` | 全綠 |

另外,`f.func != …` 與原條件等價,不算存活。實驗副本已用字面路徑刪掉。

我手走了幾條呼叫鏈,結果都對:
- **跳板緊貼呼叫位置上方,再往上是 `nterp_helper` 與 App 方法**:呼叫者是 App 方法。
- **跳板是唯一的上層框架**:沒有符合條件的框架,左連接得到 NULL,記成 `?`。
- **跳板上面全是 `libart.so`**:同樣記成 `?`。
- **`fname` 是 NULL**:`coalesce` 保住它,保留為「`.so` 名稱+0x 相對位址」。
- **並列與 `?`**:排序沿用修補前的邏輯,有測試守。

## 1. 「只認精確名稱」的測試分不出精確比對和前綴、模糊比對
severity: minor
blocking: 否。找不到現實的呼叫鏈會因此被誤跳,而且計劃已有 REVISIT 會回頭看跳過名單。
引句:「    check("App 自己名字以 art 開頭的函式照樣是呼叫者(只跳精確等於 art_jni_trampoline 的)", by.get("Java_fromArtApp", ())[2:3] == ("art.studio.Canvas.draw",), str(got))」
file: `scripts/test_lumos.py:18660`(取自快照 `r2-snapshot.patch` 第 355 行;審材外未另行核對行號)
歸因:有證據的修復回歸。這個測試是修補本輪新加的,實驗中改成前綴、`like`、轉小寫、包含 `trampoline` 都不會紅。
具體失敗場景:測試用的對照名是 `art.studio.Canvas.draw`,只有「`art` 後面直接接任何字」這種寬鬆比對會誤跳它。`art_jni_trampoline*`、`art_jni%`、不分大小寫這類寬鬆比對一樣不會誤跳它,但真實名稱 `Art_JNI_Trampoline` 或 `art_jni_trampoline_x` 會被誤跳,測試也抓不到。
修補前後:修補前根本沒有這個條件,所以沒有可比的結果。修補後,上面五種改壞都存活。補一條名字是 `art_jni_trampoline_x` 的框架,再補一條大小寫不同的,就能擋住。

## 2. 計劃第 1 條與 S21 的措辭不一致
severity: minor
blocking: 否。純措辭落差,查詢實際行為只有一種。
引句:「- [S21] 當同一個呼叫位置從幾個呼叫者進來時,caller 應是從它進來的 callsite 結束累計加總最大的那個(跳過 libart.so 的框架與 JNI 跳板 art_jni_trampoline),並列照呼叫者名字」
file: `docs/lumos-toolchain-knowledge/Projects/原生記憶體增長提示_計劃.md:197`
歸因:有證據的修復回歸。修補同步改了第 1 條(第 141 行寫「名字精確等於」並寫明 `.oat` 的其他框架照樣是呼叫者),S21 這條可驗收條款沒跟上。
具體失敗場景:S21 沒寫「精確等於」與「不按 `.oat` 整個跳過」。這兩點目前只靠測試函式名的 docstring 和斷言守,條款本身守不到。
修補前後:修補前 S21 與第 1 條都沒有這個限定,修補後只有第 1 條有。

## 3. PITFALL 行寫了驗收紀錄沒有的觀察
severity: minor
blocking: 否。只是根因欄多了一句查不到出處的描述。
引句:「同一台裝置鎖定畫面那次的呼叫鏈沒有這一框(什麼情況下才出現沒查)」
file: `docs/lumos-toolchain-knowledge/Systems/android-stability-collector.md:55`,對照 `docs/lumos-toolchain-knowledge/Verification/2026-10-29_原生配置排行實機驗收.md:36`
歸因:未判定。⚠ 驗收紀錄第 36 行只說鎖定畫面那次不採用、資料夾已刪,沒寫那次的呼叫鏈有沒有這一框,所以我無法從審材或驗收紀錄佐證這句話。
具體失敗場景:下一個 session 讀到這句,可能把「沒有這一框」當成已查證的現象。
修補前後:這句話是修補新加的,修補前不存在。

最嚴重等級見檔首,會擋推送的共 0 條。
