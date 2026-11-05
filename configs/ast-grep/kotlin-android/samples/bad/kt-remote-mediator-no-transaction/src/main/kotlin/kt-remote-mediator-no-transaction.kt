class M(private val db: AppDb, private val api: Api) : RemoteMediator<Int, User>() {
    override suspend fun load(type: LoadType, state: PagingState<Int, User>): MediatorResult {
        val page = api.page(1)
        db.userDao().clearAll() // BAD
        db.userDao().insertAll(page.items) // BAD
        remoteKeyDao.insert(Key(page.next)) // BAD
        return MediatorResult.Success(endOfPaginationReached = page.next == null)
    }
}
