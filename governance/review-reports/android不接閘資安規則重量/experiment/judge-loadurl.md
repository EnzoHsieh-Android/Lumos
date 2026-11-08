規則 kt-loadurl-external,共 40 處:TP 32、FP 8、UNSURE 0。我沒有建立或修改任何檔案。除了讀取準則、前後文檔,還用唯讀指令查了幾支原檔。

所有 TP 都沒有 manifest 可看,所以都是「未確認 exported」。

```
ruleId	檔	行	判定	理由
kt-loadurl-external	casdoor__casdoor-android-example/app/src/main/java/com/example/casdoor_android_example/WebViewActivity.kt	72	FP	FP型:測試或範例碼;repo 名 casdoor-android-example 含 example(寫法本身是 Intent EXTRA_URL 未驗就 loadUrl)
kt-loadurl-external	lbccccc__dirror-music/app/src/main/java/com/dirror/music/ui/activity/WebActivity.kt	103	TP	extra_webUrlStr 取自 Intent,未驗 scheme/host 就 loadUrl;未確認 exported
kt-loadurl-external	ptu1710__UiOt-Server/openremote/console/android/ORLib/src/main/java/io/openremote/orlib/ui/OrMainActivity.kt	155	TP	appUrl 取自 Intent,第一支分支直接 loadUrl,另一支只檢查 startsWith("http") 不查 host;未確認 exported
kt-loadurl-external	binay-kc__recipe-app/app/src/main/java/com/binay/recipeapp/uis/view/WebViewActivity.kt	33	TP	Intent url 未驗直接 loadUrl,且開 JS 與 mixed content;未確認 exported
kt-loadurl-external	bjzhou__ts-browser/app/src/main/java/com/hinnka/tsbrowser/ui/home/MainActivity.kt	169	TP	搜尋 Intent 的 QUERY 只經 toUrl() 轉換就 loadUrl,沒有 scheme/host 白名單(瀏覽器 App 但準則無例外);未確認 exported
kt-loadurl-external	Terran-Marine__ARCoreMeasuredDistance/app/src/main/java/com/gj/arcoredraw/WebActivity.kt	15	TP	Intent url 未驗直接 loadUrl 並開 JS;未確認 exported
kt-loadurl-external	beknumonov__webviewapp_android/app/src/main/java/com/beknumonov/webviewapp/MainActivity.kt	457	TP	Intent url 有值即直接 loadUrl,只有沒值才用預設,無驗證;未確認 exported
kt-loadurl-external	Vulnetix__cli/internal/sast/testdata/efficacy/vnx-android-002/ind-tp-kotlin-deeplink-query/app/src/main/java/io/quayside/tickets/promo/PromoActivity.kt	25	FP	FP型:測試或範例碼;路徑含 testdata(掃描器效能測試語料)
kt-loadurl-external	alisonthemonster__FiveThingsKotlin/app/src/main/java/alison/fivethingskotlin/WebViewActivity.kt	18	TP	Intent WEBVIEW_URL 未驗直接 loadUrl;未確認 exported
kt-loadurl-external	Vadym-Sokol-Vi__InsecureShop/app/src/main/java/com/insecureshop/WebView2Activity.kt	38	TP	dataString、query 參數 url、extras url 皆未驗直接 loadUrl;repo 名與路徑無範例關鍵字,照正式碼判;未確認 exported
kt-loadurl-external	alexsch01__YTWebView/app/src/main/java/com/alexsch01/youtube/MainActivity.kt	225	TP	onNewIntent 的 dataString 未驗直接 loadUrl;未確認 exported
kt-loadurl-external	heyTycoon14__expo-openvpn/vpnLib/src/ui/java/de/blinkt/openvpn/activities/InternalWebView.kt	45	TP	intent.data 未驗直接 loadUrl,並開 JS;未確認 exported
kt-loadurl-external	hwido__androidStudio_Kotlin/mango_contents/app/src/main/java/com/hwido/mango_contents/ViewActivity.kt	22	TP	Intent url 未驗直接 loadUrl;repo 名與路徑無範例關鍵字;未確認 exported
kt-loadurl-external	gnoemes__Shikimori-App-Remastered/app/src/main/java/com/gnoemes/shikimori/presentation/view/player/web/WebPlayerActivity.kt	87	TP	Intent ARGUMENT_URL 只判空,沒驗 scheme/host,並開 allowUniversalAccessFromFileURLs;未確認 exported
kt-loadurl-external	donglua__WhiteLabMouse/app/src/main/kotlin/org/droiders/github/ui/activity/LoginActivity.kt	25	TP	intent.data 未驗直接 loadUrl;未確認 exported
kt-loadurl-external	oneBit-pixel__VpnDemo/openvpn/src/ui/java/de/blinkt/openvpn/activities/InternalWebView.kt	45	FP	FP型:測試或範例碼;repo 名 VpnDemo 含 demo
kt-loadurl-external	autratech__autra-3ds-webview-example/android/ThreeDsWebViewActivity.kt	34	FP	FP型:測試或範例碼;repo 名含 example(寫法本身是 Intent EXTRA_URL 未驗就 loadUrl)
kt-loadurl-external	Srenezaa312__Fit-Feast/WebViewActivity.kt	24	TP	Intent EXTRA_URL 未驗直接 loadUrl;未確認 exported
kt-loadurl-external	Kuater23__psiconnect_mobile/app/src/main/java/com/works/muhtas2/NewsDetailActivity.kt	18	TP	Intent href 未驗直接 loadUrl;未確認 exported
kt-loadurl-external	Cat-Gawr__News-app/APP/main/RE.kt	79	TP	Intent NEWS_URL 只判非 null 就 loadUrl,並開 JS 與 mixed content;repo 名 News-app 非範例;未確認 exported
kt-loadurl-external	coder4world__Android-ChessAI-Assistant/app/src/main/java/com/zfdang/chess/views/WebviewActivity.kt	49	TP	Intent url 未驗直接 loadUrl,並開 JS;未確認 exported
kt-loadurl-external	taoweiji__MixPush/example/src/main/java/com/mixpush/example/WebViewActivity.kt	16	FP	FP型:測試或範例碼;路徑含 example/ 模組
kt-loadurl-external	F-e-n-y-x__nebula/app/src/main/java/com/limelight/HelpActivity.kt	69	TP	intent.data 未驗直接 loadUrl;未確認 exported
kt-loadurl-external	sahuadarsh0__GuruMantra/app/src/main/java/technited/minds/gurumantra/ui/WebPage.kt	31	TP	Intent url 未驗直接 loadUrl,並開 JS;未確認 exported
kt-loadurl-external	hyungwoo-jo__sms-forwarder-kr/app/src/main/kotlin/cn/ppps/forwarder/core/webview/AgentWebActivity.kt	35	TP	intent.data 路由失敗(onLost)時呼叫自家 loadUrl,把網址交給 AgentWebFragment 載入,過程無 scheme/host 驗證;未確認 exported
kt-loadurl-external	qdeconinck__InsecureShop/app/src/main/java/com/insecureshop/WebView2Activity.kt	40	TP	dataString、query url、extras url 皆未驗直接 loadUrl;repo 名與路徑無範例關鍵字;未確認 exported
kt-loadurl-external	sealdice__sealdice-android/app/src/main/java/com/sealdice/dice/WebviewActivity.kt	162	TP	url 取自 Intent(133 行 getStringExtra("url")),只判非 null 就 loadUrl;未確認 exported
kt-loadurl-external	zerodevid__Kas-Remaja-MVVM/app/src/main/java/com/zerodev/kasremaja/ui/webview/WebviewActivity.kt	60	TP	Intent url 未驗直接 loadUrl;未確認 exported
kt-loadurl-external	twin-te__twinte-android/app/src/main/java/net/twinte/android/MainActivity.kt	112	FP	FP型:可信來源;載入的網址由 App 伺服器設定的固定基底加課程 ID 路徑組成,Intent 只提供路徑片段,不是整條網址
kt-loadurl-external	dhruvpadhiyar18__Consistancy-App/app/src/main/java/com/consistancy/app/WebViewActivity.kt	70	TP	Intent "URL" 只判空白就 loadUrl,無 scheme/host 驗證;未確認 exported
kt-loadurl-external	BedrettinOrtak__cybergah-android/app/src/main/java/com/cybergah/app/MainActivity.kt	88	TP	深層連結 intent.data 直接 loadUrl,沒有 host 白名單(grep 未見驗證);未確認 exported
kt-loadurl-external	substrate-asia__hackathon-2022-winter/teams/27-BlockTaker/src/app/app/src/main/java/com/polkadot/bt/ui/create/PrivacyActivity.kt	39	TP	intent.data 未驗直接 loadUrl;hackathon 不在範例關鍵字內,照正式碼判;未確認 exported
kt-loadurl-external	akinemreyazici__MedMobile/app/src/main/java/com/works/muhtas2/NewsDetailActivity.kt	18	TP	Intent href 未驗直接 loadUrl;未確認 exported
kt-loadurl-external	ReachFive__identity-android-sdk-demo/src/main/java/co/reachfive/identity/sdk/demo/WebviewActivity.kt	30	FP	FP型:測試或範例碼;repo 名含 demo
kt-loadurl-external	kkzaki3973__lcg/app/src/main/java/top/easelink/lcg/ui/webview/view/WebViewActivity.kt	72	TP	onNewIntent 的 ACTION_VIEW intent.data 未驗直接 loadUrl;未確認 exported
kt-loadurl-external	prit2803__POKEMON-MDP/app/src/main/java/com/example/proyek_mdp/UI/Payment/PaymentWebViewActivity.kt	96	TP	redirect_url 取自 Intent(60 行),無驗證即 loadUrl;未確認 exported
kt-loadurl-external	AliAkhgar__react-native-openvpn/android/src/main/java/de/blinkt/openvpn/activities/InternalWebView.kt	47	TP	intent.data 未驗直接 loadUrl,並開 JS;未確認 exported
kt-loadurl-external	Nexters__draw-mobile/Draw-AOS/app/src/main/java/org/nexters/draw/MainActivity.kt	50	TP	深層連結 dataString 與 Intent url extra 皆未驗直接 loadUrl;未確認 exported
kt-loadurl-external	qlcchain__QWallet-Android/app/src/main/java/com/stratagile/qlink/ui/activity/defi/DappBrowserActivity.kt	155	TP	Intent url 未驗直接 loadUrl 到錢包 dapp 瀏覽器;未確認 exported
kt-loadurl-external	BlissRoms__platform_packages_apps_Jelly/app/src/main/java/org/lineageos/jelly/MainActivity.kt	183	FP	FP型:可信來源;網址來自 App 內部「URL 解析完成」廣播,API 33 以上以 RECEIVER_NOT_EXPORTED 註冊,且先比對 resolvedIntent 的 package 等於自己(API 33 以下註冊未帶旗標,風險略高)
總計		TP 32 / FP 8 / UNSURE 0;FP 各型:測試或範例碼 6、可信來源 2
```

我只用 Bash 唯讀查了 grep 和 sed 這類指令,沒有改動任何檔案。
