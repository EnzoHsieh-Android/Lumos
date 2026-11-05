// 語意覆核級已知誤報(代碼審 r2 規則B Finding 1):切回 Main 的寫法很多,要知道派發器是哪一個才判得準
class MainVariants(private val view: TextView, private val ui: CoroutineDispatcher, private val dispatchers: AppDispatchers) {
    fun a() = viewModelScope.launch(Dispatchers.IO) { withContext(Dispatchers.Main.immediate) { view.setText("a") } }
    fun b() = viewModelScope.launch(Dispatchers.IO) { withContext(Dispatchers.Main + CoroutineName("x")) { view.setText("b") } }
    fun c() = viewModelScope.launch(Dispatchers.IO) { withContext(dispatchers.main()) { view.setText("c") } }
    // 注入的派發器名字看不出是 Main,只能靠型別或呼叫端判
    fun d() = viewModelScope.launch(Dispatchers.IO) { withContext(ui) { view.setText("d") } }
}
