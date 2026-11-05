suspend fun refresh(dao: UserDao, users: List<User>) {
    dao.deleteAll()
    dao.insertAll(users) // BAD
}
suspend fun refresh2(db: AppDb, users: List<User>) {
    val n = db.userDao().clearAll()
    db.userDao().upsertAll(users) // BAD
}
