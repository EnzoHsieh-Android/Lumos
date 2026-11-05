fun a(db: SQLiteDatabase, name: String) = db.rawQuery("select * from user where n='$name'", null) // BAD
fun b(db: SupportSQLiteDatabase, id: String) = db.execSQL("delete from user where id = ${id.trim()}") // BAD
fun c(name: String) = SimpleSQLiteQuery("select * from user where n='" + name + "'") // BAD
fun d(db: SupportSQLiteDatabase, name: String) = db.query("select * from user where n='$name'") // BAD
fun e(helper: SQLiteOpenHelper, id: String) = helper.readableDatabase.query("select * from t where id='$id'") // BAD
// 代碼審 r2(規則B Finding 9):CREATE … AS SELECT … WHERE 的值可以綁定,不算 DDL 豁免;三引號同樣處理
fun g(db: SupportSQLiteDatabase, id: String) = db.execSQL("CREATE TABLE a AS SELECT * FROM b WHERE id='$id'") // BAD
fun h(db: SupportSQLiteDatabase, id: String) = db.execSQL("""
   CREATE TABLE z AS SELECT * FROM y WHERE a='$id'""") // BAD
