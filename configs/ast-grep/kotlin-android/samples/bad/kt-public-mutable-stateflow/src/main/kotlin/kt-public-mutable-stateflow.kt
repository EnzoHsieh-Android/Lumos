class FeedViewModel : ViewModel() {
    val state = MutableStateFlow(FeedState()) // BAD
}

class LoginViewModel : ViewModel() {
    internal val loading = MutableStateFlow(false) // BAD:internal 也是公開給模組內
}
