abstract class AppDb : RoomDatabase() {
    companion object {
        @Volatile private var INSTANCE: AppDb? = null
        fun get(ctx: Context): AppDb = INSTANCE ?: synchronized(this) {
            Room.databaseBuilder(ctx, AppDb::class.java, "app.db").build().also { INSTANCE = it } // GOOD
        }
    }
}
@Module
class DbModule {
    @Provides @Singleton
    fun db(ctx: Context) = Room.databaseBuilder(ctx, AppDb::class.java, "app.db").build() // GOOD
}
fun buildDb(ctx: Context): AppDb = Room.databaseBuilder(ctx, AppDb::class.java, "app.db").build() // GOOD 工廠
