severity: major

建過的路徑:無。我只讀檔,沒有在 `/tmp/lumos-seat-work/android不接閘資安規則重量/實驗可信-sonnet/` 底下建任何東西,也沒有動 repo。

## 固定席節點判讀

節點 `Systems/kotlin規則包`:不影響。理由有三:
- 這份計劃不改 `rules/` 和 `rules-unwired/` 的任何規則,只補型錄 7 列的實測狀態文字。
- 該節點掛 0 條合約、0 行 KEY,沒有行為宣稱會被破壞。
- [S1] 綁的型錄自檢仍守型錄格式。

不影響的前提是 [S2] 補的數字是對的,見 Finding 4。

## Finding 1
severity: minor
blocking: 否
判準:結論「7 條都不升」在資料庫那條(16%)要有站得住的理由;理由寫錯就算推論有洞,即使結論本身沒翻。
段落:〈實驗〉表的資料庫列、〈天花板〉第 2 條。
引句:「| kt-db-on-external-files | 509 | 25(11) | 全判 25 | 4(16%) | 不接閘 |」
引句:「資料庫那條真問題有 12 處來自同一個 repo,樣本不獨立。」
問題:表上這列看起來是「命中 25 ≥ 20、誤報 16% &gt; 10% 所以不升」,但 16% 不是站得住的理由。
- 區間太寬。4/25 的 95% Wilson 區間約 4% 到 37%,涵蓋 10%,點估計撐不起「超過一成」。第二批計劃有給 95% 上界(例:1.7%,上界 5.9%),這份沒給。
- 命中數不獨立。25 處只有 11 個 repo,其中 12 處是同一個 repo(LocalMusicHelper)。按獨立單位算,命中 11 &lt; 20,光這點就不過升級條件。真正站得住的理由是「獨立命中不到 20」,spec 沒寫。
- 12 處真問題的判法有爭議。判讀代理自己在結尾標了:這 12 處是 App 把 asset 複製到 `getExternalFilesDir` 再讀寫,若把「轉檔暫存庫」算匯入就全變 FP,誤報會到 16/25=64%。spec 完全沒提這個爭議。
- 判讀沒考慮儲存範圍。TP 準則沒有 scoped storage 的界線,而 TLS 的準則有 API 21 界線。約 6 處 TP 用的是 `getExternalFilesDir`(App 專屬外部目錄),Android 11 以上別的 App 讀不到,准則對這一點沒有處理。
結論方向在上述所有算法下都不變,所以只算 minor。
佐證:``file: `governance/review-reports/android不接閘資安規則重量/experiment/judge-provider-db.md:60` ``(判讀代理自己標的有爭議判定),``file: `governance/review-reports/android不接閘資安規則重量/experiment/sample-kt-db-on-external-files.txt:1` ``(樣本中重複 repo)。
建議:把資料庫那條的理由改成「獨立 repo 只有 11 個 + 12 處的判法有爭議」,並補上區間。

## Finding 2
severity: major
blocking: 是
判準:spec 宣稱「沿用前兩批量法」,就要和前兩批一致;同一份程式的 fork 不獨立,語料也不該混入故意寫弱的教材。
段落:PRIOR-ART、〈實驗〉抽樣、〈天花板〉。
引句:「量法沿用第一、二批(樣本外語料排除已出現過的 repo,升級條件命中 ≥20、誤報 ≤10%,一份樣本外單獨判)」
引句:「命中多的每個 repo 抽一處、種子 20261111、抽 40 處」
問題:只以 repo 名去重,抓不到 fork 和複製貼上。我回原檔和 sample 清單核對,看到以下現象:
- TLS 的 40 處裡有 9 處是同一支 legado 系 `HttpHelper.kt`(gj009351、GEd520、TsaiYongChuan、GymMickey、Liloupar、GitHub-workflow-APP、hectorqin、TonyStark5、xiahu0911),9 處全判 TP。另有 Lumora 與 ParafusoTV 兩處同碼。扣掉同源重複,獨立單位約 31,FP 約 11/31=35%,不是 27.5%。
- loadurl 的 40 處裡:`InternalWebView.kt`(ics-openvpn 複本)有 3 處,InsecureShop 有 2 處(Vadym-Sokol-Vi、qdeconinck),NewsDetailActivity 有 2 處(psiconnect_mobile、MedMobile)。ics-openvpn 複本在 TLS 那邊的 OkHttp 複本被判 FP「函式庫原始碼複本」,在這邊卻判 TP,口徑不一致。
- InsecureShop 是故意寫弱的資安教材。第二批語料明寫排除「資安教材與規則樣本 repo」,這批 `excl-repos.txt` 沒做。教材判 TP,TP 被灌高。
- 第二批的混合內容重量已經做了「fork 去重」(273 處去重成 244 處),這批沒做。
誤報率被系統性低估(方向偏向「該升」),但目前沒有條改變結論。因此 [天花板] 不能只寫「樣本不獨立」只限資料庫一條。
佐證:``file: `governance/review-reports/android不接閘資安規則重量/experiment/sample-kt-insecure-tls-version.txt:3` ``(legado 系 HttpHelper 多筆),``file: `governance/review-reports/android不接閘資安規則重量/experiment/judge-loadurl.md:20` ``(InsecureShop 判 TP),``file: `docs/lumos-toolchain-knowledge/Projects/Android資安靜態檢查補齊第二批_計劃.md:132` ``(fork 去重前例)。
建議:對 TLS/loadurl/cmd 的 40 處補做 fork 去重與教材排除,重算誤報;或在〈天花板〉照實寫並配回頭條件。

