fun openOne(ctx: Context): AppDb {
    return Room.databaseBuilder(ctx, AppDb::class.java, "room.db").build() // GOOD 只給檔名,放內部儲存
}
fun openTwo(ctx: Context): SQLiteDatabase {
    return SQLiteDatabase.openOrCreateDatabase(ctx.getDatabasePath("app.db"), null) // GOOD
}
