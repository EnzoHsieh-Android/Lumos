// 容易誤報:Room 官方測試寫法,記憶體資料庫在測試裡允許主執行緒查詢
class DbTest {
    private val db = Room.inMemoryDatabaseBuilder(ctx, AppDb::class.java).allowMainThreadQueries().build() // GOOD
}