## Finding 3
severity: major
blocking: 是
判準:天花板承認的限制要說明影響方向,且 REVISIT 的新形狀要能真的改善被量到的誤報來源。
段落:〈天花板〉第 3 條、REVISIT 外部網址那行、loadurl 結果列。
引句:「判讀代理看不到 manifest,外部網址那條的真問題都是」
引句:「REVISIT:2027-05-08 外部網址進 WebView 那條試第二版形狀(同函式有 scheme 或 host 比對就不報),用新語料重量,過升級條件才升」
問題:loadurl 的 20%(8/40)有三個問題:
- TP 的 32 處全部標「未確認 exported」,也就是 TP 只代表形狀對,不代表真漏洞。沒開放給其他 App 的畫面外部 Intent 進不來,真誤報率下限是 20%,實際更高。語料裡 0 個 AndroidManifest,判讀代理本來就看不到。方向在〈天花板〉沒寫。
- 20% 裡 6/8 的 FP 是「測試或範例碼」,多半靠 repo 名含 demo/example 判(VpnDemo、casdoor-android-example、autra-3ds-webview-example、ReachFive demo 等)。若不計這類,誤報是 2/34≈5.9%,反而低於 10%。所以這條要不要升,取決於「repo 名含 demo 算不算誤報」這個判讀選擇,而 spec 沒討論。消費專案的 repo 名叫 demo 的專案照樣是正式產品。
- 同規則在第二批樣本外是 1/14=7.1%,這次 20%,差三倍沒有解釋。第二批計劃寫的是「形狀不動」,所以差異只可能來自準則(第三批才補範例碼客觀特徵)或抽樣。
REVISIT 第二版形狀(scheme/host 比對)不會改善上面任何一個來源,會繼續量出同一個 ≈20%,所以這條回頭條件不會有結果。
佐證:``file: `governance/review-reports/android不接閘資安規則重量/experiment/judge-loadurl.md:5` ``(判讀逐列)。
建議:REVISIT 加「抓 manifest 判 exported」這個前提,並把範例碼判法對結論的影響寫進天花板。

## Finding 4
severity: minor
blocking: 否
判準:報出的命中數要能對回卷證檔;[S2] 把數字釘死就不該有灌水。
段落:〈實驗〉表 TLS 列、預期值表 S2。
引句:「| kt-insecure-tls-version | 608 | 428(240) | 抽 40 | 11(27.5%) | 不接閘 |」
問題:`hits-kt-insecure-tls-version.json` 428 筆裡有 67 筆是完全相同的(檔+行重複),去重後 361 處;`hits-kt-provider-openfile-traversal.json` 21 筆有 1 筆重複(DaviBaechtold 的 StickerContentProvider.kt:83 出現兩次,判讀表也判了兩次),實為 20 處,TP 12 含一筆重複,FP 8 不變,實際誤報 9/20=45%,不是 43%。[S2] 的預期值「428」就是灌水後的數字,逐列對照會「一致」但數字本身錯。另外 `judge-tls.md` 把 FDPClient 的檔名寫成 `HttpUtil.kt`,原檔是 `HttpUtils.kt`,判讀代理轉錄有偏差。
佐證:``file: `governance/review-reports/android不接閘資安規則重量/experiment/hits-kt-insecure-tls-version.json:1` ``、``file: `governance/review-reports/android不接閘資安規則重量/experiment/judge-tls.md:8` ``。
建議:命中數去重後再填表,同步改 S2 預期值。

