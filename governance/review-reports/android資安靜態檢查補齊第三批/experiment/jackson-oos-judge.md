0	AkkapongK__assistant/.../RedisConfig.kt:39	FP	FP型:可信來源;mapper 只掛在自己的 RedisTemplate,序列化 App 自己寫進 Redis 的資料(雖用 LaissezFaire,外部碰不到)
1	Central-MakeUs__CMC_BE/.../RedisConfig.kt:38	FP	FP型:可信來源;只用於 RedisCacheManager 的值序列化,存取的是自己的快取(allowIfBaseType(Any) 不算防護,但來源可信)
2	DongGeon0908__practice-redis/.../RedisConfig.kt:83	FP	FP型:可信來源;mapper 只給 Redis 快取的 GenericJackson2JsonRedisSerializer 用(雖是 LaissezFaire),也是練習專案
3	EEseka__lynk-api/.../RedisConfig.kt:36	FP	FP型:已防護;PolymorphicTypeValidator 只放 java.util.、kotlin.collections.、com.eeseka.lynk.,且只用於 Redis 快取
4	HecAguilaV__SIGA/.../RedisConfig.kt:23	FP	FP型:可信來源;LaissezFaire 的 mapper 只用於 Redis 快取管理器(TTL 1 分鐘),存取的是自己的資料
5	Jeesu-Jung__WEAVE/.../CacheConfig.kt:52	FP	FP型:可信來源;mapper 只給 Redis 快取序列化,外部碰不到
6	LoaLifeCalculator__Server/.../RedisConfig.kt:25	FP	FP型:可信來源;enableDefaultTyping 的 mapper 只用於 Redis 快取序列化
7	LovelyCatEx__crystal-framework/.../RedisConfig.kt:25	FP	FP型:可信來源;mapper 只給 ReactiveRedisTemplate 的值序列化,存取的是自己的資料(allowIfBaseType(Any) 不算防護)
8	LovesAsuna__OnlineEducation/.../RedisConfig.kt:50	FP	FP型:可信來源;mapper 只給 RedisTemplate 與 cacheManager 的值序列化,且用的是 DefaultBaseTypeLimitingValidator
9	Mart6DeLavi__emergency-notification-system/.../RedisCacheConfig.kt:22	FP	FP型:可信來源;copy 出來的 mapper 只掛在 Redis 快取管理器上,不影響原本處理 HTTP 的全域 mapper
10	P-py__watch-to-next/.../CacheConfig.kt:36	FP	FP型:已防護;PolymorphicTypeValidator 只放 com.watchtonext.、java.util.、java.time.,且只用於 Redis 快取
11	SweepHee__gme-api/.../CacheConfig.kt:28	FP	FP型:可信來源;mapper 只給 Redis 快取序列化(allowIfSubType(Object) 不算防護,但來源可信)
12	TN-Club-Algo__website/.../RedisDatabase.kt:32	FP	FP型:已防護;BasicPolymorphicTypeValidator 沒有任何 allow 規則,等於不放行任何子型別,且只用於 Redisson 自己的 codec
13	Team-4IGHTING__4Gamer-Server/.../RedisCacheConfig.kt:43	FP	FP型:可信來源;mapper 只給 Redis 快取序列化,外部碰不到
14	aintbe__jukebox/.../RedisConfig.kt:86	FP	FP型:已防護;PolymorphicTypeValidator 只允許 com.jukebox. 與 java.util.Collection 子型別,且只用於快取
15	alpas__alpas/.../JsonSerializer.kt:27	TP	框架通用的 JsonSerializer.deserialize 用 LaissezFaireSubTypeValidator 解析任意傳入字串,看不出來源限制,使用者可能拿它解外部 JSON
16	chanhl22__hhplus-server/.../CacheConfig.kt:30	FP	FP型:可信來源;mapper 只用於 Redis 快取序列化(使用預設的 polymorphicTypeValidator,範圍寬,但只讀自己寫的資料)
17	chriswoodcn__anthill/.../RedisConfig.kt:46	FP	FP型:可信來源;全域 mapper 的 copy 只掛在 Redisson 的 codec 上,原 mapper 不受影響
18	dbs24__dbs/.../MainApplicationConfig.kt:24	FP	FP型:已防護;PolymorphicTypeValidator 只放 org.dbs 與 java.util.,雖是全域 bean 但白名單限制在自家套件
19	dolong2__dcd/.../RedisConfig.kt:57	FP	FP型:可信來源;mapper 只給 Redis cacheManager 的值序列化(allowIfSubType(Any) 不算防護,但來源可信)
20	dudgns2824__problem-test-kotlin-hexagonal-multimodule/.../ObjactMapperConfig.kt:27	UNSURE	具名的 4Generic mapper 開 EVERYTHING 且 allowIfBaseType(Any);看不出是只用於 Redis/內部,還是會解外部 JSON,缺它的注入端使用處
21	f-nyx__afip-sdk-kotlin/.../ObjectMapperFactory.kt:16	UNSURE	SDK 公開的 anySupportMapper 開 EVERYTHING 且 allowIfBaseType(Any);缺呼叫端資料,不知是否用來解析 AFIP 外部 API 回應
22	fassousa__currency-converter-kotlin/.../CacheConfig.kt:31	FP	FP型:可信來源;copy 出來的 mapper 只用於 Redis 快取,為了 BigDecimal 型別還原(allowIfBaseType(Any) 不算防護,但來源可信)
23	janapc__online-course-system/.../RedisConfig.kt:35	FP	FP型:可信來源;copy 的 mapper 只用於 Redis cacheManager,不影響原本處理 HTTP 的 mapper
24	jhs512__blog-1/.../RedisCacheConfig.kt:29	FP	FP型:可信來源;mapper 只用於 Redis 快取序列化
25	kaeawc__krit/tests/fixtures/positive/security/JacksonDefaultTyping.kt:7	FP	FP型:測試或範例碼;是靜態分析工具的 positive fixture,刻意寫成不安全寫法
26	kji1111__hexagonal-architecture-boilerplate/.../CacheConfig.kt:105	FP	FP型:可信來源;customObjectMapper 在 cache-adapter 的 CacheConfig 內,供 Redis 快取序列化用(copy 全域 mapper),也是 boilerplate
27	lucasdengcn__spring-native-image-starter/.../CachingConfig.kt:66	FP	FP型:可信來源;獨立 mapper 只用於 redisSerializer 的 Redis 快取,另有一個沒開預設型別的 @Primary mapper;專案本身是 starter 範例
28	radicaled__spacebros/.../Game.kt:204	FP	FP型:可信來源;saveMap 只把遊戲地圖寫到自己的本機檔(序列化),沒有解析外部輸入
29	radicaled__spacebros/.../Game.kt:238	FP	FP型:可信來源;bootstrapCustomMap 只讀伺服器本機 assets/map.json(寫死的開發者路徑),不是外部輸入
30	shinkats__sessionredis/.../SessionConfig.kt:25	FP	FP型:可信來源;mapper 只給 Spring Session 的 Redis 序列化,還註冊了 SecurityJackson2Modules,存的是自己的 session
31	shoyoream__shoyoream-server/.../ProductCacheConfig.kt:34	FP	FP型:可信來源;mapper 只給 Redis 快取序列化(allowIfSubType(Any) 不算防護,但來源可信)
32	sjkyung__coupon-server/.../CacheConfiguration.kt:45	FP	FP型:可信來源;mapper 只給 Redis 快取序列化
33	spbu-coding-2024__graphs-graphs-team-6/.../GraphService.kt:35	UNSURE	LaissezFaire 的 mapper 用於 toJson/fromJson,看不出 fromJson 的輸入是來自外部還是自己存的圖資料(像是學生專案),缺呼叫端
34	whatever-x__backend/.../CacheConfig.kt:26	FP	FP型:可信來源;mapper 只給 Redis 快取序列化(allowIfBaseType(Any) 不算防護,但來源可信)
35	xia5800__zeta-kotlin/.../KtObjectMapper.kt:38	TP	框架的全域 KtObjectMapper.instance 單例,用 LaissezFaire + EVERYTHING,給全專案用,來源無限制
36	xia5800__zeta-kotlin-layui/.../KtObjectMapper.kt:38	TP	同 35:全域單例 mapper 用 LaissezFaire + EVERYTHING,來源無限制
37	yanglet__lemontree/.../CacheConfiguration.kt:19	FP	FP型:可信來源;mapper 只給 Redis 快取序列化(allowIfBaseType(Any) 不算防護,但來源可信)
38	yanglet__money-api/.../CacheConfiguration.kt:24	FP	FP型:可信來源;mapper 只給 Redis 快取序列化
39	zhijian-tianshi__MintCloud/.../KtObjectMapper.kt:38	TP	同 35:框架複本的全域單例 mapper 用 LaissezFaire + EVERYTHING,來源無限制
總計	40 處:TP 4(15、35、36、39)、FP 33、UNSURE 3(20、21、33)

我沒開 #1 和 #2 的全檔,只看了 ctx 裡的前後文。#1 的 mapper 掛在 cacheManager 的值序列化上,我是從這點判可信來源。