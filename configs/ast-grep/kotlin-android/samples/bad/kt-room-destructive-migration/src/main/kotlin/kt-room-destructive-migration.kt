// BAD 多行鏈式
val db = Room.databaseBuilder(ctx, AppDb::class.java, "app.db")
    .fallbackToDestructiveMigration()
    .build()
val db2 = Room.databaseBuilder(ctx, AppDb::class.java, "app.db").fallbackToDestructiveMigration(dropAllTables = true).build() // BAD
