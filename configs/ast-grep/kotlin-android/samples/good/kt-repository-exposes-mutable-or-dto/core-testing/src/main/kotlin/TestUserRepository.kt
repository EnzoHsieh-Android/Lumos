// 容易誤報:測試支援模組(core-testing)裡的假實作
class TestUserRepository {
    val users: MutableSharedFlow<List<User>> = MutableSharedFlow(replay = 1)
}
