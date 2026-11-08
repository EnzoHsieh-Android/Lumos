序號 1 到 40 依清單順序,檔名只寫到專案名加檔名,完整路徑見清單。判讀依據是各處前後文,另外打開原檔看了 Json.kt、AppConfig.kt、Serializer.kt 的用法。

1	Allertj__GraphQLServer/RedisConfiguration.kt:48	FP	FP型:可信來源;mapper 只給自己的 Redis 快取序列化用,外部碰不到
2	BedreFlyt__bedreflyt-dt-api/CacheConfig.kt:48	FP	FP型:可信來源;mapper 只用在 Redis 快取和 redisTemplate,validator 雖放行 Any 但資料是自己寫的
3	DevCHW__hhplus-concert/CacheManagerConfig.kt:41	FP	FP型:可信來源;mapper 只用在 Redis CacheManager
4	DongGeon0908__goofy-short-url/RedisConfig.kt:72	FP	FP型:可信來源;mapper 只用在 Redis 快取
5	Gamsty__JobApplicationTracker/RedisConfig.kt:61	FP	FP型:可信來源;mapper 只用在 Redis 快取設定
6	Lorwell__great-wall/Json.kt:62	TP	通用 JSON 工具的 typeMapper,用 Laissez-faire validator,對外有 `decodeValue`、`convertTypeValue` 等方法;語料裡找不到呼叫端,看不出來源限制
7	MAKSEMENS__vkr/AppConfig.kt:117	TP	這是全域 `objectMapper` Bean,validator 放行 Any;同檔的 Kafka 消費端也設了 `TRUSTED_PACKAGES="*"`,訊息來自外部佇列
8	MangKyu__spring-2-level-cache/CacheConfiguration.kt:52	FP	FP型:可信來源;mapper 只用在 `redisSerializer` 的 Redis 快取
9	NiklasJohansen__PulseEngine/DataImpl.kt:156	FP	FP型:可信來源;這是遊戲引擎讀寫本機存檔的 BSON mapper
10	NiklasJohansen__PulseEngine/DataImpl.kt:162	FP	FP型:可信來源;同上,本機存檔的 JSON mapper
11	UygarGokcen__forgeflow/CacheConfig.kt:52	FP	FP型:可信來源;mapper 只用在 Redis 快取
12	VladislavKabral__OrderTrack/RedisConfig.kt:19	FP	FP型:可信來源;mapper 只用在這支檔的 `redisTemplate`
13	YAPP-Github__28th-App-Team-2-BE/RedisCacheConfig.kt:75	FP	FP型:已防護;validator 只放行 `com.yapp.todakun.`、`java.util.`、`kotlin.collections.`,且只用在 Redis 快取
14	YoHanKi__stayloop/CacheRedisConfig.kt:61	FP	FP型:可信來源;用 `objectMapper.copy()` 做出專供 Redis 範本的 mapper,不影響全域 mapper
15	cheestree__vetly/RedisConfig.kt:41	FP	FP型:可信來源;Laissez-faire 只套在 `copy()` 出來、專供 Redis 的 mapper
16	ddaakk__hanghae99/RedisRepositoryConfig.kt:42	FP	FP型:可信來源;mapper 只用在 `redisTemplate` 的 Redis 序列化
17	devYSK__mini-lab/request-late-limiter/RedisObjectMapper.kt:36	FP	FP型:可信來源;這是 Redis 專用 mapper(類別名稱即 RedisObjectMapper),也是 mini-lab 範例
18	devYSK__mini-lab/springboot-redis-topology/ObjectMapperConfig.kt:36	FP	FP型:可信來源;Redis 拓撲實驗用的 mapper,屬範例碼
19	fede-debe__Chirp/app/RedisConfig.kt:58	FP	FP型:已防護;validator 限制為 `com.project.chirp.`、`java.util.`、`kotlin.collections.`,且只用在 Redis 快取
20	fede-debe__Chirp/common/RabbitMqConfig.kt:58	FP	FP型:已防護;雖然是訊息佇列,但 validator 只放行 `ChirpEvent` 基底類型和集合,不是 Any
21	goncalogil__my-jukebox/RedisConfiguration.kt:25	FP	FP型:可信來源;Laissez-faire 只套在 `copy()` 出來、專供 reactive Redis 範本的 mapper
22	higoods-hongik__HIGOODS-Backend/RedisCacheConfig.kt:22	FP	FP型:可信來源;mapper 是類別內的 val(非 Bean),只給 Redis CacheManager 用
23	jhs512__slog_2026_03/RedisCacheConfig.kt:29	FP	FP型:可信來源;只用在 Redis CacheManager
24	josebatista__pl_kotlin_bundle/RedisConfig.kt:31	FP	FP型:已防護;validator 限制為 `io.github.josebatista.chirp.` 加 JDK 集合,且只用在 Redis 快取
25	kingston-csj__mmorpg/JpaObjectConverter.kt:26	FP	FP型:可信來源;只做 JPA 欄位與資料庫字串互轉,資料是伺服器自己寫入的
26	line__req-shield/RedisConfiguration.kt:55	FP	FP型:測試或範例碼;這是 req-shield 的 spring-boot3-example 範例模組
27	lucasdengcn__spring-kotlin-kafka-dx-demo/RedisConfig.kt:96	FP	FP型:測試或範例碼;這是 demo 專案,mapper 只用在 `redisTemplate`
28	navikt__modia-common-utils/JsonSnapshotFormat.kt:33	FP	FP型:測試或範例碼;位於 test-utils 的快照格式工具,用 `DefaultBaseTypeLimitingValidator`
29	orbit__orbit/Serializer.kt:20	UNSURE	validator 放行 Any 加 EVERYTHING,正式碼的 internal Serializer。語料裡找不到它的呼叫端,判不出解析的是叢集內部訊息還是外部輸入
30	pagidas__ports-and-adapters-demo/CardWalletWebController.kt:32	FP	FP型:測試或範例碼;這是 ports-and-adapters-demo 專案,且 validator 只放行 `WalletIssue` 基底類型和 Collection
31	rds-network__portal-backend/RedisSessionConfig.kt:33	FP	FP型:可信來源;mapper 是 Spring Session 的 Redis 序列化器,存的是伺服器自己的 session
32	seki-shinnosuke__kotlin-backend-base/RedisSessionConfig.kt:52	FP	FP型:可信來源;同為 Spring Session 的 Redis 序列化器
33	sjkyung__hhplus-server-ecommerce/RedisConfig.kt:45	FP	FP型:可信來源;mapper 只用在 Redis CacheManager
34	t0lia__RetypeMe/RedisConfig.kt:37	FP	FP型:可信來源;mapper 只用在 Redis 範本
35	taenyeon__kotlin-api-server-guide/CacheConfig.kt:78	FP	FP型:可信來源;mapper 供 Redis 快取與快取解析器使用,且是 guide 範例專案
36	v1p3rrr__get-science-backend/CacheConfig.kt:45	FP	FP型:可信來源;mapper 只用在 Redis 快取
37	v1p3rrr__get-science-backend/RedisConfig.kt:40	FP	FP型:可信來源;mapper 只用在 Redis 範本
38	vudsen__spectre/ArthasInstanceJvmConverter.kt:15	FP	FP型:已防護;validator 只放行 `Jvm` 子類型,且只做 JPA 欄位轉換
39	waveofmymind__coupon-event-example/RedisConfig.kt:36	FP	FP型:可信來源;mapper 只用在 Redis 範本,且是 example 專案
40	yongbin1__smonkey_backend/RedisConfig.kt:43	FP	FP型:可信來源;mapper 只用在 Redis 快取

總計:40 處,TP 2、FP 37、UNSURE 1。

TP 是第 6 和第 7 處。FP 裡最多的是自家 Redis 快取或 session,其次是已限制 validator,再來是範例和測試碼。

第 3、5、7、11、12、15、16、17、18、22、23、25、26、27、32、33、34、35、38、39、40 處的 validator 是 Any 基底或 Laissez-faire,不算「已防護」。這些都是靠「只處理自己寫的資料」判 FP,不是靠 validator。