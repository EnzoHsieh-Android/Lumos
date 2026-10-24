severity: minor

最近一次修補(f3b5876f 到 0aa3adbb)改過的每一句,我都對過出處,沒有找到事實錯誤,也沒有中英不對應。下面三條是修補帶出或周邊的精度問題,都是 minor。`--check` 我實際跑過是綠的;兩個改壞實驗用的是 `/tmp/lumos-seat-work` 下的複製檔,做完已用字面絕對路徑刪除複製目錄 x(`/tmp/lumos-seat-work/code-readme-android-e2e/單審-sonnet/x`);我另外複製的 g.py 沒刪。

## F1 新加的結構檢查綁在標題字串上,標題一改檢查就整段不跑
severity: minor
blocking: 否
引句:「if root.find("s:title",ns).text in {"Android: check first, then dig one layer at a time.","Android：先判有沒有問題，再一層一層往下查"}:」
出處(兩個改壞實驗,都在複製的產生器上做):
- 實驗一:只把場景裡的標題改成 `Android: check first, then dig layers.`,validate 裡那份標題集合不動。重產後 `--check` 仍印「24 bilingual SVGs: validated…」,四層、輸入、捷徑、查證紀錄的結構檢查全被略過。
- 實驗二:把 `(438,"L2"` 改成 `"L9"`,標題不動。`--check` 紅,斷言錯誤。
- 所以「改壞一層的編號會紅」成立,但「改標題會讓檢查靜默失效」也成立。
- 原有的 defence-layer 檢查是同一種寫法,所以不算新退步。
- 佐證行:``file: `assets/readme-diagrams/generate.py:491` `` 與 ``file: `assets/readme-diagrams/generate.py:573` `` 各寫一份標題字串。
失敗場景:之後有人潤飾標題只改一處,檢查無聲變成空殼,而 Systems 節點仍宣稱它會紅。
建議改法:標題字串抽成一個常數,場景與 validate 共用。或改用 `data-kind` 之類的標記判斷是哪張圖,而不是比對標題文字。

## F2 「重跑每一條查詢」說過頭,沒寫 expect 的查詢被跳過
severity: minor
blocking: 否
引句:「with a `rerun.sh` that reruns every query on the same raw data and compares the results in one go」
出處:
- ``file: `scripts/templates/android-receipt-rerun.sh:56` ``:`if kv.get('expect', '-') == '-': continue`。沒有 expect 的查詢不跑,也不比對。
- 同一支腳本的檢查只要求至少有一條帶 expect。
- 中文版「對同一批原始資料一鍵重跑每條查詢、比對結果」同樣寫成「每條」。
- 「同一批原始資料」「原始資料不進版控」這兩點與 SKILL(artifacts 目錄不進版控)一致。
失敗場景:讀者以為紀錄裡每條查詢都被驗過。實際上只有標了預期結果的才驗。
建議改法:改成「重跑每條標了預期結果的查詢並比對」。中英兩版一起改。

## F3 「記憶體檢查沒過就直接跳 L3」涵蓋範圍比實際大
severity: minor
blocking: 否
引句:「When a memory check fails, it jumps straight to L3: the two middle layers look at where CPU time goes, and memory problems do not show there.」
出處:
- ``file: `skills/lumos-android-evidence/SKILL.md` ``(L0 第 8 步):只有 `native_unreachable`、`java_growth`、`instances`、`peak_vitals` 直接進 L3。
- 同一步:`frozen` 走 L1,`exits` 與 `strictmode` 只是去看 `stability.json` 與 `logcat.txt`。
- 同一步:專案沒有宣告測試資料時,不往下走,收據記 `[GAP] L3 未授權`。
- 這一句緊接在七項清單之後。修補把清單改成「Lumos 判斷七件事」,使「記憶體檢查」更可能被讀成七項全部。其中三項(凍結、結束紀錄、StrictMode)並不跳 L3。
- 這一句不是這次修補改的,是既有句子。
失敗場景:讀者以為畫面凍結或 StrictMode 違規也會自動去拍記憶體快照。
建議改法:改成「物件或原生記憶體越積越多、峰值太高這幾項沒過時,在已宣告只用測試資料的前提下直接跳到 L3」。凍結改說回 L1。

## 修補逐句核對表

