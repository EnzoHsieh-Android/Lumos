// 容易誤報:測試假實作故意公開可變流,讓測試推值
class FakeUserRepository {
    val userFlow = MutableSharedFlow<User>()
    val events = Channel<Event>()
    var items = mutableStateListOf<Int>()
    val live = MutableLiveData<String>()
}
