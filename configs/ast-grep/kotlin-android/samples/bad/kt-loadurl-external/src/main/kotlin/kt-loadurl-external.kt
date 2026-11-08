class WebActivity : Activity() {
    fun showOne(webView: WebView) {
        webView.loadUrl(intent.getStringExtra("url")!!) // BAD 直接用 Intent 帶來的網址
    }
    fun showTwo(webView: WebView) {
        val target = intent.dataString ?: return
        webView.loadUrl(target) // BAD 經區域變數
    }
    fun showThree(webView: WebView) {
        intent.getStringExtra("url")?.let { webView.loadUrl(it) } // BAD let 的 it
    }
}
