class FeedViewModel : ViewModel() {
    private val _state = MutableStateFlow(FeedState())
    val state: StateFlow<FeedState> = _state.asStateFlow() // GOOD
}

// 容易誤報:對外屬性名字一樣、型別宣告成唯讀 StateFlow
class LoginViewModel : ViewModel() {
    private val _loading = MutableStateFlow(false)
    val loading: StateFlow<Boolean> get() = _loading // GOOD
}