## Finding 5
severity: major
blocking: 是
判準:專案鐵則 4「承認風險要附回頭看的條件」。
段落:〈天花板〉全部 4 條,對照 REVISIT 兩行。
引句:「每條只量了一份樣本外,誤報率是 40 處以內的點估計。」
引句:「誤報只量了命中裡的比例,漏報沒量。」
問題:天花板 4 條都是承認缺口,只有 loadurl 和 TLS 兩條配了 REVISIT,而且 Finding 3 說明 loadurl 那條回頭看不到問題。其他承認沒有回頭條件:
- 點估計/只有一份樣本外:沒有區間,也沒有「到什麼時候或什麼條件要補第二份」。
- 資料庫不獨立:沒有回頭條件。
- 漏報沒量:沒有回頭條件。
- 另外 secretkeyspec(14 處/6 repo)與 weak-cipher(8 處/4 repo)「命中仍不到 20」其實取決於每條只有 2 組查詢,且 GitHub 程式搜尋有結果上限(約 1000 筆/查詢)與排序偏向,還預設排除 fork。這些語料取得限制 spec 完全沒寫。這兩條也沒有任何回頭條件(只能靠「換語料再說」)。
佐證:``file: `governance/review-reports/android不接閘資安規則重量/experiment/queries.tsv:6` ``(這兩條各 2 組查詢)。
建議:每條承認缺口各配一行 `REVISIT:` 或 `[when-…]` 回頭條件;把語料取得限制寫進天花板。

## Finding 6
severity: minor
blocking: 否
判準:判讀準則要跟前兩批一致,且對「未驗證可達性」要一貫。
段落:〈用詞〉判讀代理、`judge-criteria.md`。
引句:「誤報+判不準」佔判讀數的比例
(這句是下面〈實驗〉表頭說明的片段:「命中=規則在這份語料報的處數,括號是分布在幾個 repo;」)
問題:
- 第二批計劃第 28 行寫「判不準:算誤報比例時留在分母」,即不進分子;這批與 intake 補註把判不準進分子,並回頭改寫第二批的結案句。「沿用」不實,provider 因此是 43% 而不是 8/21=38%(cmd 80% vs 75%)。方向偏向「不升」,安全,但定義被事後改了。
- 準則對「看不到的東西」不一致:loadurl 看不到 manifest 判 TP;cmd 的 NetUtils/NetWorkUtils「未確認呼叫端」判 TP;但 provider 的 AAT「helper 不在語料」判 UNSURE。
- 我回原檔核對的 20 多處(TLS 的 Megumin、Podcini、zry98、TvSocket、TBox、QRShield、my-tv-webview、truyenplus;loadurl 的 ORLib、ts-browser、cybergah、sealdice、twinte、Consistancy;provider 的 AAT、uTag、aurora;cmd 的 propagate、Zmmoly、spectra)大致照準則判。邊界例子:Podcini 的 TLS 退回只在 TLS 1.3 不可用時,判 TP 合準則;TBox 的 TLS 1.0 是使用者勾選才開,判「外部協定強制」稍寬。
佐證:``file: `docs/lumos-toolchain-knowledge/Projects/Android資安靜態檢查補齊第二批_計劃.md:28` ``。
建議:在〈用詞〉明寫口徑差異,並說明為何改。

## 其他節
- 〈範圍〉、〈用詞〉、〈依據來源〉、〈驗收條款〉、〈回退〉:已讀,無 finding。
- 查詢設計(實驗鏡頭①):查詢字都是規則的來源詞(例 `TlsVersion.TLS_1_0`、`loadUrl intent.data`),不帶防護寫法的字,沒有偏向 FP 或 TP 一邊;但 GitHub 程式搜尋的結果上限與排序偏向沒寫,見 Finding 5。
- 「抽 40 處」和「全判」的差異(實驗鏡頭③):結論方向不變,但命中少時獨立單位更少,見 Finding 1。

## 實務隱患逐類
- 金流:無,spec 不碰付款,只改型錄文字與圖譜筆記。
- 對外送出:無,語料下載只在實驗階段,卷證只含 repo 名與程式片段,不含祕密。
- 不可逆:無,全是 repo 內文字檔,退回提交即還原。
- 守衛面:無,規則與擋的範圍都不動;唯一的間接影響是回頭改寫第二批的 RETIRE-IF/REVISIT 句子,文字在 repo 內可回退。
- 併發寫入:無,工具鏈單人、AI 依序操作。

最高等級 major;blocking 3 條
