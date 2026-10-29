severity: major

鎖檢查:`/Users/enzo/.cache/lumos/dispatch-lens/2df69969…3c8a.json.warming` 不存在,我沒碰任何鎖。固定席筆記派工詞說沒附,所以第 4 項圖譜鏡頭沒有固定席可逐條答。

**1. 新測試分不出「按名字跳過」和「按 mapping 跳過」,改成跳過所有 boot*.oat 也全綠**

severity: major
blocking: 是,測試抓不住條款要守的錯,條款只該跳 libart.so 與名字精確等於 art_jni_trampoline 的框架。
引句:「+    chain = [("com.lab.PlayerActivity.onCreate", vdex, 1), ("nterp_helper", _MS_ART, 2), ("com.lab.sdk.FakeNativeSdk.<init>", vdex, 3),」
file: `scripts/test_lumos.py:18632`(新測試)、`scripts/templates/android-stability-native.sql:68`(新條件)

假呼叫鏈裡 boot.oat 只有跳板這一個框架,所以「跳過 boot.oat 整個 mapping」和「只跳過這個名字」在測試眼裡完全等價。我在副本(`scripts/` 複製到臨時目錄,已刪)改壞後跑 `-k android_native_query`(57 支):

| 改法 | 結果 |
|---|---|
| 拿掉新條件 | 紅:`t_android_native_query_caller_jni_trampoline`,呼叫者印成 `art_jni_trampoline` |
| `f.so != 'boot.oat'` | 57 passed, 0 failed |
| `f.so not glob '*.oat'` | 57 passed, 0 failed |
| `coalesce(f.fname,'') not like 'art%'` | 57 passed, 0 failed |

只有「拿掉條件」會紅,其餘三種改壞全綠。

具體失敗場景:SDK 的 native 是從 framework Java 方法呼叫的。這類方法在真機的 boot-framework.oat 裡,名字像 `android.graphics.Bitmap.nativeCreate`,mapping 路徑是 `/system/framework/arm64/boot-framework.oat`。有人日後把條件「簡化」成按 `.oat` 跳過,這類正當呼叫者會被整個吃掉,呼叫者變成更上層的框架或「?」,測試仍然全綠。應補一條鏈:boot-framework.oat 裡有一個有名字的 Java 框架,斷言它被保留。

**2. NULL 函式名的保護沒有測試守**

severity: minor
blocking: 否,目前程式正確,只是少一道回歸守衛。
引句:「+  where not s.unknown and f.so != 'libart.so' and coalesce(f.fname, '') != 'art_jni_trampoline' group by s.leaf」
file: `scripts/templates/android-stability-native.sql:68`

我把 `coalesce(f.fname,'') != …` 改成 `f.fname != …` 後,57 支測試仍全綠。SQL 的 NULL 比較結果是 NULL,會讓沒有符號的框架被當成「要跳過」。具體場景:呼叫位置正上方是沒有符號的框架(name 為 NULL,例如未符號化的 jit-cache),呼叫者本該印成「.so+0x…」,改壞後會跳到更上層,測試看不出來。只要在鏈上加一個 NULL 名字的呼叫者並斷言它被保留即可。目前的程式碼本身是對的。

**3. 文字說「跳過 ART 的框架」,實作只認兩種;PITFALL 的 JIT 說法沒有證據 ⚠**

severity: minor
blocking: 否,措辭精度,且我給不出已確認會漏的第三個框架名字,所以只算措辭疑慮。
引句:「+   - 呼叫者:呼叫位置往上的第一個不是 ART 的框架——跳過 libart.so 裡的框架(nterp_helper 這類直譯器框架)與 JNI 跳板 art_jni_trampoline」
file: `docs/lumos-toolchain-knowledge/Projects/原生記憶體增長提示_計劃.md`(本 diff 第 50 行)

「第一個不是 ART 的框架」讀起來是通則,實際只有 libart.so 加一個精確名字。art_quick_* 這類我確定在 libart.so,已被涵蓋。另有未證實的一句:

引句:「+  PITFALL:原生配置排行的呼叫者印成 art_jni_trampoline,沒指到 App 的函式 [出處:2026-10-28 SM-X710 實機驗收」

同一行的根因寫「程式被 JIT 編譯過時跳板不出現」。驗證紀錄只記了「修好後重跑 native 與 registry 都指到 App 函式」,沒有 JIT 編譯過的那次對照。這句是推測,而且 JIT 編譯過的 JNI 跳板可能改放在 jit-cache、名字為 NULL,我判不準。建議把這句改成「未驗證」,或改成機械可查的 `[repro:]`。

**其餘鏡頭檢查**
- 條件寫在 `caller_step`,「?」判定沒被改壞。跳板是唯一上層框架時 `caller_step` 無列,`cf.func is null` 的分支會走「?」。ERROR 偽框架與並列排序的路徑沒動。
- 計劃第 1 條、S21、SQL 檔頭註解、PITFALL 行、驗證紀錄的跳過規則互相一致。S21 已加綁新測試。
- `docs/.escape-log.jsonl` 與 `docs/.governance-log.jsonl` 是記帳檔,我沒有發現矛盾。

最嚴重等級見檔首,會擋推送的共 1 條。
