val db = Room.databaseBuilder(ctx, AppDb::class.java, "app.db")
    .addMigrations(MIGRATION_1_2) // GOOD
    .fallbackToDestructiveMigrationOnDowngrade() // GOOD 只有降版
    .build()
fun build(b: RoomDatabase.Builder<AppDb>) {
    if (BuildConfig.DEBUG) b.fallbackToDestructiveMigration() // GOOD 只在 debug
}
