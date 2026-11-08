以下是兩條規則的判讀結果,全部放在同一張表。我沒有建立或修改任何檔案,也沒有動 git。

```
ruleId	檔	行	判定	理由
kt-provider-openfile-traversal	ColdP__HyperChanger/app/src/main/java/btm/m/os4/systemuihook/SettingsEntryIconHooks.kt	161	FP	FP型:已防護;檔名只從 pathSegments 的固定白名單(icons、module)對應到常數檔名,uri 內容進不了 File,另有呼叫者 UID 檢查
kt-provider-openfile-traversal	DaviBaechtold__Pinterest-to-WhatsApp/android/app/src/main/java/com/stickerfodaapp/StickerContentProvider.kt	83	TP	uri.pathSegments[1] 與 lastPathSegment 解碼後直接組進 File(packsDir,…),沒有 canonical 或白名單檢查,可用 %2F 或 .. 跳出 packsDir;WhatsApp 貼圖 provider 必須對外開放
kt-provider-openfile-traversal	DaviBaechtold__Pinterest-to-WhatsApp/android/app/src/main/java/com/stickerfodaapp/StickerContentProvider.kt	83	TP	與上一列同一處(重複區塊):uri 片段直接進 File,沒有 canonical 檢查
kt-provider-openfile-traversal	FossifyOrg__Thank-You/app/src/main/kotlin/org/fossify/thankyou/contentproviders/MyContentProvider.kt	64	FP	FP型:已防護;File(name).name 只留檔名,再加 isFontFile() 過濾,且固定在 fonts 目錄下
kt-provider-openfile-traversal	KieronQuinn__uTag/app/src/main/java/com/kieronquinn/app/utag/providers/EncryptedFileProvider.kt	69	TP	lastPathSegment 直接進 File(imagesDir,…),沒有 canonical 檢查;呼叫者套件白名單不是路徑防護,而且 SDK&gt;=36 且設定開啟時完全不檢查
kt-provider-openfile-traversal	N2K02__LocalAdb/app/src/main/java/dev/n2k02/localadb/ShizukuPayloadProvider.kt	55	FP	FP型:已防護;requested 必須在 embedded、starter、rish 三個值之內才會用到,另有 SHELL_UID 檢查
kt-provider-openfile-traversal	NLLAPPS__ACRPhoneHelper/app/src/main/java/com/nll/helper/ServerContentProvider.kt	147	TP	lastPathSegment!! 直接接到外部快取目錄後面,沒有 canonical 或白名單檢查
kt-provider-openfile-traversal	Oliver29Klozoff__IPTV-Mj/app/src/main/java/com/iptvapp/tv/LauncherArtwork.kt	140	FP	FP型:已防護;檔名必須完全符合 64 位十六進位的 regex,且 pathSegments 只能一段
kt-provider-openfile-traversal	PoCInnovation__PoC2Peer/app/common/src/main/java/com/example/android/uamp/media/library/AlbumArtContentProvider.kt	33	TP	File(uri.path) 只用 file.path.startsWith(cacheDir.path) 檢查,沒有 canonicalPath,cache/../ 可繞過
kt-provider-openfile-traversal	arnodenhond__ImageShortcut/app/src/main/java/arnodenhond/imageshortcut/ImageProvider.kt	17	TP	lastPathSegment 解碼後直接組進 File(imagesDir,id),沒有任何檢查;未確認 exported
kt-provider-openfile-traversal	awong-dev__pager/bridge-android/app/src/main/java/app/kidpager/bridge/MmsReceiver.kt	109	TP	lastPathSegment 直接進 File(dir,…),沒有檢查,而且 mode 由呼叫端決定(可寫);未確認 exported
kt-provider-openfile-traversal	bailuk__AAT/aat-android/src/main/kotlin/ch/bailu/aat/providers/GpxSendViewProvider.kt	29	UNSURE	開檔前有 providerContext.isExportAllowed(path) 把關,但該 helper 不在語料裡,看不出是不是 canonical 或白名單;缺 ProviderContext.isExportAllowed 的原始碼
kt-provider-openfile-traversal	chadyi__StudyOnTV/app/native/app/src/main/java/com/studyontv/tv/ApkProvider.kt	23	TP	lastPathSegment 直接進 File(cacheDir/updates,name),沒有 canonical 檢查
kt-provider-openfile-traversal	finamp-app__finamp/android/app/src/main/kotlin/com/unicornsonlsd/finamp/MediaItemContentProvider.kt	64	TP	File(uri.path!!) 直接開檔,沒有任何路徑限制
kt-provider-openfile-traversal	lazy-engineer__castaway/castawayplayer/src/main/java/io/github/lazyengineer/castawayplayer/service/MediaArtContentProvider.kt	17	TP	File(uri.path) 只做 startsWith(cacheDir.path),沒有 canonicalPath,可用 .. 繞過
kt-provider-openfile-traversal	likhithpraveenk__storii/android/app/src/main/kotlin/com/likhithpraveenk/storii/CoversContentProvider.kt	55	TP	來源路徑由 uri 最後一段 base64 解出(decodeSource 只解碼不驗證),file scheme 與無 scheme 都直接 File(path).inputStream() 讀取,等於任意檔案讀取
kt-provider-openfile-traversal	mooazn__finamp/android/app/src/main/kotlin/com/unicornsonlsd/finamp/MediaItemContentProvider.kt	64	TP	與 finamp-app 同碼:File(uri.path!!) 直接開檔,沒有路徑限制
kt-provider-openfile-traversal	nhaarman__acorn/samples/hello-sharedata/src/main/java/com/nhaarman/acorn/samples/hellosharedata/pictures/PictureContentProvider.kt	60	FP	FP型:測試或範例碼;路徑含 samples/ 目錄(形狀雖然是 TP,但依客觀特徵歸範例)
kt-provider-openfile-traversal	pley-media-server__pley/apps/android/app/src/main/kotlin/app/pley/android/watchnext/WatchNextImages.kt	101	FP	FP型:已防護;名稱必須符合 [0-9a-f]{64} 且 pathSegments 只能一段,並限定 mode 為 r
kt-provider-openfile-traversal	ppcharcoal__aurora/src-tauri/aurora-mobile/android/src/main/java/app/aurora/mobile/ArtProvider.kt	23	FP	FP型:已防護;檔名擋掉含 /、以 . 開頭、非 .jpg 結尾;lastPathSegment 已解碼不含 /,.. 也被擋
kt-provider-openfile-traversal	wanda1416__lvjiang/android/app/src/main/java/com/lvjiang/app/SelfTestProvider.kt	41	FP	FP型:已防護;uri.path 只對應三個固定相對路徑,其餘丟例外,另有 shell、root、自身 UID 檢查
kt-provider-openfile-traversal	總計		TP12 FP8 UNSURE1	共 21 處;FP 型:已防護 7、測試或範例碼 1
kt-db-on-external-files	Andrew05812__CK/app/src/main/java/com/taskplanner/data/local/AppDatabase.kt	37	TP	App 自己的 Room 資料庫建在 getExternalFilesDir
kt-db-on-external-files	Winnie0408__LocalMusicHelper/app/src/main/java/com/hwinzniej/musichelper/activity/ConvertPage.kt	1329	TP	App 把內建 asset 的 cloudmusic.db 複製到外部檔案目錄後以 OPEN_READWRITE 開啟並寫入,是 App 自己建立的資料庫,不是使用者選來匯入的
kt-db-on-external-files	Winnie0408__LocalMusicHelper/app/src/main/java/com/hwinzniej/musichelper/activity/ConvertPage.kt	1374	TP	同上:asset 複製到外部目錄的 QQMusic 資料庫,讀寫開啟
kt-db-on-external-files	Winnie0408__LocalMusicHelper/app/src/main/java/com/hwinzniej/musichelper/activity/ConvertPage.kt	1459	TP	同上:asset 複製到外部目錄的 kugou_music_phone_v7.db,讀寫開啟
kt-db-on-external-files	Winnie0408__LocalMusicHelper/app/src/main/java/com/hwinzniej/musichelper/activity/ConvertPage.kt	1559	TP	同上:asset 複製到外部目錄的 QQMusic,讀寫開啟
kt-db-on-external-files	Winnie0408__LocalMusicHelper/app/src/main/java/com/hwinzniej/musichelper/activity/ConvertPage.kt	1597	TP	同上:asset 複製到外部目錄的 QQMusic,讀寫開啟
kt-db-on-external-files	Winnie0408__LocalMusicHelper/app/src/main/java/com/hwinzniej/musichelper/activity/ConvertPage.kt	1760	TP	同上:外部目錄的 cloudmusic.db,讀寫開啟
kt-db-on-external-files	Winnie0408__LocalMusicHelper/app/src/main/java/com/hwinzniej/musichelper/activity/ConvertPage.kt	1834	TP	同上:外部目錄的 QQMusic,讀寫開啟
kt-db-on-external-files	Winnie0408__LocalMusicHelper/app/src/main/java/com/hwinzniej/musichelper/activity/ConvertPage.kt	1903	TP	同上:外部目錄的 kugou_music_phone_v7.db,讀寫開啟
kt-db-on-external-files	Winnie0408__LocalMusicHelper/app/src/main/java/com/hwinzniej/musichelper/activity/ConvertPage.kt	1998	TP	同上:外部目錄的 kwplayer.db,讀寫開啟
kt-db-on-external-files	Winnie0408__LocalMusicHelper/app/src/main/java/com/hwinzniej/musichelper/activity/ConvertPage.kt	2074	TP	同上:外部目錄的 QQMusic,讀寫開啟
kt-db-on-external-files	Winnie0408__LocalMusicHelper/app/src/main/java/com/hwinzniej/musichelper/activity/ConvertPage.kt	2171	TP	同上:外部目錄的 QQMusic,讀寫開啟
kt-db-on-external-files	Winnie0408__LocalMusicHelper/app/src/main/java/com/hwinzniej/musichelper/activity/ConvertPage.kt	4607	TP	同上:csv 轉換流程把 asset 的 QQMusic 複製到外部目錄後讀寫開啟,資料庫是 App 自己建的
kt-db-on-external-files	chemagonz__BRSMovilidadERP/app/src/main/java/com/advantys/brsmovilidaderp/Data/DataBase/BD.kt	26	TP	App 自己的資料庫 BRSAndroid.db 固定放在 getExternalStorageDirectory()/BRSAndroid/
kt-db-on-external-files	chemagonz__El_Cortijillo/app/src/main/java/com/advantys/el_cortijillo/Data/Database/BD.kt	25	TP	App 自己的資料庫 CortijilloDef.db 放在 getExternalStorageDirectory()/ElCortijillo/
kt-db-on-external-files	evanbattaglia__jide/app/src/main/java/com/instructure/ebattaglia/jide/Anki.kt	23	FP	FP型:匯入外部資料庫;唯讀開啟 AnkiDroid 的 collection.anki2(別的 App 的資料庫)
kt-db-on-external-files	ilemobayo__KStudio/app/versions/media session/src/main/java/com/musicplayer/aow/delegates/data/source/db/DbLiteHelper.kt	17	TP	App 自己的資料庫(外部儲存/&lt;套件名&gt;/data/db,CREATE_IF_NECESSARY 自己建立)
kt-db-on-external-files	ilemobayo__KStudio/app/versions/media session/src/main/java/com/musicplayer/aow/delegates/data/source/db/DbLiteHelper.kt	25	TP	同上:openDatabase() 中同一個外部路徑,自己建立
kt-db-on-external-files	jim0608__SeetaFace/lib_base/src/main/java/com/mysafe/lib_base/sqlite/FaceDatabase.kt	28	TP	Room 資料庫 faceDB.db 建在 getExternalFilesDir("database")
kt-db-on-external-files	jim0608__SeetaFace/seetaface/src/main/java/com/seeta/sdk/sqlite/FaceDatabase.kt	25	TP	Room 資料庫 faceDB.db 建在 getExternalFilesDir("database")
kt-db-on-external-files	mmm3w__JLPT-Mitsuki/app/src/main/java/com/mitsuki/jlpt/app/TempUtils.kt	25	FP	FP型:匯入外部資料庫;唯讀開啟外部儲存根目錄的 jlpt1.sqlite(別人準備的資料),讀出後轉進自己的 Room,是一次性匯入工具
kt-db-on-external-files	mmm3w__JLPT-Mitsuki/app/src/main/java/com/mitsuki/jlpt/app/TempUtils.kt	32	FP	FP型:匯入外部資料庫;同上,唯讀開啟外部的 jlpt.sqlite 轉進 Room
kt-db-on-external-files	shizuku__Notes/app/src/main/java/com/shizuku/tools/notes/data/database/NotesDatabase.kt	26	TP	App 自己的 Room 資料庫 notes.db 建在 getExternalFilesDir
kt-db-on-external-files	umang-choudhary__UnitTestDemo/app/src/main/java/com/example/unittestdemo/db/AppDatabase.kt	30	FP	FP型:測試或範例碼;repo 名 UnitTestDemo 含 demo(形狀是 TP)
kt-db-on-external-files	wojteksz128__Work-time-measure-app/app/src/main/kotlin/net/wojteksz128/worktimemeasureapp/database/AppDatabase.kt	40	TP	App 自己的 Room 資料庫 work-time-measure.db 建在 getExternalFilesDir
kt-db-on-external-files	總計		TP21 FP4 UNSURE0	共 25 處;FP 型:匯入外部資料庫 3、測試或範例碼 1
```

- **kt-provider-openfile-traversal 的 UNSURE:** AAT 那一處的檢查函式 `isExportAllowed` 不在語料裡,我找不到它的原始碼,所以判 UNSURE。
- **有爭議的判定:** LocalMusicHelper 的 12 處我判 TP。理由是資料庫由 App 從 asset 複製到外部目錄再讀寫,不是使用者選來匯入的。如果你把「轉檔用的暫存資料庫」也算成匯入,這 12 處會改成 FP。
- **沒有建立任何臨時目錄。**
