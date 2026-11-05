suspend fun a() {
    (1..1_000_000).asFlow().cancellable().collect { heavy(it) } // GOOD
    items.asFlow().map { convert(it) }.cancellable().collect() // GOOD
    userLiveData.asFlow().collect { show(it) } // GOOD
}

// 容易誤報:函式參照轉的 asFlow 只發一個值,不是集合迴圈
fun userFlow(): Flow<User> = ::fetchUser.asFlow() // GOOD
