class M(private val db: AppDb, private val api: Api) : RemoteMediator<Int, User>() {
    override suspend fun load(type: LoadType, state: PagingState<Int, User>): MediatorResult {
        val page = api.page(1)
        db.withTransaction {
            db.userDao().clearAll() // GOOD
            db.userDao().insertAll(page.items) // GOOD
            db.remoteKeyDao().insert(Key(page.next)) // GOOD
        }
        return MediatorResult.Success(endOfPaginationReached = page.next == null)
    }
}

// 容易誤報:不是 RemoteMediator 的 Repository 單筆寫入 DAO
class UserRepository(private val userDao: UserDao) {
    suspend fun save(user: User) = userDao.insert(user) // GOOD
}
