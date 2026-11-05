class F : Fragment() {
    fun a() {
        lifecycleScope.launch(Dispatchers.IO) {
            val d = load()
            textView.text = d // BAD
        }
    }
    fun b() {
        scope.launch(Dispatchers.Default) {
            val list = compute()
            binding.list.adapter = Adapter(list) // BAD
            progress.setVisibility(View.GONE) // BAD
        }
    }
    suspend fun c() = withContext(Dispatchers.IO) {
        title.setText(read()) // BAD
    }
}

// 名字裡藏著 main 字樣但不是 Main 派發器
class Domain(private val domainDispatcher: CoroutineDispatcher, private val tv: TextView) {
    fun a(scope: CoroutineScope) = scope.launch(Dispatchers.IO) {
        withContext(domainDispatcher) { tv.text = load() } // BAD
    }
}

// 代碼審 r2(規則B Finding 2):外層 Main 不代表內層 IO 區塊安全;mainland… 不是 Main 派發器
class Nested(private val view: TextView, private val mainlandIoDispatcher: CoroutineDispatcher) {
    fun i() = viewModelScope.launch(Dispatchers.Main) { withContext(Dispatchers.IO) { view.setText("bad") } } // BAD
    fun k() = viewModelScope.launch(Dispatchers.IO) { launch(mainlandIoDispatcher) { view.setText("bad") } } // BAD
}
