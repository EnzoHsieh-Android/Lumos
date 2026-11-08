preflight-4: ran

# r1 收貨紀錄(android資安靜態檢查補齊第二批)

## 首輪前掃

①②③直接修真檔:補「判不準=judge-oos.tsv 的 UNSURE」定義;「理由分三型」改成兩型(弱套件的樣本內 82% 併入命中不到 20 那型註記);誤報比例改寫到小數一位;DATA-27 的〈待查證〉那行註明由程式從主表撈。④語意類:

| 編號 | 修改前 | 修改後 | 依據 |
|---|---|---|---|
| P1 | 範圍 4「改名改訊息照既有格式」,初稿訊息開頭是 `[SEC-xx]`,S2 要以型錄列編號開頭 | 範圍 3 寫死 13 條規則與 2 個內建檢查各對到的型錄列編號(API-48~50、DATA-88~95、併進 DATA-79/82/83、ARCH-89),初稿的 `[SEC-xx]` 實作時換掉 | 前掃讀初稿 |
| P2 | 混合內容只寫常數與 setter | 補「整數字面值 0 也認」,預期值表加一列 | 初稿的 always-allow 也比對字面值 0 |

## 收貨(四席到齊後一次寫進卷證)

- 四份報告從子代理逐字稿存檔;整合席第 105 行「Lint 檢查頁嚴重度」被正規化當成嚴重度宣告,退回該席只改那一行措辭重交(續談同一席,內容與等級不變)。
- quote-check 四份全數錨定;refcheck 四份 missing 0;seat-check 讀不到派工單的材料清單(派工單用 seats 陣列,工具回 vacuous 豁免),沒判漏查。
- 邊界席臨時目錄 `/tmp/lumos-seat-work/android資安靜態檢查補齊第二批/` 收貨後刪。

## 編號與處置

編號:通才 g1–g6、邊界 b1–b2、整合 i1–i6、架構對齊 a1–a5(照各報告 finding 出現順序)。

| id | 席原等級 | 一句 | 重現 | 處置 |
|---|---|---|---|---|
| g1 | minor | 混合內容 40 處抽樣太小、fork 重複、產品需求判 TP 與準則不一致、`cfg.mixedContentMode = 0` 誤擋 | HIT:重判代理拿原規則跑 `cfg.mixedContentMode = 0` 報 | 折:擴大重判 120 處(fork 去重)、`= 0` 限 settings 接收者、新增用詞「產品需求」、天花板第 3 點 |
| g2 | minor | SdCardPath 的修法建議會被 kt-external-storage-hardcoded 擋 | HIT:rules/data.yml 的 kt-external-storage-hardcoded 比對 getExternalStorageDirectory | 折:範圍 2 DATA-27 標準寫法加一句、實務隱患 |
| g3 | major | 錯登列併入不接閘規則,批四口徑逼整列寫批四 | HIT:check.py batch4_expected_tags 只要現成規則欄有 內建:/資安包: 規則碼就要求批四 | 折:管不到的那半另開 DATA-96、97、98,不併 |
| g4 | minor | 〈待查證〉〈統計〉其實手寫 | HIT:check.py 只找〈待查證〉節位置、不產生 | 折:範圍 6、S4 |
| g5 | minor | DATA-95 要 AGP 8.8.0、SecretInSource 8.3.0;DATA-83 弱演算法清單少 RC5、ARCFOUR | HIT:檢查頁 Since;原始碼 VULNERABLE_* 兩個集合 | 折:範圍 1、2,實務隱患 |
| g6 | major | 語意 7 種判太快,其中幾種核心是形狀;沒有 REVISIT | HIT:MASTG-DEMO-0090 用 Semgrep 認沒帶 CryptoObject | 折:生物辨識、指令執行寫成不接閘規則(另加 setAllowFileAccess 漏網一條);其餘 5 種寫不做理由並各附 REVISIT |
| b1 | major | setter 的 has 帶 stopBy: end,內層呼叫帶 0 就報 | HIT:重判代理對照組 `setMixedContentMode(resolve(0, 1))` 原規則報、改後不報 | 折:範圍 4 setter 只看直接參數,預期值表兩列 |
| b2 | minor | 值藏在 if、elvis、括號、轉型裡漏報 | HIT:重判代理在 KernelSU 看到 if 運算式漏報 | 折:實務隱患寫已知漏報 |
| i1 | major | Zip Slip 預期值照字面測不到 | HIT:draft-rules 的 zip 規則要求函式內有 Zip 字樣 | 折:預期值表改成完整函式 |
| i2 | major | 同 g5 的 DATA-95 版本 | 同 g5 | 折(同 g5) |
| i3 | major | 「〈待查證〉由程式從主表撈」是錯的,〈統計〉沒列範圍 | HIT:同 g4;這句是首輪前掃我自己加的 | 折:範圍 6、S4 |
| i4 | minor | 同 g3 | 同 g3 | 折(同 g3) |
| i5 | minor | 初稿 8 條訊息超過 120 字 | HIT:check.py MSG_MAX=120 | 折:範圍 4 訊息一點 |
| i6 | minor | 22+1 條數在卷證查不到、與下游 25 對不上 | HIT:experiment/ 原本沒有對照表 | 折:對照表存 experiment/mobsf-compare.md,〈實驗〉〈MobSF 對照〉逐條對到下游;白話改成 17/1/4/5/23 |
| a1 | minor | Zip Slip、XXE 第二份路徑排除清單 | HIT:_KTSEC_IGNORES 恰好八項 | 折:統一八項,實驗差異寫明 |
| a2 | minor | 同 i5 | 同 i5 | 折(同 i5) |
| a3 | minor | S2 只斷言目錄沒斷言檔 | HIT:_KTSEC_PLACE 記 (目錄, 檔, 編號) | 折:範圍 4 寫每條放哪支檔、S2 |
| a4 | minor | 另開測試還是擴充 _KTSEC_* | — | 折:S1、S2 改綁既有 t_kotlin_rulepack_security_rules(擴充三張表) |
| a5 | minor | 併入列的形狀、通電批次欄沒寫 | 同 g3 | 折(同 g3) |