| 修補改的句子 | 對照出處 | 判定 |
|---|---|---|
| 別人「拿到同一批原始資料」才能重跑 | SKILL 與 `android-receipt-rerun.sh`:查詢跑在 artifacts 的 trace 上,原始檔不進版控 | 一致 |
| Lumos 負責串接:判變慢與要不要往下查、接各層工具 | SKILL 開頭「Lumos 只負責 L0 的比對,執行由 Agent 照這頁做」,往下條件在 L0 第 8 步 | 一致 |
| 摘要標題改「See what each layer does…」 | 無事實內容 | 無事實問題 |
| simpleperf 是 Android 附的效能抽樣工具,每毫秒記一次 | SKILL L2 用 `-f 1000`(1000 Hz);simpleperf 在 NDK 內 | 一致 |
| skill 和每個工具「各自」固定在一個版本 | SKILL 開頭表:skill 的 commit、Perfetto v57.2、錄製腳本、NDK 28.2 | 一致 |
| 專案自己的 UI 測試開關畫面;收集腳本在旁邊收資料;`lumos macrobench` 判七件事;每項要標準檔有一條才判 | collect.sh 的 `driver(st["driver"], …)`;`MACROBENCH_CHECK_JUDGES` 共七種;`_macrobench_judge_stability` 只處理帶 `check` 的條目 | 一致(七項數目對) |
| 「C/C++ 那一側」沒人指著的記憶體 | `native_unreachable` 用 `dumpsys meminfo --unreachable` | 一致 |
| StrictMode 要專案在測試版打開,且在設定檔宣告;沒宣告就跳過 | collect.sh 的 `strictmode_result` 在沒宣告時回 unsupported;計劃 S7 | 一致 |
| 宣告了卻沒真的打開,會收不到違規而被誤判通過 | 只認含 `StrictMode policy violation` 的行,空清單會讓 `_macrobench_stab_strictmode` 回「沒違規」;計劃 WHY 也寫了「設計審 r1 指出沒開時恆為零筆」 | 一致 |
| 已安裝 App「用檔案指紋比對」 | SKILL L0 第 3 步:從裝置拉實際安裝的 APK 算 sha256 | 一致 |
| rerun.sh 對同一批原始資料重跑;原始資料只留本機 | 見 F2;SKILL 的「不准做的事」 | 重跑範圍過說(見 F2),其餘一致 |
| 每畫一幀,較慢那一成幀的處理器時間 4.3 到 10.4 毫秒 | 驗收紀錄 2026-10-23:`frameDurationCpuMs P90 4.3→10.4` | 一致(P90 說成「較慢的一成」是通俗講法) |
| 指到實驗 App 的 `MainActivity.kt` 第 36 行 | 同一份驗收紀錄:`MainActivity.kt` 第 36 行 `busyWait(bindDelayMs)` 佔 86.6% | 一致 |
| 容差暫定:預設 10%、另有 1 毫秒下限,之後用多次實機重跑的資料重訂 | `MACROBENCH_DEFAULTS` 的 `tolerance_pct` 10.0、`abs_tolerance` 1.0;`max(base*pct, abs)`;Verification 與計劃的 `REVISIT:2026-12-21` | 一致 |
| Maestro 說明:用文字寫好點哪裡、輸入什麼的畫面自動操作工具 | 計劃以 `maestro test` 為驅動之一,Maestro 驅動目前屬子案二 | 一致 |
| 設定與標準的連結後括號由「in Chinese」改成「Chinese」 | 無事實內容 | 無事實問題 |
| 圖的說明文字(desc)全部改寫 | 兩種輸入;L0 對基準與人訂標準;有問題才 L1;L2 指函式與行號;L3 須人同意只用測試資料;虛線從 L0 到 L3;每層沒問題就記下並停;全部可重跑 | 與 SKILL 一致;中英逐項對應 |
| 英文徽章 L2「Android tool」、中文「Android 工具」;子標改成「Open/close a screen: memory, crashes」 | 無事實內容 | 無事實問題 |
| 中英兩版 README 段落、alt 文字與 SVG desc | 逐句比對 | 對應;全 repo 檢查 README 與兩張 SVG 的「收據」,零筆(英文版的 receipt 也零筆) |

## 圖譜鏡頭(固定席:Systems/README圖產生器)
- **筆記宣稱的行為**:產生器產出 24 個雙語 SVG,場景數更新,android-e2e 的 validate 四層依序為 L0 到 L3、輸入、捷徑、查證紀錄各一個。
- **結論**:這次 diff 不破壞這些宣稱。`--check` 實跑為綠,「改壞層編號會紅」我用實驗二確認成立。
- **唯一缺口**:筆記沒寫的前提,是檢查靠標題字串觸發(F1)。這是新增檢查的脆弱點,不是對既有宣稱的破壞。

總結:全篇最高為 minor
