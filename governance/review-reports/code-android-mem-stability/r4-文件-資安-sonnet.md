severity: minor

三類逐類看過。三條 finding 都是 minor,沒有 blocker 或 major。我沒碰裝置,也沒動工作樹。實驗只在 `/tmp/lumos-seat-work/code-android-mem-stability/文件-資安-sonnet/`,跑完已用字面絕對路徑刪掉。

## 類別①:提示注入
已看,無。新增的步驟和範例都叫 AI 讀本機設定檔、本機收集腳本的輸出和 run 目錄的 `logcat.txt`。

- `driver` 是專案設定裡的指令,計劃寫明與專案建置腳本同一信賴等級,攻擊者拿不到寫入點。
- Maestro 與 UI Automator 範例沒有叫 AI 執行來路不明的指令。
- `logcat.txt` 只留違規行,SKILL 沒叫 AI 照著日誌文字行動。

## 類別②:讀寫與執行越界
**中斷後快照留著要自己刪、裝置暫存要自己 `adb shell ls` 看過再刪:無越界。**
- 收集腳本只清自己的 `lumos-stability-<run-id>.*`。
- 7 天清理用 `os.path.islink` 跳過捷徑目錄和捷徑檔(`scripts/templates/android-stability-collect.sh:111-125`)。
- `run-id` 只收 `[A-Za-z0-9._-]+`,擋掉路徑穿越。
- 腳本在開跑前用 `git check-ignore` 問 7 種檔名都被忽略了才碰裝置。

只有下面第一條 finding 是這一類的缺口。

## 類別③:一步就能繞過守衛

### 一、L3 原生配置追蹤輸出不受保存規則管,也沒有存放位置限制
severity: minor
blocking: 否

引句:「`heap_profile -n <套件> --heaps com.android.art -d 10000 -o <目錄>`。`-o` 的目錄要先建好,不存在時它只印一行就結束、什麼都沒錄。原生配置把 `--heaps` 換成 `libc.malloc`。」

- **誰**:照常操作的 AI,在 L3 第 1 步用 `heap_profile`。
- **從哪**:`<目錄>` 沒指定。
- **送什麼**:AI 為了「先建好目錄」,隨手建在 repo 根或 `/tmp`。
- **拿到什麼**:這份輸出(含配置呼叫鏈的 `raw-trace`)可能落在沒被 `.gitignore` 蓋住的位置。
  - 它也不叫 `heap-*.pftrace`,不被 7 天清理認得。
  - 它不在腳本的 `check-ignore` 檢查範圍內,因為那只涵蓋收集腳本自己寫的 7 種檔名。
- **對不上的地方**:「進版控的只有查詢結果」「7 天保存」都只覆蓋 Java 快照。這份輸出沒有堆積內容,隱私風險比 `.pftrace` 快照低,所以標 minor。
- **歸因**:未判定。修前版 SKILL 的 L3 第 1 步是否也沒有 `-o` 位置限制,我沒有取出兩版逐項比對;這句是本次 diff 內容,但保存規則範圍是這次新增的。
- **建議**:`-o` 也指定 `.lumos/artifacts/android/<run-id>/heap-profile-*/`,或在保存規則裡明講「只管 `heap-*.pftrace`」。

### 二、`test_data` 的 `value: false` 宣告在 L0 與限制句裡可被讀成「有宣告」
severity: minor
blocking: 否

引句:「專案沒有 `stability.test_data` 宣告時不往下,收據記 `[GAP] L3 未授權` 並列出哪條 check 沒過,請人裁要不要宣告」

- **誰**:照常操作的 AI。
- **從哪**:專案設定是 `{"value": false, "decided_by": "Enzo", "decided_at": "2026-10-24"}`,也就是人明確裁定「不是只用假資料」。
- **送什麼**:L0 第 8 步的觸發條件只說「沒有宣告」。「不准做的事」那句寫「有它才錄」,「有它」也沒限定 `value` 是 true。
- **拿到什麼**:AI 可能判定「宣告存在」,直接進 L3 並手動執行 `java_heap_dump`。
- **擋住的因素**:L3 小標題寫了「`stability.test_data` 的 value 是 true 才做」。收集腳本本身也只在 `value` 為 true 時錄(`scripts/templates/android-stability-collect.sh:353`)。所以只剩手動 L3 路徑有風險。
- **歸因**:有證據的原有漏查。計劃 S6 已寫「沒寫或 value 是 false 都停」,SKILL 的 L0 第 8 步與限制句沒同步。
- **建議**:兩處都改成「`stability.test_data.value` 為 true 才往下」。

### 三、佔位檢查只擋 `<…>` 形狀,拿掉角括號就過
severity: minor
blocking: 否

引句:「範例的裁定人與日期是佔位,不能照抄:要先問人「這個專案是不是只在測試帳號與假資料下跑」,照對方的回答填真的人名與日期(日期佔位不改會被 --check-config 擋下)。」

- **誰**:照常操作的 AI。
- **從哪**:編輯 `reference.md` 的範例設定。
- **送什麼**:AI 把 `"<裁定的人>"` 改成 `"裁定的人"`、`TODO` 之類的字串,日期填成當天。
- **拿到什麼**:`test_data` 的人裁宣告就此通過。
- **實跑**:在臨時 git repo 放設定檔,執行 `python3.14 <工作樹>/scripts/lumos macrobench --repo . --check-config`。
  - `decided_by` 為 `裁定的人`、`TODO`、`false` 時,輸出「macrobench 設定與門檻檔都合格。」。
  - 為 `<裁定的人>` 時,輸出「擋下:… 不是空的、也不是 <裁定的人> 這種佔位」。
  - 規則在 `scripts/lumos:39428-39434`:`re.fullmatch(r"\s*<.*>\s*", by)`。
  - 退出碼不可信:我用 `| tail` 接輸出,印出的 `rc=0` 是 `tail` 的,無法判定。
- **修前版**:`f0d414532` 的 `scripts/lumos` 對 `"<裁定的人>"` 加真日期同樣印「合格」,所以佔位檢查是 r3 的修補,不是回歸。
- **歸因**:有證據的原有漏查,修補只做了一半。
- **性質**:本質上只能靠「先問人」,機器擋不了。SKILL 與 reference 只要把「靠問人」寫成唯一防線,不暗示 `--check-config` 擋得住佔位即可。

## 三問的回答
1. **原問題修復效果**:
   - 「`<裁定的人>` 佔位被擋」已驗,見第三條實跑,修前版放行、修後版擋下。
   - 「`test_data` 宣告和快照保存規則」的 SKILL 文字與腳本邏輯相符,沒有看到文件宣稱而腳本沒做的地方。
   - 捷徑目錄不被刪,我只讀了程式碼,沒實跑;這一項未判定,測試名稱是 `t_android_memstab_collect_test_data_gate`。
2. **相鄰路徑**:
   - 收集腳本路徑(`test_data` 為 false 或缺時不錄、gitignore 檢查、7 天清理)從程式碼讀起來成立,未實跑裝置路徑。
   - 手動 L3 路徑(`heap_profile` 的輸出位置、`value: false`)是文件鋪陳的缺口,即第一、二條。
3. **同一案例兩版**:只有第三條有兩版實跑。第一、二條是文件文字層面,修前版 SKILL 的對應措辭我沒有取出比對,屬未判定。

未驗範圍:整份 diff 約 754 行,我讀完兩份 skill、`reference.md` 與計劃和節點裡的資安相關句子,但沒逐行讀其餘圖譜筆記。我也沒有對真裝置或假 adb 執行收集腳本。

最嚴重 severity:minor,blocking 共 0 條。
