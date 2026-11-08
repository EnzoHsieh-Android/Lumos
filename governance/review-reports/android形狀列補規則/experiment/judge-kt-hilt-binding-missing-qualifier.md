# 判讀結果 kt-hilt-binding-missing-qualifier(樣本外 40 處)

| 序號 | 路徑:行 | 判定 TP/FP/UNSURE | 誤報類(FP 才填,用準則裡的類名) | 一句理由 |
|---|---|---|---|---|
| 1 | rachitmishra__learning-kotlin/src/main/kotlin/di/ComputerModule.kt:19 | TP | | providesGraphicRam 回傳 VideoRam 無限定詞;providesLargeGraphicRam 帶 @Named("large"),同型別 |
| 2 | mlio-n__BISTAI/.../data/di/NetworkModule.kt:36 | TP | | provideOkHttpClient 無限定詞;provideYfOkHttpClient 帶 @YfHttpClient,同為 okhttp3.OkHttpClient |
| 3 | stripe__stripe-android/.../RetryDelayModule.kt:14 | TP | | bindsDefaultRetryDelaySupplier 無限定詞;bindsLinearRetryDelaySupplier @Named(LINEAR_DELAY)、bindsExponentialBackoffRetryDelaySupplier @Named(EXPONENTIAL_BACKOFF_DELAY),同為 RetryDelaySupplier |
| 4 | MKudryash__ByteBattlesMobileApp/.../di/AppModule.kt:343 | TP | | provideAuthApiService 無限定詞;provideRefreshAuthApiService @Named("refreshAuthApiService"),同為 AuthApiService |
| 5 | akkicodes-dev__NoteFlow/.../di/DataModule.kt:45 | TP | | provideCoroutineScope 無限定詞;providesWidgetCoroutineScope 帶同檔 @WidgetCoroutineScope,同為 CoroutineScope |
| 6 | TICESoftware__tice-android/.../ConfigModule.kt:88 | TP | | provideSharedPreferences 無限定詞;provideSettingsPrefs @Named(SETTINGS_PREFS),同為 SharedPreferences |
| 7 | AlexMamo__FireApp/.../di/AppModule.kt:64 | TP | | provideSignInIntent 無限定詞;provideSplashIntent @Named(SPLASH_INTENT) 等三個,同為 Intent |
| 8 | IslombekTurakulov__MyBudget-android/.../NetworkModule.kt:68 | TP | | provideBaseOkHttpClient 無限定詞;provideAuthenticatedOkHttpClient @Named("AuthenticatedOkHttp"),同為 OkHttpClient |
| 9 | Lisir2002__MiniMe-core/.../AgentModule.kt:182 | TP | | provideDefaultOkHttpClient 無限定詞;provideDirectOkHttpClient @Named("direct")、provideProxyOkHttpClient @Named("proxy") |
| 10 | Ductam7415vn__SumUp/.../NetworkModule.kt:209 | TP | | provideGeminiApiService 無限定詞;provideRealGeminiApiService @Named("real"),同一個 import 的 GeminiApiService |
| 11 | efguydan__Spotify-Stats/.../ApiModule.kt:55 | TP | | provideRetrofit 無限定詞;provideAuthRetrofit @Named("Auth_Retrofit"),同為 Retrofit |
| 12 | dnd-side-project__dnd-15th-2-android/.../NetworkModule.kt:50 | TP | | providesHttpClient 無限定詞;providesRawHttpClient @RawHttpClient,同為 io.ktor.client.HttpClient |
| 13 | LumeraD3v__Lumera/.../NetworkModule.kt:46 | TP | | provideRetrofit 無限定詞;provideTmdbRetrofit @TmdbRetrofit 等三個帶限定詞,同為 Retrofit |
| 14 | BitsApk__BitsGroceryApp/.../NetworkModule.kt:33 | TP | | provideRetrofit 無限定詞;provideAuthRetrofit @Named("auth"),同為 Retrofit |
| 15 | eagskunst__GamingNews/.../NetworkModule.kt:30 | TP | | provideOkHttpClient 無限定詞;provideIgdbOkHttpClient @Named("igdbHttpClient"),同為 OkHttpClient |
| 16 | Konkuk-KUIT__Archiveat-Android/.../NetworkModule.kt:50 | TP | | provideOkHttpClient 無限定詞;provideNoAuthOkHttpClient @Named("NoAuthOkHttpClient"),同為 OkHttpClient |
| 17 | gaborauth__toolsboox-android/.../NetworkModule.kt:45 | TP | | provideOkHttpClient 無限定詞;provideOkHttpClientWithAccessToken @Named("accessToken"),同為 OkHttpClient |
| 18 | re-kast__android-mtn-momo-api-sdk/.../NetworkModule.kt:201 | TP | | getAuthentication 無限定詞;provideTokenRefreshAuthenticationService @Named("tokenRefresh"),同一個 import 的 AuthenticationService |
| 19 | dduongCongSon__metroApp/.../NetworkModule.kt:102 | TP | | provideRetrofit 無限定詞;provideStationRetrofit @Named("stationRetrofit")、provideMockyRetrofit @Named("busRetrofit"),同為 Retrofit |
| 20 | arthsar7__MangoFzcoTest/.../DataModule.kt:93 | TP | | provideOkHttpClient 無限定詞;provideOkHttpClientWithoutAuthenticator @Named(CLIENT_WITHOUT_AUTHENTICATOR) |
| 21 | AnARCHIS12__homelab/.../NetworkModule.kt:34 | TP | | provideOkHttpClient 無限定詞;provideInsecureOkHttpClient @Named("insecure"),同為 OkHttpClient |
| 22 | chosuhyeon0812__Foorrng/.../foorrng_owner/.../NetworkModule.kt:43 | TP | | providesRetrofitClient 無限定詞;providesAuthRetrofitClient @AuthRetrofit,同為 Retrofit |
| 23 | hosshan__kodic/.../ReleaseDataModule.kt:42 | TP | | provideOkHttpClient 無限定詞;provideApiClient @Named("Api"),同檔同一個 com.squareup.okhttp.OkHttpClient |
| 24 | sahha-ai__sahha-android/.../di/AppModule.kt:576 | TP | | provideMutex 無限定詞;provideBatchMutex @Named("BatchMutex"),同為 kotlinx Mutex |
| 25 | karasuma-2401__FoodDeliveryMobileAppFE/.../NetworkModule.kt:104 | TP | | provideOkHttpClient 無限定詞;providePublicOkHttpClient @Named("PublicOkHttpClient") |
| 26 | Juan-Felipe-Rubiano__Bochica/.../NetworkModule.kt:20 | TP | | provideOkHttpClient 無限定詞;provideSseOkHttpClient @Named("Sse") |
| 27 | gustavosilveiragss__sora/.../NetworkModule.kt:92 | TP | | provideRetrofit 無限定詞;provideRefreshRetrofit @Named("refresh") |
| 28 | mosuaelvismanje-lab__bloodonal/.../ChatModule.kt:47 | TP | | provideDefaultRemote 無限定詞;provideFirestoreRemote @Named("firestoreRemote")、provideApiRemote @Named("apiRemote"),同為 ChatRemoteDataSource;非 @IntoSet/@IntoMap |
| 29 | Christorious__ghana-voice-ledger/.../EntityModule.kt:34 | TP | | provideEntityExtractor 無限定詞;providePrimaryEntityExtractor @PrimaryEntityExtractor、provideGhanaSpecificExtractor @GhanaSpecificExtractor,同檔同為 EntityExtractor(同一個 ml.entity.* 套件) |
| 30 | rentit-team__rentit-android/.../NetworkModule.kt:39 | TP | | provideOkHttpClient 無限定詞;providePhotoUploadOkHttpClient @UploadOkHttpClient、provideRefreshTokenOkHttpClient @RefreshTokenOkHttpClient |
| 31 | chebrolukp__RealTimeWatchlist/.../di/AppModule.kt:117 | TP | | provideOkHttpClient 無限定詞;provideWebSocketOkHttpClient @Named("finnhubWebSocket") |
| 32 | Nexters__BuyOrNot-Android/.../NetworkModule.kt:89 | TP | | provideAuthApiService 無限定詞;provideReissueAuthApiService @Named("Reissue"),同為 AuthApiService |
| 33 | Quiaa__WeatherMapApp/.../di/AppModule.kt:57 | TP | | provideRetrofit 無限定詞;provideOllamaRetrofit @Named("Ollama") |
| 34 | JangMinSeong__Diet101/.../NetworkModule.kt:52 | TP | | provideRetrofit 無限定詞;provideAuthRetrofit @Named("auth") |
| 35 | printf2475__CoffeeNote/.../RepositoryModule.kt:19 | TP | | bindsCoffeeNoteRepository 無限定詞;bindsTestCoffeeNoteRepository @Named("test_coffee_note_repository"),同為 CoffeeNoteRepository |
| 36 | ihoseinam__MyDigiKala/.../NetWorkModule.kt:49 | TP | | provideRetrofit 無限定詞;providePurchaseRetrofit @Named("purchaseUrl") |
| 37 | savo-o__resona/.../NetworkModule.kt:77 | TP | | provideOkHttp 無限定詞;providePlainOkHttp @PlainHttpClient,同為 OkHttpClient |
| 38 | Kgnot__App-cotizacion-leaderled/.../RepositoryModule.kt:48 | TP | | bindQuoteRepository 無限定詞;bindLocalQuoteRepository @Named("local"),同為 QuoteRepository(同一個 import) |
| 39 | DDD-Community__Chevit-Android/.../release/.../NetworkModule.kt:74 | TP | | provideRetrofit 無限定詞;providePureRetrofit @Named("Pure") |
| 40 | djemes__forkcast/.../NetworkModule.kt:39 | TP | | provideHttpClient 無限定詞;provideAiHttpClient @Named(AI_HTTP),同為 io.ktor.client.HttpClient |

TP 40、FP 0、UNSURE 0
FP 各類:範例碼 0、型別不同 0、多重綁定 0

判讀依據是 40 個完整檔的綁定函式清單(我用臨時腳本抽出每個 @Provides/@Binds 的回傳型別與限定詞,另對有疑慮的檔核對 import)。40 處路徑都不含 `/sample/`、`/examples/`、`/demo/` 等範例碼目錄,所以沒有範例碼誤報。沒有發現泛型參數不同或同名不同套件的情形,也沒有 @IntoSet/@IntoMap 的多重綁定。

臨時檔留在 /tmp/lumos-seat-work/judge-shape/arch59/(list.txt、s.py),我沒有刪。
