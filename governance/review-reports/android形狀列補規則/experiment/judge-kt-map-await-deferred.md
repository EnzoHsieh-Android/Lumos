# 判讀結果 kt-map-await-deferred(樣本外 40 處)

| 序號 | 路徑:行 | 判定 TP/FP/UNSURE | 誤報類(FP 才填,用準則裡的類名) | 一句理由 |
|---|---|---|---|---|
| 1 | delfador__match-scheduler/.../ParallelSolver.kt:23 | TP | | `seeds.map { async }.map { it.await() }`,逐一等待 Deferred 集合 |
| 2 | KiritoXDone__c001apk/.../TopicContentViewModel.kt:198 | TP | | `selections.map { async }.map { it.await() }` |
| 3 | cliuff__boundo/.../ApkUtil.kt:87 | FP | Flow 的 map | `.asFlow().map { it.await() }`,await 發生在 Flow 的 map 裡,一筆一筆來 |
| 4 | gathindra__jvm-virtual-threads/.../CoroutineWeatherDetails.kt:56 | TP | | `vararg Deferred<T>` 上 `map { it.await() }` |
| 5 | WinNative-Emu__WinNative/.../GOGManager.kt:173 | TP | | `.map { async }…}.map { it.await() }`(完整檔 194 行確認) |
| 6 | Fatalll__GEC-rules-generator/.../Generation.kt:29 | TP | | `(…).map { async }.map { it.await() }` |
| 7 | Dieenj__readingapp/.../NewsFeedFetcher.kt:108 | TP | | `articles.map { async }.map { it.await() }` |
| 8 | Hamaad7865__carfectionist/.../ContactsViewModel.kt:232 | TP | | `photos.map { async }.map { it.await() }` |
| 9 | tesutavt__Life-Hub/.../WidgetData.kt:112 | TP | | `languages.await().map { async }.map { it.await() }` |
| 10 | lulugo19__GermanSkript/.../Duden.kt:148 | TP | | `deferreds = worte.map { async }` 後 `deferreds.map { it.await() }` |
| 11 | yashoncode__YT/.../YouTubeRepository.kt:898 | TP | | `deferreds` 是 `.map { async }`,接著 `deferreds.map { it.await() }` |
| 12 | impin2rex__Laya/.../MainViewModel.kt:2022 | TP | | `addons.map { async }.map { it.await() }` |
| 13 | Auties00__MyBicocca/.../ElearningAssignmentRepositoryImpl.kt:109 | TP | | `assignments.map { async }.map { it.await() }` |
| 14 | Ansu216__Anisu/.../CatalogRepository.kt:40 | TP | | `allSources().map { async }.map { it.await() }` |
| 15 | ChooJeongHo__MovieFinder/.../AttachKoreanRatingToBoxOfficeUseCase.kt:22 | TP | | `movies.map { async }.map { it.await() }` |
| 16 | kawamonn91__ttech-store/.../Briefing.kt:26 | TP | | `places = samples.map { async }`,接著 `places.map { it.await() }` |
| 17 | kevinpbaker__TetrisAI/.../Individual.kt:98 | TP | | 完整檔確認 `calculateBestMove` 是 `MutableList<Deferred<…>>` |
| 18 | kigawa01__fonsole/.../BackupEditor.kt:43 | TP | | `dirs` 是 `uploadDirectory` 回傳的 `List<Deferred<DirectoryModel>>`,`dirs.map { it.await() }` |
| 19 | return256__android-platform-tools-base/.../SharedJdwpSessionTest.kt:1045 | TP | | 前文已有 `def.awaitAll()`,`def` 是 Deferred 集合,之後又 `def.map { it.await() }` |
| 20 | optimusprime123x__SIH2026-Mausam/.../HomeRepositoryImpl.kt:176 | TP | | `jobs` 是 `async {…}` 的 list,`jobs.map { it.await() }` |
| 21 | EspoirX__GlideDsl/.../ImageExt.kt:165 | FP | Flow 的 map | `.map { async }.asFlow().map { it.await() }`,await 在 Flow 的 map 裡 |
| 22 | BijoySingh__Scarlet-Notes/.../MainActivity.kt:336 | TP | | `.map { GlobalScope.async }…}.map { it.await() }` |
| 23 | garthgilmour__kotlin-spring-internal-training-nov-2022/.../Program.kt:19 | TP | | 路徑含 `examples`,屬範例碼;但命中就是 `MutableList<Deferred<String>>.map { it.await() }`。依準則「範例碼只看路徑」,路徑有 `/examples/`,應改判 FP(見下方更正) |
| 24 | netomi__bat/.../Collections.kt:38 | TP | | `mapIndexed { async }.map { it.await() }` |
| 25 | snurre__AdventOfCode2018/.../Day11.kt:50 | TP | | `results` 是 `MutableList<Deferred<…>>`,`results.map { it.await() }` |
| 26 | ggggh123__Personal-Studio/.../EmptyRoomRepository.kt:82 | TP | | `targets.map { async }.map { it.await() }` |
| 27 | fishingpvalues__rustypastechat/.../WhatsAppImportManager.kt:65 | TP | | `chunk.map { async }…}.map { it.await() }` |
| 28 | open-orcha__orcha/.../ApiPlanUsage.kt:36 | TP | | `distinct.map { async }.map { it.await() }` |
| 29 | confluentinc__intellij/.../KafkaDataManager.kt:162 | UNSURE | | `runAsyncSuspend` 是外部匯入的自訂函式,repo 內找不到定義,看不出回傳是不是 Deferred |
| 30 | tintwym__movie_verse_mobile/.../MovieRespository.kt:74 | TP | | `movies.map { async }.map { it.await() }` |
| 31 | techforfriend__Nuvio-enhanced-2/.../CloudStreamRepository.kt:528 | TP | | `activeIds.map { async }.map { it.await() }` |
| 32 | rhmodding__Tickompiler/.../DecompileCommand.kt:97 | TP | | 完整檔確認 `coroutines: MutableList<Deferred<Boolean>>`,`coroutines.map { it.await() }` |
| 33 | lovehutaocute__Minexa/.../PluginManager.kt:375 | TP | | `needFetch.map { async }.map { it.await() }` |
| 34 | tolgaprm__InstagramClone/.../PostShareUseCase.kt:90 | TP | | `deferredUploadedImageUris` 是 `.map { async }`,`.map { it.await() }` |
| 35 | Terkwood__kotlin-kafka-hello/bin/main/Producer.kt:71 | TP | | `map { async { f(it) } }.map { it.await() }` |
| 36 | lordmuffin__jarvis-voice/.../ModelDownloadWorker.kt:176 | TP | | `(0 until N).map { async }.map { it.await() }` |
| 37 | pmeorsd-afk__LibreTubeHE-Kosher/.../YouTubeRepository.kt:524 | TP | | `deferreds` 是 `.map { async }`,`deferreds.map { it.await() }` |
| 38 | RidhaAF__ContactsComposeMultiplatform/.../SqlDelightContactDataSource.kt:27 | TP | | 外層 Flow 的 map 只是容器,內層是 `contactEntities`(List).`map { async }.map { it.await() }` |
| 39 | AleksK1NG__Kotlin-Spring-gRPC-Microservice/.../DataLoaderConfig.kt:30 | TP | | `(0..count).map { async }` 後接 `.map { it.await() }`(完整檔 53 行) |
| 40 | XavierClavel__Cooknco/.../MealPlanViewModel.kt:516 | TP | | `removals` 是 `.map { async }`,`removals.map { it.await() }` |

更正:第 23 處路徑含 `/examples/`,依準則「範例碼只看路徑」應判 FP。上表該列的「TP」作廢,以此為準:

| 序號 | 路徑:行 | 判定 TP/FP/UNSURE | 誤報類(FP 才填,用準則裡的類名) | 一句理由 |
|---|---|---|---|---|
| 23 | garthgilmour__kotlin-spring-internal-training-nov-2022/kotlin/examples/coroutines/.../Program.kt:19 | FP | 範例碼 | 路徑含 `/examples/`;寫法本身是 `List<Deferred>.map { it.await() }` |

TP 36、FP 3、UNSURE 1

FP 各類:Flow 的 map 2(第 3、21 處)、範例碼 1(第 23 處)、接收者非 Deferred 0
