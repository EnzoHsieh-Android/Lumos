severity: minor

## 圖譜鏡頭(固定席節點)

- 節點〈Systems/kotlin規則包〉:管 5 支檔,沒有 KEY 行、沒有合約,只有一條 `RULE:規則在真專案誤報超過命中的一成就降提示級或改形狀`。本設計不碰會擋的規則與它的範圍,只在不接閘目錄裡改規則、型錄文字與卷證。判「不影響」。理由:這條 RULE 管的是已擋的規則,而本設計的結論(7 條都不升)正是讓它們留在不接閘,不跟 RULE 衝突。
- 計劃節點本身(提交 7b4469e):沒有宣稱會被這份修訂稿改壞的行為或合約。判「不影響」。

## Finding 1
severity: minor
blocking: 否
判準:卷證要能讓外人重現抽樣與去重。
spec 段落:〈實驗〉〉外部網址那條:第二份語料(判準 v2)
問題:v2 的「同源合併後 406 處、366 個 repo」和「種子 20261112 抽 40 處」在卷證裡都重現不出來。`sample.py.txt` 只有 20261111 版。卷證沒有 v2 的命中檔、去重清單或抽樣腳本。
引句:「種子 20261112 抽 40 處;每處抓那個 repo 所有 AndroidManifest.xml(40 處都抓到)。」
佐證:
- 重算命中:`hits.jsonl` 在 scratchpad 裡共 531 筆。用 v2 的關鍵字(insecure、vuln、goat、damn、ctf、owasp、testdata、sast)濾掉後剩 504,恰好排掉 27 筆,對得上。這 504 筆分布在 418 個 repo,不是 366。
- 重現抽樣:拿 504 筆套 `sample.py.txt` 的流程、改種子 20261112,前 40 個 repo 跟 `sample-loadurl-v2.txt` 只有 6 個重疊。`pick.json` 的順序也不是洗牌順序。
- 對比第一份語料:同一支腳本重跑 TLS、loadurl、指令執行三條,抽到的位置跟 sample 檔完全一致。v2 沒有等價物。
- 其他數字對得上:`corpus-loadurl-v2.tsv` 共 1384 列、1286 個 repo,跟排除清單 `excl-repos-v2.txt` 的 6147 個零交集。6147 等於 3796 加第一批新撈的 2351 個 repo。
- 影響:v2 的 31/40 誤報不是靠這一步撐住的(v1 本來就 20% 不過關),所以只記 minor。

## Finding 2
severity: minor
blocking: 否
判準:宣稱的排除規則要在實際抽到的樣本上成立,漏網要寫進天花板。
spec 段落:〈實驗〉v2 的四點差異,與 PRIOR-ART
問題:規則說「刻意寫弱的資安教材與掃描器測試語料不進抽樣」,但抽到的 40 處裡有 2 處是掃描器測試固件。篩選只比對 repo 名或路徑上那幾個關鍵字,`fixtures` 和 `masaudit` 沒有在清單裡。
引句:「刻意寫弱的資安教材與掃描器測試語料不進抽樣、同一份程式複製到不同 repo 只抽一處」
佐證:
- 漏網兩處:序號 13 的 `hossam9k__masaudit/tests/fixtures/AND-014/clean_not_exported/...`,判 FP。序號 39 的 `mohamedma872__ai-agent-workflow-kit/ai/tasks/subagent/fixtures/security-webview/HelpActivity.kt`,判 UNSURE。
- 命中池裡還有同類的:`masaudit` 另外 3 筆 `vulnerable*`,`pwrgrep-rules/testdata` 被擋掉了,`masaudit` 沒被擋。
- 全部排掉這兩處:FP 30/38,等於 78.9%,結論不變。
- 缺的是誠實面:〈天花板〉沒有這一條。

