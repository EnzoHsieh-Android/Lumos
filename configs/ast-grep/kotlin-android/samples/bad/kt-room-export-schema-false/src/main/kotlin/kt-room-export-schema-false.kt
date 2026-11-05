@Database(entities = [User::class], version = 2, exportSchema = false) // BAD
abstract class AppDb : RoomDatabase()

@Database( // BAD 多行寫法
    entities = [User::class],
    exportSchema = false,
    version = 3,
)
abstract class OtherDb : RoomDatabase()
