fun setupOne(webView: WebView) {
    webView.settings.allowFileAccess = false // GOOD 明寫 false
    webView.settings.setAllowFileAccess(false) // GOOD
}
fun setupTwo(webView: WebView, ctx: Context) {
    // GOOD 本機內容走 WebViewAssetLoader 的 https 網址
    val loader = WebViewAssetLoader.Builder().addPathHandler("/assets/", WebViewAssetLoader.AssetsPathHandler(ctx)).build()
    webView.loadUrl("https://appassets.androidplatform.net/assets/index.html")
}
