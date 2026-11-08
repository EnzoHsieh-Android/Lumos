class WebActivity : Activity() {
    fun showOne(webView: WebView) {
        val uri = Uri.parse(intent.getStringExtra("url") ?: return)
        if (uri.scheme == "https" && uri.host in ALLOWED_HOSTS) webView.loadUrl(uri.toString()) // GOOD 驗過 scheme 與 host
    }
    fun showTwo(webView: WebView) {
        webView.loadUrl("https://example.com/help") // GOOD 固定網址
    }
}
fun showHelp(webView: WebView, page: String) {
    webView.loadUrl("https://example.com/help/" + page) // GOOD 網址不是 Intent 帶進來的
}
