# r1 收貨紀錄(android資安靜態檢查補齊第三批)

preflight-4: ran

## 首輪前掃(派一席照固定清單掃)

- ① 未定義的詞(既有八項、通電批次、批一、批三、情境決策表、證據樣式、新增告警閘、lint-waive、規則包 WHY、UNSURE、判讀代理、種子):補進〈用詞〉與實驗段,不算 finding。
- ② 壞引用:無(7 個網址都回 200;第二批計劃第 84、88、96、99、100 行對得上)。
- ③ 範圍自相矛盾(修改前→後):
  - 白話段「有一件寫得出規則」對「前兩件寫成規則」→ 改成三件找到出處、兩件寫規則、一件語意列。
  - 〈回退〉有 Systems/kotlin規則包、〈範圍〉沒有對應工作 → 補範圍 5。
  - 「排除桌面四項補掉桌面誤報」→ 3 筆只有 1 筆落在四項裡;改寫成「排除只擋得到照多平台慣例放的桌面碼」,實驗段補兩份樣本外合計 8.75% 的照實算法。
  - 缺漏:三列的級與通電批次、Jackson 的 severity → 寫進範圍 1、2。
- ④ 機械宣稱驗語意(修改前→後):
  - D-57 證據樣式放行單寫 VISIBILITY_PRIVATE(預設值)→ 改成 `setPublicVersion\(|VISIBILITY_SECRET`。
  - S3 綁的 t_kt_catalog_stats_consistent 不驗「問題數 0、三列存在」→ S3 改綁 t_kotlin_catalog_rows_wired(驗整體 0 問題),三列與 D-57 存在另開 S4 綁 t_kotlin_rulepack_security_rules。
  - 〈統計〉情境決策表列數 stats_problems 不核對 → 範圍 4 寫明照手數。
  - 既有測試對每條規則斷言恰好八項排除,密碼欄 12 項會紅 → 範圍 2 寫明測試改成逐條期望值。
  - 訊息格式還要求分號、「改用」或「改成」、不含 $ → 範圍 2 寫齊,卷證初稿要重寫。
  - 完整套件名的呼叫不認 → 寫進〈天花板〉。
- 沒有動到核心裁定的條目。

## 收貨(2026-11-08)

四席(通才、正確性、實驗可信、架構對齊)交回後一次存檔,取自逐字稿;四份已是正規化格式,引句全數錨定,refcheck 引的檔與行號都存在。通才席初交時第 2 條寫 severity major、blocking 否,兩欄矛盾,退回該席重判;該席改成 minor 並重交整份報告(與初交只差那一行,初交版不放卷證)。編號:通才 g、正確性 c、實驗可信 e、架構對齊 a。

| id | 席 | 原報 | 一句 | 重現 | 處置 |
|---|---|---|---|---|---|
| g1 | 通才 | major | 照範圍 4 只改型錄,`_KT_STATS_LINES` 還寫舊數,改壞套不上、整支測試紅;S3/S4 沒綁這支 | HIT:讀 test_lumos.py 的 _KT_STATS_LINES 與前置斷言 mut != text | 折:範圍 4 點名一起改,S3 改綁 t_kt_catalog_stats_consistent |
| g2 | 通才 | minor | 帶了 keyboardOptions 就放行,字面 KeyboardOptions(imeAction=…) 沒設密碼鍵盤漏報 | HIT:草稿規則實跑,第 4 行那種寫法不報 | 折:第三版形狀②,預期值表補列 |
| g3 | 通才 | minor | 統計括號裡證據樣式分項沒同步(31→32) | HIT:型錄 1123 行 | 折:範圍 4 寫明分項;D-57 改兩段 (無) 後是 8→9、31→32、5→6 |
| g4 | 通才 | minor | SecureTextField 名稱是死字、BasicTextField 沒測試 | HIT:Material3 SecureTextField 沒有 visualTransformation 參數 | 折:名單拿掉兩個 Secure,預期值表補 BasicTextField、BasicTextField2、SecureTextField 三列 |
| c1 | 正確性 | minor | 天花板漏列實跑量到的漏報(vt 變數、字面 KeyboardOptions 沒設 Password、TextField<T>、自訂名) | HIT:第三版逐例 `experiment/pwd-v3-cases.kt.txt` 16 例對得上 | 折:字面那種改成報,其餘寫進〈天花板〉 |
| c2 | 正確性 | minor | D-57 標準寫法「通知只說有一則新訊息」寫不出特徵,證據樣式卻只寫 setPublicVersion | HIT:型錄證據樣式規定「同一段裡有寫不出特徵的寫法…寫 (無)」 | 折:兩段都 (無)、不放情境樣本(自檢會報樣本沒有作用) |
| c3 | 正確性 | minor | 同 g3 | HIT:同 g3 | 折:同 g3 |
| c4 | 正確性 | minor | Jackson 隱含接收者不報、同鏈兩次報兩次,天花板沒寫 | HIT:讀草稿規則的 navigation_expression 條件 | 折:寫進〈天花板〉,預期值表補隱含接收者不報一列 |
| e1 | 實驗可信 | major | 兩份樣本外合計判升級站不住:第一份看過才改形狀、第一二批都是單份判 | HIT:第一份 7/40、第二版套回仍 6/40;第二批計劃逐條單份樣本外 | 折:凍結第三版形狀、另撈第三份樣本外單獨判(見〈先查世界〉與計劃〈實驗〉) |
| e2 | 實驗可信 | minor | 兩份判讀對範例碼寬嚴不一 | HIT:pwd-oos-judge 把 org.example.project 判 FP,pwd-oos2-judge 把 Login-UI 範本判 TP | 折:判讀準則補操作定義(只看路徑與 repo 名),第三份照新準則判 |
| e3 | 實驗可信 | minor | 天花板承認句沒拆成回頭條件、漏報沒量沒寫、RETIRE-IF 沒寫誰量 | HIT:讀快照〈天花板〉與 REVISIT | 折:拆成三條 REVISIT(漏報、已防護抽查、放行比例) |
| a1 | 架構對齊 | minor | 12 項排除的寫法沒交代 | HIT:compose.yml 只有一處三項多行 ignores | 折:範圍 2 寫明照 data.yml 單行 |
| a2 | 架構對齊 | minor | S4 綁的測試不讀型錄主表、不看情境樣本 | HIT:讀 t_kotlin_rulepack_security_rules | 折:S4 另開 t_kt_catalog_security_lint_batch3 |

