ruleId	檔	行	判定	理由
kt-insecure-tls-version	SoahCeruP__TheRepeator/app/src/main/java/com/therepeator/app/TheRepeatorViewModel.kt	406	TP	App 自己的 unsafe 客戶端明列 TLS_1_1、TLS_1_0,沒有版本判斷;基底客戶端也用 COMPATIBLE_TLS
kt-insecure-tls-version	LumoraPlayer__Lumora/app/src/main/java/com/lumora/scraper/utils/NetworkClient.kt	129	TP	無條件允許 TLS1.0/1.1,後面的 SDK_INT 判斷只管憑證,沒包住這行
kt-insecure-tls-version	gj009351__legado-Sigma/app/src/main/java/io/legado/app/help/http/HttpHelper.kt	54	TP	App 自己的連線用 COMPATIBLE_TLS,沒有版本判斷
kt-insecure-tls-version	royaff0__Megumin/common/src/main/java/com/sqrtf/common/api/ApiClient.kt	81	FP	FP型:舊系統相容;包在 SDK_INT in 16..21 內,只在 Android 5.0 以前走這條
kt-insecure-tls-version	AlfaazPlus__SunnahApp/app/src/main/java/com/alfaazplus/sunnah/api/RetrofitInstance.kt	18	TP	正式碼無條件用 COMPATIBLE_TLS
kt-insecure-tls-version	xiahu0911__BookshelfLib/src/main/java/com/flyersoft/source/yuedu3/HttpHelper.kt	18	TP	正式碼無條件用 COMPATIBLE_TLS
kt-insecure-tls-version	SkidderMC__FDPClient/src/main/java/net/ccbluex/liquidbounce/utils/io/HttpUtil.kt	161	TP	applyBypassHttps 對 COMPATIBLE_TLS 開放所有 TLS 版本;註解只提 Java 8 缺現代 TLS,沒有 API 21 版本判斷
kt-insecure-tls-version	GEd520__legados/app/src/main/java/io/legado/app/help/http/HttpHelper.kt	54	TP	App 自己的連線用 COMPATIBLE_TLS,沒有版本判斷
kt-insecure-tls-version	xdotli__harbor-datagen/okhttp-trailers-crash/environment/okhttp/okhttp/src/commonJvmAndroid/kotlin/okhttp3/ConnectionSpec.kt	375	FP	FP型:函式庫原始碼複本;這是 OkHttp 自己的 COMPATIBLE_TLS 定義
kt-insecure-tls-version	TsaiYongChuan__legado/app/src/main/java/io/legado/app/help/http/HttpHelper.kt	22	TP	App 自己的連線用 COMPATIBLE_TLS,沒有版本判斷
kt-insecure-tls-version	GymMickey__legadoM-Ink/app/src/main/java/io/legado/app/help/http/HttpHelper.kt	54	TP	來源連線與 secure 兩組規格都含 COMPATIBLE_TLS,沒有版本判斷
kt-insecure-tls-version	XilinJia__Podcini/app/src/main/kotlin/ac/mdiq/podcini/net/download/service/PodciniHttpClient.kt	214	TP	TLS1.3 不支援時退到 TLSv1.2/1.1/1.0,涵蓋 API 21 以上到 28 的裝置,沒有 API 21 以前的版本判斷
kt-insecure-tls-version	Liloupar__novel-server/src/main/java/org/lightink/reader/service/yuedu/http/HttpHelper.kt	22	TP	正式碼無條件把 COMPATIBLE_TLS 加進規格清單
kt-insecure-tls-version	visualnew__ParafusoTV/app/src/main/java/com/lumora/scraper/utils/NetworkClient.kt	130	TP	無條件允許 TLS1.0/1.1,後面的 SDK_INT 判斷只管憑證
kt-insecure-tls-version	Dev-Infra-Grupo-AMH__app-austa-kemj9m/src/android/app/src/main/kotlin/com/austa/superapp/core/network/ApiClient.kt	140	TP	正式碼無條件用 COMPATIBLE_TLS
kt-insecure-tls-version	szkolny-eu__FSLogin/sample/src/main/kotlin/pl/szczodrzynski/fslogin/Main.kt	23	FP	FP型:測試或範例碼;路徑含 sample 模組
kt-insecure-tls-version	rbarcala__EFrame/app/src/main/kotlin/com/antigravity/eframe/data/HttpClientFactory.kt	24	TP	無條件用 COMPATIBLE_TLS;註解講的是舊憑證問題,不是版本判斷
kt-insecure-tls-version	spacesarmat__omp/android/app/src/main/java/com/spacesarmat/omp/TvSocket.kt	42	TP	連自簽憑證電視時多加 COMPATIBLE_TLS,沒有說明電視強制舊 TLS,也沒有版本判斷
kt-insecure-tls-version	GitHub-workflow-APP__legado/app/src/main/java/io/legado/app/help/http/HttpHelper.kt	55	TP	App 自己的連線用 COMPATIBLE_TLS,沒有版本判斷
kt-insecure-tls-version	hectorqin__reader-legado/src/main/java/io/legado/app/help/http/HttpHelper.kt	30	TP	App 自己的連線用 COMPATIBLE_TLS,沒有版本判斷
kt-insecure-tls-version	phanan04__truyenplus/source-api/src/androidMain/kotlin/ireader/core/http/SSLConfiguration.kt	50	FP	FP型:已防護;這行只是版本對照,預設 minTlsVersion 為 TLS_1_2,呼叫端明確設定降級才會用 1.1
kt-insecure-tls-version	1aishwaryasharma__tarang-public/modules/fire-tv-transport/android/src/main/java/expo/modules/firetvtransport/FireTvTransportModule.kt	100	FP	FP型:外部協定強制;註解寫明連的電視只接受 TLS1.0/1.1,App 改不了
kt-insecure-tls-version	zry98__sms2telegram/app/src/main/java/io/zry/sms2telegram/PushService.kt	162	TP	TLS1.2 規格後面無條件加 COMPATIBLE_TLS,沒有版本判斷
kt-insecure-tls-version	TonyStark5__LegadoMD3/app/src/main/java/io/legado/app/help/http/HttpHelper.kt	75	TP	App 自己的連線用 COMPATIBLE_TLS,沒有版本判斷
kt-insecure-tls-version	hurist__TTSDemo/TTSLibrary/src/main/java/com/qq/wx/offlinevoice/synthesizer/online/token/TokenProvider.kt	53	FP	FP型:測試或範例碼;repo 名 TTSDemo 含 demo
kt-insecure-tls-version	volgunov-ad__TBox/app/src/main/java/vad/dashing/tbox/HttpRequestWidget.kt	194	FP	FP型:外部協定強制;只在使用者勾選 insecureCipher 去連舊設備時才開 TLS1.0/1.1,預設不開
kt-insecure-tls-version	sirbuvladste__QRShield/app/src/main/java/com/vldsir/qrshield/data/network/VirusTotalApi.kt	42	TP	連 VirusTotal 這種現代伺服器卻無條件加 COMPATIBLE_TLS
kt-insecure-tls-version	pouriyadb__Vimeo-Api/app/src/main/java/db/poorya/namavatest/hilt/NetworkModule.kt	54	TP	只用 COMPATIBLE_TLS,沒有版本判斷
kt-insecure-tls-version	BRNSystems__GPS_Game/app/src/main/java/systems/brn/gpsgame1/LoginActivity.kt	22	TP	正式碼無條件加 COMPATIBLE_TLS
kt-insecure-tls-version	zwc456baby__my-tv-webview/app/src/main/java/com/lizongying/mytv0/requests/HttpClient.kt	110	FP	FP型:舊系統相容;包在 SDK_INT &lt; 22 內
kt-insecure-tls-version	yidun__ocr-android-demo/app/src/main/java/com/netease/nis/ocrdemo/utils/HttpUtil.kt	17	FP	FP型:測試或範例碼;repo 名 ocr-android-demo 含 demo
kt-insecure-tls-version	tetrafolium__owncloud-android/owncloudApp/src/main/java/com/owncloud/android/authentication/oauth/OAuthConnectionBuilder.kt	49	FP	FP型:舊系統相容;只有 TLSv1.2 的 SSLContext 取不到(NoSuchAlgorithmException,實際上是 API 16 以前)才退到 TLSv1.1/TLSv1
kt-insecure-tls-version	abundant-ai__SWE-gen-Java/tasks/square__okhttp-8276/tests/okhttp-testing-support/src/main/kotlin/okhttp3/TestValueFactory.kt	66	FP	FP型:測試或範例碼;路徑含 tests,且是 OkHttp 測試支援碼
kt-insecure-tls-version	headuck__GoOutWithDuck/app/src/main/java/com/headuck/app/gooutwithduck/di/NetworkModule.kt	49	TP	以 COMPATIBLE_TLS 為底並明列 TLS1.1/1.0,沒有版本判斷
kt-insecure-tls-version	abdennasserAbidi367__ClockIn/app/src/main/java/com/example/mediconnect/remote/BaseNetworkModuleFactory.kt	36	TP	明列 TLS1.1/1.0,沒有版本判斷;路徑與 repo 名都沒有測試或範例特徵
kt-insecure-tls-version	AngelAvilesDev__LumVida/app/src/main/java/com/example/lumvida/Network/RetrofitClient.kt	86	TP	正式碼無條件用 COMPATIBLE_TLS
kt-insecure-tls-version	test-organization-webhook-test__vaultpay/mobile/app/src/main/java/com/vaultpay/app/network/TlsConfig.kt	238	TP	SSLContext 用 "TLSv1",無版本判斷;repo 名 vaultpay 與路徑沒有測試或範例特徵
kt-insecure-tls-version	Rve27__RvMusic-Player/app/src/main/java/com/rve/musicplayer/di/AppModule.kt	447	TP	正式碼無條件用 COMPATIBLE_TLS
kt-insecure-tls-version	binaryb3ast__playsho/app/src/main/java/com/playsho/android/network/RetrofitClient.kt	27	TP	正式碼無條件用 COMPATIBLE_TLS
kt-insecure-tls-version	sokcuri__TwimgSpeedProxy/app/src/main/java/com/sokcuri/twimgspeedproxy/RyuarinService.kt	47	TP	明列 TLS1.1/1.0,連的是一般 HTTPS 站台,沒有版本判斷
總計	40 處	-	TP 29 / FP 11 / UNSURE 0	FP 各型:舊系統相容 3、函式庫原始碼複本 1、測試或範例碼 4、外部協定強制 2、已防護 1

我只讀檔,沒有修改、新增或刪除任何檔案,也沒建過臨時目錄。
