fun buildDb(context: Context): AppDb = Room.databaseBuilder(context, AppDb::class.java, "app.db")
    .allowMainThreadQueries() // BAD
    .build()

fun buildCache(context: Context): CacheDb {
    val builder = Room.databaseBuilder(context, CacheDb::class.java, "cache.db")
    return builder.fallbackToDestructiveMigration().allowMainThreadQueries().build() // BAD
}
