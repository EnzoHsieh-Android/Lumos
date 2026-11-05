@Dao
interface UserDao {
    @Query("SELECT * FROM user")
    fun all(): List<User> // BAD:非 suspend、不回傳 Flow

    @Insert
    fun insert(user: User) // BAD
}
