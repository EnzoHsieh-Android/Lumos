```
序號	檔:行	判定	理由
0	easy-library/.../webview/WebViewActivity.kt:57	FP	FP型:不對外開放;manifest 宣告 .features.webview.WebViewActivity,沒有 intent-filter 也沒寫 exported,預設不開放
1	kotlin_study/AndoridConcepts/.../Homework_2.kt:53	TP	intent.data 沒驗就 loadUrl;manifest 的 .Homework_2 寫 android:exported="true" 並帶 MAIN intent-filter,路徑無 test/sample 類目錄
2	droidVNC-NG/.../ui/WebViewActivity.kt:61	FP	FP型:不對外開放;manifest 的 .ui.WebViewActivity 沒 intent-filter、沒寫 exported
3	CuteU/module-public/Pay/.../WebviewPayActivity.kt:153	UNSURE	manifest 抓得到但找不到 WebviewPayActivity 的宣告(可能在別的模組),看不出開不開放
4	KotatsuApp/.../cloudflare/CloudFlareActivity.kt:73	FP	FP型:不對外開放;manifest 宣告該 Activity,沒 intent-filter、沒寫 exported
5	Aite.studio/.../GoogleAuthActivity.kt:118	FP	FP型:不對外開放;manifest 寫 exported="false"
6	AndroidTVBrowser/.../MainActivity.kt:4670	TP	onNewIntent 把 intent.dataString 沒驗就 loadUrl;manifest 的 .MainActivity 寫 exported="true"(MAIN/LAUNCHER 的 intent-filter)
7	SoriGureum/.../WebAuthActivity.kt:32	FP	FP型:不對外開放;manifest 的 WebAuthActivity 沒 intent-filter、沒寫 exported
8	kycarrotsApp/.../webview/WebViewActivity.kt:318	FP	FP型:不對外開放;manifest 寫 exported="false"
9	kw-notice-v1/.../webview/WebViewActivity.kt:27	TP	intent 的 "url" 沒驗就 loadUrl(url!!);manifest 的 .view.notice.webview.WebViewActivity 寫 exported="true" 並帶 intent-filter(action FCM_CLICK_ACTION_ACTIVITY)
10	CityGuideApp/.../ECommerceActivity.kt:57	FP	FP型:不對外開放;manifest 的 ECommerceActivity 沒 intent-filter、沒寫 exported
11	DevProject/.../ShowWebViewActivity.kt:24	FP	FP型:不對外開放;manifest 寫 exported="false"
12	WebGPT/.../MainActivity.kt:149	TP	intent.dataString 沒驗就 loadUrl;manifest 的 .MainActivity 寫 exported="true",VIEW filter 的 host 限制擋不住顯式 Intent
13	masaudit/tests/fixtures/AND-014/clean_not_exported/.../ReCaptchaActivity.kt:6	FP	FP型:測試或範例碼;路徑含 tests/fixtures
14	Kotatsu-Next/.../browser/BrowserActivity.kt:44	FP	FP型:不對外開放;manifest 的 BrowserActivity 沒 intent-filter、沒寫 exported
15	openclaw-termux/.../WebViewActivity.kt:80	FP	FP型:不對外開放;manifest 寫 exported="false"
16	EX_NewsApp/.../WebViewActivity.kt:27	FP	FP型:不對外開放;manifest 寫 exported="false"
17	edfa-pg-android-sdk/sample/.../ExpresspayRedirect3dsActivity.kt:84	FP	FP型:測試或範例碼;路徑含 sample/,且載入的是 javascript: 表單填值而非外部網址
18	arxiv-vanity/.../WebView.kt:17	FP	FP型:不對外開放;manifest 的 .WebView 沒 intent-filter、沒寫 exported
19	MyPagingThree/.../webview/WebViewActivity.kt:38	UNSURE	manifest 抓得到但找不到 WebViewActivity 的宣告,看不出開不開放
20	lab9/.../WebViewActivity.kt:33	FP	FP型:不對外開放;manifest 寫 exported="false"
21	android-samples-guo/.../CustomWebViewActivity.kt:20	FP	FP型:不對外開放;manifest 寫 exported="false"(repo 名帶 samples 不算訊號)
22	CMC_Android/.../WebViewActivity.kt:28	FP	FP型:不對外開放;manifest 的 .WebViewActivity 沒 intent-filter、沒寫 exported
23	Tucao/.../browser/BrowserActivity.kt:36	FP	FP型:不對外開放;manifest 的 BrowserActivity 沒 intent-filter、沒寫 exported
24	chat-and-meet-support-assistant/.../WebviewActivity.kt:64	FP	FP型:可信來源;載入的是 App 自己組的 javascript:updateFromNative(...) 呼叫,不是外部網址;manifest 也寫 exported="false"
25	X4CodeVSCODE/.../MainActivity.kt:89	FP	FP型:已防護;toHttp() 只放行 agenthub/agenthubs/http/https,其餘回 null 不載入(host 未驗,但這是讓使用者自設伺服器網址的瀏覽器)
26	Wasla-lite/.../webviewActivity.kt:34	FP	FP型:可信來源;命中行是 shouldOverrideUrlLoading 內頁面導覽的 loadUrl,不是 Intent 網址;manifest 的 webviewActivity 也沒 intent-filter、沒寫 exported
27	Checklist-App/android-webview-legacy/.../MainActivity.kt:122	FP	FP型:已防護;loadUrl 前有 url.startsWith(APP_URL) 前綴檢查
28	fastcampus/part2/chapter5/.../WebViewActivity.kt:26	UNSURE	manifest 抓得到但找不到 WebViewActivity 的宣告(只有 MainActivity、EditActivity、AddActivity),看不出開不開放
29	ArkScreen/.../ui/common/WebViewActivity.kt:86	FP	FP型:不對外開放;manifest 的 .ui.common.WebViewActivity 沒 intent-filter、沒寫 exported;且網址先過 LinkUrl::normalize
30	flutter_moolre/.../MoolreCheckoutActivity.kt:113	FP	FP型:不對外開放;manifest 寫 exported="false"
31	Miyorare/.../cloudflare/CloudFlareActivity.kt:284	FP	FP型:不對外開放;manifest 的 CloudFlareActivity 沒 intent-filter、沒寫 exported;且已 toHttpUrlOrNull 解析驗證
32	blockstack-android/.../MainActivity.kt:38	FP	FP型:可信來源;Intent 網址只當 authRequest 參數,接在固定的 https://browser.blockstack.org/auth?authRequest= 後面,host 固定
33	Amiwatch/.../webview/CookieCatcher.kt:60	TP	intent 的 "url" 沒驗就 loadUrl(url, headers);manifest 的 .others.webview.CookieCatcher 寫 exported="true" 並帶 VIEW intent-filter
34	Ssapp/.../view/DetailActivity.kt:21	FP	FP型:不對外開放;manifest 的 DetailActivity 沒 intent-filter、沒寫 exported
35	novac-android-plugin/.../NovacWebViewActivity.kt:130	FP	FP型:不對外開放;manifest 寫 exported="false"
36	AndroidJetPack/.../BrowserActivity.kt:31	FP	FP型:不對外開放;manifest 的 BrowserActivity 沒 intent-filter、沒寫 exported
37	Health_Realtime_Tracker/.../WebActivity.kt:85	FP	FP型:不對外開放;manifest 的 WebActivity 沒 intent-filter、沒寫 exported
38	HiAndroid/.../ui/common/WebActivity.kt:19	FP	FP型:不對外開放;manifest 的 .ui.common.WebActivity 沒 intent-filter、沒寫 exported
39	ai-agent-workflow-kit/ai/tasks/subagent/fixtures/security-webview/HelpActivity.kt:17	UNSURE	fixtures 不在準則列的目錄名;manifest 只宣告 AdminActivity,找不到 HelpActivity,看不出開不開放
總計	40	TP 5(1、6、9、12、33);FP 31;UNSURE 4(3、19、28、39)	FP 各型:不對外開放 25、已防護 2、可信來源 3(24、26、32)、測試或範例碼 2(13、17)。(不對外開放 25 含 29 與 31,這兩處另有驗證。26 歸可信來源,所以可信來源是 3 不是 2;不對外開放實為 24。25+2+3+2 重算:不對外開放 24、已防護 2、可信來源 3、測試或範例碼 2,共 31)
```

總計列的括號有數字更正:FP 各型以最後這句為準,即不對外開放 24、已防護 2(25、27)、可信來源 3(24、26、32)、測試或範例碼 2(13、17),共 31。

我沒有建立、修改或刪除任何檔案,也沒有動 git。
