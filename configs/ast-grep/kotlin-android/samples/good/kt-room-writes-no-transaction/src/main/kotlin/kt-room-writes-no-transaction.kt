suspend fun refresh(db: AppDb, users: List<User>) {
    db.withTransaction {
        db.userDao().deleteAll()
        db.userDao().insertAll(users) // GOOD
    }
}
@Dao
interface UserDao {
    @Transaction
    suspend fun replace(users: List<User>) {
        deleteAll()
        insertAll(users) // GOOD 本來就不帶 dao 前綴
    }
}
suspend fun add(dao: UserDao, u: User) {
    dao.insert(u) // GOOD 前面沒有刪除
}