### 第三份樣本外判讀的機械重核

判讀代理(乾淨脈絡,只拿判讀準則與語料)交回 TP 39、FP 1;編排者逐 repo 查 `AndroidManifest.xml` 與建置檔 `compose.desktop`(`experiment/pwd-oos3-platform.tsv`):

| 序號 | repo | 判讀代理 | 重核 | 結果 |
|---|---|---|---|---|
| 4 | spbu-coding-2022/trees-2 | TP | 沒有 manifest;app/build.gradle.kts 有 compose.desktop.currentOs 與 application mainClass | 改判 FP(純桌面) |
| 32 | 8bit-void/personal-client | TP | 沒有 manifest;client/build.gradle.kts 是 kotlin("jvm")、compose.desktop、mainClass meteor.Main | 改判 FP(純桌面) |
| 2、18、36 | sztuos、ComposeTodo、ghost-browser | TP | 有 manifest、也有 desktop;命中在 commonMain 或 mobile 模組 | 維持 TP |
| 10、11、35 | Amazon-Clone-、noodle-lms、IIIT-Bazaar | TP | 沒有 manifest 也沒有建置檔,只上傳 Android 原始碼(MainActivity、Firebase) | 維持 TP |

判讀準則沒有「桌面」這一型 FP,判讀代理照準則判不出;改判理由同第一份樣本外的桌面誤報。最後 FP 3/40 = 7.5%。

## 先查世界

PRIOR-ART:密碼欄形狀(g2、g4、c1)——查 OWASP MASTG-KNOW-0055(https://mas.owasp.org/MASTG/knowledge/android/MASVS-STORAGE/MASTG-KNOW-0055/):範例寫法是遮字配 `KeyboardOptions(keyboardType = KeyboardType.Password)`,autocorrect 關掉也不算鍵盤類型;Material3 SecureTextField(https://kotlinlang.org/api/compose-multiplatform/material3/androidx.compose.material3/-secure-text-field.html)預設鍵盤就是密碼、沒有 visualTransformation 參數。採用:字面 KeyboardOptions 沒設 Password 也報、名單拿掉 Secure。沒查到 Android Lint 或 compose-rules 有同一種檢查。
PRIOR-ART:Jackson 形狀(c4)——semgrep 的 jackson-unsafe-deserialization(https://registry.semgrep.dev/rule/java.lang.security.jackson-unsafe-deserialization.jackson-unsafe-deserialization)與 Sonar RSPEC-4544(https://rules.sonarsource.com/java/type/Security%20Hotspot/RSPEC-4544)都是「在 ObjectMapper 上呼叫就報」,不分有沒有點號。不採(這輪):規則在不接閘、誤報 83%,改形狀要新語料重量,併進既有的 Jackson 第二版回頭條件;寫進〈天花板〉。
PRIOR-ART:量測方法(e1、e2)——Dwork 等人〈Generalization in Adaptive Data Analysis and Holdout Reuse〉(https://ar5iv.labs.arxiv.org/html/1506.02629):拿來調過參數的保留集會讓估計過度樂觀;做法是保留集只用一次。採用:凍結形狀雜湊後另撈全新樣本外、只判一次;前兩份改當樣本內。小樣本比例用 Wilson 區間(同第二批),上界照實寫進〈天花板〉。
PRIOR-ART:統計、證據樣式、測試綁定(g1、g3、c2、a1、a2)——專案內規則,不查外部:型錄證據樣式那段規定、situation_sample_problems 的「兩段 (無) 不放樣本」、第二批 S3/S4 綁專屬型錄測試的做法。