## Finding 3
severity: minor
blocking: 否
判準:敏感度段的數字要能從卷證重算,算不出來的要改正。
spec 段落:〈實驗〉換算法的敏感度,外部網址那條
問題:「3 處只靠 repo 名」加上「再排除教材」,照卷證只能算出 4/37(10.8%),不是 3/37(約 8%)。10.8% 超過一成,「會過條件」這句就不成立,變成壓線。
引句:「若 repo 名不算訊號,再排除教材,是 3/37 約 8%,會過條件。」
佐證(重算,資料在 `experiment/judge-loadurl.md`):
- 8 個 FP 裡範例碼 6 個。只靠 repo 名的是 casdoor-android-example、VpnDemo、autra-3ds-webview-example 這 3 個。
- 另外 3 個是靠路徑判的:Vulnetix 的 testdata、MixPush 的 example/、ReachFive 的 sdk/demo。
- 3 個只靠 repo 名的改成 TP,FP 變 5。再排除教材:Vulnetix 這個 FP 掃描器語料,加上兩份 InsecureShop(兩個 TP),樣本剩 37 處、FP 剩 4。
- 4/37 = 10.8%,Wilson 區間 4.3% 到 24.7%。要得到 3/37 得把第 4 個也改判成 TP(ReachFive 的 `sdk/demo` 路徑含 demo,casdoor 的 `com/example/` 也含 example,所以歸誰有歧義)。
- 這段本來就聲明「不靠這份語料決定」,所以不動結論。但文字寫錯了一件可驗的事,而且數字剛好踩在門檻兩側。

## Finding 4
severity: minor
blocking: 否
判準:口徑要全份一致,排除集合要列得出來。
spec 段落:〈實驗〉換算法的敏感度,TLS、指令執行、Provider、資料庫四條
問題:
- 排除了哪幾列沒有存進卷證,說「編排者重算」卻沒有清單或腳本。
- 「repo 名不算訊號」這個口徑只套在外部網址那條,其他條沒套。
佐證:
- 數字大致可驗:TLS 9/38 = 23.7%,指令執行 28/38 = 73.7%,Provider 8/19 = 42.1%,資料庫 4/25 和 3/11、Wilson 6.4% 到 34.7% 都算得出來。
- 指令執行需要排掉 2 個 FP,但判讀檔裡只有 `m14r41__scan4secrets` 1 列符合 v2 的關鍵字。第二個沒有依據。
- TLS 排掉的 2 個 FP 疑似是 `SWE-gen-Java` 的測試碼與 `harbor-datagen` 的函式庫複本。它們是基準資料集或複本,不是「刻意寫弱的資安教材」,這個口徑放寬沒寫明。
- 口徑不一致:TLS 的 TTSDemo 與 ocr-android-demo、資料庫的 UnitTestDemo 都是只憑 repo 名判 FP。照外部網址那條的做法拿掉這個訊號,TLS 約 7/38(18%)、資料庫 3/25(12%)。結論仍然是都超過一成,但資料庫那條離門檻近了。
- 建議:把排除與改判的列表存進卷證,四條用同一套口徑重算。

## Finding 5
severity: minor
blocking: 否
判準:承認的限制要涵蓋判準本身的盲區。
spec 段落:〈實驗〉v2 判準,與〈天花板〉
問題:v2 把「manifest 上沒對外開放」直接當 FP。31 個 FP 裡 24 個靠這條,占 77%,是 77.5% 的主體。這其實是量「外部 Intent 直接打得到」,不是量規則形狀精不精。
引句:「誤報裡 24 處是畫面根本沒對外開放、已防護 2、可信來源 3、測試或範例碼 2。」
佐證:
- 沒對外開放的畫面,網址可以由同 App 的 exported 元件(深層連結中繼畫面、通知的 PendingIntent、推播點擊)轉送進去。這種轉送路徑在判準裡沒處理,卷證也沒查。
- 我沒有逐一追溯,只確認序號 14、31、4、2、38 附近的 `activity-alias` 都不指向被判 FP 的 WebView 畫面。
- 40 處的 manifest 結構判讀我用腳本逐一核對,全部對得上:5 個 TP 都明寫 `exported="true"` 並帶 intent-filter;4 個 UNSURE 的 Activity 都真的不在抓到的 manifest 裡;FP 的「無 intent-filter 且沒寫 exported」與 `exported="false"` 判斷都對。Android 12 以後「帶 intent-filter 卻沒寫 exported」會編譯失敗,這 40 處裡也沒有這種情形,所以預設值那一支沒踩到。
- 缺的是〈天花板〉沒承認這條盲區,也沒給回頭條件。REVISIT 3 的第二版形狀(只報 exported 的 Activity)直接繼承這個假設。

