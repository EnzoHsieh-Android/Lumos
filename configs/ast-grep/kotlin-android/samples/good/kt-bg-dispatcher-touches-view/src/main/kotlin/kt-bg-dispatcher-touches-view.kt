class F : Fragment() {
    fun a() {
        lifecycleScope.launch(Dispatchers.IO) {
            val d = load()
            withContext(Dispatchers.Main) { textView.text = d } // GOOD
        }
    }
    fun b() {
        lifecycleScope.launch {
            val d = withContext(Dispatchers.IO) { load() }
            textView.text = d // GOOD
        }
    }
    fun c() {
        scope.launch(Dispatchers.IO) {
            val d = load()
            _state.value = d // GOOD
            runOnUiThread { title.text = d } // GOOD
        }
    }
}

// 容易誤報:背景解碼,改 View 包在 view.post { } 裡回主執行緒
class Avatar(private val image: ImageView) {
    fun load(scope: CoroutineScope, path: String) {
        scope.launch(Dispatchers.Default) {
            val bmp = decode(path)
            image.post { image.setImageBitmap(bmp) } // GOOD
        }
    }
}
