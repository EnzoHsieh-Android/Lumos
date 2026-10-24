severity: minor

已看三類,只有一條 minor。範圍是 r3-pkg-docs.patch 全部 12 個檔,skill 與 reference 兩份逐行讀過,其餘計劃與系統筆記掃過。

## ① 提示注入:已看,無
- skill 與 reference 沒有叫 AI 照外部可控文字行動的句子。
- 範例指令(`driver`、`am instrument`、`maestro test`)都來自專案自己的 `.lumos/macrobench.json`。計劃第 162 行明寫這跟專案建置腳本是同一個信賴等級。
- `exits.new` 的 desc 與 `logcat.txt` 的違規行是裝置端文字,但 skill 只叫 AI「看」,沒叫它照做。收集腳本有只留違規行的過濾。
- 沒有教 AI 下載或執行來路不明的腳本。`java_heap_dump`、`heap_profile` 釘在 Perfetto v57.2 的固定網址,SKILL 開頭已寫「不要抓 main」。

## ② 讀寫與執行越界:已看,無
- 快照放在 `.lumos/artifacts/android/<run-id>/`。收集腳本在動裝置之前,逐一用 `git check-ignore` 問 `ARTIFACTS` 裡 7 個檔名,沒被忽略就回 2(`scripts/templates/android-stability-collect.sh:27`、`scripts/templates/android-stability-collect.sh:346-352`)。
- reference 教「`adb shell ls` 看過再刪」裝置暫存,沒有萬用字元整批刪的指令。
- 7 天刪除只刪產物目錄底下的 `heap-*.pftrace`。這點我只讀了文件,沒有實跑收集腳本;腳本本身歸程式席。

## ③ 非刻意守衛繞過:1 條 minor

照 reference 範例填 `test_data`、只改日期不改人名時,偽署名過得了 `--check-config`,使用者沒授權也會錄 Java 快照。

severity: minor
blocking: 否

引句:「"test_data": {"value": true, "decided_by": "<裁定的人>", "decided_at": "<YYYY-MM-DD>"},」

- **攻擊路徑**:誰是照常操作的 AI。從哪是照抄 reference 這份範例,把 `decided_at` 換成真日期,`decided_by` 忘了換。送出去的是 `{"value": true, "decided_by": "<裁定的人>", "decided_at": "2026-10-24"}`。拿到的是 7 天保存規則所依賴的「人寫的署名宣告」被空殼署名滿足,收集腳本照樣錄兩份 heap。
- **實跑**:在 `/tmp/lumos-seat-work/code-android-mem-stability/文件-資安-sonnet/p` 建一個設定檔,執行 `python3.14 <工作樹>/scripts/lumos macrobench --repo . --check-config`。
  - `decided_by` 為 `<裁定的人>`、日期為 `2026-10-24`:印「macrobench 設定與門檻檔都合格。」,rc=0。
  - 日期為 `<YYYY-MM-DD>`:rc=2,擋下。
- **原因**:程式只擋日期佔位,`decided_by` 只要是非空字串就放行。
  - file: `scripts/lumos:39445-39450`,`decided_by` 只驗 `str` 且 `strip()` 非空。
  - reference 的文字有叫 AI 先問人,所以只有 AI 沒照做才會踩到。這是一步內可誤觸、不是刻意偽造。
- **歸因**:有證據的原有漏查,不是修補回歸。
  - 修前 44d93aba 的 reference 範例是真名 "Enzo"、真日期,`scripts/lumos:39448` 的 `decided_by` 檢查邏輯相同,所以當時就沒有佔位偵測。
  - 修後範例改成佔位,同時在文件端補了「日期佔位會被擋」的防線,但人名佔位沒補。
  - 我只對修後版本實跑了命令,修前版本是靠讀 `git show` 的程式碼比對,沒有再跑一次。
- **建議**:`decided_by` 也拒絕 `<` 開頭的佔位;或範例的人名改成一個明顯非法的值。

## 三問
1. **原問題的修復效果**:佔位日期被擋這點已用實跑驗證(rc=2)。其餘修復歸程式席與測試席,我沒驗。
2. **修補處的相鄰路徑**:`test_data` 缺省、型別錯、日期錯都回 2 或不錄快照,讀程式碼確認過。只有上面這條人名佔位漏網。
3. **同一案例兩版結果**:修後 rc=0,修前同一邏輯,見上方歸因。

## 未驗範圍
- 收集腳本實際的 7 天刪除與裝置暫存清理,沒有用假 adb 跑。
- heap_profile 的 `-o <目錄>` 在 SKILL L3 第 1 步沒有限定位置。上層規則已寫「原始檔只放 artifacts 目錄」,所以我不單獨列成 finding。
- 暫存目錄 `/tmp/lumos-seat-work/code-android-mem-stability/文件-資安-sonnet/p` 只剩空的 `.lumos` 設定檔,`.git` 已刪。

最嚴重 severity:minor,blocking 共 0 條。
