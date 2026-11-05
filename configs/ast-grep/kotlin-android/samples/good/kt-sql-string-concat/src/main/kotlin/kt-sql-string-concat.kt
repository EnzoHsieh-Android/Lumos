fun a(db: SQLiteDatabase, name: String) = db.rawQuery("select * from user where n = ?", arrayOf(name)) // GOOD
fun b(db: SQLiteDatabase) = db.rawQuery("select * from $TABLE where x = ?", arrayOf("$x")) // GOOD 常數表名,參數放綁定
fun c(name: String) = SimpleSQLiteQuery("select * from " + UserTable.NAME + " where n = ?", arrayOf(name)) // GOOD 常數串接
fun d(resolver: ContentResolver, uri: Uri) = resolver.query(uri, null, "n = ?", arrayOf(name), null) // GOOD
