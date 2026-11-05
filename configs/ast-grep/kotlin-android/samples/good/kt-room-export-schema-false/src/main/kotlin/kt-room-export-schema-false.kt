@Database(entities = [User::class], version = 2) // GOOD 預設 true
abstract class AppDb : RoomDatabase()

@Database(entities = [User::class], version = 2, exportSchema = true) // GOOD
abstract class OtherDb : RoomDatabase()
