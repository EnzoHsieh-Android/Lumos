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
