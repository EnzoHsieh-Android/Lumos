fun openOne(ctx: Context): SQLiteDatabase {
    return SQLiteDatabase.openOrCreateDatabase(File(ctx.getExternalFilesDir(null), "app.db"), null) // BAD 外部儲存
}
fun openTwo(ctx: Context): AppDb {
    val path = File(ctx.getExternalFilesDir(null), "room.db").path
    return Room.databaseBuilder(ctx, AppDb::class.java, path).build() // BAD 經區域變數
}