## Finding 6
severity: minor
blocking: 否
判準:〈天花板〉每句承認都要配做得到、不會自動滿足的回頭條件。
spec 段落:〈天花板〉與 REVISIT 六條
問題:
- 「點估計」與「第一份語料看不到 manifest」兩句,只掛在一條「每條不接閘規則要再量時」的條件下,沒有觸發事件,也不是對這兩句的具體回應。
- REVISIT 5 的標準比同份文件另一條寬鬆。
- REVISIT 3 有一個永遠成立的出口。
佐證:
- REVISIT 5(寫死金鑰、弱加密套件加到 6 組查詢,命中到 20 處才判):現在 14 處只分布在 6 個 repo,8 處只分布在 4 個 repo(`hits-kt-secretkeyspec-literal-key.json`、`hits-kt-weak-cipher-suite.json`)。REVISIT 2 為了資料庫要求「獨立 repo 至少 20 個才判」,這裡卻只要命中 20 處。同一種問題兩個標準,而且 20 處可能只來自十來個 repo。
- REVISIT 3 結尾「做不到就維持不接閘」,任何結果都算完成。規則包用 ast-grep,spec 沒說怎麼讀 manifest。
- 〈天花板〉沒給 v2 自己的信賴區間。Wilson 95% 約 62.5% 到 87.7%,真問題 5/40 約 5.5% 到 26.1%。REVISIT 1 要求下次才給。
- 方向論證也可補:加 manifest 只會把 TP 改成 FP,不會讓這 7 條翻成能升,所以第一份語料看不到 manifest 不威脅「不升」的結論。spec 沒寫這一句。

## 各審查點結論

- ①v2 判準是否先凍結:已讀,無 finding。`shasum -a 256 judge-loadurl-v2.md` 輸出跟 `judge-loadurl-v2.sha.txt` 的 `e2fd46c3...4f` 逐字相同。原始工作目錄裡 `judge-loadurl-v2.md` 的時間是 22:03:10,`pick.json` 22:20:49,`hits.jsonl` 22:20:48,`corpus/` 22:19:49,判準早於語料約 16 分鐘。判讀代理有照 v2:序號 21 的理由寫了「repo 名帶 samples 不算訊號」,17 與 13 只看路徑。
- ④口徑:已讀,無 finding。誤報÷判讀數、判不準留分母,在所有列都一致:11/40、8/40、30/40、8/21(去重 8/20)、4/25、31/40 都算得出來。`judge-loadurl-v2-result.md` 的總計列本身自己改了一次數字(先寫 25 再更正成 24),spec 採用更正後的 24,正確。
- ⑥「7 條都不升」:已讀,無 finding。命中數、去重位置數、repo 數(428/361/240、190/190/153、111/111/72、21/20/20、25/25/11、14/14/6、8/8/4)我都從 `hits-*.json` 重算過,全部相符。五條抽判的誤報比例都高於一成,另外兩條命中都不到 20,不升站得住。外部網址那條即使照 v1 也是 20%,所以不依賴 v2 的盲區。

## 實務隱患

- 金流:無。只改規則包不接閘目錄、型錄、測試與圖譜,spec 的實務隱患節同此結論。
- 對外送出:無。實驗階段的 GitHub 搜尋與 manifest 下載只讀公開 repo。
- 不可逆:無。全是 repo 內文字檔,退回提交即還原。
- 守衛面:無。不改會擋的規則,推送前行為不變。
- 資料外洩或個資:無。語料都是公開 GitHub 程式碼。
- 實驗性判讀的隱患:有,已併入 Finding 3 與 Finding 4(敏感度數字靠編排者手算、沒有可重算的清單)。

最高等級 minor;blocking 0 條

我在 `/tmp/lumos-seat-work/android不接閘資安規則重量/實驗可信二-sonnet/` 下建了三個暫存檔(重跑抽樣的輸出):
- `/tmp/lumos-seat-work/android不接閘資安規則重量/實驗可信二-sonnet/x-kt-insecure-tls-version.txt`
- `/tmp/lumos-seat-work/android不接閘資安規則重量/實驗可信二-sonnet/x-kt-loadurl-external.txt`
- `/tmp/lumos-seat-work/android不接閘資安規則重量/實驗可信二-sonnet/x-kt-command-exec-nonliteral.txt`

repo 裡的檔案我都沒動,也沒跑 commit、reset、restore、checkout 或 stash。
