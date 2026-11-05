fun buildDb(context: Context): AppDb = Room.databaseBuilder(context, AppDb::class.java, "app.db")
    .build() // GOOD:DAO 用 suspend/Flow,不開主執行緒查詢

// 容易誤報:同一條 builder 鏈掛別的設定
fun buildCache(context: Context): CacheDb = Room.databaseBuilder(context, CacheDb::class.java, "cache.db")
    .fallbackToDestructiveMigration()
    .setQueryCallback({ sql, _ -> log(sql) }, executor)
    .build()
