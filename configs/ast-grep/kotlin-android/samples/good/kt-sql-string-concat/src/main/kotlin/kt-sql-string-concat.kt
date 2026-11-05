fun a(db: SQLiteDatabase, name: String) = db.rawQuery("select * from user where n = ?", arrayOf(name)) // GOOD
fun b(db: SQLiteDatabase) = db.rawQuery("select * from $TABLE where x = ?", arrayOf("$x")) // GOOD 常數表名,參數放綁定
fun c(name: String) = SimpleSQLiteQuery("select * from " + UserTable.NAME + " where n = ?", arrayOf(name)) // GOOD 常數串接
fun d(resolver: ContentResolver, uri: Uri) = resolver.query(uri, null, "n = ?", arrayOf(name), null) // GOOD
// 容易誤報:PRAGMA 與 DDL 不能用 ? 綁定;GraphQL/搜尋客戶端的 query 不是 SQL
fun e(db: SupportSQLiteDatabase, version: Int) = db.execSQL("PRAGMA user_version = $version") // GOOD
fun f(db: SupportSQLiteDatabase, tableName: String) = db.execSQL("DROP TABLE IF EXISTS $tableName") // GOOD
fun g(apollo: SearchClient, term: String) = apollo.query("search $term") // GOOD
