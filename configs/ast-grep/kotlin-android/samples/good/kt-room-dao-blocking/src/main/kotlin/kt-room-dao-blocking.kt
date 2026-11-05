@Dao
interface UserDao {
    @Query("SELECT * FROM user")
    suspend fun all(): List<User> // GOOD

    @Insert
    suspend fun insert(user: User) // GOOD
}

// 容易誤報:非 suspend 但回傳 Flow / PagingSource,本身不會擋執行緒
@Dao
interface OrderDao {
    @Query("SELECT * FROM orders")
    fun observe(): Flow<List<Order>> // GOOD

    @Query("SELECT * FROM orders ORDER BY id")
    fun paging(): PagingSource<Int, Order> // GOOD
}
