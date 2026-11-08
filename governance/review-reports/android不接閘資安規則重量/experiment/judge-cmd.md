```
ruleId	檔	行	判定	理由
kt-command-exec-nonliteral	iill392__youlong-security/embedded/server/src/main/kotlin/roro/stellar/server/userservice/UserServiceManager.kt	125	TP	sh -c 的指令由 generateStartCommand 組成,混入 record.className、packageName 等,這些來自呼叫的客戶端 App,沒跳脫。伺服器又以高權限執行。
kt-command-exec-nonliteral	JedyYing__SG560D_AI_CPE_20260731/SG560D_AI_Assistant_收尾归档_20260717_153422/01_智能音箱_连续对话_本地TTS_PicoClaw/本机文件/SG560DVoiceAssistant/Pipi_Local_TTS_Companion_V2_2_LocalIntent/app/src/main/java/com/k2fsa/sherpa/onnx/PicoClawBridge.kt	109	FP	FP型:已防護;唯一呼叫處把語音內容包過 shellEscape,其餘是常數腳本路徑和子指令。
kt-command-exec-nonliteral	AntonioNoack__RemsEngine/JVM/src/me/anno/jvm/OpenFileExternallyImpl.kt	49	TP	openInBrowser(link) 的 link 直接拼進 sh -c 字串(Linux 只用雙引號包),Windows 和 macOS 則直接拼進 exec 字串,沒跳脫,link 可能來自外部。
kt-command-exec-nonliteral	weige369__codex-android-dev/app/src/main/java/com/codex/android/util/AndroidShellExecutor.kt	124	FP	FP型:執行指令是功能本身;這個類別就是替 AI 開發環境提供各權限等級的 shell 執行器。
kt-command-exec-nonliteral	Eltend__RootOS/management_app/app/src/main/java/com/rootos/managementapp/ui/home/HomeFragment.kt	146	FP	FP型:可信來源;$location 是寫死的 /data/adb/modules。
kt-command-exec-nonliteral	paulpierre__openclaw-android/app/src/main/java/ai/openclaw/enhanced/gateway/ShellCommandRouter.kt	133	FP	FP型:執行指令是功能本身;這是遠端閘道的 shell 指令路由器,執行指令就是它的用途。
kt-command-exec-nonliteral	uglyer__wechat_jump_ai_kotlin/src/App/AdbCaller.kt	23	FP	FP型:可信來源;ADB_PATH 和 SCREENSHOT_LOCATION 是 App 自己的常數,座標是隨機整數。
kt-command-exec-nonliteral	jonnyzzz__kotlin-game-of-life/src/jvmMain/kotlin/game-console.kt	32	FP	FP型:可信來源;$file 是寫死的 build/render.gif。
kt-command-exec-nonliteral	mlm-games__Fluffy/app/src/main/java/app/fluffy/shell/RootAccess.kt	28	UNSURE	這是 su -c 的通用包裝函式,command 來自呼叫端。缺呼叫端的組字資料,看不出有沒有混入外部檔名。
kt-command-exec-nonliteral	oklookat__spectra/app/src/main/java/com/oklookat/spectra/ui/screens/P2PDebugScreen.kt	224	TP	"ping -c 3 $targetIp" 的 targetIp 是使用者輸入,沒驗證。這個字串不經 shell 切詞,風險限於參數注入。
kt-command-exec-nonliteral	cesards__Don-Limpio/function/GradleFunctions.kt	8	FP	FP型:可信來源;gradleCommand 是開發者自己的命令列工具傳入的 gradle 指令,不是外部資料。
kt-command-exec-nonliteral	wyattabuntjer__AYN-Thor-WoW-Launcher/app/src/main/java/app/gamenative/CrashHandler.kt	77	FP	FP型:可信來源;LOG_CAT_COUNT 是常數,pid 是自己程序的 pid。
kt-command-exec-nonliteral	standardgalactic__propagate/app/src/main/java/com/ksl/plugnixconnect/FieldTesting/FieldTests/SingleRadioGatewayTest.kt	121	FP	FP型:測試或範例碼;路徑有 FieldTests 目錄,是現場測試程式,ping 位址來自測試設定變數。
kt-command-exec-nonliteral	1603-SUHAIB__220701169-CS196411-MAD-MINI-PROJECT/app/src/main/java/com/starry/myne/helpers/Utils.kt	120	FP	FP型:可信來源;getprop 的參數是寫死的 ro.miui.* 屬性名。
kt-command-exec-nonliteral	m14r41__scan4secrets/examples/sample-app/src/Main.kt	2	FP	FP型:測試或範例碼;路徑在 examples/sample-app,這是故意寫的漏洞示範。
kt-command-exec-nonliteral	vasmarfas__universal-ambient-light/app/src/main/java/com/vasmarfas/UniversalAmbientLight/common/MStarVssCaptureEncoder.kt	258	FP	FP型:可信來源;command 由 App 自己的二進位檔路徑和 params() 的內部參數組成。
kt-command-exec-nonliteral	Vishal4051M__ZapShare/android/app/src/main/kotlin/app/zapshare/mobile/MainActivity.kt	1058	FP	FP型:可信來源;$x 和 $y 是座標乘上螢幕寬高後轉成的 Int,不可能夾帶指令字元。
kt-command-exec-nonliteral	Undefined-Invalid-Null__UIN-Tool/app/src/main/java/com/UIN/Tool/plugin/SharedSupervisor.kt	156	FP	FP型:可信來源;腳本是常數,$pids 只來自腳本自己 ps 輸出的數字 PID。
kt-command-exec-nonliteral	wix-incubator__codio/codio-intellij/src/main/kotlin/com/wix/codio/Audio.kt	15	TP	audioPath 是外部檔案路徑,直接拼進 exec 字串,沒跳脫也沒白名單。
kt-command-exec-nonliteral	giorgosioak__friddo/app/src/main/java/com/giorgosioak/friddo/service/FridaServerService.kt	464	FP	FP型:可信來源;這是 su -c 包裝函式,指令由 App 內部拼出(Frida server 的路徑和參數)。
kt-command-exec-nonliteral	apkunpacker__CheckBeer/Kotlin_Implementation.kt	257	FP	FP型:可信來源;$path 是系統 pm path 回傳的 APK 路徑。
kt-command-exec-nonliteral	Luokavin__AutoGLM-For-Android/app/src/main/java/com/kevinluo/autoglm/UserService.kt	27	FP	FP型:執行指令是功能本身;這是 Shizuku 使用者服務,專門替 AI 代理執行 shell 指令。
kt-command-exec-nonliteral	Mehboob-alam1__NicVPN-v2.1/app/src/main/java/com/nicadevelop/nicavpn/service/HTTProcessManager.kt	228	FP	FP型:可信來源;$pid 讀自 App 私有目錄 filesDir 裡自己寫的 pid 檔。
kt-command-exec-nonliteral	TiG-Kira__Harmoid/app/src/main/java/com/kira/harmoid/hdc/HdcShellHandler.kt	39	FP	FP型:執行指令是功能本身;這是 HDC shell 常駐程式,替遠端 hdc 客戶端執行 shell 指令。
kt-command-exec-nonliteral	itstartstosnow__AndroidUuidDefense/Bluetooth/android/pandora/server/src/Os.kt	73	TP	request.ipAddress 來自 gRPC 請求,直接拼進 ping 指令,沒驗證。路徑和 repo 名都不是測試或範例。
kt-command-exec-nonliteral	D10NGYANG__NetworkDebugAssistant/dl10netassistant/src/main/java/com/d10ng/net/assistant/NetUtils.kt	50	TP	公開函式 pingOnce(address) 把位址直接拼進 exec 字串,沒驗證。未確認呼叫端是否已限制。
kt-command-exec-nonliteral	goroya__react-native-iperf/packages/Iperf/android/src/main/java/com/reactlibrary/Iperf.kt	44	FP	FP型:可信來源;iperfPath 是寫死的常數路徑。
kt-command-exec-nonliteral	SA-San49__anikku_modified_version/app/src/main/java/eu/kanade/tachiyomi/util/CrashLogUtil.kt	30	FP	FP型:可信來源;file.absolutePath 是 App 快取目錄下自己建的固定檔名。
kt-command-exec-nonliteral	hrishabth8__e-reader/app/src/main/java/com/starry/myne/helpers/Utils.kt	120	FP	FP型:可信來源;getprop 的參數是寫死的 ro.miui.* 屬性名。
kt-command-exec-nonliteral	leboncoin__spark-android/scripts/svg2avd/svg2avd.main.kts	113	FP	FP型:可信來源;這是開發者本機的建置腳本,程式名是 svgo 字面值,引數是本機路徑和精度數字。
kt-command-exec-nonliteral	SA-San49__anikku1/app/src/main/java/eu/kanade/tachiyomi/util/CrashLogUtil.kt	30	FP	FP型:可信來源;file.absolutePath 是 App 快取目錄下自己建的固定檔名。
kt-command-exec-nonliteral	cdcsgit__lognote/src/com/blogspot/cdcsutils/lognote/Utils.kt	125	FP	FP型:可信來源;$pid 取自本 JVM 自己的 RuntimeMXBean。
kt-command-exec-nonliteral	bitspittle__paintkit/client/src/main/kotlin/bitspittle/paintkit/client/PaintKitClient.kt	35	FP	FP型:可信來源;javaHome 是 java.home 系統屬性,jar 是程式自己建的暫存檔,adminId 是 UUID。
kt-command-exec-nonliteral	c786909486__BaseMvvmModel/library_base_compose/src/main/java/com/ckz/library_base_compose/utils/NetWorkUtils.kt	43	TP	公開函式 getNetDelayAndLost(host, pingNumber) 把 host 直接拼進 exec 字串,沒驗證。庫內找不到呼叫端,未確認是否已限制。
kt-command-exec-nonliteral	Redstonecrafter0__RedstoneLauncher/src/jvmMain/kotlin/net/redstonecraft/redstonelauncher/accounts/GitHubAccount.kt	88	FP	FP型:可信來源;可執行檔路徑來自 App 資源目錄,state 是 App 自己產生的隨機 Base64Url 字串。
kt-command-exec-nonliteral	skysoul19850730__TFHelper/src/main/kotlin/utils/ADBUtil.kt	28	FP	FP型:可信來源;這一處是 tap,座標是 MPoint 的整數欄位。
kt-command-exec-nonliteral	OmYarewar110__Dabe/app/src/main/java/com/example/dabe/ShellTool.kt	25	FP	FP型:執行指令是功能本身;ShellTool 就是替 App 內模擬的 VM 環境執行使用者或代理下的 shell 指令。
kt-command-exec-nonliteral	Zmmoly__Zmmoly25/app/src/main/java/com/zamouli/aiassistant/WebProcessorBridge.kt	239	TP	$url 直接嵌進 python -c 的原始碼字串,沒跳脫。網址若帶引號,可以注入 Python 程式碼。
kt-command-exec-nonliteral	rodion-gudz__Android-Tool/src/main/kotlin/commands.kt	5	UNSURE	exec(app, command) 把 command 拼在 SDK 路徑後面。缺呼叫端資料,看不出 command 是否含使用者輸入的值。
kt-command-exec-nonliteral	rajumark__tidefish/src/main/kotlin/screens/inspector/ADBInspect.kt	233	FP	FP型:可信來源;$id 是 adb devices 列出的裝置序號,ADBConst.path 是 App 設定的 adb 路徑。
總計	40 處	TP 8	FP 30	UNSURE 2	FP 型:可信來源 22、執行指令是功能本身 5、測試或範例碼 2、已防護 1
```

我沒有建任何檔案或目錄。
有兩處判 TP 的理由寫了「未確認呼叫端」(NetUtils.kt 和 NetWorkUtils.kt),這兩處照準則仍判 TP。
