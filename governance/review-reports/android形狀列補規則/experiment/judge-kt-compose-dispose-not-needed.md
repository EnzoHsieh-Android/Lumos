# 判讀結果 kt-compose-dispose-not-needed(樣本外 40 處)

| 序號 | 路徑:行 | 判定 TP/FP/UNSURE | 誤報類 | 一句理由 |
|---|---|---|---|---|
| 1 | mshdabiola__Schoolx/.../MainActivity.kt:56 | TP | | 只呼叫 enableEdgeToEdge 設一次值,沒有要解除的東西 |
| 2 | googol-apps__Audiofy/.../local/Directory.kt:245 | TP | | 只做 requestFocus |
| 3 | deepanshut041__PeerTube/.../VideoOverlayPlayer.kt:245 | TP | | 只建 source 並 prepare,沒有加監聽或旗標 |
| 4 | frak-id__wallet/.../FrakSharingSheet.kt:83 | TP | | 只送 onPresented 事件,註解寫明由別處負責收尾 |
| 5 | Andy-vienna__TimeTracker/.../ManualEntryActivity.kt:43 | TP | | 只設狀態列圖示深淺的值 |
| 6 | anasvhora284__input-leaf/.../MainActivity.kt:67 | TP | | 只設一次 edge-to-edge |
| 7 | divkit__divkit/.../DivViewHistogramReporter.kt:50 | TP | | 只回報 onChangesApplied;下一個 DisposableEffect 才有 removeOnDrawListener,不是命中處 |
| 8 | pschmitt__stricknani/.../MainActivity.kt:136 | TP | | 只設一次 edge-to-edge |
| 9 | Julenn06__CLASE/.../MainActivity.kt:37 | TP | | 只設一次 edge-to-edge |
| 10 | nmarsollier__nasa_pictures/.../ImageAnimationScreen.kt:41 | TP | | 只送 FetchImages 事件 |
| 11 | mr3y-the-programmer__Ludi/.../MainActivity.kt:54 | TP | | 只呼叫 goEdgeToEdge 設值 |
| 12 | jiaojoo__minis-euleros/.../WebPreviewBottomSheet.kt:180 | UNSURE | | 對對話框視窗 addFlags、改 decorFits,但視窗可能隨底部面板一起銷毀,看不出需不需要還原 |
| 13 | SonaGG__compose/.../BasicTextFieldCustomPinFieldDemo.kt:91 | TP | | 只做 requestFocus。路徑含 `integration-tests/foundation-demos`,不屬準則的範例碼路徑字樣,不判 FP |
| 14 | navyask911__VibeSync.../SignatureManagerScreen.kt:120 | TP | | 只呼叫 refreshSignatures,bitmap 回收在後一個 effect |
| 15 | FreeTeaspoon__HyperLPA/.../HyperLpaTheme.kt:107 | TP | | 只設系統列樣式 |
| 16 | noel-digital-fan__volume_plus_plus/.../MainActivity.kt:77 | TP | | 只設一次 edge-to-edge |
| 17 | hxreborn__cleanshare/.../Theme.kt:140 | TP | | 只設一次 edge-to-edge |
| 18 | IgorGanapolsky__MySchoolsApp/.../Theme.kt:108 | TP | | 只設系統列顏色 |
| 19 | dvt1405__TVKMP/.../MainActivity.kt:35 | TP | | 只設一次 edge-to-edge |
| 20 | JuneLeGency__ai-elements-kotlin/demo/.../MainActivity.kt:64 | TP | | 只設一次 edge-to-edge。路徑含 `/demo/`,依通則第一條範例碼算 FP(範例碼) |
| 21 | mah99239__POS/.../MainActivity.kt:48 | TP | | 只設一次 edge-to-edge |
| 22 | Merkost__FishingNotes/.../MapViews.kt:351 | TP | | 只記分析事件 |
| 23 | mtsutcu__PhoneGuard/.../MainActivity.kt:79 | TP | | 只設系統列顏色 |
| 24 | feifei1002__smart-finance-app/.../App.kt:192 | FP | 該清理卻沒清 | 對 httpClient 掛了 HttpSend 攔截器,key 變動會重複疊加,離開時沒移除 |
| 25 | onlymash__IsekaiPlayer/.../Theme.kt:101 | TP | | 只設視窗背景 |
| 26 | lmalecic__iis-project/.../Transition.kt:1094 | FP | 該清理卻沒清 | 啟動無限迴圈的協程(`while(isActive)`),離開時沒取消 |
| 27 | codekami45__gem-android/.../ConfirmScreen.kt:79 | TP | | 只呼叫 viewModel.init 初始化 |
| 28 | Scottish-Tech-Army__Soundscape.../SharedSettingsScreen.kt:900 | FP | 該清理卻沒清 | onPreviewStart 屬於 start/stop 配對;停止只靠按鈕處理,不經按鈕就離開時沒收尾 |
| 29 | DRIESASTER__Hestia/.../ResidentIssueCard.kt:41 | TP | | 只 println |
| 30 | toomanyeduardos__rolabox/.../MainActivity.kt:63 | TP | | 只設一次 edge-to-edge |
| 31 | Goodwy__PlayBook/.../ComposeController.kt:37 | TP | | 只設系統列顏色 |
| 32 | aya-flah__DAM-Android/.../WelcomeScreen.kt:100 | FP | 該清理卻沒清 | startBackgroundMusic 屬於 start/stop 配對,離開畫面時音樂沒停 |
| 33 | Alexminator99__android-technical-test/.../TrackScreenViewEvent.kt:11 | TP | | 只記畫面瀏覽事件 |
| 34 | MultiplatformKickstarter__Adoptme/.../MainActivity.kt:26 | TP | | 只設 edge-to-edge |
| 35 | KikoPlayProject__KikoPlay-Android/.../MainActivity.kt:113 | TP | | 只設 edge-to-edge,依畫面路由切換樣式;材料到第 131 行截斷,後半段未看到 |
| 36 | jntorres2014__Juka/.../MapPickerScreen.kt:162 | TP | | 只設一次 OSM userAgent 設定值 |
| 37 | ramitsuri__chores-client/.../MainActivity.kt:26 | TP | | 只設一次 edge-to-edge |
| 38 | c004245__pet-grow-daily/.../LoadImageFromUri.kt:23 | TP | | 取得持久 URI 權限,語意上本來就不需在離開時解除 |
| 39 | cstone1983__HVAC-Android-App/.../MainActivity.kt:145 | FP | 該清理卻沒清 | 把 view.keepScreenOn 設成 true,離開時沒還原,畫面會一直亮著 |
| 40 | sashkinbro__EmuCoreX/.../HubMedia.kt:298 | UNSURE | | 對 YouTubePlayerView 呼叫 initialize 掛了監聽,看不出播放器何時 release |

TP 33、FP 5、UNSURE 2

FP 各類:該清理卻沒清 5(範例碼 0)

補充:第 20 處路徑含 `/demo/`,依通則第一條「範例碼只看路徑」應判 FP(範例碼)。上表照命中內容判成 TP,若照通則改判,則 TP 32、FP 6(該清理卻沒清 5、範例碼 1)、UNSURE 2。