沒有放行、沒有重現不到的;--refuted-set none。

## 先查世界

- PRIOR-ART:錯登混列(g3、i4、a5)——查 Google 資安包原始碼:Google 自己把弱演算法(VulnerableCryptoAlgorithm)與不安全模式填充(UnsafeCryptoAlgorithmUsage)拆成兩個 issue、各管一件事;MobSF 也是一種寫法一條規則。採用「一列管一件事」,管不到的另開新列。來源:https://github.com/google/android-security-lints(摘錄 experiment/lint-badcrypto-excerpt.md)。
- PRIOR-ART:混合內容 setter 誤報(b1)——ast-grep 官方關係規則文件:has 預設 stopBy neighbor 只看下一層,stopBy: end 找到葉節點。採用:逐層寫到 value_argument。來源:https://ast-grep.github.io/guide/rule-config/relational-rule.html。排除:單純拿掉 stopBy: end(重判代理實測永遠對不上,Kotlin 參數在第三層)。
- PRIOR-ART:語意 7 種(g6)——OWASP MASTG-DEMO-0090 用 Semgrep 認 BiometricPrompt.authenticate 沒帶 CryptoObject(https://mas.owasp.org/MASTG/demos/android/MASVS-AUTH/MASTG-DEMO-0090/MASTG-DEMO-0090/);Semgrep Kotlin 規則 command-injection-formatted-runtime-call 只認串接與 String.format、官方標低信心(https://registry.semgrep.dev/rule/kotlin.lang.security.command-injection-formatted-runtime-call.command-injection-formatted-runtime-call)。採用:兩條寫成不接閘形狀規則;指令那條實驗誤報高就收窄成 Semgrep 的形狀。LocalServerSocket、XOR、通知、鍵盤快取查不到權威出處支持「出現就是錯」,不寫規則、附 REVISIT。
- PRIOR-ART:〈待查證〉〈統計〉手寫(g4、i3)、AGP 版本(g5、i2)、Zip Slip 預期值(i1)、訊息長度與放置(i5、a1–a4)——規則包既有慣例與官方檢查頁、Zip Path Traversal 官方頁的範例,沒有要另查的業界做法。
