fun a(db: SQLiteDatabase, name: String) = db.rawQuery("select * from user where n='$name'", null) // BAD
fun b(db: SupportSQLiteDatabase, id: String) = db.execSQL("delete from user where id = ${id.trim()}") // BAD
fun c(name: String) = SimpleSQLiteQuery("select * from user where n='" + name + "'") // BAD
