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
